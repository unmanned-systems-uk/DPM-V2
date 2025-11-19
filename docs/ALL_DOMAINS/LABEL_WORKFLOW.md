# GitHub Label Workflow Guide

**WHO:** All Domains (Air-Side, Ground-Side, SystemTools, PM)
**Created:** 2025-11-19
**Purpose:** Standardized label usage for issue tracking and workflow management

---

## 🎯 Label System Overview

We use a **clean, consolidated label system** with no duplicates. Labels track issue lifecycle, priority, domain ownership, and testing status.

---

## 📋 Status Labels (Workflow Progression)

**Format:** `status:*` (no spaces!)

| Label | Description | When to Use | Color |
|-------|-------------|-------------|-------|
| `status:todo` | Not started - waiting to begin work | Issue created but not assigned/started | Purple (#d4c5f9) |
| `status:in-progress` | Currently being worked on | Domain agent actively working on issue | Yellow (#FCD34D) |
| `status:review` | Code complete, ready for review before testing | Code done, needs peer/PM review | Purple (#A855F7) |
| `status:ready` | Code complete, ready for testing | Code reviewed, ready for user testing | Green (#10B981) |
| `status:testing` | In testing phase | User actively testing the fix/feature | Purple (#8B5CF6) |
| `status:fixed` | Confirmed fixed by AI and User testing | User verified working - ready to close | Green (#0e8a16) |
| `status:blocked` | Blocked by dependency | Cannot proceed until blocker resolved | Red (#EF4444) |

---

## 🧪 Testing Labels (User-Facing)

| Label | Description | Who Sets It | Color |
|-------|-------------|-------------|-------|
| `needs-testing` | Waiting for user testing verification | PM/Domain when code ready | Orange (#FFA500) |
| `tested-pass` | User testing completed - PASS ✅ | User after successful test | Green (#28a745) |
| `tested-fail` | User testing completed - FAIL ❌ | User if issue still broken | Red (#d73a4a) |

---

## 🏷️ Domain Labels

| Label | Description |
|-------|-------------|
| `air-side` | Air-Side (Pi 5 SBC) related |
| `ground-side` | Ground-Side (Android H16) related |
| `systemtools` | SystemTools (Python diagnostic app) |
| `dev-tools` | Development Tools general |
| `all-domains` | Affects all domains |
| `pm` | Project Manager coordination |

---

## ⚠️ Priority Labels

| Label | Description | SLA |
|-------|-------------|-----|
| `priority:critical` | Must fix immediately | Same day |
| `priority:high` | High priority | 2-3 days |
| `priority:medium` | Medium priority | 1 week |
| `priority:low` | Low priority | Backlog |

---

## 🔧 Type Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to documentation |
| `protocol` | Protocol compliance and enforcement |
| `architecture` | Architecture and system design |
| `workflow` | Workflow improvements and process |
| `automation` | Automation and bot features |

---

## 📊 Issue Lifecycle with Labels

### **Standard Issue Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                     ISSUE CREATED                            │
│                    status:todo                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   WORK STARTED                               │
│                status:in-progress                            │
│         (Domain agent actively working)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  CODE COMPLETE                               │
│                 status:review                                │
│            (Optional: needs code review)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              READY FOR TESTING                               │
│         status:ready + needs-testing                         │
│          (PM/Domain requests user test)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                USER TESTING                                  │
│               status:testing                                 │
│           (User actively testing)                            │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌─────────────────────┐  ┌─────────────────────┐
    │    TEST PASS ✅      │  │    TEST FAIL ❌      │
    │   tested-pass        │  │   tested-fail        │
    │  status:fixed        │  │ status:in-progress   │
    │                      │  │   (back to work)     │
    └─────────────────────┘  └─────────────────────┘
                │
                ▼
         CLOSE ISSUE
```

---

## 🔄 Blocked Issue Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   BLOCKED                                    │
│              status:blocked                                  │
│  (Add comment explaining blocker + link to blocking issue)  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   Blocker resolved?
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              UNBLOCK & RESUME                                │
│         Remove status:blocked                                │
│         Add status:in-progress                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Label Usage Examples

### **Example 1: Bug Fix (Issues #162, #164)**

**Initial state:**
```
Title: [SYSTEMTOOLS][CRITICAL][PROTOCOL] SystemTools Logger Not Protocol Compliant
Labels: bug, priority:critical, protocol, systemtools, status:in-progress
```

**When code complete:**
```
Action: Domain comments "Code complete, ready for testing"
Update: Add status:ready, needs-testing
Remove: status:in-progress
```

**When user tests (success):**
```
Action: User comments "Tested - all logs have context now! ✅"
Update: Add tested-pass, status:fixed
Remove: status:ready, needs-testing
Then: Close issue
```

**When user tests (failure):**
```
Action: User comments "Still finding 10 logs without context ❌"
Update: Add tested-fail, status:in-progress
Remove: status:ready, needs-testing
Then: Domain continues work
```

### **Example 2: New Feature Request**

**Initial state:**
```
Title: [GROUND-SIDE][FEATURE] Add Battery Monitoring to Health Tab
Labels: enhancement, ground-side, priority:medium, status:todo
```

**Work starts:**
```
Action: Ground-Side agent comments "Starting implementation"
Update: Add status:in-progress
Remove: status:todo
```

**Code review needed:**
```
Action: Domain comments "Implementation complete, requesting PM review"
Update: Add status:review
Remove: status:in-progress
```

**After review:**
```
Action: PM comments "Code looks good, ready for testing"
Update: Add status:ready, needs-testing
Remove: status:review
```

### **Example 3: Blocked Issue**

**Blocked state:**
```
Title: [AIR-SIDE][FEATURE] Implement Camera Auto-Focus
Labels: enhancement, air-side, priority:high, status:blocked

Comment: "Blocked by Sony SDK update (Issue #123). Cannot proceed until
         SDK v2.5 is installed on Pi 5."
```

**Blocker resolved:**
```
Action: PM comments "SDK v2.5 installed on Pi 5"
Update: Remove status:blocked
        Add status:in-progress
```

---

## ✅ Best Practices

### **1. Always Use Status Labels**
❌ BAD:
```
Issue #162: No status label
→ PM can't tell if it's being worked on
```

✅ GOOD:
```
Issue #162: status:in-progress
→ PM knows SystemTools is actively working
```

### **2. Update Status When State Changes**
Domain agents should comment AND update labels:
```markdown
**WHO:** CC-SystemTools

Implementation complete! All 549 log calls now use protocol-compliant format.

Ready for user testing.

[Updates: status:in-progress → status:ready, adds needs-testing]
```

### **3. Use Testing Labels Consistently**
PM/Domain workflow:
1. Domain completes work → `status:ready` + `needs-testing`
2. PM asks user to test
3. User tests and adds `tested-pass` or `tested-fail`
4. If pass → `status:fixed` → close issue
5. If fail → `status:in-progress` → domain continues

### **4. Document Blockers**
When adding `status:blocked`:
```markdown
**Blocked by:** Issue #123 (Sony SDK update)
**Can't proceed until:** SDK v2.5 installed on Pi 5
**Estimated unblock:** 2025-11-20
```

### **5. Clean Up Labels When Closing**
Before closing an issue, final labels should be:
```
status:fixed + tested-pass + (domain) + (priority) + (type)
```

Remove labels like:
- `needs-testing` (no longer relevant)
- `status:ready` (superseded by status:fixed)

---

## 🚫 What NOT to Do

### ❌ **Don't Use Multiple Status Labels**
```
BAD: status:in-progress + status:ready
→ Confusing! What's the actual status?

GOOD: status:ready
→ Clear single state
```

### ❌ **Don't Leave Issues Without Status**
```
BAD: Issue has bug, priority:high, air-side... but no status:*
→ Is anyone working on this? Who knows!

GOOD: Issue has status:in-progress
→ Clear that work is happening
```

### ❌ **Don't Skip Testing Labels**
```
BAD: Domain marks status:fixed without user testing
→ Did user actually verify this works?

GOOD: status:ready + needs-testing → User tests → tested-pass → status:fixed
→ Clear verification trail
```

### ❌ **Don't Use Old Deleted Labels**
These labels were **deleted** during cleanup:
- `status: in-progress` (had space - use `status:in-progress`)
- `status: blocked` (had space - use `status:blocked`)
- `status:fix` (use `status:todo`)
- `status:fixing` (use `status:in-progress`)
- `status:complete` (use `status:fixed` then close issue)

---

## 🔍 Finding Issues by Status

### **CLI Commands**

```bash
# All issues in progress
gh issue list --label "status:in-progress" --state open

# All issues ready for testing
gh issue list --label "status:ready" --state open

# All blocked issues
gh issue list --label "status:blocked" --state open

# All critical issues in progress
gh issue list --label "priority:critical,status:in-progress" --state open

# Combine domain + status
gh issue list --label "systemtools,status:in-progress" --state open
```

### **GitHub Web Interface**

Use label filters:
- `is:issue is:open label:status:in-progress`
- `is:issue is:open label:needs-testing`
- `is:issue is:open label:status:blocked`

---

## 📊 PM Monitoring Dashboard (Quick Commands)

```bash
# What's being worked on right now?
gh issue list --label "status:in-progress" --state open --json number,title,labels

# What needs user testing?
gh issue list --label "needs-testing" --state open

# What's blocked?
gh issue list --label "status:blocked" --state open --json number,title,labels

# Critical issues status
gh issue list --label "priority:critical" --state open --json number,title,labels

# Recent test failures
gh issue list --label "tested-fail" --state open
```

---

## 🔄 Migration Notes (2025-11-19)

**Deleted labels:**
- `status: in-progress` (duplicate with space)
- `status: blocked` (duplicate with space)
- `status: review` (duplicate with space)
- `status:fix` (redundant)
- `status:fixing` (redundant)
- `status:complete` (redundant)

**Added labels:**
- `status:review` (no space)

**Updated descriptions:**
- `status:ready` → "Code complete, ready for testing"

**First issues using new system:**
- Issue #162: Added `status:in-progress`
- Issue #164: Added `status:in-progress`

---

## 📚 Related Documentation

- **Issue Templates:** `.github/ISSUE_TEMPLATE/*.md` - Use protocol_compliance.md template
- **PM Rules:** `.claude/PM_RULES_CRITICAL.md` - PM responsibilities
- **Multi-Domain:** `.claude/MULTI_DOMAIN_COORDINATION.md` - Cross-domain workflow

---

## 🎯 Quick Reference Card

```
ISSUE LIFECYCLE:
todo → in-progress → review → ready → testing → fixed → CLOSE

TESTING FLOW:
needs-testing → (user tests) → tested-pass/tested-fail

BLOCKED FLOW:
blocked → (resolve) → in-progress

STATUS AT A GLANCE:
🟣 status:todo          → Not started
🟡 status:in-progress   → Actively working
🟣 status:review        → Code review needed
🟢 status:ready         → Ready for user test
🟣 status:testing       → User testing now
🟢 status:fixed         → Confirmed working
🔴 status:blocked       → Cannot proceed

TESTING LABELS:
🟠 needs-testing        → User, please test!
🟢 tested-pass          → User: Works! ✅
🔴 tested-fail          → User: Broken ❌
```

---

**Last Updated:** 2025-11-19
**Label Cleanup:** Completed
**System:** Consolidated, no duplicates
