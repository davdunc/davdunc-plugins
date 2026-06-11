---
description: Generate annotated daily report card with grades and pattern analysis
---

# DailyReview Workflow

**Depends on:** Today's DAS exports (Trades.csv / Orders.csv / Tickets.csv) in `Trade_Review/YYYY/MM/YYYY-MM-DD/`

## ⛔ HARD RULES (do not skip — all have failed in production)

1. **`falcon-stats ingest` is the ONLY allowed P&L source.** Do NOT hand-roll FIFO aggregation from Trades.csv directly — it produces wrong round-trip counts and undercounts P&L. (Failure mode 2026-06-02: hand-rolled FIFO undercounted LIVE by $6.71 because it grouped by ticker instead of identifying entry→exit clusters.)
2. **Both accounts MUST be confirmed before drafting any P&L summary.** Live (1RB16917) AND Sim (TR4425). If only one account's data is in hand, the draft is BLOCKED — surface the gap, request the other source, do NOT draft-with-assumption. (Failure mode 2026-06-01 + 2026-06-02: reported "$0 LIVE" with zero LIVE visibility while operator had 42 LIVE fills.)
3. **R-units required for all P&L + outcome reporting.** Read the R-CONFIG block at `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md → Trading Preferences → Risk Parameters` at the start of every run. Express the P&L summary in both R-units AND dollars (R first, dollar in parens). Trade grades use R-outcomes (e.g., "+2.3R" / "−0.5R"). Daily max + per-trade caps in R. Linked memory: `[[r-units-default]]`.
4. **Publish is deterministic.** After synthesis completes, immediately fire Reviews file write + Slack post + Notion append in parallel. Do NOT prompt the user about publishing or channel selection. Content adjustments are askable; the act of publishing is not. Linked memory: `[[publish-is-deterministic]]`.

Linked memory: `[[trading-skill-multi-account-spec]]` (severity: CRITICAL, recurrences: 2)

## Steps

### 0. Canonical Ingest (REQUIRED FIRST STEP)

```bash
# Locate today's DAS export folder — Windows username varies by machine
TODAY=$(date +%Y-%m-%d)
EXPORT_DIR=$(find /mnt/c/Users/*/OneDrive/Documents/Trade_Review -type d -name "$TODAY" 2>/dev/null | head -1)
[ -z "$EXPORT_DIR" ] && EXPORT_DIR=$(find /mnt/c/Users/*/OneDrive*/Desktop/Trade_Review -type d -name "$TODAY" 2>/dev/null | head -1)
echo "Found: $EXPORT_DIR"

# Required: Trades.csv must exist with Account column
[ -f "$EXPORT_DIR/Trades.csv" ] || { echo "BLOCKED: no Trades.csv in $EXPORT_DIR"; exit 1; }

# Run falcon-stats ingest — auto-splits by Account column, writes to DynamoDB,
# prints DailyStats per account with: realized P&L, win rate, peak equity (w/ time),
# trough equity (w/ time), max drawdown (w/ time), streak.
falcon-stats ingest "$EXPORT_DIR"
```

**Output to capture verbatim from `falcon-stats ingest`** — this is the source of truth for the report card:
- Round-trip count (NOT raw fill count)
- Realized P&L per account
- Win rate + W/L count per account
- Peak equity + timestamp per account
- Trough equity + timestamp per account
- Max drawdown + timestamp per account
- Streak (NW or NL)

If `falcon-stats ingest` errors or returns no rows, **STOP and diagnose** — do not fall back to hand-rolling. Common causes: wrong export path, Trades.csv missing the Account column, broker rrno format change.

### 1. Verify Multi-Account Coverage

After ingest, confirm BOTH accounts appear in output:

```
──────────────────────────────────────────────────
  YYYY-MM-DD — 1RB16917 (LIVE)
──────────────────────────────────────────────────
  ...stats...

──────────────────────────────────────────────────
  YYYY-MM-DD — TR4425 (SIM)
──────────────────────────────────────────────────
  ...stats...
```

If only one account section appears: BLOCKED. Either the operator only traded one account today (confirm with them explicitly) OR the export is partial. Do not draft until confirmed.

### 2. Grade Each Ticker

For each ticker traded, evaluate:

| Criteria | Weight | Description |
|----------|--------|-------------|
| Setup quality | High | Was this a playbook setup (Offsides / Fashionably Late)? |
| Covariance alignment | High | Did the trade direction match the z-score signal? (NORMAL → FL long, EXTREME → Offsides short) |
| Entry precision | High | Entry at planned level with confirmation? |
| Stop discipline | High | Was stop honored? Any averaging down? |
| Exit quality | Medium | Let winners run or cut too early? Payload captured vs available? |
| Size appropriateness | Medium | Conviction sizing or scattered small lots? Half size after loss? |
| Overtrading | High | How many executions vs. necessary? (Max 10 round-trips/day) |
| Account filter | Medium | Was the ticker in account range? ($3-50 sweet, $50-400 A+ only) |

### 2b. Statistical Covariance Check (Post-Trade)

For each ticker traded, pull the z-score at time of trade and evaluate:
- Was the stock NORMAL, EXTENDED, or EXTREME?
- Did the trade direction match the covariance signal?
- If EXTREME stock was traded long = wrong direction (grade penalty)
- If NORMAL stock was shorted without catalyst = wrong setup (grade penalty)

**Grading Scale:**
- **A**: Clean playbook trade, precise entry/exit, disciplined
- **B**: Right idea, good execution with minor issues
- **C**: Right direction but poor execution (churning, early exits)
- **D**: Wrong thesis or major discipline violation
- **F**: Revenge trade, averaging down, no plan

### 3. Identify Patterns

Check against known behavioral patterns from TELOS and intelligence base:
- Revenge trading (grinding same ticker after losses)
- Averaging down into losers
- Inverse allocation (best trades in sim, worst in live)
- Exiting winners too early
- Overtrading (too many executions for the P&L)
- Trading outside the game plan

### 4. Calculate Discipline Score

Score out of 10 using the canonical rubric (`Reference/ReportingSchema.md` →
*Discipline rubric*, backed by `tradekit.reporting.grading`). The number is
reproducible from the checklist, not eyeballed:

- Followed the published game plan (not screen impulses)? (+2)
- Only playbook setups (Offsides / Fashionably Late)? (+1)
- Honored stops; no averaging down? (+2)
- No revenge trading? (+1)
- Paused / reset after losses? (+1)
- Took the thesis trade live with conviction sizing? (+1)
- Conviction sizing, not scattered small lots? (+1)
- Account separation — LIVE served the plan, not a parallel impulse book? (+1)

### 5. Compare to Prior Days

Read prior **records** (not prose) — `tradekit cards trend --since <date>`,
which queries the persisted daily cards. Use the canonical column set
(`Reference/ReportingSchema.md` → *Canonical multi-day comparison columns*):
```
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
```

### 6. Extract Lessons

Identify 1-2 actionable lessons. Format for potential TELOS update.

### 7. Post to #watchlist — Review Format

After generating the review, post to Slack channel **#watchlist** (ID: `C0B5U2DHB0U`) using this format:

```
*TRADE REVIEW — [Date]* | Live P&L: [+/-$X.XX]

*Discipline Score:* [X/10]
*1% Change Result:* [Did they follow the behavioral focus? One line.]

*TRADES:*
[TICKER] [LONG/SHORT] [shares] → [+/-$X.XX] | [Grade] — [8-word verdict]
[TICKER] ...

*PATTERN TODAY:*
[One sentence on the dominant behavioral pattern observed]

*LESSON:*
[Single most actionable takeaway — one sentence]
```

**Guidelines:**
- Keep it under 20 lines — accountability snapshot, not full debrief
- Discipline score front and center
- Grade every ticker in one line: symbol, direction, P&L, letter grade, verdict
- One pattern, one lesson — force prioritization
- Exclude test/agent trades; note if any were running

### 8. Output Format

**P&L Summary table is MANDATORY and uses `falcon-stats ingest` output verbatim — both accounts as separate rows + combined row, with peak equity / trough / max drawdown / streak columns.** No exceptions.

```
## Daily Report Card — [Date]

### P&L Summary — Both Accounts *(via `falcon-stats ingest`, N round-trips properly identified)*

| Account | Round-Trips | Win Rate | Realized | Peak Equity | Trough | Max DD | Streak |
|---------|-------------|----------|----------|-------------|--------|--------|--------|
| **LIVE (1RB16917)** | N | X% (WW/LL) | $+/-X.XX | $+/-X.XX @ HH:MM:SS | $-X.XX @ HH:MM:SS | $X.XX @ HH:MM:SS | NW or NL |
| **SIM (TR4425)** | N | X% (WW/LL) | $+/-X.XX | $+/-X.XX @ HH:MM:SS | $-X.XX @ HH:MM:SS | $X.XX @ HH:MM:SS | NW or NL |
| **COMBINED** | N | X% (WW/LL) | $+/-X.XX | — | — | — | — |

**Headline:** [one sentence on the day's shape — what worked, what didn't]

### Equity Curve Notes
- Account-by-account commentary on the equity curve shape (smooth ascending vs choppy vs deep-drawdown-then-recover)
- Call out the deepest moment (trough or max DD time) — what happened then?
- Call out the streak that ended the day — was it built on plan or scrappy?

### Trade-by-Trade Review
[Per ticker: account, direction, size, entry/exit detail, realized P&L, grade, verdict]
Group by ticker but show account split when same ticker hit both books.

### Monitored but NOT TRADED
[Tickers where chart screenshots exist but no fills — confirms watch-discipline]

### Patterns Identified
[Behavioral patterns observed — account-separation shape, off-plan containment, banned-ticker respect, etc.]

### Discipline Score: X/10
[Per-criterion breakdown from the canonical 8-criterion rubric (Step 4 / `Reference/ReportingSchema.md`). "Account separation" is a first-class criterion — LIVE activity serves the published plan, not parallel-impulse.]

### Multi-Day Trend
[Canonical columns — same as Step 5 and WeeklyReview's Daily Breakdown. "LIVE RTs" = round-trips from `falcon-stats ingest`, NOT raw fill count. "Avg Grade" = mean of the day's trade grades on the one A/B/C/D/F ladder.]
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
[Last 5-6 sessions with both accounts]

### Lessons
[1-3 actionable takeaways — include Kai's own meta-lessons if a workflow/tool gap surfaced]

### Behavioral Contract for Tomorrow
> *"[One-paragraph contract — what to maintain, what to refine]"*
```

### 9. Persist the structured card

Write the day to the canonical store so it joins the comparable record set (this
is what `cards trend` / `cards weekly` later read — not the prose above):

```bash
# falcon.json   = the deterministic falcon-stats ingest output (verbatim)
# narrative.json = the structured judgment built in steps 2-6
#   (trades[], discipline{} rubric flags, patterns[], lessons[], headline, ...)
tradekit cards ingest --falcon-stats falcon.json --narrative narrative.json --date "$TODAY"
```

falcon owns the numbers (carried through unchanged); the narrative carries the
grades/discipline/patterns/lessons. See `Reference/ReportingSchema.md → Ingest`
for the narrative contract.

### Anti-patterns (DO NOT)

- ❌ Hand-roll P&L from Trades.csv with FIFO matching — wrong round-trip count, undercounts P&L
- ❌ Report SIM-only data via `/tmp/das_quote.py` and call it "the day" — that script defaults to TR4425 and is LIVE-blind by design (use `--all-accounts` flag if you must pull DAS direct)
- ❌ Draft the P&L summary before `falcon-stats ingest` returns
- ❌ Skip the equity curve (peak/trough/max DD) — those metrics are baked into the DailyStats output specifically because they reveal the day's shape that raw P&L hides
- ❌ Quote "Avg R" without checking whether trades had `planned_stop` set — most manual trades don't, making R unreliable; note "R unreliable today" when applicable

### Cross-references
- **Canonical reporting schema:** `Reference/ReportingSchema.md` — the one grade ladder, discipline rubric, R-unit format, and multi-day columns this card renders (backed by `tradekit.reporting`). When prose and code disagree, code wins.
- Multi-account spec: `[[trading-skill-multi-account-spec]]` — CRITICAL, 2 recurrences
- Account column parsing: `[[check-account-column-first]]`
- DAS routing safety: `[[das-sell-opens-short-not-close]]`
- Position state verification: `[[check-position-state-before-recommending]]`
