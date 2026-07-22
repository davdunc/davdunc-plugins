# TrapScan Workflow

Scan a recurring life problem against Meadows' eight system traps and apply the documented way out. Use when the same problem keeps returning despite repeated event-level fixes — that recurrence is the signature of a trap.

## Voice Notification

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the TrapScan workflow in the LifeSystems skill to scan for system traps"}' \
  > /dev/null 2>&1 &
```

Running the **TrapScan** workflow in the **LifeSystems** skill to scan for system traps...

## Step 1: Gather the pattern's history

Read the problem's paper trail before theorizing:

```
~/.claude/PAI/USER/TELOS/CHALLENGES.md
~/.claude/PAI/USER/TELOS/PROBLEMS.md
~/.claude/PAI/USER/TELOS/LEARNED.md
~/.claude/PAI/USER/TELOS/WRONG.md
~/.claude/PAI/USER/TELOS/updates.md   # how often has this same item resurfaced?
```

Count recurrences. A problem that has appeared in three update cycles under different names is structurally generated — proceed. A first-time event may not need this workflow; say so.

## Step 2: Match against the eight traps

Test the pattern against each trap. Life-domain recognition signs and ways out are tabulated in `References/TelosMapping.md`; the underlying structures are in the SystemsThinking skill's `Archetypes.md`. The eight, with their life signatures:

| Trap | Life signature |
|------|----------------|
| **Policy resistance** | Every fix gets quietly undone — by you, family, or circumstances. Actors pulling the stock toward different goals. |
| **Tragedy of the commons** | A shared, unpriced resource (your attention, evenings, savings) drained by many individually-reasonable claims. |
| **Drift to low performance** | Standards erode; each year's "acceptable" is benchmarked against last year's actual. "I'm doing okay considering…" |
| **Escalation** | Keeping up — spending, working hours, visible output — driven by comparison to a reference that also moves. |
| **Success to the successful** | The already-strong skill/project/relationship gets all the investment; the weak one starves into failure that "proves" the allocation right. |
| **Shifting the burden (addiction)** | A symptomatic relief (caffeine, doomscrolling, comfort spending, heroic all-nighters) that weakens the system's own capacity to solve the real problem. |
| **Rule beating** | Technically hitting your own metric while missing its purpose — logging the workout that wasn't really one, inbox-zero by archiving. |
| **Seeking the wrong goal** | Faithfully optimizing a proxy (income, followers, streak length) while the thing it stood for stagnates. |

Name **one primary trap** (occasionally two interacting). If nothing matches, say so honestly and fall back to the SystemsThinking Iceberg workflow.

## Step 3: Apply the canonical way out

Do not invent a bespoke fix before stating the canonical one — Meadows already solved the general case. The way out for each trap is the "Canonical way out" column of the trap table in `References/TelosMapping.md`; read it and state the matched trap's exit verbatim before adapting it to the user's situation.

## Step 4: Report and persist

Output: the pattern, its recurrence count, the named trap, the structure (one drawn loop), the canonical way out, and **≤3 concrete moves** tagged with expected delay. Offer to record the trap and moves in CHALLENGES.md via the **Telos Update workflow**. If a belief change is implicated, flag it for BELIEFS.md — that is paradigm-level leverage.

## Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"TrapScan","input":"8_WORD_SUMMARY","status":"ok","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
