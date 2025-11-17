# PM End of Day (EOD) Tasks

**Purpose:** Daily checklist for PM session closure to ensure proper tracking and documentation

**When to Execute:** At the end of each PM work session with significant changes

---

## 📋 PM EOD Checklist

### 1. Issue Management ✅

**Review and Update:**
- [ ] Close verified/completed issues with final comments
- [ ] Update in-progress issues with current status
- [ ] Link related issues in comments
- [ ] Verify issue labels are correct
- [ ] Check for blocked issues that need attention

**Commands:**
```bash
# List open issues
gh issue list --state open

# Close completed issue with comment
gh issue close <number> --comment "✅ COMPLETE - Brief summary"

# Update issue status
gh issue comment <number> --body "Status update: ..."
```

---

### 2. MASTER Functionality Tracker (Issue #128) ✅

**Update System Capability List:**

**When to Update:**
- New feature implementation complete
- Issue closure that adds functionality
- Integration testing reveals new capabilities
- Bug fix that restores broken functionality
- Architecture changes affecting capabilities

**Update Steps:**
1. Open Issue #128: `gh issue view 128`
2. Review today's completed work
3. Add new capabilities to appropriate domain section
4. Update capability status (✅ complete, ⏳ in progress, ❌ broken)
5. Update "Current Status Summary" section
6. Update "Last Full Update" timestamp
7. Post update comment with changes

**Comment Template:**
```markdown
## Update: YYYY-MM-DD HH:MM UTC

**Added Capabilities:**
- [Air-Side] Feature name - Brief description (Issue #XXX)
- [SystemTools] Feature name - Brief description (Issue #XXX)

**Modified Capabilities:**
- [Domain] Feature name - What changed (Issue #XXX)

**Status Changes:**
- [Domain] Feature: ✅→⏳ (explanation)
- [Domain] Feature: ⏳→✅ (Issue #XXX complete)

**Removed/Deprecated:**
- [Domain] Feature name - Why removed (Issue #XXX)
```

**Post Comment:**
```bash
gh issue comment 128 --body "$(cat <<'EOF'
## Update: YYYY-MM-DD HH:MM UTC

[Your changes here]
EOF
)"
```

---

### 3. Git Repository Status ✅

**Check and Commit Outstanding Changes:**
- [ ] Review `git status`
- [ ] Check for uncommitted PM documentation
- [ ] Commit any PM-created files (.claude/*, docs/*, etc.)
- [ ] Verify main branch is up to date
- [ ] Check for untracked files that should be committed

**Commands:**
```bash
# Check status
git status

# Review uncommitted changes
git diff

# Add and commit PM docs
git add .claude/PM_*.md docs/*.md
git commit -m "[PM][DOCS] Update PM documentation - YYYY-MM-DD

- Updated PM EOD tasks
- Reviewed functionality tracker
- Documented completed work

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Check main branch status
git log --oneline -5
```

---

### 4. Domain Session Status ✅

**Check All Domain Sessions:**
- [ ] Air-Side: Check for pending work or blocked state
- [ ] Ground-Side: Check for pending work or blocked state
- [ ] SystemTools: Check for pending work or blocked state

**Tmux Session Check:**
```bash
# List all sessions
tmux list-sessions

# Check each domain
tmux capture-pane -t Air -p | tail -20
tmux capture-pane -t Ground -p | tail -20
tmux capture-pane -t Tools -p | tail -20

# Note any pending work or blockers
```

**Document Findings:**
- Any sessions waiting for user input?
- Any sessions with errors?
- Any sessions with pending tasks?
- Should sessions be closed or left running?

---

### 5. Documentation Updates ✅

**Update PM Documentation as Needed:**
- [ ] `.claude/PM_RULES_CRITICAL.md` - If workflow changed
- [ ] `.claude/TMUX_COMMUNICATION_PROTOCOL.md` - If protocol updated
- [ ] `.claude/MULTI_DOMAIN_COORDINATION.md` - If coordination changed
- [ ] `.claude/LESSONS_LEARNED.md` - If lessons learned today
- [ ] `.claude/PM_START.md` - If startup protocol changed

**Check for Stale Documentation:**
- Review dates on PM documents
- Update any references to old issues
- Remove deprecated information
- Add WHO/Date stamps to changes

---

### 6. Runtime Status File ✅

**Update RUNTIME_STATUS.json (if exists):**
- [ ] Update `timestamp`
- [ ] Update `session_type` if changed
- [ ] Update `status` (ACTIVE, PENDING, COMPLETE, etc.)
- [ ] Update `completed_today` list
- [ ] Update `system_state`
- [ ] Add any new priority tasks

**File Location:** `/home/anthony/DPM-V2/RUNTIME_STATUS.json`

---

### 7. User Handoff Notes ✅

**Prepare Handoff for Next Session:**

**Create Brief Summary:**
- What was completed today?
- What issues were closed?
- What is in progress?
- What is blocked and why?
- What should be prioritized next?

**Save to:** `/tmp/PM_EOD_SUMMARY_YYYY_MM_DD.txt`

**Template:**
```markdown
# PM EOD Summary - YYYY-MM-DD

## Completed Today
- Issue #XXX: Feature name - Status
- Issue #XXX: Feature name - Status

## In Progress
- Issue #XXX: Feature name - Current status, blockers

## Blocked
- Issue #XXX: Feature name - Reason, needed resolution

## Next Session Priorities
1. Priority task 1
2. Priority task 2
3. Priority task 3

## Notes for Next PM Session
- Important context
- Decisions made
- Workarounds implemented

---
**Session Duration:** X hours
**Issues Closed:** X
**Issues Updated:** X
**New Issues Created:** X
```

---

### 8. Cleanup and Preparation ✅

**Clean Up Temporary Files:**
- [ ] Review `/tmp/PM_*.txt` files
- [ ] Archive important temp files to project docs
- [ ] Delete obsolete temp files
- [ ] Clear any temporary test data

**Prepare for Next Session:**
- [ ] Verify all critical files are committed
- [ ] Check for any "TODO" or "FIXME" comments in PM docs
- [ ] Ensure MASTER functionality tracker is current
- [ ] Leave clear notes in tmux sessions if applicable

---

## 🎯 Quick EOD Workflow

**Fast checklist for routine days:**

1. **60 seconds:** Check git status, commit PM docs
2. **60 seconds:** Update Issue #128 if capabilities changed
3. **30 seconds:** Close completed issues
4. **30 seconds:** Check tmux sessions for blockers
5. **60 seconds:** Write brief EOD summary

**Total: ~4 minutes**

---

## 📊 Weekly EOD Tasks (Friday or End of Week)

**Additional tasks for end of week:**

- [ ] Review ALL open issues, clean up stale ones
- [ ] Update Issue #128 with comprehensive week review
- [ ] Archive important temp files to permanent locations
- [ ] Review and update LESSONS_LEARNED.md
- [ ] Plan next week's priorities
- [ ] Run full system test if major changes this week

---

## 🔔 Reminders

**Don't Forget:**
- Issue #128 (MASTER tracker) is the single source of truth for capabilities
- Always update timestamps when editing PM docs
- Link related issues in comments for traceability
- User-facing summary helps with context restoration
- Commit PM docs before ending session

**PM Mantra:** *"If it's not in Issue #128, it's not officially tracked"*

---

**Created:** 2025-11-17
**Last Updated:** 2025-11-17 00:30 UTC
**Maintained By:** CC-PM

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
