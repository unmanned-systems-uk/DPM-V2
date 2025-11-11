# Data View

**Architecture View:** Data
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Overview

The Data View describes the data model, data flow, persistence, and synchronization patterns in DPM-V2.

**Key Documents:** `docs/protocol/*.json` - Complete protocol specifications

---

## Data Model

### Camera Properties

**Core Entities:**
- **ShutterSpeed:** 1/8000s to 30s (56 discrete values)
- **Aperture:** f/1.4 to f/22 (23 values, lens-dependent)
- **ISO:** 100 to 102400 (discrete steps)
- **WhiteBalance:** Auto, Daylight, Shade, Cloudy, Incandescent, Fluorescent, Flash, Custom (2500K-10000K)
- **FocusMode:** AF-S, AF-C, DMF, MF
- **DriveMode:** Single, Continuous Hi/Mid/Lo
- **FileFormat:** RAW, JPEG, RAW+JPEG

**Property Specification Format (JSON):**
```json
{
  "property_name": "shutter_speed",
  "display_name": "Shutter Speed",
  "type": "enum",
  "sdk_property_id": "0x5005",
  "values": [
    {"sdk_value": "0x00010001", "display_value": "1/8000", "sort_order": 1},
    {"sdk_value": "0x00010002", "display_value": "1/6400", "sort_order": 2}
  ],
  "default": "1/250",
  "unit": "seconds"
}
```

### System Telemetry

**Metrics:**
- CPU usage (per-core + average)
- Memory consumption (MB)
- Disk usage (GB free)
- Temperature (°C)
- Uptime (seconds)
- Network statistics (packets sent/received)

### Camera Status

**State:**
- Connected (boolean)
- Camera model (string)
- Battery level (percentage, future)
- Image count (number of photos on card)
- Current property values (ISO, aperture, etc.)
- Error state (if any)

---

## Data Flow

### Command Flow (Ground → Air → Camera)

```
Ground-Side UI
  → ViewModel (property change)
  → Repository (send command)
  → TcpClient (serialize JSON)
  → Network (TCP port 5000)
  → Air-Side NetworkService (receive)
  → CommandHandler (parse, route)
  → CameraService (validate, execute)
  → Sony SDK (native call)
  → Camera (execute command)
  → [Response path reversed]
```

### Telemetry Flow (Camera/System → Air → Ground)

```
Camera/SystemMonitor (query state)
  → StatusBroadcaster (5Hz timer)
  → NetworkService (serialize JSON)
  → Network (UDP port 5001)
  → Ground-Side UdpListener (receive)
  → Repository (deserialize)
  → ViewModel (update state)
  → UI (display update)
```

**Characteristics:**
- Fire-and-forget (no acknowledgment)
- Continuous 5Hz stream
- Lossy OK (next update in 200ms)

---

## Data Persistence

### Air-Side

**PropertySpecifications:** Embedded in Docker image (`/app/specs/*.json`)
- Loaded at startup
- Read-only during runtime
- Version-controlled in git

**Logs:** Written to `/var/log/payload-manager/`
- Rotated daily
- Retained for 7 days
- Retrievable via SSH

**No User Data:** Air-Side is stateless (no settings persistence)

### Ground-Side

**Settings:** AndroidX DataStore (Preferences)
- Network IP address
- User preferences
- Last known good values
- Persisted in app private storage

**PropertySpecifications:** Embedded in APK assets
- Same JSON as Air-Side
- Loaded at app startup
- Version must match Air-Side

**No Image Storage:** Photos stored on camera SD card, not in app

### Dev-Tools

**Diagnostics Log:** Optionally save sessions to text files
- User-initiated save
- Stored in user documents folder

---

## Data Synchronization

### Property Specification Sync

**Problem:** Air-Side and Ground-Side must have matching property specs

**Solution:** Specification-First Architecture
1. Single source of truth: `docs/protocol/*.json`
2. Air-Side: Copies JSON into Docker image at build time
3. Ground-Side: Copies JSON into APK assets at build time
4. Version check on connection (future enhancement)

**Ensures:**
- UI shows same valid values as Air-Side validates
- No mismatch errors
- Adding property updates both sides automatically

### Status Synchronization

**Pattern:** Eventually Consistent (via UDP broadcast)

**Flow:**
- Air-Side: Broadcast current state every 200ms
- Ground-Side: Update UI on receive
- No acknowledgment (UDP fire-and-forget)
- Eventual consistency within 200ms

**Trade-off:**
- Accept potential packet loss (rare on local network)
- Gain simplicity and performance
- Status updates continuous, so loss doesn't matter

### Command-Response Sync

**Pattern:** Request-Response over TCP

**Flow:**
- Ground→Air: Command with sequence ID
- Air→Ground: Response with matching sequence ID
- Timeout if no response (5 seconds)

**Ensures:**
- Reliable command delivery (TCP)
- Response correlation
- Error detection

---

## Data Validation

### Air-Side Validation

**PropertyLoader validates:**
- Property value is in valid set (from JSON specs)
- Value format matches expected type
- Property is supported by current camera model

**Rejects:**
- Invalid values → Error response
- Unknown properties → Error response
- Malformed JSON → Error response

### Ground-Side Validation

**UI validation:**
- Dropdowns only show valid values (from specs)
- Sliders constrained to valid range
- Type-safe Kotlin data classes
- User cannot enter invalid data

**Defense in Depth:** Both sides validate independently

---

## Data Formats

### JSON Message Protocol

**Common Structure:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command|response|status|heartbeat|notification",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": { ... }
}
```

**See `docs/protocol/README.md` for complete specifications**

### Property Value Mapping

**SDK Value ↔ Display Value:**

Example (ISO):
- SDK: Integer (100, 200, 400, 800...)
- Display: String ("100", "200", "400", "800"...)
- Mapping: Defined in property specs JSON

**Handled by PropertyLoader in both Air/Ground**

---

## Data Integrity

### Mechanisms

**TCP for Commands:** Ensures reliable delivery
**Sequence IDs:** Detect lost/duplicate messages
**JSON Schema Validation:** Catch malformed messages
**Type Safety:** Kotlin/C++ strong typing
**Property Validation:** Against specs on both sides

### Error Handling

**Malformed Data:**
- Log error with details
- Return error response (don't crash)
- Continue operation

**Invalid Commands:**
- Validate before execution
- Return error code and message
- Don't send to camera (prevent camera errors)

---

## Data Performance

### Metrics

**Message Sizes:**
- Command: ~200 bytes typical
- Response: ~300 bytes typical
- Status: ~1KB (full system+camera state)
- Heartbeat: ~100 bytes

**Network Bandwidth:**
- Status: 5KB/sec (5Hz × 1KB)
- Commands: Sporadic, <1KB/sec average
- Total: <10KB/sec typical, <50KB/sec peak

**Latency:**
- Command round-trip: <50ms (TCP + SDK)
- Status update: 200ms maximum staleness

---

## Future Enhancements

**Version Negotiation:**
- Detect spec version mismatch on connect
- Reject incompatible versions
- Guide user to update

**Property Change Notifications:**
- Camera-initiated property changes
- Broadcast when camera mode dial changed
- Sync UI immediately

**Telemetry History:**
- Store last N status updates
- Enable trend analysis in SystemTools
- Plot CPU/memory over time

---

## Related Documents

- **Protocol Specifications:** `docs/protocol/*.json`
- **Integration Points:** `docs/ALL_DOMAINS/INTEGRATION_POINTS.md`
- **Logical View:** `view-logical.md` - Component interactions
- **Property Mapping:** `docs/protocol/PROTOCOL_VALUE_MAPPING.md`

