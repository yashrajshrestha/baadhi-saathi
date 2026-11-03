# Baadhi Saathi (बाढी साथी): A Flood Friend for Nepali Households, Built with Strands

## The problem

Nepal had two deadly floods in 2026 that no one in the path could see coming: a glacial-lake flood down
the Bhote Koshi in August, and a flash flood on the Budhi Gandaki on 11 October, when a landslide dam
upstream gave way. Bridges and homes were lost.

Nepal does have forecasts and warnings. GloFAS forecasts river flow days ahead, DHM runs river gauges, and
warning texts go out by SMS. But after the August floods, reporters found the texts often came **late**,
**in Nepali only**, and **without saying what to do or where to go**. Some families by the river got none
at all. A forecast in cubic meters per second reaches experts and newsrooms. It does not reach a family in
Arughat as "move the grain upstairs tonight, and if the river suddenly drops, go up to the health post."

That last step, from data to one household's action, is what Baadhi Saathi ("flood friend") does.

## What it does

Tell it where a household lives and which language they read. It checks five things, then writes today's
advice in plain Nepali or English, as a short message or three SMS texts:

1. **find_place**: which river matters for this household (three pilot places: Arughat on the Budhi
   Gandaki, Narayanghat on the Narayani, Chatara on the Koshi).
2. **upstream_watch**: the floods no forecast can see. Each place lists its known landslide-dam and
   glacial-lake sources upstream and the warning signs anyone can see (the river suddenly drops, a roar,
   muddy water, a fast rise). If an upstream gauge reports a surge, the place goes straight to **DANGER**,
   with an arrival time (river distance ÷ 10–30 km/h).
3. **river_outlook**: the seven-day river flow from the free Open-Meteo Flood API (GloFAS). The code
   compares the coming peak with the river's own last 90 days and sets a level: calm, watch, warning or
   danger. The thresholds are simple multiples, written down so a ward officer can read them.
4. **rain_outlook**: three-day rain totals, with 60 mm and 120 mm a day as the heavy lines.
5. **safe_places**: higher ground for that place, in both languages, plus Nepal's emergency numbers
   (1149 NEOC, 100 police, 102 ambulance).

Amazon Nova Lite on Amazon Bedrock writes the words. A full answer costs well under one US cent.

## Safety lives in code, not in the prompt

My first version put the rules in the system prompt: "check everything", "never make it sound safer", "write
in Nepali". Then I tested it. In one afternoon, Nova Lite:

- named a **bridge** as a safe place during a flood surge,
- gave **112** as the emergency number (Nepal's are 1149, 100 and 102),
- answered a Nepali household **in English**,
- skipped the rain check, and once
- called the place lookup **twelve times in a row** with a name it had copied wrong.

A prompt asks. Code decides. So I moved every rule that matters into the Strands agent loop, using what the
*Building AI Agents with Strands SDK* workshop teaches:

**A steering handler (Module 3).** `FloodSafetyHandler` runs inside the loop. Before each tool call it
checks that the place is known, and that the warning signs are fetched in the household's own language
(they are written by people, so the model copies them instead of translating them badly). After each draft
answer it checks the draft against what the tools found, in code:
- every check ran;
- the draft is in the household's script;
- nothing reassuring ("don't worry", "खतरा छैन") under a warning;
- a real safe place is named;
- only Nepal's emergency numbers;
- "go now" during a surge;
- never send people towards a flood source upstream.

A draft that fails goes back to the model with the reason, at most twice.

**A hook (Module 2).** `ToolBudget` is the workshop's rate limiter, applied here: past 14 tool calls in one
turn, further calls are refused; past 22, the run is cancelled.

**Code has the last word.** The first line is always the code's level. Under a warning or danger, the lines
that matter most are written by the code from the tools' data, never by the model:
- where to go (the real safe places, in Nepali or English);
- when the water may arrive;
- who to call.

If the model still fails the checks after its two rewrites, or errors, its words are dropped and the
household gets the code's message alone. Whatever goes wrong inside the model, a message still goes out,
and it is correct.

**Session memory (Module 4).** With `--household`, a `FileSessionManager` keeps each family's place,
language and last level. The next visit needs no place and no language. The comparison line is written by
the code from the saved level ("Last check 15 June: WATCH. Today: DANGER, higher."): asked to write it,
the model simply left it out.

**Evals (Module 7).** `evals/run.py` uses strands-agents-evals. Each case's expected level is computed by the
code from the same data, so the agent is checked against the data, not against another model's opinion. A
deterministic `SafetyChecks` evaluator checks the household rules, and an `OutputEvaluator` judge (Nova Pro)
asks whether the family would know what to do and whether anything is claimed that the data cannot support.

Results on 2 and 3 November 2026, six cases, run with two agent models (the judge was Nova Pro both times):

| Case | Expected level | Nova Lite: safety checks / judge | Nova Pro: safety checks / judge |
|---|---|---|---|
| Today, Narayanghat, English | CALM | pass / pass | pass / pass |
| Replay 17 Jul 2026, Chatara, English | WARNING | pass / pass | pass / pass |
| Replay 11 Jul 2026, Arughat, Nepali | WARNING | pass / pass | pass / pass |
| Simulated upstream surge, Arughat, Nepali | DANGER now | pass / pass | pass / pass |
| Simulated upstream surge, Arughat, English SMS | DANGER now | pass / pass | pass / pass |
| Remembered household, asked with no place or language | WARNING | pass / pass | pass / pass |

Steering sent drafts back five times, in three of the six cases, for Nova Lite and once for Nova Pro. Both
end up passing, so the agent stays on Nova Lite, which costs several times less: the steering absorbs its
mistakes. One earlier Nova Pro run stopped before its checks in the Nepali surge case; the code dropped its
words and sent its own danger message, which is the design working, though the eval counts it as a fail. The first eval run did not go this
well: every replay case failed for both models. The free weather archive was returning "503 Service
Unavailable", and the agent refused to advise without its rain check. Now a missing rain forecast is said
plainly ("rain forecast unavailable today") and the river and upstream checks still decide the level. The
full messages are in `evals/results-nova-lite-v1.md` and `evals/results-nova-pro-v1.md`.

## Two kinds of flood, shown honestly

**A flood the forecast can see.** `--as-of` replays a past day with the river and rain recorded since. On
17 July 2026, three days before the Koshi at Chatara peaked at about 6,000 m³/s (four times its usual
flow), Baadhi Saathi's level was **WARNING**: pack documents and medicines, move animals and grain, here is
where to go. At Arughat the Budhi Gandaki shows **WARNING** from 10 July, four days before its 14 July peak.
This is hindsight with recorded data, not the forecast issued that morning, and the agent says so in its
answer.

**A flood no forecast can see.** The 11 October flood came from a landslide dam breaking. River and rain
forecasts can't see that, and this agent says so plainly. What can help is a gauge upstream. A real gauge
would publish one small MQTT message to AWS IoT Core, and an IoT Rule would hand it to the agent. On a
laptop, a simulator writes the same message:

```
python -m saathi.simulate surge chumchet --rise 3.2
python -m saathi.agent "Arughat" --lang ne --sms
```

Arughat, 60 km downstream, gets **"अहिले खतरा"** (DANGER NOW): go to the health post or the school's upper
floor, the water may reach you in two to six hours, and call 1149. The time is computed by the code, not
guessed.

## What I learned

The workshop's progression maps onto safety:
- tools give the agent facts (Module 1);
- hooks stop it running away (Module 2);
- steering holds it to the rules (Module 3);
- memory makes it personal (Module 4);
- evals tell you whether any of it works (Module 7).

The most useful lesson was negative. The model is very good at words and not trustworthy with facts that
can hurt someone: a place name, a phone number, a time. So the model writes the explanation, and the code
owns the facts. I only learned which facts by testing it until it broke.

The evals also found a bug that was not the model's at all. The river check finds "the river" by scanning
the forecast grid around a village for the biggest flow. At Arughat that picked a larger river 20 km away,
not the Budhi Gandaki. Mapping the grid by hand showed the right cell, and every pilot place now pins its
river cell. A forecast for the wrong river looks just as convincing as one for the right river.

**Caught while making the demo video.** During a simulated Chumchet surge, Nova Lite wrote to Arughat
"अग्लो ठाउँमा जानुहोस्: चुम्चेट / त्सुम् उपत्यका" ("go to high ground: Chumchet / Tsum valley"), the very
place the flood starts. None of the checks caught it, because they only asked whether a real safe place
was named, not whether a dangerous one was. Each upstream source now carries its names in both scripts,
and steering refuses a draft that sends people towards one ("the flood comes from Chumchet, go to the
school now" still passes). It has a test, like every other rule.

## Honest limits

- Three pilot places; the safe places are examples that each ward office would need to confirm.
- The river levels compare the forecast with the river's own recent history; they are not DHM's official
  warning and danger lines (DHM's gauge site isn't reachable from outside Nepal).
- Nova Lite's Nepali is understandable but not polished; the emergency lines are always the code's own Nepali.
- It supports DHM and ward office alerts. It never replaces them.

## Try it

```bash
git clone https://github.com/yashrajshrestha/baadhi-saathi && cd baadhi-saathi
python3 -m venv .venv && .venv/bin/pip install -e ".[dev,evals]"
.venv/bin/pytest -q                                              # 39 tests, no AWS needed
python -m saathi.agent "Chatara" --dry-run                       # the numbers, no model
AWS_PROFILE=you python -m saathi.agent "Arughat" --lang ne --show-steps
```

- **Repository**: https://github.com/yashrajshrestha/baadhi-saathi (MIT)
- **Demo video**: {VIDEO}
- **Built for**: AWS Builder Center *Strands SDK: Workshop to Ship*, climate resilience track
