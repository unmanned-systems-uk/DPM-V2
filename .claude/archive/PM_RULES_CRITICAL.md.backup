# PM (Project Manager) Critical Rules
**WHO:** CC-PM
**Created:** 2025-11-14
**Purpose:** Essential rules for PM session to maximize efficiency and maintain context

---

## 🎯 RULE 1: ALWAYS Delegate Coding to Domain Agents

### ❌ **PM MUST NEVER:**
- Write implementation code directly
- Modify source files for features/fixes
- Build projects directly (except for verification)
- Run domain-specific tests

### ✅ **PM MUST ALWAYS:**
- Delegate ALL coding tasks to domain agents via tmux
- Use domain agents (Air-Side, Ground-Side, SystemTools) for implementations
- Reserve PM context for coordination, monitoring, documentation
- Only perform PM-specific tasks (issue management, git coordination, integration testing)

### **Why This Rule Exists:**
- **PM Context Preservation**: PM session has limited context (200k tokens)
- **Efficiency**: Domain agents are already set up with domain-specific context
- **Specialization**: Domain agents know their codebase better
- **Parallel Execution**: Multiple domains can work simultaneously

### **Example - CORRECT:**
```markdown
User: "Fix the NetworkSink timeout issue in Ground-Side"

PM Response:
✅ Sending task to Ground-Side session...
[Uses tmux send-keys to Ground-Side-AS session]

PM monitors Ground-Side session for completion
PM updates Issue when Ground-Side reports done
```

### **Example - INCORRECT:**
```markdown
User: "Fix the NetworkSink timeout issue in Ground-Side"

PM Response:
❌ Let me read the NetworkSink code and fix it...
❌ [PM reads file, modifies code, commits]
❌ This wastes PM context on domain-specific work
```

---

## 🎯 RULE 2: Tmux Communication Protocol (MANDATORY)

### **CRITICAL:** Read `.claude/TMUX_COMMUNICATION_PROTOCOL.md` for complete protocol

**All tmux cross-domain communication MUST follow these rules:**

1. **WHO Tag Format (NEW - 2025-11-16):**
   ```
   WHO: {Sender} To {Recipient}

   {Message content}
   ```
   - Example: "WHO: PM To Air-Side\n\nWork on Issue #118" C-m
   - **NEVER** use # prefix (it's a Claude API command, not a comment!)

2. **ALWAYS Use Carriage Return:**
   - MUST include `C-m` or `Enter` at end
   - Forgetting C-m means command typed but NOT executed

3. **Verification:**
   - Always check session after sending: `tmux capture-pane -t {session} -p | tail -20`
   - Verify command is being processed, not stuck at prompt

### **Quick Reference - Correct Format:**
```bash
tmux send-keys -t Air "WHO: PM To Air-Side

Work on Issue #118 - implement universal logging.
See /tmp/pm_design_recommendation.md for spec." C-m

# Then verify
sleep 2 && tmux capture-pane -t Air -p | tail -20
```

**See `.claude/TMUX_COMMUNICATION_PROTOCOL.md` for:**
- Complete message format specification
- Examples by scenario
- Common mistakes to avoid
- Best practices
- Verification protocol

---

## 🎯 RULE 2.1: Carriage Return Details (Subset of Rule 2)

### **CRITICAL:** `tmux send-keys` Requires C-m or Enter

**Problem:** Forgetting carriage return means command is typed but NOT executed

### ❌ **INCORRECT (Forgotten Many Times):**
```bash
tmux send-keys -t Air-Side-PI "Work on Issue #74" Enter
# Command is typed but NOT sent - just sits in prompt!
```

### ✅ **CORRECT:**
```bash
tmux send-keys -t Air-Side-PI "Work on Issue #74" C-m
# Command is sent AND executed
```

### **Alternative (Also Correct):**
```bash
tmux send-keys -t Air-Side-PI "Work on Issue #74"
tmux send-keys -t Air-Side-PI Enter
# Separate send-keys for text and Enter
```

### **Verification:**
Always check tmux session after sending command:
```bash
sleep 2 && tmux capture-pane -t Air-Side-PI -p | tail -20
# Should see command being processed, NOT sitting at prompt
```

### **PM Session Self-Check:**
Before ANY tmux send-keys command, ask:
- "Did I include C-m or Enter?"
- "Will this command actually execute?"

---

## 🎯 RULE 3: Monitor Domain Progress via tmux

### **Real-Time Monitoring Protocol:**

**Every 10-15 minutes during active work:**
```bash
# Check all domain sessions
tmux capture-pane -t Ground-Side-AS -p | tail -20
tmux capture-pane -t Ai-Side-PI -p | tail -20
tmux capture-pane -t DPM-SystemTools -p | tail -20
```

**Look for:**
- ✅ "✓" or "Complete" - Task finished
- ❌ "ERROR" or "FAILED" - Needs attention
- ⏸️ Waiting prompts - Domain needs input
- 🔄 "Thinking..." - Domain is working

### **When to Intervene:**
- Domain reports blocked
- Errors detected in output
- Domain asks question via tmux
- Progress stalled for >30 minutes

---

## 🎯 RULE 4: PM-Only Tasks

### **PM Responsibilities (DO in PM session):**
1. **Issue Management**
   - Create issues with clear requirements
   - Update issue status and progress
   - Link related issues
   - Close issues when complete

2. **Git Coordination**
   - Monitor git status across domains
   - Coordinate branch merges
   - Resolve merge conflicts
   - Push to remote

3. **Documentation**
   - Update LESSONS_LEARNED.md
   - Document workarounds and decisions
   - Maintain PM_START.md and coordination docs

4. **Integration Testing**
   - Run multi-domain integration tests
   - Verify cross-domain functionality
   - Document integration results

5. **Monitoring & Reporting**
   - Monitor tmux sessions
   - Report status to user
   - Track overall progress
   - Identify blockers

### **Domain-Specific Tasks (DELEGATE to domains):**
1. **Code Implementation**
   - Writing new features
   - Fixing bugs
   - Refactoring code
   - Adding tests

2. **Building & Testing**
   - Running builds
   - Running unit tests
   - Debugging failures

3. **Domain Documentation**
   - Code comments
   - API documentation
   - Component READMEs

---

## 🎯 RULE 5: Context Management

### **PM Context Budget: 200,000 tokens**

**Current Usage Tracking:**
Always monitor token usage at end of each response

**High-Cost Activities (Avoid in PM):**
- ❌ Reading large source files (1000+ lines)
- ❌ Reading multiple domain codebases
- ❌ Extensive code analysis
- ❌ Long debugging sessions

**Low-Cost Activities (Good for PM):**
- ✅ Reading PM instruction files
- ✅ Checking issue statuses
- ✅ Monitoring tmux outputs (tail -20)
- ✅ Git status checks
- ✅ Writing documentation

### **Context Preservation Strategies:**

1. **Delegate Heavy Reading:**
   ```markdown
   ❌ PM: Read entire Air-Side codebase
   ✅ PM: Ask Air-Side "Does StructuredLogger have UDP output?"
   ```

2. **Use Targeted Commands:**
   ```bash
   ❌ git diff (shows all changes - huge)
   ✅ git diff --stat (shows summary only)
   ✅ git diff file.txt | head -40 (limited output)
   ```

3. **Limit tmux Captures:**
   ```bash
   ❌ tmux capture-pane -t Air-Side-PI -p (entire buffer)
   ✅ tmux capture-pane -t Air-Side-PI -p | tail -30 (recent only)
   ```

---

## 🎯 RULE 6: Efficient tmux Communication (Deprecated - See Rule 2)

### **IMPORTANT:** This section has been superseded by comprehensive protocol.

**See `.claude/TMUX_COMMUNICATION_PROTOCOL.md` for complete specification.**

**Quick reminders (full details in protocol doc):**

1. **Use WHO Tag Format:**
   ```bash
   ✅ "WHO: PM To Air-Side

   Work on Issue #74 - Air-Side UDP log streaming..." C-m
   ```

2. **Be Specific and Complete:**
   - Include issue numbers
   - Provide context
   - Define success criteria
   - Link to documentation

3. **Always Verify Receipt:**
   ```bash
   tmux send-keys -t Air "..." C-m
   sleep 2
   tmux capture-pane -t Air -p | tail -20
   ```

**See `.claude/TMUX_COMMUNICATION_PROTOCOL.md` for:**
- Complete message templates
- Scenario-based examples
- Common mistakes
- Verification protocol

---

## 🎯 RULE 7: Session Memory/Context Extension

### **Claude Code Settings:**

**Location:** `.claude/settings.local.json`

**Available Settings:**
```json
{
  "permissions": {
    "allow": [...],
    "deny": [],
    "ask": []
  }
}
```

**Note:** Context/memory settings are NOT configurable per-session
- Context window is fixed at 200k tokens (Sonnet 4.5)
- No way to extend PM session context via settings
- Must use strategies above to preserve context

### **Alternative: Use Multiple PM Sessions**

If PM context exhausted:
1. **Document current state** in issues
2. **Start new PM session** with /start-pm
3. **PM reads status from issues** (not from chat history)
4. **Continue coordination**

---

## 🎯 RULE 8: Use Extended Thinking for Complex Coordination

### **What is Extended Thinking?**

Extended thinking enables Claude to show step-by-step reasoning before delivering answers. Perfect for PM coordination tasks!

**Best for:**
- ✅ Planning complex multi-domain coordination
- ✅ Debugging intricate integration issues
- ✅ Creating implementation plans for new features
- ✅ Analyzing cross-domain dependencies
- ✅ Resolving conflicts and blockers

### **How to Enable Extended Thinking:**

**Method 1: Toggle During Session**
```
Press Tab to enable/disable extended thinking
```

**Method 2: Request in Prompt**
```
"Think deeply about how to coordinate Air-Side and Ground-Side for Issue #82"
"Think hard about potential integration conflicts"
```

**Method 3: Environment Variable (Permanent)**
```bash
export MAX_THINKING_TOKENS=10000
# Then restart Claude Code
```

**Intensifying Phrases:**
- "think" - Basic reasoning
- "think deeply" - More thorough analysis
- "think hard" - Even deeper reasoning
- "think more" - Extended reasoning
- "think longer" - Maximum depth

### **When to Use Extended Thinking in PM:**

**✅ USE for:**
1. **Integration Planning**
   - "Think deeply about merging Air-Side, Ground-Side, SystemTools"
   - Complex dependency analysis
   - Conflict prediction

2. **Debugging Multi-Domain Issues**
   - "Think hard about why logs aren't flowing between domains"
   - Cross-domain error analysis
   - Root cause investigation

3. **Architecture Decisions**
   - "Think deeply about the best approach for dynamic IP discovery"
   - Evaluating multiple solutions
   - Trade-off analysis

4. **Blocker Resolution**
   - "Think hard about how to resolve the ADB multiple device issue"
   - Alternative approaches
   - Workaround evaluation

**❌ DON'T USE for:**
- Simple status checks
- Routine monitoring
- Basic issue updates
- Straightforward git commands

### **Example - PM Using Extended Thinking:**

```markdown
User: "How should we coordinate Air-Side and Ground-Side for Issue #82?"

PM: "Let me think deeply about this coordination strategy..."

[Extended thinking enabled - Claude shows reasoning]

Thinking:
1. Analyze dependencies between domains
2. Identify potential conflicts
3. Determine optimal merge order
4. Plan integration test sequence
5. Consider rollback strategies

Response:
Based on deep analysis, here's the coordination plan:
[Detailed, well-reasoned response]
```

### **Extended Thinking + Plan Mode:**

**Powerful Combination for PM:**
```bash
# Start in Plan Mode with extended thinking
claude --permission-mode plan

# Then use thinking prompts
> "Think deeply about the multi-domain integration approach"
```

**Benefits:**
- Safe analysis (no changes made)
- Deep reasoning enabled
- Comprehensive planning
- Risk-free exploration

### **Token Usage Consideration:**

**Extended thinking uses additional tokens:**
- Basic thinking: ~1k-2k tokens
- Deep thinking: ~5k-10k tokens
- Maximum thinking: ~10k-32k tokens

**PM Context Budget:**
- Total: 200k tokens
- Reserve ~20k for extended thinking on complex tasks
- Still leaves 180k for coordination work

**Best Practice:**
Use extended thinking **selectively** for complex decisions, not routine tasks.

---

## 🎯 RULE 9: Use opusplan Model for Complex PM Tasks

### **What is opusplan?**

Hybrid model that automatically:
1. Uses **Opus** for planning and architecture decisions (superior reasoning)
2. Switches to **Sonnet** for code generation (efficiency)

### **When PM Should Consider opusplan:**

**✅ USE for:**
- Complex multi-domain architecture decisions
- Integration strategy planning
- Conflict resolution requiring deep analysis
- Long-term roadmap planning

**❌ DON'T USE for:**
- Routine monitoring (Sonnet is fine)
- Simple coordination tasks
- Quick status updates
- Standard git operations

### **How to Use opusplan:**

**Not available as environment variable in Claude Code**
- Check Claude Code version for opusplan support
- May require specific Claude Code version/config

**Alternative:**
Request deep thinking with Sonnet (current model):
```
"Think deeply about..." (triggers extended reasoning)
```

---

## 🎯 RULE 10: Architecture Documentation Updates

### **CRITICAL:** Track All Architecture Changes

**When ANY domain updates architecture documentation:**

1. **Domain Responsibilities:**
   - Comment out deprecated sections (NEVER delete)
   - Add WHO/Date/Time stamps to new sections
   - Create `[ARCHITECTURE][DOMAIN]` issue
   - Use architecture label for PM tracking

2. **PM Responsibilities:**
   - Monitor for architecture label: `gh issue list --label architecture`
   - Review domain-specific architecture doc changes
   - Integrate into master architecture documents
   - Close architecture update issue when integrated

3. **Deprecation Protocol:**
   ```markdown
   <!-- DEPRECATED: YYYY-MM-DD by WHO
        Reason: [Why replaced]
        Superseded by: [New section reference]

   ## Old Section
   [Preserved content...]
   -->
   ```

4. **New Section Protocol:**
   ```markdown
   ## New Section

   **WHO:** CC-[Domain]
   **Date:** YYYY-MM-DD
   **Time:** HH:MM UTC
   **Supersedes:** [What this replaces]
   **Related Issue:** #[number]
   ```

5. **Master Doc Updates:**
   - Update `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md`
   - Update `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` (if applicable)
   - Maintain architectural evolution timeline
   - Commit with clear reference to domain changes

### **Why This Rule Exists:**
- **Preserve History:** See what approaches were tried before
- **PM Tracking:** Architecture changes don't slip through unnoticed
- **Accountability:** WHO/Date stamps show evolution
- **Master Doc Sync:** PM knows exactly what needs updating
- **Future Sessions:** Claude can learn from architectural evolution

### **Reference Document:**
See `.claude/ARCHITECTURE_UPDATE_RULES.md` for complete workflow and templates.

---

## 📋 PM Session Checklist

**Before Starting Work:**
- [ ] Read /home/anthony/.claude/CLAUDE.md (connection details)
- [ ] Read .claude/PM_START.md (startup protocol)
- [ ] Read .claude/MULTI_DOMAIN_COORDINATION.md (coordination framework)
- [ ] **Review Issue #101** if task requires extended thinking or complex coordination
- [ ] Verify all tmux sessions active
- [ ] Check current branch and git status
- [ ] Review open critical issues

**During Work:**
- [ ] Delegate ALL coding to domain agents
- [ ] Use C-m or Enter in tmux send-keys
- [ ] Monitor domains every 10-15 minutes
- [ ] Update issues with progress
- [ ] Track token usage
- [ ] Use targeted commands (tail, head, --stat)

**Before Ending Session:**
- [ ] Document current state in issues
- [ ] Commit PM-created documentation
- [ ] Update LESSONS_LEARNED.md if needed
- [ ] Leave clear notes for next PM session

---

## 🚨 Common PM Mistakes to Avoid

1. ❌ **Coding directly instead of delegating**
   - Wastes PM context
   - Slower than using domain experts

2. ❌ **Forgetting C-m in tmux send-keys**
   - Command not executed
   - Causes confusion and delays

3. ❌ **Reading entire files instead of asking domains**
   - Consumes massive context
   - Domain agents already know their code

4. ❌ **Not monitoring tmux sessions regularly**
   - Miss errors and completions
   - Can't provide timely help

5. ❌ **Creating issues without clear requirements**
   - Domains waste time asking for clarification
   - Slower execution

---

## ✅ PM Success Patterns

1. ✅ **Clear delegation with context**
2. ✅ **Regular monitoring (every 15 min)**
3. ✅ **Efficient context usage**
4. ✅ **Comprehensive documentation**
5. ✅ **Proactive issue updates**
6. ✅ **Always use C-m in tmux commands**

---

## 🎯 RULE 11: Protocol Enforcement & Cross-Domain Compliance

### **CRITICAL:** protocol/*.json Files are Single Source of Truth

**All domains MUST use protocol JSON files for:**
- Log contexts (`protocol/log_contexts.json`)
- Commands (`protocol/commands.json`)
- Any cross-domain standards

### ❌ **PM MUST NEVER Allow:**
- Hardcoded values that should be in protocol files
- Domains implementing custom formats instead of protocol
- Manual duplication of protocol data across domains
- "Good enough" implementations that violate protocol

### ✅ **PM MUST ALWAYS:**
1. **Verify Protocol Compliance at Start of Phase:**
   - Check all domains use protocol/*.json files
   - Verify no hardcoded protocol data
   - Test cross-domain compatibility

2. **Regular Compliance Checks (Weekly):**
   ```bash
   # Check SystemTools log format compliance
   grep -r 'logger\.\(debug\|info\)(' SystemTools/ | grep -v '\[.*\]' | wc -l
   # Should be 0 violations

   # Check Air-Side uses LogContext enum
   ssh dpm@10.0.1.53 "grep -r 'LOG_' ~/DPM-V2/sbc/src | grep -v 'LogContext::' | wc -l"
   # Should be 0 violations

   # Check Ground-Side uses StructuredLogger
   grep -r 'Log\.\(d\|i\|w\|e\)(' android/app/src | wc -l
   # Should be 0 (should use Timber/StructuredLogger)
   ```

3. **Enforce Protocol Changes Workflow:**
   - **STEP 1:** Update protocol/*.json file FIRST
   - **STEP 2:** Create [PROTOCOL] tagged commit
   - **STEP 3:** Update ALL domains to match
   - **STEP 4:** Test cross-domain compatibility
   - **NEVER** allow domain-specific implementations without protocol update

4. **Create Compliance Issues Immediately:**
   - Found 549 violations? Create CRITICAL issue
   - Block Phase completion until compliance restored
   - Do NOT allow manual fixes without architectural solution

### **Real Example - What Just Happened:**

**Problem Found:**
- SystemTools had 549 log statements without context tags
- Air-Side correctly enforces `LogContext` enum (protocol-compliant)
- SystemTools `logger.py` does NOT enforce protocol (non-compliant)

**Correct PM Response:**
1. ✅ STOP manual fixing (549 individual edits)
2. ✅ Identify root cause (logger doesn't enforce protocol)
3. ✅ Create CRITICAL issue #162
4. ✅ Require architectural fix (ProtocolLogger wrapper)
5. ✅ Update PM rules (this rule!)
6. ✅ Add protocol enforcement to regular checks

**Incorrect PM Response (Don't Do This):**
1. ❌ Let domain fix 549 logs manually
2. ❌ Move on after partial fix
3. ❌ Hope it doesn't happen again
4. ❌ Not check other domains for same issue

### **Why This Rule Exists:**
- **Cross-Domain Compatibility:** Protocols ensure domains can communicate
- **Single Source of Truth:** No duplication, no divergence
- **Maintainability:** Change protocol once, all domains follow
- **Quality:** Catch violations early, enforce standards

### **PM Compliance Checklist (Add to PM_START.md):**
```bash
# Add to regular PM startup checks
echo "=== Protocol Compliance Check ==="
echo "SystemTools log format violations:"
grep -r 'logger\.\(debug\|info\)(' SystemTools/ --include="*.py" | \
  grep -v '\[COMMAND\]' | grep -v '\[NETWORK\]' | grep -v '\[DISCOVERY\]' | \
  grep -v '\[CONFIG\]' | grep -v '\[SYSTEM\]' | grep -v '\[HEALTH\]' | \
  grep -v '\[CAMERA\]' | grep -v '\[STORAGE\]' | grep -v '\[SYNC\]' | \
  grep -v '\[UI\]' | wc -l
```

### **Related Issues:**
- #162 - SystemTools Protocol Non-Compliance (549 violations)
- #82 - Phase 1 Integration Testing (blocked by protocol violations)
- #159 - Log Context Protocol Violation (root cause: no enforcement)

---

---

## 🔗 Related Issues

**Issue #101:** [WORKFLOW][RESEARCH] PM Session Optimization
- Extended thinking usage guide
- Context management strategies
- Best practices and findings
- **Review before complex coordination tasks**

---

**Review this file before EVERY PM session!**
