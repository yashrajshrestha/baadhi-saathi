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


def test_a_replay_reads_recorded_rain_which_has_no_chance_of_rain():
    seen = {}

    def fake(p):
        seen.update(p)
        return {"daily": {"time": ["2026-07-17", "2026-07-18", "2026-07-19"], "precipitation_sum": [40.0, 95.0, 10.0]}}

    out = rain.outlook(26.87, 87.16, fetch=fake, as_of="2026-07-17")
    assert (seen["start_date"], seen["end_date"]) == ("2026-07-17", "2026-07-19")
    assert out["heaviest"]["label"] == "heavy" and out["next_days"][0]["chance_pct"] is None


def test_a_name_copied_from_the_listing_is_found():
    for name in places.listing():                       # "Chatara, Sunsari (Koshi)" once looped twelve times
        assert places.find(name) is not None
    assert places.find("Household in Chatara")["key"] == "chatara"
    assert places.find("चतरा")["key"] == "chatara" and places.find("Pokhara") is None
