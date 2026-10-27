"""Agent wiring without any model or network: the tools answer, and the level line is never lost."""
import json

from saathi import agent, rivers


def test_tools_answer_in_json_and_unknown_places_list_the_known_ones():
    tools = {t.tool_name: t for t in agent.make_tools()}
    assert set(tools) == {"find_place", "upstream_watch", "river_outlook", "rain_outlook", "safe_places"}
    found = json.loads(tools["find_place"](query="Arughat"))
    assert found["river"] == "Budhi Gandaki" and found["key"] == "arughat"
    unknown = json.loads(tools["find_place"](query="Pokhara"))
    assert "known" in unknown and len(unknown["known"]) == 3
    safe = json.loads(tools["safe_places"](place_key="chatara"))
    assert safe["emergency"]["NEOC (disaster)"] == "1149" and "ward office" in safe["note"]


def test_finish_puts_the_codes_level_first_in_both_languages():
    out = agent.finish("सबै ठीक छ, चिन्ता नगर्नुहोस्।", "danger", "ne")
    assert out.startswith("खतरा:") and out.endswith("नगर्नुहोस्।")
    assert agent.finish("", "watch", "en") == "WATCH: the river will run higher than usual"


def test_dry_run_uses_the_tools_and_sets_the_headline(monkeypatch):
    past = [100.0] * 90
    fut = [100.0, 110.0, 260.0, 200.0, 150.0, 120.0, 100.0]       # 260 >= 1.5 * 150? no: high = 100 -> 260 >= 2.5*100 -> danger
    series = {"time": [f"d{i}" for i in range(97)], "river_discharge": past + fut, "river_discharge_max": past + fut}

    def fetch(params):
        if params.get("past_days"):
            return {"latitude": params["latitude"], "longitude": params["longitude"], "daily": series}
        return {"latitude": params["latitude"], "longitude": params["longitude"], "daily": {"river_discharge": [100.0]}}

    monkeypatch.setattr(rivers, "_get", fetch)
    monkeypatch.setattr(agent.rain, "outlook", lambda lat, lon, days=3, fetch=None: {"next_days": [], "heaviest": None})
    monkeypatch.setattr(agent.upstream, "ALERT_DIR", __import__("pathlib").Path("/nonexistent"))
    out = agent.dry_run("Narayanghat", "en")
    assert out["river"]["level"] == "warning" and out["headline"].startswith("WARNING")
    assert out["upstream"]["alerts"] == [] and out["upstream"]["warning_signs"]
