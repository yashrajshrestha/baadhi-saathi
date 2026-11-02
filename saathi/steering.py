"""Steering: the safety rules live in code and run inside the Strands agent loop.

Three rules, all deterministic (no second model call):

1. Look before you speak. Every place-specific tool needs the place from find_place first; called
   too early it is cancelled with a hint (steer_before_tool -> Guide). And the agent may not answer
   until find_place, upstream_watch, river_outlook, rain_outlook and safe_places have all succeeded
   in this turn: a draft that comes too early is dropped and the model is told what is missing
   (steer_after_model -> Guide).
2. In the household's language. A draft mostly in the wrong script (English for a Nepali reader, or
   the reverse) is sent back: a warning nobody can read is no warning.
3. Never calmer than the data. When the tools say warning or danger, or an upstream surge is live,
   a draft that reassures ("don't worry", "खतरा छैन") or does not say where to go is dropped and the
   model is told to rewrite it. During a surge the draft must also say to go now.

`finish()` in agent.py still stamps the code's level line on top of the final answer; steering makes
the words under it agree. After MAX_RETRIES rewrites in one turn the draft is accepted, so a stubborn
model cannot loop forever, and the headline still carries the level.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry
from strands.vended_plugins.steering import Guide, Proceed, SteeringHandler

from .places import EMERGENCY
from .rivers import LEVELS

EMERGENCY_NUMBERS = set(EMERGENCY.values())

REQUIRED = ("find_place", "upstream_watch", "river_outlook", "rain_outlook", "safe_places")
SURGE_REQUIRED = ("find_place", "upstream_watch", "safe_places")   # water is coming: rain no longer matters
NEEDS_PLACE = REQUIRED[1:]
MAX_RETRIES = 2

# Reassurance that must not appear under a warning or danger. Lower-case; Nepali as written.
CALMING = (
    "no danger", "no risk", "no flood", "nothing to worry", "don't worry", "do not worry",
    "no need to worry", "safe to stay", "no need to move", "no action needed",
    "चिन्ता नगर्नुहोस्", "खतरा छैन", "जोखिम छैन", "बाढी आउँदैन", "डराउनु पर्दैन",
)
GO_WORDS = ("high ground", "higher ground", "upper floor", "अग्लो", "माथिल्लो", "उच्च", "सुरक्षित ठाउँ")
NOW_WORDS = ("now", "immediately", "at once", "अहिले", "तुरुन्त", "यसै क्षण", "यही बेला", "छिटो")


def turn_messages(agent) -> list[dict]:
    """This request's messages only. With session memory, earlier days are in agent.messages too, and the
    conversation manager trims old messages mid-turn, so the turn is found by the marker in its request
    (agent.state "turn_marker"), not by a position."""
    marker = agent.state.get("turn_marker")
    if marker:
        for i in range(len(agent.messages) - 1, -1, -1):
            m = agent.messages[i]
            if m.get("role") == "user" and any(marker in c.get("text", "") for c in m.get("content", [])):
                return agent.messages[i:]
    return agent.messages[agent.state.get("turn_start") or 0:]


def missing_checks(seen: dict) -> list[str]:
    """Checks not yet run this turn; during a live surge only place, upstream and safe places are needed."""
    return [t for t in (SURGE_REQUIRED if seen["surge"] else REQUIRED) if t not in seen["ok"]]


def tool_results(messages: list[dict]) -> list[tuple[str, str, Any]]:
    """(tool name, status, parsed JSON result or None) for every tool result in these messages."""
    names, out = {}, []
    for m in messages:
        for c in m.get("content", []):
            if "toolUse" in c:
                names[c["toolUse"].get("toolUseId")] = c["toolUse"].get("name")
            tr = c.get("toolResult")
            if tr:
                text = "".join(p.get("text", "") for p in tr.get("content", []))
                try:
                    data = json.loads(text)
                except ValueError:
                    data = None
                out.append((names.get(tr.get("toolUseId"), "?"), tr.get("status", "success"), data))
    return out


def picture(messages: list[dict]) -> dict:
    """What the tools said in these messages: which succeeded, the worst level, live alerts, safe places."""
    ok, levels, alerts, safe, safe_ne, landmarks = set(), [], [], [], [], []
    for name, status, data in tool_results(messages):
        if status != "success" or not isinstance(data, dict) or "error" in data:
            continue
        ok.add(name)
        if data.get("level") in LEVELS:
            levels.append(data["level"])
        alerts += data.get("alerts", [])
        safe += data.get("safe_places", [])
        safe_ne += data.get("safe_places_ne", [])
        landmarks += data.get("landmarks", [])
    surge = bool(alerts)
    level = "danger" if surge else max(levels, key=LEVELS.index) if levels else "calm"
    return {"ok": ok, "level": level, "surge": surge, "alerts": alerts, "safe": safe + safe_ne,
            "safe_en": safe, "safe_ne": safe_ne, "landmarks": landmarks}


def text_of(message: dict) -> str:
    return "\n".join(c.get("text", "") for c in message.get("content", []) if "text" in c)


def devanagari_share(text: str) -> float:
    """Share of letters that are Devanagari (Nepali script); 0.0 for text without letters."""
    letters = [c for c in text if c.isalpha()]
    return sum("ऀ" <= c <= "ॿ" for c in letters) / len(letters) if letters else 0.0


def wrong_numbers(draft: str) -> list[str]:
    """Phone numbers in the draft that are not Nepal's emergency numbers (a model once wrote 112)."""
    ascii_digits = draft.translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    found = re.findall(r"(?:call|dial|phone|number|फोन|डायल|नम्बर)\D{0,20}?(\d{3,5})\b", ascii_digits, flags=re.I)
    found += re.findall(r"\b(\d{3,5})\s*(?:मा फोन|मा डायल)", ascii_digits)
    return [n for n in found if n not in EMERGENCY_NUMBERS]


def problem(draft: str, seen: dict, lang: str | None = None) -> str | None:
    """Why this draft may not go to the household, or None if it may."""
    missing = missing_checks(seen)
    if missing:
        return ("Do not answer yet. Before advising this household you must call: " + ", ".join(missing)
                + ". Call them, then write the advice.")
    bad = wrong_numbers(draft)
    if bad:
        return (f"{bad[0]} is not a Nepal emergency number. Use only the numbers from safe_places: "
                "1149 (NEOC, disaster), 100 (police), 102 (ambulance).")
    if lang == "ne" and devanagari_share(draft) < 0.6:
        return ("This household reads Nepali. Rewrite the whole advice in Nepali (Devanagari script), "
                "short sentences, using safe_places_ne for the safe places.")
    if lang == "en" and devanagari_share(draft) > 0.4:
        return "This household asked for English. Rewrite the whole advice in English."
    if seen["level"] in ("warning", "danger"):
        low = draft.lower()
        calm = next((w for w in CALMING if w in low), None)
        if calm:
            return (f"The tools say {seen['level'].upper()}. Your draft says \"{calm}\", which makes the risk sound "
                    "smaller than it is. Rewrite it without reassurance: say what is coming and what to do today.")
        marks = [m.lower() for m in seen.get("landmarks", [])]
        named = any(m in low for m in marks) if marks else any(w in low for w in GO_WORDS)
        if not named:
            return ("The level is " + seen["level"].upper() + ". Say exactly where to go: name one of the safe places "
                    "from safe_places (safe_places_ne in Nepali), not just 'high ground'.")
        if seen["surge"] and not any(w in low for w in NOW_WORDS):
            return ("A surge is coming down the river right now. Tell them to go to high ground immediately, "
                    "give the arrival window, and keep it to a few short lines.")
    return None


class FloodSafetyHandler(SteeringHandler):
    """Gates tools on the place and gates the final answer on the full check and the computed level."""

    name = "flood-safety"

    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        self.retries: dict[tuple, int] = {}
        self.guided: list[str] = []          # every guidance given, for --show-steps and the evals
        self.verbose = verbose

    def _guide(self, reason: str) -> Guide:
        self.guided.append(reason)
        if self.verbose:
            print(f"  !! steering: {reason}", file=sys.stderr, flush=True)
        return Guide(reason=reason)

    async def steer_before_tool(self, *, agent, tool_use, **kwargs: Any):
        name = tool_use.get("name")
        if name in NEEDS_PLACE and "find_place" not in picture(turn_messages(agent))["ok"]:
            return self._guide("Call find_place first: the other tools need the place key and coordinates it returns.")
        lang = agent.state.get("lang")
        if name == "upstream_watch" and lang and (tool_use.get("input") or {}).get("lang", "en") != lang:
            # the warning signs are written by people in both languages; fetch them, do not translate them
            return self._guide(f"Call upstream_watch with lang=\"{lang}\": the warning signs exist in that language "
                               "already, so copy them instead of translating.")
        return Proceed(reason="place known")

    async def steer_after_model(self, *, agent, message, stop_reason, **kwargs: Any):
        if stop_reason != "end_turn":
            return Proceed(reason="not a final answer")
        reason = problem(text_of(message), picture(turn_messages(agent)), agent.state.get("lang"))
        if not reason:
            return Proceed(reason="advice matches the checks")
        key = (id(agent), agent.state.get("turn_marker") or agent.state.get("turn_start"))
        if self.retries.get(key, 0) >= MAX_RETRIES:
            return Proceed(reason="rewrite budget spent; finish() still stamps the level line")
        self.retries[key] = self.retries.get(key, 0) + 1
        return self._guide(reason)


class ToolBudget(HookProvider):
    """A runaway-loop guard (the workshop's Module 2 rate limiter, for this agent). A model once called
    find_place twelve times in a row with a name it had copied wrong. Past SOFT tool calls in one turn,
    each further call is cancelled with a hint to answer; past HARD, the run is cancelled and advise()
    falls back to the code's own message."""

    SOFT, HARD = 14, 22

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.stopped = False

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.before)

    def before(self, event: BeforeToolCallEvent) -> None:
        calls = sum(1 for m in turn_messages(event.agent) for c in m.get("content", []) if "toolUse" in c)
        if calls > self.HARD:
            self.stopped = True
            event.cancel_tool = "Tool budget spent."
            event.agent.cancel(after_current_tools=True)
            if self.verbose:
                print(f"  !! tool budget: {calls} calls this turn, run stopped; the code answers", file=sys.stderr, flush=True)
        elif calls > self.SOFT:
            event.cancel_tool = ("Too many tool calls this turn. Stop calling tools and write the advice now "
                                 "with the results you already have.")
