# Claude Code - READ THIS FIRST
## DPM Payload Manager Project Rules & Workflow

**Date Created:** October 25, 2025
**Last Updated:** October 29, 2025
**Version:** 2.4 (Platform ID Commit Prefix Mandatory)
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

- 🔹 **WindowsTools (Python Diagnostic)?** → Working in `WindowsTools/` directory
  - Read Common Rules below, then jump to [WindowsTools Specifics](#-windowstools-specifics-python-diagnostic)
  - Check `WindowsTools/PROGRESS_AND_TODO.md` for current status

- 🔹 **Protocol/Documentation?** → Working in `docs/` directory
  - Read Common Rules below
  - Focus on Protocol Synchronization section

---

## 🔴 CRITICAL: PROTOCOL FILE LOCATION

**BOTH Air-Side AND Ground-Side Claude Code instances MUST understand this:**

### Protocol Files Location

**✅ CORRECT Location for Communal Protocol Files:**
```
~/DPM-V2/protocol/
  ├── camera_properties.json    ← Shared by BOTH Air-Side and Ground-Side
  ├── commands.json              ← Shared by BOTH Air-Side and Ground-Side
  └── [other protocol specs]     ← Shared specification files
```

**❌ WRONG - Protocol files are NOT in docs/ folder:**
```
~/DPM-V2/docs/protocol/   ← ❌ OLD LOCATION - DO NOT USE
```

### Key Rules for Protocol Files

1. **🔴 Protocol files MUST be at `~/DPM-V2/protocol/`**
   - These are RUNTIME specification files
   - NOT documentation files
   - Shared by both platforms

2. **🔴 NEVER hard-code camera property values**
   - Air-Side C++: PropertyLoader loads from `protocol/camera_properties.json`
   - Ground-Side Android: PropertyLoader loads from `assets/camera_properties.json` (bundled copy)
   - Android must sync assets file from root protocol/ directory

3. **🔴 Single Source of Truth**
   - `~/DPM-V2/protocol/camera_properties.json` is the master
   - Air-Side reads directly from protocol/
   - Ground-Side must copy to assets/ before building APK

4. **🔴 Never commit if protocol files are missing**
   - Check that `protocol/camera_properties.json` exists
   - Verify PropertyLoader can load it
   - Test before committing

### Documentation Location

**Documentation files (not protocol specs) go in docs/:**
```
~/DPM-V2/docs/
  ├── CC_READ_THIS_FIRST.md          ← You are here
  ├── CAMERA_PROPERTIES_FIX_TRACKING.md
  ├── ISO_AUTO_FIX_SUMMARY.md
  └── protocol/                      ← Protocol DOCUMENTATION (not specs)
      ├── PROTOCOL_VALUE_MAPPING.md
      ├── README_protocol.md
      └── [other protocol docs]
```

**Summary:**
- **Protocol SPECS** (JSON files) → `~/DPM-V2/protocol/`
- **Protocol DOCS** (markdown explanations) → `~/DPM-V2/docs/protocol/`

---

## 📋 COMMON SESSION START CHECKLIST
**Every session, regardless of platform:**

### 1. Read This Document
- ✅ **ALWAYS** read `CC_READ_THIS_FIRST.md` first (this file)
- This is your source of truth for workflow rules

### 2. 🔴 MANDATORY: Ask User Which Platform They're Working On
- ✅ **REQUIRED** - At the start of EVERY session, ask the user:

  **"Which platform are you working on today?"**
  - **Air-Side** (C++ SBC) → Platform ID: `AIR-SIDE`
  - **Ground-Station** (Android) → Platform ID: `ANDROID`
  - **Windows Tools** (Python) → Platform ID: `WINDOWS`
  - **Protocol/Docs** → Platform ID: `PROTOCOL` or `DOCS`

- ✅ **Record the platform ID** - You'll use it in ALL commit messages
- ✅ **DO NOT PROCEED** until user confirms their platform
- ⚠️ **CRITICAL** - The platform ID MUST be prefixed to ALL git commits this session

**Example Session Start:**
```
Claude: "Which platform are you working on today? (Air-Side, Ground-Station/Android, or Windows Tools)"
User: "Air-Side"
Claude: "Got it! Working on Air-Side platform. All commits will use [AIR-SIDE] prefix."
```

### 3. Pull Latest Changes from Git
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

### 3. Check Protocol Synchronization
- ✅ **MANDATORY** - Check `protocol/commands.json` for new commands
- ✅ **MANDATORY** - Check `protocol/camera_properties.json` for new properties
- ✅ Check if the other platform has implemented things you need to implement
- ✅ **ASK USER** about any new commands/properties before implementing
- ⚠️ **CRITICAL** - Protocol sync MUST happen every session

**🔴 CRITICAL: Protocol files are at ~/DPM-V2/protocol/ NOT in docs/ folder! 🔴**
**These are shared specification files used by BOTH Air-Side and Ground-Side**

**Run these checks:**

```bash
# For AIR-SIDE: Check what you need to implement
cat protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.air_side == false) | .key'

cat protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.air_side == false) | .key'

# For GROUND-SIDE: Check what you need to implement
cat protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.ground_side == false) | .key'

cat protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.ground_side == false) | .key'
```

### 4. Check Current Status
- ✅ Read the appropriate `PROGRESS_AND_TODO.md`:
  - **Air-side:** `sbc/docs/PROGRESS_AND_TODO.md`
  - **Ground-side:** `android/docs/PROGRESS_AND_TODO.md`
- Understand:
  - What phase we're in
  - What's been completed
  - What's currently blocked
  - What to work on next

### 5. Read Relevant Technical Docs (If Needed)
- ⚠️ **DO NOT** read `Project_Summary_and_Action_Plan.md` unless explicitly asked
- ⚠️ **DO NOT** re-read technical specs you've already reviewed in this session
- ✅ **DO** read specific technical docs when starting new features

**Air-Side Docs:**
- `sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md` - When implementing new components
- `sbc/docs/DOCKER_SETUP.md` - When working with Docker or Sony SDK
- Protocol specs - When implementing protocol features
- **Sony SDK HTML Documentation** - When working on camera integration (see Air-Side section)

**Ground-Side Docs:**
- `docs/Command_Protocol_Specification_v1.0.md` - When implementing protocol features
- `docs/Protocol_Implementation_Quick_Start.md` - Protocol implementation guide
- `docs/Phase1_Requirements_Update.md` - Feature requirements
- `docs/Updated_System_Architecture_H16.md` - System architecture
- Android-specific guides when implementing UI/networking

### 6. Understand Git Status
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
cat protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.SIDE_side == false) | .key'
# Replace SIDE with 'air' or 'ground'

# Check what the OTHER side has implemented
cat protocol/commands.json | jq -r '.commands | to_entries[] |
  select(.value.implemented.OTHER_side == true and
         .value.implemented.YOUR_side == false) | .key'
# These are ready to implement - the other side can already handle them!
```

**Camera Properties Check:**
```bash
# Check for new properties
cat protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.SIDE_side == false) | .key'

# Check what the OTHER side has implemented
cat protocol/camera_properties.json | jq -r '.properties | to_entries[] |
  select(.value.implemented.OTHER_side == true and
         .value.implemented.YOUR_side == false) | .key'

# Check Phase 1 priority properties
cat protocol/camera_properties.json | jq '.implementation_phases.phase_1.properties[]'
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
1. User adds command to protocol/commands.json
   └─ Sets "air_side": false, "ground_side": might be true

2. CC detects new command at session start
   └─ Asks user what it does and if it should be implemented

3. CC implements in C++ (tcp_server.cpp)
   ├─ Add handler function (e.g., handleCameraFocus)
   ├─ Add route in processCommand()
   ├─ Add Sony SDK calls if needed
   ├─ Add any new error codes to messages.h
   └─ Test implementation

4. CC updates protocol/commands.json
   └─ Set "air_side": true

5. CC updates sbc/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [AIR-SIDE][PROTOCOL] Implemented [command.name] command
```

**Ground-Side Flow:**
```
1. User adds command to protocol/commands.json
   └─ May add commented-out method to NetworkClient.kt

2. CC detects new command at session start
   └─ Asks user about UI requirements

3. CC implements in Kotlin
   ├─ Uncomment/add method in NetworkClient.kt
   ├─ Add ViewModel method to call it
   ├─ Add UI button/control in appropriate Fragment
   ├─ Add error handling
   └─ Test with air-side (if available)

4. CC updates protocol/commands.json
   └─ Set "ground_side": true

5. CC updates android/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [ANDROID][PROTOCOL] Implemented [command.name] UI
```

#### Camera Properties Workflow

**Key Insight:** `camera.set_property` is ONE command that sets MANY properties.

**Properties are different from commands:**
- Commands: One command → One handler → One UI element
- Properties: One command → Many properties → Many UI elements

**When implementing camera properties:**

1. **Check which properties are Phase 1:**
   ```bash
   cat protocol/camera_properties.json | jq '.implementation_phases.phase_1.properties[]'
   ```

2. **Pick ONE property to implement at a time:**
   - Start with high-priority (exposure triangle: shutter, aperture, ISO)
   - Implement air-side Sony SDK call
   - Add ground-side UI control
   - Test thoroughly
   - Mark property as implemented

3. **UI considerations (ground-side):**
   - Check `ui_hints` in protocol/camera_properties.json:
     - `dropdown` → Spinner/Dropdown
     - `slider` → SeekBar
     - `segmented_control` → RadioGroup/ToggleButton
   - Different properties need different controls
   - Some properties depend on others (e.g., WB temperature requires WB mode = "temperature")

4. **Example: Implementing shutter_speed:**
   ```
   Air-Side:
   - Add to handleCameraSetProperty()
   - Map value to Sony SDK ShutterSpeedValue enum
   - Call SDK::SetDeviceProperty(CrDeviceProperty_ShutterSpeed, value)
   - Test with real camera
   - Mark "air_side": true
   
   Ground-Side:
   - Add Spinner with values from validation.values in JSON
   - Wire to networkClient.setCameraProperty("shutter_speed", value)
   - Implement validation
   - Test end-to-end
   - Mark "ground_side": true
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

❌ **DON'T:**
- Implement commands/properties not in JSON files
- Assume what something should do without asking
- Mark implemented until fully done and tested
- Skip protocol check at session start
- Implement multiple things at once
- Send commands/properties the other side can't handle

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
**Last Updated:** October 25, 2025 15:30 - After implementing shutter_speed property
```

### Rule #2: Commit to Git Regularly

**Commit frequency rules:**

1. **After completing any functional unit:**
   - ✅ New feature implemented and tested
   - ✅ Bug fixed and verified
   - ✅ New component created
   - ✅ Documentation updated significantly

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
[PLATFORM-ID][TYPE] Component: Brief one-line summary (max 72 chars)

- Detailed point 1 (what changed)
- Detailed point 2 (why it changed)
- Detailed point 3 (impact/result)
```

**🔴 MANDATORY: Platform ID Prefixes**
- `[AIR-SIDE]` - Changes to Air-Side (C++ SBC in sbc/)
- `[ANDROID]` - Changes to Ground-Station Android app (android/)
- `[WINDOWS]` - Changes to Windows Tools (WindowsTools/)
- `[PROTOCOL]` - Changes to protocol specs (protocol/)
- `[DOCS]` - Documentation changes only

**Valid TYPE prefixes (after Platform ID):**
- `[FEATURE]` - New functionality
- `[FIX]` - Bug fix
- `[PROTOCOL]` - Protocol implementation
- `[DOCS]` - Documentation update
- `[REFACTOR]` - Code restructuring
- `[TEST]` - Testing additions
- `[BUILD]` - Build system changes
- `[WIP]` - Work in progress

**Good Examples:**
```bash
[AIR-SIDE][PROTOCOL] Camera: Implemented shutter_speed property

- Sony SDK CrDeviceProperty_ShutterSpeed integration
- PropertyLoader reads values from protocol/camera_properties.json
- Validation: Enum values match specification
- Testing: Verified with Sony A1 camera

[AIR-SIDE][FIX] Docker: Resolved CrAdapter dynamic loading issue

- Root cause: Adapters statically linked in CMakeLists.txt
- Solution: Only link libCr_Core.so, copy CrAdapter/ to build dir
- Result: SDK now loads adapters dynamically

[ANDROID][FEATURE] Added camera control screen

- Implemented CameraControlFragment with MVVM pattern
- Added exposure controls (shutter, aperture, ISO)
- Connected to NetworkClient for command sending
- Tested on emulator and H16 hardware

[WINDOWS][FIX] Fix protocol.py heartbeat to match spec v1.1.0

- Added missing protocol_version field
- Fixed timestamp from milliseconds to seconds
- Corrected heartbeat payload structure
- Added client_id="WPC"

[PROTOCOL][FEATURE] Add heartbeat_spec.json v1.1.0

- Created official heartbeat message specification
- Added client_id field for client tracking
- Documented requirements for all three platforms
```

**Bad Examples:**
```bash
# ❌ Missing platform ID prefix
[FEATURE] Added stuff

# ❌ Missing platform ID AND type
Fixed bug

# ❌ Missing platform ID
[FEATURE] Implemented camera shutter speed property control with dropdown UI and validation

# ❌ Too vague (even with platform ID)
[AIR-SIDE][FEATURE] Added stuff

# ❌ No context
[ANDROID][FIX] Fixed bug

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

### 📚 Sony SDK Documentation Reference

**🔴 CRITICAL: ALWAYS CHECK SDK DOCUMENTATION BEFORE IMPLEMENTING CAMERA FUNCTIONS! 🔴**

The Sony Camera Remote SDK includes comprehensive HTML documentation that MUST be consulted when working with camera functions. Many past issues have occurred from assuming how SDK functions work rather than checking the documentation.

**Primary Documentation Location:**
```
CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/function_list/function_list.html
```

**When to Consult SDK Documentation:**

✅ **ALWAYS before:**
- Implementing any new camera property
- Calling any SDK function for the first time
- Making assumptions about function behavior
- Implementing error handling for SDK calls
- Working with SDK callback objects
- Handling SDK enumerations or constants

❌ **NEVER:**
- Assume SDK function behavior without checking docs
- Guess at parameter requirements
- Implement without verifying return value meanings
- Copy code patterns without understanding them

**Key SDK Documentation Sections:**

1. **Function List** (`function_list.html`)
   - Complete list of all SDK functions
   - Function signatures and parameters
   - Return value descriptions
   - Usage notes and requirements

2. **Camera Property Codes** 
   - `CrDeviceProperty_*` enum values
   - Valid values for each property
   - Property dependencies and restrictions

3. **Callback Interfaces**
   - `ICrCameraObjectInfo` - Camera enumeration callbacks
   - `CrDevicePropertyCallback` - Property change notifications
   - Object lifetime requirements (CRITICAL!)

4. **Error Codes**
   - `CrError_*` enum definitions
   - Error condition meanings
   - Proper error handling patterns

**Documentation Access Methods:**

```bash
# Open in browser (if running on Pi with desktop)
firefox ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/function_list/function_list.html

# Or copy to development machine for browsing
scp -r pi@192.168.x.x:~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/ ./sony_sdk_docs/
```

**Example Workflow - Adding New Camera Property:**

```
1. Check camera_properties.json for property name and validation
   └─ Example: "shutter_speed" with values ["1/8000", "1/4000", ...]

2. Open SDK HTML documentation
   └─ Search for "ShutterSpeed" or browse property list

3. Find CrDeviceProperty_ShutterSpeed in docs
   ├─ Read property description
   ├─ Check valid values (CrShutterSpeed enum)
   ├─ Note any dependencies or restrictions
   └─ Review example usage if provided

4. Implement in C++ with verified information
   ├─ Map JSON values to SDK enum values
   ├─ Use exact SDK function signature from docs
   ├─ Handle all documented error codes
   └─ Follow documented callback requirements

5. Test with real camera
   └─ Verify behavior matches documentation
```

**Common SDK Documentation Gotchas:**

⚠️ **Callback Object Lifetime**
- Documentation specifies callback object lifetime requirements
- Stack-allocated callbacks may cause connection failures
- Always check object lifetime requirements in docs

⚠️ **Property Dependencies**
- Some properties require specific camera modes
- Some properties depend on other property values
- Documentation lists these dependencies explicitly

⚠️ **Asynchronous Operations**
- Many SDK operations are asynchronous
- Documentation specifies when callbacks are used
- Response timing varies by operation

⚠️ **Thread Safety**
- Documentation indicates which functions are thread-safe
- Some operations require specific thread context
- Always verify thread safety requirements

**Quick Reference Commands:**

```bash
# Search SDK documentation for specific property
grep -r "CrDeviceProperty_ShutterSpeed" ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/

# List all device properties in SDK headers
grep "CrDeviceProperty_" ~/sony_sdk/include/CrDefines.h

# Find error code definitions
grep "CrError_" ~/sony_sdk/include/CrError.h
```

**Remember:** The Sony SDK HTML documentation has been instrumental in resolving past issues (like the callback object lifetime problem diagnosed at 90% confidence). Taking 5 minutes to read the documentation can save hours of debugging!

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
│   │   └── sony_camera.cpp  # Sony SDK wrapper
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

**Issue: "SDK function not working as expected"**
```bash
# FIRST: Check the Sony SDK HTML documentation!
# Location: CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/

# Then verify:
# 1. Function signature matches documentation
# 2. Parameters are correct type and order
# 3. Return value is being checked properly
# 4. Callback requirements are met
# 5. Thread safety requirements are satisfied
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

---

## 🔹 WINDOWSTOOLS SPECIFICS (Python Diagnostic)

### WindowsTools Session Start Extensions

**Additional checks for Python/Windows development:**

1. **Check Python Environment:**
   ```bash
   python --version  # Should be Python 3.x
   pip list | grep -E "tkinter"  # Check tkinter available
   ```

2. **Verify Protocol Access:**
   ```bash
   ls ../protocol/
   # Should see commands.json, camera_properties.json
   ```

3. **Check Configuration:**
   ```bash
   cat WindowsTools/config.json
   # Verify air_side_ip and ports are correct
   ```

### 🚨 CRITICAL: Stay in Your Lane!

**WindowsTools Development Boundaries:**

**✅ YOU MAY:**
- Create/modify ANY files in `WindowsTools/` directory
- Read from `protocol/` directory (commands.json, camera_properties.json)
- Read documentation in `docs/` directory
- Update `WindowsTools/PROGRESS_AND_TODO.md`
- Commit with `[WINDOWS][FEATURE]` or `[WINDOWS][FIX]` prefix

**❌ YOU MUST NOT:**
- Modify files in `sbc/` directory (Air-Side code)
- Modify files in `android/` directory (Ground-Side code)
- Modify files in `protocol/` directory (unless explicitly coordinated)
- Modify `docs/CC_READ_THIS_FIRST.md` (unless adding WindowsTools notes)
- Commit changes outside WindowsTools/ without explicit user approval

### Python/tkinter Development

**Project Structure:**
```
WindowsTools/
├── main.py              # Application entry point (DiagnosticApp class)
├── requirements.txt     # Python dependencies
├── config.json          # Runtime configuration (auto-created)
├── gui/
│   ├── main_window.py   # Main window framework
│   ├── widgets.py       # Reusable GUI components
│   ├── tab_connection.py    # Phase 1
│   ├── tab_protocol.py      # Phase 2
│   ├── tab_command.py       # Phase 2
│   ├── tab_camera.py        # Phase 2
│   ├── tab_system.py        # Phase 2
│   └── tab_config.py        # Phase 1
├── network/
│   ├── tcp_client.py    # TCP client for commands
│   ├── udp_listener.py  # UDP listeners (status 5Hz, heartbeat 1Hz)
│   ├── heartbeat.py     # Heartbeat sender (1Hz)
│   └── protocol.py      # Protocol message formatting
├── utils/
│   ├── config.py        # Configuration management
│   ├── logger.py        # Logging system
│   └── protocol_loader.py  # Loads protocol JSON files
├── logs/                # Log files (auto-created)
├── templates/           # Command templates (future)
└── docs/
    ├── PROGRESS_AND_TODO.md
    ├── DIAGNOSTIC_TOOL_PLAN.md
    └── README.md
```

**Running the Tool:**
```bash
cd WindowsTools
python main.py
```

**Development Workflow:**
```bash
# 1. Always pull first
git pull origin main

# 2. Check current status
cat WindowsTools/PROGRESS_AND_TODO.md

# 3. Make changes (ONLY in WindowsTools/)

# 4. Test
cd WindowsTools
python main.py

# 5. Commit with proper prefix
git add WindowsTools/
git commit -m "[WINDOWS][FEATURE] Description"
git push origin main
```

### Python Best Practices (Mandatory)

**Code Style:**
- ✅ Follow PEP 8 style guidelines
- ✅ Use type hints where appropriate
- ✅ Docstrings for all classes and functions
- ✅ Clear variable names (no single letters except counters)

**Error Handling:**
```python
try:
    # Risky operation
except SpecificException as e:
    logger.error(f"Error: {e}")
    messagebox.showerror("Error", f"Operation failed: {e}")
```

**Threading:**
- ✅ Use `threading.Thread(daemon=True)` for background tasks
- ✅ Never block the GUI thread
- ✅ Use callbacks to update GUI from background threads

**GUI Updates:**
```python
# Good: Update GUI from main thread
def callback_from_network():
    self.after(0, self._update_ui_safely)

# Bad: Update GUI from network thread (will crash)
def callback_from_network():
    self.status_label.config(text="Connected")  # ❌ CRASH!
```

### Callback Chaining Pattern

**CRITICAL:** When multiple components need callbacks, CHAIN them, don't replace:

```python
# ✅ GOOD: Chain callbacks
original_callback = client.on_connected

def my_callback():
    if original_callback:
        original_callback()  # Call original first
    # Then do my stuff
    self.do_my_thing()

client.on_connected = my_callback

# ❌ BAD: Replace callbacks (breaks other components)
client.on_connected = self.my_callback  # Original lost!
```

**This was the bug that caused connection status not updating!**

### Integration with Air-Side

**Network Ports:**
- TCP 5000: Command channel (handshake, commands, responses)
- UDP 5001: Status broadcasts from Air-Side (5 Hz)
- UDP 5002: Heartbeat bidirectional (1 Hz)

**Typical Flow:**
1. User clicks "Connect"
2. TCP connects to Air-Side (10.0.1.53:5000)
3. Send handshake message
4. Air-Side responds
5. UDP listeners auto-start (status 5Hz, heartbeat 1Hz)
6. Heartbeat sender auto-starts (1Hz)
7. Real-time updates flow to dashboards

**Message Flow:**
```
WindowsTools                    Air-Side
    │                              │
    ├──── TCP: Handshake ────────→│
    │←──── TCP: Response ──────────┤
    │                              │
    ├──── TCP: Command ───────────→│
    │←──── TCP: Response ──────────┤
    │                              │
    │←──── UDP 5001: Status ───────┤ (5 Hz continuous)
    │←──── UDP 5002: Heartbeat ────┤ (1 Hz)
    ├──── UDP 5002: Heartbeat ────→│ (1 Hz)
```

### WindowsTools Testing Checklist

**Before committing:**
- [ ] Application starts without errors
- [ ] All tabs load correctly
- [ ] Can connect to Air-Side (if available)
- [ ] No Python exceptions in console
- [ ] Log files created correctly in `logs/`
- [ ] Configuration persists in `config.json`
- [ ] Only modified files in `WindowsTools/` directory
- [ ] Commit message has `[WINDOWS][FEATURE]` or `[WINDOWS][FIX]` prefix

**Phase 2 Features to Test:**
- [ ] Protocol Inspector captures all messages
- [ ] Command Sender sends commands correctly
- [ ] Camera Dashboard updates from UDP status
- [ ] System Monitor updates from UDP status
- [ ] Heartbeat sender/receiver working (check Protocol Inspector)
- [ ] Connection status updates properly when connected/disconnected

### WindowsTools Troubleshooting

**Issue: "tkinter not available"**
```bash
# Windows: tkinter usually included with Python
# If missing:
pip install tk

# Or reinstall Python with tcl/tk option enabled
```

**Issue: "Protocol files not found"**
```bash
# Check you're running from correct directory
pwd  # Should be in DPM-V2/WindowsTools or DPM-V2

# Check protocol files exist
ls ../protocol/
# Should see: commands.json, camera_properties.json
```

**Issue: "Can't connect to Air-Side"**
```bash
# Check Air-Side is running
# Check IP address in config.json (default: 10.0.1.53)
# Check firewall not blocking ports 5000-5002
# Check you're on the same network as Air-Side

# Test with ping
ping 10.0.1.53
```

**Issue: "UDP messages not received"**
```bash
# Check UDP listeners started (should auto-start on TCP connect)
# Check Windows firewall allows Python to receive UDP
# Check Air-Side is sending UDP broadcasts
# Use Protocol Inspector tab to see if messages arriving
```

**Issue: "Callbacks not firing"**
```bash
# Check callback chaining (see Callback Chaining Pattern above)
# Ensure you're not replacing other components' callbacks
# Use logger.debug() to trace callback execution
```

**Issue: "GUI freezes"**
```bash
# Never block GUI thread with long operations
# Use threading.Thread(daemon=True) for background tasks
# Use .after() or callbacks to update GUI from background threads
```

### Phase Status (As of Oct 29, 2025)

**✅ Phase 1 - Foundation:** 100% Complete
- Basic TCP client
- Configuration management
- Connection Monitor tab
- Configuration tab

**✅ Phase 2 - Core Monitoring:** 100% Complete
- UDP status/heartbeat listeners
- Protocol Inspector tab
- Command Sender tab
- Camera Dashboard tab
- System Monitor tab
- Full protocol monitoring operational

**⏳ Phase 3 - Advanced:** 0% Not Started
- Docker logs viewer (SSH integration)
- Real-time graphs (matplotlib)
- Custom command templates
- Advanced filtering

**⏳ Phase 4 - Testing:** 0% Not Started
- Automated test sequences
- Stress testing
- Performance monitoring

**⏳ Phase 5 - Polish:** 0% Not Started
- Dark mode theme
- Keyboard shortcuts
- Error handling improvements
- Performance optimization

**Current Focus:** User testing Phase 2 with real Air-Side connection

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
cat protocol/protocol_v1.0.json | jq '.constants.protocol_version'

# 2. Check command is implemented on both sides
cat protocol/commands.json | jq '.commands."command.name".implemented'

# 3. Check for typos in command names
# 4. Verify JSON syntax is correct
# 5. Check network connectivity (ping the other side)
```

**Issue: "Property validation failing"**
```bash
# Check property definition:
cat protocol/camera_properties.json | jq '.properties."property_name".validation'

# Verify:
# 1. Value is in allowed values list
# 2. Value matches expected type
# 3. Dependencies are satisfied (e.g., WB mode for WB temperature)
# 4. Camera is in correct mode (some properties restricted by mode)
```

---

## 📝 SUMMARY - THE GOLDEN RULES

### Universal Rules (Both Platforms)

1. 🔴 **ALWAYS read CC_READ_THIS_FIRST.md at session start**
2. 🔴 **ALWAYS verify protocol files are at ~/DPM-V2/protocol/ NOT docs/protocol/**
3. 🔴 **ALWAYS pull latest from Git before starting work**
4. 🔴 **ALWAYS check protocol synchronization (protocol/commands.json + protocol/camera_properties.json)**
5. 🔴 **ALWAYS read appropriate PROGRESS_AND_TODO.md**
6. 🔴 **ALWAYS update PROGRESS_AND_TODO.md after significant changes**
7. 🔴 **ALWAYS commit regularly (every 30-60 min)**
8. 🔴 **ALWAYS use [TYPE] prefix in commit messages**
9. 🔴 **ALWAYS verify build succeeds before committing**
10. 🔴 **ALWAYS commit before ending session**
11. 🔴 **ALWAYS work incrementally (one thing at a time)**
12. 🔴 **NEVER hard-code camera property values - use ~/DPM-V2/protocol/camera_properties.json**

### Platform-Specific Rules

**Air-Side (C++):**
- 🟡 **ALWAYS check Sony SDK HTML documentation before implementing camera functions**
- 🟡 Run valgrind regularly for memory leak detection
- 🟡 Use smart pointers, avoid raw new/delete
- 🟡 Check Sony SDK return values
- 🟡 Test with Docker if applicable

**Ground-Side (Android):**
- 🟡 Follow MVVM architecture pattern
- 🟡 Use Coroutines for async operations
- 🟡 Check commented-out methods in NetworkClient.kt
- 🟡 Test on device/emulator before committing

**WindowsTools (Python):**
- 🟡 **ONLY modify files in WindowsTools/ directory**
- 🟡 **ALWAYS chain callbacks, never replace them**
- 🟡 Follow PEP 8 style guidelines
- 🟡 Never block GUI thread (use threading.Thread(daemon=True))
- 🟡 Test application starts before committing
- 🟡 Use [WINDOWS][FEATURE] or [WINDOWS][FIX] commit prefixes

---

## 🎓 FOR NEW CLAUDE CODE INSTANCES

### First Session on This Project:

1. ✅ Read this file (CC_READ_THIS_FIRST.md) - you're doing it!
2. ✅ Identify platform (air-side, ground-side, or WindowsTools)
3. ✅ Read appropriate PROGRESS_AND_TODO.md thoroughly
   - Air-Side: `sbc/docs/PROGRESS_AND_TODO.md`
   - Ground-Side: `android/docs/PROGRESS_AND_TODO.md`
   - WindowsTools: `WindowsTools/PROGRESS_AND_TODO.md`
4. ✅ Skim Project_Summary_and_Action_Plan.md (overview only)
5. ✅ Read protocol documentation (commands.json, camera_properties.json)
6. ✅ Check `git log --oneline -20` (understand recent history)
7. ✅ Identify current phase and next task
8. ✅ **[Air-Side Only]** Bookmark Sony SDK HTML documentation location
9. ✅ Start working!

### Subsequent Sessions:

1. ✅ Read this file (CC_READ_THIS_FIRST.md)
2. ✅ Pull latest from Git
3. ✅ Check protocol synchronization
4. ✅ Read appropriate PROGRESS_AND_TODO.md
5. ✅ Check `git status` and `git log --oneline -5`
6. ✅ Continue work

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
- [ ] All code changes are committed
- [ ] All commits have descriptive messages with [TYPE] prefix
- [ ] All commits pushed to origin/main
- [ ] Build succeeds (make/gradle)
- [ ] No compiler errors or unresolved warnings
- [ ] Memory leaks checked (air-side with valgrind)
- [ ] No orphaned documentation
- [ ] No [WIP] commits unless work is genuinely incomplete

**If all checked: You're good! 🎉**

---

**Document Status:** ✅ Active - Combined Air-Side & Ground-Side
**Version:** 2.2 - CRITICAL: Protocol Files Location Clarification
**Last Updated:** October 28, 2025
**Location:** Project root (DPM-V2/docs/CC_READ_THIS_FIRST.md)
**Maintained By:** Human oversight, enforced by Claude Code

**🔴 REMEMBER: Read this document at the start of EVERY session! 🔴**