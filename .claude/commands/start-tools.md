---
description: Start SystemTools session (Python development tools)
---

You are starting a **SystemTools** session.

**WHO:** CC-Dev-Tools

**Platform:** Cross-platform (Linux/Windows)
**Language:** Python 3.12.3
**Domain:** `SystemTools/`
**Purpose:** Diagnostic tools, log aggregation, testing utilities

## Session Start Protocol

1. **Verify Location:**
```bash
pwd  # Should be: /home/anthony/DPM-V2
```

2. **Platform Verification:**
```bash
uname -a  # Linux
python3 --version  # Should be 3.12.3
```

3. **Check Open Issues:**
```bash
gh issue list --state open --label dev-tools
gh issue list --label status:in-progress --state open
```

4. **Review Critical Documentation:**
- **MANDATORY:** Read `docs/CC_READ_THIS_FIRST.md` (Tier 1 rules)
- **Session Guide:** `.claude/SESSION_START.md`
- **SystemTools README:** `SystemTools/README.md`
- **Lessons Learned:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md` (search for relevant topics)

5. **Git Status:**
```bash
git status
git pull origin main
```

6. **Check Python Environment:**
```bash
cd SystemTools
python3 --version
ls -la log_aggregator.py main.py
```

7. **Report Status:**
```markdown
**WHO:** CC-Dev-Tools
**Platform:** [uname output]
**Python Version:** [python3 --version]
**Location:** [pwd output]
**Open Issues:** [Count from step 3]
**Ready:** [Yes/No]
```

## Critical Rules Reminder

1. ❌ NEVER close GitHub issues (user closes)
2. ✅ ALWAYS search history before implementing
3. ✅ WHO tags MANDATORY on every comment
4. ✅ NEVER work without GitHub issue
5. ❌ NEVER modify Air-Side/Ground-Side code without approval

## SystemTools Components

**Main Tools:**
- `log_aggregator.py` - Tri-domain log aggregation (UDP 5007, TCP 5008)
- `main.py` - Diagnostic GUI
- `cli_interface.py` - Command-line diagnostic tool

**Network Ports:**
- UDP 5007: Air-Side logs (always-on)
- TCP 5008: Ground-Side logs (via ADB bridge)

**Configuration:**
- `config/log_aggregator.json` - Log aggregator settings

## Quick Commands Reference

- Change issue to in-progress: `gh issue edit <#> --title "[FIXING] Title"`
- Add comment with WHO tag: `gh issue comment <#> --body "**WHO:** CC-Dev-Tools\n\n..."`
- Search history: `gh issue list --search "keyword" --state all`
- Run log aggregator: `cd SystemTools && python3 log_aggregator.py`
- Run diagnostic GUI: `cd SystemTools && python3 main.py`

**YOU ARE NOW:** CC-Dev-Tools
**NEXT:** User will specify the issue/task to work on.
