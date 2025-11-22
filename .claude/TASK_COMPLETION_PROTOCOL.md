# Task Completion Protocol

**WHO:** All Domain Agents (CC-Air-Side, CC-Ground-Side, CC-Dev-Tools)

## When Task Complete

Follow these steps **every time** you complete an assigned task:

### 1. Update GitHub Issue
✅ Add completion comment to the assigned GitHub issue with:
- **WHO:** tag (CC-Air-Side, CC-Ground-Side, or CC-Dev-Tools)
- Brief summary of what was completed
- Key deliverables (files modified, tests run, etc.)
- Any blockers or notes for future work

### 2. Report to PM Session
✅ Send completion report to PM tmux session:

**Air-Side:**
```bash
tmux send-keys -t PM "# **WHO:** CC-Air-Side
# Issue #[NUM] - Task Complete
[Brief summary with key deliverables]
" C-m
```

**Ground-Side:**
```bash
tmux send-keys -t PM "# **WHO:** CC-Ground-Side
# Issue #[NUM] - Task Complete
[Brief summary with key deliverables]
" C-m
```

**SystemTools:**
```bash
tmux send-keys -t PM "# **WHO:** CC-SystemTools
# Issue #[NUM] - Task Complete
[Brief summary with key deliverables]
" C-m
```

### 3. Wait for Acknowledgment
✅ Wait for PM acknowledgment or next assignment
- Do NOT start new work without PM assignment
- Do NOT close GitHub issues (PM closes)
- Do NOT commit/push without explicit instruction

## Example Completion Report

```bash
tmux send-keys -t PM "# **WHO:** CC-Air-Side
# Issue #144 - Task Complete
Implemented camera status broadcast in health snapshot.
Modified: sbc/health_monitor.cpp, sbc/health_monitor.h
Testing: Verified 200ms broadcast frequency on UDP 5004
Ready for next assignment.
" C-m
```

## Critical Rules

- ❌ NEVER skip the completion report (PM needs to know you're done)
- ❌ NEVER close GitHub issues (user closes)
- ❌ NEVER start new work without PM assignment
- ✅ ALWAYS use WHO tags in all communications
- ✅ ALWAYS update the issue BEFORE reporting to PM
