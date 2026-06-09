# falcon-gameplan

MorningGamePlan engine, packaged as a Claude Code plugin so any machine gets the
toolchain via the `davdunc-plugins` marketplace instead of machine-local
`~/falcon/dashboard` scripts.

## What it provides

- **spy_gex** — SPY Gamma Exposure regime, magnet strikes, zero-gamma flip (yfinance + BSM)
- **camarilla** — Camarilla S3/S4/R3/R4 pivots from prior-day OHLCV
- **edgar** — recent SEC EDGAR filings (8-K / S-3 / 424B) for catalysts + dilution
- **screen_gappers** — pre-market Finviz gappers (reuses `falcon-screener`)
- **dilution_scan** — reverse-split + ATM combo → Day-2/Day-3 short watch (reuses `sangre-signal`)
- **quote / ohlcv** — Polygon market data (reuses `falcon-core`)

## Install

```bash
/plugin install falcon-gameplan@davdunc-plugins
cd "$CLAUDE_PLUGIN_ROOT/Tools" && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e ~/src/TradingAsBuddies/{falcon-core,falcon-screener,sangre-signal}
```

Requires `POLYGON_API_KEY`, `FINVIZ_API_KEY`, `ALPHAVANTAGE_API_KEY` in `~/.claude/.env`.

See `skills/falcon-gameplan/SKILL.md` for tool details and gotchas.
