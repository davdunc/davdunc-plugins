# lifesystems

Systems thinking for your life, from Donella Meadows' *Thinking in Systems: A Primer* (2008). Treats a personal Life OS as what it is — a system of stocks (energy, money, skills, trust, attention), flows (habits, commitments), and feedback loops — and intervenes where leverage is highest instead of where effort is easiest.

## Workflows

| Workflow | Use when |
|----------|----------|
| **LifeMap** | Model one life domain as stocks/flows with reinforcing and balancing loops — including the economist's question: where are the incentives? |
| **TrapScan** | A problem keeps coming back despite fixes — match it against Meadows' eight system traps and apply the documented way out |
| **LeverageAudit** | A goal is stuck — classify its strategies against the 12 leverage points and find the higher-leverage move |
| **FeedbackCheck** | No visible progress — find the missing, delayed, distorted, or unheeded feedback loop |
| **Dance** | Quarterly/whole-life review using the "Dancing with Systems" practices — resilience over optimization |

## Expectations and dependencies

- **Life OS data**: workflows read a TELOS-style directory at `~/.claude/PAI/USER/TELOS/` (GOALS.md, BELIEFS.md, CHALLENGES.md, STRATEGIES.md, …). Without it, workflows still run — they'll ask you for the context instead of reading it.
- **PAI companions (optional)**: designed to pair with a `SystemsThinking` skill (canonical Meadows reference material) and a `Telos` skill (backed-up Life OS writes). Absent those, the skill's own `References/TelosMapping.md` carries the applied tables, and it will simply avoid writing files for you.
- Voice notifications post to `localhost:31337` and are fire-and-forget; harmless if no listener exists.

## Design principles

Every workflow ends in **at most three concrete moves**, each tagged with its leverage point (12 = parameters, weakest → 1 = transcending paradigms, strongest) and its expected delay — because life stocks respond slowly, and judging an intervention inside its delay window is how good interventions die.
