# Camera Focus Control Fix - Implementation Instructions

## Summary

This document provides the fix for the camera focus control issue where `camera.focus` commands fail with SDK error `0x8402` (CrError_Api_InvalidCalled).

## Root Cause Analysis

The error `0x8402` indicates that the Focus_Operation API is being called in an invalid state. After analyzing the SDK documentation and implementation, the following issues were identified:

### Primary Issues

1. **Missing Property Validation**: The code doesn't verify that `FocalDistanceInMeter` property is actually "enabled" (readable) before attempting focus operations. The SDK requires this property to be enabled for Focus_Operation to work.

2. **No Speed Range Validation**: The code doesn't query `Focus_Speed_Range` to determine valid speed values. Using speeds outside the camera's supported range can cause failures.

3. **Missing Property State Checks**: The code doesn't verify if `Focus_Operation` itself is settable in the current camera state.

4. **Timing Issues**: Rapid property queries followed immediately by commands can cause issues with some cameras.

## Implementation Steps

### Step 1: Deploy Diagnostic Version (Optional but Recommended)

First, deploy the diagnostic version to understand the exact issue with your camera:

```bash
# SSH to Raspberry Pi
ssh dpm@10.0.1.53
# Password: 2350

# Backup current file
cd ~/DPM-V2/sbc/src/camera
cp camera_sony.cpp camera_sony.cpp.backup

# Copy diagnostic version (you'll need to transfer the file first)
# Replace lines 356-430 in camera_sony.cpp with the content from camera_sony_diagnostic.cpp

# Rebuild and deploy
cd ~/DPM-V2/sbc
./build_container.sh
./run_container.sh prod

# Monitor logs
docker logs -f payload-manager

# Test focus command from Windows Tools or Android app
# Check the detailed diagnostic output in logs
```

### Step 2: Deploy Fixed Version

After understanding the issue, deploy the fix:

```bash
# SSH to Raspberry Pi
ssh dpm@10.0.1.53

# Edit camera_sony.cpp
cd ~/DPM-V2/sbc/src/camera
nano camera_sony.cpp

# Replace the focus() method (lines 356-430) with the content from camera_sony_fixed.cpp
# The fixed version includes:
# - Focus_Speed_Range query and validation
# - Enhanced FocalDistanceInMeter checking
# - Speed clamping to valid ranges
# - Timing delays to prevent interference
# - Better error reporting

# Save and exit (Ctrl+X, Y, Enter)

# Rebuild
cd ~/DPM-V2/sbc
./build_container.sh

# Stop current container
docker stop payload-manager && docker rm payload-manager

# Start new container
./run_container.sh prod
```

### Step 3: Test Focus Commands

Test the fix using these commands:

```bash
# Monitor logs in one terminal
ssh dpm@10.0.1.53
docker logs -f payload-manager

# In another terminal, send test commands
# Test NEAR focus
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":100,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"near","speed":1}}}' | nc 10.0.1.53 5000

# Wait 2 seconds, then test STOP
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":101,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"stop"}}}' | nc 10.0.1.53 5000

# Test FAR focus
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":102,"timestamp":1730000000,"payload":{"command":"camera.focus","parameters":{"action":"far","speed":2}}}' | nc 10.0.1.53 5000

# Test AUTO FOCUS HOLD
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":103,"timestamp":1730000000,"payload":{"command":"camera.auto_focus_hold","parameters":{"state":"press"}}}' | nc 10.0.1.53 5000

echo '{"protocol_version":"1.0","message_type":"command","sequence_id":104,"timestamp":1730000000,"payload":{"command":"camera.auto_focus_hold","parameters":{"state":"release"}}}' | nc 10.0.1.53 5000
```

## Key Changes in the Fix

### 1. Focus_Speed_Range Query
```cpp
// Query the camera's supported speed range
auto speed_result = SDK::GetSelectDeviceProperties(
    device_handle_, 1, speed_range_codes, &speed_range_list, &speed_range_count
);
// Extract min/max speeds and clamp user input to valid range
```

### 2. Enhanced FocalDistanceInMeter Checking
```cpp
// Check if property is actually enabled (readable)
focal_distance_enabled = focal_distance_list[0].IsGetEnableCurrentValue();
if (!focal_distance_enabled) {
    Logger::warning("FocalDistanceInMeter property is NOT enabled");
    // Additional checks for focus mode, etc.
}
```

### 3. Speed Validation and Clamping
```cpp
// Ensure speed is within camera's supported range
if (focus_operation < min_speed) {
    focus_operation = min_speed;
}
if (focus_operation > max_speed) {
    focus_operation = max_speed;
}
```

### 4. Timing Improvements
```cpp
// Add small delay after property queries
std::this_thread::sleep_for(std::chrono::milliseconds(50));

// Add delay after focus command to prevent interference
std::this_thread::sleep_for(std::chrono::milliseconds(100));
```

### 5. Enhanced Error Reporting
```cpp
if (result == 0x8402) {
    Logger::error("Error 0x8402: Focus_Operation called in invalid state");
    Logger::error("Possible causes:");
    Logger::error("  1. Camera not in manual focus mode");
    Logger::error("  2. FocalDistanceInMeter property not enabled");
    // ... detailed diagnostics
}
```

## Alternative Solutions

If the primary fix doesn't work, try these alternatives:

### Alternative 1: Enable Live View First
Some cameras require live view to be active for focus operations:

```cpp
// Before focus operation, start live view
SDK::CrDeviceProperty lv_prop;
lv_prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_LiveView_Status);
lv_prop.SetCurrentValue(0x01);  // Enable
SDK::SetDeviceProperty(device_handle_, &lv_prop);
```

### Alternative 2: Set Manual Focus Mode
Ensure camera is in manual focus mode:

```cpp
SDK::CrDeviceProperty mode_prop;
mode_prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FocusMode);
mode_prop.SetCurrentValue(SDK::CrFocusMode::CrFocus_MF);
SDK::SetDeviceProperty(device_handle_, &mode_prop);
```

### Alternative 3: Use Different Focus Method
If Focus_Operation continues to fail, try using zoom/focus position setting:

```cpp
// Use CrDeviceProperty_FocusPositionSetting instead
SDK::CrDeviceProperty pos_prop;
pos_prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_FocusPositionSetting);
// Set position value...
```

## Expected Behavior After Fix

✅ **Success Indicators:**
- No more `0x8402` errors in logs
- Focus commands execute without errors
- Focal distance updates correctly in responses
- Property readbacks remain responsive

✅ **Log Output Should Show:**
```
[INFO] Focus_Speed_Range detected: -7 to 7
[INFO] FocalDistanceInMeter property is enabled and readable
[INFO] Executing focus action: NEAR (closer objects), speed=1
[INFO] Focus action 'near' executed successfully
```

## Verification Checklist

- [ ] Camera is in Manual Focus mode
- [ ] FocalDistanceInMeter property shows as "enabled" in logs
- [ ] Focus_Speed_Range is successfully queried
- [ ] No SDK errors (0x8402 or others) when sending focus commands
- [ ] Focus actually moves the lens (verify visually)
- [ ] Property updates (ISO, shutter, etc.) remain responsive after focus
- [ ] Both near/far/stop actions work
- [ ] auto_focus_hold press/release works

## Rollback Instructions

If issues arise:

```bash
# Restore backup
ssh dpm@10.0.1.53
cd ~/DPM-V2/sbc/src/camera
cp camera_sony.cpp.backup camera_sony.cpp

# Rebuild and deploy
cd ~/DPM-V2/sbc
./build_container.sh
docker stop payload-manager && docker rm payload-manager
./run_container.sh prod
```

## Ground-Side Considerations

The Android app should:
1. Not send focus commands too rapidly (add 100ms delay between commands)
2. Handle error responses gracefully
3. Show focus distance in UI when available
4. Disable focus controls if camera reports focus not available

## Contact for Issues

If the fix doesn't resolve the issue:
1. Run the diagnostic version and capture full logs
2. Note the exact camera model and firmware version
3. Document which specific step fails
4. Check if Sony Remote App works with the same camera setup

---

**Created:** 2025-10-31
**Author:** Claude (AI Assistant)
**Status:** Ready for Implementation