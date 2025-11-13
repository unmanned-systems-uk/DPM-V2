# Phase 1 Foundation Infrastructure - Testing Plan

**Issue:** #72
**Components:** ConfigManager, StructuredLogger, HealthMonitor
**Status:** Implementation Complete - Testing Pending
**Last Updated:** 2025-11-13

---

## 🎯 Testing Objectives

Verify that all three Phase 1 Foundation Infrastructure components work correctly:
1. **ConfigManager** - Hierarchical JSON configuration loading
2. **StructuredLogger** - JSON logging with 3 sinks (console, file, network)
3. **HealthMonitor** - Metrics collection and UDP broadcasting

---

## ⚙️ Prerequisites

### Hardware
- [ ] Raspberry Pi 5 (8GB RAM) running Ubuntu 24.04 LTS ARM64
- [ ] Sony ILCE-1 camera connected via USB
- [ ] Network connection (Ethernet or WiFi)

### Software
- [ ] Docker 28.5.1+ installed
- [ ] payload-manager:latest image built
- [ ] Ground-Side H16 Android app (for receiving UDP broadcasts)
- [ ] SystemTools Python diagnostics (optional, for log streaming)

### Configuration Files
- [ ] `sbc/config/default.json` - Baseline configuration
- [ ] `sbc/config/development.json` - Dev environment overrides (optional)
- [ ] `sbc/config/production.json` - Production overrides (optional)

---

## 🧪 Test Suite 1: ConfigManager

### Test 1.1: Basic Configuration Loading
**Objective:** Verify ConfigManager loads default.json correctly

**Steps:**
1. Start payload_manager in Docker container
2. Check startup logs for "ConfigManager initialized"
3. Verify no JSON parse errors in logs

**Expected Results:**
```
[INFO] Initializing ConfigManager...
[INFO] ConfigManager initialized - config loaded from JSON files
```

**Pass Criteria:**
- [ ] ConfigManager initializes without errors
- [ ] No JSON parse errors in logs
- [ ] Application starts successfully

---

### Test 1.2: Configuration Value Access
**Objective:** Verify dot notation access works correctly

**Steps:**
1. Check logs for network configuration values:
   - TCP port: 5000
   - UDP status port: 5001
   - UDP heartbeat port: 5002
   - UDP health port: 5004
   - Ground IP: 192.168.144.11

**Expected Results:**
```
[INFO] TCP Command Server: 0.0.0.0:5000
[INFO] UDP Status Broadcast: 192.168.144.11:5001 (5 Hz)
[INFO] Heartbeat: 192.168.144.11:5002 (1 Hz)
[INFO] HealthMonitor broadcasting started: 192.168.144.11:5004 (5 Hz)
```

**Pass Criteria:**
- [ ] All ports match default.json values
- [ ] Ground IP matches configuration
- [ ] No default value fallbacks used

---

### Test 1.3: Environment-Specific Overrides
**Objective:** Test development.json overrides default.json

**Steps:**
1. Set environment: `export DPM_ENVIRONMENT=development`
2. Restart payload_manager
3. Verify development settings applied (e.g., SystemTools log streaming enabled)

**Expected Results:**
- Development-specific values override defaults
- Logs show "environment: development"

**Pass Criteria:**
- [ ] Environment override works
- [ ] Development settings applied correctly

---

## 🧪 Test Suite 2: StructuredLogger

### Test 2.1: Console Sink (JSON Output)
**Objective:** Verify JSON-formatted logs to stdout

**Steps:**
1. Start payload_manager
2. Trigger a command via TCP (e.g., `camera.capture`)
3. Observe console output for JSON log entries

**Expected Results:**
```json
{"timestamp":"2025-11-13T10:30:47.456Z","level":"INFO","context":"COMMAND","thread":"123456","message":"Processing command: camera.capture"}
```

**Pass Criteria:**
- [ ] Logs output as valid JSON
- [ ] Timestamp in ISO 8601 format
- [ ] Level, context, thread fields present
- [ ] Message field contains log text

---

### Test 2.2: File Sink (Rotation)
**Objective:** Verify file logging with rotation at 50MB

**Steps:**
1. Check log file location: `/var/log/dpm/air-side.jsonl`
2. Generate logs (run commands, capture images)
3. Monitor file size
4. Verify rotation when file exceeds 50MB

**Expected Results:**
- Log file created at configured path
- JSON Lines format (.jsonl)
- Files rotate: `air-side.jsonl` → `air-side.1.jsonl` → `air-side.2.jsonl`

**Pass Criteria:**
- [ ] Log file created and writable
- [ ] JSON Lines format (one JSON object per line)
- [ ] File rotation works at 50MB threshold
- [ ] Old logs preserved (max 3 files)

---

### Test 2.3: Network Sink - SystemTools Always-On
**Objective:** Verify always-on UDP streaming to SystemTools

**Steps:**
1. Set `logging.network_systemtools_enabled: true` in config
2. Set `logging.network_systemtools_ip` to SystemTools PC IP
3. Start payload_manager
4. On SystemTools PC, listen on UDP port 5005:
   ```bash
   nc -ul 5005
   ```
5. Trigger commands and observe UDP log packets

**Expected Results:**
- UDP packets received on SystemTools PC
- Packets contain JSON log entries
- Logs stream continuously (always-on)

**Pass Criteria:**
- [ ] UDP packets received on port 5005
- [ ] Packets contain valid JSON
- [ ] Streaming works continuously without commands

---

### Test 2.4: Network Sink - Ground-Side On-Demand
**Objective:** Verify on-demand Ground-Side log streaming

**Steps:**
1. Send `logging.enable_streaming` command via TCP:
   ```json
   {
     "protocol_version": "1.0",
     "message_type": "command",
     "sequence_id": 1,
     "payload": {
       "command": "logging.enable_streaming",
       "parameters": {
         "duration_sec": 30
       }
     }
   }
   ```
2. On Ground-Side H16, listen on UDP port 5005
3. Verify logs stream for 30 seconds
4. Verify streaming auto-disables after duration

**Expected Results:**
```json
{
  "status": "success",
  "result": {
    "status": "enabled",
    "duration_sec": 30
  }
}
```

**Pass Criteria:**
- [ ] Command response shows "enabled"
- [ ] UDP logs received on Ground-Side
- [ ] Streaming stops after 30 seconds
- [ ] Streaming can be manually disabled with `logging.disable_streaming`

---

## 🧪 Test Suite 3: HealthMonitor

### Test 3.1: Health Metrics Collection
**Objective:** Verify metrics collected every 500ms

**Steps:**
1. Start payload_manager
2. Send `health.get_snapshot` command via TCP:
   ```json
   {
     "protocol_version": "1.0",
     "message_type": "command",
     "sequence_id": 2,
     "payload": {
       "command": "health.get_snapshot"
     }
   }
   ```
3. Parse response and verify all metric fields present

**Expected Results:**
```json
{
  "status": "success",
  "result": {
    "timestamp": "2025-11-13T10:30:47.456Z",
    "system": {
      "cpu_percent": 15.2,
      "memory_used_mb": 512,
      "memory_total_mb": 7930,
      "disk_used_mb": 14336,
      "disk_total_mb": 59392,
      "network_rx_mbps": 1.5,
      "network_tx_mbps": 2.1
    },
    "camera": {
      "connected": true,
      "sdk_latency_ms": 0.0,
      "usb_traffic_mbps": 0,
      "error_count": 0
    },
    "network": {
      "tcp_connected": true,
      "tcp_latency_ms": 0.0,
      "udp_loss_percent": 0.0,
      "command_queue_depth": 0
    },
    "sync": {
      "exposure_rate_hz": 0.0,
      "health_rate_hz": 0.0,
      "property_reads_sec": 0
    }
  }
}
```

**Pass Criteria:**
- [ ] All metric fields present in response
- [ ] System metrics show realistic values
- [ ] Camera connection status accurate
- [ ] Timestamp in ISO 8601 format

---

### Test 3.2: UDP Health Broadcasting
**Objective:** Verify 5 Hz health broadcasts to Ground-Side

**Steps:**
1. On Ground-Side H16, listen on UDP port 5004
2. Start payload_manager on Air-Side
3. Monitor UDP packets for 10 seconds
4. Count packets received (should be ~50 packets in 10 sec)

**Expected Results:**
- UDP packets received every 200ms (5 Hz)
- Each packet contains full HealthSnapshot JSON
- No packet loss under normal conditions

**Pass Criteria:**
- [ ] Packets received at ~5 Hz rate
- [ ] Packet format matches HealthSnapshot structure
- [ ] Broadcasts continue indefinitely
- [ ] Ground-Side can parse packets successfully

---

### Test 3.3: Threshold Detection
**Objective:** Verify warnings logged when thresholds exceeded

**Steps:**
1. Check `default.json` thresholds:
   - CPU warn: 70%, critical: 90%
   - Memory warn: 400 MB, critical: 480 MB
2. Simulate high load (stress CPU/memory)
3. Check logs for threshold warnings

**Expected Results:**
```json
{"level":"WARNING","context":"SYSTEM","message":"CPU usage exceeded warning threshold","cpu_percent":75.3,"threshold":70}
```

**Pass Criteria:**
- [ ] Warnings logged when thresholds exceeded
- [ ] Warning messages contain actual values
- [ ] Critical warnings logged at higher thresholds

---

## 🧪 Test Suite 4: Integration Tests

### Test 4.1: Config → Logging Integration
**Objective:** Verify StructuredLogger uses ConfigManager settings

**Steps:**
1. Modify `logging.file_max_size_mb` in config (e.g., 10 MB)
2. Restart payload_manager
3. Generate logs until file rotates
4. Verify rotation happens at configured size

**Pass Criteria:**
- [ ] File rotation respects configured size
- [ ] Log level respects config setting
- [ ] Network streaming uses configured ports/IPs

---

### Test 4.2: Health → Logging Integration
**Objective:** Verify health warnings logged via StructuredLogger

**Steps:**
1. Trigger threshold warning (high CPU/memory)
2. Check structured logs for warning entries
3. Verify JSON format with structured fields

**Pass Criteria:**
- [ ] Health warnings appear in structured logs
- [ ] Warnings include metric values as structured fields
- [ ] Warnings routed to all sinks (console, file, network)

---

### Test 4.3: End-to-End Phase 1 Workflow
**Objective:** Full system test with all components

**Steps:**
1. Start payload_manager with default config
2. Enable Ground-Side log streaming
3. Monitor health broadcasts on Ground-Side
4. Send camera commands via TCP
5. Retrieve health snapshot
6. Verify all data flows correctly

**Pass Criteria:**
- [ ] ConfigManager loads successfully
- [ ] StructuredLogger logs to all 3 sinks
- [ ] HealthMonitor broadcasts at 5 Hz
- [ ] Commands execute successfully
- [ ] Health snapshot returns valid data
- [ ] No errors or crashes during 30-minute run

---

## 📊 Test Results Summary

| Test Suite | Total Tests | Passed | Failed | Status |
|------------|-------------|--------|--------|--------|
| ConfigManager | 3 | - | - | ⏳ Pending |
| StructuredLogger | 4 | - | - | ⏳ Pending |
| HealthMonitor | 3 | - | - | ⏳ Pending |
| Integration | 3 | - | - | ⏳ Pending |
| **TOTAL** | **13** | **-** | **-** | **⏳ Pending** |

---

## 🐛 Known Issues / TODOs

### Metrics Not Yet Implemented
- [ ] Camera SDK latency tracking (main.cpp:302)
- [ ] TCP latency tracking (main.cpp:311)
- [ ] UDP packet loss tracking (main.cpp:312)
- [ ] Command queue depth tracking (main.cpp:313)

**Impact:** These fields will report 0.0 until implemented. Does not affect core functionality.

---

## ✅ Sign-Off

**Tester:** _________________
**Date:** _________________
**Overall Status:** ⏳ Pending / ✅ Pass / ❌ Fail

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Next Steps After Testing:**
1. Update Issue #72 with test results
2. Mark issue as **[TESTED]** in title
3. Create follow-up issues for any failures
4. Proceed to Phase 2 implementation if all tests pass
