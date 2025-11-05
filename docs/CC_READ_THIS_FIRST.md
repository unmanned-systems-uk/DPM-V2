# DPM-V2 Payload Manager
*Last Updated: 2025-11-04 | Branch: main | Version: 2.6*

## 🎯 Quick Start
**Type `START` at session beginning for automatic setup!**

```
START         - Interactive platform selection
START AIR     - Air-side (Pi 5/C++ SBC)
START GROUND  - Ground-side (H16 Android)
START TOOLS   - SystemTools (Python diagnostics)
START DOCS    - Documentation/Protocol work
```

## 📂 Three-Domain Architecture (20 lines)
| Domain | Platform | Language | Location | Purpose |
|--------|----------|----------|----------|---------|
| **Air-Side** | Pi 5 SBC | C++/Sony SDK | `sbc/` | Camera control, edge processing |
| **Ground-Side** | H16 Android | Java/Kotlin | `android/` | User interface, mission control |
| **Dev-Side** | Cross-platform | Python | `SystemTools/` | Diagnostics, testing, monitoring |

## 🗂️ Critical Paths (30 lines)
```
DPM-V2/
├── protocol/              # ⚠️ PROTOCOL SPECS (JSON) - Single source of truth
│   ├── commands.json      # Command definitions
│   └── camera_properties.json  # Camera property specs
├── sbc/                   # AIR-SIDE: Pi 5 C++ implementation
│   ├── src/               # C++ source code
│   └── docs/PROGRESS_AND_TODO.md
├── android/               # GROUND-SIDE: H16 Android app
│   ├── app/src/           # Kotlin source
│   └── docs/PROGRESS_AND_TODO.md
├── SystemTools/           # DEV-SIDE: Python diagnostic tools
│   ├── main.py            # Entry point
│   └── PROGRESS_AND_TODO.md
└── docs/                  # Documentation (not protocol!)
    ├── ALL_DOMAINS/       # Cross-domain docs
    ├── AIR_SIDE/          # Air-specific docs
    ├── GROUND_SIDE/       # Ground-specific docs
    └── DEVELOPMENT_SIDE/  # Tool docs
```

## 🔌 Network Configuration (20 lines)
| Service | Protocol | Port | Direction | Purpose |
|---------|----------|------|-----------|---------|
| Commands | TCP | 9001 | Ground→Air | Control commands |
| Status | UDP | 9002 | Air→Ground | Telemetry/heartbeat |
| Video | UDP | 9003 | Air→Ground | Live stream |
| SSH | TCP | 22 | Dev→Air | Remote access |

**Air-Side (Pi 5)**: `192.168.x.x` (configure in SystemTools)
**Ground-Side (H16)**: Android device via ADB or network

## ✅ Session Checklist (40 lines)
### Every Session MUST:
1. **Identify Platform** - Claude asks which domain
2. **Check Branch** - `git branch --show-current` (must be `main`)
3. **Pull Latest** - `git pull origin main` (check conflicts)
4. **Check Protocol Sync** - Review protocol/*.json for updates
5. **Read Progress** - Check domain-specific PROGRESS_AND_TODO.md
6. **Check Status** - `git status` for uncommitted changes

### Protocol Sync Commands:
```bash
# Check unimplemented air-side items
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.air_side == false) | .key'

# Check unimplemented ground-side items
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.ground_side == false) | .key'
```

## 📝 Git Commit Protocol (30 lines)
**Format:** `[DOMAIN][TYPE] Brief description`

**Domain Tags:**
- `[AIR]` - Air-side (Pi 5 C++) changes
- `[GROUND]` - Ground-side (Android) changes
- `[TOOLS]` - SystemTools (Python) changes
- `[DOCS]` - Documentation/Protocol changes

**Type Tags:**
- `[FEATURE]` - New functionality
- `[FIX]` - Bug fix
- `[PROTOCOL]` - Protocol implementation
- `[WIP]` - Work in progress

**Example:**
```
[AIR][PROTOCOL] Implement shutter_speed property via Sony SDK
[GROUND][FEATURE] Add gimbal control UI to camera screen
[TOOLS][FIX] Resolve UDP timeout in diagnostic panel
```

## 🚀 Quick Commands (40 lines)
### Air-Side (Pi 5 SBC)
```bash
cd sbc/
./build.sh                    # Build C++ code
./run_payload_manager.sh      # Run application
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/sony_sdk/lib
```

### Ground-Side (H16 Android)
```bash
cd android/
./gradlew assembleDebug       # Build APK
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb logcat -s NetworkClient
```

### Dev-Side (SystemTools)
```bash
cd SystemTools/
python main.py                # Launch diagnostic GUI
# 10 functional tabs for monitoring/control
```

### Git Workflow
```bash
git pull origin main          # Start of session
git add -A                    # Stage changes
git commit -m "[DOMAIN][TYPE] Description"
git push origin main          # End of session
```

---
## 📋 Key Rules (30 lines)
1. **Protocol files at `protocol/` NOT `docs/protocol/`**
2. **Never hard-code camera properties - use JSON specs**
3. **Update PROGRESS_AND_TODO.md after significant changes**
4. **Commit every 30-60 minutes or functional unit**
5. **One command/property implementation at a time**
6. **Test thoroughly before marking "implemented"**
7. **Cross-domain changes need separate commits**
8. **Create Git branch for any major or risky changes, test then merge**
9. **SystemTools: ALWAYS chain callbacks, never replace** (see DEVELOPMENT_SIDE/DEVTOOLS_MODE_GUIDE.md)
10. **Cross-domain commits need implementation instructions** (see GIT_PROTOCOL_GUIDE.md)
11. **Do not modify any code in a Domain you are not assigned to. If you feel this is necessary you must get user approval**

### 🚀 NEW GitHub-Based Project Management (Added 2025-11-05)
11. **GitHub Issues = Primary Task Tracking**
    - All tasks tracked as GitHub Issues with labels
    - Use `gh` CLI for creating/updating issues
    - GitKraken for visual project monitoring
12. **Claude Code GitHub Workflow:**
    ```bash
    # Start session
    .github\scripts\cc-start-session.ps1

    # Work on issue
    .github\scripts\cc-work-on-issue.ps1 123

    # Complete issue
    .github\scripts\cc-complete-issue.ps1 123
    ```
13. **Issue Labels:**
    - Domain: `air-side`, `ground-side`, `dev-tools`
    - Priority: `priority:critical/high/medium/low`
    - Status: `status:in-progress/blocked/testing`
14. **Documentation Now Secondary:**
    - Markdown files for context/history only
    - GitHub Issues for active task management
    - Progress reports auto-generated from GitHub

### 🧪 CRITICAL: Testing & Issue Closure Workflow (Added 2025-11-05)
15. **After Implementing ANY Feature:**
    - CC MUST provide clear testing instructions
    - Include exact commands/steps for user to verify
    - Specify expected vs actual behavior
16. **Testing Verification Protocol:**
    - After implementation, CC asks: "Please test using: [specific instructions]"
    - User tests and reports: "Testing successful" or "Issues found: [details]"
    - If issues found, CC fixes and requests retest
17. **Issue Closure Process:**
    - Only after successful test, CC asks: "Testing successful? Should I close issue #X?"
    - If YES: Run `.github\scripts\cc-complete-issue.ps1 X`
    - Creates PR automatically linked to issue
18. **Merge to Main Protocol:**
    - CC asks: "Ready to merge PR #Y to main branch?"
    - If YES: CC provides merge command or user merges via GitHub/GitKraken
    - If NO: Leave PR open for review
19. **Complete Workflow Example:**
    ```
    CC: "Feature implemented. Please test by running: python main.py"
    User: "Test successful"
    CC: "Great! Should I close issue #4?"
    User: "Yes"
    CC: [Runs cc-complete-issue.ps1 4, creates PR]
    CC: "PR #5 created. Ready to merge to main?"
    User: "Yes"
    CC: [Merges or provides merge instructions]
    ```

---
*Total: ~260 lines | Details in domain-specific docs under `docs/`*