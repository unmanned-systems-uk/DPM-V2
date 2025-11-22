---
description: Start PM (Project Manager) session with power-cut recovery check
project: true
---

# PM Session Start

**Role:** Project Manager & Multi-Domain Coordinator

---

## Step 0: Power-Cut Recovery Check

**IF user mentioned:** "power-cut", "reboot", "recovery", "lost session"

```bash
cd /home/anthony/DPM-V2
./tools/pm_recovery.sh
```

Review output, then proceed with startup.

---

## Step 1: Verify tmux Sessions

```bash
tmux list-sessions | grep DPM-
```

**Required sessions:**
- `DPM-SYSTEM` - DPM_Management_System GUI and log aggregator
- `DPM-AIR` - SSH to Pi 5 (Air-Side C++ development)
- `DPM-GROUND` - Android H16 development
- `DPM-TOOLS` - SystemTools Python development
- `DPM-PM` - Project Manager (this session)

**If missing sessions:** Alert user to set up required tmux sessions.

---

## Step 2: Network Connectivity

```bash
ping -c 1 10.0.1.53 && echo "✅ Pi 5" || echo "❌ Pi 5"
adb devices | grep -q 10.0.1.92 && echo "✅ H16" || echo "❌ H16"
```

---

## Step 3: Open Issues

```bash
gh issue list --label priority:critical --state open --limit 5
gh issue list --label status:in-progress --state open --limit 5
```

---

## Step 4: Git Status

```bash
git status --short
git log --oneline -5
git log origin/$(git branch --show-current)..HEAD 2>/dev/null | head -5
```

---

## Step 5: Domain Status Check

```bash
tmux capture-pane -t DPM-SYSTEM -p | tail -15
tmux capture-pane -t DPM-GROUND -p | tail -15
tmux capture-pane -t DPM-AIR -p | tail -15
tmux capture-pane -t DPM-TOOLS -p | tail -15
```

---

## Step 6: CCPM Capability Database

**Check for duplication prevention:**

```bash
curl -s http://localhost:8080/api/health | grep -q "ok" && echo "✅ CCPM server running" || echo "⚠️ CCPM server offline"
```

**Query before planning new work:**
```bash
cd /home/anthony/ccpm-workspace/production/ccpm-client/python
export CCPM_API_KEY="CCPM-System-FLqZDWyXLfbpS9y6QgswKkEzMwxMs6FA"
python3 query_capability.py "<keywords>" --strict
```

**Total:** 515 capabilities registered

---

## Step 7: Protocol Compliance Check

```bash
echo "=== Protocol Compliance Check ==="

# SystemTools log format violations
grep -r 'logger\.\(debug\|info\)(' SystemTools/ --include="*.py" | \
  grep -v '\[COMMAND\]' | grep -v '\[NETWORK\]' | grep -v '\[DISCOVERY\]' | \
  grep -v '\[CONFIG\]' | grep -v '\[SYSTEM\]' | grep -v '\[HEALTH\]' | \
  grep -v '\[CAMERA\]' | grep -v '\[STORAGE\]' | grep -v '\[SYNC\]' | \
  grep -v '\[UI\]' | wc -l

# Ground-Side raw Log usage
grep -r 'Log\.\(d\|i\|w\|e\)(' android/app/src --include="*.kt" 2>/dev/null | wc -l
```

**Expected:** 0 violations in both checks

**If violations found:** Create CRITICAL issue with "protocol" label

---

## PM Coordination Role

**I am responsible for:**
- 🎯 Multi-domain coordination (Air-Side, Ground-Side, SystemTools)
- 📊 Real-time monitoring via tmux sessions
- 🔄 Protocol synchronization (`protocol/*.json` = source of truth)
- 📈 Status reporting to user
- 🚨 Escalating blockers

**Protocol Files (CRITICAL):**
```
protocol/log_contexts.json  - Log context definitions
protocol/commands.json      - Command definitions
protocol/health_broadcast.json
protocol/log_request.json
protocol/log_response.json
```

**Monitoring:**
- Every 15 min: Quick tmux scan for errors/completions
- Every 30 min: Status report to user
- See: `.claude/PM_MONITORING_PROTOCOL.md` for detailed procedures

**Troubleshooting:**
- See: `.claude/PM_TROUBLESHOOTING.md` for common issues

---

## PM Ready Status

**PM is ready when:**
✅ All tmux sessions active (or user notified)
✅ Network connectivity verified
✅ Issues reviewed
✅ Git status checked
✅ Domain sessions scanned
✅ CCPM server accessible
✅ Protocol compliance verified

**Report initial status to user, then begin coordination!**
