# Claude Code - READ THIS FIRST
## DPM Payload Manager Project Rules & Workflow

**Date Created:** October 25, 2025
**Last Updated:** October 30, 2025
**Version:** 2.5 (Platform Identification & START Command)
**Status:** 🔴 **MANDATORY - READ EVERY SESSION**

---

## ⚡ QUICK START COMMAND

**Type `START` at the beginning of any session for automatic setup!**

When you type **START**, Claude Code will automatically:

1. ✅ Ask which platform you're working on (Air/Ground/WindowsTools/Docs)
2. ✅ Confirm current Git branch (should be `main`)
3. ✅ Run `git pull origin main` and check for conflicts
4. ✅ Verify protocol files are at correct location (`~/DPM-V2/protocol/`)
5. ✅ Check protocol synchronization (commands.json & camera_properties.json)
6. ✅ Read the appropriate PROGRESS_AND_TODO.md
7. ✅ Run `git status` and show uncommitted changes
8. ✅ Identify current phase and next recommended task
9. ✅ Ready to work!

**Example:**
```
User: START
Claude: 
  🎯 Which platform are you working on?
  1. 🔹 AIR-SIDE (C++ SBC in sbc/)
  2. 🔹 GROUND-SIDE (Android in android/)
  3. 🔹 WINDOWSTOOLS (Python Diagnostic in WindowsTools/)
  4. 🔹 DOCS (Protocol/Documentation)
  
User: 1
Claude: 
  ✅ Air-Side mode activated
  ✅ Confirming branch: main
  ✅ Running git pull...
  ✅ Checking protocol files location...
  ✅ Checking protocol sync...
  ✅ Reading sbc/docs/PROGRESS_AND_TODO.md...
  [proceeds with session initialization]
```

**Alternative:** You can also specify platform directly:
- `START AIR` - Start air-side session
- `START GROUND` - Start ground-side session
- `START WINDOWS` - Start WindowsTools session
- `START DOCS` - Start documentation session

---

## 🎯 PLATFORM IDENTIFICATION (MANDATORY!)

**🔴 CRITICAL: Claude Code MUST ask which platform at the start of EVERY session! 🔴**

### Platform Question (Always Ask First!)

**At the start of EVERY work session, Claude Code MUST ask:**

```
🎯 Which platform are you working on today?

1. 🔹 AIR-SIDE (C++ SBC)
   - Working in sbc/ directory
   - C++ development
   - Sony SDK integration
   - Raspberry Pi 4 target

2. 🔹 GROUND-SIDE (Android App)
   - Working in android/ directory
   - Kotlin development
   - H16 Ground Station target

3. 🔹 WINDOWSTOOLS (Python Diagnostic)
   - Working in WindowsTools/ directory
   - Python/tkinter development
   - Windows PC diagnostic tool

4. 🔹 DOCS/PROTOCOL
   - Working in docs/ or protocol/ directories
   - Protocol specification
   - Cross-platform documentation

Please respond with: AIR, GROUND, WINDOWS, or DOCS
```

**Wait for user response before proceeding!**

**Once platform is identified:**
- Set context for entire session
- Apply platform-specific rules
- Read platform-specific documentation
- Use platform-specific commit prefixes

### Platform-Specific Session Paths

**If AIR-SIDE selected:**
- ✅ Read Common Rules (below)
- ✅ Read [Air-Side Specifics](#-air-side-specifics-c-sbc)
- ✅ Check `sbc/docs/PROGRESS_AND_TODO.md`
- ✅ Verify Docker status (if applicable)
- ✅ Check Sony SDK availability
- ✅ Bookmark Sony SDK HTML documentation
- ✅ Set Git commit prefix to `[AIR]`

**If GROUND-SIDE selected:**
- ✅ Read Common Rules (below)
- ✅ Read [Ground-Side Specifics](#-ground-side-specifics-android-app)
- ✅ Check `android/docs/PROGRESS_AND_TODO.md`
- ✅ Check commented-out methods in NetworkClient.kt
- ✅ Verify ADB connectivity
- ✅ Set Git commit prefix to `[GROUND]`

**If WINDOWSTOOLS selected:**
- ✅ Read Common Rules (below)
- ✅ Read [WindowsTools Specifics](#-windowstools-specifics-python-diagnostic)
- ✅ Check `WindowsTools/PROGRESS_AND_TODO.md`
- ✅ Verify Python environment
- ✅ Test application launch
- ✅ Set Git commit prefix to `[WINDOWS]`

**If DOCS/PROTOCOL selected:**
- ✅ Read Common Rules (below)
- ✅ Focus on protocol synchronization
- ✅ Check both air and ground implementation status
- ✅ Set Git commit prefix to `[DOCS]`

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

### 1. Platform Identification (NEW!)
- ✅ **MANDATORY** - Claude Code asks which platform
- ✅ User responds: AIR, GROUND, WINDOWS, or DOCS
- ✅ Claude Code sets context for entire session
- ✅ All subsequent rules filtered by platform

### 2. Branch Confirmation (MANDATORY!)
- ✅ **MANDATORY** - Confirm current Git branch
- ✅ Run `git branch --show-current`
- ✅ Should return: `main`
- ⚠️ **If NOT on main branch**: STOP and ask user what to do
- ⚠️ **Never work on wrong branch!**

### 3. Read This Document
- ✅ **ALWAYS** read `CC_READ_THIS_FIRST.md` first (this file)
- This is your source of truth for workflow rules

### 4. Pull Latest Changes from Git
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

### 5. Check Protocol Synchronization
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

### 6. Check Current Status
- ✅ Read the appropriate `PROGRESS_AND_TODO.md`:
  - **Air-side:** `sbc/docs/PROGRESS_AND_TODO.md`
  - **Ground-side:** `android/docs/PROGRESS_AND_TODO.md`
  - **WindowsTools:** `WindowsTools/PROGRESS_AND_TODO.md`
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
- **Sony SDK HTML Documentation** - When working on camera integration (see Air-Side section)

**Ground-Side Docs:**
- `docs/Command_Protocol_Specification_v1.0.md` - When implementing protocol features
- `docs/Protocol_Implementation_Quick_Start.md` - Protocol implementation guide
- `docs/Phase1_Requirements_Update.md` - Feature requirements
- `docs/Updated_System_Architecture_H16.md` - System architecture
- Android-specific guides when implementing UI/networking

**WindowsTools Docs:**
- `WindowsTools/PROGRESS_AND_TODO.md` - Current status and tasks
- `WindowsTools/README.md` - Setup and usage instructions

### 8. Understand Git Status
- ✅ Run `git status` to check for uncommitted changes
- ✅ Identify what needs to be committed
- ✅ Check current branch (should be `main`)

---

## 🔄 COMMON WORKFLOW RULES
**These rules apply to ALL platforms:**

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

4. CC updates commands.json
   └─ Set "air_side": true

5. CC updates sbc/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [AIR][PROTOCOL] Implemented [command.name] command
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

4. CC updates commands.json
   └─ Set "ground_side": true

5. CC updates android/docs/PROGRESS_AND_TODO.md

6. CC commits with clear message
   └─ [GROUND][PROTOCOL] Implemented [command.name] UI
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
   - Check `ui_hints` in camera_properties.json:
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
**Last Updated:** October 29, 2025 15:30 - After implementing shutter_speed property
```

### Rule #2: Commit to Git Regularly (UPDATED WITH PLATFORM PREFIXES!)

**🔴 NEW REQUIREMENT: All commits MUST include platform prefix! 🔴**

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

**Commit Message Format (UPDATED!):**

```bash
[PLATFORM][TYPE] Component: Brief one-line summary (max 72 chars)

- Detailed point 1 (what changed)
- Detailed point 2 (why it changed)
- Detailed point 3 (impact/result)
```

**Valid PLATFORM prefixes:**
- `[AIR]` - Air-side (C++ SBC) changes
- `[GROUND]` - Ground-side (Android) changes
- `[WINDOWS]` - WindowsTools (Python diagnostic) changes
- `[DOCS]` - Documentation/Protocol (cross-platform)

**Valid TYPE prefixes:**
- `[FEATURE]` - New functionality
- `[FIX]` - Bug fix
- `[PROTOCOL]` - Protocol implementation
- `[DOCS]` - Documentation update
- `[REFACTOR]` - Code restructuring
- `[TEST]` - Testing additions
- `[BUILD]` - Build system changes
- `[WIP]` - Work in progress

**Platform Prefix Rules:**
- ✅ **AIR-SIDE work**: MUST use `[AIR]` prefix
- ✅ **GROUND-SIDE work**: MUST use `[GROUND]` prefix
- ✅ **WINDOWSTOOLS work**: MUST use `[WINDOWS]` prefix
- ✅ **DOCS/PROTOCOL**: Use `[DOCS]` prefix (no platform-specific code)
- ✅ **Cross-platform changes**: Use multiple commits, one per platform

**Good Examples:**
```bash
[AIR][PROTOCOL] Camera: Implemented shutter_speed property

- Air-side: Sony SDK CrDeviceProperty_ShutterSpeed integration
- Added validation for shutter speed values
- Updated handleCameraSetProperty() handler
- Testing: Verified with Sony A1 camera

[GROUND][PROTOCOL] Camera: Implemented shutter_speed UI

- Added Spinner with standard shutter speeds
- Connected to networkClient.setCameraProperty()
- Validation: Enum values from camera_properties.json
- Testing: Verified end-to-end with air-side

[AIR][FIX] Docker: Resolved CrAdapter dynamic loading issue

- Root cause: Adapters statically linked in CMakeLists.txt
- Solution: Only link libCr_Core.so, copy CrAdapter/ to build dir
- Result: SDK now loads adapters dynamically

[GROUND][FEATURE] Android: Added camera control screen

- Implemented CameraControlFragment with MVVM pattern
- Added exposure controls (shutter, aperture, ISO)
- Connected to NetworkClient for command sending
- Tested on emulator and H16 hardware

[WINDOWS][FEATURE] Protocol Inspector: Added JSON formatting

- Implemented syntax highlighting for JSON messages
- Added expand/collapse for nested structures
- Improved readability of protocol messages

[DOCS] Protocol: Added focus control commands

- Updated commands.json with camera.focus command
- Added camera.set_focus_area command
- Both marked air_side=false, ground_side=false
- Ready for implementation in next session

[AIR][WIP] Camera: Partial Sony SDK integration

- Connected to camera successfully
- Can read properties but not set yet
- Need to debug SetDeviceProperty callback issue
- Committing for end of session
```

**Bad Examples:**
```bash
# Missing platform prefix
[FEATURE] Added stuff

# No context
Fixed bug

# Too long in title
[AIR][FEATURE] Implemented camera shutter speed property control with dropdown UI and validation

# No details
[GROUND][FIX] Camera works now

# Wrong platform prefix (air work with ground prefix)
[GROUND][PROTOCOL] Implemented C++ camera handler
```

**Cross-Platform Changes:**
If you modify multiple platforms in one session, make **separate commits**:

```bash
# Commit 1: Air-side changes
git add sbc/
git commit -m "[AIR][PROTOCOL] Camera: Implemented shutter_speed handler"

# Commit 2: Ground-side changes
git add android/
git commit -m "[GROUND][PROTOCOL] Camera: Added shutter_speed UI"

# Commit 3: WindowsTools changes
git add WindowsTools/
git commit -m "[WINDOWS][FEATURE] Added shutter_speed display"

# Commit 4: Protocol updates
git add protocol/
git commit -m "[DOCS] Protocol: Marked shutter_speed implemented all sides"
```

### 🔴 NEW REQUIREMENT: Cross-Platform Implementation Instructions

**CRITICAL: When Claude Code works on one platform and the changes will impact another platform, the commit message MUST include detailed implementation instructions for that platform!**

**Why This Matters:**
- The other platform's Claude Code instance needs to understand what was done
- Detailed commit messages enable the other platform to integrate smoothly
- Prevents miscommunication and implementation errors
- Provides context that code alone cannot convey

**When This Applies:**
- ✅ Implementing a feature on Air-Side that Ground-Side will need to use
- ✅ Implementing a feature on Ground-Side that Air-Side will need to support
- ✅ Fixing a bug on one side that affects the other side
- ✅ Making protocol changes that both sides need to understand
- ✅ Implementing diagnostic features that reveal issues on other platforms

**Commit Message Format for Cross-Platform Work:**

```bash
[PLATFORM][TYPE] Component: Brief summary

Root Cause / Context:
- What problem this solves
- Why this approach was chosen
- What was wrong before

Technical Details:
- Specific implementation details
- SDK functions used (if Air-Side)
- UI components added (if Ground-Side)
- Protocol messages involved
- Timing/sequencing requirements
- Error handling approach

Fixes / Implements:
- List specific issues resolved
- List specific features enabled
- Note any side effects or limitations

Testing:
- How it was tested
- Test results
- What scenarios were verified

Files Changed:
- path/to/file.cpp (method_name, lines X-Y)
- path/to/other_file.h (added new_function)

Documentation:
- Links to any docs created
- Summary docs if extensive
- API documentation updates

For [OTHER_PLATFORM] Integration:
- Specific instructions for the other platform
- Expected behavior from this side
- Protocol expectations
- Error codes to handle
- Timing considerations
```

**Excellent Example (Air-Side Fix with Ground-Side Instructions):**

```bash
[AIR][FIX] Camera: Fix focus control SDK error 0x8402

Root Cause:
- FocalDistanceInMeter property not properly validated as "enabled"
- SDK requires property state checks before Focus_Operation calls
- Missing timing delays caused interference between operations

Technical Details:
- Added Focus_Speed_Range query to validate and clamp speed values (1-3)
- Added property state checks before Focus_Operation attempts
- Added timing delays: 50ms post-query, 100ms post-command
- Enhanced error logging with specific failure diagnostics
- Created diagnostic version for troubleshooting camera-specific issues

Sony SDK Functions Used:
- CrDeviceProperty_FocalDistanceInMeter (validation)
- CrDeviceProperty_Focus_Speed_Range (speed clamping)
- CrDeviceProperty_Focus_Operation (near/far/stop)
- CrDeviceProperty_AutoFocusHold (press/release)

Fixes:
- SDK error 0x8402 (CrError_Api_InvalidCalled) on all focus commands
- Focus operations (near/far/stop) now work reliably
- Property readback slowdown after focus commands resolved
- Auto-focus hold (press/release) now functional

Testing:
- Verified focus commands execute without errors
- Focal distance updates correctly during operation
- Property queries remain responsive after focus commands
- Tested all 6 speed levels (near 1-3, far 1-3)
- Tested auto-focus hold press and release

Files Changed:
- sbc/src/camera/camera_sony.cpp (focus() method, lines 356-430)
- sbc/src/camera/camera_sony.h (added focus speed validation)
- sbc/include/protocol/messages.h (added focus error codes)

Documentation:
- Added docs/FOCUS_FIX_INSTRUCTIONS.md (implementation guide)
- Added docs/FOCUS_FIX_SUMMARY.md (executive summary)
- Created diagnostic version in camera_sony_diagnostic.cpp
- Created production fix in camera_sony_fixed.cpp

For GROUND-SIDE Integration:
- Focus commands now work as documented in protocol
- Expected response time: <100ms for command acknowledgment
- Focal distance updates arrive via UDP status broadcasts
- Error codes to handle:
  * 0x8402: Camera not ready (retry after 100ms)
  * Focus speed auto-clamped to 1-3 range (no error if out of range)
- Timing: Wait 100ms between consecutive focus commands
- UI Recommendation: Disable focus buttons during active operation
- Testing: Use diagnostic mode logs if issues occur
```

**Good Example (Ground-Side UI with Air-Side Context):**

```bash
[GROUND][FEATURE] Camera: Add manual focus controls UI

Context:
- Implements Phase 1 manual focus per Focus_Control_Implementation_Guide.md
- Air-Side focus commands implemented and tested in commit c83a58a
- Provides 6-speed directional control (near/far, speeds 1-3)

UI Implementation:
- Added FocusSection component with 6 direction/speed buttons
- Added AutoFocusHoldButton with press-and-hold behavior
- Added focus mode display (MF/AF-S/AF-C) from camera status
- Visual feedback: AF button changes gray→green when pressed
- Icons: 👤 for near (person), 🏔️ for far (mountain)

NetworkClient Methods:
- focusCamera(action: String, speed: Int) sends camera.focus command
- setAutoFocusHold(state: String) sends camera.auto_focus_hold command
- Parameters validated before sending

Protocol Messages:
- camera.focus: {action: "near"/"far"/"stop", speed: 1-3}
- camera.auto_focus_hold: {state: "press"/"release"}

Files Changed:
- app/src/main/java/com/dpm/groundstation/ui/SonyRemoteControlScreen.kt
  * Added FocusSection component (lines 958-1037)
  * Added AutoFocusHoldButton composable (lines 1063-1116)
- app/src/main/java/com/dpm/groundstation/network/NetworkClient.kt
  * Added focusCamera() method (line 245)
  * Added setAutoFocusHold() method (line 267)

Testing:
- ✅ Buttons trigger correct protocol messages
- ✅ AF Hold button responds to press/release correctly
- ✅ Focus mode display updates from UDP status
- ⏳ End-to-end testing with Air-Side pending

For AIR-SIDE Context:
- Ground-Side sends focus commands as documented
- Expects camera.focus response within 100ms
- Expects focal_distance updates via UDP status broadcasts
- Will display focus mode from status.camera.focus_mode field
- May send rapid commands if user holds button - Air-Side should debounce
```

**Bad Example (Missing Context):**

```bash
[AIR][FIX] Camera: Fixed focus

- Fixed the focus bug
- It works now
```

**Why This is Bad:**
- No explanation of what was wrong
- No technical details for debugging
- No testing information
- Ground-Side has no idea what changed or how to use it
- Future Claude Code instances can't understand the fix

**Enforcement:**

✅ **DO:**
- Include root cause analysis for fixes
- List all technical changes in detail
- Specify exact SDK functions/API calls used
- Document timing and sequencing requirements
- Provide test results and verification steps
- Include explicit instructions for other platform
- List all files changed with line numbers
- Reference created documentation

❌ **DON'T:**
- Write vague commit messages like "fixed bug"
- Assume other platform will figure it out
- Skip technical details "to save time"
- Forget to mention protocol changes
- Leave out testing information
- Omit error handling details
- Forget timing requirements

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

**WindowsTools (Python):**
```bash
cd WindowsTools
python DiagnosticTool.py  # Should launch without errors

# If errors occur, FIX IT before committing
# Test all tabs load correctly
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

3. **Locate Sony SDK HTML Documentation:**
   ```bash
   # Sony SDK API documentation location:
   ~/sony_sdk/doc/html/index.html
   
   # CRITICAL: Always reference Sony SDK documentation when:
   # - Implementing new camera properties
   # - Working with Sony SDK API calls
   # - Debugging Sony SDK errors
   # - Understanding property enums and values
   ```

4. **Check Build Directory:**
   ```bash
   ls sbc/build/
   # Should exist and contain CMake files
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

**🔴 CRITICAL: Always check Sony SDK HTML documentation before implementing!**

**Documentation Location:**
```bash
~/sony_sdk/doc/html/index.html
```

**Key Documentation Sections:**
- API Reference → Device Properties → Camera Properties
- Class Reference → SCRSDK namespace
- Examples → Remote Sample Application

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

**When Implementing New Camera Properties:**
1. Open Sony SDK HTML docs
2. Find the property in CrDeviceProperty enum
3. Check available values in corresponding Value enum
4. Note any dependencies or restrictions
5. Implement using documented approach
6. Test with actual camera

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

**Issue: "Don't know which Sony SDK property to use"**
```bash
# SOLUTION: Open Sony SDK HTML documentation
open ~/sony_sdk/doc/html/index.html

# Navigate to:
# 1. API Reference → Device Properties
# 2. Find the property you need
# 3. Check available values and enums
# 4. Review example code if available
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

### WindowsTools Overview

**Purpose:** Python/tkinter diagnostic tool for monitoring and testing DPM protocol on Windows PC

**Current Status:** Phase 2 Complete (Core Monitoring)
- Connection Monitor
- Protocol Inspector
- Command Sender
- Camera Dashboard
- System Monitor

**Key Features:**
- Real-time TCP/UDP protocol monitoring
- Send test commands to Air-Side
- View camera status and system health
- JSON formatting and syntax highlighting
- Callback-based architecture

### WindowsTools Session Start Extensions

**Additional checks for Python development:**

1. **Check Python Version:**
   ```bash
   python --version
   # Should be Python 3.9 or newer
   ```

2. **Check Dependencies:**
   ```bash
   cd WindowsTools
   pip list | grep -E "tkinter|netifaces"
   ```

3. **Test Application Launch:**
   ```bash
   python DiagnosticTool.py
   # Should open GUI without errors
   ```

### WindowsTools Architecture

**File Structure:**
```
WindowsTools/
├── DiagnosticTool.py          # Main entry point
├── config.json                # User settings (IP, ports)
├── README.md                  # Setup instructions
├── PROGRESS_AND_TODO.md       # Development status
├── components/
│   ├── connection_manager.py  # TCP/UDP networking
│   ├── tab_connection.py      # Connection Monitor tab
│   ├── tab_protocol.py        # Protocol Inspector tab
│   ├── tab_command.py         # Command Sender tab
│   ├── tab_camera.py          # Camera Dashboard tab
│   └── tab_system.py          # System Monitor tab
└── utils/
    └── logger.py              # Logging utilities
```

### Critical WindowsTools Rules

**🔴 RULE #1: ONLY modify files in WindowsTools/ directory**
- Never modify Air-Side C++ code
- Never modify Ground-Side Android code
- Never modify protocol/ files (read-only for WindowsTools)
- Only work within WindowsTools/ boundary

**🔴 RULE #2: Callback Chaining Pattern (MANDATORY!)**

WindowsTools uses a callback-based architecture. **NEVER replace existing callbacks!**

**❌ WRONG - Replaces callback:**
```python
# This BREAKS other components!
connection_manager.set_status_callback(my_new_callback)
```

**✅ CORRECT - Chains callback:**
```python
# Get existing callback
existing_callback = connection_manager.status_callback

# Create new callback that calls both
def chained_callback(data):
    # Call existing first (maintains others' functionality)
    if existing_callback:
        existing_callback(data)
    
    # Then do your work
    my_processing(data)

# Set the chained callback
connection_manager.set_status_callback(chained_callback)
```

**Why This Matters:**
- Multiple tabs may listen to the same callback
- Replacing a callback breaks other components
- Always chain callbacks to preserve functionality

**Callback Types in WindowsTools:**
- `status_callback` - UDP status messages (5 Hz)
- `heartbeat_callback` - UDP heartbeat messages (1 Hz)
- `response_callback` - TCP command responses
- `connection_callback` - TCP connection state changes

### WindowsTools Best Practices

**Python Style:**
- ✅ Follow PEP 8 style guidelines
- ✅ Use type hints where appropriate
- ✅ Document functions with docstrings
- ✅ Keep functions focused and small

**GUI Threading:**
- ✅ Never block the GUI thread
- ✅ Use `threading.Thread(daemon=True)` for background tasks
- ✅ Use `.after()` or callbacks to update GUI from threads
- ✅ Test that GUI remains responsive

**Error Handling:**
- ✅ Catch and log network errors
- ✅ Display user-friendly error messages
- ✅ Don't crash on malformed protocol messages
- ✅ Validate JSON before parsing

**Configuration:**
- ✅ Store user settings in `config.json`
- ✅ Provide sensible defaults
- ✅ Validate IP addresses and ports
- ✅ Save configuration on exit

### WindowsTools Development Workflow

**When adding a new feature:**

1. **Plan the feature**
   - Which tab does it belong in?
   - What protocol messages does it need?
   - What callbacks are required?

2. **Update appropriate component file**
   - `tab_connection.py` - Connection status features
   - `tab_protocol.py` - Protocol inspection features
   - `tab_command.py` - Command sending features
   - `tab_camera.py` - Camera status features
   - `tab_system.py` - System health features

3. **Chain callbacks properly**
   - Get existing callback first
   - Create chained callback
   - Set chained callback

4. **Test thoroughly**
   - Test with Air-Side running
   - Test with Air-Side not running
   - Test rapid message flow
   - Test GUI responsiveness

5. **Update documentation**
   - Update `WindowsTools/PROGRESS_AND_TODO.md`
   - Update `WindowsTools/README.md` if user-facing
   - Document any new dependencies

### WindowsTools Troubleshooting

**Issue: "Application won't start"**
```bash
# Check Python version
python --version  # Must be 3.9+

# Check tkinter installed
python -c "import tkinter"  # Should not error

# Check for syntax errors
python -m py_compile DiagnosticTool.py
```

**Issue: "Can't connect to Air-Side"**
```bash
# Check IP configuration in config.json
cat config.json  # Verify air_side_ip is correct

# Check network connectivity
ping 192.168.144.20  # Or your Air-Side IP

# Check Air-Side is running
# Use Protocol Inspector tab to see if messages arriving
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

### Universal Rules (All Platforms)

1. 🔴 **ALWAYS ask which platform at session start (NEW!)**
2. 🔴 **ALWAYS use platform prefix in Git commits (NEW!)**
3. 🔴 **ALWAYS include detailed cross-platform instructions in commits (NEW!)**
4. 🔴 **ALWAYS confirm current Git branch (should be `main`)**
5. 🔴 **ALWAYS read CC_READ_THIS_FIRST.md at session start**
6. 🔴 **ALWAYS verify protocol files are at ~/DPM-V2/protocol/ NOT docs/protocol/**
7. 🔴 **ALWAYS pull latest from Git before starting work**
8. 🔴 **ALWAYS check protocol synchronization (protocol/commands.json + protocol/camera_properties.json)**
9. 🔴 **ALWAYS read appropriate PROGRESS_AND_TODO.md**
10. 🔴 **ALWAYS update PROGRESS_AND_TODO.md after significant changes**
11. 🔴 **ALWAYS commit regularly (every 30-60 min)**
12. 🔴 **ALWAYS verify build succeeds before committing**
13. 🔴 **ALWAYS commit before ending session**
14. 🔴 **ALWAYS work incrementally (one thing at a time)**
15. 🔴 **NEVER hard-code camera property values - use ~/DPM-V2/protocol/camera_properties.json**

### Platform-Specific Rules

**Air-Side (C++):**
- 🟡 **ALWAYS check Sony SDK HTML documentation before implementing camera functions**
- 🟡 Run valgrind regularly for memory leak detection
- 🟡 Use smart pointers, avoid raw new/delete
- 🟡 Check Sony SDK return values
- 🟡 Test with Docker if applicable
- 🟡 Use `[AIR]` prefix in all Git commits

**Ground-Side (Android):**
- 🟡 Follow MVVM architecture pattern
- 🟡 Use Coroutines for async operations
- 🟡 Check commented-out methods in NetworkClient.kt
- 🟡 Test on device/emulator before committing
- 🟡 Use `[GROUND]` prefix in all Git commits

**WindowsTools (Python):**
- 🟡 **ONLY modify files in WindowsTools/ directory**
- 🟡 **ALWAYS chain callbacks, never replace them**
- 🟡 Follow PEP 8 style guidelines
- 🟡 Never block GUI thread (use threading.Thread(daemon=True))
- 🟡 Test application starts before committing
- 🟡 Use `[WINDOWS]` prefix in all Git commits

---

## 🎓 FOR NEW CLAUDE CODE INSTANCES

### First Session on This Project:

1. ✅ Read this file (CC_READ_THIS_FIRST.md) - you're doing it!
2. ✅ **ASK USER: Which platform are you working on? (AIR/GROUND/WINDOWS/DOCS)**
3. ✅ Confirm current Git branch (should be `main`)
4. ✅ Identify platform and set context
5. ✅ Read appropriate PROGRESS_AND_TODO.md thoroughly
   - Air-Side: `sbc/docs/PROGRESS_AND_TODO.md`
   - Ground-Side: `android/docs/PROGRESS_AND_TODO.md`
   - WindowsTools: `WindowsTools/PROGRESS_AND_TODO.md`
6. ✅ Skim Project_Summary_and_Action_Plan.md (overview only)
7. ✅ Read protocol documentation (commands.json, camera_properties.json)
8. ✅ Check `git log --oneline -20` (understand recent history)
9. ✅ Identify current phase and next task
10. ✅ **[Air-Side Only]** Bookmark Sony SDK HTML documentation location
11. ✅ Start working!

### Subsequent Sessions:

1. ✅ Read this file (CC_READ_THIS_FIRST.md)
2. ✅ **ASK USER: Which platform are you working on? (AIR/GROUND/WINDOWS/DOCS)**
3. ✅ Confirm current Git branch (should be `main`)
4. ✅ Pull latest from Git
5. ✅ Check protocol synchronization
6. ✅ Read appropriate PROGRESS_AND_TODO.md
7. ✅ Check `git status` and `git log --oneline -5`
8. ✅ Continue work

---

## ✅ SESSION END CHECKLIST

**Before ending EVERY work session, verify:**

- [ ] Platform was identified at session start
- [ ] All Git commits use correct `[PLATFORM]` prefix
- [ ] Cross-platform commits include detailed instructions for other platform
- [ ] Current branch is `main`
- [ ] PROGRESS_AND_TODO.md updated with today's work
- [ ] All task checkboxes reflect reality
- [ ] Completion percentages updated
- [ ] Visual progress bars updated (if applicable)
- [ ] "Last Updated" timestamp is current
- [ ] Issue Tracker reflects current bugs/blockers
- [ ] Protocol JSON files updated if implemented commands/properties
- [ ] All code changes are committed with `[PLATFORM][TYPE]` format
- [ ] All commits have descriptive messages with implementation details
- [ ] All commits pushed to origin/main
- [ ] Build succeeds (make/gradle/python)
- [ ] No compiler errors or unresolved warnings
- [ ] Memory leaks checked (air-side with valgrind)
- [ ] No orphaned documentation
- [ ] No [WIP] commits unless work is genuinely incomplete

**If all checked: You're good! 🎉**

---

**Document Status:** ✅ Active - v2.6 with Cross-Platform Commit Message Requirements
**Version:** 2.6 - Cross-platform implementation instructions + all v2.5 features
**Last Updated:** October 31, 2025
**Location:** Project root (DPM-V2/docs/CC_READ_THIS_FIRST.md)
**Maintained By:** Human oversight, enforced by Claude Code

**🔴 REMEMBER: Read this document at the start of EVERY session! 🔴**
**🔴 NEW: Always identify your platform (AIR/GROUND/WINDOWS/DOCS) first! 🔴**
**🔴 NEW: Always use [PLATFORM][TYPE] in Git commits! 🔴**
**🔴 NEW: Always confirm Git branch is `main` before starting! 🔴**
**🔴 NEW: Cross-platform commits MUST include detailed instructions for other platform! 🔴**