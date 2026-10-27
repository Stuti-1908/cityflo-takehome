# Decision record: which routes were late this week

For Priya, Friday review. Week of 2026-08-03 to 2026-08-09, 5,250 trips
kept of 5,292, 40 routes. "Excess" is arrival (normalised to +05:30)
minus scheduled departure, minus the runtime the trip is measured
against. All rules are in `config.json`; every number below came from
the `cityflo-ops` MCP tools.

## Verdict

**Four routes are LATE, the other 36 are ON_TIME.** A route is LATE if
its `wd_median` is at least 4.0 min. `wd_median` is the median excess
after removing the route's single worst day.

**Worst three**
1. **R-33**: wd_median 5.0, 47% of trips over 5 min late
2. **R-26**: wd_median 4.0, 43% over 5 min
3. **R-37**: wd_median 4.0, 40% over 5 min

**#4 R-31 is LATE but borderline**: wd_median 4.0, 33% over 5 min and
no trip over 10 min late. R-12 is **ON_TIME** (wd_median 1.5).

R-33 and R-26 stay in the worst three under every drop-one-day run.
The third slot is the soft one: R-37 holds it in 5 of 7 runs, R-31 in 2.

### All 40 routes

Columns: rank, route, trips kept, wd_median, median, share of trips
over 5 min and over 10 min late, p90 excess, verdict. Order is
wd_median, then share over 5 min, then p90.

| # | route | n | wd_med | median | >5m | >10m | p90 | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | R-33 | 104 | 5.0 | 5.0 | 47% | 8% | 10 | LATE |
| 2 | R-26 | 103 | 4.0 | 4.0 | 43% | 4% | 9 | LATE |
| 3 | R-37 | 105 | 4.0 | 4.0 | 40% | 5% | 9 | LATE |
| 4 | R-31 | 112 | 4.0 | 4.0 | 33% | 0% | 8 | LATE |
| 5 | R-17 | 147 | 3.0 | 3.0 | 28% | 5% | 8 | ON_TIME |
| 6 | R-40 | 152 | 3.0 | 3.0 | 22% | 2% | 7 | ON_TIME |
| 7 | R-08 | 126 | 3.0 | 3.0 | 21% | 2% | 7 | ON_TIME |
| 8 | R-15 | 119 | 2.5 | 3.0 | 21% | 3% | 8 | ON_TIME |
| 9 | R-09 | 146 | 2.0 | 2.0 | 23% | 3% | 7 | ON_TIME |
| 10 | R-34 | 124 | 2.0 | 3.0 | 23% | 1% | 8 | ON_TIME |
| 11 | R-27 | 143 | 2.0 | 2.0 | 22% | 3% | 8 | ON_TIME |
| 12 | R-07 | 147 | 2.0 | 3.0 | 22% | 2% | 7 | ON_TIME |
| 13 | R-21 | 124 | 2.0 | 2.0 | 21% | 0% | 7 | ON_TIME |
| 14 | R-18 | 154 | 2.0 | 2.0 | 21% | 2% | 7 | ON_TIME |
| 15 | R-05 | 105 | 2.0 | 2.0 | 19% | 3% | 7 | ON_TIME |
| 16 | R-19 | 125 | 2.0 | 3.0 | 18% | 2% | 7 | ON_TIME |
| 17 | R-11 | 137 | 2.0 | 2.0 | 17% | 3% | 7 | ON_TIME |
| 18 | R-20 | 145 | 2.0 | 2.0 | 17% | 3% | 6 | ON_TIME |
| 19 | R-22 | 112 | 2.0 | 2.0 | 16% | 3% | 6 | ON_TIME |
| 20 | R-02 | 105 | 2.0 | 2.0 | 14% | 0% | 6 | ON_TIME |
| 21 | R-39 | 154 | 1.5 | 2.0 | 16% | 2% | 6 | ON_TIME |
| 22 | R-12 | 112 | 1.5 | 2.0 | 13% | 2% | 6 | ON_TIME |
| 23 | R-35 | 132 | 1.0 | 2.0 | 24% | 16% | 48 | ON_TIME |
| 24 | R-03 | 103 | 1.0 | 2.0 | 20% | 0% | 7 | ON_TIME |
| 25 | R-38 | 146 | 1.0 | 1.0 | 16% | 2% | 7 | ON_TIME |
| 26 | R-32 | 133 | 1.0 | 1.0 | 16% | 1% | 7 | ON_TIME |
| 27 | R-25 | 139 | 1.0 | 1.0 | 14% | 2% | 7 | ON_TIME |
| 28 | R-10 | 126 | 1.0 | 1.0 | 14% | 2% | 6 | ON_TIME |
| 29 | R-36 | 132 | 1.0 | 1.0 | 10% | 0% | 5 | ON_TIME |
| 30 | R-01 | 153 | 1.0 | 1.0 | 8% | 2% | 5 | ON_TIME |
| 31 | R-24 | 146 | 0.0 | 1.0 | 11% | 2% | 6 | ON_TIME |
| 32 | R-28 | 151 | 0.0 | 1.0 | 10% | 1% | 5 | ON_TIME |
| 33 | R-23 | 132 | 0.0 | 0.0 | 6% | 0% | 5 | ON_TIME |
| 34 | R-16 | 146 | 0.0 | 0.0 | 5% | 0% | 4 | ON_TIME |
| 35 | R-14 | 118 | -1.0 | 0.0 | 31% | 10% | 10 | ON_TIME |
| 36 | R-04 | 144 | -1.0 | 0.0 | 10% | 0% | 5 | ON_TIME |
| 37 | R-30 | 147 | -1.0 | -1.0 | 7% | 1% | 5 | ON_TIME |
| 38 | R-13 | 133 | -1.0 | -1.0 | 6% | 0% | 4 | ON_TIME |
| 39 | R-29 | 151 | -1.0 | -1.0 | 4% | 0% | 4 | ON_TIME |
| 40 | R-06 | 117 | -2.0 | -2.0 | 5% | 0% | 3 | ON_TIME |

R-14 (#35) is ON_TIME only because of the REC-114 call below. R-35 (#23)
is ON_TIME only because of the worst-day call below. Read both sections
before defending those two.

## Limits that apply to every call

- One week of data. Cell sizes are 15 to 22 trips per route-day.
- Costs are in trips, not rupees. I have no refund or incentive figures,
  so "cost" below is the number of trips behind the call.
- Reading the 4xx series as R-14 and R-27 (series is the last two digits
  of the vehicle class) is Priya's reading. The export has no class
  column, so the data cannot confirm it.
- The ops log has no dates or route ids and says it is last week's.

---

## 1. Data cleaning: drop 42 rows, keep 59 repeated-arrival pairs

**The rule.** Normalise every arrival to +05:30. Drop a trip if its
arrival does not parse (24 rows, all the literal `08:60`, a dropped
unit's placeholder) or if arrival is before departure after
normalisation (18 rows). Do not de-duplicate trips that share a route
and arrival minute: 59 such pairs remain (one of the original 60 lost a
member to the sentinel drop). The single `+00:00` row is a valid trip
that normalises to excess -2.

**The case it breaks on.** `T1-00417` (R-04, 2026-08-05) is dropped
because it arrived 5 min before it departed. It may be a real trip with
a bad clock, and so may the 17 like it. `T1-00136` (R-01, 24 sentinel
rows in all) is dropped too, and a bus that fell off the network
mid-trip is exactly the bus most likely to be late. For the repeats,
`T1-00059` and `T1-00066` (R-01, both arrive 07:02 on 08-05) look like
one unit stamping twice. I keep the rule because it moves nothing that
matters: keeping the 18 negative rows leaves the LATE set and the worst
three unchanged, and de-duplicating all 59 pairs also leaves them
unchanged (largest wd_median shift 0.5). The repeats have a median
excess of +2.0, like everything else.

**The cost, and who pays.** 42 of 5,292 rows (0.8%) are out. The
largest losses are R-27 (4 of 147) and R-29 and R-04 (3 each). Of the
four LATE routes, R-31 and R-37 lost nothing, R-26 lost 2 and R-33
lost 1. The risk is quiet: if the 24 dark-unit trips were the slow
ones, the depots that lose a bus to the network gap look better than
they are. Priya pays if a depot head shows a dark-bus trip she dropped.

**What would change my mind.** Ops confirming that `08:60` marks a bus
that was live and late (then count those 24 as late). Any route losing
more than 2% of its trips to cleaning. Evidence that a repeated pair is
one physical arrival counted twice, for example the same vehicle id on
both rows.

---

## 2. REC-114: schedule_v2 all week on R-14, "no change" honoured on R-27

**The rule.** A route in `schedule_v2.csv` is measured against its
revised runtime for the whole week, unless its note is `no change`.
That puts R-14 on 53 min for all 118 kept trips. R-27 ("no change")
stays on each trip's own `scheduled_runtime_min`. It is the
`skip_v2_notes` list in `config.json`.

**The case it breaks on.** `T1-01677` (R-14, Mon 08-03, export 35 min,
took 47): the export says +12, our rule says -6, so a trip that ran 12
minutes long counts as early. The rule also does not help every R-14
trip: `T1-01778` (Sun 08-09, export 55, took 72) is +19 under v2 and
+17 under the export. On R-27, `T1-03452` (Thu 08-06, export 55, took
58) is +3 under our rule and would be +13 under v2's 45. I keep the rule
for R-14 because its median elapsed time is 53.0 both before and after
Aug 5, while its export runtimes average about 45. The export understates
the route all week, and v2's 53 matches what the buses do. I keep it for
R-27 because v2 says "no change", and R-27's export runtimes rose from a
mean of 44.5 (Mon to Wed) to 47.5 (Thu to Sun) as its elapsed time rose.
That fits a timetable change, but it is a hypothesis and not proof.

**The cost, and who pays.** R-14 under v2: 37 of 118 trips over 5 min
(31%) and 12 over 10 min (10%). Under the export it would be 85 (72%)
and 28 (24%), and it would be the #1 worst route. If v2 is the wrong
yardstick, 12 to 28 trips more than 10 min late go unflagged, and the
refund queue and app-store ratings pay. If it is right and we flagged
R-14, its depot head loses the on-time incentive for a route that runs
as its timetable now says. R-27 under v2 would show 39 trips over 10 min
(27%); under its own runtimes it shows 5 (3%). R-27 is ON_TIME either
way (wd_median 2.0 vs 3.0), so that choice changes its ranking, not its
verdict. I made the R-27 change after seeing R-27's numbers.

**What would change my mind.** Ops saying REC-114 applies only to trips
from 08-05, or that the review's R-14 figures use a runtime other than
53 (then R-14 moves toward the export view). Ops confirming the R-27
timetable did not change on Thursday, so its Thu to Sun slowdown is
real: v2's 45 would then be the right yardstick (wd_median 3.0, still
under the line, but 27% of trips over 10 min).

---

## 3. The verdict line: wd_median at least 4.0, and the R-35 Wednesday

**The rule.** `wd_median`: take each route's daily median excess, drop
every trip from the day with the highest one (earliest day on a tie),
and take the median of the rest. LATE if that is 4.0 min or more. No
route is named in the rule.

**The case it breaks on.** R-35 on Wed 08-05: all 19 trips are late, the
day's median is +52, and `T1-04521` (12:21, scheduled 35, took 96) is
+61. The rule drops that day, so R-35 reads 1.0 and ON_TIME, though its
mean is 8.1, its p90 is 48 and 21 trips (16%) are over 10 min late, the
worst p90 of any route. The ops log's Wed entries are a diversion
(~35 min, AM) and a city-wide crowd. R-35 is the only route that moved,
by about 50 min all day, so neither tag explains it. I keep the rule
because a one-day failure is an incident, not a weekly pattern, and
Priya's verdict is weekly. The line itself is knife-edge: 3.5 and 4.0
give the same four routes, but 4.5 leaves only R-33.

**The cost, and who pays.** Clearing R-35 means 19 trips on one day, 21
trips over 10 min late in all, went into no verdict. If that outage
repeats, the riders and the refund queue pay for it. Flagging R-35 on
the mean would instead put a good depot head at risk over one bad day.
`worst_day_median` is in every route's output, so Priya can report the
Wednesday as a separate incident without it counting as a verdict.

**What would change my mind.** A second bad day on R-35 (it would
survive the drop and flag as LATE). Any route with two or more bad days
in a week, since the rule drops only one. A weekly review that wants
incidents counted, in which case I would use the median alone.

---

## 4. Worst three: the tie-break between R-26, R-37 and R-31

**The rule.** Rank by wd_median, then share of trips over 5 min late,
then p90. R-26, R-37 and R-31 are all at 4.0, so the order is 43%, 40%,
33% over 5 min (44, 42 and 37 trips). That gives R-26 #2, R-37 #3, R-31
#4.

**The case it breaks on.** R-31 has 37 trips over 5 min and none over 10
min, yet it is flagged LATE. R-37 has 5 trips over 10 min and R-26 has 4,
so ranking by the over-10-min count would put R-37 ahead of R-26.
Dropping Mon 08-03 or Fri 08-07 lets R-31 into the worst three in place
of R-37. I keep the rule because it is stated and re-runnable, not a hand pick.
It was fixed after the earlier leaderboard had already shown these
three tied, so it is not a blind choice.

**The cost, and who pays.** The #3 and #4 gap is 5 trips over 5 min
(42 vs 37). The R-37 depot head carries the "worst three" label to the
regional review on that gap, and R-31's depot head keeps a LATE flag
with no trip over 10 min late. If the order is wrong, Priya has to
explain why the stronger-looking route was named.

**What would change my mind.** A second week where R-31 beats R-37 on
the same rule. Priya telling me the incentive is paid on over-10-min
trips, which would put the over-10-min share ahead of the over-5-min
share in the tie-break.

---

## 5. Directive (a): no free text or phone numbers in any output

**The rule.** The ops log reaches tool output only as `{day, time,
categories}` with categories from a closed list in `config.json`
(weather_diversion, crowd_event, vehicle, rider_complaint, staffing,
normal). Every tool result passes a guard that raises if it contains
a phone-like number (+country code, or 10 or more digits in a row) or
any text from an ops-log line. Tests cover both.

**The case it breaks on.** The Wed 06:40 log line becomes
`weather_diversion`, with no route. So when R-35's Wednesday is
questioned, Priya cannot point to a log entry that explains it, only a
tag that doesn't name the route. The guard is also text matching: it
would miss a paraphrase and could block a harmless string that quotes a
log line. I keep it because directive (a) was signed off, and no
verdict depends on the log text.

**The cost, and who pays.** All 6 log lines survive only as a tag, a day
and a time. The verdicts use none of them. Priya pays in credibility if a
depot head asks what the log said about their route, because she can
cite only a day, a time and a category. Riders are protected: there are
no phone numbers or complaint text in this export, and none can reach
output.

**What would change my mind.** Ops adding route or ticket ids to the log
(then tag the line with the id). A complaint-ticket export being added
to the tool, which would need its own redaction tests.
