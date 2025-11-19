# Task Agent Usage Guide - All Domains

**WHO:** All Domain Agents (Air-Side, Ground-Side, SystemTools, PM)
**Created:** 2025-11-19
**Purpose:** Exploit Task agents to maximize efficiency and preserve context

---

## 🎯 Core Principle: Use Task Agents Aggressively

**Task agents are a force multiplier.** Every domain should spawn Task agents liberally for:
- Multi-step investigations
- Repetitive work across multiple files
- Exploratory searches
- Parallel execution opportunities
- Anything consuming >5k tokens

**Default mindset:** "Should I use a Task agent for this?" (not "Can I do this manually?")

---

## What Are Task Agents?

**Task agents** are specialized Claude sub-agents that:
- Run autonomously with their own context
- Work in **parallel** (multiple agents simultaneously)
- Return a final report when complete
- **Don't pollute your main session context**
- Can use different models (haiku for speed, sonnet for complexity)

**Key insight:** Task agents have **separate 200k context budgets**. Your main session context is precious - delegate heavy work to Task agents!

---

## Available Task Agent Types

### 1. **Explore Agent** (Most Common)
**Best for:** Codebase exploration, finding files, searching code

**Thoroughness levels:**
- `"quick"` - Basic searches (< 1 minute)
- `"medium"` - Moderate exploration (1-3 minutes)
- `"very thorough"` - Comprehensive analysis (3-10 minutes)

**Example:**
```
Task(
  subagent_type="Explore",
  description="Find all USB camera code",
  prompt="Find all files related to USB camera operations in sbc/src/.
          Search for 'libusb', 'usb_', 'camera' keywords.
          Return list of files with brief description of each.
          Thoroughness: medium",
  model="haiku"
)
```

### 2. **Plan Agent**
**Best for:** Planning implementation steps, breaking down complex tasks

**Example:**
```
Task(
  subagent_type="Plan",
  description="Plan StructuredLogger migration",
  prompt="Plan migration of Ground-Side to use StructuredLogger for all logs.
          Analyze current Log.d/i/w/e usage, identify patterns, suggest migration strategy.
          Thoroughness: medium"
)
```

### 3. **general-purpose Agent**
**Best for:** Multi-step tasks, research, complex coordination

**Example:**
```
Task(
  subagent_type="general-purpose",
  description="Verify protocol compliance",
  prompt="Check all domains for protocol/log_contexts.json compliance:
          1. Verify SystemTools uses ProtocolLogger
          2. Check Air-Side uses LogContext enum
          3. Check Ground-Side uses StructuredLogger
          Return violation counts and specific examples.",
  model="sonnet"
)
```

---

## When to Use Task Agents

### ✅ USE Task Agents For:

**Multi-Step Investigations:**
- "Find all places where camera properties are set"
- "Analyze health monitoring flow across domains"
- "Check protocol compliance in all Python files"

**Repetitive Work:**
- Refactoring 30+ files to use new API
- Updating imports across entire directory
- Adding log contexts to 100+ log statements

**Exploratory Searches:**
- "How does UDP discovery work?"
- "Where is the camera SDK initialized?"
- "Find all network socket creation code"

**Parallel Opportunities:**
- Batch A: Update network/ files
- Batch B: Update gui/ files
- Batch C: Update utils/ files
- → Spawn 3 Task agents in parallel!

**Context-Heavy Operations:**
- Reading 10+ files to understand a feature
- Analyzing log outputs across sessions
- Comparing implementations across domains

### ❌ DON'T Use Task Agents For:

**Simple, Direct Operations:**
- Reading 1 specific file you already know the path to
- Single grep search with known pattern
- Editing 1-2 files
- Running a single command

**Interactive Work Requiring Feedback:**
- User needs to make decisions mid-task
- Incremental testing with user verification
- Debugging that requires user input

---

## Domain-Specific Use Cases

### Air-Side (C++ Development)

**Example 1: Sony SDK API Search**
```
Task(
  subagent_type="Explore",
  description="Find Sony SDK property setters",
  prompt="Search sbc/src/camera/ for all Sony SDK property setter calls.
          Look for patterns like: camera->Set*, SetProperty*, etc.
          Return list of properties we currently support.
          Thoroughness: medium",
  model="haiku"
)
```

**Example 2: Memory Leak Investigation**
```
Task(
  subagent_type="Explore",
  description="Find potential memory leaks",
  prompt="Search for 'new' without matching 'delete' in sbc/src/.
          Also check for malloc/free imbalance.
          Look for smart pointer usage.
          Return suspicious patterns.
          Thoroughness: very thorough",
  model="sonnet"
)
```

**Example 3: Parallel Refactoring**
```
# Spawn 3 agents in parallel:
Task(..., prompt="Refactor sbc/src/camera/ to use LogContext enum")
Task(..., prompt="Refactor sbc/src/network/ to use LogContext enum")
Task(..., prompt="Refactor sbc/src/command/ to use LogContext enum")
```

### Ground-Side (Android/Kotlin Development)

**Example 1: Find All Log.d Usage**
```
Task(
  subagent_type="Explore",
  description="Find raw Log usage",
  prompt="Find all Log.d/i/w/e calls in android/app/src/.
          Exclude StructuredLogger.kt and DPMApplication.kt.
          Group by file and count per file.
          Thoroughness: medium",
  model="haiku"
)
```

**Example 2: UI Component Analysis**
```
Task(
  subagent_type="Explore",
  description="Find all Composable screens",
  prompt="Find all @Composable functions in android/app/src/main/java/ui/.
          List screen names and their navigation routes.
          Identify which screens need StructuredLogger integration.
          Thoroughness: medium"
)
```

**Example 3: Protocol Implementation Check**
```
Task(
  subagent_type="general-purpose",
  description="Verify command implementations",
  prompt="Check which protocol/commands.json commands are implemented in Ground-Side.
          Compare protocol file to NetworkClient.kt and ProtocolMessages.kt.
          Return list of unimplemented commands.
          Thoroughness: medium"
)
```

### SystemTools (Python Development)

**Example 1: Import Analysis** (What SystemTools did today!)
```
Task(
  subagent_type="Explore",
  description="Find old logger imports",
  prompt="Find all files using 'from utils.logger import logger'.
          List files and count logger calls per file.
          Prioritize by call count (refactor high-usage files first).
          Thoroughness: quick",
  model="haiku"
)
```

**Example 2: GUI Tab Discovery**
```
Task(
  subagent_type="Explore",
  description="Find all GUI tabs",
  prompt="Find all tab_*.py files in SystemTools/gui/.
          List tab names, their classes, and main functions.
          Check which tabs use network clients.
          Thoroughness: medium"
)
```

**Example 3: Batch Refactoring** (Exactly what SystemTools is doing!)
```
# Spawn parallel agents for different directories:
Task(..., prompt="Refactor SystemTools/analytics/ to protocol_logger")
Task(..., prompt="Refactor SystemTools/network/ to protocol_logger")
Task(..., prompt="Refactor SystemTools/gui/ to protocol_logger")
```

### PM (Project Management)

**Example 1: Protocol Compliance Check**
```
Task(
  subagent_type="Explore",
  description="Run protocol compliance audit",
  prompt="Check all domains for protocol violations:
          1. SystemTools: grep for logger calls without context
          2. Ground-Side: grep for raw Log.d usage
          3. Verify protocol/log_contexts.json exists and is complete
          Return violation counts and examples.
          Thoroughness: medium",
  model="haiku"
)
```

**Example 2: Integration Test Verification**
```
Task(
  subagent_type="general-purpose",
  description="Verify Phase 1 tests",
  prompt="Check status of 5 Phase 1 integration tests:
          1. Read test definitions from Issue #82
          2. Check SystemTools logs for test execution
          3. Verify each test PASS/FAIL status
          4. Identify any blockers
          Return test status matrix.
          Thoroughness: medium"
)
```

**Example 3: Domain Progress Monitoring**
```
Task(
  subagent_type="Explore",
  description="Check all domain progress",
  prompt="Check progress across all domains:
          1. Capture tmux session outputs (TOOLS, GROUND, AIR)
          2. Identify what each domain is working on
          3. Check for errors or blocked status
          4. Estimate completion percentage
          Return concise status report.
          Thoroughness: quick",
  model="haiku"
)
```

---

## Best Practices

### 1. **Use Parallel Task Agents**
When you have independent batches of work:
```
# ✅ GOOD - Spawn 3 agents in single message (parallel):
Task(..., prompt="Batch A")
Task(..., prompt="Batch B")
Task(..., prompt="Batch C")

# ❌ BAD - Spawn sequentially (slow):
Task(..., prompt="Batch A")
[wait for result]
Task(..., prompt="Batch B")
[wait for result]
```

### 2. **Choose the Right Model**
```
model="haiku"   # Fast, cheap - Use for: searches, counts, simple analysis
model="sonnet"  # Balanced - Use for: refactoring, complex analysis (default)
model="opus"    # Powerful - Use for: architecture decisions (rarely needed)
```

### 3. **Write Detailed Prompts**
Task agents are stateless - you can't guide them mid-task!

```
# ❌ BAD (vague):
Task(prompt="Check the logs")

# ✅ GOOD (specific):
Task(prompt="Search SystemTools/network/log_listeners.py for all logger.info() calls.
            Count total calls, group by log context.
            Return list showing: context, line number, message preview.
            Also note any calls missing context parameter.
            Thoroughness: medium")
```

### 4. **Specify Thoroughness Level**
```
"quick"          # < 1 minute - Surface-level search
"medium"         # 1-3 minutes - Balanced (default for most tasks)
"very thorough"  # 3-10 minutes - Deep analysis across many locations
```

### 5. **Preserve Your Context**
Ask yourself: "Will this consume >5k tokens?"

```
# ❌ Consumes YOUR context:
Reading 10 files manually
Running 20 grep searches
Analyzing complex code flow

# ✅ Uses Task agent context (free for you):
Task(prompt="Read these 10 files and analyze...")
```

---

## Efficiency Gains

**Example: SystemTools Refactoring (Today)**

**Without Task Agents:**
- SystemTools reads 549 files manually
- Updates each file one by one
- Context exhausted after ~100 files
- Session restart required
- **Total time:** 3-4 hours

**With Task Agents (What SystemTools is doing):**
- Spawn 3-4 parallel Task agents
- Each handles a batch (analytics/, network/, gui/)
- Agents work simultaneously
- Main context preserved for coordination
- **Total time:** 30-60 minutes

**Efficiency gain:** 3-4x faster! 🚀

---

## Anti-Patterns to Avoid

### ❌ **Anti-Pattern 1: Manual Iteration**
```
# BAD - Reading 30 files manually:
for file in files:
    Read(file)
    Analyze...
    Update...
# → Consumes massive context!
```

**✅ Solution:**
```
Task(prompt="Read all 30 files in network/ directory.
            Update each to use protocol_logger.
            Return summary of changes.")
```

### ❌ **Anti-Pattern 2: Sequential Task Agents**
```
# BAD - Sequential (slow):
Task(prompt="Do batch A")
[wait]
Task(prompt="Do batch B")
[wait]
```

**✅ Solution:**
```
# GOOD - Parallel (fast):
[In single message]
Task(prompt="Do batch A")
Task(prompt="Do batch B")
Task(prompt="Do batch C")
```

### ❌ **Anti-Pattern 3: Vague Prompts**
```
# BAD - Agent doesn't know what you want:
Task(prompt="Check the code")
```

**✅ Solution:**
```
# GOOD - Clear, actionable, specific:
Task(prompt="Search sbc/src/camera/ for all Sony SDK error handling.
            Look for try/catch blocks and error return codes.
            List files with error handling and files without.
            Recommend which files need better error handling.
            Thoroughness: medium")
```

---

## When to Resume vs. Spawn New

Task agents can be **resumed** if you need to continue previous work:

```
# First execution:
task_id = Task(...)

# Later, resume instead of spawning new:
Task(resume=task_id, prompt="Continue with additional analysis...")
```

**Use resume when:**
- Following up on previous Task agent's findings
- Agent had relevant context you want to preserve
- Iterative refinement of previous analysis

**Spawn new when:**
- Completely different task
- Fresh perspective needed
- Previous agent completed successfully

---

## Measuring Success

**Good indicators you're using Task agents well:**

✅ Your main session context stays low (<50k tokens used)
✅ Complex investigations complete in <10 minutes
✅ You spawn 2+ Task agents per session
✅ Parallel work happens (multiple agents simultaneously)
✅ You rarely read >5 files manually

**Bad indicators (underusing Task agents):**

❌ Main session context >100k tokens
❌ Reading 10+ files manually
❌ Spending 30+ minutes on exploratory searches
❌ Never spawning Task agents
❌ Sequential processing of independent work

---

## Quick Reference: Task Agent Decision Tree

```
┌─ Need to do work? ─────────────────────────────┐
│                                                 │
├─ Is it 1-2 simple operations?                  │
│  └─ YES → Do it directly (Read, Grep, Edit)    │
│  └─ NO → Continue...                            │
│                                                  │
├─ Will it take >5k tokens?                       │
│  └─ YES → Use Task agent                        │
│  └─ NO → Continue...                             │
│                                                  │
├─ Is it exploratory/investigative?               │
│  └─ YES → Use Task agent (Explore)              │
│  └─ NO → Continue...                             │
│                                                  │
├─ Is it repetitive across many files?            │
│  └─ YES → Use Task agent                        │
│  └─ NO → Continue...                             │
│                                                  │
├─ Are there parallel opportunities?              │
│  └─ YES → Spawn multiple Task agents            │
│  └─ NO → Maybe do it directly                   │
│                                                  │
└─ When in doubt → USE TASK AGENT! ───────────────┘
```

---

## Examples From Real Work (2025-11-19)

### SystemTools: Issue #162 Refactoring
**Task:** Fix 549 log violations across 34 files

**Approach:**
```python
# Spawned parallel Task agents:
Task(prompt="Refactor analytics/ to protocol_logger")    # 4 files
Task(prompt="Refactor network/ to protocol_logger")      # 7 files
Task(prompt="Refactor gui/ to protocol_logger")          # 15 files
# ... etc.
```

**Result:** 54% complete in ~30 minutes, working in parallel

### PM: Protocol Compliance Check
**Task:** Discover protocol violations across all domains

**What COULD have been done:**
```python
Task(
  subagent_type="Explore",
  prompt="Audit all domains for protocol compliance:
          1. Check SystemTools for logger violations
          2. Check Ground-Side for raw Log usage
          3. Check Air-Side for LogContext compliance
          4. Compare all domains to protocol/log_contexts.json
          Return violation counts with specific examples.
          Thoroughness: medium"
)
```

**Result:** Would have discovered BOTH #162 (SystemTools) and #164 (Ground-Side) violations in single Task agent call!

---

## Summary

**Key Takeaway:** Task agents are not just a convenience - they're a **strategic tool** for efficient development.

**Default mindset for ALL domains:**
- "Can I parallelize this?" → Spawn multiple Task agents
- "Will this consume my context?" → Use Task agent
- "Is this exploratory?" → Use Explore agent
- "Is this repetitive?" → Use Task agent

**Remember:** Your 200k context budget is precious. Task agents have their own budgets - exploit them aggressively!

---

**Related Documentation:**
- `.claude/PM_RULES_CRITICAL.md` - PM-specific rules (consider adding RULE 12)
- `.claude/MULTI_DOMAIN_COORDINATION.md` - Cross-domain coordination
- Claude Code docs on Task agents (if available)

---

**Version:** 1.0
**Last Updated:** 2025-11-19
**Applies To:** All Domains (Air-Side, Ground-Side, SystemTools, PM)
