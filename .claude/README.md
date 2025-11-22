# .claude/ Directory Guide

**Purpose:** Central configuration and documentation for DPM-V2 Claude Code sessions

**Last Updated:** 2025-11-22

---

## Quick Start

**Starting a session:**
- PM (Project Manager): `/start-pm`
- PM Workflow (Admin/Docs): `/start-pm-workflow`
- Air-Side (Pi 5 C++): `/start-air`
- Ground-Side (Android Kotlin): `/start-ground`
- SystemTools (Python): `/start-tools`

**Ending a task:**
- Air-Side: `/eot-air`
- Ground-Side: `/eot-ground`
- SystemTools: `/eot-tools`

---

## Directory Structure

### Slash Commands (`commands/`)
Executable workflows loaded on-demand:

```
commands/
├── start-pm.md              PM session (161 lines)
├── start-pm-workflow.md     PM admin/docs session (201 lines)
├── start-air.md             Air-Side session (115 lines)
├── start-ground.md          Ground-Side session (126 lines)
├── start-tools.md           SystemTools session (133 lines)
├── eot-air.md               Air-Side task completion (120 lines)
├── eot-ground.md            Ground-Side task completion (121 lines)
├── eot-tools.md             SystemTools task completion (121 lines)
├── issue.md                 GitHub issue helper (286 lines)
└── sos.md                   Emergency help (158 lines)
```

**Total:** 10 slash commands

---

### Reference Documentation (Root)

**Session Management:**
- `SESSION_START.md` - General session start guide (215 lines)
- `LAST_SESSION.md` - Most recent session summary (updated at EOD)
- `PM_START.md` - PM session reference (148 lines)
- `PM_MONITORING_PROTOCOL.md` - PM monitoring procedures (241 lines)
- `PM_TROUBLESHOOTING.md` - PM common issues (52 lines)

**Rules & Protocols:**
- `RULES_CRITICAL.md` - Top-level critical rules (89 lines)
- `PM_RULES_CRITICAL.md` - PM-specific rules (706 lines)
- `DOMAIN_AGENT_RULES.md` - Shared domain agent rules (109 lines)
- `TASK_COMPLETION_PROTOCOL.md` - Task completion workflow (67 lines)
- `TMUX_COMMUNICATION_PROTOCOL.md` - tmux messaging protocol (504 lines)

**Coordination & Architecture:**
- `MULTI_DOMAIN_COORDINATION.md` - Multi-domain workflows (452 lines)
- `SYSTEMTOOLS_COORDINATION.md` - SystemTools coordination (155 lines)
- `CONNECTION_DETAILS.md` - Network/device details (280 lines)
- `PLATFORM_VERIFICATION.md` - Platform checks (245 lines)
- `ARCHITECTURE_UPDATE_RULES.md` - Architecture change process (312 lines)

**Domain-Specific:**
- `AIR_SIDE_RTC_TEST_PLAN.md` - Air-Side test plan (384 lines)
- `DPM_MASTER_START.md` - Multi-agent orchestrator (269 lines)

**Historical/Reference:**
- `LESSONS_LEARNED_CRITICAL.md` - Historical lessons (484 lines)
- `COMPRESSION_EMERGENCY.md` - Emergency compression guide (52 lines)

**Tracking:**
- `CCPM_CAPABILITY_TRACKING.md` - CCPM integration guide (108 lines)
- `DOC_SIZE_AUDIT.md` - Documentation size audit (274 lines)
- `MASTER_OPTIMIZATION_TODO.md` - Optimization roadmap (created 2025-11-22)

**Migration Docs:**
- `AGENT_MIGRATION_SUMMARY.md` - Agent architecture migration (176 lines)
- `AGENT_SPAWN_HELPER.md` - Agent spawning guide (89 lines)
- `PROTOCOL_VIOLATION_FIX_COORDINATION.md` - Protocol fix coordination (248 lines)

**Phase-Specific:**
- `DPM_V2_PHASE_1B_SETUP.md` - Phase 1B setup (348 lines)
- `PM_EOD_TASKS.md` - PM EOD tasks (286 lines)

---

### Agent Definitions (`agents/`)

Domain agent identity files:

```
agents/
├── air-side/
│   └── AGENT_DEFINITION.md
├── ground-side/
│   └── AGENT_DEFINITION.md
├── pm/
│   └── AGENT_DEFINITION.md
└── system-tools/
    └── AGENT_DEFINITION.md
```

---

### Archive (`archive/`)

Historical dated documents:

```
archive/
├── PM_EOD_2025-11-19.md         End of day report (388 lines)
└── PM_NEXT_SESSION_2025-11-19.md Next session plan (213 lines)
```

**Note:** Use `LAST_SESSION.md` pattern going forward instead of dated files.

---

## Key Principles

### 1. On-Demand Loading
- Slash commands contain executable workflows
- Reference docs consulted only when needed
- Reduces token overhead by ~90%

### 2. Single Source of Truth
- `protocol/*.json` - Protocol specifications (not in .claude/)
- CCPM database - Capability registry (not duplicated in docs)
- LAST_SESSION.md - Session handoff (not dated files)

### 3. Size Guidelines (CCPM)
- Session start commands: ≤100 lines (ideal)
- Slash commands: ≤200 lines (practical limit)
- Reference docs: ≤300 lines (exceptions for historical/test docs)

### 4. No Duplication
- Shared content extracted to common files
- Examples: DOMAIN_AGENT_RULES.md shared by all domains
- TASK_COMPLETION_PROTOCOL.md referenced by all agents

---

## Common Tasks

### Starting a Session
```bash
/start-pm              # Full PM session
/start-pm-workflow     # Admin/docs only
/start-air             # Air-Side development
/start-ground          # Ground-Side development
/start-tools           # SystemTools development
```

### Completing a Task
```bash
/eot-air               # Air-Side reports to PM
/eot-ground            # Ground-Side reports to PM
/eot-tools             # SystemTools reports to PM
```

### Finding Information
- **Protocol specs:** `~/DPM-V2/protocol/*.json`
- **Capabilities:** Query CCPM database (not static docs)
- **Last session:** `.claude/LAST_SESSION.md`
- **Critical rules:** `.claude/RULES_CRITICAL.md`

---

## Optimization History

**2025-11-22:** Major optimization sprint
- Consolidated 9 → 4 start commands
- Eliminated 720-line redundant capability list
- Created 3 EOT enforcement commands
- Archived dated PM documents
- 90% token overhead reduction

**See:** `MASTER_OPTIMIZATION_TODO.md` for ongoing optimization roadmap

---

## File Naming Conventions

**Patterns:**
- `*_CRITICAL.md` - Critical/mandatory reading
- `PM_*.md` - PM-specific documentation
- `*_PROTOCOL.md` - Protocol/procedure documentation
- `*_2025-*.md` - Dated files (should be archived)
- `start-*.md` - Session start commands
- `eot-*.md` - End of task commands

---

## Getting Help

**Emergency:**
- `/sos` - Emergency help command

**Documentation Issues:**
- Check `MASTER_OPTIMIZATION_TODO.md` for known issues
- Report problems via GitHub issues

**Session Confusion:**
- Read `SESSION_START.md` for general guidance
- Read domain-specific start command for details

---

**Maintained by:** CC-PM (Project Manager)
**Architecture:** On-demand slash commands + reference documentation
**Goal:** Minimize token overhead while maintaining full functionality
