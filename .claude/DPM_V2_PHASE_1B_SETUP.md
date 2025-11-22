# DPM-V2 Phase 1B Setup Instructions
**Issue #153: AI Agent Persistent Memory System**
**Date:** 2025-11-20
**Status:** Ready for DPM-V2 PM

---

## What This Is

Phase 1B of Issue #153 has been deployed to CCPM and is now available for DPM-V2.

**Purpose:** Auto-inject DPM-V2 capabilities into SESSION_START.md at session start, so PM doesn't forget what already exists.

**Expected Impact:** Reduce PM forgetting rate from 75% → 40%

---

## DPM-V2 Project Registration

✅ **DPM-V2 is now registered in CCPM database as Project ID 2**

```sql
Project ID: 2
Name: DPM-V2
Description: Drone Payload Management V2 - Multi-platform drone payload system
GitHub: unmanned-systems-uk/dpm-v2
```

---

## How to Use Phase 1B for DPM-V2

### Step 1: Register DPM-V2 Capabilities

**Current State:** No capabilities registered yet.

**Register capabilities as you build:**

```bash
# From DPM-V2 workspace
python3 ~/ccpm-workspace/production/ccpm-client/python/register_capability.py \
    --project-id 2 \
    --name "UDP Health Broadcast Handler" \
    --category networking \
    --description "Air-Side UDP health broadcast to Ground-Side" \
    --implementation-file "sbc/src/health_monitor.cpp" \
    --status production

# Register more capabilities
python3 ~/ccpm-workspace/production/ccpm-client/python/register_capability.py \
    --project-id 2 \
    --name "ADB Bridge Communication" \
    --category integration \
    --description "Python bridge for ADB communication with Ground-Side" \
    --implementation-file "SystemTools/adb_bridge.py" \
    --status production
```

**Key DPM-V2 Capabilities to Register:**

**Air-Side (Pi 5 - C++):**
- UDP Health Broadcast Handler
- Payload State Manager
- Camera Control Module
- Sensor Data Acquisition
- Power Management System

**Ground-Side (Android H16):**
- UDP Health Receiver
- ADB Command Interface
- Mission Control UI
- Data Storage Manager
- Network Configuration

**SystemTools (Python):**
- Log Aggregator
- ADB Bridge
- Performance Monitor
- Configuration Manager
- Test Automation Tools

---

### Step 2: Add AUTO-GENERATED CAPABILITIES Marker

**Edit DPM-V2's SESSION_START.md** (`/home/anthony/DPM-V2/.claude/SESSION_START.md`):

Add this section before the FINAL CHECKPOINT section:

```markdown
---

<!-- AUTO-GENERATED CAPABILITIES -->

**No capabilities loaded.** Run session init script:
```bash
~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh 2
```

---

## 📋 FINAL CHECKPOINT
...
```

**Why Important:** This marker tells inject-pm-context.sh where to inject capabilities.

---

### Step 3: Run Session Initialization Before PM Sessions

**Before starting DPM-V2 PM work:**

```bash
# Initialize DPM-V2 PM session (Project ID 2)
~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh 2

# Output:
# ═══════════════════════════════════════════════════════════
#   PM Session Initialization (Issue #153 Phase 1B)
# ═══════════════════════════════════════════════════════════
#
# Step 1/2: Injecting capability context...
# Generating PM capabilities context for Project 2...
# ✅ PM context updated successfully!
#    Capabilities injected: [number]
#    ...
#
# Step 2/2: Session tracking ready
#    Session ID: pm-session-20251120-HHMMSS
#
# ✅ PM session initialized successfully!
# ═══════════════════════════════════════════════════════════
```

---

### Step 4: PM Session Workflow

**When PM starts:**
1. PM reads `/home/anthony/DPM-V2/.claude/SESSION_START.md`
2. PM sees auto-generated capabilities list
3. PM knows what exists BEFORE planning new work

**When user asks PM to implement something:**
- PM checks capabilities list first
- If exists: PM says "We already have XYZ in [file]"
- If missing: PM implements without duplication

**When PM forgets anyway:**
- User corrects: "We already have XYZ"
- Log the correction:
  ```bash
  python3 ~/ccpm-workspace/production/ccpm-client/python/log_pm_correction.py
  ```
- Track improvement over time

---

## Automation Options

### Option 1: Manual (Simple)

**Before each DPM-V2 PM session:**
```bash
~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh 2
```

### Option 2: Auto-run on tmux session start

**Add to DPM-V2 tmux session script:**
```bash
# In ~/.tmux/dpm-v2-session.sh or similar
~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh 2 --quiet
```

### Option 3: Add to DPM-V2 .bashrc check

**Add to ~/.bashrc:**
```bash
# Auto-initialize DPM-V2 PM session
if [[ "$PWD" == "/home/anthony/DPM-V2" ]] && [[ "$TMUX_PANE" == "%0" ]]; then
    ~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh 2 --quiet 2>/dev/null || true
fi
```

---

## Verification

### Check Registered Capabilities

```bash
# Query all DPM-V2 capabilities
python3 ~/ccpm-workspace/production/ccpm-client/python/query_capability.py \
    --project-id 2

# Generate capability report
python3 ~/ccpm-workspace/production/ccpm-client/python/generate_pm_capabilities.py \
    --project-id 2 \
    --output /home/anthony/DPM-V2/.claude/DPM_V2_CAPABILITIES.md
```

### Check What PM Will See

```bash
# View capabilities section in SESSION_START.md
grep -A 30 "AUTO-GENERATED CAPABILITIES" /home/anthony/DPM-V2/.claude/SESSION_START.md
```

### Test with Real PM

1. Start fresh DPM-V2 PM session
2. Ask: "Do we have UDP health monitoring in DPM-V2?"
3. Expected: PM responds with capability details from SESSION_START.md
4. If PM forgets: Log correction and track improvement

---

## DPM-V2 Specific Notes

### Domain Structure

DPM-V2 has multiple domains:
- **Air-Side** (CC-Air-Side) - Pi 5, C++, sbc/
- **Ground-Side** (CC-Ground-Side) - Android H16, Kotlin/Java, android/
- **Dev-Tools** (CC-Dev-Tools) - Python, SystemTools/

**Register capabilities with domain in metadata:**

```bash
python3 register_capability.py \
    --project-id 2 \
    --name "UDP Health Broadcast" \
    --category networking \
    --metadata '{"domain": "air-side", "language": "cpp", "platform": "pi5"}'
```

### Multi-Platform Considerations

DPM-V2 capabilities span multiple platforms:
- **Air-Side:** Raspberry Pi 5 (ARM64, Linux)
- **Ground-Side:** Android H16 (ARM64, Android 12)
- **SystemTools:** Development PC (x86_64, Ubuntu 22.04)

**Tag platform in implementation_file:**
```
sbc/src/health_monitor.cpp (Air-Side)
android/app/.../HealthReceiver.kt (Ground-Side)
SystemTools/log_aggregator.py (Dev-Tools)
```

---

## Success Metrics for DPM-V2

### Phase 1B Goals

**Before Phase 1B:**
- PM forgetting rate: ~75%
- PM asks: "Does DPM-V2 have feature XYZ?"
- User reminds: "Yes, in sbc/src/xyz.cpp"

**After Phase 1B:**
- PM forgetting rate: ~40% (target)
- PM sees: Auto-generated capabilities at session start
- PM checks: Capabilities before planning duplicate work

**Measure Success:**
```bash
# Log corrections when PM forgets
python3 ~/ccpm-workspace/production/ccpm-client/python/log_pm_correction.py \
    --project-id 2

# Check forgetting rate over time
python3 ~/ccpm-workspace/production/ccpm-client/python/log_pm_correction.py --stats
```

---

## Next Steps

### Immediate (Before Next DPM-V2 PM Session)

1. ✅ DPM-V2 registered in database (Project ID 2)
2. ⏳ Add AUTO-GENERATED CAPABILITIES marker to SESSION_START.md
3. ⏳ Register initial DPM-V2 capabilities (5-10 key features)
4. ⏳ Test pm-session-init.sh with Project ID 2
5. ⏳ Update DPM-V2 SESSION_START.md with Issue #153 reference

### This Week (Phase 1 Completion)

6. Register all existing DPM-V2 capabilities (~20-30 total)
7. Run pm-session-init.sh before each PM session
8. Log PM corrections for 1 week baseline
9. Measure actual forgetting rate reduction

### Weeks 1-2 (Phase 2)

10. Deploy Project Agent specifically for DPM-V2
11. RAG-based context retrieval for large DPM-V2 codebase
12. Proactive suggestions for cross-domain capabilities
13. Measure 40% → 5% improvement

---

## Troubleshooting

### "No capabilities registered yet"

**Solution:** Register DPM-V2 capabilities first using register_capability.py

### "CCPM server not running"

**Solution:** Start CCPM server (needed for database access)
```bash
cd ~/ccpm-workspace/production/ccpm-server
./ccpm-server &
```

### "ERROR: SESSION_START.md marker not found"

**Solution:** Add `<!-- AUTO-GENERATED CAPABILITIES -->` marker to SESSION_START.md

---

## Related Documentation

**Primary Issue:**
- Issue #153 - AI Agent Persistent Memory System

**CCPM Documentation:**
- `~/ccpm-workspace/production/ccpm-server/scripts/README_PHASE_1B.md` - Complete Phase 1B guide
- `~/ccpm-workspace/production/docs/AGENT_ARCHITECTURE.md` - Full three-tier design
- `~/ccpm-workspace/production/docs/lessons-learned/ISSUE_153_META_LESSON.md` - Why this matters

**Scripts:**
- `~/ccpm-workspace/production/ccpm-client/python/register_capability.py` - Register capabilities
- `~/ccpm-workspace/production/ccpm-client/python/query_capability.py` - Query capabilities
- `~/ccpm-workspace/production/ccpm-client/python/generate_pm_capabilities.py` - Generate markdown
- `~/ccpm-workspace/production/ccpm-server/scripts/pm-session-init.sh` - Session initialization

---

**Last Updated:** 2025-11-20
**Author:** CCPM-Project-Developer
**Status:** Ready for DPM-V2 PM to Use
**Next:** Register DPM-V2 capabilities and test with real PM session
