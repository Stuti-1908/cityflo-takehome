# Cityflo on-time MCP server

MCP server (stdio) that answers: which routes were late this week, by how
much, and which three were worst. Rules live in `config.json`; logic in
`lateness.py`; tools in `server.py`.

## Run

```
python -m venv .venv
.venv\Scripts\python -m pip install "mcp>=1.2,<2" pytest
claude mcp add cityflo-ops -- "%CD%\.venv\Scripts\python.exe" "%CD%\server.py"
.venv\Scripts\python -m pytest
```

`data/` (the bundle) is committed, so a clone runs as-is.

## Tools

| tool | use |
|---|---|
| `data_quality_report` | rows dropped (with ids), tz offsets, ops-log tags |
| `route_lateness` | one route's stats and verdict |
| `rank_routes` | LATE list and worst three |
| `explain_trip` | how one trip was kept/dropped and measured |
| `sensitivity_check` | worst three under other rules and day drops |

Lateness = elapsed (arrival normalised to +05:30) minus the runtime the
trip is measured against. LATE if `wd_median >= 4.0` (median after
removing each route's single worst day). Reasons are in `DECISION.md`.
