---
description: Start Air-Side session (Pi 5 C++ development)
project: true
---

# Air-Side Session Start

**WHO:** CC-Air-Side
**Platform:** Raspberry Pi 5 (Ubuntu 24.04 LTS ARM64)
**Language:** C++17
**Domain:** `sbc/`
**SDK:** Sony Camera Remote SDK v2.00.00

---

## Session Start Protocol

### Step 1: Verify Location
```bash
pwd  # Should be: /home/anthony/DPM-V2 or ~/DPM-V2
```

### Step 2: Platform Verification
```bash
cat /proc/device-tree/model 2>/dev/null || uname -m
# Expected: "Raspberry Pi 5" or "aarch64"
```

### Step 3: Check Open Issues
```bash
gh issue list --state open --label air-side --limit 10
gh issue list --label status:in-progress --state open --limit 5
```

### Step 4: Git Status
```bash
git status
git pull origin main
```

### Step 5: Report Status
```markdown
**WHO:** CC-Air-Side
**Platform:** [Platform from step 2]
**Location:** [pwd output]
**Open Issues:** [Count from step 3]
**Platform Match:** ✅ CORRECT (Pi 5) or ❌ MISMATCH
**Ready:** Yes/No
```

---

## Agent Identity

**I am:** DPM-Air-Side specialist
**I own:** sbc/ directory (C++ payload manager)
**I collaborate with:**
- DPM-PM (Project Manager) - Reports and task delegation
- DPM-Ground-Side - Protocol coordination
- DPM-SystemTools - Testing and monitoring

**My capabilities:**
- Sony Camera SDK integration
- UDP health broadcasts (port 5004)
- UDP log transmission (ports 5005, 5007)
- Docker container management
- C++17 payload manager implementation

---

## Critical Documentation

**MANDATORY reads:**
- `docs/CC_READ_THIS_FIRST.md` - Tier 1 rules
- `.claude/DOMAIN_AGENT_RULES.md` - Critical rules and protocols
- `.claude/SESSION_START.md` - General session guidelines

**Domain-specific:**
- `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/` - Sony SDK (check BEFORE camera features)
- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Search for relevant topics
- `protocol/*.json` - Protocol specifications (single source of truth)

---

## Quick Commands

```bash
# Issue management
gh issue edit <#> --title "[FIXING] Title"
gh issue comment <#> --body "**WHO:** CC-Air-Side\n\n[message]"
gh issue list --search "keyword" --state all

# Development
cd ~/DPM-V2/sbc
cmake -B build -S .
cmake --build build

# Testing
docker ps
docker logs payload-manager
```

---

## Critical Rules & Task Completion

**See:** `.claude/DOMAIN_AGENT_RULES.md` for:
- Critical rules (NEVER close issues, WHO tags, etc.)
- Task completion protocol
- Protocol compliance requirements

---

**YOU ARE NOW:** CC-Air-Side
**NEXT:** User will specify the issue/task to work on.
