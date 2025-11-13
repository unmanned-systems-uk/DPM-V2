# SystemTools Readiness Status

**Date**: 2025-11-13
**Status**: ✅ Ready for Air-Side UDP Log Streaming
**Awaiting**: Issue #86 - Air-Side Logger to StructuredLogger Migration

---

## Configuration Summary

### SystemTools Log Aggregator
- **Location**: `/home/anthony/DPM-V2/SystemTools/log_aggregator.py`
- **Status**: Operational and tested
- **Listening**: UDP `0.0.0.0:5007` (Air-Side), TCP `localhost:5008` (Ground-Side)
- **Host IP**: `10.0.1.83`

### Air-Side Configuration (Pi 5)
- **Host**: `10.0.1.53`
- **Container**: `payload-manager` (Up and running)
- **Config File**: `/app/sbc/config/local.json` (deployed)
- **Configuration**:
  ```json
  {
    "logging": {
      "network_systemtools_enabled": true,
      "network_systemtools_ip": "10.0.1.83",
      "network_systemtools_port": 5007
    }
  }
  ```

### Ground-Side Configuration (Android H16)
- **Host**: `10.0.1.92:5555` (ADB)
- **Status**: Pending (requires NetworkSink implementation)
- **Expected Port**: TCP `5008` (via ADB forward)

---

## Verification Results

### ✅ Completed
1. **Log Aggregator Functionality**
   - UDP listener successfully bound to `0.0.0.0:5007`
   - TCP listener successfully bound to `localhost:5008`
   - JSON parsing and display working
   - Filter capabilities tested (level, domain, context, search)

2. **Air-Side Configuration**
   - Network configuration updated in `default.json`
   - Production override disabled SystemTools logging
   - `local.json` created to re-enable and configure SystemTools
   - Configuration successfully loaded (verified in container logs)

3. **Network Connectivity**
   - Pi 5 reachable at `10.0.1.53`
   - SystemTools machine at `10.0.1.83`
   - Both on same `10.0.1.x` subnet
   - Port `5007` confirmed listening via `ss -ulnp`

### ❌ Blocked (Awaiting Issue #86)
1. **StructuredLogger Usage**
   - Infrastructure initialized and operational
   - NetworkSink configured correctly
   - **Application code still using legacy `Logger` class**
   - No UDP packets received (no structured logs being generated)

---

## Testing Commands

### Start Log Aggregator (Air-Side Only)
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --domain=AIR
```

### Start Log Aggregator (All Domains)
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py
```

### Filter by Log Level
```bash
python3 log_aggregator.py --level=ERROR
python3 log_aggregator.py --level=WARN
```

### Search Logs
```bash
python3 log_aggregator.py --search="HealthMonitor"
python3 log_aggregator.py --search="aperture"
```

### Export Logs
```bash
python3 log_aggregator.py --export=logs_$(date +%Y%m%d_%H%M%S).json
python3 log_aggregator.py --export=logs.csv --export-format=csv
```

---

## Post-Migration Verification (Issue #86)

Once Air-Side migration is complete, verify with:

### 1. Check JSON Log File on Pi 5
```bash
ssh dpm@10.0.1.53 "docker exec payload-manager tail -f /var/log/dpm/air-side.jsonl"
```

Expected output:
```json
{"timestamp":"2025-11-13T05:40:00.000Z","level":"INFO","context":"HealthMonitor","message":"Health check completed","cpu_percent":25.3,"memory_mb":450}
```

### 2. Verify UDP Streaming to SystemTools
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py --domain=AIR
```

Expected output (color-coded in terminal):
```
[AIR] [INFO] [HealthMonitor] Health check completed
  └─ cpu_percent: 25.3
  └─ memory_mb: 450
[AIR] [DEBUG] [NetworkManager] Sent UDP status
  └─ destination_ip: 192.168.144.11
  └─ destination_port: 5001
  └─ sequence: 123
```

### 3. Check Network Packets (Optional)
```bash
# On SystemTools machine (requires sudo)
sudo tcpdump -i any -n udp port 5007 -A
```

---

## Known Issues

### Issue 1: Production Config Disables SystemTools
- **Impact**: SystemTools logging disabled by default in production
- **Workaround**: `local.json` overrides this setting
- **Permanent Fix**: Update `sbc/config/production.json` or use environment-specific config

### Issue 2: Log File Directory May Not Exist
- **Path**: `/var/log/dpm/air-side.jsonl`
- **Impact**: FileSink may fail if directory doesn't exist
- **Fix**: Ensure directory created in Docker image or at runtime

---

## Dependencies

### Python Packages
```
rich==13.7.0  # Terminal formatting
```

Install with:
```bash
pip install -r /home/anthony/DPM-V2/SystemTools/requirements.txt
```

### Network Access
- Pi 5 must be able to reach `10.0.1.83:5007` (UDP)
- Android H16 must have ADB forward active: `adb forward tcp:5008 tcp:5008`

---

## Next Steps

1. **Wait for Issue #86 completion** (Air-Side migration)
2. **Test UDP log reception** once migration deployed
3. **Implement Ground-Side NetworkSink** (similar pattern)
4. **Enable tri-domain log aggregation** (Air + Ground + SystemTools)

---

## Contact

- **SystemTools**: `/home/anthony/DPM-V2/SystemTools/`
- **Config**: `/home/anthony/DPM-V2/SystemTools/config/log_aggregator.json`
- **Issue**: https://github.com/unmanned-systems-uk/DPM-V2/issues/86
