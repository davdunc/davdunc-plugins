# Data Sources

## Finviz Elite Export API

- **Purpose:** Pre-market gap screener, ticker discovery, fundamentals + technicals snapshot
- **Base endpoint:** `https://elite.finviz.com/export`
- **Auth:** Append `&auth=FINVIZ_API_KEY` (never log the token)
- **Response format:** CSV with header row; parse with `csv.DictReader`
- **API key env var:** `FINVIZ_API_KEY` (from `~/.claude/.env`)

### URL Construction

```
https://elite.finviz.com/export?v=111&f={filters}&ft=4&c={columns}&auth={FINVIZ_API_KEY}
```

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `v` | View preset (111 = overview) | `v=111` |
| `f` | Comma-separated filter codes | `f=geo_usa,sh_price_o3,ta_gap_u3` |
| `ft` | Filter type (4 = strict) | `ft=4` |
| `c` | Comma-separated column IDs | `c=1,65,61,67` |
| `auth` | API token | `auth=KEY` |

### Common Filter Codes

| Filter | Code | Notes |
|--------|------|-------|
| US stocks only | `geo_usa` | Always include |
| Price over $3 | `sh_price_o3` | Sweet-spot floor |
| Price under $50 | `sh_price_u50` | Sweet-spot ceiling |
| Avg volume > 500K | `sh_avgvol_o500` | Liquidity floor |
| Gap up > 3% | `ta_gap_u3` | Pre-market gapper |
| Gap up > 5% | `ta_gap_u5` | Strong gapper |

### Key Column IDs (trading-relevant)

| ID | Column | Category |
|----|--------|----------|
| 1 | Ticker | identity |
| 2 | Company | identity |
| 49 | Average True Range | technical |
| 61 | Gap | price-volume |
| 63 | Average Volume | price-volume |
| 64 | Relative Volume | price-volume |
| 65 | Price | price-volume |
| 66 | Change | price-volume |
| 67 | Volume | price-volume |
| 68 | Earnings Date | events |
| 71 | After-Hours Close | price-volume |
| 72 | After-Hours Change | price-volume |
| 81 | Prev Close | price-volume |
| 86 | Open | price-volume |
| 87 | High | price-volume |
| 88 | Low | price-volume |

### Phase 2 Screener Profile (sweet-spot gap-ups)

```
f=geo_usa,sh_price_o3,sh_price_u50,sh_avgvol_o500,ta_gap_u3
c=1,65,61,63,64,66,67
```

Returns: Ticker, Price, Gap, Avg Volume, Relative Volume, Change, Volume

### Column Schema

Full validated column ID range: 0–150. See JSON schema at:
`~/.claude/skills/Trading/Config/FinvizColumnSchema.json`

## Massive.com API
- **Purpose:** OHLCV historical candle data
- **Key endpoints:**
  - Daily candles: for Camarilla pivot calculation, support/resistance
  - Intraday candles (1min, 5min): for pattern analysis
- **Key fields:** Open, High, Low, Close, Volume per period
- **Used for:** Camarilla pivot calculation, ATR computation, trend identification
- **API key location:** `~/.claude/LifeOS/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md`

## CBOE Delayed Quotes (Options — GEX)
- **Purpose:** Options open interest + implied volatility for the SPY GEX (gamma exposure) snapshot
- **Endpoint:** `https://cdn.cboe.com/api/global/delayed_quotes/options/{SYM}.json` (index roots take an underscore prefix, e.g. `SPX` → `_SPX`)
- **No API key required** (public CDN; send a `User-Agent` header)
- **Key fields:** `open_interest`, `iv`, `gamma`, `delta` per contract; `current_price` for spot
- **Used for:** `tradekit gex` (module `tradekit.analysis.gex`) — dealer net gamma, zero-gamma flip, magnet strikes. Ships in [tradekit](https://github.com/davdunc/tradekit), not in this plugin
- **Why CBOE:** open interest is an end-of-day figure (it doesn't move intraday), so a ~15-min-delayed EOD-settled feed is *correct* for a morning GEX. yfinance's `openInterest` returned 0; provider options tiers may not be entitled.

## SEC EDGAR
- **Purpose:** Company filings for catalyst identification, dilution checks, insider-transaction verification
- **No API key required, but sec.gov returns HTTP 403 without a descriptive `User-Agent`** containing a
  contact (name or email) — this is SEC's fair-access policy, not a bug. Read the contact string from the
  `EDGAR_USER_AGENT` env var (documented in `PREFERENCES.md`'s API key table, not yet set as of
  2026-09-22 — if unset, ask the operator once for a contact string rather than hardcoding one).
- **The flow that actually works (confirmed 2026-09-21/22, `efts.sec.gov` full-text search was never
  used successfully — do not rely on it as the primary path):**
  1. `GET https://www.sec.gov/files/company_tickers.json` → find the ticker, take its `cik_str`,
     zero-pad to 10 digits.
  2. `GET https://data.sec.gov/submissions/CIK<10-digit-CIK>.json` → `filings.recent` gives parallel
     arrays (`filingDate`, `form`, `accessionNumber`, `primaryDocument`) for the most recent ~1000 filings.
  3. Build the document URL: `https://www.sec.gov/Archives/edgar/data/<CIK>/<accessionNumber without
     dashes>/<primaryDocument>` and fetch that directly for the filing text/XML.
  4. For Form 4 (insider transactions) specifically, parse the XML: `<rptOwnerName>`,
     `<transactionDate><value>`, `<transactionCode>` (`P`=open-market purchase, `S`=sale),
     `<transactionShares><value>`, `<transactionPricePerShare><value>`.
  5. Space requests ~2s apart; this is a handful of calls per ticker, not a bulk scrape.
- **Key filing types:**
  - 8-K: Material events (earnings, acquisitions, leadership changes, offerings)
  - 10-Q: Quarterly financials
  - 10-K: Annual financials
  - S-1: IPO registration
  - SC 13D/G: Institutional ownership changes
  - 4: Insider transactions
- **Catalyst keywords:** acquisition, merger, partnership, offering, FDA, approval, contract, restructuring, bankruptcy, investigation

## DAS Trader Exports
- **Path:** `{{WINDOWS_HOME}}/OneDrive/Desktop/Trade_Review/YYYY-MM/YYYY-MM-DD/`
- **Files:**
  - `Trades.csv` — Individual executions (TradeID, Account, B/S, Symbol, Qty, Price, Time)
  - `Orders.csv` — Order history
  - `Tickets.csv` — Ticket data
  - `pnl-by-position-*.csv` — P&L summary by position
  - `pnl-by-position-*.jpg` — P&L screenshot
  - `positions-*.csv` — Position details
  - `*.jpg` — Chart screenshots per ticker
- **Accounts:** {{LIVE_ACCOUNT}} (live/Cobra), {{SIM_ACCOUNT}} (sim)
