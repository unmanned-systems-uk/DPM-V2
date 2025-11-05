# Issue #1: Ground-Side Implementation - Focus Distance Readback

**Status:** 🟡 Open
**Priority:** High
**Category:** Bug Fix - Feature Completion
**Component:** Android App - Camera Control
**Related Air-Side Issue:** #1 (Fixed in commit TBD)
**Created:** 2025-11-05
**Air-Side Status:** ✅ Fixed and Deployed

---

## Summary

Implement Ground-Side support for focal distance readback from Air-Side camera. Air-Side is now broadcasting `focal_distance_meters` in UDP status messages, but Ground-Side needs to parse and display this data.

---

## Problem Statement

**Current State:**
- ❌ FocusDistanceOverlay UI component exists but never displays (no data)
- ❌ CameraViewModel has `_focusDistanceM` StateFlow but it's always `null`
- ❌ SimpleCameraSettings doesn't include `focal_distance_meters` field
- ❌ syncCameraSettings() doesn't sync focal distance from UDP broadcasts

**Expected Behavior:**
- ✅ FocusDistanceOverlay displays real-time focal distance (e.g., "5.2m", "∞")
- ✅ Progress bar shows focus position on logarithmic scale
- ✅ Updates automatically from UDP status broadcasts (5 Hz)

---

## Root Cause Analysis

### Air-Side (✅ FIXED):
1. ✅ Added `focal_distance_meters` field to CameraStatus struct (messages.h:134)
2. ✅ Updated getStatus() to populate focal distance via getFocalDistanceMeters() (camera_sony.cpp:294)
3. ✅ UDP broadcasts now include `focal_distance_meters` in JSON under `camera.settings`
4. ✅ Container rebuilt and restarted with fix

### Ground-Side (❌ NEEDS FIX):
1. ❌ SimpleCameraSettings missing `focalDistanceMeters` field (ProtocolMessages.kt:99-106)
2. ❌ syncCameraSettings() doesn't sync focal distance (CameraViewModel.kt:563-590)

---

## Implementation Instructions

### File 1: ProtocolMessages.kt

**Location:** `/android/app/src/main/java/uk/unmannedsystems/dpm_android/network/ProtocolMessages.kt`

**Current Code (lines 99-106):**
```kotlin
data class SimpleCameraSettings(
    @SerializedName("shutter_speed") val shutterSpeed: String = "",
    val aperture: String = "",
    val iso: String = "",
    @SerializedName("white_balance") val whiteBalance: String = "",
    @SerializedName("focus_mode") val focusMode: String = "",
    @SerializedName("file_format") val fileFormat: String = ""
)
```

**Updated Code (add new field after line 105):**
```kotlin
data class SimpleCameraSettings(
    @SerializedName("shutter_speed") val shutterSpeed: String = "",
    val aperture: String = "",
    val iso: String = "",
    @SerializedName("white_balance") val whiteBalance: String = "",
    @SerializedName("focus_mode") val focusMode: String = "",
    @SerializedName("file_format") val fileFormat: String = "",
    @SerializedName("focal_distance_meters") val focalDistanceMeters: Float? = null  // NEW: Focus distance in meters (-1 = infinity, null = unknown)
)
```

**Why:**
- Air-Side now sends `focal_distance_meters` in the UDP status JSON
- Field name matches Air-Side: `camera.settings.focal_distance_meters`
- Type is `Float?` because:
  - `null` = no data available (camera disconnected or query failed)
  - `-1f` = infinity focus
  - `0.0f` = unknown/query failed
  - Positive values = distance in meters (e.g., `5.2f` = 5.2 meters)

---

### File 2: CameraViewModel.kt

**Location:** `/android/app/src/main/java/uk/unmannedsystems/dpm_android/camera/CameraViewModel.kt`

**Current Code (lines 563-622 - syncCameraSettings method):**
```kotlin
private fun syncCameraSettings(settings: uk.unmannedsystems.dpm_android.network.SimpleCameraSettings) {
    _cameraState.update { state ->
        var newState = state

        // Sync shutter speed (if not empty)
        if (settings.shutterSpeed.isNotEmpty()) {
            val shutterSpeed = ShutterSpeed.entries.find {
                it.displayValue == settings.shutterSpeed
            }
            if (shutterSpeed != null && shutterSpeed != state.shutterSpeed) {
                Log.d(TAG, "Syncing shutter speed: ${settings.shutterSpeed}")
                newState = newState.copy(shutterSpeed = shutterSpeed)
            }
        }

        // Sync aperture (if not empty)
        if (settings.aperture.isNotEmpty()) {
            // Remove "f/" prefix if present
            val apertureValue = settings.aperture.removePrefix("f/")
            val aperture = Aperture.entries.find {
                it.displayValue == apertureValue
            }
            if (aperture != null && aperture != state.aperture) {
                Log.d(TAG, "Syncing aperture: ${settings.aperture}")
                newState = newState.copy(aperture = aperture)
            }
        }

        // Sync ISO (if not empty)
        if (settings.iso.isNotEmpty()) {
            val iso = ISO.entries.find {
                it.displayValue == settings.iso || it.displayValue == "ISO ${settings.iso}"
            }
            if (iso != null && iso != state.iso) {
                Log.d(TAG, "Syncing ISO: ${settings.iso}")
                newState = newState.copy(iso = iso)
            }
        }

        // ... (more sync code for white balance, focus mode, file format)

        newState
    }
}
```

**Add this code at the end of syncCameraSettings() (after all other syncs, before `newState` return):**
```kotlin
        // Sync focal distance (if available)
        settings.focalDistanceMeters?.let { distance ->
            // Update focal distance StateFlow for FocusDistanceOverlay
            _focusDistanceM.value = distance

            // Log for debugging
            val distanceStr = when {
                distance < 0 -> "infinity"
                distance == 0.0f -> "unknown"
                distance < 1.0f -> "${(distance * 100).toInt()}cm"
                else -> String.format("%.1fm", distance)
            }
            Log.d(TAG, "Syncing focal distance: $distanceStr (raw: $distance)")
        }
```

**Where to add it:**
- After all existing sync blocks (ISO, white balance, focus mode, file format)
- Before the final `newState` return statement
- Around line 622

**Why:**
- `_focusDistanceM` is already defined (line 26-27) but never populated
- FocusDistanceOverlay already observes this StateFlow (line 223 in SonyRemoteControlScreen.kt)
- Once populated, overlay will automatically display

---

## JSON Data Structure Reference

**UDP Status Broadcast from Air-Side:**
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 12345,
  "timestamp": 1730844000,
  "payload": {
    "system": { ... },
    "camera": {
      "connected": true,
      "model": "ILCE-1",
      "battery_percent": 85,
      "remaining_shots": 1234,
      "settings": {
        "shutter_speed": "1/250",
        "aperture": "5.6",
        "iso": "400",
        "white_balance": "Auto",
        "focus_mode": "AF-S",
        "file_format": "RAW+JPEG",
        "focal_distance_meters": 5.2    <-- NEW FIELD
      }
    },
    "gimbal": { ... }
  }
}
```

**Field Values:**
- `5.2` = Focused at 5.2 meters
- `12.5` = Focused at 12.5 meters
- `-1.0` = Focused at infinity (∞)
- `0.0` = Unknown/query failed
- Field absent or `null` = Camera disconnected or property unavailable

---

## Testing Checklist

### Unit Testing:
- [ ] SimpleCameraSettings parses focal_distance_meters from JSON correctly
- [ ] Null values handled gracefully (no crashes)
- [ ] Negative values (-1) parsed correctly for infinity
- [ ] Zero values (0.0) handled as unknown

### Integration Testing:
- [ ] Connect to Air-Side with camera attached
- [ ] Verify FocusDistanceOverlay appears when camera connected
- [ ] Focus camera at known distance (e.g., 5 meters)
- [ ] Verify overlay displays correct distance
- [ ] Focus to infinity, verify "∞" displayed
- [ ] Disconnect camera, verify overlay disappears

### UI/UX Testing:
- [ ] Progress bar moves smoothly as focus changes
- [ ] Distance text updates in real-time (5 Hz from UDP)
- [ ] Overlay positioned correctly (bottom center of video feed)
- [ ] No UI lag or stuttering during focus changes
- [ ] Overlay style matches other overlays (transparency, colors)

---

## Verification Commands

### Check UDP Broadcasts on Ground-Side:

If you want to verify the UDP JSON contains focal_distance_meters before implementing:

```bash
# On Android device (via adb):
adb shell
su  # if rooted
tcpdump -i wlan0 -A port 5001 | grep -A 50 "focal_distance"

# Or on Air-Side Pi:
docker logs payload-manager | grep "Sent UDP status" | tail -5
```

### Check Air-Side is Broadcasting Correctly:

```bash
# On Air-Side Pi:
docker logs payload-manager 2>&1 | grep "focal_distance_meters" | head -10

# Should see logs with focal distance values in JSON
```

---

## Expected Behavior After Fix

### When Camera Disconnected:
- FocusDistanceOverlay: Hidden (null data)
- StateFlow value: `null`

### When Camera Connected - Close Focus (0.5m):
- FocusDistanceOverlay: Shows "50cm" with progress bar at ~15%
- StateFlow value: `0.5f`

### When Camera Connected - Portrait Focus (5m):
- FocusDistanceOverlay: Shows "5.0m" with progress bar at ~55%
- StateFlow value: `5.0f`

### When Camera Connected - Infinity Focus:
- FocusDistanceOverlay: Shows "∞" with progress bar at 100%
- StateFlow value: `-1.0f`

### When Focus Query Fails:
- FocusDistanceOverlay: Hidden (or shows "Unknown")
- StateFlow value: `0.0f` or `null`

---

## Related Files (No Changes Needed)

These files are already correct and work with the fix:

**✅ FocusDistanceOverlay.kt (lines 26-98)**
- Already accepts `Float?` parameter
- Already handles null (hides overlay)
- Already handles -1 (displays "∞")
- Already formats distances correctly
- Already has progress bar logic

**✅ SonyRemoteControlScreen.kt (lines 223-228)**
- Already observes `viewModel.focusDistanceM`
- Already passes to FocusDistanceOverlay
- Positioned correctly (BottomCenter)

**✅ CameraViewModel.kt (lines 26-27)**
- Already has `_focusDistanceM` StateFlow defined
- Just needs population via sync

---

## Dependencies

### Required:
- ✅ Air-Side focal distance fix deployed (commit TBD)
- ✅ Air-Side container rebuilt and running
- ✅ UDP broadcast working (5 Hz status updates)

### Optional:
- Kotlin Serialization (already in use)
- StateFlow/Compose (already in use)

---

## Estimated Effort

**Total:** 15-30 minutes

1. **ProtocolMessages.kt update:** 2 minutes
   - Add one line to data class

2. **CameraViewModel.kt update:** 5 minutes
   - Add sync block for focal distance

3. **Build and deploy:** 5 minutes
   - Gradle build
   - Install APK on device

4. **Testing:** 10-15 minutes
   - Connect to Air-Side
   - Test various focus distances
   - Verify overlay behavior

---

## Success Criteria

**This issue is complete when:**

1. ✅ SimpleCameraSettings includes `focalDistanceMeters` field
2. ✅ syncCameraSettings() populates `_focusDistanceM` StateFlow
3. ✅ FocusDistanceOverlay displays real-time focal distance
4. ✅ Overlay updates at 5 Hz with UDP broadcasts
5. ✅ Infinity focus displays as "∞"
6. ✅ Close focus displays in cm (e.g., "50cm")
7. ✅ Medium/far focus displays in meters (e.g., "5.2m")
8. ✅ Progress bar animates correctly
9. ✅ No crashes or UI glitches
10. ✅ Feature tested with real Sony A1 camera

---

## Notes

### Why focal_distance_meters was missing:

When the camera settings sync was first implemented, the Sony SDK's `getFocalDistanceMeters()` function was never integrated into the status broadcast. The Air-Side code had the capability to query focal distance, but never included it in the CameraStatus struct sent via UDP.

This has now been fixed on Air-Side (2025-11-05), so Ground-Side just needs to parse and display the new field.

### Air-Side Implementation Details:

**Air-Side changes made:**
1. Added `float focal_distance_meters` to CameraStatus struct (messages.h:134)
2. Added field to JSON serialization (messages.h:153)
3. Updated getStatus() to call getFocalDistanceMeters() (camera_sony.cpp:294)
4. Rebuilt container and restarted

**Air-Side commit:** TBD (will be committed with [AIR-SIDE][FIX] prefix)

---

## Contact / Questions

If you encounter issues:
1. Check Air-Side is running latest container: `docker ps | grep payload-manager`
2. Verify UDP broadcasts contain focal_distance_meters: `docker logs payload-manager | grep focal`
3. Check Ground-Side receives UDP: Settings → Network → Connection Status
4. Enable verbose logging in CameraViewModel: Change Log.d to Log.i for sync messages

---

**Issue Created:** 2025-11-05
**Air-Side Fixed:** 2025-11-05
**Ground-Side Status:** Ready for implementation
**Assignee:** Ground-Side Developer
**Milestone:** Focus Distance Feature Completion
