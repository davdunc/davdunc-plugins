# Rules of Engagement

## Pre-Session
- Complete all 6 phases of the Morning Routine Checklist before market open
- Audit DAS Trader hotkeys before any session
- Identify the thesis trade — the ONE ticker that gets live capital

## During Session
1. **No trades in the first 5 minutes** unless pre-planned ORB with confirmed price action
2. **Playbook trades only** — if it's not in the game plan, it doesn't get traded
3. **One loss = pause 5 minutes** — review, don't revenge trade
4. **Three losses = done for the day** — protect capital, review in the afternoon
5. **Symbol stop hit (-$280) = close ticker, lock it for the session.** Do not reopen. Discuss with a teammate before returning to any ticker after a symbol stop.
5. **Thesis trade gets priority** — don't let screen movers steal attention and capital
6. **ATR-based stops on every single trade** — no exceptions
7. **No averaging down into losers** — if the first entry goes against you, honor the stop
8. **Adding is only for winners**
9. **Maximum 1-2 tickers on live per session**

## Position Sizing
- Max risk per trade: 1% of account (~$280)
- **Symbol stop: once a ticker hits -$280 loss in a session, close it and do not re-enter that day.** The loss is the stop. 160 executions after the stop is blown is not trading — it is a behavioral emergency.
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
