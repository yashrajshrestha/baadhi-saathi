from saathi import places, rain


def test_rain_labels_follow_the_dhm_style_thresholds():
    fake = lambda p: {"daily": {"time": ["2026-07-01", "2026-07-02", "2026-07-03"],
                                "precipitation_sum": [2.0, 75.0, 130.0],
                                "precipitation_probability_max": [20, 80, 95]}}
    out = rain.outlook(27.7, 84.4, fetch=fake)
    assert [d["label"] for d in out["next_days"]] == ["dry", "heavy", "very heavy"]
    assert out["heaviest"]["day"] == "2026-07-03"


def test_places_are_found_by_key_or_name_in_either_script():
    assert places.find("Arughat")["river"] == "Budhi Gandaki"
    assert places.find("नारायणघाट, चितवन")["key"] == "narayanghat"
    assert places.find("Chatara, Sunsari")["lat"] == 26.87
    assert places.find("Pokhara") is None
    assert len(places.listing()) == 3 and places.EMERGENCY["NEOC (disaster)"] == "1149"
