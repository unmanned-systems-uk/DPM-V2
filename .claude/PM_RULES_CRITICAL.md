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

## 🎯 RULE 2: ALWAYS Use Carriage Return in tmux Commands

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

## 🎯 RULE 6: Efficient tmux Communication

### **Best Practices:**

1. **Be Specific and Complete:**
   ```bash
   ✅ "Please work on Issue #74 - Air-Side UDP log streaming. Check if StructuredLogger has UDP output capability. If not, implement UDP streaming to 10.0.1.83:5007 when log streaming is enabled." C-m

   ❌ "Work on #74" C-m
   # Too vague - domain needs to ask for clarification
   ```

2. **Include Context:**
   ```bash
   ✅ "Ground-Side → SystemTools integration is complete. Now implement Air-Side → SystemTools for Issue #74." C-m

   ❌ "Do Air-Side now" C-m
   # No context - what about Air-Side?
   ```

3. **Provide Issue Numbers:**
   ```bash
   ✅ "Please work on Issue #99 - Fix Dynamic IP Connection" C-m

   ❌ "Fix the IP thing" C-m
   # Domain can't find relevant issue
   ```

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

## 📋 PM Session Checklist

**Before Starting Work:**
- [ ] Read /home/anthony/.claude/CLAUDE.md (connection details)
- [ ] Read .claude/PM_START.md (startup protocol)
- [ ] Read .claude/MULTI_DOMAIN_COORDINATION.md (coordination framework)
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

**Review this file before EVERY PM session!**
