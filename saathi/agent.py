"""The Strands agent: five tools, Bedrock Nova Lite for the words, and a risk level the model cannot lower.

    python -m saathi.agent "Arughat" [--lang ne|en] [--sms] [--household ID] [--as-of YYYY-MM-DD] [--dry-run]

Flow: the agent looks up the place, checks upstream alerts, calls river_outlook and rain_outlook
(numbers and a risk level computed in code), fetches safe places and emergency numbers, then writes
advice for one household in plain Nepali or English.

Three layers keep it honest:
- steering (saathi/steering.py): no answer before every check has run, and a draft that sounds calmer
  than the computed level, or does not say where to go, is sent back to be rewritten;
- `finish()`: the code's own level line is stamped on top of whatever the model wrote;
- `--dry-run`: the tool outputs alone, no model and no AWS login.

--household keeps one household's place, language and past days between runs (FileSessionManager);
--as-of replays a past day from recorded data.

Environment: AWS_PROFILE (e.g. personal) and BEDROCK_REGION (default us-east-1) for Bedrock;
MODEL_ID to change the model (default amazon.nova-lite-v1:0); SAATHI_SESSIONS for the memory folder.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from strands import Agent, tool
from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent, HookProvider, HookRegistry

from datetime import date, datetime
from pathlib import Path

from . import places, rain, rivers, upstream
from .steering import REQUIRED, FloodSafetyHandler, ToolBudget, missing_checks, picture, problem, turn_messages

MODEL_ID = os.environ.get("MODEL_ID", "amazon.nova-lite-v1:0")
REGION = os.environ.get("BEDROCK_REGION", "us-east-1")
SESSIONS = Path(os.environ.get("SAATHI_SESSIONS", "sessions"))   # one folder per remembered household

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

HINDI_TO_NEPALI = {
    "आपका": "तपाईंको", "आपकी": "तपाईंको", "आपके": "तपाईंका", "आपको": "तपाईंलाई", "आप ": "तपाईं ",
    "सिर्फ़": "मात्र", "सिर्फ": "मात्र", "औषधियाँ": "औषधिहरू", "बैग": "झोला",
    "अगला ": "आउने ", "अगले ": "आउने ", "दस्तावेज़": "कागजात", "धुँधला": "धमिलो",
}

# Under a warning, danger or surge, where to go, when the water comes and who to call are written by the
# code from the tools' data, never by the model: a model once named a bridge as a safe place, and 112.
ACTION_WORDS = {
    "en": {"go": "Where to go: {places}.", "when": "The water may reach you between {a} and {b}.",
           "take": "Take documents, medicines and your phone. Move animals and grain up.",
           "call": "Emergency: 1149 (NEOC), 100 (police), 102 (ambulance).", "or": " or "},
    "ne": {"go": "कहाँ जाने: {places}।", "when": "पानी {a} देखि {b} बीच आइपुग्न सक्छ।",
           "take": "कागजात, औषधि र फोन लिनुहोस्। पशु र अन्न माथि सार्नुहोस्।",
           "call": "आपतकालीन फोन: 1149 (NEOC), 100 (प्रहरी), 102 (एम्बुलेन्स)।", "or": " वा "},
}


def action_block(seen: dict, lang: str) -> str:
    """The code's own where-to-go / when / who-to-call lines; empty when the level is calm or watch."""
    if seen["level"] not in ("warning", "danger"):
        return ""
    w = ACTION_WORDS.get(lang, ACTION_WORDS["en"])
    names = seen["safe_ne"] if lang == "ne" and seen["safe_ne"] else seen["safe_en"]
    lines = [w["go"].format(places=w["or"].join(names))] if names else []
    for alert in seen["alerts"]:
        if alert.get("arrives_between"):
            lines.append(w["when"].format(a=alert["arrives_between"][0], b=alert["arrives_between"][1]))
            break
    return "\n".join(lines + [w["take"], w["call"]])

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
- For Nepali, use Nepali forms, not Hindi: "तपाईंको" not "आपका", "सुझाव" not "सलाह", "हुनुहुन्छ" not "हैं",
  "अग्लो" not "ऊँचा", "धमिलो" not "धुँधला", "कागजात" not "दस्तावेज़". Call upstream_watch with the household's
  lang and copy its warning signs as written; name the safe places from safe_places_ne as written.
- If earlier days for this household are in the conversation, check again anyway (rivers change), then say
  in one line how today compares with last time, for example "higher than yesterday".
- If river_outlook notes a REPLAY, say once that this is a replay of a past day, not today's forecast.
"""


class StepPrinter(HookProvider):
    """Prints each tool call to stderr so a viewer can watch the agent work."""

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.before)
        registry.add_callback(AfterToolCallEvent, self.after)

    def before(self, event: BeforeToolCallEvent) -> None:
        args = json.dumps(event.tool_use.get("input", {}), ensure_ascii=False)
        print(f"  -> {event.tool_use['name']}({args})", file=sys.stderr, flush=True)

    def after(self, event: AfterToolCallEvent) -> None:
        text = "".join(p.get("text", "") for p in event.result.get("content", []))
        note = ""
        try:
            d = json.loads(text)
            if d.get("level"):
                note = f" level={d['level']}"
            if d.get("alerts"):
                note += f" alerts={len(d['alerts'])}"
        except ValueError:
            pass
        print(f"  <- {event.tool_use['name']} done{note}", file=sys.stderr, flush=True)


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
        return json.dumps(rivers.summary(rivers.outlook(place, lat, lon, as_of=as_of())), ensure_ascii=False)

    @tool
    def rain_outlook(lat: float, lon: float) -> str:
        """Three-day rain forecast: millimetres per day and whether each day counts as heavy.

        Args:
            lat: Latitude.
            lon: Longitude.
        """
        return json.dumps(rain.outlook(lat, lon, as_of=as_of()), ensure_ascii=False)

    @tool
    def safe_places(place_key: str) -> str:
        """Known higher ground or shelters for a pilot place, plus emergency numbers. These are examples the ward office must confirm.

        Args:
            place_key: The key returned by find_place, e.g. "arughat".
        """
        p = places.PLACES.get(place_key)
        if not p:
            return json.dumps({"error": "unknown place"})
        return json.dumps({"safe_places": p["safe_places"], "safe_places_ne": p.get("safe_places_ne", []),
                           "landmarks": p.get("landmarks", []),
                           "emergency": places.EMERGENCY,
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


def finish(model_text: str, level: str, lang: str, surge: bool = False, action: str = "") -> str:
    """The code's level line always comes first, then the code's action block (warning and above), then
    the model's words."""
    head = level_line(level, lang, surge)
    if action:
        head = f"{head}\n{action}"
    # Nova sometimes emits its scratchpad in <thinking> tags; a household should never see it.
    body = re.sub(r"<thinking>.*?</thinking>", "", model_text, flags=re.DOTALL)
    body = re.sub(r"</?[A-Za-z_]+>", "", body)  # stray <message> style tags Nova sometimes wraps output in
    body = body.replace("**", "").strip()  # markdown bold means nothing on a phone screen
    body = re.sub(r"(?i)\b(SMS|message|सन्देश)\s*\d\s*/\s*\d\s*:?\s*", "", body)  # "SMS 1/3:" labels, anywhere
    if lang == "ne":
        # Nova Lite drifts into Hindi pronouns about half the time; enforce Nepali in code, like the level.
        for hindi, nepali in HINDI_TO_NEPALI.items():
            body = body.replace(hindi, nepali)
    # Nova sometimes repeats a paragraph word for word; on a phone that is a wasted SMS.
    paragraphs = list(dict.fromkeys(p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()))
    body = "\n\n".join(paragraphs)
    return head if not body else f"{head}\n\n{body}"


def as_of() -> str | None:
    """Replay date (YYYY-MM-DD) from SAATHI_AS_OF, read at call time; None means today's forecast."""
    return os.environ.get("SAATHI_AS_OF") or None


def household_id(name: str) -> str:
    return "household-" + (re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "default")


def build_agent(model=None, show_steps: bool = False, household: str | None = None) -> Agent:
    """The agent with its safety steering. With `household`, a FileSessionManager keeps that household's
    conversation and state (place, language) across runs, so tomorrow's message needs no setup."""
    if model is None:
        from strands.models import BedrockModel
        model = BedrockModel(model_id=MODEL_ID, region_name=REGION, temperature=0.2, max_tokens=1500)   # Devanagari costs many more tokens than English
    hooks = [StepPrinter()] if show_steps else []
    session = None
    if household:
        from strands.session.file_session_manager import FileSessionManager
        session = FileSessionManager(session_id=household_id(household), storage_dir=str(SESSIONS))
    steering, budget = FloodSafetyHandler(verbose=show_steps), ToolBudget(verbose=show_steps)
    agent = Agent(model=model, tools=make_tools(), system_prompt=SYSTEM, callback_handler=None, hooks=hooks + [budget],
                  plugins=[steering], session_manager=session)
    agent.saathi_session, agent.saathi_steering, agent.saathi_budget = session, steering, budget
    return agent


def dry_run(place: str, lang: str) -> dict:
    """Tool outputs only: what the model would have been shown."""
    p = places.find(place)
    if not p:
        return {"error": "unknown place", "known": places.listing()}
    up = upstream.watch(p["key"], lang)
    river = rivers.summary(rivers.outlook(p["name"], p["lat"], p["lon"], as_of=as_of()))
    level = worst([river["level"], up["level"]])
    return {"place": p["name"], "level": level, "upstream": up, "river": river,
            "rain": rain.outlook(p["lat"], p["lon"], as_of=as_of()),
            "safe": p["safe_places"], "emergency": places.EMERGENCY,
            "headline": level_line(level, lang, surge=bool(up["alerts"]))}


def advise(place: str | None = None, lang: str | None = None, sms: bool = False, agent: Agent | None = None,
           show_steps: bool = False, household: str | None = None) -> str:
    """One turn of advice. Place and language may be left out for a household the agent has met before."""
    agent = agent or build_agent(show_steps=show_steps, household=household)
    place = place or agent.state.get("place")
    lang = lang or agent.state.get("lang") or "ne"
    if not place:
        raise ValueError("no place given and none remembered for this household")
    agent.state.set("place", place)
    agent.state.set("lang", lang)
    marker = f"[check {datetime.now().isoformat(timespec='seconds')}]"
    agent.state.set("turn_marker", marker)   # steering and the level read this turn only (see turn_messages)
    sms_rule = ("SMS mode: three short messages, no labels like 'SMS 1/3'. No dates, no m3/s, no coordinates; "
                "say 'normal', 'higher than usual', 'very high' instead. " if sms else "")
    last = agent.state.get("last")
    memory = (f"Last check for this household: {last['date']}, level {last['level']}. Say in one line how today "
              "compares. " if last else "")
    ask = (f"{marker} Household in {place}. Language: {lang}. {sms_rule}{memory}"
           "Check the river and rain, then give today's advice.")
    try:
        body = str(agent(ask))
    except Exception as e:   # any model or loop failure: the household still gets the code's message
        print(f"  !! model failed ({type(e).__name__}); the code answers", file=sys.stderr, flush=True)
        body = ""
    seen = picture(turn_messages(agent))   # the most severe level any tool computed in this turn
    if not body or missing_checks(seen):
        # the model stopped before finishing its checks: the code checks, and the model's words are not sent
        seen, body = code_picture(place, lang), ""
    elif problem(body, seen, lang):
        body = ""   # still failing after the rewrites steering allowed: send the code's message only
    agent.state.set("last", {"date": as_of() or date.today().isoformat(), "level": seen["level"]})
    if getattr(agent, "saathi_session", None):
        agent.saathi_session.sync_agent(agent)   # state set after the last message is not saved otherwise
    return finish(body, seen["level"], lang, seen["surge"], action_block(seen, lang))


def code_picture(place: str, lang: str) -> dict:
    """The same picture steering builds, computed by the code alone (no model)."""
    p = places.find(place)
    up = upstream.watch(p["key"], lang)
    river = rivers.summary(rivers.outlook(p["name"], p["lat"], p["lon"], as_of=as_of()))
    return {"ok": set(REQUIRED), "level": "danger" if up["alerts"] else river["level"], "surge": bool(up["alerts"]),
            "alerts": up["alerts"], "safe": p["safe_places"] + p.get("safe_places_ne", []),
            "safe_en": p["safe_places"], "safe_ne": p.get("safe_places_ne", []), "landmarks": p.get("landmarks", [])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("place", nargs="?", help="pilot place; may be left out with --household after the first run")
    ap.add_argument("--lang", choices=["ne", "en"], help="default: the household's last language, else ne")
    ap.add_argument("--sms", action="store_true")
    ap.add_argument("--household", help="remember this household (place, language, past days) between runs")
    ap.add_argument("--as-of", help="replay a past day, YYYY-MM-DD, with recorded river and rain data")
    ap.add_argument("--dry-run", action="store_true", help="tool outputs only, no model, no AWS")
    ap.add_argument("--show-steps", action="store_true", help="print each tool call to stderr as it happens")
    a = ap.parse_args()
    if a.as_of:
        os.environ["SAATHI_AS_OF"] = a.as_of
    if a.dry_run:
        if not a.place:
            ap.error("--dry-run needs a place")
        print(json.dumps(dry_run(a.place, a.lang or "ne"), ensure_ascii=False, indent=2))
        return
    if not a.place and not a.household:
        ap.error("give a place, or --household for a household seen before")
    print(advise(a.place, a.lang, a.sms, show_steps=a.show_steps, household=a.household))


if __name__ == "__main__":
    sys.exit(main())
