# Rules of Engagement

## ⛔ THE VALIDITY GATE (operator-defined 2026-07-30)

**A trade is valid only when ALL of the following are true. Any single false = no trade.**

1. The stock is one of the **best available opportunities** — not merely one that is moving.
2. **Market context and price action match a defined setup** from the playbook.
3. The trade has a **one-sentence thesis** and a **clear trigger**.
4. **Allocation, stop, entry, and target are defined before execution.**
5. The entry is **planned, not chased**.
6. **Reward-to-risk meets the playbook minimum** and the trade has **positive expected value**.
7. **Confirmation, time of day, and risk limits permit** the trade.

This gate sits *above* every rule below it. The rules below describe how to trade well once a
trade is valid; this gate decides whether there is a trade at all.

**Operational form — if you cannot say all four out loud before clicking, there is no trade:**

> *"I am buying/shorting **{TICKER}** because **{one-sentence thesis}**.
> I enter at **{trigger}**, stop **{level}**, target **{level}**, size **{N}R**."*

**How it applies to the known failure modes:**

| Failure | Which condition catches it |
|---|---|
| 17 round-trips in a session (2026-07-29) | #1 — the 5th attempt is never a *best available* opportunity |
| ~15 fills on one name in 9 minutes | #5 — re-entering a name you just exited is chasing |
| Direction flipping within minutes | #3 — a thesis that reverses in 60 seconds was never a thesis |
| Holding 16m / 21m past the kill | #7 — time of day and the 15-minute kill are permission conditions |
| Trading after the kill time | #7 |
| Sympathy names on a headline | #2 and #6 — no defined setup, no measured R:R |
| Untradeable spread (CMI $19.33, VIVK 590K float) | #6 — a spread wider than the target destroys expectancy |

Linked: `[[base-hit-playbook]]`, `[[trigger-kill-time]]`, `[[activity-over-patience]]`.

## ⛔ NO OVERNIGHT HOLDS IN DAS (operator-defined 2026-08-05)

**Every DAS position is flat before the close. No exceptions, either direction, winner or
loser.** If it cannot be closed, it should not have been opened.

This is absolute and sits alongside the validity gate — it is not a preference and not
conditional on the position being profitable.

**Operational form:**
- Every entry must be closable inside the session. A position that cannot be flattened
  before the close was never a valid trade.
- **Being in profit is not a reason to carry.** It is the specific rationalisation that
  caused the failure below.
- Flat check before the close, every session. Any open position gets closed, not evaluated.

**Why this rule exists — 2026-07-31 → 2026-08-04, SPCX:**

| Mark | SPCX | Position (short 10 @ 111.31) |
|---|---:|---:|
| Fri 07-31 close | 108.37 | **+$29.40 = +1.05R** ✅ |
| Mon 08-03 close | 114.53 | **−$32.20 = −1.15R** ❌ |
| Tue 08-04 cover ~05:07 | ~115.80 | **≈ −$45 = −1.6R** |

The position was **up more than 1R at Friday's close and was carried.** It breached the
per-symbol stop **on Monday — a session with zero trades placed.** By the third fill of
Tuesday it was already −$31.45, and the remaining 44 fills / 397 shares in that name
produced **−8.6R on the day, −9.6R overall** — the largest loss in the record.

The per-symbol stop is a *session* rule and could not fire on a position held across
sessions. This rule closes that gap.

Full detail: `USER/TRADING/Reviews/REVIEW-2026-08-04.md`.

## Pre-Session
- Complete all 6 phases of the Morning Routine Checklist before market open
- Audit DAS Trader hotkeys before any session
- Identify the thesis trade — the ONE ticker that gets live capital

## During Session
1. **No trades in the first 5 minutes** unless pre-planned ORB with confirmed price action
2. **Playbook trades only** — if it's not in the game plan, it doesn't get traded
3. **One loss = pause 5 minutes** — review, don't revenge trade
4. **Three losses = done for the day** — protect capital, review in the afternoon
5. **Symbol stop hit (−1R) = close ticker, lock it for the session.** Do not reopen. Discuss with a teammate before returning to any ticker after a symbol stop. *(1R = LIVE $28 / SIM $75 per the `PREFERENCES.md` R-CONFIG — never the stale "$280".)*
5. **Thesis trade gets priority** — don't let screen movers steal attention and capital
6. **ATR-based stops on every single trade** — no exceptions
7. **No averaging down into losers** — if the first entry goes against you, honor the stop
8. **Adding is only for winners**
9. **Maximum 1-2 tickers on live per session**

## Position Sizing
- **Max risk per trade: 1R.** LIVE **$28** (0.1% of $28K working capital) / SIM **$75**.
  Sourced from the `PREFERENCES.md` R-CONFIG — never hard-coded here.
- **Symbol stop: once a ticker hits −1R cumulative in a session, close it and do not
  re-enter that day.** The loss is the stop. 160 executions after the stop is blown is not
  trading — it is a behavioral emergency.

> **Corrected 2026-08-05.** This section previously read **−$280** (1% of the account) in
> three places, while `PREFERENCES.md` has said **−$28** (0.1%) since 2026-07-24 and every
> published review was scored against $28. Under the stale figure, the 2026-08-04 SPCX loss
> of −$219 read as *inside* the per-symbol stop; it was in fact a **7.8R breach**. One
> decimal place, and it made the worst session in the record look compliant.
- Prove edge in sim first — minimum 5 profitable sessions before going live on a ticker
- Size into conviction on thesis trades

## Restricted Tickers (SIM ONLY Until Proven)

Tickers below are banned from the LIVE account based on 13-month DynamoDB data analysis. Each requires 5 consecutive profitable sim sessions before returning to live.

### Banned — Negative Edge Despite High Volume

| Ticker | Trades | Win% | Total P&L | Why Banned | Reinstatement Criteria |
|--------|--------|------|-----------|-----------|----------------------|
| **AMD** | 85 | 69% | -$782 | Inverse sizing: wins small, loses massive (-$573 worst). THE poster child for C5. | 5 consecutive sim sessions with avg winner > avg loser |
| **UGRO** | 73 | 38% | -$553 | Revenge trading pattern (C4). 38% win rate = no edge. | 5 sim sessions at 50%+ win rate with max 3 trades/session |
| **AMZN** | 17 | 53% | -$735 | Outside account range at $195. Avg loss -$43/trade. Can't size properly. | Only if price drops below $50 (unlikely) |
| **CRCL** | 38 | 50% | -$500 | 50% win rate but losers 2x winners. No positive expectancy. | 5 sim sessions with profit factor > 1.5 |
| **DELL** | 40 | 45% | -$287 | Below 50% win rate, worst single loss -$413. | 5 sim sessions with win rate > 55% |
| **SOFI** | 34 | 68% | -$247 | Wins 68% but still loses money — inverse R. | 5 sim sessions with avg winner > avg loser |
| **BA** | 22 | 50% | -$258 | Coin flip with outsized losses. No edge. | 5 sim sessions with profit factor > 1.5 |
| **CRWV** | 22 | 41% | -$261 | Below 50% win rate, worst single -$261. | 5 sim sessions at 55%+ win rate |

### Banned — Grind Pattern (SIM Only Until 5 Consecutive Profitable Sessions)

| Ticker | Session | Execs | P&L | Why Banned | Reinstatement |
|--------|---------|-------|-----|-----------|---------------|
| **MU** | 2026-05-27 | 181 live | -$324.94 | 90+ round trips over 6.5 hours, off-plan, $280 symbol stop blown at exec ~20, exhaustion-lens grind on a choppy range | 5 sim sessions using Risk-Off at Choppy Edges setup with ≤10 executions/session |

### Banned — Single-Trade Catastrophes

| Ticker | Trades | P&L | Why Banned |
|--------|--------|-----|-----------|
| **VERI** | 1 | -$562 | Single trade destroyed a month of gains |
| **GWH** | 2 | -$468 | One -$576 loss wiped a winner |
| **FROG** | 7 | -$563 | 14% win rate — no business trading this |
| **MNDR** | 4 | -$380 | One -$361 loss, 25% win rate |
| **STI** | 1 | -$320 | Single catastrophic loss |
| **TGL** | 1 | -$268 | Single catastrophic loss |

### Approved — Proven Edge (Live OK)

| Ticker | Trades | Win% | Total P&L | Why Approved |
|--------|--------|------|-----------|-------------|
| **SOXL** | 76 | 75% | +$360 | Consistent edge, good R, high volume proven |
| **ONDS** | 29 | 72% | +$308 | Strong win rate + positive expectancy |
| **INTC** | 21 | 62% | +$336 | Earnings edge, good recent performance |
| **MSFT** | 12 | 92% | +$22 | Highest win rate but small P&L — sizing opportunity |
| **IBIT** | 7 | 71% | +$156 | Consistent with BTC momentum |
| **USO** | 163 | 55% | -$124 | Most traded, near breakeven — CAUTION: reduce size |

### USO Special Note
USO is your most-traded ticker at 163 round-trips. It's not banned because you're near breakeven and 55% win rate shows marginal edge. BUT: the volume suggests grinding. **Cap at 5 round-trips per session on USO.** If you can't make it work in 5, the edge isn't there that day.

## Post-Session
- Export DAS Trader data (Trades.csv, Orders.csv, P&L screenshots)
- Run daily review before end of day
- Extract and save lessons to TELOS
