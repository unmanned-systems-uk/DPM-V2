# Security & Reliability View

**Architecture View:** Security & Reliability
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Security Architecture

### Current State: Minimal Security (Development Focus)

**Authentication:** ❌ None currently implemented
- No login/password
- No API keys
- Open network connections

**Rationale:** Development/testing phase, closed network environment

**Production Requirements (Future):**
- Air-Side: SSH key-based auth
- Network: VPN or encrypted tunnel
- Commands: HMAC signature verification

### Network Security

**Current:**
- Unencrypted TCP/UDP (JSON plaintext)
- Static IP addressing (predictable)
- Open ports (5000, 5001, 5002)

**Mitigation:**
- Closed network (R16 link, not internet-exposed)
- Physical security (UAV platform)
- Network isolation (no routing to internet)

**Future:**
- TLS for TCP channel
- DTLS for UDP (or switch to secure protocol)
- Certificate-based mutual auth

### USB Security

**Risk:** Malicious USB devices

**Mitigation:**
- Camera-only USB connection (no general USB storage)
- Sony SDK validates camera identity
- Docker device whitelist (`/dev/bus/usb`)

---

## Reliability Architecture

### Fault Tolerance

**Camera Disconnect:**
- Detection: SDK callback + polling
- Response: Auto-reconnect every 5 seconds
- User notification: Real-time UI alert
- Recovery: Automatic when camera reconnected

**Network Disconnect:**
- Detection: Heartbeat timeout (10 sec)
- Response: Exponential backoff reconnect
- User indication: Connection status indicator
- Recovery: Automatic on network restore

**Air-Side Crash:**
- Detection: Docker health check
- Response: Docker restart policy (always)
- Data loss: Minimal (stateless service)
- Recovery time: <10 seconds

### Error Handling

**Categories:**
1. **Recoverable:** Camera disconnect, network timeout
   - Auto-retry with backoff
   - User notification
   - Continue operation

2. **User Error:** Invalid command, bad parameter
   - Return error response
   - Log for diagnostics
   - Don't crash

3. **Fatal:** SDK initialization failure, hardware fault
   - Log critical error
   - Graceful shutdown
   - Restart via Docker

### Availability Targets

**Goal:** 99% uptime during flight operations

**Achieved:**
- MTBF: >20 hours continuous operation
- Recovery time: <10 seconds for most failures
- Zero data loss (stateless, camera stores images)

---

## Monitoring & Diagnostics

**Real-Time Monitoring:**
- System telemetry (5Hz): CPU, memory, temperature
- Connection health: Heartbeat (1Hz)
- Error logging: Syslog + file logs

**Diagnostic Tools:**
- SystemTools: Packet monitoring, command testing
- SSH access: Log retrieval, system diagnostics
- Docker logs: Container stdout/stderr

---

## Related Documents

- **Deployment:** `view-deployment.md` - Physical security
- **Context:** `view-context.md` - External system dependencies
- **Lessons Learned:** `LESSONS_LEARNED.md` - Operational reliability patterns
