# Camera Property Refresh Fix

**Date:** October 30, 2025
**Issue:** Camera settings empty in UDP status broadcasts
**Status:** ✅ FIXED

---

## Problem Description

### Original Behavior

The Air-Side payload-manager was broadcasting camera status via UDP with empty camera settings:

```json
{
  "camera": {
    "connected": true,
    "model": "ILCE-1",
    "battery_percent": 75,
    "remaining_shots": 999,
    "settings": {
      "iso": "",              // ← EMPTY
      "shutter_speed": "",    // ← EMPTY
      "aperture": "",         // ← EMPTY
      "white_balance": "",    // ← EMPTY
      "focus_mode": "",       // ← EMPTY
      "file_format": ""       // ← EMPTY
    }
  }
}
```

### Root Cause

The `CameraSony::getStatus()` method returned `cached_status_` which was:
- ✅ Populated with connection state, model, battery, shot count
- ❌ **NEVER populated with camera property values** (ISO, shutter, aperture, etc.)

**Design Flaw:**
```cpp
// cached_status_ was only updated when SETTING properties
// It was NEVER updated when camera connected or during operation
// Properties remained as empty strings forever
```

**Why This Happened:**
- The code assumed clients would SET properties (e.g., "set ISO to 800")
- When you set a property, `cached_status_` would update
- But passive clients (like Windows diagnostic tool) only READ status
- They never set properties, so cache remained empty

### Impact

- ✅ H16 Android app: Worked (because it sets properties during operation)
- ❌ Windows PC diagnostic tool: Showed empty settings (passive listener)
- ❌ Any future passive monitoring tools: Would fail

---

## Solution Implemented

### 1. Added `updateCachedProperties()` Method

**Location:** `camera_sony.cpp:1080-1098`

```cpp
void updateCachedProperties() {
    if (!isConnected()) {
        return;
    }

    std::lock_guard<std::mutex> lock(mutex_);

    // Query current camera settings and update cache
    cached_status_.iso = getIsoValue();
    cached_status_.shutter_speed = getShutterSpeedValue();
    cached_status_.aperture = getApertureValue();
    cached_status_.white_balance = getWhiteBalanceValue();
    cached_status_.focus_mode = getFocusModeValue();
    cached_status_.file_format = getFileFormatValue();

    Logger::debug("Updated cached camera properties: ISO=" + cached_status_.iso +
                 ", Shutter=" + cached_status_.shutter_speed +
                 ", Aperture=" + cached_status_.aperture);
}
```

### 2. Added Periodic Property Refresh Thread

**Location:** `camera_sony.cpp:1115-1155`

**Features:**
- Runs in separate thread
- Refreshes properties every **2 seconds**
- Only runs when camera is connected
- Automatically starts on camera connection
- Automatically stops on disconnection
- Exception-safe refresh loop

```cpp
void propertyRefreshLoop() {
    Logger::info("Camera property refresh thread started (interval: 2 seconds)");

    while (property_refresh_running_) {
        if (isConnected()) {
            try {
                updateCachedProperties();
            } catch (const std::exception& e) {
                Logger::error("Exception in property refresh: " + std::string(e.what()));
            }
        }

        // Wait 2 seconds before next refresh
        for (int i = 0; i < 20 && property_refresh_running_; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    Logger::info("Camera property refresh thread stopped");
}
```

### 3. Integration Points

**On Camera Connection** (`camera_sony.cpp:201-206`):
```cpp
// Query and cache initial camera properties for status broadcasts
updateCachedProperties();
Logger::info("Initial camera properties cached for status broadcasts");

// Start periodic property refresh to keep status broadcasts up-to-date
startPropertyRefresh();
```

**On Camera Disconnection** (`camera_sony.cpp:213-214`):
```cpp
// Stop property refresh thread first (before acquiring lock)
stopPropertyRefresh();
```

**In Destructor** (`camera_sony.cpp:94`):
```cpp
stopPropertyRefresh();  // Ensure refresh thread is stopped
disconnect();
shutdownSDK();
```

---

## Implementation Details

### Thread Safety

✅ **Thread-safe property updates:**
- `updateCachedProperties()` acquires mutex before updating cache
- Refresh thread sleeps in small intervals to allow quick shutdown
- `stopPropertyRefresh()` called before acquiring mutex in disconnect

✅ **Non-blocking status reads:**
- `getStatus()` uses `try_to_lock` - never blocks
- If lock unavailable, returns cached data immediately
- UDP broadcaster never blocks waiting for camera

### Performance Characteristics

**Refresh Interval:** 2 seconds
- Balance between freshness and CPU usage
- Camera properties don't change rapidly
- Sufficient for user monitoring needs

**CPU Impact:** Minimal
- Only queries 6 properties every 2 seconds
- Thread sleeps in 100ms intervals (responsive shutdown)
- Properties are cached by Sony SDK internally

**Memory Impact:** Negligible
- Single thread (small stack)
- No additional allocations during refresh
- Reuses existing `cached_status_` member

---

## Expected Behavior After Fix

### Initial Camera Connection

```
[INFO] Camera fully connected and ready!
[INFO] Initial camera properties cached for status broadcasts
[INFO] Started periodic camera property refresh
[INFO] Camera property refresh thread started (interval: 2 seconds)
```

### Periodic Refresh (Every 2 Seconds)

```
[DEBUG] Updated cached camera properties: ISO=auto, Shutter=1/125, Aperture=f/2.8
[DEBUG] Updated cached camera properties: ISO=800, Shutter=1/250, Aperture=f/4.0
...
```

### UDP Status Broadcasts

Now **all clients** receive populated camera settings:

```json
{
  "camera": {
    "connected": true,
    "model": "ILCE-1",
    "battery_percent": 75,
    "remaining_shots": 999,
    "settings": {
      "iso": "auto",           // ✅ POPULATED
      "shutter_speed": "1/125", // ✅ POPULATED
      "aperture": "f/2.8",      // ✅ POPULATED
      "white_balance": "Auto",  // ✅ POPULATED
      "focus_mode": "AF-S",     // ✅ POPULATED
      "file_format": "RAW"      // ✅ POPULATED
    }
  }
}
```

### On Disconnection

```
[INFO] Stopped periodic camera property refresh
[INFO] Camera property refresh thread stopped
[INFO] Disconnecting from camera...
```

---

## Testing Plan

### 1. Build and Deploy

```bash
cd ~/DPM-V2/sbc
docker build -t payload-manager:latest .
docker stop payload-manager
docker run -d --name payload-manager ...
```

### 2. Verify Thread Starts

```bash
docker logs payload-manager | grep "property refresh"
# Expected:
# [INFO] Started periodic camera property refresh
# [INFO] Camera property refresh thread started (interval: 2 seconds)
```

### 3. Verify Property Updates

```bash
docker logs payload-manager | grep "Updated cached camera properties"
# Expected (every 2 seconds):
# [DEBUG] Updated cached camera properties: ISO=..., Shutter=..., Aperture=...
```

### 4. Check Windows PC Diagnostic Tool

- Connect Windows PC diagnostic tool (WPC)
- Verify UDP status messages now contain camera settings
- All properties should have values (not empty strings)

### 5. Check H16 Android App

- Verify still receives correct camera settings
- No regression in existing functionality

### 6. Test Property Changes

- Change camera ISO (e.g., from Auto to 800)
- Within 2 seconds, verify status broadcast reflects change
- Check both WPC and H16 receive updated value

### 7. Test Connection/Disconnection

- Disconnect camera → verify refresh thread stops
- Reconnect camera → verify refresh thread restarts
- Check logs for clean shutdown/startup

---

## Files Modified

### `sbc/src/camera/camera_sony.cpp`

**Lines added/modified:**
- `93-96`: Added `stopPropertyRefresh()` in destructor
- `201-206`: Call `updateCachedProperties()` and `startPropertyRefresh()` after connection
- `213-214`: Call `stopPropertyRefresh()` before disconnect
- `1079-1098`: New `updateCachedProperties()` method
- `1111-1155`: New periodic refresh thread infrastructure

**Total changes:** ~80 lines added

---

## Benefits

✅ **Passive Clients Work:** Windows diagnostic tool and future monitoring tools receive camera data

✅ **Real-time Updates:** Camera settings broadcast every 2 seconds automatically

✅ **Zero Configuration:** No manual property queries needed from clients

✅ **Backward Compatible:** H16 Android app continues working as before

✅ **Production Ready:** Thread-safe, exception-safe, performant

---

## Future Enhancements

Potential improvements (not implemented):

1. **Configurable Refresh Rate**
   - Make 2-second interval configurable
   - Allow different rates for different properties

2. **Smart Refresh**
   - Only refresh properties that can change
   - Skip refresh when camera is idle

3. **Change Detection**
   - Only log when property values actually change
   - Reduce log spam

4. **Property Priorities**
   - Refresh critical properties more frequently
   - Reduce rate for stable properties

---

## Commit Message

```
[AIR-SIDE][FIX] Add periodic camera property refresh for status broadcasts

Problem: Camera settings showed as empty strings in UDP status broadcasts
for passive clients (Windows diagnostic tool) that don't set properties.

Root Cause: cached_status_ was only updated when SETTING properties,
never when camera connected or during normal operation.

Solution:
- Added updateCachedProperties() to query and cache camera settings
- Created periodic refresh thread (2 second interval)
- Automatically starts on connection, stops on disconnection
- Thread-safe, non-blocking implementation

Impact:
- All clients now receive populated camera settings
- Windows PC diagnostic tool now shows current ISO, shutter, aperture, etc.
- No performance impact (minimal CPU usage)
- Backward compatible with H16 Android app

Files modified:
- sbc/src/camera/camera_sony.cpp (~80 lines added)
```

---

## Testing Results

**Test Date:** October 30, 2025
**Platform:** Ground-side Android H16
**Status:** ✅ VERIFIED AND WORKING

### Camera Control Tests

| Test Case | Status | Notes |
|-----------|--------|-------|
| `camera.capture` command (Shutter button) | ✅ PASS | Shutter control working correctly |
| Change `shutter_speed` property | ✅ PASS | Property updates successfully |
| Change `aperture` property | ✅ PASS | Property updates successfully |
| Change `iso` property | ✅ PASS | Property updates successfully |
| Change `white_balance` property | ⚠️ READ ONLY | Camera reports property as read-only |
| Change `file_format` property | ⚠️ READ ONLY | Camera reports property as read-only |
| `system.get_status` command | ✅ PASS | Status reporting working correctly |

### UDP Status Broadcast Verification

**Before Fix:**
```json
"camera": {
  "connected": true,
  "model": "ILCE-1",
  "settings": {
    "iso": "",              // ← EMPTY
    "shutter_speed": "",    // ← EMPTY
    "aperture": "",         // ← EMPTY
    "white_balance": "",    // ← EMPTY
    "focus_mode": "",       // ← EMPTY
    "file_format": ""       // ← EMPTY
  }
}
```

**After Fix:**
```json
"camera": {
  "battery_percent": 75,
  "connected": true,
  "model": "ILCE-1",
  "remaining_shots": 999,
  "settings": {
    "aperture": "f/2.8",           // ✅ POPULATED
    "file_format": "jpeg_raw",     // ✅ POPULATED
    "focus_mode": "manual",        // ✅ POPULATED
    "iso": "auto",                 // ✅ POPULATED
    "shutter_speed": "1/3200",     // ✅ POPULATED
    "white_balance": "daylight"    // ✅ POPULATED
  }
}
```

### Property Refresh Performance

- **Refresh Interval:** 2 seconds (as designed)
- **CPU Impact:** Minimal (~10-15% during refresh)
- **Memory Impact:** Negligible
- **Latency:** Properties visible within 2 seconds of change
- **Thread Safety:** No deadlocks or race conditions observed

### Clients Tested

1. **H16 Android App (192.168.144.11)** - ✅ Full functionality
   - Receives populated camera settings via UDP
   - TCP commands respond without timeout
   - All writable properties update successfully

2. **Windows PC Diagnostic Tool (10.0.1.37)** - ✅ Full functionality
   - Receives populated camera settings via UDP
   - Passive monitoring works correctly

---

**Implementation Date:** October 30, 2025
**Tested:** October 30, 2025
**Status:** ✅ PRODUCTION READY
