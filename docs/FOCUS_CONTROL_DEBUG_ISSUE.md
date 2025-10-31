# Camera Focus Control Implementation Issue - Debug Request

## Issue Summary

**Problem:** Camera focus control (`camera.focus` and `camera.auto_focus_hold` commands) are failing with SDK error `0x8402` (CrError_Api_InvalidCalled). Additionally, when focus commands are sent, camera property readback becomes slow and erratic.

**Status:**
- ✅ Protocol parsing fixed (parameters now read from `payload["parameters"]`)
- ✅ Focus operation encoding fixed (now uses signed integer: `-speed` for near, `+speed` for far, `0` for stop)
- ✅ Focal distance query added before focus operations
- ❌ Still failing with SDK error 0x8402
- ❌ Camera property updates slow after focus commands

**Severity:** High - Core camera functionality not working

---

## System Architecture

### Air-Side (Raspberry Pi 5)
- **Hardware:** Raspberry Pi 5, Sony ILCE-1 camera via USB
- **OS:** Ubuntu Server ARM64
- **Implementation:** C++ with Sony Camera Remote SDK v2.00.00
- **Container:** Docker (Ubuntu 22.04 ARM64 base)
- **Binary:** `/app/bin/payload_manager`

### Ground-Side (Android GCS)
- **Platform:** Android (details unknown - needs investigation)
- **Implementation:** Kotlin (assumed)
- **Communication:** TCP socket to Air-Side port 5000

### Protocol
- **Version:** DPM Protocol v1.0
- **Transport:** TCP (port 5000)
- **Format:** JSON messages

---

## Remote Access Information

### SSH Access to Raspberry Pi
```bash
ssh dpm@10.0.1.53
# Password: 2350
```

### Docker Container Access
```bash
# From Windows PC (after SSH):
ssh dpm@10.0.1.53

# Once connected to Pi:
# View running containers
docker ps

# Access container shell
docker exec -it payload-manager bash

# View live logs
docker logs -f payload-manager

# View last 100 lines of logs
docker logs payload-manager 2>&1 | tail -100

# Search logs for specific errors
docker logs payload-manager 2>&1 | grep -E "camera.focus|SDK error|0x8402"

# Check camera connection
docker logs payload-manager 2>&1 | grep -E "Camera connected|PC Remote"
```

### Build and Deployment
```bash
# From Windows PC:
ssh dpm@10.0.1.53
cd ~/DPM-V2/sbc

# Full rebuild (compiles C++ code inside Docker)
./build_container.sh

# Deploy to production
./run_container.sh prod

# Stop and restart container
docker stop payload-manager && docker rm payload-manager
./run_container.sh prod

# View build output
docker logs payload-manager 2>&1 | head -50
```

---

## SDK Documentation Reference

### Local Path (on Windows PC)
```
D:\DPM\CrSDK_v2.00.00_20250805a_Linux64ARMv8\CrSDK_API_Reference_v2.00.00\html
```

### Key Documentation Files
- **Focus Operation:** `dp/dp_Focus_Operation.html`
- **Focal Distance:** `dp/dp_FocalDistanceInMeter.html`
- **Focus Speed Range:** `dp/dp_Focus_Speed_Range.html`
- **Error Codes:** `CrError.h` reference
- **Push Auto Focus:** `dp/dp_PushAutoFocus.html`

### Remote Path (on Raspberry Pi)
```bash
# SDK location
/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/

# Documentation
/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/

# View documentation via SSH
ssh dpm@10.0.1.53
cat /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/_sources/dp/dp_Focus_Operation.rst.txt
```

---

## Current Implementation

### Air-Side Focus Implementation
**File:** `/home/dpm/DPM-V2/sbc/src/camera/camera_sony.cpp`

**Key Code (lines 356-430):**
```cpp
bool focus(const std::string& action, int speed = 3) override {
    if (!isConnected()) {
        Logger::error("Cannot focus: camera not connected");
        return false;
    }

    std::unique_lock<std::mutex> lock(mutex_, std::try_to_lock);
    if (!lock.owns_lock()) {
        Logger::warning("Cannot focus: camera busy with another operation");
        return false;
    }

    // Query focal distance to ensure property is enabled
    CrInt32u property_codes[] = {
        SDK::CrDevicePropertyCode::CrDeviceProperty_FocalDistanceInMeter
    };
    SDK::CrDeviceProperty* property_list = nullptr;
    int property_count = 0;
    auto query_result = SDK::GetSelectDeviceProperties(
        device_handle_, 1, property_codes, &property_list, &property_count
    );

    if (CR_SUCCEEDED(query_result) && property_list) {
        SDK::ReleaseDeviceProperties(device_handle_, property_list);
        Logger::debug("Focal distance property is enabled");
    } else {
        Logger::warning("Focal distance property query failed - focus may not work");
    }

    // Map action and speed to focus operation value
    // Positive (1-7): Tele/Far, Negative (-1 to -7): Wide/Near, Zero: Stop
    CrInt8 focus_operation;
    if (action == "near") {
        focus_operation = -speed;
        Logger::info("Executing focus action: NEAR (closer objects), speed=" + std::to_string(speed));
    } else if (action == "far") {
        focus_operation = speed;
        Logger::info("Executing focus action: FAR (distant objects), speed=" + std::to_string(speed));
    } else if (action == "stop") {
        focus_operation = 0;
        Logger::info("Executing focus action: STOP");
    } else {
        Logger::error("Invalid focus action: " + action);
        return false;
    }

    // Set focus operation property
    SDK::CrDeviceProperty prop;
    prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_Focus_Operation);
    prop.SetCurrentValue(static_cast<CrInt64u>(focus_operation));
    prop.SetValueType(SDK::CrDataType_Int8);

    auto result = SDK::SetDeviceProperty(device_handle_, &prop);

    if (CR_FAILED(result)) {
        Logger::error("Failed to set focus operation. SDK error: 0x" + toHexString(result));
        return false;
    }

    Logger::info("Focus action '" + action + "' executed successfully");
    return true;
}
```

### Protocol Specification
**File:** `/home/dpm/DPM-V2/protocol/commands.json`

```json
{
  "camera.focus": {
    "description": "Control manual focus operation (near/far/stop)",
    "parameters": {
      "action": {
        "type": "string",
        "enum": ["near", "far", "stop"],
        "required": true
      },
      "speed": {
        "type": "integer",
        "minimum": 1,
        "maximum": 3,
        "default": 3,
        "required": false
      }
    },
    "response": {
      "success": {
        "action": "string",
        "speed": "integer",
        "focus_distance_m": "float | 'infinity' (optional)"
      },
      "errors": [1000, 3001, 3002, 3003, 3004]
    }
  }
}
```

---

## Log Analysis

### Recent Air-Side Logs (Focus Attempts)

**Access Command:**
```bash
ssh dpm@10.0.1.53
docker logs payload-manager 2>&1 | grep -E "camera.focus|SDK error|Focal distance" | tail -50
```

**Sample Output:**
```
[2025-10-31 03:07:55.181] [DEBUG] Received from 192.168.144.11: {"command":"camera.focus","parameters":{"action":"stop"}}
[2025-10-31 03:07:55.181] [INFO] Processing command: camera.focus
[2025-10-31 03:07:55.181] [INFO] Executing camera.focus command: action=stop, speed=3
[2025-10-31 03:07:55.181] [INFO] Executing focus action: STOP
[2025-10-31 03:07:55.181] [ERROR] Failed to set focus operation. SDK error: 0x0x8402
[2025-10-31 03:07:58.661] [DEBUG] Received from 192.168.144.11: {"command":"camera.focus","parameters":{"action":"near","speed":1}}
[2025-10-31 03:07:58.661] [INFO] Executing focus action: NEAR (closer objects), speed=1
[2025-10-31 03:07:58.661] [ERROR] Failed to set focus operation. SDK error: 0x0x8402
```

**Camera Connection Status:**
```bash
docker logs payload-manager 2>&1 | grep -E "Camera connected|PC Remote mode"
```
```
[2025-10-31 03:13:10.867] [INFO] Camera connected (SDK connection version)
[2025-10-31 03:13:11.297] [INFO] Successfully set camera priority to PC Remote mode
```

### Property Update Timing Issue

**Command:**
```bash
docker logs payload-manager 2>&1 | grep -A5 "camera.set_property.*iso.*400"
```

**Observed Behavior:**
```
[03:03:09.666] Processing command: camera.set_property
[03:03:09.666] Setting property: iso = 400
[03:03:09.666] Property set successfully
[03:03:09.666] Getting property: iso
[03:03:09.666] Raw SDK value for iso: 0x140 (dec: 320)  # ← Still showing old value!
```

**Issue:** Camera reports success but immediate readback shows old value (320 instead of 400).

---

## SDK Error Code Analysis

**Error:** `0x8402`

**From SDK Documentation (`CrError.h`):**
```cpp
CrError_Api                     = 0x8400,
CrError_Api_InvalidCalled       = 0x8402,  // ← Our error
```

**Meaning:** "API called in invalid state or context"

**SDK Documentation Statement:**
> "This device property [Focus_Operation] is valid when CrDeviceProperty_FocalDistanceInMeter or CrDeviceProperty_FocalDistanceInFeet is enabled."

---

## Known Working Reference

**Sony Remote App Behavior:**
- ✅ Focus control (near/far) works WITHOUT live view enabled
- ✅ Shows focal distance readout during focus operations
- ✅ Property updates are immediate and responsive

**This proves:** Focus should work without live view requirement.

---

## Questions for Investigation

### 1. SDK Property Requirements
- **Q:** What does "enabled" mean for `FocalDistanceInMeter`?
  - Is it readable? Writable? Has enable flag set?
  - Do we need to SET this property before USING Focus_Operation?

- **Q:** What is the valid range from `Focus_Speed_Range`?
  - Are we sending values (1-3) within the camera's supported range?
  - Should we query this property first?

### 2. Camera State Requirements
- **Q:** Does Focus_Operation require a specific camera mode?
  - Manual focus mode? (Already set: logs show `focus_mode = manual`)
  - Specific shooting mode?
  - Shutter state?

- **Q:** Is there a "focus session" that needs to be started?
  - Does Remote app start live view or monitoring first?
  - Are there prerequisite SDK calls we're missing?

### 3. Threading/Timing Issues
- **Q:** Why do property readbacks slow down after focus commands?
  - Are we holding the mutex too long?
  - Is the camera entering a busy state?
  - Do focus operations block the SDK?

### 4. Ground-Side Protocol
- **Q:** Is Ground-side sending commands too rapidly?
  - Should there be delays between focus commands?
  - Are we overwhelming the camera with requests?

---

## Testing Methodology

### Air-Side Testing (SSH Required)

**Test 1: Verify Camera State**
```bash
ssh dpm@10.0.1.53
docker exec -it payload-manager bash

# Check if test binaries exist
ls -la /app/bin/test_*

# If available, run camera property query test
/app/bin/test_camera_properties
```

**Test 2: Manual Focus Command via netcat**
```bash
# From Pi or another machine on same network
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"near","speed":1}}}' | nc 10.0.1.53 5000
```

**Test 3: Monitor Logs in Real-Time**
```bash
# Terminal 1: Watch logs
ssh dpm@10.0.1.53
docker logs -f payload-manager

# Terminal 2: Send test commands
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":2,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"far","speed":2}}}' | nc 10.0.1.53 5000
```

### SDK Documentation Review

**Files to Check:**
1. `dp/dp_Focus_Operation.html` - Main focus operation docs
2. `dp/dp_FocalDistanceInMeter.html` - Prerequisite property
3. `dp/dp_Focus_Speed_Range.html` - Valid speed values
4. `dp/dp_PushAutoFocus.html` - Alternative AF method
5. `dp/dp_FocusMagnificationSetting.html` - Related focus properties

**Key Questions:**
- What properties must be GET before SET of Focus_Operation?
- Are there example code snippets in SDK?
- What is the proper sequence of SDK calls?

---

## Related Files

### Air-Side Implementation
```
/home/dpm/DPM-V2/sbc/src/camera/camera_sony.cpp     # Focus implementation
/home/dpm/DPM-V2/sbc/src/camera/camera_sony.h       # Header
/home/dpm/DPM-V2/sbc/src/camera/camera_interface.h  # Interface
/home/dpm/DPM-V2/sbc/src/protocol/tcp_server.cpp    # Protocol handler
/home/dpm/DPM-V2/sbc/src/protocol/messages.h        # Message formats
```

### Documentation
```
/home/dpm/DPM-V2/docs/Ground_Side_Focus_Implementation_Guide.md  # Ground-side guide
/home/dpm/DPM-V2/docs/Focus_Implementation_Summary.md            # Summary
/home/dpm/DPM-V2/protocol/commands.json                          # Protocol spec
```

### SDK Reference
```
/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/app/CRSDK/       # SDK headers
/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/
```

---

## Requested Actions

### Primary Goal
**Fix camera focus control to work reliably like Sony Remote App**

### Specific Tasks

1. **Analyze SDK Requirements**
   - Review all Focus_Operation prerequisites in SDK docs
   - Identify missing property queries or settings
   - Determine correct API call sequence

2. **Fix Air-Side Implementation**
   - Add any missing property initialization
   - Correct SDK call sequence if needed
   - Add better error logging with specific failure points
   - Verify thread safety and mutex usage

3. **Investigate Property Slowdown**
   - Determine why ISO and other property readbacks slow after focus commands
   - Check if focus operations block or change camera state
   - Verify proper mutex release and SDK cleanup

4. **Ground-Side Review** (if needed)
   - Check if Android app sends commands too rapidly
   - Verify proper error handling and retry logic
   - Ensure protocol compliance

5. **Testing Plan**
   - Provide test commands to verify fix
   - Document expected vs actual behavior
   - Create regression tests

---

## Success Criteria

✅ **Focus commands work without errors**
- `camera.focus` with action="near/far/stop" succeeds
- `camera.auto_focus_hold` with state="press/release" succeeds
- No SDK error 0x8402 or other errors

✅ **Focal distance readback functional**
- Response includes `focus_distance_m` field
- Shows accurate distance or "infinity"

✅ **Property updates remain responsive**
- ISO, shutter, aperture readbacks work normally
- No slowdown or erratic behavior after focus commands

✅ **Matches Sony Remote App behavior**
- Works without live view requirement
- Responsive and immediate
- Reliable repeated use

---

## Additional Context

### Recent Changes
1. Fixed protocol parsing (parameters object structure)
2. Fixed focus operation encoding (signed integer with speed)
3. Added focal distance property query before focus operations

### Current Status
- Camera connects successfully
- PC Remote mode enabled
- Manual focus mode confirmed
- Other commands (capture, set_property) working
- Only focus commands failing with 0x8402

### Observations
- Sony Remote app works perfectly with same camera
- Error is consistent across all focus actions (near/far/stop)
- Error appears immediately, not after timeout
- Camera remains connected after error

---

## Contact Information

**System Owner:** DPM Team
**Remote Access:** SSH to 10.0.1.53 (password: 2350)
**Container:** `payload-manager` (Docker)
**Logs:** `docker logs payload-manager`

**Response Format:**
- Updated code files (with clear change markers)
- Explanation of root cause
- Testing commands to verify fix
- Any Ground-side changes needed
- Documentation updates if protocol changes

---

## Appendix: Quick Command Reference

```bash
# === SSH Access ===
ssh dpm@10.0.1.53
# Password: 2350

# === Docker Commands ===
docker logs payload-manager 2>&1 | tail -100           # Last 100 log lines
docker logs -f payload-manager                         # Follow logs live
docker exec -it payload-manager bash                   # Shell access
docker stop payload-manager && docker rm payload-manager  # Remove container

# === Build & Deploy ===
cd ~/DPM-V2/sbc
./build_container.sh                                   # Full rebuild
./run_container.sh prod                                # Deploy production

# === Log Analysis ===
docker logs payload-manager 2>&1 | grep "camera.focus"           # Focus commands
docker logs payload-manager 2>&1 | grep "SDK error"              # SDK errors
docker logs payload-manager 2>&1 | grep "Camera connected"       # Connection status
docker logs payload-manager 2>&1 | grep "0x8402"                 # Specific error

# === Test Commands ===
# Send test focus command (from Pi or network machine)
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":99,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"near","speed":2}}}' | nc 10.0.1.53 5000

# === SDK Documentation ===
cat /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/_sources/dp/dp_Focus_Operation.rst.txt
```

---

**Generated:** 2025-10-31 03:15 UTC
**For:** Claude Opus Analysis & Debugging
**Priority:** High
**Status:** Awaiting Investigation
