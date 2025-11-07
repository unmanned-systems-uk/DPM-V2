# WHO Tag System - Comprehensive Guide
*Version 1.0 | Created: 2025-11-07 | Part of Issue #24*

## 📋 Table of Contents
1. [Overview](#overview)
2. [Purpose & Benefits](#purpose--benefits)
3. [Format Specification](#format-specification)
4. [Usage Rules](#usage-rules)
5. [Examples](#examples)
6. [Integration with Historical Learning](#integration-with-historical-learning)
7. [Enforcement](#enforcement)
8. [FAQ](#faq)

---

## Overview

The **WHO Tag System** is a mandatory protocol for all GitHub issue comments in the DPM-V2 project. Every issue comment must begin with a WHO tag identifying the author's role and domain.

**Why?** Because Claude Code has no memory between sessions. WHO tags enable:
- Clear attribution of who worked on what
- Cross-domain tracking (Air↔Ground↔Tools)
- Historical context for future sessions
- Self-documenting collaboration

**Status:** ✅ MANDATORY as of 2025-11-07

**Related:** Issue #24 (WHO Tag Enhancement), Issue #21 (Historical Learning System)

---

## Purpose & Benefits

### 1. Clear Attribution
**Problem:** Without WHO tags, future Claude Code instances can't tell who made which decisions or implementations.

**Solution:** Every comment clearly states the author.

**Example:**
```markdown
**WHO:** CC-Air-Side
Added debug logging to getFocalDistanceMetersLocked()
```
*Now we know CC-Air-Side added this, not CC-Ground-Side or User*

### 2. Cross-Domain Tracking
**Problem:** Issues often involve work across Air-Side, Ground-Side, and Dev-Tools. Without attribution, handoffs are confusing.

**Solution:** WHO tags show exactly when work transitions between domains.

**Example:**
```markdown
**WHO:** CC-Air-Side
Implementation complete. Ground-Side needs to parse focal_distance_meters field.

**WHO:** CC-Ground-Side
Parsing implemented. UI update pending.

**WHO:** User (Anthony)
Tested. UI now displays focus distance correctly.
```
*Clear narrative: Air→Ground→User testing*

### 3. Historical Context
**Problem:** Claude Code starts each session with zero memory. Past decisions are invisible.

**Solution:** WHO tags + historical search = instant context.

**Example:**
```bash
# Find what CC-Air-Side tried for focus issues
gh issue list --search "focus WHO: CC-Air-Side" --state all
```

### 4. Workflow Analysis
**Problem:** Hard to measure how issues flow across domains or identify bottlenecks.

**Solution:** WHO tags enable analytics.

**Example Metrics:**
- Average time Air-Side → Ground-Side handoff
- Which domain creates most issues
- User vs CC issue creation ratio

### 5. Accountability & Ownership
**Problem:** Unclear who made which technical decisions.

**Solution:** Clear ownership trail.

**Example:**
```markdown
**WHO:** CC-Project-Manager
Decision: Implement Air-Side first, then Ground-Side can mock data for UI testing.
```

### 6. Knowledge Transfer
**Problem:** Repeated mistakes because past attempts aren't documented with attribution.

**Solution:** WHO tags + failure documentation = lessons learned.

**Example:**
```markdown
**WHO:** CC-Air-Side
Attempt 1: Added debug logging
Result: ❌ Failed - logs never appeared
Lesson: Camera connection must be established first

**WHO:** CC-Air-Side (different session)
Read above - ensured camera connection first before adding logging. ✅ Success!
```

---

## Format Specification

### Standard Format
```markdown
**WHO:** <Role>
```

### Valid Roles

#### Claude Code Instances
- `**WHO:** CC-Air-Side` - Claude Code working on Pi 5 C++ Air-Side
- `**WHO:** CC-Ground-Side` - Claude Code working on H16 Android Ground-Side
- `**WHO:** CC-Dev-Tools` - Claude Code working on SystemTools Python
- `**WHO:** CC-Project-Manager` - Claude Code in PM coordination role

#### Human Users
- `**WHO:** User (Anthony)` - User Anthony (project owner)
- `**WHO:** User (name)` - Any other human user

### Markdown Formatting
**MUST use:**
- Double asterisks: `**WHO:**` (creates bold)
- Space after colon: `**WHO:** ` not `**WHO:**Role`
- Newline after WHO tag before content

**Example (correct):**
```markdown
**WHO:** CC-Air-Side

Implementation complete. Changes:
- camera_sony.cpp: Added getFocalDistanceMeters()
```

**Example (incorrect - missing newline):**
```markdown
**WHO:** CC-Air-Side Implementation complete.
```

### Placement
**MUST be:**
- First line of every issue comment
- First line of issue description (when creating issue)
- Present in EVERY comment, not just first one

**Example Issue Flow:**
```markdown
Issue #123 created by CC-Project-Manager

[Issue description starts with:]
**WHO:** CC-Project-Manager
This issue tracks implementation of...

---

[First comment by CC-Air-Side:]
**WHO:** CC-Air-Side
Starting implementation. Air-Side changes...

---

[Second comment by User:]
**WHO:** User (Anthony)
Tested. Works great!
```

---

## Usage Rules

### Rule 1: ALWAYS Use WHO Tags
**MANDATORY for:**
- ✅ All GitHub issue comments
- ✅ All GitHub issue descriptions
- ✅ All GitHub PR descriptions
- ✅ All GitHub PR comments

**NOT required for:**
- ❌ Git commit messages (use [DOMAIN] tags instead)
- ❌ Code comments
- ❌ Documentation prose (except when documenting specific decisions)

### Rule 2: WHO Tag MUST Be First
**Correct order:**
```markdown
**WHO:** CC-Air-Side

Implementation status: ...
```

**Incorrect order:**
```markdown
Implementation status: ...

**WHO:** CC-Air-Side
```

### Rule 3: Every Comment Needs WHO Tag
**Even if same person comments multiple times in a row:**
```markdown
**WHO:** CC-Air-Side
First comment at 10:00 AM

---

**WHO:** CC-Air-Side
Update at 2:00 PM - now complete
```

**Why?** Comments may be read out of chronological order or filtered. Each must be self-identifying.

### Rule 4: Use Correct Role
**Choose the role matching your current work:**
- Working on Air-Side C++? → `CC-Air-Side`
- Working on Ground-Side Android? → `CC-Ground-Side`
- Working on SystemTools Python? → `CC-Dev-Tools`
- Coordinating cross-domain? → `CC-Project-Manager`
- Human user? → `User (name)`

**Don't mix roles in single comment:**
```markdown
❌ Bad:
**WHO:** CC-Air-Side and CC-Ground-Side
Both sides updated...

✅ Good:
**WHO:** CC-Project-Manager
Coordination update:
- Air-Side: [status]
- Ground-Side: [status]
```

### Rule 5: Include User Name
**For human users, always include name:**
```markdown
✅ Good: **WHO:** User (Anthony)
❌ Bad: **WHO:** User
```

**Why?** Multiple users may work on project. Name disambiguation is critical.

---

## Examples

### Example 1: Bug Report
```markdown
**WHO:** User (Anthony)

Bug: Focus distance shows 0.0m when in manual focus mode.

Steps to reproduce:
1. Switch to manual focus
2. Check UI - shows 0.0m
3. Expected: Should show actual focus distance

Environment:
- Air-Side: commit aa6da54
- Ground-Side: v1.2.3 APK
```

### Example 2: Implementation Update
```markdown
**WHO:** CC-Air-Side

Implementation complete. Air-Side changes:
- camera_sony.cpp:683 - Added getFocalDistanceMetersLocked()
- messages.h:45 - Added focal_distance_meters field to StatusMessage
- Container rebuilt and deployed

Testing results:
- ✅ Camera query successful
- ✅ Value included in UDP broadcast
- ⏳ Waiting for Ground-Side to parse and display

Ground-Side TODO:
- Update ProtocolMessages.kt to parse focal_distance_meters
- Update CameraViewModel.kt to expose as LiveData
- Update CameraScreen.kt to display in UI
- See: android/docs/ISSUE-001-FOCAL-DISTANCE-GROUNDSIDE-FIX.md
```

### Example 3: Cross-Domain Handoff
```markdown
**WHO:** CC-Ground-Side

Air-Side implementation verified! Ground-Side status:

Testing results:
- ✅ Receiving focal_distance_meters in UDP status packets
- ✅ Parsing correctly in ProtocolMessages.kt (line 156)
- ✅ LiveData updating in CameraViewModel.kt (line 289)
- ❌ UI not displaying - investigating CameraScreen.kt

Next steps:
- Fix UI binding issue in CameraScreen.kt
- Expected: LiveData observer not triggering recomposition
- Will update when resolved
```

### Example 4: User Testing
```markdown
**WHO:** User (Anthony)

Testing complete - SUCCESS! 🎉

Test scenario:
1. Powered on camera and Air-Side
2. Connected Ground-Side H16 tablet
3. Switched between auto focus and manual focus
4. Adjusted focus distance manually

Results:
- ✅ Focus distance displays correctly in all modes
- ✅ Updates in real-time (< 100ms latency)
- ✅ Values match camera LCD display
- ✅ No crashes or freezes

Approve closing this issue.
```

### Example 5: PM Coordination
```markdown
**WHO:** CC-Project-Manager

Cross-domain coordination status for Issue #24:

Air-Side Progress:
- ✅ Issue #1 - Focus distance readback (COMPLETE)
- ⏳ Issue #2 - AF Hold bug (IN PROGRESS - 60% complete)

Ground-Side Progress:
- ✅ Issue #10 - Parsing implementation (COMPLETE)
- ✅ Issue #1 - UI updates (COMPLETE)
- ⏳ Issue #22 - Command routing (BLOCKED - waiting for Air-Side)

Dev-Tools Progress:
- ⏳ Issue #12 - Mock mode (NOT STARTED)

Integration Testing:
- ⏳ Pending completion of Issue #2 and #22

Timeline:
- Expected completion: 2025-11-10
- Blocker: Issue #22 depends on Issue #2
```

### Example 6: Failed Attempt Documentation
```markdown
**WHO:** CC-Air-Side

Attempt 3: Memory Leak Investigation

What: Added RAII wrapper for Sony SDK resources
Code: camera_sony.cpp:450-480
Result: ❌ Failed - Memory still leaks

Details:
- Wrapped CrDeviceHandle in unique_ptr with custom deleter
- Leak persists: 2MB per hour
- Valgrind output shows leak in Sony SDK itself, not our code
- Leak source: libCrCommandSdk.so internal buffers

Lesson: Sony SDK may have internal leak. Need to:
1. Contact Sony support
2. Consider periodic camera reconnection as workaround
3. Monitor production for OOM events

Next: Will try Attempt 4 - periodic connection reset every 6 hours
```

---

## Integration with Historical Learning

WHO tags are integral to the **Historical Learning System** (Issue #21). They enable powerful search patterns.

### Search by Domain
```bash
# Find all Air-Side work on focus
gh issue list --search "focus WHO: CC-Air-Side" --state all

# Find all Ground-Side implementations
gh issue list --search "WHO: CC-Ground-Side implemented" --state all

# Find all PM coordination
gh issue list --search "WHO: CC-Project-Manager" --state all
```

### Search by User vs CC
```bash
# Find user-reported bugs
gh issue list --search "WHO: User bug" --state all --label bug

# Find CC-created issues
gh issue list --search "WHO: CC-" --state all
```

### Extract Domain-Specific Comments
```bash
# Extract only Air-Side comments from an issue
gh issue view 24 --comments | grep -A 20 "WHO: CC-Air-Side"

# Extract cross-domain handoffs
gh issue view 24 --comments | grep -B 2 -A 10 "needs to"
```

### Pattern Recognition
```bash
# Find repeated failures
.github/scripts/search-history.sh "failed" --show-failed | grep "WHO:"

# Track issue transitions across domains
gh issue view 24 --comments | grep "WHO:" | nl
```

---

## Enforcement

### For Claude Code Instances
**MANDATORY:** All Claude Code instances (Air/Ground/Dev/PM) MUST use WHO tags.

**Enforcement:**
1. **Issue templates** include WHO tag field - cannot be skipped
2. **CC_READ_THIS_FIRST.md** documents WHO tag protocol
3. **This guide** provides comprehensive examples
4. **PM role** monitors compliance

**Non-compliance:**
- If WHO tag missing, PM or User should add comment requesting it
- Pattern of non-compliance → Update Claude Code prompt/instructions

### For Human Users
**ENCOURAGED:** Users should use WHO tags for clarity.

**Enforcement:**
- NOT mandatory for users (User burden too high)
- Templates suggest WHO tag format
- Examples demonstrate value

**Exception:** Critical user input (bug reports, testing results) should include WHO tag for historical context.

### Automated Checking (Future)
**Potential GitHub Action:**
```yaml
# Future: Check for WHO tags in issue comments
name: WHO Tag Checker
on: [issue_comment]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check WHO tag
        run: |
          if ! echo "${{ github.event.comment.body }}" | grep -q "^\*\*WHO:\*\*"; then
            echo "⚠️ Warning: Comment missing WHO tag (not enforced yet)"
          fi
```

---

## FAQ

### Q: Do I need WHO tags in git commits?
**A:** No. Git commits use `[DOMAIN][TYPE]` tags (e.g., `[AIR][FIX]`). WHO tags are for GitHub issues/PRs only.

### Q: What if I'm working across multiple domains in one session?
**A:** Use WHO tag matching your primary role for that comment. If coordinating, use `CC-Project-Manager`.

### Q: Can I change WHO tag mid-session?
**A:** Each comment gets its own WHO tag. If you switch domains, use the new domain's WHO tag in the next comment.

Example:
```markdown
**WHO:** CC-Air-Side
Air-Side implementation complete.

[Switches to Ground-Side work]

**WHO:** CC-Ground-Side
Ground-Side implementation started.
```

### Q: What if multiple Claude instances work on same issue?
**A:** Each uses their own WHO tag. WHO tags distinguish between sessions.

Example:
```markdown
**WHO:** CC-Air-Side
Session 1: Attempted debug logging approach - failed.

---

**WHO:** CC-Air-Side
Session 2: Read Session 1 comments. Trying different approach with Sony SDK query.
```

### Q: Do WHO tags go in PR descriptions?
**A:** Yes! PRs should include WHO tag in description.

Example:
```markdown
**WHO:** CC-Air-Side

## Summary
This PR implements focus distance readback for Issue #1.

## Changes
- camera_sony.cpp: Added getFocalDistanceMeters()
- messages.h: Added focal_distance_meters field

## Testing
Tested with Sony A7S III camera. Focus distance displays correctly.
```

### Q: What about issue titles?
**A:** No WHO tag in titles. Titles should be descriptive: `[DOMAIN][TYPE] Description`

### Q: Can users opt out?
**A:** Yes, WHO tags are encouraged but not mandatory for human users. However, critical input (bug reports, test results) benefits from WHO tags for historical context.

### Q: How does this work with GitHub notifications?
**A:** WHO tags are first line of comment, so they appear in notification previews. This helps recipients quickly identify who wrote what.

### Q: What if I forget the WHO tag?
**A:** Edit the comment to add it. GitHub allows comment editing.

---

## Summary

**WHO tags are mandatory for all GitHub issue comments.** They enable:
1. ✅ Clear attribution
2. ✅ Cross-domain tracking
3. ✅ Historical context
4. ✅ Workflow analysis
5. ✅ Accountability
6. ✅ Knowledge transfer

**Format:**
```markdown
**WHO:** <Role>

[Content]
```

**Roles:**
- `CC-Air-Side`, `CC-Ground-Side`, `CC-Dev-Tools`, `CC-Project-Manager`
- `User (name)`

**Always use WHO tags. They cost 10 seconds but save hours of confusion.**

---

*For questions or suggestions about WHO tags, create an issue with label: workflow*

**Related Documents:**
- `docs/CC_READ_THIS_FIRST.md` - WHO Tag Protocol section
- `.github/ISSUE_TEMPLATE/` - All templates include WHO tag fields
- Issue #24 - WHO Tag Enhancement (parent issue)
- Issue #21 - Historical Learning System (related)
