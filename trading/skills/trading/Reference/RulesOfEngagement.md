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

| Mark | SPCX | Position (short from 111.31) |
|---|---:|---:|
| Fri 07-31 close | 108.37 | **+1.05R** ✅ |
| Mon 08-03 close | 114.53 | **−1.15R** ❌ |
| Tue 08-04 cover ~05:07 | ~115.80 | **≈ −1.6R** |

The position was **up more than 1R at Friday's close and was carried.** It breached the
per-symbol stop **on Monday — a session with zero trades placed.** It was already beyond 1R by the
third fill on Tuesday, and the grind that followed in that name produced **−8.6R on the day, −9.6R
overall** — the largest loss in the record.

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
5. **Symbol stop hit (−1R) = close ticker, lock it for the session.** Do not reopen. Discuss with a teammate before returning to any ticker after a symbol stop. *(1R is per account and read from the `PREFERENCES.md` R-CONFIG; LIVE and SIM are never blended.)*
5. **Thesis trade gets priority** — don't let screen movers steal attention and capital
6. **ATR-based stops on every single trade** — no exceptions
7. **No averaging down into losers** — if the first entry goes against you, honor the stop
8. **Adding is only for winners**
9. **Maximum 1-2 tickers on live per session**

## Position Sizing
- **Max risk per trade: 1R.** LIVE 1R is **0.1% of working capital**; SIM 1R is operator-set.
  Both are read from the `PREFERENCES.md` R-CONFIG — never hard-coded here, and never
  published in this public repo.
- **Symbol stop: once a ticker hits −1R cumulative in a session, close it and do not
  re-enter that day.** The loss is the stop. 160 executions after the stop is blown is not
  trading — it is a behavioral emergency.

> **Corrected 2026-08-05.** This section previously stated the per-symbol stop as **1% of the
> account** in three places, while `PREFERENCES.md` has said **0.1%** since 2026-07-24 and every
> published review was scored against the smaller figure. Under the stale number the 2026-08-04
> SPCX loss read as *inside* the per-symbol stop; it was in fact a **7.8R breach**. One decimal
> place, and it made the worst session in the record look compliant.
- Prove edge in sim first — minimum 5 profitable sessions before going live on a ticker
- Size into conviction on thesis trades

## Restricted Tickers (SIM ONLY Until Proven)

Tickers below are banned from the LIVE account based on 13-month DynamoDB data analysis. Each requires 5 consecutive profitable sim sessions before returning to live.

> **This is a public plugin, so no trade counts, win rates or P&L are published here.** The bans
> are enforced by the behaviour that earned them and the condition for lifting them, neither of
> which needs a dollar figure. The underlying numbers live in the private review store; where a
> reason once cited a dollar amount it is now stated in R, which is the unit the rules are
> written in anyway and does not go stale as the account changes.

### Banned — Negative Edge Despite High Volume

| Ticker | Why Banned | Reinstatement Criteria |
|--------|-----------|----------------------|
| **AMD** | Inverse sizing: wins small, loses massive — worst single loss many multiples of the per-trade cap. THE poster child for C5. | 5 consecutive sim sessions with avg winner > avg loser |
| **UGRO** | Revenge trading pattern (C4). Win rate well under half — no edge. | 5 sim sessions at 50%+ win rate with max 3 trades/session |
| **AMZN** | Share price is outside the account's sizing range; a 1.5-ATR stop cannot be expressed in whole shares at 1R. | Only if the price falls far enough to size properly |
| **CRCL** | Coin-flip win rate with losers roughly twice the winners. No positive expectancy. | 5 sim sessions with profit factor > 1.5 |
| **DELL** | Below 50% win rate, and the worst single loss ran to several R. | 5 sim sessions with win rate > 55% |
| **SOFI** | Wins about two-thirds of the time and still loses money — inverse R. | 5 sim sessions with avg winner > avg loser |
| **BA** | Coin flip with outsized losses. No edge. | 5 sim sessions with profit factor > 1.5 |
| **CRWV** | Below 50% win rate, worst single loss equal to the whole ticker's deficit. | 5 sim sessions at 55%+ win rate |

### Banned — Grind Pattern (SIM Only Until 5 Consecutive Profitable Sessions)

| Ticker | Why Banned | Reinstatement |
|--------|-----------|---------------|
| **MU** | 90+ round trips in a single session over 6½ hours, off-plan, symbol stop blown around the twentieth execution, exhaustion-lens grind on a choppy range | 5 sim sessions using Risk-Off at Choppy Edges setup with ≤10 executions/session |

### Banned — Single-Trade Catastrophes

| Ticker | Why Banned |
|--------|-----------|
| **VERI** | One trade gave back a month of gains |
| **GWH** | A single loss wiped out a winner and then some |
| **FROG** | Win rate in the teens — no business trading this |
| **MNDR** | One outsized loss against a quarter win rate |
| **STI** | Single catastrophic loss |
| **TGL** | Single catastrophic loss |

Each of these breached `PER_SYMBOL_MAX_R` in one trade. That is the common thread, and it is a
sizing failure rather than a selection one — the same loss at correct size would have been −1R.

### Approved — Proven Edge (Live OK)

| Ticker | Why Approved |
|--------|-------------|
| **SOXL** | Consistent edge, good R, high volume proven — the Base Hit anchor |
| **ONDS** | Strong win rate with positive expectancy |
| **INTC** | Earnings edge, good recent performance |
| **MSFT** | Highest win rate on the book, but position sizes are too small to matter — a sizing opportunity, not a problem |
| **IBIT** | Consistent with BTC momentum |
| **USO** | Most-traded name and roughly breakeven — **CAUTION: reduce size** |

### USO Special Note
USO is the most-traded ticker on the book by a wide margin. It is not banned: the win rate shows a
marginal edge and the P&L is near breakeven. But that volume against that result is the signature of
grinding, not of edge. **Cap at 5 round-trips per session on USO.** If it cannot be made to work in
five, the edge is not there that day.

## Post-Session
- Export DAS Trader data (Trades.csv, Orders.csv, P&L screenshots)
- Run daily review before end of day
- Extract and save lessons to TELOS
