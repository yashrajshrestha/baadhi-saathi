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
    assert agent.finish("", "danger", "ne", surge=True).startswith("अहिले खतरा")   # happening now, not a forecast


def test_dry_run_uses_the_tools_and_sets_the_headline(monkeypatch):
    past = [100.0] * 90
    fut = [100.0, 110.0, 260.0, 200.0, 150.0, 120.0, 100.0]       # 260 >= 1.5 * 150? no: high = 100 -> 260 >= 2.5*100 -> danger
    series = {"time": [f"d{i}" for i in range(97)], "river_discharge": past + fut, "river_discharge_max": past + fut}

    def fetch(params):
        if params.get("past_days"):
            return {"latitude": params["latitude"], "longitude": params["longitude"], "daily": series}
        return {"latitude": params["latitude"], "longitude": params["longitude"], "daily": {"river_discharge": [100.0]}}

    monkeypatch.setattr(rivers, "_get", fetch)
    monkeypatch.setattr(agent.rain, "outlook", lambda lat, lon, days=3, fetch=None, as_of=None: {"next_days": [], "heaviest": None})
    monkeypatch.setattr(agent.upstream, "ALERT_DIR", __import__("pathlib").Path("/nonexistent"))
    out = agent.dry_run("Narayanghat", "en")
    assert out["river"]["level"] == "warning" and out["headline"].startswith("WARNING")
    assert out["upstream"]["alerts"] == [] and out["upstream"]["warning_signs"]


def test_finish_drops_repeated_paragraphs_and_hindi_words():
    out = agent.finish("अगला दिनहरुमा पानी बढ्छ।\n\nअग्लो ठाउँमा जानुहोस्।\n\nअग्लो ठाउँमा जानुहोस्।", "danger", "ne")
    assert out.count("अग्लो ठाउँमा जानुहोस्।") == 1 and "आउने दिनहरुमा" in out and "अगला" not in out


def test_under_a_warning_the_code_says_where_to_go_when_and_who_to_call():
    seen = {"level": "danger", "surge": True, "alerts": [{"arrives_between": ["21:00", "23:00"]}],
            "safe_en": ["Arughat school building (upper floor)"], "safe_ne": ["आरुघाट विद्यालय भवन (माथिल्लो तला)"]}
    ne = agent.action_block(seen, "ne")
    assert "आरुघाट विद्यालय" in ne and "21:00" in ne and "1149" in ne
    out = agent.finish("SMS 1/3: अग्लो ठाउँमा जानुहोस्।", "danger", "ne", surge=True, action=ne)
    assert out.startswith("अहिले खतरा") and out.index("कहाँ जाने") < out.rindex("अग्लो ठाउँमा जानुहोस्।") and "SMS 1/3" not in out
    assert agent.action_block({**seen, "level": "watch", "surge": False}, "en") == ""


def test_sms_labels_are_removed_even_inside_a_line():
    out = agent.finish("पानी बढ्यो। SMS 2/3: अग्लो ठाउँमा जानुहोस्।", "watch", "ne")
    assert "SMS" not in out and "अग्लो ठाउँमा जानुहोस्।" in out


def test_finish_drops_a_line_repeated_inside_different_paragraphs():
    out = agent.finish("Go to the school now.\nWater comes 01:00-05:00.\n\nPack a bag.\nWater comes 01:00-05:00.",
                       "danger", "en", surge=True)
    assert out.count("Water comes 01:00-05:00.") == 1 and "Pack a bag." in out


def test_the_code_says_how_today_compares_with_last_time():
    assert agent.compare_line(None, "calm", "en") == ""
    assert agent.compare_line({"date": "2026-11-01", "level": "calm"}, "warning", "en") == \
        "Last check 2026-11-01: CALM. Today: WARNING, higher."
    assert agent.compare_line({"date": "2026-11-01", "level": "warning"}, "calm", "ne") == \
        "पछिल्लो जाँच 2026-11-01: चेतावनी। आज: शान्त, घटेको।"
    assert agent.compare_line({"date": "2026-11-01", "level": "calm"}, "calm", "ne").endswith("उस्तै।")
