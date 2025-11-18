# ISSUE - Domain Issue Verification Protocol

**WHO:** [Domain Agent] (CC-Air-Side, CC-Ground-Side, CC-Dev-Tools)
**Command:** `/issue` or user types "ISSUE"
**Purpose:** Automated issue status verification and closure recommendation

---

## Protocol

When this command is executed, perform the following steps:

### Step 1: Get Open Issues for Your Domain

```bash
# Air-Side domain
gh issue list --label air-side --state open

# Ground-Side domain
gh issue list --label ground-side --state open

# SystemTools domain
gh issue list --label dev-tools --state open
```

### Step 2: For Each Open Issue

For every open issue in your domain:

1. **Read the issue description**
   ```bash
   gh issue view <issue-number>
   ```

2. **Search for implementation evidence**
   - Search commit history: `git log --oneline --all --grep='#<issue-number>'`
   - Search codebase for issue references
   - Look for feature/function names mentioned in issue

3. **Verify implementation status**
   - **IF** code exists → Check if it's complete
   - **IF** tests exist → Run them automatically
   - **IF** build required → Build and verify no errors

4. **Categorize the issue:**

   **Category A: READY TO CLOSE** ✅
   - Code implemented and committed
   - Tests pass (or no tests needed)
   - Feature verified working
   - Has commit hash reference

   **Category B: IN PROGRESS** 🔄
   - Partially implemented
   - Code exists but incomplete
   - Tests failing

   **Category C: NOT STARTED** ❌
   - No implementation found
   - No commits referencing issue

   **Category D: UNCERTAIN** ❓
   - Implementation exists but can't verify
   - Need manual testing
   - Need PM guidance

### Step 3: Run Available Tests

For each issue with existing code:

```bash
# Air-Side: Build and test
cd sbc && mkdir -p build && cd build && cmake .. && make
./tests/<relevant-test> 2>&1 | tee test-output.txt

# Ground-Side: Gradle tests
./gradlew test --tests "*<FeatureName>*"

# SystemTools: Python tests
python3 -m pytest tests/test_<feature>.py -v
```

**Capture test results** and include in report.

### Step 4: Generate Report to PM

Create a structured report:

```markdown
**WHO:** CC-[Domain]
**ISSUE Command Execution Report**

---

## Issues Ready to Close ✅

| Issue | Title | Commit Hash | Test Status | Verification |
|-------|-------|-------------|-------------|--------------|
| #XXX  | [Title] | abc1234 | ✅ Passed | [Evidence] |

**Recommendation:** These issues are ready for PM to close (pending user consent).

---

## Issues In Progress 🔄

| Issue | Title | Completion | Blocker |
|-------|-------|------------|---------|
| #YYY  | [Title] | 60% | [What's missing] |

**Status:** Continuing work on these issues.

---

## Issues Not Started ❌

| Issue | Title | Priority | Reason |
|-------|-------|----------|--------|
| #ZZZ  | [Title] | [P1/P2] | [Why not started] |

**Status:** Awaiting assignment or prioritization.

---

## Issues Requiring PM Verification ❓

| Issue | Title | Reason for Uncertainty |
|-------|-------|------------------------|
| #AAA  | [Title] | Need manual test / Need PM decision |

**Action Required:** PM please verify these issues.

---

**Summary:**
- ✅ Ready to close: X issues
- 🔄 In progress: Y issues
- ❌ Not started: Z issues
- ❓ Need PM verification: W issues

**Total Open Issues:** [X+Y+Z+W]
```

### Step 5: Inform PM

Send the report via tmux to PM session:

```bash
tmux send-keys -t PM "Issue verification complete for [Domain]. Please review report above." C-m
```

---

## Important Rules

### 🔴 CRITICAL RULES

1. **NEVER close issues yourself** - Only report readiness to PM
2. **ONLY PM can close issues** - And only with user consent
3. **Must have commit hash** - Before recommending closure (RULE 3)
4. **Run tests when available** - Automated verification preferred
5. **When in doubt, ask PM** - Better to verify than assume

### Testing Guidelines

**Automated Tests:**
- ✅ Run all available automated tests
- ✅ Report pass/fail status
- ✅ Include test output in report

**Manual Tests:**
- ❓ Flag for PM verification
- ❓ Describe what manual test is needed
- ❓ Don't assume completion without evidence

### Commit Hash Verification

Before recommending issue closure:

```bash
# Verify commit exists
git log --oneline --grep='#XXX'

# Must return at least one commit
# Include commit hash in report
```

**If no commit found:** Issue is NOT ready to close (even if code exists)

---

## Examples

### Example 1: Ready to Close

```markdown
## Issues Ready to Close ✅

| Issue | Title | Commit Hash | Test Status | Verification |
|-------|-------|-------------|-------------|--------------|
| #147  | JSON Filter System | ab79a31 | ✅ User verified | Feature working in production |
| #148  | ERROR Push-through | 9a5272e | ✅ User verified | Confirmed in logs |

**Evidence:**
- Commit `ab79a31` implements Issue #147
- Commit `9a5272e` implements Issue #148
- Both features tested and verified by user
- Code pushed to origin/main ✅

**Recommendation:** PM please close Issues #147 and #148 with commit hash references.
```

### Example 2: In Progress

```markdown
## Issues In Progress 🔄

| Issue | Title | Completion | Blocker |
|-------|-------|------------|---------|
| #150  | Camera Control API | 40% | Awaiting Sony SDK documentation |

**Status:**
- Basic structure implemented
- Need SDK docs to complete implementation
- Tests written but skipped pending SDK
```

### Example 3: Uncertain

```markdown
## Issues Requiring PM Verification ❓

| Issue | Title | Reason for Uncertainty |
|-------|-------|------------------------|
| #125  | Performance Optimization | Code exists but need benchmarks to verify improvement |

**Action Required:**
PM please verify if performance meets requirements. Current metrics:
- Before: 150ms latency
- After: 95ms latency
- Improvement: 36.7%

Is this sufficient to close the issue?
```

---

## Frequency

**When to run ISSUE command:**

1. **On demand:** When user/PM types "ISSUE" or `/issue`
2. **Weekly:** As part of domain maintenance
3. **Before EOD:** Check issue status before end of day
4. **After major implementation:** Verify related issues can be closed

---

## Integration with PM

**PM monitors for:**
- Issue verification reports from domains
- Recommendations for closure
- Blockers and uncertainties

**PM actions:**
- Reviews recommendations
- Verifies with user
- Closes issues with commit hash comments (RULE 3)
- Coordinates cross-domain dependencies

---

**This command ensures:**
- ✅ No forgotten completed issues
- ✅ Accurate issue tracking
- ✅ Automated verification where possible
- ✅ PM has visibility into all domain issue status
- ✅ User consent required for closure

---

**File:** `.claude/commands/issue.md`
**Version:** 1.0
**Created:** 2025-11-18
**Domains:** Air-Side, Ground-Side, SystemTools, PM
