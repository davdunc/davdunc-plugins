---
description: Run rules engine against a given trading day and report violations
---

# ComplianceCheck Workflow

**Triggers:** "compliance check", "rule check", "did I break any rules"

Runs the `falcon-stats compliance` rules engine against a single trading day. Loads executions + round-trips from canonical SQLite (`~/Projects/Falcon/trades.db`), evaluates against the rules at `~/.claude/PAI/USER/TRADING/Rules.yaml`, and prints any violations.

## Voice + Text Notification

**When executing this workflow, do BOTH:**

1. **Send voice notification:**
   ```bash
   curl -s -X POST http://localhost:8888/notify \
     -H "Content-Type: application/json" \
     -d '{"message": "Running the ComplianceCheck workflow in the Trading skill to check the day against your rules"}' \
     > /dev/null 2>&1 &
   ```

2. **Output text notification:**
   ```
   Running the **ComplianceCheck** workflow in the **Trading** skill to check the day against your rules...
   ```

## Steps

### 1. Run the Compliance CLI (PRIMARY ACTION)

```bash
falcon-stats compliance <YYYY-MM-DD>
```

Flags:
- `--db PATH` — override `$FALCON_DB` (default `~/Projects/Falcon/trades.db`)
- `--rules PATH` — override `$FALCON_RULES_YAML` (default `~/.claude/PAI/USER/TRADING/Rules.yaml`)
- `--json` — emit violations as a JSON list

Exit code: `0` if no violations, `1` if any.

If the requested date has no executions in SQLite yet, run the IngestTrades workflow first.

### 2. Parse Violations

Each violation has shape:

```
rule:     banned_ticker | per_symbol_loss_cap | daily_loss_cap |
          max_round_trips_per_day | swing_not_allowed | session_window
symbol:   ticker or null
detail:   human-readable explanation
severity: block | warn
```

### 3. Output Format

```
═══ COMPLIANCE CHECK — [Date] ═══

Account: <account>
Rules version: [from Rules.yaml]

VIOLATIONS: [count]   BLOCKS: [n]   WARNS: [n]

[symbol] [rule] [severity] — [detail]
...

VERDICT:
[One sentence: clean day | warnings to review | blocks — review with team]
```

If `--json` was used, present the JSON list verbatim and follow with the human summary above.

### 4. When to Use

- After IngestTrades, before publishing the DailyReview, to surface broken rules early.
- Ad-hoc audit on a prior date: `falcon-stats compliance 2026-05-27`.
- Weekly retrospective: run for each trading day Mon-Fri and aggregate.

### 5. Rules File Location

Authoritative rules: `~/.claude/PAI/USER/TRADING/Rules.yaml`. Schema includes `banned_tickers`, `per_symbol_loss_cap`, `daily_loss_cap`, `max_round_trips_per_day`, `swing_trade_allowed`, and `session_windows`. Edit there to change limits — do NOT inline-override in this workflow.
