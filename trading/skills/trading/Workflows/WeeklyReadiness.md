---
description: Sunday evening weekly readiness review — strategic prep for the coming trading week
---

# WeeklyReadiness Workflow

**When:** Sunday evening (5-6 PM CT) or on demand ("build my weekly review")
**Output:** Notion page (shareable) in David Duncan Daily Game Plan database
**Purpose:** Strategic weekly prep — different from the tactical daily MorningGamePlan

---

## Overview

The weekly readiness review covers six areas:

1. **Previous Week Earnings Results** — who beat, who missed, how stocks reacted
2. **Coming Week Earnings Calendar** — key reports, dates, estimates
3. **Aggressive Movers** — stocks that moved >10% last week
4. **News-Impacted Stocks** — geopolitical, regulatory, sector catalysts for coming week
5. **YouTube Intel** — transcripts and key insights from trusted channels
6. **Macro Context** — Substrate US metrics, VIX, oil, sentiment, regime

All tickers are filtered for David's account ($3-50 sweet spot, up to $400 for A+ setups) and framed for Fashionably Late and Offsides scalp entries.

---

## Steps

### Phase 1: Data Collection (Parallel Agents)

Launch 4 agents in parallel:

**Agent 1 — Earnings Research:**
- Search for last week's earnings results (WebSearch)
- Search for coming week's earnings calendar (WebSearch)
- For each: ticker, EPS actual vs estimate, revenue, stock reaction %
- Filter to tickers in account price range

**Agent 2 — Aggressive Movers + News:**
- Search for stocks that moved >10% in the previous week (WebSearch)
- Search for major news catalysts for coming week (geopolitical, FDA, regulatory, macro events)
- Cross-reference with economic calendar from Substrate (FOMC, CPI, jobs, GDP)
- Filter to account price range

**Agent 3 — YouTube Transcript Extraction:**
- Load channel config from `Config/youtube-channels.json`
- For each channel, find videos from the past 7 days (WebSearch for "[channel name] latest video")
- Extract transcripts or key content using Parser skill (WebFetch on video pages)
- Extract: key tickers mentioned, setups discussed, market outlook, lessons
- Summarize each video in 3-5 bullet points with timestamps if available

**Agent 4 — Macro Context:**
- Read Substrate US-Common-Metrics data (`~/.claude/data/Substrate/US-Common-Metrics/US-Common-Metrics.md`)
- Read Substrate Trading-Metrics (`~/.claude/data/Substrate/Trading-Metrics/trading-metrics-historical.csv`)
- Pull current VIX, oil, consumer sentiment, Fed funds rate, 10Y yield
- Determine market regime: Trending / Ranging / Gap Day / Choppy / Overextended
- Include David's personal trading stats for the past week from falcon-stats

### Phase 2: Synthesis

After all agents return:

1. **Merge tickers** — deduplicate across earnings, movers, news, and YouTube mentions
2. **Score relevance** — tickers mentioned by multiple sources rank higher
3. **Filter by account size** — $3-50 sweet spot, $50-400 acceptable, >$400 excluded
4. **ATR check** — flag any ticker that can't deliver a $1 intraday move
5. **Statistical Covariance Analysis** — for each candidate ticker:
   - Pull 90 days of daily OHLCV from Polygon REST API
   - Calculate: 20-day mean, 20-day std dev, z-score (current price vs 20-day mean)
   - Calculate: weekly high/low, range position (%), annualized volatility
   - Classify: NORMAL (|z| < 2), EXTENDED (2-3), EXTREME (>3)
   - **Setup signal rule:** NORMAL → Fashionably Late long. EXTREME → Offsides short.
6. **Level analysis** — for top 5-8 tickers, identify key support/resistance levels
7. **Setup framing** — for each ticker, combine covariance status + levels to describe the specific Fashionably Late and/or Offsides Reversal entry scenario

### Phase 3: Build Document

Structure the Notion page:

```
# Weekly Readiness Review — [Week of Date]

## Market Regime
[Regime assessment from macro data + Substrate metrics]
[David's personal stats from the past week — falcon-stats summary]

## Discipline Reminder
[Pull latest challenge from TELOS/CHALLENGES.md — the active behavioral pattern to watch]
[Goal from most recent daily review]

## Coming Week Catalysts
### Earnings Calendar
[Table: Date | Ticker | Price | Est EPS | Est Rev | Notes]

### Economic Calendar
[FOMC, CPI, jobs, GDP — from Substrate + WebSearch]

### News & Sector Catalysts
[Geopolitical, regulatory, sector-specific catalysts]

## Previous Week Review
### Earnings Results
[Table: Ticker | EPS Beat/Miss | Rev Beat/Miss | Stock Reaction | Still In Range?]

### Aggressive Movers (>10%)
[Table: Ticker | Move % | Catalyst | Day 2+ Opportunity?]

## Watchlist — Top Picks for the Week
### [Ticker 1] — [Setup Type]
- Price: $X | Levels: S $X / R $X
- Catalyst: [why this week]
- Fashionably Late: [entry scenario]
- Offsides Reversal: [entry scenario]
- Payload: [R target]

[Repeat for 5-8 tickers]

## YouTube Intel
### [Channel Name] — "[Video Title]"
- Key tickers: [list]
- Market outlook: [1-2 sentences]
- Best insight: [quote or paraphrase]

[Repeat for each video extracted]

## Macro Dashboard
[Table from Substrate: GDP, CPI, unemployment, VIX, oil, sentiment, rates]

## Rules for the Week
1. [From TELOS discipline reminder]
2. [From most recent daily review goal]
3. One thesis trade per day. Payload over price action.
```

### Phase 4: Publish to Notion

- Create page in David Duncan Daily Game Plan database
- Title: "Weekly Readiness — Week of [Date]"
- Properties: Date, Market Regime, Monthly Goal, Weekly Goal, 1% Change
- Content: Full document from Phase 3

### Phase 5: Syndicate (Optional)

If David requests:
- Post summary to Slack #general
- Generate StockTwits-ready version (sanitized, no PII)
- Publish to blog (davidduncan.org via GitLab pipeline)

---

## YouTube Channel Configuration

Channels are configured in `Config/youtube-channels.json`. To add or remove channels:

```json
{
  "channels": [
    {
      "name": "Channel Name",
      "handle": "@handle",
      "url": "https://www.youtube.com/@handle",
      "focus": "What to extract from this channel",
      "max_videos": 3
    }
  ]
}
```

---

## Integration Points

- **Substrate US-Common-Metrics** — macro data for regime assessment
- **Substrate Trading-Metrics** — David's personal performance trends
- **falcon-stats** — weekly P&L, win rate, discipline score
- **TELOS/CHALLENGES.md** — active behavioral patterns to watch
- **Trading/Reviews/** — most recent daily review for goal carryover
- **Parser skill** — YouTube transcript extraction
- **Notion MCP** — page creation and publishing

---

## Account Size Filter

| Price Range | Status | Criteria |
|-------------|--------|----------|
| $3-50 | Sweet spot | Include all playbook setups |
| $50-100 | Acceptable | 10-25 shares, limited scaling |
| $100-400 | A+ only | Only if catalyst + setup + ATR all grade A+ |
| $400+ | Excluded | Cannot size properly |

**ATR minimum:** Every ticker must be able to deliver $1 intraday move.

---

## Discipline Integration

Every weekly review includes:
1. **TELOS challenge check** — which behavioral pattern is most active?
2. **Previous week discipline scores** — trend from daily reviews
3. **Goal carryover** — what was the goal from the last daily review?
4. **Weekly commitment** — one sentence: "This week I will [specific behavior]"
