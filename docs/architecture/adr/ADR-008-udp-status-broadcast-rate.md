# ADR-008: UDP Status Broadcast Rate (5Hz)

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team, UX Designer
**Related Issues:** #11 (Network monitoring)
**Related Views:** `view-integration.md`, `view-data.md`

---

## Context

Ground-Side UI displays real-time camera and system status. Questions:
1. What update rate provides smooth UX?
2. What rate is network-efficient?
3. What rate is achievable on Pi 5?

**UX Requirements:**
- User perceives updates as "instant" (<100ms)
- No visible lag when property changes
- Smooth value transitions (not jumpy)

**Network Constraints:**
- R16 link: 20-50 Mbps bandwidth
- Status message: ~1KB
- Want to minimize bandwidth usage

---

## Decision

**Status broadcast rate: 5 Hz (200ms interval)**

**Rationale:**
- 200ms < 250ms human perception threshold (feels instant)
- 5KB/sec bandwidth usage (0.025% of 20Mbps link)
- Pi 5 can easily handle 5Hz with <1% CPU

---

## Alternatives Considered

### Alternative 1: 10Hz (100ms)

**Pros:** Even smoother UX
**Cons:** 2× bandwidth (10KB/sec), still negligible
**Rejection:** Diminishing returns - 200ms already feels instant

### Alternative 2: 1Hz (1000ms)

**Pros:** Minimal bandwidth (1KB/sec)
**Cons:** Visible lag, jerky UI updates (1 second feels slow)
**Rejection:** Poor UX

### Alternative 3: Variable Rate (1Hz idle, 10Hz active)

**Pros:** Bandwidth optimization
**Cons:** Complexity (state machine), mode transitions jarring
**Rejection:** Premature optimization - 5KB/sec already minimal

---

## Consequences

### Positive

✅ **Smooth UX:** 200ms feels instant to users
✅ **Network Efficient:** 5KB/sec negligible on 20Mbps link
✅ **CPU Efficient:** <1% CPU on Pi 5
✅ **Simple:** Fixed rate, no adaptive logic

### Negative

⚠️ **Packet Loss Visible:** If 2+ consecutive packets lost (>400ms gap), UI feels laggy
- Mitigation: Rare on local network (<0.1% loss), acceptable trade-off

---

## Performance Metrics

**Measured:**
- Broadcast jitter: ±2ms (very stable)
- CPU per broadcast: 0.2%
- Network usage: 5.1 KB/sec average

---

## Related Decisions

- **ADR-003:** TCP/UDP Protocol Split (why UDP for status)
- **ADR-009:** Heartbeat Timeout (10 seconds)

---

## References

- Integration View: `view-integration.md` (Telemetry Broadcast pattern)
- Data View: `view-data.md` (Telemetry flow)
