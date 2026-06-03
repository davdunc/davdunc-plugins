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
- **Disqualifiers:** EXTREME z-score (>3) on the long side; cross before 10:00 ET

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
- **Case study — MU 2026-05-27:** Clear tradeable windows at 11:54–12:20 and 12:44–13:14 CT. Range was defined, edges were readable. The mistake was using the exhaustion lens (waiting for MU to show it was done selling) instead of the risk-off lens (trading the range boundary and getting out). 181 executions using the wrong lens; 2-3 clean trades available with the right one.

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
