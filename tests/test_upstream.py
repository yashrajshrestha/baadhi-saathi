"""Upstream surge alerts: message validation, arrival windows, expiry, and the level they force."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from saathi import agent, places, upstream

NPT = timezone(timedelta(hours=5, minutes=45))
T0 = datetime(2026, 10, 11, 4, 0, tzinfo=NPT)   # the hour the Budhi Gandaki dam broke


def drop(tmp_path, **msg):
    (tmp_path / f"{msg['station']}.json").write_text(json.dumps(msg))


def test_messages_must_name_a_station_a_kind_and_a_time():
    with pytest.raises(ValueError):
        upstream.parse({"station": "chumchet", "kind": "surge"})
    with pytest.raises(ValueError):
        upstream.parse({"station": "chumchet", "kind": "tsunami", "observed_at": T0.isoformat()})
    assert upstream.parse(json.dumps({"station": "chumchet", "kind": "surge", "observed_at": T0.isoformat()}))["kind"] == "surge"


def test_arrival_window_uses_the_fast_wave_for_the_earliest_time():
    assert upstream.arrival(T0.isoformat(), 60) == ("06:00", "10:00")    # 60 km at 30 and 10 km/h


def test_a_surge_upstream_makes_the_place_danger_with_an_arrival_window(tmp_path):
    drop(tmp_path, station="chumchet", kind="surge", observed_at=T0.isoformat(), rise_m=3.2)
    w = upstream.watch("arughat", "ne", now=T0 + timedelta(minutes=10), alert_dir=tmp_path)
    assert w["level"] == "danger"
    assert w["alerts"][0]["arrives_between"] == ("06:00", "10:00") and w["alerts"][0]["rise_m"] == 3.2
    assert w["warning_signs"] == places.WARNING_SIGNS["ne"] and "SMS" in w["act_on_signs"]


def test_alerts_for_other_rivers_and_old_alerts_are_ignored(tmp_path):
    drop(tmp_path, station="bhote-koshi", kind="surge", observed_at=T0.isoformat())
    assert upstream.watch("arughat", now=T0, alert_dir=tmp_path)["alerts"] == []        # different river
    drop(tmp_path, station="chumchet", kind="blockage", observed_at=T0.isoformat())
    later = T0 + timedelta(hours=upstream.MAX_AGE_H + 1)
    assert upstream.watch("arughat", now=later, alert_dir=tmp_path)["level"] is None      # expired


def test_a_blockage_is_danger_without_a_time_because_it_can_burst_any_minute(tmp_path):
    drop(tmp_path, station="chumchet", kind="blockage", observed_at=T0.isoformat())
    a = upstream.watch("arughat", now=T0, alert_dir=tmp_path)["alerts"][0]
    assert a["kind"] == "blockage" and "arrives_between" not in a


def test_every_pilot_place_knows_its_sudden_flood_sources():
    for key, p in places.PLACES.items():
        assert p["upstream"], key
        assert upstream.watch(key, now=T0, alert_dir=None)["sudden_flood_sources"]


def test_the_worst_level_wins():
    assert agent.worst(["calm", None, "danger", "watch"]) == "danger"
    assert agent.worst([None]) == "calm"
