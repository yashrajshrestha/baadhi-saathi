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
