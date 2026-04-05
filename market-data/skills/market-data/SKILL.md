---
name: market-data
description: Download historical stock market data (minute and daily OHLCV) from Massive.com (Polygon.io) flat files for any US stock ticker and date range. Use when the user asks for stock price data, historical candles, or market data for any date that is NOT today.
argument-hint: "<TICKER> <START_DATE> [END_DATE]"
allowed-tools: Bash Read Write Grep Glob
---

# Retrieve Historical Stock Market Data

Download and store minute-level and daily OHLCV data from Massive.com (Polygon.io) S3 flat files for any US-listed stock.

## Prerequisites

- [Massive.com](https://massive.com) (Polygon.io) subscription with flat file access (any paid plan)
- AWS CLI (`aws`) installed and available on PATH
- Python 3.9+ for timestamp conversion and data verification
- gzip/zcat for decompression (standard on Linux/macOS)

## Arguments

Parse the arguments from: `$ARGUMENTS`

Expected formats:
- `TICKER START_DATE` — single date (e.g., `GSAT 2026-04-01`)
- `TICKER START_DATE END_DATE` — date range (e.g., `GSAT 2026-04-01 2026-04-05`)

Dates must be in `YYYY-MM-DD` format. If the user provides a relative date like "last Thursday", calculate the absolute date from today's date.

**IMPORTANT:** This skill is for historical data only. Do NOT use for current-day data — use the Massive MCP server's `call_api` tool or the REST API for real-time/today's data instead.

## Credentials

The skill needs two S3 credentials from Massive.com. Resolve them in this order of priority:

### 1. Environment variables (preferred)

```bash
MASSIVE_AK="${MASSIVE_S3_ACCESS_KEY:-${MASSIVE_ACCESS_KEY:-}}"
MASSIVE_SK="${MASSIVE_S3_SECRET_KEY:-${MASSIVE_SECRET_ACCESS_KEY:-}}"
```

This supports both naming conventions:
- `MASSIVE_S3_ACCESS_KEY` / `MASSIVE_S3_SECRET_KEY` (used by the equities-watchlist MCP server)
- `MASSIVE_ACCESS_KEY` / `MASSIVE_SECRET_ACCESS_KEY` (standalone convention)

### 2. Dotenv file fallback

If the env vars are not set, check for a `.env` file. Support common formats:

```bash
if [[ -z "$MASSIVE_AK" ]]; then
  for ENV_FILE in "${DOTENV_PATH:-}" "$PWD/.env" "$HOME/.env"; do
    [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]] || continue
    MASSIVE_AK=$(grep -E '^\s*(export\s+)?MASSIVE_S3_ACCESS_KEY\s*=' "$ENV_FILE" \
      | head -1 | sed 's/^[^=]*=\s*//' | sed 's/^["'\'']//' | sed 's/["'\'']\s*$//')
    [[ -z "$MASSIVE_AK" ]] && MASSIVE_AK=$(grep -E '^\s*(export\s+)?MASSIVE_ACCESS_KEY\s*=' "$ENV_FILE" \
      | head -1 | sed 's/^[^=]*=\s*//' | sed 's/^["'\'']//' | sed 's/["'\'']\s*$//')
    MASSIVE_SK=$(grep -E '^\s*(export\s+)?MASSIVE_S3_SECRET_KEY\s*=' "$ENV_FILE" \
      | head -1 | sed 's/^[^=]*=\s*//' | sed 's/^["'\'']//' | sed 's/["'\'']\s*$//')
    [[ -z "$MASSIVE_SK" ]] && MASSIVE_SK=$(grep -E '^\s*(export\s+)?MASSIVE_SECRET_ACCESS_KEY\s*=' "$ENV_FILE" \
      | head -1 | sed 's/^[^=]*=\s*//' | sed 's/^["'\'']//' | sed 's/["'\'']\s*$//')
    [[ -n "$MASSIVE_AK" && -n "$MASSIVE_SK" ]] && break
  done
fi
```

### 3. Fail with instructions

If neither method yields credentials, stop and tell the user:

> Massive.com S3 credentials not found. Set them via one of these methods:
>
> **Option A — Environment variables:**
> ```bash
> export MASSIVE_S3_ACCESS_KEY="your-access-key-id"
> export MASSIVE_S3_SECRET_KEY="your-secret-key"
> ```
>
> **Option B — Dotenv file** (`./.env`, `~/.env`, or set `DOTENV_PATH`):
> ```
> MASSIVE_S3_ACCESS_KEY=your-access-key-id
> MASSIVE_S3_SECRET_KEY=your-secret-key
> ```
>
> Get your S3 credentials from: https://massive.com/dashboard

## S3 Configuration

- **Endpoint:** `https://files.massive.com`
- **Bucket:** `flatfiles`

### Available flat file paths

| Data Type | Path Pattern |
|-----------|-------------|
| Minute aggregates | `us_stocks_sip/minute_aggs_v1/{YYYY}/{MM}/{YYYY-MM-DD}.csv.gz` |
| Daily aggregates | `us_stocks_sip/day_aggs_v1/{YYYY}/{MM}/{YYYY-MM-DD}.csv.gz` |
| Trades | `us_stocks_sip/trades_v1/{YYYY}/{MM}/{YYYY-MM-DD}.csv.gz` |
| Quotes | `us_stocks_sip/quotes_v1/{YYYY}/{MM}/{YYYY-MM-DD}.csv.gz` |

This skill downloads **minute aggregates** and **daily aggregates** by default. Trades and quotes are available but significantly larger — only download those if the user specifically requests tick-level data.

### CSV format (minute and daily aggregates)

```
ticker,volume,open,close,high,low,window_start,transactions
```

- `window_start` is Unix epoch in **nanoseconds** (divide by 1e9 for seconds)
- All timestamps are in UTC
- Minute files include all sessions: premarket (4:00 AM ET), regular (9:30 AM-4:00 PM ET), and postmarket (4:00-8:00 PM ET)

## Data storage

Data is stored under a configurable base directory:

```bash
DATA_DIR="${MARKET_DATA_DIR:-$HOME/market_data}"
```

Users can override by setting the `MARKET_DATA_DIR` environment variable.

### File naming convention

```
{DATA_DIR}/{TICKER}/{TICKER}_{YYYY-MM-DD}_minute.csv   — per-minute OHLCV, all sessions
{DATA_DIR}/{TICKER}/{TICKER}_{YYYY-MM-DD}_daily.csv    — daily OHLCV (single row, no header)
```

## Procedure

### Step 1: Parse arguments and validate

Extract TICKER (uppercase), START_DATE, and optional END_DATE from `$ARGUMENTS`. If only one date is given, set END_DATE = START_DATE.

Generate the list of weekday dates to download. Skip weekends (Saturday/Sunday). Use:

```bash
python3 -c "
from datetime import date, timedelta
start = date.fromisoformat('$START_DATE')
end = date.fromisoformat('$END_DATE')
d = start
while d <= end:
    if d.weekday() < 5:
        print(d.isoformat())
    d += timedelta(days=1)
"
```

### Step 2: Create local directory

```bash
mkdir -p "$DATA_DIR/$TICKER"
```

### Step 3: Download and extract data

For each date in the range:

1. **Check if data already exists locally.** If `$DATA_DIR/$TICKER/${TICKER}_${DATE}_minute.csv` already exists and has more than 1 line (header + data), skip that date and report it was cached.

2. **Download the full-market minute file** to a temp location:
   ```bash
   AWS_ACCESS_KEY_ID="$MASSIVE_AK" AWS_SECRET_ACCESS_KEY="$MASSIVE_SK" \
     aws s3 cp "s3://flatfiles/us_stocks_sip/minute_aggs_v1/${YYYY}/${MM}/${DATE}.csv.gz" \
     "/tmp/${DATE}_minute_all.csv.gz" --endpoint-url https://files.massive.com
   ```

3. **Extract ticker-specific rows** (include header):
   ```bash
   zcat "/tmp/${DATE}_minute_all.csv.gz" | head -1 > "$DATA_DIR/$TICKER/${TICKER}_${DATE}_minute.csv"
   zcat "/tmp/${DATE}_minute_all.csv.gz" | grep "^${TICKER}," >> "$DATA_DIR/$TICKER/${TICKER}_${DATE}_minute.csv"
   ```

4. **Download and extract daily aggregate:**
   ```bash
   AWS_ACCESS_KEY_ID="$MASSIVE_AK" AWS_SECRET_ACCESS_KEY="$MASSIVE_SK" \
     aws s3 cp "s3://flatfiles/us_stocks_sip/day_aggs_v1/${YYYY}/${MM}/${DATE}.csv.gz" \
     "/tmp/${DATE}_day_all.csv.gz" --endpoint-url https://files.massive.com
   zcat "/tmp/${DATE}_day_all.csv.gz" | grep "^${TICKER}," > "$DATA_DIR/$TICKER/${TICKER}_${DATE}_daily.csv"
   ```

5. **Clean up temp files:**
   ```bash
   rm -f "/tmp/${DATE}_minute_all.csv.gz" "/tmp/${DATE}_day_all.csv.gz"
   ```

### Step 4: Verify and report

After all dates are processed, report:

1. List all files created/cached with sizes and row counts
2. For each date, show the time range covered (first/last bar in ET) and session summary:
   - Premarket: first/last bar, high/low
   - Regular session: open/high/low/close, volume
   - Postmarket: first/last bar, high/low
3. Show the daily OHLCV summary for each date

Use this Python snippet to convert timestamps to Eastern Time (auto-detects EST/EDT):

```python
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except ImportError:
    ET = timezone(timedelta(hours=-4))  # fallback, assumes EDT

dt = datetime.fromtimestamp(int(window_start) / 1e9, tz=timezone.utc).astimezone(ET)
```

### Error handling

- **S3 download fails for a date:** Warn `No data available for {DATE} (non-trading day or holiday)` and continue.
- **Ticker has no rows:** Warn `No bars found for {TICKER} on {DATE}. Ticker may not have traded or may be invalid.`
- **Credentials missing:** Show the setup instructions from the Credentials section above.
- **AWS CLI not installed:** Tell the user to install it: `pip install awscli` or via their package manager.
