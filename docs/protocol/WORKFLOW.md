# Protocol Synchronization Workflow
**Quick Reference Guide for User and Claude Code**

---

## 🎯 Purpose

This document explains the **commented-out method workflow** for keeping air-side (SBC) and ground-side (Android) protocol implementations synchronized.

---

## 📋 User Workflow

### Adding a New Command

**Step 1: Define in Protocol**
```bash
# Edit docs/protocol/commands.json
{
  "camera.new_command": {
    "description": "What this command does",
    "parameters": {
      "param1": { "type": "string", "required": true }
    },
    "response": { ... },
    "implemented": {
      "air_side": false,
      "ground_side": false,
      "version": "1.1.0"
    }
  }
}
```

**Step 2: Add Commented-Out Method to Android (Optional but Recommended)**
```kotlin
// In NetworkClient.kt

// Existing commands
fun captureImage() { ... }
fun getSystemStatus() { ... }

// NEW COMMAND - Commented out until ready
// fun newCommand(param1: String) {
//     val command = Command(
//         command = "camera.new_command",
//         parameters = mapOf("param1" to param1)
//     )
//     sendCommand(command)
// }
```

**Step 3: Let CC Know**
- Next session, CC will detect the commented method
- CC will ask what it does and when to implement it
- You can add multiple commands at once - CC will ask about priorities

---

## 🤖 Claude Code Workflow

### Every Session Start

**CC MUST run these checks:**

```bash
# 1. Check for unimplemented commands
cat docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.SIDE_side == false) | .key'
# (Replace SIDE with 'air' or 'ground')

# 2. For Android: Check for commented methods
grep -n "^\s*// fun " android/app/src/main/java/.../NetworkClient.kt

# 3. Check what the other side has implemented
cat docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.air_side == true and
         .value.implemented.ground_side == false) | .key'
```

**If anything found:**
1. List all findings to user
2. Ask what to implement and in what order
3. Verify other side is ready (for end-to-end testing)
4. Implement ONE command at a time
5. Update `commands.json` after each completion

---

## 🔄 Full Implementation Flow

### Example: Adding camera.focus Command

**Phase 1: Planning (User)**
```json
// User adds to commands.json
{
  "camera.focus": {
    "description": "Manual focus control",
    "parameters": {
      "action": {"type": "string", "enum": ["near", "far", "stop"]},
      "speed": {"type": "integer", "default": 3}
    },
    "implemented": {
      "air_side": false,
      "ground_side": false
    }
  }
}
```

```kotlin
// User adds commented method to NetworkClient.kt
// fun focusCamera(direction: String, speed: Int = 3) {
//     val command = Command(
//         command = "camera.focus",
//         parameters = mapOf("action" to direction, "speed" to speed)
//     )
//     sendCommand(command)
// }
```

**Phase 2: Air-Side Implementation (CC working on SBC)**
```
CC Session Start:
├─ Detects camera.focus in commands.json
├─ Sees "air_side": false
├─ Asks user: "Should I implement camera.focus?"
├─ User says: "Yes, use Sony SDK focus control"
│
├─ CC implements:
│   ├─ handleCameraFocus() in tcp_server.cpp
│   ├─ Sony SDK focus commands
│   └─ Error handling
│
├─ CC tests implementation
├─ CC updates commands.json: "air_side": true
└─ CC commits: [PROTOCOL] Implemented camera.focus
```

**Phase 3: Ground-Side Implementation (CC working on Android)**
```
CC Session Start:
├─ Detects commented focusCamera() method
├─ Checks commands.json: "air_side": true ✅
├─ Asks user: "Air-side ready. Implement focusCamera UI?"
├─ User says: "Yes, add buttons on camera control screen"
│
├─ CC implements:
│   ├─ Uncomments focusCamera() method
│   ├─ Adds ViewModel.focusCamera()
│   ├─ Adds UI buttons (Near/Far/Stop)
│   └─ Error handling
│
├─ CC tests end-to-end with air-side
├─ CC updates commands.json: "ground_side": true
└─ CC commits: [PROTOCOL] Implemented camera.focus UI
```

---

## ✅ Benefits of This Workflow

### Prevents Drift
- ❌ **Without this**: Android has methods that air-side doesn't handle
- ✅ **With this**: `commands.json` shows exactly what's implemented

### Clear Communication
- ❌ **Without this**: CC guesses what commands need
- ✅ **With this**: Commented methods are explicit TODOs

### Incremental Development
- ❌ **Without this**: Implement 10 commands, only test at end
- ✅ **With this**: Implement → Test → Commit → Repeat

### Easy Planning
- ❌ **Without this**: Lose track of planned features
- ✅ **With this**: Commented methods + JSON = full roadmap

---

## 🚀 Quick Reference

### For User

**Adding One Command:**
1. Update `commands.json`
2. Add commented method (optional)
3. Tell CC "implement camera.X"

**Adding Many Commands:**
1. Update `commands.json` with all
2. Add all as commented methods
3. CC will ask which to prioritize
4. CC implements one at a time

**Checking Status:**
```bash
# What's implemented?
cat docs/protocol/commands.json | jq '.commands | to_entries[] |
  select(.value.implemented.air_side == true and
         .value.implemented.ground_side == true) | .key'

# What's in progress?
cat docs/protocol/commands.json | jq '.commands | to_entries[] |
  select(.value.implemented.air_side != .value.implemented.ground_side) |
  {key: .key, status: .value.implemented}'
```

### For Claude Code

**Session Start Checklist:**
- [ ] Read CC_READ_THIS_FIRST.md
- [ ] Run protocol sync checks
- [ ] List unimplemented commands to user
- [ ] List commented methods to user
- [ ] Ask priorities before implementing
- [ ] Implement ONE command fully before next

**Never:**
- ❌ Implement without checking `commands.json`
- ❌ Uncomment all methods at once
- ❌ Skip asking user about priorities
- ❌ Mark complete without testing

---

## 📊 Example Session Output

```
CC: Starting session on air-side...

Checking protocol synchronization...

Commands in protocol not yet implemented here:
1. camera.focus (ground_side: false, air_side: false)
2. camera.set_property (ground_side: true, air_side: false) ⚠️
3. camera.get_properties (ground_side: false, air_side: false)

⚠️ WARNING: camera.set_property is implemented on ground-side but
not here! The Android app can send this command but I can't handle it.

Questions:
1. Which command should I implement first?
2. For camera.set_property - what Sony SDK calls should I use?
3. Should I implement them all, or start with high priority ones?

[Waits for user response...]
```

---

**Maintained by:** DPM Team
**Last Updated:** 2025-10-25
**Status:** Active Workflow
