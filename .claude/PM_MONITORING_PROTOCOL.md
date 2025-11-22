# PM Monitoring Protocol

**Purpose:** Real-time domain monitoring, status tracking, and coordination procedures

**Referenced by:** `.claude/PM_START.md`

---

## 📊 PM Monitoring Loop (Every 15-30 Minutes)

### Quick Status Scan

```bash
# 1. Check all tmux sessions for activity
tmux capture-pane -t DPM-SYSTEM -p | tail -10
tmux capture-pane -t DPM-GROUND -p | tail -10
tmux capture-pane -t DPM-AIR -p | tail -10
tmux capture-pane -t DPM-TOOLS -p | tail -10

# 2. Check for errors
tmux capture-pane -t DPM-SYSTEM -p | grep -E "(ERROR|FAIL|✗)" | tail -5
tmux capture-pane -t DPM-GROUND -p | grep -E "(ERROR|FAIL|✗)" | tail -5
tmux capture-pane -t DPM-AIR -p | grep -E "(ERROR|FAIL|✗)" | tail -5

# 3. Check for completions
tmux capture-pane -t DPM-SYSTEM -p | grep -E "(✓|✅|Complete)" | tail -5
tmux capture-pane -t DPM-GROUND -p | grep -E "(✓|✅|Complete)" | tail -5
tmux capture-pane -t DPM-AIR -p | grep -E "(✓|✅|Complete)" | tail -5

# 4. Check issue updates
gh issue list --label status:in-progress --state open --json number,title,updatedAt
```

### Status Report to User

**Format:**
```markdown
**PM Status Update** - [Timestamp]

**Domain Activity:**
🟢 Ground-Side (#73): [Status from tmux] - [Component working on]
🟢 Air-Side (#72): [Status from tmux] - [Component working on]
🟢 SystemTools (#74): [Status from tmux] - [Component working on]

**Progress:**
- Ground-Side: XX% complete
- Air-Side: XX% complete
- SystemTools: XX% complete

**Blockers:** [None | List blockers]
**Next Checkpoint:** [Next milestone]
```

---

## 🎯 PM Active Monitoring Capabilities

### Real-Time Progress Tracking

**What PM can see:**
1. **Code being written** - View actual implementation in progress
2. **Compilation errors** - Catch build failures immediately
3. **Test results** - See test passes/failures in real-time
4. **Git commits** - Track when code is committed
5. **Tool usage** - See which files are being read/edited
6. **Blockers** - Identify when a domain is stuck

### Example Monitoring Commands

```bash
# See what Ground-Side is currently doing
tmux capture-pane -t DPM-GROUND -p | tail -50

# Check if Air-Side has errors
tmux capture-pane -t DPM-AIR -p | grep -B5 -A5 "ERROR"

# See SystemTools test results
tmux capture-pane -t DPM-TOOLS -p | grep -E "(PASS|FAIL|✓|✗)"

# Monitor Ground-Side compilation
tmux capture-pane -t DPM-GROUND -p | grep -E "(gradlew|Build|Compil)"

# Watch for Git activity
tmux capture-pane -t DPM-GROUND -p | grep -E "(git add|git commit|git push)"
```

---

## 🚨 PM Alert Triggers

### Auto-Check for These Conditions:

**Error Patterns:**
```bash
# Critical errors
grep -E "(CRITICAL|FATAL|CRASH)" <session-output>

# Build failures
grep -E "(BUILD FAILED|compilation error)" <session-output>

# Test failures
grep -E "(FAIL|FAILED|✗.*test)" <session-output>

# Blocked status
grep -E "(BLOCKED|blocked|waiting for)" <session-output>
```

**When detected:**
1. Alert user immediately
2. Check relevant issue for blocker updates
3. Verify if other domains affected
4. Coordinate resolution

---

## 🔄 PM Coordination Actions

### When Domain Reports Progress

```bash
# Verify claim by checking tmux session
tmux capture-pane -t [Domain] -p | tail -100

# Update tracking dashboard
# Comment on issue with verification
```

### When Domain Reports Complete

```bash
# 1. Verify completion in tmux session
tmux capture-pane -t [Domain] -p | grep "Complete"

# 2. Check for PR
gh pr list --author [domain-user]

# 3. Review changes
gh pr view [PR-number]

# 4. Mark for integration testing
```

### When Domain Reports Blocked

```bash
# 1. Check tmux session for context
tmux capture-pane -t [Domain] -p | tail -100

# 2. Identify blocker type
# - Dependency on another domain?
# - Technical issue?
# - Missing information?

# 3. Coordinate resolution
# - If dependency: check provider domain status
# - If technical: escalate to user
# - If information: provide from docs
```

---

## 📋 PM Daily Workflow

### Start of Session (User types "START PM")

1. ✅ Verify tmux sessions active
2. ✅ Check network connectivity
3. ✅ Review open issues
4. ✅ Check git status
5. ✅ Scan all domain sessions
6. ✅ Report initial status to user

### During Active Work

**Every 15 minutes:**
- Quick tmux scan (30 seconds)
- Check for errors/completions
- Note any state changes

**Every 30 minutes:**
- Full status report to user
- Update GitHub issues
- Check for blockers

**On domain notification:**
- Immediate verification via tmux
- Coordinate with other domains if needed
- Update tracking

### End of Session (User types "EXIT")

1. Capture final state from all tmux sessions
2. Update all issue statuses
3. Document any blockers
4. Create handoff notes
5. Report summary to user

---

## 🎯 PM Success Metrics

**Good PM session:**
- ✅ All domains working independently
- ✅ No blocking dependencies unresolved
- ✅ Real-time visibility maintained
- ✅ User only monitors (minimal intervention)
- ✅ Progress updates every 30 min
- ✅ Issues/PRs tracked accurately

**PM value-add:**
- Early error detection via tmux monitoring
- Faster coordination (no waiting for issue updates)
- Accurate progress tracking
- Proactive blocker resolution
- Integration readiness awareness

---

## 📞 User Commands for PM

```bash
# General status
"PM, what's the overall status?"

# Domain-specific
"PM, what's Ground-Side doing right now?"
"PM, check Air-Side for errors"
"PM, is SystemTools ready for integration?"

# Coordination
"PM, coordinate Ground-Side and Air-Side integration"
"PM, prepare for integration testing"

# Reporting
"PM, give me a detailed status report"
"PM, what blockers exist?"
```

---

**Last Updated:** 2025-11-21
