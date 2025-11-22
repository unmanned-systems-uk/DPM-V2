# .claude/ Directory Size Audit - 2025-11-19

## Overview

**ccpm Rule:** Initial session start documents should be ≤100 lines, but can reference other documents.

**Audit Date:** 2025-11-19
**Audited By:** CC-PM

---

## Executive Summary

**Total Files:** 20
**Files Over 100 Lines:** 15 (75%)
**Files Under 100 Lines:** 5 (25%)

**Critical Issues:**
- PM_START.md: 496 lines (session start doc - major violation)
- SESSION_START.md: 215 lines (session start doc - moderate violation)
- start-tools.md: 102 lines (session start doc - minor violation, just over)

---

## Files Over 100 Lines (Violations)

### 🔴 Critical Priority (Session Start Documents)

| File | Lines | Status | Recommended Action |
|------|-------|--------|-------------------|
| **PM_START.md** | 496 | 🔴 CRITICAL | Split into PM_START.md (≤100) + referenced docs |
| **SESSION_START.md** | 215 | 🔴 HIGH | Extract sections to separate docs |
| **start-tools.md** | 102 | 🟡 LOW | Minor trim needed (2 lines) |

### 🟠 High Priority (Referenced by Session Starts)

| File | Lines | Status | Recommended Action |
|------|-------|--------|-------------------|
| **PM_RULES_CRITICAL.md** | 706 | 🟠 HIGH | Split into smaller topic-specific docs |
| **TMUX_COMMUNICATION_PROTOCOL.md** | 504 | 🟠 HIGH | Extract examples to separate file |
| **LESSONS_LEARNED_CRITICAL.md** | 484 | 🟠 HIGH | Keep as reference (historical log) |
| **MULTI_DOMAIN_COORDINATION.md** | 452 | 🟠 HIGH | Extract workflows to separate docs |

### 🟡 Medium Priority (Operational Documents)

| File | Lines | Status | Recommended Action |
|------|-------|--------|-------------------|
| **PM_EOD_2025-11-19.md** | 388 | 🟡 MEDIUM | Archive to .claude/archive/ |
| **AIR_SIDE_RTC_TEST_PLAN.md** | 384 | 🟡 MEDIUM | Keep as reference (test plan) |
| **ARCHITECTURE_UPDATE_RULES.md** | 312 | 🟡 MEDIUM | Extract examples to separate file |
| **PM_EOD_TASKS.md** | 286 | 🟡 MEDIUM | Consolidate with PM_START.md refactor |
| **CONNECTION_DETAILS.md** | 280 | 🟡 MEDIUM | Keep as reference (infrastructure) |
| **PLATFORM_VERIFICATION.md** | 245 | 🟡 MEDIUM | Keep as reference (verification) |
| **PM_NEXT_SESSION_2025-11-19.md** | 213 | 🟡 MEDIUM | Replace with LAST_SESSION.md pattern |
| **SYSTEMTOOLS_COORDINATION.md** | 155 | 🟡 MEDIUM | Keep as is (moderate size) |

---

## Files Under 100 Lines (Compliant)

| File | Lines | Status |
|------|-------|--------|
| **RULES_CRITICAL.md** | 89 | ✅ GOOD |
| **start-air.md** | 80 | ✅ GOOD |
| **TASK_COMPLETION_PROTOCOL.md** | 67 | ✅ GOOD (NEW) |
| **COMPRESSION_EMERGENCY.md** | 52 | ✅ GOOD |
| **start-ground.md** | 97 | ✅ GOOD (was 101, fixed) |
| **start-pm.md** | 12 | ✅ GOOD |

---

## Recommended Refactoring Plan

### Phase 1: Session Start Documents (URGENT)

#### 1.1 PM_START.md (496 lines → ≤100 lines)

**Current Structure:**
- Session start protocol
- Monitoring loops
- Status reporting templates
- Tmux commands reference
- Issue management workflows
- Completion protocols

**Proposed Split:**
```
PM_START.md (≤100 lines)
├─ PM_MONITORING_PROTOCOL.md (monitoring loops, status checks)
├─ PM_ISSUE_MANAGEMENT.md (issue workflows, delegation)
├─ PM_TMUX_COMMANDS.md (tmux command reference)
└─ PM_REPORTING_TEMPLATES.md (status report templates)
```

**PM_START.md should contain:**
- WHO: CC-PM
- Session start checklist (7 steps)
- Critical rules reminder
- References to detailed protocols

#### 1.2 SESSION_START.md (215 lines → ≤100 lines)

**Current Structure:**
- Multi-domain overview
- Git workflow
- Documentation structure
- Common commands

**Proposed Split:**
```
SESSION_START.md (≤100 lines)
├─ GIT_WORKFLOW.md (branching, commits, PRs)
├─ DOC_STRUCTURE.md (documentation hierarchy)
└─ COMMON_COMMANDS.md (frequently used commands)
```

#### 1.3 start-tools.md (102 lines → ≤100 lines)

**Action:** Minor trim (remove 2 lines)
- Condense Quick Commands Reference section
- Already references TASK_COMPLETION_PROTOCOL.md

### Phase 2: High Priority Referenced Documents

#### 2.1 PM_RULES_CRITICAL.md (706 lines)

**Action:** Split into topic-specific docs
```
PM_RULES_CRITICAL.md (≤100 lines - index)
├─ PM_RULES_GITHUB.md (issue management, labeling, closing)
├─ PM_RULES_COORDINATION.md (domain delegation, tmux)
├─ PM_RULES_WORKFLOW.md (session flow, monitoring)
└─ PM_RULES_VIOLATIONS.md (common mistakes, fixes)
```

#### 2.2 TMUX_COMMUNICATION_PROTOCOL.md (504 lines)

**Action:** Extract examples
```
TMUX_COMMUNICATION_PROTOCOL.md (≤100 lines - core protocol)
└─ TMUX_EXAMPLES.md (detailed examples, templates)
```

#### 2.3 MULTI_DOMAIN_COORDINATION.md (452 lines)

**Action:** Extract workflows
```
MULTI_DOMAIN_COORDINATION.md (≤100 lines - overview)
├─ AIR_SIDE_WORKFLOW.md (Air-Side specific)
├─ GROUND_SIDE_WORKFLOW.md (Ground-Side specific)
└─ SYSTEMTOOLS_WORKFLOW.md (SystemTools specific)
```

### Phase 3: Operational Documents

#### 3.1 Archive Dated Documents

**Action:** Create `.claude/archive/` directory
- Move PM_EOD_2025-11-19.md → archive/
- Move PM_NEXT_SESSION_2025-11-19.md → archive/

**Reason:** Historical records, not active session docs

#### 3.2 Create LAST_SESSION.md Pattern

**Action:** Create `.claude/LAST_SESSION.md` (≤100 lines)
- Replace dated PM_EOD_*.md and PM_NEXT_SESSION_*.md
- Single source of truth for "what we were working on"
- Updated at EOD by PM
- Read at session start for context

**Structure:**
```markdown
# Last Session Summary

**Date:** [ISO date]
**Session Duration:** [hours]
**Main Work:** [brief description]

## Completed
- [x] Issue #XXX - Brief description

## In Progress
- [ ] Issue #YYY - Brief description (60% complete)

## Blocked
- [ ] Issue #ZZZ - Brief description (blocked by: H16 offline)

## Next Session Priority
1. Continue Issue #YYY
2. Test Issue #XXX on H16 when online

## Key Decisions Made
- Decision 1
- Decision 2

## Open Questions
- Question 1
- Question 2
```

---

## Implementation Priority

### Immediate (Do Now)
1. ✅ Create TASK_COMPLETION_PROTOCOL.md (DONE)
2. ✅ Update start-*.md to reference it (DONE)
3. 🔄 Trim start-tools.md by 2 lines (IN PROGRESS)
4. Create LAST_SESSION.md

### Short Term (This Session)
5. Refactor PM_START.md (496 → ≤100)
6. Refactor SESSION_START.md (215 → ≤100)
7. Create archive/ directory, move dated docs

### Medium Term (Next Session)
8. Refactor PM_RULES_CRITICAL.md (706 → ≤100)
9. Refactor TMUX_COMMUNICATION_PROTOCOL.md (504 → ≤100)
10. Refactor MULTI_DOMAIN_COORDINATION.md (452 → ≤100)

### Long Term (Future)
11. Review all ≤100 line docs for further optimization
12. Create .claude/README.md explaining directory structure
13. Document refactoring rationale for future sessions

---

## Success Metrics

**Target:** ≤3 files over 100 lines (excluding archives)

**Current State:**
- 15 files over 100 lines (75%)
- 3 session start docs violating rule

**Goal State:**
- ≤3 files over 100 lines (15%)
- 0 session start docs violating rule
- All references < 2 levels deep

---

## Notes

### What Should Stay Large?

**LESSONS_LEARNED_CRITICAL.md (484 lines):**
- Historical log of mistakes and fixes
- Should NOT be split (lose context)
- Acceptable violation (referenced, not session start)

**AIR_SIDE_RTC_TEST_PLAN.md (384 lines):**
- Comprehensive test plan
- Referenced document, not session start
- Splitting would reduce usefulness

**CONNECTION_DETAILS.md (280 lines):**
- Infrastructure reference
- Referenced document
- Acceptable size for infrastructure docs

### Refactoring Principles

1. **Session start docs MUST be ≤100 lines** (strict rule)
2. **Referenced docs SHOULD be ≤100 lines** (guideline)
3. **Historical logs CAN exceed 100 lines** (acceptable)
4. **Test plans CAN exceed 100 lines** (acceptable)
5. **Infrastructure docs CAN exceed 100 lines** (acceptable)

---

**Audit Complete:** 2025-11-19
**Next Review:** After PM_START.md refactor
