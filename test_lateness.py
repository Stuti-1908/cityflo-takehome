import pytest

import lateness as L

CFG = L.load_config()
DS = L.Dataset(CFG)


def test_42_rows_dropped_with_reasons():
    assert DS.raw_n == 5292
    assert len(DS.dropped) == 42
    reasons = {}
    for _, _, why in DS.dropped:
        reasons[why] = reasons.get(why, 0) + 1
    assert reasons == {"unparseable_arrival": 24, "negative_elapsed": 18}
    assert len(DS.trips) == 5250


def test_no_remaining_trip_has_negative_elapsed():
    assert min(t["elapsed"] for t in DS.trips) >= 0


def test_repeated_arrival_pairs_are_kept():
    assert len(DS.repeat_pairs) == 59
    assert all(t in DS.by_id for ids in DS.repeat_pairs.values() for t in ids)


def test_utc_row_is_normalised_to_ist():
    utc = [t for t in DS.trips if t["tz_raw"] == "+00:00"]
    assert len(utc) == 1
    t = utc[0]
    # raw stamp is 5h30m behind IST; after normalising it is a normal trip
    assert abs(DS.excess(t)) < 15


def test_rec114_applies_to_r14_all_week():
    r14 = [t for t in DS.trips if t["route"] == "R-14"]
    assert {DS.basis(t) for t in r14} == {(53.0, "schedule_v2")}
    assert any(t["day"] < "2026-08-05" for t in r14)


def test_no_change_note_keeps_r27_on_export_runtimes():
    assert DS.v2_active("R-14") and not DS.v2_active("R-27")
    r27 = [t for t in DS.trips if t["route"] == "R-27"]
    assert all(DS.basis(t) == (t["export_runtime"], "export") for t in r27)
    assert DS.route_stats("R-27")["wd_median"] == 2.0


def test_r27_on_v2_if_no_change_rows_are_not_skipped():
    ds = DS.with_schedule("all_week", overrides={}, skip_notes=[])
    assert ds.v2_active("R-27")
    assert ds.route_stats("R-27")["wd_median"] == 3.0


def test_r35_wed_spike_is_dropped_as_worst_day_not_by_override():
    s = DS.route_stats("R-35")
    assert s["worst_day"] == "2026-08-05"
    assert s["worst_day_median"] > 40
    assert s["mean"] > 8 and s["wd_median"] < CFG["verdict"]["late_threshold_min"]
    assert not s["late"]
    assert CFG["schedule"]["route_overrides"] == {}


def test_verdicts_and_worst_three():
    ranked = DS.ranked()
    assert [s["route"] for s in ranked if s["late"]] == ["R-33", "R-26", "R-37", "R-31"]
    assert [s["route"] for s in ranked[:3]] == ["R-33", "R-26", "R-37"]
    assert DS.route_stats("R-12")["wd_median"] == 1.5
    assert not DS.route_stats("R-12")["late"]


def test_ops_log_exposed_as_category_tags_only():
    tags = L.ops_log_tags(CFG)
    assert len(tags) == 6
    allowed = set(CFG["ops_log_categories"]) | {"uncategorised"}
    for e in tags:
        assert set(e) == {"day", "time", "categories"}
        assert set(e["categories"]) <= allowed


def test_guard_blocks_raw_log_text_and_phone_numbers():
    with pytest.raises(ValueError):
        L.guard({"x": "SV Road waterlogged, western corridor diverted ~35min all AM"}, CFG)
    with pytest.raises(ValueError):
        L.guard({"x": "call 9876543210"}, CFG)
    with pytest.raises(ValueError):
        L.guard(["+91 9876543210"], CFG)
    assert L.guard({"trip": "T1-00059", "t": "2026-08-05 06:17"}, CFG)


def test_tool_outputs_pass_the_guard():
    import server
    server.data_quality_report()
    server.rank_routes()
    server.sensitivity_check()
    server.route_lateness("R-35")
    server.explain_trip("T1-04521")
