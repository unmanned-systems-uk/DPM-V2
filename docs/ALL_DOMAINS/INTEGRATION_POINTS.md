# Cross-Domain Integration Points
*Critical interfaces between Air-Side, Ground-Side, and Dev-Side*
*Last Updated: 2025-11-13*

## 🔌 Network Topology

```
         ┌─────────────────────────────┐
         │   Air-Side (Pi 5 / C++)     │
         │      IP: 10.0.1.53          │
         └────┬────────┬────────┬──────┘
              │        │        │
    TCP:9001  │  UDP:9002/3  SSH:22
              ▼        ▼        ▼
         ┌────────────────────────────┐
         │     Network Switch          │
         └────┬────────────────┬──────┘
              │                │
              ▼                ▼
    ┌──────────────┐  ┌──────────────┐
    │  Ground-Side │  │   Dev-Side   │
    │ H16 Android  │  │ Python Tools │
    │ 10.0.1.92    │  │ 10.0.1.x     │
    └──────────────┘  └──────────────┘
```

## 📡 Protocol Specifications

### TCP Command Channel (Port 9001)
**Direction**: Ground → Air (bidirectional)
**Protocol**: JSON over TCP
**Persistence**: Long-lived connection

#### Message Format
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "command": "camera.capture",
    "parameters": {}
  }
}
```

### UDP Status Broadcast (Port 9002/9003)
**Direction**: Air → Ground/Dev (unidirectional)
**Protocol**: JSON over UDP
**Frequency**: 5 Hz (200ms interval)

#### Status Message Format
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 5678,
  "timestamp": 1698765434,
  "payload": {
    "system": {
      "cpu_percent": 18.5,
      "memory_mb": 147,
      "disk_gb": 12.3,
      "temperature_c": 45.2
    },
    "camera": {
      "connected": true,
      "mode": "M",
      "iso": 400,
      "aperture": "5.6",
      "shutter_speed": "1/250",
      "focus_mode": "MF",
      "focal_distance_m": null  // ⚠️ Issue here
    }
  }
}
```

### UDP Heartbeat (Port 5002)
**Direction**: Bidirectional
**Protocol**: JSON over UDP
**Frequency**: 1 Hz
**Timeout**: 10 seconds

#### Heartbeat Format (v1.1.0)
```json
{
  "protocol_version": "1.1.0",
  "message_type": "heartbeat",
  "sequence_id": 42,
  "timestamp": 1698765434,  // SECONDS not milliseconds
  "payload": {
    "sender": "ground",  // or "air" or "dev"
    "client_id": "H16",  // or "RPi-Air" or "WPC"
    "uptime_seconds": 3600
  }
}
```

### UDP Log Streaming (Port 5005)
**Direction**: Air → Ground/Dev (unidirectional, on-demand)
**Protocol**: JSON over UDP
**Activation**: Via `logging.enable_streaming` command
**Duration**: Configurable (default 300 seconds)

#### Purpose
Real-time log streaming from Air-Side to Ground-Side and SystemTools for debugging and diagnostics.

#### Features
- **Dynamic Client Registration**: Air-Side discovers client IP from TCP connection
- **On-Demand Activation**: Clients enable streaming via command
- **Auto-Disable**: Streaming automatically stops after duration expires
- **Multi-Client Support**: Multiple clients can receive logs simultaneously

#### Log Entry Format
```json
{
  "timestamp": "2025-11-13T20:43:33.058Z",
  "level": "INFO",
  "context": "SYSTEM",
  "domain": "AIR",
  "thread": "thread-name",
  "message": "Log message here",
  "fields": {
    "key": "value"
  }
}
```

#### Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARN`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical system failures

#### Log Contexts
- `SYSTEM`: System-level operations
- `NETWORK`: Network communication
- `CAMERA`: Camera operations
- `GIMBAL`: Gimbal control (future)

#### Activation Flow
```
1. Ground-Side sends TCP command:
   {"command": "logging.enable_streaming", "parameters": {"duration_sec": 300}}
   ↓
2. Air-Side extracts client IP from TCP connection
   ↓
3. Air-Side creates NetworkSink for client <ip>:5005
   ↓
4. Air-Side streams log entries via UDP
   ↓
5. Ground-Side UdpLogReceiver parses and displays logs
   ↓
6. Auto-disable after duration expires
```

## 🔄 Command Implementations

### Implemented Commands (All Domains)

| Command | Air-Side | Ground-Side | Dev-Side | Status |
|---------|----------|-------------|----------|--------|
| `handshake` | ✅ | ✅ | ✅ | Working |
| `system.get_status` | ✅ | ✅ | ✅ | Working |
| `camera.capture` | ✅ | ✅ | ✅ | Working |
| `camera.set_property` | ✅ | ✅ | ✅ | Working |
| `camera.get_properties` | ✅ | ✅ | ✅ | Working |
| `camera.focus` | ⚠️ | ⚠️ | ✅ | Issues |
| `camera.auto_focus_hold` | ⚠️ | ⚠️ | ✅ | Issues |
| `logging.enable_streaming` | ⚠️ | ✅ | 🔄 | Issue #92 |
| `logging.disable_streaming` | ⚠️ | ✅ | 🔄 | Issue #92 |

### Pending Commands (Phase 2)

| Command | Purpose | Priority |
|---------|---------|----------|
| `camera.start_recording` | Video capture | High |
| `camera.stop_recording` | Video control | High |
| `gimbal.set_angle` | Gimbal control | Medium |
| `file.list` | Content management | Medium |
| `file.download` | File transfer | Medium |
| `system.reboot` | Remote restart | Low |

## 🔗 Data Flow Examples

### Camera Capture Flow
```
1. User taps capture button (Ground-Side)
   ↓
2. Android sends TCP command to Air-Side:9001
   {"command": "camera.capture"}
   ↓
3. Air-Side processes command
   - Calls Sony SDK capture function
   - Saves image to storage
   ↓
4. Air-Side sends response via TCP
   {"success": true, "filename": "IMG_0001.jpg"}
   ↓
5. Air-Side includes in next UDP status broadcast
   {"last_capture": "IMG_0001.jpg", "storage_remaining_gb": 45.2}
   ↓
6. Ground-Side and Dev-Side receive status update
```

### Property Change Flow
```
1. User adjusts ISO slider (Ground-Side)
   ↓
2. Android sends TCP command:
   {"command": "camera.set_property", "property": "iso", "value": "800"}
   ↓
3. Air-Side PropertyLoader validates against camera_properties.json
   ↓
4. Air-Side calls Sony SDK SetDeviceProperty
   ↓
5. Air-Side confirms via TCP response
   ↓
6. New ISO value broadcast in UDP status (all clients see update)
```

## 📋 Shared Resources

### Protocol Specifications
**Location**: `protocol/` directory (repository root)
**Single Source of Truth**: All domains read from same files

| File | Purpose | Format |
|------|---------|--------|
| `commands.json` | Command definitions | JSON schema |
| `camera_properties.json` | Property specifications | JSON schema |
| `heartbeat_spec.json` | Heartbeat protocol v1.1.0 | JSON schema |

### Property Loading Rules
1. Air-Side loads directly from `protocol/camera_properties.json`
2. Ground-Side bundles copy in `assets/camera_properties.json`
3. Dev-Side references for validation only
4. **Never hard-code property values**

## ⚠️ Integration Issues

### Known Problems

#### 1. Focus Distance Not Broadcasting
- **Symptom**: `focal_distance_m` always null in status
- **Impact**: Ground-Side overlay shows no data
- **Root Cause**: Air-Side can't read property from SDK
- **Workaround**: None currently

#### 2. Client Identification
- **Status**: ✅ Resolved
- **Solution**: Heartbeat v1.1.0 with client_id field
- **Implementation**: All domains updated

#### 3. Multi-Port UDP
- **Status**: ✅ Resolved
- **Solution**: Air-Side broadcasts to both 9002 and 9003
- **Benefit**: Supports multiple ground stations

## 🔐 Security Considerations

### Current State
- ⚠️ No authentication on TCP commands
- ⚠️ No encryption on network traffic
- ⚠️ SSH uses password authentication

### Phase 2 Improvements
- [ ] Add command authentication tokens
- [ ] Implement TLS for TCP channel
- [ ] Use SSH keys instead of passwords
- [ ] Add rate limiting on commands

## 📊 Performance Requirements

### Latency Targets
| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Command Response | <100ms | 47ms | ✅ |
| Status Update | 200ms | 200ms | ✅ |
| Video Stream | <500ms | 380ms | ✅ |
| Heartbeat | 1000ms | 1000ms | ✅ |

### Throughput Requirements
| Channel | Required | Current | Status |
|---------|----------|---------|--------|
| TCP Commands | 10 cmd/s | 50 cmd/s | ✅ |
| UDP Status | 5 msg/s | 5 msg/s | ✅ |
| Video Stream | 10 Mbps | 8 Mbps | ✅ |

## 🔄 Version Compatibility

### Protocol Versions
| Component | Version | Compatible With |
|-----------|---------|-----------------|
| Command Protocol | 1.0 | All domains |
| Heartbeat Protocol | 1.1.0 | All domains (updated Oct 29) |
| Camera Properties | 1.2.0 | All domains |
| Status Format | 1.0 | All domains |

### Breaking Changes Log
- **Oct 29**: Heartbeat v1.0 → v1.1.0 (added client_id, changed timestamp unit)
- **Oct 28**: PropertyLoader introduced (backward compatible)

## 📝 Integration Testing

### Test Scenarios
1. ✅ Single client command/response
2. ✅ Multi-client status reception
3. ✅ Heartbeat timeout detection
4. ✅ Property synchronization
5. ⚠️ Focus control (known issues)
6. ⏳ Network failure recovery
7. ⏳ High load stress test

### Integration Test Commands
```bash
# Test TCP connection
nc 10.0.1.53 9001

# Monitor UDP status
nc -u -l 9002

# Send test heartbeat
echo '{"protocol_version":"1.1.0","message_type":"heartbeat","sequence_id":1,"timestamp":1698765434,"payload":{"sender":"test","client_id":"TEST","uptime_seconds":0}}' | nc -u 10.0.1.53 5002
```

---
*For domain-specific details, see respective CURRENT_STATUS.md files*
*For blocking issues, see BLOCKERS.md*
*For version alignment, see SYNC_STATUS.md*