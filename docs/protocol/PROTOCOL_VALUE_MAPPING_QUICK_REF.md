# Protocol Value Mapping - Quick Reference
**For Claude Code: Camera Property Implementation**

**Date:** October 25, 2025  
**Status:** 🔴 **MANDATORY - Read Before Implementing camera.set_property**

---

## 🎯 The Golden Rule

**Protocol uses human-readable values. Air-side converts to Sony SDK format.**

```
Ground-Side sends:    "shutter_speed": "1/8000"
Protocol transmits:   "shutter_speed": "1/8000"
Air-Side converts to: ShutterSpeed = 0x00010001
Sony SDK receives:    CrDeviceProperty_ShutterSpeed, 0x00010001
```

---

## ✅ DO

### Ground-Side (Android):
```kotlin
// ✅ Correct - Send human-readable values
networkClient.setCameraProperty("shutter_speed", "1/8000")
networkClient.setCameraProperty("aperture", "f/2.8")
networkClient.setCameraProperty("iso", "800")
networkClient.setCameraProperty("white_balance", "daylight")
```

### Air-Side (C++):
```cpp
// ✅ Correct - Map human-readable to Sony SDK
ErrorCode setShutterSpeed(const std::string& value) {
    auto it = SHUTTER_SPEED_MAP.find(value);
    if (it == SHUTTER_SPEED_MAP.end()) {
        return ErrorCode::INVALID_PROPERTY_VALUE;
    }
    CrInt32u sony_value = it->second;
    SDK::SetDeviceProperty(CrDeviceProperty_ShutterSpeed, &sony_value, ...);
}
```

---

## ❌ DON'T

### Ground-Side:
```kotlin
// ❌ Wrong - Don't send Sony SDK raw values
networkClient.setCameraProperty("shutter_speed", "0x00010001")  // NO!
networkClient.setCameraProperty("shutter_speed", 65537)          // NO!

// ❌ Wrong - Don't send numbers as numbers
networkClient.setCameraProperty("iso", 800)  // NO! Send "800" (string)
```

### Air-Side:
```cpp
// ❌ Wrong - Don't accept raw Sony SDK values from protocol
if (value == "0x00010001") { ... }  // NO! Protocol doesn't send these

// ❌ Wrong - Don't crash on invalid values
CrInt32u sony_value = SHUTTER_SPEED_MAP[value];  // Crashes if not found!
```

---

## 📋 Implementation Checklist

### When Implementing a Property on Air-Side:

1. **Create mapping table:**
   ```cpp
   const std::unordered_map<std::string, CrInt32u> PROPERTY_MAP = {
       {"human_readable_value", SONY_SDK_CONSTANT},
       ...
   };
   ```

2. **Implement setter with validation:**
   ```cpp
   ErrorCode setProperty(const std::string& value) {
       // Step 1: Validate
       auto it = PROPERTY_MAP.find(value);
       if (it == PROPERTY_MAP.end()) {
           return ErrorCode::INVALID_PROPERTY_VALUE;
       }
       
       // Step 2: Convert
       CrInt32u sony_value = it->second;
       
       // Step 3: Call Sony SDK
       CrInt32u ret = SDK::SetDeviceProperty(...);
       
       return (ret == CrError_None) ? ErrorCode::SUCCESS : ErrorCode::CAMERA_ERROR;
   }
   ```

3. **Add routing in handleCameraSetProperty():**
   ```cpp
   if (property == "property_name") {
       result = camera_->setProperty(value);
   }
   ```

4. **Update camera_properties.json:**
   ```json
   "implemented": {
       "air_side": true,
       "ground_side": false
   }
   ```

### When Implementing a Property on Ground-Side:

1. **Load values from camera_properties.json:**
   ```kotlin
   val propertyValues = listOf("auto", "1/8000", "1/4000", ...)
   ```

2. **Create UI control based on ui_hints:**
   - `dropdown` → Spinner
   - `slider` → SeekBar
   - `segmented_control` → RadioGroup

3. **Send human-readable value:**
   ```kotlin
   fun setProperty(value: String) {
       networkClient.setCameraProperty("property_name", value)
   }
   ```

4. **Update camera_properties.json:**
   ```json
   "implemented": {
       "air_side": true,
       "ground_side": true
   }
   ```

---

## 🔍 Validation Strategy

### Ground-Side (Optional):
```kotlin
// Validate before sending
if (value !in validValues) {
    showError("Invalid value")
    return
}
networkClient.setCameraProperty(property, value)
```

### Air-Side (Mandatory):
```cpp
// Always validate in setter
auto it = PROPERTY_MAP.find(value);
if (it == PROPERTY_MAP.end()) {
    // Invalid value - reject
    return ErrorCode::INVALID_PROPERTY_VALUE;
}
// Proceed...
```

---

## 📊 Special Cases

### Numeric Properties (ISO, Temperature)

**Still send as strings:**
```kotlin
// ✅ Correct
networkClient.setCameraProperty("iso", "800")
networkClient.setCameraProperty("white_balance_temperature", "5500")

// ❌ Wrong
networkClient.setCameraProperty("iso", 800)  // Don't send as number
```

**Air-side converts:**
```cpp
ErrorCode setISO(const std::string& value) {
    if (value == "auto") {
        sony_value = 0xFFFFFFFF;
    } else {
        int iso_num = std::stoi(value);  // Convert string to int
        sony_value = static_cast<CrInt32u>(iso_num);
    }
    // ... call Sony SDK
}
```

---

## 🚨 Common Mistakes

### Mistake #1: Sending Wrong Format
```kotlin
// ❌ User sees: "1/8000"
// ❌ You send: "0x00010001"
setCameraProperty("shutter_speed", "0x00010001")

// ✅ Send what user sees
setCameraProperty("shutter_speed", "1/8000")
```

### Mistake #2: Not Validating
```cpp
// ❌ Crashes if value not in map
CrInt32u sony_value = SHUTTER_SPEED_MAP[value];

// ✅ Check first
auto it = SHUTTER_SPEED_MAP.find(value);
if (it == SHUTTER_SPEED_MAP.end()) return ErrorCode::INVALID_PROPERTY_VALUE;
```

### Mistake #3: Forgetting Error Messages
```cpp
// ❌ Generic error
return ErrorCode::INVALID_PROPERTY_VALUE;

// ✅ Helpful error
LOG_ERROR("Invalid shutter speed: " << value << ". Valid: auto, 1/8000, 1/4000, ...");
return ErrorCode::INVALID_PROPERTY_VALUE;
```

---

## 📚 Where to Find Information

### Mapping Tables:
- **Document:** `docs/protocol/PROTOCOL_VALUE_MAPPING.md`
- **Section:** "Air-Side Implementation" → "Mapping Tables"
- **Contains:** Complete mappings for all Phase 1 properties

### Property Definitions:
- **File:** `docs/protocol/camera_properties.json`
- **Look for:** `validation.values` - these are protocol values
- **Look for:** `protocol.example` - example of what to send

### Sony SDK Constants:
- **Document:** Sony Camera Remote SDK documentation
- **File:** `CrTypes.h` in Sony SDK
- **Look for:** Property codes and value enums

---

## 🎓 Quick Examples

### Example 1: Shutter Speed
```
User selects:   "1/8000"
Ground sends:   {"property": "shutter_speed", "value": "1/8000"}
Air receives:   "shutter_speed", "1/8000"
Air maps to:    0x00010001
Sony SDK gets:  CrDeviceProperty_ShutterSpeed, 0x00010001
```

### Example 2: White Balance
```
User selects:   "Daylight"
Ground sends:   {"property": "white_balance", "value": "daylight"}
Air receives:   "white_balance", "daylight"
Air maps to:    0x00000001
Sony SDK gets:  CrDeviceProperty_WhiteBalance, 0x00000001
```

### Example 3: ISO (Numeric)
```
User selects:   "800"
Ground sends:   {"property": "iso", "value": "800"}  ← Still a string!
Air receives:   "iso", "800"
Air converts:   std::stoi("800") = 800
Sony SDK gets:  CrDeviceProperty_IsoSensitivity, 800
```

---

## ✅ Before You Start

**Air-Side:**
- [ ] Read PROTOCOL_VALUE_MAPPING.md
- [ ] Find Sony SDK constants in CrTypes.h
- [ ] Create mapping table
- [ ] Implement setter with validation
- [ ] Add error logging
- [ ] Test with real camera

**Ground-Side:**
- [ ] Read camera_properties.json for property
- [ ] Check validation.values for allowed values
- [ ] Check ui_hints.control_type for UI type
- [ ] Implement UI control
- [ ] Send human-readable value
- [ ] Test with air-side

---

## 🔗 Related Documentation

- **Full Specification:** `docs/protocol/PROTOCOL_VALUE_MAPPING.md`
- **Property Definitions:** `docs/protocol/camera_properties.json`
- **Protocol README:** `docs/protocol/README.md`
- **CC Workflow:** `CC_READ_THIS_FIRST.md` (project root)

---

**Remember:** 
- 🟢 Protocol = Human-readable
- 🔵 Air-side = Converts to Sony SDK
- 🟣 Ground-side = Just sends what user sees

**Status:** 🔴 Mandatory Reading  
**Version:** 1.0  
**Last Updated:** October 25, 2025
