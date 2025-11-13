---
description: Start PM (Project Manager) session with power-cut recovery check
---

Read and execute the PM start protocol from `.claude/PM_START.md`.

If user mentioned "power-cut", "reboot", "recovery", or "lost session", run the recovery protocol first:
```bash
./tools/pm_recovery.sh
```

Then proceed with normal PM start checklist from `.claude/PM_START.md`.
