---
description: Saturday weekly readiness review — lives in its own portable repo; this file is a pointer
---

# WeeklyReadiness Workflow — Moved

**This workflow lives in its own repo:** `github.com/davdunc/weekly-readiness` (private), cloned
to `~/Projects/weekly-readiness`. Run `Workflow/WeeklyReadiness.md` from there.

Moved 2026-09-14 so it runs from any machine via `git pull` instead of whichever machine's
`~/.claude` copy is current. The scheduled weekly run is owned by one host (see that repo's
README). The channel list is that repo's `Config/youtube-channels.json`.

The daily **MorningGamePlan** reads this workflow's Notion output (the "Week of YYYY-MM-DD" page)
as its foundation. When it is missing, the game plan says so in its HEADER (it does not stop).

Do not copy the workflow back into this skill (Kestrel `docs/SKILLS.md` SK-3).
