---
description: Build the daily morning game plan with market data, intelligence, and Notion integration
---

# MorningGamePlan Workflow

## ⛔ HARD RULE: Publish is Deterministic

Once Phase 6 (synthesis) completes, **immediately fire Phase 7 (Slack) + Phase 8 (DAS Market Viewer) + Notion Game Plan DB entry in parallel.** Do NOT prompt the user with AskUserQuestion for publish-yes-or-no, channel selection, or send-confirmation. The default IS all three channels. Linked memory: `[[publish-is-deterministic]]`.

Adjustments to gameplan CONTENT (thesis pick, watchlist edits, ticker additions) ARE valid AskUserQuestion topics — those are content decisions. But the act of publishing the FINAL synthesis is part of the workflow contract, not an option.

Failure mode this prevents: 2026-06-03 — drafted clean gameplan, then asked "publish y/n + channel selection + thesis edits" → operator rejected the publish question as friction.

## ⛔ HARD RULE: R-Units Required

**All trade plans, stops, targets, and recap numbers use R-units.** Read the R-CONFIG block at the top of `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md → Trading Preferences → Risk Parameters` at the start of every run. Express stops as both price + per-share R, targets as R-multiples, daily limits as ±NR, position sizing as fraction-of-R-exposure. Always include the derived dollar in parentheses for readability (e.g., "1R ($280)"). Linked memory: `[[r-units-default]]`.

**Anti-pattern:** Hard-coding dollar amounts ("max $280 risk", "target $30.50") in workflow output. R-units are the lingua franca; dollars derive from PREFERENCES.

## Steps

### Phase 1: Market Context (6:00-6:20 CT)

1. **Check futures/ETFs:**
   - `MarketData.ts quote SPY QQQ IWM /CL GLD`
   - Assess overnight direction and gap

2. **Economic calendar:**
   - Check for FOMC, CPI, jobs, GDP, or other scheduled releases
   - Flag any events that could cause volatility

3. **USMetrics Macro Context:**
   Read `~/.claude/data/Substrate/US-Common-Metrics/us-metrics-current.csv` and extract the six key trading signals:

   | Signal | Metric | Threshold | Regime Label |
   |--------|--------|-----------|--------------|
   | Volatility | VIX (VIXCLS) | <15 tight / 15-20 calm / 20-30 elevated / >30 spike | CALM / ELEVATED / SPIKE |
   | Yield curve | 10Y-2Y Spread (T10Y2Y) | >0 = normal / <0 = inverted | NORMAL / INVERTED |
   | Consumer stress | UMich Sentiment (UMCSENT) | >75 ok / 60-75 cautious / <60 stress | OK / CAUTIOUS / STRESS |
   | Energy | WTI Crude (DCOILWTICO) | <80 low / 80-100 moderate / >100 elevated | LOW / MODERATE / ELEVATED |
   | Systemic risk | Financial Stress Index (STLFSI4) | <0 = low / 0-1 = moderate / >1 = high | LOW / MODERATE / HIGH |
   | Dollar | USD Index (DTWEXBGS) | directional note only | UP / DOWN / FLAT |

   Output the compact macro bias block:
   ```
   ══ MACRO CONTEXT ══════════════════════════════════
   VIX:          [value]  → [CALM/ELEVATED/SPIKE]  — [one-line implication for today]
   Yield Curve:  [value]  → [NORMAL/INVERTED]  — [one-line implication]
   Consumer:     [value]  → [OK/CAUTIOUS/STRESS]  — [sector bias note]
   Oil:          $[value] → [LOW/MODERATE/ELEVATED]  — [inflation/energy note]
   Stress Index: [value]  → [LOW/MODERATE/HIGH]  — [systemic risk note]
   ══ REGIME BIAS ════════════════════════════════════
   [2-sentence synthesis: what this macro backdrop means for today's setups]
   ═══════════════════════════════════════════════════
   ```

   **VIX → Setup filter:**
   - CALM (15-20): FL Long bias, trending setups preferred, good breakout follow-through
   - ELEVATED (20-30): Both directions viable, wider stops needed, reduce size
   - SPIKE (>30): Reversal/fade setups only, no momentum longs, sim-first

   **Consumer stress → Sector filter:**
   - STRESS (<60): Caution on retail/discretionary longs (AMZN, WMT, AZO, etc.)
   - OK/CAUTIOUS: No sector filter applied

   Note: If Substrate data is more than 7 days old, flag it and run `bun ~/.claude/skills/USMetrics/Tools/UpdateSubstrateMetrics.ts` before proceeding.

4. **Determine market regime** (informed by steps 1-3 above):
   - Trending / Ranging / Gap Day / High Volatility / Choppy
   - Use VIX signal from step 3 as primary input
   - Query intelligence: `Intelligence/MarketRegimes/[regime].md` for how to trade today

### Phase 2: Scanning & Watchlist (6:15-6:45 CT)

1. **Run Finviz screener:**
   - Pre-market gappers > 3% with volume > 500K
   - Unusual volume movers
   - Earnings/catalyst plays

2. **For each candidate ticker:**
   - `MarketData.ts quote TICKER` — fundamentals snapshot
   - `MarketData.ts ohlcv TICKER --period daily --range 5d` — calculate Camarilla pivots
   - `EdgarLookup.ts filings TICKER --days 14` — recent SEC filings
   - Extract catalyst keywords from filings

3. **Statistical Covariance Analysis (for each candidate ticker):**
   - Pull 90 days of daily OHLCV from Polygon REST API (`api.polygon.io/v2/aggs/ticker/TICKER/range/1/day/`)
   - Calculate: 20-day mean, 20-day std dev, z-score (current price vs 20-day mean)
   - Calculate: weekly high/low, range position (%), annualized volatility
   - Classify: NORMAL (|z| < 2), EXTENDED (2-3), EXTREME (>3)
   - **Setup signal rule:** NORMAL stocks → Fashionably Late long candidates. EXTREME stocks → Offsides short candidates.
   - Filter: must deliver $1 intraday move (check avg daily range)
   - Filter: account size ($3-50 sweet spot, $50-400 A+ only, >$400 excluded)

4. **Grade each ticker** (per PlaybookSetups.md grading criteria + covariance status)

5. **Separate into two categories:**
   - **Fresh News:** New catalysts today (earnings, filings, breaking news)
   - **Second Day Plays / Technical Setups:** Day 2 continuations, HTF setups, range breaks

### Phase 3: Query Intelligence Base (6:45-7:00 CT)

For each ticker on the watchlist:

1. **Match to playbook setup:**
   - Search `Intelligence/Setups/` for matching patterns
   - Pull relevant analyst insights for this setup type

2. **Check analyst commentary:**
   - Search `Intelligence/Analysts/` for any recent mentions of ticker or sector

3. **Load relevant psychology reminders:**
   - Based on recent review patterns (e.g., "exiting winners too early")
   - Pull from `Intelligence/Psychology/`

### Phase 4: Build the Game Plan (7:00-7:15 CT)

1. **Create Notion entry** in David Duncan Daily Game Plan database:
   - Date, Monthly Goal, Weekly Goal
   - Market Regime
   - 1% Change (behavioral focus from recent lessons)

2. **Populate Fresh News sub-database:**
   - Ticker, Support (Camarilla S3/S4), Resistance (Camarilla R3/R4)
   - Inflexion point, Bias, Setup type, Trading Plan, Notes

3. **Populate Second Day Plays sub-database:**
   - Same fields, focused on continuation and technical patterns

4. **Each Trading Plan field should include:**
   - Entry trigger (specific price action confirmation)
   - Stop loss (ATR-based or level-based)
   - Profit targets (R:R ratio)
   - Intelligence note (what analysts/intel says about this setup)

### Phase 5: Identify the Thesis Trade (7:15-7:30 CT)

> "Trade the thesis, not the ticker that's moving the most on your screen."

1. **Which ticker has the highest conviction?**
   - Strongest catalyst + cleanest chart + best setup grade
   - Intelligence base confirms edge in this setup type

2. **Mark as PRIMARY TRADE:**
   - This gets live capital
   - Define exact entry, stop, targets
   - Plan to size into conviction (not 5-share lots)

3. **Prepare both directions:**
   - Long scenario AND short scenario for the primary ticker

### Phase 6: Output Summary

Present the complete game plan:
```
═══ MORNING GAME PLAN — [Date] ═══

Market Regime: [regime]
1% Change: [behavioral focus]
Thesis Trade: [TICKER] — [setup type] — [direction]

MACRO CONTEXT:
VIX [value] → [CALM/ELEVATED/SPIKE] | Consumer [value] → [OK/CAUTIOUS/STRESS] | Oil $[value] → [LOW/MODERATE/ELEVATED]
Regime bias: [one-sentence synthesis for today's setups]

STATISTICAL COVARIANCE:
[table: Ticker | Price | Z-Score | Status | Range Pos | Ann Vol | Setup Signal]
Rule: NORMAL → FL long. EXTREME → Offsides short.

FRESH NEWS:
[table of tickers with levels, bias, plan — filtered by account size + covariance]

SECOND DAY PLAYS:
[table of tickers with levels, bias, plan]

INTELLIGENCE NOTES:
[relevant analyst insights for today's setups]

RULES REMINDER:
[top 3 rules from RulesOfEngagement.md based on recent patterns]
```

### Phase 7: Post to #watchlist — Discipline Workshop Format

Post the trading plan to Slack channel **#watchlist** (ID: `C0B5U2DHB0U`) using the discipline workshop format below. This is a focused, accountability-first summary — not the full game plan dump.

```
*GAME PLAN — [Date]* | Regime: [regime]

*1% Change:* [behavioral focus from recent review]
*Yesterday's Discipline:* [X/10 — one-line pattern note]

*THESIS TRADE:* [TICKER] — [setup] — [LONG/SHORT]
• Entry: [specific trigger]
• Stop: [level] ([ATR-based or level])
• Target: [level] ([R:R])
• Edge: [one-line intel note]

*WATCHLIST:*
[TICKER] | [bias] | [z-score status] | [key level]
[TICKER] | [bias] | [z-score status] | [key level]
...

*RULES FOR TODAY:*
1. [rule 1 — most relevant to recent pattern]
2. [rule 2]
3. [rule 3]
```

**Guidelines:**
- Keep it under 40 lines — this is for focus, not reference
- Lead with the behavioral commitment (1% Change) — discipline first
- Thesis trade must have all four fields (entry, stop, target, edge) or don't post it
- Watchlist: max 6 tickers, z-score status only (NORMAL / EXTENDED / EXTREME)
- Rules: pull the 3 most relevant from RulesOfEngagement.md based on recent review patterns

### Phase 8: DAS Market Viewer (auto)

After presenting the game plan, automatically populate DAS Trader Market Viewer:

1. **Collect all plan tickers** — thesis trade + fresh news + second day plays (deduplicated)
   - Include context tickers if they appear as active setups (SPY, QQQ for regime reads)
   - Order: thesis trade first, then fresh news, then second day plays

2. **Run das_market_viewer.py:**
   ```bash
   python3 ~/falcon/dashboard/das_market_viewer.py TICKER1 TICKER2 TICKER3 ...
   ```
   - Always writes `C:\Cobra Trading_x64\GamePlan-Today.txt` (1-right-click load fallback)
   - If DAS is running: probes CMD API SCRIPT commands to auto-populate Market Viewer
   - Reports to stderr whether auto-load succeeded or file-only

3. **Output to user:**
   ```
   ══ DAS MARKET VIEWER ══════════════════════
   Tickers written → C:\Cobra Trading_x64\GamePlan-Today.txt
   [If DAS running]: Auto-load attempted via CMD API — check Market Viewer
   [If DAS not open]: Right-click Market Viewer tab → Load → GamePlan-Today.txt
   ═══════════════════════════════════════════
   ```
