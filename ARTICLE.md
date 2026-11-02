# Baadhi Saathi (बाढी साथी) — A Flood Advice Agent for Nepal

## The Problem

Nepal loses lives to floods every monsoon. In late 2024, the Bhote Koshi glacier flood and Budhi Gandaki flash flood killed hundreds and destroyed bridges. Official forecasts from GloFAS and DHM exist — they reach experts and newsrooms. They do not reach a family in Arughat as "move the grain upstairs tonight."

River forecasts are numbers: cubic meters per second, return periods, probability thresholds. A farmer in Gorkha district does not read hydrographs. They need three lines in Nepali telling them what to do today.

That last-mile step — turning forecast data into household advice — is what Baadhi Saathi does.

## What Baadhi Saathi Does

Baadhi Saathi ("Flood Friend" in Nepali) is a Strands SDK agent that reads river and rain forecasts for one household in Nepal and says, in plain Nepali or English, what to do today.

The agent runs five tools in sequence:

1. **find_place** — identifies which river matters for the household (three pilot places: Arughat, Narayanghat, Chatara).
2. **river_outlook** — fetches the seven-day river flow from the free Open-Meteo Flood API (GloFAS data). Compares the coming peak against the river's recent 90-day flow and sets a level: calm, watch, warning, or danger.
3. **rain_outlook** — pulls three-day rain totals, flagging anything above 60mm/day as heavy.
4. **upstream_watch** — checks for sudden floods that no forecast can see: landslide dams, glacial lake outbursts, upstream gauge surges. Each pilot place has its known threat sources listed.
5. **safe_places** — returns higher ground, shelters, and emergency numbers (1149 NEOC, 100 Police, 102 Ambulance).

The agent then writes advice: short sentences, no jargon, concrete steps for today. The risk level is stamped by code, not the model — so a soothing paragraph can never hide a "danger" warning.

## How It's Built with Strands SDK

Baadhi Saathi uses these Strands SDK features from the workshop:

**Tools (`@tool` decorator)** — Each data source is a plain Python function decorated with `@tool`. The LLM reads the docstrings to decide when to call them. No manual routing needed.

```python
from strands import Agent, tool

@tool
def river_outlook(place_key: str) -> str:
    """Seven-day river flow forecast for the place."""
    # Fetches GloFAS data, computes risk level in code
    ...
```

**System prompt with strict rules** — The agent has guardrails baked into the system prompt: it must call tools in order, never downplay risk, and always include upstream warning signs and safe places.

**Risk level enforcement** — The risk level (calm/watch/warning/danger) is computed deterministically in Python, not by the LLM. A `finish()` function stamps the code's level on top of whatever the model writes. This is the same principle as Module 3's steering handlers — deterministic control over the agent's output.

**Model-agnostic design** — Defaults to Amazon Nova Lite on Bedrock (cheap, fast), but works with any model Strands supports. A `--dry-run` flag skips the model entirely and outputs raw tool data, costing nothing.

## Social Impact

**Focus area: Climate Resilience**

Nepal is one of the most flood-vulnerable countries in the world. The agent targets three pilot communities along major rivers:

- **Arughat, Gorkha** — on the Budhi Gandaki, threatened by upstream landslide dams and Manaslu glacial lakes
- **Narayanghat, Chitwan** — on the Narayani, the confluence of multiple rivers from the Annapurna range
- **Chatara, Sunsari** — on the Koshi, Nepal's largest river, known for catastrophic floods

Each place has verified safe locations, emergency contacts, and known upstream threat sources. The agent delivers advice in Nepali (बाढी साथी), making it accessible to communities that official forecasts don't reach.

**What makes it different from existing tools:**
- Existing forecasts are numbers for experts. This agent translates them into household actions.
- It handles the sudden floods that forecasts miss: landslide dam breaks and glacial lake outbursts, using upstream gauge surge detection.
- The warning signs section tells people what to watch for with their own eyes — a roaring sound, suddenly muddy water, a rapid rise — so they can act even without connectivity.

## Running It

```bash
# Advice in Nepali
python -m saathi.agent "Arughat" --lang ne

# English, SMS-friendly format
python -m saathi.agent "Narayanghat" --lang en --sms

# Dry run (no AWS cost, no model call)
python -m saathi.agent "Chatara" --dry-run
```

## What I Learned

Building Baadhi Saathi with the Strands SDK workshop taught me that the hardest part of an agent isn't the LLM — it's the tools. Getting real flood data from Open-Meteo, computing risk levels that a ward officer can verify, and making sure the model never softens a danger warning — that's where the engineering lives.

The workshop's progression from basic tools (Module 1) to hooks and steering (Modules 2-3) directly shaped how I built the risk enforcement. The agent loop handles the complexity of calling five APIs and writing advice; my code handles the safety guarantees.

## Links

- **Repository**: https://github.com/yashrajshrestha/baadhi-saathi
- **Demo video**: [link to video]
- **Workshop**: Building AI Agents with Strands SDK: From Simple Loops to Multi-Agent Swarms
