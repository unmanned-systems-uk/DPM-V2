# Multi-Domain Coordination Framework
**WHO:** CC-PM (Project Manager)
**Created:** 2025-11-13
**Purpose:** Parallel multi-domain execution with PM oversight

---

## 🎯 Coordination Model

```
┌─────────────────────────────────────────────────────────┐
│                    CC-PM (Coordinator)                   │
│  - Issues setup                                          │
│  - Monitors all domains                                  │
│  - Integration testing                                   │
│  - Conflict resolution                                   │
└─────────────────────────────────────────────────────────┘
           │                │                │
    ┌──────▼─────┐   ┌─────▼──────┐   ┌────▼─────┐
    │ CC-Air-Side│   │ CC-Ground  │   │CC-System │
    │            │   │   -Side    │   │  Tools   │
    │ Issue #72  │   │ Issue #73  │   │Issue #74 │
    │            │   │            │   │          │
    │Independent │   │Independent │   │Independent│
    │ Execution  │   │ Execution  │   │ Execution │
    └────────────┘   └────────────┘   └──────────┘
           │                │                │
           └────────────────┴────────────────┘
                           │
                    User Monitors
                  (Can help any domain)
```

---

## 📋 PM Responsibilities

### Pre-Flight (Setup Phase)
- ✅ **Verify tmux sessions active** (Air-Side-PI, Ground-Side, SystemTools)
- ✅ Create/update domain issues with clear requirements
- ✅ Define success criteria for each domain
- ✅ Identify dependencies between domains
- ✅ Set up branching strategy
- ✅ Create monitoring checkpoints
- ✅ Prepare integration test plan
- ✅ **Use Task agents for complex setup** (compliance checks, issue analysis)

### In-Flight (Execution Phase)
- 🔄 **Monitor tmux sessions for real-time progress** (every 15-30 min)
- 🔄 **Use Task agents for monitoring** (domain progress checks, log analysis)
- 🔄 Monitor issue updates from all domains
- 🔄 Check for merge conflicts
- 🔄 Coordinate dependency handoffs
- 🔄 Answer domain questions
- 🔄 Track overall progress

### Post-Flight (Integration Phase)
- ✅ Review all domain PRs
- ✅ Merge in correct order
- ✅ Run integration tests
- ✅ Document results
- ✅ Close parent issue

---

## 📊 Domain Status Tracking

### Current Status (2025-11-13)

| Domain | Issue | Status | Progress | Blockers | Next Step |
|--------|-------|--------|----------|----------|-----------|
| Air-Side | #72 | in-progress | 95% | None | Testing validation |
| Ground-Side | #73 | todo | 40% | None | Health Dashboard UI |
| SystemTools | #74 | testing | 100% | None | Integration tests |

---

## 🚀 Domain Launch Checklist

### Before Starting Any Domain Session:

**PM Verifies:**
- [ ] Issue has clear requirements
- [ ] Success criteria defined
- [ ] Dependencies documented
- [ ] Branch name specified
- [ ] Test plan exists
- [ ] WHO tag in issue title

**Domain Requirements:**
- [ ] `.claude/instructions/{domain}.md` exists
- [ ] Issue assigned to domain
- [ ] No blockers listed
- [ ] Related issues linked

---

## 📝 Communication Protocol

### Issue Updates (Required)

**Each domain MUST update their issue:**
- **Start:** "Starting work on [component]"
- **Progress:** Every significant milestone (25%, 50%, 75%)
- **Blocked:** Immediately if blocked
- **Complete:** "Implementation complete, ready for review"

**Format:**
```markdown
**WHO:** CC-{Domain}
**Progress:** XX%
**Status:** [Working on | Blocked | Complete]
**Completed:** [List of completed items]
**Next:** [What's next]
**Blockers:** [Any blockers or NONE]
**ETA:** [Estimated completion]
```

### PM Monitoring

**PM checks every domain issue:**
- Every 30 minutes during active work
- Immediately on "Blocked" status
- On completion notification

---

## 🔀 Branching Strategy

### Branch Naming Convention

```bash
# Air-Side
feature/phase1-air-side-{component}
# Example: feature/phase1-air-side-testing

# Ground-Side
feature/phase1-ground-side-{component}
# Example: feature/phase1-ground-side-health-dashboard

# SystemTools
feature/phase1-systemtools-{component}
# Example: feature/phase1-systemtools-integration
```

### Workflow

```bash
# Domain creates branch
git checkout -b feature/phase1-{domain}-{component}

# Work, commit, push
git add .
git commit -m "[{DOMAIN}] Component implementation"
git push origin feature/phase1-{domain}-{component}

# Create PR (DO NOT MERGE)
gh pr create --title "[{DOMAIN}] Phase 1: {Component}" \
  --body "Closes #{issue}" \
  --label "{domain},phase-1"

# Update issue with PR link
# Wait for PM review and merge
```

---

## ⚠️ Conflict Resolution

### If Domain Gets Blocked:

1. **Update issue immediately:**
   ```markdown
   **WHO:** CC-{Domain}
   **Status:** 🚫 BLOCKED
   **Blocker:** [Describe blocker]
   **Need:** [What's needed to unblock]
   ```

2. **Tag PM in comment:**
   ```
   @CC-PM - Blocked on [issue]. Need [help/decision/resource].
   ```

3. **PM responds within 15 minutes** (during active session)

### If Domains Conflict:

**PM Coordinates:**
- Identify conflict (file, approach, dependency)
- Call coordination meeting (all domains + user)
- Make decision
- Document in parent issue
- Update affected domain issues

---

## 📊 Progress Dashboard

### PM Creates Real-Time View

**In Parent Issue (#69):**
```markdown
## Multi-Domain Progress Dashboard
**Last Updated:** [Timestamp] by CC-PM

| Domain | Status | Branch | PR | Progress | ETA |
|--------|--------|--------|----|---------|----|
| Air-Side | 🟢 Working | feature/phase1-air-testing | #XX | 95% | 1hr |
| Ground-Side | 🟡 Starting | feature/phase1-ground-health | - | 40% | 4hr |
| SystemTools | 🟢 Complete | feature/phase1-systemtools | #XX | 100% | Done |

**Overall:** 78% complete
**Blockers:** None
**Next Milestone:** Ground-Side Health Dashboard complete
```

---

## 🧪 Integration Testing Protocol

### When All Domains Report "Complete"

**PM Executes:**

1. **Review all PRs**
   ```bash
   gh pr list --label "phase-1" --state open
   ```

2. **Merge in dependency order**
   ```bash
   # Order matters!
   # 1. Air-Side (no dependencies)
   gh pr merge {air-pr} --squash

   # 2. SystemTools (depends on Air log format)
   gh pr merge {systemtools-pr} --squash

   # 3. Ground-Side (depends on Air health format)
   gh pr merge {ground-pr} --squash
   ```

3. **Pull latest and rebuild**
   ```bash
   git pull
   # Rebuild Air-Side Docker
   ssh dpm@10.0.1.53 "cd ~/DPM-V2 && git pull && cd sbc && ./build_container.sh"
   ```

4. **Run integration tests** (Issue #82)
   ```bash
   # Execute comprehensive test suite
   # Document results in Issue #82
   ```

5. **Update parent issue** (#69)
   ```markdown
   **WHO:** CC-PM
   **Status:** ✅ Phase 1 COMPLETE
   **Integration Tests:** XX/33 PASSED
   **Final Report:** [Link to #82]
   ```

---

## 📁 Domain-Specific Instructions

Each domain has detailed instructions in:
- `.claude/instructions/air-side.md`
- `.claude/instructions/ground-side.md`
- `.claude/instructions/systemtools.md`

These files contain:
- Domain-specific setup
- Code standards
- Testing requirements
- Common issues and solutions

---

## 🎯 Success Criteria for Multi-Domain Coordination

**Process Success:**
- ✅ All domains work independently
- ✅ No blocking conflicts
- ✅ PM coordinates smoothly
- ✅ User only monitors (minimal intervention)
- ✅ Faster than sequential execution

**Technical Success:**
- ✅ All domain implementations complete
- ✅ Integration tests pass
- ✅ No regression bugs
- ✅ Clean Git history
- ✅ Documentation complete

---

## 📞 User Role

**User Monitors:**
- Issue updates from all domains
- PM coordination actions
- Overall progress

**User Intervenes Only When:**
- Physical device access needed (H16 button press, Pi 5 reboot)
- Major decision required (architecture change, scope change)
- Conflict PM cannot resolve
- Any domain requests user input

**User Can:**
- Ask for status update: "PM, give me overall status"
- Check specific domain: "What's Ground-Side progress?"
- Request priority change: "Focus on {domain} first"
- Stop/start any domain: "Pause Air-Side, continue Ground-Side"

---

## 🔄 Handoff Protocol

### Between Domains

**If Domain A depends on Domain B:**

1. **Domain B completes component**
2. **Domain B updates issue:**
   ```markdown
   Component X complete - ready for Domain A integration
   **API:** [Document interface]
   **Testing:** [How to verify]
   ```
3. **PM notifies Domain A:**
   ```markdown
   @CC-Domain-A: Domain B completed component X.
   You can now integrate. See Domain B issue for API details.
   ```

### User to PM

**User signals:**
```
"All domains ready - integrate and test"
```

**PM executes:**
- Integration protocol (above)
- Reports results
- Closes parent issue

---

## 📊 Monitoring Dashboards

### PM Real-Time tmux Monitoring (Every 15-30 Minutes):

```bash
# Verify all sessions active
tmux list-sessions
# Expected: Air-Side-PI, Ground-Side, SystemTools

# Monitor Ground-Side progress (Android)
tmux capture-pane -t Ground-Side -p | tail -30

# Monitor Air-Side progress (Pi 5)
tmux capture-pane -t Air-Side-PI -p | tail -30

# Monitor SystemTools progress (Python)
tmux capture-pane -t SystemTools -p | tail -30

# Check for errors across all domains
tmux capture-pane -t Ground-Side -p | grep -E "(ERROR|FAIL|✗)"
tmux capture-pane -t Air-Side-PI -p | grep -E "(ERROR|FAIL|✗)"
tmux capture-pane -t SystemTools -p | grep -E "(ERROR|FAIL|✗)"

# Check for completions
tmux capture-pane -t Ground-Side -p | grep -E "(✓|✅|Complete)"
tmux capture-pane -t Air-Side-PI -p | grep -E "(✓|✅|Complete)"
tmux capture-pane -t SystemTools -p | grep -E "(✓|✅|Complete)"
```

### PM GitHub Monitoring (Every 30 Minutes):

```bash
# Quick status check
gh issue list --label "phase-1" --json number,title,labels,updatedAt \
  --jq '.[] | {issue: .number, status: [.labels[] | select(.name | startswith("status:")) | .name][0], updated: .updatedAt}'

# Check for blockers
gh issue list --label "status:blocked" --state open

# Check PR status
gh pr list --label "phase-1" --state open
```

### PM Reports to User:

**Format:**
```markdown
**PM Status Update** - [Time]

🟢 Air-Side: 95% - Testing validation
🟡 Ground-Side: 40% - Starting Health Dashboard
🟢 SystemTools: 100% - Complete, awaiting integration

**Overall:** 78% complete
**Blockers:** None
**ETA:** 4 hours (Ground-Side Health Dashboard)
```

---

## 🎯 Next Session Setup

**For completing Phase 1:**

1. **PM updates Issue #73** with Health Dashboard requirements
2. **PM creates branch:** `feature/phase1-ground-health`
3. **User starts Ground-Side:** "START GROUND-SIDE - Issue #73"
4. **PM monitors** Ground-Side progress
5. **When complete:** PM integrates and tests

**Parallel execution possible if other work identified.**

---

**This framework enables:**
- ✅ Fast parallel execution
- ✅ Clear ownership per domain
- ✅ PM coordination overhead
- ✅ User monitoring only
- ✅ Clean Git workflow
- ✅ Reduced context switching

---

## 🚀 Efficiency Multipliers

**All domains should exploit Task agents aggressively!**

See **`docs/ALL_DOMAINS/TASK_AGENT_USAGE_GUIDE.md`** for:
- When to spawn Task agents (multi-step work, parallel opportunities, >5k token operations)
- Domain-specific examples (Air-Side C++, Ground-Side Kotlin, SystemTools Python, PM)
- Parallel execution strategies
- Context preservation techniques

**Key principle:** Default to "Should I use a Task agent?" not "Can I do this manually?"

---

**Ready to implement for Phase 1 completion and all future multi-domain work!**
