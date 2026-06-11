---
description: Aggregate weekly trading data — P&L, patterns, discipline trend, and lessons
---

# WeeklyReview Workflow

## Steps

> **Canonical schema:** this workflow renders the same grade ladder, discipline
> rubric, and multi-day columns defined in `Reference/ReportingSchema.md`. The
> aggregation below is also available directly as `tradekit cards weekly`.

### 1. Load All Daily Reviews

Prefer the **persisted records**: `tradekit cards trend --since <Mon> --until <Fri>`
reads the structured daily cards for the week (and `tradekit cards weekly`
produces the full rollup). Fall back to the prose reviews in
`~/.claude/PAI/USER/TRADING/Reviews/` only if a day was never ingested.

If records don't exist for some days, ingest trades for those days first.

### 2. Aggregate P&L

| Metric | Calculation |
|--------|-------------|
| Weekly Live P&L | Sum of all daily live P&L |
| Weekly Sim P&L | Sum of all daily sim P&L |
| Total Round-Trips | Sum of all daily LIVE round-trips (not raw fills) |
| Win Rate | Winning positions / total decided positions |
| Best Trade | Highest single-position P&L |
| Worst Trade | Lowest single-position P&L |
| Avg Discipline Score | Mean of daily scores (each N/10 from the canonical rubric) |

### 3. Pattern Analysis

Across the week, identify:
- **Recurring behavioral patterns** (revenge trading, overtrading, etc.)
- **Improving patterns** (what got better day over day?)
- **Setup performance** (which setups were profitable? which lost money?)
- **Account allocation** (how much edge is staying in sim vs going live?)

### 4. Ticker Analysis

Which tickers appeared multiple days?
- Cumulative P&L per ticker across the week
- Flag any tickers that should be banned or promoted to live

### 5. Intelligence Gap Analysis

- What setups worked but aren't well-documented in the intelligence base?
- What analyst content would have helped this week?
- What intelligence queries came up that had no results?

### 6. Update Recommendations

Suggest updates to:
- **PlaybookSetups.md** — new setups to add or refine
- **RulesOfEngagement.md** — rules to add or modify
- **TELOS** — lessons, wisdom, or challenge updates
- **Intelligence base** — content to ingest or topics to research

### 7. Output Format

```
═══ WEEKLY REVIEW — Week of [Date] ═══

P&L SUMMARY:
Live: $X | Sim: $X | Total: $X
Round-Trips: X | Win Rate: X% | Avg Discipline: X/10

DAILY BREAKDOWN:
[canonical columns — identical to DailyReview's Multi-Day Trend]
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |

BEST TRADE: [ticker, setup, P&L, what made it work]
WORST TRADE: [ticker, P&L, what went wrong]

PATTERNS:
[bulleted list of behavioral patterns]

SETUP PERFORMANCE:
[table: setup type, times traded, win rate, avg P&L]

RECOMMENDATIONS:
[bulleted list of updates to make]

NEXT WEEK'S FOCUS:
[1-2 sentences on what to prioritize]
```
