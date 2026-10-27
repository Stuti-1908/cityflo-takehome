"""Route-lateness logic for the Cityflo ops export. No MCP dependency.

Lateness ("excess") for a trip = elapsed minutes (arrival normalised to
the configured UTC offset, minus scheduled departure) minus the runtime
it is measured against. Every rule below is read from config.json.
"""
import copy
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent
FMT = "%Y-%m-%d %H:%M"
SCHEDULE_MODES = ("all_week", "from_effective", "off")


def load_config(path=None):
    with open(path or ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)


def _offset_min(s):
    sign = 1 if s[0] == "+" else -1
    h, m = s[1:].split(":")
    return sign * (int(h) * 60 + int(m))


def _p90(xs):
    xs = sorted(xs)
    return xs[int(0.9 * (len(xs) - 1))]


def _r(x, nd=1):
    return None if x is None else round(x, nd)


class Dataset:
    """Cleaned trips plus the rules that produced them."""

    def __init__(self, cfg):
        self.cfg = cfg
        d = ROOT / cfg["data_dir"]
        self.v2 = {}
        with open(d / "schedule_v2.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.v2[r["route"]] = (float(r["revised_runtime_min"]), r["effective_date"], r["note"].strip())
        target = _offset_min(cfg["tz_normalize_to"])
        self.trips, self.dropped, self.raw_n = [], [], 0
        self.tz_counts = Counter()
        with open(d / "trips.csv", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.raw_n += 1
                self.tz_counts[r["tz_offset"]] += 1
                dep = datetime.strptime(r["scheduled_departure"], FMT)
                try:
                    arr = datetime.strptime(r["actual_arrival"], FMT)
                except ValueError:
                    if cfg["cleaning"]["drop_unparseable_arrival"]:
                        self.dropped.append((r["trip_id"], r["route"], "unparseable_arrival"))
                        continue
                    raise
                arr += timedelta(minutes=target - _offset_min(r["tz_offset"]))
                el = (arr - dep).total_seconds() / 60
                if el < 0 and cfg["cleaning"]["drop_negative_elapsed"]:
                    self.dropped.append((r["trip_id"], r["route"], "negative_elapsed"))
                    continue
                self.trips.append({
                    "trip_id": r["trip_id"], "route": r["route"],
                    "dep": dep, "arr": arr, "day": dep.date().isoformat(),
                    "elapsed": el, "export_runtime": float(r["scheduled_runtime_min"]),
                    "tz_raw": r["tz_offset"], "arrival_raw": r["actual_arrival"],
                })
        self.routes = sorted({t["route"] for t in self.trips})
        arr_pairs = defaultdict(list)
        for t in self.trips:
            arr_pairs[(t["route"], t["arrival_raw"])].append(t["trip_id"])
        self.repeat_pairs = {k: v for k, v in arr_pairs.items() if len(v) > 1}
        self.by_id = {t["trip_id"]: t for t in self.trips}

    # -- schedule basis ------------------------------------------------
    def mode_for(self, route):
        s = self.cfg["schedule"]
        return s.get("route_overrides", {}).get(route, s["mode"])

    def v2_active(self, route):
        """v2 applies only to routes whose note is not a configured 'skip' note."""
        if route not in self.v2:
            return False
        skip = {n.lower() for n in self.cfg["schedule"].get("skip_v2_notes", [])}
        return self.v2[route][2].lower() not in skip

    def basis(self, t):
        """(runtime minutes, label) the trip is measured against."""
        mode = self.mode_for(t["route"])
        if mode != "off" and self.v2_active(t["route"]):
            minutes, eff, _ = self.v2[t["route"]]
            if mode == "all_week" or t["day"] >= eff:
                return minutes, "schedule_v2"
        return t["export_runtime"], "export"

    def excess(self, t):
        return t["elapsed"] - self.basis(t)[0]

    # -- statistics ----------------------------------------------------
    def route_stats(self, route, drop_days=()):
        ts = [t for t in self.trips if t["route"] == route and t["day"] not in drop_days]
        if not ts:
            return None
        xs = [self.excess(t) for t in ts]
        days = defaultdict(list)
        for t, x in zip(ts, xs):
            days[t["day"]].append(x)
        day_med = {d: median(v) for d, v in days.items()}
        worst_day = min(d for d, m in day_med.items() if m == max(day_med.values()))
        rest = [x for d, v in days.items() if d != worst_day for x in v]
        wd = median(rest) if rest else median(xs)
        n = len(xs)
        s = {
            "route": route, "n": n,
            "mean": mean(xs), "median": median(xs), "wd_median": wd,
            "p90": _p90(xs),
            "pct_over_5m": 100 * sum(x > 5 for x in xs) / n,
            "pct_over_10m": 100 * sum(x > 10 for x in xs) / n,
            "worst_day": worst_day, "worst_day_median": day_med[worst_day],
            "day_medians": {d: day_med[d] for d in sorted(day_med)},
        }
        v = self.cfg["verdict"]
        s["late"] = s[v["metric"]] >= v["late_threshold_min"]
        return s

    def rank_key(self, s):
        v = self.cfg["verdict"]
        return tuple(-s[k] for k in [v["metric"]] + v["tie_breakers"]) + (s["route"],)

    def ranked(self, drop_days=(), metric=None):
        stats = [self.route_stats(r, drop_days) for r in self.routes]
        stats = [s for s in stats if s]
        if metric and metric != self.cfg["verdict"]["metric"]:
            tb = self.cfg["verdict"]["tie_breakers"]
            return sorted(stats, key=lambda s: tuple(-s[k] for k in [metric] + tb) + (s["route"],))
        return sorted(stats, key=self.rank_key)

    def with_schedule(self, mode=None, overrides=None, skip_notes=None):
        cfg = copy.deepcopy(self.cfg)
        if mode:
            cfg["schedule"]["mode"] = mode
        if overrides is not None:
            cfg["schedule"]["route_overrides"] = overrides
        if skip_notes is not None:
            cfg["schedule"]["skip_v2_notes"] = skip_notes
        return Dataset(cfg)


# -- ops log: structured tags only (directive a) ------------------------
LOG_LINE = re.compile(r"^(\w{3})\s+(\d{2}:\d{2})\s+(.*)$")


def ops_log_tags(cfg):
    out = []
    path = ROOT / cfg["data_dir"] / "ops_log.txt"
    if not path.exists():
        return out
    cats = cfg["ops_log_categories"]
    for line in path.read_text(encoding="utf-8").splitlines():
        m = LOG_LINE.match(line.strip())
        if not m:
            continue
        day, hhmm, text = m.groups()
        low = text.lower()
        tags = [c for c, kws in cats.items() if c != "normal" and any(k in low for k in kws)]
        if not tags and any(k in low for k in cats.get("normal", [])):
            tags = ["normal"]
        out.append({"day": day, "time": hhmm, "categories": tags or ["uncategorised"]})
    return out


# -- output guard (directive a) -----------------------------------------
_PII = re.compile(r"\+\d{1,3}[\s-]?\d{8,}|\b\d{10,}\b")


def guard(obj, cfg):
    """Raise if any string in a tool result looks like PII or a raw log line."""
    path = ROOT / cfg["data_dir"] / "ops_log.txt"
    lines = []
    if path.exists():
        lines = [l.strip().lower() for l in path.read_text(encoding="utf-8").splitlines() if len(l.strip()) > 12]

    def walk(o):
        if isinstance(o, str):
            if _PII.search(o):
                raise ValueError("blocked: PII-like pattern in output")
            low = o.lower()
            if any(l in low or (len(low) > 12 and low in l) for l in lines):
                raise ValueError("blocked: raw ops-log text in output")
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(k)
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)

    walk(obj)
    return obj
