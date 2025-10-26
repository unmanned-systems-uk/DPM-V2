# Camera Status Synchronization

**Last Updated:** 2025-10-26
**Protocol Version:** 1.1
**Status:** Implemented ✅

## Overview

The Air Side automatically queries the camera's current settings when the camera connects and includes them in **every** status broadcast (5 Hz UDP messages). This allows the Ground Side (Android app) to **synchronize its UI with the actual camera state** on startup and maintain accuracy during operation.

## Use Case

**Problem:** When the Android app connects to the Air Side, the UI shows default values, not what the camera is actually set to.

**Solution:** The status broadcast now includes current camera settings, so the app can:
1. Display correct values immediately on connection
2. Update UI when camera settings change externally (e.g., manual camera adjustment)
3. Maintain synchronization without polling

---

## Status Broadcast Format

### UDP Status Message (5 Hz broadcast to 192.168.144.11:5001)

```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 42,
  "timestamp": 1698765432,
  "payload": {
    "system": {
      "uptime_seconds": 3600,
      "cpu_percent": 25.5,
      "memory_mb": 512,
      "memory_total_mb": 4096,
      "disk_free_gb": 50.5,
      "network_rx_mbps": 0.5,
      "network_tx_mbps": 1.2
    },
    "camera": {
      "connected": true,
      "model": "ILCE-1",
      "battery_percent": 75,
      "remaining_shots": 1234,
      "settings": {
        "shutter_speed": "1/1000",
        "aperture": "f/5.6",
        "iso": "400",
        "white_balance": "auto",
        "focus_mode": "auto",
        "file_format": "raw+jpeg"
      }
    },
    "gimbal": {
      "connected": false
    }
  }
}
```

### Camera Not Connected

When the camera is not connected, the `settings` object is **omitted**:

```json
{
  "camera": {
    "connected": false,
    "model": "none",
    "battery_percent": 0,
    "remaining_shots": 0
    // No "settings" object
  }
}
```

---

## Android Implementation

### 1. Parse Status Messages

Update your status message parser to handle the new `settings` object:

```kotlin
data class CameraSettings(
    val shutterSpeed: String,
    val aperture: String,
    val iso: String,
    val whiteBalance: String,
    val focusMode: String,
    val fileFormat: String
)

data class CameraStatus(
    val connected: Boolean,
    val model: String,
    val batteryPercent: Int,
    val remainingShots: Int,
    val settings: CameraSettings? = null  // Null when not connected
)

fun parseStatusMessage(json: JSONObject): CameraStatus {
    val cameraJson = json.getJSONObject("payload").getJSONObject("camera")

    return CameraStatus(
        connected = cameraJson.getBoolean("connected"),
        model = cameraJson.getString("model"),
        batteryPercent = cameraJson.getInt("battery_percent"),
        remainingShots = cameraJson.getInt("remaining_shots"),
        settings = if (cameraJson.has("settings")) {
            val settingsJson = cameraJson.getJSONObject("settings")
            CameraSettings(
                shutterSpeed = settingsJson.getString("shutter_speed"),
                aperture = settingsJson.getString("aperture"),
                iso = settingsJson.getString("iso"),
                whiteBalance = settingsJson.getString("white_balance"),
                focusMode = settingsJson.getString("focus_mode"),
                fileFormat = settingsJson.getString("file_format")
            )
        } else null
    )
}
```

### 2. Update UI When Settings Arrive

```kotlin
private fun handleCameraStatus(status: CameraStatus) {
    if (status.connected && status.settings != null) {
        // Update UI to match camera settings
        updateShutterSpeedSelector(status.settings.shutterSpeed)
        updateApertureSelector(status.settings.aperture)
        updateIsoSelector(status.settings.iso)
        updateWhiteBalanceSelector(status.settings.whiteBalance)
        updateFocusModeSelector(status.settings.focusMode)
        updateFileFormatSelector(status.settings.fileFormat)

        Log.d(TAG, "Camera settings synchronized: ${status.settings}")
    } else {
        // Camera disconnected - show disabled/default state
        disableCameraControls()
    }
}
```

### 3. Initial Synchronization Flow

```kotlin
// When connection is established
fun onConnected() {
    // Status broadcasts happen automatically at 5 Hz
    // Just listen for the first status message with camera settings

    statusMessageReceiver.setOnStatusReceivedListener { status ->
        if (firstConnectionSync && status.camera.connected) {
            // First status received - synchronize UI
            handleCameraStatus(status.camera)
            firstConnectionSync = false
            Log.i(TAG, "Initial camera settings synchronized")
        } else {
            // Subsequent updates - keep UI in sync
            handleCameraStatus(status.camera)
        }
    }
}
```

### 4. Handle UI Changes vs Camera Changes

To prevent feedback loops when user changes settings:

```kotlin
private var userTriggeredChange = false

fun onUserChangedShutterSpeed(newValue: String) {
    userTriggeredChange = true
    sendCameraCommand("set_property", "shutter_speed", newValue)
    // Will receive confirmation in next status broadcast
}

private fun updateShutterSpeedSelector(value: String) {
    if (!userTriggeredChange) {
        // Only update UI if NOT a user-triggered change
        // (to avoid fighting with user input)
        shutterSpeedSpinner.setSelection(value)
    }
    userTriggeredChange = false  // Reset flag
}
```

---

## Settings Values

### shutter_speed
**Type:** String
**Values:** `"1/8000"` to `"1/3"` (35 speeds), or `"auto"`
**Example:** `"1/1000"`

See `CAMERA_SHUTTER_SPEEDS.md` for complete list.

### aperture
**Type:** String
**Values:** `"f/1.4"` to `"f/22"` (camera-dependent), or `"auto"`
**Example:** `"f/5.6"`

### iso
**Type:** String
**Values:** `"100"`, `"200"`, `"400"`, `"800"`, `"1600"`, `"3200"`, etc., or `"auto"`
**Example:** `"400"`

### white_balance
**Type:** String
**Values:** `"auto"`, `"daylight"`, `"cloudy"`, `"tungsten"`, `"fluorescent"`, `"flash"`, `"custom"`
**Example:** `"auto"`
**Note:** Currently returns empty string (`""`) - implementation pending

### focus_mode
**Type:** String
**Values:** `"auto"`, `"manual"`, `"continuous"`
**Example:** `"auto"`
**Note:** Currently returns empty string (`""`) - implementation pending

### file_format
**Type:** String
**Values:** `"jpeg"`, `"raw"`, `"raw+jpeg"`
**Example:** `"raw+jpeg"`
**Note:** Currently returns empty string (`""`) - implementation pending

---

## Empty String Handling

Properties not yet implemented (white_balance, focus_mode, file_format) return empty string (`""`):

```kotlin
fun handleSetting(value: String) {
    when {
        value.isEmpty() -> {
            // Property not yet implemented on air side
            // Show disabled/unavailable state
            disableControl()
        }
        value == "unknown" -> {
            // Air side couldn't read property from camera
            // Show error state
            showErrorState()
        }
        else -> {
            // Valid value - update UI
            updateControl(value)
        }
    }
}
```

---

## Broadcast Frequency

- **Rate:** 5 Hz (every 200ms)
- **Destination:** 192.168.144.11:5001 (UDP broadcast)
- **Automatic:** Starts when Air Side service starts

### Performance Considerations

- Settings are queried from camera every broadcast (5 times per second)
- If this becomes too slow, consider:
  - Caching settings and only querying on change
  - Reducing broadcast rate
  - Querying properties less frequently

---

## Testing

### 1. Verify Initial Synchronization

**Steps:**
1. Set camera to specific values (e.g., shutter: 1/500, aperture: f/8, ISO: 800)
2. Start Air Side service
3. Connect Android app
4. **Verify:** App displays correct initial values

### 2. Verify External Changes

**Steps:**
1. Connect Android app to Air Side
2. Manually change camera setting using camera dial
3. **Verify:** App UI updates within 200ms

### 3. Verify User Changes

**Steps:**
1. Change setting in Android app
2. **Verify:** Command succeeds
3. **Verify:** Next status broadcast confirms new value
4. **Verify:** UI shows new value

---

## Error Handling

### Camera Disconnected

```kotlin
if (!status.camera.connected) {
    // Disable all camera controls
    disableAllCameraControls()
    showMessage("Camera disconnected")
}
```

### Property Read Failed

If Air Side cannot read a property, it returns `"unknown"`:

```kotlin
if (settings.shutterSpeed == "unknown") {
    showError("Could not read shutter speed from camera")
}
```

### Unsupported Property

Not-yet-implemented properties return empty string:

```kotlin
if (settings.focusMode.isEmpty()) {
    // Focus mode not yet implemented
    hideFocusModeControl()  // Or show as disabled
}
```

---

## Future Enhancements

### Phase 2
- Implement `white_balance` property querying
- Implement `focus_mode` property querying
- Implement `file_format` property querying

### Phase 3
- Add camera mode (M, A, S, P, Auto)
- Add exposure compensation
- Add metering mode
- Add drive mode (single, continuous, timer)

---

## Related Documentation

- `CAMERA_SHUTTER_SPEEDS.md` - Complete shutter speed reference
- `/sbc/src/protocol/messages.h` - CameraStatus structure definition
- `/sbc/src/camera/camera_sony.cpp` - Property query implementation

---

## Implementation Notes

**Air Side:**
- Settings queried in `CameraSony::getStatus()` (camera_sony.cpp:210-248)
- Settings added to UDP broadcast in `UDPBroadcaster::sendStatus()` (udp_broadcaster.cpp:101-151)
- Broadcast happens automatically at 5 Hz

**Ground Side:**
- Parse `settings` object from status messages
- Update UI when `settings` values change
- Handle empty/unknown values gracefully
- Prevent UI feedback loops when user changes settings

---

**Status:** ✅ **Ready for Android Integration**
