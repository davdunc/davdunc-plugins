# LifeMap Workflow

Model one life domain as a system: stocks, flows, feedback loops, and delays. This is the foundation workflow — TrapScan and LeverageAudit both work better on a domain that has been mapped.

## Voice Notification

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the LifeMap workflow in the LifeSystems skill to map a life domain"}' \
  > /dev/null 2>&1 &
```

Running the **LifeMap** workflow in the **LifeSystems** skill to map a life domain...

## Step 1: Pick the domain and gather revealed behavior

Ask (or infer from the request) which domain: health, money, work, craft/skills, relationships, community, attention. Then read the TELOS files that touch it:

```
# Aspirational layer (what the system says it wants)
~/.claude/PAI/USER/TELOS/GOALS.md
~/.claude/PAI/USER/TELOS/MISSION.md

# Revealed layer (what the system actually does)
~/.claude/PAI/USER/TELOS/PROJECTS.md
~/.claude/PAI/USER/TELOS/CHALLENGES.md
~/.claude/PAI/USER/TELOS/STRATEGIES.md
```

**Weight the revealed layer over the aspirational one.** Meadows: purpose is deduced from behavior. If available, ask the user for one week of actual time allocation — it outranks every aspirational file.

## Step 2: Name the stocks

List the domain's stocks — accumulations that change slowly and carry the system's memory. Draw from the standard life-stock inventory (energy, health, money, skills, relationships, trust, reputation, attention, options) plus domain-specific ones. For each stock note: current level (rough), trend (rising/flat/falling), and the evidence.

**Include soft stocks** (trust, morale, sense of progress). Unmeasured ≠ unreal.

## Step 3: Name the flows

For each stock: what fills it (inflows) and what drains it (outflows)? Flows are the habits, routines, commitments, and expenses of daily life — the ONLY way any stock changes. A goal stated at stock level ("be fit," "have savings") with no identified flow is a wish, not a plan.

## Step 4: Find the loops

Identify at least one reinforcing (R) and one balancing (B) loop:

- **R loops** — compounding: skill → opportunity → practice → skill; visibility → invitations → visibility. Also vicious: fatigue → poor sleep habits → fatigue.
- **B loops** — goal-seeking or limiting: effort rises until energy budget pushes back; spending rises until the account balance corrects it.

**Mark every delay explicitly** (`—[3 mo]→`). Delays between flow changes and visible stock changes are where humans abandon working interventions.

**Then ask the economist's question: where are the incentives?** Incentives are connectors — they create the dynamic movement between parts. For each loop, name what actually rewards or penalizes the behavior in it (money, approval, relief, identity). A loop with no identified incentive is probably drawn wrong; a bad incentive found here is usually the real finding of the whole map.

## Step 5: Render and report

Produce a diagram (Mermaid or ASCII; use the Art skill for polished rendering) plus:

1. **Stocks table** — stock, level, trend, dominant inflow, dominant outflow
2. **Loop list** — each loop labeled R/B with its delay
3. **Stated vs revealed purpose** — one paragraph on the gap, if any
4. **≤3 observations** (not yet interventions — that's LeverageAudit's job)

## Step 6: Offer persistence

Offer to store the map's key findings in TELOS (CHALLENGES.md or a domain note) **via the Telos skill's Update workflow** — never by direct edit.

## Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"LifeMap","input":"8_WORD_SUMMARY","status":"ok","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
