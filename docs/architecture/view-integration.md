# Integration View

**Architecture View:** Integration
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Overview

Cross-domain interfaces and integration patterns between Air-Side, Ground-Side, and Dev-Tools.

**Key Document:** `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` - Complete protocol specs

---

## Integration Patterns

### Pattern 1: Command-Response (TCP)

**Participants:** Ground-Side ↔ Air-Side, Dev-Tools ↔ Air-Side

**Protocol:** JSON over TCP (Port 5000)
- Long-lived connection
- Client (Ground/Tools) connects to Server (Air)
- Bidirectional request-response
- Sequence ID for correlation

**Message Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "command": "camera.capture"
  }
}
```

**Use Cases:**
- Camera control commands
- Property get/set
- System queries

**Error Handling:**
- Response status field (success/error)
- Error codes and messages
- Timeout: 5 seconds

---

### Pattern 2: Telemetry Broadcast (UDP)

**Participants:** Air-Side → Ground-Side, Air-Side → Dev-Tools

**Protocol:** JSON over UDP (Port 5001)
- Unidirectional (Air→Ground/Tools)
- Fire-and-forget (no acknowledgment)
- Fixed 5Hz rate (200ms interval)

**Message Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 5678,
  "timestamp": 1698765434,
  "payload": {
    "system": {"cpu_percent": 18.5},
    "camera": {"connected": true, "iso": 400}
  }
}
```

**Use Cases:**
- Real-time status display
- System health monitoring
- Camera state sync

**Characteristics:**
- Lossy OK (next update in 200ms)
- No flow control
- Eventually consistent

---

### Pattern 3: Heartbeat (UDP)

**Participants:** Bidirectional (Air ↔ Ground, Air ↔ Tools)

**Protocol:** JSON over UDP (Port 5002)
- Bidirectional heartbeat exchange
- 1Hz rate
- Timeout: 10 seconds → trigger reconnect

**Use Cases:**
- Connection health monitoring
- Detect network failures
- Trigger auto-reconnect

---

## Interface Specifications

### TCP Command Interface (Port 5000)

**Endpoint:** Air-Side (server)
**Client:** Ground-Side, Dev-Tools

**Commands:**
- `camera.capture` - Trigger shutter
- `camera.set_property` - Set property value
- `camera.get_property` - Query property
- `system.status` - Query system metrics

**Response Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "status": "success|error",
    "result": {...},
    "error_code": "...",
    "error_message": "..."
  }
}
```

---

### UDP Status Interface (Port 5001)

**Endpoint:** Air-Side (broadcaster)
**Listener:** Ground-Side, Dev-Tools

**Content:**
- System metrics (CPU, memory, disk, temp)
- Camera status (connected, properties)
- Network statistics
- Sequence number (detect packet loss)

---

### UDP Heartbeat Interface (Port 5002)

**Endpoint:** All participants (bidirectional)

**Content:**
- Sender identifier
- Client ID
- Uptime
- Timestamp (seconds, not milliseconds)

---

## Data Format Standards

### JSON Encoding

**Rules:**
- UTF-8 encoding
- No pretty-printing (compact)
- Timestamps in UNIX seconds (integer)
- Property values as strings (even numbers)

### Error Codes

**Format:** `CATEGORY_SPECIFIC_ERROR`

**Examples:**
- `CAMERA_NOT_CONNECTED`
- `INVALID_PROPERTY_VALUE`
- `SDK_ERROR_0x8402`
- `TIMEOUT`

---

## Integration Challenges & Solutions

### Challenge 1: Property Specification Sync

**Problem:** Air/Ground must have matching property specs

**Solution:** Specification-First Architecture
- Single JSON source in `docs/protocol/`
- Copied into both domains at build time
- PropertyLoader in both Air (C++) and Ground (Kotlin)

---

### Challenge 2: Network Latency

**Problem:** R16 link has 20-50ms latency

**Solution:**
- Asynchronous command/response (non-blocking)
- Status broadcast separate from commands (no wait)
- UI optimistic updates (assume success, revert on error)

---

### Challenge 3: UDP Packet Loss

**Problem:** UDP unreliable, packets may be lost

**Solution:**
- High broadcast rate (5Hz) → loss doesn't matter
- Sequence numbers detect loss (for diagnostics)
- TCP for critical commands (reliable)

---

## Testing Integration

### Unit Testing

**Air-Side:** Mock Sony SDK, test components in isolation
**Ground-Side:** Mock network layer, test ViewModels
**Protocol:** JSON schema validation

### Integration Testing

**SystemTools:** Command builder tests full protocol
**Packet Analysis:** Monitor UDP broadcasts
**Response Validation:** Verify protocol compliance

### End-to-End Testing

**Hardware-in-Loop:** Full system with real camera
**Network Scenarios:** WiFi vs R16 link
**Failure Testing:** Camera disconnect, network loss

---

## Related Documents

- **Protocol:** `docs/ALL_DOMAINS/INTEGRATION_POINTS.md`
- **Specifications:** `docs/protocol/*.json`
- **Logical:** `view-logical.md` - Component interactions
- **Data:** `view-data.md` - Data flow
