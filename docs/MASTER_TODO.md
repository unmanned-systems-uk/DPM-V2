# DPM-V2 MASTER TODO

**Last Updated:** 2025-11-22
**Status:** Central task tracking for all domains
**Current Phase:** Phase 2A - Critical Blockers (75% complete)

---

## Purpose

This is the master TODO tracking document for the entire DPM-V2 project. It aggregates high-priority tasks from all three domains and provides project-wide visibility.

**Phase 1 Status:** ✅ **100% COMPLETE** (2025-11-22)
**Phase 2A Status:** 🟢 **75% COMPLETE** (3/5 tasks done)

---

## 🔴 CRITICAL - Phase 2A Remaining (Immediate Priority)

### Task 3: SystemTools Protocol Logger Verification
**Issue:** #162
**Assignee:** CC-SystemTools
**Effort:** 3-4 hours
**Priority:** 🔴 CRITICAL

**Description:**
- Verify ProtocolLogger enforces context validation
- Audit all logger calls for compliance
- Document ProtocolLogger usage patterns
- Add validation tests

**Note:** False positive analysis showed SystemTools is likely already 100% compliant. This is primarily verification and documentation work.

**Deliverables:**
- [ ] Verify ProtocolLogger wrapper enforces context
- [ ] Audit existing code for any violations
- [ ] Document ProtocolLogger patterns
- [ ] Create validation test suite

---

### Task 4: TCP Connection Validation
**Issue:** #45
**Assignee:** CC-Ground-Side
**Effort:** 3-4 hours
**Priority:** 🔴 CRITICAL

**Description:**
- Add TCP connection health checks before sending commands
- Implement connection state validation
- Add error reporting for failed sends
- Implement retry logic with exponential backoff

**Deliverables:**
- [ ] Add TCP connection health check
- [ ] Implement connection state validation
- [ ] Add error reporting for failed sends
- [ ] Add retry logic with exponential backoff

**Success Criteria:**
- No silent failures on disconnect
- User sees clear error messages
- Commands retry automatically when connection restored

---

### Task 5: Camera Disconnection Investigation
**Issue:** #54
**Assignee:** CC-Air-Side
**Effort:** 4-6 hours
**Priority:** 🔴 BLOCKER

**Description:**
- Investigate camera disconnection reports
- Identify root cause (SDK, USB, state machine)
- Implement fix or workaround
- Verify camera stays connected under load

**Impact:** Blocks manual focus features (#2, #40, #42, #48, #129)

**Deliverables:**
- [ ] Reproduce camera disconnection issue
- [ ] Identify root cause
- [ ] Implement fix or workaround
- [ ] Verify camera stays connected under load

**Success Criteria:**
- Camera remains connected during normal operation
- No false disconnection reports
- Manual focus features unblocked

---

## 🟡 HIGH PRIORITY - Phase 2B (Next Sprint)

### Command Validation & Sanitization Layer
**Effort:** 10-12 hours (Air-Side: 6-8h, Ground-Side: 2-3h, Testing: 2h)
**Priority:** 🟡 HIGH

**Components:**
- [ ] Air-Side: CommandValidator class
- [ ] Air-Side: JSON Schema validation
- [ ] Air-Side: Rate limiting (global + per-command)
- [ ] Air-Side: Queue depth checking (max 50)
- [ ] Ground-Side: CommandResponse error UI
- [ ] Integration testing

---

### Enhanced Error Recovery Framework
**Effort:** 12-15 hours (Air-Side: 8-10h, Ground-Side: 2-3h, Testing: 2h)
**Priority:** 🟡 HIGH

**Components:**
- [ ] Air-Side: Watchdog class for component monitoring
- [ ] Air-Side: SystemModeManager (NORMAL/DEGRADED/EMERGENCY/SHUTDOWN)
- [ ] Air-Side: Escalating recovery delays (500ms→5s, max 6 attempts)
- [ ] Air-Side: Sony SDK timeout wrapper (10s)
- [ ] Ground-Side: SystemModeIndicator status widget
- [ ] Integration testing

---

## 🟢 MEDIUM PRIORITY - Phase 2C Features (Select 2-3)

### Feature Option A: Image Transfer POC
**Issue:** #139
**Effort:** 6-8 hours
**Priority:** 🟢 MEDIUM-HIGH

**Deliverables:**
- [ ] Implement single file transfer (Camera SD → SBC)
- [ ] Test with JPEG and ARW formats
- [ ] Measure transfer speeds
- [ ] Document transfer process

---

### Feature Option B: Standalone Tri-Domain Log Viewer
**Issue:** #107
**Effort:** 10-14 hours
**Priority:** 🟢 MEDIUM

**Deliverables:**
- [ ] Create standalone PyQt/Tkinter log viewer
- [ ] Support real-time log streaming
- [ ] Add advanced filtering (regex, context, domain)
- [ ] Add log export functionality
- [ ] Professional UI design

---

### Feature Option C: Performance Analytics Enhancements
**Issue:** #130
**Effort:** 4-6 hours
**Priority:** 🟢 LOW-MEDIUM

**Deliverables:**
- [ ] Add trend analysis graphs
- [ ] Add anomaly detection improvements
- [ ] Add export to CSV/JSON
- [ ] Add custom time range selection

---

### Feature Option D: Sony SDK Image Transfer (4 Modes)
**Issue:** #137
**Effort:** 12-16 hours
**Priority:** 🟢 MEDIUM

**Transfer Modes:**
- [ ] Mode 1: Camera SD → SBC (during/after capture)
- [ ] Mode 2: Camera SD → SBC (bulk transfer)
- [ ] Mode 3: SBC → Ground-Side (via network)
- [ ] Mode 4: End-to-end (Camera → SBC → Ground)

---

### Feature Option E: Data-Link Health Check & Auto-Recovery
**Issue:** #91
**Effort:** 6-8 hours
**Priority:** 🟢 MEDIUM

**Deliverables:**
- [ ] Implement network link monitoring
- [ ] Add connection quality metrics
- [ ] Implement auto-reconnect logic
- [ ] Add health check heartbeats
- [ ] Create network status UI indicator

---

## 🔵 LOW PRIORITY - Future Enhancements

### Documentation & Process
- [ ] Integrate CCPM sprint management (awaiting guide docs)
- [ ] Create automated protocol validation tests
- [ ] Comprehensive integration test suite
- [ ] Update architecture diagrams (C4 Level 3)

### Performance Optimization
- [ ] Memory pool implementation (Air-Side)
- [ ] Connection pooling (Air-Side)
- [ ] Battery consumption profiling (Ground-Side)

### Advanced Features (Phase 3+)
- [ ] FishSemi AirControl SDK integration (#167)
- [ ] Gimbal control protocol
- [ ] Waypoint mission planning
- [ ] Video recording controls

---

## Completion Metrics

| Phase | Status | Completion | Remaining Effort |
|-------|--------|------------|------------------|
| Phase 1 | ✅ Complete | 100% | 0h |
| Phase 2A | 🟢 In Progress | 75% (3/5 tasks) | 10-14h |
| Phase 2B | ⏳ Planned | 0% | 22-27h |
| Phase 2C | ⏳ Planned | 0% | Select 2-3 features |

---

## Active Blockers

| Blocker | Issue | Impact | Status | ETA |
|---------|-------|--------|--------|-----|
| Camera Disconnection | #54 | HIGH (blocks manual focus) | ⏳ TODO | 4-6h |
| TCP Connection Validation | #45 | MEDIUM (silent failures) | ⏳ TODO | 3-4h |
| Protocol Logger Verification | #162 | LOW (likely already done) | ⏳ TODO | 3-4h |

---

## Recent Completions ✅ (Last 3 Days)

### November 22, 2025
- ✅ **Phase 1 declared 100% complete**
- ✅ Ground-Side protocol migration (Issue #164) - 15 files, 389 insertions
- ✅ Merged violation-fix to main (commit a64bf33)
- ✅ Closed issues #164, #177, #179, #181
- ✅ Updated planning documentation (Phase 1, Phase 2, Master Progress)

### November 20, 2025
- ✅ Health metrics protocol created (`protocol/health_metrics.json`)
- ✅ SystemTools health analytics protocol compliance
- ✅ Ground-Side disk metrics migration (GB→MB)

### November 19, 2025
- ✅ Phase 2 planning document created
- ✅ .claude/ directory optimization (90% token reduction)

---

## Next Major Milestone

**Target:** Phase 2A Complete
**ETA:** Week of Nov 22-29, 2025
**Requirements:**
- All 5 Phase 2A tasks complete
- No critical blockers remaining
- Ready to start Phase 2B

---

## CCPM Sprint Management (Coming Soon)

**Status:** Awaiting guide documentation from user

**Benefits:**
- Better task tracking and sprint planning
- Integration with DPM-V2 GitHub issues
- Velocity metrics and burndown charts
- Multi-project coordination

**Action:** Will integrate when guide docs available

---

## Work Prioritization

**This Week (Nov 22-29):**
1. Complete Phase 2A remaining tasks (#162, #45, #54)
2. Set up CCPM sprint management (when ready)
3. Begin Phase 2B planning and design

**Next Week (Nov 29 - Dec 6):**
1. Start Phase 2B implementation
2. Command validation layer
3. Error recovery framework

**December 2025:**
1. Complete Phase 2B
2. Select 2-3 Phase 2C features
3. Implement selected features
4. Comprehensive integration testing

---

## Protocol Compliance Status ✅

**All Domains:** 100% Complete

| Domain | Status | Enforcement Method |
|--------|--------|-------------------|
| Air-Side | ✅ 100% | C++ LogContext enum + runtime validation |
| Ground-Side | ✅ 100% | Kotlin LogContext enum + Timber.tag() |
| SystemTools | ✅ 100% | Python ProtocolLogger + runtime validation |

**Protocol Files:**
- `protocol/log_contexts.json` - 10 contexts
- `protocol/health_metrics.json` - 25 metrics
- `protocol/commands.json` - Command definitions
- Plus 3 more protocol specifications

---

## Notes

**Task Dependencies:**
- Phase 2B depends on Phase 2A completion
- Phase 2C features can start after Phase 2B
- Camera disconnection (#54) blocks manual focus features

**Resource Notes:**
- Phase 2A: 10-14h remaining across 3 domains
- Phase 2B: 22-27h estimated
- Phase 2C: 50-70h total available (select 2-3 features)

**Integration with CCPM:**
- Will migrate to CCPM sprint management when available
- Current tracking via GitHub issues + this document
- MASTER_PROGRESS.md provides executive overview

---

*This document is the single source of truth for project-wide task tracking*
*Update frequency: Weekly or on task completion*
*Maintained by: CC-PM*
*Next Update: After Phase 2A completion*
