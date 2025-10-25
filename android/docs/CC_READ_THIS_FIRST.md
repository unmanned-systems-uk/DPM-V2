# Claude Code - READ THIS FIRST
## DPM Ground Station Android App Rules & Workflow

**Date Created:** October 24, 2025  
**Version:** 1.0  
**Status:** 🔴 **MANDATORY - READ EVERY SESSION**

---

## 🎯 PURPOSE OF THIS DOCUMENT

This document establishes the **mandatory workflow** for Claude Code (CC) when working on the DPM Ground Station Android application. These rules ensure:

1. **Documentation stays current** - No orphaned docs
2. **Git commits happen regularly** - Traceable history
3. **Progress is tracked** - Always know where we are
4. **Efficiency** - No redundant reading of large planning docs

---

## 📋 SESSION START CHECKLIST

**Every time you (Claude Code) start working, follow these steps:**

### 1. Read This Document
- ✅ **ALWAYS** read `CC_READ_THIS_FIRST.md` first (this file)
- This is your source of truth for workflow rules

### 2. Check Protocol Synchronization
- ✅ **MANDATORY** - Check `docs/protocol/commands.json` for new commands
- ✅ Look for commented-out methods in `NetworkClient.kt`
- ✅ Check if air-side has implemented commands you can now enable
- ✅ **ASK USER** about any new commented commands before implementing
- ⚠️ **CRITICAL** - Protocol sync MUST happen every session

### 3. Check Current Status
- ✅ Read `PROGRESS_AND_TODO.md` to understand:
  - What phase we're in
  - What's been completed
  - What's currently blocked
  - What to work on next

### 3. Read Relevant Technical Docs (If Needed)
- ⚠️ **DO NOT** read `Project_Summary_and_Action_Plan.md` unless explicitly asked
- ⚠️ **DO NOT** re-read technical specs you've already reviewed in this session
- ✅ **DO** read specific technical docs when starting new features:
  - `Command_Protocol_Specification_v1.0.md` - When implementing protocol features
  - `Protocol_Implementation_Quick_Start.md` - Protocol implementation guide
  - `Phase1_Requirements_Update.md` - Feature requirements
  - `Updated_System_Architecture_H16.md` - System architecture
  - Android-specific guides when implementing UI/networking

### 4. Understand Git Status
- ✅ Check what files have been modified since last commit
- ✅ Identify what needs to be committed

---

## 🔄 MANDATORY WORKFLOW RULES

### Rule #0: Protocol Synchronization (MOST IMPORTANT!)

**🔴 CRITICAL: Check protocol files EVERY SESSION before doing ANY work! 🔴**

#### Session Start Protocol Check

**ALWAYS do this at the start of EVERY session:**

```bash
# 1. Check for new commands in protocol definition
cat ../docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.ground_side == false) | .key'

# This will list commands NOT YET implemented on ground-side
```

```bash
# 2. Check for commands air-side has but you don't
cat ../docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.air_side == true and
         .value.implemented.ground_side == false) | .key'

# These commands are READY to use - air-side can handle them!
```

**If you see ANY commands listed:**
1. **STOP** and read the command definition in `commands.json`
2. **ASK THE USER:**
   - "I see new command(s) in the protocol: [list them]"
   - "What UI should these commands have?"
   - "Should I implement them now, or are they planned for later?"
3. **WAIT** for user response before proceeding
4. **DO NOT** assume you know what to implement

#### Commented-Out Commands Workflow

**The user will add commands to NetworkClient.kt as COMMENTED-OUT methods:**

```kotlin
class NetworkClient {
    // Implemented commands
    fun captureImage() { ... }

    // Planned commands (commented out until ready)
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

**Your job:**
1. **At session start**, search for commented `// fun` in `NetworkClient.kt`
2. **Ask user**: "I see X commented-out commands. Should I implement any of them?"
3. **Check** if air-side has implemented the corresponding handler
4. **If air-side ready + user approves**:
   - Uncomment the method
   - Add UI elements to call it
   - Test end-to-end
   - Update `commands.json` to `"ground_side": true`
5. **If air-side NOT ready**: Ask user if you should wait or implement anyway (for testing)

#### Adding New Commands (Ground-Side)

**When implementing a new command:**

```
1. User adds command definition to docs/protocol/commands.json
   └─ Sets "ground_side": false, "air_side": false (or true if ready)

2. User adds COMMENTED-OUT method to NetworkClient.kt
   └─ This serves as a TODO and prevents forgetting

3. CC detects commented method at session start
   └─ Asks user what it does and if UI is needed

4. CC implements:
   ├─ Uncomment method in NetworkClient.kt
   ├─ Add ViewModel method to call it
   ├─ Add UI button/control
   ├─ Add error handling
   └─ Test with air-side (if available)

5. CC updates commands.json
   └─ Set "ground_side": true

6. CC updates docs/IMPLEMENTATION_STATUS.md
   └─ Mark command as complete in coverage table

7. CC commits with clear message
   └─ [PROTOCOL] Implemented [command.name] command
```

#### Protocol Sync Rules

✅ **DO:**
- Check protocol files at START of every session
- Check for commented-out methods in `NetworkClient.kt` every session
- Ask user about new commands before implementing
- Verify air-side has implemented handler before enabling command
- Update `commands.json` immediately after implementing
- Keep `commands.json` as single source of truth
- Add UI for every command (even if simple test button)

❌ **DON'T:**
- Uncomment methods without checking if air-side is ready
- Implement commands not in `commands.json`
- Assume what UI a command needs without asking
- Mark `"ground_side": true` until fully implemented and tested
- Add commands without updating protocol documentation
- Skip protocol check at session start
- Send commands the air-side can't handle (check `commands.json`!)

#### Example Session Start

```
CC: Starting session, checking protocol sync...

[runs: cat docs/protocol/commands.json | jq ...]

CC: Protocol check results:

Commands air-side has but I don't:
1. camera.capture - ✅ Ready to use
2. system.get_status - ✅ Ready to use

Commented-out methods in NetworkClient.kt:
1. setCameraProperty() - line 245
2. focusCamera() - line 257
3. getCameraProperties() - line 269

Checking air-side status:
- camera.set_property: air_side = false (NOT READY)
- camera.focus: air_side = false (NOT READY)
- camera.get_properties: air_side = false (NOT READY)

Questions:
1. Should I uncomment and implement camera.capture (air-side ready)?
2. The other commands aren't ready on air-side yet. Should I:
   a) Wait for air-side to implement them first?
   b) Implement UI anyway for testing purposes?
3. What UI should the capture button look like?

[WAITS for user response before proceeding]
```

#### Handling Multiple New Commands

**If user adds many commented-out methods at once:**

```kotlin
// User adds 10 new methods all commented out

// CC's approach:
// 1. List all commented methods
// 2. Ask which to prioritize
// 3. Implement ONE at a time
// 4. Test each before moving to next
// 5. Uncomment ONLY after tested
```

**DO NOT uncomment all at once - implement incrementally!**

### Rule #1: Update PROGRESS_AND_TODO.md After Every Significant Change

**When to update:**
- ✅ After completing any task in a phase
- ✅ After discovering/resolving a bug
- ✅ After creating new files/classes
- ✅ After significant debugging sessions
- ✅ When switching from one phase/component to another
- ✅ After successful testing on device
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
**Last Updated:** October 24, 2025 15:30 - After implementing TCP client connection
```

### Rule #2: Commit to Git Regularly

**Commit frequency rules:**

1. **After completing any functional unit:**
   - ✅ New activity/fragment implemented
   - ✅ New ViewModel created
   - ✅ Network component working
   - ✅ UI feature completed
   - ✅ Bug fixed and verified

2. **Before switching tasks:**
   - ✅ Always commit current work before starting something new
   - Even if incomplete - use WIP (Work In Progress) tag

3. **At end of session:**
   - ✅ **MANDATORY** - Commit all changes before ending work
   - Update docs first, then commit

4. **After successful device testing:**
   - ✅ Document test results in PROGRESS_AND_TODO.md
   - ✅ Commit the working feature

**Commit Message Format:**

```bash
# Feature implementation
git commit -m "[FEATURE] Component: Brief description

- Detailed point 1
- Detailed point 2
- Resolves: issue reference if applicable"

# UI implementation
git commit -m "[UI] Screen/Component: Brief description

- What UI elements added
- What functionality implemented
- How it connects to ViewModel"

# Bug fix
git commit -m "[FIX] Component: Brief description of bug

- Root cause
- Solution applied
- Testing performed"

# Documentation update
git commit -m "[DOCS] Updated file

- What changed
- Why it changed"

# Work in progress
git commit -m "[WIP] Component: What you're working on

- Current state
- Next steps"
```

**Example Commits:**
```bash
# Good examples
git commit -m "[FEATURE] Network: Implemented TCP client

- Created TcpClient.kt with connection management
- Integrated Kotlin Coroutines for async operations
- Successfully connects to 192.168.144.20:5000
- Handles reconnection on connection loss"

git commit -m "[UI] Camera Control: Added exposure controls

- Shutter speed, aperture, ISO selectors implemented
- LiveData binding to ViewModel working
- UI updates reflect camera status from air-side
- Tested on Android emulator API 30"

git commit -m "[FIX] UDP: Resolved heartbeat timeout issue

- Root cause: UDP socket not bound to correct port
- Solution: Bind to port 5002 instead of ephemeral port
- Result: Heartbeat now detected reliably"

git commit -m "[DOCS] Updated PROGRESS_AND_TODO.md with network layer progress

- Added Network Layer implementation section
- Marked TCP client complete
- Updated completion status to 25%"
```

### Rule #3: Never Leave Orphaned Documentation

**Before making code changes:**
- ✅ Check if any documentation references affected code
- ✅ Plan documentation updates alongside code changes

**After making code changes:**
- ✅ Update relevant technical documentation
- ✅ Update PROGRESS_AND_TODO.md
- ✅ Update architecture docs if structure changed
- ✅ Update README.md if build/run process changed

**Red flags - don't let these happen:**
- ❌ Code exists but not mentioned in PROGRESS_AND_TODO.md
- ❌ Classes created but not tracked in documentation
- ❌ Features working but marked as "Not Started" in docs
- ❌ Issues resolved but still marked "Active" in Issue Tracker
- ❌ Completion percentages not updated after significant work
- ❌ APK deployed but no deployment notes

### Rule #4: Git Workflow

**Standard workflow:**

```bash
# 1. Start of session - check status
git status
git log --oneline -5  # Review recent commits

# 2. Before starting work - pull latest
git pull origin main

# 3. Make changes, test, verify (build APK if needed)

# 4. Update documentation (PROGRESS_AND_TODO.md)

# 5. Stage changes
git add -A  # Or specific files

# 6. Review what you're committing
git diff --cached

# 7. Commit with descriptive message
git commit -m "[TYPE] Component: Description

- Details
- Details"

# 8. Push to remote
git push origin main

# 9. Verify push succeeded
git log --oneline -1
```

**If you get stuck/errors:**
```bash
# Check current branch
git branch

# Check remote status
git remote -v

# Pull latest if behind
git pull origin main
```

### Rule #5: Android-Specific Workflow

**Build and Test Cycle:**

```bash
# 1. Gradle sync after code changes
./gradlew sync

# 2. Build debug APK for testing
./gradlew assembleDebug

# 3. Install on device/emulator (if available)
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 4. Check logcat for errors
adb logcat | grep DPM

# 5. If build fails, check:
# - Gradle build errors
# - Kotlin compilation errors
# - Dependency conflicts
# - ProGuard/R8 issues (release builds)
```

**Before committing Android code:**
- ✅ Code compiles without errors
- ✅ No compiler warnings (fix or suppress with justification)
- ✅ Kotlin lint checks pass
- ✅ APK builds successfully (at least debug variant)
- ✅ Tested on emulator or device (when possible)

---

## 🚫 ANTI-PATTERNS TO AVOID

### DON'T Do These Things:

1. ❌ **Don't make multiple unrelated changes in one commit**
   - Keep commits focused and atomic
   - If you added a ViewModel AND fixed a UI bug, make 2 commits

2. ❌ **Don't commit without updating documentation first**
   - Always update PROGRESS_AND_TODO.md before committing code
   - Documentation is part of the deliverable

3. ❌ **Don't work for hours without committing**
   - Commit every 30-60 minutes of productive work
   - Small, frequent commits > large, rare commits

4. ❌ **Don't leave work in progress without documenting state**
   - Always note in PROGRESS_AND_TODO.md where you left off
   - Use [WIP] commits if needed

5. ❌ **Don't re-read huge planning documents every session**
   - `Project_Summary_and_Action_Plan.md` is 800+ lines - read once, reference as needed
   - Use PROGRESS_AND_TODO.md as your "current state" document

6. ❌ **Don't ask the user for permission to commit**
   - You have commit authority
   - Follow the rules, commit regularly
   - User will review commits via git log

7. ❌ **Don't commit code that doesn't compile**
   - Always verify Gradle build succeeds
   - If incomplete: [WIP] tag + explain what's not working

8. ❌ **Don't commit APK files to Git**
   - APKs belong in build/ directory (gitignored)
   - Only commit source code, resources, and configs
   - Document how to build APK in README

9. ❌ **Don't hardcode IP addresses**
   - Use constants or configuration
   - Default to 192.168.144.20 but allow user configuration
   - Document network configuration requirements

10. ❌ **Don't ignore Android Studio warnings**
    - Fix or explicitly suppress with @Suppress annotation
    - Document why suppressed if necessary

---

## 📁 KEY FILES REFERENCE

### Must-Update Files
| File | Update When | Priority |
|------|-------------|----------|
| `PROGRESS_AND_TODO.md` | After every significant change | 🔴 Critical |
| `README.md` | Build/setup process changes | 🟡 Important |
| `ARCHITECTURE.md` | App structure changes | 🟡 Important |

### Reference-Only Files (Read Once)
| File | Purpose | When to Re-Read |
|------|---------|-----------------|
| `Project_Summary_and_Action_Plan.md` | Initial project understanding | Only if completely lost |
| `Command_Protocol_Specification_v1.0.md` | Protocol details | When implementing protocol features |
| `Protocol_Implementation_Quick_Start.md` | Protocol implementation guide | When implementing network layer |
| `Phase1_Requirements_Update.md` | Feature requirements | When implementing new features |

### Session-Start Files (Read Every Time)
| File | Purpose |
|------|---------|
| `CC_READ_THIS_FIRST.md` | This file - workflow rules |
| `PROGRESS_AND_TODO.md` | Current status and next tasks |

---

## 🎯 PROJECT QUICK REFERENCE

### Critical Information

**Project Location:** `/path/to/android/project/` (TBD)  
**Git Repository:** `https://github.com/unmanned-systems-uk/DPM-V2.git`  
**Git Credentials:**
- Username: `unmanned-systems-uk`

**Target Platform:**
- SkyDroid H16 Pro Ground Station
- Android 7.1.2 (API 25) minimum
- Android 11 (API 30) target
- Custom H16 firmware

**Development Tools:**
- Android Studio (latest stable)
- JDK 17 (Eclipse Adoptium)
- Gradle 8.x
- Kotlin 1.9.x

**Important Paths:**
- Project: `/android/` (relative to repo root)
- Source: `/android/app/src/main/`
- Resources: `/android/app/src/main/res/`
- Manifests: `/android/app/src/main/AndroidManifest.xml`

### Network Configuration

**Air-Side Addresses:**
- TCP Commands: `192.168.144.20:5000`
- UDP Status (receive): `192.168.144.11:5001` (listen on ground station)
- UDP Heartbeat: `192.168.144.20:5002` (bidirectional)

**Ground Station:**
- IP: `192.168.144.11` (H16 ground station address)
- Network: H16 internal network (192.168.144.x)

### Build Commands

**Gradle Build:**
```bash
# Sync project
./gradlew sync

# Build debug APK
./gradlew assembleDebug

# Build release APK (signed)
./gradlew assembleRelease

# Clean build
./gradlew clean build

# Run tests
./gradlew test

# Run lint checks
./gradlew lint
```

**ADB Commands:**
```bash
# List connected devices
adb devices

# Install APK
adb install -r app/build/outputs/apk/debug/app-debug.apk

# Uninstall app
adb uninstall com.dpm.groundstation

# View logs
adb logcat | grep DPM

# Clear logs
adb logcat -c

# Connect to H16 wirelessly
adb connect 192.168.144.11:5555
```

### Current Phase

**Phase:** Phase 1 - Planning & Setup  
**Status:** Documentation created, ready to begin development  
**Current Blocker:** None - awaiting start  
**Next Steps:** Set up Android Studio project, create protocol data classes

---

## 🔍 DECISION TREE: "What Should I Do?"

### Visual Session Workflow

```
╔═══════════════════════════════════════════════════════════════╗
║                    START OF SESSION                           ║
╚═══════════════════════════════════════════════════════════════╝
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Read CC_READ_THIS_FIRST.md           │ ◄── MANDATORY
         │  (Workflow rules & standards)          │     Every session
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Read PROGRESS_AND_TODO.md             │ ◄── MANDATORY
         │  (Current status, next tasks)          │     Every session
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  git status && git log -5              │
         │  (Check uncommitted work)              │
         └────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │ Any uncommitted changes from last time? │
        └─────────────────────────────────────────┘
                 │                        │
                 │ YES                    │ NO
                 ▼                        │
    ┌─────────────────────┐              │
    │ Complete & commit   │              │
    │ OR mark as [WIP]    │              │
    └─────────────────────┘              │
                 │                        │
                 └────────┬───────────────┘
                          ▼
         ┌────────────────────────────────────────┐
         │  Identify current task from            │
         │  PROGRESS_AND_TODO.md                  │
         │  (First unchecked [ ] in current phase)│
         └────────────────────────────────────────┘
                              │
                              ▼
╔═══════════════════════════════════════════════════════════════╗
║                    WORK CYCLE (30-60 min)                     ║
╚═══════════════════════════════════════════════════════════════╝
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
    ┌─────────────────────┐   ┌─────────────────────┐
    │  Need reference     │   │  Implement/debug    │
    │  docs?              │   │  work on task       │
    └─────────────────────┘   └─────────────────────┘
                 │                         │
                 ▼                         │
    Read relevant docs:                    │
    • Protocol specs (commands/responses)  │
    • Phase1 Requirements (features)       │
    • Architecture docs (structure)        │
    • Android docs (APIs/patterns)         │
                 │                         │
                 └────────────┬────────────┘
                              ▼
         ┌────────────────────────────────────────┐
         │  Build APK & test (when possible)     │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Work complete or 30-60 min passed?   │
         └────────────────────────────────────────┘
                              │
                              ▼
╔═══════════════════════════════════════════════════════════════╗
║                    COMMIT CYCLE                               ║
╚═══════════════════════════════════════════════════════════════╝
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Test changes (compile, verify)        │
         │  ./gradlew assembleDebug               │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Update PROGRESS_AND_TODO.md           │ ◄── MANDATORY
         │  • Mark tasks [x]                      │     Before commit
         │  • Update completion %                 │
         │  • Add to Recent Updates               │
         │  • Update timestamp                    │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  Update other docs if needed           │
         │  • README (build changes)              │
         │  • ARCHITECTURE (structure changes)    │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  git add -A                            │
         │  (Stage code + docs together)          │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  git diff --cached                     │
         │  (Review what you're committing)       │
         └────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────────┐
         │  git commit -m "[TYPE] ..."            │
         │  (Use proper format & prefix)          │
         └────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │ More work to do in this session?        │
        └─────────────────────────────────────────┘
                 │                        │
           YES   │                        │ NO
                 │                        │
                 ▼                        ▼
         Back to WORK CYCLE      ┌────────────────┐
                                  │  git push      │
                                  │  origin main   │
                                  └────────────────┘
                                          │
                                          ▼
╔═══════════════════════════════════════════════════════════════╗
║                    END OF SESSION                             ║
╚═══════════════════════════════════════════════════════════════╝
```

### Scenario Flowcharts

#### Scenario A: Just Completed a Feature

```
Feature Complete
        │
        ▼
┌───────────────┐
│ Test it       │
│ thoroughly    │
│ Build APK     │
└───────────────┘
        │
        ▼
┌────────────────────────────────┐
│ Update PROGRESS_AND_TODO.md    │
│ ├─ Mark task [x]               │
│ ├─ Update completion %         │
│ ├─ Add to Recent Updates       │
│ └─ Update timestamp            │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│ Update other docs if needed    │
│ (README, ARCHITECTURE)          │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│ git add -A                     │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│ git commit -m "[FEATURE] ..."  │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│ git push origin main           │
└────────────────────────────────┘
        │
        ▼
    Continue work
    or end session
```

#### Scenario B: Discovered a Bug

```
Bug Found
     │
     ▼
┌────────────────────────────────┐
│ Investigate & document         │
│ findings                       │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ Update PROGRESS_AND_TODO.md    │
│ ├─ Add to Issue Tracker       │
│ ├─ Document symptoms           │
│ ├─ Document error details      │
│ └─ Update timestamp            │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ git commit -m                  │
│ "[DOCS] Documented bug #X"     │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ Work on fixing the bug         │
│ (may take multiple cycles)     │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ Bug fixed!                     │
│ Test thoroughly                │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ Update PROGRESS_AND_TODO.md    │
│ ├─ Mark issue RESOLVED         │
│ ├─ Document solution           │
│ ├─ Remove from blockers        │
│ └─ Update timestamp            │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ git commit -m                  │
│ "[FIX] Resolved bug #X"        │
└────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│ git push origin main           │
└────────────────────────────────┘
```

#### Scenario C: End of Work Session

```
Session Ending
        │
        ▼
┌───────────────────┐
│ Is work complete? │
└───────────────────┘
    │           │
  YES │         │ NO
    │           │
    ▼           ▼
Complete    Incomplete
update      update with
            [WIP] tag
    │           │
    └─────┬─────┘
          ▼
┌────────────────────────────────┐
│ Update PROGRESS_AND_TODO.md    │
│ ├─ Document current state      │
│ ├─ List what's done            │
│ ├─ List next steps             │
│ └─ Update timestamp            │
└────────────────────────────────┘
          │
          ▼
┌────────────────────────────────┐
│ Verify all changes committed   │
│ git status (should be clean)   │
└────────────────────────────────┘
          │
          ▼
    ┌─────────────┐
    │ Clean?      │
    └─────────────┘
      │         │
    NO│         │YES
      │         │
      ▼         │
  Stage &       │
  commit        │
  everything    │
      │         │
      └────┬────┘
           ▼
┌────────────────────────────────┐
│ git push origin main           │
└────────────────────────────────┘
           │
           ▼
       ╔═══════╗
       ║ DONE  ║ ◄── Can safely end session
       ╚═══════╝
```

---

## 🚀 EFFICIENCY TIPS

### For Claude Code (You)

1. **Batch Documentation Updates**
   - Don't update docs after every tiny change
   - Update after completing logical units of work
   - BUT: Always update before committing code

2. **Use Git Effectively**
   - `git status` frequently
   - `git diff` before committing
   - `git log --oneline -5` to see recent history

3. **Leverage Your Context**
   - You remember the current session's work
   - No need to re-read everything you already know
   - Focus on PROGRESS_AND_TODO.md for state

4. **Android Studio Shortcuts**
   - Use Gradle sync after dependency changes
   - Build frequently to catch errors early
   - Use logcat to debug runtime issues
   - Leverage Android Studio's inspection warnings

5. **Testing Strategy**
   - Test network components with mock data first
   - UI can be built with placeholder data
   - Integration testing when air-side available
   - Emulator sufficient for most development

### For User (Human)

1. **Trust the Process**
   - CC will commit regularly without asking
   - Review commits via `git log` when curious
   - PROGRESS_AND_TODO.md always shows current state

2. **Quick Status Checks**
   - Ask: "What's our current status?" → CC reads PROGRESS_AND_TODO.md
   - Ask: "What did you do today?" → CC summarizes recent commits
   - Ask: "What's blocking us?" → CC checks Issue Tracker

3. **Override When Needed**
   - CC follows these rules by default
   - You can always say "don't commit yet" if needed
   - You can ask for specific documentation updates

---

## 📊 METRICS TO MAINTAIN

### Documentation Health
- ✅ PROGRESS_AND_TODO.md updated within last 24 hours
- ✅ All completed tasks marked [x]
- ✅ Completion percentages accurate (±5%)
- ✅ No "Last Updated" timestamps older than 48 hours

### Git Health
- ✅ No more than 2 hours of work without commit
- ✅ All commits have descriptive messages
- ✅ No uncommitted changes at end of session
- ✅ Main branch always buildable (no broken commits)

### Code Health
- ✅ All code follows Kotlin conventions
- ✅ All features tracked in PROGRESS_AND_TODO.md
- ✅ All bugs documented in Issue Tracker
- ✅ Gradle builds successfully
- ✅ No compiler errors or unresolved warnings
- ✅ APK builds and installs (when tested)

---

## 🆘 TROUBLESHOOTING

### Workflow Questions

**Q: "I'm not sure what to work on next"**
```
A: Follow this process:
1. Read PROGRESS_AND_TODO.md
2. Check "RECENT UPDATES" for context
3. Look at current phase section
4. Find first unchecked [ ] task
5. Check Issue Tracker for blockers
6. If still unclear, check "Next Steps" section
```

**Q: "Should I ask permission to commit?"**
```
A: NO! You have commit authority. Just follow the rules:
- Commit every 30-60 minutes
- Use [TYPE] prefixes
- Update docs first
- Write clear messages
- Commit and push without asking
```

**Q: "How much detail in commit messages?"**
```
A: Good commit message format:
[TYPE] Component: Brief one-line summary (max 72 chars)

- Detail 1 (what changed)
- Detail 2 (why it changed)
- Detail 3 (impact/result)

Example length: 3-5 bullet points is ideal
Too short: Just "[FEATURE] Added UI" ❌
Too long: 20 bullet points ❌
Just right: 3-5 clear, specific points ✅
```

**Q: "Do I update docs before or after committing?"**
```
A: BEFORE! Always this order:
1. Make code changes
2. Test changes (build APK)
3. Update PROGRESS_AND_TODO.md
4. Update other relevant docs
5. Stage all changes (code + docs)
6. Commit everything together
7. Push

Never commit code without updating docs!
```

### Technical Issues

**Issue: "Gradle build failed"**
```bash
# Check error messages
./gradlew assembleDebug --stacktrace

# Common causes:
# 1. Dependency conflict
#    - Check build.gradle dependencies
#    - Update conflicting versions
#    - Sync Gradle

# 2. Kotlin compilation error
#    - Read error message carefully
#    - Fix syntax/type errors
#    - Check imports

# 3. Resource issue
#    - Check XML syntax
#    - Check resource IDs
#    - Clean build: ./gradlew clean

# 4. Cache corruption
#    - Invalidate caches: File > Invalidate Caches / Restart
#    - Delete .gradle/ directory
#    - Delete build/ directory
#    - Re-sync and rebuild
```

**Issue: "Can't connect to device via ADB"**
```bash
# Check device connection
adb devices

# If "unauthorized":
# 1. Check device screen for USB debugging prompt
# 2. Allow debugging on device
# 3. Try again: adb devices

# If device not showing:
# 1. Check USB cable
# 2. Enable developer options on device
# 3. Enable USB debugging in developer options
# 4. Try different USB port
# 5. Restart ADB: adb kill-server && adb start-server

# For H16 (wireless):
adb connect 192.168.144.11:5555
# Ensure H16 is on same network
```

**Issue: "App crashes on startup"**
```bash
# View crash logs
adb logcat | grep AndroidRuntime

# Common causes:
# 1. Missing permissions in manifest
#    - Add INTERNET permission
#    - Add NETWORK_STATE permission

# 2. Null pointer exception
#    - Check initialization order
#    - Verify LiveData observers set up
#    - Check lateinit properties

# 3. Network on main thread
#    - Move network calls to coroutines
#    - Use viewModelScope or lifecycleScope

# 4. Resource not found
#    - Check layout IDs match
#    - Rebuild project
#    - Clean and sync Gradle
```

**Issue: "Network connection failing"**
```bash
# Verify network in logcat
adb logcat | grep DPM

# Check:
# 1. INTERNET permission in manifest
# 2. Correct IP address (192.168.144.20)
# 3. Correct port (5000 TCP, 5001/5002 UDP)
# 4. Network available on device
# 5. Air-side service running
# 6. Firewall not blocking

# Test with ping (if possible):
adb shell ping 192.168.144.20
```

---

## 📝 SUMMARY - THE GOLDEN RULES

1. 🔴 **ALWAYS read this file (CC_READ_THIS_FIRST.md) at session start**
2. 🔴 **ALWAYS read PROGRESS_AND_TODO.md to understand current state**
3. 🔴 **ALWAYS update PROGRESS_AND_TODO.md after significant changes**
4. 🔴 **ALWAYS commit regularly (every 30-60 min of work)**
5. 🔴 **ALWAYS use descriptive commit messages with [TYPE] prefix**
6. 🔴 **ALWAYS commit before ending a work session**
7. 🔴 **ALWAYS verify Gradle build succeeds before committing**
8. 🟡 **DON'T re-read large planning docs unless necessary**
9. 🟡 **DON'T commit code that doesn't compile**
10. 🟡 **DON'T commit APK files to Git**
11. 🟡 **DON'T leave orphaned documentation**
12. 🟡 **DON'T hardcode network configuration**
13. 🟢 **DO work efficiently and maintain documentation in parallel**
14. 🟢 **DO test on device/emulator when possible**
15. 🟢 **DO follow Kotlin and Android best practices**

---

## 🎓 FOR NEW CLAUDE CODE INSTANCES

**If this is your first time on this project:**

1. ✅ Read this file (CC_READ_THIS_FIRST.md) - you're doing it!
2. ✅ Read PROGRESS_AND_TODO.md thoroughly
3. ✅ Skim Project_Summary_and_Action_Plan.md (overview only)
4. ✅ Read Command_Protocol_Specification_v1.0.md (protocol details)
5. ✅ Read Protocol_Implementation_Quick_Start.md (implementation guide)
6. ✅ Check `git log --oneline -20` (understand recent history)
7. ✅ Identify current phase and next task
8. ✅ Start working!

**On subsequent sessions:**
1. ✅ Read CC_READ_THIS_FIRST.md (this file)
2. ✅ Read PROGRESS_AND_TODO.md (current state)
3. ✅ Check `git status` and `git log --oneline -5`
4. ✅ Continue work

---

## ✅ CHECKLIST - AM I FOLLOWING THE RULES?

Before ending each work session, verify:

- [ ] PROGRESS_AND_TODO.md updated with today's work
- [ ] All task checkboxes reflect reality
- [ ] Completion percentages updated
- [ ] Visual progress bars updated
- [ ] "Last Updated" timestamp is current
- [ ] Issue Tracker reflects current bugs/blockers
- [ ] All code changes are committed
- [ ] All commits have descriptive messages
- [ ] All commits pushed to origin/main
- [ ] Gradle build succeeds (./gradlew assembleDebug)
- [ ] No compiler errors or unresolved warnings
- [ ] No orphaned documentation
- [ ] No [WIP] commits unless work is genuinely incomplete

**If all checked: You're good! 🎉**

---

## 🎯 ANDROID-SPECIFIC BEST PRACTICES

### Code Style
- ✅ Follow Kotlin coding conventions
- ✅ Use meaningful variable/function names
- ✅ Add KDoc comments for public APIs
- ✅ Keep functions small and focused
- ✅ Use data classes for models
- ✅ Use sealed classes for states
- ✅ Prefer immutability (val over var)

### Architecture
- ✅ Follow MVVM pattern
- ✅ Separate concerns (UI, ViewModel, Repository, Network)
- ✅ Use LiveData/StateFlow for reactive data
- ✅ Use Coroutines for async operations
- ✅ Keep Activities/Fragments thin
- ✅ Business logic in ViewModels
- ✅ Network logic in separate classes

### Threading
- ✅ Never block main thread
- ✅ Use Dispatchers.IO for network/disk
- ✅ Use Dispatchers.Main for UI updates
- ✅ Use viewModelScope for ViewModel coroutines
- ✅ Use lifecycleScope for UI coroutines
- ✅ Handle cancellation properly

### Error Handling
- ✅ Catch and handle exceptions
- ✅ Show user-friendly error messages
- ✅ Log errors with appropriate level
- ✅ Don't let app crash silently
- ✅ Provide retry mechanisms
- ✅ Handle network failures gracefully

### Testing
- ✅ Build frequently to catch errors early
- ✅ Test on emulator when possible
- ✅ Test on real H16 hardware when available
- ✅ Check logcat for warnings/errors
- ✅ Verify UI updates correctly
- ✅ Test connection failure scenarios

---

**Document Status:** ✅ Active - Use This Every Session  
**Version:** 1.0  
**Last Updated:** October 24, 2025  
**Maintained By:** Human oversight, enforced by Claude Code

**🔴 REMEMBER: This document is your first read every session! 🔴**