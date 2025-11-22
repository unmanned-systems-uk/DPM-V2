# Git Workflow Reference

**Purpose:** Git procedures for DPM-V2 development

**Referenced by:** `.claude/SESSION_START.md`

---

## Issue Workflow

### Starting Work
```bash
# Change title IMMEDIATELY when starting (not at EOD)
gh issue edit <#> --title "[FIXING] Title"

# Add comment with WHO tag
gh issue comment <#> --body "**WHO:** CC-[Domain]

Starting work on this issue.
[Brief description of approach]"
```

### During Work
```bash
# Add progress updates
gh issue comment <#> --body "**WHO:** CC-[Domain]

Progress update:
- [x] Completed X
- [ ] Working on Y
- [ ] TODO: Z"
```

### Completing Work
```bash
# Mark complete and request testing
gh issue comment <#> --body "**WHO:** CC-[Domain]

Work complete. Ready for testing.

**Changes:**
- [Description of changes]

**Testing:**
- [How to test]"

# DO NOT close issue - user closes after verification
```

### User Verification
```bash
# User changes title after testing confirms fix
gh issue edit <#> --title "[FIXED] Title"

# User closes issue
gh issue close <#>
```

---

## Commit Format

### Domain Prefixes
```
[AIR][FIX] Description          # Air-Side bug fix
[AIR][FEATURE] Description      # Air-Side new feature
[GROUND][FIX] Description       # Ground-Side bug fix
[GROUND][FEATURE] Description   # Ground-Side new feature
[TOOLS][FIX] Description        # SystemTools bug fix
[TOOLS][FEATURE] Description    # SystemTools new feature
[PM][DOCS] Description          # PM documentation
[PM][WORKFLOW] Description      # PM workflow improvement
```

### Additional Tags
```
[PROTOCOL] - Protocol changes (affects multiple domains)
[CRITICAL] - Critical fix
[TESTED] - Tested and verified
[WIP] - Work in progress (avoid committing WIP)
```

### Examples
```bash
git commit -m "[AIR][FIX] Sony SDK camera reconnection timeout - Issue #45"
git commit -m "[GROUND][FEATURE] Add configuration UI for network settings - Issue #73"
git commit -m "[TOOLS][FIX] Log aggregator memory leak in UDP receiver - Issue #82"
git commit -m "[PM][DOCS] Update multi-domain coordination guide"
```

---

## Architecture Updates

**Schedule:**
- **Wednesday:** Quick status update (15-30 min)
- **Friday:** Comprehensive update (45-90 min)

**Check day:**
```bash
date +%A
```

**Process:**
- See Issue #62 for architecture update checklist
- Update relevant diagrams (C4, sequence, etc.)
- Document changes in ADR if architectural decision made

---

## Historical Search (MANDATORY)

**BEFORE implementing ANY feature:**

```bash
# Search for similar past work
gh issue list --search "focus" --state all
gh issue list --search "camera reconnect" --state all
gh issue list --search "[keyword]" --state all

# View issue and ALL comments
gh issue view <#> --comments

# Document your findings
gh issue comment <#> --body "**WHO:** CC-[Domain]

Historical search results:
- Found #X: Attempted Y, failed because Z
- Found #Y: Different approach with W
- My approach: Will try A because B"
```

**Why this matters:**
- Avoid repeating failed approaches
- Build on successful patterns
- Show you researched before implementing

---

## Branch Strategy

**Main branch:** `main`
**Working branches:** `feature/description` or `fix/description`

```bash
# Create feature branch
git checkout -b feature/camera-settings-ui

# Work on branch
git add .
git commit -m "[GROUND][FEATURE] Description"

# Push and create PR
git push -u origin feature/camera-settings-ui
gh pr create --title "[GROUND][FEATURE] Description" --body "Fixes #XX"
```

---

## Common Git Commands

```bash
# Check status
git status
git log --oneline -10

# Check for unpushed commits
git log origin/$(git branch --show-current)..HEAD

# View changes
git diff
git diff --staged

# Amend last commit (if not pushed)
git commit --amend --no-edit

# Pull latest
git pull origin main

# Check remote
git remote -v
```

---

**Last Updated:** 2025-11-22
**See Also:** `.claude/DOMAIN_AGENT_RULES.md` for critical rules
