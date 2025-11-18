# SystemTools Coordination Rules - CRITICAL

**Created:** 2025-11-18
**Reason:** Prevent duplicate app launches and coordination failures

---

## 🔴 CRITICAL RULE: Check SYSTEM Session First

**Problem:** SystemTools domain (TOOLS session) launching GUI apps without checking if already running in SYSTEM session

**Impact:** Duplicate apps, resource conflicts, user confusion

---

## MANDATORY Checks Before Launching GUI

### Rule 1: ALWAYS Check SYSTEM Session First

```bash
# Before launching ANY GUI application, check SYSTEM session:
tmux capture-pane -t SYSTEM -p | tail -50

# Look for:
- DPM_Management_System.py running → USE IT (don't launch duplicate)
- main.py running → WRONG APP (old version)
- No GUI running → OK to launch
```

### Rule 2: Use Correct Application

**Current Application:** `DPM_Management_System.py`
**Old Application:** `main.py` ❌ DO NOT USE

```bash
# CORRECT:
cd SystemTools && python3 DPM_Management_System.py

# WRONG:
cd SystemTools && python3 main.py  # OLD VERSION
```

### Rule 3: Coordinate with SYSTEM Session

**SYSTEM session is for:**
- Running GUI applications (DPM_Management_System.py)
- Running log aggregator
- Local system operations

**TOOLS session is for:**
- Development work (editing code)
- Testing (when GUI already running in SYSTEM)
- Automation scripts

**If GUI needed:**
1. Check SYSTEM session first
2. If running → Use tmux to interact or tell user to use GUI
3. If not running → Launch in SYSTEM session (not TOOLS)

---

## Examples

### ❌ WRONG - What SystemTools did today:

```bash
# In TOOLS session:
cd SystemTools && python3 main.py &  # WRONG APP + DUPLICATE
```

**Problems:**
1. Didn't check SYSTEM session first
2. Launched old app (main.py)
3. Created duplicate when DPM_Management_System.py already running

### ✅ CORRECT - What should happen:

```bash
# In TOOLS session:
# 1. Check SYSTEM session first
tmux capture-pane -t SYSTEM -p | tail -50

# 2. See DPM_Management_System.py is running
# 3. Tell user: "DPM_Management_System.py is already running in SYSTEM session.
#               Please use that window for GUI testing."

# OR if not running:
# 4. Send instruction to SYSTEM session to launch it
tmux send-keys -t SYSTEM "cd /home/anthony/DPM-V2/SystemTools && python3 DPM_Management_System.py" C-m
```

---

## Session Responsibilities

### SYSTEM Session
- **Purpose:** Run GUI applications and system services
- **Applications:** DPM_Management_System.py, log_aggregator.py
- **Access:** User interacts directly via GUI
- **Monitoring:** PM monitors via tmux capture-pane

### TOOLS Session (SystemTools Domain)
- **Purpose:** Development and code maintenance
- **Activities:** Edit code, run tests, automation scripts
- **GUI Testing:** Use existing GUI in SYSTEM session
- **Rule:** Never launch duplicate GUIs

---

## PM Coordination

**PM should:**
- Monitor both SYSTEM and TOOLS sessions
- Coordinate GUI testing between sessions
- Prevent duplicate launches
- Verify correct application is running

**PM Instructions to TOOLS:**
```
"Test system.get_config using the DPM_Management_System.py GUI
already running in SYSTEM session (check tmux SYSTEM for status)"
```

---

## Fixing This Issue Today

**Immediate Actions:**
1. Kill main.py in TOOLS session
2. Verify DPM_Management_System.py in SYSTEM session
3. Use SYSTEM session for GUI testing
4. Update TOOLS session to monitor, not launch

**Future Prevention:**
- Add this check to SESSION_START.md for TOOLS domain
- PM provides clearer instructions about session coordination
- Document in PM_START.md

---

## Related Files

- `.claude/PM_START.md` - PM session startup (updated with SYSTEM session)
- `.claude/SESSION_START.md` - General session rules
- `SystemTools/SYSTEMTOOLS_READINESS.md` - SystemTools documentation

---

**This rule prevents:**
- ❌ Duplicate application launches
- ❌ Wrong application versions running
- ❌ Resource conflicts
- ❌ User confusion about which app to use

**Remember:** SYSTEM session = GUI apps, TOOLS session = development/testing code
