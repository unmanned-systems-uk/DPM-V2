# ADR-009: Heartbeat Timeout (10 Seconds)

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #11
**Related Views:** `view-integration.md`, `view-security-reliability.md`

---

## Context

System needs to detect network/node failures and trigger reconnection. Questions:
1. How quickly should we detect failures?
2. What timeout balances false positives vs. quick detection?

**Requirements:**
- Detect genuine failures (network down, Air-Side crashed)
- Avoid false positives (transient packet loss)
- Trigger auto-reconnect on timeout

---

## Decision

**Heartbeat timeout: 10 seconds** (10 consecutive missed 1Hz heartbeats)

**Heartbeat rate: 1Hz** (every second)

**Rationale:**
- 10 seconds fast enough for user to notice connection lost
- 10 consecutive packets unlikely lost accidentally (UDP loss <2%)
- Allows network hiccups without false alarms

---

## Alternatives Considered

### Alternative 1: 5 Second Timeout

**Pros:** Faster failure detection
**Cons:** False positives on slow network (R16 occasional 3-5 sec lag)
**Rejection:** Real-world R16 link sometimes has 5 sec latency spikes

### Alternative 2: 30 Second Timeout

**Pros:** Very robust against false positives
**Cons:** 30 seconds too long for user to wait
**Rejection:** Poor UX - user thinks system frozen

### Alternative 3: TCP Keep-Alive

**Pros:** Built into TCP stack
**Cons:** TCP keep-alive default 2 hours (too slow), configurable but OS-specific
**Rejection:** UDP heartbeat more flexible and cross-platform

---

## Consequences

### Positive

✅ **Fast Detection:** 10 seconds acceptable for user ("it's reconnecting")
✅ **Robust:** False positives rare (<0.01% observed)
✅ **Simple:** Fixed timeout, no adaptive logic

### Negative

⚠️ **Not Instant:** 10 sec delay before reconnect triggered
- Acceptable: Most failures recover within 10 sec anyway

---

## Implementation

**Air-Side:**
```cpp
if (now - last_heartbeat_received > 10s) {
    LOG(WARNING) << "Ground-Side heartbeat timeout, connection lost";
    // Note: Air-Side is server, doesn't reconnect (waits for Ground to reconnect)
}
```

**Ground-Side:**
```kotlin
if (now - lastHeartbeatReceived > 10.seconds) {
    connectionState.value = ConnectionState.DISCONNECTED
    reconnect()
}
```

---

## Related Decisions

- **ADR-003:** TCP/UDP Protocol Split (heartbeat uses UDP)
- **ADR-008:** Status Broadcast Rate (5Hz status separate from 1Hz heartbeat)
- **ADR-014:** Auto-Reconnect Strategy (what happens after timeout)

---

## References

- Integration View: `view-integration.md` (Heartbeat pattern)
- Security & Reliability View: `view-security-reliability.md` (Fault tolerance)
