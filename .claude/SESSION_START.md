# DPM-V2 Session Start Guide

**WHO:** CC-Project-Manager
**Purpose:** Quick context loading for Claude Code sessions
**Read this:** At the start of EVERY DPM-V2 session

---

## 📋 Session Start Checklist (3-5 minutes)

### 1. Confirm Location ✅
```bash
pwd
# Should be: /home/anthony/DPM-V2
```

### 2. Read Key Context
- ✅ You've already read README.md (user told you to)
- ✅ You've already read this file (SESSION_START.md)
- ✅ Now read: DPM_KEY_FACTORS.md (quick reference)
- ✅ Then read: docs/CC_READ_THIS_FIRST.md (complete session guide)

### 3. Check Current Status
```bash
# Check git status
git status

# Check open issues
gh issue list --repo unmanned-systems-uk/DPM-V2 --state open

# Check issues in progress from last session
gh issue list --label status:in-progress --state open --repo unmanned-systems-uk/DPM-V2

# Check completed issues awaiting closure
gh issue list --label status:complete --state open --repo unmanned-systems-uk/DPM-V2

# Check recent commits
git log --oneline -5
```

**⚠️ If you see issues with `status:in-progress` label:**
- These are works-in-progress from previous session
- Resume these first before starting new work
- Check issue comments for latest status

**⚠️ If you see issues with `status:complete` label:**
- These are done but waiting for user approval to close
- Review and ask user if ready to close

### 4. Identify Your Domain
DPM-V2 has a **three-domain + PM architecture:**

**Which domain are you working in today?**

- **Air-Side** (CC-Air-Side)
  - Raspberry Pi 5 C++ code
  - Sony SDK camera control
  - Location: `sbc/`
  - Docs: `docs/AIR_SIDE/`

- **Ground-Side** (CC-Ground-Side)
  - SkyDroid H16 Android app
  - Kotlin UI code
  - Location: `android/`
  - Docs: `docs/GROUND_SIDE/`

- **Dev-Tools** (CC-Dev-Tools)
  - SystemTools Python diagnostics
  - Location: `SystemTools/`
  - Docs: `docs/DEVELOPMENT_SIDE/`

- **Project Manager** (CC-Project-Manager)
  - Cross-domain coordination
  - GitHub issue management
  - Documentation updates
  - Docs: `docs/ALL_DOMAINS/`

### 5. Check Day of Week (Architecture Updates)

**📅 Mid-Week Update (Wednesday):**
- ⚠️ Mid-week architecture update due today
- Quick status refresh required (15-30 min)
- Update domain CURRENT_STATUS.md before starting new work
- See Issue #62 for details

**📅 End-of-Week Update (Friday):**
- ⚠️ End-of-week comprehensive update due today
- Full architecture documentation review (45-90 min)
- Update architecture docs, progress docs, lessons learned
- See Issue #62 for complete checklist

**If today is Wednesday or Friday:**
```bash
# Check current day
date +%A

# If Wednesday - quick update needed
# If Friday - comprehensive update needed
```

### 6. Mandatory Workflows ⚠️

**Issue-First Workflow (MANDATORY):**
- ❌ **NEVER start work without a GitHub issue**
- ✅ **Check if issue exists first**
- ✅ **Create issue if none exists**
- ✅ **Comment when starting work** (with WHO tag)
- ✅ **Update progress during work**
- ✅ **Never close issues** (user closes them)

**Historical Search (MANDATORY - CRITICAL!):**
- ❌ **NEVER implement new features without searching history**
- ✅ **Search past issues for similar work**
- ✅ **Learn from past successes and failures**
- ✅ **Document findings in issue comments**
- ✅ **Avoid repeating failed approaches**

```bash
# Search for similar past work
.github/scripts/search-history.ps1 "focus"  # Windows
# OR
gh issue list --repo unmanned-systems-uk/DPM-V2 \
  --search "[keywords]" --state all        # Linux

# Read relevant issues
gh issue view [number] --repo unmanned-systems-uk/DPM-V2
```

**WHO Tags (MANDATORY):**
All work must be attributed with WHO tags:
- **CC-Air-Side** - Pi 5 C++ camera control
- **CC-Ground-Side** - H16 Android UI
- **CC-Dev-Tools** - SystemTools diagnostics
- **CC-Project-Manager** - PM coordination
- **User (Anthony)** - User requests/approvals

**Example:**
```markdown
**WHO:** CC-Air-Side

Implemented getFocalDistanceMeters() function.
Air-Side changes complete.

Ground-Side needs to:
- Update ProtocolMessages.kt to parse focal_distance_meters
- See android/docs/ISSUE-001-FOCAL-DISTANCE-GROUNDSIDE-FIX.md
```

**Read full workflow:** [docs/ALL_DOMAINS/WHO_TAG_GUIDE.md](../docs/ALL_DOMAINS/WHO_TAG_GUIDE.md)

---

## 🎯 Domain-Specific Checklists

### Air-Side (CC-Air-Side) Sessions

```bash
# 1. Check Air-Side issues
gh issue list --label air-side --state open

# 2. Review Sony SDK reference
# docs/AIR_SIDE/SONY_SDK_REFERENCE.md
# docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html

# 3. Check protocol sync
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.air_side == false) | .key'

# 4. Check Air-Side progress
cat sbc/docs/PROGRESS_AND_TODO.md

# 5. Verify environment
cd sbc/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/sony_sdk/lib
```

**⚠️ CRITICAL for Air-Side:**
- **ALWAYS consult Sony SDK docs before implementing camera functions**
- SDK location: `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html`
- 2000+ pages of comprehensive API documentation
- Check function signatures, parameters, return values
- Verify supported camera models

---

### Ground-Side (CC-Ground-Side) Sessions

```bash
# 1. Check Ground-Side issues
gh issue list --label ground-side --state open

# 2. Check protocol sync
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.ground_side == false) | .key'

# 3. Check Ground-Side progress
cat android/docs/PROGRESS_AND_TODO.md

# 4. Check for Air-Side handoffs
gh issue list --label "status:needs-ground-impl" --state open

# 5. Prepare Android environment
cd android/
```

**Key Focus:**
- TCP command transmission (Port 9001)
- UDP status reception (Port 9002)
- UI updates and LiveData
- Kotlin coroutines for async operations

---

### Dev-Tools (CC-Dev-Tools) Sessions

```bash
# 1. Check Dev-Tools issues
gh issue list --label dev-tools --state open

# 2. Check SystemTools version
cat SystemTools/version.py

# 3. Check progress
cat SystemTools/PROGRESS_AND_TODO.md

# 4. Prepare Python environment
cd SystemTools/
python --version  # Should be 3.8+
```

**Key Focus:**
- Network diagnostics
- Log download (SFTP/SCP)
- Command testing
- Status visualization
- Cross-platform compatibility

---

### Project Manager (CC-Project-Manager) Sessions

```bash
# 1. Check ALL open issues
gh issue list --state open

# 2. Check for issue overlap (consolidation check)
gh issue list --state open --limit 50

# 3. Check for lessons-learned issues
gh issue list --label lessons-learned --state open

# 4. Review all domain progress
cat sbc/docs/PROGRESS_AND_TODO.md
cat android/docs/PROGRESS_AND_TODO.md
cat SystemTools/PROGRESS_AND_TODO.md

# 5. Check protocol sync across domains
cat protocol/commands.json | jq '.commands'

# 6. Review lessons learned
cat docs/ALL_DOMAINS/LESSONS_LEARNED.md

# 7. Review master status
cat docs/ALL_DOMAINS/MASTER_STATUS.md
```

**PM Responsibilities:**
- Cross-domain coordination
- GitHub issue management
- Protocol synchronization oversight
- Progress tracking and reporting
- Testing coordination
- Lessons learned extraction
- CCPM feedback (Issue #69)

**PM Must:**
- Check for duplicate/overlapping issues
- Process lessons-learned issues
- Forward validated lessons to CCPM
- Coordinate cross-domain handoffs
- Update LESSONS_LEARNED.md after issue closures

---

## ✅ After Reading This

You now have full context for DPM-V2 work:
- ✅ Location confirmed
- ✅ Domain identified
- ✅ Current status known
- ✅ Mandatory workflows understood
- ✅ WHO tags memorized
- ✅ Ready to work!

**Remember:**
- **Always search historical issues before implementing**
- **Never start work without an issue**
- **Never close issues** (user closes them)
- **Always use WHO tags**
- **Coordinate across domains for cross-cutting work**

---

## 🚀 Quick Reference Commands

**Session Start:**
```bash
pwd                              # Confirm location
git status                       # Check current state
git pull origin main             # Get latest changes
gh issue list --state open       # View open issues
```

**During Work:**
```bash
# Start work on issue (change title AND label immediately)
gh issue edit <#> --title "[FIXING] Issue title" --add-label "status:in-progress"
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nStarting work on [task]"

# Update progress
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nProgress update: [status]"

# Complete work (AI suggests change to complete)
gh issue comment <#> --body "**WHO:** CC-[Domain]\n\nImplementation complete. Testing:\n✅ AI testing: Complete\n✅ User testing: [status]\n\nSuggestion: Change to [FIXED] + status:complete?"

# After user confirms (change title AND label)
gh issue edit <#> --title "[FIXED] Issue title" --add-label "status:complete" --remove-label "status:in-progress"
```

**Session End:**
```bash
git add -A
git commit -m "[DOMAIN][TYPE] Description"
git push origin main
```

**Cross-Domain Handoff:**
```bash
gh issue comment <#> --body "**WHO:** CC-Air-Side\n\nAir-Side complete. Ground-Side needs to: [specific instructions]"
gh issue edit <#> --add-label "ground-side" --add-label "status:needs-ground-impl"
```

---

## 🚪 Exit Protocol

**When user types "EXIT":**

1. **Identify yourself with WHO tag:**
   ```markdown
   **WHO:** CC-[Your-Domain]

   Are you sure you want to exit?
   ```

2. **Check Day of Week (Architecture Updates):**
   ```markdown
   ⚠️ Checking if architecture updates are due...

   **If Wednesday:**
   Mid-week architecture update is due today. Have you updated:
   - ✅ Domain CURRENT_STATUS.md?
   - ✅ MASTER_STATUS.md?

   This is a 15-30 min task. Should I help with the update before exiting?
   See Issue #62 for details.

   **If Friday:**
   End-of-week comprehensive architecture documentation is due today. Have you completed:
   - ✅ Architecture documentation review?
   - ✅ Progress documentation updates?
   - ✅ Lessons learned capture?
   - ✅ MASTER_STATUS.md full refresh?

   This is a 45-90 min task. Should I help with the update before exiting?
   See Issue #62 for complete checklist.
   ```

3. **Check EOD (End of Day) status:**
   ```markdown
   ⚠️ We have not run EOD (End of Day) yet.

   EOD workflow captures:
   - What worked well today
   - What didn't work (blockers, errors, challenges)
   - Lessons learned
   - Process improvements
   - Cross-domain coordination notes

   **EOD must run first before exiting.**

   Should I run EOD now?
   ```

4. **Wait for user confirmation:**
   - **"Yes, run EOD"** → Execute EOD workflow, capture lessons, then exit
   - **"Skip EOD"** → Ask again: "Are you certain? Lessons may be lost."
   - **"Cancel"** → Continue working (don't exit)

**Why EOD is mandatory:**
- Captures operational insights for future sessions
- Updates LESSONS_LEARNED.md
- Prevents loss of valuable domain-specific knowledge
- Tracks cross-domain coordination
- Creates lessons-learned GitHub issue

---

**Session Start Complete!** Ready for productive work.

**Next:** User will tell you which domain to work in and what task to tackle.
