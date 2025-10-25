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

### `message_schemas.json` (future)
**JSON Schema definitions for message validation**
- Full JSON Schema for all message types
- Can be used for runtime validation
- Code generation potential

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

## 🎯 Best Practices

### ✅ DO
- **Always update JSON first** - Then implement in code
- **Version changes together** - Protocol spec + both implementations
- **Document everything** - Why a command exists, not just what it does
- **Track implementation** - Use `implemented` field in `commands.json`
- **Test both sides** - Before marking as implemented

### ❌ DON'T
- **Don't implement without updating spec** - Spec is the contract
- **Don't change error codes** - They're part of the API
- **Don't skip the JSON** - It's the source of truth
- **Don't partially implement** - Finish one command fully before starting another

## 🔍 Validation

### Checking Synchronization

```bash
# Check if a command is implemented on both sides
cat commands.json | jq '.commands."camera.capture".implemented'

# List all unimplemented commands
cat commands.json | jq -r 'to_entries[] |
  select(.value.implemented.air_side == false or
         .value.implemented.ground_side == false) | .key'

# Get error code for a specific error
cat protocol_v1.0.json | jq '.error_codes.camera_errors.codes."1000"'
```

### Manual Validation Checklist

- [ ] `protocol_v1.0.json` has the same version as markdown spec
- [ ] All commands in `commands.json` are documented in markdown
- [ ] All error codes in JSON match C++ `messages.h`
- [ ] Port numbers in JSON match C++ `config.h` and Android `NetworkSettings.kt`
- [ ] Implementation flags in `commands.json` are accurate

## 📚 Related Files

### SBC (C++)
- `sbc/src/config.h` - Port numbers, timing constants
- `sbc/src/protocol/messages.h` - Error codes, message structures
- `sbc/src/protocol/tcp_server.cpp` - Command handlers

### Android (Kotlin)
- `android/.../network/NetworkSettings.kt` - Network configuration
- `android/.../network/NetworkClient.kt` - Command implementation
- `android/.../network/ProtocolMessages.kt` - Message data classes

### Documentation
- `docs/Command_Protocol_Specification_v1.0.md` - Full protocol documentation
- `docs/protocol/` - This directory

## 🚀 Future Improvements

1. **Code Generation** - Generate C++ and Kotlin code from JSON schemas
2. **Runtime Validation** - Use JSON schemas to validate messages
3. **Automated Testing** - Generate test cases from command definitions
4. **Version Management** - Automated protocol version compatibility checks
5. **Documentation Generation** - Auto-generate parts of markdown from JSON

---

**Maintained by:** DPM Team
**Last Updated:** 2025-10-25
**Protocol Version:** 1.0.0
