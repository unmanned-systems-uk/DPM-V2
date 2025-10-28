# Claude Code - READ THIS FIRST
## DPM Payload Manager Project Rules & Workflow

**Date Created:** October 25, 2025  
**Last Updated:** October 27, 2025 - Added Specification-First Enforcement  
**Version:** 2.1 (Combined Air-Side + Ground-Side + Spec Enforcement)  
**Status:** 🔴 **MANDATORY - READ EVERY SESSION**

---

## 🎯 QUICK START - WHERE AM I WORKING?

**Identify your platform first:**

- 🔹 **Air-Side (C++ SBC)?** → Working in `sbc/` directory
  - Read Common Rules below, then jump to [Air-Side Specifics](#-air-side-specifics-c-sbc)
  - Check `sbc/docs/PROGRESS_AND_TODO.md` for current status

- 🔹 **Ground-Side (Android)?** → Working in `android/` directory  
  - Read Common Rules below, then jump to [Ground-Side Specifics](#-ground-side-specifics-android-app)
  - Check `android/docs/PROGRESS_AND_TODO.md` for current status

- 🔹 **Protocol/Documentation?** → Working in `docs/` directory
  - Read Common Rules below
  - Focus on Protocol Synchronization section

---

## 🚨 SPECIFICATION-FIRST ENFORCEMENT

**CRITICAL RULE: The specification files are the SINGLE SOURCE OF TRUTH.**

### The Problem We're Solving

**Past Issue (Oct 2025):**
```
camera_properties.json (12 ISO values) ← OUTDATED SPEC
        ✗                    ✗
  Air-Side (C++)      Ground-Side (Android)
  HARDCODED 35 ISOs   HARDCODED ??? ISOs
  
  → DIVERGENCE! Spec didn't match implementations
```

**Correct Architecture:**
```
camera_properties.json (COMPLETE - 35 ISO values)
        ↓                    ↓
  Air-Side (C++)      Ground-Side (Android)
  Reads/generates     Reads/generates
  from spec           from spec
  
  → SYNCHRONIZED! Spec is single source of truth
```

### Forbidden Actions

❌ **NEVER hardcode camera property values** in Air-Side or Ground-Side code  
❌ **NEVER implement a property without reading** `camera_properties.json` first  
❌ **NEVER assume values** - always derive from specification  
❌ **NEVER add values to implementation** without updating specification first  
❌ **NEVER commit code with hardcoded property arrays/maps** (exceptions: generated code)

### Required Workflow for Camera Properties

```
1. User identifies need for new property value (e.g., ISO 102400)
   ↓
2. CC STOPS and asks: "Should I update camera_properties.json first?"
   ↓
3. User confirms or CC updates camera_properties.json
   ↓
4. COMMIT the spec change: [PROTOCOL] Add ISO 102400 to camera_properties.json
   ↓
5. PULL latest (in case other side updated)
   ↓
6. NOW implement in Air-Side C++ (read from JSON or use code generation)
   ↓
7. BUILD and TEST thoroughly
   ↓
8. COMMIT Air-Side: [FEATURE] Implement ISO 102400 support
   ↓
9. Update camera_properties.json: "air_side": true
   ↓
10. COMMIT: [PROTOCOL] Mark ISO implementation complete on air-side
    ↓
11. Ground-Side CC pulls, sees new ISO value, asks user about UI
    ↓
12. Implement in Android (load from spec, don't hardcode)
    ↓
13. Update "ground_side": true
    ↓
14. COMMIT: [PROTOCOL] Mark ISO implementation complete on ground-side
```

### Specification Update Triggers

🔴 **STOP and update spec FIRST if you discover:**
- New valid camera property value (e.g., additional ISO value)
- New Sony SDK property code
- New enum value for existing property
- Missing validation rule
- Incorrect type definition
- Any mismatch between spec and reality

**Process:**
1. STOP coding immediately
2. Update `camera_properties.json`
3. Commit spec update
4. THEN implement in code

---

## 📋 COMMON SESSION START CHECKLIST
**Every session, regardless of platform:**

### 1. Read This Document
- ✅ **ALWAYS** read `CC_READ_THIS_FIRST.md` first (this file)
- This is your source of truth for workflow rules

### 2. Pull Latest Changes from Git
- ✅ **MANDATORY** - Always pull latest before doing ANY work
- ✅ Run `git pull origin main` at start of EVERY session
- ✅ This ensures you have latest protocol definitions
- ✅ This ensures you have changes from the other platform (air ↔ ground)
- ⚠️ **CRITICAL** - Never work on stale code!

**If git pull shows conflicts:**
1. **STOP** immediately
2. **Tell user**: "Git pull has conflicts that need resolution"
3. **List** the conflicting files
4. **Wait** for user to resolve or give instructions
5. **DO NOT** attempt to resolve conflicts without user approval

### 3. Run Protocol Synchronization Audit (NEW!)

**MANDATORY: Run audit script at start of EVERY session**

```bash
# If audit script exists, run it
if [ -f tools/audit_protocol_sync.sh ]; then
    ./tools/audit_protocol_sync.sh
else
    echo "⚠️  Audit script not found - manual check required"
fi
```

**Manual checks if script doesn't exist:**

```bash
# Check for recent spec updates
git log --oneline --since="1 day ago" -- docs/protocol/

# Check YOUR platform's implementation status
# Air-Side:
jq '.properties | to_entries[] | select(.value.implemented.air_side == false) | .key' \
  docs/protocol/camera_properties.json

# Ground-Side:
jq '.properties | to_entries[] | select(.value.implemented.ground_side == false) | .key' \
  docs/protocol/camera_properties.json
```

### 4. Check Protocol Synchronization

- ✅ **MANDATORY** - Check `docs/protocol/commands.json` for new commands
- ✅ **MANDATORY** - Check `docs/protocol/camera_properties.json` for new properties
- ✅ Check if the other platform has implemented things you need to implement
- ✅ **ASK USER** about any new commands/properties before implementing
- ⚠️ **CRITICAL** - Protocol sync MUST happen every session

**Run these checks:**

```bash
# For AIR-SIDE: Check what you need to implement
cat docs/protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.air_side == false) | .key'

cat docs/protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.air_side == false) | .key'

# For GROUND-SIDE: Check what you need to implement  
cat docs/protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.ground_side == false) | .key'

cat docs/protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.ground_side == false) | .key'
```

### 5. Check for Hardcoded Values (NEW!)

**Search for specification violations:**

```bash
# Air-Side: Search for hardcoded property arrays
grep -rn "std::vector.*ISO\|ISO.*{" sbc/src/ | grep -v generated | grep -v "\/\/"

# Ground-Side: Search for hardcoded property arrays  
grep -rn "arrayOf.*ISO\|listOf.*ISO" android/app/src/ | grep -v generated | grep -v "\/\/"

# If you find ANY hardcoded arrays, STOP and report to user
```

### 6. Check Current Status
- ✅ Read the appropriate `PROGRESS_AND_TODO.md`:
  - **Air-side:** `sbc/docs/PROGRESS_AND_TODO.md`
  - **Ground-side:** `android/docs/PROGRESS_AND_TODO.md`
- Understand:
  - What phase we're in
  - What's been completed
  - What's currently blocked
  - What to work on next

### 7. Read Relevant Technical Docs (If Needed)
- ⚠️ **DO NOT** read `Project_Summary_and_Action_Plan.md` unless explicitly asked
- ⚠️ **DO NOT** re-read technical specs you've already reviewed in this session
- ✅ **DO** read specific technical docs when starting new features

**Air-Side Docs:**
- `sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md` - When implementing new components
- `sbc/docs/DOCKER_SETUP.md` - When working with Docker or Sony SDK
- Protocol specs - When implementing protocol features
- Sony SDK docs - When working on camera integration

**Ground-Side Docs:**
- `docs/Command_Protocol_Specification_v1.0.md` - When implementing protocol features
- `docs/Protocol_Implementation_Quick_Start.md` - Protocol implementation guide
- `docs/Phase1_Requirements_Update.md` - Feature requirements
- `docs/Updated_System_Architecture_H16.md` - System architecture
- Android-specific guides when implementing UI/networking

### 8. Understand Git Status
- ✅ Run `git status` to check for uncommitted changes
- ✅ Identify what needs to be committed
- ✅ Check current branch (should be `main`)

---

## 🔄 COMMON WORKFLOW RULES
**These rules apply to BOTH platforms:**

### Rule #0: Protocol Synchronization (MOST IMPORTANT!)

**🔴 CRITICAL: Check protocol files EVERY SESSION before doing ANY work! 🔴**

#### Session Start Protocol Check

**Commands Check:**
```bash
# Check for new commands
cat docs/protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.SIDE_side == false) | .key'
# Replace SIDE with 'air' or 'ground'

# Check what the OTHER side has implemented
cat docs/protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.OTHER_side == true and
         .value.implemented.YOUR_side == false) | .key'
# These are ready to implement - the other side can already handle them!
```

**Camera Properties Check:**
```bash
# Check for new properties
cat docs/protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.SIDE_side == false) | .key'

# Check what the OTHER side has implemented
cat docs/protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.OTHER_side == true and
         .value.implemented.YOUR_side == false) | .key'

# Check Phase 1 priority properties
cat docs/protocol/camera_properties.json | jq '.implementation_phases.phase_1.properties[]'
```

**If you see ANY commands OR properties listed:**
1. **STOP** and read the definition in the JSON file
2. **ASK THE USER:**
   - "I see new item(s) in the protocol: [list them]"
   - "What should these do? (for air-side) / What UI should these have? (for ground-side)"
   - "Should I implement them now, or are they planned for later?"
3. **WAIT** for user response before proceeding
4. **DO NOT** assume you know what to implement

#### Adding New Commands

**When implementing a new command:**

**Air-Side Flow:**
```
1. User adds command to docs/protocol/commands.json
   └─ Sets "air_side": false, "ground_side": might be true

2. CC detects new command at session start
   └─ Asks user what it does and if it should be implemented

3. CC implements in C++ (tcp_server.cpp)
   ├─ Add handler function (e.g., handleCameraFocus)
   ├─ Add route in processCommand()
   ├─ Add Sony SDK calls if needed
   ├─ Add any new error codes to messages.h
   └─ Test implementation

4. CC updates commands.json
   └─ Set "air_side": true

5. CC updates sbc/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [PROTOCOL] Implemented [command.name] command
```

**Ground-Side Flow:**
```
1. User adds command to docs/protocol/commands.json
   └─ May add commented-out method to NetworkClient.kt

2. CC detects new command at session start
   └─ Asks user about UI requirements

3. CC implements in Kotlin
   ├─ Uncomment/add method in NetworkClient.kt
   ├─ Add ViewModel method to call it
   ├─ Add UI button/control in appropriate Fragment
   ├─ Add error handling
   └─ Test with air-side (if available)

4. CC updates commands.json
   └─ Set "ground_side": true

5. CC updates android/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [PROTOCOL] Implemented [command.name] UI
```

#### Camera Properties Workflow (SPECIFICATION-FIRST!)

**Key Insight:** `camera.set_property` is ONE command that sets MANY properties.

**Properties are different from commands:**
- Commands: One command → One handler → One UI element
- Properties: One command → Many properties → Many UI elements

**When implementing camera properties:**

1. **READ camera_properties.json FIRST:**
   ```bash
   cat docs/protocol/camera_properties.json | jq '.properties."property_name"'
   ```

2. **Check which properties are Phase 1:**
   ```bash
   cat docs/protocol/camera_properties.json | jq '.implementation_phases.phase_1.properties[]'
   ```

3. **Verify values in specification:**
   - Check `validation.values[]` array
   - These are the ONLY valid values
   - Do NOT add values not in spec
   - If you find new valid values, update spec FIRST

4. **Pick ONE property to implement at a time:**
   - Start with high-priority (exposure triangle: shutter, aperture, ISO)
   - Implement air-side Sony SDK call (using spec values)
   - Add ground-side UI control (using spec values)
   - Test thoroughly
   - Mark property as implemented

5. **Implementation approach (choose one):**
   - **Option A (Recommended):** Code generation from JSON
   - **Option B:** Runtime JSON loading
   - **Option C (FORBIDDEN):** Hardcoding values

6. **UI considerations (ground-side):**
   - Check `ui_hints` in camera_properties.json:
     - `dropdown` → Spinner/Dropdown
     - `slider` → SeekBar
     - `segmented_control` → RadioGroup/ToggleButton
   - Different properties need different controls
   - Some properties depend on others (e.g., WB temperature requires WB mode = "temperature")

7. **Example: Implementing shutter_speed:**
   ```
   Air-Side:
   - READ camera_properties.json for shutter_speed values
   - Generate or load mapping to Sony SDK ShutterSpeedValue enum
   - Add to handleCameraSetProperty()
   - Call SDK::SetDeviceProperty(CrDeviceProperty_ShutterSpeed, value)
   - Test with real camera
   - Mark "air_side": true in JSON
   - COMMIT: [FEATURE] Implement shutter_speed property
   - COMMIT: [PROTOCOL] Mark shutter_speed air-side complete
   
   Ground-Side:
   - READ camera_properties.json for shutter_speed values
   - Load values from JSON (don't hardcode!)
   - Add Spinner with values from specification
   - Wire to networkClient.setCameraProperty("shutter_speed", value)
   - Implement validation
   - Test end-to-end
   - Mark "ground_side": true in JSON
   - COMMIT: [FEATURE] Implement shutter_speed UI
   - COMMIT: [PROTOCOL] Mark shutter_speed ground-side complete
   ```

#### Protocol Sync Rules

✅ **DO:**
- Check protocol files at START of every session
- Check for both commands AND properties
- Ask user about new items before implementing
- Verify the other platform's status before implementing
- Update JSON files immediately after implementing
- Keep JSON as single source of truth
- Implement incrementally (one command/property at a time)
- Test thoroughly before marking as implemented
- Run audit script to detect divergence
- Read spec before implementing any property

❌ **DON'T:**
- Implement commands/properties not in JSON files
- Assume what something should do without asking
- Mark implemented until fully done and tested
- Skip protocol check at session start
- Implement multiple things at once
- Send commands/properties the other side can't handle
- **Hardcode property values in source code**
- **Add values to code without updating spec first**
- **Assume spec is complete - verify against reality**

### Rule #1: Update PROGRESS_AND_TODO.md After Every Significant Change

**When to update:**
- ✅ After completing any task in a phase
- ✅ After discovering/resolving a bug
- ✅ After creating new files
- ✅ After significant debugging sessions
- ✅ When switching from one phase/component to another
- ✅ **AT MINIMUM: At end of every work session**

**What to update:**
```markdown
## RECENT UPDATES (October XX, 2025)
- Add new developments at the top
- Keep dated entries

## [Current Phase Section]
- Update task checkboxes: [ ] → [x]
- Update status notes
- Document any blockers

## OVERALL PROGRESS
- Update completion percentages
- Update visual progress bars
- Update "Last Updated" timestamp

## ISSUE TRACKER
- Add new issues discovered
- Update status of existing issues
- Mark resolved issues
```

**Format Example:**
```markdown
**Last Updated:** October 27, 2025 15:30 - After fixing specification divergence
```

### Rule #2: Commit to Git Regularly

**Commit frequency rules:**

1. **After completing any functional unit:**
   - ✅ New feature implemented and tested
   - ✅ Bug fixed and verified
   - ✅ New component created
   - ✅ Documentation updated significantly
   - ✅ **Specification updated**

2. **Time-based minimum:**
   - ✅ Commit at least every 30-60 minutes of active work
   - Even if work is incomplete - use WIP tag

3. **Before switching tasks:**
   - ✅ Always commit current work before starting something new

4. **At end of session:**
   - ✅ **MANDATORY** - Commit all changes before ending work
   - Update docs first, then commit

**Commit Message Format:**

```bash
[TYPE] Component: Brief one-line summary (max 72 chars)

- Detailed point 1 (what changed)
- Detailed point 2 (why it changed)
- Detailed point 3 (impact/result)
```

**Valid TYPE prefixes:**
- `[FEATURE]` - New functionality
- `[FIX]` - Bug fix
- `[PROTOCOL]` - Protocol implementation or specification update
- `[DOCS]` - Documentation update
- `[REFACTOR]` - Code restructuring
- `[TEST]` - Testing additions
- `[BUILD]` - Build system changes
- `[WIP]` - Work in progress

**Good Examples:**
```bash
[PROTOCOL] Camera: Add complete ISO value range to specification

- Added all 35 ISO values from 50 to 102400
- Discovered from Sony A1 camera capabilities
- Air-side and ground-side will now sync from this spec
- Prevents future divergence

[FIX] Air-Side: Remove hardcoded ISO values, load from spec

- Refactored sony_camera.cpp to load ISO from JSON
- Added PropertyLoader class for runtime JSON loading
- Removed hardcoded ISO map
- Tested with complete ISO range

[PROTOCOL] Camera: Mark shutter_speed complete on both sides

- Air-side: Implemented and tested
- Ground-side: UI implemented and tested
- End-to-end integration verified
```

**Bad Examples:**
```bash
# Too vague
[FEATURE] Added stuff

# No context
Fixed bug

# Too long in title
[FEATURE] Implemented camera shutter speed property control with dropdown UI and validation

# No details
[FIX] Camera works now
```

### Rule #3: Never Leave Orphaned Documentation

**Before making code changes:**
- ✅ Check if any documentation references affected code
- ✅ Plan documentation updates alongside code changes

**After making code changes:**
- ✅ Update relevant technical documentation
- ✅ Update appropriate PROGRESS_AND_TODO.md
- ✅ Update protocol JSON files if implementing commands/properties
- ✅ Update BUILD_AND_IMPLEMENTATION_PLAN.md if architecture changed (air-side)
- ✅ Update DOCKER_SETUP.md if Docker/build process changed (air-side)

**Documentation to code ratio:**
- For every 100 lines of code, expect ~20-30 lines of documentation updates
- If you wrote code but didn't update any docs, something is wrong!

### Rule #4: Build Verification Before Committing

**MANDATORY: Every commit must have a working build**

**Air-Side (C++):**
```bash
cd sbc/build
cmake ..
make -j4

# If build fails, FIX IT before committing
# If build succeeds, optionally run tests:
./test_camera  # or other test executables
```

**Ground-Side (Android):**
```bash
cd android
./gradlew assembleDebug

# If build fails, FIX IT before committing
# Success produces: app/build/outputs/apk/debug/app-debug.apk
```

**Never commit broken code!**

### Rule #5: Work Incrementally

**Implement one thing at a time:**
- ✅ One command/property fully before starting another
- ✅ One component fully before starting another
- ✅ One bug fix fully before starting another

**Testing at each step:**
- ✅ Test immediately after implementing
- ✅ Don't accumulate untested code
- ✅ Fix issues before moving on

**Benefits:**
- Easier to debug (smaller changes)
- Clearer git history
- Less overwhelming
- Higher quality

---

## 🔹 AIR-SIDE SPECIFICS (C++ SBC)

### Air-Side Session Start Extensions

**Additional checks for C++ development:**

1. **Check Docker Status** (if using Docker):
   ```bash
   docker ps | grep dpm
   # Should show running container if applicable
   ```

2. **Verify Sony SDK:**
   ```bash
   ls ~/sony_sdk/lib/
   # Should see libCr_Core.so and CrAdapter/ directory
   ```

3. **Check Build Directory:**
   ```bash
   ls sbc/build/
   # Should exist and contain CMake files
   ```

4. **Check for hardcoded values (NEW!):**
   ```bash
   grep -rn "std::vector.*ISO\|ISO.*{" sbc/src/ | grep -v generated | grep -v "\/\/"
   # Should return NOTHING or only generated files
   ```

### C++ Build System

**CMake Configuration:**
```bash
cd sbc/build
cmake .. -DCMAKE_BUILD_TYPE=Debug  # For development
cmake .. -DCMAKE_BUILD_TYPE=Release  # For production

make -j4  # Use 4 parallel jobs
```

**Build Targets:**
```bash
make payload_server    # Main executable
make test_camera       # Camera test utility
make clean             # Clean build artifacts
make install           # Install to system (optional)
```

**Build Output:**
- Executables: `sbc/build/`
- Libraries: `sbc/build/lib/`

### Specification-Compliant Implementation (Air-Side)

**Preferred Approach: Code Generation**

If `tools/generate_property_code.py` exists:

```cmake
# In CMakeLists.txt
add_custom_command(
    OUTPUT ${CMAKE_SOURCE_DIR}/src/camera/generated_properties.cpp
    COMMAND python3 ${CMAKE_SOURCE_DIR}/../tools/generate_property_code.py 
            > ${CMAKE_SOURCE_DIR}/src/camera/generated_properties.cpp
    DEPENDS ${CMAKE_SOURCE_DIR}/../docs/protocol/camera_properties.json
    COMMENT "Generating camera property code from specification"
)

add_custom_target(generate_properties ALL
    DEPENDS ${CMAKE_SOURCE_DIR}/src/camera/generated_properties.cpp
)
```

**Alternative: Runtime JSON Loading**

```cpp
// camera_property_loader.h
#include <nlohmann/json.hpp>
#include <unordered_map>
#include <string>

class PropertyLoader {
public:
    static std::unordered_map<std::string, CrInt64u> loadIsoValues();
    static std::unordered_map<std::string, CrInt64u> loadShutterValues();
    // ... other properties
    
private:
    static json loadSpecification();
    static CrInt64u mapIsoToSonySDK(const std::string& iso);
};

// Usage in sony_camera.cpp
void SonyCamera::initialize() {
    iso_map_ = PropertyLoader::loadIsoValues();
    // Now iso_map_ contains values from specification
}
```

**NEVER do this:**
```cpp
// ❌ FORBIDDEN - Hardcoded values
const std::vector<std::string> ISO_VALUES = {
    "50", "64", "80", "100", // ...
};

// ❌ FORBIDDEN - Hardcoded map
const std::unordered_map<std::string, CrInt64u> ISO_MAP = {
    {"50", CrISO_50},
    {"64", CrISO_64},
    // ...
};
```

### Docker Workflow (If Applicable)

**Starting Docker Container:**
```bash
cd sbc
docker-compose up -d  # Start in background
docker-compose logs -f  # View logs
```

**Accessing Container:**
```bash
docker exec -it dpm-sbc bash
# Now you're inside the container
cd /workspace
```

**Building Inside Docker:**
```bash
docker exec -it dpm-sbc bash
cd /workspace/build
cmake ..
make -j4
```

**Stopping Docker:**
```bash
docker-compose down
```

### Memory Leak Testing

**MANDATORY for C++ development:**

```bash
# After every significant change, run valgrind:
cd sbc/build
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --verbose \
         --log-file=valgrind-out.txt \
         ./payload_server

# Check the output:
cat valgrind-out.txt | grep "definitely lost"
cat valgrind-out.txt | grep "indirectly lost"

# Should see: "All heap blocks were freed -- no leaks are possible"
```

**When to run valgrind:**
- ✅ After implementing new features
- ✅ Before committing significant changes
- ✅ Weekly during active development
- ✅ Before marking tasks as complete

### Sony SDK Integration

**Common SDK Operations:**

```cpp
// Initialize SDK
CrInt32u ret = SDK::Init();

// Get device list
ICrEnumCameraObjectInfo* camera_list = nullptr;
ret = SDK::EnumCameraObjects(&camera_list);

// Connect to camera
SDK::Connect(device_handle, callback);

// Get property
SDK::GetDeviceProperty(device_handle, property_code, &value);

// Set property
SDK::SetDeviceProperty(device_handle, property_code, &value);

// Release SDK
SDK::Release();
```

**Error Code Handling:**
```cpp
if (ret != CrError_None) {
    // Map to DPM error codes
    return ErrorCode::CAMERA_ERROR;
}
```

### C++ Best Practices (Mandatory)

**C++17 Features:**
- ✅ Use `std::unique_ptr` and `std::shared_ptr` for memory management
- ✅ Use RAII for resource management
- ✅ Use `std::optional` for optional values
- ✅ Use structured bindings where appropriate
- ✅ Use `constexpr` for compile-time constants

**Threading:**
- ✅ Use `std::thread` for threads
- ✅ Use `std::mutex` for synchronization
- ✅ Use `std::lock_guard` or `std::unique_lock` for lock management
- ✅ Avoid manual lock/unlock

**Memory Management:**
- ✅ Prefer stack allocation over heap
- ✅ Use smart pointers for heap allocation
- ✅ Never use raw `new`/`delete` without good reason
- ✅ Initialize all variables
- ✅ Use `std::vector` instead of C arrays

**Error Handling:**
- ✅ Return error codes or exceptions
- ✅ Check all Sony SDK return values
- ✅ Log errors appropriately
- ✅ Clean up resources on error paths

**Code Organization:**
```cpp
// Good structure:
class CameraManager {
private:
    std::unique_ptr<SonyCameraImpl> impl_;
    std::mutex mutex_;
    
public:
    CameraManager() = default;
    ~CameraManager() = default;
    
    // Disable copy
    CameraManager(const CameraManager&) = delete;
    CameraManager& operator=(const CameraManager&) = delete;
    
    // Enable move
    CameraManager(CameraManager&&) = default;
    CameraManager& operator=(CameraManager&&) = default;
    
    ErrorCode connect();
    ErrorCode setProperty(const std::string& property, const PropertyValue& value);
};
```

### Air-Side File Structure

```
sbc/
├── CMakeLists.txt           # Main CMake config
├── src/
│   ├── main.cpp             # Entry point
│   ├── config.h             # Configuration constants
│   ├── network/
│   │   ├── tcp_server.cpp   # TCP command server
│   │   └── udp_broadcaster.cpp  # UDP status/heartbeat
│   ├── protocol/
│   │   └── message_handler.cpp  # JSON message processing
│   ├── camera/
│   │   ├── sony_camera.cpp      # Sony SDK wrapper
│   │   ├── property_loader.cpp  # Load properties from JSON
│   │   └── generated_properties.cpp  # Generated from spec (if using code gen)
│   └── gimbal/
│       └── gimbal_interface.cpp  # Gimbal control
├── include/
│   └── [corresponding headers]
├── build/                   # CMake build directory
├── tests/
│   └── test_camera.cpp      # Test utilities
└── docs/
    ├── PROGRESS_AND_TODO.md
    ├── BUILD_AND_IMPLEMENTATION_PLAN.md
    └── DOCKER_SETUP.md
```

### Air-Side Troubleshooting

**Issue: "Sony SDK header not found"**
```bash
# Check SDK location
ls ~/sony_sdk/include/
# Should see CrTypes.h, ICrCameraObjectInfo.h, etc.

# Verify CMakeLists.txt includes:
include_directories(${CMAKE_SOURCE_DIR}/../sony_sdk/include)
```

**Issue: "libCr_Core.so: cannot open shared object file"**
```bash
# Add to LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/sony_sdk/lib

# Or add to CMakeLists.txt:
set(CMAKE_INSTALL_RPATH "${CMAKE_SOURCE_DIR}/../sony_sdk/lib")
```

**Issue: "Camera not detected"**
```bash
# Check USB connection
lsusb | grep Sony
# Should see: Bus XXX Device XXX: ID 054c:XXXX Sony Corp.

# Check permissions
ls -l /dev/bus/usb/XXX/XXX
# Should be accessible by your user

# Check udev rules:
cat /etc/udev/rules.d/99-sony-camera.rules
# Should have: SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"
```

**Issue: "Valgrind reports memory leaks"**
```bash
# Common causes:
# 1. Forgot to release Sony SDK
# 2. Raw pointers instead of smart pointers
# 3. Circular references in shared_ptr

# Fix:
# - Ensure SDK::Release() is called
# - Convert raw pointers to unique_ptr/shared_ptr
# - Break circular references with weak_ptr
```

**Issue: "Hardcoded values detected"**
```bash
# Search for violations
grep -rn "std::vector.*ISO\|ISO.*{" sbc/src/ | grep -v generated

# If found:
# 1. STOP implementing
# 2. Refactor to use PropertyLoader or code generation
# 3. Verify camera_properties.json has correct values
# 4. Update spec if needed
# 5. Re-implement using spec
```

---

## 🔹 GROUND-SIDE SPECIFICS (Android App)

### Ground-Side Session Start Extensions

**Additional checks for Android development:**

1. **Check Gradle Status:**
   ```bash
   cd android
   ./gradlew --status
   ```

2. **Check Device Connection:**
   ```bash
   adb devices
   # Should show connected device or emulator
   ```

3. **Check for Wireless ADB (H16):**
   ```bash
   adb connect 192.168.144.11:5555
   ```

4. **Check for hardcoded values (NEW!):**
   ```bash
   grep -rn "arrayOf.*ISO\|listOf.*ISO" android/app/src/ | grep -v generated | grep -v "\/\/"
   # Should return NOTHING or only generated files
   ```

### Android Build System

**Gradle Build:**
```bash
cd android

# Clean build
./gradlew clean

# Build debug APK
./gradlew assembleDebug

# Build release APK (signed)
./gradlew assembleRelease

# Install on connected device
./gradlew installDebug

# Run tests
./gradlew test
```

**Build Output:**
- Debug APK: `app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `app/build/outputs/apk/release/app-release.apk`

### Specification-Compliant Implementation (Ground-Side)

**Copy specification to assets:**

```
android/app/src/main/assets/camera_properties.json
# Copy from docs/protocol/camera_properties.json
```

**Load at runtime:**

```kotlin
// PropertyLoader.kt
object PropertyLoader {
    fun loadIsoValues(context: Context): List<String> {
        val json = context.assets.open("camera_properties.json")
            .bufferedReader()
            .use { it.readText() }
        
        val spec = JSONObject(json)
        val isoArray = spec.getJSONObject("properties")
            .getJSONObject("iso")
            .getJSONObject("validation")
            .getJSONArray("values")
        
        return (0 until isoArray.length()).map { isoArray.getString(it) }
    }
    
    fun loadShutterValues(context: Context): List<String> {
        // Similar implementation
    }
    
    // ... other properties
}

// In your Fragment/ViewModel
class CameraControlFragment : Fragment() {
    private lateinit var isoValues: List<String>
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Load from specification, NOT hardcoded
        isoValues = PropertyLoader.loadIsoValues(requireContext())
    }
    
    private fun setupIsoSpinner() {
        val adapter = ArrayAdapter(
            requireContext(),
            android.R.layout.simple_spinner_item,
            isoValues  // From spec, not hardcoded!
        )
        binding.isoSpinner.adapter = adapter
    }
}
```

**NEVER do this:**
```kotlin
// ❌ FORBIDDEN - Hardcoded values
val isoValues = arrayOf(
    "50", "64", "80", "100", // ...
)

// ❌ FORBIDDEN - Hardcoded list
val isoValues = listOf(
    "50", "64", "80", "100", // ...
)
```

### APK Deployment

**Install via ADB:**
```bash
# Install new APK
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Install to specific device
adb -s <device_id> install -r app-debug.apk

# Uninstall first (if needed)
adb uninstall com.dpm.groundstation
adb install app-debug.apk
```

**Launch App:**
```bash
adb shell am start -n com.dpm.groundstation/.MainActivity
```

### Viewing Logs

**Logcat:**
```bash
# View all app logs
adb logcat | grep DPM

# View specific tag
adb logcat -s NetworkClient

# Save to file
adb logcat > logcat.txt

# Clear logs first
adb logcat -c
adb logcat | grep DPM
```

### Commented-Out Commands Workflow (Ground-Side)

**Ground-side uses a specific pattern for planned features:**

```kotlin
class NetworkClient {
    // ✅ IMPLEMENTED commands
    fun captureImage() {
        val command = Command(...)
        sendCommand(command)
    }

    // 🔜 PLANNED commands (commented out until ready)
    // fun setCameraProperty(property: String, value: Any) {
    //     val command = Command(
    //         command = "camera.set_property",
    //         parameters = mapOf("property" to property, "value" to value)
    //     )
    //     sendCommand(command)
    // }

    // fun focusCamera(direction: String, speed: Int = 3) {
    //     val command = Command(
    //         command = "camera.focus",
    //         parameters = mapOf("action" to direction, "speed" to speed)
    //     )
    //     sendCommand(command)
    // }
}
```

**CC Workflow:**
1. At session start, search for `// fun` in NetworkClient.kt
2. Ask user: "I see X commented-out commands. Should I implement any?"
3. Check if air-side has implemented the handler
4. If air-side ready + user approves:
   - Uncomment the method
   - Add ViewModel method
   - Add UI elements to call it
   - **Load property values from spec, don't hardcode**
   - Test end-to-end
   - Update `commands.json` to `"ground_side": true`

### Android Architecture (MVVM)

**Required Pattern:**

```
UI Layer (Fragment/Activity)
    ↓ observes
ViewModel (holds UI state)
    ↓ calls
Repository (optional, for complex data)
    ↓ calls
NetworkClient (protocol implementation)
    ↓ sends
Network Commands
```

**Example:**
```kotlin
// Fragment
class CameraControlFragment : Fragment() {
    private val viewModel: CameraViewModel by viewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.cameraState.observe(viewLifecycleOwner) { state ->
            // Update UI
        }
        
        binding.captureButton.setOnClickListener {
            viewModel.captureImage()
        }
    }
}

// ViewModel
class CameraViewModel(private val networkClient: NetworkClient) : ViewModel() {
    private val _cameraState = MutableLiveData<CameraState>()
    val cameraState: LiveData<CameraState> = _cameraState
    
    fun captureImage() {
        viewModelScope.launch {
            try {
                networkClient.captureImage()
                _cameraState.value = CameraState.Capturing
            } catch (e: Exception) {
                _cameraState.value = CameraState.Error(e.message)
            }
        }
    }
}
```

### Kotlin Best Practices (Mandatory)

**Coroutines:**
- ✅ Use `viewModelScope` in ViewModels
- ✅ Use `lifecycleScope` in Fragments/Activities
- ✅ Use `Dispatchers.IO` for network/disk operations
- ✅ Use `Dispatchers.Main` for UI updates
- ✅ Handle cancellation properly

**Null Safety:**
- ✅ Use nullable types (`Type?`) when values can be null
- ✅ Use safe calls (`?.`) for nullable access
- ✅ Use `!!` only when absolutely certain non-null
- ✅ Prefer `?.let { }` over null checks

**Data Classes:**
- ✅ Use `data class` for models
- ✅ Use `sealed class` for state representations
- ✅ Prefer immutability (`val` over `var`)

**Example:**
```kotlin
// State representation
sealed class CameraState {
    object Idle : CameraState()
    object Connecting : CameraState()
    object Connected : CameraState()
    object Capturing : CameraState()
    data class Error(val message: String) : CameraState()
}

// Data model
data class CameraSettings(
    val shutterSpeed: String,
    val aperture: String,
    val iso: Int,
    val whiteBalance: String
)
```

### Ground-Side File Structure

```
android/
├── app/
│   ├── build.gradle
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── assets/
│       │   └── camera_properties.json  # Copy of spec!
│       ├── java/com/dpm/groundstation/
│       │   ├── MainActivity.kt
│       │   ├── ui/
│       │   │   ├── camera/
│       │   │   │   ├── CameraControlFragment.kt
│       │   │   │   └── CameraViewModel.kt
│       │   │   └── status/
│       │   │       └── StatusFragment.kt
│       │   ├── network/
│       │   │   ├── NetworkClient.kt
│       │   │   ├── NetworkSettings.kt
│       │   │   └── ProtocolMessages.kt
│       │   └── util/
│       │       ├── PropertyLoader.kt  # NEW - Loads from spec
│       │       └── Extensions.kt
│       └── res/
│           ├── layout/
│           ├── values/
│           └── drawable/
├── build.gradle
├── settings.gradle
└── docs/
    └── PROGRESS_AND_TODO.md
```

### Ground-Side Troubleshooting

**Issue: "Gradle build failed"**
```bash
# Check error messages
./gradlew assembleDebug --stacktrace

# Common causes:
# 1. Dependency conflict → Update versions in build.gradle
# 2. Kotlin compilation error → Check syntax and imports
# 3. Resource issue → Check XML files
# 4. Cache corruption → ./gradlew clean or invalidate caches
```

**Issue: "Can't connect to device via ADB"**
```bash
# Check device connection
adb devices

# If "unauthorized":
# - Check device screen for USB debugging prompt
# - Allow debugging on device

# If device not showing:
# - Enable developer options on device
# - Enable USB debugging
# - Try different USB port
# - Restart ADB: adb kill-server && adb start-server

# For H16 (wireless):
adb connect 192.168.144.11:5555
```

**Issue: "App crashes on startup"**
```bash
# View crash logs
adb logcat | grep AndroidRuntime

# Common causes:
# 1. Missing permissions in manifest
# 2. Null pointer exception → Check initialization
# 3. Network on main thread → Use coroutines
# 4. Resource not found → Clean and rebuild
# 5. Missing camera_properties.json in assets
```

**Issue: "Network connection failing"**
```bash
# Verify network in logcat
adb logcat | grep DPM

# Check:
# 1. INTERNET permission in manifest
# 2. Correct IP address (192.168.144.20)
# 3. Correct ports (5000 TCP, 5001/5002 UDP)
# 4. Air-side service running
# 5. Firewall not blocking
```

**Issue: "Property values don't match air-side"**
```bash
# Check specification
cat docs/protocol/camera_properties.json | jq '.properties.iso'

# Verify assets file is up to date
# 1. Compare assets/camera_properties.json with docs/protocol/camera_properties.json
# 2. If different, copy latest version
# 3. Rebuild app
# 4. Clear app data and reinstall
```

---

## 🛠️ COMMON TROUBLESHOOTING

### Git Issues

**Issue: "Git pull has conflicts"**
```bash
# See conflicting files
git status

# For protocol files (CAREFUL!):
# 1. DON'T auto-merge protocol JSON files
# 2. Tell user to manually merge
# 3. Verify both sides' implementations are preserved

# For code files:
# 1. Identify conflict markers <<<< >>>> ====
# 2. Discuss with user which version to keep
# 3. Test after resolving
```

**Issue: "Accidentally committed to wrong branch"**
```bash
# If not pushed yet:
git reset --soft HEAD~1  # Undo commit, keep changes
git stash                # Save changes
git checkout main        # Switch to correct branch
git stash pop            # Restore changes
git commit              # Commit again

# If already pushed: Contact user!
```

### Protocol Issues

**Issue: "Commands not working between platforms"**
```bash
# Debugging steps:
# 1. Check protocol versions match
cat docs/protocol/protocol_v1.0.json | jq '.constants.protocol_version'

# 2. Check command is implemented on both sides
cat docs/protocol/commands.json | jq '.commands."command.name".implemented'

# 3. Check for typos in command names
# 4. Verify JSON syntax is correct
# 5. Check network connectivity (ping the other side)
```

**Issue: "Property validation failing"**
```bash
# Check property definition:
cat docs/protocol/camera_properties.json | jq '.properties."property_name".validation'

# Verify:
# 1. Value is in allowed values list
# 2. Value matches expected type
# 3. Dependencies are satisfied (e.g., WB mode for WB temperature)
# 4. Camera is in correct mode (some properties restricted by mode)
```

**Issue: "Specification divergence detected"**
```bash
# Run audit
./tools/audit_protocol_sync.sh

# If divergence found:
# 1. STOP all implementation work
# 2. Identify which is correct: spec or implementation?
# 3. If implementation is correct:
#    - Update specification first
#    - Commit: [PROTOCOL] Update spec with correct values
# 4. If specification is correct:
#    - Refactor implementation to match spec
#    - Remove hardcoded values
#    - Commit: [FIX] Remove hardcoded values, use spec
# 5. Verify sync with audit script
# 6. Resume normal work
```

---

## 📝 SUMMARY - THE GOLDEN RULES

### Universal Rules (Both Platforms)

1. 🔴 **ALWAYS read CC_READ_THIS_FIRST.md at session start**
2. 🔴 **ALWAYS pull latest from Git before starting work**
3. 🔴 **ALWAYS run protocol audit script (if available)**
4. 🔴 **ALWAYS check protocol synchronization (commands.json + camera_properties.json)**
5. 🔴 **ALWAYS read specification before implementing properties**
6. 🔴 **NEVER hardcode camera property values**
7. 🔴 **ALWAYS read appropriate PROGRESS_AND_TODO.md**
8. 🔴 **ALWAYS update PROGRESS_AND_TODO.md after significant changes**
9. 🔴 **ALWAYS commit regularly (every 30-60 min)**
10. 🔴 **ALWAYS use [TYPE] prefix in commit messages**
11. 🔴 **ALWAYS verify build succeeds before committing**
12. 🔴 **ALWAYS commit before ending session**
13. 🔴 **ALWAYS work incrementally (one thing at a time)**

### Specification-First Rules (CRITICAL!)

14. 🔴 **ALWAYS update specification BEFORE implementing new property values**
15. 🔴 **ALWAYS load property values from JSON (or generate from JSON)**
16. 🔴 **NEVER assume specification is complete - verify and update**
17. 🔴 **ALWAYS commit spec updates separately from implementation**
18. 🔴 **ALWAYS run audit checks for hardcoded values before committing**

### Platform-Specific Rules

**Air-Side (C++):**
- 🟡 Run valgrind regularly for memory leak detection
- 🟡 Use smart pointers, avoid raw new/delete
- 🟡 Check Sony SDK return values
- 🟡 Test with Docker if applicable
- 🟡 Use PropertyLoader or code generation for camera properties

**Ground-Side (Android):**
- 🟡 Follow MVVM architecture pattern
- 🟡 Use Coroutines for async operations
- 🟡 Check commented-out methods in NetworkClient.kt
- 🟡 Test on device/emulator before committing
- 🟡 Copy camera_properties.json to assets/ directory
- 🟡 Use PropertyLoader to load values from assets

---

## 🎓 FOR NEW CLAUDE CODE INSTANCES

### First Session on This Project:

1. ✅ Read this file (CC_READ_THIS_FIRST.md) - you're doing it!
2. ✅ Identify platform (air-side or ground-side)
3. ✅ Read appropriate PROGRESS_AND_TODO.md thoroughly
4. ✅ Skim Project_Summary_and_Action_Plan.md (overview only)
5. ✅ Read protocol documentation (commands.json, camera_properties.json)
6. ✅ **Run audit script (if available)**
7. ✅ **Check for hardcoded values in codebase**
8. ✅ Check `git log --oneline -20` (understand recent history)
9. ✅ Identify current phase and next task
10. ✅ Start working!

### Subsequent Sessions:

1. ✅ Read this file (CC_READ_THIS_FIRST.md)
2. ✅ Pull latest from Git
3. ✅ **Run audit script**
4. ✅ Check protocol synchronization
5. ✅ **Search for hardcoded values**
6. ✅ Read appropriate PROGRESS_AND_TODO.md
7. ✅ Check `git status` and `git log --oneline -5`
8. ✅ Continue work

---

## ✅ SESSION END CHECKLIST

**Before ending EVERY work session, verify:**

- [ ] PROGRESS_AND_TODO.md updated with today's work
- [ ] All task checkboxes reflect reality
- [ ] Completion percentages updated
- [ ] Visual progress bars updated (if applicable)
- [ ] "Last Updated" timestamp is current
- [ ] Issue Tracker reflects current bugs/blockers
- [ ] Protocol JSON files updated if implemented commands/properties
- [ ] **Specification updated if discovered new property values**
- [ ] **No hardcoded property values in new code**
- [ ] All code changes are committed
- [ ] All commits have descriptive messages with [TYPE] prefix
- [ ] All commits pushed to origin/main
- [ ] Build succeeds (make/gradle)
- [ ] No compiler errors or unresolved warnings
- [ ] Memory leaks checked (air-side with valgrind)
- [ ] No orphaned documentation
- [ ] No [WIP] commits unless work is genuinely incomplete
- [ ] **Audit script passes (if available)**

**If all checked: You're good! 🎉**

---

## 🔧 TOOLS AND SCRIPTS

### Available Tools (Check if they exist)

**Protocol Audit Script:**
```bash
# Location: tools/audit_protocol_sync.sh
# Purpose: Check for specification divergence
# Run at: Every session start

./tools/audit_protocol_sync.sh
```

**Property Code Generator (Future):**
```bash
# Location: tools/generate_property_code.py
# Purpose: Generate C++ code from camera_properties.json
# Run: Automatically via CMake

python3 tools/generate_property_code.py > sbc/src/camera/generated_properties.cpp
```

**Pre-Commit Hook:**
```bash
# Location: .git/hooks/pre-commit
# Purpose: Prevent committing hardcoded property values
# Runs: Automatically on git commit

# If not installed, check .git/hooks/ directory
```

### Creating Missing Tools

If audit script doesn't exist, create it:

```bash
#!/bin/bash
# tools/audit_protocol_sync.sh

echo "======================================"
echo "PROTOCOL SYNCHRONIZATION CHECK"
echo "======================================"

# Check camera_properties.json
echo "📋 Checking camera_properties.json..."
jq -r '.properties.iso.validation.values[]?' docs/protocol/camera_properties.json | sort -n

echo ""
echo "⚠️  NOW MANUALLY CHECK:"
echo "  Air-Side:  grep -rn 'ISO.*{' sbc/src/ | grep -v generated"
echo "  Ground-Side: grep -rn 'arrayOf.*ISO' android/app/src/ | grep -v generated"
echo ""
```

---

**Document Status:** ✅ Active - Combined Air-Side & Ground-Side + Spec Enforcement  
**Version:** 2.1  
**Last Updated:** October 27, 2025  
**Location:** Project root (DPM-V2/CC_READ_THIS_FIRST.md)  
**Maintained By:** Human oversight, enforced by Claude Code

**🔴 REMEMBER: Read this document at the start of EVERY session! 🔴**
**🔴 REMEMBER: Specification is SINGLE SOURCE OF TRUTH! 🔴**