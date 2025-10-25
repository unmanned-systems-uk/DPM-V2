# DPM Air-Side (SBC) - Architecture Documentation

**Version**: 1.0
**Date**: October 25, 2025
**Project**: Drone Payload Manager (DPM) - Air-Side Service
**Platform**: Raspberry Pi 5 (Ubuntu 22.04 LTS ARM64)
**Language**: C++17

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Structure](#2-project-structure)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Components](#4-core-components)
5. [Network Layer](#5-network-layer)
6. [Camera Integration](#6-camera-integration) - Phase 2
7. [Gimbal Integration](#7-gimbal-integration) - Phase 2
8. [Video Streaming](#8-video-streaming) - Phase 2
9. [Protocol Implementation](#9-protocol-implementation) - Phase 2
10. [Threading Model](#10-threading-model) - Phase 2
11. [Memory Management](#11-memory-management) - Phase 3
12. [Error Handling](#12-error-handling) - Phase 3
13. [Configuration System](#13-configuration-system) - Phase 3
14. [Dependencies](#14-dependencies) - Phase 3
15. [Build System](#15-build-system) - Phase 3
16. [Testing](#16-testing) - Phase 4
17. [Code Conventions](#17-code-conventions) - Phase 4
18. [Deployment](#18-deployment) - Phase 4
19. [Performance Optimization](#19-performance-optimization) - Phase 4
20. [Known Issues & Technical Debt](#20-known-issues--technical-debt) - Phase 4
21. [Future Roadmap](#21-future-roadmap) - Phase 4

---

## 1. Executive Summary

### 1.1 Project Overview

**Purpose**: Real-time payload management service for professional UAV operations running on Raspberry Pi 5, providing centralized control of Sony Alpha cameras and gimbal systems via network communication with H16 ground station.

**Primary Responsibilities**:
- **Sony Camera Control**: USB-based camera control via Sony Camera Remote SDK v2.00.00
  - Shutter release (capture)
  - Property management (shutter speed, aperture, ISO, white balance, focus mode, file format, drive mode, white balance temperature)
  - Camera status monitoring
  - Automatic reconnection on disconnect
- **Network Communication**: Dual protocol (TCP/UDP) communication with H16 ground station
  - TCP command server (port 5000) - bidirectional command/response
  - UDP status broadcaster (port 5001, 5Hz) - real-time telemetry
  - UDP heartbeat (port 5002, 1Hz) - connection health monitoring
- **System Monitoring**: Real-time system resource monitoring and reporting
  - CPU usage, memory consumption
  - Network statistics
  - Uptime tracking
- **Notification System**: Real-time UI notifications for critical events
  - Camera disconnect/reconnect warnings
  - System status changes
  - Error condition alerts

**Deployment**: Runs as containerized Docker service on Raspberry Pi 5, communicating with H16 ground station over 192.168.144.x (Ethernet) or 10.0.1.x (WiFi) network.

### 1.2 Technology Stack

**Programming Language**: C++17

**Why C++17**:
- **Performance**: Real-time operations require low latency (<50ms command response)
- **Hardware Integration**: Direct Sony SDK integration requires C++ native libraries
- **Memory Control**: Embedded system constraints (4-8GB RAM) demand efficient memory management
- **Industry Standard**: UAV payload systems universally use C/C++ for reliability and predictability
- **Thread Control**: Precise multi-threading control for concurrent network/camera/gimbal operations

**Core Libraries**:
- **Sony Camera Remote SDK v2.00.00** (Proprietary C++ libraries)
  - `libCr_Core.so` - Core camera control library
  - `CrAdapter/*.so` - Dynamic camera model adapters
- **nlohmann-json 3.11.2+** (Header-only JSON library)
  - JSON parsing and serialization for protocol messages
  - Header-only deployment simplifies dependency management
- **POSIX Sockets** (libc)
  - TCP/UDP networking (no external dependencies)
  - Native Linux socket API for maximum performance
- **pthreads** (libc)
  - Multi-threading support (native POSIX threads)
  - Thread synchronization primitives
- **libxml2** (System library)
  - Required by Sony SDK for camera metadata parsing
- **libusb-1.0** (System library)
  - USB device access for Sony camera communication

**Build System**:
- **CMake 3.16+** - Cross-platform build configuration
- **GCC 11.4.0** (ARM64) - GNU C++ compiler with C++17 support
- **Make/Ninja** - Build execution
- **Docker** - Containerized build and deployment environment

**Operating System**:
- **Ubuntu 22.04 LTS ARM64** (Jammy Jellyfish)
- **Kernel**: Linux 6.17.0-1003-raspi (Raspberry Pi optimized)
- **Init System**: systemd (service management via Docker restart policies)

### 1.3 Key Features

**Implemented** (✅):

**Network Communication**:
- ✅ TCP command server (port 5000) - Full duplex JSON protocol
- ✅ UDP status broadcaster (port 5001, 5Hz) - Real-time telemetry streaming
- ✅ UDP heartbeat (port 5002, 1Hz) - Connection health monitoring with timeout detection
- ✅ Dynamic IP configuration via environment variable (DPM_GROUND_IP)
- ✅ Notification system - Real-time UI alerts for camera events

**Protocol Implementation** (Protocol v1.0):
- ✅ JSON-based message protocol with sequence IDs and timestamps
- ✅ Message types: handshake, command, response, status, heartbeat, notification
- ✅ Command routing and validation
- ✅ Error code system (5000-5999 protocol errors, 1000-1999 camera errors)

**Sony Camera Integration**:
- ✅ Sony Alpha camera connection via USB (tested with ILCE-1)
- ✅ Camera status monitoring (connected, model, battery, remaining shots)
- ✅ Shutter release command (complete DOWN→UP sequence)
- ✅ Camera property control (8 Phase 1 properties implemented):
  - shutter_speed (auto, 1/8000 through 30s)
  - aperture (auto, f/1.4 through f/22)
  - iso (auto, 100 through 102400)
  - white_balance (12 presets: auto, daylight, shade, cloudy, tungsten, fluorescent variants, flash, temperature, custom)
  - white_balance_temperature (2500-9900 Kelvin)
  - focus_mode (af_s, af_c, af_a, dmf, manual)
  - file_format (jpeg, raw, jpeg_raw)
  - drive_mode (single, continuous_lo/hi, self_timer_10s/2s, bracket)
- ✅ Automatic camera reconnection (30-second health check + on-demand retry)
- ✅ Camera disconnect/reconnect notifications to UI

**System Monitoring**:
- ✅ CPU usage percentage tracking
- ✅ Memory usage monitoring (used/total)
- ✅ System uptime tracking
- ✅ Network statistics (placeholder - disk/network I/O)

**Not Yet Implemented** (⏳):
- ⏳ Gimbal control (Gremsy gSDK / SimpleBGC integration)
- ⏳ RTSP video streaming
- ⏳ Content management (image download from camera)
- ⏳ MAVLink flight controller integration
- ⏳ Storage management and media catalog
- ⏳ Advanced camera features (exposure compensation, metering mode, image quality)

### 1.4 Development Status

**Current Phase**: Phase 1 Complete - Camera Integration Operational

**Current Version**: 1.1.0 (Protocol v1.0)

**Completion Status**: 99% Phase 1 Complete

**Recent Milestones** (October 23-25, 2025):
- ✅ **October 25, 15:48** - Fixed critical camera lockup bug (shutter release sequence)
- ✅ **October 25, 14:51** - Implemented camera reconnection system with UI notifications
- ✅ **October 25, 05:47** - Completed camera property commands (8 Phase 1 properties)
- ✅ **October 25, 03:30** - Ground-side value format documentation created
- ✅ **October 24, 22:45** - Fixed camera callback timing issue (41ms connection time)
- ✅ **October 24, 16:00** - Implemented camera.capture command with Sony SDK
- ✅ **October 23, 14:00** - Core network stack operational (TCP/UDP/Heartbeat)

**Current Work**:
- Testing camera property control with Android ground station
- Verifying camera reconnection behavior under production conditions

**Next Milestones**:
- Phase 2: Gimbal integration (Gremsy T3V3 or SimpleBGC)
- Phase 2: Video streaming infrastructure (RTSP/GStreamer)
- Phase 2: Content download system (image transfer from camera)

### 1.5 Target Hardware

**Single Board Computer**:
- **Model**: Raspberry Pi 5 Model B Rev 1.1
- **CPU**: Broadcom BCM2712 (Quad-core Cortex-A76 ARM v8.2-A 64-bit SoC @ 2.4GHz)
- **RAM**: 8GB LPDDR4X-4267 SDRAM (tested configuration)
- **Storage**: microSD card 32GB+ (SanDisk Extreme PRO UHS-I U3 V30 recommended)
- **USB**: USB 3.0 ports (2x USB 3.0, 2x USB 2.0)
- **Network**: Gigabit Ethernet + WiFi 5 (802.11ac dual-band)

**Connected Hardware**:
- **Camera**: Sony Alpha ILCE-1 (Sony A1)
  - Connection: USB 3.0 Type-C
  - Control: Sony Camera Remote SDK v2.00.00
  - PC Remote Mode required for SDK control
  - Tested connection time: 41ms (from discovery to ready)
- **Gimbal**: (Phase 2)
  - Gremsy T3V3 (serial UART connection) OR
  - SimpleBGC-based gimbal (serial UART connection)
- **Network**: Ethernet to H16 ground station
  - Default: 192.168.144.x network (R16 Ethernet)
  - Alternative: 10.0.1.x network (WiFi testing)
  - Configurable via DPM_GROUND_IP environment variable
- **Flight Controller**: (Future) Ardupilot-based via MAVLink

**Operating Environment**:
- **Temperature**: -10°C to 50°C (operational), -20°C to 60°C (storage)
- **Humidity**: 10% to 90% non-condensing
- **Vibration**: UAV flight conditions (tested in flight)
- **Power**: 5V 3A via USB-C (27W PSU recommended)
- **Power Backup**: Battery-backed power supply recommended for aerial operations

**USB Configuration Requirements**:
- USB memory allocation: 150MB (configured via usbcore.usbfs_memory_mb=150)
- Required for Sony camera bulk transfers and high-resolution image operations
- Configured in `/boot/firmware/cmdline.txt`

---

## 2. Project Structure

### 2.1 Directory Layout

```
sbc/
├── CMakeLists.txt                  # Root CMake build configuration
├── README.md                       # Project overview and quick start
├── Dockerfile                      # Development container definition
├── Dockerfile.prod                 # Production container definition
├── .gitignore                      # Git ignore rules
│
├── build_container.sh              # Build Docker image script
├── run_container.sh                # Run container script (prod/wifi/dev modes)
├── rebuild.sh                      # Quick rebuild helper
├── shell.sh                        # Container shell access
├── test_camera.sh                  # Camera connection test script
│
├── src/                            # Source files (.cpp)
│   ├── main.cpp                    # Application entry point (service lifecycle)
│   │
│   ├── protocol/                   # Network protocol implementation
│   │   ├── tcp_server.cpp          # TCP command server (port 5000)
│   │   ├── tcp_server.h            # TCP server interface
│   │   ├── udp_broadcaster.cpp     # UDP status broadcaster (5Hz, port 5001)
│   │   ├── udp_broadcaster.h       # UDP broadcaster interface
│   │   ├── heartbeat.cpp           # UDP heartbeat manager (1Hz, port 5002)
│   │   ├── heartbeat.h             # Heartbeat interface
│   │   └── messages.h              # Protocol message structures and helpers
│   │
│   ├── camera/                     # Sony camera integration
│   │   ├── camera_sony.cpp         # Sony SDK implementation (actual camera)
│   │   ├── camera_sony.h           # Sony camera class definition
│   │   ├── camera_interface.h      # Abstract camera interface
│   │   └── camera_stub.cpp         # Stub implementation (testing without camera)
│   │
│   ├── utils/                      # Utility functions
│   │   ├── logger.cpp              # Thread-safe logging system
│   │   ├── logger.h                # Logger interface
│   │   ├── system_info.cpp         # System monitoring (CPU/memory/uptime)
│   │   └── system_info.h           # System info interface
│   │
│   ├── config.h                    # Global configuration constants
│   │
│   ├── test_camera.cpp             # Sony SDK camera connection test
│   ├── test_shutter.cpp            # Camera shutter release test
│   └── test_integration.cpp        # Component integration test
│
├── docs/                           # Documentation
│   ├── SBC_ARCHITECTURE.md         # This file - comprehensive architecture docs
│   ├── PROGRESS_AND_TODO.md        # Development progress tracker
│   ├── CC_READ_THIS_FIRST.md       # Claude Code workflow instructions
│   ├── BUILD_AND_IMPLEMENTATION_PLAN.md  # Phase-based implementation plan
│   ├── DOCKER_SETUP.md             # Docker deployment guide
│   ├── GIT_WORKFLOW.md             # Git branching and commit conventions
│   ├── WIFI_TESTING.md             # WiFi network testing guide
│   ├── GROUND_SIDE_VALUE_FORMAT.md # Android app value format reference
│   └── protocol/                   # Protocol specifications
│       ├── protocol_v1.0.json      # Protocol definition (commands, errors, formats)
│       ├── camera_properties.json  # Camera property specifications
│       ├── commands.json           # Command implementation tracking
│       └── PROTOCOL_VALUE_MAPPING.md  # Sony SDK value conversion tables
│
└── logs/                           # Runtime logs (created by container)
    └── payload_manager.log         # Service log file
```

### 2.2 Source Code Organization

**File Count Summary**:
- C++ Source files (.cpp): 11 files
- Header files (.h): 9 files
- Test programs: 3 programs (test_camera, test_shutter, test_integration)
- Documentation files: 15+ markdown files

**Module Breakdown**:

| Module | Files | Lines of Code | Purpose |
|--------|-------|---------------|---------|
| Protocol Layer | 6 files | ~2,500 LOC | TCP/UDP networking, message handling |
| Camera Integration | 3 files | ~1,800 LOC | Sony SDK wrapper, property control |
| Utilities | 4 files | ~800 LOC | Logging, system monitoring |
| Main Service | 1 file | ~300 LOC | Service lifecycle, component coordination |
| Configuration | 1 file | ~50 LOC | Global constants |
| **Total** | **15 files** | **~5,450 LOC** | Complete payload manager |

### 2.3 External Dependencies

**Sony Camera Remote SDK** (Proprietary):
- Location: `/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/`
- Libraries:
  - `libCr_Core.so` - Core SDK library (linked at build time)
  - `CrAdapter/*.so` - Camera model adapters (loaded dynamically at runtime)
- Headers: `app/CRSDK/*.h`
- Size: ~50MB total

**System Libraries** (Ubuntu 22.04 packages):
- `nlohmann-json3-dev` - JSON parsing (header-only)
- `libxml2-dev` - XML parsing (Sony SDK dependency)
- `libusb-1.0-0-dev` - USB device access

**No External Networking Libraries**:
- Uses native POSIX sockets (no Boost, no external dependencies)
- Minimizes attack surface and deployment complexity

### 2.4 Build Artifacts

**Primary Executable**:
- `payload_manager` - Main service binary (~450KB stripped)

**Test Executables**:
- `test_camera` - Sony SDK connection test (~120KB)
- `test_shutter` - Camera shutter control test (~125KB)
- `test_integration` - Component integration test (~180KB)

**Runtime Requirements**:
- Sony SDK libraries in `LD_LIBRARY_PATH` or adjacent `CrAdapter/` directory
- Writable log directory: `/home/dpm/DPM/sbc/logs/`
- Network access on ports 5000-5002
- USB access for camera communication

---

## 3. Architecture Overview

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5 (Air Side)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │           Payload Manager Service (Docker)                │ │
│  │                                                           │ │
│  │  ┌─────────────┐                                         │ │
│  │  │   main()    │  Service Lifecycle & Component Coord.  │ │
│  │  └──────┬──────┘                                         │ │
│  │         │                                                │ │
│  │         ├──────────┬──────────┬──────────┬──────────┐   │ │
│  │         │          │          │          │          │   │ │
│  │    ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌──▼──┐│ │
│  │    │TCP Srv │ │UDP Bcast│ │Heartbeat│ │Camera  │ │Logger││ │
│  │    │:5000   │ │:5001 5Hz│ │:5002 1Hz│ │ Sony   │ │      ││ │
│  │    └────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘ └──────┘│ │
│  │         │         │          │          │               │ │
│  │         │         │          │          │               │ │
│  │         │         │          │     ┌────▼────┐          │ │
│  │         │         │          │     │Sony SDK │          │ │
│  │         │         │          │     │CrAdapter│          │ │
│  │         │         │          │     └────┬────┘          │ │
│  └─────────┼─────────┼──────────┼──────────┼───────────────┘ │
│            │         │          │          │                 │
│        Ethernet   Ethernet   Ethernet      USB 3.0          │
│            │         │          │          │                 │
└────────────┼─────────┼──────────┼──────────┼─────────────────┘
             │         │          │          │
             │         │          │     ┌────▼────────┐
             │         │          │     │ Sony ILCE-1 │
             │         │          │     │  (Camera)   │
             │         │          │     └─────────────┘
             │         │          │
        192.168.144.x Network (Ethernet)
        or 10.0.1.x Network (WiFi)
             │         │          │
             ▼         ▼          ▼
    ┌────────────────────────────────┐
    │   H16 Ground Station (GCS)     │
    │   192.168.144.11 or 10.0.1.92  │
    │                                │
    │  TCP Client     UDP Listener   │
    │  :5000 (cmd)    :5001 (status) │
    │                 :5002 (hbeat)  │
    └────────────────────────────────┘
```

### 3.2 Component Interaction Flow

**Startup Sequence**:
```
1. main() entry point
   ├─> Initialize Sony SDK
   ├─> Create CameraSony instance
   ├─> Attempt camera connection (5-second discovery timeout)
   │   ├─ Success: Camera ready (41ms typical connection time)
   │   └─ Failure: Continue without camera, health check will retry
   ├─> Create TCPServer (port 5000)
   ├─> Create UDPBroadcaster (port 5001, target: ground station IP)
   ├─> Create Heartbeat (port 5002, send+receive)
   ├─> Start all components (spawn threads)
   ├─> Start camera health check thread (30s interval)
   └─> Enter main loop (monitor heartbeat timeout, handle Ctrl+C)
```

**Runtime Operation**:
```
┌─────────────────────┐         ┌──────────────────┐
│  Ground Station     │         │  Payload Manager │
│  (H16 Android App)  │         │  (Raspberry Pi)  │
└──────────┬──────────┘         └────────┬─────────┘
           │                             │
           │  1. TCP Handshake           │
           ├────────────────────────────>│
           │  {"message_type":"handshake",...}
           │                             │
           │  2. Handshake Response      │
           │<────────────────────────────┤
           │  {"status":"success","capabilities":[...]}
           │                             │
           │  3. UDP Status Stream       │
           │<════════════════════════════│ (5 Hz continuous)
           │  {"camera":{"connected":true,"model":"ILCE-1",...}}
           │                             │
           │  4. UDP Heartbeat Bidirectional
           │<───────────────────────────>│ (1 Hz each direction)
           │  {"sender":"payload_manager","uptime_seconds":123}
           │                             │
           │  5. TCP Command             │
           ├────────────────────────────>│
           │  {"command":"camera.capture",...}
           │                             │
           │     [Camera executes: DOWN + 100ms + UP]
           │                             │
           │  6. TCP Response            │
           │<────────────────────────────┤
           │  {"status":"success","result":{...}}
           │                             │
           │  7. Camera Disconnect Event │
           │<────────────────────────────│ (notification)
           │  {"message_type":"notification","level":"warning",...}
           │                             │
           │  [30s health check detects disconnect, auto-reconnect]
           │                             │
           │  8. Camera Reconnect Event  │
           │<────────────────────────────│ (notification)
           │  {"message_type":"notification","level":"info",...}
```

### 3.3 Threading Model

**Thread Architecture**:

```
Main Thread (payload_manager)
├─ [Initial Setup] SDK init, component creation
├─ [Main Loop] Heartbeat timeout monitoring (500ms poll)
└─ [Shutdown Handler] Signal SIGINT/SIGTERM → graceful stop

Thread 1: TCP Accept Loop (TCPServer::acceptLoop)
├─ [Blocking] accept() on port 5000
├─ [On Connection] Spawn client handler thread
└─ [Lifetime] Runs until server.stop()

Thread 2+: TCP Client Handler (TCPServer::handleClient) [one per client]
├─ [Blocking] recv() on client socket
├─ [On Message] Parse JSON → processCommand() → send response
├─ [Lifetime] Until client disconnects
└─ [Auto-cleanup] Detached threads

Thread N: UDP Status Broadcaster (UDPBroadcaster::broadcastLoop)
├─ [Timed Sleep] 200ms intervals (5 Hz)
├─ [On Tick] Query system status → serialize JSON → UDP send
└─ [Lifetime] Runs until broadcaster.stop()

Thread N+1: Heartbeat Send (Heartbeat::sendLoop)
├─ [Timed Sleep] 1000ms intervals (1 Hz)
├─ [On Tick] Create heartbeat message → UDP send
└─ [Lifetime] Runs until heartbeat.stop()

Thread N+2: Heartbeat Receive (Heartbeat::receiveLoop)
├─ [Blocking] recvfrom() on port 5002
├─ [On Message] Parse heartbeat → update timestamp
└─ [Lifetime] Runs until heartbeat.stop()

Thread N+3: Camera Health Check (cameraHealthCheckThread)
├─ [Timed Sleep] 30 second intervals (chunked into 1s sleeps)
├─ [On Tick] Check camera.isConnected()
│   ├─ If disconnected: attempt reconnect + send WARNING notification
│   └─ If reconnected: send INFO notification
└─ [Lifetime] Runs until g_health_check_running = false

Sony SDK Callback Thread (IDeviceCallback)
├─ [SDK Internal] Managed by libCr_Core.so
├─ [Callbacks] OnConnected(), OnDisconnected(), OnError(), OnWarning()
└─ [Thread-Safe] Uses atomic<bool> for connection state
```

**Thread Synchronization**:
- **Mutexes**: Camera operations (camera_sony.cpp: mutex_), client list (tcp_server.cpp: clients_mutex_)
- **Atomics**: Connection flags (atomic<bool> connected_), shutdown flags (atomic<bool> running_)
- **No Deadlocks**: Single mutex per critical section, no nested locking
- **Thread-Safe Logging**: Logger uses mutex-protected file writes

### 3.4 Data Flow Patterns

**Command Processing Flow**:
```
Ground Station → TCP Socket → TCPServer::handleClient()
    → Parse JSON message
    → TCPServer::processCommand()
        → Validate protocol_version, sequence_id
        → Route to command handler:
            ├─ handleHandshake()
            ├─ handleSystemGetStatus()
            ├─ handleCameraCapture()
            ├─ handleCameraSetProperty()
            └─ handleCameraGetProperties()
        → Handler calls CameraInterface methods
        → Camera operation executes (Sony SDK calls)
        → Create response JSON (success or error)
    → Send response to client
    → Log command execution
```

**Status Broadcasting Flow**:
```
Timer (200ms) → UDPBroadcaster::broadcastLoop()
    → SystemInfo::getStatus()
        ├─ Read /proc/uptime
        ├─ Read /proc/stat (CPU usage)
        ├─ Read /proc/meminfo (memory)
        └─ Calculate network stats (placeholder)
    → CameraInterface::getStatus()
        ├─ Query Sony SDK for battery level
        ├─ Query Sony SDK for remaining shots
        └─ Return camera model + connection state
    → Create status JSON message
        ├─ Add system telemetry
        ├─ Add camera telemetry
        ├─ Add sequence_id + timestamp
    → UDP sendto() to ground station IP:5001
    → Increment sequence counter
```

**Notification Broadcasting Flow** (Camera Events):
```
Event Trigger (camera disconnect/reconnect)
    → CameraHealthCheckThread detects state change
    → TCPServer::sendNotification()
        ├─ Create notification JSON
        │   ├─ level: "warning" | "info" | "error"
        │   ├─ category: "camera" | "gimbal" | "system" | "network"
        │   ├─ title: "Camera Disconnected" | "Camera Connected"
        │   ├─ message: Human-readable description
        │   ├─ action: "reconnecting" | "" (optional)
        │   └─ dismissible: true | false
        ├─ Serialize to JSON string
        └─ Send to all active TCP clients
            ├─ Lock clients_mutex_
            ├─ Iterate active_clients_
            └─ send() with MSG_DONTWAIT (non-blocking)
```

### 3.5 Error Handling Strategy

**Error Code Ranges** (Protocol v1.0):
- **5000-5999**: Protocol errors (invalid JSON, unknown command, etc.)
- **1000-1999**: Camera errors (not connected, busy, invalid property, etc.)
- **2000-2999**: Gimbal errors (future)
- **3000-3999**: Network errors (timeout, message too large, etc.)
- **4000-4999**: System errors (insufficient storage, permission denied, etc.)

**Error Response Pattern**:
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 42,
  "timestamp": 1729876543,
  "payload": {
    "command": "camera.capture",
    "status": "error",
    "error": {
      "code": 1000,
      "message": "Camera not connected",
      "details": "Sony SDK enumeration returned no devices"
    }
  }
}
```

**Recovery Strategies**:

| Error Scenario | Detection | Recovery Action | Notification |
|----------------|-----------|----------------|--------------|
| Camera disconnect | isConnected() = false | Auto-reconnect (30s health check + on-demand) | WARNING → INFO on success |
| Network timeout | recv() timeout | Close connection, wait for reconnect | None (client-side retry) |
| Invalid command | Unknown command string | Return error 5003 | None |
| Sony SDK error | CR_FAILED() macro | Log error, return COMMAND_FAILED | ERROR notification if critical |
| USB memory error | Sony SDK warnings 0x131074 | Fixed (shutter release sequence) | None (prevented) |

---

## 4. Core Components

### 4.1 Main Service (main.cpp)

**Purpose**: Service lifecycle management and component coordination.

**Responsibilities**:
- Initialize Sony SDK
- Create and configure all service components
- Start multi-threaded services
- Monitor system health (heartbeat timeout)
- Handle graceful shutdown on SIGINT/SIGTERM
- Coordinate camera health check thread

**Key Code Structure**:
```cpp
int main(int argc, char* argv[]) {
    // 1. Initialize subsystems
    Logger::init(config::LOG_FILE);
    Logger::setLevel(Logger::Level::DEBUG);

    // 2. Register signal handlers
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    // 3. Create camera interface
    g_camera = std::shared_ptr<CameraInterface>(createCamera());  // Sony SDK
    bool camera_connected = g_camera->connect();  // 5s timeout

    // 4. Create network components
    g_tcp_server = std::make_unique<TCPServer>(config::TCP_PORT);
    g_tcp_server->setCamera(g_camera);

    g_udp_broadcaster = std::make_unique<UDPBroadcaster>(...);
    g_udp_broadcaster->setCamera(g_camera);

    g_heartbeat = std::make_unique<Heartbeat>(...);

    // 5. Start all components (spawn threads)
    g_tcp_server->start();           // Thread: TCP accept loop
    g_udp_broadcaster->start();      // Thread: UDP broadcast loop
    g_heartbeat->start();            // Thread: Heartbeat send + receive

    // 6. Start camera health check
    g_health_check_running = true;
    g_health_check_thread = std::thread(cameraHealthCheckThread);

    // 7. Main loop - monitor heartbeat timeout
    while (!g_shutdown_requested) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        double time_since_heartbeat = g_heartbeat->getTimeSinceLastHeartbeat();
        if (time_since_heartbeat > config::HEARTBEAT_TIMEOUT_SEC) {
            Logger::warning("Ground heartbeat timeout: " +
                          std::to_string(time_since_heartbeat) + "s");
        }
    }

    // 8. Graceful shutdown
    g_health_check_running = false;
    g_health_check_thread.join();
    g_heartbeat->stop();
    g_udp_broadcaster->stop();
    g_tcp_server->stop();
    g_camera->disconnect();

    return 0;
}
```

**Camera Health Check Thread**:
```cpp
void cameraHealthCheckThread() {
    bool was_connected = g_camera->isConnected();
    const int CHECK_INTERVAL_SEC = 30;

    while (g_health_check_running) {
        // Sleep in 1-second chunks for responsive shutdown
        for (int i = 0; i < CHECK_INTERVAL_SEC && g_health_check_running; ++i) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        bool is_connected = g_camera->isConnected();

        // Detect disconnect event
        if (was_connected && !is_connected) {
            Logger::warning("Camera disconnected - attempting reconnection");
            g_tcp_server->sendNotification(
                NotificationLevel::WARNING,
                NotificationCategory::CAMERA,
                "Camera Disconnected",
                "Camera connection lost - attempting automatic reconnection",
                "reconnecting",
                false  // Not dismissible
            );
            was_connected = false;
        }

        // Attempt reconnection
        if (!is_connected) {
            if (g_camera->connect()) {
                Logger::info("Camera reconnected successfully!");
                g_tcp_server->sendNotification(
                    NotificationLevel::INFO,
                    NotificationCategory::CAMERA,
                    "Camera Connected",
                    "Camera successfully reconnected and ready",
                    "",
                    true  // Dismissible
                );
                was_connected = true;
            }
        }
    }
}
```

**Shutdown Behavior**:
- Responds to SIGINT (Ctrl+C) and SIGTERM (Docker stop)
- Stops all threads in reverse startup order
- Gracefully closes network sockets before thread join
- Disconnects camera (releases Sony SDK resources)
- No resource leaks (validated with valgrind in testing)

### 4.2 Configuration System (config.h)

**Purpose**: Centralized configuration constants and runtime settings.

**Design Philosophy**:
- Compile-time constants (constexpr) for performance
- Runtime environment variable support for dynamic IP configuration
- No external config files (simplifies Docker deployment)
- Type-safe constants (no magic numbers in code)

**Configuration Categories**:

**Network Configuration**:
```cpp
namespace config {
    constexpr int TCP_PORT = 5000;              // Command server port
    constexpr int UDP_STATUS_PORT = 5001;       // Status broadcast port
    constexpr int UDP_HEARTBEAT_PORT = 5002;    // Heartbeat port (send+receive)

    constexpr const char* GROUND_IP = "192.168.144.11";  // Default (R16 ethernet)
    constexpr const char* AIR_IP = "192.168.144.20";     // This device

    // Dynamic IP override via environment variable
    inline std::string getGroundStationIP() {
        const char* env_ip = std::getenv("DPM_GROUND_IP");
        if (env_ip != nullptr && env_ip[0] != '\0') {
            return std::string(env_ip);  // WiFi testing: DPM_GROUND_IP=10.0.1.92
        }
        return GROUND_IP;  // Default
    }
}
```

**Timing Configuration**:
```cpp
constexpr int STATUS_INTERVAL_MS = 200;      // 5 Hz (200ms period)
constexpr int HEARTBEAT_INTERVAL_MS = 1000;  // 1 Hz (1000ms period)
constexpr int HEARTBEAT_TIMEOUT_SEC = 10;    // Warning threshold
```

**Protocol Configuration**:
```cpp
constexpr const char* PROTOCOL_VERSION = "1.0";
constexpr const char* SERVER_ID = "payload_manager";
constexpr const char* SERVER_VERSION = "1.0.0";
```

**Buffer Sizes**:
```cpp
constexpr int TCP_BUFFER_SIZE = 8192;   // TCP recv buffer (8KB)
constexpr int UDP_BUFFER_SIZE = 4096;   // UDP recv buffer (4KB)
constexpr int MAX_TCP_CLIENTS = 5;      // Concurrent TCP connections
```

**Capabilities Advertisement**:
```cpp
constexpr const char* CAPABILITIES[] = {
    "handshake",
    "system.get_status"
    // Camera commands dynamically added at runtime
};
constexpr int CAPABILITIES_COUNT = 2;
```

**Future Enhancement**: Configuration file support for advanced deployments (config.json).

### 4.3 Logger (utils/logger.cpp)

**Purpose**: Thread-safe, level-based logging system with stdout+file output.

**Design**:
- **Thread-Safe**: Mutex-protected writes for concurrent logging from all threads
- **Dual Output**: Console (stdout/stderr) + file (configurable path)
- **Level Filtering**: DEBUG, INFO, WARN, ERROR with runtime level control
- **Timestamps**: Millisecond-precision timestamps on all log entries
- **Thread IDs**: Logs thread ID for debugging multi-threaded issues
- **Color Coding**: ANSI color codes for console output (errors = red, warnings = yellow)

**API**:
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
};
```

**Log Format**:
```
[2025-10-25 15:48:35.754] [INFO ] [281473615321120] Payload Manager Service Starting...
[2025-10-25 15:48:40.812] [ERROR] [281473615321120] Failed to enumerate cameras. Status: 0x0
[2025-10-25 15:48:40.812] [WARN ] [281473615321120] Sony camera connection failed - will retry
```

**Usage Pattern**:
```cpp
// Initialization (main.cpp)
Logger::init("/home/dpm/DPM/sbc/logs/payload_manager.log");
Logger::setLevel(Logger::Level::DEBUG);

// Throughout codebase
Logger::info("TCP server listening on port " + std::to_string(port_));
Logger::warning("Camera not connected - attempting reconnection");
Logger::error("Failed to send shutter DOWN command. Status: 0x" + std::to_string(status));
```

**File Rotation**: Not implemented (future enhancement for production deployments).

### 4.4 System Monitor (utils/system_info.cpp)

**Purpose**: Query system resource utilization for telemetry reporting.

**Monitored Metrics**:
- **Uptime**: System uptime in seconds (from `/proc/uptime`)
- **CPU Usage**: Overall CPU percentage (from `/proc/stat`, calculated as delta)
- **Memory**: Used and total memory in MB (from `/proc/meminfo`)
- **Disk Space**: Free disk space in GB (placeholder - currently returns 0)
- **Network I/O**: RX/TX rates in Mbps (placeholder - currently returns 0)

**API**:
```cpp
struct SystemStatus {
    int64_t uptime_seconds;
    double cpu_percent;
    int64_t memory_mb;
    int64_t memory_total_mb;
    double disk_free_gb;
    double network_rx_mbps;
    double network_tx_mbps;

    json toJson() const;  // Serialize to JSON for status messages
};

class SystemInfo {
public:
    static SystemStatus getStatus();
};
```

**Implementation Details**:
- **Non-blocking**: Quick reads from procfs (no system calls that can hang)
- **Lightweight**: Minimal CPU overhead (~0.1% additional CPU usage at 5Hz)
- **Cross-Platform Ready**: Linux-specific now, abstraction layer for future ports

**Example Output**:
```json
{
  "uptime_seconds": 12345,
  "cpu_percent": 15.3,
  "memory_mb": 1024,
  "memory_total_mb": 8192,
  "disk_free_gb": 0,      // Placeholder
  "network_rx_mbps": 0,   // Placeholder
  "network_tx_mbps": 0    // Placeholder
}
```

---

## 5. Network Layer

### 5.1 TCP Command Server (protocol/tcp_server.cpp)

**Purpose**: Bidirectional command/response communication with ground station.

**Port**: 5000 (TCP)

**Protocol**: JSON-based message protocol with sequence IDs and timestamps

**Architecture**:
```
TCPServer
├─ Main Thread: acceptLoop() - Listens on port 5000
│   └─ On accept(): Spawn client handler thread (detached)
├─ Client Handler Threads: handleClient(socket, ip)
│   ├─ Blocking recv() on client socket
│   ├─ Parse JSON messages (newline-delimited)
│   ├─ processCommand() → route to handler
│   ├─ Send JSON response
│   └─ Loop until disconnect
└─ Thread-Safe Client Tracking (for notifications)
    ├─ active_clients_ (vector<int>) protected by clients_mutex_
    └─ sendNotification() broadcasts to all clients
```

**Supported Message Types**:
```
Incoming (from Ground Station):
- handshake     → handleHandshake()
- command       → processCommand() → route to specific handler

Outgoing (to Ground Station):
- response      → Command execution result (success or error)
- notification  → Unsolicited event alerts (camera disconnect, etc.)
```

**Command Handlers**:

| Command | Handler | Description | Camera Required |
|---------|---------|-------------|----------------|
| `handshake` | handleHandshake() | Initial connection, capability negotiation | No |
| `system.get_status` | handleSystemGetStatus() | System resource telemetry | No |
| `camera.capture` | handleCameraCapture() | Trigger camera shutter (DOWN+UP sequence) | Yes |
| `camera.set_property` | handleCameraSetProperty() | Set camera property (8 Phase 1 properties) | Yes |
| `camera.get_properties` | handleCameraGetProperties() | Query camera properties | Yes |

**Example: Camera Capture Handler** (with auto-reconnect):
```cpp
json TCPServer::handleCameraCapture(const json& payload, int seq_id) {
    // Check camera availability
    if (!camera_) {
        return createErrorResponse(seq_id, "camera.capture",
                                  ErrorCode::INTERNAL_ERROR,
                                  "Camera interface not initialized");
    }

    // On-demand reconnection if disconnected
    if (!camera_->isConnected()) {
        Logger::info("Camera not connected - attempting immediate reconnection");
        bool reconnected = camera_->connect();
        if (reconnected) {
            sendNotification(NotificationLevel::INFO, NotificationCategory::CAMERA,
                           "Camera Connected",
                           "Camera successfully reconnected and ready");
        } else {
            return createErrorResponse(seq_id, "camera.capture",
                                      ErrorCode::COMMAND_FAILED,
                                      "Camera not connected");
        }
    }

    // Execute capture (DOWN + 100ms + UP)
    bool success = camera_->capture();

    if (!success) {
        return createErrorResponse(seq_id, "camera.capture",
                                  ErrorCode::COMMAND_FAILED,
                                  "Failed to trigger camera shutter");
    }

    return createSuccessResponse(seq_id, "camera.capture", {
        {"status", "captured"},
        {"message", "Shutter released successfully"}
    });
}
```

**Socket Configuration**:
```cpp
// Server socket options
SO_REUSEADDR  = 1  // Allow rapid restarts (bind to same port immediately)
SO_REUSEPORT  = 1  // Multiple processes can bind (Docker networking)

// Client socket options (per connection)
TCP_NODELAY   = 1  // Disable Nagle's algorithm (low latency priority)
SO_KEEPALIVE  = 1  // Detect dead connections (TCP keepalive probes)
```

**Message Framing**:
- Newline-delimited JSON (`\n` separator)
- Accumulates partial messages in buffer
- Maximum message size: 8192 bytes (TCP_BUFFER_SIZE)

**Graceful Shutdown**:
```cpp
void TCPServer::stop() {
    running_ = false;
    close(server_socket_);  // Unblocks accept()
    accept_thread_.join();  // Wait for accept thread
    // Client threads are detached (auto-cleanup on disconnect)
}
```

**Connection Lifecycle**:
```
Ground Station connects → TCP 3-way handshake
    → acceptLoop() spawns handleClient() thread
    → Client sends handshake message
    → Server responds with capabilities
    → [Bidirectional command/response exchange]
    → [Server may send unsolicited notifications]
    → Client disconnects or network failure
    → handleClient() removes client from active_clients_
    → Thread exits (detached cleanup)
```

### 5.2 UDP Status Broadcaster (protocol/udp_broadcaster.cpp)

**Purpose**: Real-time telemetry streaming to ground station at 5 Hz.

**Port**: 5001 (UDP, outbound to ground station)

**Frequency**: 5 Hz (200ms interval)

**Architecture**:
```
UDPBroadcaster
└─ Broadcast Thread: broadcastLoop()
    ├─ Timer: sleep(200ms)
    ├─ Query system status (SystemInfo::getStatus())
    ├─ Query camera status (camera_->getStatus())
    ├─ Create status JSON message
    ├─ UDP sendto() to ground_ip:5001
    └─ Increment sequence_id
```

**Status Message Structure**:
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 42,
  "timestamp": 1729876543,
  "payload": {
    "system": {
      "uptime_seconds": 12345,
      "cpu_percent": 15.3,
      "memory_mb": 1024,
      "memory_total_mb": 8192,
      "disk_free_gb": 0,
      "network_rx_mbps": 0,
      "network_tx_mbps": 0
    },
    "camera": {
      "connected": true,
      "model": "ILCE-1",
      "battery_percent": 85,
      "remaining_shots": 1234
    },
    "gimbal": {
      "connected": false
    }
  }
}
```

**Message Size**: 400-410 bytes typical (well under UDP MTU of 1472 bytes)

**Reliability**: UDP (fire-and-forget)
- No delivery guarantee
- No acknowledgment
- Ground station tolerates occasional packet loss (5Hz redundancy)
- Sequence ID allows ground station to detect gaps

**Socket Configuration**:
```cpp
socket(AF_INET, SOCK_DGRAM, 0);  // UDP socket
// No special options (no broadcast flag, unicast to ground station IP)
```

**Example Log Output**:
```
[DEBUG] Sent UDP status (seq=0, bytes=403)
[DEBUG] Sent UDP status (seq=1, bytes=403)
[DEBUG] Sent UDP status (seq=2, bytes=402)
```

**Performance**:
- CPU Usage: ~0.2% (background thread, minimal JSON serialization overhead)
- Network Bandwidth: ~16 Kbit/s outbound (400 bytes × 5 Hz × 8 bits/byte)

### 5.3 Heartbeat System (protocol/heartbeat.cpp)

**Purpose**: Bidirectional connection health monitoring between air and ground.

**Port**: 5002 (UDP, bidirectional)

**Frequency**: 1 Hz (both directions)

**Architecture**:
```
Heartbeat
├─ Send Thread: sendLoop()
│   ├─ Timer: sleep(1000ms)
│   ├─ Create heartbeat JSON
│   ├─ UDP sendto() to ground_ip:5002
│   └─ Increment sequence_id
│
└─ Receive Thread: receiveLoop()
    ├─ Blocking recvfrom() on port 5002
    ├─ Parse incoming heartbeat JSON
    ├─ Update last_heartbeat_time_
    └─ Log receipt (DEBUG level)
```

**Heartbeat Message Structure**:
```json
{
  "protocol_version": "1.0",
  "message_type": "heartbeat",
  "sequence_id": 42,
  "timestamp": 1729876543,
  "payload": {
    "sender": "payload_manager",
    "uptime_seconds": 12345
  }
}
```

**Timeout Detection**:
```cpp
// Main thread monitors timeout
while (!g_shutdown_requested) {
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    double time_since_heartbeat = g_heartbeat->getTimeSinceLastHeartbeat();
    if (time_since_heartbeat > config::HEARTBEAT_TIMEOUT_SEC) {  // 10 seconds
        Logger::warning("Ground heartbeat timeout: " +
                      std::to_string(time_since_heartbeat) + "s");
    }
}
```

**Implementation**:
```cpp
class Heartbeat {
public:
    void start();  // Spawn send and receive threads
    void stop();   // Stop both threads
    double getTimeSinceLastHeartbeat() const;  // Seconds since last ground heartbeat

private:
    void sendLoop();     // Send heartbeat every 1s
    void receiveLoop();  // Receive ground heartbeat

    std::atomic<bool> running_;
    std::thread send_thread_;
    std::thread receive_thread_;
    std::chrono::steady_clock::time_point last_heartbeat_time_;
    std::mutex time_mutex_;
};
```

**Socket Configuration**:
```cpp
// Send socket (outbound to ground station)
socket(AF_INET, SOCK_DGRAM, 0);

// Receive socket (listen on port 5002)
socket(AF_INET, SOCK_DGRAM, 0);
bind(port 5002);
```

**Example Log Output**:
```
[DEBUG] Sent heartbeat (seq=0)
[DEBUG] Received heartbeat from ground (seq=15)
[DEBUG] Sent heartbeat (seq=1)
[DEBUG] Received heartbeat from ground (seq=16)
```

**Timeout Action**:
- Current: Log warning every 10 seconds
- Future: Could trigger emergency failsafe (land drone, loiter mode, etc.)

### 5.4 Notification System (protocol/messages.h + tcp_server.cpp)

**Purpose**: Unsolicited event alerts from air-side to ground-side UI.

**Transport**: TCP (via existing command connection)

**Use Cases**:
- Camera disconnect/reconnect events
- System errors requiring user attention
- Status changes requiring UI updates
- (Future) Gimbal errors, storage warnings, flight controller events

**Notification Message Structure**:
```json
{
  "protocol_version": "1.0",
  "message_type": "notification",
  "sequence_id": 42,
  "timestamp": 1729876543,
  "payload": {
    "level": "warning",        // "info" | "warning" | "error"
    "category": "camera",       // "camera" | "gimbal" | "system" | "network"
    "title": "Camera Disconnected",
    "message": "Camera connection lost - attempting automatic reconnection",
    "action": "reconnecting",   // Optional: current action being taken
    "dismissible": false        // Can user dismiss this notification?
  }
}
```

**Notification Levels**:
```cpp
enum class NotificationLevel {
    INFO,     // Informational (green) - camera reconnected, operation complete
    WARNING,  // Attention required (yellow) - camera disconnect, low battery
    ERROR     // Critical issue (red) - system error, operation failed
};
```

**Notification Categories**:
```cpp
enum class NotificationCategory {
    CAMERA,   // Camera-related events
    GIMBAL,   // Gimbal-related events (future)
    SYSTEM,   // System/SBC events (CPU overload, storage full, etc.)
    NETWORK   // Network connectivity issues
};
```

**Broadcast Implementation**:
```cpp
void TCPServer::sendNotification(NotificationLevel level,
                                NotificationCategory category,
                                const std::string& title,
                                const std::string& message,
                                const std::string& action,
                                bool dismissible) {
    // Create notification JSON
    int seq_id = notification_seq_id_++;
    json notification = createNotificationMessage(
        seq_id, level, category, title, message, action, dismissible
    );
    std::string notification_str = notification.dump() + "\n";

    Logger::info("Broadcasting notification: " + title);

    // Send to all connected TCP clients
    std::lock_guard<std::mutex> lock(clients_mutex_);
    for (int client_socket : active_clients_) {
        ssize_t bytes_sent = send(client_socket, notification_str.c_str(),
                                 notification_str.size(), MSG_DONTWAIT);
        if (bytes_sent < 0) {
            Logger::warning("Failed to send notification to client: " +
                          std::string(strerror(errno)));
        }
    }
}
```

**Example Notifications**:

**Camera Disconnect (WARNING)**:
```json
{
  "level": "warning",
  "category": "camera",
  "title": "Camera Disconnected",
  "message": "Camera connection lost - attempting automatic reconnection",
  "action": "reconnecting",
  "dismissible": false
}
```

**Camera Reconnect (INFO)**:
```json
{
  "level": "info",
  "category": "camera",
  "title": "Camera Connected",
  "message": "Camera successfully reconnected and ready",
  "action": "",
  "dismissible": true
}
```

**Ground-Side UI Handling**:
- **INFO**: Display as toast/snackbar (auto-dismiss after 3-5 seconds)
- **WARNING**: Display as persistent notification with progress indicator (dismiss when resolved)
- **ERROR**: Display as alert dialog requiring user acknowledgment

---

**END OF PHASE 1 DOCUMENTATION**

Sections 6-21 will be completed in subsequent phases:
- **Phase 2** (Sections 6-10): Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model
- **Phase 3** (Sections 11-15): Memory Management, Error Handling, Configuration System, Dependencies, Build System
- **Phase 4** (Sections 16-21): Testing, Code Conventions, Deployment, Performance Optimization, Known Issues & Technical Debt, Future Roadmap

---

**Document Generation Date**: October 25, 2025
**Generated By**: Claude Code (Anthropic)
**Air-Side Version**: 1.1.0
**Protocol Version**: 1.0
