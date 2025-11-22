# PM Next Session Instructions - 2025-11-19

**URGENT: Read this file on session startup**

---

## Session Context

**Previous Session:** 2025-11-18 (Full day - Protocol compliance cleanup)
**Status:** All code committed ✅, Testing pending ⏳
**Read First:** `PM_EOD_2025-11-18.md` (comprehensive summary)

---

## CRITICAL: Pending Work

### 1. Air-Side Container Rebuild Required 🔴

**Why:** Code changes in commit `07ef754` not active in running container
- Fixed: 12 log context violations
- Implemented: `system.get_config` handler
- Implemented: `system.update_config` handler

**Commands:**
```bash
ssh dpm@10.0.1.53
cd /home/dpm/DPM-V2/sbc
git pull origin main
./rebuild.sh
```

⏱️ **Duration:** ~5-10 minutes

**Status Check:**
- Ask user: "Has Air-Side container been rebuilt?"
- If NO: "Air-Side rebuild required before testing. Please run rebuild commands."
- If YES: Proceed to testing

---

### 2. Testing Required ⏳

**From SystemTools DPM Management System:**

#### Test 1: system.get_config (Issue #115)
1. Open SystemTools → Air-Side Config tab
2. Click "📥 Get Config (from Air-Side)"
3. **Expected:** UI populates with config sections (not 0 sections!)
4. **Check logs:** `air-side.jsonl` should show `[COMMAND] Executing system.get_config`

**If Pass:** ✅ Issue #115 ready to close
**If Fail:** ❌ Debug and fix

#### Test 2: system.update_config (Issue #116)
1. Modify config values in SystemTools UI
2. Click "💾 Update Config (to Air-Side)"
3. **Expected:** Success message with updated fields
4. **Verify:** Changes persist in `sbc/config/local.json`
5. **Check logs:** `[COMMAND] Executing system.update_config`, `[COMMAND] Configuration updated: X succeeded`

**If Pass:** ✅ Issue #116 ready to close
**If Fail:** ❌ Debug and fix

---

### 3. Close Issues After Verification ✅

**Only after BOTH tests pass:**

```bash
gh issue close 115 -c "✅ Tested and verified working. Config data populates SystemTools UI correctly. Air-Side logs show [COMMAND] context (protocol-compliant)."

gh issue close 116 -c "✅ Tested and verified working. Config updates persist to local.json and return proper response format per protocol specification."
```

**RULE 3 Reminder:** Issues were updated with commit hash BEFORE closing (already done ✅)

---

## Verification Checklist

Use this checklist when starting session:

- [ ] Read `PM_EOD_2025-11-18.md` (full context)
- [ ] Read `PROTOCOL_COMPLIANCE_AUDIT.md` (understand violations fixed)
- [ ] Check: Has Air-Side container been rebuilt?
- [ ] Check: Are Issues #115, #116 still open? (should be YES)
- [ ] Coordinate: Air-Side rebuild if not done
- [ ] Test: system.get_config from SystemTools
- [ ] Test: system.update_config from SystemTools
- [ ] Verify: Logs show `[COMMAND]` context (not `[NETWORK]`)
- [ ] Close: Issues #115, #116 after verification
- [ ] Check: Any other pending work from EOD summary

---

## Quick Reference: What Was Fixed Yesterday

1. **Log Context Violations** ✅
   - 12 instances: `LogContext::NETWORK` → `LogContext::COMMAND`
   - File: `sbc/src/protocol/tcp_server.cpp`
   - User observation resolved: "Processing command shows [NETWORK]"

2. **system.get_config** ✅ (Issue #115)
   - Handler implemented: `handleSystemGetConfig()` lines 874-900
   - Uses `ConfigManager::exportConfig()`
   - Protocol-compliant response format

3. **system.update_config** ✅ (Issue #116)
   - Handler implemented: `handleSystemUpdateConfig()` lines 902-987
   - Persists to `local.json`
   - Detects restart requirements

**Commit:** `07ef754` (pushed to origin/main)

---

## Session Startup Flow

```
1. New PM session starts
   ↓
2. PM reads this file (PM_NEXT_SESSION_2025-11-19.md)
   ↓
3. PM asks user: "Has Air-Side container been rebuilt?"
   ↓
   If NO → Provide rebuild instructions
   If YES → Continue
   ↓
4. PM coordinates testing from SystemTools
   ↓
5. User tests system.get_config (Issue #115)
   ↓
6. User tests system.update_config (Issue #116)
   ↓
7. PM closes issues after verification
   ↓
8. PM checks for other pending work
   ↓
9. Session continues with normal work
```

---

## Important Context Files

**Must Read:**
- `PM_EOD_2025-11-18.md` - Comprehensive summary of yesterday's work
- `PROTOCOL_COMPLIANCE_AUDIT.md` - Detailed violation analysis
- `LESSONS_LEARNED_CRITICAL.md` - 5 mandatory rules established

**Reference:**
- `protocol/commands.json` - System.get_config/update_config specs
- `protocol/log_contexts.json` - NETWORK vs COMMAND definitions

---

## What NOT To Do

❌ **Don't assume testing is complete** - Check with user
❌ **Don't close issues without testing** - RULE 3 enforcement
❌ **Don't start new work before verifying fixes** - Pending work first
❌ **Don't forget to check Air-Side rebuild status** - Critical for testing

---

## User Communication

**Opening Message Template:**

```
Good morning! Continuing from yesterday's protocol compliance session.

**Status Check:**
- Has Air-Side container been rebuilt? (git pull + ./rebuild.sh on Pi 5)
- Are you ready to test system.get_config and system.update_config from SystemTools?

**Pending Work:**
1. Test Issue #115 (system.get_config)
2. Test Issue #116 (system.update_config)
3. Close both issues after verification

**Yesterday's Summary:** PM_EOD_2025-11-18.md
- Fixed 12 log context violations
- Implemented both config commands
- All code committed and pushed ✅

Ready to proceed with testing?
```

---

## Success Criteria

**Session complete when:**
- ✅ Air-Side container rebuilt with new code
- ✅ system.get_config tested and working
- ✅ system.update_config tested and working
- ✅ Logs show `[COMMAND]` context (protocol-compliant)
- ✅ Issues #115, #116 closed with verification comment
- ✅ No other pending work from EOD summary

---

**File Status:** Active for 2025-11-19 session
**Auto-Delete:** After issues #115, #116 closed
**Supersedes:** None (first next-session file)

---

**Generated:** 2025-11-18 EOD
**For Session:** 2025-11-19 (next morning)
**Priority:** 🔴 CRITICAL - Read on startup
