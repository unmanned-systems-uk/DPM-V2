# Build and Implementation Plan
## Air Side Payload Manager - Phase 1 (MVP)

**Version:** 1.0
**Date:** October 23, 2025
**Status:** Planning Complete - Awaiting Approval
**Target Platform:** Raspberry Pi (Linux ARM64v8)
**Target Platform ssh address:** 10.0.1.127
**Target Platform ssh username:** dpm
**Target Platform ssh password:** 2350
**Target Platform sudo password:** 2350

---

## Documentation Review Status

**Completed Reviews:**
- ✅ CC_Air_Side_Implementation_Instructions.md
- ✅ Air_Side_Implementation_Guide.md
- ✅ Connectivity_Test_Strategy.md
- ✅ Sony SDK README.md (`~/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/README.md`)
- ✅ Sony SDK example code (RemoteCli.cpp, CameraDevice.h/cpp)
- ✅ Sony SDK CMakeLists.txt
- ✅ Sony SDK API headers (CameraRemote_SDK.h, IDeviceCallback.h)

**Key Sony SDK Findings:**
- SDK Location: `~/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/`
- Headers: `app/CRSDK/`
- Libraries: `external/crsdk/` (libCr_Core.so, libCr_PTP_IP.so, etc.)
- Namespace: `SCRSDK`
- Callback-based architecture using `IDeviceCallback` interface
- C++17 standard required

---

## BUILD PLAN

### 1. Project Directory Structure

```
/home/dpm/DPM/sbc/
├── CMakeLists.txt
├── README.md
├── docs/
│   ├── BUILD_AND_IMPLEMENTATION_PLAN.md (this file)
│   └── PROGRESS_AND_TODO.md
├── src/
│   ├── main.cpp
│   ├── config.h
│   ├── protocol/
│   │   ├── tcp_server.h
│   │   ├── tcp_server.cpp
│   │   ├── udp_broadcaster.h
│   │   ├── udp_broadcaster.cpp
│   │   ├── heartbeat.h
│   │   ├── heartbeat.cpp
│   │   └── messages.h
│   ├── camera/
│   │   ├── camera_interface.h
│   │   └── camera_stub.cpp          # Phase 1: STUB only
│   └── utils/
│       ├── logger.h
│       ├── logger.cpp
│       ├── system_info.h
│       └── system_info.cpp
├── build/                             # CMake build directory (gitignored)
└── logs/                              # Runtime logs
```

### 2. CMakeLists.txt Strategy

**Approach:**
- CMake 3.16+ (available on Ubuntu 20.04)
- C++17 standard (required by Sony SDK)
- Find nlohmann/json via system package or fallback to header-only
- Reference Sony SDK headers and libraries (prepared for Phase 2, not linked in Phase 1)
- RPATH configuration for runtime library loading
- Install target for deployment

**Key Configuration:**
```cmake
cmake_minimum_required(VERSION 3.16)
project(payload_manager VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS NO)

# Compiler warnings
add_compile_options(-Wall -Wextra -Wpedantic -fsigned-char)

# Find nlohmann/json
find_package(nlohmann_json 3.10.0 QUIET)
if(NOT nlohmann_json_FOUND)
    # Fallback: use header-only from external/
endif()

# Sony SDK paths (prepared for Phase 2)
set(SONY_SDK_ROOT "${CMAKE_SOURCE_DIR}/../../SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8")
set(SONY_SDK_INCLUDE "${SONY_SDK_ROOT}/app/CRSDK")
set(SONY_SDK_LIB_DIR "${SONY_SDK_ROOT}/external/crsdk")

# RPATH for runtime libraries
set(CMAKE_BUILD_RPATH "$ORIGIN")
set(CMAKE_INSTALL_RPATH "$ORIGIN")
set(CMAKE_BUILD_RPATH_USE_ORIGIN ON)

# Link libraries (Phase 1 - basic dependencies only)
target_link_libraries(payload_manager
    PRIVATE
        pthread
        nlohmann_json::nlohmann_json
)

# Install target
install(TARGETS payload_manager DESTINATION /usr/local/bin)
```

### 3. Dependency Management

**System Packages (install via apt):**
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    g++ \
    nlohmann-json3-dev \
    libudev-dev
```

**Dependencies:**
- **nlohmann/json**: System package (nlohmann-json3-dev)
- **pthread**: Standard Linux threading
- **POSIX sockets**: Standard Linux networking

**Sony SDK (Phase 2):**
- Will reference from: `~/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/`
- NOT linked in Phase 1 (stub only)

### 4. Build Steps

**Development Build:**
```bash
cd /home/dpm/DPM/sbc
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . -j4
```

**Release Build:**
```bash
cd /home/dpm/DPM/sbc
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j4
```

**Installation:**
```bash
sudo cmake --install .
# Installs to: /usr/local/bin/payload_manager
```

**Verification:**
```bash
./payload_manager --version  # Check build info
ldd ./payload_manager        # Check library dependencies
```

### 5. Testing Approach

**Alignment with Connectivity_Test_Strategy.md:**

**Phase 1 Tests (Network Layer):**
- Ping test: Verify < 10ms latency, 0% packet loss
- Port availability: Check TCP 5000, UDP 5001/5002
- Network throughput: > 10 Mbps

**Phase 2 Tests (Protocol Layer):**
- Manual TCP command test using netcat or Python script
- UDP status listener (verify 5 Hz broadcast)
- Heartbeat exchange monitor (verify 1 Hz bidirectional)

**Phase 3 Tests (Application Layer):**
- Integration with Android app
- Connection/disconnection testing
- Status reception verification

**Phase 4 Tests (Error Handling):**
- Service unavailable scenarios
- Connection loss/recovery
- Invalid command handling
- Timeout testing

**Testing Tools:**
- Python test scripts from Connectivity_Test_Strategy.md
- `netcat` for quick protocol tests
- `tcpdump` for packet capture
- `journalctl` for service logs
- `valgrind` for memory leak detection

### 6. Deployment

**Installation Locations:**
- Binary: `/usr/local/bin/payload_manager`
- Logs: `/home/dpm/DPM/sbc/logs/payload_manager.log`
- Config: `/home/dpm/DPM/sbc/config.h` (compile-time)

**Systemd Service (Future Phase):**
```ini
[Unit]
Description=DPM Payload Manager Service
After=network.target

[Service]
Type=simple
User=dpm
WorkingDirectory=/home/dpm/DPM/sbc
ExecStart=/usr/local/bin/payload_manager
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**File Permissions:**
- Binary: 755 (readable and executable)
- Logs directory: 755 (dpm:dpm)
- Log files: 644 (dpm:dpm)

---

## IMPLEMENTATION STRATEGY

### 1. Component Architecture

**Layered Architecture:**
```
┌─────────────────────────────────────────┐
│           main.cpp                      │
│  (Entry point, initialization, signals) │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
┌───────▼─────────┐  ┌──────▼────────┐
│  Protocol Layer  │  │  Camera Layer │
│  - TCP Server    │  │  - Stub (P1)  │
│  - UDP Broadcast │  │  - SDK (P2)   │
│  - Heartbeat     │  │               │
└────────┬─────────┘  └───────────────┘
         │
┌────────▼─────────┐
│   Utils Layer    │
│  - Logger        │
│  - System Info   │
└──────────────────┘
```

**Component Responsibilities:**

**main.cpp:**
- Application entry point
- Component initialization
- Signal handling (SIGTERM, SIGINT)
- Main event loop
- Graceful shutdown coordination

**TCP Server (protocol/tcp_server.cpp):**
- Listen on port 5000
- Accept client connections
- Receive JSON commands
- Parse and validate messages
- Dispatch to command handlers
- Send JSON responses
- Multi-threaded client handling

**UDP Broadcaster (protocol/udp_broadcaster.cpp):**
- Broadcast status every 200ms (5 Hz)
- Gather system information
- Gather camera status (stub in Phase 1)
- Format JSON status message
- Send to 192.168.144.11:5001

**Heartbeat Handler (protocol/heartbeat.cpp):**
- Send heartbeat every 1000ms (1 Hz) to 192.168.144.11:5002
- Receive heartbeat from ground
- Track last received heartbeat time
- Log warnings if heartbeat timeout (>10 seconds)

**Camera Stub (camera/camera_stub.cpp):**
- Implement camera interface
- Return placeholder status data
- Simulate camera properties
- NO Sony SDK calls in Phase 1

**Logger (utils/logger.cpp):**
- Thread-safe file logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Timestamped messages
- Thread ID in log entries

**System Info (utils/system_info.cpp):**
- Read CPU usage from /proc/stat
- Read memory usage from /proc/meminfo
- Read disk space from filesystem
- Read network stats from /proc/net/dev
- Calculate uptime from /proc/uptime

### 2. Thread Model

**Thread Architecture (5 threads):**

1. **Main Thread**
   - Event loop
   - Signal handling
   - Component lifecycle management
   - Shutdown coordination

2. **TCP Accept Thread**
   - Listen for incoming connections on port 5000
   - Accept new clients
   - Spawn client handler threads

3. **TCP Client Threads** (dynamic, one per connection)
   - Receive commands from specific client
   - Parse JSON
   - Execute command
   - Send response
   - Auto-cleanup on disconnect

4. **UDP Status Broadcast Thread**
   - Timer loop (200ms interval)
   - Gather status from all sources
   - Format and send status message

5. **Heartbeat Thread**
   - Combined send/receive
   - Timer for send (1000ms interval)
   - Async receive with timeout
   - Track connection health

**Thread Safety:**
- Logger: `std::mutex` around file writes
- Shutdown flag: `std::atomic<bool>`
- Camera state (Phase 2): `std::mutex` if shared
- No shared mutable state between protocol threads in Phase 1

**Shutdown Sequence:**
1. Signal handler sets atomic shutdown flag
2. Main thread stops accepting new connections
3. Protocol threads check flag and exit loops
4. Main thread joins all worker threads
5. Components cleanup (RAII + explicit cleanup)
6. Exit

### 3. Error Handling Approach

**Error Handling Strategy:**

**System Calls:**
- Check all return values
- Log errors with `strerror(errno)`
- Throw exceptions for fatal errors (constructor failures)
- Return error codes for recoverable errors

**Network Errors:**
- Bind failure: Log and exit (fatal)
- Send failure (UDP): Log warning, continue
- Recv failure (TCP): Log debug, close connection
- Accept failure: Log error, retry

**JSON Parsing:**
- Try/catch around `nlohmann::json::parse()`
- Return error response with code 5000 (Invalid JSON)
- Log malformed messages at DEBUG level

**Command Errors:**
- Unknown command: Error code 5003
- Invalid parameters: Error code 5000
- Internal error: Error code 5004

**Error Response Format:**
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
      "message": "Command not implemented in Phase 1",
      "details": "Camera control requires Phase 2"
    }
  }
}
```

**Error Codes (Phase 1):**
- 5000: Invalid message format / Invalid JSON
- 5001: Invalid protocol version
- 5002: Command not implemented
- 5003: Unknown command
- 5004: Internal server error

### 4. Sony SDK Integration Approach

**Phase 1 (Current Implementation):**
- Create `CameraInterface` abstract base class
- Implement `CameraStub` with placeholder data
- Returns hardcoded status:
  - `connected: false`
  - `model: "unknown"`
  - `battery_percent: 0`
  - `remaining_shots: 0`
- NO Sony SDK includes
- NO Sony SDK library linking

**Phase 2 (Future Implementation):**
- Create `CameraSony` implementing `CameraInterface`
- Link Sony SDK libraries
- Initialize SDK: `SCRSDK::Init()`
- Enumerate cameras: `SCRSDK::EnumCameraObjects()`
- Connect to camera: `SCRSDK::Connect()` with callback
- Implement `SCRSDK::IDeviceCallback` for camera events
- Map protocol properties to SDK properties
- Handle camera commands (capture, set property, etc.)
- Cleanup: `SCRSDK::Disconnect()`, `SCRSDK::Release()`

**Interface Design:**
```cpp
class CameraInterface {
public:
    virtual ~CameraInterface() = default;

    virtual bool connect() = 0;
    virtual void disconnect() = 0;
    virtual bool isConnected() const = 0;

    // Returns JSON object with camera status
    virtual nlohmann::json getStatus() const = 0;

    // Phase 2: Additional methods
    // virtual bool setProperty(const std::string& prop, const std::string& value) = 0;
    // virtual bool capture() = 0;
    // virtual bool startRecording() = 0;
    // virtual bool stopRecording() = 0;
};
```

### 5. Logging Approach

**Implementation Details:**

**Log Format:**
```
[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] [ThreadID] Message
```

**Example:**
```
[2025-10-23 10:30:45.123] [INFO] [1234] Payload Manager starting...
[2025-10-23 10:30:45.125] [DEBUG] [1234] TCP server binding to 0.0.0.0:5000
[2025-10-23 10:30:45.126] [INFO] [1234] TCP server listening on port 5000
[2025-10-23 10:30:45.127] [INFO] [1235] UDP broadcaster started (5 Hz)
[2025-10-23 10:30:45.128] [INFO] [1236] Heartbeat handler started (1 Hz)
[2025-10-23 10:30:48.234] [ERROR] [1237] Failed to send heartbeat: Network unreachable
```

**Logger Class Design:**
```cpp
class Logger {
public:
    enum class Level { DEBUG, INFO, WARNING, ERROR };

    static void init(const std::string& log_file_path);
    static void setLevel(Level min_level);
    static void close();

    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warning(const std::string& message);
    static void error(const std::string& message);

private:
    static void log(Level level, const std::string& message);
    static std::string levelToString(Level level);
    static std::string getTimestamp();

    static std::ofstream log_file_;
    static std::mutex mutex_;
    static Level min_level_;
};
```

**Log File Location:**
- Path: `/home/dpm/DPM/sbc/logs/payload_manager.log`
- Rotation: Not implemented in Phase 1 (manual cleanup)
- Permissions: 644 (dpm:dpm)

**Usage:**
```cpp
Logger::init("/home/dpm/DPM/sbc/logs/payload_manager.log");
Logger::setLevel(Logger::Level::DEBUG);

Logger::info("TCP server started on port 5000");
Logger::debug("Received command: system.get_status");
Logger::error("Failed to bind socket: " + std::string(strerror(errno)));
```

### 6. Configuration Management

**config.h - Compile-time Constants:**
```cpp
#ifndef CONFIG_H
#define CONFIG_H

namespace config {
    // Network configuration
    constexpr int TCP_PORT = 5000;
    constexpr int UDP_STATUS_PORT = 5001;
    constexpr int UDP_HEARTBEAT_PORT = 5002;
    constexpr const char* GROUND_IP = "192.168.144.11";
    constexpr const char* AIR_IP = "192.168.144.20";

    // Timing configuration
    constexpr int STATUS_INTERVAL_MS = 200;      // 5 Hz
    constexpr int HEARTBEAT_INTERVAL_MS = 1000;  // 1 Hz
    constexpr int HEARTBEAT_TIMEOUT_SEC = 10;

    // Protocol configuration
    constexpr const char* PROTOCOL_VERSION = "1.0";
    constexpr const char* SERVER_ID = "payload_manager";
    constexpr const char* SERVER_VERSION = "1.0.0";

    // Logging configuration
    constexpr const char* LOG_FILE = "/home/dpm/DPM/sbc/logs/payload_manager.log";

    // Buffer sizes
    constexpr int TCP_BUFFER_SIZE = 8192;
    constexpr int UDP_BUFFER_SIZE = 4096;
}

#endif // CONFIG_H
```

**Future Enhancements (Phase 2+):**
- Runtime configuration file (JSON/YAML)
- Environment variable overrides
- Configuration validation
- Hot-reload support

### 7. Message Protocol Implementation

**Base Message Structure:**
All messages follow this JSON format:
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

**messages.h - Message Structures:**
```cpp
struct BaseMessage {
    std::string protocol_version;
    std::string message_type;
    int sequence_id;
    int64_t timestamp;
    nlohmann::json payload;
};

struct HandshakeCommand {
    std::string client_id;
    std::string client_version;
};

struct HandshakeResponse {
    std::string server_id;
    std::string server_version;
    std::vector<std::string> capabilities;
};

struct SystemStatus {
    int64_t uptime_seconds;
    double cpu_percent;
    int64_t memory_mb;
    int64_t memory_total_mb;
    double disk_free_gb;
    double network_rx_mbps;
    double network_tx_mbps;
};

struct CameraStatus {
    bool connected;
    std::string model;
    int battery_percent;
    int remaining_shots;
};

struct StatusBroadcast {
    SystemStatus system;
    CameraStatus camera;
    // Phase 3: GimbalStatus gimbal;
};

struct HeartbeatMessage {
    std::string sender;  // "air" or "ground"
    int64_t uptime_seconds;
};
```

**Phase 1 Commands to Implement:**
1. `handshake` - Initial connection handshake
2. `system.get_status` - Get system status

**Phase 1 Commands to Reject (Error 5002):**
- `camera.set_property`
- `camera.capture`
- `camera.get_properties`
- `camera.record`
- Any camera/gimbal commands

---

## KEY DESIGN DECISIONS

### Decision Log

1. **No Sony SDK in Phase 1**
   - Rationale: Focus on network protocol validation first
   - Impact: Faster initial delivery, cleaner testing
   - Risk: None (stub interface compatible with Phase 2)

2. **POSIX Sockets (no Boost.Asio)**
   - Rationale: Simpler, fewer dependencies, adequate for use case
   - Impact: More manual network code, but full control
   - Risk: More verbose code, but well-understood patterns

3. **nlohmann/json from System Package**
   - Rationale: Widely available, excellent documentation, easy to use
   - Impact: Simple JSON handling with minimal code
   - Risk: Slightly slower than alternatives, but acceptable for this protocol

4. **Thread-per-Client for TCP**
   - Rationale: Simple design, adequate for low connection count (1-2 clients)
   - Impact: Easy to implement and debug
   - Risk: Not scalable to hundreds of clients (not a concern here)

5. **RPATH Configuration**
   - Rationale: Simplifies Sony SDK library loading in Phase 2
   - Impact: No need for LD_LIBRARY_PATH setup
   - Risk: None, standard practice

6. **File-based Logging**
   - Rationale: Better for headless operation, persistent across restarts
   - Impact: Easier debugging, log analysis
   - Risk: Log file growth (manual cleanup for Phase 1)

7. **Compile-time Configuration**
   - Rationale: Simpler for Phase 1, no file parsing needed
   - Impact: Requires rebuild to change config
   - Risk: Less flexible, but adequate for MVP

---

## IMPLEMENTATION SEQUENCE

### Incremental Build Order

**Step 1: Foundation**
- Create project structure
- Write CMakeLists.txt
- Create config.h
- Create messages.h

**Step 2: Logger**
- Implement utils/logger.h/cpp
- Unit test: write logs, verify format

**Step 3: System Info**
- Implement utils/system_info.h/cpp
- Unit test: read CPU, memory, disk stats

**Step 4: TCP Server**
- Implement protocol/tcp_server.h/cpp
- Implement handshake handler
- Implement system.get_status handler
- Test: netcat connections, command/response

**Step 5: UDP Broadcaster**
- Implement protocol/udp_broadcaster.h/cpp
- Integrate system_info
- Test: UDP listener receives 5 Hz messages

**Step 6: Heartbeat Handler**
- Implement protocol/heartbeat.h/cpp
- Test: bidirectional heartbeat exchange

**Step 7: Camera Stub**
- Implement camera/camera_interface.h
- Implement camera/camera_stub.cpp
- Integrate into UDP broadcaster

**Step 8: Main Integration**
- Implement src/main.cpp
- Signal handling
- Component initialization
- Test: full system integration

**Step 9: Testing & Validation**
- Run Connectivity_Test_Strategy.md Phase 1-2 tests
- Fix bugs
- Run Phase 3-4 tests with Android app
- Performance validation
- Memory leak check (valgrind)

**Step 10: Documentation & Deployment**
- Update README.md
- Document build process
- Document testing results
- Create deployment guide

---

## RISKS & MITIGATION

### Identified Risks

**1. Network Configuration Issues**
- Risk: Static IP not set correctly, ports blocked
- Mitigation: Document network setup steps, provide verification scripts
- Severity: Medium
- Likelihood: Medium

**2. Port Conflicts**
- Risk: Ports 5000-5002 already in use
- Mitigation: Check port availability at startup, fail fast with clear error
- Severity: Low
- Likelihood: Low

**3. Thread Resource Overhead**
- Risk: Too many threads, excessive context switching
- Mitigation: Monitor with htop, limit max TCP connections if needed
- Severity: Low
- Likelihood: Low

**4. JSON Parsing Performance**
- Risk: nlohmann/json overhead at high message rates
- Mitigation: Profile with realistic load, optimize if needed (unlikely for Phase 1)
- Severity: Low
- Likelihood: Low

**5. Sony SDK Integration Complexity (Phase 2)**
- Risk: Callback threading issues, SDK lifecycle management
- Mitigation: Study example code thoroughly, incremental testing
- Severity: Medium
- Likelihood: Medium (future phase)

**6. Log File Growth**
- Risk: Logs fill disk over time
- Mitigation: Document manual cleanup, implement rotation in future phase
- Severity: Low
- Likelihood: Medium

**7. Raspberry Pi Resource Limits**
- Risk: Insufficient CPU/memory on target hardware
- Mitigation: Test on actual hardware early, monitor resource usage
- Severity: Medium
- Likelihood: Low

---

## SUCCESS CRITERIA

### Phase 1 Completion Criteria

**Functionality:**
- ✅ Service compiles without errors or warnings (-Wall -Wextra)
- ✅ Service starts and runs without crashes
- ✅ TCP server accepts connections on port 5000
- ✅ Handshake exchange works correctly
- ✅ system.get_status command returns valid data
- ✅ Status broadcasts sent at ~5 Hz (measured with test script)
- ✅ Heartbeat sent/received at ~1 Hz (measured)
- ✅ JSON parsing/generation works for all messages
- ✅ Logging produces readable, timestamped logs
- ✅ Graceful shutdown on SIGTERM/SIGINT

**Testing:**
- ✅ All Phase 1 tests pass (Network Layer)
- ✅ All Phase 2 tests pass (Protocol Layer)
- ✅ All Phase 3 tests pass (Application Layer)
- ✅ At least 80% of Phase 4 tests pass (Error Handling)
- ✅ Android app can connect and receive status updates
- ✅ No memory leaks detected (valgrind clean)
- ✅ Resource usage within limits (< 30% CPU, < 256 MB RAM)

**Code Quality:**
- ✅ Code follows C++17 best practices
- ✅ RAII for all resource management
- ✅ Smart pointers (no raw pointer ownership)
- ✅ Const correctness
- ✅ Thread-safe implementation verified
- ✅ Clean shutdown verified
- ✅ README documents build and run process

**Documentation:**
- ✅ Build plan documented (this file)
- ✅ Progress tracked (PROGRESS_AND_TODO.md)
- ✅ README with build instructions
- ✅ Code comments for complex logic
- ✅ API documentation for public interfaces

---

## TIMELINE ESTIMATE

**Estimated Implementation Time:**
- Step 1-2 (Foundation + Logger): 1 hour
- Step 3 (System Info): 30 minutes
- Step 4 (TCP Server): 2 hours
- Step 5 (UDP Broadcaster): 1 hour
- Step 6 (Heartbeat): 1 hour
- Step 7 (Camera Stub): 30 minutes
- Step 8 (Main Integration): 1 hour
- Step 9 (Testing & Validation): 2 hours
- Step 10 (Documentation): 30 minutes

**Total Estimated Time:** ~10 hours of implementation work

**Assumptions:**
- No major blockers
- Development environment ready
- Dependencies available
- Testing infrastructure available

---

## NEXT STEPS

1. **Await User Approval** of this build plan
2. **Install Dependencies** on Raspberry Pi
3. **Create Project Structure** (directories, files)
4. **Implement Step-by-Step** following sequence above
5. **Test Incrementally** after each major component
6. **Integration Testing** with Android app
7. **Deploy and Validate** on actual hardware

---

## IMPLEMENTATION STATUS (October 24, 2025)

### ✅ Phase 1 Implementation: COMPLETE

**All Core Components Implemented:**
- ✅ Logger system (utils/logger.cpp/h)
- ✅ System info reader (utils/system_info.cpp/h)
- ✅ TCP command server (protocol/tcp_server.cpp/h)
- ✅ UDP status broadcaster (protocol/udp_broadcaster.cpp/h)
- ✅ Heartbeat handler (protocol/heartbeat.cpp/h)
- ✅ Camera stub interface (camera/camera_stub.cpp, camera_interface.h)
- ✅ Main application (src/main.cpp)
- ✅ Build system (CMakeLists.txt)
- ✅ **Binary builds successfully:** `build/payload_manager`

### ✅ Docker Deployment: COMPLETE

**Problem Identified:**
- Sony SDK requires libxml2 v2.x (Ubuntu 20.04/22.04)
- Host system: Ubuntu 25.04 with libxml2 v16.x (incompatible ABI)
- Linker errors: `undefined reference to xmlParseFile@LIBXML2_2.4.30`

**Solution Implemented:**
- ✅ Created Dockerfile.prod with Ubuntu 22.04 base
- ✅ Compiled C++ payload_manager inside container (no libxml2 errors!)
- ✅ Built Docker image: `payload-manager:latest` (1.03GB)
- ✅ Deployed container in production mode with:
  - Host networking (192.168.144.20)
  - USB passthrough (/dev/bus/usb)
  - Auto-restart enabled
  - Persistent logs volume
- ✅ Created build/run helper scripts
- ✅ Updated all documentation for C++ implementation

**Container Status:**
```
Name: payload-manager
Status: Running
Uptime: Stable
Mode: Production (restart: always)
Binary: /app/sbc/build/payload_manager
Sony SDK: /app/sdk (fully integrated)
```

### ✅ Sony SDK Integration: IN PROGRESS

**Completed:**
- ✅ Created test_camera.cpp - Basic SDK testing
- ✅ Created test_shutter.cpp - Shutter command testing
- ✅ Fixed adapter loading issue (error 0x34563):
  - Copy CrAdapter/ to build directory
  - Only link libCr_Core.so dynamically
  - Adapters load at runtime from ./CrAdapter/
- ✅ Camera enumeration working (Sony A1 detected via USB)
- ✅ RemoteCli verified working in Docker container
- ✅ test_camera successfully connects to camera

**Current Issue:**
- 🐛 Connection error 0x8208 in test_shutter.cpp:195
  - SDK::Connect() succeeds but OnConnected callback never fires
  - Prevents shutter command testing
  - RemoteCli works fine (need to compare implementation)
  - Under active investigation

### 📋 Pending

**Network Testing:**
- ⏸️ Blocked - No ethernet connector on Air receiver yet
- TCP server (port 5000)
- UDP broadcaster (port 5001)
- Heartbeat (port 5002)
- Android app integration

**Camera Testing:**
- [x] USB camera enumeration - ✅ Works
- [x] Sony SDK connection test (test_camera) - ✅ Works
- [ ] **DEBUG:** Fix connection error 0x8208
- [ ] Test shutter down/up commands
- [ ] Verify photo capture on camera
- [ ] Property queries (battery, settings)
- [ ] Replace camera_stub with camera_sony implementation

### 📊 Overall Status

**Implementation:** 100% Complete ✅
**Docker Setup:** 100% Complete ✅
**Sony SDK Integration:** 80% Complete (debugging connection issue)
**Network Testing:** 0% (Blocked - hardware)
**Camera Testing:** 60% (enumeration works, debugging commands)

**Overall Project Completion:** ~75%

---

**Document Status:** Implementation Complete, Camera Testing In Progress 🐛
**Current Work:** Debugging connection error 0x8208
**Blocking:** Camera battery recharging
**Phase:** Phase 1 Complete, Phase 2 (Camera SDK) Active Development
**Last Updated:** October 24, 2025 (Shutter testing in progress)
