# Air-Side Coordination: StructuredLogger Migration

**Issue**: [#86 - Migrate from Logger to StructuredLogger for UDP log streaming](https://github.com/unmanned-systems-uk/DPM-V2/issues/86)
**Date**: 2025-11-13
**Status**: ⏳ Awaiting Air-Side Implementation

---

## Coordination Summary

SystemTools has prepared the infrastructure for receiving UDP logs from Air-Side. The log aggregator is operational and configured, but Air-Side needs to migrate from the legacy `Logger` class to `StructuredLogger` to enable UDP streaming.

---

## What SystemTools Completed

### 1. Configuration Updates ✅
- Updated `sbc/config/default.json` with correct SystemTools endpoint
  - IP: `10.0.1.83` (SystemTools development machine)
  - Port: `5007` (UDP listener)
- Deployed `local.json` to Pi 5 container to override production settings
- Verified configuration loaded successfully

### 2. Network Verification ✅
- Log aggregator listening on `0.0.0.0:5007` (UDP)
- Network connectivity confirmed between Pi 5 and SystemTools
- Port binding verified with `ss -ulnp`

### 3. Testing Infrastructure ✅
- Log aggregator functional with real-time display
- Filtering capabilities (level, domain, context, search)
- Export capabilities (JSON, CSV, text)
- Documentation created (`SYSTEMTOOLS_READINESS.md`)

---

## What Air-Side Needs to Do

### Primary Task: Logger → StructuredLogger Migration

**Current State:**
```cpp
// All logging currently uses legacy Logger
Logger::info("HealthMonitor initialized");
Logger::debug("Sent UDP status to " + ip);
Logger::warn("No heartbeat received");
Logger::error("Camera connection failed");
```

**Target State:**
```cpp
// Migrate to StructuredLogger with context and metadata
SLOG_INFO("HealthMonitor", "HealthMonitor initialized", {});

SLOG_DEBUG("NetworkManager", "Sent UDP status", {
    {"destination_ip", ip},
    {"destination_port", port},
    {"sequence", seq}
});

SLOG_WARN("Heartbeat", "No heartbeat received", {
    {"timeout_seconds", timeout}
});

SLOG_ERROR("Camera", "Camera connection failed", {
    {"error", error_msg}
});
```

### Implementation Priority

**Phase 1 (Critical Path):**
1. HealthMonitor logs (system metrics, health checks)
2. NetworkManager logs (UDP status broadcasts)
3. StatusBroadcaster logs
4. HeartbeatManager logs

**Phase 2 (Important):**
5. Camera SDK operations
6. Gimbal operations
7. Command handling

**Phase 3 (Nice-to-have):**
8. Initialization/startup logs
9. Configuration loading
10. Property loading

### Context String Standards

For consistency across logs, use these context identifiers:

| Context | Usage |
|---------|-------|
| `HealthMonitor` | Health monitoring, system metrics |
| `NetworkManager` | TCP/UDP network operations |
| `Camera` | Camera SDK operations |
| `Gimbal` | Gimbal control |
| `ConfigManager` | Configuration loading/saving |
| `PropertyLoader` | Property specification loading |
| `CommandHandler` | Command processing |
| `StatusBroadcaster` | Status UDP broadcasts |
| `HeartbeatManager` | Heartbeat monitoring |

---

## Verification Checklist

Once Air-Side completes the migration, verify:

### On Air-Side (Pi 5)
```bash
# 1. Check JSON log file
ssh dpm@10.0.1.53 "docker exec payload-manager tail -20 /var/log/dpm/air-side.jsonl"

# Expected: JSON formatted logs
# {"timestamp":"...","level":"INFO","context":"HealthMonitor","message":"..."}
```

### On SystemTools (10.0.1.83)
```bash
# 2. Run log aggregator
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --domain=AIR

# Expected: Real-time Air-Side logs streaming in with color coding
# [AIR] [INFO] [HealthMonitor] Health check completed
#   └─ cpu_percent: 25.3
#   └─ memory_mb: 450
```

### Network Verification (Optional)
```bash
# 3. Capture UDP packets
sudo tcpdump -i any -n udp port 5007 -c 5

# Expected: JSON payloads from 10.0.1.53
```

---

## Common Issues & Solutions

### Issue 1: No logs received despite migration
**Check:**
1. NetworkSink enabled: `network_systemtools_enabled: true` in config
2. Correct IP/port in Pi 5 config (verify via `docker exec payload-manager cat /app/sbc/config/local.json`)
3. Container restarted after config changes
4. Firewall not blocking UDP 5007

**Debug:**
```bash
# On SystemTools - verify listener
ss -ulnp | grep 5007

# On Pi 5 - verify config
docker exec payload-manager cat /app/sbc/config/local.json
docker logs payload-manager | grep "network_systemtools"
```

### Issue 2: Logs only showing old format
**Cause**: Code still using `Logger::` instead of `SLOG_*` macros

**Fix**: Complete migration of all `Logger::` calls

### Issue 3: Performance impact
**Monitor**: UDP broadcast timing (should remain ~200ms interval)

**Mitigation**: StructuredLogger uses async queues, minimal impact expected

---

## Testing After Migration

### Test 1: Basic Connectivity
```bash
# Terminal 1: Start aggregator
python3 log_aggregator.py --domain=AIR

# Terminal 2: Trigger logs on Pi (restart container)
ssh dpm@10.0.1.53 "docker restart payload-manager"

# Expected: See initialization logs in Terminal 1
```

### Test 2: Filtering
```bash
# Filter by level
python3 log_aggregator.py --level=ERROR

# Search for specific component
python3 log_aggregator.py --search="HealthMonitor"

# Filter by context
python3 log_aggregator.py --context=Camera
```

### Test 3: Export
```bash
# Export 10 seconds of logs
timeout 10 python3 log_aggregator.py --export=air_logs_$(date +%Y%m%d).json

# Verify JSON structure
jq '.[] | {timestamp, level, context, message}' air_logs_*.json | head -20
```

---

## Performance Expectations

### Baseline (Current)
- UDP status broadcasts: ~200ms interval
- Heartbeat: 1 second interval
- Logs: Console only (legacy Logger)

### After Migration
- UDP status broadcasts: ~200ms interval (no change expected)
- Heartbeat: 1 second interval (no change expected)
- Logs: Console + File + UDP network sink
- Additional overhead: <1ms per log entry (async queues)

### Monitoring
Watch for any timing regressions:
```bash
# Monitor UDP broadcast timing
ssh dpm@10.0.1.53 "docker logs payload-manager --tail 100 | grep 'Sent UDP status'"
```

---

## Success Criteria

Migration is complete when:

- [ ] All `Logger::` calls replaced with `SLOG_*` macros
- [ ] Appropriate context strings assigned
- [ ] Metadata included in structured logs
- [ ] JSON logs visible in `/var/log/dpm/air-side.jsonl`
- [ ] UDP logs successfully received by SystemTools
- [ ] No compilation errors or warnings
- [ ] No performance regression in UDP timing
- [ ] SystemTools displays real-time Air-Side logs

---

## References

- **Issue #86**: https://github.com/unmanned-systems-uk/DPM-V2/issues/86
- **SystemTools Readiness**: `/home/anthony/DPM-V2/SystemTools/SYSTEMTOOLS_READINESS.md`
- **StructuredLogger API**: `/home/anthony/DPM-V2/sbc/src/logging/structured_logger.h`
- **NetworkSink Implementation**: `/home/anthony/DPM-V2/sbc/src/logging/sinks/network_sink.h`

---

## Contact

For questions or issues:
- Review `SYSTEMTOOLS_READINESS.md` for testing procedures
- Check Issue #86 for latest status and discussion
- SystemTools log aggregator code: `/home/anthony/DPM-V2/SystemTools/log_aggregator.py`
