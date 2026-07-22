# LeverageAudit Workflow

Audit one goal's strategies against Meadows' 12 leverage points, expose how much effort is going into low-leverage interventions, and propose at least one materially higher-leverage move.

## Voice Notification

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the LeverageAudit workflow in the LifeSystems skill to audit goal leverage"}' \
  > /dev/null 2>&1 &
```

Running the **LeverageAudit** workflow in the **LifeSystems** skill to audit goal leverage...

## Step 1: Load the goal and its strategies

```
~/.claude/PAI/USER/TELOS/GOALS.md        # the goal, its metric, its deadline
~/.claude/PAI/USER/TELOS/STRATEGIES.md   # current strategies serving it
~/.claude/PAI/USER/TELOS/PROJECTS.md     # projects claiming to serve it
~/.claude/PAI/USER/TELOS/BELIEFS.md      # the paradigm layer underneath it
```

If the user named the goal, extract exactly it. If not, list active goals and ask which to audit.

## Step 2: Classify every current strategy by leverage point

Use Meadows' 12 points — full canonical detail with worked examples is in the SystemsThinking skill's `LeveragePoints.md`; the life-domain mapping is in `References/TelosMapping.md`. Compressed ladder, weakest → strongest:

| # | Leverage point | Life translation |
|---|----------------|------------------|
| 12 | Parameters | Tweak amounts: wake time, budget lines, session length, prices |
| 11 | Buffers | Slack: emergency fund, free evenings, energy reserves |
| 10 | Stock-and-flow structure | Physical arrangement: where you live/work, what's in the kitchen, defaults |
| 9 | Delays | Shorten feedback lag: weekly not annual reviews, faster invoicing |
| 8 | Balancing loops | Strengthen self-correction: hard stops, spending alerts, rest rules |
| 7 | Reinforcing loops | Slow a vicious spiral / feed a virtuous one: compounding skills, audiences, savings |
| 6 | Information flows | Change what you see daily: dashboards, tracking, making costs visible |
| 5 | Rules | Change your own rules: what a workday is, what gets a yes, incentives |
| 4 | Self-organization | Build capacity to restructure: learning to learn, meta-skills, communities |
| 3 | Goals | Change the goal itself: what the system is actually for |
| 2 | Paradigms | Change the belief the system arises from (BELIEFS.md territory) |
| 1 | Transcending paradigms | Hold paradigms lightly; identity not welded to any of them |

Produce a table: strategy → leverage point # → why classified there.

## Step 3: Diagnose the distribution

Typical finding (call it out when true): **most effort clusters at points 12–9** — schedule tweaks and parameter pushes — because they're easy and visible, while the goal stays stuck for reasons living at 6, 5, 3, or 2. State where this goal's distribution sits and what that predicts.

## Step 4: Propose the higher-leverage move

Propose **1–3 moves, at least one ≥3 rungs above the current center of gravity.** For each: the leverage point number, the concrete action, the expected delay before the stock responds, and the risk. If the audit surfaces a paradigm question (it often does at point 2 — "what do you believe about money/success/obligation here?"), pose it explicitly rather than burying it in advice.

**Honesty rule:** higher leverage = harder to push and slower to show. Never present a paradigm move as a quick win.

## Step 5: Persist

Offer to update STRATEGIES.md (revised strategy set) and, where a belief was surfaced, BELIEFS.md — both **via the Telos Update workflow only**.

## Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"LeverageAudit","input":"8_WORD_SUMMARY","status":"ok","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
