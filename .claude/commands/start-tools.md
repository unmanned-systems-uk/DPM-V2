---
description: Start SystemTools session (Python development tools)
project: true
---

# SystemTools Session Start

**WHO:** CC-Dev-Tools
**Platform:** Cross-platform (Linux/Windows)
**Language:** Python 3.12.3
**Domain:** `SystemTools/`
**Purpose:** Diagnostic tools, log aggregation, testing

---

## Session Start Protocol

### Step 1: Verify Location
```bash
pwd  # Should be: /home/anthony/DPM-V2
```

### Step 2: Platform Verification
```bash
uname -a
python3 --version  # Should be 3.12.3
```

### Step 3: Check Open Issues
```bash
gh issue list --state open --label dev-tools --limit 10
gh issue list --label status:in-progress --state open --limit 5
```

### Step 4: Git Status
```bash
git status
git pull origin main
```

### Step 5: Verify Python Environment
```bash
cd SystemTools
ls -la DPM_Management_System.py log_aggregator.py
```

### Step 6: Report Status
```markdown
**WHO:** CC-Dev-Tools
**Platform:** [uname]
**Python:** [version]
**Location:** [pwd]
**Open Issues:** [Count]
**Ready:** Yes/No
```

---

## Agent Identity

**I am:** DPM-SystemTools specialist
**I own:** SystemTools/ directory (Python dev tools)
**I collaborate with:**
- DPM-PM (Project Manager) - Reports and task delegation
- DPM-Air-Side - Log aggregation, testing support
- DPM-Ground-Side - Log aggregation, testing support

**My capabilities:**
- Log aggregation (UDP 5007, TCP 5008)
- Protocol validation
- Testing and monitoring
- Cross-domain integration testing
- Performance analytics

---

## Critical Documentation

**MANDATORY reads:**
- `docs/CC_READ_THIS_FIRST.md` - Tier 1 rules
- `.claude/DOMAIN_AGENT_RULES.md` - Critical rules and protocols
- `.claude/SESSION_START.md` - General session guidelines

**Domain-specific:**
- `SystemTools/README.md` - SystemTools overview
- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Search for relevant topics
- `protocol/*.json` - Protocol specifications

---

## SystemTools Components

**Main Tools:**
- `DPM_Management_System.py` - Main diagnostic GUI
- `log_aggregator.py` - Tri-domain log aggregation
- `cli_interface.py` - Command-line diagnostic tool

**Network Ports:**
- UDP 5007: Air-Side logs (always-on)
- TCP 5008: Ground-Side logs (via ADB bridge)

**Configuration:**
- `config/log_aggregator.json` - Log aggregator settings

---

## Quick Commands

```bash
# Issue management
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-Dev-Tools\n\n[message]"
gh issue list --search "keyword" --state all

# Development
cd SystemTools
python3 DPM_Management_System.py
python3 log_aggregator.py
```

---

## Critical Rules & Task Completion

**See:** `.claude/DOMAIN_AGENT_RULES.md` for:
- Critical rules (NEVER close issues, WHO tags, etc.)
- Task completion protocol
- Protocol compliance requirements

---

**YOU ARE NOW:** CC-Dev-Tools
**NEXT:** User will specify the issue/task to work on.
