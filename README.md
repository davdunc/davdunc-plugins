# davdunc-plugins

[Claude Code](https://claude.ai/claude-code) plugins for equities trading: watchlist generation, trading plans, and historical market data retrieval powered by [Massive.com](https://massive.com) (Polygon.io).

## Plugins

### [market-data](market-data/)

**Type:** Claude Code skill (`/market-data`)

Download historical per-minute and daily OHLCV data from Massive.com flat files for any US-listed ticker. Includes premarket, regular session, and postmarket candles stored locally for analysis.

```
/market-data GSAT 2026-04-01
/market-data AAPL 2026-03-25 2026-03-28
```

- 1-minute bars with full extended hours coverage
- Local caching (won't re-download dates you already have)
- Configurable storage directory

### [equities-watchlist](equities-watchlist/)

**Type:** MCP server

Daily equities watchlist and trading plan generator. Screens for high-volume, high-volatility candidates and builds structured morning briefs.

**Tools:**
- `get_watchlist` — Screen and rank candidates using Finviz + Polygon data (RVOL, ATR, premarket volume)
- `get_trading_plan` — Generate a morning trading plan with market overview, Camarilla pivots, and news
- `get_previous_day_analysis` — Analyze prior session intraday moves from flat file minute data
- `get_calendar_events` — Economic releases, earnings, and ex-dividend dates

**Prompts:**
- `morning_trading_brief` — Full structured brief with bias, if/then trade plans, and stocks to avoid

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- [Massive.com](https://massive.com) subscription (any paid plan with flat file access)
- AWS CLI for flat file downloads
- Python 3.11+

## Configuration

Both plugins use Massive.com credentials. Set via environment variables or a `.env` file:

```bash
# S3 flat file access
export MASSIVE_S3_ACCESS_KEY="your-access-key-id"
export MASSIVE_S3_SECRET_KEY="your-secret-key"

# API access (equities-watchlist)
export POLYGON_API_KEY="your-api-key"

# Optional: Finviz Elite (equities-watchlist screening)
export FINVIZ_API_KEY="your-finviz-key"
```

See each plugin's README for detailed setup instructions.

## Installation

### market-data skill

```bash
# As a Claude Code plugin
claude plugin install davdunc/davdunc-plugins --path market-data

# Or copy directly
cp -r market-data/skills/market-data ~/.claude/skills/
```

### equities-watchlist MCP server

```bash
cd equities-watchlist
pip install -e .

# Register with Claude Code
claude mcp add equities-watchlist -- equities-watchlist
```

## License

MIT
