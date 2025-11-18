# 🆘 SOS - Sync of Session

**Trigger:** When user types `/sos`, `sos`, or `SOS`

**Purpose:** Emergency refresh of project rules and validation during long sessions

---

## Execution Procedure

### Step 1: Acknowledge and Stash Context
```
🆘 SOS ACTIVATED - Syncing Session Rules

📦 Stashing current work context...
- Current task: [describe what we're working on]
- Active todos: [list current todos]
- Open files: [list files being edited]
```

### Step 2: Re-read Critical Documents
```
📚 Re-reading critical rules...
✅ .claude/PM_RULES_CRITICAL.md
✅ .claude/LESSONS_LEARNED_CRITICAL.md
✅ protocol/log_contexts.json
✅ protocol/commands.json
✅ [Current issue requirements if applicable]
```

### Step 3: Validate Current Work
```
🔍 Validating current work against rules...

Checking:
- [ ] Are we following single-point-of-truth for protocols?
- [ ] Have .claude changes been committed?
- [ ] Are issues closed only after git commits verified?
- [ ] Are we hardcoding protocol structures?
- [ ] Is SDK location correctly documented/used?
```

### Step 4: Report Violations
```
⚠️ Violations Detected:
1. [List any rule violations found]
2. [Specific examples from current work]

OR

✅ No violations detected - current work complies with rules
```

### Step 5: Provide Recommendations
```
💡 Recommendations:
1. [Specific actions to fix violations]
2. [Preventive measures]
3. [Best practices to apply]
```

### Step 6: Resume with Refreshed Mindset
```
🎯 Session rules refreshed. Continuing work with:
- [Current task restated]
- [Rules to apply]
- [Quality checklist]

Ready to proceed.
```

---

## When to Use SOS

**Triggers:**
- Session duration >4 hours
- Feeling "drift" from best practices
- About to make major architectural decision
- Noticed rule violations accumulating
- User explicitly requests: "sos"

**Frequency:**
- As needed, but recommended every 4-6 hours in long sessions
- Before committing major changes
- Before closing multiple issues

---

## Example Output

```
User: sos

PM: 🆘 SOS ACTIVATED - Syncing Session Rules

📦 Stashing current work context...
- Current task: Re-implementing system.get_config (Issue #115)
- Active todos: 7 items (3 in progress, 4 pending)
- Open files: tcp_server.cpp, config_manager.h

📚 Re-reading critical rules...
✅ .claude/PM_RULES_CRITICAL.md
✅ .claude/LESSONS_LEARNED_CRITICAL.md
✅ protocol/log_contexts.json
✅ protocol/commands.json
✅ Issue #115 requirements

🔍 Validating current work against rules...

Checking:
- ❌ Single-point-of-truth: Issue #115 has no protocol spec in commands.json
- ✅ .claude changes: No uncommitted changes
- ❌ Issues before commits: Issue #115 closed but no commits found
- ❌ Hardcoding: tcp_server.cpp hardcodes response format
- ✅ SDK location: Correctly using /workspace/sdk

⚠️ Violations Detected:
1. Issue #115 marked CLOSED without git commits
2. system.get_config response format not defined in protocol/commands.json
3. tcp_server.cpp hardcodes JSON structure instead of reading protocol

💡 Recommendations:
1. Create protocol/commands.json entry for system.get_config with exact response format
2. Update tcp_server.cpp to read response format from protocol
3. Re-implement, test, commit BEFORE marking issue complete
4. Update issue with commit hash

🎯 Session rules refreshed. Continuing re-implementation with:
- Protocol-first approach
- Commit verification before closing
- Single source of truth enforcement

Ready to proceed.
```

---

## Implementation Notes

This command should:
1. Pause current work
2. Create mental checkpoint
3. Re-inject critical rules into context
4. Validate current work
5. Provide actionable feedback
6. Resume work with proper mindset

**Do NOT:**
- Lose current context
- Restart conversation
- Abandon current task

**DO:**
- Refresh rules
- Validate compliance
- Suggest corrections
- Continue with better awareness
