"""Rain outlook from the free Open-Meteo weather API: daily rain totals and the chance of heavy rain."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

API = "https://api.open-meteo.com/v1/forecast"
HEAVY_MM = 60.0       # a day at or above this is "heavy" for Nepal's hills (DHM uses 60 mm/24 h as a warning line)
VERY_HEAVY_MM = 120.0


def _get(params: dict, timeout: float = 20) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r)


def outlook(lat: float, lon: float, days: int = 3, fetch=_get) -> dict:
    d = fetch({"latitude": lat, "longitude": lon, "daily": "precipitation_sum,precipitation_probability_max",
               "forecast_days": days, "timezone": "Asia/Kathmandu"})
    out = []
    for day, mm, p in zip(d["daily"]["time"], d["daily"]["precipitation_sum"], d["daily"]["precipitation_probability_max"]):
        mm = mm or 0.0
        label = "very heavy" if mm >= VERY_HEAVY_MM else "heavy" if mm >= HEAVY_MM else "light" if mm >= 5 else "dry"
        out.append({"day": day, "rain_mm": round(mm, 1), "chance_pct": p, "label": label})
    worst = max(out, key=lambda x: x["rain_mm"]) if out else None
    return {"next_days": out, "heaviest": worst,
            "thresholds_mm": {"heavy": HEAVY_MM, "very_heavy": VERY_HEAVY_MM}}
