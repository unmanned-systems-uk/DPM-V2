# GitHub Issue Workflow - MANDATORY ENFORCEMENT

## ⚠️ CRITICAL: This Workflow is NOT Optional

**Date:** 2025-11-06
**Problem:** Claude Code instances are NOT following issue update protocols
**Impact:** Complete workflow breakdown, confusion, wasted time

## 🆔 WHO TAG REQUIREMENT - MANDATORY

**ALL issue comments MUST start with a WHO tag:**

- `[CC-Air-Side]` - Claude Code working on Air-Side (Pi 5 SBC)
- `[CC-Ground-Side]` - Claude Code working on Ground-Side (H16 Android)
- `[CC-Tools]` - Claude Code working on SystemTools (Python)
- `[CC-Docs]` - Claude Code working on documentation
- `[User]` - Human user providing input/testing results

**Example:**
```bash
gh issue comment 10 --body "**[CC-Ground-Side]** Implementation complete. Testing instructions: ..."
```

**BETTER: Use scripts or files to avoid escaping issues:**
```powershell
# Method 1: Use the WHO script (recommended)
.github\scripts\issue-comment-who.ps1 -IssueNumber 10 -Who "CC-Ground-Side" -Comment "Implementation complete..."

# Method 2: Write to file first (for complex comments)
@"
[CC-Ground-Side]

Implementation complete. Testing instructions:
1. Run the application
2. Check the output
"@ | Out-File comment.md
gh issue comment 10 --body-file comment.md
Remove-Item comment.md
```

**Why:** Clear attribution, cross-domain coordination, audit trail, avoids shell escaping problems

## The Problem We're Solving

### What Happened with Issue #10:
1. **Air-Side Claude** implemented fix but:
   - ❌ Did NOT update issue until prompted
   - ❌ Did NOT provide Ground-Side instructions until prompted

2. **Ground-Side Claude** implemented fix but:
   - ❌ Did NOT update issue #10
   - ❌ Did NOT check what Air-Side had done

**Result:** User had no idea what was happening, work was duplicated, workflow completely broken.

## MANDATORY Workflow - NO EXCEPTIONS

### 1. Starting Work on ANY Issue

```bash
# MUST DO IMMEDIATELY when starting work:
gh issue edit <number> --add-label "status:in-progress"
gh issue comment <number> --body "**[CC-Ground-Side]** Starting work on: [specific description]"
```

**If you don't do this:** User doesn't know work has started, might assign to someone else.

### 2. When You Make ANY Change

```bash
# MUST DO after EVERY significant change:
gh issue comment <number> --body "**[CC-Ground-Side]** Progress update: [what was done]"
```

**If you don't do this:** User has no visibility into progress.

### 3. When Implementation is Complete

```bash
# MUST DO when code is ready for testing:
gh issue comment <number> --body "**[CC-Ground-Side]** Implementation complete.

Testing instructions:
1. [Step 1]
2. [Step 2]

Expected result: [what should happen]"

gh issue edit <number> --remove-label "status:in-progress" --add-label "status:testing"
```

**If you don't do this:** User doesn't know it's ready to test.

### 4. Cross-Domain Requirements

When your fix requires another domain to make changes:

```bash
# MUST DO IMMEDIATELY after your implementation:
gh issue comment <number> --body "**[CC-Air-Side]** Air-Side complete.

**Ground-Side needs to implement:**
1. [Specific change 1]
2. [Specific change 2]

Code location: [file and line numbers]
Example: [provide code snippet if helpful]"

gh issue edit <number> --add-label "status:needs-ground-impl"
```

**If you don't do this:** Other domain doesn't know they need to act, work stops.

### 5. Issue Closure

```bash
# ONLY after user confirms testing successful:
gh issue close <number> --comment "**[CC-Ground-Side]** Fixed in commit [hash].

What was done: [summary]
Files changed: [list]"
```

**NEVER close without user confirmation!**

## Examples of CORRECT Workflow

### Example 1: Single Domain Fix

```bash
# Claude Air-Side session
User: "Work on issue #1 - fix focus distance readback"

# Claude IMMEDIATELY:
gh issue edit 1 --add-label "status:in-progress"
gh issue comment 1 --body "**[CC-Air-Side]** Starting work on focus distance readback in camera_sony.cpp"

# After implementation:
gh issue comment 1 --body "**[CC-Air-Side]** Implementation complete.

Testing instructions:
1. Run ./run_payload_manager.sh
2. Connect from SystemTools
3. Click 'Get Focus Distance'

Expected: Should show actual focus distance value, not 0"

gh issue edit 1 --remove-label "status:in-progress" --add-label "status:testing"
```

### Example 2: Cross-Domain Fix

```bash
# Claude Air-Side session
User: "Fix issue #10 - implement focus distance parsing"

# Claude IMMEDIATELY:
gh issue edit 10 --add-label "status:in-progress"
gh issue comment 10 --body "**[CC-Air-Side]** Starting implementation of getFocusDistance()"

# After Air-Side implementation:
gh issue comment 10 --body "**[CC-Air-Side]** Air-Side implementation complete.

**Ground-Side needs to implement:**
1. Parse focus_distance from status updates
2. Update CameraViewModel.kt line 234 to extract 'focus_distance' field
3. Display in UI at CameraControlScreen.kt line 456

Example parsing code:
\`\`\`kotlin
val focusDistance = statusData.optDouble('focus_distance', 0.0)
\`\`\`

Testing: After both sides implemented, focus distance should update in Android UI"

gh issue edit 10 --add-label "status:needs-ground-impl" --add-label "ground-side"
```

## 🚨 Session Start Requirements - MANDATORY

**BEFORE starting ANY work, EVERY Claude Code session MUST:**

```bash
# Step 1: Check ALL open issues
gh issue list --state open

# Step 2: Check domain-specific issues
gh issue list --label air-side --state open      # Air-Side sessions
gh issue list --label ground-side --state open   # Ground-Side sessions
gh issue list --label dev-tools --state open     # Dev-Tools sessions
```

**Why This Matters:**
- **Prevents missed work**: You may have open issues assigned to you
- **Avoids duplication**: Another domain may have completed their part
- **Ensures coordination**: Cross-domain issues need visibility
- **Maintains continuity**: Understand current state before starting

**Common Workflow Violation:**
```
❌ Ground-Side session starts
❌ User: "Implement feature X"
❌ Claude implements feature X
❌ User: "Why didn't you check Issue #34?"
❌ Issue #34 was already open for Ground-Side with detailed requirements!
```

**Correct Workflow:**
```
✅ Ground-Side session starts
✅ Claude: "Let me check open issues first"
✅ Claude runs: gh issue list --label ground-side --state open
✅ Claude: "I see Issue #34 is open for Ground-Side. Should I work on that?"
✅ User confirms or redirects
```

**This check is MANDATORY at session start - no exceptions!**

## Verification Checklist

Claude Code MUST be able to answer YES to all:

- [ ] Did I check open issues at session start?
- [ ] Did I check domain-specific issues?
- [ ] Did I include WHO tag in ALL comments? (e.g., `[CC-Ground-Side]`)
- [ ] Did I update the issue when I started work?
- [ ] Did I comment on what I'm implementing?
- [ ] Did I provide clear testing instructions?
- [ ] Did I specify what other domains need to do (if applicable)?
- [ ] Did I wait for user confirmation before closing?

## Enforcement

If Claude Code fails to follow this workflow:

1. **User will immediately stop the session**
2. **User will document the failure**
3. **Session will restart with explicit reminder**

## The Golden Rule

**"If you're working on an issue, GitHub should show that you're working on it!"**

No silent work. No assuming the user knows. Always communicate through GitHub issues.

---

*This is not a suggestion. This is mandatory. Failure to follow breaks the entire development workflow.*