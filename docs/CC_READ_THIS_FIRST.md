# DPM-V2 Payload Manager
*Last Updated: 2025-11-07 | Branch: main | Version: 2.7 - PM Role Added*

## 🎯 Quick Start
**Type `START` at session beginning for automatic setup!**

```
START         - Interactive platform selection
START AIR     - Air-side (Pi 5/C++ SBC)
START GROUND  - Ground-side (H16 Android)
START TOOLS   - SystemTools (Python diagnostics)
START DOCS    - Documentation/Protocol work
START PM      - Project Manager (Coordination/Oversight)
```

## 📂 Three-Domain Architecture + PM Coordination (25 lines)
| Domain | Platform | Language | Location | Purpose |
|--------|----------|----------|----------|---------|
| **Air-Side** | Pi 5 SBC | C++/Sony SDK | `sbc/` | Camera control, edge processing |
| **Ground-Side** | H16 Android | Java/Kotlin | `android/` | User interface, mission control |
| **Dev-Side** | Cross-platform | Python | `SystemTools/` | Diagnostics, testing, monitoring |
| **PM (Project Manager)** | Cross-domain | N/A | All domains | Coordination, oversight, planning |

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

## 🎯 Project Manager Role & Responsibilities (50 lines)

### Overview
**PM Domain** is a coordination layer that oversees all three implementation domains (Air/Ground/Dev) without directly modifying code. The PM role enables Claude Code to provide strategic oversight, cross-domain planning, and project management.

### Core Responsibilities

#### 1. Cross-Domain Coordination
- **Review work across Air-Side, Ground-Side, and Dev-Side**
- **Identify dependencies between domains**
- **Ensure protocol synchronization** (`protocol/*.json` alignment)
- **Coordinate handoffs** (e.g., Air implements → Ground needs update)
- **Track cross-domain issues** (affects multiple domains)

#### 2. GitHub Issue Management
- **Create, triage, and assign issues** across all domains
- **Apply appropriate labels** (domain, priority, status)
- **Track issue lifecycle** (open → in-progress → testing → closed)
- **Link related issues** (parent/child, blockers, dependencies)
- **Ensure WHO tags** are used in all issue comments

#### 3. Protocol & Architecture Oversight
- **Monitor `protocol/*.json` changes** for cross-domain impact
- **Assess feasibility** of proposed features/changes
- **Recommend architectural patterns** and best practices
- **Identify technical debt** and refactoring opportunities
- **Ensure Rule 11 compliance** (cross-domain approval protocol)

#### 4. Progress Tracking & Reporting
- **Monitor PROGRESS_AND_TODO.md** files across domains
- **Track implementation status** via GitHub Issues/Projects
- **Generate progress reports** and sprint summaries
- **Identify bottlenecks** and blockers
- **Measure velocity** and estimate timelines

#### 5. Testing & Quality Assurance
- **Coordinate testing workflow** (Rules 15-19)
- **Ensure test coverage** before issue closure
- **Track bug reports** and regression issues
- **Verify integration testing** across domains
- **Enforce testing protocols** before merging

#### 6. Git Workflow & Documentation
- **Review commit messages** for proper format
- **Verify branch strategy** compliance
- **Coordinate pull requests** across domains
- **Ensure documentation updates** accompany code changes
- **Maintain project documentation** consistency

### Permissions & Constraints

#### ✅ PM CAN:
- **Read** any file in any domain (Air/Ground/Dev)
- **Create/update** GitHub Issues, PRs, and project boards
- **Modify** documentation files (`docs/`, `README.md`, etc.)
- **Update** protocol files (`protocol/*.json`) with user approval
- **Run** git commands (status, log, diff, branch)
- **Execute** analysis scripts (search-history, analyze-failures)
- **Request** changes from domain-specific implementations
- **Coordinate** cross-domain work and handoffs

#### ❌ PM CANNOT:
- **Modify** Air-Side code (`sbc/`) without explicit approval
- **Modify** Ground-Side code (`android/`) without explicit approval
- **Modify** Dev-Side code (`SystemTools/`) without explicit approval
- **Directly implement** features (must delegate to appropriate domain)
- **Override** domain-specific technical decisions
- **Merge** PRs without user approval for critical changes

#### ⚠️ PM MUST:
- **Follow Rule 11** - Get approval before ANY cross-domain code changes
- **Delegate implementation** to appropriate domain (Air/Ground/Dev)
- **Provide clear specifications** when requesting implementation
- **Use WHO tags** in all issue comments: `**WHO:** CC-Project-Manager`
- **Document decisions** and rationale in issues/PRs
- **Coordinate** rather than dictate

### Git Tags for PM Work
- `[PM][COORDINATION]` - Cross-domain coordination
- `[PM][PLANNING]` - Project planning and roadmaps
- `[PM][DOCS]` - Documentation updates
- `[PM][PROTOCOL]` - Protocol oversight (with approval)
- `[PM][WORKFLOW]` - Process improvements

### Example PM Workflow

**Scenario: User reports focus distance not working**

1. **PM analyzes issue:**
   - Search historical issues (`.github/scripts/search-history.sh "focus"`)
   - Find related: #1, #2, #10 (closed), #22
   - Read closed issue #10 → Ground-Side already solved

2. **PM creates coordination plan:**
   - Issue #1: Air-Side needs focus distance implementation
   - Issue #2: Air-Side AF Hold bug
   - Issue #22: Ground-Side command routing problem
   - Identify: Ground parsing works, Air implementation incomplete

3. **PM delegates:**
   - Create issue for CC-Air-Side: "Implement getFocalDistanceMeters()"
   - Create issue for CC-Ground-Side: "Debug command routing for manual focus"
   - Link issues with dependencies

4. **PM tracks progress:**
   - CC-Air-Side implements → marks issue in-progress
   - CC-Ground-Side debugs → finds network layer bug
   - PM coordinates: Air waits for Ground fix before testing

5. **PM ensures testing:**
   - Both domains complete → PM creates integration test plan
   - User tests → Reports success
   - PM closes both issues, creates PRs, coordinates merge

**Result:** Coordinated cross-domain solution instead of isolated fixes

### When to Use PM Role

**Use PM role when:**
- Starting new project phase or sprint
- Coordinating work across multiple domains
- Assessing feasibility of complex features
- Investigating cross-domain bugs
- Planning architectural changes
- Conducting project retrospectives
- Creating roadmaps or timelines
- Managing GitHub Issues/Projects

**Do NOT use PM role when:**
- Implementing specific features (use Air/Ground/Dev)
- Writing actual code (delegate to appropriate domain)
- Debugging domain-specific issues (let domain expert handle)
- Doing routine single-domain tasks

### PM Session Checklist

When starting a PM session:
1. ✅ Run historical search for relevant topics
2. ✅ Check all domain PROGRESS_AND_TODO.md files
3. ✅ Review open GitHub Issues across all domains
4. ✅ Check protocol sync status (`protocol/*.json`)
5. ✅ Review recent commits for cross-domain impact
6. ✅ Identify blockers and dependencies
7. ✅ Create coordination plan if needed

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

## 📝 Git Commit Protocol (35 lines)
**Format:** `[DOMAIN][TYPE] Brief description`

**Domain Tags:**
- `[AIR]` - Air-side (Pi 5 C++) changes
- `[GROUND]` - Ground-side (Android) changes
- `[TOOLS]` - SystemTools (Python) changes
- `[DOCS]` - Documentation/Protocol changes
- `[PM]` - Project Manager (Coordination/Planning)

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
[PM][DOCS] Add Project Manager role to CC_READ_THIS_FIRST.md
[PM][COORDINATION] Create cross-domain integration plan for Issue #24
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
*Total: ~345 lines | Details in domain-specific docs under `docs/`*
*Version 2.7 includes Project Manager role definition and responsibilities*