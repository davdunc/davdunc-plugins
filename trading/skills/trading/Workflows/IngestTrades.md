---
description: Ingest DAS Trader exports and generate structured trade data
---

# IngestTrades Workflow

## Steps

### 1. Locate Today's Trade Files

```
Base path: {{WINDOWS_HOME}}/OneDrive/Desktop/Trade_Review/
Today's folder: YYYY-MM/YYYY-MM-DD/
```

List all files in today's folder. Expected files:
- `Trades.csv` — Individual executions
- `Orders.csv` — Order history
- `pnl-by-position-*.csv` — P&L summary
- `pnl-by-position-*.jpg` — P&L screenshot
- `positions-*.csv` — Position details
- `execution-by-route-*.csv` — Route data
- `*.jpg` / `*.png` — Chart screenshots per ticker

### 2. Parse P&L by Position

Read `pnl-by-position-*.csv` (or screenshot if CSV missing). Extract:

| Field | Source |
|-------|--------|
| Account | ACCID column ({{LIVE_ACCOUNT}} = live, {{SIM_ACCOUNT}} = sim) |
| Symbol | Symbol column |
| Shares | Shares column (total traded) |
| Realized P&L | Realized column |
| ECN Fees | ECNFEE column |
| Net P&L | P & L column |

**Calculate totals:**
- Live P&L ({{LIVE_ACCOUNT}} rows)
- Sim P&L ({{SIM_ACCOUNT}} rows)
- Total P&L

### 3. Parse Trade-by-Trade Timeline

Read `Trades.csv`. For each trade extract:
- Time, Account, Symbol, B/S (buy/sell), SHORT flag, Qty, Price, Route

**Group by symbol, then sort by time.** This creates the chronological trade narrative per ticker.

### 4. Read Chart Screenshots

Read any `*.jpg` or `*.png` files that match ticker names (e.g., `ARM-2026-03-27-*.jpg`). These provide visual context for the review.

### 5. Output Structured Data

Present:
1. **P&L Summary Table** — All positions with account, shares, P&L
2. **Per-Ticker Trade Timeline** — Chronological buys/sells with annotations
3. **Chart Context** — Screenshots for each traded ticker
4. **Account Totals** — Live vs Sim breakdown

### 6. Save to Reviews Archive

After generating the review, save a summary to:
`~/.claude/LifeOS/USER/TRADING/Reviews/YYYY-MM-DD.md`
