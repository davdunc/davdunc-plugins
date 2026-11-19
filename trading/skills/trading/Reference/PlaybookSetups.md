# Playbook Setups

## Active Setups

### Gap Up / Gap Down
- **Trigger:** Pre-market gap > 3% with catalyst and volume
- **Entry:** Wait for first pullback after open, enter on reclaim of VWAP or key level
- **Stop:** Below pre-market low (long) or above pre-market high (short)
- **Target:** Previous day high/low or ATR extension

### Opening Range Breakout (ORB)
- **Trigger:** Stock establishes clear range in first 5-15 minutes
- **Entry:** Break above/below the range with volume confirmation
- **Stop:** Opposite side of the opening range
- **Target:** 1:2 or 1:3 R:R based on ATR

### VWAP Plays (Reclaim / Rejection)
- **Trigger:** Stock approaching VWAP with momentum
- **Entry:** Long on VWAP reclaim with volume; short on VWAP rejection with volume
- **Stop:** Opposite side of VWAP + buffer
- **Target:** Next key level or previous high/low of day

### Fashionably Late (FL) — 9-EMA × VWAP Cross
- **Trigger:** 9-EMA crosses UP through VWAP (long) or DOWN through VWAP (short), confirmed by significant increase in volume OR ATR at the cross candle
- **Entry:** On the cross candle close, after open volatility settles (typically after 10:00 ET)
- **Stop:** Below VWAP (long) or above VWAP (short) + ATR buffer. If using 2× ATR stop → cut shares in half
- **Target:** Next key level, R3/S3 Camarilla, or ATR extension
- **Confirmation required:** Volume spike (>2× recent average) OR ATR expansion on the cross candle — without one of these the cross is noise
- **Volume must PERSIST, not just spike — the 50/2 rule:** call the confirmation candle's volume `V0`. Each of the **next two candles must print ≥ 50% of `V0`**. If either fails, the move has no supply behind it: **exit at that candle's close and do not re-enter on the same signal.** A re-entry is a fresh setup and needs a fresh `V0`, measured from the bar you are re-entering on — never from the original spike.
- **Disqualifiers:** EXTREME z-score (>3) on the long side; cross before 10:00 ET; **any name that executed a reverse split within the last 5 sessions** (see below)

> **Why the persistence rule exists — LGCL, 2026-09-01.**
> The entry was correct on every stated criterion: 9-EMA had been above VWAP for eight
> minutes and the spread was widening, and the entry candle printed 37,565 shares against a
> 14,663 four-bar average — **2.56×**, clearing the spike requirement outright. Then volume
> collapsed 95% in seven minutes: 37,565 → 21,745 → 11,451 → 12,154 → 12,959 → 5,218 → 2,938 → 1,992.
>
> **The indicator never signalled an exit.** The 9-EMA/VWAP spread kept *widening* the whole
> way down, +0.215 at entry to +0.301 twelve minutes later. Price and volume left; the signal
> stayed bullish. Any rule that reads only the cross will hold you through this.
>
> Applied to that tape, the 50/2 rule fires at 09:55 (11,451 = 30% of `V0`) and exits only
> marginally better than the actual stop. **Its real value is the second half:** it blocks the
> 09:57 re-entry, where trailing volume was 12,959 = 34% of the original `V0`. That re-entry
> was the larger of the two losses.
>
> **The threshold is provisional.** 50% over two candles is derived from one session and has
> not been validated across a sample. It is deliberately loose — a normal liquid name easily
> holds half its spike volume for two bars, so this should almost never fire on the tape FL is
> designed for. If it fires often on liquid names, it is mis-tuned; raise the bar count before
> raising the percentage.
>
> **Enforcer:** `~/.claude/Tools/fl_volume_check.py` (operator-local tool, not shipped in this plugin) — checks all three gates against live
> DAS bars in about four seconds. Run it the minute after an FL entry candle closes:
> ```
> fl_volume_check.py LGCL                                   # live, last closed bar
> fl_volume_check.py LGCL --entry 09:53                     # live, a specific entry
> fl_volume_check.py LGCL --date 2026-09-01 --entry 09:53   # replay
> ```
> Exit 0 PASS · 1 FAIL · 2 PENDING · 3 no data. It reports PENDING rather than PASS when a
> follow bar has not closed — a pass on evidence that does not exist yet is the same error
> as reading the spike alone. Per `Reference/ReportingSchema.md` Rule 0 the rule is now
> enforceable, but the 50 pct threshold itself is still unvalidated: use it to gate a trade,
> not yet to grade one.

> **Reverse-split names cannot support FL.**
> FL needs a volume base to sustain the move, and a name whose float was just compressed has
> no such base — one spike candle can be the entire session's interest. LGCL executed a
> **1-for-125 reverse split on the morning it was traded** (its second in eleven months,
> after a 1-for-40 in Oct 2025).
>
> There is a second, worse problem: **the ATR is unusable on these names, and it fails
> loudly enough to notice only if you look.** LGCL's prior-day ATR14 computed to **24.327 on
> a $4.69 stock** because the price history is unadjusted against the same-day action.
> `sizing_column.py` returns a share count from that number without flagging it. Check
> `https://api.polygon.io/v3/reference/splits?ticker=<T>` before sizing any sub-$10 name.
> Linked: `[[falcon-split-unaware]]`, `[[dilution-scan-needs-edgar]]`.

#### Backtested 15-minute rule (2026-09-27) — the tradeable form of FL

> Three years of Massive minute data (2023-09-25 → 2026-09-25), 16 gameplan single stocks,
> `{{DAS_HOTKEYS_REPO}}/backtest/backtest_fl_week.py`. The 1-minute cross as traded on
> 2026-09-24 has no edge (−7,680R). The 15-minute version does, and only in this form:
>
> - **Chart:** 15-minute, **regular hours only**, 9-EMA and 34-SMA warm from four prior sessions.
> - **Signal:** a completed bar whose close moves the 9-EMA across the 34-SMA, with that bar's
>   volume > 1.5× the average of the prior 20 bars. **A cross printed on a prior day's bar does
>   not count** (see the gate correction below).
> - **Entry:** market at the next bar's open, **09:45–11:00 only**. Two entries per name per day.
> - **Stop:** 0.75 × ATR(14, 15-minute), sized as if it were 1.5×ATR; 1R per PREFERENCES.md R-CONFIG.
> - **Breakeven:** stop to entry once a completed bar has shown +0.5R.
> - **Exit:** hold to the close. No target, no partials (a +1R partial removes 85% of the P&L).
> - **Universe:** single stocks only; the seven ETFs and commodities lost money under this rule.
> - **Catalyst (2026-09-27, EDGAR join):** prefer names with an earnings release or 8-K in the prior
>   24 hours. Those are 9% of trades and 30% of the paper profit (204 trades, +59R, +0.29R each vs
>   +0.07R; p = 0.004) and **three quarters of what survives 5¢ slippage (+48R vs +17R)**. With
>   ordinary fills FL is a catalyst trade; without one, trade it only if measured stop slippage is
>   under 2¢. `{{DAS_HOTKEYS_REPO}}/docs/forward-tests/catalysts-2023-2026.md`.
>
> | Result, three years | Trades | Win rate | R | Max DD | Sharpe | 5¢ stop slippage |
> |---|---:|---:|---:|---:|---:|---:|
> | Rule above | 2,282 | 9.9% | +201 | 12.4R | 2.17 | +65 |
> | First-bar entries only (09:45) | 1,073 | 10.2% | +150 | | | +82 |
>
> Half the trades scratch at breakeven; one in ten pays, averaging 2.6R. The edge is the first
> bar after the open and decays to nothing by 11:00.
>
> **Gate correction (2026-09-27).** The figure of +292R quoted on 09-26 counted 387 entries at the
> 09:30 open on a cross printed on the *prior day's* 15:45 bar (the backtest gated on the signal
> bar's time, so yesterday's close passed a 09:45 gate). Those made +242R and are a different,
> untested trade ("overnight cross"); removed, the intraday rule is +201R. Never quote the old number.
>
> **PlayBook (SMB format):** `{{DAS_HOTKEYS_REPO}}/docs/playbook/PlayBook-Fashionably-Late.pptx`
> (also on OneDrive Desktop/PlayBooks). Example chart: MSTR 2026-08-27, 09:45 long.
> **Driver flags still to build:** `--bar-minutes 15 --stop-mult 0.75 --be-after 0.5 --last-entry
> 11:00`, single stocks only, breakeven via `%OrderAct`.

### 34-SMA Premarket Trend (S34PT) — pre-open limit at the 34-SMA in the premarket trend
*Backtested 2026-09-27, three years, 14 medium/large-cap gameplan stocks
(`{{DAS_HOTKEYS_REPO}}/backtest/backtest_sma34_trend.py`, report
`{{DAS_HOTKEYS_REPO}}/docs/forward-tests/sma34-trend-3y.md`). Status: **1R paper experiment**, in-sample.*

- **Scan (09:15):** premarket volume ≥ 2× the name's own 20-day median premarket volume. Best
  between 2× and 3×; above 5× it trades worse. No ETFs, commodities, sub-$10 or reverse-split names.
- **No catalyst of its own (2026-09-27, EDGAR join):** skip any name that reported earnings or filed an
  8-K in the prior 24 hours. 84% of earnings mornings pass the premarket filter and they lose (106
  earnings/8-K trades, −27R, −0.26R each; p = 0.017). Without them: 627 trades, **+114R**, DD 26.7R,
  **+69R after 5¢ slippage**. The heavy premarket this play wants is a sympathy move, upgrade or sector
  headline, not the company's own report. `{{DAS_HOTKEYS_REPO}}/docs/forward-tests/catalysts-2023-2026.md`.
- **Direction:** on the **extended-hours 15-minute chart**, 9-EMA above the premarket VWAP → long,
  below → short. Read once, pre-open.
- **Order (before 09:30):** limit at the 34-SMA value of the last completed 15-minute bar before the
  open, only if the 09:29 price is on the trade side of it (buy below the market / short above it).
- **Stop:** **1.0 × ATR(14, 15-minute)**, bracketed with the order. Not 0.75: the opening minute's
  range takes a 0.75 stop within a median of one minute (344 of 521 first-fifteen-minute fills).
- **Target:** none. **Exit on the first 15-minute close back across the 9-EMA**, after at least one
  bar has closed with the trade. Flat at 15:55. One entry per name; one position per day if that
  is the account rule.
- **Size:** 1R ÷ stop distance, with 1R and the share cap per `PREFERENCES.md` R-CONFIG.

| Form, three years | Trades | Win rate | R | Max DD | 5¢ stop slippage |
|---|---:|---:|---:|---:|---:|
| **As above** (pre-open order, 1.0×ATR, 9-EMA exit) | 733 | 27.1% | **+86.5** | 35.4R | +35.3 |
| Same, one position a day (heaviest premarket) | 230 | 28.3% | +31.9 | 19.9R | |
| Original idea: 0.75×ATR stop, 1.8R target, pre-open | 733 | 33.7% | −14.3 | 53.5R | −70.3 |
| Original idea, re-priced intraday, extended-hours chart | 1,034 | 35.5% | −70.7 | 103.9R | −130.6 |
| Intraday, regular-hours chart, entries 10:00–14:00, 1.8R target | 576 | 41.3% | +50.7 | 16.3R | +18.7 |

**What the test taught.** With a 1.8R target the trade is a coin flip on the opening range at
a 35.7% breakeven win rate. The two changes that made it work are the trailing exit (winners
average 2.6R, the ten largest are 144% of the profit) and a stop outside the opening minute.
2024 was flat and the three months of 2023 supplied 38 of the 86R: **in-sample**, walk-forward
pending. **Do not trade it off a regular-hours chart in this form** (+13R) and do not add a
target or partials.

**PlayBook (SMB format):** `{{DAS_HOTKEYS_REPO}}/docs/playbook/PlayBook-34SMA-Premarket-Trend.pptx`
(also on OneDrive Desktop/PlayBooks). Example chart: RKLB 2026-05-11, 09:30 entry, 15:30 exit.
**To build:** premarket-ratio scan in the driver, pre-open bracket
hotkey, 9-EMA-close exit monitor; measure the first twenty live stop fills on {{SIM_ACCOUNT}} first.


### Late-Day 9/34 Cross (LD934) — volume-gated EMA/SMA cross

Operator's rule, stated 2026-09-05: **9-EMA crossing the 34-SMA, gated by volume.** With
volume the cross precedes a significant surge; without it, price cuts back through the entry
*and* the 34-SMA within 3 minutes. Reference instance: INTC 2026-09-04, entry 15:15-15:16 ET,
exit 16:22 ET, **+$1.09/share over 67 minutes**.

- **Timeframe:** 1-minute chart. 9-EMA and 34-SMA on close.
- **Trigger:** volume expansion **≥2× the trailing 30-bar average** on or immediately before
  the cross bar. On the reference instance the 15:15 bar printed **344,737 vs a 97,152
  average = 3.5×**, and the cross completed on the *next* bar.
- **Sequencing — volume leads, the cross confirms:**
  ```
  15:15   c 94.55   ema9 94.498  sma34 94.499  diff -0.001   vol 344,737 (3.5x)  <- volume
  15:16   c 94.62   ema9 94.524  sma34 94.502  diff +0.021   vol 218,334 (2.1x)  <- cross
  ```
  The volume bar is the leading edge; the cross is the confirmation one bar later. Waiting for
  the cross costs ~7¢ and removes the guesswork.
- **Entry:** the cross bar's close. *(94.62)*
- **Stop:** below the 34-SMA. Size from **1.5 × 5-minute ATR14** at entry — *not* the 1-min
  chart's ATR. See the sizing trap below.
- **Exit: the opposite cross.** This is not discretionary — the 16:22 exit on the reference
  instance **is** a 9/34 down-cross at 95.64, printed in the cross table for that day.
- **Time window:** trigger **15:00-15:40 ET**. See "why the window is the whole setup."
- **Result on the reference instance:** 94.62 → 95.64 = **+$1.02/sh**, high 95.94.

**Disqualifiers**
- Volume under 2× on the cross bar — this is the operator's own rule and it survives testing.
- Reverse split within 5 sessions.
- Any cross outside the 15:00-15:40 window.

---

#### Test of the volume gate — INTC, 2026-09-04, all 32 crosses

Every 9/34 cross that day, bucketed by volume, scored on whether price cut back through both
the entry and the 34-SMA within 3 minutes:

| Volume vs 30-bar avg | n | cut back ≤3 min | avg 10-min move |
|---|---|---|---|
| **≥3×** | 2 | **0 (0%)** | −0.120 |
| **2–3×** | 2 | **0 (0%)** | +0.059 |
| **<2×** | 28 | **7 (25%)** | −0.003 |

**The operator's claim is directionally confirmed:** zero cutbacks above 2× volume, 25% below
it. The volume gate does what he says it does.

**Three caveats that matter more than the confirmation.**

1. **n=4 above 2×.** One session. This is a signal to keep collecting, not a validated edge.
2. **The 10-minute expectancy above 3× was negative (−0.120).** Both ≥3× crosses were
   premarket down-crosses that went nowhere. **The edge is not a quick surge** — the reference
   trade measured at 10 minutes was **−0.01**, and made its $1.02 over the following hour. Do
   not judge this setup at 10 minutes; that is not where its money is.
3. **32 crosses in one session is unusable.** This is the same defect flagged in
   `[[project-ema9-sma34-cross-research]]` — the raw cross generates ~30× more signals than FL
   and drowns in them.

#### Why the 15:00-15:40 window is the whole setup

Applying the time filter to that day's 32 crosses leaves **exactly one: 15:16.** The one that
worked.

The window is not a preference, it is the mechanism. The move is fed by the **closing
auction** — the 15:55 five-minute bar carried **3,856,829 shares**, roughly 3× the entire
preceding hour's average, and it printed the high. A cross at 11:00 has no auction behind it.
A cross after 15:40 has no runway to reach it.

#### The sizing trap

Same 1.5-ATR rule, same stock, same minute — a **150× spread** depending on which chart the
ATR study sits on:

| Basis | Stop | Size @ 1R, relative to the governing row |
|---|---|---|
| 1-min ATR (what the DAS chart displayed: 0.031) | $0.047 | ~6.6× |
| **5-min ATR14 (`sizing_column.py`) — governs** | **$0.31** | **1×** |
| daily ATR14 (4.243) | $6.36 | ~0.05× |

`GetStudyVal($STUDY_ATR)` returns the study from whichever chart `$WND_CHART` names. **If that
is the 1-minute chart, the scripts will size off 0.031 and hand back a 4.7¢ stop** on a trade
meant to run an hour. Related: `[[reference-position-size-from-atr]]`,
`[[reference-das-getstudyval-label]]`.

#### The exit runs in after-hours — SLP is enabled and in regular use

The 16:22 exit fills on **22,197 shares** against 3.86M at the auction — a 99.4% liquidity
collapse. A market order there is a donation, and ordinary stop types (`SM`, `SL`) are blocked
outside RTH entirely.

**Stop Limit P (`SLP`) is enabled on this account and the operator uses it regularly**
(confirmed 2026-09-05). It is the only stop type that functions after 16:00.
The operator-local `DAS/ShortScripts.md` §3 (not shipped in this plugin) places one from a chart click.

#### RESOLVED — exit at the bell, not the reverse cross

Tested across 14 sessions × 5 tickers (INTC, AVGO, SNOW, DELL, MU), scoring every qualifying
15:00-15:40 volume-gated up-cross:

| | bell (16:00) | reverse cross |
|---|---|---|
| better in | **6 of 7** | 1 of 7 |
| avg move | **+1.552/sh** | +0.580/sh |
| win rate | **71%** | 29% |

**The reverse cross is a lagging exit.** By the time the 9-EMA crosses back under the 34-SMA
the move has already turned, and on the reference instance it also fills into 2,919 shares
where the order moves the price against itself. Flatten at the bell.

That also removes the after-hours dependency entirely — a 16:00 exit needs no `SLP`, no thin
book, and no attention after the close.

#### ⚠ THE EXPECTANCY IS ONE DAY — read this before sizing up

With a 1.5 × 5-min-ATR stop modelled, holding to the bell:

```
stopped out before the bell:  2 / 7
avg R, survivors only:        +1.36R  (n=5)
avg R, stop-outs at -1R:      +0.69R  (n=7)
```

+0.69R per setup at roughly 0.5 setups/day looks like an edge. **It is not, yet.** Split by
date:

| Sample | n | avg R |
|---|---|---|
| **2026-09-04 only** | 2 | **+3.35R** |
| **every other session** | 5 | **−0.38R** |

INTC +3.66R and MU +3.04R both landed on 09-04. Strip that one day and the remaining five
instances are **negative**. And 09-04 was **NFP day** — a high-volatility tape.

That matches `[[project-ema9-sma34-cross-research]]` exactly: *"edge is HPE-day-dependent;
needs multi-day validation."* This test does not overturn that note, it reproduces it.

**Compounding the problem:** the reference instance is one of the two 09-04 trades, and it is
the instance the setup was derived from. It cannot also be evidence for it.

**What this means for Tuesday.** Trade it in SIM, log every trigger taken or not, and record
the day's realised volatility alongside. The hypothesis worth testing is not "does LD934
work" — it is **"does LD934 work only on high-volatility days."** Five more instances split
by tape regime settles it. Until then, per `Reference/ReportingSchema.md` Rule 0, this must
not size LIVE capital.


#### The SHORT variant — inverse of the long, with two differences

Operator's reference instance: **INTC 2026-09-04, short 13:08, cover 14:26 on the reverse cross,
about +0.9% of price.** Structure mirrors the long exactly — a 9/34 **down**-cross at 13:04, entry four
bars later, and the reverse **up**-cross at 14:22 as the exit signal.

**Difference 1 — the short does NOT use the bell.** The long's edge is the closing auction
pushing price up; for a short that same auction is the risk. On this instance:

```
short 13:08 -> cover on the reverse cross 14:26   ≈  +0.9%
short 13:08 -> hold to the bell         16:00   ≈  -0.3%
```

**Difference 2 — no 15:00-15:40 window.** The long needs auction runway; the short does not.
This one triggered at 13:04. Tested range is 09:45-15:30.

#### Short-side test — 14 sessions × 5 tickers, 09:45-15:30

Exit on the reverse cross, 1.5 × 5-min-ATR stop, stop-outs scored −1R:

| Volume gate | n | avg R | stopped |
|---|---|---|---|
| **≥2×** | 17 | **+0.17R** | 1/17 |
| ≥1× | 136 | **−0.11R** | 7/136 |

**The volume gate is load-bearing on the short side too** — dropping it from 2× to 1× flips
expectancy negative and produces 136 signals in 14 days, which is unusable. That independently
corroborates the operator's rule.

**⚠ But the reference instance does not satisfy it.** The 13:04 down-cross printed **0.6×**
the 30-bar average, and 13:08 was **1.2×** — both in the bucket the test measures at −0.11R.
It is a winning trade drawn from a losing population. Either the short's volume read differs
from the long's, or this instance is a survivor.

**Opening-bar caution:** crosses in the first 15 minutes show volume multiples of 100×+ because
the 30-bar trailing average is nearly empty. Including 09:30-09:45 turned n=17/+0.17R into
n=40/−0.12R. Start the scan at **09:45**.

#### Superseded — original open question on the exit

On the reference instance the cross exit **cost 12¢/share**:

```
15:59   close 95.81   volume 1,582,118    <- closing auction
16:00   close 95.76   volume   113,835
16:22   close 95.64   volume     2,919    <- reverse cross. 0.2% of auction volume.

flatten at 16:00 -> 95.76      hold to the cross -> 95.64      -0.12/sh
```

At the governing 5-min-ATR size that is roughly 0.4R handed back. The cross also fills into 2,919 shares,
where the exit order itself moves the price. **Unresolved on n=1** — see the exit-rule test
below before treating either as the rule.


#### ⚠ LARGE-SAMPLE TEST — the raw cross has no edge, and RVOL does not separate

Re-run with the **correct RVOL definition** the operator uses: cumulative volume from the open
to the cross minute, divided by the **median cumulative volume at the same minute across the
prior 12 sessions** — time-of-day normalised. That measures whether the *name* is hot today,
which is a different question from whether one *bar* is a spike. The earlier tests on this
page used bar-vs-trailing-30-average and were measuring the wrong thing.

14 sessions × 5 tickers, 09:45-15:30, 1.5 × 5-min-ATR stop, stop-outs at −1R:

**LONG (n=408)**

| RVOL band | n | R @ reverse cross | R @ bell | stopped |
|---|---|---|---|---|
| ≥100% | 159 | −0.04 | **+0.21** | 9/159 |
| 70-100% | 123 | −0.03 | +0.13 | 4/123 |
| <70% | 126 | +0.03 | **+0.71** | 5/126 |

**SHORT (n=396)**

| RVOL band | n | R @ reverse cross | R @ bell | stopped |
|---|---|---|---|---|
| ≥100% | 152 | −0.04 | −0.23 | 10/152 |
| 70-100% | 120 | +0.01 | −0.33 | 2/120 |
| <70% | 124 | −0.12 | −0.80 | 6/124 |

**Three conclusions, in order of how well supported they are.**

1. **The raw 9/34 cross has no edge.** 804 instances, reverse-cross exits cluster at
   −0.04 to +0.03R — indistinguishable from zero after costs. This is the strongest result on
   the page and it is negative. The cross alone is not a signal.
2. **The long/short asymmetry around the close is real and large-sample.** Holding to the bell
   is positive for longs in every RVOL band (+0.13 to +0.71R) and negative for shorts in every
   band (−0.23 to −0.80R). n=804. **Longs hold into the auction; shorts must not.**
3. ~~RVOL does not separate winners from losers.~~ **This finding is void — it answers a
   question the rule never asked.** Clarified by the operator 2026-09-05: **RVOL is an
   admission screen, not a signal.** Its job is to confirm the name is *in play* and that the
   day's volume can support momentum — a floor to trade above, not a variable to optimise.
   Banding it and measuring predictive power tests something nobody claimed.

   The correct architecture is three separate layers, and this page had been conflating the
   first two:

   | Layer | Question | Rule |
   |---|---|---|
   | **Screen** | is this name worth watching today? | RVOL ≥ 100% |
   | **Setup** | when do I act on it? | 9/34 cross in the window |
   | **Exit** | how do I get out? | bell for longs, reverse cross for shorts |

   RVOL belongs in the same family as `[[feedback-watchlist-premarket-movement-gate]]` — an
   admission test applied *before* setups are considered, alongside R-viability. Do not tune
   it; a name either clears the floor or is not on the board.

**What this does NOT rule out.** This scan runs 09:45-15:30 and therefore **abandons the
15:00-15:40 window**, which is the one filter that showed promise (7 instances, +0.69R — though
2 of those were a single NFP day). A midday cross with no auction runway is a different setup
from a 15:16 cross, and pooling them may be washing out the effect.

**Caveat on the RVOL definition itself.** The operator reads RVOL from his platform; this
implementation is cumulative-vs-12-session-median. Other common definitions (vs 5-day average,
vs full-day average, bar-level rather than cumulative) will produce different bands. He is
adding an RVOL study to `chart1` so it can be read live via `GetStudyVal()` — **name the study
so `$STUDY_RVOL` can address it**, per `[[reference-das-getstudyval-label]]`.

**Bottom line for sizing:** nothing here supports LIVE capital yet. The bell/cross asymmetry
is worth acting on as a *rule about exits*. The entry remains unvalidated.

#### Status

**Zero live instances.** The operator was flat at 15:02:53 on the reference day — short into
the 15:00 lows — and the setup fired twelve minutes later. One retrospective example plus a
one-session test of the volume gate. Per `Reference/ReportingSchema.md` Rule 0 this must not
be used to grade a session until it has a real sample. **Log every trigger, taken or not**, so
the sample builds.

### HitchHiker Scalp — Opening-Drive Consolidation Continuation
*Source: SMB Capital cheat sheet (Google Drive, SMB folder). Long rules below; invert for shorts.*

**Premise:** an In Play stock drives off the open and then **refuses to pull back** — it holds up and goes sideways. That non-pullback is the signal: orders acting without price sensitivity are institutional programs that need to get filled, and those run for hours, not minutes. The scalp hitches a ride on the program.

- **Trigger:** break of the 1-minute bar range out of the consolidation (the *HitchHiker Candle*)
- **Entry:** aggressive — pay the offer as soon as the range breaks. **Do NOT wait for the bar to close**
- **Stop:** hard stop, one-and-done. **$0.02 below the consolidation low**
- **Target:** exit in **waves** — ½ into the first wave (when the initial rush slows), ½ into the second (the grinding wave that accelerates late)
- **Expectancy:** 55-60% win rate · **1.9 : 1** reward-to-risk

**Consolidation qualifiers — all must hold:**
- Minimum **5 min**, maximum **20 min**
- Consolidation low sits in the **upper 1/3 of the day's range** (inverted: lower 1/3 for shorts)
- Ideally forms **above a key level** — premarket high or prior-day high

**Odds increasers:** volume on the HitchHiker candle **≥30% above the prior candle** · SPY/QQQ/IWM trending the same way · sector trending with it.

**Odds decreasers:** over-extension on the initial move (one big candle instead of a drive) · multiple attempts at the range before the real break · **fighting the bigger-picture trend of the day**.

- **Ideal window:** opening-drive trade — see it setting up **before 09:59 ET**
- **Disqualifiers (never take it):** consolidation that is merely **choppy** — no defined range, large wicks both directions, erratic price with no real participation. A pullback after the drive voids the premise entirely; the whole edge is that it *didn't* pull back.

**Regime note:** the "don't fight the day's trend" factor pairs this with gamma regime — in negative-gamma/momentum-extends tape take the HitchHiker **in the trend's direction** (shorts in a down tape), not against it.

### Breakout (Key Level)
- **Trigger:** Stock approaching significant resistance/support with building volume
- **Entry:** On break of level with volume > 2x average
- **Stop:** Below breakout level + ATR buffer
- **Target:** Measured move or next resistance/support

### Risk-Off at Choppy Edges

- **When:** Stock has lost directional momentum and is range-bound — multiple failed breakout attempts, price oscillating between defined highs and lows, no clean trend on 1-min or 5-min
- **The tell:** You keep watching for a breakout that isn't coming. That feeling is the signal to switch lenses.
- **Entry:** At range boundary — long near the range low on a volume-supported bounce; short near the range high on a volume-supported rejection. Wait for the candle to confirm the edge held before entering.
- **Stop:** Just outside the range boundary (below range low for longs, above range high for shorts). Tight — if the range breaks, you're wrong.
- **Target:** Opposite edge of the range. Take it. Do not hold through.
- **Size:** Minimum size only. Choppy = reduced conviction = reduced size.
- **Exit rule:** If price stalls mid-range and doesn't reach the target within 2-3 candles, exit flat. Do not wait.
- **Disqualifiers:** Earnings within 5 days; spread > $0.10; stock still in trend on 5-min; pre-10:00 AM ET
- **Key distinction — Exhaustion vs. Risk-Off:**
  - *Exhaustion watching* is passive: you hold a thesis and wait for the move to die, looking for the perfect fade signal. It keeps you in a stock that isn't moving for you.
  - *Risk-Off at Choppy Edges* is active: you recognize the range structure, trade its boundaries with tight stops, and exit clean. No thesis. No waiting. Just the edge and the stop.
- **Case study — MU (the session behind its SIM-only ban in RulesOfEngagement):** Clear tradeable windows at 12:54–13:20 and 13:44–14:14 ET. Range was defined, edges were readable. The mistake was using the exhaustion lens (waiting for MU to show it was done selling) instead of the risk-off lens (trading the range boundary and getting out). 90+ round trips using the wrong lens; 2-3 clean trades available with the right one.

### Relief Gap (RG) — oversold name, soft catalyst, gap into a shelf

Added 2026-10-01 from the IBM example (down 10.7% in twelve sessions, +5.8% premarket on a product
release, gap landing on the September 24 high at 232.62). Status: **forward test; backtest on the
23-name Massive set pending (`backtest/backtest_relief_gap.py`, report in
`docs/forward-tests/relief-gap-2023-2026.md`).** Not Active until the test says go.

- **Context (the setup, not the news):** close-to-close decline of 8% or more over the prior ten
  sessions, prior close within 2% of the 20-session low, no earnings in the window (earnings gaps
  are Earnings Reaction, a different playbook). The catalyst is soft: product release, upgrade,
  partnership, index inclusion.
- **Trigger:** gap of 3% or more into a prior resistance shelf (the most recent swing high or
  consolidation floor above). That shelf is the line in the sand and the first objective at once.
- **The hold test is the edge:** the first 5-minute bar closes above the opening print with VWAP
  under price. Soft-catalyst gaps on oversold names fade more often than earnings gaps; the trade
  only exists if the open is defended.
- **Entry:** the first pullback that holds VWAP and the opening print, on a closed 5-minute bar. If
  the gap is already more than about 2–3 ATR without a pullback, do not take the opening entry;
  default to the Fashionably Late cross after 09:45 ET.
- **Stop:** under the opening-range low or the premarket low, whichever is nearer, floored at
  1.5 × the 5-minute ATR at entry.
- **T1:** the shelf if entered below it; otherwise the next daily resistance (IBM: 237.86).
  **T2:** half the ten-session decline retraced.
- **Disqualifiers:** earnings catalyst; index risk-off at the open ($ADD under −1000 and falling);
  gap already beyond 3 ATR with no pullback; spread wider than the usual 5-minute range.
- **No-trade:** never short the relief gap on Day 1. Lose the opening print and VWAP in the first
  15 minutes and the gap is being sold; stand aside.
- **Grade:** B+ by default (technical context with a soft catalyst); A only with premarket volume
  above 10% of the ten-day average before the open.
- **Lineage:** the "gapping off weekly support" and "hold green, above the opening print" reads in
  the SMB morning sheets (IBM 06-23, DDOG 08-06, ARM/LRCX 07-30, TTD 08-07); our generic Gap Up /
  Gap Down entry supplies the mechanics, this section supplies the context that makes it a
  different trade.

### Short Overextension Fade
- **Trigger:** Stock gapped or ran 10%+ with climactic volume, losing momentum
- **Entry:** Short below VWAP after first failed bounce (confirmed lower high)
- **Stop:** Above the high of the failed bounce
- **Target:** Prior day close or next support level
- **Note:** This was the KOD setup on 3/27 — probe small, size up on confirmation

## Camarilla Pivot Points
Used for daily Support/Resistance levels. Calculated from prior day OHLCV:
- R4 = Close + (High - Low) × 1.1/2
- R3 = Close + (High - Low) × 1.1/4
- R2 = Close + (High - Low) × 1.1/6
- R1 = Close + (High - Low) × 1.1/12
- S1 = Close - (High - Low) × 1.1/12
- S2 = Close - (High - Low) × 1.1/6
- S3 = Close - (High - Low) × 1.1/4
- S4 = Close - (High - Low) × 1.1/2

## Setup Grading
- **A+**: Clear catalyst + clean chart + high relative volume + thesis alignment
- **A**: Strong catalyst + clean setup + good volume
- **B+**: Moderate catalyst or technical-only with excellent chart
- **B**: Decent setup, some uncertainty
- **C**: Marginal — sim only
