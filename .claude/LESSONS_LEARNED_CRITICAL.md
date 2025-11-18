# Critical Lessons Learned - Multi-Domain Project Management

**Date:** 2025-11-18
**Context:** Long development session revealed fundamental architectural drift issues
**Severity:** 🔴 CRITICAL - Affects all future development

---

## 🚨 Problems Identified

### Problem 1: .claude Folders Not Committed
**What Happened:**
- User keeps re-approving permissions already granted
- Permissions stored in `.claude/settings.local.json`
- `.claude/` in `.gitignore` - changes not persisted

**Impact:**
- User frustration - repeated permission dialogs
- Lost configuration across sessions
- Inconsistent development environment

**Root Cause:**
- `.claude/` folders excluded from git
- No policy on what should/shouldn't be committed

---

### Problem 2: Protocol Hardcoding Violations
**What Happened:**
- Air-Side `system.get_config` returns data in one format
- SystemTools expects different format
- Air-Side says "working fine" - blames SystemTools
- **Reality:** No single source of truth for response format

**Examples:**
1. **Config Response Format:**
   - Air-Side sends: `{"payload": {"result": {"config": {...}}}}`
   - SystemTools expects: `{"payload": {"config": {...}}}`
   - **No protocol spec** defining the correct format

2. **Log Contexts:**
   - Air-Side has: CAMERA, NETWORK, COMMAND, SYSTEM, STORAGE, HEALTH
   - Ground-Side has: CAMERA, NETWORK, COMMAND, SYSTEM, STORAGE, UI
   - **Mismatch discovered** - only fixed today with protocol/log_contexts.json

**Impact:**
- Cross-domain integration failures
- Blame-shifting between domains
- Wasted debugging time

**Root Cause:**
- Hardcoded protocol structures in each domain
- No enforcement of protocol compliance
- Missing validation against protocol specs

---

### Problem 3: Lost Work - system.get_config/set_config
**What Happened:**
1. **Yesterday:** Implemented, tested, closed issues #115 & #116
2. **Today:** Code missing from Air-Side
3. **Analysis:** Implemented but never committed to git
4. **Cause:** POC image transfer reverted uncommitted work

**Timeline:**
- Issues marked CLOSED with passing tests
- Implementation existed only in running Docker container
- Source code never committed
- Container rebuilt → work lost

**Impact:**
- 4+ hours of work lost
- Had to re-implement from issue specs
- User lost confidence in development process

**Root Cause:**
- **No enforcement:** Issues closed before commits verified
- **No validation:** Closing issue doesn't check git for commits
- **No protection:** Uncommitted work vulnerable to reverts

---

### Problem 4: Sony SDK Location Ambiguity
**What Happened:**
- Air-Side tried multiple SDK paths
- Considered copying SDK into Docker container
- No clear documentation of SDK location strategy

**Observed Behavior:**
- Searching: `/home/dpm/SonySDK/...`
- Searching: `/workspace/sdk/...`
- Searching: `/app/sdk/...`
- Thinking: "Maybe I need to copy SDK..."

**Impact:**
- Wasted time searching for SDK
- Risk of duplicating large SDK files
- Confusion about build environment

**Root Cause:**
- No canonical documentation of SDK location
- No environment variable standardization
- No validation in CMakeLists.txt

---

### Problem 5: Session Drift - Rules Forgotten
**What Happened:**
- Long development sessions (8+ hours)
- Rules gradually forgotten
- Best practices erode
- Single-point-of-truth violations accumulate

**Examples:**
- Forgot to commit .claude changes
- Forgot to update protocol before implementing
- Forgot to verify commits before closing issues
- Forgot Sony SDK location conventions

**Impact:**
- Quality degradation over time
- User has to re-teach rules mid-session
- Inconsistent code quality

**Root Cause:**
- No mechanism to refresh rules during session
- Context window fills with implementation details
- Original constraints pushed out of active memory

---

## ✅ MANDATORY RULES - NON-NEGOTIABLE

### RULE 1: .claude Folder Commit Policy

**MUST commit to git:**
- `.claude/commands/` - Custom slash commands (user-created)
- `.claude/PM_*.md` - PM session rules and workflows
- `.claude/*_CRITICAL.md` - Critical documentation
- `.claude/LESSONS_LEARNED_*.md` - This file and similar

**MUST NOT commit to git:**
- `.claude/settings.local.json` - Contains user-specific paths
- `.claude/cache/` - Temporary cache files
- `.claude/tmp/` - Temporary working files

**Enforcement:**
```bash
# Add to .gitignore
.claude/settings.local.json
.claude/cache/
.claude/tmp/

# Remove blanket .claude/ exclusion
# Explicitly include important files:
!.claude/commands/
!.claude/PM_*.md
!.claude/*_CRITICAL.md
!.claude/LESSONS_LEARNED_*.md
```

**Commit Frequency:**
- After every PM session (end of day)
- After creating new slash commands
- After updating PM rules

---

### RULE 2: Single Point of Truth - Protocol Compliance

**NEVER hardcode protocol structures in domain code.**

**Process for ANY network command:**

1. **Create/Update Protocol Spec FIRST:**
   ```bash
   protocol/commands.json         # Command definitions
   protocol/log_contexts.json     # Log context definitions
   protocol/responses.json        # Response format specs
   protocol/events.json          # Event format specs
   ```

2. **Commit Protocol Change:**
   ```bash
   git commit -m "[PROTOCOL] Add system.get_config command spec"
   ```

3. **Inform PM:**
   - Post to PM session: "Protocol updated: system.get_config"
   - PM coordinates implementation across domains

4. **Implement in Each Domain:**
   - Air-Side reads protocol spec
   - Ground-Side reads protocol spec
   - SystemTools reads protocol spec
   - **ALL generate code from SAME spec**

5. **Validate Compliance:**
   - Test messages against protocol schema
   - Automated validation in CI/CD (future)

**Examples:**

❌ **WRONG - Hardcoded:**
```cpp
// Air-Side tcp_server.cpp
json response;
response["config"] = config_data;  // ← Hardcoded structure
return response;
```

✅ **CORRECT - Protocol-Driven:**
```cpp
// Air-Side tcp_server.cpp
// Read from protocol/commands.json
json spec = Protocol::getCommandSpec("system.get_config");
return Protocol::formatResponse(spec, config_data);
```

**Enforcement:**
- PM reviews all protocol changes
- No PR approval without protocol update
- Automated schema validation (future)

---

### RULE 3: Never Close Issues Before Commits

**Process for closing ANY issue:**

1. ✅ Implementation complete
2. ✅ Tests passed
3. ✅ **Code committed to git** ← VERIFY THIS
4. ✅ **Commit hash recorded in issue comment**
5. ✅ **Push to remote**
6. ✅ ONLY THEN close issue

**Verification Checklist:**
```bash
# Before closing issue #XXX, run:
git log --oneline --grep="#XXX"  # ← Should show commit
git status                        # ← Should be clean
git diff origin/main             # ← Should include changes

# If any check fails, DO NOT close issue
```

**Issue Close Template:**
```markdown
## Implementation Complete

**Commits:**
- abc1234 [AIR-SIDE][FEATURE] Implement system.get_config - Issue #115
- def5678 [AIR-SIDE][TEST] Add tests for system.get_config - Issue #115

**Verification:**
- ✅ Code committed
- ✅ Tests passed
- ✅ Pushed to origin/main
- ✅ Changes visible in git log

**Safe to close.**
```

**PM Responsibility:**
- Verify commits exist before approving issue closure
- Re-open issues if commits not found

---

### RULE 4: SDK Location - Single Source of Truth

**Canonical SDK Location Documentation:**

**File:** `sbc/docs/SDK_LOCATIONS.md`

```markdown
# Sony SDK Location Configuration

## Development Machine (Local)
- Path: ~/Sony_SDK/CrSDK_v2.00.00_20251030a_Linux64PC/
- Used for: Code analysis, testing

## Raspberry Pi 5 (Host)
- Path: /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/
- Used for: Production builds, Docker mounts

## Docker Container (Runtime)
- Mount: /workspace/sdk → /home/dpm/SonySDK/...
- CMake detects: if(EXISTS "/workspace/sdk") → use it
- Never copy SDK INTO container - always mount

## CMakeLists.txt Auto-Detection
```cpp
if(EXISTS "/workspace/sdk")
    set(SONY_SDK_ROOT "/workspace/sdk")  # Docker
elif(EXISTS "/home/dpm/SonySDK")
    set(SONY_SDK_ROOT "/home/dpm/SonySDK")  # Pi 5 host
else()
    message(FATAL_ERROR "Sony SDK not found")  # FAIL LOUDLY
endif()
```

## Never:
- ❌ Copy SDK into Docker container
- ❌ Search multiple paths at runtime
- ❌ Hard-code SDK paths in code

## Always:
- ✅ Mount SDK via Docker volume
- ✅ Use CMake auto-detection
- ✅ Fail build if SDK not found
```

**Enforcement:**
- Document in sbc/README.md
- CMake FATAL_ERROR if SDK not found
- Never proceed with missing SDK

---

### RULE 5: SOS - Sync-of-Session Command

**Purpose:** Refresh rules and mindset during long sessions without losing context

**When to use:**
- Session >4 hours
- Rules being forgotten
- Feeling "drift" from best practices
- Before major architecture decisions

**Implementation:**

**File:** `.claude/commands/sos.md`

```markdown
# SOS (Sync-of-Session) - Emergency Rules Refresh

## Execution Steps:

1. **Stash Current Work:**
   - Save current conversation state
   - Note current task and context
   - Preserve todo list

2. **Re-read Critical Rules:**
   - .claude/PM_RULES_CRITICAL.md
   - .claude/LESSONS_LEARNED_CRITICAL.md
   - protocol/ (all protocol files)
   - Current issue requirements

3. **Validate Current Work Against Rules:**
   - Are we following single-point-of-truth?
   - Have we committed .claude changes?
   - Is work committed before closing issues?
   - Are we hardcoding protocols?

4. **Resume with Refreshed Mindset:**
   - Continue current task
   - Apply rules to current work
   - Suggest corrections if violations found

## Trigger:
User types: `sos` or `SOS` or `/sos`

## Output:
- Summary of rules refreshed
- Validation of current work
- Suggestions for corrections
- Ready to continue with proper mindset
```

**User Experience:**
```
User: sos

PM: 🆘 SOS - Syncing Session Rules...

✅ Stashed current work context
✅ Re-read PM_RULES_CRITICAL.md
✅ Re-read LESSONS_LEARNED_CRITICAL.md
✅ Re-read protocol/log_contexts.json
✅ Current issue: #115 system.get_config

⚠️ Validation Check:
- Current work: Re-implementing system.get_config
- Issue #115 status: CLOSED (2025-11-16)
- Git commits: NOT FOUND ❌
- Protocol spec: EXISTS (protocol/commands.json) ✅

🔍 Violations Detected:
1. Issue closed without git commits
2. Need to verify protocol compliance

💡 Recommendations:
1. Re-implement system.get_config
2. Commit immediately after testing
3. Verify response matches protocol/commands.json
4. Update issue with commit hash

Session rules refreshed. Ready to continue with proper compliance.
```

---

## 🎯 Action Items - Immediate

### 1. Update .gitignore
```bash
# Remove blanket .claude/ exclusion
# Add specific exclusions:
.claude/settings.local.json
.claude/cache/
.claude/tmp/

# Explicitly include:
!.claude/commands/
!.claude/PM_*.md
!.claude/*_CRITICAL.md
!.claude/LESSONS_LEARNED_*.md
```

### 2. Create Protocol Files
- ✅ protocol/log_contexts.json (DONE)
- ⏳ protocol/commands.json (UPDATE with system.get_config spec)
- ⏳ protocol/responses.json (CREATE response format specs)

### 3. Create SDK Location Docs
- ⏳ sbc/docs/SDK_LOCATIONS.md
- ⏳ Update sbc/README.md with SDK requirements
- ⏳ Update CMakeLists.txt with FATAL_ERROR on missing SDK

### 4. Implement SOS Command
- ⏳ .claude/commands/sos.md
- ⏳ Test SOS functionality
- ⏳ Add to PM_RULES_CRITICAL.md

### 5. Audit Current Work
- ⏳ Check Air-Side for protocol violations
- ⏳ Check SystemTools for hardcoded structures
- ⏳ Verify all closed issues have commits

---

## 💭 Suggest for Claude Project Memory

**The following principles should be added to Claude Project Memory:**

1. **"NEVER close issues before verifying git commits exist"**
   - Check git log before closing
   - Record commit hash in issue

2. **"ALWAYS update protocol JSON before implementing network commands"**
   - protocol/commands.json is single source of truth
   - Coordinate via PM for cross-domain changes

3. **".claude/ folder commit policy - commit PM rules, NOT settings.local.json"**
   - Prevents permission re-approval issues
   - Preserves project knowledge

4. **"Sony SDK location is ALWAYS /workspace/sdk in Docker, /home/dpm/SonySDK on Pi 5"**
   - Never search multiple paths
   - Never copy SDK into container
   - CMake FATAL_ERROR if not found

5. **"Use 'sos' command when session >4 hours to refresh rules"**
   - Prevents architectural drift
   - Maintains code quality

---

## 📚 Related Documentation

- `.claude/PM_RULES_CRITICAL.md` - PM session rules
- `protocol/log_contexts.json` - Log context definitions
- `protocol/commands.json` - Command protocol specs
- `sbc/docs/SDK_LOCATIONS.md` - Sony SDK location guide

---

**This document is a living record. Update when new lessons are learned.**

**Last Updated:** 2025-11-18
**Next Review:** After each PM session
