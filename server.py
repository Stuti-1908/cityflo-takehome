"""Cityflo on-time-performance MCP server (stdio).

Run: .venv\\Scripts\\python server.py   (rules live in config.json)
"""
from collections import Counter

from mcp.server.fastmcp import FastMCP

import lateness as L

mcp = FastMCP("cityflo-ops")
CFG = L.load_config()
DS = L.Dataset(CFG)


def _ds(schedule_mode=None):
    if schedule_mode is None:
        return DS
    if schedule_mode not in L.SCHEDULE_MODES:
        raise ValueError(f"schedule_mode must be one of {L.SCHEDULE_MODES}")
    return DS.with_schedule(schedule_mode, overrides={})


def _row(s):
    return {
        "route": s["route"], "n": s["n"], "late": s["late"],
        "wd_median": L._r(s["wd_median"]), "median": L._r(s["median"]),
        "mean": L._r(s["mean"]), "p90": L._r(s["p90"]),
        "pct_over_5m": L._r(s["pct_over_5m"], 0), "pct_over_10m": L._r(s["pct_over_10m"], 0),
        "worst_day": s["worst_day"], "worst_day_median": L._r(s["worst_day_median"]),
    }


def _basis_desc(ds, route):
    mode = ds.mode_for(route)
    if ds.v2_active(route) and mode != "off":
        return f"schedule_v2 {ds.v2[route][0]:g}m ({mode})"
    return "export scheduled_runtime_min"


@mcp.tool()
def data_quality_report() -> dict:
    """Rows kept/dropped by rule (with trip ids), tz offsets, repeated-arrival
    pairs, and ops-log events as category tags only (no log text)."""
    reasons = Counter(r for _, _, r in DS.dropped)
    out = {
        "rows_raw": DS.raw_n, "rows_kept": len(DS.trips),
        "dropped_by_reason": dict(reasons),
        "dropped_trip_ids": {r: [t for t, _, rr in DS.dropped if rr == r] for r in reasons},
        "tz_offsets_seen": dict(DS.tz_counts),
        "tz_normalised_to": CFG["tz_normalize_to"],
        "repeated_arrival_pairs_kept": len(DS.repeat_pairs),
        "schedule_v2_routes": {r: {"minutes": m, "effective": e, "note": n, "applied": DS.v2_active(r)}
                              for r, (m, e, n) in DS.v2.items()},
        "rules": {k: CFG[k] for k in ("cleaning", "schedule", "verdict", "ranking")},
        "ops_log_events": L.ops_log_tags(CFG),
    }
    return L.guard(out, CFG)


@mcp.tool()
def route_lateness(route: str, schedule_mode: str | None = None) -> dict:
    """Lateness stats and LATE verdict for one route (e.g. 'R-27').
    schedule_mode overrides config: all_week | from_effective | off."""
    ds = _ds(schedule_mode)
    s = ds.route_stats(route)
    if s is None:
        raise ValueError(f"unknown route {route}")
    out = _row(s)
    out["measured_against"] = _basis_desc(ds, route)
    out["day_medians"] = {d: L._r(m) for d, m in s["day_medians"].items()}
    out["rule"] = (f"LATE if {CFG['verdict']['metric']} >= "
                   f"{CFG['verdict']['late_threshold_min']}m; wd_median = median excess "
                   "after removing the single day with the highest daily median")
    return L.guard(out, CFG)


@mcp.tool()
def rank_routes(schedule_mode: str | None = None) -> dict:
    """All routes ranked worst-first; flagged-LATE list and the worst three.
    Order: wd_median, then pct_over_5m, then p90 (from config)."""
    ds = _ds(schedule_mode)
    ranked = ds.ranked()
    n = CFG["ranking"]["worst_n"]
    out = {
        "schedule_mode": schedule_mode or CFG["schedule"]["mode"],
        "route_overrides": {} if schedule_mode else CFG["schedule"]["route_overrides"],
        "late_routes": [_row(s) for s in ranked if s["late"]],
        "worst_three": [_row(s) for s in ranked[:n]],
        "ranking": [[s["route"], L._r(s["wd_median"]), L._r(s["pct_over_5m"], 0),
                     L._r(s["p90"]), s["late"]] for s in ranked],
        "ranking_columns": ["route", "wd_median", "pct_over_5m", "p90", "late"],
    }
    return L.guard(out, CFG)


@mcp.tool()
def explain_trip(trip_id: str) -> dict:
    """How one trip was treated: kept or dropped, the runtime it was measured
    against, its excess, and whether it shares an arrival minute with another trip."""
    for tid, route, reason in DS.dropped:
        if tid == trip_id:
            return L.guard({"trip_id": tid, "route": route, "status": "dropped", "reason": reason}, CFG)
    t = DS.by_id.get(trip_id)
    if t is None:
        raise ValueError(f"unknown trip {trip_id}")
    minutes, label = DS.basis(t)
    partners = [p for k, v in DS.repeat_pairs.items() if trip_id in v for p in v if p != trip_id]
    s = DS.route_stats(t["route"])
    out = {
        "trip_id": trip_id, "route": t["route"], "status": "kept",
        "departure": t["dep"].strftime(L.FMT), "arrival_ist": t["arr"].strftime(L.FMT),
        "tz_raw": t["tz_raw"], "elapsed_min": L._r(t["elapsed"]),
        "measured_against_min": minutes, "basis": label,
        "export_runtime_min": t["export_runtime"],
        "excess_min": L._r(DS.excess(t)),
        "same_arrival_minute_as": partners,
        "on_route_worst_day": t["day"] == s["worst_day"],
        "route_wd_median": L._r(s["wd_median"]),
    }
    return L.guard(out, CFG)


@mcp.tool()
def sensitivity_check() -> dict:
    """Does the worst three survive other defensible choices? Varies the
    REC-114 schedule rule, the ranking metric, and drops each day in turn."""
    n = CFG["ranking"]["worst_n"]
    top = lambda ranked: [s["route"] for s in ranked[:n]]
    out = {"baseline_top3": top(DS.ranked()), "baseline_late": [s["route"] for s in DS.ranked() if s["late"]]}
    sched = {}
    for mode in L.SCHEDULE_MODES:
        d = DS.with_schedule(mode, overrides={})
        r = d.ranked()
        sched[mode] = {"top3": top(r), "late": [s["route"] for s in r if s["late"]]}
    d = DS.with_schedule("all_week", overrides={}, skip_notes=[])
    r = d.ranked()
    sched["all_week_incl_no_change_rows"] = {"top3": top(r), "late": [s["route"] for s in r if s["late"]]}
    out["by_schedule_rule"] = sched
    out["by_metric"] = {m: top(DS.ranked(metric=m)) for m in ("wd_median", "median", "mean", "p90", "pct_over_10m")}
    days = sorted({t["day"] for t in DS.trips})
    lodo, seen = {}, Counter()
    for day in days:
        r = DS.ranked(drop_days=(day,))
        lodo[day] = top(r)
        seen.update(top(r))
    out["leave_one_day_out_top3"] = lodo
    out["top3_appearances_across_days"] = dict(seen.most_common())
    out["stable_in_every_day_drop"] = sorted(k for k, v in seen.items() if v == len(days))
    return L.guard(out, CFG)


if __name__ == "__main__":
    mcp.run()
