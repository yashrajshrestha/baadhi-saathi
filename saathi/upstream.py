"""Upstream surge alerts: the part no forecast can do.

A gauge near a landslide dam or glacial lake sees the surge pass and publishes one small message.
In production that message travels over MQTT to AWS IoT Core (topic `saathi/surge/<river>/<station>`),
an IoT Rule hands it to a Lambda, and the agent turns it into a warning per downstream place. Here
the same message can also be dropped as a JSON file into ALERT_DIR (the simulator does that), so the
whole chain runs on a laptop.

Message (MQTT payload or file), all fields required except note:
    {"station": "chumchet", "kind": "surge" | "blockage", "observed_at": "2026-10-11T04:00:00+05:45",
     "rise_m": 3.2, "note": "optional free text"}

A "surge" means water is coming: every place downstream goes to danger, and the arrival window is
distance / wave speed. A "blockage" means the river is dammed upstream (often seen as the river
dropping): danger too, with no arrival time, because a burst could come any minute.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from . import places

ALERT_DIR = Path(os.environ.get("SAATHI_ALERT_DIR", "alerts"))
MAX_AGE_H = 12
# Outburst waves in steep Himalayan valleys move at roughly these speeds. The fast end gives the
# earliest arrival, which is the one people must act on.
WAVE_KMH = (10.0, 30.0)
KINDS = ("surge", "blockage")


def parse(payload: str | bytes | dict) -> dict:
    msg = payload if isinstance(payload, dict) else json.loads(payload)
    missing = [k for k in ("station", "kind", "observed_at") if not msg.get(k)]
    if missing:
        raise ValueError("alert missing " + ", ".join(missing))
    if msg["kind"] not in KINDS:
        raise ValueError(f"unknown kind {msg['kind']!r}")
    msg["observed_at"] = datetime.fromisoformat(msg["observed_at"]).isoformat()
    return msg


def arrival(observed_at: str, km: float) -> tuple[str, str]:
    """(earliest, latest) arrival time as HH:MM, from the observation time and river distance."""
    t = datetime.fromisoformat(observed_at)
    fast, slow = WAVE_KMH[1], WAVE_KMH[0]
    return ((t + timedelta(hours=km / fast)).strftime("%H:%M"), (t + timedelta(hours=km / slow)).strftime("%H:%M"))


def active(now: datetime | None = None, alert_dir: Path | None = None) -> list[dict]:
    """Alerts received in the last MAX_AGE_H hours (from files the simulator or the IoT bridge wrote)."""
    d = alert_dir or ALERT_DIR
    if not d.is_dir():
        return []
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            msg = parse(f.read_text())
        except (ValueError, OSError):
            continue
        t = datetime.fromisoformat(msg["observed_at"])
        ref = now or datetime.now(t.tzinfo)
        if timedelta(0) <= ref - t <= timedelta(hours=MAX_AGE_H):
            out.append(msg)
    return out


def watch(place_key: str, lang: str = "en", now: datetime | None = None, alert_dir: Path | None = None) -> dict:
    """Upstream picture for one place: known sudden-flood sources, warning signs, and any live alert."""
    p = places.PLACES[place_key]
    sources = {s["id"]: s for s in p.get("upstream", [])}
    alerts = []
    for msg in active(now, alert_dir):
        src = sources.get(msg["station"])
        if not src:
            continue
        a = {"station": src["name"], "kind": msg["kind"], "observed_at": msg["observed_at"], "km": src["km"],
             "rise_m": msg.get("rise_m"), "note": msg.get("note")}
        if msg["kind"] == "surge":
            a["arrives_between"] = arrival(msg["observed_at"], src["km"])
        alerts.append(a)
    return {
        "place": p["name"],
        "level": "danger" if alerts else None,   # None: no say; the river forecast decides
        "alerts": alerts,
        "sudden_flood_sources": [s["name"] for s in sources.values()],
        "warning_signs": places.WARNING_SIGNS[lang],
        "act_on_signs": places.ACT_ON_SIGNS[lang],
        "limits": "Upstream gauges catch a surge only after it starts. Lead time is the travel time, minutes to hours.",
    }
