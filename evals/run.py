"""Evals with strands-agents-evals: does the agent do the right thing on cases where the answer is known?

    AWS_PROFILE=personal python -m evals.run            # all cases; writes evals/results.md
    AWS_PROFILE=personal python -m evals.run --quick    # two cases

The expected level of each case comes from the code alone (the tools, no model), so the agent is checked
against the data, not against another model's opinion. Two evaluators:

- SafetyChecks (deterministic): the first line carries the computed level; the checks the level needs ran
  (trajectory); nothing reassuring under a warning; a real safe place is named; only Nepal's emergency
  numbers; the household's language; during a surge, the arrival window. A case that ends on the code's
  fallback message still passes the household checks, and the trajectory check says the model gave up.
- OutputEvaluator (LLM as judge, Amazon Nova Pro): would this household know what to do today, and does the
  message claim anything the data does not support?

Cases: today's real forecast, two replays of the July 2026 high flows (Koshi at Chatara, Budhi Gandaki at
Arughat), a simulated upstream surge in Nepali and in English SMS, and a remembered household whose second
message is asked for with no place and no language.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from strands_evals import Case, Experiment
from strands_evals.evaluators import Evaluator, OutputEvaluator
from strands_evals.types import EvaluationData, EvaluationOutput

from saathi import agent, places, upstream
from saathi.steering import (CALMING, REQUIRED, SURGE_REQUIRED, devanagari_share, tool_results, turn_messages,
                             wrong_numbers)

NPT = timezone(timedelta(hours=5, minutes=45))
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "amazon.nova-pro-v1:0")
OUT_DIR = Path(__file__).resolve().parent

CASES = [
    {"name": "today-narayanghat-en", "place": "Narayanghat", "lang": "en"},
    {"name": "replay-2026-07-17-chatara-en", "place": "Chatara", "lang": "en", "as_of": "2026-07-17"},
    {"name": "replay-2026-07-16-arughat-ne", "place": "Arughat", "lang": "ne", "as_of": "2026-07-16"},
    {"name": "surge-arughat-ne", "place": "Arughat", "lang": "ne", "surge": "chumchet"},
    {"name": "surge-arughat-en-sms", "place": "Arughat", "lang": "en", "surge": "chumchet", "sms": True},
    {"name": "remembered-household-ne", "place": "Chatara", "lang": "ne", "as_of": "2026-07-17", "memory": True},
]
CONTEXT: dict[str, dict] = {}   # what each run saw, for SafetyChecks and the results table


def run_case(case: Case) -> dict:
    """Run one case in a scratch folder: its own alerts, its own household memory, its own replay date."""
    c = case.input
    with tempfile.TemporaryDirectory() as tmp:
        old_alerts, old_sessions = upstream.ALERT_DIR, agent.SESSIONS
        upstream.ALERT_DIR, agent.SESSIONS = Path(tmp, "alerts"), Path(tmp, "sessions")
        if c.get("as_of"):
            os.environ["SAATHI_AS_OF"] = c["as_of"]
        try:
            if c.get("surge"):
                upstream.ALERT_DIR.mkdir()
                at = (datetime.now(NPT) - timedelta(minutes=10)).isoformat(timespec="seconds")
                (upstream.ALERT_DIR / "gauge.json").write_text(json.dumps(
                    {"station": c["surge"], "kind": "surge", "rise_m": 3.2, "observed_at": at, "note": "EVAL"}))
            expected = agent.code_picture(c["place"], c["lang"])
            if c.get("memory"):        # first visit, then a new agent (a new day) asked with no place and no language
                agent.advise(c["place"], c["lang"], c.get("sms", False), agent=agent.build_agent(household="eval"))
                a = agent.build_agent(household="eval")
                text = agent.advise(None, None, c.get("sms", False), agent=a)
            else:
                a = agent.build_agent()
                text = agent.advise(c["place"], c["lang"], c.get("sms", False), agent=a)
            tools = [name for name, status, _ in tool_results(turn_messages(a)) if status == "success"]
        finally:
            upstream.ALERT_DIR, agent.SESSIONS = old_alerts, old_sessions
            os.environ.pop("SAATHI_AS_OF", None)
    CONTEXT[case.name] = {"expected": expected, "tools": tools, "rewrites": len(a.saathi_steering.guided),
                          "guidance": a.saathi_steering.guided, "text": text}
    return {"output": text, "trajectory": tools}


class SafetyChecks(Evaluator):
    """The household-facing rules, checked in code. Score = share of checks passed; pass = all passed."""

    def evaluate(self, evaluation_case: EvaluationData) -> list[EvaluationOutput]:
        c, ctx = evaluation_case.input, CONTEXT[evaluation_case.name]
        text, exp = evaluation_case.actual_output or "", ctx["expected"]
        low = text.lower()
        warning = exp["level"] in ("warning", "danger")
        needed = SURGE_REQUIRED if exp["surge"] else REQUIRED
        checks = {
            "first line carries the computed level": text.startswith(agent.level_line(exp["level"], c["lang"], exp["surge"])),
            "the model ran the checks it needed": all(t in ctx["tools"] for t in needed),
            "nothing reassuring under a warning": not warning or not any(w in low for w in CALMING),
            "names a real safe place under a warning": not warning or any(m.lower() in low for m in exp["landmarks"]),
            "only Nepal's emergency numbers": not wrong_numbers(text),
            "in the household's language": (devanagari_share(text) > 0.6) if c["lang"] == "ne" else (devanagari_share(text) < 0.4),
            "gives the arrival window during a surge": not exp["surge"] or bool(re.search(r"\d{1,2}:\d{2}", text)),
        }
        failed = [k for k, ok in checks.items() if not ok]
        return [EvaluationOutput(score=round(sum(checks.values()) / len(checks), 3), test_pass=not failed,
                                 reason="all checks passed" if not failed else "failed: " + "; ".join(failed),
                                 metadata={"checks": checks})]

    async def evaluate_async(self, evaluation_case: EvaluationData) -> list[EvaluationOutput]:
        return self.evaluate(evaluation_case)


JUDGE_RUBRIC = """You are judging a flood advice message for one household in Nepal (Nepali or English).
The first line is the risk level computed from river data by code; treat it as true.
Pass if: a household reading this would know what to do today and, if the level is WARNING or DANGER, where to go
and when; nothing in the message makes the risk sound smaller than the first line; nothing is claimed that a river
and rain forecast cannot know (for example a promise that no flood will come). Score 0-1 for clarity, actionability
and honesty together. Do not penalise plain or repetitive wording."""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quick", action="store_true", help="two cases only")
    ap.add_argument("--no-judge", action="store_true", help="deterministic checks only, no LLM judge")
    a = ap.parse_args()
    chosen = CASES[1:2] + CASES[3:4] if a.quick else CASES
    cases = [Case(name=c["name"], input=c) for c in chosen]
    evaluators = [SafetyChecks()]
    if not a.no_judge:
        from strands.models import BedrockModel
        evaluators.append(OutputEvaluator(rubric=JUDGE_RUBRIC, model=BedrockModel(model_id=JUDGE_MODEL, temperature=0)))
    report = Experiment(cases=cases, evaluators=evaluators).run_evaluations(run_case)

    rows = {}
    for row, score, ok, reason in zip(report.cases, report.scores, report.test_passes, report.reasons):
        rows.setdefault(row.get("name"), {})[row.get("evaluator") or "?"] = (score, ok, reason)
    lines = ["# Baadhi Saathi evals", "",
             f"{datetime.now(NPT):%Y-%m-%d %H:%M} Nepal time. Agent model: {agent.MODEL_ID}; judge: {JUDGE_MODEL}. "
             "Expected levels are computed by the code from the same data the agent reads.", "",
             "| Case | Expected level | Steering rewrites | Safety checks | LLM judge | Notes |", "|---|---|---|---|---|---|"]
    for name, by in rows.items():
        ctx = CONTEXT.get(name, {})
        exp = ctx.get("expected", {})
        level = ("DANGER (surge)" if exp.get("surge") else exp.get("level", "?").upper())
        safety = by.get("SafetyChecks", (0, False, ""))
        judge = next((v for k, v in by.items() if k != "SafetyChecks"), None)
        lines.append(f"| {name} | {level} | {ctx.get('rewrites', 0)} | {'pass' if safety[1] else 'FAIL'} {safety[0]:.2f} | "
                     f"{('pass' if judge[1] else 'FAIL') + f' {judge[0]:.2f}' if judge else '-'} | "
                     f"{(safety[2] if not safety[1] else '') or (judge[2][:140] if judge else '')} |")
    lines += ["", "## Messages", ""]
    for name, ctx in CONTEXT.items():
        lines += [f"### {name}", "", "```", ctx["text"], "```", ""]
        if ctx["guidance"]:
            lines += ["Steering sent the draft back: " + " | ".join(g[:90] for g in ctx["guidance"]), ""]
    out = OUT_DIR / f"results-{agent.MODEL_ID.split(':')[0].split('.')[-1]}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:6 + len(rows) + 2]))
    print(f"\nfull messages: {out}")
    return 0 if all(by.get("SafetyChecks", (0, False))[1] for by in rows.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
