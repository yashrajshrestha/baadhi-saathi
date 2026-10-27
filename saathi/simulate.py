"""Pretend upstream gauge: writes the same message an MQTT sensor would publish.

    python -m saathi.simulate surge chumchet [--rise 3.2] [--minutes-ago 10]
    python -m saathi.simulate blockage chumchet
    python -m saathi.simulate clear

The file lands in SAATHI_ALERT_DIR (default ./alerts). The topic it would use on AWS IoT Core is
printed too, so the demo shows exactly what a real gauge would send.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone

from . import upstream

NPT = timezone(timedelta(hours=5, minutes=45))   # Nepal time


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", choices=[*upstream.KINDS, "clear"])
    ap.add_argument("station", nargs="?")
    ap.add_argument("--rise", type=float, default=3.0, help="metres the river rose at the gauge")
    ap.add_argument("--minutes-ago", type=float, default=5)
    a = ap.parse_args()
    d = upstream.ALERT_DIR
    if a.kind == "clear":
        for f in d.glob("*.json"):
            f.unlink()
        print(f"cleared {d}/")
        return
    if not a.station:
        ap.error("station is required")
    msg = {"station": a.station, "kind": a.kind, "rise_m": a.rise if a.kind == "surge" else None,
           "observed_at": (datetime.now(NPT) - timedelta(minutes=a.minutes_ago)).isoformat(timespec="seconds"),
           "note": "SIMULATED gauge message"}
    upstream.parse(msg)  # same validation the real path uses
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{a.station}-{msg['observed_at'].replace(':', '')}.json"
    path.write_text(json.dumps(msg, ensure_ascii=False, indent=2))
    print(f"MQTT topic: saathi/{a.kind}/{a.station}\npayload:    {json.dumps(msg, ensure_ascii=False)}\nwritten:    {path}")


if __name__ == "__main__":
    main()
