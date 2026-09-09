# Offsides Short — Scaled Fade on EXTREME Z-Score Gap

## When to Deploy
Pre-market identifies a stock with z-score ≥ +5σ on the open (vs 20-day mean) AND a same-session 8-K / earnings catalyst that's driving the gap. The setup is the offsides fade — the gap is technically/algorithmically overextended and the morning flush is statistically likely.

Filters:
- Z-score ≥ +5σ (EXTREME per the morning gameplan covariance classification)
- Real same-day catalyst (8-K, earnings beat) — not just sympathy
- PM volume ≥ 1M shares (need liquidity for scaled entries)
- Account-size fit: $50-$400 sweet spot (A-grade); >$400 requires conviction sizing

## Execution Template (per MRVL 2026-06-02 reference trade)

### Entry — 3-Leg Scaled Short Sale Into the Gap-Up
- Scale SS in 3 legs as the stock pushes higher in the first ~90 seconds post-open
- Use REB25 / REB25L route (NOT SMRTL — SMRTL on a sell-to-close would mis-route, see [[das-sell-opens-short-not-close]])
- Each leg: 5 shares (or your standard offsides-short size)
- Spaced ~30-60 seconds apart to ride the algo squeeze without front-running it

Reference shape (three shorts scaled up into the squeeze):
```
09:00:20  SS leg 1  REB25
09:00:54  SS leg 2  REB25   ~0.4% higher
09:01:51  SS leg 3  REB25   ~0.8% higher than leg 1
                    ─────
Average cost lands between legs 2 and 3
```
Legs are equal-sized and spaced by time, not by a price grid — the point is to be filled
progressively better as the algo pushes, not to pyramid.

### Cover — On the Morning Flush
- Watch for VWAP rejection + first 1-min red bar with volume
- Cover ALL legs on the flush — don't leave runners; this is a defined-edge scalp, not a swing
- Use SMAT route for covers (BUY auto-closes shorts cleanly)
- Cover in 3 legs as price reverses

Reference shape (three covers inside the first ninety seconds):
```
09:30:18  B  leg 1  SMAT
09:30:47  B  leg 2  SMAT
09:31:03  B  leg 3  SMAT
                    ─────
~0.85% per share average across the three legs
```
The percentage is the number that transfers. Absolute P&L depends on the size the account
can carry, and a size that fits one book is wrong for another.

### Optional 4th Buy — Starter Long on the Reclaim
If price bounces decisively off the post-flush low, a small starter long (5sh) for the bounce is OK — but treat as a separate trade with its own stop, not part of the offsides-short P&L.

## Risk Frame
- **Pre-defined invalidation**: if stock holds above the post-open high for more than 2 bars (5-min), the squeeze is winning — cover the leg(s) at small loss and abandon. Don't add against momentum.
- **Time stop**: if flush hasn't started by minute 5 post-open, the algo isn't tiring — exit flat.
- **Per-symbol stop lockout**: respect the 1R per-ticker hard stop from the R-CONFIG. Size the legs from `max_shares = 1R / (1.5 × ATR)` and set the DAS stop at that distance — never from notional, which is the cost of the position and says nothing about its risk.

## Cross-Account Coordination
This setup works on BOTH accounts when the plan pre-assigns scope:
- **SIM**: clean three-leg execution per the template above
- **LIVE**: the same setup taken larger tends to fragment into many more round-trips — more iterative, less clean structure, and the round-trip count is where the edge leaks
- **Key rule**: pre-assign which account gets which size in the morning gameplan. Don't decide mid-tape ("account separation" pattern).

## Anti-Patterns to Avoid
- Don't fire on a < +5σ gap — the template needs EXTREME, not just EXTENDED
- Don't fade earnings winners without a same-day catalyst confirmed in 8-K/news
- Don't hold past the morning flush — give back is real (see HPE 2026-06-02: opened $63 → traded $58.45 by 9:01 → bounced to $58.5 by 9:15)
- Don't average down if the squeeze keeps going — that's the MU/AMD grind pattern

## Reference Trades
| Symbol | Z-score | Legs | Outcome | Notes |
|--------|---------|------|---------|-------|
| MRVL | +5.34σ | 3-leg SS / 3-leg cover | green | Template trade — the cleanest reference for this setup |
| MRVL | +5.34σ | 20 round-trip fills | green, but far less per fill | Same thesis and same session taken larger; the structure fragmented and most of the edge went with it |

The pair is the lesson: identical thesis, identical tape, and the disciplined three-leg version
kept what the twenty-fill version gave away. Round-trip count is the leak.

## Linked Memories
- [[das-sell-opens-short-not-close]] — Route SMRTL vs REB25 matters
- [[check-account-column-first]] — DAS CSVs mix LIVE + SIM; tag by Account
- [[trading-skill-multi-account-spec]] — Cross-account setups need pre-assignment

## Status
**Validated single-day, 2-account.** Need 3+ more EXTREME z-score gap days to confirm the edge is real and not MRVL-specific. Until then, treat as a high-probability setup with documented template but unproven multi-instance edge.
