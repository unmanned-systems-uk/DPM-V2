# Phase 1 Multi-Domain Testing - Executable Plan

**WHO:** CC-PM (Project Manager)
**Date:** 2025-11-13
**Test Coordination:** Issue #82
**Progress Tracking:** This file + Issue #82 updates

---

## ✅ Access Confirmed

- ✅ **SSH to Pi 5:** `ssh dpm@10.0.1.53` (key authentication working)
- ✅ **SystemTools Local:** Python 3.12.3, log_aggregator.py available
- ⏳ **ADB to H16:** Requires installation (`sudo apt install adb`)
- ✅ **User Available:** For H16 physical operations

---

## 🎯 Test Execution Strategy

### Phase A: Air-Side + SystemTools (Execute Now)
**Can Execute:** 26 tests (Pi 5 SSH + Local SystemTools)
**Blocked:** 0 tests
**Duration:** 2-3 hours

### Phase B: Ground-Side Integration (After ADB setup)
**Requires:** ADB installed + H16 connection
**Tests:** 6 tests
**Duration:** 1 hour

---

## 📝 Test Execution Log

**Format:** Each test logs: Status, Output, Issues, Evidence

---

# SUITE 1: Air-Side Domain Tests (13 tests)

## Test 1.1: ConfigManager - Load Default Configuration ✅

**Status:** READY TO EXECUTE
**Method:** SSH to Pi 5, check Docker logs

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -i 'config'"
```

**Expected:**
- "ConfigManager initialized" message
- "Configuration loaded" message
- No errors

**Actual Result:** [TO BE FILLED]

---

## Test 1.2: ConfigManager - Environment Override ✅

**Status:** READY TO EXECUTE
**Method:** Check which environment loaded (development vs production)

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -E 'environment|config.*loaded'"
```

**Expected:**
- Environment config loaded (development.json for dev mode)
- Overrides applied

**Actual Result:** [TO BE FILLED]

---

## Test 1.3: StructuredLogger - Console Sink (JSON Output) ✅

**Status:** READY TO EXECUTE
**Method:** Capture logs and validate JSON format

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 --tail=20 | head -5"
```

**Validation:**
```bash
# Extract one log line and validate JSON
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 --tail=50 | grep '^{' | head -1 | python3 -m json.tool"
```

**Expected:**
- Valid JSON output
- Fields: timestamp, level, context, message, thread, function, line

**Actual Result:** [TO BE FILLED]

---

## Test 1.4: StructuredLogger - File Sink (Rotation) ✅

**Status:** READY TO EXECUTE
**Method:** Check log files inside container

**Command:**
```bash
ssh dpm@10.0.1.53 "docker exec payload-manager ls -lh /var/log/dpm/"
ssh dpm@10.0.1.53 "docker exec payload-manager head -5 /var/log/dpm/air-side.jsonl"
```

**Expected:**
- air-side.jsonl exists
- JSON Lines format
- File size tracking for rotation

**Actual Result:** [TO BE FILLED]

---

## Test 1.5: StructuredLogger - Network Sink (UDP to SystemTools) ✅

**Status:** READY TO EXECUTE
**Method:** Start log_aggregator locally, check for Air-Side logs

**Commands:**
```bash
# Terminal 1: Start log aggregator
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py

# Check logs appear from Air-Side (10.0.1.53)
```

**Expected:**
- UDP packets received on port 5007
- Logs displayed in blue (Air-Side)
- Real-time streaming

**Actual Result:** [TO BE FILLED]

---

## Test 1.6: HealthMonitor - Metrics Collection ✅

**Status:** READY TO EXECUTE
**Method:** Check Docker logs for health metrics

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -i 'health'"
```

**Expected:**
- Health snapshots being collected
- Metrics categories: System, Camera, Network, Sync

**Actual Result:** [TO BE FILLED]

---

## Test 1.7: HealthMonitor - UDP Broadcast to Ground-Side ⏳

**Status:** READY TO EXECUTE
**Method:** Listen on UDP port 5004 for broadcasts

**Command:**
```bash
# Listen for health broadcasts
nc -ul 5004
```

**Expected:**
- UDP packets at ~5 Hz (200ms interval)
- JSON health data

**Actual Result:** [TO BE FILLED]

---

## Test 1.8: HealthMonitor - Threshold Warnings ✅

**Status:** READY TO EXECUTE
**Method:** Check logs for any threshold warnings

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -iE 'warn|threshold|critical'"
```

**Expected:**
- Warnings if thresholds exceeded
- No warnings if system healthy

**Actual Result:** [TO BE FILLED]

---

## Test 1.9: Protocol Commands - enable_log_streaming ⏳

**Status:** REQUIRES GROUND-SIDE CONNECTION
**Method:** Send command via Ground-Side or SystemTools

**Command:** [Requires TCP connection to port 5000]

**Expected:**
- Command acknowledged
- UDP stream to Ground starts

**Actual Result:** [TO BE FILLED - Requires Ground connection]

---

## Test 1.10: Protocol Commands - disable_log_streaming ⏳

**Status:** REQUIRES GROUND-SIDE CONNECTION
**Method:** Send command via Ground-Side

**Expected:**
- Command acknowledged
- UDP stream stops

**Actual Result:** [TO BE FILLED - Requires Ground connection]

---

## Test 1.11: Configuration Persistence ✅

**Status:** READY TO EXECUTE
**Method:** Check for local.json creation

**Command:**
```bash
ssh dpm@10.0.1.53 "docker exec payload-manager ls -la /app/config/"
```

**Expected:**
- default.json, development.json, production.json exist
- local.json created if runtime changes made

**Actual Result:** [TO BE FILLED]

---

## Test 1.12: Error Handling - Invalid Config ✅

**Status:** MANUAL TEST
**Method:** Create invalid JSON, restart, verify fallback

**Expected:**
- Error logged for invalid JSON
- Fallback to default config
- Service continues

**Actual Result:** [SKIP FOR NOW - Don't break running system]

---

## Test 1.13: Memory Leak Check (30-minute soak) ⏳

**Status:** LONG-RUNNING TEST
**Method:** Monitor memory over 30 minutes

**Command:**
```bash
# Initial memory
ssh dpm@10.0.1.53 "docker stats payload-manager --no-stream"

# After 30 minutes
ssh dpm@10.0.1.53 "docker stats payload-manager --no-stream"
```

**Expected:**
- Memory growth < 10 MB
- No crashes

**Actual Result:** [TO BE FILLED - Start at end of test session]

---

# SUITE 2: SystemTools Domain Tests (7 tests)

## Test 2.1: Log Aggregator - UDP Listener (Air-Side) ✅

**Status:** READY TO EXECUTE
**Method:** Start log_aggregator, verify Air-Side logs received

**Command:**
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py
```

**Expected:**
- UDP socket bound to 0.0.0.0:5007
- Air-Side logs displayed in blue
- Real-time updates

**Actual Result:** [TO BE FILLED]

---

## Test 2.2: Log Aggregator - TCP Listener (Ground-Side) ⏳

**Status:** BLOCKED - Requires ADB
**Method:** ADB bridge + Ground-Side logging

**Actual Result:** [BLOCKED - Need ADB setup]

---

## Test 2.3: Log Aggregator - Merged Timeline ⏳

**Status:** BLOCKED - Requires Ground-Side

**Actual Result:** [BLOCKED - Need both Air + Ground]

---

## Test 2.4: Log Aggregator - Filtering (Level) ✅

**Status:** READY TO EXECUTE
**Method:** Run with level filter

**Command:**
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --level=ERROR
```

**Expected:**
- Only ERROR level logs shown
- Counts correct

**Actual Result:** [TO BE FILLED]

---

## Test 2.5: Log Aggregator - Filtering (Domain) ⏳

**Status:** BLOCKED - Requires Ground-Side

**Actual Result:** [BLOCKED - Need both domains]

---

## Test 2.6: Log Aggregator - Export JSON ✅

**Status:** READY TO EXECUTE
**Method:** Collect logs, export to JSON

**Command:**
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --export-json=test_export.json
# Run for 30 seconds, then Ctrl+C
cat test_export.json | python3 -m json.tool | head -20
```

**Expected:**
- JSON file created
- Valid JSON array format

**Actual Result:** [TO BE FILLED]

---

## Test 2.7: Log Aggregator - Replay Mode ✅

**Status:** READY TO EXECUTE (after 2.6)
**Method:** Replay from exported JSON

**Command:**
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --replay=test_export.json
```

**Expected:**
- Logs loaded from file
- Display matches original

**Actual Result:** [TO BE FILLED]

---

# SUITE 3: Integration Tests (4 tests)

## Test 3.1: Air → SystemTools - Log Streaming ✅

**Status:** READY TO EXECUTE
**Method:** Full end-to-end test

**Commands:**
```bash
# Start SystemTools
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py

# Verify Air-Side is sending
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -i 'network.*systemtools'"
```

**Expected:**
- Logs transmitted via UDP
- Latency < 1 second
- No packet loss

**Actual Result:** [TO BE FILLED]

---

## Test 3.2: Air → Ground - Health Broadcasting ⏳

**Status:** BLOCKED - Requires H16 app

**Actual Result:** [BLOCKED - Need Ground-Side Health Dashboard]

---

## Test 3.3: Air → Ground - On-Demand Log Streaming ⏳

**Status:** BLOCKED - Requires H16 app

**Actual Result:** [BLOCKED - Need Ground-Side Log Viewer]

---

## Test 3.4: Tri-Domain Scenario ⏳

**Status:** BLOCKED - Requires H16 app

**Actual Result:** [BLOCKED - Need all three domains]

---

# SUITE 4: Performance Baseline (4 tests)

## Test 4.1: Log Throughput ✅

**Status:** READY TO EXECUTE
**Method:** Measure SystemTools reception rate

**Commands:**
```bash
# Start aggregator, count logs over 60 seconds
cd /home/anthony/DPM-V2/SystemTools
timeout 60 python3 log_aggregator.py | wc -l
```

**Expected:**
- Sustained rate > 500 logs/sec
- Packet loss < 1%

**Actual Result:** [TO BE FILLED]

---

## Test 4.2: Health Broadcast Timing ⏳

**Status:** READY TO EXECUTE
**Method:** Capture health packets, measure timing

**Command:**
```bash
# Capture 20 health packets
timeout 5 nc -ul 5004 | head -20
```

**Expected:**
- Average: 200ms ± 10ms
- Frequency: ~5 Hz

**Actual Result:** [TO BE FILLED]

---

## Test 4.3: Configuration Load Time ✅

**Status:** READY TO EXECUTE
**Method:** Check Docker logs for timing

**Command:**
```bash
ssh dpm@10.0.1.53 "docker logs payload-manager 2>&1 | grep -A2 'ConfigManager.*Loading'"
```

**Expected:**
- Load time < 100ms

**Actual Result:** [TO BE FILLED]

---

## Test 4.4: Memory Footprint ✅

**Status:** READY TO EXECUTE
**Method:** Check Docker stats

**Command:**
```bash
ssh dpm@10.0.1.53 "docker stats payload-manager --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}'"
```

**Expected:**
- Phase 1 overhead < 50 MB

**Actual Result:** [TO BE FILLED]

---

# SUITE 5: Reliability & Error Handling (4 tests)

## Test 5.1: Network Interruption - UDP Loss ⏳

**Status:** MANUAL TEST
**Method:** Block UDP port temporarily

**Expected:**
- No crashes
- Logs resume after unblock

**Actual Result:** [SKIP - Don't disrupt running system]

---

## Test 5.2: Disk Full - Log Rotation ⏳

**Status:** MANUAL TEST
**Method:** Artificially limit disk

**Expected:**
- Error logged
- Console logging continues
- No crash

**Actual Result:** [SKIP - Don't disrupt running system]

---

## Test 5.3: High CPU Load ⏳

**Status:** MANUAL TEST
**Method:** Run CPU stress test

**Expected:**
- Logging continues
- Health monitoring continues
- Latency < 1 second

**Actual Result:** [SKIP - Don't disrupt running system]

---

## Test 5.4: Restart Recovery ✅

**Status:** READY TO EXECUTE
**Method:** Restart container, verify clean startup

**Command:**
```bash
ssh dpm@10.0.1.53 "docker restart payload-manager && sleep 5 && docker logs payload-manager --tail=50"
```

**Expected:**
- Graceful shutdown
- Clean restart
- Config reloaded

**Actual Result:** [TO BE FILLED]

---

# Test Execution Summary

## Executable Now (Without ADB)

| Suite | Tests Ready | Tests Blocked | Total |
|-------|-------------|---------------|-------|
| 1. Air-Side | 9 | 2 | 11 |
| 2. SystemTools | 4 | 3 | 7 |
| 3. Integration | 1 | 3 | 4 |
| 4. Performance | 4 | 0 | 4 |
| 5. Reliability | 1 | 3 | 4 |
| **TOTAL** | **19** | **11** | **30** |

**Note:** Test 1.12, 5.1, 5.2, 5.3 skipped to avoid disrupting running system

## Execution Order

1. **Start SystemTools log_aggregator** (Terminal 1)
2. **Execute Air-Side tests** (1.1 - 1.11) via SSH
3. **Execute SystemTools tests** (2.1, 2.4, 2.6, 2.7)
4. **Execute Integration test** (3.1)
5. **Execute Performance tests** (4.1 - 4.4)
6. **Execute Reliability test** (5.4 - restart)
7. **Start memory leak test** (1.13 - 30 min soak)
8. **Document all results in Issue #82**

---

**Status:** Ready to begin test execution
**Duration Estimate:** 2-3 hours for Phase A (19 tests)
**Next:** Start SystemTools log_aggregator and begin Test 1.1
