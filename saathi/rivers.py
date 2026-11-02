"""River outlook from the free Open-Meteo Flood API (GloFAS), and a risk level computed in code.

GloFAS is a 0.05° grid. The cell nearest a village is usually a side-stream, so `channel_cell`
scans the neighbourhood and keeps the cell with the largest discharge: that is the river. The risk
level is set here, not by the language model, by comparing the coming days with the river's own
recent history: the model may explain a level, never lower it.

Honest limit: this data sees rain-driven river floods days ahead. It cannot see a landslide dam
breaking or a glacial lake bursting (Budhi Gandaki, 11 Oct 2026; Bhote Koshi, Aug 2026). For
those the agent's job is what to do once the official alert comes, not prediction.
"""
from __future__ import annotations

import json
import statistics
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, timedelta

API = "https://flood-api.open-meteo.com/v1/flood"
STEP = 0.05          # GloFAS grid spacing in degrees
SCAN = 3             # cells either side: a 7x7 window, about 35 km
PAST_DAYS = 90       # the river's own recent history, for the thresholds
FORECAST_DAYS = 7

LEVELS = ("calm", "watch", "warning", "danger")


def _get(params: dict, timeout: float = 20) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)


def channel_cell(lat: float, lon: float, fetch=None) -> tuple[float, float, float]:
    """(lat, lon, today's discharge) of the main river cell near a point."""
    fetch = fetch or _get   # looked up at call time, so tests can swap _get
    best = None
    for i in range(-SCAN, SCAN + 1):
        for j in range(-SCAN, SCAN + 1):
            try:
                d = fetch({"latitude": round(lat + i * STEP, 3), "longitude": round(lon + j * STEP, 3),
                           "daily": "river_discharge", "forecast_days": 1})
                q = d["daily"]["river_discharge"][0]
            except Exception:
                continue
            if q is not None and (best is None or q > best[2]):
                best = (d["latitude"], d["longitude"], q)
    if best is None:
        raise RuntimeError("no river data around this point")
    return best


@dataclass
class Outlook:
    place: str
    lat: float
    lon: float
    days: list[str]
    discharge: list[float]            # past PAST_DAYS + forecast, daily mean m³/s
    discharge_max: list[float]        # same, daily max (ensemble)
    today_index: int
    typical: float = 0.0              # median of the past window
    high: float = 0.0                 # 90th percentile of the past window
    level: str = "calm"
    peak_day: str = ""
    peak: float = 0.0
    notes: list[str] = field(default_factory=list)

    def forecast(self) -> list[tuple[str, float, float]]:
        return list(zip(self.days[self.today_index:], self.discharge[self.today_index:],
                        self.discharge_max[self.today_index:]))


def risk_level(peak: float, typical: float, high: float) -> str:
    """calm: within the usual range. watch: above the recent 90th percentile. warning: 1.5x that.
    danger: 2.5x that, or 3x typical, whichever comes first. Thresholds are deliberately simple and
    written down, so a ward officer can read them."""
    if high <= 0 or typical <= 0:
        return "calm"
    if peak >= max(2.5 * high, 3.0 * typical):
        return "danger"
    if peak >= 1.5 * high:
        return "warning"
    if peak > high:
        return "watch"
    return "calm"


def window(as_of: str | None) -> dict:
    """Request parameters for the past window plus the coming days. With `as_of` (YYYY-MM-DD) the same
    window is taken from the record, so a past flood can be replayed: hindsight with the data on file
    now, not the forecast that was issued that morning."""
    if not as_of:
        return {"past_days": PAST_DAYS, "forecast_days": FORECAST_DAYS}
    day = date.fromisoformat(as_of)
    return {"start_date": (day - timedelta(days=PAST_DAYS)).isoformat(),
            "end_date": (day + timedelta(days=FORECAST_DAYS - 1)).isoformat()}


def outlook(place: str, lat: float, lon: float, fetch=None, as_of: str | None = None) -> Outlook:
    fetch = fetch or _get
    clat, clon, _ = channel_cell(lat, lon, fetch)
    d = fetch({"latitude": clat, "longitude": clon, "daily": "river_discharge,river_discharge_max",
               **window(as_of)})
    days = d["daily"]["time"]
    q = [x if x is not None else 0.0 for x in d["daily"]["river_discharge"]]
    qmax = [x if x is not None else 0.0 for x in d["daily"].get("river_discharge_max") or q]
    today = PAST_DAYS
    past = [x for x in q[:today] if x > 0]
    o = Outlook(place, clat, clon, days, q, qmax, today)
    if past:
        o.typical = statistics.median(past)
        o.high = sorted(past)[int(0.9 * (len(past) - 1))]
    fut = list(zip(days[today:], qmax[today:]))
    o.peak_day, o.peak = max(fut, key=lambda x: x[1])
    o.level = risk_level(o.peak, o.typical, o.high)
    if o.peak > 0 and o.typical > 0:
        o.notes.append(f"peak {o.peak:.0f} m3/s on {o.peak_day}, {o.peak / o.typical:.1f}x the recent typical flow")
    if as_of:
        o.notes.append(f"REPLAY as of {as_of}: recorded flows, not the forecast issued that day")
    return o


def summary(o: Outlook) -> dict:
    """The compact, numeric picture the agent hands to the language model."""
    return {
        "place": o.place, "river_cell": [o.lat, o.lon], "level": o.level,
        "typical_m3s": round(o.typical, 1), "recent_high_m3s": round(o.high, 1),
        "peak_m3s": round(o.peak, 1), "peak_day": o.peak_day,
        "next_days": [{"day": d, "mean": round(m, 1), "max": round(x, 1)} for d, m, x in o.forecast()],
        "notes": o.notes,
        "limits": "River forecast only. Cannot see landslide-dam breaks or glacial lake floods; follow DHM and local alerts.",
    }
