"""River outlook: channel scan, risk thresholds and summary, with a fake Open-Meteo so tests need no network."""
from saathi import rivers


def fake_api(cells, series):
    """cells: {(lat, lon): today's discharge}; series: the full daily arrays for the chosen cell."""
    def fetch(params):
        key = (params["latitude"], params["longitude"])
        if params.get("past_days"):
            return {"latitude": key[0], "longitude": key[1], "daily": series}
        if key not in cells:
            raise RuntimeError("no data")
        return {"latitude": key[0], "longitude": key[1], "daily": {"river_discharge": [cells[key]]}}
    return fetch


def test_channel_cell_picks_the_biggest_river_in_the_neighbourhood():
    cells = {(27.7, 84.43): 4.0, (27.65, 84.33): 1380.0, (27.75, 84.48): 90.0}
    lat, lon, q = rivers.channel_cell(27.7, 84.43, fetch=fake_api(cells, {}))
    assert (lat, lon, q) == (27.65, 84.33, 1380.0)


def test_risk_levels_are_simple_multiples_of_the_rivers_own_history():
    assert rivers.risk_level(peak=900, typical=1000, high=1500) == "calm"
    assert rivers.risk_level(peak=1600, typical=1000, high=1500) == "watch"
    assert rivers.risk_level(peak=2300, typical=1000, high=1500) == "warning"
    assert rivers.risk_level(peak=3800, typical=1000, high=1500) == "danger"
    assert rivers.risk_level(peak=5, typical=0, high=0) == "calm"      # no history, no claim


def test_outlook_builds_thresholds_from_the_past_and_finds_the_peak():
    past = [100.0] * 80 + [150.0] * 10                 # median 100, 90th percentile 150
    future = [110.0, 120.0, 400.0, 300.0, 200.0, 150.0, 120.0]
    days = [f"d{i}" for i in range(97)]
    series = {"time": days, "river_discharge": past + future, "river_discharge_max": past + future}
    o = rivers.outlook("Test", 27.7, 84.43, fetch=fake_api({(27.7, 84.43): 100.0}, series))
    assert (o.typical, o.high) == (100.0, 150.0)
    assert (o.peak_day, o.peak, o.level) == ("d92", 400.0, "danger")   # 400 >= max(375, 300)
    s = rivers.summary(o)
    assert s["level"] == "danger" and len(s["next_days"]) == 7 and "landslide" in s["limits"]


def test_a_replay_asks_for_the_same_window_from_the_record():
    assert rivers.window(None) == {"past_days": rivers.PAST_DAYS, "forecast_days": rivers.FORECAST_DAYS}
    assert rivers.window("2026-07-17") == {"start_date": "2026-04-18", "end_date": "2026-07-23"}
    seen = {}

    def fetch(params):
        seen.update(params)
        n = rivers.PAST_DAYS + rivers.FORECAST_DAYS
        if "start_date" in params:
            return {"latitude": 27.7, "longitude": 84.43,
                    "daily": {"time": [f"d{i}" for i in range(n)], "river_discharge": [100.0] * n,
                              "river_discharge_max": [100.0] * n}}
        return {"latitude": 27.7, "longitude": 84.43, "daily": {"river_discharge": [100.0]}}

    o = rivers.outlook("Test", 27.7, 84.43, fetch=fetch, as_of="2026-07-17")
    assert seen["start_date"] == "2026-04-18" and "past_days" not in seen
    assert any("REPLAY as of 2026-07-17" in n for n in o.notes)


def test_a_pinned_river_cell_is_used_without_scanning():
    from saathi import places
    asked = []

    def fetch(params):
        asked.append((params["latitude"], params["longitude"]))
        n = rivers.PAST_DAYS + rivers.FORECAST_DAYS
        return {"latitude": params["latitude"], "longitude": params["longitude"],
                "daily": {"time": [f"d{i}" for i in range(n)], "river_discharge": [100.0] * n, "river_discharge_max": [100.0] * n}}

    o = rivers.outlook("Arughat", 28.04, 84.82, fetch=fetch, cell=(28.025, 84.775))
    assert asked == [(28.025, 84.775)] and (o.lat, o.lon) == (28.025, 84.775)   # one request, not 49
    assert all(len(p["river_cell"]) == 2 for p in places.PLACES.values())
