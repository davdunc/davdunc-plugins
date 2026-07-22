# Dance Workflow

Periodic whole-life review built on Meadows' "Dancing with Systems" — the practices for living *with* complex systems rather than trying to control them. Run quarterly, at year boundaries, or whenever the request is "step back and look at the whole."

This is deliberately not an optimization pass. Its questions are about resilience, honesty, and time horizons — the things weekly execution never checks.

## Voice Notification

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the Dance workflow in the LifeSystems skill to review the whole life system"}' \
  > /dev/null 2>&1 &
```

Running the **Dance** workflow in the **LifeSystems** skill to review the whole life system...

## Step 0: Freshness gate

On multi-machine setups, verify the local TELOS copy is current against its sync remote before reviewing. A whole-life review on weeks-stale data is worse than none — it re-litigates decisions already made elsewhere.

## Step 1: Get the beat

Read the system's actual behavior over time before judging it:

```
~/.claude/PAI/USER/TELOS/updates.md   # what actually changed, how often
~/.claude/PAI/USER/TELOS/LEARNED.md
~/.claude/PAI/USER/TELOS/WRONG.md
~/.claude/PAI/USER/TELOS/GOALS.md
~/.claude/PAI/USER/TELOS/BELIEFS.md
~/.claude/PAI/USER/TELOS/CHALLENGES.md
~/.claude/PAI/USER/TELOS/PROJECTS.md
```

Summarize the period's trajectory in 3–5 sentences of observed behavior — no evaluation yet. Meadows' first practice: before you disturb the system, watch how it behaves.

## Step 2: Walk the practices

Work through the Dancing-with-Systems practices as questions against the material read:

1. **Expose your mental models.** Where did behavior contradict a stated belief this period? Each contradiction is either a WRONG.md candidate (belief was false) or a structure problem (belief is true but the system can't act on it). Name which.
2. **Honor and expand information.** What decision was made on missing or stale information? What feedback loop would have prevented it? (Feed candidates to FeedbackCheck.)
3. **Pay attention to what is important, not just what is quantifiable.** Which soft stocks (relationships, trust, joy, health-adjacent-to-energy) moved this period without any file noticing?
4. **Locate responsibility in the system.** For the period's biggest frustration: what structure produced it? (If it recurs, hand to TrapScan.) Resist both self-blame and other-blame — both are event-layer.
5. **Stay humble; stay a learner.** What did WRONG.md gain this period? An empty WRONG.md over a full quarter is itself a signal — either nothing was risked or nothing was admitted.
6. **Expand time horizons.** Which current decisions look different on a 5-year horizon? Which stocks being drained now (health, trust, options) have delays long enough that today's comfort is borrowing from a future self?
7. **Defend resilience against optimization.** Inventory the buffers: financial slack, calendar slack, energy reserve, skill redundancy. Did any get "optimized away"? A fully-allocated life is one perturbation from cascade.
8. **Celebrate complexity — go for the good of the whole.** Is any single stock (income, output, one relationship, one metric) being maximized at the expense of the system? Self-organization needs freedom and mess at the edges.
9. **Check for purpose drift.** A system's purpose is what it does, not what it says — and systems drift toward perpetuating themselves. Which commitments, projects, or organizations in PROJECTS.md now exist mainly to keep existing? Which of your own routines serve their original purpose versus their own continuation?

## Step 3: Report

Produce the review in this shape:

1. **The beat** — observed trajectory, 3–5 sentences
2. **Practice findings** — only the practices that surfaced something (skip empty ones)
3. **System health** — stocks table: rising / stable / draining, with soft stocks included
4. **≤3 moves** — each tagged with leverage point and expected delay; deliberately few. If last Dance's moves weren't taken, lead with that fact instead of proposing new ones.

## Step 4: Persist

Offer TELOS updates — WRONG.md admissions, BELIEFS.md revisions, CHALLENGES.md additions, GOALS.md adjustments — **via the Telos Update workflow** (backup + changelog). Optionally hand off to Telos **WriteReport** for a formatted document.

## Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"LifeSystems","workflow":"Dance","input":"8_WORD_SUMMARY","status":"ok","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
