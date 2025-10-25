# Claude Code - READ THIS FIRST
## DPM Payload Manager Project Rules & Workflow

**Date Created:** October 24, 2025  
**Version:** 1.0  
**Status:** 🔴 **MANDATORY - READ EVERY SESSION**

---

## 🎯 PURPOSE OF THIS DOCUMENT

This document establishes the **mandatory workflow** for Claude Code (CC) when working on the DPM Payload Manager project. These rules ensure:

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

### 2. Pull Latest Changes from Git
- ✅ **MANDATORY** - Always pull latest before doing ANY work
- ✅ Run `git pull origin main` at start of EVERY session
- ✅ This ensures you have latest protocol definitions
- ✅ This ensures you have changes from ground-side/air-side
- ⚠️ **CRITICAL** - Never work on stale code!

**If git pull shows conflicts:**
1. **STOP** immediately
2. **Tell user**: "Git pull has conflicts that need resolution"
3. **List** the conflicting files
4. **Wait** for user to resolve or give instructions
5. **DO NOT** attempt to resolve conflicts without user approval

### 3. Check Protocol Synchronization
- ✅ **MANDATORY** - Check `docs/protocol/commands.json` for new commands
- ✅ Look for commands with `"air_side": false`
- ✅ Check if ground-side has added commands you need to implement
- ✅ **ASK USER** about any new commands before implementing
- ⚠️ **CRITICAL** - Protocol sync MUST happen every session

### 4. Check Current Status
- ✅ Read `PROGRESS_AND_TODO.md` to understand:
  - What phase we're in
  - What's been completed
  - What's currently blocked
  - What to work on next

### 5. Read Relevant Technical Docs (If Needed)
- ⚠️ **DO NOT** read `Project_Summary_and_Action_Plan.md` unless explicitly asked
- ⚠️ **DO NOT** re-read technical specs you've already reviewed in this session
- ✅ **DO** read specific technical docs when starting new features:
  - `BUILD_AND_IMPLEMENTATION_PLAN.md` - When implementing new components
  - `DOCKER_SETUP.md` - When working with Docker or Sony SDK
  - Protocol specs - When implementing protocol features
  - Sony SDK docs - When working on camera integration

### 6. Understand Git Status
- ✅ Run `git status` to check for uncommitted changes
- ✅ Identify what needs to be committed
- ✅ Check current branch (should be `main`)

---

## 🔄 MANDATORY WORKFLOW RULES

### Rule #0: Protocol Synchronization (MOST IMPORTANT!)

**🔴 CRITICAL: Check protocol files EVERY SESSION before doing ANY work! 🔴**

#### Session Start Protocol Check

**ALWAYS do this at the start of EVERY session:**

```bash
# 1. Check for new commands in protocol definition
cat docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.air_side == false) | .key'

# This will list commands NOT YET implemented on air-side
```

**If you see ANY commands listed:**
1. **STOP** and read the command definition in `commands.json`
2. **ASK THE USER:**
   - "I see new command(s) in the protocol: [list them]"
   - "What should these commands do?"
   - "Should I implement them now, or are they planned for later?"
3. **WAIT** for user response before proceeding
4. **DO NOT** assume you know what to implement

#### Adding New Commands (Air-Side)

**When implementing a new command:**

```
1. User adds command to docs/protocol/commands.json
   └─ Sets "air_side": false, "ground_side": true (if Android already has it)

2. CC detects new command at session start
   └─ Asks user what it does and if it should be implemented

3. CC implements the command handler in tcp_server.cpp
   ├─ Add handler function (e.g., handleCameraFocus)
   ├─ Add route in processCommand()
   ├─ Add any new error codes to messages.h
   └─ Test implementation

4. CC updates commands.json
   └─ Set "air_side": true

5. CC updates docs/IMPLEMENTATION_STATUS.md
   └─ Mark command as complete in coverage table

6. CC commits with clear message
   └─ [PROTOCOL] Implemented [command.name] command
```

#### Checking What Ground-Side Has

**Check what Android app has implemented:**

```bash
cat docs/protocol/commands.json | jq -r 'to_entries[] |
  select(.value.implemented.ground_side == true and
         .value.implemented.air_side == false) | .key'
```

**These are commands the Android app can SEND but you can't HANDLE yet!**

#### Protocol Sync Rules

✅ **DO:**
- Check protocol files at START of every session
- Ask user about new commands before implementing
- Update `commands.json` immediately after implementing
- Keep `commands.json` as single source of truth
- Verify error codes match between `protocol_v1.0.json` and `messages.h`
- Update `IMPLEMENTATION_STATUS.md` when completing commands

❌ **DON'T:**
- Implement commands not in `commands.json`
- Assume what a command should do without asking
- Mark `"air_side": true` until fully implemented and tested
- Add commands without updating protocol documentation
- Skip protocol check at session start

#### Example Session Start

```
CC: Starting session, checking protocol sync...

[runs: cat docs/protocol/commands.json | jq ...]

CC: I found 2 commands not yet implemented on air-side:
1. camera.focus - No description in protocol
2. camera.get_properties - Marked as planned-v1.1

I see camera.focus has "ground_side": true, meaning the
Android app can already send this command but I can't
handle it yet.

Questions:
1. What should camera.focus do? (parameters, behavior)
2. Should I implement it now or is it scheduled for later?
3. Are there any Sony SDK calls I should use for this?

[WAITS for user response before proceeding]
```

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
- Update "Last Updated" timestamp

## ISSUE TRACKER
- Add new issues discovered
- Update status of existing issues
- Mark resolved issues
```

**Format Example:**
```markdown
**Last Updated:** October 24, 2025 15:30 - After implementing camera connection fix
```

### Rule #2: Commit to Git Regularly

**Commit frequency rules:**

1. **After completing any functional unit:**
   - ✅ New feature implemented and tested
   - ✅ Bug fixed and verified
   - ✅ New component created
   - ✅ Documentation updated significantly

2. **Before switching tasks:**
   - ✅ Always commit current work before starting something new
   - Even if incomplete - use WIP (Work In Progress) tag

3. **At end of session:**
   - ✅ **MANDATORY** - Commit all changes before ending work
   - Update docs first, then commit

4. **After significant debugging:**
   - ✅ Document findings in PROGRESS_AND_TODO.md
   - ✅ Commit the documentation update

**Commit Message Format:**

```bash
# Feature implementation
git commit -m "[FEATURE] Component: Brief description

- Detailed point 1
- Detailed point 2
- Resolves: issue reference if applicable"

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
git commit -m "[FEATURE] Camera: Implemented Sony SDK enumeration

- Added test_camera.cpp for basic connection testing
- Integrated Sony SDK headers and libraries in CMake
- Successfully enumerates Sony A1 camera via USB"

git commit -m "[FIX] Docker: Resolved CrAdapter dynamic loading issue

- Root cause: Adapters statically linked in CMakeLists.txt
- Solution: Only link libCr_Core.so, copy CrAdapter/ to build dir
- Result: SDK now loads adapters dynamically, error 0x34563 resolved"

git commit -m "[DOCS] Updated PROGRESS_AND_TODO.md with Docker solution

- Added Docker deployment section (Phase 1.5)
- Documented libxml2 ABI resolution
- Updated completion status to 68%"
```

### Rule #3: Never Leave Orphaned Documentation

**Before making code changes:**
- ✅ Check if any documentation references affected code
- ✅ Plan documentation updates alongside code changes

**After making code changes:**
- ✅ Update relevant technical documentation
- ✅ Update PROGRESS_AND_TODO.md
- ✅ Update BUILD_AND_IMPLEMENTATION_PLAN.md if architecture changed
- ✅ Update DOCKER_SETUP.md if Docker/build process changed

**Red flags - don't let these happen:**
- ❌ Code exists but not mentioned in PROGRESS_AND_TODO.md
- ❌ Files created but not tracked in BUILD_AND_IMPLEMENTATION_PLAN.md
- ❌ Features working but marked as "Not Started" in docs
- ❌ Issues resolved but still marked "Active" in Issue Tracker
- ❌ Completion percentages not updated after significant work

### Rule #4: Git Workflow

**Standard workflow:**

```bash
# 1. Start of session - ALWAYS pull latest first
git pull origin main

# 2. Check status and recent commits
git status
git log --oneline -5  # Review recent commits

# 3. Make changes, test, verify

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



## 🚫 ANTI-PATTERNS TO AVOID

### DON'T Do These Things:

1. ❌ **Don't make multiple unrelated changes in one commit**
   - Keep commits focused and atomic
   - If you fixed a bug AND added a feature, make 2 commits

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

7. ❌ **Don't commit broken code without marking it [WIP]**
   - If code doesn't compile: [WIP] tag + explain in commit message
   - If feature is incomplete: [WIP] tag + document what's left

---

## 📁 KEY FILES REFERENCE

### Must-Update Files
| File | Update When | Priority |
|------|-------------|----------|
| `PROGRESS_AND_TODO.md` | After every significant change | 🔴 Critical |
| `BUILD_AND_IMPLEMENTATION_PLAN.md` | Architecture/build changes | 🟡 Important |
| `DOCKER_SETUP.md` | Docker/SDK integration changes | 🟡 Important |

### Reference-Only Files (Read Once)
| File | Purpose | When to Re-Read |
|------|---------|-----------------|
| `Project_Summary_and_Action_Plan.md` | Initial project understanding | Only if completely lost |
| Protocol specifications | Protocol implementation details | When implementing protocol features |
| Sony SDK documentation | Camera integration details | When working on camera code |

### Session-Start Files (Read Every Time)
| File | Purpose |
|------|---------|
| `CC_READ_THIS_FIRST.md` | This file - workflow rules |
| `PROGRESS_AND_TODO.md` | Current status and next tasks |

---

## 🎯 PROJECT QUICK REFERENCE

### Critical Information

**Project Location:** `/home/dpm/DPM/sbc/`  
**Git Repository:** `https://github.com/unmanned-systems-uk/DPM.git`  
**Git Credentials:**
- Username: `unmanned-systems-uk`


**Target Platform:**
- Raspberry Pi 4 (ARM64v8)
- SSH: `dpm@10.0.1.127` (password: `2350`)
- Ubuntu 25.04 (host) / Ubuntu 22.04 (Docker container)

**Docker Container:**
- Name: `payload-manager`
- Image: `payload-manager:latest`
- Status: Always running (production mode)
- Access: `sudo docker exec -it payload-manager bash`

**Important Paths:**
- Project: `/home/dpm/DPM/sbc/`
- Sony SDK: `/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/`
- Logs: `/home/dpm/DPM/sbc/logs/`
- Build: `/home/dpm/DPM/sbc/build/` (host)
- Container Build: `/app/sbc/build/` (inside Docker)

### Build Commands

**Host (for development/testing):**
```bash
cd /home/dpm/DPM/sbc
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . -j4
```

**Docker (production):**
```bash
cd /home/dpm/DPM/sbc
./build_container.sh       # Rebuild image
./run_container.sh prod    # Run in production
./shell.sh                 # Access container shell
./rebuild.sh               # Quick rebuild inside container
```

### Current Phase

**Phase:** Phase 1.5 - Docker Deployment + Camera Integration  
**Status:** Docker ✅ Complete, Camera Testing 🐛 Debugging  
**Current Blocker:** Connection error 0x8208 (OnConnected callback not firing)  
**Next Steps:** Debug camera connection, compare with RemoteCli implementation

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
    • BUILD_PLAN (architecture)            │
    • DOCKER_SETUP (Sony SDK)              │
    • GIT_WORKFLOW (Git help)              │
    • CC_QUICK_REF (fast lookup)           │
                 │                         │
                 └────────────┬────────────┘
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
         │  • BUILD_PLAN (architecture changes)   │
         │  • DOCKER_SETUP (Docker changes)       │
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
│ (BUILD_PLAN, DOCKER_SETUP)     │
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
│ ├─ Document error codes        │
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

## 🔍 DECISION TREE: "What Should I Do?"

### Scenario 1: Starting a New Session
```
START
  ↓
Read CC_READ_THIS_FIRST.md (this file)
  ↓
Read PROGRESS_AND_TODO.md
  ↓
Check git status
  ↓
Identify current task from PROGRESS_AND_TODO.md
  ↓
Proceed with work
```

### Scenario 2: Just Completed a Feature
```
Feature Complete
  ↓
Test it
  ↓
Update PROGRESS_AND_TODO.md
  ├─ Mark task complete [x]
  ├─ Update completion %
  ├─ Add to Recent Updates
  └─ Update Last Updated timestamp
  ↓
Update other relevant docs if needed
  ↓
git add -A
  ↓
git commit -m "[FEATURE] ..."
  ↓
git push origin main
```

### Scenario 3: Discovered a Bug
```
Bug Found
  ↓
Investigate and document findings
  ↓
Update PROGRESS_AND_TODO.md
  ├─ Add to Issue Tracker
  ├─ Document symptoms
  ├─ Document attempted fixes
  └─ Update Last Updated
  ↓
git commit -m "[DOCS] Documented bug #X"
  ↓
Fix the bug
  ↓
Update PROGRESS_AND_TODO.md
  ├─ Mark issue resolved
  └─ Update Last Updated
  ↓
git commit -m "[FIX] Resolved bug #X"
  ↓
git push origin main
```

### Scenario 4: End of Work Session
```
Session Ending
  ↓
Is work complete? 
  ├─ YES → Update docs, commit with [FEATURE]
  └─ NO → Update docs, commit with [WIP]
  ↓
Update PROGRESS_AND_TODO.md
  ├─ Document current state
  ├─ List next steps
  └─ Update Last Updated
  ↓
git add -A
  ↓
git commit -m "[TYPE] Current state"
  ↓
git push origin main
  ↓
DONE - Can safely end session
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

4. **Template Responses**
   - When updating PROGRESS_AND_TODO.md, use consistent format
   - When committing, use consistent message format
   - Maintain professional, concise documentation

5. **Parallel Work**
   - You can update docs while explaining what you did
   - Commit messages can be composed while staging files
   - Efficiency comes from batching, not skipping

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
- ✅ All code documented in BUILD_AND_IMPLEMENTATION_PLAN.md
- ✅ All features tracked in PROGRESS_AND_TODO.md
- ✅ All bugs documented in Issue Tracker
- ✅ Docker builds successfully
- ✅ Tests pass (when implemented)

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

**Q: "I don't know if I should read a document"**
```
A: Use this decision tree:
├─ Is it CC_READ_THIS_FIRST.md? 
│  └─ YES → ALWAYS read it (every session)
├─ Is it PROGRESS_AND_TODO.md?
│  └─ YES → ALWAYS read it (current state)
├─ Have I read it this session?
│  └─ NO → Read it
├─ Is it >500 lines?
│  └─ YES → Only read relevant sections
├─ Is it Project_Summary_and_Action_Plan.md?
│  └─ RARELY → Only if completely lost
└─ Am I implementing something related to the doc?
   └─ YES → Read relevant sections
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
Too short: Just "[FIX] Fixed bug" ❌
Too long: 20 bullet points ❌
Just right: 3-5 clear, specific points ✅
```

**Q: "Do I update docs before or after committing?"**
```
A: BEFORE! Always this order:
1. Make code changes
2. Test changes
3. Update PROGRESS_AND_TODO.md
4. Update other relevant docs
5. Stage all changes (code + docs)
6. Commit everything together
7. Push

Never commit code without updating docs!
```

**Q: "The user told me to do something that contradicts these rules"**
```
A: User instructions override these rules. However:
1. Acknowledge the override: "I understand you want me to..."
2. Follow user's instructions
3. Note any concerns if safety/quality impacted
4. Return to standard workflow after user's request complete
```

### Technical Issues

**Issue: "Git push failed"**
```bash
# Symptoms: Authentication failed, rejected push


# Solution 2: Pull first, then push
git pull origin main
# Resolve any conflicts if needed
git push origin main

# Solution 3: Check branch
git branch
# Should show: * main

# Solution 4: Check network
ping github.com
```

**Issue: "Docker container not running"**
```bash
# Check status
sudo docker ps -a | grep payload-manager

# If stopped, restart
sudo docker start payload-manager

# If doesn't exist, rebuild
cd /home/dpm/DPM/sbc
./build_container.sh
./run_container.sh prod

# Verify running
sudo docker ps | grep payload-manager
```

**Issue: "Can't compile inside Docker"**
```bash
# Access container
sudo docker exec -it payload-manager bash

# Check build directory
cd /app/sbc/build
ls -la

# If build corrupted, clean rebuild
cd /app/sbc
rm -rf build
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j4

# Or use helper script
cd /app/sbc
./rebuild.sh
```

**Issue: "File not found in container"**
```bash
# Verify file exists on host
ls -la /home/dpm/DPM/sbc/src/camera/camera_sony.cpp

# Check if mounted correctly
sudo docker exec payload-manager ls -la /app/sbc/src/camera/

# If missing, rebuild container
cd /home/dpm/DPM/sbc
./build_container.sh
./run_container.sh prod
```

**Issue: "Camera not detected"**
```bash
# Check on host first
lsusb | grep Sony

# If not on host:
# 1. Check camera is powered on
# 2. Check USB cable connected
# 3. Try different USB port

# If on host but not in container:
sudo docker exec payload-manager lsusb | grep Sony
# If missing, container needs USB passthrough
# Rebuild with: ./run_container.sh prod
```

### Process Issues

**Issue: "I made many changes without committing"**
```
Solution: Break into multiple commits now
1. Stage related changes together
2. Commit each logical group separately
3. Use [WIP] if some parts incomplete
4. Push all commits when done

Example:
git add src/camera/camera_sony.cpp src/camera/camera_sony.h
git commit -m "[FEATURE] Camera: Add Sony SDK wrapper"

git add docs/PROGRESS_AND_TODO.md
git commit -m "[DOCS] Updated progress with camera work"

git push origin main
```

**Issue: "I updated code but forgot to update docs"**
```
Solution: Update docs now, then amend or new commit
# If last commit just pushed:
1. Update docs now
2. New commit: [DOCS] Added missing documentation

# If last commit not pushed yet:
1. Update docs now
2. Stage docs: git add docs/PROGRESS_AND_TODO.md
3. Amend: git commit --amend --no-edit
4. Push: git push origin main
```

**Issue: "PROGRESS_AND_TODO.md has conflicting information"**
```
Solution: Fix conflicts immediately
1. Read entire document carefully
2. Identify all conflicts (e.g., task [x] but status "Not Started")
3. Determine correct state
4. Update all conflicting sections
5. Verify consistency:
   - Checkboxes match Recent Updates
   - Progress % matches visual bars
   - Issue Tracker accurate
   - Completion status realistic
6. Commit: [DOCS] Fixed documentation conflicts
```

**Issue: "Uncertain if this counts as 'significant change'"**
```
Decision Guide:

UPDATE DOCS FOR:
✅ Completed any task in a phase
✅ Discovered or fixed a bug
✅ Created new files
✅ Significant debugging (>30 min)
✅ Switched components/phases
✅ End of work session

DON'T UPDATE FOR:
❌ Fixed a typo
❌ Minor formatting changes
❌ Small refactoring (<10 lines)
❌ Reading documentation
❌ Exploring code

WHEN IN DOUBT:
If you spent >20 minutes on it → Update docs
If it changes project state → Update docs
If someone asks "what did you do?" this would be mentioned → Update docs
```

---

## 📝 SUMMARY - THE GOLDEN RULES

1. 🔴 **ALWAYS read this file (CC_READ_THIS_FIRST.md) at session start**
2. 🔴 **ALWAYS read PROGRESS_AND_TODO.md to understand current state**
3. 🔴 **ALWAYS update PROGRESS_AND_TODO.md after significant changes**
4. 🔴 **ALWAYS commit regularly (every 30-60 min of work)**
5. 🔴 **ALWAYS use descriptive commit messages with [TYPE] prefix**
6. 🔴 **ALWAYS commit before ending a work session**
7. 🟡 **DON'T re-read large planning docs unless necessary**
8. 🟡 **DON'T commit broken code without [WIP] tag**
9. 🟡 **DON'T leave orphaned documentation**
10. 🟢 **DO work efficiently and maintain documentation in parallel**

---

## 🎓 FOR NEW CLAUDE CODE INSTANCES

**If this is your first time on this project:**

1. ✅ Read this file (CC_READ_THIS_FIRST.md) - you're doing it!
2. ✅ Read PROGRESS_AND_TODO.md thoroughly
3. ✅ Skim Project_Summary_and_Action_Plan.md (overview only)
4. ✅ Read BUILD_AND_IMPLEMENTATION_PLAN.md (understand architecture)
5. ✅ Read DOCKER_SETUP.md (understand build environment)
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
- [ ] "Last Updated" timestamp is current
- [ ] Issue Tracker reflects current bugs/blockers
- [ ] All code changes are committed
- [ ] All commits have descriptive messages
- [ ] All commits pushed to origin/main
- [ ] No orphaned documentation
- [ ] No [WIP] commits unless work is genuinely incomplete

**If all checked: You're good! 🎉**

---

**Document Status:** ✅ Active - Use This Every Session  
**Version:** 1.0  
**Last Updated:** October 24, 2025  
**Maintained By:** Human oversight, enforced by Claude Code

**🔴 REMEMBER: This document is your first read every session! 🔴**
