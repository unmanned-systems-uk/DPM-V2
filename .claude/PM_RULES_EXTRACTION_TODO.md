# PM_RULES Detailed Extraction - TODO

**Created:** 2025-11-22
**Status:** Index created, detailed extraction pending

---

## What Was Done

✅ PM_RULES_CRITICAL.md reduced from 706 → 96 lines (86% reduction)
✅ Created index with rule summary and references
✅ Backed up original to `.claude/archive/PM_RULES_CRITICAL.md.backup`

---

## What Remains

The 11 detailed rules need to be extracted from the backup into 3 topic-specific files:

### 1. PM_RULES_COORDINATION.md (To Create)
**Extract from backup:**
- Rule 1: ALWAYS Delegate Coding to Domain Agents
- Rule 2: Tmux Communication Protocol (MANDATORY)
- Rule 2.1: Carriage Return Details
- Rule 3: Monitor Domain Progress via tmux
- Rule 6: Efficient tmux Communication (deprecated)

**Estimated size:** ~250 lines

### 2. PM_RULES_WORKFLOW.md (To Create)
**Extract from backup:**
- Rule 4: PM-Only Tasks
- Rule 5: Context Management
- Rule 7: Session Memory/Context Extension
- Rule 8: Use Extended Thinking for Complex Coordination
- Rule 9: Use opusplan Model for Complex PM Tasks

**Estimated size:** ~300 lines

### 3. PM_RULES_PROTOCOL.md (To Create)
**Extract from backup:**
- Rule 10: Architecture Documentation Updates
- Rule 11: Protocol Enforcement & Cross-Domain Compliance

**Estimated size:** ~150 lines

---

## Quick Extraction Guide

**For next session:**

```bash
# 1. Read backup
cat .claude/archive/PM_RULES_CRITICAL.md.backup

# 2. Extract sections by rule number
# Rules 1-3, 6 → PM_RULES_COORDINATION.md
# Rules 4-5, 7-9 → PM_RULES_WORKFLOW.md
# Rules 10-11 → PM_RULES_PROTOCOL.md

# 3. Verify index references match
# Update PM_RULES_CRITICAL.md if needed
```

---

## Current Status

**Functional:** ✅ Yes - Index provides rule summary and pointers
**Optimal:** ⏳ No - Detailed rules still in 706-line backup
**Priority:** Medium - Can be done in future session

**Benefit of current state:**
- 86% reduction in PM_RULES_CRITICAL.md achieved
- Index provides quick reference
- Backup preserves all content
- Detailed extraction is mechanical work (no design needed)

---

**Next Action:** Extract detailed rules when token budget allows
**File to extract from:** `.claude/archive/PM_RULES_CRITICAL.md.backup`
