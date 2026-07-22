# FeedbackCheck Workflow

Find the missing, delayed, or distorted feedback loops behind a stalled goal. Meadows: missing feedback is the single most common cause of system malfunction — and restoring it (leverage point 6) is usually the cheapest structural fix available.

## Voice Notification

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the FeedbackCheck workflow in the LifeSystems skill to check goal feedback"}' \
  > /dev/null 2>&1 &
```

Running the **FeedbackCheck** workflow in the **LifeSystems** skill to check goal feedback...

## Step 1: Load goals and their instrumentation

```
~/.claude/PAI/USER/TELOS/GOALS.md      # goals and any stated metrics
~/.claude/PAI/USER/TELOS/METRICS.md    # what is actually measured, and how often
~/.claude/PAI/USER/TELOS/STATE.md      # current recorded state
~/.claude/PAI/USER/TELOS/updates.md    # cadence of actual reviews (revealed, not stated)
```

## Step 2: Audit each goal's feedback loop against four failure modes

For each active goal (or the one named), answer:

1. **Missing** — Is there any recurring signal at all connecting daily action to this goal? A goal reviewed only when guilt strikes has no loop.
2. **Delayed** — Does the measured signal lag the action badly? (Weight lags training; revenue lags outreach; reputation lags contribution.) Delay-dominated loops produce oscillation: burst of effort → no visible result → quit → decay → alarm → burst. If the update history shows this sawtooth, say so.
3. **Distorted** — Is the signal a proxy that can drift from the purpose (streaks, hours logged, follower counts)? Proxy-only feedback feeds the rule-beating and wrong-goal traps.
4. **Unheeded** — Does the signal exist but arrive where no decision is made? (A dashboard nobody opens is not a loop.) Feedback must land at the decision point — the moment you choose the next hour.

## Step 3: Design the repaired loop

For each broken loop, specify the repair with all four properties:

- **Signal**: a flow-level measure under direct control (sessions/week, offers/month) — not only the lagging stock
- **Cadence**: matched to the system's tempo — usually weekly for life systems; never longer than the decision cycle it must inform
- **Destination**: where it will actually be seen at decision time (STATE.md, morning review, a standing note)
- **Stated delay**: how long before the *stock* should visibly respond — written down in advance so the delay window doesn't get read as failure

## Step 4: Report and persist

Output a table — goal | loop status (missing/delayed/distorted/unheeded/healthy) | repair — followed by **≤3 concrete moves**. Offer to write repaired metrics into METRICS.md and review cadence into GOALS.md **via the Telos Update workflow**.

## Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"FeedbackCheck","input":"8_WORD_SUMMARY","status":"ok","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
