# DPM Protocol Shared Definitions

This directory contains the **single source of truth** for the DPM communication protocol between the Android ground station and Raspberry Pi air-side payload manager.

## 📁 Files

### `protocol_v1.0.json`
**Core protocol constants and definitions**
- Protocol version
- Port numbers
- Timing constants
- Network configuration
- Error code ranges
- Message types

**Usage:**
- Both SBC (C++) and Android (Kotlin) should reference this file
- Contains version-independent constants
- Update when adding new error codes or message types

### `commands.json`
**Command definitions and specifications**
- All supported commands
- Parameter types and validation rules
- Response formats
- Implementation status tracking
- Error codes per command

**Usage:**
- Reference when implementing new commands
- Use for validation
- Track implementation progress across platforms

### `camera_properties.json` 🆕
**Camera property definitions and specifications**
- All Sony camera properties (exposure, focus, white balance, etc.)
- Property types, validation rules, and allowed values
- Sony SDK mapping (property codes, functions)
- UI hints (control types, grouping, priority)
- Implementation status tracking per property
- Property dependencies and camera mode restrictions
- Phase-based implementation roadmap

**Key insight:** `camera.set_property` is ONE command that can set HUNDREDS of properties.
- This file defines all valid properties
- Each property has its own implementation tracking
- Properties are grouped by category and phase
- Different properties need different UI controls

**Usage:**
- Check before implementing `camera.set_property` UI
- Reference Sony SDK mapping when implementing air-side
- Track which properties are implemented per phase
- Validate property values before sending commands
- Plan UI based on `ui_hints` section

### `message_schemas.json` (future)
**JSON Schema definitions for message validation**
- Full JSON Schema for all message types
- Can be used for runtime validation
- Code generation potential

---

## 📐 Architecture: Commands vs Properties

### Commands Architecture
```
One Command → One Handler → One UI Element

Example:
camera.capture → handleCameraCapture() → Capture Button
gimbal.set_angle → handleGimbalSetAngle() → Gimbal Control Widget
```

### Properties Architecture
```
One Command → Many Properties → Many UI Elements

camera.set_property → {
  shutter_speed → Dropdown (1/8000 to 30s)
  aperture → Dropdown (f/1.4 to f/22)
  iso → Dropdown (100 to 102400)
  white_balance → Dropdown (presets)
  white_balance_temperature → Slider (2500K-9900K)
  focus_mode → Segmented Control
  file_format → Segmented Control
  ... (100+ more properties)
}
```

**Why separate files?**
- `commands.json`: ~20 commands, stable, rarely changes
- `camera_properties.json`: ~100+ properties, grows over time
- Cleaner separation of concerns
- Easier to find and manage properties
- Independent implementation tracking

---

## 🔄 Synchronization Workflow

### Adding a New Command

1. **Define in `commands.json`:**
   ```json
   "camera.new_command": {
     "description": "...",
     "parameters": {...},
     "response": {...},
     "implemented": {
       "air_side": false,
       "ground_side": false,
       "version": "1.1.0"
     }
   }
   ```

2. **Update `Command_Protocol_Specification_v1.0.md`:**
   - Add command documentation
   - Include examples
   - Document use cases

3. **Implement Air-Side (C++):**
   - Add handler in `tcp_server.cpp`
   - Update `commands.json` → `"air_side": true`
   - Test implementation

4. **Implement Ground-Side (Kotlin):**
   - Add method in `NetworkClient.kt`
   - Update `commands.json` → `"ground_side": true`
   - Test implementation

5. **Commit all together:**
   - Specification update
   - JSON definition update
   - Both implementations
   - Tests

### Adding a New Camera Property

1. **Define in `camera_properties.json`:**
   ```json
   "new_property": {
     "display_name": "Property Name",
     "category": "exposure",
     "description": "What it does",
     "type": "string",
     "validation": {
       "type": "enum",
       "values": ["value1", "value2"],
       "default": "value1"
     },
     "sony_sdk": {
       "property_code": "CrDeviceProperty_Something",
       "get_function": "GetDeviceProperty",
       "set_function": "SetDeviceProperty",
       "value_mapping": "How to convert values",
       "notes": "Important details"
     },
     "ui_hints": {
       "control_type": "dropdown",
       "group": "Exposure",
       "priority": "high"
     },
     "implemented": {
       "air_side": false,
       "ground_side": false,
       "version": "1.1.0",
       "notes": ""
     }
   }
   ```

2. **Implement Air-Side (C++):**
   - Add property handling in `handleCameraSetProperty()`
   - Map property name to Sony SDK call
   - Validate property value
   - Update `camera_properties.json` → `"air_side": true`
   - Test with real camera

3. **Implement Ground-Side (Kotlin):**
   - Add UI control based on `ui_hints.control_type`
   - Implement validation based on `validation` rules
   - Wire up to `networkClient.setCameraProperty(property, value)`
   - Update `camera_properties.json` → `"ground_side": true`
   - Test end-to-end

4. **Commit:**
   ```
   [PROTOCOL] Implemented [property_name] camera property
   
   - Added [property_name] definition to camera_properties.json
   - Air-side: Sony SDK [property_code] integration
   - Ground-side: [control_type] UI control in CameraControlFragment
   - Validation: [describe validation rules]
   - Testing: Verified with [camera model]
   ```

### Adding Error Codes

1. **Add to `protocol_v1.0.json`:**
   ```json
   "camera_errors": {
     "codes": {
       "1008": "NEW_ERROR_CODE"
     }
   }
   ```

2. **Update C++ (`messages.h`):**
   ```cpp
   enum class ErrorCode {
     ...
     NEW_ERROR_CODE = 1008
   };
   ```

3. **Update Kotlin (if needed):**
   ```kotlin
   object ErrorCodes {
     const val NEW_ERROR_CODE = 1008
   }
   ```

---

## 🎯 Best Practices

### ✅ DO
- **Always update JSON first** - Then implement in code
- **Version changes together** - Protocol spec + both implementations
- **Document everything** - Why a command/property exists, not just what it does
- **Track implementation** - Use `implemented` field in JSON files
- **Test both sides** - Before marking as implemented
- **Implement properties incrementally** - One property at a time
- **Check property dependencies** - Some properties require others to be set first
- **Validate on both sides** - Client + Server validation
- **Use ui_hints** - Let JSON guide UI implementation

### ❌ DON'T
- **Don't implement without updating spec** - Spec is the contract
- **Don't change error codes** - They're part of the API
- **Don't skip the JSON** - It's the source of truth
- **Don't partially implement** - Finish one command/property fully before starting another
- **Don't add properties without Sony SDK mapping** - Need to know how to implement
- **Don't ignore camera mode restrictions** - Some properties unavailable in certain modes
- **Don't assume UI type** - Use `ui_hints.control_type` from JSON

---

## 🔍 Validation Commands

### Checking Synchronization

```bash
# Check if a command is implemented on both sides
cat commands.json | jq '.commands."camera.capture".implemented'

# List all unimplemented commands
cat commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.air_side == false or
         .value.implemented.ground_side == false) | .key'

# Check Phase 1 camera properties status
cat camera_properties.json | jq -r '.implementation_phases.phase_1.properties[] as $prop |
  "\($prop): \(.properties[$prop].implemented | "air=\(.air_side) ground=\(.ground_side)")"'

# List properties ready for ground-side implementation (air-side done)
cat camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.air_side == true and
         .value.implemented.ground_side == false) | .key'

# Get error code for a specific error
cat protocol_v1.0.json | jq '.error_codes.camera_errors.codes."1000"'

# Check property validation rules
cat camera_properties.json | jq '.properties."shutter_speed".validation'

# Get Sony SDK mapping for a property
cat camera_properties.json | jq '.properties."shutter_speed".sony_sdk'

# List all high-priority properties
cat camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.ui_hints.priority == "high") | .key'
```

### Manual Validation Checklist

- [ ] `protocol_v1.0.json` has the same version as markdown spec
- [ ] All commands in `commands.json` are documented in markdown
- [ ] All camera properties in `camera_properties.json` have Sony SDK mappings
- [ ] All error codes in JSON match C++ `messages.h`
- [ ] Port numbers in JSON match C++ `config.h` and Android `NetworkSettings.kt`
- [ ] Implementation flags in `commands.json` and `camera_properties.json` are accurate
- [ ] Property dependencies are documented
- [ ] UI hints are provided for all properties
- [ ] Phase 1 properties are clearly identified

---

## 📚 Related Files

### SBC (C++)
- `sbc/src/config.h` - Port numbers, timing constants
- `sbc/src/protocol/messages.h` - Error codes, message structures
- `sbc/src/protocol/tcp_server.cpp` - Command handlers
- `sbc/src/camera/sony_camera.cpp` - Sony SDK property handling

### Android (Kotlin)
- `android/.../network/NetworkSettings.kt` - Network configuration
- `android/.../network/NetworkClient.kt` - Command implementation
- `android/.../network/ProtocolMessages.kt` - Message data classes
- `android/.../ui/CameraControlFragment.kt` - Camera property UI

### Documentation
- `docs/Command_Protocol_Specification_v1.0.md` - Full protocol documentation
- `docs/Phase1_Requirements_Update.md` - Phase 1 feature requirements
- `docs/Protocol_Implementation_Quick_Start.md` - Implementation guide
- `docs/protocol/` - This directory

---

## 🚀 Future Improvements

1. **Code Generation** - Generate C++ and Kotlin code from JSON schemas
2. **Runtime Validation** - Use JSON schemas to validate messages
3. **Automated Testing** - Generate test cases from command/property definitions
4. **Version Management** - Automated protocol version compatibility checks
5. **Documentation Generation** - Auto-generate parts of markdown from JSON
6. **Property Groups** - Auto-generate UI groups based on categories
7. **Dependency Validation** - Runtime check of property dependencies

---

## 📊 Implementation Status Overview

### Commands
- Check `commands.json` for full status
- Use `jq` queries above to get current counts

### Camera Properties  
- **Phase 1** (Weeks 3-10):
  - Core exposure triangle (shutter, aperture, ISO)
  - White balance presets and temperature
  - Focus mode selection
  - File format (JPEG/RAW)
  - Drive mode (single/continuous)
  
- **Phase 2** (Weeks 11-15):
  - Exposure compensation
  - Metering modes
  - Image quality settings
  - Video settings
  
- **Phase 3** (Post-Phase 1):
  - Picture profiles
  - Color modes
  - Advanced features

Run status checks frequently to track progress!

---

**Maintained by:** DPM Team  
**Last Updated:** 2025-10-25  
**Protocol Version:** 1.0.0  
**Camera Properties Version:** 1.0.0
