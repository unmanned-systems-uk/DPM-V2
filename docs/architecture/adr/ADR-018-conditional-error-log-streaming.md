# ADR-018: Conditional ERROR Log Streaming to SystemTools

**WHO:** CC-Air-Side
**Date:** 2025-11-18
**Time:** 22:45 UTC
**Status:** Accepted
**Deciders:** Air-Side Development Team, PM
**Related Issues:** #148
**Related Views:** `view-logical.md`, `view-integration.md`, `view-security-reliability.md`
**Supersedes:** All-or-nothing SystemTools log streaming

---

## Context

### Problem

SystemTools passive logging uses a binary on/off switch (`logging.network_systemtools_enabled`):

**Original Behavior:**
```
logging.network_systemtools_enabled = true  → All logs sent (INFO, WARNING, ERROR)
logging.network_systemtools_enabled = false → NO logs sent (including ERROR)
```

**User Pain Point:**
1. User disables passive logging to save network bandwidth during normal operations
2. Critical error occurs (camera disconnect, SDK failure, system crash)
3. **ERROR not visible** in SystemTools → requires SSH to Pi 5 to check logs
4. Defeats purpose of remote diagnostics

**Field Deployment Scenario:**
- System deployed in remote location (aerial platform, vehicle)
- User disables passive logging to reduce telemetry bandwidth
- Critical failure occurs
- **No way to see the error remotely** → requires physical access or SSH

### Design Question

How can we ensure critical errors are always visible in SystemTools while still allowing bandwidth reduction?

**Options Considered:**

1. **Option A:** Keep current behavior (all-or-nothing)
   - Simple implementation
   - Users lose remote error visibility when passive logging disabled

2. **Option B:** Add separate config option: `logging.network_systemtools_errors_always`
   - Flexible (user can disable even ERROR logs if they want)
   - Config complexity increases
   - Default should be `true` anyway (you always want errors)

3. **Option C:** Always send ERROR logs, regardless of enabled state
   - Simple (no extra config)
   - Sensible default (errors are critical by definition)
   - Users can filter in SystemTools UI if needed

4. **Option D:** Rate-limit non-ERROR logs when disabled
   - Complex implementation
   - Hard to tune rate limits
   - Still doesn't guarantee ERROR visibility

---

## Decision

**We will use Option C: Always Send ERROR Logs**

When `logging.network_systemtools_enabled = false`, ERROR logs bypass the check and are still sent to SystemTools.

### Implementation

**Location:** `sbc/src/logging/sinks/network_sink.cpp` (NetworkSink::write)

**Before:**
```cpp
// Send to SystemTools if enabled (always-on monitoring)
if (systemtools_enabled_) {
    sendUDP(systemtools_ip_, systemtools_port_, data);
}
```

**After:**
```cpp
// Send to SystemTools if enabled (always-on monitoring)
// CRITICAL: Always send ERROR logs regardless of enabled state (Issue #148)
// This ensures critical errors are visible in SystemTools even when
// passive logging is disabled for bandwidth savings
bool is_error_log = log_entry.contains("level") && log_entry["level"] == "ERROR";
if (systemtools_enabled_ || is_error_log) {
    sendUDP(systemtools_ip_, systemtools_port_, data);
}
```

### Behavior Matrix

| Passive Logging State | INFO Logs | WARNING Logs | ERROR Logs | Network Bandwidth |
|----------------------|-----------|--------------|------------|-------------------|
| **enabled = true** | ✅ Sent | ✅ Sent | ✅ Sent | High (all logs) |
| **enabled = false** | ❌ Blocked | ❌ Blocked | ✅ **SENT** | Low (errors only) |

---

## Consequences

### Positive

1. **✅ Always See Critical Errors:**
   - ERROR logs visible in SystemTools even with passive logging disabled
   - Remote diagnostics capability maintained
   - No SSH required to check error logs

2. **✅ Bandwidth Reduction Still Achieved:**
   - INFO/WARNING/DEBUG logs properly blocked
   - Typical operation: <1% of normal log volume
   - ERROR logs are rare (by definition of "error")

3. **✅ Better Field Deployment:**
   - Remote systems can report failures
   - Reduces mean-time-to-diagnosis (MTTD)
   - No physical access required for basic diagnostics

4. **✅ Sensible Default:**
   - No extra configuration needed
   - Behavior matches user expectation ("I want to see errors")
   - Clear documentation in logs: "CRITICAL: Always send ERROR logs..."

### Negative

1. **⚠️ Cannot Completely Disable Error Streaming:**
   - If user wants ZERO logs to SystemTools, this prevents it
   - Mitigation: Extremely rare use case; filtering available in SystemTools UI

2. **⚠️ Potential Privacy Concern:**
   - ERROR logs may contain sensitive info (file paths, usernames)
   - Mitigations:
     - Closed network (no external access per ADR-015)
     - ERROR logs already sanitized in StructuredLogger
     - User controls SystemTools IP (can point to /dev/null if needed)

### Mitigations

1. **Documentation:**
   - Clearly document in config schema
   - Note in SystemTools UI: "ERROR logs always streamed"
   - Include rationale in user manual

2. **Filtering:**
   - SystemTools Log Viewer can filter by level
   - User can hide ERROR logs in UI if desired
   - Filtering happens on SystemTools side (bandwidth already saved)

3. **Future Enhancement:**
   - If user requests complete disable, add separate override config
   - Example: `logging.network_systemtools_force_disable: true` (default: false)

---

## Rationale

### Why ERROR Logs Are Special

1. **By Definition Critical:**
   - ERROR = "Something went wrong that requires attention"
   - Not advisory (INFO), not concerning (WARNING)
   - Indicates actual failure condition

2. **Low Volume:**
   - Healthy system: 0-5 ERROR logs per hour
   - Failing system: User WANTS to see these immediately
   - Bandwidth impact: Negligible

3. **Diagnostic Value:**
   - ERROR logs often contain root cause info
   - First indication of system degradation
   - Enables proactive maintenance

### Remote Diagnostics Use Case

**Scenario:**
```
1. Aerial platform operating with minimal telemetry
2. User disables passive logging (saves 99% bandwidth)
3. Camera USB connection fails (physical vibration)
4. ERROR logged: "Failed to enumerate cameras. Status: 0x0"
5. ✅ ERROR appears in SystemTools immediately
6. User knows to check camera physical connection
7. Problem diagnosed without landing aircraft
```

**Without This Decision:**
```
Same scenario steps 1-4...
5. ❌ ERROR NOT sent (passive logging disabled)
6. User sees camera disconnected but no ERROR details
7. Must land aircraft, SSH to Pi 5, check logs
8. 30+ minutes lost, possibly mission failure
```

---

## Related Decisions

- **ADR-017:** Runtime Configuration Application (enables dynamic toggle)
- **ADR-015:** Closed Network Security Posture (mitigates privacy concern)
- **ADR-006:** Multi-Threaded Air-Side Design (thread safety considerations)

---

## Testing Strategy

### Test Cases

1. **Passive Logging Enabled:**
   ```
   Config: logging.network_systemtools_enabled = true
   Trigger: LOG_INFO(), LOG_WARNING(), LOG_ERROR()
   Expected: All logs appear in SystemTools
   ```

2. **Passive Logging Disabled - INFO Blocked:**
   ```
   Config: logging.network_systemtools_enabled = false
   Trigger: LOG_INFO("Test message")
   Expected: Log NOT in SystemTools
   ```

3. **Passive Logging Disabled - ERROR Sent:**
   ```
   Config: logging.network_systemtools_enabled = false
   Trigger: LOG_ERROR("Critical failure")
   Expected: Log APPEARS in SystemTools ✅
   ```

4. **Runtime Toggle:**
   ```
   Initial: logging.network_systemtools_enabled = true (all logs sent)
   Command: system.update_config({"network_systemtools_enabled": false})
   Trigger: LOG_INFO(), LOG_ERROR()
   Expected: INFO blocked, ERROR sent
   ```

### Validation Criteria

- ✅ ERROR logs bypass enabled check
- ✅ INFO/WARNING/DEBUG properly blocked when disabled
- ✅ No performance degradation (check already exists, just extended)
- ✅ Thread-safe (NetworkSink::write already mutex-protected)

---

## Implementation Details

### Code Location

**File:** `sbc/src/logging/sinks/network_sink.cpp`
**Method:** `NetworkSink::write(const json& log_entry)`
**Lines:** 50-56

### Performance Impact

**None.** The check is:
```cpp
bool is_error_log = log_entry.contains("level") && log_entry["level"] == "ERROR";
```

- `contains()`: O(1) hash map lookup
- String comparison: Trivial (level field is always present)
- Executed only when log is written (already on logging path)
- No additional locking or I/O

### Memory Impact

**None.** No new data structures. Only one additional boolean variable (stack-allocated).

---

## Compliance

**ISO/IEC/IEEE 42010:2011:** Stakeholder concern addressed - Remote diagnostics capability
**C4 Model:** Impacts Level 3 (Components) - NetworkSink logging behavior
**Quality Attributes:**
- ✅ Reliability: Critical errors always reported
- ✅ Maintainability: Clear code comments explain behavior
- ✅ Performance: Zero overhead (check on existing path)

---

## References

- Implementation: `sbc/src/logging/sinks/network_sink.cpp` lines 50-56
- Related Issue: #148
- Git Commit: 9a5272e (pending push)
- Testing: Issue #148 checklist

---

**Approved by:** CC-Air-Side, PM
**Review Date:** 2025-11-18
**Next Review:** After field deployment feedback (3-6 months)
