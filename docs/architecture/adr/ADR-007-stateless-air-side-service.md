# ADR-007: Stateless Air-Side Service

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #33 (Deployment), #46, #50, #51
**Related Views:** `view-logical.md`, `view-security-reliability.md`

---

## Context

Air-Side service may crash or restart due to:
- Docker container restarts
- Code updates and redeployment
- System reboots
- Unhandled exceptions

**Design Question:** Should Air-Side persist state between restarts?

---

## Decision

**Air-Side will be STATELESS** - no persistent state stored between restarts.

**What is NOT persisted:**
- Camera property values (always query camera on connect)
- Last command results
- Client connection history
- Runtime configuration changes

**What IS persisted (via Docker volumes):**
- Logs (`/var/log/payload-manager/`)
- Protocol specifications (embedded in Docker image, not runtime state)

**Rationale:** Camera is source of truth for camera state. Air-Side is a passthrough service.

---

## Alternatives Considered

### Alternative 1: Persist Camera State to Disk

**Approach:** Save camera properties to file, reload on restart

**Rejection:** Camera state may have changed while offline. Stale state causes errors.

### Alternative 2: Persist User Preferences

**Approach:** Remember user's last ISO, aperture settings

**Rejection:** User preferences managed by Ground-Side (Android DataStore). Air-Side just executes commands.

---

## Consequences

### Positive

✅ **Fast Recovery:** Restart time <10 seconds (no state to load)
✅ **Simple Deployment:** No state migration between versions
✅ **Reliable:** No corrupted state files causing startup failures
✅ **Idempotent:** Multiple restarts produce identical behavior

### Negative

⚠️ **Camera Reconnection:** Must re-enumerate camera after restart (~2 seconds)
⚠️ **No Command History:** Cannot replay last commands (acceptable - user controls from Ground-Side)

---

## Related Decisions

- **ADR-004:** Docker Containerization (enables fast stateless restarts)
- **ADR-006:** Multi-Threaded Design (no persistent thread state)

---

## References

- Security & Reliability View: `view-security-reliability.md` (Fault tolerance section)
- LESSONS_LEARNED.md: Container restart persistence
