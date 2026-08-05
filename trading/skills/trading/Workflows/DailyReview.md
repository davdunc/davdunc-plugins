---
description: Generate annotated daily report card with grades and pattern analysis
---

# DailyReview Workflow

**Depends on:** Today's DAS exports (Trades.csv / Orders.csv / Tickets.csv) in `Trade_Review/YYYY/MM/YYYY-MM-DD/`

## ⛔ HARD RULES (do not skip — all have failed in production)

0. **`Reference/ReportingSchema.md` is the canonical contract.** The grade ladder, the
   8-criterion discipline rubric (shown as a checklist, not just a total), the multi-day
   comparison columns, R rendering, and file naming all come from it — not from templates
   inlined in this file. Where this workflow and the schema disagree, **the schema wins**.
   Rule 0 of the schema also applies: `tradekit cards *` does not exist as of 2026-08-05,
   so anything depending on it is ASPIRATIONAL and cannot be used to score a review.
1. **`falcon-stats ingest` is the ONLY allowed P&L source.** Do NOT hand-roll FIFO aggregation from Trades.csv directly — it produces wrong round-trip counts and undercounts P&L. (Failure mode 2026-06-02: hand-rolled FIFO undercounted LIVE by $6.71 because it grouped by ticker instead of identifying entry→exit clusters.)
2. **Both accounts MUST be confirmed before drafting any P&L summary.** Live ({{LIVE_ACCOUNT}}) AND Sim ({{SIM_ACCOUNT}}). If only one account's data is in hand, the draft is BLOCKED — surface the gap, request the other source, do NOT draft-with-assumption. (Failure mode 2026-06-01 + 2026-06-02: reported "$0 LIVE" with zero LIVE visibility while operator had 42 LIVE fills.)
3. **R-units required for all P&L + outcome reporting.** Read the R-CONFIG block at `~/.claude/LifeOS/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md → Trading Preferences → Risk Parameters` at the start of every run. Express the P&L summary in both R-units AND dollars (R first, dollar in parens). Trade grades use R-outcomes (e.g., "+2.3R" / "−0.5R"). Daily max + per-trade caps in R. Linked memory: `[[r-units-default]]`.
4. **Publish is deterministic.** After synthesis completes, immediately fire Reviews file write + Slack post + **Discord Daily Report Card post** + Notion append in parallel. Do NOT prompt the user about publishing or channel selection. Content adjustments are askable; the act of publishing is not. Failures are isolated — a Discord webhook error must not block Slack, Notion, or the Reviews file. Linked memory: `[[publish-is-deterministic]]`.
5. **Channel topology + Notion protocol.** Slack #general (C0HFFCLN8) + Notion + **Discord Daily Report Card** = PUBLIC; Google Drive = PRIVATE. The Discord forum channel receives **accountability-only content in R-units** — discipline score, 1% Change result, per-ticker grade + R-multiple, one pattern, one lesson. Never dollar P&L, account IDs, LIVE/SIM assignment, equity-curve figures, or share counts. Notion review section appends to the day's main page following the 7-section protocol (see `~/.claude/LifeOS/USER/SKILLCUSTOMIZATIONS/Trading/NOTION_PROTOCOL.md`). Required post-review property updates on the main page: `Status=REVIEWED`, `Combined R=<float>`, `Discipline Score=<1-10>`, `Thesis Outcome=<WIN/LOSS/INVALIDATED/NOT-TAKEN>`. Required sub-DB updates: set `Outcome` (WIN/LOSS/SCRATCH/NOT-TAKEN) on each Fresh News + Second Day Plays entry that fired. Private Drive: upload full `REVIEW-YYYY-MM-DD.md` to `Game_Plan` folder. Linked: `[[channel-topology]]`, `[[notion-gameplan-protocol]]`.

6. **Falcon-cluster bus.** After publishing the public + private artifacts, post a review-complete beacon to Slack #falcon-cluster ({{SLACK_CLUSTER_ID}}) so LifeOS agents on other machines (ddd-laptop, home-pda) detect this session's review state without polling S3. Use `~/.claude/Tools/falcon-cluster-handoff.sh state "DailyReview published — Combined R=<R> · Discipline=<N>/10 · channels: Notion+Slack+Drive"` OR `slack_send_message` to {{SLACK_CLUSTER_ID}} from within the session. Linked: `[[falcon-cluster-agent-sync]]`.

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
  YYYY-MM-DD — {{LIVE_ACCOUNT}} (LIVE)
──────────────────────────────────────────────────
  ...stats...

──────────────────────────────────────────────────
  YYYY-MM-DD — {{SIM_ACCOUNT}} (SIM)
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

Score 1-10 based on:
- Followed morning game plan? (+2)
- Playbook trades only? (+2)
- Honored stops? (+2)
- No revenge trading? (+1)
- Paused after losses? (+1)
- Thesis trade taken live? (+1)
- Appropriate sizing? (+1)

### 5. Compare to Prior Days

Load recent reviews from `~/.claude/LifeOS/USER/TRADING/Reviews/` and show trend:
```
Date | Live P&L | Sim P&L | Discipline | Key Pattern
```

### 6. Extract Lessons

Identify 1-2 actionable lessons. Format for potential TELOS update.

### 7. Post to #general — Review Format

After generating the review, post to Slack channel **#general** (ID: `C0HFFCLN8`, workspace
`saturdayinaustin`) using this format.

<!-- 2026-07-28: this step previously said "#watchlist ({{SLACK_PUBLIC_ID}})", contradicting Hard Rule 5
     in this same file. Verified via the Slack API that no #watchlist channel exists in the
     workspace — #general (C0HFFCLN8) is the real target, matching [[channel-topology]]. Posts
     addressed to the old ID went nowhere. -->

**⚠️ #general is a PUBLIC channel** — all workspace members are in it. Per `[[channel-topology]]`
and `[[r-units-default]]`, express P&L in **R-multiples, not dollars**, and never include broker
account IDs or LIVE/SIM assignment.

```
*TRADE REVIEW — [Date]* | Net: [+/-N.NR]

*Discipline Score:* [X/10]
*1% Change Result:* [Did they follow the behavioral focus? One line.]

*TRADES:*
[TICKER] [LONG/SHORT] → [+/-N.NR] | [Grade] — [8-word verdict]
[TICKER] ...

*PATTERN TODAY:*
[One sentence on the dominant behavioral pattern observed]

*LESSON:*
[Single most actionable takeaway — one sentence]
```

**Guidelines:**
- Keep it under 20 lines — accountability snapshot, not full debrief
- Discipline score front and center
- Grade every ticker in one line: symbol, direction, R-multiple, letter grade, verdict
- One pattern, one lesson — force prioritization
- Exclude test/agent trades; note if any were running

**R-units, not dollars (2026-07-28).** This template previously carried `Live P&L: [+/-$X.XX]` and
per-trade dollar amounts into a channel every workspace member reads. R-multiples carry the same
discipline signal without publishing P&L. Share counts are dropped for the same reason — shares ×
R-value backs directly into position size and account size. The dollar figures stay in the private
Drive copy and the local `REVIEW-YYYY-MM-DD.md`, where they belong.

### 7b. Post to Discord — Daily Report Card (forum channel)

Fires in parallel with Step 7. Post the **same accountability-only R-unit body** built for Slack —
build the PUBLIC payload once, send it to both. Do NOT derive this from the private Drive review.

```bash
python3 ~/.claude/Tools/discord_post.py \
  --file <accountability-review.md> \
  --webhook-env DISCORD_REPORTCARD_WEBHOOK \
  --thread-name "Daily Report Card — YYYY-MM-DD"
```

**`--thread-name` is mandatory here.** This is a Discord *forum* channel, and a webhook post to a
forum channel without a thread name is rejected — the title becomes the forum post title. The tool
creates the thread on the first chunk and posts any remaining chunks into it; without that, each
chunk would open its own separate forum post.

The tool also handles the Slack→Discord conversions (bold, links, table padding) and suppresses
link-preview cards. Verify with `--dry-run` whenever the review format changes.

**Content ceiling — accountability only:**

| Include | Exclude |
|---|---|
| Discipline score | Dollar P&L (any account) |
| 1% Change result | Broker account IDs, LIVE/SIM assignment |
| Per-ticker grade + R-multiple | Share counts (backs into position size) |
| One pattern, one lesson | Equity curve, peak/trough, drawdown |
| Thesis outcome | Multi-day R-trend / P&L history |

**Failure handling:** non-zero exit reports which chunks failed. Log and continue — Discord never
blocks Slack, Notion, Drive, or the Reviews file write.

#### Round-trip section (append to the report card)

```bash
export AWS_PROFILE=pai-workstation-lenovo AWS_DEFAULT_REGION=us-east-2
~/Projects/falcon-stats/.venv/bin/python ~/.claude/Tools/roundtrip_report.py --date YYYY-MM-DD
```

Emits net R, win rate, best/worst, and a per-round-trip table (time, ticker, side, hold, R, W/L)
already inside a code fence so it aligns in Discord. Reads **falcon-trades DynamoDB**, the system of
record per `[[trading-activity-source-of-truth]]` — not the local DAS export folders, which only
exist on the machine that ran the ingest.

Deliberately omits dollar P&L, account IDs, and **share counts** — shares × R-value backs into
position and account size, which defeats quoting R in the first place. It auto-flags days above the
10-round-trip overtrading threshold, and reports any row overflow as a count rather than truncating
silently.

**Gotcha (fixed 2026-07-28):** `falcon-stats trades` / `sanitized` read a local `TRADE_REVIEW_PATH`
directory and printed "No trade data found" on any machine without the DAS exports — even for days
with data in DynamoDB. They now fall back to DynamoDB and say which source they used. Linked:
`[[das-review-gotchas]]`.

### 8. Output Format

**P&L Summary table is MANDATORY and uses `falcon-stats ingest` output verbatim — both accounts as separate rows + combined row, with peak equity / trough / max drawdown / streak columns.** No exceptions.

```
## Daily Report Card — [Date]

### P&L Summary — Both Accounts *(via `falcon-stats ingest`, N round-trips properly identified)*

| Account | Round-Trips | Win Rate | Realized | Peak Equity | Trough | Max DD | Streak |
|---------|-------------|----------|----------|-------------|--------|--------|--------|
| **LIVE ({{LIVE_ACCOUNT}})** | N | X% (WW/LL) | $+/-X.XX | $+/-X.XX @ HH:MM:SS | $-X.XX @ HH:MM:SS | $X.XX @ HH:MM:SS | NW or NL |
| **SIM ({{SIM_ACCOUNT}})** | N | X% (WW/LL) | $+/-X.XX | $+/-X.XX @ HH:MM:SS | $-X.XX @ HH:MM:SS | $X.XX @ HH:MM:SS | NW or NL |
| **COMBINED** | N | X% (WW/LL) | $+/-X.XX | — | — | — | — |

**Headline:** [one sentence on the day's shape — what worked, what didn't]

### Equity Curve Notes
- Account-by-account commentary on the equity curve shape (smooth ascending vs choppy vs deep-drawdown-then-recover)
- Call out the deepest moment (trough or max DD time) — what happened then?
- Call out the streak that ended the day — was it built on plan or scrappy?

### Trade-by-Trade Review (per-ticker journal blocks)

For EACH ticker that was traded (TRADED tickers — not the never-fired watchlist), produce a journal block with these 4 mandatory subsections:

```
### TICKER — <one-line verdict> — <Trade Rating: A/B/C/D/F>

**Account / direction / size / R outcome:**
- LIVE/SIM: side, qty, avg entry → avg exit, realized R (with $)
- (cross-account if both)

**Did Well:**
- 1-3 bullets on what was right about this trade — entry timing, sizing discipline, stop placement, exit decision, plan-adherence
- Concrete observations, not platitudes ("scaled in 3 legs cleanly" not "good execution")

**Went Wrong:**
- 1-3 bullets on what failed or could improve — chase entry, late exit, oversized, off-plan, no-stop, ignored PM update, etc.
- If nothing went wrong: write "Nothing — clean playbook execution" and explain
- Honest > kind: this is the journal, not PR

**Top Playbook:**
- ONE primary playbook name from the canonical list: Gap Up/Down, ORB, VWAP Reclaim, VWAP Rejection, FL (9EMA×VWAP), Breakout (Key Level), Risk-Off Choppy Edges, Short Overextension Fade, Offsides Short (EXTREME z), Day 2 Continuation, Failed Breakdown Reclaim, Bounce Trade, Earnings Reaction, Off-Plan / Impulse, Other
- If trade used multiple, name the DOMINANT one and note the second in parentheses

**Trade Rating:** A/B/C/D/F  
- A = clean playbook execution, planned R:R achieved or favorable invalidation
- B = right idea, minor execution issues
- C = right direction, sloppy execution (churn, early exit, late entry)
- D = wrong thesis OR major discipline violation contained
- F = revenge / averaging-down / off-plan grind / banned-list violation
```

For NOT-TAKEN tickers from the published watchlist (trigger fired, no fill): a shorter block:

```
### TICKER — NOT TAKEN (trigger fired)
- Trigger that fired + time
- Reason not taken (if known) OR "no entry placed"
- What it would have made: estimated R-outcome if taken at the documented level
- Lesson: missed-trade lesson if it would have worked; learning-no-lesson if it wouldn't have

**Top Playbook:** <name>
**Trade Rating:** NOT-TAKEN (separate from A-F grading)
```

The 4 journal subsections (Did Well / Went Wrong / Top Playbook / Trade Rating) MUST appear for every traded ticker — they populate the corresponding Notion sub-DB properties (`Did Well`, `Went Wrong`, `Top Playbook`, `Trade Rating`) on the Fresh News + Second Day Plays entries.

### Monitored but NOT TRADED
[Tickers where chart screenshots exist but no fills — confirms watch-discipline]

### Patterns Identified
[Behavioral patterns observed — account-separation shape, off-plan containment, banned-ticker respect, etc.]

### Discipline Score: X/10
[Breakdown by criterion incl. NEW criterion: "Disciplined account separation" — LIVE activity serves the published plan, not parallel-impulse]

### Multi-Day Trend
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
[Last 5-6 sessions with both accounts]

### Lessons
[1-3 actionable takeaways — include Kai's own meta-lessons if a workflow/tool gap surfaced]

### Behavioral Contract for Tomorrow
> *"[One-paragraph contract — what to maintain, what to refine]"*
```

### 9. Round-Trip Blotter (REQUIRED artifact — part of every review)

Generate a self-contained visual blotter charting **every round-trip** on the 1-minute tape, and include it in the review. Standing deliverable (David's request, 2026-07-25).

**Data:**
- Round-trips: `falcon-trades` DynamoDB (`PK=TRADE#YYYY-MM-DD`) — per RT: symbol, side, shares, avg_entry, avg_exit, entry_time, exit_time, pnl, r_multiple. **Trade times are ET.**
- RTH 1-min bars: TradingView `get_ohlcv` (`1m`) per traded symbol. **TV bar `t` is UTC**; map a trade's ET time to bar time as **UTC = ET + 4h (EDT) / +5h (EST)** — use `ZoneInfo`, never hardcode.
- **Premarket bars (before 09:30 ET): TradingView has NONE** — pull from **Massive.com flat files** via the `market-data` skill (`us_stocks_sip/minute_aggs_v1/YYYY/MM/DATE.csv.gz`). CSV cols: `ticker,volume,open,close,high,low,window_start(ns),transactions` — note the **open,close,high,low** order; `window_start` is ns UTC.

**Render — use the tradekit routine (built for this):**
```bash
cd ~/src/tradekit && PAI_AWS_PROFILE=pai-workstation-lenovo AWS_REGION=us-east-2 \
  .venv/bin/tradekit blotter YYYY-MM-DD \
  --out ~/.claude/LifeOS/USER/TRADING/Reviews/YYYY-MM-DD-blotter
```
(The command's default output is `~/market_data/blotter/{date}`; pass `--out` to land it in the Reviews archive.)
`tradekit blotter DATE` (module `tradekit.reports.blotter`) pulls round-trips from `falcon-trades` DynamoDB + all-session 1-min bars from Massive flat files and writes **one PNG per round-trip** → `~/.claude/LifeOS/USER/TRADING/Reviews/{DATE}-blotter/`. Dark terminal candlesticks, entry ▲ / exit ▼, win green / loss red. (Interactive HTML version — canonical template `Reviews/2026-07-24-blotter.html` — is optional.)

**Publish (part of the deterministic publish set):**
1. PNGs are archived by the command → `Reviews/{DATE}-blotter/`.
2. **Upload the PNGs into the Notion EOD page inside a collapsible toggle** so the charts render inline. The Notion MCP attachment tool CANNOT upload local files (only public URLs / inline text) — use the **Notion File Upload API** via `~/.claude/Tools/notion_blotter_upload.py YYYY-MM-DD <notion_page_id>` (reads `NOTION_API_KEY` from `~/.claude/.env`; `--dir` defaults to the Reviews blotter folder). It uploads each PNG and appends one collapsible toggle with all charts as children. *(This uploader is personal-infra glue, deliberately kept out of the public tradekit repo.)*
3. (Optional) also publish the interactive HTML as an Artifact + link it in the review `.md`.

Linked: `[[r-units-default]]`, `[[reference_falcon_stats_lenovo]]`, `[[reference_massive_setup]]`.

### Anti-patterns (DO NOT)

- ❌ Hand-roll P&L from Trades.csv with FIFO matching — wrong round-trip count, undercounts P&L
- ❌ Report SIM-only data via `/tmp/das_quote.py` and call it "the day" — that script defaults to {{SIM_ACCOUNT}} and is LIVE-blind by design (use `--all-accounts` flag if you must pull DAS direct)
- ❌ Draft the P&L summary before `falcon-stats ingest` returns
- ❌ Skip the equity curve (peak/trough/max DD) — those metrics are baked into the DailyStats output specifically because they reveal the day's shape that raw P&L hides
- ❌ Quote "Avg R" without checking whether trades had `planned_stop` set — most manual trades don't, making R unreliable; note "R unreliable today" when applicable

### Cross-references
- Multi-account spec: `[[trading-skill-multi-account-spec]]` — CRITICAL, 2 recurrences
- Account column parsing: `[[check-account-column-first]]`
- DAS routing safety: `[[das-sell-opens-short-not-close]]`
- Position state verification: `[[check-position-state-before-recommending]]`
