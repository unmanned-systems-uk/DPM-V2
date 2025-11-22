# PM (Project Manager) Critical Rules - Index

**WHO:** CC-PM
**Purpose:** Essential rules for PM session efficiency and context preservation

**IMPORTANT:** This is an index. Full rules are in topic-specific files below.

---

## Rule Categories

**All PM rules are organized into 3 categories:**

1. **Coordination & Delegation** → `.claude/PM_RULES_COORDINATION.md`
2. **Workflow & Context Management** → `.claude/PM_RULES_WORKFLOW.md`
3. **Protocol & Architecture** → `.claude/PM_RULES_PROTOCOL.md`

---

## Quick Rule Summary

### 🔄 Coordination & Delegation
**File:** `PM_RULES_COORDINATION.md`

- **Rule 1:** ALWAYS delegate coding to domain agents
- **Rule 2:** Tmux communication protocol (MANDATORY)
- **Rule 2.1:** Carriage return (C-m) required
- **Rule 3:** Monitor domain progress via tmux
- **Rule 6:** Efficient tmux communication (deprecated - see Rule 2)

**Key:** PM NEVER writes code. Domain agents implement. PM coordinates.

### 📋 Workflow & Context Management
**File:** `PM_RULES_WORKFLOW.md`

- **Rule 4:** PM-only tasks (what PM can/should do)
- **Rule 5:** Context management (preserve token budget)
- **Rule 7:** Session memory/context extension
- **Rule 8:** Use extended thinking for complex coordination
- **Rule 9:** Use opusplan model for complex PM tasks

**Key:** Manage context wisely. PM session has limited tokens.

### 🔧 Protocol & Architecture
**File:** `PM_RULES_PROTOCOL.md`

- **Rule 10:** Architecture documentation updates (Wed/Fri)
- **Rule 11:** Protocol enforcement & cross-domain compliance

**Key:** Enforce `protocol/*.json` as single source of truth.

---

## Critical Reminders

**Before ANY session:**
1. ✅ Verify tmux sessions exist for all domains
2. ✅ Check open issues (critical + in-progress)
3. ✅ Read `.claude/LAST_SESSION.md` for context

**During session:**
1. ✅ Delegate ALL coding to domain agents
2. ✅ Use tmux send-keys with C-m for communication
3. ✅ Monitor domain progress via `tmux capture-pane`

**When assigning work:**
1. ✅ Create/update GitHub issue FIRST
2. ✅ Send clear instructions via tmux
3. ✅ Verify agent received and acknowledged
4. ✅ Monitor progress periodically

---

## Emergency Quick Reference

**Lost context?**
```bash
cat .claude/COMPRESSION_EMERGENCY.md
cat .claude/PM_START.md
```

**Need full rules?**
- Coordination: `cat .claude/PM_RULES_COORDINATION.md`
- Workflow: `cat .claude/PM_RULES_WORKFLOW.md`
- Protocol: `cat .claude/PM_RULES_PROTOCOL.md`

**Tmux help?**
```bash
cat .claude/TMUX_COMMUNICATION_PROTOCOL.md
cat .claude/PM_MONITORING_PROTOCOL.md
```

---

**Last Updated:** 2025-11-22
**Status:** Refactored from 706-line monolithic file
