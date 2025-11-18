# Phase 1 Functionality Audit - Before Creating Issues

**Date:** 2025-11-15
**Purpose:** Verify what exists before creating implementation issues
**PM Rule:** "For absolute thoroughness, check/confirm if functionality already available"

---

## Audit Results Summary

| Component | Functionality | Status | Notes |
|-----------|--------------|--------|-------|
| **Air-Side** | ConfigManager (internal) | ✅ EXISTS | Loads default.json, development.json |
| **Air-Side** | `system.get_config` TCP command | ❌ MISSING | Ground-Side expects this |
| **Air-Side** | `system.update_config` TCP command | ❌ MISSING | Ground-Side expects this |
| **Air-Side** | `logging.enable_streaming` TCP command | ✅ EXISTS | Tested and working |
| **Air-Side** | `logging.disable_streaming` TCP command | ✅ EXISTS | Tested and working |
| **SystemTools** | TCP Client infrastructure | ✅ EXISTS | TCPClient class + protocol.py |
| **SystemTools** | Config Management UI | ❌ MISSING | No UI to send get_config/set_config |
| **SystemTools** | On-Demand Logging UI | ❌ MISSING | No UI to send logging.enable_streaming |
| **SystemTools** | log_viewer_gui.py | ✅ EXISTS | 600 lines, passive log display only |
| **Ground-Side** | Sends `get_config` TCP command | ✅ EXISTS | AdvancedSettingsViewModel.kt:73 |
| **Ground-Side** | Expects Air-Side response | ✅ READY | Falls back with warning when Air-Side doesn't respond |

---

## Detailed Audit

### Air-Side TCP Commands - Complete List

**File:** `sbc/src/protocol/tcp_server.cpp` + `protocol/commands.json`

| Command | Status | Handler Function | Tested |
|---------|--------|-----------------|--------|
| `handshake` | ✅ Implemented | `handleHandshake()` | Yes |
| `system.get_status` | ✅ Implemented | `handleGetStatus()` | Yes |
| `camera.capture` | ✅ Implemented | `handleCapture()` | Yes |
| `camera.focus` | ✅ Implemented | `handleFocus()` | Yes |
| `camera.auto_focus_hold` | ✅ Implemented | `handleAutoFocusHold()` | Yes |
| `camera.set_property` | ✅ Implemented | `handleSetProperty()` | Yes |
| `camera.get_properties` | ✅ Implemented | `handleGetProperties()` | Yes |
| `logging.enable_streaming` | ✅ Implemented | `handleEnableLogStreaming()` | Yes |
| `logging.disable_streaming` | ✅ Implemented | `handleDisableLogStreaming()` | Yes |
| `health.get_snapshot` | ✅ Implemented | `handleGetHealthSnapshot()` | Yes |
| **`system.get_config`** | ❌ **NOT IMPLEMENTED** | ❌ Missing | No |
| **`system.update_config`** | ❌ **NOT IMPLEMENTED** | ❌ Missing | No |

**Air-Side Gap Analysis:**
- ConfigManager class exists and works internally ✅
- Can read config values via `CONFIG_INT()`, `CONFIG_STRING()` macros ✅
- **BUT:** No TCP command handlers to expose config externally ❌
- **Impact:** Ground-Side cannot read/update Air-Side config remotely

---

### SystemTools Infrastructure - Existing Capabilities

**TCP Client:** `SystemTools/network/tcp_client.py`
```python
class TCPClient:
    def connect(self) -> bool
    def send_command(self, command: str, parameters: Dict[str, Any]) -> bool
    def disconnect(self)
```
- ✅ Can connect to Air-Side TCP server
- ✅ Can send any command with parameters
- ✅ Receives responses in queue
- ✅ Threading support for async operations

**Protocol:** `SystemTools/network/protocol.py`
```python
class ProtocolMessage:
    def create_command(self, command: str, parameters: Dict[str, Any]) -> str
    def create_handshake() -> str
    def create_heartbeat() -> str
```
- ✅ Creates properly formatted DPM protocol messages
- ✅ Parses responses
- ✅ Handles sequence IDs automatically

**Existing UI:** `SystemTools/log_viewer_gui.py` (600 lines)
- ✅ Log aggregation from Air-Side (UDP 5007) and Ground-Side (TCP 5008)
- ✅ Filtering by domain, level, category
- ✅ Search functionality
- ✅ Export to file
- ❌ **NO** TCP command sending UI
- ❌ **NO** config management UI
- ❌ **NO** on-demand logging request UI

**Conclusion:** Infrastructure ready, UI components missing

---

### Ground-Side - What Already Works

**Config Request:** `android/.../ui/settings/AdvancedSettingsViewModel.kt`
```kotlin
// Line 73
val result = NetworkManager.sendCommand("get_config", emptyMap())

// Fallback when Air-Side doesn't respond:
Log.w(TAG, "Air-Side does not support get_config command, using default config")
```

**Status:**
- ✅ Ground-Side sends `get_config` command
- ✅ Expects Air-Side to respond with config JSON
- ✅ Has fallback behavior (uses default config)
- ⚠️ Currently always falls back because Air-Side doesn't have handler

**Logging Request:** User claims "Already implemented!!!"
- Need to verify if Ground-Side can send `logging.enable_streaming` to Air-Side
- Need to verify if Ground-Side has UDP listener for Air-Side logs (port 5005)

---

## Issues to Create

Based on audit results, PM needs to create these issues:

### Issue 1: [AIR-SIDE] Implement system.get_config TCP Command
**Status:** ❌ Confirmed MISSING
**Priority:** 🔴 Critical (Priority 1)
**Blockers:** None - ConfigManager already exists
**Effort:** 2-3 hours

**Requirements:**
- Add TCP handler: `handleGetConfig()`
- Return all config from ConfigManager
- Format as JSON response
- Add to protocol/commands.json

**Files to modify:**
- `sbc/src/protocol/tcp_server.cpp`
- `sbc/src/config/config_manager.h` (add `getAllConfig()` method)
- `sbc/src/config/config_manager.cpp`
- `sbc/protocol/commands.json`

---

### Issue 2: [AIR-SIDE] Implement system.update_config TCP Command
**Status:** ❌ Confirmed MISSING
**Priority:** 🔴 Critical (Priority 1)
**Blockers:** Issue 1 complete (uses same ConfigManager methods)
**Effort:** 3-4 hours

**Requirements:**
- Add TCP handler: `handleUpdateConfig()`
- Accept partial or full config updates
- Validate values before applying
- Runtime updates only (unless persist flag set)
- Persist flag ONLY from SystemTools IP (security)
- Log all config changes

**Files to modify:**
- `sbc/src/protocol/tcp_server.cpp`
- `sbc/src/config/config_manager.h` (add `setConfig()`, `persistConfig()` methods)
- `sbc/src/config/config_manager.cpp`
- `sbc/protocol/commands.json`

---

### Issue 3: [SYSTEMTOOLS] Create DPM_Management_System.py
**Status:** ❌ Confirmed MISSING
**Priority:** 🔴 Critical (Priority 1)
**Blockers:** None
**Effort:** 1-2 hours

**Requirements:**
- Copy `log_viewer_gui.py` → `DPM_Management_System.py`
- Keep existing log aggregation functionality
- Add infrastructure for new tabs/features
- Prepare for config management and on-demand logging

**Deliverable:**
- New file maintaining current functionality
- Ready to extend with new features

---

### Issue 4: [SYSTEMTOOLS] Configuration Management UI
**Status:** ❌ Confirmed MISSING
**Priority:** 🔴 Critical (Priority 1)
**Blockers:** Issue 1, 2, 3 complete
**Effort:** 4-6 hours

**Requirements:**
- Add "Configuration" tab to DPM_Management_System.py
- Use existing TCPClient to send commands
- Tree view for config hierarchy
- Edit fields with validation
- "Get Config" button (sends `system.get_config`)
- "Apply" button (sends `system.update_config` runtime)
- "Save to Default" button (sends with persist=true)

**Deliverable:**
- Full config management UI
- Can read/write all Air-Side config from PC

---

### Issue 5: [SYSTEMTOOLS] On-Demand Logging UI (Air-Side)
**Status:** ❌ Confirmed MISSING
**Priority:** 🔴 Critical (Priority 1)
**Blockers:** Issue 3 complete
**Effort:** 3-4 hours

**Requirements:**
- Add "On-Demand Logs" section to DPM_Management_System.py
- Use existing TCPClient to send `logging.enable_streaming`
- Duration input field
- Start/Stop buttons
- Countdown timer
- Display logs (already works via UDP 5007)

**Deliverable:**
- Can request Air-Side logs on demand
- Can control duration
- Can stop early

---

### Issue 6: [PM] Integration Test - Config Management
**Status:** ⏳ Waiting for Issues 1, 2, 4
**Priority:** 🔴 Critical (Priority 1)
**Effort:** 2-3 hours

**Test cases:**
1. Fetch config from Air-Side
2. Modify logging level and apply (runtime)
3. Verify Air-Side logs reflect change
4. Persist changes to default.json
5. Restart Air-Side, verify persistence
6. Test validation (invalid values)

---

### Issue 7: [PM] Integration Test - On-Demand Logging
**Status:** ⏳ Waiting for Issue 5
**Priority:** 🔴 Critical (Priority 1)
**Effort:** 1-2 hours

**Test cases:**
1. Request Air-Side logs for 60 seconds
2. Verify logs appear in SystemTools
3. Verify auto-stop after timeout
4. Test manual stop
5. Test simultaneous on-demand + passive logging

---

## Ground-Side Verification Needed

**User claim:** "Already implemented!!! We have on demand logging from Air-Side to Ground-Side"

**PM needs to verify:**
- [ ] Does Ground-Side send `logging.enable_streaming` TCP command?
- [ ] Does Ground-Side have UDP listener on port 5005?
- [ ] Does Ground-Side display Air-Side logs in UI?

**If YES:** Document as working, no issue needed
**If NO:** Create issue for Ground-Side implementation (Priority 2 per user)

---

## Next Steps

1. **PM creates 7 child issues** (listed above)
2. **Link all to Issue #114** (master tracking)
3. **Assign priority order:**
   - Phase 1A: Issue 3 (Create DPM_Management_System.py)
   - Phase 1B: Issues 1, 2 (Air-Side config commands)
   - Phase 1C: Issue 4 (SystemTools config UI)
   - Phase 1D: Issue 5 (SystemTools on-demand logging)
   - Phase 1E: Issues 6, 7 (Integration tests)

4. **Coordinate domain sessions:**
   - Air-Side: Issues 1, 2
   - SystemTools: Issues 3, 4, 5
   - PM: Issues 6, 7 (testing)

5. **Update Issue #114** with audit results and issue links

---

**Audit complete. Ready to create issues.**
