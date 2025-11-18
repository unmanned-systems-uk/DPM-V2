# Priority 1 Implementation Roadmap - SystemTools + Air-Side

**Date:** 2025-11-15
**Goal:** Build comprehensive SystemTools management system to fully test Air-Side functionality
**Workflow:** Air-Side implementation → SystemTools implementation → Test → THEN Ground-Side

---

## Phase 1A: Foundation - Create DPM Management System

### Task 1.A.1: Create DPM_Management_System.py
**Domain:** SystemTools
**Status:** ⏳ TODO
**Effort:** 1-2 hours

**Actions:**
- [ ] Copy log_viewer_gui.py → DPM_Management_System.py
- [ ] Keep existing log aggregation functionality
- [ ] Prepare for additions: config management, on-demand logging

**Deliverable:** New file that maintains current log viewing + space for new features

---

## Phase 1B: Configuration Management - Air-Side ↔ SystemTools

### Current Status:
- ✅ Air-Side: ConfigManager (internal) - loads from JSON files
- ❌ Air-Side: TCP handlers for get_config/set_config
- ❌ SystemTools: TCP client to send config commands
- ✅ Ground-Side: Sends get_config (but Air-Side doesn't respond)

### Task 1.B.1: Air-Side - Implement get_config TCP Command
**Domain:** Air-Side
**Status:** ⏳ TODO
**Effort:** 2-3 hours
**Blockers:** None

**Requirements:**
- Implement TCP handler: `config.get_config`
- Return ALL config from ConfigManager (entire default.json merged with development.json)
- Response format:
```json
{
  "seq_id": 123,
  "status": "success",
  "command": "config.get_config",
  "result": {
    "config": {
      "network": {...},
      "logging": {...},
      "health": {...},
      "camera": {...},
      "timing": {...},
      "sync": {...},
      "buffers": {...},
      "protocol": {...}
    }
  }
}
```

**Files to modify:**
- `sbc/src/protocol/tcp_server.cpp` - Add handler
- `sbc/src/config/config_manager.h` - Add `getAllConfig()` method
- `sbc/src/config/config_manager.cpp` - Implement serialization to JSON

**Success criteria:**
- [ ] TCP command handler responds
- [ ] Returns valid JSON with all config values
- [ ] No crashes or errors

---

### Task 1.B.2: Air-Side - Implement set_config TCP Command
**Domain:** Air-Side
**Status:** ⏳ TODO
**Effort:** 3-4 hours
**Blockers:** Task 1.B.1 complete

**Requirements:**
- Implement TCP handler: `config.set_config`
- Accept partial or full config updates
- Validate values before applying
- Runtime updates (development.json behavior)
- Special command for persistence (write to default.json) - ONLY from SystemTools

**Request format:**
```json
{
  "seq_id": 124,
  "command": "config.set_config",
  "payload": {
    "parameters": {
      "config": {
        "logging": {
          "level": "DEBUG",
          "network_systemtools_enabled": true
        }
      },
      "persist": false  // true = write to default.json (SystemTools only)
    }
  }
}
```

**Response format:**
```json
{
  "seq_id": 124,
  "status": "success",
  "command": "config.set_config",
  "result": {
    "updated_values": ["logging.level", "logging.network_systemtools_enabled"],
    "persisted": false
  }
}
```

**Files to modify:**
- `sbc/src/protocol/tcp_server.cpp` - Add handler
- `sbc/src/config/config_manager.h` - Add `setConfig()`, `persistConfig()` methods
- `sbc/src/config/config_manager.cpp` - Implement updates and persistence

**Security:**
- Validate all values before applying
- Reject invalid ranges (e.g., ports outside 1024-65535)
- Log all config changes
- Persist flag ONLY allowed from SystemTools IP (not Ground-Side)

**Success criteria:**
- [ ] Can update individual config values at runtime
- [ ] Can update nested config values
- [ ] Validation rejects invalid values
- [ ] Persist flag writes to default.json
- [ ] Changes apply immediately to running system

---

### Task 1.B.3: SystemTools - Implement Config Management UI
**Domain:** SystemTools
**Status:** ⏳ TODO
**Effort:** 4-6 hours
**Blockers:** Task 1.B.1, 1.B.2 complete

**Requirements:**
- Add "Configuration" tab to DPM_Management_System.py
- TCP client to send get_config/set_config commands
- Tree view to display config hierarchy
- Edit fields for all values
- "Get Config" button - fetch from Air-Side
- "Apply" button - send updates to Air-Side (runtime)
- "Save to Default" button - persist to default.json

**UI Layout:**
```
┌─ Configuration Tab ──────────────────────┐
│ [Air-Side] [Ground-Side]                 │
│                                           │
│ Network Configuration                     │
│  ├─ tcp_port:        [5000      ] [Edit] │
│  ├─ udp_status_port: [5001      ] [Edit] │
│  └─ ground_ip:       [192.168...] [Edit] │
│                                           │
│ Logging Configuration                     │
│  ├─ level:           [INFO ▼   ] [Edit]  │
│  ├─ file_enabled:    [✓]                 │
│  └─ network_systemtools_enabled: [✓]     │
│                                           │
│ [Get Config] [Apply Changes] [Save to Default] │
│                                           │
│ Status: Connected to Air-Side 10.0.1.53  │
└───────────────────────────────────────────┘
```

**Implementation:**
- Use tkinter TreeView or similar for config display
- Validate inputs before sending
- Show success/error messages
- Persist SystemTools → Air-Side TCP connection

**Success criteria:**
- [ ] Can fetch config from Air-Side
- [ ] Can edit and apply runtime changes
- [ ] Can persist changes to default.json
- [ ] Validation prevents invalid inputs
- [ ] Clear status messages

---

## Phase 1C: On-Demand Logging - Air-Side ↔ SystemTools

### Current Status:
- ✅ Air-Side: `logging.enable_streaming` command implemented
- ❌ SystemTools: Cannot send TCP command to request logs
- ✅ SystemTools: Receives passive UDP logs (always-on mode)

### Task 1.C.1: SystemTools - Implement On-Demand Log Request
**Domain:** SystemTools
**Status:** ⏳ TODO
**Effort:** 3-4 hours
**Blockers:** None

**Requirements:**
- Add "On-Demand Logs" section to DPM_Management_System.py
- TCP client to send `logging.enable_streaming` command
- Duration input field (1-3600 seconds)
- Start/Stop buttons
- Display countdown timer
- Listen for UDP logs on port 5007 (already working)

**UI Addition:**
```
┌─ On-Demand Logging ──────────────────────┐
│ Air-Side Logs                             │
│ Duration: [600] seconds                   │
│ [Request Logs] [Stop Streaming]           │
│                                           │
│ Status: Streaming (240 seconds remaining) │
│                                           │
│ Ground-Side Logs                          │
│ Duration: [600] seconds                   │
│ [Request Logs] [Stop Streaming]           │
│                                           │
│ Status: Not streaming                     │
└───────────────────────────────────────────┘
```

**TCP Command to Air-Side:**
```json
{
  "seq_id": 200,
  "command": "logging.enable_streaming",
  "payload": {
    "parameters": {
      "duration_sec": 600
    }
  }
}
```

**Implementation:**
- Send TCP command when user clicks "Request Logs"
- Start countdown timer
- UDP listener already receives logs (no changes needed)
- Auto-stop after duration
- Manual stop via `logging.disable_streaming` command

**Success criteria:**
- [ ] Can request logs via TCP command
- [ ] Receives UDP logs after request
- [ ] Countdown timer works
- [ ] Auto-stops after duration
- [ ] Manual stop works

---

### Task 1.C.2: SystemTools - Implement Ground-Side On-Demand Logging
**Domain:** SystemTools
**Status:** ⏳ TODO
**Effort:** 2-3 hours
**Blockers:** Ground-Side implements TCP command handler

**Requirements:**
- Same as Task 1.C.1, but for Ground-Side
- Send TCP command to H16 to request logs
- H16 streams logs via TCP or UDP (TBD based on Ground-Side implementation)

**Note:** This depends on Ground-Side implementing the command handler first (Priority 2)

---

## Phase 1D: Health Monitoring Validation

### Task 1.D.1: Verify Health Broadcasts Working
**Domain:** PM Coordination
**Status:** ⏳ TODO
**Effort:** 1 hour

**Actions:**
- [ ] Check if Air-Side is broadcasting health on UDP
- [ ] Check if Ground-Side is receiving health broadcasts
- [ ] Document any gaps

**Success criteria:**
- [ ] Health broadcasts confirmed working OR gaps identified for fixing

---

## Phase 1E: Integration Testing

### Test Suite 1: SystemTools ↔ Air-Side Config Management
**Prerequisites:** Tasks 1.B.1, 1.B.2, 1.B.3 complete

**Test cases:**
1. Fetch config from Air-Side via SystemTools
2. Modify logging level (INFO → DEBUG) and apply
3. Verify Air-Side logs reflect DEBUG level
4. Modify network port and apply
5. Persist changes to default.json
6. Restart Air-Side and verify changes persist
7. Test validation (invalid port, out of range values)

**Success criteria:** All test cases pass

---

### Test Suite 2: SystemTools On-Demand Logs
**Prerequisites:** Task 1.C.1 complete

**Test cases:**
1. Request Air-Side logs for 60 seconds
2. Verify logs appear in SystemTools UI
3. Verify auto-stop after 60 seconds
4. Request logs again with different duration
5. Test manual stop before timeout
6. Test simultaneous on-demand + passive logging

**Success criteria:** All test cases pass

---

## Priority 1 Deliverables

**When Phase 1 is complete:**
- ✅ DPM_Management_System.py fully functional
- ✅ SystemTools can read ALL Air-Side config
- ✅ SystemTools can update Air-Side config (runtime + persist)
- ✅ SystemTools can request Air-Side logs on-demand
- ✅ SystemTools can test ALL Air-Side functionality from PC
- ✅ Integration tests passing

**Then proceed to:** Priority 2 - Migrate to Ground-Side (H16)

---

## Child Issues to Create

1. **[AIR-SIDE]** Implement config.get_config TCP command
2. **[AIR-SIDE]** Implement config.set_config TCP command
3. **[SYSTEMTOOLS]** Create DPM_Management_System.py from log_viewer_gui.py
4. **[SYSTEMTOOLS]** Implement Configuration Management UI
5. **[SYSTEMTOOLS]** Implement On-Demand Logging UI (Air-Side)
6. **[PM]** Integration test suite - Config Management
7. **[PM]** Integration test suite - On-Demand Logging

---

**PM will create these issues and coordinate implementation in priority order.**
