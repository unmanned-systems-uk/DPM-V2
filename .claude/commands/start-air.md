---
description: Start Air-Side session (Pi 5 C++ development)
---

You are starting an **Air-Side** session.

**WHO:** CC-Air-Side

**Platform:** Raspberry Pi 5 (Ubuntu 24.04 LTS ARM64)
**Language:** C++17
**Domain:** `sbc/`
**SDK:** Sony Camera Remote SDK v2.00.00

## Session Start Protocol

1. **Verify Location:**
```bash
pwd  # Should be: /home/anthony/DPM-V2 or ~/DPM-V2
```

2. **Platform Verification:**
```bash
cat /proc/device-tree/model 2>/dev/null || uname -m
# Expected: "Raspberry Pi 5" or similar
```

3. **Check Open Issues:**
```bash
gh issue list --state open --label air-side
gh issue list --label status:in-progress --state open
```

4. **Review Critical Documentation:**
- **MANDATORY:** Read `docs/CC_READ_THIS_FIRST.md` (Tier 1 rules)
- **Session Guide:** `.claude/SESSION_START.md`
- **Sony SDK:** `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/` (check BEFORE implementing camera features)
- **Lessons Learned:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md` (search for relevant topics)

5. **Git Status:**
```bash
git status
git pull origin main
```

6. **Report Status:**
```markdown
**WHO:** CC-Air-Side
**Platform:** [Platform detected from step 2]
**Location:** [pwd output]
**Open Issues:** [Count from step 3]
**Platform Match:** ✅ CORRECT (Pi 5) or ❌ MISMATCH (wrong system!)
**Ready:** [Yes/No]
```

## Critical Rules Reminder

1. ❌ NEVER close GitHub issues (user closes)
2. ✅ ALWAYS search history before implementing
3. ✅ WHO tags MANDATORY on every comment
4. ✅ NEVER work without GitHub issue
5. ❌ NEVER modify Ground-Side/SystemTools code without approval

## Quick Commands Reference

- Change issue to in-progress: `gh issue edit <#> --title "[FIXING] Title"`
- Add comment with WHO tag: `gh issue comment <#> --body "**WHO:** CC-Air-Side\n\n..."`
- Search history: `gh issue list --search "keyword" --state all`
- Check Sony SDK: Open `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html`

**YOU ARE NOW:** CC-Air-Side
**NEXT:** User will specify the issue/task to work on.
