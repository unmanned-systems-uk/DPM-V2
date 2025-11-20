# Project Manager Start Protocol
**WHO:** CC-PM (Project Manager)
**Purpose:** Multi-domain coordination with real-time visibility

---

## 🚀 PM START - Quick Checklist (2-5 minutes)

When user types **"START PM"**, execute this protocol:

### Step 0: Power-Cut Recovery Check (IF NEEDED)

**IF user mentions:** "power-cut", "reboot", "lost session", "recovery"

**THEN run recovery protocol FIRST:**

```bash
cd /home/anthony/DPM-V2
./tools/pm_recovery.sh
```

**This will:**
- ✅ Check system uptime (detect if reboot occurred)
- ✅ Verify network connectivity to all devices
- ✅ Check git repository status
- ✅ Read runtime status files (RUNTIME_STATUS.json)
- ✅ Check running services (Docker, ADB, log_aggregator)
- ✅ Review GitHub issues for last activity
- ✅ Detect uncommitted work
- ✅ Reconstruct PM state

**After recovery script completes:**
- Review output to understand system state
- Check recommendations section for next steps
- Proceed with normal PM start checklist

**Recovery Documentation:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md` (Power-Cut Recovery section)

---

### Step 1: Verify tmux Sessions (CRITICAL)

```bash
tmux list-sessions
```

**Required sessions:**
- ✅ **AIR** - SSH to Pi 5 (10.0.1.53) running Claude Code - Air-Side C++ development
- ✅ **GROUND** - Local Android H16 development session
- ✅ **TOOLS** - Local SystemTools Python development session
- ✅ **SYSTEM** - DPM_Management_System GUI and log aggregator (CRITICAL for local operations)
- ✅ **PM** - Project Manager coordination session (this session)

**Optional sessions:**
- **PYTHON** - Additional Python development/testing session

**If sessions missing:**
```markdown
⚠️ **PM REQUIRES TMUX SESSIONS FOR REAL-TIME MONITORING**

Please set up the following tmux sessions:

1. **SYSTEM** (CRITICAL - for local operations):
   ```bash
   tmux new-session -s SYSTEM
   cd /home/anthony/DPM-V2/SystemTools
   python3 DPM_Management_System.py
   ```

2. **AIR**:
   ```bash
   tmux new-session -s AIR
   ssh dpm@10.0.1.53
   cd ~/DPM-V2/sbc
   claude-code
   ```

3. **GROUND**:
   ```bash
   tmux new-session -s GROUND
   cd /home/anthony/DPM-V2/android
   claude-code
   ```

4. **TOOLS**:
   ```bash
   tmux new-session -s TOOLS
   cd /home/anthony/DPM-V2/SystemTools
   claude-code
   ```

5. **PM** (optional - for coordination):
   ```bash
   tmux new-session -s PM
   cd /home/anthony/DPM-V2
   claude-code
   ```

6. **PYTHON** (optional - for testing):
   ```bash
   tmux new-session -s PYTHON
   cd /home/anthony/DPM-V2
   python3
   ```

Once all required sessions (SYSTEM, AIR, GROUND, TOOLS) are active, type "START PM" again.
```

### Step 2: Verify Network Connectivity

```bash
# Check Pi 5 accessibility
ping -c 1 10.0.1.53

# Check H16 accessibility
adb devices | grep 10.0.1.92

# Check Jetson (future)
ping -c 1 10.0.1.113
```

### Step 3: Check Open Issues

```bash
# Critical issues
gh issue list --label priority:critical --state open

# In-progress issues
gh issue list --label status:in-progress --state open

# All open issues by domain
gh issue list --label air-side --state open
gh issue list --label ground-side --state open
gh issue list --label dev-tools --state open
```

### Step 4: Verify Git Status

```bash
# Current branch and changes
git status

# Recent commits
git log --oneline -5

# Check for unpushed commits
git log origin/$(git branch --show-current)..HEAD
```

### Step 5: Real-Time Domain Status Check

```bash
# SYSTEM session (local operations)
tmux capture-pane -t SYSTEM -p | tail -30

# Ground-Side progress
tmux capture-pane -t GROUND -p | tail -30

# Air-Side progress
tmux capture-pane -t AIR -p | tail -30

# SystemTools progress
tmux capture-pane -t TOOLS -p | tail -30
```

### Step 6: Capability Database Check (NEW - Duplication Prevention)

**IMPORTANT:** Query ccpm capability database BEFORE planning any new work to prevent duplicate implementations

```bash
# Check if ccpm server is running
curl -s http://localhost:8080/api/health | grep -q "ok" && echo "✅ CCPM server running" || echo "⚠️ CCPM server offline"

# Quick capability query examples:
cd /home/anthony/ccpm-workspace/production/ccpm-client/python

# Example: Check if feature exists before planning
export CCPM_API_KEY="CCPM-System-FLqZDWyXLfbpS9y6QgswKkEzMwxMs6FA"
python3 query_capability.py "Performance Analytics" --strict
# Exit code 1 = found = duplication warning
# Exit code 0 = not found = safe to implement

# View all networking capabilities
python3 query_capability.py "" --category networking
```

**When Planning New Work:**
1. ✅ **ALWAYS query capability database first** using `query_capability.py`
2. ✅ Use `--strict` mode to get exit code warning if capability exists
3. ✅ If found: Review existing implementation, extend instead of duplicating
4. ✅ If not found: Proceed with new implementation
5. ✅ After completing: Register new capability using `register_capability.py`

**Quick Reference:**
- Query script: `/home/anthony/ccpm-workspace/production/ccpm-client/python/query_capability.py`
- Register script: `/home/anthony/ccpm-workspace/production/ccpm-client/python/register_capability.py`
- Full guide: `/home/anthony/ccpm-workspace/production/ccpm-client/python/PM_WORKFLOW_GUIDE.md`
- Total capabilities: **515** (Air-Side: 150, Ground-Side: 120, SystemTools: 200, Cross-Domain: 45)

**Backfill Status:** ✅ COMPLETE (2025-11-20) - All DPM-V2 capabilities from day one registered

---

### Step 7: Protocol Compliance Check (CRITICAL - See PM RULE 11)

**IMPORTANT:** protocol/*.json files are SINGLE SOURCE OF TRUTH for cross-domain standards

```bash
echo "=== Protocol Compliance Check ==="

# 1. SystemTools log format compliance
echo "SystemTools log format violations:"
grep -r 'logger\.\(debug\|info\)(' SystemTools/ --include="*.py" | \
  grep -v '\[COMMAND\]' | grep -v '\[NETWORK\]' | grep -v '\[DISCOVERY\]' | \
  grep -v '\[CONFIG\]' | grep -v '\[SYSTEM\]' | grep -v '\[HEALTH\]' | \
  grep -v '\[CAMERA\]' | grep -v '\[STORAGE\]' | grep -v '\[SYNC\]' | \
  grep -v '\[UI\]' | wc -l
# Expected: 0 violations (after Issue #162 is fixed)

# 2. Air-Side LogContext enforcement (if accessible)
# ssh dpm@10.0.1.53 "grep -r 'LOG_' ~/DPM-V2/sbc/src | grep -v 'LogContext::' | wc -l"
# Expected: 0 violations

# 3. Ground-Side StructuredLogger usage
echo "Ground-Side raw Log usage (should use Timber/StructuredLogger):"
grep -r 'Log\.\(d\|i\|w\|e\)(' android/app/src --include="*.kt" 2>/dev/null | wc -l
# Expected: 0 (should use StructuredLogger)
```

**If violations found:**
- ✅ Create CRITICAL issue with "protocol" label
- ✅ Block Phase completion until compliance restored
- ✅ Delegate architectural fix (NOT manual edits)
- ✅ Reference PM RULE 11

**Protocol Files to Verify:**
- `protocol/log_contexts.json` - Log context definitions (8 contexts)
- `protocol/commands.json` - Command definitions
- All domains MUST enforce at runtime (no hardcoded values)

---

## 📊 PM Monitoring Loop (Every 15-30 Minutes)

### Quick Status Scan

```bash
# 1. Check all tmux sessions for activity
tmux capture-pane -t SYSTEM -p | tail -10
tmux capture-pane -t GROUND -p | tail -10
tmux capture-pane -t AIR -p | tail -10
tmux capture-pane -t TOOLS -p | tail -10

# 2. Check for errors
tmux capture-pane -t SYSTEM -p | grep -E "(ERROR|FAIL|✗)" | tail -5
tmux capture-pane -t GROUND -p | grep -E "(ERROR|FAIL|✗)" | tail -5
tmux capture-pane -t AIR -p | grep -E "(ERROR|FAIL|✗)" | tail -5

# 3. Check for completions
tmux capture-pane -t SYSTEM -p | grep -E "(✓|✅|Complete)" | tail -5
tmux capture-pane -t GROUND -p | grep -E "(✓|✅|Complete)" | tail -5
tmux capture-pane -t AIR -p | grep -E "(✓|✅|Complete)" | tail -5

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
tmux capture-pane -t GROUND -p | tail -50

# Check if Air-Side has errors
tmux capture-pane -t AIR -p | grep -B5 -A5 "ERROR"

# See SystemTools test results
tmux capture-pane -t TOOLS -p | grep -E "(PASS|FAIL|✓|✗)"

# Monitor Ground-Side compilation
tmux capture-pane -t GROUND -p | grep -E "(gradlew|Build|Compil)"

# Watch for Git activity
tmux capture-pane -t GROUND -p | grep -E "(git add|git commit|git push)"
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

## 🔧 Troubleshooting

### If tmux session not responding

```bash
# Check if session exists
tmux list-sessions

# Check if session frozen
tmux capture-pane -t [session] -p -S -1000

# Reconnect to session
tmux attach -t [session]
```

### If domain appears stuck

```bash
# Get full recent output
tmux capture-pane -t [Domain] -p -S -500 | tail -100

# Check for waiting prompts
tmux capture-pane -t [Domain] -p | grep -E "(\?|waiting|input|press)"

# Notify user for intervention
```

### If network connectivity lost

```bash
# Check Pi 5
ping 10.0.1.53

# Check H16
adb devices

# Reconnect if needed
ssh dpm@10.0.1.53
adb connect 10.0.1.92:5555
```

---

## 📁 Related Documentation

- `.claude/SESSION_START.md` - General session start
- `.claude/MULTI_DOMAIN_COORDINATION.md` - Coordination framework
- `.claude/CONNECTION_DETAILS.md` - Network/device details
- `.claude/PLATFORM_VERIFICATION.md` - Platform checks

---

**PM is ready when:**
✅ All required tmux sessions active (SYSTEM, AIR, GROUND, TOOLS)
✅ Network connectivity verified
✅ Issue status checked
✅ Git status clean
✅ Initial domain scan complete

**Type "START PM" to begin!**
