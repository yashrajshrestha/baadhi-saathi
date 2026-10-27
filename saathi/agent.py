"""The Strands agent: four tools, Bedrock Nova Lite for the words, and a risk level the model cannot lower.

    python -m saathi.agent "Arughat" [--lang ne|en] [--sms] [--dry-run]

Flow: the agent looks up the place, calls river_outlook and rain_outlook (numbers and a risk level
computed in code), fetches safe places and emergency numbers, then writes advice for one household
in plain Nepali or English. `finish()` stamps the code's own level line on top of whatever the model
wrote, so a soothing paragraph can never hide a "danger". --dry-run skips the model and prints the
tool outputs, which costs nothing and needs no AWS login.

Environment: AWS_PROFILE (e.g. personal) and BEDROCK_REGION (default us-east-1) for Bedrock;
MODEL_ID to change the model (default amazon.nova-lite-v1:0).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from strands import Agent, tool

from . import places, rain, rivers, upstream

MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.environ.get("BEDROCK_REGION", "us-east-1")

LEVEL_WORDS = {
    "calm":    {"en": "CALM: no river flood expected in the next 7 days", "ne": "शान्त: आगामी ७ दिन नदी बाढीको सम्भावना छैन"},
    "watch":   {"en": "WATCH: the river will run higher than usual", "ne": "सतर्क: नदी सामान्यभन्दा माथि बग्नेछ"},
    "warning": {"en": "WARNING: a high flow is coming, prepare now", "ne": "चेतावनी: ठूलो बहाव आउँदैछ, अहिले नै तयारी गर्नुहोस्"},
    "danger":  {"en": "DANGER: very high flow forecast, move valuables and plan to leave", "ne": "खतरा: धेरै ठूलो बहावको पूर्वानुमान, सामान माथि सार्नुहोस् र जाने तयारी गर्नुहोस्"},
}

# When an upstream gauge has seen a surge or a blockage, the forecast wording is wrong: this is happening now.
SURGE_WORDS = {
    "en": "DANGER NOW: a flood surge is coming down the river. Go to high ground immediately",
    "ne": "अहिले खतरा: नदीमा बाढी आउँदैछ। तुरुन्तै अग्लो ठाउँमा जानुहोस्",
}

SYSTEM = """You are Baadhi Saathi (बाढी साथी), a flood friend for one household in Nepal.
Use the tools in this order: find_place, upstream_watch, river_outlook, rain_outlook, safe_places. Then write advice.
Rules:
- If upstream_watch reports a live alert, that comes first and nothing else matters: say to go to high ground NOW,
  name the safe place, and give the arrival window. Keep it to a few short lines.
- Always include the warning signs from upstream_watch (river suddenly dropping, roar, muddy water, fast rise)
  and that people should move up at once if they see one, without waiting for an SMS.
- Write for someone who reads slowly. Short sentences. No jargon, no numbers bigger than needed.
- Never make the risk sound smaller than the level the tools give. You may add caution, never remove it.
- Give concrete steps for today: documents and medicines in one bag, phone charged, where the high ground is,
  move animals and grain if the level is warning or danger, who to call.
- Say plainly that this reads river and rain forecasts only; it cannot see a landslide dam or glacier lake burst,
  so people must still follow DHM and ward office alerts.
- Language: write in the language asked for (ne = Nepali in Devanagari, en = English). In SMS mode, at most
  3 messages of 160 characters each.
"""


def make_tools() -> list:
    @tool
    def find_place(query: str) -> str:
        """Find a pilot place by name (English or Nepali) and return its river and coordinates.

        Args:
            query: A place name such as "Arughat", "Narayanghat" or "चतरा".
        """
        p = places.find(query)
        if not p:
            return json.dumps({"error": "unknown place", "known": places.listing()})
        return json.dumps({k: p[k] for k in ("key", "name", "name_ne", "lat", "lon", "river", "river_ne", "context")}, ensure_ascii=False)

    @tool
    def river_outlook(place: str, lat: float, lon: float) -> str:
        """Seven-day river flow forecast near a point and a risk level (calm, watch, warning, danger) computed from the river's own recent history.

        Args:
            place: Place name, for the record.
            lat: Latitude of the household.
            lon: Longitude of the household.
        """
        return json.dumps(rivers.summary(rivers.outlook(place, lat, lon)), ensure_ascii=False)

    @tool
    def rain_outlook(lat: float, lon: float) -> str:
        """Three-day rain forecast: millimetres per day and whether each day counts as heavy.

        Args:
            lat: Latitude.
            lon: Longitude.
        """
        return json.dumps(rain.outlook(lat, lon), ensure_ascii=False)

    @tool
    def safe_places(place_key: str) -> str:
        """Known higher ground or shelters for a pilot place, plus emergency numbers. These are examples the ward office must confirm.

        Args:
            place_key: The key returned by find_place, e.g. "arughat".
        """
        p = places.PLACES.get(place_key)
        if not p:
            return json.dumps({"error": "unknown place"})
        return json.dumps({"safe_places": p["safe_places"], "emergency": places.EMERGENCY,
                           "note": "Confirm with the ward office; routes may be cut when water rises."}, ensure_ascii=False)

    @tool
    def upstream_watch(place_key: str, lang: str = "en") -> str:
        """Sudden-flood check: live upstream gauge alerts (surge or river blockage) with arrival times, the known
        landslide-dam and glacial-lake sources above this place, and the warning signs people can see themselves.

        Args:
            place_key: The key returned by find_place, e.g. "arughat".
            lang: "ne" for Nepali warning signs, "en" for English.
        """
        if place_key not in places.PLACES:
            return json.dumps({"error": "unknown place"})
        return json.dumps(upstream.watch(place_key, lang if lang in ("ne", "en") else "en"), ensure_ascii=False)

    return [find_place, upstream_watch, river_outlook, rain_outlook, safe_places]


def worst(levels) -> str:
    """The most severe of the levels given; None and unknown values are ignored."""
    known = [l for l in levels if l in LEVELS]
    return max(known, key=LEVELS.index) if known else "calm"


LEVELS = rivers.LEVELS


def level_line(level: str, lang: str, surge: bool = False) -> str:
    if surge:
        return SURGE_WORDS.get(lang, SURGE_WORDS["en"])
    return LEVEL_WORDS.get(level, LEVEL_WORDS["calm"]).get(lang, LEVEL_WORDS["calm"]["en"])


def finish(model_text: str, level: str, lang: str, surge: bool = False) -> str:
    """The code's level line always comes first; the model's words follow."""
    head = level_line(level, lang, surge)
    body = model_text.strip()
    return head if not body else f"{head}\n\n{body}"


def build_agent(model=None) -> Agent:
    if model is None:
        from strands.models import BedrockModel
        model = BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.2, max_tokens=600)
    return Agent(model=model, tools=make_tools(), system_prompt=SYSTEM, callback_handler=None)


def dry_run(place: str, lang: str) -> dict:
    """Tool outputs only: what the model would have been shown."""
    p = places.find(place)
    if not p:
        return {"error": "unknown place", "known": places.listing()}
    up = upstream.watch(p["key"], lang)
    river = rivers.summary(rivers.outlook(p["name"], p["lat"], p["lon"]))
    level = worst([river["level"], up["level"]])
    return {"place": p["name"], "level": level, "upstream": up, "river": river, "rain": rain.outlook(p["lat"], p["lon"]),
            "safe": p["safe_places"], "emergency": places.EMERGENCY,
            "headline": level_line(level, lang, surge=bool(up["alerts"]))}


def advise(place: str, lang: str = "ne", sms: bool = False, agent: Agent | None = None) -> str:
    agent = agent or build_agent()
    ask = (f"Household in {place}. Language: {lang}. {'SMS mode.' if sms else ''} "
           "Check the river and rain, then give today's advice.")
    result = agent(ask)
    # the most severe level any tool computed, read back from the tool results in the conversation
    seen, surge = [], False
    for m in agent.messages:
        for c in m.get("content", []):
            tr = c.get("toolResult")
            if tr:
                for part in tr.get("content", []):
                    txt = part.get("text", "")
                    if '"level"' in txt:
                        try:
                            d = json.loads(txt)
                        except ValueError:
                            continue
                        seen.append(d.get("level"))
                        surge = surge or bool(d.get("alerts"))
    return finish(str(result), worst(seen), lang, surge)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("place")
    ap.add_argument("--lang", default="ne", choices=["ne", "en"])
    ap.add_argument("--sms", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="tool outputs only, no model, no AWS")
    a = ap.parse_args()
    if a.dry_run:
        print(json.dumps(dry_run(a.place, a.lang), ensure_ascii=False, indent=2))
        return
    print(advise(a.place, a.lang, a.sms))


if __name__ == "__main__":
    sys.exit(main())
