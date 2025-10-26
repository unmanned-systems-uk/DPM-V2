# Camera Shutter Speed Values - Sony Alpha 1

**Last Updated:** 2025-10-26
**Status:** Tested and Verified ✅

## Supported Shutter Speed Range

The Sony Alpha 1 in **Manual (M) mode** supports **35 shutter speed values** from 1/8000 to 1/3 second.

### Complete List of Supported Values

```json
{
  "shutter_speeds": [
    "1/8000", "1/6400", "1/5000", "1/4000", "1/3200", "1/2500",
    "1/2000", "1/1600", "1/1250", "1/1000", "1/800",  "1/640",
    "1/500",  "1/400",  "1/320",  "1/250",  "1/200",  "1/160",
    "1/125",  "1/100",  "1/80",   "1/60",   "1/50",   "1/40",
    "1/30",   "1/25",   "1/20",   "1/15",   "1/13",   "1/10",
    "1/8",    "1/6",    "1/5",    "1/4",    "1/3"
  ]
}
```

## Format for `camera.set_property` Command

### Protocol Message Format
```json
{
  "protocol_version": "1.1",
  "message_type": "command",
  "sequence_id": 123,
  "timestamp": 1698765432,
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "shutter_speed",
      "value": "1/1000"
    }
  }
}
```

### Valid String Values
Send the shutter speed as a **string** in fraction format:
- Fast: `"1/8000"`, `"1/6400"`, `"1/5000"`, etc.
- Medium: `"1/1000"`, `"1/500"`, `"1/250"`, etc.
- Slow: `"1/30"`, `"1/15"`, `"1/8"`, `"1/4"`, `"1/3"`

### Auto Mode
```json
{
  "property": "shutter_speed",
  "value": "auto"
}
```

## Not Supported

### Long Exposures (>0.5 seconds)
Long exposures beyond 1/2 second are **NOT** supported via the `shutter_speed` property in Manual mode:
- ❌ `"0.4"`, `"0.5"`, `"0.6"`, `"0.8"`, `"1.0"`, etc.
- ❌ `"2.0"`, `"4.0"`, `"8.0"`, `"15.0"`, `"30.0"`

These require:
- **Bulb (B) mode** on the camera
- A different API call for bulb exposure control
- Future implementation in Phase 2

### Bulb Mode
BULB mode is a separate camera mode, not a shutter speed value:
- ❌ Cannot set via `camera.set_property`
- Requires mode change + exposure timing control
- Planned for future implementation

## SDK Implementation Details

### Air Side Encoding (Internal)
The air-side (Raspberry Pi) converts human-readable strings to Sony SDK format:

**Format:** `0xNNNNDDDD`
- `NNNN` = Numerator (upper 2 bytes)
- `DDDD` = Denominator (lower 2 bytes)

For fraction speeds, numerator is always `0x0001`:

| Display  | SDK Value    | Calculation              |
|----------|--------------|--------------------------|
| 1/8000   | 0x00011F40   | 0x0001 / 0x1F40 (8000)   |
| 1/1000   | 0x000103E8   | 0x0001 / 0x03E8 (1000)   |
| 1/250    | 0x000100FA   | 0x0001 / 0x00FA (250)    |
| 1/60     | 0x0001003C   | 0x0001 / 0x003C (60)     |
| 1/3      | 0x00010003   | 0x0001 / 0x0003 (3)      |

**Important:** Ground-side apps should use **string values** only (e.g., `"1/1000"`), NOT hex values.

## Testing Results

### Verified Working (2025-10-26)
- ✅ All 35 speeds from 1/8000 to 1/3 tested and confirmed
- ✅ Values change immediately on camera LCD
- ✅ Readback verification matches set value
- ✅ No errors or warnings

### Verified Not Working
- ❌ Long exposures (0.4" to 30") return error or no effect
- ❌ Values require different camera mode or API

## Android App Integration

### UI Recommendations

**Speed Selector Options:**
1. **Preset buttons** for common speeds:
   - 1/8000, 1/4000, 1/2000, 1/1000, 1/500, 1/250, 1/125, 1/60, 1/30, 1/15

2. **Dropdown/Picker** with all 35 speeds

3. **Quick +/- buttons** to step through available speeds

### Example Android Code

```kotlin
val supportedShutterSpeeds = listOf(
    "1/8000", "1/6400", "1/5000", "1/4000", "1/3200", "1/2500",
    "1/2000", "1/1600", "1/1250", "1/1000", "1/800",  "1/640",
    "1/500",  "1/400",  "1/320",  "1/250",  "1/200",  "1/160",
    "1/125",  "1/100",  "1/80",   "1/60",   "1/50",   "1/40",
    "1/30",   "1/25",   "1/20",   "1/15",   "1/13",   "1/10",
    "1/8",    "1/6",    "1/5",    "1/4",    "1/3"
)

fun setShutterSpeed(speed: String) {
    if (speed !in supportedShutterSpeeds && speed != "auto") {
        // Invalid value - show error
        return
    }

    // Send command to air side
    sendCommand("camera.set_property", mapOf(
        "property" to "shutter_speed",
        "value" to speed
    ))
}
```

### Validation

Always validate user input against the supported list:
```kotlin
fun isValidShutterSpeed(value: String): Boolean {
    return value == "auto" || value in supportedShutterSpeeds
}
```

## Response Format

### Success Response
```json
{
  "protocol_version": "1.1",
  "message_type": "response",
  "sequence_id": 123,
  "timestamp": 1698765433,
  "payload": {
    "command": "camera.set_property",
    "status": "success",
    "result": {
      "property": "shutter_speed",
      "value": "1/1000",
      "status": "success"
    }
  }
}
```

### Error Response
```json
{
  "protocol_version": "1.1",
  "message_type": "response",
  "sequence_id": 123,
  "timestamp": 1698765433,
  "payload": {
    "command": "camera.set_property",
    "status": "error",
    "error_code": 4001,
    "error_message": "Invalid shutter speed value: 0.5"
  }
}
```

## Query Current Value

Use `camera.get_properties` to read current shutter speed:

```json
{
  "command": "camera.get_properties",
  "parameters": {
    "properties": ["shutter_speed"]
  }
}
```

Response:
```json
{
  "status": "success",
  "result": {
    "shutter_speed": "1/1000"
  }
}
```

## Future Enhancements

1. **Bulb Mode Support** (Phase 2)
   - Add mode switching capability
   - Add exposure timing control
   - Support for exposures > 30 seconds

2. **Auto Mode Detection** (Phase 2)
   - Query available speeds based on current lighting
   - Suggest optimal shutter speed

3. **Exposure Compensation** (Phase 2)
   - Allow fine-tuning within a shutter speed

## Related Properties

- **Aperture:** See `CAMERA_APERTURE_VALUES.md`
- **ISO:** See `CAMERA_ISO_VALUES.md`
- **Exposure Mode:** See `CAMERA_MODES.md` (future)

---

**For questions or issues, refer to:**
- `/docs/TEMP_Property_Mapping_Process.md` - Complete discovery journey
- `/sbc/src/camera/camera_sony.cpp` - Implementation details
