---
description: Extract trading lessons and push to TELOS life framework
---

# UpdateTelos Workflow

## Steps

### 1. Identify Lessons to Save

From the most recent daily or weekly review, extract:
- New lessons learned (→ WISDOM.md)
- New challenges identified (→ CHALLENGES.md)
- Goal progress or new goals (→ GOALS.md)
- Patterns that need correction (→ CHALLENGES.md)
- Things the trader was wrong about (→ WRONG.md)

### 2. Check for Duplicates

Read existing TELOS files to avoid duplicating lessons:
- `~/.claude/LifeOS/USER/TELOS/WISDOM.md`
- `~/.claude/LifeOS/USER/TELOS/CHALLENGES.md`
- `~/.claude/LifeOS/USER/TELOS/GOALS.md`

If a lesson is a refinement of an existing entry, update rather than duplicate.

### 3. Format and Execute Updates

Use the TELOS Update workflow tool:
```bash
bun ~/.claude/skills/Telos/Tools/UpdateTelos.ts "[FILE]" "[CONTENT]" "[DESCRIPTION]"
```

### 4. Also Update Trading Intelligence

If the lesson relates to a specific setup or pattern:
- Append to the relevant intelligence file in `~/.claude/LifeOS/USER/TRADING/Intelligence/`
- This keeps personal experience alongside analyst content

### 5. Confirm

List all updates made and which files were modified.
