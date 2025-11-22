# Project Manager Start Protocol - Reference Guide

**Purpose:** Background information and detailed procedures for PM session startup
**Executable Command:** `/start-pm` (slash command contains the actual workflow)

**Use this document for:** Understanding PM workflow details, troubleshooting, learning the rationale behind procedures.

---

## Overview

The PM (Project Manager) role coordinates multi-domain development across:
- **Air-Side**: Raspberry Pi 5 (C++ payload manager)
- **Ground-Side**: Android H16 (Kotlin app)
- **SystemTools**: Development PC (Python tools)

**Primary Responsibilities:**
- Real-time monitoring via tmux sessions
- Protocol synchronization enforcement
- Issue tracking and delegation
- Status reporting to user
- Blocker escalation

---

## Session Start Workflow

**Quick Start:** Type `/start-pm` to execute the 7-step startup checklist.

**The 7 Steps:**

### Step 0: Power-Cut Recovery (Conditional)
If system was rebooted or session lost, run recovery script to reconstruct state.

### Step 1: Verify tmux Sessions
Ensure all domain AI agents are running in their dedicated tmux sessions.

### Step 2: Network Connectivity
Verify Pi 5 (10.0.1.53) and H16 (10.0.1.92) are reachable.

### Step 3: Open Issues
Review critical and in-progress GitHub issues for context.

### Step 4: Git Status
Check repository state, recent commits, and unpushed work.

### Step 5: Domain Status Check
Scan tmux sessions to see what each domain is currently working on.

### Step 6: CCPM Capability Database
Verify capability database is accessible for duplication prevention.

### Step 7: Protocol Compliance Check
Scan codebase for protocol violations (hardcoded values, raw log usage).

---

## Protocol Compliance (CRITICAL)

**Single Source of Truth:** `protocol/*.json` files

All domains MUST enforce protocol compliance at runtime:
- **Air-Side**: LogContext enum (C++)
- **Ground-Side**: StructuredLogger with context parameter (Kotlin)
- **SystemTools**: ProtocolLogger wrapper (Python)

**Protocol Files:**
```
protocol/log_contexts.json       - 8 log contexts (COMMAND, NETWORK, etc.)
protocol/commands.json           - Command definitions
protocol/health_broadcast.json   - Health metrics format
protocol/log_request.json        - On-demand log request format
protocol/log_response.json       - Log response format
```

**Violation Detection:**
PM startup checks for hardcoded log contexts and raw log usage. Any violations trigger CRITICAL issue creation.

---

## CCPM Capability Database

**Purpose:** Prevent duplicate development across 515 registered capabilities.

**Query Workflow:**
```bash
cd /home/anthony/ccpm-workspace/production/ccpm-client/python
export CCPM_API_KEY="CCPM-System-FLqZDWyXLfbpS9y6QgswKkEzMwxMs6FA"
python3 query_capability.py "<keywords>" --strict
```

**Exit codes:**
- `1` = Capability exists (duplication warning)
- `0` = Not found (safe to implement)

**Distribution:**
- Air-Side: 150 capabilities
- Ground-Side: 120 capabilities
- SystemTools: 200 capabilities
- Cross-Domain: 45 capabilities

---

## Real-Time Monitoring

**See:** `.claude/PM_MONITORING_PROTOCOL.md` for detailed monitoring procedures.

**Quick Reference:**
- Every 15 min: Scan tmux sessions for errors/completions
- Every 30 min: Status report to user
- On-demand: Deep dive into specific domain activity

**Monitoring Commands:**
```bash
tmux capture-pane -t DPM-SYSTEM -p | tail -30
tmux capture-pane -t DPM-GROUND -p | tail -30
tmux capture-pane -t DPM-AIR -p | tail -30
tmux capture-pane -t DPM-TOOLS -p | tail -30
```

---

## Troubleshooting

**See:** `.claude/PM_TROUBLESHOOTING.md` for common issues and resolutions.

**Quick Issues:**
- tmux session not responding
- Domain appears stuck
- Network connectivity lost

---

## Related Documentation

- `.claude/commands/start-pm.md` - **EXECUTABLE slash command** (primary)
- `.claude/PM_MONITORING_PROTOCOL.md` - Monitoring loops and coordination
- `.claude/PM_TROUBLESHOOTING.md` - Common issues and resolutions
- `.claude/MULTI_DOMAIN_COORDINATION.md` - Coordination framework
- `.claude/CONNECTION_DETAILS.md` - Network and device details
- `.claude/PLATFORM_VERIFICATION.md` - Platform checks
- `.claude/DPM_MASTER_START.md` - Multi-agent orchestration (advanced)

---

**Last Updated:** 2025-11-22
**Type:** Reference Documentation
**Executable Command:** `/start-pm`
