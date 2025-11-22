# PM Workflow Session Start

**Purpose:** Lightweight PM session for workflow cleanup, documentation updates, and process improvements WITHOUT distraction from project development.

**Use When:**
- Working on PM documentation
- Cleaning up .claude/ directory
- Refactoring PM processes
- Updating workflow protocols
- Administrative tasks (issue cleanup, etc.)

**Skips:**
- ❌ System health checks
- ❌ Domain tmux session setup
- ❌ Network connectivity verification
- ❌ Real-time domain monitoring
- ❌ CCPM database checks

**Keeps:**
- ✅ Last session summary reading
- ✅ Git status check
- ✅ Issue review
- ✅ Focus on workflow tasks

---

## Startup Protocol

### Step 1: Read Last Session Summary ✅

```bash
echo "=== LAST SESSION SUMMARY ==="
cat .claude/LAST_SESSION.md
echo ""
echo "=== END SUMMARY ==="
```

**Report to user:**
- Date of last session
- What was completed
- What's in progress
- Next priorities

---

### Step 2: Git Repository Status ✅

```bash
# Quick status check
git status --short
git branch --show-current
```

**Check for:**
- Uncommitted PM documentation changes
- Files in `.claude/` modified
- Staged but not committed files

---

### Step 3: Open Issues Quick Review ✅

```bash
# Show critical and in-progress issues only
gh issue list --label "priority:critical" --state open --limit 5
gh issue list --label "status:in-progress" --state open --limit 5
```

**Purpose:** Context awareness without deep dive

---

### Step 4: Workflow Session Declaration ✅

**Announce to user:**

```
📋 PM WORKFLOW SESSION STARTED

Session Type: Administrative/Workflow
Focus: Process improvements, documentation, cleanup
Project Work: PAUSED (no domain monitoring)

Domain tmux sessions: NOT STARTED
Health monitoring: DISABLED
Real-time coordination: INACTIVE

Ready for workflow tasks.
```

---

## Workflow Session Focus Areas

**Typical Tasks:**
1. **PM Documentation Updates**
   - Refactor oversized .claude/ files
   - Update PM protocols
   - Clean up stale documentation

2. **Issue Management**
   - Close verified issues
   - Update stale issues
   - Create new tracking issues
   - Update Issue #128 (MASTER tracker)

3. **Git Repository Cleanup**
   - Commit PM documentation changes
   - Review and clean .gitignore
   - Archive old branches

4. **Workflow Process Improvements**
   - Update EOD/SOD protocols
   - Refine PM communication templates
   - Document lessons learned

5. **CCPM Database Maintenance**
   - Register new capabilities
   - Update capability descriptions
   - Clean up duplicates

---

## End of Workflow Session

**When user types "EXIT" or "DONE":**

1. **Commit PM Documentation Changes:**
   ```bash
   git status
   git add .claude/
   git commit -m "[PM][WORKFLOW] Session cleanup - $(date +%Y-%m-%d)

   - Updated PM documentation
   - Cleaned up workflow files
   - Improved process protocols

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

2. **Update LAST_SESSION.md:**
   - Document workflow changes made
   - List files created/modified/deleted
   - Note any process improvements

3. **Brief Summary to User:**
   ```
   Workflow session complete:
   - Files modified: X
   - Documentation updated: Y
   - Issues updated: Z
   - Ready to resume project work
   ```

---

## Switching to Project Work

**If user wants to start project work AFTER workflow session:**

```
User: "Start project work now"
PM: "Switching to full PM session..."

Then execute: /start-pm
```

This will:
- Start all domain tmux sessions
- Run health checks
- Enable real-time monitoring
- Switch context to project development

---

## Quick Reference

**Start Workflow Session:**
```
/start-pm-workflow
```

**Start Full PM Session:**
```
/start-pm
```

**Difference:**
- `/start-pm-workflow`: Lightweight, admin/docs only, no domain monitoring
- `/start-pm`: Full PM with health checks, tmux sessions, real-time coordination

---

**Created:** 2025-11-21
**Purpose:** Enable focused workflow improvements without project distraction
**Session Type:** Administrative/Documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
