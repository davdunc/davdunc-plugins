# market-data

A [Claude Code](https://claude.ai/claude-code) plugin that downloads historical US stock market data from [Massive.com](https://massive.com) (formerly Polygon.io) flat files.

Retrieves per-minute OHLCV candles (including premarket, regular session, and postmarket) and daily aggregates for any US-listed ticker, stored locally for analysis.

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- [Massive.com](https://massive.com) subscription with flat file / S3 access (any paid plan)
- AWS CLI (`aws`)
- Python 3.9+

## Installation

### From this repository

```bash
claude plugin install davdunc/davdunc-plugins --path market-data
```

### Manual

Copy the `market-data` directory into your Claude Code plugins or skills folder:

```bash
# As a plugin (recommended)
cp -r market-data ~/.claude/plugins/market-data

# Or as a standalone skill
mkdir -p ~/.claude/skills
cp -r market-data/skills/market-data ~/.claude/skills/
```

## Configuration

Set your Massive.com S3 credentials using either method:

### Environment variables (recommended)

```bash
export MASSIVE_S3_ACCESS_KEY="your-access-key-id"
export MASSIVE_S3_SECRET_KEY="your-secret-key"
```

Also supports the alternate naming convention:
```bash
export MASSIVE_ACCESS_KEY="your-access-key-id"
export MASSIVE_SECRET_ACCESS_KEY="your-secret-key"
```

### Dotenv file

Add to `./.env` or `~/.env` (or set `DOTENV_PATH`):

```
MASSIVE_S3_ACCESS_KEY=your-access-key-id
MASSIVE_S3_SECRET_KEY=your-secret-key
```

### Optional settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MARKET_DATA_DIR` | `~/market_data` | Where downloaded data is stored |
| `DOTENV_PATH` | `./.env` then `~/.env` | Path to dotenv file for credentials |

## Usage

```
/market-data GSAT 2026-04-01
/market-data AAPL 2026-03-25 2026-03-28
/market-data NVDA 2026-01-02 2026-01-31
```

The skill will:
1. Download full-market minute and daily flat files from Massive.com S3
2. Extract only the requested ticker's rows
3. Store them locally (skips dates already cached)
4. Report session summaries (premarket/regular/postmarket) with OHLCV data

### Output structure

```
~/market_data/
  GSAT/
    GSAT_2026-04-01_minute.csv    # 1-min bars, all sessions
    GSAT_2026-04-01_daily.csv     # Daily OHLCV
    GSAT_2026-04-02_minute.csv
    GSAT_2026-04-02_daily.csv
```

### CSV format

```csv
ticker,volume,open,close,high,low,window_start,transactions
GSAT,100.000000,67.680000,67.680000,67.680000,67.680000,1775042760000000000,1
```

| Field | Description |
|-------|-------------|
| `ticker` | Stock symbol |
| `volume` | Share volume for the bar |
| `open` | Opening price |
| `close` | Closing price |
| `high` | High price |
| `low` | Low price |
| `window_start` | Unix epoch in **nanoseconds** (UTC) |
| `transactions` | Number of trades in the bar |

Minute files include all extended-hours sessions (premarket 4:00 AM through postmarket 8:00 PM ET).

## Related

- **[equities-watchlist](../equities-watchlist/)** — MCP server for daily watchlist generation, trading plans, Camarilla pivots, and intraday analysis. Uses the same Massive.com flat files for automated screening.
- **[Massive MCP Server](https://github.com/massive-com/mcp_massive)** — Official Massive.com MCP server for real-time and historical API queries (not flat files).

## Data source

[Massive.com flat files](https://massive.com/flat-files) via S3-compatible endpoint. Covers all US SIP (consolidated tape) data:

| Type | Description | Downloaded by default |
|------|-------------|----------------------|
| Minute aggregates | 1-min OHLCV, all sessions | Yes |
| Daily aggregates | Daily OHLCV | Yes |
| Trades | Tick-level trade data | No (request explicitly) |
| Quotes | NBBO quote data | No (request explicitly) |

## License

MIT
