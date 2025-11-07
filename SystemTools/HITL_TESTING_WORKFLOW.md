# SystemTools HITL Testing Workflow

**Document Version:** 1.0
**Created:** November 7, 2025
**Domain:** SystemTools (Dev-Side)
**Status:** Active

---

## Overview

This document defines the Human-In-The-Loop (HITL) testing workflow for the DPM SystemTools diagnostics system, integrating with the CCPM testing framework.

---

## WHO Tag Standard

All GitHub issue comments from Claude Code in the SystemTools domain MUST use the WHO tag:

```markdown
[CC-SystemTools]
```

**Examples:**
```markdown
[CC-SystemTools] Implementation complete. Test plan created.

[CC-SystemTools]

## Bug Fix Complete

Testing required for ADB connection fix.
```

---

## Historical Search Workflow

Before implementing ANY feature or fix, Claude Code MUST:

### 1. Search Historical Issues
```powershell
.github\scripts\search-history.ps1 "<keyword>"
```

### 2. Review Related Issues
Read all related closed and open issues to understand:
- What was tried before
- Why it failed or succeeded
- What approaches to avoid

### 3. Document Findings
In the issue comment, document:
```markdown
[CC-SystemTools]

## 🧠 Historical Learning Applied

**Search performed:** <keyword>

**Related issues found:**
- Issue #X: Tried [approach] - [outcome]
- Issue #Y: Tried [approach] - [outcome]

**My approach:**
[Explain why your approach is different and why it should succeed]
```

---

## HITL Testing Procedure

### When CC Completes Implementation

**Step 1: Label the issue**
```bash
gh issue edit <number> --add-label "needs-testing"
```

**Step 2: Post implementation complete comment**
```markdown
[CC-SystemTools]

## ✅ Implementation Complete

**What was implemented:**
- Feature/fix description
- Files modified

**Testing Required:**
User testing needed to verify:
1. [Test item 1]
2. [Test item 2]
3. [Test item 3]

**Test Environment:**
- SystemTools version: [version]
- Dependencies: [any new dependencies]
- Hardware: [Air-Side, H16, etc.]
```

**Step 3: Create test plan (if CCPM available)**
```bash
# POST to CCPM API
curl -X POST https://ccpm-url/api/test-plans \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": <number>,
    "project_id": 2,
    "test_items": [
      "Test item 1",
      "Test item 2"
    ]
  }'
```

### When User Tests

**Step 1: Run SystemTools**
```bash
cd SystemTools
python main.py
```

**Step 2: Execute test items**
Follow the test checklist provided by CC

**Step 3: Document results**
- ✅ Pass - Feature works as expected
- ❌ Fail - Feature has issues
- ⏭️ Skip - Could not test (explain why)

**Step 4: Post results to GitHub**
```markdown
[WHO: Anthony]

## 🧪 Testing Complete

**Test Result:** PASS/FAIL

**Items Tested:**
- ✅ Test item 1
- ❌ Test item 2 - [reason for failure]
- ⏭️ Test item 3 - [reason skipped]

**Notes:**
[Any additional observations]
```

**Step 5: Update labels**
```bash
# If passed
gh issue edit <number> --remove-label "needs-testing" --add-label "tested-pass"

# If failed
gh issue edit <number> --remove-label "needs-testing" --add-label "tested-fail"
```

### When Testing Fails

CC must:
1. Review failure notes
2. Implement fixes
3. Restart testing workflow

```markdown
[CC-SystemTools]

## 🔧 Fix Implemented

**Issue:** [what failed]

**Root cause:** [analysis]

**Fix applied:** [what was changed]

**Re-testing required:**
Please retest:
- [specific area that was fixed]
```

---

## Test Plan Template for SystemTools

### Standard Diagnostic Test Plan

```markdown
## SystemTools Diagnostic Test Plan

**Issue:** #<number>
**Feature:** <feature name>
**Tester:** <name>
**Date:** <YYYY-MM-DD>

### Environment Setup
- [ ] SystemTools installed and running
- [ ] Air-Side reachable at 10.0.1.53
- [ ] H16 connected via ADB (10.0.1.92:5555)
- [ ] All dependencies installed

### Connection Tests
- [ ] TCP connection to Air-Side succeeds
- [ ] SSH connection to Air-Side succeeds
- [ ] ADB connection to H16 succeeds
- [ ] UDP listeners receiving data

### Feature-Specific Tests
- [ ] [Test specific to the feature]
- [ ] [Test specific to the feature]
- [ ] [Test specific to the feature]

### Error Handling Tests
- [ ] Handles connection failures gracefully
- [ ] Displays error messages clearly
- [ ] Does not crash on invalid input

### Performance Tests
- [ ] Responds within expected time (<2s for UI actions)
- [ ] Does not freeze or hang
- [ ] Memory usage stays reasonable

### Documentation Tests
- [ ] Feature documented in PROGRESS_AND_TODO.md
- [ ] User instructions clear
- [ ] Code comments sufficient

### Pass/Fail Criteria
**Pass:** All items checked, no critical failures
**Fail:** Any critical feature fails or system crashes
**Partial:** Minor issues that don't block usage
```

---

## Common Test Scenarios

### 1. New Tab Implementation

```markdown
**Testing Required:**
1. New tab appears in notebook
2. Tab loads without errors
3. UI elements render correctly
4. Functionality works as expected
5. No errors in console/logs
6. Other tabs still work normally
```

### 2. Network Feature

```markdown
**Testing Required:**
1. Connection establishes successfully
2. Data transmitted/received correctly
3. Handles connection loss gracefully
4. Reconnection works
5. Error messages informative
6. Logs show correct information
```

### 3. ADB Feature

```markdown
**Testing Required:**
1. ADB connection to 10.0.1.92:5555 succeeds
2. Commands execute on H16
3. Output displayed correctly
4. Handles ADB not found error
5. Handles device not found error
6. Disconnect works cleanly
```

### 4. UI Enhancement

```markdown
**Testing Required:**
1. UI elements render correctly
2. Buttons/controls respond to clicks
3. Text is readable
4. Colors/indicators work
5. Layout adjusts to window size
6. No visual glitches
```

---

## Testing Labels

| Label | Meaning | Who Sets |
|-------|---------|----------|
| `needs-testing` | Awaiting user verification | CC |
| `tested-pass` | User testing passed | User |
| `tested-fail` | User testing failed | User |
| `cc-blocked-human` | CC waiting for user action | CC |
| `user-blocked-cc` | User waiting for CC fix | User |

---

## CCPM Integration

### API Endpoints (When Available)

**Create Test Plan:**
```http
POST /api/test-plans
Content-Type: application/json

{
  "issue_id": 28,
  "project_id": 2,
  "test_items": [
    "TCP connection succeeds",
    "ADB connection succeeds"
  ],
  "environment": "SystemTools + Air-Side + H16",
  "tester": "Anthony"
}
```

**Submit Test Results:**
```http
POST /api/test-plans/:id/results
Content-Type: application/json

{
  "status": "pass",
  "results": [
    {"item": "TCP connection succeeds", "status": "pass"},
    {"item": "ADB connection succeeds", "status": "pass"}
  ],
  "notes": "All tests passed successfully",
  "evidence": "logs/test-output.txt"
}
```

**Get Pending Tests:**
```http
GET /api/testing/projects/2/pending
```

Returns list of pending DPM tests with urgency indicators.

---

## Workflow Compliance Checklist

Before starting ANY implementation, CC must verify:

- [ ] ✅ Searched historical issues for related work
- [ ] ✅ Documented findings in comment
- [ ] ✅ Explained why approach is different
- [ ] ✅ Using [CC-SystemTools] WHO tag
- [ ] ✅ Not repeating failed solutions

After completing implementation, CC must:

- [ ] ✅ Added `needs-testing` label
- [ ] ✅ Posted implementation complete comment
- [ ] ✅ Provided clear test instructions
- [ ] ✅ Updated PROGRESS_AND_TODO.md
- [ ] ✅ NOT closed issue (only user closes after testing)

---

## Examples

### Example 1: Bug Fix Workflow

```markdown
[CC-SystemTools]

## 🧠 Historical Learning Applied

**Search performed:** "ADB connection"

**Related issues found:**
- Issue #20: ADB diagnostics tab works correctly
- Issue #28: Connection Monitor ADB failed

**Root cause identified:**
H16 Diagnostics tab uses `adb connect <ip>:5555` before checking devices.
Connection Monitor was not doing this for network devices.

**My approach:**
Enhance ADBClient to detect network addresses (containing ':') and automatically
run `adb connect` before querying device list. This matches the working approach
from H16 Diagnostics tab.

---

## ✅ Implementation Complete

**Files Modified:**
- `network/adb_client.py` - Added network device connection
- `gui/tab_connection.py` - Pass H16 IP when connecting

**Testing Required:**
1. Open Connection Monitor tab
2. Click "Connect All" or "ADB Connect"
3. Verify ADB connects to 10.0.1.92:5555
4. Verify no error messages in log
5. Verify H16 status shows "Connected"
```

### Example 2: Feature Implementation

```markdown
[CC-SystemTools]

## 🧠 Historical Learning Applied

**Search performed:** "GitHub integration"

**Related issues found:**
- No previous attempts to integrate GitHub in SystemTools

**My approach:**
Create new tab using native urllib (no external dependencies) to match
project's minimal dependency philosophy. Implement read-only features first
(view issues, comments) before write operations.

---

## ✅ Implementation Complete

**Files Created:**
- `gui/tab_github_integration.py` - GitHub Integration tab

**Files Modified:**
- `main.py` - Added GitHub tab to notebook

**Testing Required:**
1. Open GitHub Integration tab
2. Configure GitHub token in Settings
3. Click "Load Issues"
4. Verify issues display correctly
5. Click an issue to view details
6. Verify comments display correctly
7. Try adding a comment (requires token)
```

---

## Success Metrics

**Workflow is successful when:**
1. ✅ All CC comments include [CC-SystemTools] WHO tag
2. ✅ Historical search performed before every implementation
3. ✅ Test plans created for all new features/fixes
4. ✅ User tests before issues are closed
5. ✅ Testing failures result in fixes, not closed issues
6. ✅ No duplicate work from repeating past failures

---

## References

- **Main Workflow Guide:** `docs/CC_READ_THIS_FIRST.md`
- **Issue #26:** New Workflow Requirements
- **Issue #27:** HITL Testing System (CCPM)
- **Issue #29:** HITL Testing for Diagnostics System
- **Search Script:** `.github/scripts/search-history.ps1`

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
