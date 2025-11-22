---
description: End of Task - Ground-Side reports completion to PM via tmux
project: true
---

# End of Task - Ground-Side

**Purpose:** Force proper task completion reporting to PM via tmux

**When to use:** After completing ANY task assigned via GitHub issue

---

## Step 1: Verify Task Completion

**Before running this command, ensure:**
- ✅ Code is committed and pushed
- ✅ App builds successfully (./gradlew assembleDebug)
- ✅ Tests pass (if applicable)
- ✅ GitHub issue is updated with final status
- ✅ No blocking errors remain

**If NOT complete:** Do NOT use this command. Finish the task first.

---

## Step 2: Gather Required Information

**You MUST provide:**
1. **Issue number:** `#XXX`
2. **Brief summary:** One sentence describing what was done
3. **Status:** "Complete and ready for review" or "Complete with notes"
4. **Notes (optional):** Any blockers, warnings, or next steps

---

## Step 3: Report to PM via tmux

**Execute this command:**

```bash
tmux send-keys -t DPM-PM "
**WHO:** CC-Ground-Side
**Task Complete**

**Issue:** #[NUMBER]
**Summary:** [One sentence describing completion]
**Status:** [Complete and ready for review / Complete with notes]
**Commit:** [git log -1 --oneline]

[Optional notes, blockers, warnings]
" C-m
```

**CRITICAL:** Replace `[NUMBER]`, `[Summary]`, `[Status]`, and `[Commit]` with actual values!

---

## Step 4: Wait for PM Acknowledgment

**DO NOT start new work until PM responds.**

PM will either:
- ✅ Acknowledge completion and assign new task
- ❌ Request changes or clarification
- 📋 Close issue and update tracking

---

## Example Usage

```bash
# Good example
tmux send-keys -t DPM-PM "
**WHO:** CC-Ground-Side
**Task Complete**

**Issue:** #164
**Summary:** Migrated StructuredLogger to protocol-compliant implementation with context enforcement
**Status:** Complete and ready for review
**Commit:** b4d3f2a Fix Ground-Side StructuredLogger protocol compliance

All 223 raw Log.d/i/w/e calls migrated to StructuredLogger with context parameters.
Protocol compliance check passes. Testing blocked by H16 offline.
" C-m
```

---

## Common Mistakes (AVOID)

❌ **Forgetting to send to PM:**
```bash
# This does nothing - PM never knows you're done!
echo "Task complete"
```

❌ **Missing WHO tag:**
```bash
tmux send-keys -t DPM-PM "Task complete #164" C-m
# PM doesn't know which domain agent sent this
```

❌ **No issue number:**
```bash
tmux send-keys -t DPM-PM "**WHO:** CC-Ground-Side - Task complete" C-m
# PM can't track which issue was completed
```

---

## After Reporting

**Wait for PM response, then:**
- Read PM's next instructions
- Start new task only after PM acknowledgment
- If PM requests changes, address them immediately

---

**Remember:** This command is MANDATORY at end of every task. No exceptions.
