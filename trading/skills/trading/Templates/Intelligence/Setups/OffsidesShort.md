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

Reference (MRVL 2026-06-02 SIM):
```
09:00:20  SS 5 @ $255.00  REB25
09:00:54  SS 5 @ $256.00  REB25
09:01:51  SS 5 @ $258.00  REB25
                        ─────
Avg short cost: $256.33  (15 shares)
```

### Cover — On the Morning Flush
- Watch for VWAP rejection + first 1-min red bar with volume
- Cover ALL legs on the flush — don't leave runners; this is a defined-edge scalp, not a swing
- Use SMAT route for covers (BUY auto-closes shorts cleanly)
- Cover in 3 legs as price reverses

Reference (MRVL 2026-06-02 SIM):
```
09:30:18  B  5 @ $253.07  SMAT  → +$16.32
09:30:47  B  5 @ $254.74  SMAT  → +$7.97
09:31:03  B  5 @ $254.62  SMAT  → +$8.57
                                 ─────
Realized: +$32.86 net on 15 shares
~$2.19/share avg = ~+0.85% per share
```

### Optional 4th Buy — Starter Long on the Reclaim
If price bounces decisively off the post-flush low, a small starter long (5sh) for the bounce is OK — but treat as a separate trade with its own stop, not part of the offsides-short P&L.

## Risk Frame
- **Pre-defined invalidation**: if stock holds above the post-open high for more than 2 bars (5-min), the squeeze is winning — cover the leg(s) at small loss and abandon. Don't add against momentum.
- **Time stop**: if flush hasn't started by minute 5 post-open, the algo isn't tiring — exit flat.
- **Per-symbol stop lockout**: respect the $280/ticker hard stop. If 3 legs at 5 shares each = 15sh × ~$256 = $3840 notional, a $280 loss = ~7.3% adverse move = $18.67/share. Set DAS stop accordingly.

## Cross-Account Coordination (per 2026-06-02 reference)
This setup works on BOTH accounts when the plan pre-assigns scope:
- **SIM**: clean 3-leg execution per template above (+$32.85 net)
- **LIVE**: larger position (27sh both sides via 20 round-trip fills, +$11.86 net) — more iterative execution, less clean structure, but profitable
- **Combined**: +$44.71 on a single setup across both accounts
- **Key rule**: pre-assign which account gets which size in the morning gameplan. Don't decide mid-tape ("account separation" pattern).

## Anti-Patterns to Avoid
- Don't fire on a < +5σ gap — the template needs EXTREME, not just EXTENDED
- Don't fade earnings winners without a same-day catalyst confirmed in 8-K/news
- Don't hold past the morning flush — give back is real (see HPE 2026-06-02: opened $63 → traded $58.45 by 9:01 → bounced to $58.5 by 9:15)
- Don't average down if the squeeze keeps going — that's the MU/AMD grind pattern

## Reference Trades
| Date | Symbol | Account | Z-score | Legs | Realized | Notes |
|------|--------|---------|---------|------|----------|-------|
| 2026-06-02 | MRVL | SIM {{SIM_ACCOUNT}} | +5.34σ | 3-leg SS / 3-leg cover | +$32.85 | Template trade — cleanest reference |
| 2026-06-02 | MRVL | LIVE {{LIVE_ACCOUNT}} | +5.34σ | 20 round-trip fills | +$11.86 | Same thesis, larger size, more iterative |

## Linked Memories
- [[das-sell-opens-short-not-close]] — Route SMRTL vs REB25 matters
- [[check-account-column-first]] — DAS CSVs mix LIVE + SIM; tag by Account
- [[trading-skill-multi-account-spec]] — Cross-account setups need pre-assignment

## Status
**Validated single-day, 2-account.** Need 3+ more EXTREME z-score gap days to confirm the edge is real and not MRVL-specific. Until then, treat as a high-probability setup with documented template but unproven multi-instance edge.
