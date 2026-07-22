---
name: LifeSystems
description: "Apply Donella Meadows' Thinking in Systems to the personal TELOS Life OS — treat your life as a system of stocks, flows, and feedback loops, then intervene where leverage is highest. Five workflows: LifeMap (model a life domain as stocks/flows with reinforcing and balancing loops), TrapScan (scan CHALLENGES/PROBLEMS for Meadows' eight system traps and apply the documented way out), LeverageAudit (classify a goal's strategies against Meadows' 12 leverage points and propose higher-leverage moves — beliefs are paradigm-level, schedules are parameters), FeedbackCheck (find missing, delayed, or distorted feedback loops behind stalled goals), Dance (periodic whole-life review using the Dancing with Systems practices — resilience over optimization, expanded time horizons, humility). USE WHEN life system, life leverage, stuck goal, recurring life problem, why do I keep, habit loop, burnout pattern, overcommitted, goal audit, life review, self-sabotage, life balance, dancing with systems, apply systems thinking to my life, TELOS analysis. NOT FOR general or technical systems analysis (use SystemsThinking), TELOS data entry, reports, or dashboards (use Telos)."
effort: high
---

## Customization

**Before executing, check for user customizations at:**
`~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/LifeSystems/`

If this directory exists, load and apply any `PREFERENCES.md`, configurations, or resources found there. These override default behavior. If the directory does not exist, proceed with skill defaults.

## MANDATORY: Voice Notification (REQUIRED BEFORE ANY ACTION)

**You MUST send this notification BEFORE doing anything else when this skill is invoked.**

1. **Send voice notification:**
   ```bash
   curl -s -X POST http://localhost:31337/notify \
     -H "Content-Type: application/json" \
     -d '{"message": "Running the WORKFLOWNAME workflow in the LifeSystems skill to ACTION"}' \
     > /dev/null 2>&1 &
   ```

2. **Output text notification:**
   ```
   Running the **WorkflowName** workflow in the **LifeSystems** skill to ACTION...
   ```

---

# LifeSystems Skill

Your life is a system: a set of stocks (energy, health, savings, skills, relationships, reputation, attention) connected by flows (habits, routines, commitments) and governed by feedback loops you mostly didn't design. This skill applies Donella Meadows' *Thinking in Systems* to the TELOS Life OS at `~/.claude/PAI/USER/TELOS/` — so that when the same life problem keeps coming back, you fix the structure that generates it instead of re-fighting the event.

The core Meadows move, applied to a life: **stop asking "what should I do?" and ask "what structure keeps producing what I'm already doing?"** Willpower is an event-layer fix. Structure is where behavior comes from.

## Life-as-System Axioms

1. **Stocks change slowly.** Fitness, savings, trust, expertise — all bathtubs. No intervention on a flow shows up in the stock quickly. Most people quit good interventions inside the delay.
2. **A system's purpose is deduced from behavior, not stated goals.** If the calendar says the system's purpose is "answer other people's requests," that is its purpose — whatever MISSION.md says. The gap between stated and revealed purpose is the first diagnostic.
3. **Missing feedback is the most common malfunction.** Goals stall when no signal connects daily action to the goal's stock. Adding a feedback loop is cheap and high-leverage.
4. **The traps are structural, not moral.** Doomscrolling, eroding standards, overcommitment — each matches a documented Meadows trap with a documented way out. Naming the trap removes the shame and reveals the fix.
5. **Beliefs are the paradigm layer.** In Meadows' leverage ordering, the paradigm a system arises from is the second-highest intervention point. `BELIEFS.md` is not a journal — it is the highest-leverage file in the Life OS.
6. **Resilience beats optimization.** A maximally efficient life — no slack, no buffers, every hour allocated — is a brittle system. Meadows: the ability to survive perturbation is worth more than peak performance. Systems self-repair only *within a range* — buffers exist to keep shocks inside that range.
7. **Change the connectors, not the elements.** Replace every player on a team and the system barely changes; change the rules and it's a different game. Swapping life elements (a new app, gym, planner, city) rarely changes outcomes — the connectors (incentives, information, rules, relationships) decide what the system does. When tempted to swap an element, first ask what connector the old one was embedded in.

For canonical definitions (stocks, flows, loop types, hierarchy, self-organization), see the SystemsThinking skill's `Foundation.md` — this skill does not restate the canon, it applies it.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **LifeMap** | "map my life", "model this domain", "stocks and flows of my life", understand a life area structurally | `Workflows/LifeMap.md` |
| **TrapScan** | "why do I keep…", "recurring problem", "self-sabotage", "scan for traps", persistent pattern that resists fixes | `Workflows/TrapScan.md` |
| **LeverageAudit** | "stuck goal", "goal audit", "where's the leverage", "highest-leverage change in my life" | `Workflows/LeverageAudit.md` |
| **FeedbackCheck** | "no progress on", "stalled", "can't tell if it's working", "what am I not measuring" | `Workflows/FeedbackCheck.md` |
| **Dance** | "life review", "dancing with systems", "quarterly review", "step back and look at the whole" | `Workflows/Dance.md` |

## Gotchas

- **Never edit TELOS files directly.** All writes to `~/.claude/PAI/USER/TELOS/` go through the **Telos** skill's Update workflow — it creates timestamped backups and logs the change. This skill *reads* TELOS freely; it *writes* only via Telos.
- **Check TELOS freshness first on multi-machine setups.** If the Life OS syncs across machines (e.g., via an S3 backup script), a stale local copy silently poisons every analysis. Compare local file mtimes against the sync remote before a deep review; warn the user if local is older.
- **Delays will make good interventions look like failures.** Any stock-level change (fitness, savings, reputation) lags its flow-level intervention by weeks to months. Never evaluate an intervention inside its delay window — state the expected delay when proposing it.
- **Behavior reveals purpose; don't analyze aspirations.** When mapping a domain, read time/money/attention allocation (calendars, PROJECTS, actual habits), not just the aspirational files. The revealed system is the real one.
- **Soft stocks count.** Mood, trust, sense of safety, marital goodwill — unmeasurable but real. Dropping them because they lack numbers is itself Meadows' "seeking the wrong goal" trap (optimizing the measurable proxy).
- **Analysis can become the addiction.** Running this skill repeatedly without acting on its output is "shifting the burden to the intervenor" — the analysis relieves the discomfort the discomfort was supposed to drive action. Every workflow ends with at most three concrete moves; if the last run's moves weren't taken, say so before producing new ones.
- **Don't optimize away all slack.** If an audit finds "wasted" buffer time, unallocated money, or redundant skills, that is often resilience, not waste. Flag before recommending its removal.

## Quick Reference

- **5 workflows** — LifeMap, TrapScan, LeverageAudit, FeedbackCheck, Dance
- **8 traps** applied to life domains — table in `References/TelosMapping.md`
- **12 leverage points** mapped to TELOS files — table in `References/TelosMapping.md`; canonical detail in SystemsThinking `LeveragePoints.md`
- **Life stocks inventory** — energy, health, money, skills, relationships, trust, reputation, attention, options

**Context files (loaded on demand):**
- `References/TelosMapping.md` — the Meadows-concept → TELOS-file map: which file holds the paradigms, goals, rules, information flows, and system memory; trap recognition signs per life domain

## Integration

**Depends on:**
- **SystemsThinking** — canonical Meadows/Senge material: `Foundation.md` (definitions), `LeveragePoints.md` (the 12 points in full), `Archetypes.md` (structural patterns). LifeSystems applies this canon to a life; it never restates it.
- **Telos** — owns the Life OS storage. Read TELOS files directly; write only through the Telos Update workflow (backups + changelog).

**Works well with:**
- **FirstPrinciples** — decompose a life assumption before mapping the loops around it.
- **BeCreative / Ideate** — generate intervention candidates after LeverageAudit names the intervention point.
- **Art** — render the stock-and-flow or causal-loop diagrams LifeMap produces.
- **Telos WriteReport** — turn a Dance review into a formatted report.

## Examples

**Example 1: Recurring overcommitment**
```
User: "why do I keep overcommitting to community projects?"
→ TrapScan workflow
→ Reads CHALLENGES.md, PROJECTS.md
→ Match: Tragedy of the Commons — attention is the commons; each project
  claims "just a few hours" against a shared, unpriced attention stock
→ Meadows' way out: regulate the commons — a hard WIP limit on active
  projects, priced against a visible attention budget
→ Proposes CHALLENGES.md update via Telos skill
```

**Example 2: Stalled fitness goal**
```
User: "my fitness goal has been stuck for months"
→ FeedbackCheck workflow
→ Finds: goal has annual target but no weekly signal (missing feedback
  loop); the only measured number is weight, which lags training by
  weeks (delay-induced oscillation: effort spikes, plateau, quit)
→ Fix: add a flow-level metric (sessions/week) with a 7-day cadence —
  leverage point 6 (information flows), far cheaper than a new plan
```

**Example 3: Goal audit before a new year**
```
User: "audit my income diversification goal for leverage"
→ LeverageAudit workflow
→ Reads GOALS.md, STRATEGIES.md for the goal's current strategies
→ Classifies: 4 of 5 strategies are parameter-level (tweak rates,
  hours, prices — leverage points 12–10)
→ Proposes one rules-level move (change what gets your default hour)
  and surfaces the paradigm question underneath (BELIEFS.md: what do
  you believe about who pays for your work?)
```

## Best Practices

1. **Read before intervening — "get the beat of the system."** Review `updates.md`, `LEARNED.md`, and `WRONG.md` history before proposing changes. Meadows' first practice: watch how the system behaves before you touch it.
2. **One loop drawn beats ten insights stated.** Every LifeMap and TrapScan output should contain at least one explicit loop (R or B) with its delay marked.
3. **Always state the leverage level of a proposal.** "Wake up earlier" is a parameter. "Change what feedback you see daily" is information. "Change what you believe success is" is paradigm. Label them so low-leverage busywork is visible as such.
4. **End with ≤3 moves.** Meadows warns against the analyst's temptation to redesign everything. Three concrete moves, each tagged with its leverage point and expected delay.
5. **Feed results back into TELOS.** A trap identified belongs in CHALLENGES.md; a belief surfaced belongs in BELIEFS.md; a lesson belongs in LEARNED.md — via the Telos Update workflow, so the Life OS itself accumulates the system's memory.

---

**Attribution:** Framework from Donella Meadows, *Thinking in Systems: A Primer* (2008) and "Dancing with Systems" (2001); leverage points from "Places to Intervene in a System" (1999). Canonical reference material lives in the SystemsThinking skill.

## Execution Log

After completing any workflow, append a single JSONL entry:

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"WORKFLOW_USED","input":"8_WORD_SUMMARY","status":"ok|error","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
