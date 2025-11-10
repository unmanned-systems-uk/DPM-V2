# DPM-V2 Key Factors - Quick Reference

**WHO:** CC-Project-Manager
**Purpose:** Single source of truth for all DPM-V2 project information
**Last Updated:** 2025-11-09

---

## 🎯 What is DPM-V2?

DPM-V2 (Drone Payload Manager V2) is a professional UAV payload management system for Sony camera control via SkyDroid H16 Pro.

**Status:** ✅ Phase 1 In Progress | 📅 Phase 2 Planned

---

## 📊 Current Status

**Production Ready:** Partial (UDP communication, basic camera control)
**Current Phase:** Phase 1 - Sony SDK Foundation
**Active Work:** Camera property implementation, focus control

**Working Location:** `/home/anthony/DPM-V2`

---

## 🏗️ Technology Stack

**Air-Side (Drone):**
- Raspberry Pi 5 8GB
- Ubuntu 24.04 LTS ARM64
- C++17 with Sony Camera Remote SDK v2.00.00
- UDP communication (status broadcast)
- TCP server (command reception)

**Ground-Side (Controller):**
- SkyDroid H16 Pro (Android)
- Java/Kotlin
- Custom UI for camera control
- TCP client / UDP receiver

**Dev-Tools (Diagnostics):**
- Python (cross-platform)
- SystemTools diagnostic GUI
- 10 functional tabs
- Network monitoring, log analysis

**Communication:**
- H16 R16 digital data-link
- TCP: 9001 (commands Ground→Air)
- UDP: 9002 (status Air→Ground)
- UDP: 9003 (video stream)

---

## 📁 Project Structure

```
DPM-V2/
├── README.md                   (Main project overview)
├── DPM_KEY_FACTORS.md          (This file - quick reference)
│
├── protocol/                   (⚠️ PROTOCOL SPECS - Single source of truth)
│   ├── commands.json           (Command definitions)
│   └── camera_properties.json  (Camera property specs)
│
├── sbc/                        (AIR-SIDE: Raspberry Pi 5 C++ code)
│   ├── src/                    (C++ source code)
│   ├── docs/                   (Air-side documentation)
│   ├── build.sh                (Build script)
│   └── run_payload_manager.sh  (Run application)
│
├── android/                    (GROUND-SIDE: SkyDroid H16 Android app)
│   ├── app/src/                (Kotlin source)
│   ├── docs/                   (Ground-side documentation)
│   └── gradlew                 (Android build)
│
├── SystemTools/                (DEV-TOOLS: Python diagnostics)
│   ├── main.py                 (Entry point)
│   ├── docs/                   (Tools documentation)
│   └── version.py
│
├── docs/                       (DOCUMENTATION)
│   ├── CC_READ_THIS_FIRST.md   (⭐ SESSION START GUIDE)
│   ├── AIR_SIDE/               (Air-side specific docs)
│   ├── GROUND_SIDE/            (Ground-side specific docs)
│   ├── DEVELOPMENT_SIDE/       (Dev-tools specific docs)
│   ├── ALL_DOMAINS/            (Cross-cutting documentation)
│   │   ├── LESSONS_LEARNED.md  (Historical insights)
│   │   ├── WHO_TAG_GUIDE.md    (WHO tag protocol)
│   │   └── MASTER_STATUS.md    (Overall project status)
│   └── protocol/               (Protocol documentation)
│
├── .claude/                    (Workflow system)
│   └── settings.local.json     (Claude Code settings)
│
├── .github/                    (GitHub integration)
│   ├── ISSUE_TEMPLATE/         (7 comprehensive templates)
│   ├── domain-config.json
│   └── scripts/                (Automation scripts)
│
└── tools/                      (Development utilities)
```

---

## 🎯 Development Phases

### ✅ Phase 1: Sony SDK Foundation (CURRENT)
**Goal:** Establish reliable camera control via Sony SDK
**Status:** In Progress

**Key Deliverables:**
- ✅ UDP status broadcast (Air→Ground)
- ✅ TCP command reception (Ground→Air)
- 🚧 Sony SDK camera property control
- 🚧 Focus distance implementation
- 🚧 Comprehensive camera property support
- 🚧 Protocol JSON specifications

**Core Technologies:**
- Sony Camera Remote SDK v2.00.00
- C++17 camera interface
- UDP/TCP networking
- Android Kotlin UI

**Documentation:** `docs/AIR_SIDE/`, `docs/GROUND_SIDE/`

---

### 📅 Phase 2: AI & Vision Systems (PLANNED)
**Goal:** Intelligent processing on Jetson platform
**Status:** Planned for future

**Planned Features:**
- AI/ML object detection
- Real-time tracking
- Vision-based automation
- Edge processing on Jetson
- Advanced camera automation

**Target Platform:** NVIDIA Jetson (ARM64)

**Documentation:** To be created in `docs/phases/phase-2-ai-vision/`

---

### 💡 Phase 3+: Future Expansion (CONCEPTUAL)
**Goal:** Advanced autonomy and multi-platform support
**Status:** Long-term vision

---

## 🏷️ WHO Tag System (MANDATORY)

**All work must be attributed with WHO tags**

### DPM Domain Tags

**CC-Air-Side**
- Raspberry Pi 5 C++ code
- Sony SDK integration
- UDP status broadcasting
- TCP command reception
- Example: `**WHO:** CC-Air-Side`

**CC-Ground-Side**
- Android H16 app
- Kotlin UI code
- Command transmission
- Status display
- Example: `**WHO:** CC-Ground-Side`

**CC-Dev-Tools**
- SystemTools Python code
- Diagnostic interfaces
- Testing utilities
- Log analysis
- Example: `**WHO:** CC-Dev-Tools`

**CC-Project-Manager**
- Cross-domain coordination
- GitHub issue management
- Planning and oversight
- Documentation updates
- Example: `**WHO:** CC-Project-Manager`

**User (Anthony)**
- User requests
- Requirements
- Testing feedback
- Approvals
- Example: `**WHO:** User (Anthony)`

### Where to Use WHO Tags

✅ **GitHub issue comments** (start of every comment)
✅ **Git commits** (in domain tags)
✅ **Documentation updates** (in headers)
✅ **Task context files** (in headers)
✅ **Cross-domain handoffs** (critical!)

**See:** [docs/ALL_DOMAINS/WHO_TAG_GUIDE.md](docs/ALL_DOMAINS/WHO_TAG_GUIDE.md) for complete guide

---

## 📋 Issue-First Workflow (MANDATORY)

**GitHub Issues = Single Source of Truth**

### Core Rules

1. **NEVER start work without a GitHub issue**
   - Check existing: `gh issue list --state open`
   - Create if needed: `gh issue create`

2. **ALWAYS search historical issues FIRST**
   - Before implementing: `.github/scripts/search-history.ps1 "keyword"`
   - Learn from past attempts
   - Document findings in issue

3. **UPDATE issue during work**
   - When starting: Add `status:in-progress` label
   - During work: Comment on progress
   - Document blockers immediately
   - Document ALL attempts (including failures)

4. **REPORT completion and WAIT for approval**
   - Provide testing instructions
   - Wait for user confirmation
   - Only close after testing succeeds
   - **NEVER close issues yourself**

5. **CROSS-DOMAIN coordination**
   - Air-Side completes → Comment instructions for Ground-Side
   - Add appropriate domain labels
   - Link related issues
   - Clear handoff communication

**See:** [docs/CC_READ_THIS_FIRST.md](docs/CC_READ_THIS_FIRST.md) for complete workflow

---

## 🔧 Key Features (Current)

### Air-Side (Raspberry Pi 5)
- Sony Camera Remote SDK integration
- UDP status broadcast (9002)
- TCP command server (9001)
- Camera property control
- Focus distance reporting
- Heartbeat/telemetry

### Ground-Side (SkyDroid H16)
- Android Kotlin UI
- TCP command client
- UDP status receiver
- Real-time camera control
- Live property display
- Mission control interface

### Dev-Tools (SystemTools)
- 10-tab diagnostic GUI
- Network monitoring
- Log download (SFTP/SCP)
- Command testing
- Status visualization
- Cross-platform (Windows/Linux)

---

## 🚀 Quick Commands

```bash
# Air-Side (Pi 5 C++)
cd sbc/
./build.sh                      # Build C++ code
./run_payload_manager.sh        # Run application

# Ground-Side (Android)
cd android/
./gradlew assembleDebug         # Build APK
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb logcat -s NetworkClient     # View logs

# Dev-Tools (Python)
cd SystemTools/
python main.py                  # Launch diagnostic GUI

# GitHub Issue Management
gh issue list --state open      # View open issues
gh issue create                 # Create new issue
gh issue comment <#> --body "..." # Update issue

# Git Workflow
git pull origin main            # Session start
git status                      # Check changes
git add -A && git commit -m "[DOMAIN][TYPE] Description"
git push origin main            # Session end

# Protocol Sync
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.air_side == false) | .key'
```

---

## 📝 Important Files

**Session Start:**
- README.md - Project overview
- DPM_KEY_FACTORS.md - This file (quick reference)
- docs/CC_READ_THIS_FIRST.md - Complete session guide

**Protocol (Single Source of Truth):**
- protocol/commands.json - Command definitions
- protocol/camera_properties.json - Property specifications

**Domain Progress:**
- sbc/docs/PROGRESS_AND_TODO.md - Air-Side status
- android/docs/PROGRESS_AND_TODO.md - Ground-Side status
- SystemTools/PROGRESS_AND_TODO.md - Dev-Tools status

**Cross-Domain:**
- docs/ALL_DOMAINS/LESSONS_LEARNED.md - Historical insights
- docs/ALL_DOMAINS/MASTER_STATUS.md - Overall status
- docs/ALL_DOMAINS/WHO_TAG_GUIDE.md - WHO tag protocol

**Reference:**
- docs/AIR_SIDE/SONY_SDK_REFERENCE.md - Sony SDK quick guide
- docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/ - Full SDK docs (2000+ pages)

---

## ⚠️ Critical Information

**Sony SDK:**
- Location: `~/sony_sdk/`
- Version: v2.00.00
- Documentation: `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html`
- **ALWAYS consult SDK docs before implementing camera functions**

**Protocol Files:**
- ⚠️ Located at `protocol/` NOT `docs/protocol/`
- Single source of truth for commands and properties
- JSON format with implementation tracking
- Must sync across Air/Ground/Tools

**Network Configuration:**
- Air-Side: `192.168.x.x` (configure in SystemTools)
- TCP 9001: Commands (Ground→Air)
- UDP 9002: Status (Air→Ground)
- UDP 9003: Video stream

**Repository:**
- GitHub: https://github.com/unmanned-systems-uk/DPM-V2
- Working Directory: `/home/anthony/DPM-V2`
- Main Branch: `main`

---

## 🎓 Key Decisions & Lessons

### Technology Choices
- **Raspberry Pi 5 over Pi 4** - Better performance, 8GB RAM
- **C++17 for Air-Side** - Sony SDK native interface, performance
- **Kotlin for Ground-Side** - Modern Android development
- **Python for Dev-Tools** - Cross-platform, rapid development
- **UDP for status** - Low latency, acceptable packet loss
- **TCP for commands** - Reliability required

### Architecture Decisions
- **Three-domain separation** - Clear ownership and expertise
- **Protocol JSON as source of truth** - Prevents drift between Air/Ground
- **UDP status broadcast** - Real-time telemetry without polling
- **WHO tag system** - Clear attribution and cross-domain tracking
- **Issue-first workflow** - Complete history and coordination

### What Works Well
- WHO tag attribution
- Historical issue search
- Cross-domain coordination via issues
- Protocol JSON synchronization
- SystemTools diagnostic capabilities

### Lessons Learned (from docs/ALL_DOMAINS/LESSONS_LEARNED.md)
- Always search history before implementing
- Document failed attempts (prevent repetition)
- Cross-domain work requires explicit handoff instructions
- Protocol sync critical for Air/Ground coordination
- Testing before closure prevents rework

**See:** [docs/ALL_DOMAINS/LESSONS_LEARNED.md](docs/ALL_DOMAINS/LESSONS_LEARNED.md) for complete lessons

---

## 📚 Workflow Files

**Session Management:**
- docs/CC_READ_THIS_FIRST.md - Complete session checklist
- DPM_KEY_FACTORS.md - This file (quick reference)

**Issue Management:**
- .github/ISSUE_TEMPLATE/ - 7 comprehensive templates
  - bug_report.md
  - feature_request.md
  - cross_domain_coordination.md
  - protocol_implementation.md
  - lessons_learned.md
  - bug_report_with_history.md

**Automation:**
- .github/scripts/search-history.ps1 - Historical issue search
- .github/scripts/cc-complete-issue.ps1 - Issue completion

**Quick Session Start:**
1. User says: "Claude read README.md"
2. README tells you to read CC_READ_THIS_FIRST.md
3. Then read DPM_KEY_FACTORS.md (this file)
4. Total time: 3-5 minutes, full context loaded

---

## 🔗 Quick Links

- **Repository:** https://github.com/unmanned-systems-uk/DPM-V2
- **Issues:** https://github.com/unmanned-systems-uk/DPM-V2/issues
- **Air-Side Docs:** docs/AIR_SIDE/
- **Ground-Side Docs:** docs/GROUND_SIDE/
- **Dev-Tools Docs:** docs/DEVELOPMENT_SIDE/
- **Cross-Domain Docs:** docs/ALL_DOMAINS/
- **Sony SDK Docs:** docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/

---

## 🎯 Current Focus

**Phase 1 Active Work:**
- Sony SDK camera property implementation
- Focus distance control and reporting
- Camera property synchronization
- Protocol JSON completion

**Next Priorities:**
- Complete Phase 1 camera control
- Test comprehensive property support
- Prepare for Phase 2 planning (AI/Vision)

---

**Last Updated:** 2025-11-09
**Phase:** 1 (Sony SDK Foundation)
**Status:** In Progress
**Next:** Complete camera property implementation
