# DPM-V2 MASTER TODO
*Last Updated: 2025-11-04*
*Status: Central tracking document for all domain tasks*

## Purpose
This is the master TODO tracking document for the entire DPM-V2 project. It aggregates high-priority tasks from all three domains (Air-Side, Ground-Side, Development-Side) and provides project-wide visibility.

## Update Process
1. Domain TODOs are updated daily in `docs/<domain>/TODO.md`
2. This master file is updated weekly or when critical tasks change
3. Claude Code sessions update their domain TODO first, then propagate here

---

## 🔴 CRITICAL - Cross-Domain Issues (Immediate)

### Focus System Issues (Affects: Air + Ground)
- [ ] **Fix focus distance readback** [AIR+GROUND]
  - Air: Add `focal_distance_m` to UDP broadcast
  - Ground: Parse and display in FocusDistanceOverlay
  - Priority: MEDIUM - UI lacks feedback

- [ ] **Fix AF Hold in Manual Focus mode** [AIR+GROUND]
  - Air: Check SDK restrictions, implement mode switching
  - Ground: Update UI expectations
  - Priority: LOW - Workaround exists

### Documentation Sync
- [ ] **Update all PROGRESS_AND_TODO.md files** [ALL]
  - Move active tasks to domain TODO.md files
  - Keep PROGRESS_AND_TODO.md for historical tracking only

---

## 🟡 HIGH PRIORITY - This Week

### AIR-SIDE (Pi 5 SBC)
- [ ] Resolve property read errors (0x8402)
- [ ] Optimize PropertyLoader caching
- [ ] Improve camera reconnection logic

### GROUND-SIDE (Android H16)
- [ ] Add build timestamp to System Status UI
- [ ] Define comprehensive testing framework
- [ ] Test on real H16 hardware

### DEVELOPMENT-SIDE (SystemTools)
- [ ] Test documentation structure with live session
- [ ] Implement SSH-based Docker log streaming
- [ ] Add real-time graphs (latency, throughput)

---

## 🟢 MEDIUM PRIORITY - Next Sprint

### Project Management Features
- [ ] Create project status dashboard [DEV]
- [ ] Implement TODO management UI [DEV]
- [ ] Add Git integration metrics [DEV]

### Extended Camera Features
- [ ] Video recording controls [AIR+GROUND]
- [ ] Storage management [AIR+GROUND]
- [ ] Advanced exposure modes [AIR+GROUND]

### Gimbal Integration
- [ ] Define gimbal control protocol [AIR]
- [ ] Implement gimbal UI [GROUND]
- [ ] Add gimbal diagnostics [DEV]

---

## 🔵 LOW PRIORITY - Future

### Performance Optimization
- [ ] Memory pool implementation [AIR]
- [ ] Connection pooling [AIR]
- [ ] Battery consumption profiling [GROUND]

### Advanced Features
- [ ] Content download management [GROUND]
- [ ] Waypoint mission planning [AIR]
- [ ] Telemetry recording [DEV]

---

## Completion Metrics

| Domain | Phase | Status | Completion |
|--------|-------|--------|------------|
| Air-Side | Phase 1 | Complete | 100% |
| Ground-Side | Phase 1 | Testing | 85% |
| Development-Side | Phase 2 | Complete | 60% |
| **Overall** | **MVP** | **Testing** | **82%** |

## Active Blockers
1. Focus distance readback - Needs investigation
2. Testing framework definition - Pending
3. H16 hardware availability - Scheduled

## Next Major Milestone
**Target:** Phase 1 Complete for all domains
**Date:** End of Week (2025-11-08)
**Requirements:**
- All critical issues resolved
- Testing framework defined
- Hardware testing complete

---

*This document is the single source of truth for project-wide task tracking*
*Update frequency: Weekly or on critical changes*
*Maintained by: All domain leads via Claude Code*