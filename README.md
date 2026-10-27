# Baadhi Saathi (बाढी साथी) — Flood Friend

A Strands agent that reads the river and rain forecast for one household in Nepal and says, in plain
Nepali or English, what to do today.

Nepal lost people and bridges to floods twice in late 2026: the Bhote Koshi glacier flood in August and
the Budhi Gandaki flash flood of 11 October. Official data exists: GloFAS river forecasts, rain forecasts,
DHM river gauges with warning and danger lines. It reaches experts and newsrooms. It does not reach a
family in Arughat as "move the grain upstairs tonight". That last step is what this agent does.

## What it does

```
python -m saathi.agent "Arughat" --lang ne          # advice in Nepali
python -m saathi.agent "Narayanghat" --lang en --sms # three short messages
python -m saathi.agent "Chatara" --dry-run           # the numbers only, no model, no AWS
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
The code stamps its own level line on top of the model's words (`finish()`), so a soothing paragraph can
never hide a danger. The model may add caution; it cannot remove it.

## Honest limits

- This reads **river and rain forecasts**. It sees monsoon river floods days ahead. It **cannot** see a
  landslide dam breaking or a glacial lake bursting; the 11 October flood would not have shown up here.
  For those, the agent's job is what to do once the official alert comes.
- Safe places are examples to be confirmed with the ward office. Routes can be cut when water rises.
- It supports DHM and ward alerts. It never replaces them.

## Run it

```
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q                      # no network, no AWS
AWS_PROFILE=personal .venv/bin/python -m saathi.agent "Arughat" --lang ne
```

Bedrock needs an AWS identity with `bedrock:InvokeModel` on Nova Lite in `BEDROCK_REGION` (default
us-east-1). A full answer costs well under one US cent.

## Status

Built for the AWS Builder Center hackathon *Strands SDK: Workshop to Ship* (28 Oct – 4 Nov 2026),
climate-resilience track. MIT licence.
