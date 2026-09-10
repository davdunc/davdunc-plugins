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

### Earnings Gap-Down Fade (post-earnings continuation short)
*Drafted 2026-09-10 from the ORCL/ADBE session. Structure and risk terms are taken from the
existing playbook and David's standing rules; the setup-specific thresholds are a FIRST DRAFT
and want correcting after a few live reps.*

- **Setup class:** WATCH-ONLY at the open per the watchlist grouping — earnings movers are
  **open-only, no premarket entries.** The premarket print on an earnings name is a quote, not
  a market; ORCL was −2.04% premarket and −3.42% inside the first half-hour.
- **Trigger:** stock gapped DOWN on an earnings release (previous close → open), and after the
  open puts in a **confirmed lower high below VWAP**. The gap is the context; the failed bounce
  is the trigger. Never the gap itself.
- **Entry:** short the failed bounce — first lower high that rejects VWAP or the opening-range
  high, on a 5-min close. **Not before 10:00 ET** and not before the first analyst note has
  landed; earnings-reaction direction frequently inverts on the first sell-side revision, which
  is why the Kill-time rule already carves out earnings trades.
- **Stop:** above the high of the failed bounce. If that is wider than 1.5×ATR, the name is
  telling you the bounce was not a lower high — skip it rather than widening.
- **Target:** T1 the opening-range low or the gap-day low; T2 the next daily support / S3
  Camarilla. Park targets **short of round numbers** per the standing back-off rule.
- **Kill:** open + 60 min (continuation setups need trend confirmation, not a first-bar entry).

**Why the edge exists.** An earnings gap is a *re-rating*, not a pop. Institutions reposition
over days, so the drift persists — the same mechanism that makes the R/S + ATM fade work
(persistent mechanical seller), sourced from repositioning rather than dilution.

**Sizing gate comes first, as always.** Mega-caps gap small in percent and large in dollars.
ORCL at 156 sizes to low single-digit shares at our 1R; ADBE at 248 is worse. **Run the 1R check before
the chart** — most large-cap earnings movers resolve to context-only, and that is a finding,
not a disappointment.

**Disqualifiers:**
- Gap-down name that is *already* at a multi-day low with no bounce to short — you are chasing,
  not fading. The setup needs a bounce to fail.
- No lower high by 10:30 ET → the sellers were done at the open. Stand down.
- Spread > $0.10, or premarket volume that is not credible.
- **Never apply this to a gap-UP earnings runner.** That is the Day-1 anti-rule; a squeeze on a
  re-rating can extend well past rationality. Different setup, opposite side.

**Scanner note — the reason this was missed on 2026-09-10.** The premarket mover scan gates on
**≥3% move**; ORCL was −2.04% and was excluded. A percentage gate with no dollar-volume or
market-cap term systematically hides mega-cap earnings reactions, which are the highest-quality
instances of this setup. **The earnings calendar must be its own workflow step** — it cannot be
reached from a percentage scan.

**Case study — ORCL 2026-09-10.** Reported after the 09-09 close. Premarket −2.04% at 158.33 on
781k shares; by 09:08 ET it was **−3.42% at 156.10 on 21.1M shares.** ADBE ran the same shape
(−1.20% premarket → −2.66%). Trade Brigade had called software *"drift lower and pain"* with a
possible head-and-shoulders on IGV the night before — sector read and single-name catalyst
pointing the same way. **The name never reached the plan**: the evening review had flagged
"Thu PPI + ECB + ORCL/ADBE earnings" and only the macro half of that line was used.

### Round-Number Tap-and-React (the "80/20" level reaction)
*Added 2026-09-10 from Chart Fanatics, "The Strategy That Made MILLIONS Explained In 60 Seconds"
(`Si5u3W1YlWI`). Source is a 60-second Nasdaq-futures short; the mechanism transfers to equities,
the instrument and targets do not. See the adaptation note below.*

- **The level:** psychological round numbers. On the source's Nasdaq framing these are the **x80
  and x20** of each thousand (25,680 / 25,620) — "there's levels in between but the big ones are
  going to be 80 and 20." On equities the equivalent is the whole and half dollar on mid-priced
  names, and the 5-point strikes on SPY/QQQ where option gamma already concentrates.
- **Trigger — the tap, not the approach.** Price must actually *touch* the level and then show
  an **immediate reaction** off it. Approaching a level is not a trade. A tap with no reaction is
  not a trade. The reaction is the level proving it is being defended.
- **Entry:** after the reaction confirms, not at the level. The source taps 680 and enters **695**
  — paying 15 points for the confirmation. **That premium is the edge, not a cost.** Entering at
  the level is hoping; entering after the reaction is knowing. Same logic as
  [[wait-for-crowd-confirmation]].
- **Stop:** the level itself. Once momentum slows, stop to **break-even at the level** — if it is
  reclaimed against you, the reason for the trade is gone.
- **Target: deliberately small.** "I don't look for 100, 200, 300 points. I'm just looking to get
  15 to 30 points." Scale in two pieces (source: one contract at 695, another at 703). Let a
  runner go to break-even rather than round-tripping the whole position.
- **Kill:** open + 30 min. This is an opening-hour order-flow setup; the clustered inventory that
  makes it work is gone by mid-morning.

**Why the edge exists.** Resting orders and stops cluster at round numbers. The "instant reaction"
is that inventory being hit. It is not a chart pattern — it is a queue.

**How this fits the round-number back-off rule (they are NOT in conflict).**
The standing rule parks **targets** short of round numbers — 439.81, not 440 — because the round
number is confusion-space chop. This setup uses the round number as an **entry/reaction level**.
Both are the same observation from opposite sides: *round numbers are where the fighting happens.*
Trade the reaction at them; do not try to sell into them.

**ADAPTATION NOTE — do not lift the numbers.** The source trades NQ, where a point is $20 and a
15–30 point target is $300–600 per contract. That is orders of magnitude above our 1R. What
transfers is the **sequence**: level → tap → reaction → entry above the level → break-even stop at
the level → small scaled targets. Size it with the normal 1R gate; the setup does not earn an
exception.

**Disqualifiers:**
- No tap. Price stalled near the level and turned — that is a different (weaker) setup.
- Tap with no visible reaction, or a reaction that dies inside one bar. The level failed.
- Names that cannot be sized at 1R. A round number on a $500 stock is not reachable for us.
- Pre-open. The source explicitly anchors to the New York open; premarket round-number prints on
  thin volume are not the queue this setup trades.
- Wide spread. If the spread is a meaningful fraction of the expected 15–30 point equivalent, the
  edge is gone before entry.

**Related on 2026-09-10:** SPY's GEX map put a −$3.4B put pocket at **760** with **765** flipping
positive — round numbers carrying real dealer inventory, visible in the options data rather than
inferred from the chart. When GEX and a round number agree on the same price, that is the highest-
quality version of this level.

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
