# Reporting Schema — The One Contract

**Status:** canonical for every artifact produced by the Trading skill.
**Supersedes:** the copy at `davdunc-plugins/trading/skills/trading/Reference/ReportingSchema.md`,
which lives in a plugin that is **not enabled** and therefore never loads.

Derived 2026-08-05 from that document plus the consistency audit at
`USER/TRADING/Reviews/2026-08-05-consistency-audit.md`, which measured **15 mutually
incompatible comparison-table variants** across shipped reviews.

## Rule 0 — enforceability

**Every rule below carries an enforcement point. A rule with no enforcer is marked
`ASPIRATIONAL` and MUST NOT be used to score a review.**

This exists because the prior contract deferred to `tradekit.reporting` / `tradekit cards`
as its tiebreaker, and that code was never written. A contract whose arbiter does not exist
cannot resolve disagreement, so every workflow silently became its own authority. Do not
repeat that: if it is not executable, say so in the line itself.

| Enforcer | Status |
|---|---|
| `falcon-stats ingest` / `trades` | ✅ exists |
| `das_flat_check.py` | ✅ exists, on a timer |
| `tradekit cards *` | ❌ **does not exist** — anything depending on it is ASPIRATIONAL |
| `tradekit blotter` | ⚠️ code exists, **not wired to CLI** |

## Rule 1 — one source of truth per fact

| Fact | Authority | Never |
|---|---|---|
| Whether/when a trade happened | `falcon-trades` DynamoDB | Reviews folder, export folders |
| Fill price, size, **time** | Cobra `Account _ Trade Execution` → `ExecutionTime` | `TradeDate`, `Activity` export |
| Realized P&L, round-trips | `falcon-stats ingest` — carried verbatim | recomputed by hand |
| Live price | DAS CMD API | TradingView outside RTH |
| Historical bars | Massive/Polygon flat files | DAS |
| 1R and risk limits | `PREFERENCES.md` R-CONFIG **verified against trader-desk S3** | `SKILL.md`, `RulesOfEngagement.md` |
| Float / share data | Finviz | — |

**Deterministic vs judgment:** if a number came off the broker, falcon produces it and the
review carries it through **unchanged**. If it requires judgment over unstructured input
(grade, discipline, pattern), the review produces it against the rubrics below.

## Rule 2 — the trade date is `ExecutionTime`

Cobra stamps `TradeDate` **one session earlier** than the actual trading day. Verified twice
independently on 2026-08-05 (07-31 and 08-04 exports).

Validation, mandatory before any review is written: **every fill price must fall inside that
day's high/low.** A fill outside the range means the date is wrong, not the tape.

## Rule 3 — R-units

Format: `+2.3R ($644)` — R first, dollars in parentheses.
`1R = abs(entry − stop) × shares`.

**When `planned_stop` is absent, render `R n/a`. Never fabricate.** On 2026-07-30, 14 of 16
round-trips had no stop order; an earlier build manufactured an R for all of them and
reported −0.5R on a +$274 day.

**1R = LIVE $28 / SIM $75**, sourced from the `PREFERENCES.md` R-CONFIG. That block is the
only authority; no other file may hard-code a dollar figure.

> **Resolved 2026-08-05 (operator decision).** `SKILL.md` and `RulesOfEngagement.md` had
> carried **$280** (1% of $28K) against PREFERENCES' **$28** (0.1%) — a 10× split from a
> single decimal place. $28 is correct and matches every review scored to date. All three
> files plus `MorningGamePlan.md`'s worked example were corrected. Verify against the
> trader-desk S3 copy when next reachable; this machine is documented to drift.

## Rule 4 — one grade ladder

`A · B · C · D · F`, identical for setup quality and executed-trade quality.

| Grade | Score | Meaning |
|---|---|---|
| A | ≥ 80 | Clean, by the book |
| B | ≥ 65 | Right idea, minor issues |
| C | ≥ 50 | Acceptable but flawed |
| D | ≥ 35 | Wrong thesis or real discipline slip |
| F | < 35 | Revenge trade / averaging down / no plan |

## Rule 5 — one discipline rubric, summing to 10

Scored per criterion, never eyeballed. **The review must show the checklist, not just the
total.** (Both 07-30 and 08-04 reported a total with no per-criterion breakdown.)

| # | Criterion | Pts |
|---|---|:--:|
| 1 | Followed the published game plan, not screen impulses | 2 |
| 2 | Only playbook setups | 1 |
| 3 | Honored stops; no averaging down | 2 |
| 4 | No revenge trading | 1 |
| 5 | Paused / reset after losses | 1 |
| 6 | Took the thesis trade with conviction sizing | 1 |
| 7 | Conviction sizing, not scattered small lots | 1 |
| 8 | Account separation — LIVE served the plan | 1 |
| | **Total** | **10** |

## Rule 6 — canonical comparison columns

Every multi-day table — DailyReview "Compare to prior days", "Multi-Day Trend", WeeklyReview
"Daily Breakdown" — uses **exactly these columns in this order**:

```
| Date | LIVE P&L | LIVE RTs | SIM P&L | Discipline | Avg Grade | Key Pattern |
```

- `LIVE RTs` = **round-trips**, never raw fill count. `LIVE Execs` is banned.
- `Discipline` = `N/10` from Rule 5.
- `Avg Grade` = mean of executed-trade grades on the Rule 4 ladder.

**`Workflows/DailyReview.md:310` currently templates `LIVE Execs` and must be corrected** —
it contradicts both this rule and its own Step 0.

## Rule 7 — file naming

```
Reviews/YYYY-MM-DD-gameplan.md          game plan
Reviews/YYYY-MM-DD-review.md            daily report card
Reviews/YYYY-MM-DD-blotter.html         round-trip blotter
Reviews/YYYY-MM-DD-evening-notes.md     evening video review
Reviews/YYYY-MM-DD-<topic>.md           anything else
```

Lowercase, ISO date first, one convention. The `REVIEW-YYYY-MM-DD.md` form is **deprecated**;
existing files stay, new ones use the above.

## Rule 8 — channel routing by privacy class

| Class | Contains | Goes to | Never |
|---|---|---|---|
| **PUBLIC** | levels, tickers, thesis | Slack `#general`, Notion | any P&L, account id, R total |
| **PRIVATE** | P&L, R, discipline, account ids | Google Drive, Discord report-card forum | Slack, Notion |
| **LOCAL** | full detail | `USER/TRADING/Reviews/` | — |

Every artifact carries a footer declaring its class. Public versions strip methodology
pedagogy entirely. Discord report-card is a **forum** — new posts need `thread_name`.

## Rule 9 — no-trade days are still recorded

A session with no trades produces a game plan stating the posture and **is not published to
public channels**. Absence of trades is data; absence of a record is a gap.

## Remediation checklist

1. [ ] Reconcile 1R against trader-desk S3; propagate to all three files — **blocks everything**
2. [ ] Choose one canonical Trading skill copy; make the other a pointer
3. [x] Install this schema into the runtime copy
4. [ ] Cite it from local MorningGamePlan / DailyReview / WeeklyReview
5. [ ] Fix `DailyReview.md:310` → `LIVE RTs`, add `Avg Grade`
6. [ ] Fix `SKILL.md` Core Paths (wrong Windows user and folder) and the "1%" figure
7. [ ] Wire `blotter` into the tradekit CLI
8. [ ] Build `tradekit cards`, or mark that section ASPIRATIONAL in both copies
9. [ ] Move private specifics into `SKILLCUSTOMIZATIONS/Trading/EXTEND.yaml` so there is no
       remaining reason to fork the skill
10. [ ] Add a CI check to `davdunc-plugins` asserting the canonical header string
