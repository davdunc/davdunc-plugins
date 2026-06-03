---
name: Trading
description: Intraday trading intelligence system — morning game plans, trade ingestion, daily reviews, market data, SEC filings, and content extraction from analysts. USE WHEN trading, game plan, ingest trades, daily review, weekly review, research ticker, market data, quote, OHLCV, SEC filings, EDGAR, extract trading content, trading intelligence, analyst insights, morning prep.
---

# Trading

Intraday momentum trading intelligence system for davdunc. Integrates DAS Trader exports, Finviz screener, Massive.com OHLCV, SEC EDGAR filings, and analyst content extraction into a searchable intelligence base that powers daily game plans.

## Customization

**Before executing, check for user customizations at:**
`~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/`

## Voice Notification

**When executing a workflow, do BOTH:**

1. **Send voice notification**:
   ```bash
   curl -s -X POST http://localhost:8888/notify \
     -H "Content-Type: application/json" \
     -d '{"message": "Running the WORKFLOWNAME workflow in the Trading skill to ACTION"}' \
     > /dev/null 2>&1 &
   ```

2. **Output text notification**:
   ```
   Running the **WorkflowName** workflow in the **Trading** skill to ACTION...
   ```

## Core Paths

- **DAS Trader exports:** `/mnt/c/Users/davdunc/OneDrive/Desktop/Trade_Review/`
- **Intelligence base:** `~/.claude/PAI/USER/TRADING/Intelligence/`
- **Historical reviews:** `~/.claude/PAI/USER/TRADING/Reviews/`
- **TELOS integration:** `~/.claude/PAI/USER/TELOS/`
- **Notion workspace:** TeamJaDaDa — David Duncan Daily Game Plan database

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **MorningGamePlan** | "morning game plan", "build game plan", "prep for trading" | `Workflows/MorningGamePlan.md` |
| **IngestTrades** | "ingest trades", "review trades", "daily report" | `Workflows/IngestTrades.md` |
| **DailyReview** | "daily review", "report card", "how did I do" | `Workflows/DailyReview.md` |
| **WeeklyReview** | "weekly review", "week summary" | `Workflows/WeeklyReview.md` |
| **WeeklyReadiness** | "weekly readiness", "build my weekly review", "sunday prep", "week ahead" | `Workflows/WeeklyReadiness.md` |
| **ResearchTicker** | "research TICKER", "look up TICKER", "what's the story on" | `Workflows/ResearchTicker.md` |
| **IngestContent** | "ingest video", "extract from youtube", "add analyst content" | `Workflows/IngestContent.md` |
| **QueryIntelligence** | "what does my intel say", "search intelligence", "what do analysts say" | `Workflows/QueryIntelligence.md` |
| **EveningVideoReview** | "evening review", "video review", "tradertv", "stocked up", "what did they say today", "review today's videos" | `Workflows/EveningVideoReview.md` |
| **UpdateTelos** | "save trading lessons", "update telos with trading" | `Workflows/UpdateTelos.md` |

## Examples

**Example 1: Morning game plan**
```
User: "build my morning game plan"
→ Invokes MorningGamePlan workflow
→ Scans Finviz for pre-market gappers
→ Pulls OHLCV + Camarilla pivots for each
→ Checks EDGAR for recent filings
→ Queries intelligence base for matching setups
→ Creates Notion entry with pre-filled data
```

**Example 2: Ingest and review trades**
```
User: "ingest my trades from today"
→ Invokes IngestTrades workflow
→ Reads DAS Trader CSVs from today's Trade_Review folder
→ Parses P&L by position, trade-by-trade timeline
→ Generates annotated daily report card with grades
```

**Example 3: Extract analyst content**
```
User: "ingest this video https://youtube.com/watch?v=xyz"
→ Invokes IngestContent workflow
→ Extracts transcript and key insights
→ Classifies by setup, regime, psychology
→ Appends to intelligence base files
→ Tagged with source, date, context
```

## Quick Reference

- **Accounts:** 1RB16917 (live/Cobra), TR4425 (sim)
- **Time zone:** Central — market open 8:30 CT
- **Platform:** DAS Trader Pro + ThinkorSwim (Bookmap)
- **Strategies:** Momentum — gaps, breakouts, VWAP, ORB, 9EMA x VWAP/21EMA
- **Risk:** ~$28K account, 1% per trade max risk

**Full Documentation:**
- Setup definitions: `PlaybookSetups.md`
- Trading rules: `RulesOfEngagement.md`
- Data source APIs: `DataSources.md`
- Analyst sources: `AnalystSources.md`
