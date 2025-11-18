# Tmux Inter-Domain Communication Protocol
**Created:** 2025-11-16
**Purpose:** Mandatory protocol for ALL cross-domain communication via tmux
**Applies To:** ALL domains (PM, Air-Side, Ground-Side, SystemTools)

---

## 🚨 CRITICAL RULES - NO EXCEPTIONS

### Rule 1: WHO Tag Format (MANDATORY)

**ALL tmux messages to other domains MUST start with WHO tag:**

```
WHO: {Sender} To {Recipient}

{Message content}
```

**Valid Senders/Recipients:**
- `PM` - Project Manager session
- `Air-Side` - Air-Side C++ development session
- `Ground-Side` - Ground-Side Android development session
- `SystemTools` - SystemTools Python development session

**Examples:**

✅ **CORRECT:**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Please work on Issue #118 - Implement universal logging with destination_ip and destination_port parameters. See /tmp/pm_design_recommendation.md for complete specification." C-m
```

✅ **CORRECT:**
```bash
tmux send-keys -t Ground "WHO: Air-Side To Ground-Side

Air-Side implementation complete. Ground-Side needs to parse new 'focus_distance' field in status updates. See Issue #10 comment for API details." C-m
```

❌ **INCORRECT (No WHO tag):**
```bash
tmux send-keys -t Air "Work on Issue #118" C-m
# Missing WHO tag - recipient doesn't know who sent this
```

❌ **INCORRECT (Wrong format):**
```bash
tmux send-keys -t Air "# PM: Work on Issue #118" C-m
# Used # prefix which is Claude API command, not comment!
# This may add to project memory instead of sending message
```

❌ **INCORRECT (No carriage return):**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118"
# Missing C-m - command typed but NOT executed!
```

---

### Rule 2: ALWAYS Send Carriage Return (MANDATORY)

**CRITICAL:** `tmux send-keys` requires `C-m` or `Enter` to execute the command.

**Problem:** Forgetting carriage return means command is typed but NOT executed - it just sits at the prompt!

✅ **CORRECT:**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118" C-m
# Command is sent AND executed
```

✅ **CORRECT (Alternative):**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118"
tmux send-keys -t Air Enter
# Separate send-keys for text and Enter - also works
```

❌ **INCORRECT:**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118" Enter
# "Enter" is literal text, not carriage return!
# Must use C-m, not "Enter"
```

**Verification After Sending:**
```bash
sleep 2 && tmux capture-pane -t Air -p | tail -20
# Should see command being processed, NOT sitting at prompt
```

---

### Rule 3: NEVER Use # Prefix (CRITICAL)

**# is a Claude API command to add to project memory, NOT a comment!**

❌ **NEVER DO THIS:**
```bash
tmux send-keys -t Air "# PM: Work on Issue #118" C-m
# This is a Claude API command, NOT a comment!
# May add to project memory instead of sending to domain
```

✅ **USE THIS INSTEAD:**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118" C-m
# Clear WHO tag format, no ambiguity
```

---

## 📋 Message Format Specification

### Complete Message Template

```
WHO: {Sender} To {Recipient}

{Clear description of task/request}

{Optional: Context or background}
{Optional: Links to issues, files, or documentation}
{Optional: Success criteria or deliverables}
```

### Examples by Scenario

#### Scenario 1: PM Delegating Work

```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Please implement Issue #115 - system.get_config TCP command.

Requirements:
1. Add handler in tcp_server.cpp
2. Return all config from ConfigManager
3. Format as JSON response
4. Update protocol/commands.json

See /home/anthony/DPM-V2/PM_PRIORITY1_ROADMAP.md for detailed spec.

Success criteria:
- TCP command responds with valid JSON
- All config values included
- No crashes or errors" C-m
```

#### Scenario 2: Cross-Domain Handoff

```bash
tmux send-keys -t Ground "WHO: Air-Side To Ground-Side

Air-Side Issue #10 implementation complete.

Ground-Side needs to:
1. Parse 'focus_distance' field from status updates
2. Update CameraViewModel.kt line 234
3. Display in UI at CameraControlScreen.kt line 456

API details in Issue #10 latest comment.
Example code provided." C-m
```

#### Scenario 3: PM Requesting Status

```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Status update request for Issue #118.

Please provide:
- Current progress percentage
- Completed tasks
- Remaining tasks
- Any blockers
- Estimated completion time" C-m
```

#### Scenario 4: Domain Asking Question

```bash
tmux send-keys -t PM "WHO: Air-Side To PM

Question about Issue #118 implementation.

Should destination_ip parameter be optional or required?
If optional, what should be the fallback behavior?

Context: PM design doc says 'backward compatible' but unclear if destination_ip is required for new format." C-m
```

---

## 🔍 Verification Protocol

### After Sending Every tmux Message

**PM MUST verify message was received:**

```bash
# 1. Send message
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118" C-m

# 2. Wait for processing
sleep 2

# 3. Capture and check
tmux capture-pane -t Air -p | tail -20

# 4. Look for:
# ✅ Message appears in output
# ✅ Domain is processing (thinking, reading files, etc.)
# ❌ Message still sitting at prompt (missing C-m!)
# ❌ Error messages
```

**If message not processed:**
1. Check if C-m was included
2. Check if session is in correct state (not in vim, not waiting for input)
3. Re-send with C-m
4. Document issue for future reference

---

## 📊 Domain Responsibilities

### When Receiving tmux Message

**Domain MUST:**
1. **Acknowledge receipt** (update issue or send response via tmux)
2. **Parse WHO tag** to identify sender
3. **Read full message** before starting work
4. **Ask clarifying questions** if requirements unclear
5. **Update GitHub issue** when starting work
6. **Report progress** periodically
7. **Notify sender** when complete or blocked

**Example Response:**
```bash
tmux send-keys -t PM "WHO: Air-Side To PM

Received Issue #118 request.

Starting implementation now.
Have reviewed design doc at /tmp/pm_design_recommendation.md.
Will update Issue #118 with progress.

ETA: 2-3 hours for 9-task implementation." C-m
```

---

## 🚨 Common Mistakes to Avoid

### Mistake 1: Forgetting C-m
```bash
❌ tmux send-keys -t Air "WHO: PM To Air-Side Work on #118"
# Command typed but NOT executed!
```

### Mistake 2: Using # Prefix
```bash
❌ tmux send-keys -t Air "# PM: Work on #118" C-m
# Claude API command, not comment!
```

### Mistake 3: No WHO Tag
```bash
❌ tmux send-keys -t Air "Work on Issue #118" C-m
# Recipient doesn't know who sent this
```

### Mistake 4: Vague Message
```bash
❌ tmux send-keys -t Air "WHO: PM To Air-Side Fix the logging thing" C-m
# What logging thing? Which issue? What specifically?
```

### Mistake 5: Not Verifying Receipt
```bash
# Sent message but never checked if Air-Side received it
# Air-Side might be stuck waiting for input or in vim
```

---

## ✅ Best Practices

### 1. Be Specific and Complete

✅ **GOOD:**
```bash
"WHO: PM To Air-Side

Implement Issue #118 - Universal logging with destination_ip/destination_port.
See /tmp/pm_design_recommendation.md for spec.
9 tasks total, estimated 2-3 hours.
Update Issue #118 with progress."
```

❌ **BAD:**
```bash
"WHO: PM To Air-Side

Do Issue #118"
```

### 2. Include Context

✅ **GOOD:**
```bash
"WHO: PM To Air-Side

SystemTools completed their part of Issue #118 (15 min).
Now Air-Side needs to implement universal streaming.
Design approved: explicit destination_ip + destination_port.
No filtering, backward compatible."
```

❌ **BAD:**
```bash
"WHO: PM To Air-Side

Do your part now"
```

### 3. Provide Issue Numbers

✅ **GOOD:**
```bash
"WHO: PM To Air-Side

Work on Issue #115 - system.get_config TCP command"
```

❌ **BAD:**
```bash
"WHO: PM To Air-Side

Add the config getter thing"
```

### 4. Define Success Criteria

✅ **GOOD:**
```bash
"WHO: PM To SystemTools

Test Issue #117 config management.

Success criteria:
- Can fetch config from Air-Side
- Can edit and apply runtime changes
- Can persist to default.json
- Validation prevents invalid inputs"
```

❌ **BAD:**
```bash
"WHO: PM To SystemTools

Test the config stuff"
```

---

## 📞 PM Monitoring Protocol

### PM Must Check Sessions Regularly

**Every 10-15 minutes during active work:**

```bash
# Check all domain sessions
tmux capture-pane -t Air -p | tail -30
tmux capture-pane -t Ground -p | tail -30
tmux capture-pane -t Tools -p | tail -30
```

**Look for:**
- ✅ "Complete" or "✓" - Task finished
- ❌ "ERROR" or "FAILED" - Needs attention
- ⏸️ Waiting prompts - Domain needs input
- 🔄 "Thinking..." or file operations - Domain is working
- 📝 WHO tag responses - Domain communicating back

---

## 🎯 Session-Specific Examples

### PM Session → Air-Side

```bash
# Full example with verification
tmux send-keys -t Air-Side-PI "WHO: PM To Air-Side

Air-Side NetworkSink dynamic config bug fix needed.

Issue: Passive logging doesn't stop/start when config changed via system.update_config

Files affected:
- sbc/src/logging/sinks/network_sink.cpp
- Need to add ConfigManager include
- Update write() method to check config dynamically

This is Task 1 of 9 for Issue #118.
Please report when complete." C-m

# Verify
sleep 3
tmux capture-pane -t Air-Side-PI -p | tail -20
```

### PM Session → Ground-Side

```bash
tmux send-keys -t Ground-Side-AS "WHO: PM To Ground-Side

Please review Issue #126 - Ground-Side universal logging migration.

Status: BLOCKED - Awaiting Air-Side + SystemTools testing
Action needed: None yet, just FYI
Will notify when ready for Ground-Side implementation.

Estimated: 1-2 days until Air-Side completes testing." C-m
```

### PM Session → SystemTools

```bash
tmux send-keys -t DPM-SystemTools "WHO: PM To SystemTools

Issue #118 command format update complete - excellent work!

Next step: Wait for Air-Side to implement universal streaming.
Then: End-to-end testing of on-demand logging.

You can work on other tasks in meantime.
Will notify when Air-Side ready." C-m
```

---

## 🔗 Related Documents

- `.claude/PM_RULES_CRITICAL.md` - PM-specific critical rules (includes Rule 2 on C-m)
- `.claude/MULTI_DOMAIN_COORDINATION.md` - Multi-domain coordination framework
- `docs/GITHUB_ISSUE_WORKFLOW_ENFORCEMENT.md` - Issue update protocol with WHO tags

---

## 📋 Checklist for Every tmux Message

**Before sending, verify:**
- [ ] WHO tag present: "WHO: {Sender} To {Recipient}"
- [ ] Message is specific and complete
- [ ] Issue number included (if applicable)
- [ ] Context provided
- [ ] Success criteria defined (if delegating work)
- [ ] NO # prefix used
- [ ] C-m or Enter included at end
- [ ] Newlines properly formatted

**After sending, verify:**
- [ ] Waited 2-3 seconds for processing
- [ ] Captured pane output
- [ ] Message appears in session
- [ ] Domain is processing (not stuck at prompt)
- [ ] No error messages

---

## 🎯 Enforcement

**Violations of this protocol:**
1. **Missing WHO tag** → Message origin unclear, coordination fails
2. **Missing C-m** → Command not executed, work not started
3. **Using # prefix** → Message may be misinterpreted as API command
4. **Vague message** → Domain wastes time asking for clarification

**All domains MUST follow this protocol for effective cross-domain coordination.**

---

**Last Updated:** 2025-11-16
**Maintained by:** PM
**Status:** ACTIVE - Mandatory for all sessions
