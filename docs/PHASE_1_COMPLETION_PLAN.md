# Phase 1 Completion Plan - Issue #69

**Status**: 85% Complete → Target: 100%
**Remaining Effort**: 4-6 hours
**Date**: 2025-11-19

## Completed ✅

### Gap 1: Structured Logging (100% COMPLETE)
- ✅ Air-Side StructuredLogger with protocol-compliant contexts
- ✅ Ground-Side Log Integration to SystemTools
- ✅ SystemTools Tri-Domain Log Aggregation
- ✅ Ground-Side Log Viewer UI (LogViewerScreen.kt)
- ✅ SystemTools Log Viewer (tab_logs.py)
- ✅ JSON structured logging with size-based rotation (50MB, 3 files)

### Gap 2: Health Monitoring (70% COMPLETE)
- ✅ Health database (`performance.db`) with 62,671+ snapshots
- ✅ Analytics Dashboard (`tab_analytics.py`)
- ✅ Comprehensive metrics (CPU, memory, disk, network, camera, TCP/UDP)
- ⚠️ UDP broadcast frequency - NEEDS VERIFICATION
- ⚠️ Threshold alerts - NEEDS IMPLEMENTATION/VERIFICATION
- ⚠️ 3-tier storage (RAM/Disk/Summary) - NEEDS VERIFICATION

### Gap 3: Configuration Management (85% COMPLETE)
- ✅ SystemTools Config UI (tab_config.py)
- ✅ Ground-Side Advanced Settings (AdvancedSettingsScreen.kt)
- ✅ Air-Side config commands (system.get_config, system.update_config)
- ✅ Protocol defines comprehensive config structure
- ✅ Config-driven architecture (hardcoded values moved to config)
- ⚠️ Runtime config updates - NEEDS TESTING
- ⚠️ Ground-Side Configuration Manager - TODO (Add API for H16 config management)

## Remaining Work

### Task 1: Verify & Configure UDP Broadcast Frequencies (2 hours)

**Config Parameters** (from `protocol/commands.json`):
```json
{
  "timing": {
    "health_interval_ms": 5000,      // Health broadcast (target: 5s per spec)
    "status_interval_ms": 1000,      // Camera status broadcast (1s)
    "heartbeat_interval_ms": 1000    // Heartbeat (1s per protocol)
  },
  "health": {
    "monitor_enabled": true,
    "interval_ms": 5000,
    "broadcast_enabled": true
  }
}
```

**Steps:**
1. Fix API `send_command()` to capture responses (OR use direct UDP listener)
2. Query current Air-Side config: `system.get_config`
3. Verify broadcast intervals match spec
4. Test runtime update: `system.update_config({'timing.health_interval_ms': 5000})`
5. Verify changes persist after container restart
6. Document configurable broadcast frequencies in user guide

**Success Criteria:**
- [ ] Health broadcasts every 5 seconds (configurable)
- [ ] Config changes via API without rebuild
- [ ] Changes persist across restarts

---

### Task 2: Verify 3-Tier Storage Strategy (1 hour)

**Config Parameters**:
```json
{
  "health": {
    "ram_buffer_size": 360,           // 30min at 5s interval (360 snapshots)
    "disk_retention_days": 7,         // 7 days on disk
    "summary_retention_years": 1      // 1 year summary data
  }
}
```

**Steps:**
1. Check `performance.db` schema for summary tables
2. Verify RAM buffer implementation in health monitoring code
3. Check disk retention logic (7-day cleanup)
4. Verify summary aggregation (1-year retention)
5. Query database to confirm data retention matches config

**Success Criteria:**
- [ ] RAM buffer holds 30min (360 snapshots at 5s)
- [ ] Disk stores 7 days of detailed metrics
- [ ] Summary table holds 1 year of aggregated data
- [ ] Old data automatically cleaned up

---

### Task 3: Implement Threshold Alerts (1.5 hours)

**Config Parameters** (from `protocol/system_properties.json`):
- CPU > 80% = Warning, > 95% = Critical
- Memory < 200MB = Warning, < 100MB = Critical
- Battery < 20% = Warning, < 10% = Critical
- Temperature > 75°C = Warning, > 85°C = Critical

**Steps:**
1. Add alert threshold checks in health monitoring loop
2. Implement alert notification system (log + UI indicator)
3. Add alert history to `performance.db`
4. Display active alerts in Analytics Dashboard
5. Test threshold triggers with simulated metrics

**Success Criteria:**
- [ ] Alerts trigger when thresholds exceeded
- [ ] Alerts visible in Analytics Dashboard
- [ ] Alert history stored in database
- [ ] Configurable thresholds (via config.json)

---

### Task 4: Ground-Side Configuration Manager (1.5 hours)

**Current State:**
- ✅ Ground-Side has AdvancedSettingsScreen.kt
- ✅ SettingsManager.kt handles local settings
- ⚠️ No API for remote Ground-Side config queries (like Air-Side has)

**Requirements:**
- Add Ground-Side API endpoint: `ground_side.get_config()`
- Add Ground-Side API endpoint: `ground_side.update_config(updates)`
- H16 config structure similar to Air-Side (network, logging, health, etc.)
- SystemTools Config tab can manage both Air-Side AND Ground-Side config

**Steps:**
1. Add ADB command interface for Ground-Side config queries
2. Implement `ground_side.get_config()` in `ground_side_controller.py`
3. Implement `ground_side.update_config()` in `ground_side_controller.py`
4. Update SystemTools Config UI to show both domains
5. Test runtime config changes on H16

**Success Criteria:**
- [ ] Can query Ground-Side config via API
- [ ] Can update Ground-Side config via API
- [ ] Changes visible in H16 Advanced Settings
- [ ] Changes persist across H16 restarts

---

### Task 5: Testing & Documentation (1 hour)

**Testing:**
1. End-to-end test: Change Air-Side health interval via SystemTools Config UI
2. End-to-end test: Change Ground-Side log level via SystemTools Config UI
3. Verify all Phase 1 success criteria
4. HITL test: Monitor health broadcasts on network
5. HITL test: Trigger threshold alerts with load test

**Documentation:**
1. Update issue #69 with completion checklist
2. Document configurable parameters in user guide
3. Create ADR for configuration management architecture
4. Update Phase 1 status in architecture docs
5. Record Phase 1 achievements in CHANGELOG

**Success Criteria:**
- [ ] All Phase 1 success criteria verified
- [ ] Documentation complete
- [ ] Issue #69 ready to close
- [ ] Ready to start Phase 2

---

## Phase 1 Success Criteria (Final Checklist)

### Structured Logging:
- [x] Air logs visible in Ground-Side Log Viewer
- [x] SystemTools shows merged Air+Ground logs
- [x] JSON format with structured contexts
- [x] Size-based rotation (50MB, 3 files)

### Health Monitoring:
- [x] Health Dashboard displays metrics
- [ ] Real-time threshold alerts **← NEEDS WORK**
- [ ] UDP broadcast every 5 seconds (configurable) **← NEEDS VERIFICATION**
- [ ] 3-tier storage (30min RAM / 7day disk / 1year summary) **← NEEDS VERIFICATION**

### Configuration Management:
- [x] All hardcoded values in config.json
- [ ] Config changes via UI (no rebuild) - Air-Side **← NEEDS TESTING**
- [ ] Config changes via UI (no rebuild) - Ground-Side **← TODO**
- [x] Hierarchical JSON config structure
- [x] Runtime updates supported (protocol level)

---

## Dependencies & Blockers

**API Response Handling**:
- Current `send_command()` only confirms command sent
- Need to capture TCP/UDP responses for config queries
- Options:
  1. Add response listener to API (proper solution)
  2. Use direct UDP packet capture for testing (workaround)
  3. Check container logs for config values (workaround)

**Ground-Side Config API**:
- Requires ADB command interface design
- May need H16 app update to expose config via ADB

---

## Next Steps

1. **Start with Task 1**: Verify/configure broadcast frequencies (can test without API fix)
2. **Task 2 & 3**: Database verification and alerts (independent of API)
3. **Task 4**: Ground-Side config manager (parallel development)
4. **Task 5**: Final testing and documentation

**Estimated Timeline**: 1-2 days to complete Phase 1

---

## Notes

- User requested: "UDP broadcast frequency as configurable setting"
- User requested: "Add Ground-Side Configurator" (not yet implemented)
- Protocol already defines all necessary config parameters
- Main gap is API response handling + Ground-Side config interface
