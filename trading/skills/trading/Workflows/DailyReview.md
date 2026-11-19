---
description: Generate annotated daily report card with grades and pattern analysis
---

# DailyReview Workflow

**Depends on:** a **running DAS session** — Step 0 captures the blotter over the CMD API and
writes the exports itself. It no longer depends on someone having exported from the DAS UI.
Export root is `Desktop/Trade_Review/YYYY/MM/YYYY-MM-DD/` (e.g. under
`{{WINDOWS_HOME}}/OneDrive/Desktop/`) — moved to `Morning_Review` 2026-07-01 and **back to
`Trade_Review` 2026-09-03**, so Cobra reports now sit in the same folder as that day's chart
images. Read it from `TRADE_REVIEW_PATH`, never a literal.

**Host tools.** Scripts referenced as `~/.claude/Tools/<name>` (`das-capture-nightly.sh`,
`falcon-stats`, `position_check.py`, `streak_check.py`, `martingale_check.py`, `iv_rank.py`,
`discord_post.py`, `roundtrip_report.py`, `notion_blotter_upload.py`, `falcon-cluster-handoff.sh`)
are host tools the operator provides at those paths. They are not bundled with this skill.

## ⛔ HARD RULES (do not skip — all have failed in production)

0. **`Reference/ReportingSchema.md` is the canonical contract.** The grade ladder, the
   7-criterion discipline rubric (shown as a per-criterion table, not just a total), the multi-day
   comparison columns, R rendering, and file naming all come from it — not from templates
   inlined in this file. Where this workflow and the schema disagree, **the schema wins**.
   Rule 0 of the schema also applies: anything a tool does not yet compute is ASPIRATIONAL and
   cannot be used to score a review.
1. **`falcon-stats ingest` is the ONLY allowed P&L source.** Do NOT hand-roll FIFO aggregation from Trades.csv directly — it produces wrong round-trip counts and undercounts P&L. (Failure mode 2026-06-02: hand-rolled FIFO undercounted LIVE P&L because it grouped by ticker instead of identifying entry→exit clusters.)
2. **Both accounts MUST be confirmed before drafting any P&L summary.** Live ({{LIVE_ACCOUNT}}) AND Sim ({{SIM_ACCOUNT}}). If only one account's data is in hand, the draft is BLOCKED — surface the gap, request the other source, do NOT draft-with-assumption. (Failure mode 2026-06-01 + 2026-06-02: reported a flat LIVE day with zero LIVE visibility while the operator had dozens of LIVE fills.)
3. **R-units required for all P&L + outcome reporting.** Read the R-CONFIG block at `~/.claude/LifeOS/USER/SKILLCUSTOMIZATIONS/Trading/PREFERENCES.md → Trading Preferences → Risk Parameters` at the start of every run. Express the P&L summary in both R-units AND dollars (R first, dollar in parens). Trade grades use R-outcomes (e.g., "+2.3R" / "−0.5R"). Daily max + per-trade caps in R. Linked memory: `[[r-units-default]]`.
4. **Publish is deterministic.** After synthesis completes, immediately fire Reviews file write + Slack post + **Discord Daily Report Card post** + Notion append in parallel. Do NOT prompt the user about publishing or channel selection. Content adjustments are askable; the act of publishing is not. Failures are isolated — a Discord webhook error must not block Slack, Notion, or the Reviews file. Linked memory: `[[publish-is-deterministic]]`.
5. **Channel topology + Notion protocol.** Slack #general ({{SLACK_PUBLIC_ID}}) + Notion + **Discord Daily Report Card** = PUBLIC; Google Drive = PRIVATE. The Discord forum channel receives **accountability-only content in R-units** — discipline score, 1% Change result, per-ticker grade + R-multiple, one pattern, one lesson. Never dollar P&L, account IDs, LIVE/SIM assignment, equity-curve figures, or share counts. Notion review section appends to the day's main page following the 7-section protocol (see `~/.claude/LifeOS/USER/SKILLCUSTOMIZATIONS/Trading/NOTION_PROTOCOL.md`). Required post-review property updates on the main page: `Status=REVIEWED`, `Combined R=<float>`, `Discipline Score=<1-10>`, `Thesis Outcome=<WIN/LOSS/INVALIDATED/NOT-TAKEN>`. Required sub-DB updates: set `Outcome` (WIN/LOSS/SCRATCH/NOT-TAKEN) on each Fresh News + Second Day Plays entry that fired. Private Drive: upload full `REVIEW-YYYY-MM-DD.md` to `Game_Plan` folder. Linked: `[[channel-topology]]`, `[[notion-gameplan-protocol]]`.

6. **Falcon-cluster bus.** After publishing the public + private artifacts, post a review-complete beacon to Slack #falcon-cluster ({{SLACK_CLUSTER_ID}}) so LifeOS agents on other machines (ddd-laptop, home-pda) detect this session's review state without polling S3. Use `~/.claude/Tools/falcon-cluster-handoff.sh state "DailyReview published — Combined R=<R> · Discipline=<N>/10 · channels: Notion+Slack+Drive"` OR `slack_send_message` to {{SLACK_CLUSTER_ID}} from within the session. Linked: `[[falcon-cluster-agent-sync]]`.

7. **Capture before DAS closes — this is the only irreversible step in the workflow.** SIM fills exist ONLY inside the running DAS session; no broker statement carries them and nothing reconstructs them afterwards. Run Step 0 FIRST, before any analysis. **DAS must not be shut down until the capture logs `RESULT: ok`.** (Failure mode 2026-08-07 → 2026-08-18: nine consecutive sessions lost because the manual end-of-day export never ran and nobody noticed until 08-18. Those days are gone permanently — they cannot be backfilled from any source.) Linked memory: `[[project-das-daily-sim-capture]]`.

8. **Volatility context is a required field on every graded trade.** Run
   `~/src/tradekit/.venv/bin/python ~/.claude/Tools/iv_rank.py <tickers>` for every traded ticker plus
   SPY, and put a `**Vol context:**` line in each journal block: `IV30 · IVR · IV%ile · HV20 · IV/HV`.
   The P&L summary carries SPY's line. Operator rule 2026-09-24, citing Bob Sosnoff (Tastytrade /
   Lossdog.com): ignoring volatility as a factor of any trade may make it impossible to be profitable.
   **IVR prints `n/a` until the local history has ≥20 sessions for that ticker** — write it as `n/a`
   with the session count and use the IV/HV ratio as the stated proxy. Never invent a rank. A stop
   that was sized off price on a high-IVR name, or a breakout chased at low IVR with no volume, is
   graded under criterion 3 / 2 respectively with the vol line as the evidence. Linked memory:
   `[[iv-rank-in-reviews]]`.

9. **Market Vision alignment (Kestrel D-18, 2026-11-17).** Pull the day's reads from
   `~/.claude/LifeOS/USER/TRADING/Vision/vision-log.jsonl`.
   - Put the verdict sequence (premarket → 08:45 → updates → 14:30) in the P&L summary.
   - In each journal block, add `**Vision:** <verdict at entry> · with / against`.
   - An entry against a TREND verdict (I-28) is graded under "Followed morning game plan".
   - If no read exists for the day, write `Vision: UNAVAILABLE — no read logged`. Never reconstruct one after the fact.
   - **Four-box (D-19):** add the box sequence (open → midday → close) to the summary, and `box at entry · with / against` to each journal block. A momentum entry in **LSLW**, or a counter-trend continuation in a trend box, is graded under "Followed morning game plan". If no box was logged, write `Box: UNAVAILABLE`. Never reconstruct it from bars after the fact.
   - **Ratio grid (D-24):** add the grid count sequence (premarket → open → midday → close, e.g. `1/4 → 2/4 → 3/4`) and any pair that printed a **higher low** to the summary. In the market-evaluation paragraph, say whether the tape was a counter-trend bounce (falling ratios) or a tone change (higher lows, rising slopes). Context only, not graded. If no grid was logged, write `Ratios: UNAVAILABLE`. Never rebuild it from bars after the fact.

Linked memory: `[[trading-skill-multi-account-spec]]` (severity: CRITICAL, recurrences: 2)

## Steps

### 0. Capture + Canonical Ingest (REQUIRED FIRST STEP — run before anything else)

**Do this before reading a chart, before opening Notion, before any analysis.** Everything
downstream is reconstructible from DynamoDB; the DAS session blotter is not. Capture first,
think second.

**SOURCE PRECEDENCE — LIVE and SIM are NOT the same chain.**

| Account | Authority | Then | Fallback |
|---|---|---|---|
| **LIVE** ({{LIVE_ACCOUNT}}) | **broker transaction log / broker report** | DAS report | CMD API capture |
| **SIM** ({{SIM_ACCOUNT}}) | DAS report | — | CMD API capture |

**For LIVE the broker log REPLACES the DAS report.** It is a recount of exactly what
transacted in the marketplace — the counterparty's own record of what cleared. DAS is the
front end; the broker is the record. Where they disagree the broker wins: busted or amended
trades, price improvement and real fees appear there and not necessarily in the DAS view.

**The broker record exists for LIVE ONLY.** SIM has no counterparty, so nothing outside DAS
ever witnessed those fills. That is why a SIM session lost before capture is unrecoverable
from any source, and why DAS sits at the TOP of the SIM chain rather than the middle.

The CMD API capture is the **fallback for both** — it runs only when no report exists for the
date, and it must never overwrite one.

```bash
# Skips automatically and exits 0 if operator reports already exist for the date.
# Captures over the CMD API only as the fallback, then runs `falcon-stats ingest`.
~/.claude/Tools/das-capture-nightly.sh
```

**The EOD process must never clobber the reports.** On 2026-08-18 this step ran at 18:47 and
rewrote the operator's 17:18 `Trades.csv` / `Orders.csv`, and the review was then built on the
fallback source. The capture is scoped to `DAS_ACCOUNT`, so it returned **SIM only** while the
reports carried **both accounts** — the LIVE trade (the planned short) was invisible until
the per-account reports were re-exported by hand, and the review's headline finding was wrong
until then. The guard now refuses; `DAS_CAPTURE_FORCE=1` overrides deliberately.

**Report files to look for** (any one means reports exist):
`Trades.csv` · `Orders.csv` · `Accounts.csv` · `Tickets.csv` · `Accounts-<ACCOUNT>.csv`

`Accounts-<ACCOUNT>.csv` is the per-account breakdown and is the cleanest source for
per-account P&L — it carries `Trades`, `Day-trade P&L`, `Short Shares` and `Net Share` per
symbol, which is everything the report card needs except per-fill timestamps.

Exit codes — **treat 2 as an incident, not a warning**:

| Code | Meaning | Action |
|---|---|---|
| 0 | Captured + ingested, or a genuine flat day (says which) | proceed |
| 2 | **DAS was not running — today's SIM fills are gone permanently** | log it, note the gap in the review, do not pretend the day was flat |
| 3 | Login rejected | fix creds in `~/.claude/.env`, rerun |
| 4 | Orphan fills — some fill had no matching order | rerun with `--settle 15`; never ingest a partial session |
| 5 | Ingest failed | CSVs are on disk, re-ingest with `~/.claude/Tools/falcon-stats ingest <dir>` |

**If DAS is already closed** the CMD API has nothing to give. Fall back to whatever CSVs the
UI happened to write, and if there are none the day is unrecoverable — say so in the review
rather than reporting a flat day. A silent zero and a lost day must never render the same.

**`--date` CANNOT recover an earlier session.** DAS sends fills as `HH:MM:SS` with no date;
the tool stamps them with whatever `--date` says. Pointing it at a past date therefore
**relabels the currently-loaded session and fabricates a record for that date**. On 2026-08-25
this wrote that day's round-trips into the previous date's `TRADE#YYYY-MM-DD` partition and
export folder; both had to be deleted by hand. The tool now refuses unless `--force-relabel` is passed.

A genuinely missed date is recovered from the **reports**, not from DAS:
```bash
~/.claude/Tools/falcon-stats ingest <path-to-that-date's-export-dir>
```

Ingest auto-splits by the `Account` column, writes to DynamoDB, and prints DailyStats per
account: realized P&L, win rate, peak equity (w/ time), trough equity (w/ time), max
drawdown (w/ time), streak. Re-running is **idempotent** — stale rows for that date+account
are deleted before the rewrite, so capturing twice in a session is safe and costs nothing.

**Always invoke `~/.claude/Tools/falcon-stats`, never the bare binary or the venv path.**
Without the wrapper, `db.py` falls through to the ambient `[default]` AWS profile — a
different account in the wrong region where `falcon-trades` does not exist. DynamoDB does
not error there, it returns **zero rows**, which this workflow would render as "no trades
today." Linked memory: `[[reference-falcon-stats-lenovo]]`.

**Output to capture verbatim from `falcon-stats ingest`** — this is the source of truth for the report card:
- Round-trip count (NOT raw fill count)
- Realized P&L per account
- Win rate + W/L count per account
- Peak equity + timestamp per account
- Trough equity + timestamp per account
- Max drawdown + timestamp per account
- Streak (NW or NL)

If `falcon-stats ingest` errors or returns no rows, **STOP and diagnose** — do not fall back to hand-rolling. Common causes: wrong export path, Trades.csv missing the Account column, broker rrno format change.

### 0b. Position Size Check (REQUIRED — run before grading anything)

```bash
python3 ~/.claude/Tools/position_check.py <export-dir>/Trades.csv
```

Exit 0 ok · 1 marginal · **2 oversized**. `R_VALUE` and `MIN_STOP_ATR` are read from the
PREFERENCES R-CONFIG, never hard-coded in the script.

```
max_shares = R_VALUE / (MIN_STOP_ATR x ATR14_at_entry)
```

**Risk is `shares x stop_distance`. Notional is the cost of the position and does not bound
risk** — the stop distance comes from the instrument's volatility, not its price. A notional
cap fails hardest on low-priced high-volatility names, which is where the playbook lives.

**Why this runs before grading.** A stop can only be honored if it can be placed. If a
1R-compliant stop would sit inside the noise band, a `PER_SYMBOL_MAX_R` breach is **arithmetic,
not willpower** — and grading it as stop discipline prescribes the wrong fix.

| Result | Reading | Fix |
|---|---|---|
| **OVERSIZED** | 1R stop was unplaceable at that size | **Reduce shares.** "Honor your stops" is not the remedy |
| **ok / marginal** + large loss | Stop was placeable and was not placed | **Genuine stop discipline.** Score under criterion 3 |

**Two gotchas, both learned the hard way on 2026-08-28:**

1. **Measure ATR at the entry timestamp.** A name entered premarket mid-spike had an ATR nearly
   4x what it read 35 minutes later. At entry the position was close to 2x oversized; measured
   later, the same position looks compliant.
2. **A DAS chart's ATR readout refers to the last bar in its loaded dataset**, not the window
   on screen. A chart opened in the evening reports post-market ATR even when scrolled back to
   the trade. On 08-28 one chart's ATR readout matched the post-market value, roughly a tenth of
   the trade-time ATR. The indicator was right; it was answering about a different bar.

### 0c. Losing-Streak Check (REQUIRED — run with 0b)

```bash
python3 ~/.claude/Tools/streak_check.py <export-dir>/Trades.csv
```

Exit 0 no trigger · 1 a trigger fired and the stand-down held · **2 stand-down violated**.
Thresholds are read from the PREFERENCES `LOSING_STREAK_POLICY` block.

**The trigger is not the failure — the next entry is.** The ladder cannot prevent the first
large loss; only the entry bracket does that (0b). Its job is the trade *after*. So read the
output for the violation lines, not the trigger lines.

**Output shape** (illustrative tickers and values):

```
[T1] HH:MM:SS L1  AAA cumulative -N.NR    stand-down 15 min  -> !! opened BBB after 8 min
[T2] HH:MM:SS L2  drawdown N.NR           stand-down 30 min  -> !! BBB 8 min, CCC 21 min
[T1] HH:MM:SS L3  DDD cumulative -N.NR    SESSION OVER       -> !! DDD 0, EEE 12, FFF 53
```

**Read 0b and 0c together; they compose.** On 2026-08-28 the ladder ended the session early
only because sizing had already been skipped. Re-scored with ATR-compliant sizes, the same
trades flip from a net loss to a net gain in R, and the ladder degrades from a shutdown to two
15-minute pauses — Level 3 never fires. A Level 3 in the report is therefore usually evidence of a
**sizing** failure upstream, not of an unusually bad tape.

**Do not conclude a trigger cost the operator money** without re-scoring at compliant size
first. On the raw numbers that shutdown looks like it forfeited a later multi-R winner; at
correct size the shutdown never happens.

### 0d. Martingale Check (REQUIRED — automatic F, run with 0b/0c)

```bash
python3 ~/.claude/Tools/martingale_check.py <export-dir>/Trades.csv
```

Exit 0 clean · **2 averaging down found**. Operator rule 2026-11-14 (Kestrel SPEC D-15 / I-23).

- **Averaging down** = a new order that adds to an open position while it is underwater against its
  average cost: a long add below the average, or a short add above it. Partial fills of one order
  count once. **There is no price tolerance.** A 10-cent add against you is still an add against you.
- **Penalty:** every flagged account+ticker gets **Trade Rating F, automatically**, regardless of
  the trade's outcome or anything else about it. In the journal block, write `AUTO-FAIL:
  martingale` plus the add (time, held @ avg → added @ price). The public card shows the F. The
  **discipline score is scored normally**, so do not deduct twice for the same add.
- **Out of scope:** sizing up on a *fresh* trade after a loss (that's the operator's choice,
  2026-11-14). It is still graded by judgment under revenge and sizing.
- **First run (backfill):** run it over recent sessions when first installed; the initial backfill
  flagged adds in both accounts across several sessions.

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
| Covariance alignment | High | **ASPIRATIONAL (Rule 0): do not score until a tool computes it** (Kestrel `kestrel.zscore`, D-7). Did the trade direction match the z-score signal? (NORMAL → FL long, EXTREME → Offsides short) |
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

After generating the review, post to Slack channel **#general** (ID: `{{SLACK_PUBLIC_ID}}`, workspace
`{{SLACK_WORKSPACE}}`) using this format.

<!-- 2026-07-28: this step previously said "#watchlist ({{SLACK_WATCHLIST_ID}})", contradicting Hard Rule 5
     in this same file. Verified via the Slack API that no #watchlist channel exists in the
     workspace — #general ({{SLACK_PUBLIC_ID}}) is the real target, matching [[channel-topology]]. Posts
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
export AWS_PROFILE={{AWS_PROFILE}} AWS_DEFAULT_REGION={{AWS_REGION}}
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

**Vol context:** IV30 · IVR (or `n/a (N sess)`) · IV%ile · HV20 · IV/HV at entry — from `iv_rank.py`; one line, then the read (rich/cheap/mid)

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
[Per-criterion table, the 7-criterion rubric in Step 4 (ReportingSchema Rule 5). Never a bare total.]

### Multi-Day Trend
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
[Last 5-6 sessions with both accounts]

### Lessons
[1-3 actionable takeaways — include Kai's own meta-lessons if a workflow/tool gap surfaced]

### Behavioral Contract for Tomorrow
> *"[One-paragraph contract — what to maintain, what to refine]"*
```

### 9. Round-Trip Blotter (REQUIRED artifact — part of every review)

Generate a self-contained visual blotter charting **every round-trip** on the 1-minute tape, and include it in the review. Standing deliverable (operator's request, 2026-07-25).

**Data:**
- Round-trips: `falcon-trades` DynamoDB (`PK=TRADE#YYYY-MM-DD`) — per RT: symbol, side, shares, avg_entry, avg_exit, entry_time, exit_time, pnl, r_multiple. **Trade times are ET.**
- RTH 1-min bars: TradingView `get_ohlcv` (`1m`) per traded symbol. **TV bar `t` is UTC**; map a trade's ET time to bar time as **UTC = ET + 4h (EDT) / +5h (EST)** — use `ZoneInfo`, never hardcode.
- **Premarket bars (before 09:30 ET): TradingView has NONE** — pull from **Massive.com flat files** via the `market-data` skill (`us_stocks_sip/minute_aggs_v1/YYYY/MM/DATE.csv.gz`). CSV cols: `ticker,volume,open,close,high,low,window_start(ns),transactions` — note the **open,close,high,low** order; `window_start` is ns UTC.

**Render — use the tradekit routine (built for this):**
```bash
cd ~/src/tradekit && PAI_AWS_PROFILE={{AWS_PROFILE}} AWS_REGION={{AWS_REGION}} \
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
