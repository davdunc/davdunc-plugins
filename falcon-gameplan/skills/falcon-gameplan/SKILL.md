---
name: falcon-gameplan
description: >-
  MorningGamePlan engine — the data/analytics tools behind the daily pre-market
  trading plan. USE WHEN building a morning game plan, computing SPY gamma
  exposure (GEX) regime, Camarilla pivots for a ticker, scanning pre-market
  Finviz gappers, detecting reverse-split + ATM dilution combos, or looking up
  recent SEC EDGAR filings. Packages the falcon toolchain as a plugin so any
  machine has it without local ~/falcon/dashboard scripts. NOT FOR order
  execution (that is DAS/dastrader) or historical bulk OHLCV (use market-data).
---

# falcon-gameplan

Pre-market intelligence tools for the MorningGamePlan workflow. Each tool is a
self-contained script under `Tools/`, run via the plugin venv
(`Tools/.venv/bin/python`). Output is markdown/JSON for direct paste into the
game plan.

## Setup (once per machine)

```bash
cd "$CLAUDE_PLUGIN_ROOT/Tools"
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# Reuse the falcon org libraries (cloned to ~/src/TradingAsBuddies):
.venv/bin/pip install -e ~/src/TradingAsBuddies/falcon-core \
                       -e ~/src/TradingAsBuddies/falcon-screener \
                       -e ~/src/TradingAsBuddies/sangre-signal
```

Keys read from `~/.claude/.env`: `POLYGON_API_KEY`, `FINVIZ_API_KEY`,
`ALPHAVANTAGE_API_KEY`. (Finviz export endpoint 301-redirects — fetch with `-L`.)

## Tools

| Tool | Status | Command |
|------|--------|---------|
| **spy_gex** | BUILD | `python Tools/spy_gex.py --max-dte 14` — SPY Gamma Exposure regime + magnet strikes + zero-gamma flip (HARD RULE for the macro block) |
| **camarilla** | BUILD | `python Tools/camarilla.py TICKER` — Camarilla S3/S4/R3/R4 pivots from prior-day OHLCV |
| **edgar** | BUILD | `python Tools/edgar.py TICKER --days 14` — recent SEC filings (8-K/S-3/424B) for catalyst + dilution detection |
| **screen_gappers** | REUSE falcon-screener | pre-market gappers >3%, vol >500K |
| **dilution_scan** | REUSE sangre-signal | R-S + ATM combo → Day-2/Day-3 short watch (NEVER Day-1) |
| **quote / ohlcv** | REUSE falcon-core | Polygon quotes + daily bars |

## Gotchas

- **GEX regime drives setup bias:** positive GEX → fade/mean-revert; negative GEX → trends extend. Magnet strikes are intraday targets/triggers.
- **Dilution combo is Day-2/Day-3 ONLY** — never short Day-1 of the halt-runner.
- **DAS Market Viewer** (Phase 8) lives in `dastrader`/falcon-core, not here — and needs DAS reachable (WSL mirrored-networking).
- Tools must work offline-degraded: if a data source is down, emit a clear `[UNAVAILABLE: reason]` line rather than failing the whole plan.
