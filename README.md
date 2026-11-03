# Baadhi Saathi (बाढी साथी) — Flood Friend

A Strands agent that reads the river and rain forecast for one household in Nepal and says, in plain
Nepali or English, what to do today.

Nepal lost people and bridges to floods twice in late 2026: the Bhote Koshi glacier flood in August and
the Budhi Gandaki flash flood of 11 October. Official data exists: GloFAS river forecasts, rain forecasts,
DHM river gauges with warning and danger lines. It reaches experts and newsrooms. It does not reach a
family in Arughat as "move the grain upstairs tonight". That last step is what this agent does.

## What it does

```
python -m saathi.agent "Arughat" --lang ne           # advice in Nepali
python -m saathi.agent "Narayanghat" --lang en --sms  # three short messages
python -m saathi.agent "Chatara" --dry-run            # the numbers only, no model, no AWS
python -m saathi.push --no-send                       # today's SMS for every subscribed phone
```

1. `find_place` — which river matters for this household (three pilot places for now).
2. `river_outlook` — seven-day river flow from the free Open-Meteo Flood API (GloFAS). The code finds
   the river cell (the nearest grid cell is usually a side-stream), compares the coming peak with the
   river's own last 90 days, and sets a level: **calm, watch, warning, danger**. The thresholds are
   simple multiples, written down in `saathi/rivers.py`, so a ward officer can read them.
3. `rain_outlook` — three-day rain totals, with 60 mm and 120 mm per day as the heavy lines.
4. `safe_places` — higher ground and shelters for the pilot place, plus 1149 (NEOC), 100, 102.
5. `upstream_watch` — the sudden floods no forecast can see. Each pilot place lists its known
   landslide-dam and glacial-lake sources upstream, and the warning signs anyone can see
   (river suddenly dropping, a roar, muddy water, a fast rise). When an upstream gauge reports a
   surge, the place goes straight to **danger** with an arrival window (distance ÷ 10–30 km/h).

### Upstream gauges and AWS IoT

A real gauge near a landslide dam or glacial lake would publish one small MQTT message to AWS IoT Core:

```
gauge ──MQTT saathi/surge/<station>──► AWS IoT Core ──IoT Rule──► Lambda ──► agent ──► SMS per ward
{"station": "chumchet", "kind": "surge", "observed_at": "2026-10-11T04:00:00+05:45", "rise_m": 3.2}
```

The simulator sends the same message to a local folder, so the whole chain runs on a laptop:

```
python -m saathi.simulate surge chumchet --rise 3.2      # a surge passes the Chumchet gauge
python -m saathi.agent "Arughat" --dry-run               # Arughat is now DANGER, arriving 06:00–10:00
python -m saathi.simulate clear
```

Then Amazon Bedrock (Nova Lite) writes the advice: short sentences, today's steps, in the language asked.

## Safety lives in code, not in the prompt

A prompt asks; code decides. Four layers, each from a Strands feature taught in the *Workshop to Ship*
workshop, applied to a flood:

| Layer | Strands feature | What it enforces |
|---|---|---|
| `FloodSafetyHandler` (`saathi/steering.py`) | steering handler (`steer_before_tool`, `steer_after_model`) | no tool before the place is known; warning signs fetched in the household's language, not translated; no answer until every check has run; a draft in the wrong script, with reassurance under a warning, without a named safe place, with a wrong emergency number, without "go now" in a surge, or sending people towards an upstream flood source is sent back to be rewritten (at most twice) |
| `ToolBudget` | hook (`BeforeToolCallEvent`) | a runaway tool loop is cut off: past 14 calls in a turn tools are refused, past 22 the run is cancelled |
| `finish()` + `action_block()` | plain code after the loop | the level line is the code's, on top; under warning or danger, *where to go, when the water comes and who to call* are written by the code from the tools' data; if the model still fails the checks, or errors, its words are dropped and the household gets the code's message |
| `--household` | `FileSessionManager` | remembers each household's place, language and last level, so tomorrow's message needs no setup; the code writes how today compares |

Why so strict: in testing, Nova Lite once named a **bridge** as a safe place during a surge, gave **112**
(not a Nepal number), answered a Nepali household in English, and skipped the rain check. Every one of
those is now caught by a rule in code, and there is a test for each.

```
python -m saathi.agent "Arughat" --lang ne --show-steps          # watch the tools and any steering
python -m saathi.agent "Chatara" --household "Gita" --lang ne    # first visit
python -m saathi.agent --household "Gita"                        # next day: no place, no language needed
python -m saathi.agent "Chatara" --as-of 2026-07-17 --lang en    # replay a past day from recorded data
```

`--as-of` replays a past day with the river and rain **recorded since**, not the forecast issued that
morning, so it shows what the rules would have said, with hindsight. On 17 July 2026, three days before the
Koshi at Chatara peaked at about 6,000 m³/s (four times its usual flow), the level was **WARNING**.

## Evals

`evals/run.py` uses **strands-agents-evals**. Each case's expected level is computed by the code from the
same data (no model), then two evaluators score the agent's message: `SafetyChecks` (deterministic: level
line, required checks ran, no reassurance under a warning, a real safe place named, only Nepal's emergency
numbers, the household's language, the arrival window in a surge) and an `OutputEvaluator` judge (Amazon
Nova Pro: would this household know what to do, and is anything claimed that the data cannot support?).

```
AWS_PROFILE=personal python -m evals.run          # 6 cases; results in evals/results-<model>.md
```

## Honest limits

- This reads **river and rain forecasts**. It sees monsoon river floods days ahead. It **cannot** see a
  landslide dam breaking or a glacial lake bursting; the 11 October flood would not have shown up here.
  For those, the agent's job is what to do once the official alert comes.
- Safe places are examples to be confirmed with the ward office. Routes can be cut when water rises.
- Three pilot places. The river levels compare the coming peak with the river's own last 90 days; they
  are not DHM's warning and danger lines (DHM's gauges are not reachable from outside Nepal).
- Nova Lite's Nepali is understandable but not polished; it sometimes slips into Hindi words, which the
  code replaces where it knows them. The emergency lines are always the code's own Nepali.
- It supports DHM and ward alerts. It never replaces them.

## Run it

```
python3 -m venv .venv && .venv/bin/pip install -e ".[dev,evals]"
.venv/bin/pytest -q                      # 41 tests, no network, no AWS
AWS_PROFILE=personal .venv/bin/python -m saathi.agent "Arughat" --lang ne
```

Bedrock needs an AWS identity with `bedrock:InvokeModel` on Nova Lite in `BEDROCK_REGION` (default
us-east-1). A full answer costs well under one US cent.

## Status

Built for the AWS Builder Center hackathon *Strands SDK: Workshop to Ship* (28 Oct – 4 Nov 2026),
climate-resilience track. MIT licence.
