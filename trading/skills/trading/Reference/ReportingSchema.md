# Reporting Schema — The One Contract

This is the **single source of truth** for how trading results are measured,
graded, and compared. Every workflow that produces a report (MorningGamePlan,
DailyReview, WeeklyReview) renders these and only these — so day-over-day
results line up and support data-driven decisions instead of drifting.

It is backed by code in `tradekit` (`tradekit.reporting`), which owns the math
and persistence. When a workflow and this doc disagree, **the code wins** —
update both to match.

## Role boundary: tradekit ↔ falcon

- **falcon** = *deterministic* evaluation. `falcon-stats ingest` is the
  authoritative P&L / win-rate / equity-curve source. Those numbers are never
  recomputed here — they are embedded verbatim (the P&L Summary row).
- **tradekit** = *unstructured → structured*. It takes news, filings, analyst
  commentary, chart screenshots, and the narrative of the day and produces the
  **graded, ordered, comparable** records in this schema (setup grades,
  discipline score, patterns, lessons). Those structured documents are the
  hand-off back to falcon for downstream deterministic use.

Practical rule: if a number is deterministic (came off the broker/exports),
falcon produces it and tradekit carries it through unchanged; if a result
requires judgment over unstructured inputs, tradekit produces it as a structured
field on the ladder/rubric below.

## Grade ladder (one ladder, five rungs)

`A · B · C · D · F` — used identically for *setup quality* (the screener's 0–100
composite) and *executed-trade quality*. A "C" means the same thing on both
sides.

| Grade | 0–100 score | Meaning |
|-------|-------------|---------|
| A | ≥ 80 | Clean, by-the-book (setup or execution) |
| B | ≥ 65 | Right idea, minor issues |
| C | ≥ 50 | Acceptable but flawed (churn, early exits, weak setup) |
| D | ≥ 35 | Wrong thesis or a real discipline slip |
| F | < 35 | Revenge trade / averaging down / no plan |

> Prior drift this fixes: the screener used A/B/C/F (no D) while reviews used
> A/B/C/D/F. Same letter, different meaning. Now unified.

## R-units (the risk lingua franca)

All stops, targets, daily limits, and recap numbers are **R-units**, dollar in
parens: `+2.3R ($644)`. 1R = `abs(entry − stop) × shares`. When a trade has no
recorded `planned_stop`, R is **unreliable** — render `R n/a`, never fabricate.
Dollars derive from the R-CONFIG (`r_dollars`, `daily_max_r`, `per_trade_max_r`).

## Discipline rubric (one rubric, sums to 10)

Reproducible from a per-criterion checklist — not eyeballed.

| Criterion | Points |
|-----------|:------:|
| Followed the published game plan (not screen impulses) | 2 |
| Only playbook setups (Offsides / Fashionably Late) | 1 |
| Honored stops; no averaging down | 2 |
| No revenge trading | 1 |
| Paused / reset after losses | 1 |
| Took the thesis trade live with conviction sizing | 1 |
| Conviction sizing, not scattered small lots | 1 |
| Account separation — LIVE served the plan, not a parallel impulse book | 1 |

> Prior drift this fixes: the rubric listed 7 criteria; "account separation" was
> scored in practice but missing from the list. It is now a first-class
> criterion and the weights sum to exactly 10.

## Canonical multi-day comparison columns

Every comparison table — DailyReview "Compare to prior days", DailyReview
"Multi-Day Trend", WeeklyReview "Daily Breakdown" — uses **these columns, in
this order**. No variants.

```
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
```

- **LIVE RTs** = round-trips (from `falcon-stats ingest`), never raw fill count.
- **Discipline** = `N/10` from the rubric above.
- **Avg Grade** = mean of the day's executed-trade grades on the one ladder.

## Persistence (NoSQL-native, object-storage-archivable)

Each report is one self-contained JSON document:

- **Game plan** → `record_type=GAMEPLAN`, `pk=GAMEPLAN#GLOBAL`, `sk=<date>`
- **Daily card** → `record_type=DAILYCARD`, `pk=DAILYCARD#GLOBAL`, `sk=<date>`
  (one document per day, covering **both** accounts)

The same item maps onto DynamoDB (`pk`/`sk`, like `falcon-stats`) and archives
verbatim to object storage at `record_type/scope/date.json`. Comparison reads
*records*, not prose.

## CLI

```bash
tradekit cards trend  --since 2026-06-01            # canonical multi-day table
tradekit cards weekly --since 2026-06-08            # weekly rollup
tradekit cards show   2026-06-11                    # one daily card
tradekit cards export --record-type DAILYCARD       # JSONL bulk/archive
```
