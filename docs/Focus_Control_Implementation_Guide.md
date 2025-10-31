# Focus Control Implementation - Phase 1: Manual Focus

**Feature:** Manual Camera Focus Control (Ground-Side UI + Air-Side Implementation)  
**Priority:** Phase 1 Core Feature  
**Status:** Not Started  
**Platform:** Both Air-Side (C++) and Ground-Side (Android)

---

## 📋 OVERVIEW

This task implements **manual focus control** for the Sony camera through the DPM payload manager. Focus is a complex feature with multiple modes and controls - Phase 1 focuses specifically on **manual focus operations only**.

### Phased Approach

- **Phase 1 (THIS TASK):** Manual Focus - 6-speed directional control + Auto-Focus Hold button
- **Phase 2:** Focus Magnifier (Focus Assist) - Visual aid for precise focusing
- **Phase 3:** Auto Focus Basic Modes - Standard AF modes (Single, Continuous)
- **Phase 4:** Auto Focus Advanced - Advanced AF features (tracking, eye AF, etc.)
- **Phase 5:** Touch Screen Object Picker - Touch-to-focus interface

---

## 🎯 PHASE 1 SCOPE: MANUAL FOCUS

### Controls Required

**6-Speed Directional Focus:**
- **Near Direction:** `<<<` (speed 3), `<<` (speed 2), `<` (speed 1)
- **Far Direction:** `>` (speed 1), `>>` (speed 2), `>>>` (speed 3)
- **Icons:** Person icon (near side) 👤 | Mountain icon (far side) 🏔️
- **Reference Image:** `~/docs/ManualFocus.jpg`

**Auto-Focus Hold Button:**
- **Function:** Temporary auto-focus override while in manual mode
- **Behavior:** 
  - **On Press:** Enable auto-focus temporarily
  - **On Release:** Return to manual focus
- **Purpose:** Focus helper - quickly acquire focus, then fine-tune manually

### Sony SDK Functions

**Primary Function (Manual Focus):**
```
CrDeviceProperty_Focus_Operation
```
*Note: Verify this is correct - may need adjustment during implementation*

**Auto-Focus Hold Function:**
```
CrDeviceProperty_AutoFocusHold
```

---

## 🏗️ ARCHITECTURE

### Ground-Side (Android UI)

**Location:** Advanced Camera Control → Manual Focus Tab

**UI Changes:**
1. **Move Manual Focus Tab Up:**
   - Currently may be in Sub Settings
   - **New Position:** Below Main Settings, above Sub Settings
   - Make more prominent for Phase 1 priority

2. **Add Manual Focus Controls:**
   - **6 Direction Buttons:** Near `<<<` `<<` `<` | `>` `>>` `>>>` Far (already in place)
   - **Icons:** Person 👤 (near) | Mountain 🏔️ (far)
   - **Auto-Focus Hold Button:** 
     - Icon from ManualFocus.jpg
     - Hold-to-focus behavior (not toggle)

3. **Mode-Based Display:**
   - **IF** `focus_mode == "manual"` → Show manual controls
   - **ELSE** → Replace tab content with auto-focus controls (Phase 3+)

### Air-Side (C++ Implementation)

**Command:** `camera.focus`

**Parameters:**
```json
{
  "action": "near" | "far" | "stop",
  "speed": 1 | 2 | 3
}
```

**Sony SDK Integration:**
- Map action/speed to `CrDeviceProperty_Focus_Operation` values
- Handle focus start/stop commands
- Implement Auto-Focus Hold via `CrDeviceProperty_AutoFocusHold`

---

## 📝 IMPLEMENTATION TASKS

### Air-Side Tasks (C++)

- [ ] **Research Sony SDK Focus Functions:**
  - [ ] Review `CrDeviceProperty_Focus_Operation` in SDK docs
  - [ ] Review `CrDeviceProperty_AutoFocusHold` in SDK docs
  - [ ] Verify enumeration values for near/far/stop
  - [ ] Verify speed parameter mapping (1-3)
  - [ ] Check if focus mode must be set to manual first

- [ ] **Implement `camera.focus` Command:**
  - [ ] Add command handler in `tcp_server.cpp`
  - [ ] Parse `action` and `speed` parameters
  - [ ] Map to Sony SDK property values
  - [ ] Call `SDK::SetDeviceProperty(CrDeviceProperty_Focus_Operation, value)`
  - [ ] Add error handling for invalid parameters
  - [ ] Add error handling for camera not in manual mode

- [ ] **Implement Auto-Focus Hold:**
  - [ ] Add `camera.auto_focus_hold` command
  - [ ] Parse `enable` parameter (true/false)
  - [ ] Call `SDK::SetDeviceProperty(CrDeviceProperty_AutoFocusHold, value)`
  - [ ] Handle enable/disable transitions

- [ ] **Update Protocol Files:**
  - [ ] Add `camera.focus` to `docs/protocol/commands.json`
  - [ ] Add `camera.auto_focus_hold` to `commands.json`
  - [ ] Mark `air_side: true` after implementation
  - [ ] Document parameters and validation rules

- [ ] **Testing with Real Camera:**
  - [ ] Test focus near at each speed (1, 2, 3)
  - [ ] Test focus far at each speed (1, 2, 3)
  - [ ] Test focus stop
  - [ ] Test auto-focus hold enable/disable
  - [ ] Test error cases (wrong mode, invalid speed)
  - [ ] Verify focus responds appropriately

### Ground-Side Tasks (Android)

- [ ] **Review Existing UI Structure:**
  - [ ] Locate Advanced Camera Control screen
  - [ ] Identify current tab structure
  - [ ] Locate manual focus tab (if exists)
  - [ ] Understand current fragment/layout hierarchy

- [ ] **Implement Manual Focus UI:**
  - [ ] Create/update Manual Focus Fragment
  - [ ] Add 6 direction buttons (near/far, speeds 1-3)
  - [ ] Add person and mountain icons
  - [ ] Add auto-focus hold button (reference ManualFocus.jpg)
  - [ ] Implement hold-to-activate behavior for AF hold
  - [ ] Style consistently with existing UI

- [ ] **Implement NetworkClient Methods:**
  - [ ] Add `focusCamera(action: String, speed: Int)` method
  - [ ] Add `setAutoFocusHold(enable: Boolean)` method
  - [ ] Build and send `camera.focus` command JSON
  - [ ] Build and send `camera.auto_focus_hold` command JSON
  - [ ] Add error handling for network failures

- [ ] **Implement ViewModel Logic:**
  - [ ] Add focus action methods to ViewModel
  - [ ] Add auto-focus hold methods to ViewModel
  - [ ] Handle button press/release events
  - [ ] Update UI state based on responses
  - [ ] Handle error states gracefully

- [ ] **Implement Mode-Based Display:**
  - [ ] Check current focus mode from camera status
  - [ ] Show manual controls IF mode == "manual"
  - [ ] Show placeholder/message IF mode != "manual"
  - [ ] (Phase 3+) Replace with auto-focus UI

- [ ] **Update Protocol Files:**
  - [ ] Mark `ground_side: true` in `commands.json`
  - [ ] Update `android/docs/PROGRESS_AND_TODO.md`

- [ ] **Testing:**
  - [ ] Test on emulator (UI behavior)
  - [ ] Test on H16 hardware (full integration)
  - [ ] Test all 6 focus speeds
  - [ ] Test auto-focus hold button behavior
  - [ ] Test error handling (no connection, etc.)

---

## 📚 SONY SDK FOCUS FUNCTIONS (Reference)

### Complete List of Focus-Related Functions

**Manual Focus Functions:**
- `CrDeviceProperty_Focus_Operation` - Primary manual focus control
- `CrDeviceProperty_NearFar` - Alternate near/far control
- `CrDeviceProperty_FocusPositionCurrentValue` - Read current position
- `CrDeviceProperty_FocusPositionSetting` - Set absolute position
- `CrDeviceProperty_Focus_Speed_Range` - Query supported speeds

**Auto-Focus Functions (Phase 3+):**
- `CrDeviceProperty_FocusMode` - Set focus mode (Manual/AF-S/AF-C/etc.)
- `CrDeviceProperty_FocusModeStatus` - Read current mode
- `CrDeviceProperty_AutoFocusHold` - Temporary AF hold in manual mode
- `CrDeviceProperty_PushAutoFocus` - Trigger AF (half-shutter)
- `CrDeviceProperty_FocusArea` - Set AF area
- `CrDeviceProperty_FocusDrivingStatus` - Read focus drive state

**Focus Assist Functions (Phase 2):**
- `CrDeviceProperty_Focus_Magnifier_Setting` - Enable focus magnifier
- `CrDeviceProperty_AFInFocusMagnifier` - AF during magnification
- `CrDeviceProperty_InitialFocusMagnifier` - Initial magnification ratio
- `CrDeviceProperty_FocusMagnificationTime` - Duration of magnification

**Advanced Functions (Phase 4+):**
- `CrDeviceProperty_FocusTrackingStatus` - Tracking AF status
- `CrDeviceProperty_FocusTouchSpotStatus` - Touch AF status
- `CrDeviceProperty_TouchFunctionInMF` - Touch behavior in MF
- `CrDeviceProperty_FunctionOfTouchOperation` - Touch operation function

**Bracketing Functions (Out of Scope):**
- `CrDeviceProperty_FocusBracket*` - Focus bracketing (focus stacking)

*Note: This list is for reference. Phase 1 only uses the manual focus functions.*

---

## ⚠️ IMPORTANT NOTES

### Protocol Synchronization

**BEFORE STARTING IMPLEMENTATION:**
1. Check if `camera.focus` already exists in `docs/protocol/commands.json`
2. Check if `camera.auto_focus_hold` exists
3. If commands exist, verify parameters match this plan
4. If parameters differ, **ASK USER** before proceeding

### Dependencies

**Air-Side:**
- Sony camera must be connected and initialized
- Camera must be set to manual focus mode first
- Test with `test_camera` or similar before integrating

**Ground-Side:**
- Network connection must be established
- Camera status must be received (to know current mode)
- UI must check mode before showing controls

### Verification

**After implementing each component:**
- Air-side: Test with real camera, verify focus movement
- Ground-side: Test UI behavior on device
- Integration: Test end-to-end with both sides running

---

## 📊 COMPLETION CRITERIA

### Air-Side Complete When:
- ✅ `camera.focus` command implemented and tested
- ✅ `camera.auto_focus_hold` command implemented and tested
- ✅ All 6 speeds (near/far 1-3) work correctly
- ✅ Focus stop command works
- ✅ Auto-focus hold enable/disable works
- ✅ Protocol JSON files updated
- ✅ `sbc/docs/PROGRESS_AND_TODO.md` updated
- ✅ Code committed with proper [PROTOCOL] tag

### Ground-Side Complete When:
- ✅ Manual focus UI implemented and functional
- ✅ All 6 direction buttons work
- ✅ Auto-focus hold button works (hold behavior)
- ✅ Mode-based display works correctly
- ✅ Network commands send successfully
- ✅ Error handling works
- ✅ Protocol JSON files updated
- ✅ `android/docs/PROGRESS_AND_TODO.md` updated
- ✅ Code committed with proper [PROTOCOL] tag

### Integration Complete When:
- ✅ Full end-to-end test passes
- ✅ Camera focuses near/far at all speeds via Android UI
- ✅ Auto-focus hold works via Android button
- ✅ No crashes or errors
- ✅ Documented in both PROGRESS_AND_TODO files

---

## 🚀 GETTING STARTED

### For Claude Code Session:

1. **Read Session Start Documents:**
   - `CC_READ_THIS_FIRST.md` (mandatory every session)
   - Appropriate `PROGRESS_AND_TODO.md` (air or ground)
   - This document (Focus Control Implementation)

2. **Check Protocol Status:**
   ```bash
   # Check if commands already exist
   cat docs/protocol/commands.json | jq '.commands | keys' | grep focus
   ```

3. **Determine Platform:**
   - Air-side? → Start with Sony SDK research
   - Ground-side? → Start with UI structure review
   - Both? → User will specify which to start

4. **Begin Implementation:**
   - Work incrementally (one function at a time)
   - Test frequently
   - Update docs after each milestone
   - Commit regularly with [PROTOCOL] or [FEATURE] tags

---

## 📐 COMMAND PROTOCOL SPECIFICATION

### camera.focus Command

**Direction:** Ground → Air  
**Transport:** TCP Port 5000  
**Format:** JSON

**Request:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 12345,
  "timestamp": 1730390400,
  "payload": {
    "command": "camera.focus",
    "parameters": {
      "action": "near",
      "speed": 3
    }
  }
}
```

**Parameters:**
- `action` (string, required): Focus direction
  - Valid values: `"near"`, `"far"`, `"stop"`
- `speed` (integer, optional): Focus speed (1-3)
  - Default: 3
  - Valid values: 1 (slow), 2 (medium), 3 (fast)
  - Only used when action is "near" or "far"

**Response (Success):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 12345,
  "timestamp": 1730390401,
  "payload": {
    "success": true,
    "command": "camera.focus"
  }
}
```

**Response (Error):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 12345,
  "timestamp": 1730390401,
  "payload": {
    "success": false,
    "command": "camera.focus",
    "error_code": 3001,
    "error_message": "Camera not in manual focus mode"
  }
}
```

**Error Codes:**
- `3001` - Camera not in manual focus mode
- `3002` - Invalid focus action
- `3003` - Invalid focus speed
- `3004` - Camera not connected
- `3005` - Focus operation failed

---

### camera.auto_focus_hold Command

**Direction:** Ground → Air  
**Transport:** TCP Port 5000  
**Format:** JSON

**Request:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 12346,
  "timestamp": 1730390400,
  "payload": {
    "command": "camera.auto_focus_hold",
    "parameters": {
      "enable": true
    }
  }
}
```

**Parameters:**
- `enable` (boolean, required): Enable or disable auto-focus hold
  - `true` - Temporarily enable auto-focus
  - `false` - Return to manual focus

**Response (Success):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 12346,
  "timestamp": 1730390401,
  "payload": {
    "success": true,
    "command": "camera.auto_focus_hold"
  }
}
```

**Response (Error):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 12346,
  "timestamp": 1730390401,
  "payload": {
    "success": false,
    "command": "camera.auto_focus_hold",
    "error_code": 3006,
    "error_message": "Auto-focus hold not available"
  }
}
```

**Error Codes:**
- `3006` - Auto-focus hold not available
- `3007` - Camera not connected
- `3008` - Operation failed

---

## 🔧 IMPLEMENTATION EXAMPLES

### Air-Side C++ Example (Conceptual)

```cpp
// In tcp_server.cpp command handler

void handleCameraFocus(const json& params, json& response) {
    // Validate parameters
    if (!params.contains("action")) {
        response["success"] = false;
        response["error_code"] = 3002;
        response["error_message"] = "Missing action parameter";
        return;
    }
    
    std::string action = params["action"];
    int speed = params.value("speed", 3); // Default speed 3
    
    // Validate action
    if (action != "near" && action != "far" && action != "stop") {
        response["success"] = false;
        response["error_code"] = 3002;
        response["error_message"] = "Invalid focus action";
        return;
    }
    
    // Validate speed
    if (speed < 1 || speed > 3) {
        response["success"] = false;
        response["error_code"] = 3003;
        response["error_message"] = "Invalid focus speed (must be 1-3)";
        return;
    }
    
    // Map to Sony SDK values (example - verify with SDK docs)
    CrInt32u focusOperation;
    if (action == "near") {
        // Map speed to near operation value
        focusOperation = CrFocus_Near_1 + (speed - 1); // Example mapping
    } else if (action == "far") {
        // Map speed to far operation value
        focusOperation = CrFocus_Far_1 + (speed - 1); // Example mapping
    } else { // stop
        focusOperation = CrFocus_Stop;
    }
    
    // Call Sony SDK
    CrInt32u result = SDK::SetDeviceProperty(
        m_device_handle,
        CrDeviceProperty_Focus_Operation,
        &focusOperation,
        sizeof(focusOperation)
    );
    
    if (result == CrError_None) {
        response["success"] = true;
        LOG_INFO("Focus operation successful: action=" + action + ", speed=" + std::to_string(speed));
    } else {
        response["success"] = false;
        response["error_code"] = 3005;
        response["error_message"] = "Focus operation failed";
        LOG_ERROR("Sony SDK error: " + std::to_string(result));
    }
}
```

### Ground-Side Kotlin Example (Conceptual)

```kotlin
// In NetworkClient.kt

suspend fun focusCamera(action: String, speed: Int = 3): Result<Unit> {
    val command = Command(
        command = "camera.focus",
        parameters = mapOf(
            "action" to action,
            "speed" to speed
        )
    )
    
    return withContext(Dispatchers.IO) {
        try {
            val response = sendCommand(command)
            if (response.payload.success) {
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.payload.error_message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

suspend fun setAutoFocusHold(enable: Boolean): Result<Unit> {
    val command = Command(
        command = "camera.auto_focus_hold",
        parameters = mapOf("enable" to enable)
    )
    
    return withContext(Dispatchers.IO) {
        try {
            val response = sendCommand(command)
            if (response.payload.success) {
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.payload.error_message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

```kotlin
// In ManualFocusFragment.kt

class ManualFocusFragment : Fragment() {
    private val viewModel: CameraViewModel by viewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // Near buttons
        binding.btnNearSlow.setOnClickListener { 
            viewModel.focusNear(speed = 1) 
        }
        binding.btnNearMedium.setOnClickListener { 
            viewModel.focusNear(speed = 2) 
        }
        binding.btnNearFast.setOnClickListener { 
            viewModel.focusNear(speed = 3) 
        }
        
        // Far buttons
        binding.btnFarSlow.setOnClickListener { 
            viewModel.focusFar(speed = 1) 
        }
        binding.btnFarMedium.setOnClickListener { 
            viewModel.focusFar(speed = 2) 
        }
        binding.btnFarFast.setOnClickListener { 
            viewModel.focusFar(speed = 3) 
        }
        
        // Auto-focus hold button (press and hold behavior)
        binding.btnAfHold.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    viewModel.setAutoFocusHold(true)
                    true
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    viewModel.setAutoFocusHold(false)
                    true
                }
                else -> false
            }
        }
        
        // Observe errors
        viewModel.errorState.observe(viewLifecycleOwner) { error ->
            if (error != null) {
                Toast.makeText(context, error, Toast.LENGTH_SHORT).show()
            }
        }
    }
}
```

---

## 📖 ADDITIONAL RESOURCES

### Project References
- **Main Project Summary:** `docs/Project_Summary_and_Action_Plan.md`
- **Claude Code Workflow:** `docs/CC_READ_THIS_FIRST.md`
- **Air-Side Progress:** `sbc/docs/PROGRESS_AND_TODO.md`
- **Ground-Side Progress:** `android/docs/PROGRESS_AND_TODO.md`
- **Protocol Specification:** `docs/Command_Protocol_Specification_v1.0.md`

### Sony SDK Documentation
- **API Reference:** `Sony_CameraRemoteSDK_API-Reference_v2.00.00.pdf`
- **Sample Application:** `RemoteSampleApp_IM_v2_00_00.pdf`
- **SDK Headers:** `~/sony_sdk/include/`

### UI Reference
- **Manual Focus Layout:** `~/docs/ManualFocus.jpg`

---

**Document Status:** Ready for Implementation  
**Created:** October 31, 2025  
**Phase:** Phase 1 - Manual Focus Only  
**Estimated Time:** 
- Air-side: 4-6 hours
- Ground-side: 4-6 hours  
- Integration: 2 hours
- **Total:** 10-14 hours

---

## 📞 SUPPORT

If you encounter issues during implementation:

1. **Check Sony SDK Documentation** - Focus-related properties and enumerations
2. **Review Working Examples** - `test_shutter.cpp` and `RemoteCli` for SDK patterns
3. **Test Incrementally** - Verify each function works before moving to next
4. **Update Progress Docs** - Keep PROGRESS_AND_TODO.md current with blockers
5. **Commit Frequently** - Use [PROTOCOL] or [FEATURE] tags appropriately

Remember: Phase 1 is **manual focus only**. Advanced features come in later phases!
