"""Push today's advice to subscribed phones. Nobody types a command during a flood.

    python -m saathi.push --no-send              # generate the SMS for every place, print, send nothing
    python -m saathi.push                        # send via Amazon SNS
    python -m saathi.push --place arughat        # one place only

Subscribers live in subscribers.json next to this package (gitignored; see subscribers.example.json):
    {"arughat": ["+9779800000000"], "narayanghat": [], "chatara": []}

The same run() is called two ways in production:
  - EventBridge schedule at 06:00 Nepal time: the daily message for every place.
  - AWS IoT Core rule -> Lambda handler() when an upstream gauge publishes a surge: the place goes
    to danger and the message goes out at once, without waiting for the morning.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from . import places, upstream
from .agent import advise

SUBSCRIBERS = Path(os.environ.get("SAATHI_SUBSCRIBERS", Path(__file__).resolve().parent.parent / "subscribers.json"))
MAX_SMS = 3


def load_subscribers(path: Path = SUBSCRIBERS) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: [n for n in v if n] for k, v in data.items()}


def to_sms(advice: str, limit: int = 300) -> list[str]:
    """Pack the headline and the model's paragraphs into at most MAX_SMS texts."""
    text = re.sub(r"(?im)^[ \t]*(SMS|message|सन्देश)[ \t]*\d[ \t]*/[ \t]*\d[ \t]*:?[ \t]*", "", advice)
    units: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) <= limit:
            units.append(line)
        else:  # one long paragraph: break at sentence ends (danda or full stop)
            units.extend(s for s in re.split(r"(?<=[।.!?])\s+", line) if s)
    msgs: list[str] = []
    for u in units:
        if msgs and len(msgs[-1]) + 1 + len(u) <= limit:
            msgs[-1] += "\n" + u
        else:
            msgs.append(u)
    return msgs[:MAX_SMS]


def send(phone: str, text: str, sns=None) -> str:
    sns = sns or _sns()
    r = sns.publish(PhoneNumber=phone, Message=text,
                    MessageAttributes={"AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}})
    return r["MessageId"]


def _sns():
    import boto3
    return boto3.client("sns", region_name=os.environ.get("SNS_REGION", os.environ.get("BEDROCK_REGION", "us-east-1")))


def run(place_filter: str | None = None, lang: str = "ne", no_send: bool = False) -> list[dict]:
    subs = load_subscribers()
    report = []
    for key, phones in subs.items():
        if place_filter and key != place_filter:
            continue
        if not phones:
            continue
        p = places.find(key)
        if not p:
            print(f"skip {key}: unknown place", file=sys.stderr)
            continue
        advice = advise(p["name"], lang=lang, sms=True)
        msgs = to_sms(advice)
        for phone in phones:
            for i, m in enumerate(msgs, 1):
                if no_send:
                    print(f"--- {p['name']} -> {phone}  ({i}/{len(msgs)}, {len(m)} chars)\n{m}\n")
                    mid = None
                else:
                    mid = send(phone, m)
                    print(f"sent {i}/{len(msgs)} to {phone}: {mid}", file=sys.stderr)
                report.append({"place": key, "phone": phone, "part": i, "message_id": mid})
    return report


def handler(event, context=None):
    """Lambda entry. An IoT gauge message has a 'station'; a schedule event does not."""
    if isinstance(event, dict) and "station" in event:
        upstream.parse(event)
        d = upstream.ALERT_DIR
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{event['station']}.json").write_text(json.dumps(event), encoding="utf-8")
    return {"sent": run(no_send=os.environ.get("SAATHI_NO_SEND") == "1")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--place", help="only this place key, e.g. arughat")
    ap.add_argument("--lang", default="ne", choices=["ne", "en"])
    ap.add_argument("--no-send", action="store_true", help="generate and print, do not call SNS")
    a = ap.parse_args()
    r = run(a.place, a.lang, a.no_send)
    if not r:
        print("nothing to send: add phone numbers to subscribers.json", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
