"""Steering rules without a model: what counts as checked, what counts as too calm, and the retry budget."""
import asyncio
import json

from strands.vended_plugins.steering import Guide, Proceed

from saathi import agent, steering


def call(name, i):
    return {"role": "assistant", "content": [{"toolUse": {"toolUseId": f"t{i}", "name": name, "input": {}}}]}


def result(i, data, status="success"):
    return {"role": "user", "content": [{"toolResult": {"toolUseId": f"t{i}", "status": status,
                                                         "content": [{"text": json.dumps(data, ensure_ascii=False)}]}}]}


def full_check(level="warning", alerts=()):
    msgs = []
    outputs = {
        "find_place": {"key": "arughat"},
        "upstream_watch": {"level": "danger" if alerts else None, "alerts": list(alerts)},
        "river_outlook": {"level": level},
        "rain_outlook": {"next_days": []},
        "safe_places": {"safe_places": ["Arughat school building (upper floor)"], "landmarks": ["school", "विद्यालय"]},
    }
    for i, (name, data) in enumerate(outputs.items()):
        msgs += [call(name, i), result(i, data)]
    return msgs


class FakeState(dict):
    def get(self, k, default=None):
        return super().get(k, default)

    def set(self, k, v):
        self[k] = v


class FakeAgent:
    def __init__(self, messages, turn_start=0):
        self.messages = messages
        self.state = FakeState(turn_start=turn_start)


def test_picture_reads_the_worst_level_and_ignores_failed_tools():
    msgs = full_check("watch") + [call("river_outlook", 9), result(9, {"level": "danger"}, status="error")]
    seen = steering.picture(msgs)
    assert seen["ok"] == set(steering.REQUIRED) and seen["level"] == "watch" and not seen["surge"]
    assert steering.picture(full_check("calm", alerts=[{"station": "Chumchet"}]))["level"] == "danger"


def test_no_answer_before_every_check_has_run():
    seen = steering.picture(full_check()[:4])                     # find_place and upstream_watch only
    why = steering.problem("Pack a bag.", seen)
    assert "river_outlook" in why and "rain_outlook" in why and "safe_places" in why


def test_a_warning_cannot_be_talked_down_and_must_say_where_to_go():
    seen = steering.picture(full_check("warning"))
    assert "WARNING" in steering.problem("The river is high but don't worry, stay home.", seen)
    assert "Say exactly where to go" in steering.problem("Pack documents and medicines in one bag.", seen)
    assert "Say exactly where to go" in steering.problem("Pack a bag and move to higher ground.", seen)   # too vague
    assert steering.problem("Pack a bag and go to the school's upper floor tonight.", seen) is None
    assert steering.problem("खतरा छैन, घरमै बस्नुहोस्।", seen) is not None
    assert steering.problem("All calm today.", steering.picture(full_check("calm"))) is None   # calm may reassure


def test_a_live_surge_must_say_go_now():
    seen = steering.picture(full_check("calm", alerts=[{"station": "Chumchet"}]))
    assert "immediately" in steering.problem("Move to the school with your family.", seen)
    assert steering.problem("Go to the school now. The water arrives 06:00-08:00.", seen) is None


def test_tools_wait_for_the_place_and_drafts_get_two_rewrites_at_most():
    h = steering.FloodSafetyHandler()
    early = FakeAgent([])
    assert isinstance(asyncio.run(h.steer_before_tool(agent=early, tool_use={"name": "river_outlook"})), Guide)
    assert isinstance(asyncio.run(h.steer_before_tool(agent=early, tool_use={"name": "find_place"})), Proceed)
    placed = FakeAgent(full_check()[:2])
    placed.state.set("lang", "ne")      # Nepali household: the warning signs must be fetched in Nepali, not translated
    up = {"name": "upstream_watch", "input": {"place_key": "arughat"}}
    assert isinstance(asyncio.run(h.steer_before_tool(agent=placed, tool_use=up)), Guide)
    up["input"]["lang"] = "ne"
    assert isinstance(asyncio.run(h.steer_before_tool(agent=placed, tool_use=up)), Proceed)

    a = FakeAgent(full_check("danger"))
    draft = {"role": "assistant", "content": [{"text": "Nothing to worry about."}]}
    actions = [asyncio.run(h.steer_after_model(agent=a, message=draft, stop_reason="end_turn")) for _ in range(3)]
    assert [type(x) for x in actions] == [Guide, Guide, Proceed]       # MAX_RETRIES, then finish() has the last word
    assert isinstance(asyncio.run(h.steer_after_model(agent=a, message=draft, stop_reason="tool_use")), Proceed)


def test_only_this_turn_counts_once_a_household_is_remembered():
    yesterday = full_check("danger")
    today = full_check("calm")
    a = FakeAgent(yesterday + today, turn_start=len(yesterday))
    assert steering.picture(steering.turn_messages(a))["level"] == "calm"    # yesterday's danger is history
    assert agent.household_id("Ram's house, Arughat!") == "household-ram-s-house-arughat"


def test_a_nepali_household_gets_nepali_and_an_english_one_english():
    seen = steering.picture(full_check("calm"))
    assert "Nepali" in steering.problem("Pack a bag and keep your phone charged.", seen, "ne")
    assert steering.problem("झोलामा कागजात र औषधि राख्नुहोस्। फोन चार्ज गर्नुहोस्।", seen, "ne") is None
    assert "English" in steering.problem("झोलामा कागजात र औषधि राख्नुहोस्।", seen, "en")
    assert steering.devanagari_share("abc अआइ") == 0.5


def test_only_nepal_emergency_numbers_may_be_given():
    assert steering.wrong_numbers("Call 112 if you need help.") == ["112"]
    assert steering.wrong_numbers("आवश्यक भएमा ११२ मा फोन गर्नुहोस्।") == ["112"]
    assert steering.wrong_numbers("Call 1149 (NEOC) or 100. The peak is 6323 m3/s.") == []
    seen = steering.picture(full_check("calm"))
    assert "not a Nepal emergency number" in steering.problem("All calm. Call 112 if worried.", seen, "en")


def test_the_turn_is_found_by_its_marker_even_after_old_messages_are_trimmed():
    ask = {"role": "user", "content": [{"text": "[check 2026-11-02T19:00:00] Household in Narayanghat."}]}
    a = FakeAgent(full_check("danger")[3:] + [ask] + full_check("calm"), turn_start=99)   # stale position
    a.state.set("turn_marker", "[check 2026-11-02T19:00:00]")
    seen = steering.picture(steering.turn_messages(a))
    assert seen["level"] == "calm" and seen["ok"] == set(steering.REQUIRED)


def test_during_a_surge_rain_no_longer_holds_up_the_warning():
    msgs = full_check("calm", alerts=[{"station": "Chumchet"}])
    surge_only = [m for i, m in enumerate(msgs) if i // 2 not in (2, 3)]        # no river_outlook, no rain_outlook
    seen = steering.picture(surge_only)
    assert seen["surge"] and steering.missing_checks(seen) == []
    assert steering.missing_checks(steering.picture(full_check("calm")[:6])) == ["rain_outlook", "safe_places"]


def test_a_runaway_loop_is_cut_off():
    class Ev:
        def __init__(self, agent):
            self.agent, self.cancel_tool = agent, False

    looping = FakeAgent([call("find_place", i) for i in range(16)])
    looping.cancelled = False
    looping.cancel = lambda after_current_tools=False: setattr(looping, "cancelled", True)
    budget = steering.ToolBudget()
    ev = Ev(looping)
    budget.before(ev)
    assert ev.cancel_tool and "write the advice now" in ev.cancel_tool and not looping.cancelled
    looping.messages += [call("find_place", 100 + i) for i in range(8)]
    ev = Ev(looping)
    budget.before(ev)
    assert looping.cancelled and budget.stopped
    fine = Ev(FakeAgent(full_check()))
    budget.before(fine)
    assert fine.cancel_tool is False
