# Claude Code Instructions: Air Side SBC Implementation
## DPM Payload Manager - Initial Connectivity Phase

**Version:** 1.0  
**Date:** October 22, 2025  
**Target Platform:** Raspberry Pi (Linux ARM64v8)  
**Language:** C++17  
**Sony SDK:** CrSDK v2.00.00

---

## CRITICAL: Read-First Requirements

Claude Code (CC) **MUST** complete these steps **BEFORE** writing any implementation code:

### 1. Documentation Review (MANDATORY)
Read and understand ALL of these documents in order:

1. **This instruction document** (CC_Air_Side_Implementation_Instructions.md)
2. **Air_Side_Implementation_Guide.md** - Complete system architecture and requirements
3. **Connectivity_Test_Strategy.md** - Testing approach and validation criteria
4. **Sony SDK README** (`/mnt/user-data/uploads/README.md`)
5. **Sony SDK Readme PDF** (`Camera_Remote_SDK_Readme_v2_00_00.pdf`)
6. **Sony Sample App Manual** (`RemoteSampleApp_IM_v2_00_00.pdf`)
7. **ALL Air_side (this code) must reside on the sbc directory** (`~/DPM/sbc')
8. **Claude Code must consult the user and clarify any ambiguous requirements before proceeding.**
### 2. Example Code Review (MANDATORY)
Examine the Sony SDK example application code structure:

- Location: `CrSDK_v2.00.00_20250805a_Linux64ARMv8/app/`
- Key files to understand:
  - `RemoteCli.cpp` - Entry point and main loop
  - `CameraDevice.cpp/h` - Camera SDK interface
  - `ConnectionInfo.cpp/h` - Connection management
  - CMakeLists.txt structure
  - How SDK headers and libraries are integrated

### 3. SDK API Reference (MANDATORY)
Review the API reference documentation:
- Location: `CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/`
- Understand the API functions, callbacks, and data structures

### 4. Strategy Discussion (MANDATORY)
**BEFORE implementing any code**, CC must:

1. Present a **build plan** including:
   - Project directory structure
   - CMakeLists.txt approach
   - Dependency management strategy
   - Build steps and verification

2. Present an **implementation strategy** including:
   - Component architecture
   - Thread model
   - Error handling approach
   - Sony SDK integration approach
   - Testing strategy alignment

3. **Wait for approval** from the user before proceeding

---

## Project Context

### What We're Building
A C++ service that runs on a Raspberry Pi (Air Side) to:
1. Communicate with an Android app (Ground Side) over Ethernet
2. Control a Sony camera via the Sony Camera Remote SDK
3. Support initial connectivity testing (Phase 1 / MVP)

### Network Architecture
```
Android App (H16)          Raspberry Pi (Air Side)
192.168.144.11      <-->   192.168.144.20
                  Ethernet

Protocols:
- TCP Port 5000: Command/Response
- UDP Port 5001: Status Broadcast (5 Hz)
- UDP Port 5002: Heartbeat (1 Hz)
```

### What Already Exists
- **Ground Side (Android App)**: COMPLETE - working and tested
- **Protocol Specification**: COMPLETE - defined in Air_Side_Implementation_Guide.md
- **Sony Camera SDK**: PROVIDED - CrSDK v2.00.00 for Linux ARM64v8
- **Test Strategy**: COMPLETE - Connectivity_Test_Strategy.md

### What Needs to Be Built
**Air Side Service** (This project) - Initial connectivity implementation focusing on:

**Phase 1 (Initial Implementation - CURRENT FOCUS):**
- TCP server on port 5000
- Handshake message exchange
- Basic status broadcast (system info only, no camera yet)
- Heartbeat send/receive
- Logging infrastructure
- Network communication validation

**Future Phases (Not Now):**
- Phase 2: Camera control integration
- Phase 3: Advanced features

---

## Sony Camera SDK Integration

### SDK Location and Structure
```
CrSDK_v2.00.00_20250805a_Linux64ARMv8/
├── app/                           # Example source code
│   ├── CRSDK/                    # Public headers
│   ├── CameraDevice.cpp/h        # Reference implementation
│   ├── RemoteCli.cpp             # Main example app
│   └── ...
├── cmake/                         # CMake helper files
├── external/
│   └── crsdk/
│       ├── CrAdapter/            # Protocol adapters (PTP/IP, PTP/USB)
│       │   ├── libCr_PTP_IP.so
│       │   ├── libCr_PTP_USB.so
│       │   ├── libssh2.so
│       │   └── libusb-1.0.so
│       ├── libCr_Core.so         # Core SDK library
│       ├── libmonitor_protocol.so
│       └── libmonitor_protocol_pf.so
└── CMakeLists.txt
```

### Key SDK Concepts (From Documentation)
1. **Camera connection modes**: USB and Network (PTP/IP)
2. **Callback-based architecture**: IDeviceCallback interface
3. **Property system**: Get/Set camera properties
4. **Threading requirements**: SDK manages its own threads
5. **Resource management**: Explicit Init/Release calls

### SDK Integration Requirements
- Include headers from `app/CRSDK/`
- Link against `libCr_Core.so` and adapter libraries
- Copy runtime .so files to deployment location
- Implement IDeviceCallback for camera events
- Handle SDK initialization and cleanup

---

## Implementation Phases

### Phase 1: Basic Connectivity (CURRENT - MVP)
**Goal:** Establish and verify network communication with Android app

**Scope:**
1. ✅ TCP Server (port 5000)
   - Accept connections
   - Receive commands
   - Send responses
   - Handle disconnections

2. ✅ UDP Broadcaster (port 5001)
   - Send status messages at 5 Hz
   - Include system info (CPU, memory, uptime)
   - Placeholder camera status (not connected)

3. ✅ Heartbeat Handler (port 5002)
   - Send heartbeat every 1 second
   - Receive heartbeat from ground
   - Detect connection loss

4. ✅ Protocol Implementation
   - JSON message parsing/generation
   - Handshake exchange
   - system.get_status command
   - Response formatting

5. ✅ Logging System
   - Structured logging to file
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Timestamp and context

**NOT in Phase 1:**
- ❌ Camera SDK integration (placeholder only)
- ❌ Camera control commands
- ❌ Image capture
- ❌ Gimbal control
- ❌ Advanced error recovery

### Phase 2: Camera Control (FUTURE)
Will add Sony SDK integration, camera control commands, property management.

### Phase 3: Advanced Features (FUTURE)
Will add video recording, content download, gimbal control.

---

## Project Structure

### Recommended Directory Layout
```
/home/dpm/payload_manager/
├── CMakeLists.txt
├── README.md
├── src/
│   ├── main.cpp
│   ├── config.h
│   ├── protocol/
│   │   ├── tcp_server.h/cpp
│   │   ├── udp_broadcaster.h/cpp
│   │   ├── heartbeat.h/cpp
│   │   ├── messages.h
│   │   └── json_handler.cpp
│   ├── camera/
│   │   ├── camera_interface.h      # Interface/stub for Phase 1
│   │   └── camera_stub.cpp         # Placeholder implementation
│   └── utils/
│       ├── logger.h/cpp
│       └── system_info.h/cpp
├── include/
│   └── sony_sdk/                    # Sony SDK headers (symlink or copy)
├── lib/
│   └── sony_sdk/                    # Sony SDK .so files (symlink or copy)
├── external/                        # Third-party dependencies
│   └── nlohmann_json/              # If not system-installed
└── build/                           # CMake build directory
```

### Key Files for Phase 1

**main.cpp**: Entry point
- Initialize logger
- Create and start TCP server
- Create and start UDP broadcaster
- Create and start heartbeat handler
- Main event loop
- Signal handling (graceful shutdown)

**tcp_server.h/cpp**: TCP command server
- Listen on port 5000
- Accept connections
- Parse JSON commands
- Route to handlers
- Send JSON responses
- Multi-threaded client handling

**udp_broadcaster.h/cpp**: Status broadcaster
- Broadcast every 200ms (5 Hz)
- Send to 192.168.144.11:5001
- Include system status
- Include placeholder camera status

**heartbeat.h/cpp**: Heartbeat handler
- Send UDP to 192.168.144.11:5002 every 1 second
- Receive heartbeat from ground
- Timeout detection

**messages.h**: Message structures
- Command message structure
- Response message structure
- Status message structure
- Heartbeat message structure

**logger.h/cpp**: Logging system
- File-based logging
- Rotating logs (optional)
- Thread-safe
- Configurable levels

**system_info.h/cpp**: System monitoring
- CPU usage
- Memory usage
- Disk space
- Uptime
- Network statistics

**camera_stub.cpp**: Placeholder camera interface
- Simulated camera connection status
- Placeholder properties
- No actual SDK calls (Phase 2)

---

## Dependencies

### System Requirements
```bash
# Required packages on Raspberry Pi
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    g++ \
    libudev-dev \
    nlohmann-json3-dev \
    libboost-system-dev \
    libboost-thread-dev
```

### C++ Libraries
1. **nlohmann/json**: JSON parsing/generation
   - System package: `nlohmann-json3-dev`
   - Or include as header-only

2. **Standard C++17**: Threading, filesystem, networking
   - std::thread
   - std::mutex
   - std::condition_variable
   - std::filesystem (optional)

3. **POSIX**: Network sockets
   - sys/socket.h
   - netinet/in.h
   - arpa/inet.h

4. **Sony Camera SDK** (Phase 2)
   - libCr_Core.so
   - libCr_PTP_IP.so
   - libCr_PTP_USB.so
   - Related libraries

---

## Protocol Details (Phase 1)

### Message Format
All messages are JSON with this base structure:
```json
{
  "protocol_version": "1.0",
  "message_type": "command|response|status|heartbeat",
  "sequence_id": 12345,
  "timestamp": 1729339200,
  "payload": {
    // Message-specific content
  }
}
```

### Phase 1 Commands to Implement

#### 1. Handshake (Receive)
Ground sends on initial connection:
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1,
  "timestamp": 1729339200,
  "payload": {
    "command": "handshake",
    "parameters": {
      "client_id": "dpm_ground_001",
      "client_version": "1.0.0"
    }
  }
}
```

Response:
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1,
  "timestamp": 1729339201,
  "payload": {
    "command": "handshake",
    "status": "success",
    "result": {
      "server_id": "payload_manager",
      "server_version": "1.0.0",
      "capabilities": ["system.get_status"]
    }
  }
}
```

#### 2. system.get_status Command
Request:
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 2,
  "timestamp": 1729339210,
  "payload": {
    "command": "system.get_status",
    "parameters": {}
  }
}
```

Response:
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 2,
  "timestamp": 1729339211,
  "payload": {
    "command": "system.get_status",
    "status": "success",
    "result": {
      "uptime_seconds": 3600,
      "cpu_percent": 25.5,
      "memory_mb": 512,
      "memory_total_mb": 4096,
      "disk_free_gb": 28.5,
      "network_rx_mbps": 1.2,
      "network_tx_mbps": 0.8
    }
  }
}
```

### Status Broadcast (UDP)
Sent every 200ms to 192.168.144.11:5001:
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 1001,
  "timestamp": 1729339300,
  "payload": {
    "system": {
      "uptime_seconds": 3600,
      "cpu_percent": 25.5,
      "memory_mb": 512
    },
    "camera": {
      "connected": false,
      "model": "unknown",
      "battery_percent": 0,
      "remaining_shots": 0
    },
    "gimbal": {
      "connected": false
    }
  }
}
```

### Heartbeat (UDP)
Sent every 1000ms to 192.168.144.11:5002:
```json
{
  "protocol_version": "1.0",
  "message_type": "heartbeat",
  "sequence_id": 500,
  "timestamp": 1729339350,
  "payload": {
    "sender": "air",
    "uptime_seconds": 3600
  }
}
```

---

## Error Handling

### Error Response Format
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 123,
  "timestamp": 1729339400,
  "payload": {
    "command": "camera.capture",
    "status": "error",
    "error": {
      "code": 5002,
      "message": "Camera not connected",
      "details": "No camera detected on USB or network"
    }
  }
}
```

### Error Codes (Phase 1)
- `5000`: Invalid message format
- `5001`: Invalid protocol version
- `5002`: Command not implemented
- `5003`: Unknown command
- `5004`: Internal server error

---

## Build Plan Requirements

CC must develop and present a **detailed build plan** covering:

### 1. CMakeLists.txt Strategy
- How to find/link nlohmann/json
- How to integrate Sony SDK headers and libraries
- Compiler flags (C++17, warnings, optimization)
- Install targets
- Platform-specific considerations

### 2. Dependency Management
- System packages vs. bundled dependencies
- Sony SDK library path setup
- Runtime library loading (LD_LIBRARY_PATH or RPATH)

### 3. Build Steps
- Precise commands to build the project
- How to verify build success
- Output binary location and naming

### 4. Testing Approach
- Unit test strategy (if applicable)
- Integration test plan
- How to align with Connectivity_Test_Strategy.md

### 5. Deployment
- Binary installation location
- Configuration files
- Systemd service setup (future)
- File permissions

---

## Testing Requirements

### Phase 1 Testing Objectives
The implementation is successful when it passes these tests from `Connectivity_Test_Strategy.md`:

#### ✅ Phase 1: Network Layer Tests
- Ping test: < 10ms latency, 0% packet loss
- Port availability: 5000 (TCP), 5001/5002 (UDP)
- Network throughput: > 10 Mbps

#### ✅ Phase 2: Protocol Layer Tests
- TCP command test: Valid JSON, correct sequence_id
- UDP status broadcast: 5 Hz rate (±20ms)
- Heartbeat exchange: 1 Hz bidirectional

#### ✅ Phase 3: Application Layer Tests
- Connection from Android app succeeds
- Status updates received on Android
- Graceful disconnect works

#### ✅ Phase 4: Error Handling Tests
- Service unavailable detection
- Connection loss recovery
- Invalid command handling
- Timeout handling

### Manual Testing Tools
Use these from the test strategy:
- Simple TCP test client (Python script)
- UDP status listener (Python script)
- Heartbeat monitor (Python script)
- netcat for quick tests

---

## Code Quality Requirements

### C++ Best Practices
1. **RAII**: All resources managed with RAII
2. **Smart pointers**: Use unique_ptr/shared_ptr, avoid raw pointers
3. **Const correctness**: const references for input parameters
4. **Move semantics**: std::move for large objects
5. **Thread safety**: Proper mutex usage, avoid data races
6. **Exception safety**: Strong exception guarantee where possible

### Documentation
- Doxygen-style comments for public APIs
- Inline comments for complex logic
- README with build instructions
- Architecture diagram (optional but recommended)

### Error Handling
- Check all system call return values
- Use exceptions for exceptional conditions
- Log all errors with context
- Graceful degradation where possible

### Performance
- Avoid allocations in hot paths
- Use string_view for temporary strings
- Profile critical sections
- Monitor resource usage (memory, CPU)

---

## Sony SDK Integration Guidance (Phase 2 Preview)

While Phase 1 uses stubs, here's what Phase 2 will need:

### SDK Initialization Pattern
```cpp
// From Sony example code structure
SCRSDK::CrError Init() {
    return SCRSDK::Init();  // Initialize SDK
}

void Release() {
    SCRSDK::Release();  // Clean up SDK
}
```

### Camera Enumeration Pattern
```cpp
// Enumerate connected cameras
SCRSDK::ICrEnumCameraObjectInfo* camera_list = nullptr;
auto err = SCRSDK::EnumCameraObjects(&camera_list);
if (err != SCRSDK::CrError_None) {
    // Handle error
}
```

### Callback Interface
```cpp
class CameraCallback : public SCRSDK::IDeviceCallback {
public:
    void OnConnected(SCRSDK::DeviceConnectionVersioin version) override {
        // Camera connected
    }
    
    void OnDisconnected(SCRSDK::CrError error) override {
        // Camera disconnected
    }
    
    void OnPropertyChanged() override {
        // Camera property changed
    }
    
    // ... other callbacks
};
```

**Note:** Phase 1 does NOT implement these - only stubs/placeholders.

---

## Success Criteria for Phase 1

Phase 1 implementation is **complete and successful** when:

### Functionality
- ✅ Service compiles without errors or warnings
- ✅ Service starts and runs without crashes
- ✅ TCP server accepts connections on port 5000
- ✅ Handshake exchange works correctly
- ✅ system.get_status command returns valid data
- ✅ Status broadcasts sent at ~5 Hz (measured)
- ✅ Heartbeat sent/received at ~1 Hz (measured)
- ✅ JSON parsing/generation works for all messages
- ✅ Logging produces readable, timestamped logs

### Testing
- ✅ All Phase 1-3 tests from Connectivity_Test_Strategy.md pass
- ✅ At least 80% of Phase 4 (error handling) tests pass
- ✅ Android app can connect and receive status updates
- ✅ No memory leaks detected (valgrind or similar)
- ✅ Resource usage within limits (< 30% CPU, < 256 MB RAM)

### Code Quality
- ✅ Code follows C++17 best practices
- ✅ No compiler warnings with -Wall -Wextra
- ✅ Thread-safe implementation verified
- ✅ Clean shutdown on SIGTERM/SIGINT
- ✅ README documents build and run process

---

## Workflow for Claude Code

### Step 1: Read and Understand ⏸️ PAUSE
1. Read all mandatory documentation (see top of this document)
2. Review Sony SDK example code structure
3. Understand the protocol from Air_Side_Implementation_Guide.md
4. Understand test requirements from Connectivity_Test_Strategy.md

### Step 2: Build Plan Development ⏸️ PAUSE
1. Design project structure
2. Plan CMakeLists.txt approach
3. Identify dependencies and how to manage them
4. Plan build steps
5. **Present plan to user and wait for approval**

### Step 3: Implementation Plan ⏸️ PAUSE
1. Design component architecture
2. Plan threading model
3. Design error handling strategy
4. Plan logging approach
5. **Present plan to user and wait for approval**

### Step 4: Implementation 🔨 START CODING
1. Set up project structure
2. Implement core components incrementally:
   - Logger first (needed for everything)
   - TCP server
   - UDP broadcaster
   - Heartbeat handler
   - Message handling
   - System info collection
3. Build and test each component

### Step 5: Integration Testing 🧪 TEST
1. Build complete service
2. Run Phase 1-2 tests from Connectivity_Test_Strategy.md
3. Fix issues
4. Run Phase 3-4 tests
5. Optimize and refine

### Step 6: Documentation 📝 DOCUMENT
1. Update README with build instructions
2. Document any deviations from specification
3. Document known issues or limitations
4. Create deployment guide

---

## Important Notes

### What CC Should NOT Do
- ❌ Implement camera control (Phase 2)
- ❌ Implement image capture (Phase 2)
- ❌ Implement gimbal control (Phase 3)
- ❌ Over-engineer beyond Phase 1 requirements
- ❌ Skip the documentation review
- ❌ Start coding without presenting a build plan
- ❌ Deviate from protocol specification without discussion

### What CC MUST Do
- ✅ Read ALL documentation before coding
- ✅ Review Sony SDK example code
- ✅ Present build plan and wait for approval
- ✅ Present implementation strategy and wait for approval
- ✅ Focus on Phase 1 only
- ✅ Follow C++17 best practices
- ✅ Align with Connectivity_Test_Strategy.md
- ✅ Use Sony SDK reference implementation patterns
- ✅ Test incrementally during development

### Communication Protocol
When CC has questions:
1. Ask specific, technical questions
2. Reference specific sections of documentation
3. Propose solutions for approval
4. Highlight any ambiguities or conflicts in specs

When CC presents plans:
1. Be detailed and specific
2. Show understanding of requirements
3. Explain rationale for design decisions
4. Identify risks or concerns
5. Wait for explicit approval

---

## Reference Documents Summary

| Document | Purpose | Key Content |
|----------|---------|-------------|
| This file | Instructions for CC | Overall guidance and workflow |
| Air_Side_Implementation_Guide.md | System architecture | Network setup, protocol, system design |
| Connectivity_Test_Strategy.md | Testing approach | Test phases, success criteria, tools |
| README.md (Sony SDK) | SDK build guide | Dependencies, build commands |
| Camera_Remote_SDK_Readme_v2_00_00.pdf | SDK overview | SDK contents, structure, notes |
| RemoteSampleApp_IM_v2_00_00.pdf | Example app manual | Reference implementation details |

---

## Next Actions for Claude Code

**NOW:**
1. ✅ Acknowledge receipt of instructions
2. ✅ Confirm understanding of workflow
3. ✅ Begin documentation review phase
4. ⏸️ DO NOT write any code yet
5. ⏸️ DO NOT present any plans yet

**AFTER reading documentation:**
1. Present build plan (CMakeLists.txt approach)
2. Wait for approval
3. Present implementation strategy
4. Wait for approval
5. Begin Phase 1 implementation

---

**Document Status:** Complete ✅  
**Ready for:** Claude Code to begin documentation review  
**Phase:** Pre-Implementation / Planning  
**Last Updated:** October 22, 2025

