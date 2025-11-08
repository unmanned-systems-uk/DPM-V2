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

## 🚨 CRITICAL WORKFLOW RULES (MUST READ!)

**FAILURE TO FOLLOW THESE RULES BREAKS THE ENTIRE WORKFLOW:**

1. **ALWAYS search historical issues BEFORE implementing anything**
2. **ALWAYS update GitHub issues when working on them**
3. **NEVER implement without checking what was tried before**
4. **NEVER repeat failed solutions from previous issues**
5. **ALWAYS document what you tried and why it failed/succeeded**
6. **ALWAYS provide cross-domain instructions when needed**
7. **NEVER close issues without user confirmation**

**Example Workflow Failures:**
- **Issue #10:** Air/Ground didn't update GitHub = workflow breakdown
- **Focus Issues #1,#2:** Repeated same failed attempts = wasted time
- **Result: Confusion, duplicated work, repeated failures**

## 🧠 MANDATORY: Learn from History First

**BEFORE working on ANY issue, you MUST:**

```bash
# 1. Search for similar historical issues
.github\scripts\search-history.ps1 "focus"  # or relevant keyword

# 2. Read what failed before
gh issue view <#> --comments | grep -i "tried\|failed\|didn't work"

# 3. Document your approach based on history
gh issue comment <#> --body "Found previous attempts in #X and #Y:
- #X tried [approach] but failed because [reason]
- #Y tried [approach] but failed because [reason]
I will try [NEW approach] because [why it's different]"
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

#### 7. Lessons Learned & Knowledge Management
- **Maintain LESSONS_LEARNED.md** registry (`docs/ALL_DOMAINS/LESSONS_LEARNED.md`)
  - ⚠️ **IMPORTANT:** This is the ONLY lessons learned file - do NOT create duplicates in other locations
  - All domains (Air/Ground/Dev/PM) must append to this centralized file
- **Extract lessons** from closed issues (what failed, what worked, why)
- **Update after each issue closure** with key insights
- **Identify patterns** across multiple issues
- **Conduct monthly reviews** of lessons learned
- **Ensure searchability** and proper categorization
- **Link lessons** back to source issues for traceability

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
6. ✅ Review LESSONS_LEARNED.md for relevant patterns
7. ✅ Identify blockers and dependencies
8. ✅ Create coordination plan if needed

When ending a PM session (after issue closure):
1. ✅ Extract lessons from closed issues
2. ✅ Update LESSONS_LEARNED.md with new insights
3. ✅ Document what failed and what worked
4. ✅ Link lessons back to source issues
5. ✅ Update Quick Reference Index if needed

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
2. **Check Open Issues** - `gh issue list --state open` for assigned/relevant issues (CRITICAL: Don't miss domain-specific work!)
3. **Check Branch** - `git branch --show-current` (must be `main`)
4. **Pull Latest** - `git pull origin main` (check conflicts)
5. **Check Protocol Sync** - Review protocol/*.json for updates
6. **Read Progress** - Check domain-specific PROGRESS_AND_TODO.md
7. **Check Status** - `git status` for uncommitted changes

### 🔴 Air-Side Sessions MUST ALSO:
8. **Check Air-Side Issues** - `gh issue list --label air-side --state open`
9. **Review Sony SDK Reference** - `docs/AIR_SIDE/SONY_SDK_REFERENCE.md`
10. **BEFORE implementing camera function** - Check `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html`
11. **Document SDK findings** - Note function signatures, prerequisites, constraints in issue comments

### 🟢 Ground-Side Sessions MUST ALSO:
8. **Check Ground-Side Issues** - `gh issue list --label ground-side --state open`
9. **Review Android PROGRESS** - `docs/GROUND_SIDE/PROGRESS_AND_TODO.md`

### 🔵 Dev-Tools Sessions MUST ALSO:
8. **Check Dev-Tools Issues** - `gh issue list --label dev-tools --state open`
9. **Check SystemTools Version** - `SystemTools/version.py`

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

## 🏷️ WHO Tag Protocol (40 lines)

### MANDATORY: All GitHub Issue Comments Must Use WHO Tags

**Every GitHub issue comment/update MUST start with a WHO tag identifying the author:**

**Format:**
```markdown
**WHO:** CC-Air-Side
**WHO:** CC-Ground-Side
**WHO:** CC-Dev-Tools
**WHO:** CC-Project-Manager
**WHO:** User (name)
```

### Purpose
1. **Clear Attribution** - Know who worked on what and when
2. **Cross-Domain Tracking** - See when work transitions Air↔Ground↔Tools
3. **Historical Context** - Future Claude instances understand decision-making context
4. **Workflow Analysis** - Track how issues flow across domains
5. **Accountability** - Clear ownership of implementations and decisions
6. **Knowledge Transfer** - Self-documenting collaboration between sessions

### When to Use WHO Tags

**ALWAYS use WHO tags when:**
- Creating new GitHub issues
- Commenting on existing issues
- Updating issue status or progress
- Documenting implementation decisions
- Reporting test results
- Requesting cross-domain work
- Documenting failures or lessons learned

### Examples

**Good - Clear Attribution:**
```markdown
**WHO:** CC-Air-Side

Implementation complete. Air-Side changes:
- camera_sony.cpp: Added getFocalDistanceMeters()
- messages.h: Added focal_distance_meters field
- Container rebuilt and tested

Ground-Side needs to:
- Update ProtocolMessages.kt to parse focal_distance_meters field
- See android/docs/ISSUE-001-FOCAL-DISTANCE-GROUNDSIDE-FIX.md
```

**Good - Cross-Domain Handoff:**
```markdown
**WHO:** CC-Ground-Side

Air-Side implementation verified. Ground-Side testing results:
- ✅ Receiving focal_distance_meters in UDP status packets
- ✅ Parsing correctly in ProtocolMessages.kt
- ❌ UI not updating - investigating CameraViewModel.kt

Next: Fix LiveData update in CameraViewModel
```

**Good - User Input:**
```markdown
**WHO:** User (Anthony)

Testing complete. Focus distance now displays correctly on both manual and auto focus modes.

Approve closing this issue.
```

**Bad - No WHO Tag:**
```markdown
Implementation complete. Testing required.
```
*Why bad: Can't tell if this was CC-Air, CC-Ground, or User. No context for future sessions.*

### Benefits in Practice

**Without WHO tags (confusing):**
```
Comment 1: "Tried approach A, didn't work"
Comment 2: "Implemented solution B"
Comment 3: "Still not working"
```
*Who tried what? Which domain? What's the current status?*

**With WHO tags (clear):**
```
**WHO:** CC-Air-Side
Tried approach A (adding debug logging), didn't work - no logs appeared

**WHO:** CC-Ground-Side
Implemented solution B (fixed UDP parsing), ready for Air-Side testing

**WHO:** CC-Air-Side
Tested solution B - still not working. Air-Side never receives UDP packets.
Found: Network configuration issue in docker-compose.yml
```
*Clear narrative: Ground fixed parsing, but Air has network issue. Next step obvious.*

### Integration with Historical Learning (Issue #21)

WHO tags enable powerful historical search patterns:
```bash
# Find all Air-Side work on focus issues
gh issue list --search "focus WHO: CC-Air-Side" --state all

# Find User-reported bugs
gh issue list --search "WHO: User bug" --state all

# Track cross-domain coordination
gh issue view 24 --comments | grep "WHO:"
```

### Enforcement

**Issue templates** (`.github/ISSUE_TEMPLATE/`) include WHO tag fields.

**All Claude Code instances** must use WHO tags - no exceptions.

**Users** are encouraged to use WHO tags for clarity, especially when providing test results or reporting issues.

**See full guide:** `docs/ALL_DOMAINS/WHO_TAG_GUIDE.md`

## 🚀 Quick Commands (40 lines)
### Air-Side (Pi 5 SBC)
```bash
cd sbc/
./build.sh                    # Build C++ code
./run_payload_manager.sh      # Run application
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/sony_sdk/lib
```

**🔴 CRITICAL: Sony SDK API Reference**
```bash
# ALWAYS reference SDK docs when implementing camera functions:
# Location: docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html
# 2000+ pages of comprehensive API documentation

# How to use:
# 1. Open index.html in browser
# 2. Search for function/property name
# 3. Check parameters, return values, examples
# 4. Verify supported camera models
```

**See:** `docs/AIR_SIDE/SONY_SDK_REFERENCE.md` for quick guide

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

### 🚨 CRITICAL: GitHub Issue Management is MANDATORY (Updated 2025-11-06)

**⚠️ WORKFLOW FAILURE WARNING: Not updating issues BREAKS the entire development workflow!**

11. **MANDATORY Issue Updates - EVERY SESSION:**
    ```bash
    # STEP 1: Check issues at session start
    gh issue list --repo unmanned-systems-uk/DPM-V2 --state open

    # STEP 2: When working on ANY issue
    gh issue edit <number> --add-label "status:in-progress"
    gh issue comment <number> --body "Starting work on [specific task]"

    # STEP 3: When implementation complete
    gh issue comment <number> --body "Implementation complete. Testing required: [instructions]"
    gh issue edit <number> --remove-label "status:in-progress" --add-label "status:testing"

    # STEP 4: After successful test
    gh issue close <number> --comment "Fixed in commit [hash]. [What was done]"
    ```

12. **CROSS-DOMAIN Issue Protocol (MANDATORY):**
    When Air-Side fixes an issue that requires Ground-Side changes:
    ```bash
    # Air-Side MUST:
    gh issue comment <number> --body "Air-Side complete. Ground-Side needs to: [specific instructions]"
    gh issue edit <number> --add-label "ground-side" --add-label "status:needs-ground-impl"

    # Ground-Side MUST:
    gh issue comment <number> --body "Ground-Side implementation complete. [What was done]"
    gh issue edit <number> --remove-label "status:needs-ground-impl" --add-label "status:testing"
    ```

13. **Issue Update CHECKLIST (Claude Code MUST follow):**
    - [ ] Check issue status BEFORE starting work
    - [ ] Add "status:in-progress" label when starting
    - [ ] Comment what you're implementing
    - [ ] Update issue IMMEDIATELY after changes
    - [ ] Provide CLEAR testing instructions
    - [ ] Add cross-domain instructions if needed
    - [ ] Close issue ONLY after confirmed testing

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
*Total: ~469 lines | Details in domain-specific docs under `docs/`*
*Version 2.7 includes Project Manager role definition and WHO tag protocol*