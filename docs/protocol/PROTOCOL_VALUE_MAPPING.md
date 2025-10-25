# Protocol Value Mapping Specification
**DPM Camera Properties Protocol Design**

**Version:** 1.0  
**Date:** October 25, 2025  
**Status:** ✅ **APPROVED - Option B Implementation**

---

## 🎯 Critical Design Decision

### The Question:
How should camera property values be transmitted in the protocol?
- Send Sony SDK raw values (e.g., `0x00010001`)?
- Send human-readable values (e.g., `"1/8000"`)?

### The Answer: **Human-Readable Values (Option B)**

**Protocol uses human-readable strings. Air-side handles conversion to Sony SDK format.**

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GROUND STATION                          │
│                                                                 │
│  User selects: "1/8000" from dropdown                          │
│         ↓                                                       │
│  ViewModel: setCameraProperty("shutter_speed", "1/8000")       │
│         ↓                                                       │
│  NetworkClient: Sends JSON command                             │
│         ↓                                                       │
└─────────────────────────────────────────────────────────────────┘
                           │
                   Protocol Message
                   {
                     "command": "camera.set_property",
                     "parameters": {
                       "property": "shutter_speed",
                       "value": "1/8000"  ← Human-readable!
                     }
                   }
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                          AIR-SIDE (SBC)                         │
│                                                                 │
│  TCP Server receives: "shutter_speed", "1/8000"                │
│         ↓                                                       │
│  handleCameraSetProperty() routes to setShutterSpeed()         │
│         ↓                                                       │
│  Mapping Table: "1/8000" → 0x00010001                         │
│         ↓                                                       │
│  Sony SDK: SetDeviceProperty(ShutterSpeed, 0x00010001)        │
│         ↓                                                       │
│  Camera applies setting                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Why Option B (Human-Readable Values)?

### 1. Protocol Simplicity
- ✅ Human-readable and debuggable
- ✅ Network captures show: `"shutter_speed": "1/8000"`
- ✅ Not: `"shutter_speed": 65537` (meaningless hex)
- ✅ Easier to validate and test

### 2. Separation of Concerns
- **Ground-side:** UI/UX layer (knows display values only)
- **Protocol:** Transport layer (camera-agnostic)
- **Air-side:** Hardware abstraction (knows Sony SDK specifics)

### 3. Future-Proofing
- ✅ Camera-agnostic protocol
- ✅ Switching to different camera? Only air-side changes
- ✅ Multiple camera support easier
- ✅ Web interface doesn't need Sony SDK knowledge

### 4. Testing & Debugging
- ✅ Test ground-side without real camera
- ✅ Mock air-side with readable values
- ✅ Logs are human-readable
- ✅ Error messages make sense

### 5. Error Handling
- ✅ User sees: "Invalid shutter speed: 1/8001"
- ❌ Not: "Invalid shutter speed: 0x00010002"

---

## 🚫 Rejected Alternatives

### Option A: Ground-side converts (REJECTED)
```kotlin
// Ground-side would need Sony SDK mappings
fun setShutterSpeed(value: String) {
    val sonyValue = mapToSonySDK(value)  // 0x00010001
    setCameraProperty("shutter_speed", sonyValue)
}
```

**Why rejected:**
- ❌ Couples Android app to Sony SDK
- ❌ Can't support different cameras easily
- ❌ Protocol becomes less readable
- ❌ Harder to test without camera knowledge

### Option C: Send both formats (REJECTED)
```json
{
  "shutter_speed": {
    "display_value": "1/8000",
    "sony_sdk_value": "0x00010001"
  }
}
```

**Why rejected:**
- ❌ Redundant data in every message
- ❌ Must keep two values in sync
- ❌ Wastes bandwidth
- ❌ Error-prone

---

## 📐 Implementation Specification

### Protocol Message Format

**Command:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 123,
  "timestamp": 1729339200,
  "payload": {
    "command": "camera.set_property",
    "parameters": {
      "property": "shutter_speed",
      "value": "1/8000"
    }
  }
}
```

**Response (Success):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 123,
  "timestamp": 1729339201,
  "payload": {
    "status": "success",
    "property": "shutter_speed",
    "value": "1/8000",
    "confirmed": true
  }
}
```

**Response (Error):**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 123,
  "timestamp": 1729339201,
  "payload": {
    "status": "error",
    "error_code": 1005,
    "error_message": "Invalid shutter speed value: '1/8001'. Valid values: auto, 1/8000, 1/4000, 1/2000, 1/1000, ..."
  }
}
```

---

## 🔹 Ground-Side Implementation

### Requirements:
1. Use human-readable values from `camera_properties.json`
2. Send exactly as displayed to user
3. No Sony SDK knowledge required
4. Validate against `validation.values` before sending

### Example Implementation:

```kotlin
// NetworkClient.kt
fun setCameraProperty(property: String, value: String) {
    val command = Command(
        command = "camera.set_property",
        parameters = mapOf(
            "property" to property,
            "value" to value  // Human-readable value
        )
    )
    sendCommand(command)
}

// CameraViewModel.kt
class CameraViewModel {
    // Shutter speed values from camera_properties.json
    val shutterSpeeds = listOf(
        "auto", "1/8000", "1/4000", "1/2000", "1/1000", 
        "1/500", "1/250", "1/125", "1/60", "1/30", 
        "1/15", "1/8", "1/4", "1/2", "1", "2", "4", "8", "15", "30"
    )
    
    fun setShutterSpeed(value: String) {
        // Optional: Validate before sending
        if (value !in shutterSpeeds) {
            _errorState.value = "Invalid shutter speed: $value"
            return
        }
        
        viewModelScope.launch {
            try {
                networkClient.setCameraProperty("shutter_speed", value)
            } catch (e: Exception) {
                _errorState.value = e.message
            }
        }
    }
}

// UI Fragment
shutterSpeedSpinner.adapter = ArrayAdapter(
    requireContext(),
    android.R.layout.simple_spinner_item,
    viewModel.shutterSpeeds
)

shutterSpeedSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
    override fun onItemSelected(parent: AdapterView<*>, view: View, position: Int, id: Long) {
        val value = viewModel.shutterSpeeds[position]
        viewModel.setShutterSpeed(value)
    }
    override fun onNothingSelected(parent: AdapterView<*>) {}
}
```

---

## 🔹 Air-Side Implementation

### Requirements:
1. Accept human-readable values from protocol
2. Validate against known values
3. Convert to Sony SDK format
4. Return clear error messages
5. Maintain mapping tables

### Mapping Tables (sony_camera.cpp):

```cpp
// sony_camera.cpp

#include <unordered_map>
#include <string>

namespace {

// Shutter Speed Mapping
// Values from Sony Camera Remote SDK documentation
const std::unordered_map<std::string, CrInt32u> SHUTTER_SPEED_MAP = {
    {"auto",   0x00000000},
    {"1/8000", 0x00010001},
    {"1/4000", 0x00010002},
    {"1/2000", 0x00010003},
    {"1/1000", 0x00010004},
    {"1/500",  0x00010005},
    {"1/250",  0x00010006},
    {"1/125",  0x00010007},
    {"1/60",   0x00010008},
    {"1/30",   0x00010009},
    {"1/15",   0x0001000A},
    {"1/8",    0x0001000B},
    {"1/4",    0x0001000C},
    {"1/2",    0x0001000D},
    {"1",      0x0001000E},
    {"2",      0x0001000F},
    {"4",      0x00010010},
    {"8",      0x00010011},
    {"15",     0x00010012},
    {"30",     0x00010013}
};

// Aperture Mapping (f-stops)
const std::unordered_map<std::string, CrInt32u> APERTURE_MAP = {
    {"auto", 0x00000000},
    {"f/1.4", 0x01000140},
    {"f/2.0", 0x01000200},
    {"f/2.8", 0x01000280},
    {"f/4.0", 0x01000400},
    {"f/5.6", 0x01000560},
    {"f/8.0", 0x01000800},
    {"f/11",  0x01001100},
    {"f/16",  0x01001600},
    {"f/22",  0x01002200}
};

// ISO Mapping
const std::unordered_map<std::string, CrInt32u> ISO_MAP = {
    {"auto",   0xFFFFFFFF},
    {"100",    100},
    {"200",    200},
    {"400",    400},
    {"800",    800},
    {"1600",   1600},
    {"3200",   3200},
    {"6400",   6400},
    {"12800",  12800},
    {"25600",  25600},
    {"51200",  51200},
    {"102400", 102400}
};

// White Balance Mapping
const std::unordered_map<std::string, CrInt32u> WHITE_BALANCE_MAP = {
    {"auto",                0x00000000},
    {"daylight",            0x00000001},
    {"shade",               0x00000002},
    {"cloudy",              0x00000003},
    {"tungsten",            0x00000004},
    {"fluorescent_warm",    0x00000005},
    {"fluorescent_cool",    0x00000006},
    {"fluorescent_day",     0x00000007},
    {"fluorescent_daylight", 0x00000008},
    {"flash",               0x00000009},
    {"underwater",          0x0000000A},
    {"custom",              0x0000000B},
    {"temperature",         0x0000000C}
};

// Focus Mode Mapping
const std::unordered_map<std::string, CrInt32u> FOCUS_MODE_MAP = {
    {"af_s",   0x00000001},  // Single AF
    {"af_c",   0x00000002},  // Continuous AF
    {"af_a",   0x00000003},  // Automatic AF
    {"dmf",    0x00000004},  // Direct Manual Focus
    {"manual", 0x00000005}   // Manual Focus
};

// File Format Mapping
const std::unordered_map<std::string, CrInt32u> FILE_FORMAT_MAP = {
    {"jpeg",     0x00000001},
    {"raw",      0x00000002},
    {"jpeg_raw", 0x00000003}
};

// Drive Mode Mapping
const std::unordered_map<std::string, CrInt32u> DRIVE_MODE_MAP = {
    {"single",         0x00000001},
    {"continuous_lo",  0x00000002},
    {"continuous_hi",  0x00000003},
    {"self_timer_10s", 0x00000004},
    {"self_timer_2s",  0x00000005},
    {"bracket",        0x00000006}
};

} // anonymous namespace

// Property setter implementations
ErrorCode SonyCamera::setShutterSpeed(const std::string& value) {
    auto it = SHUTTER_SPEED_MAP.find(value);
    if (it == SHUTTER_SPEED_MAP.end()) {
        // Log valid values for debugging
        std::string valid_values = "Valid values: ";
        for (const auto& pair : SHUTTER_SPEED_MAP) {
            valid_values += pair.first + ", ";
        }
        LOG_ERROR("Invalid shutter speed: " << value << ". " << valid_values);
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_ShutterSpeed,
        &sony_value,
        sizeof(sony_value)
    );
    
    if (ret != CrError_None) {
        LOG_ERROR("Sony SDK error setting shutter speed: " << std::hex << ret);
        return ErrorCode::CAMERA_ERROR;
    }
    
    LOG_INFO("Shutter speed set to: " << value);
    return ErrorCode::SUCCESS;
}

ErrorCode SonyCamera::setAperture(const std::string& value) {
    auto it = APERTURE_MAP.find(value);
    if (it == APERTURE_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_FNumber,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setISO(const std::string& value) {
    auto it = ISO_MAP.find(value);
    if (it == ISO_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_IsoSensitivity,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setWhiteBalance(const std::string& value) {
    auto it = WHITE_BALANCE_MAP.find(value);
    if (it == WHITE_BALANCE_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_WhiteBalance,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setWhiteBalanceTemperature(int kelvin) {
    // Temperature is numeric, but protocol sends as string: "5500"
    // Convert string to int before calling this function
    
    if (kelvin < 2500 || kelvin > 9900) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = static_cast<CrInt32u>(kelvin);
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_ColorTemperature,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setFocusMode(const std::string& value) {
    auto it = FOCUS_MODE_MAP.find(value);
    if (it == FOCUS_MODE_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_FocusMode,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setFileFormat(const std::string& value) {
    auto it = FILE_FORMAT_MAP.find(value);
    if (it == FILE_FORMAT_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_FileType,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}

ErrorCode SonyCamera::setDriveMode(const std::string& value) {
    auto it = DRIVE_MODE_MAP.find(value);
    if (it == DRIVE_MODE_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    CrInt32u sony_value = it->second;
    CrInt32u ret = SDK::SetDeviceProperty(
        device_handle_,
        CrDeviceProperty_DriveMode,
        &sony_value,
        sizeof(sony_value)
    );
    
    return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
}
```

### Command Handler (tcp_server.cpp):

```cpp
// tcp_server.cpp

ErrorCode TcpServer::handleCameraSetProperty(const nlohmann::json& payload) {
    // Extract parameters
    if (!payload.contains("property") || !payload.contains("value")) {
        return ErrorCode::MISSING_REQUIRED_FIELD;
    }
    
    std::string property = payload["property"];
    
    // Value must be a string (even for numeric properties)
    if (!payload["value"].is_string()) {
        return ErrorCode::INVALID_PARAMETER;
    }
    
    std::string value = payload["value"];
    
    // Route to appropriate property handler
    ErrorCode result;
    
    if (property == "shutter_speed") {
        result = camera_->setShutterSpeed(value);
    } else if (property == "aperture") {
        result = camera_->setAperture(value);
    } else if (property == "iso") {
        result = camera_->setISO(value);
    } else if (property == "white_balance") {
        result = camera_->setWhiteBalance(value);
    } else if (property == "white_balance_temperature") {
        // Special case: convert string to int
        try {
            int kelvin = std::stoi(value);
            result = camera_->setWhiteBalanceTemperature(kelvin);
        } catch (const std::exception& e) {
            return ErrorCode::INVALID_PROPERTY_VALUE;
        }
    } else if (property == "focus_mode") {
        result = camera_->setFocusMode(value);
    } else if (property == "file_format") {
        result = camera_->setFileFormat(value);
    } else if (property == "drive_mode") {
        result = camera_->setDriveMode(value);
    } else {
        return ErrorCode::INVALID_CAMERA_PROPERTY;
    }
    
    return result;
}
```

---

## 🔍 Validation Strategy

### Ground-Side Validation (Optional but Recommended)
```kotlin
// Validate before sending
fun setCameraProperty(property: String, value: String): Boolean {
    val validValues = getValidValuesForProperty(property)
    if (value !in validValues) {
        _errorState.value = "Invalid $property value: $value"
        return false
    }
    networkClient.setCameraProperty(property, value)
    return true
}
```

### Air-Side Validation (Mandatory)
```cpp
// Always validate in mapping functions
ErrorCode setProperty(const std::string& value) {
    auto it = PROPERTY_MAP.find(value);
    if (it == PROPERTY_MAP.end()) {
        // Value not in mapping table = invalid
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    // ... proceed with Sony SDK call
}
```

---

## 📊 Special Cases

### Numeric Properties (ISO, Temperature)

**Protocol still uses strings:**
```json
{
  "command": "camera.set_property",
  "parameters": {
    "property": "iso",
    "value": "800"  ← String, not number
  }
}
```

**Why?**
- Consistent with other properties
- Easier validation
- "auto" is also a valid value for ISO

**Air-side conversion:**
```cpp
ErrorCode setISO(const std::string& value) {
    if (value == "auto") {
        // Handle auto ISO
        sony_value = 0xFFFFFFFF;
    } else {
        // Convert string to number
        try {
            int iso_num = std::stoi(value);
            // Validate range
            if (iso_num < 100 || iso_num > 102400) {
                return ErrorCode::INVALID_PROPERTY_VALUE;
            }
            sony_value = static_cast<CrInt32u>(iso_num);
        } catch (...) {
            return ErrorCode::INVALID_PROPERTY_VALUE;
        }
    }
    // ... call Sony SDK
}
```

### Range Properties (Temperature, Manual Focus)

**Protocol:**
```json
{
  "property": "white_balance_temperature",
  "value": "5500"
}
```

**Air-side:**
```cpp
ErrorCode setWhiteBalanceTemperature(const std::string& value) {
    int kelvin = std::stoi(value);
    
    // Validate range
    if (kelvin < 2500 || kelvin > 9900) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    
    // Sony SDK accepts Kelvin directly
    CrInt32u sony_value = static_cast<CrInt32u>(kelvin);
    // ... call Sony SDK
}
```

---

## ⚠️ Common Pitfalls to Avoid

### 1. Don't Send Raw Numbers
❌ **Wrong:**
```json
{"property": "iso", "value": 800}
```

✅ **Correct:**
```json
{"property": "iso", "value": "800"}
```

### 2. Don't Hardcode Sony SDK Values
❌ **Wrong:**
```kotlin
// Ground-side should NOT know this
networkClient.setCameraProperty("shutter_speed", "0x00010001")
```

✅ **Correct:**
```kotlin
networkClient.setCameraProperty("shutter_speed", "1/8000")
```

### 3. Don't Skip Validation
❌ **Wrong:**
```cpp
// Assuming value is valid
CrInt32u sony_value = SHUTTER_SPEED_MAP[value];  // Crashes if not found!
```

✅ **Correct:**
```cpp
auto it = SHUTTER_SPEED_MAP.find(value);
if (it == SHUTTER_SPEED_MAP.end()) {
    return ErrorCode::INVALID_PROPERTY_VALUE;
}
CrInt32u sony_value = it->second;
```

### 4. Don't Forget Error Messages
❌ **Wrong:**
```json
{"status": "error", "error_code": 1005}
```

✅ **Correct:**
```json
{
  "status": "error",
  "error_code": 1005,
  "error_message": "Invalid shutter speed value: '1/8001'. Valid values: auto, 1/8000, 1/4000, ..."
}
```

---

## 🧪 Testing

### Unit Tests (Air-Side)

```cpp
// test_sony_camera.cpp

TEST(SonyCameraTest, SetShutterSpeed_ValidValue) {
    SonyCamera camera;
    ErrorCode result = camera.setShutterSpeed("1/8000");
    EXPECT_EQ(result, ErrorCode::SUCCESS);
}

TEST(SonyCameraTest, SetShutterSpeed_InvalidValue) {
    SonyCamera camera;
    ErrorCode result = camera.setShutterSpeed("1/9999");
    EXPECT_EQ(result, ErrorCode::INVALID_PROPERTY_VALUE);
}

TEST(SonyCameraTest, SetShutterSpeed_AutoMode) {
    SonyCamera camera;
    ErrorCode result = camera.setShutterSpeed("auto");
    EXPECT_EQ(result, ErrorCode::SUCCESS);
}
```

### Integration Tests

```bash
# Test with real camera
# Send command via TCP
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"camera.set_property","parameters":{"property":"shutter_speed","value":"1/8000"}}}' | nc 192.168.144.20 5000

# Expected response:
# {"protocol_version":"1.0","message_type":"response","sequence_id":1,"payload":{"status":"success",...}}
```

---

## 📚 References

### Sony SDK Documentation
- Property codes from: Sony Camera Remote SDK v2.00.00
- ShutterSpeedValue enum: `CrTypes.h`
- FNumberValue enum: `CrTypes.h`
- ISO sensitivity: Direct numeric values

### DPM Protocol Files
- `camera_properties.json` - Property definitions
- `protocol_v1.0.json` - Error codes
- `commands.json` - Command structure

---

## ✅ Implementation Checklist

### Air-Side:
- [ ] Create mapping tables for all Phase 1 properties
- [ ] Implement property setter functions in `sony_camera.cpp`
- [ ] Add routing in `handleCameraSetProperty()`
- [ ] Add error messages with valid values
- [ ] Write unit tests for all mappings
- [ ] Test with real camera hardware

### Ground-Side:
- [ ] Load property values from `camera_properties.json`
- [ ] Implement `setCameraProperty()` in NetworkClient
- [ ] Add UI controls (dropdowns, sliders)
- [ ] Optional: Add client-side validation
- [ ] Test with air-side (real or mock)

### Documentation:
- [ ] Update `Command_Protocol_Specification_v1.0.md`
- [ ] Add examples to protocol README
- [ ] Document mapping tables source (Sony SDK docs)

---

**Document Status:** ✅ Approved Specification  
**Version:** 1.0  
**Last Updated:** October 25, 2025  
**Implementation:** Required for all camera property commands
