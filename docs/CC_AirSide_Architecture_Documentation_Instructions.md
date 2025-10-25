# Claude Code: Air-Side (SBC) Architecture Documentation - Phased Approach

## 📋 Overview

**Purpose**: Generate comprehensive C++ Air-Side architecture documentation in 4 phases to avoid API token limits.

**Target File**: `sbc/docs/SBC_ARCHITECTURE.md`

**Total Sections**: 21 sections across 4 phases

**Estimated Time**: 6-8 hours (1.5-2 hours per phase)

**Problem Solved**: Avoids "Claude's response exceeded the 32000 output token maximum" error

---

## 🎯 Why Phased Approach?

Claude Code has a 32,000 output token limit. Generating the entire C++ architecture document (~12,000+ lines) in one response exceeds this limit.

**Solution**: Break documentation into 4 manageable phases, each creating 5-6 sections.

---

## 📐 Phase Breakdown

| Phase | Sections | Content | Est. Tokens |
|-------|----------|---------|-------------|
| **1** | 1-5 | Executive Summary, Project Structure, Architecture Overview, Core Components, Network Layer | ~18,000 |
| **2** | 6-10 | Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model | ~19,000 |
| **3** | 11-15 | Memory Management, Error Handling, Configuration System, Dependencies, Build System | ~16,000 |
| **4** | 16-21 | Testing, Code Conventions, Deployment, Performance, Known Issues, Future Roadmap | ~14,000 |

---

## 🚀 Phase 1: Foundation & Core (Sections 1-5)

### Task for Claude Code

```
Task: Create SBC_ARCHITECTURE.md - Phase 1 of 4

Create file: sbc/docs/SBC_ARCHITECTURE.md

Generate comprehensive C++ architecture documentation for SECTIONS 1-5 ONLY:

═══════════════════════════════════════════════════════════════════

# DPM Air-Side (SBC) - Architecture Documentation

**Version**: 1.0  
**Date**: [Generation Date]  
**Project**: Drone Payload Manager (DPM) - Air-Side Service  
**Platform**: Raspberry Pi 4 (Ubuntu 22.04 LTS ARM64)  
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

**Purpose**: Real-time payload management service for professional UAV operations

**Primary Responsibilities**:
- Sony camera control via USB SDK
- Gimbal control (Gremsy gSDK / SimpleBGC Serial API)
- Network communication with H16 ground station (TCP/UDP)
- Video streaming via RTSP (if implemented)
- Status monitoring and reporting at 5Hz
- Content management (image/video download and storage)
- Heartbeat monitoring for connection health

**Deployment**: Runs as system service on Raspberry Pi 4, communicates with H16 ground station over 10.0.1.x network

### 1.2 Technology Stack

**Programming Language**: C++17

**Why C++17**:
- Performance requirements for real-time operations
- Direct hardware/SDK integration (Sony SDK, gimbal SDKs)
- Low-latency network communication
- Efficient memory management for embedded system
- Industry standard for UAV payload systems

**Core Libraries**:
- Sony Camera Remote SDK v2.00.00 (C++ libraries)
- nlohmann-json 3.11.2+ (JSON parsing)
- POSIX Sockets (TCP/UDP networking)
- pthreads (multi-threading)
- libusb-1.0 (USB device access)
- [List all other libraries found]

**Optional Libraries** (if used):
- GStreamer (video streaming)
- FFmpeg (video encoding)
- Boost (networking/utilities)
- [Others]

**Build System**:
- CMake 3.16+
- GCC 11+ / Clang 12+ (ARM64 cross-compilation)
- Make / Ninja

**Operating System**:
- Ubuntu 22.04 LTS ARM64
- Kernel: [Document actual version]
- Systemd for service management

### 1.3 Key Features

**Implemented** (✅ - document what exists):
- ✅ TCP command server (port 5000)
- ✅ UDP status broadcaster (port 5001, 5Hz)
- ✅ UDP heartbeat (port 5002, 1Hz)
- ✅ JSON protocol implementation
- ✅ Sony camera basic control
- [List all implemented features]

**In Progress** (🚧):
- 🚧 [Features being developed]

**Planned** (⏳):
- ⏳ RTSP video streaming
- ⏳ Content download from camera
- ⏳ [Other planned features]

### 1.4 Development Status

**Current Phase**: [Document actual phase from PROGRESS_AND_TODO.md]

**Completed Milestones**:
- [List completed items]

**Current Work**:
- [What's being worked on now]

**Next Milestones**:
- [What's coming next]

### 1.5 Target Hardware

**Single Board Computer**:
- Model: Raspberry Pi 4 Model B
- RAM: 4GB or 8GB (recommended 8GB for video streaming)
- Storage: microSD card 32GB+ (Class 10 or UHS-I)
- CPU: Quad-core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz

**Connected Hardware**:
- **Camera**: Sony Alpha series (USB 3.0 connection)
  - Tested models: [List if documented]
- **Gimbal**: 
  - Gremsy T3V3 (serial connection) OR
  - SimpleBGC-based gimbal (serial connection)
- **Network**: Ethernet/WiFi to H16 ground station (10.0.1.x network)
- **Flight Controller**: Ardupilot-based (MAVLink, future integration)

**Operating Environment**:
- Temperature: -10°C to 50°C (operational)
- Humidity: 10% to 90% non-condensing
- Vibration: UAV flight conditions
- Power: 5V 3A via USB-C (battery-backed recommended)

═══════════════════════════════════════════════════════════════════

## 2. Project Structure

### 2.1 Directory Layout

```
sbc/
├── CMakeLists.txt                 # Root CMake configuration
├── README.md                      # Project overview
├── LICENSE                        # License information
├── .gitignore                     # Git ignore rules
│
├── src/                           # Source files (.cpp)
│   ├── main.cpp                   # Application entry point
│   ├── payload_manager.cpp        # Main service coordinator
│   │
│   ├── network/                   # Network communication
│   │   ├── tcp_server.cpp
│   │   ├── udp_broadcaster.cpp
│   │   ├── heartbeat_manager.cpp
│   │   └── [list all other .cpp files]
│   │
│   ├── protocol/                  # Protocol implementation
│   │   ├── message_handler.cpp
│   │   ├── command_processor.cpp
│   │   └── [list all]
│   │
│   ├── camera/                    # Sony camera integration
│   │   ├── sony_camera.cpp
│   │   └── [list all]
│   │
│   ├── gimbal/                    # Gimbal control
│   │   ├── [list all .cpp files]
│   │
│   ├── video/                     # Video streaming (if exists)
│   │   └── [list all]
│   │
│   ├── utils/                     # Utility functions
│   │   └── [list all]
│   │
│   └── storage/                   # Storage management
│       └── [list all]
│
├── include/                       # Header files (.hpp)
│   ├── payload_manager.hpp
│   ├── network/
│   │   └── [list all .hpp files]
│   ├── protocol/
│   │   └── [list all]
│   ├── camera/
│   │   └── [list all]
│   ├── gimbal/
│   │   └── [list all]
│   ├── video/
│   │   └── [list all]
│   ├── utils/
│   │   └── [list all]
│   └── storage/
│       └── [list all]
│
├── tests/                         # Unit and integration tests
│   ├── CMakeLists.txt
│   └── [list all test files]
│
├── config/                        # Configuration files
│   └── [list all config files]
│
├── scripts/                       # Utility scripts
│   ├── install_dependencies.sh
│   ├── build.sh
│   └── [list all scripts]
│
├── docs/                          # Documentation
│   ├── SBC_ARCHITECTURE.md        # This file
│   ├── PROGRESS_AND_TODO.md
│   └── [list all docs]
│
├── external/                      # External dependencies
│   ├── sony_sdk/                  # Sony Camera Remote SDK
│   │   ├── include/
│   │   └── lib/
│   └── [list other external deps]
│
└── build/                         # CMake build directory (gitignored)
    └── [Generated files]
```

**Total Source Files**: [Count actual .cpp files]
**Total Header Files**: [Count actual .hpp files]
**Lines of Code**: [Estimate if possible]

### 2.2 Module Organization

For EACH module directory (network/, protocol/, camera/, etc.), document:

**Module Name**: [e.g., Network Module]
**Directory**: `src/network/`, `include/network/`
**Purpose**: [Brief description]
**Files**: [Count]
**Key Classes**: [List main classes]
**Dependencies**: [What this module depends on]
**Used By**: [What depends on this module]

Example format:
```
#### Network Module
**Location**: `src/network/`, `include/network/`
**Purpose**: Handle TCP/UDP communication with ground station
**Files**: 5 source files, 5 header files
**Key Classes**:
- TcpServer - TCP command listener and handler
- UdpBroadcaster - UDP status broadcasting at 5Hz
- HeartbeatManager - Bidirectional heartbeat monitoring
**Dependencies**: POSIX sockets, pthreads, nlohmann-json
**Used By**: PayloadManager, CommandProcessor
```

[REPEAT FOR ALL MODULES]

### 2.3 File Naming Conventions

**Header Files**: `snake_case.hpp`
- Example: `tcp_server.hpp`, `sony_camera.hpp`, `gimbal_interface.hpp`

**Source Files**: `snake_case.cpp`
- Example: `tcp_server.cpp`, `sony_camera.cpp`, `gimbal_interface.cpp`

**Class Names**: `PascalCase`
- Example: `TcpServer`, `SonyCamera`, `GimbalInterface`

**Function Names**: `snake_case`
- Example: `send_command()`, `get_camera_status()`, `initialize_gimbal()`

**Member Variables**: `snake_case_` (trailing underscore)
- Example: `socket_fd_`, `camera_handle_`, `running_`

**Constants**: `UPPER_SNAKE_CASE`
- Example: `MAX_BUFFER_SIZE`, `DEFAULT_PORT`, `TIMEOUT_MS`

**Namespaces**: `lowercase` (single word or snake_case)
- Example: `namespace dpm`, `namespace network`, `namespace camera_control`

═══════════════════════════════════════════════════════════════════

## 3. Architecture Overview

### 3.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DPM Air-Side Service                         │
│                   (Raspberry Pi 4 - C++17)                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Main Thread (PayloadManager)                  │ │
│  │  - Service initialization                                 │ │
│  │  - Subsystem coordination                                 │ │
│  │  - Periodic health checks                                 │ │
│  │  - Graceful shutdown handling                            │ │
│  └───────────────────────┬───────────────────────────────────┘ │
│                          │                                      │
│  ┌───────────────────────┴───────────────────────────────────┐ │
│  │           Network Layer (Multi-threaded)                   │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐ │ │
│  │  │ TCP Server   │  │ UDP Broadcaster │  │ Heartbeat    │ │ │
│  │  │ Thread       │  │ Thread          │  │ Manager      │ │ │
│  │  │ Port 5000    │  │ Port 5001       │  │ Thread       │ │ │
│  │  │ (Commands)   │  │ (Status 5Hz)    │  │ Port 5002    │ │ │
│  │  │              │  │                 │  │ (HB 1Hz)     │ │ │
│  │  └──────┬───────┘  └────────┬────────┘  └──────┬───────┘ │ │
│  └─────────┼───────────────────┼──────────────────┼─────────┘ │
│            │                   │                  │            │
│  ┌─────────▼───────────────────▼──────────────────▼─────────┐ │
│  │              Protocol Handler Layer                       │ │
│  │  ┌──────────────────┐  ┌────────────────────────────┐    │ │
│  │  │ Message Parser   │  │  Command Processor         │    │ │
│  │  │ (JSON)           │  │  (Dispatcher + Executor)   │    │ │
│  │  │ - Validation     │  │  - Command queue           │    │ │
│  │  │ - Deserialization│  │  - Async execution         │    │ │
│  │  └──────────────────┘  └────────────────────────────┘    │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────▼───────────────────────────────┐ │
│  │                    Control Layer                           │ │
│  │  ┌──────────────────┐  ┌────────────────┐  ┌───────────┐ │ │
│  │  │ Camera           │  │ Gimbal         │  │ Storage   │ │ │
│  │  │ Controller       │  │ Controller     │  │ Manager   │ │ │
│  │  │ - Sony SDK wrap  │  │ - Multi-gimbal │  │ - Cleanup │ │ │
│  │  │ - Capture        │  │ - Position     │  │ - Monitor │ │ │
│  │  │ - Settings       │  │ - Mode control │  │           │ │ │
│  │  └────────┬─────────┘  └───────┬────────┘  └─────┬─────┘ │ │
│  └───────────┼────────────────────┼──────────────────┼───────┘ │
│              │                    │                  │          │
│  ┌───────────▼────────────────────▼──────────────────▼───────┐ │
│  │              Hardware Interface Layer                      │ │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │ Sony SDK     │  │ Gremsy SDK  │  │ File System     │  │ │
│  │  │ C++ Wrapper  │  │ / SimpleBGC │  │ POSIX I/O       │  │ │
│  │  │              │  │ Serial API  │  │                 │  │ │
│  │  └──────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ USB / Serial / Ethernet
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        Physical Hardware                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Sony       │  │ Gremsy/    │  │ Ethernet   │  │ microSD  │ │
│  │ Camera     │  │ SimpleBGC  │  │ to H16     │  │ Storage  │ │
│  │ (USB 3.0)  │  │ Gimbal     │  │ (10.0.1.x) │  │ (32GB+)  │ │
│  │            │  │ (Serial)   │  │            │  │          │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Design Patterns Used

Document each design pattern with C++ code examples from actual codebase:

#### 3.2.1 RAII (Resource Acquisition Is Initialization)

**Purpose**: Automatic resource management via object lifetime

**Usage in Project**:
- Socket file descriptors
- File handles
- Sony SDK objects
- Mutex locks
- Thread management

**Example from Actual Code**:
```cpp
// Include actual example from project, e.g., TcpServer constructor/destructor
class TcpServer {
private:
    int socket_fd_;  // Resource
    
public:
    TcpServer(uint16_t port) {
        // Acquire resource in constructor
        socket_fd_ = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_fd_ < 0) {
            throw std::runtime_error("Failed to create socket");
        }
        // ... bind, listen
    }
    
    ~TcpServer() {
        // Release resource in destructor (automatic cleanup)
        if (socket_fd_ >= 0) {
            close(socket_fd_);
        }
    }
    
    // Delete copy constructor/assignment to prevent double-free
    TcpServer(const TcpServer&) = delete;
    TcpServer& operator=(const TcpServer&) = delete;
    
    // Allow move semantics if needed
    TcpServer(TcpServer&& other) noexcept 
        : socket_fd_(std::exchange(other.socket_fd_, -1)) {}
};
```

**Benefits**:
- No memory leaks
- Exception-safe
- Clear ownership semantics
- Automatic cleanup

---

#### 3.2.2 Dependency Injection

**Purpose**: Improve testability and flexibility

**Example from Actual Code**:
```cpp
// Show actual constructor injection from project
class CommandProcessor {
private:
    std::shared_ptr<CameraController> camera_;
    std::shared_ptr<GimbalInterface> gimbal_;
    
public:
    // Dependencies injected via constructor
    CommandProcessor(
        std::shared_ptr<CameraController> camera,
        std::shared_ptr<GimbalInterface> gimbal
    ) : camera_(camera), gimbal_(gimbal) {}
    
    void process_camera_command(const json& cmd) {
        // Use injected dependency
        camera_->execute_command(cmd);
    }
};
```

**Benefits**:
- Easier unit testing (mock dependencies)
- Loose coupling
- Flexible configuration

---

#### 3.2.3 Strategy Pattern

**Purpose**: Multiple algorithm implementations with common interface

**Usage**: Gimbal implementations (Gremsy vs SimpleBGC)

**Example from Actual Code**:
```cpp
// Abstract interface
class GimbalInterface {
public:
    virtual ~GimbalInterface() = default;
    
    virtual bool initialize() = 0;
    virtual bool set_angle(float pitch, float yaw, float roll) = 0;
    virtual bool set_mode(GimbalMode mode) = 0;
    virtual GimbalStatus get_status() const = 0;
};

// Concrete implementations
class GremsyGimbal : public GimbalInterface {
    // Gremsy gSDK implementation
    bool set_angle(float pitch, float yaw, float roll) override {
        // Gremsy-specific code
    }
};

class SimpleBGCGimbal : public GimbalInterface {
    // SimpleBGC Serial API implementation
    bool set_angle(float pitch, float yaw, float roll) override {
        // SimpleBGC-specific code
    }
};

// Factory or runtime selection
std::unique_ptr<GimbalInterface> create_gimbal(GimbalType type) {
    if (type == GimbalType::GREMSY) {
        return std::make_unique<GremsyGimbal>();
    } else {
        return std::make_unique<SimpleBGCGimbal>();
    }
}
```

---

#### 3.2.4 Observer Pattern (if used)

**Purpose**: Notify multiple objects of state changes

[Document if observer pattern is used, with actual code examples]

---

#### 3.2.5 Singleton Pattern (if used)

**Purpose**: Single instance of Logger, Config, etc.

**Example**:
```cpp
// If Logger uses singleton, show actual implementation
class Logger {
private:
    Logger() = default;
    
public:
    static Logger& instance() {
        static Logger instance;  // Thread-safe in C++11+
        return instance;
    }
    
    // Delete copy/move
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    
    void log(LogLevel level, const std::string& message);
};

// Usage
Logger::instance().log(LogLevel::INFO, "Service started");
```

**Caution**: Document any concerns about testability or global state

---

### 3.3 Threading Architecture

```
Main Thread (PayloadManager)
    │
    ├─► TCP Server Thread
    │   └─► Connection Handler Threads (pool)
    │
    ├─► UDP Broadcaster Thread
    │
    ├─► Heartbeat Send Thread
    │
    ├─► Heartbeat Receive Thread
    │
    └─► Command Processor Thread (if separate)
        └─► Camera/Gimbal operations (may block)
```

**Thread Count**: [Document typical thread count]

**Thread Management**:
- Thread creation: [How threads are created]
- Thread joining: [How threads are cleaned up]
- Thread pools: [If used]

**Synchronization Primitives**:
- `std::mutex` - [Usage]
- `std::lock_guard` / `std::unique_lock` - [Usage]
- `std::atomic` - [Usage]
- `std::condition_variable` - [If used]

**Thread Safety Strategy**:
[Describe approach to thread safety, data sharing, etc.]

---

### 3.4 Data Flow Diagrams

#### Command Flow (Ground → Air)

```
H16 Ground Station (Android App)
    ↓
TCP Connection (10.0.1.11:5000 → 10.0.1.20:5000)
    ↓
TCP Server Thread (Raspberry Pi)
    ↓ recv() on socket
Raw bytes (length-prefixed JSON)
    ↓ Parse length
Read JSON payload
    ↓ nlohmann::json::parse()
JSON object (command)
    ↓ Validate protocol
MessageHandler
    ↓ Extract command type
CommandProcessor
    ↓ Dispatch to controller
CameraController / GimbalController
    ↓ SDK call
Sony Camera SDK / Gimbal SDK
    ↓ USB/Serial
Hardware (Camera / Gimbal)
    ↓ Operation result
Response (success/error)
    ↓ Build response JSON
TCP Server Thread
    ↓ send() on socket
H16 Ground Station
```

#### Status Flow (Air → Ground)

```
Camera/Gimbal State Change
    ↓ Callback or polling
Controller updates internal state
    ↓ Mutex-protected write
Shared state object
    ↓ 5Hz timer
Status Builder (UDP Broadcaster Thread)
    ↓ Read state (mutex-protected)
Collect all status fields
    ↓ nlohmann::json build
JSON status message
    ↓ Serialize to string
UDP packet
    ↓ sendto() broadcast
10.0.1.255:5001 (or direct to H16)
    ↓ Network
H16 Ground Station
    ↓ Parse and display
Android App UI Update
```

═══════════════════════════════════════════════════════════════════

## 4. Core Components

### 4.1 PayloadManager (Main Service Class)

**Files**: 
- `src/payload_manager.cpp`
- `include/payload_manager.hpp`

**Purpose**: Main application coordinator, lifecycle manager, and subsystem orchestrator

**Class Definition**:
```cpp
// Include ACTUAL class structure from code
class PayloadManager {
public:
    PayloadManager();
    ~PayloadManager();
    
    // Lifecycle
    bool initialize(const std::string& config_file);
    void run();
    void shutdown();
    
    // Status
    bool is_running() const { return running_; }
    
private:
    // Subsystems (document actual members)
    std::unique_ptr<TcpServer> tcp_server_;
    std::unique_ptr<UdpBroadcaster> udp_broadcaster_;
    std::unique_ptr<HeartbeatManager> heartbeat_manager_;
    
    std::unique_ptr<CommandProcessor> command_processor_;
    std::unique_ptr<CameraController> camera_controller_;
    std::unique_ptr<GimbalInterface> gimbal_;
    
    // State
    std::atomic<bool> running_;
    std::mutex state_mutex_;
    
    // Configuration
    Config config_;
    
    // Threads
    std::thread tcp_thread_;
    std::thread udp_thread_;
    std::thread heartbeat_send_thread_;
    std::thread heartbeat_recv_thread_;
    
    // [Document all actual members]
    
    // Private methods (document actual methods)
    void init_network();
    void init_camera();
    void init_gimbal();
    void main_loop();
    void cleanup();
    
    // Signal handling
    static void signal_handler(int signal);
    static PayloadManager* instance_;
};
```

**Initialization Sequence**:
```cpp
// Document actual initialization from code
bool PayloadManager::initialize(const std::string& config_file) {
    // Step 1: Load configuration
    config_ = ConfigParser::load(config_file);
    
    // Step 2: Initialize logger
    Logger::instance().set_level(config_.log_level);
    Logger::instance().log(LogLevel::INFO, "Starting DPM Air-Side Service");
    
    // Step 3: Initialize network subsystems
    init_network();
    
    // Step 4: Initialize camera
    init_camera();
    
    // Step 5: Initialize gimbal
    init_gimbal();
    
    // Step 6: Start threads
    tcp_thread_ = std::thread(&PayloadManager::tcp_server_loop, this);
    udp_thread_ = std::thread(&PayloadManager::udp_broadcaster_loop, this);
    // ... start all threads
    
    // Step 7: Register signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    return true;
}
```

**Main Event Loop**:
```cpp
// Document actual main loop
void PayloadManager::main_loop() {
    using namespace std::chrono;
    auto next_check = steady_clock::now();
    
    while (running_) {
        // 1. Check heartbeat status
        if (!heartbeat_manager_->is_connected()) {
            Logger::instance().log(LogLevel::WARN, "Heartbeat lost");
            // Handle disconnection
        }
        
        // 2. Monitor system health
        check_system_health();
        
        // 3. Periodic maintenance tasks
        // (if any)
        
        // 4. Sleep until next check (e.g., 1 second)
        next_check += seconds(1);
        std::this_thread::sleep_until(next_check);
    }
}
```

**Shutdown Sequence**:
```cpp
// Document actual shutdown
void PayloadManager::shutdown() {
    Logger::instance().log(LogLevel::INFO, "Shutting down DPM Air-Side Service");
    
    // 1. Stop accepting new commands
    running_ = false;
    
    // 2. Signal all threads to stop
    tcp_server_->stop();
    udp_broadcaster_->stop();
    heartbeat_manager_->stop();
    
    // 3. Wait for threads to finish (join)
    if (tcp_thread_.joinable()) tcp_thread_.join();
    if (udp_thread_.joinable()) udp_thread_.join();
    // ... join all threads
    
    // 4. Release hardware resources
    if (camera_controller_) {
        camera_controller_->disconnect();
    }
    if (gimbal_) {
        gimbal_->shutdown();
    }
    
    // 5. Close network connections
    // (handled by RAII destructors)
    
    // 6. Flush logs
    Logger::instance().flush();
}
```

**Signal Handling**:
```cpp
// Document signal handler implementation
void PayloadManager::signal_handler(int signal) {
    if (instance_) {
        Logger::instance().log(LogLevel::INFO, 
            "Received signal " + std::to_string(signal));
        instance_->shutdown();
    }
}
```

**Threading Model**:
- Main thread: Runs main_loop(), handles signals
- TCP thread: Accepts connections, spawns handlers
- UDP thread: Broadcasts status at 5Hz
- Heartbeat threads: Send/receive heartbeat at 1Hz
- [Document actual threading]

---

### 4.2 main.cpp (Entry Point)

**File**: `src/main.cpp`

**Purpose**: Application entry point, CLI parsing, daemonization

**Structure**:
```cpp
// Include actual main() structure
int main(int argc, char* argv[]) {
    // 1. Parse command-line arguments
    std::string config_file = "/etc/dpm/payload_manager.conf";
    bool daemon_mode = false;
    LogLevel log_level = LogLevel::INFO;
    
    // ... argument parsing
    
    // 2. Daemonize if requested
    if (daemon_mode) {
        daemonize();
    }
    
    // 3. Setup logging
    Logger::instance().set_level(log_level);
    
    // 4. Create PayloadManager
    PayloadManager manager;
    
    // 5. Initialize
    if (!manager.initialize(config_file)) {
        std::cerr << "Failed to initialize PayloadManager" << std::endl;
        return 1;
    }
    
    // 6. Run (blocking)
    manager.run();
    
    // 7. Cleanup (called from signal handler or after run())
    manager.shutdown();
    
    // 8. Exit
    return 0;
}
```

**Command-Line Options** (document actual options):
```bash
./payload_manager [options]

Options:
  -c, --config <file>    Configuration file path (default: /etc/dpm/payload_manager.conf)
  -d, --daemon           Run as background daemon
  -v, --verbose          Enable verbose logging (DEBUG level)
  -l, --log-level <level> Set log level (DEBUG, INFO, WARN, ERROR)
  -h, --help             Show help message
  --version              Show version information
```

**Return Codes**:
- 0: Normal exit
- 1: Initialization failure
- 2: Configuration error
- [Document actual return codes]

═══════════════════════════════════════════════════════════════════

## 5. Network Layer

### 5.1 Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Network Layer Architecture                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         TCP Server (Port 5000)                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Accept Thread                               │   │   │
│  │  │  - listen() on socket                        │   │   │
│  │  │  - accept() incoming connections             │   │   │
│  │  │  - Spawn handler thread per connection       │   │   │
│  │  └──────────────┬───────────────────────────────┘   │   │
│  │                 │                                    │   │
│  │  ┌──────────────▼───────────────────────────────┐   │   │
│  │  │  Connection Handler Threads (Pool)           │   │   │
│  │  │  - recv() command (length + JSON)            │   │   │
│  │  │  - Parse and validate                        │   │   │
│  │  │  - Pass to CommandProcessor                  │   │   │
│  │  │  - send() response                           │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      UDP Broadcaster (Port 5001)                    │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Broadcast Thread (5Hz timer)                │   │   │
│  │  │  - Collect status from subsystems            │   │   │
│  │  │  - Build JSON status message                 │   │   │
│  │  │  - sendto() broadcast to 10.0.1.255          │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     Heartbeat Manager (Port 5002)                   │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Send Thread (1Hz timer)                     │   │   │
│  │  │  - Build heartbeat JSON                      │   │   │
│  │  │  - sendto() to ground station                │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Receive Thread                              │   │   │
│  │  │  - recvfrom() ground station heartbeat       │   │   │
│  │  │  - Update last_received timestamp            │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Timeout Monitor (periodic check)            │   │   │
│  │  │  - Check last_received vs current time       │   │   │
│  │  │  - Set disconnected if timeout exceeded      │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 TcpServer Class

**Files**:
- `src/network/tcp_server.cpp`
- `include/network/tcp_server.hpp`

**Purpose**: Accept and handle TCP command connections from H16 ground station

**Class Definition**:
```cpp
// Include ACTUAL class definition from code
class TcpServer {
public:
    TcpServer(uint16_t port);
    ~TcpServer();
    
    // Lifecycle
    bool start();
    void stop();
    bool is_running() const;
    
    // Set command handler callback
    void set_command_handler(
        std::function<std::string(const std::string&)> handler
    );
    
private:
    // Socket resources
    int server_fd_;
    uint16_t port_;
    sockaddr_in server_addr_;
    
    // Threading
    std::thread accept_thread_;
    std::atomic<bool> running_;
    
    // Connection handlers
    std::vector<std::thread> handler_threads_;
    std::mutex handlers_mutex_;
    
    // Command callback
    std::function<std::string(const std::string&)> command_handler_;
    
    // Private methods
    void accept_loop();
    void handle_connection(int client_fd, sockaddr_in client_addr);
    std::string receive_message(int fd);
    void send_response(int fd, const std::string& response);
};
```

**Socket Initialization**:
```cpp
// Document actual socket setup
bool TcpServer::start() {
    // 1. Create socket
    server_fd_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd_ < 0) {
        Logger::instance().log(LogLevel::ERROR, "Failed to create socket");
        return false;
    }
    
    // 2. Set socket options
    int opt = 1;
    setsockopt(server_fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // 3. Bind to port
    server_addr_.sin_family = AF_INET;
    server_addr_.sin_addr.s_addr = INADDR_ANY;  // 0.0.0.0
    server_addr_.sin_port = htons(port_);
    
    if (bind(server_fd_, (struct sockaddr*)&server_addr_, sizeof(server_addr_)) < 0) {
        Logger::instance().log(LogLevel::ERROR, "Failed to bind to port");
        close(server_fd_);
        return false;
    }
    
    // 4. Listen (backlog = 10)
    if (listen(server_fd_, 10) < 0) {
        Logger::instance().log(LogLevel::ERROR, "Failed to listen");
        close(server_fd_);
        return false;
    }
    
    // 5. Start accept thread
    running_ = true;
    accept_thread_ = std::thread(&TcpServer::accept_loop, this);
    
    Logger::instance().log(LogLevel::INFO, 
        "TCP server listening on port " + std::to_string(port_));
    
    return true;
}
```

**Accept Loop**:
```cpp
// Document actual accept loop
void TcpServer::accept_loop() {
    while (running_) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        
        // Set timeout for accept() to allow periodic running_ check
        struct timeval tv;
        tv.tv_sec = 1;  // 1 second timeout
        tv.tv_usec = 0;
        setsockopt(server_fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        
        // Accept connection (blocking with timeout)
        int client_fd = accept(server_fd_, 
                               (struct sockaddr*)&client_addr, 
                               &client_len);
        
        if (client_fd < 0) {
            if (errno == EWOULDBLOCK || errno == EAGAIN) {
                // Timeout, check running_ and continue
                continue;
            } else {
                // Real error
                Logger::instance().log(LogLevel::ERROR, "accept() failed");
                continue;
            }
        }
        
        // Log connection
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, INET_ADDRSTRLEN);
        Logger::instance().log(LogLevel::INFO, 
            "Accepted connection from " + std::string(client_ip));
        
        // Spawn handler thread
        std::thread handler(&TcpServer::handle_connection, this, client_fd, client_addr);
        
        // Store thread for later joining
        {
            std::lock_guard<std::mutex> lock(handlers_mutex_);
            handler_threads_.push_back(std::move(handler));
        }
    }
}
```

**Message Protocol**:

**Format**: Length-prefixed JSON
- **Length**: 4 bytes, uint32_t, network byte order (big-endian)
- **Payload**: UTF-8 JSON string

**Receiving**:
```cpp
std::string TcpServer::receive_message(int fd) {
    // 1. Receive length (4 bytes)
    uint32_t length_network;
    ssize_t bytes = recv(fd, &length_network, 4, MSG_WAITALL);
    if (bytes != 4) {
        throw std::runtime_error("Failed to receive length");
    }
    
    // 2. Convert network to host byte order
    uint32_t length = ntohl(length_network);
    
    // 3. Validate length (max 1MB)
    if (length > 1024 * 1024) {
        throw std::runtime_error("Message too large");
    }
    
    // 4. Receive payload
    std::vector<char> buffer(length);
    bytes = recv(fd, buffer.data(), length, MSG_WAITALL);
    if (bytes != static_cast<ssize_t>(length)) {
        throw std::runtime_error("Failed to receive payload");
    }
    
    // 5. Convert to string
    return std::string(buffer.begin(), buffer.end());
}
```

**Sending**:
```cpp
void TcpServer::send_response(int fd, const std::string& response) {
    // 1. Get length
    uint32_t length = response.size();
    
    // 2. Convert to network byte order
    uint32_t length_network = htonl(length);
    
    // 3. Send length
    send(fd, &length_network, 4, 0);
    
    // 4. Send payload
    send(fd, response.data(), length, 0);
}
```

**Connection Handler**:
```cpp
void TcpServer::handle_connection(int client_fd, sockaddr_in client_addr) {
    // Set socket timeout (5 seconds)
    struct timeval tv;
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(client_fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
    
    try {
        while (running_) {
            // 1. Receive command
            std::string command_json = receive_message(client_fd);
            
            // 2. Process command (via callback)
            std::string response_json;
            if (command_handler_) {
                response_json = command_handler_(command_json);
            } else {
                response_json = R"({"status":"error","message":"No handler"})";
            }
            
            // 3. Send response
            send_response(client_fd, response_json);
        }
    } catch (const std::exception& e) {
        Logger::instance().log(LogLevel::WARN, 
            "Connection handler exception: " + std::string(e.what()));
    }
    
    // Close connection
    close(client_fd);
    
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, INET_ADDRSTRLEN);
    Logger::instance().log(LogLevel::INFO, 
        "Closed connection from " + std::string(client_ip));
}
```

**Error Handling**:
- Connection timeout: 30 seconds (no activity)
- Receive timeout: 5 seconds per operation
- Socket errors: Log and close connection
- Malformed messages: Send error response, continue
- JSON parse errors: Send error response, continue

**Thread Safety**:
- `handler_threads_` vector protected by `handlers_mutex_`
- Callback `command_handler_` set once at initialization (no mutex needed)
- Each connection has its own thread and socket fd (no sharing)

---

### 5.3 UdpBroadcaster Class

**Files**:
- `src/network/udp_broadcaster.cpp`
- `include/network/udp_broadcaster.hpp`

**Purpose**: Broadcast status messages to H16 ground station at 5Hz

**Class Definition**:
```cpp
// Include actual class from code
class UdpBroadcaster {
public:
    UdpBroadcaster(uint16_t port, const std::string& target_ip);
    ~UdpBroadcaster();
    
    // Lifecycle
    bool start();
    void stop();
    bool is_running() const;
    
    // Set status provider callback
    void set_status_provider(
        std::function<std::string()> provider
    );
    
private:
    // Socket
    int socket_fd_;
    uint16_t port_;
    std::string target_ip_;
    sockaddr_in target_addr_;
    
    // Threading
    std::thread broadcast_thread_;
    std::atomic<bool> running_;
    
    // Status callback
    std::function<std::string()> status_provider_;
    
    // Private methods
    void broadcast_loop();
    void send_status(const std::string& status_json);
};
```

**Broadcast Frequency**: 5 Hz (200 milliseconds between broadcasts)

**Implementation**:
```cpp
// Document actual broadcast loop
void UdpBroadcaster::broadcast_loop() {
    using namespace std::chrono;
    auto next_broadcast = steady_clock::now();
    const auto interval = milliseconds(200);  // 5 Hz
    
    while (running_) {
        // 1. Get status from provider callback
        std::string status_json;
        if (status_provider_) {
            status_json = status_provider_();
        } else {
            status_json = R"({"status":"no_provider"})";
        }
        
        // 2. Send UDP packet
        send_status(status_json);
        
        // 3. Sleep until next broadcast (200ms)
        next_broadcast += interval;
        std::this_thread::sleep_until(next_broadcast);
    }
}

void UdpBroadcaster::send_status(const std::string& status_json) {
    ssize_t sent = sendto(socket_fd_, 
                          status_json.c_str(), 
                          status_json.size(), 
                          0,
                          (struct sockaddr*)&target_addr_, 
                          sizeof(target_addr_));
    
    if (sent < 0) {
        Logger::instance().log(LogLevel::WARN, "Failed to send UDP status");
    }
}
```

**Socket Setup**:
```cpp
bool UdpBroadcaster::start() {
    // 1. Create UDP socket
    socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (socket_fd_ < 0) {
        Logger::instance().log(LogLevel::ERROR, "Failed to create UDP socket");
        return false;
    }
    
    // 2. Enable broadcast (if broadcasting to 10.0.1.255)
    int broadcast = 1;
    setsockopt(socket_fd_, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast));
    
    // 3. Setup target address
    target_addr_.sin_family = AF_INET;
    target_addr_.sin_port = htons(port_);
    inet_pton(AF_INET, target_ip_.c_str(), &target_addr_.sin_addr);
    
    // 4. Start broadcast thread
    running_ = true;
    broadcast_thread_ = std::thread(&UdpBroadcaster::broadcast_loop, this);
    
    Logger::instance().log(LogLevel::INFO, 
        "UDP broadcaster started on port " + std::to_string(port_));
    
    return true;
}
```

---

### 5.4 HeartbeatManager Class

**Files**:
- `src/network/heartbeat_manager.cpp`
- `include/network/heartbeat_manager.hpp`

**Purpose**: Monitor connection health via bidirectional heartbeat exchange

[Document HeartbeatManager implementation following same pattern as above]

**Heartbeat Frequency**: 1 Hz (1 second interval)

**Timeout Detection**: Disconnect if no heartbeat received for [X] seconds

[Include actual implementation details]

---

### 5.5 Network Error Handling

**Socket Errors**:
- `ECONNREFUSED`: Log and retry
- `ETIMEDOUT`: Log and close connection
- `EPIPE`: Broken pipe, close connection
- [Document actual error handling]

**Recovery Strategies**:
[Document reconnection logic, retry policies, etc.]

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Use ACTUAL code from the codebase (not pseudo-code)
✅ Include complete class definitions with all members
✅ Include actual implementation snippets
✅ Document threading model clearly
✅ Include ASCII architecture diagrams
✅ Be comprehensive and detailed
✅ Keep output under 20,000 tokens

At the end of Section 5, add status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-5: Executive Summary, Project Structure, Architecture Overview, Core Components, Network Layer | ✅ **COMPLETE** |
| **Phase 2** | 6-10: Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model | ⏳ Pending |
| **Phase 3** | 11-15: Memory Management, Error Handling, Configuration System, Dependencies, Build System | ⏳ Pending |
| **Phase 4** | 16-21: Testing, Code Conventions, Deployment, Performance, Known Issues, Future Roadmap | ⏳ Pending |

**Next Action**: Run Phase 2 to continue documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Air-Side (SBC) architecture documentation - Phase 1 (Sections 1-5)"
```

---

## 🚀 Phase 2: Hardware Integration (Sections 6-10)

### Task for Claude Code

```
Task: Continue SBC_ARCHITECTURE.md - Phase 2 of 4

IMPORTANT: APPEND to existing file: sbc/docs/SBC_ARCHITECTURE.md
(Read file first to maintain consistency, then append)

Generate SECTIONS 6-10:

═══════════════════════════════════════════════════════════════════

## 6. Camera Integration

### 6.1 Sony Camera Remote SDK Integration

**SDK Version**: Sony Camera Remote SDK v2.00.00

**SDK Location**: `external/sony_sdk/`

**Libraries**:
- `libCrAdapter.so` - Core adapter library
- `libCrImageDataBlock.so` - Image data handling
- [List all Sony SDK libraries used]

**Include Files**:
- `CrDeviceProperty.h` - Camera properties and controls
- `ICrCameraObjectInfo.h` - Camera object interface
- [List all Sony SDK headers used]

**Documentation**:
- API Reference: `Sony_CameraRemoteSDK_API-Reference_v2.00.00.pdf`
- Sample Code: `RemoteSampleApp_IM_v2_00_00.pdf`

---

### 6.2 SonyCamera Class (Low-Level Wrapper)

**Files**:
- `src/camera/sony_camera.cpp`
- `include/camera/sony_camera.hpp`

**Purpose**: Low-level C++ wrapper around Sony Camera Remote SDK

**Class Definition**:
```cpp
// Include ACTUAL class from code
class SonyCamera {
public:
    SonyCamera();
    ~SonyCamera();
    
    // Lifecycle
    bool initialize();
    bool connect(const std::string& camera_id = "");
    bool disconnect();
    bool is_connected() const;
    
    // Camera control
    bool set_shutter_speed(const std::string& value);
    bool set_aperture(const std::string& value);
    bool set_iso(int value);
    bool set_white_balance(WhiteBalanceMode mode, int temperature = 0);
    bool set_focus_mode(FocusMode mode);
    bool set_focus_position(int position);
    
    // Capture
    bool capture_image();
    bool start_video_recording();
    bool stop_video_recording();
    
    // Live view (if implemented)
    bool start_live_view(LiveViewCallback callback);
    bool stop_live_view();
    
    // Status
    CameraStatus get_status() const;
    
private:
    // Sony SDK objects
    SCRSDK::ICrEnumCameraObjectInfo* camera_list_;
    SCRSDK::CrDeviceHandle device_handle_;
    
    // State
    bool connected_;
    mutable std::mutex state_mutex_;
    CameraStatus status_;
    
    // Callbacks
    LiveViewCallback live_view_callback_;
    
    // Sony SDK callbacks (static)
    static void property_callback(
        SCRSDK::CrDeviceProperty* properties,
        CrInt32u num_properties,
        void* user_data
    );
    
    static void liveview_callback(
        SCRSDK::CrLiveViewProperty prop,
        const CrU8* data,
        CrInt32u size,
        void* user_data
    );
    
    // Helper methods
    bool enumerate_cameras();
    bool set_property(CrInt32u property_key, CrInt64u value);
    CrInt64u get_property(CrInt32u property_key) const;
};
```

**Sony SDK Initialization**:
```cpp
// Document actual Sony SDK initialization
bool SonyCamera::initialize() {
    // 1. Initialize SDK
    CrError result = SCRSDK::Init();
    if (result != CrError_None) {
        Logger::instance().log(LogLevel::ERROR, 
            "Failed to initialize Sony SDK");
        return false;
    }
    
    // 2. Enumerate cameras
    if (!enumerate_cameras()) {
        Logger::instance().log(LogLevel::ERROR, 
            "No Sony cameras found");
        return false;
    }
    
    Logger::instance().log(LogLevel::INFO, 
        "Sony SDK initialized successfully");
    
    return true;
}

bool SonyCamera::enumerate_cameras() {
    // Get camera list
    SCRSDK::EnumCameraObjectInfo(&camera_list_);
    
    if (!camera_list_ || camera_list_->GetCount() == 0) {
        return false;
    }
    
    // Log found cameras
    CrInt32u count = camera_list_->GetCount();
    Logger::instance().log(LogLevel::INFO, 
        "Found " + std::to_string(count) + " Sony camera(s)");
    
    return true;
}
```

**Camera Connection**:
```cpp
bool SonyCamera::connect(const std::string& camera_id) {
    if (!camera_list_ || camera_list_->GetCount() == 0) {
        return false;
    }
    
    // Get first camera (or find by ID)
    auto camera_info = camera_list_->GetCameraObjectInfo(0);
    
    // Create connection info
    SCRSDK::CrSdkConnectionInfo conn_info;
    // ... fill connection info from camera_info
    
    // Connect to camera
    CrError result = SCRSDK::Connect(&conn_info, this, &device_handle_);
    if (result != CrError_None) {
        Logger::instance().log(LogLevel::ERROR, 
            "Failed to connect to camera");
        return false;
    }
    
    // Register callbacks
    SCRSDK::SetDevicePropertyCallback(device_handle_, 
                                      property_callback, 
                                      this);
    
    connected_ = true;
    Logger::instance().log(LogLevel::INFO, "Camera connected");
    
    return true;
}
```

**Property Control Examples**:
```cpp
// Document actual property control implementation
bool SonyCamera::set_shutter_speed(const std::string& value) {
    // Convert string (e.g., "1/125") to Sony SDK value
    CrInt64u sdk_value = convert_shutter_to_sdk_value(value);
    
    // Set property via Sony SDK
    return set_property(SCRSDK::CrDevicePropertyCode::CrDeviceProperty_ShutterSpeed, 
                       sdk_value);
}

bool SonyCamera::set_property(CrInt32u property_key, CrInt64u value) {
    if (!connected_) {
        return false;
    }
    
    // Create property list
    SCRSDK::CrDeviceProperty prop;
    prop.SetCode(property_key);
    prop.SetCurrentValue(value);
    prop.SetValueType(SCRSDK::CrDataType_UInt64);
    
    // Send to camera
    CrError result = SCRSDK::SetDeviceProperty(device_handle_, &prop);
    
    if (result != CrError_None) {
        Logger::instance().log(LogLevel::ERROR, 
            "Failed to set camera property");
        return false;
    }
    
    return true;
}
```

**Callback Handling**:
```cpp
// Static callback wrapper
void SonyCamera::property_callback(
    SCRSDK::CrDeviceProperty* properties,
    CrInt32u num_properties,
    void* user_data
) {
    // Cast user_data back to SonyCamera instance
    SonyCamera* instance = static_cast<SonyCamera*>(user_data);
    
    // Process properties
    for (CrInt32u i = 0; i < num_properties; ++i) {
        CrInt32u code = properties[i].GetCode();
        CrInt64u value = properties[i].GetCurrentValue();
        
        // Update internal state based on property code
        std::lock_guard<std::mutex> lock(instance->state_mutex_);
        switch (code) {
            case SCRSDK::CrDeviceProperty_ShutterSpeed:
                instance->status_.shutter_speed = 
                    convert_sdk_to_shutter_string(value);
                break;
            case SCRSDK::CrDeviceProperty_FNumber:
                instance->status_.aperture = 
                    convert_sdk_to_aperture_string(value);
                break;
            // ... handle all properties
        }
    }
}
```

**Resource Management** (RAII):
```cpp
SonyCamera::~SonyCamera() {
    if (connected_) {
        disconnect();
    }
    
    // Release camera list
    if (camera_list_) {
        camera_list_->Release();
        camera_list_ = nullptr;
    }
    
    // Release SDK
    SCRSDK::Release();
}
```

**Error Handling**:
[Document error handling strategies for Sony SDK errors]

---

### 6.3 CameraController Class (High-Level Interface)

**Files**:
- `src/camera/camera_controller.cpp`
- `include/camera/camera_controller.hpp`

**Purpose**: High-level camera control interface, command queue, state management

[Document CameraController following similar pattern]

---

### 6.4 Live View Integration (if implemented)

[Document Sony SDK live view callbacks and frame handling]

---

### 6.5 Content Management

[Document content download, storage management]

═══════════════════════════════════════════════════════════════════

## 7. Gimbal Integration

### 7.1 Gimbal Interface (Abstract Base Class)

**Files**:
- `include/gimbal/gimbal_interface.hpp`

**Purpose**: Abstract interface for multiple gimbal implementations

**Class Definition**:
```cpp
// Include actual interface
class GimbalInterface {
public:
    virtual ~GimbalInterface() = default;
    
    // Lifecycle
    virtual bool initialize(const std::string& device_path) = 0;
    virtual bool connect() = 0;
    virtual bool disconnect() = 0;
    virtual bool is_connected() const = 0;
    
    // Control
    virtual bool set_angle(float pitch, float yaw, float roll) = 0;
    virtual bool set_mode(GimbalMode mode) = 0;
    virtual bool go_home() = 0;
    virtual bool calibrate() = 0;  // Phase 2 feature
    
    // Status
    virtual GimbalStatus get_status() const = 0;
    virtual GimbalAngles get_angles() const = 0;
};
```

---

### 7.2 Gremsy Gimbal Implementation

**Files**:
- `src/gimbal/gremsy_gimbal.cpp`
- `include/gimbal/gremsy_gimbal.hpp`

**Purpose**: Gremsy gSDK integration

**Gremsy gSDK**:
- Repository: https://github.com/Gremsy/gSDK
- Location: `external/gremsy_sdk/`
- Communication: Serial (UART)

[Document Gremsy implementation in detail]

---

### 7.3 SimpleBGC Gimbal Implementation

**Files**:
- `src/gimbal/simplebgc_gimbal.cpp`
- `include/gimbal/simplebgc_gimbal.hpp`

**Purpose**: SimpleBGC Serial API integration

**SimpleBGC Serial API**:
- Repository: https://github.com/basecamelectronics/sbgc32-serial-api
- Location: `external/simplebgc_api/`
- Communication: Serial (UART)

[Document SimpleBGC implementation in detail]

═══════════════════════════════════════════════════════════════════

## 8. Video Streaming

[If RTSP streaming is implemented, document it in detail]
[If not yet implemented, note: "Planned for future phase"]

### 8.1 RTSP Server Architecture (if implemented)

[Document GStreamer or FFmpeg-based RTSP server]

### 8.2 Video Encoding (if implemented)

[Document H.264 encoding setup]

### 8.3 Sony SDK Live View Integration (if implemented)

[Document how Sony SDK frames feed into RTSP stream]

═══════════════════════════════════════════════════════════════════

## 9. Protocol Implementation

### 9.1 Message Format

**Protocol Version**: 1.0

**Transport**:
- TCP (Port 5000): Commands (Ground → Air)
- UDP (Port 5001): Status (Air → Ground, 5Hz)
- UDP (Port 5002): Heartbeat (Bidirectional, 1Hz)

**Encoding**: JSON (UTF-8)

**Message Structure**:
```json
{
    "protocol_version": "1.0",
    "message_type": "command|status|response|heartbeat",
    "sequence_id": 12345,
    "timestamp": 1729339200,
    "payload": {
        // Message-specific content
    }
}
```

### 9.2 Command Messages (Ground → Air)

**Format**:
```json
{
    "protocol_version": "1.0",
    "message_type": "command",
    "sequence_id": 42,
    "timestamp": 1729339200,
    "payload": {
        "command": "camera.set_property",
        "parameters": {
            "property": "shutter_speed",
            "value": "1/125"
        }
    }
}
```

**Supported Commands** (document all actual commands):
- `camera.set_property` - Set camera parameter
- `camera.capture` - Capture image
- `camera.record_start` - Start video recording
- `camera.record_stop` - Stop video recording
- `gimbal.set_angle` - Set gimbal position
- `gimbal.set_mode` - Set gimbal mode
- [List ALL supported commands]

### 9.3 Response Messages (Air → Ground)

**Format**:
```json
{
    "protocol_version": "1.0",
    "message_type": "response",
    "sequence_id": 42,  // Matches command sequence_id
    "timestamp": 1729339201,
    "payload": {
        "status": "success|error",
        "message": "Operation completed",
        "data": {
            // Optional response data
        }
    }
}
```

### 9.4 Status Messages (Air → Ground, 5Hz)

**Format**:
```json
{
    "protocol_version": "1.0",
    "message_type": "status",
    "sequence_id": 1000,
    "timestamp": 1729339200,
    "payload": {
        "system": {
            "cpu_usage": 45.2,
            "memory_usage": 512,
            "temperature": 58.3,
            "uptime": 3600
        },
        "network": {
            "connection_state": "connected",
            "signal_strength": -65
        },
        "camera": {
            "connected": true,
            "shutter_speed": "1/125",
            "aperture": "f/4.0",
            "iso": 800,
            "recording": false
        },
        "gimbal": {
            "connected": true,
            "mode": "follow",
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0
        }
    }
}
```

### 9.5 Heartbeat Messages (Bidirectional, 1Hz)

**Format**:
```json
{
    "protocol_version": "1.0",
    "message_type": "heartbeat",
    "sequence_id": 5000,
    "timestamp": 1729339200,
    "payload": {
        "sender": "air_side|ground_station",
        "status": "alive"
    }
}
```

### 9.6 MessageHandler Class

**Files**:
- `src/protocol/message_handler.cpp`
- `include/protocol/message_handler.hpp`

**Purpose**: JSON message parsing and validation

[Document MessageHandler implementation]

### 9.7 CommandProcessor Class

**Files**:
- `src/protocol/command_processor.cpp`
- `include/protocol/command_processor.hpp`

**Purpose**: Command dispatching and execution

[Document CommandProcessor implementation]

### 9.8 StatusBuilder Class

**Files**:
- `src/protocol/status_builder.cpp`
- `include/protocol/status_builder.hpp`

**Purpose**: Build status JSON messages

[Document StatusBuilder implementation]

═══════════════════════════════════════════════════════════════════

## 10. Threading Model

### 10.1 Thread Architecture

```
Main Thread (PayloadManager)
│   - Service initialization
│   - Signal handling
│   - Main event loop (health checks)
│   - Shutdown coordination
│
├─► Network Threads
│   │
│   ├─► TCP Accept Thread
│   │   └─► TCP Connection Handler Threads (pool, one per connection)
│   │
│   ├─► UDP Broadcaster Thread (5Hz)
│   │
│   └─► Heartbeat Threads
│       ├─► Send Thread (1Hz)
│       └─► Receive Thread
│
├─► Command Processor Thread (if separate)
│   └─► Executes camera/gimbal commands
│
└─► Camera/Gimbal Callback Threads (SDK-managed)
    ├─► Sony SDK property callbacks
    └─► Sony SDK live view callbacks (if active)
```

**Total Thread Count** (typical): [Document actual count, e.g., "5-10 threads"]

### 10.2 Thread Management

**Thread Creation**:
```cpp
// Example thread creation pattern
std::thread tcp_thread_;

void start_tcp_server() {
    tcp_thread_ = std::thread(&PayloadManager::tcp_server_loop, this);
}
```

**Thread Joining**:
```cpp
void shutdown() {
    running_ = false;  // Signal threads to stop
    
    if (tcp_thread_.joinable()) {
        tcp_thread_.join();
    }
    // ... join all threads
}
```

### 10.3 Synchronization Primitives

**Mutexes**:
```cpp
// Examples of mutex usage
std::mutex state_mutex_;  // Protect shared state
std::mutex queue_mutex_;  // Protect command queue

// Usage with lock_guard (automatic unlock)
{
    std::lock_guard<std::mutex> lock(state_mutex_);
    // Access shared state
}

// Usage with unique_lock (manual unlock, condition variables)
{
    std::unique_lock<std::mutex> lock(queue_mutex_);
    // Wait on condition variable, etc.
}
```

**Atomic Variables**:
```cpp
// For simple flags and counters
std::atomic<bool> running_{false};
std::atomic<int> sequence_id_{0};

// Usage (thread-safe without mutex)
running_ = true;
int seq = sequence_id_.fetch_add(1);
```

**Condition Variables** (if used):
```cpp
std::condition_variable command_available_;
std::mutex queue_mutex_;
std::queue<Command> command_queue_;

// Producer thread
{
    std::lock_guard<std::mutex> lock(queue_mutex_);
    command_queue_.push(cmd);
    command_available_.notify_one();
}

// Consumer thread
{
    std::unique_lock<std::mutex> lock(queue_mutex_);
    command_available_.wait(lock, [this] { 
        return !command_queue_.empty(); 
    });
    Command cmd = command_queue_.front();
    command_queue_.pop();
}
```

### 10.4 Thread Safety Guidelines

**Rules**:
1. Shared state must be protected by mutex
2. Use RAII lock guards (`std::lock_guard`, `std::unique_lock`)
3. Prefer atomics for simple flags/counters
4. Avoid long mutex holds (especially in network threads)
5. Document thread ownership of resources

**Thread-Safe Classes**:
[List classes that are thread-safe and explain why]

**Non-Thread-Safe Classes**:
[List classes that require external synchronization]

### 10.5 Deadlock Prevention

**Strategies**:
1. Lock ordering: Always acquire mutexes in same order
2. Use `std::lock()` for multiple mutexes
3. Avoid nested locking when possible
4. Timeout on locks if blocking is risky

**Lock Hierarchy** (if defined):
[Document lock ordering to prevent deadlocks]

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read existing document for consistency
✅ Append sections (don't overwrite)
✅ Use ACTUAL code from codebase
✅ Document Sony SDK integration thoroughly
✅ Document gimbal implementations
✅ Document complete protocol
✅ Document threading model clearly
✅ Include code examples
✅ Keep under 20,000 tokens

Update status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-5: Executive Summary, Project Structure, Architecture Overview, Core Components, Network Layer | ✅ Complete |
| **Phase 2** | 6-10: Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model | ✅ **COMPLETE** |
| **Phase 3** | 11-15: Memory Management, Error Handling, Configuration System, Dependencies, Build System | ⏳ Pending |
| **Phase 4** | 16-21: Testing, Code Conventions, Deployment, Performance, Known Issues, Future Roadmap | ⏳ Pending |

**Next Action**: Run Phase 3 to continue documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Air-Side (SBC) architecture documentation - Phase 2 (Sections 6-10)"
```

---

## 🚀 Phase 3: System Infrastructure (Sections 11-15)

### Task for Claude Code

```
Task: Continue SBC_ARCHITECTURE.md - Phase 3 of 4

IMPORTANT: APPEND to existing file: sbc/docs/SBC_ARCHITECTURE.md
(Read entire document for context, then append)

Generate SECTIONS 11-15:

═══════════════════════════════════════════════════════════════════

## 11. Memory Management

### 11.1 C++17 Memory Management Principles

**Philosophy**: RAII + Smart Pointers + Modern C++ Idioms

**Key Principles**:
1. **No manual new/delete** - Use smart pointers
2. **RAII for resources** - Constructor acquires, destructor releases
3. **Clear ownership** - unique_ptr, shared_ptr, weak_ptr
4. **Move semantics** - Avoid unnecessary copies
5. **Stack allocation preferred** - Heap only when necessary

### 11.2 Smart Pointer Usage

#### unique_ptr (Exclusive Ownership)

**Usage**: Single owner, movable but not copyable

**Examples from Project**:
```cpp
// Subsystem ownership
std::unique_ptr<TcpServer> tcp_server_;
std::unique_ptr<CameraController> camera_controller_;
std::unique_ptr<GimbalInterface> gimbal_;

// Creation
tcp_server_ = std::make_unique<TcpServer>(5000);

// Transfer ownership (move)
auto gimbal = std::make_unique<GremsyGimbal>();
gimbal_ = std::move(gimbal);  // Ownership transferred

// Automatic cleanup (destructor releases)
```

**When to use**:
- Subsystem ownership in main class
- Factory return values
- Resource handles (files, sockets via wrapper classes)

---

#### shared_ptr (Shared Ownership)

**Usage**: Multiple owners, reference counted

**Examples from Project**:
```cpp
// Shared dependency injection
std::shared_ptr<CameraController> camera_;
std::shared_ptr<GimbalInterface> gimbal_;

// Multiple objects share ownership
CommandProcessor cmd_processor(camera_, gimbal_);
StatusBuilder status_builder(camera_, gimbal_);
// Both objects hold shared_ptr, camera stays alive as long as one owner exists

// Creation
auto camera = std::make_shared<CameraController>();

// Automatic cleanup when last owner destroyed
```

**When to use**:
- Dependency injection (multiple users)
- Callback contexts (if lifetime uncertain)
- Shared caches or resources

**Caution**: Avoid circular references (use weak_ptr)

---

#### weak_ptr (Non-Owning Observer)

**Usage**: Observes shared_ptr without ownership

**Examples**:
```cpp
// Observer pattern to avoid circular references
class CameraObserver {
    std::weak_ptr<CameraController> camera_;
    
    void check_camera() {
        // Convert weak_ptr to shared_ptr (check if still alive)
        if (auto camera = camera_.lock()) {
            // Use camera safely
            camera->get_status();
        } else {
            // Camera has been destroyed
        }
    }
};
```

**When to use**:
- Break circular references
- Observer patterns
- Caches where you don't want to keep object alive

### 11.3 RAII Pattern Examples

**Socket Wrapper**:
```cpp
class Socket {
private:
    int fd_;
    
public:
    Socket() : fd_(-1) {}
    
    explicit Socket(int domain, int type, int protocol) {
        fd_ = socket(domain, type, protocol);
        if (fd_ < 0) {
            throw std::runtime_error("Failed to create socket");
        }
    }
    
    ~Socket() {
        if (fd_ >= 0) {
            close(fd_);
        }
    }
    
    // Delete copy
    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;
    
    // Allow move
    Socket(Socket&& other) noexcept 
        : fd_(std::exchange(other.fd_, -1)) {}
    
    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) close(fd_);
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }
    
    int get() const { return fd_; }
};
```

**File Wrapper**:
```cpp
class File {
private:
    FILE* fp_;
    
public:
    explicit File(const char* path, const char* mode) {
        fp_ = fopen(path, mode);
        if (!fp_) {
            throw std::runtime_error("Failed to open file");
        }
    }
    
    ~File() {
        if (fp_) fclose(fp_);
    }
    
    // Delete copy, allow move (similar to Socket)
    
    FILE* get() const { return fp_; }
};
```

### 11.4 Move Semantics

**Purpose**: Avoid unnecessary copies, transfer resources efficiently

**Example**:
```cpp
// Function returning large object (efficient with move)
std::vector<uint8_t> read_large_file(const std::string& path) {
    std::vector<uint8_t> buffer;
    // ... read file into buffer
    return buffer;  // Move, not copy (RVO or move constructor)
}

// Caller
auto data = read_large_file("image.jpg");  // No copy made
```

### 11.5 Memory Leak Prevention

**Strategies**:
1. Use smart pointers (automatic cleanup)
2. Use RAII wrappers for all resources
3. Regular valgrind testing
4. Code reviews focused on resource management

**Valgrind Testing**:
```bash
# Run service under valgrind
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         ./payload_manager

# No leaks if output shows:
# "All heap blocks were freed -- no leaks are possible"
```

**Memory Leak Checklist**:
- [ ] All new/delete replaced with smart pointers
- [ ] All malloc/free replaced with RAII or smart pointers
- [ ] All file handles wrapped in RAII
- [ ] All socket fds wrapped in RAII
- [ ] All SDK objects properly released
- [ ] Valgrind test passed (no leaks)

### 11.6 Performance Considerations

**Stack vs Heap**:
- Prefer stack allocation (faster, automatic cleanup)
- Use heap only for: large objects, dynamic lifetime, polymorphism

**Avoiding Allocations**:
- Pre-allocate buffers
- Object pools for frequently created/destroyed objects
- Move instead of copy

═══════════════════════════════════════════════════════════════════

## 12. Error Handling

### 12.1 Error Handling Strategy

**Philosophy**: Fail fast, log thoroughly, recover gracefully

**Approaches**:
1. **Exceptions**: For initialization/configuration errors
2. **Return codes**: For operational errors (network, hardware)
3. **Logging**: All errors logged with context
4. **Recovery**: Retry, fallback, or graceful degradation

### 12.2 Exception Usage

**When to use exceptions**:
- Initialization failures (constructor, initialize())
- Configuration parsing errors
- Unrecoverable resource failures

**Exception Types**:
```cpp
// Standard exceptions
throw std::runtime_error("Failed to initialize camera");
throw std::invalid_argument("Invalid configuration value");
throw std::system_error(errno, std::system_category(), "socket() failed");

// Custom exceptions (if defined)
class CameraException : public std::runtime_error {
    // ...
};
```

**Exception Safety**:
- Constructors: Exception-safe (RAII)
- Destructors: No exceptions (marked noexcept)
- Functions: Document which exceptions can be thrown

### 12.3 Return Code Pattern

**When to use return codes**:
- Network operations (expected failures)
- Camera/gimbal commands (may fail normally)
- File operations

**Pattern**:
```cpp
bool send_command(const Command& cmd) {
    if (!connected_) {
        Logger::instance().log(LogLevel::ERROR, "Not connected");
        return false;
    }
    
    if (!validate_command(cmd)) {
        Logger::instance().log(LogLevel::ERROR, "Invalid command");
        return false;
    }
    
    // Attempt operation
    if (/* operation fails */) {
        Logger::instance().log(LogLevel::ERROR, "Command failed");
        return false;
    }
    
    return true;
}
```

### 12.4 Error Logging

**Logger Class**:
[Document Logger implementation]

**Log Levels**:
- DEBUG: Verbose diagnostic information
- INFO: Normal operational messages
- WARN: Unexpected but recoverable conditions
- ERROR: Error conditions that don't crash service

**Log Format**:
```
[2025-10-25 10:30:45.123] [INFO] [TcpServer] Connection accepted from 10.0.1.11
[2025-10-25 10:30:46.456] [ERROR] [SonyCamera] Failed to set shutter speed: SDK error 0x8001
```

### 12.5 Recovery Strategies

**Network Errors**:
- TCP disconnect: Close socket, wait for reconnect
- UDP send fail: Log warning, continue (best-effort)
- Heartbeat timeout: Mark disconnected, continue operation

**Camera Errors**:
- SDK error: Log, return error to ground station
- Camera disconnect: Attempt reconnection every 5 seconds
- Command timeout: Return error after timeout

**Gimbal Errors**:
- Serial error: Attempt reconnection
- Invalid response: Retry command up to 3 times
- Timeout: Return error

═══════════════════════════════════════════════════════════════════

## 13. Configuration System

### 13.1 Configuration File Format

**File**: `/etc/dpm/payload_manager.conf` (default)

**Format**: INI-style or JSON

**Example** (if INI):
```ini
[network]
tcp_port = 5000
udp_status_port = 5001
udp_heartbeat_port = 5002
bind_address = 0.0.0.0
target_ip = 10.0.1.11

[camera]
auto_connect = true
default_shutter = 1/125
default_aperture = f/4.0
default_iso = 800

[gimbal]
type = gremsy
device = /dev/ttyUSB0
baudrate = 115200

[system]
log_level = INFO
log_file = /var/log/dpm/payload_manager.log

[storage]
base_path = /mnt/storage/dpm
max_size_mb = 10240
cleanup_enabled = true
```

**Example** (if JSON):
```json
{
    "network": {
        "tcp_port": 5000,
        "udp_status_port": 5001,
        "udp_heartbeat_port": 5002,
        "bind_address": "0.0.0.0",
        "target_ip": "10.0.1.11"
    },
    "camera": {
        "auto_connect": true,
        "defaults": {
            "shutter": "1/125",
            "aperture": "f/4.0",
            "iso": 800
        }
    },
    "gimbal": {
        "type": "gremsy",
        "device": "/dev/ttyUSB0",
        "baudrate": 115200
    },
    "system": {
        "log_level": "INFO",
        "log_file": "/var/log/dpm/payload_manager.log"
    }
}
```

### 13.2 ConfigParser Class

**Files**:
- `src/utils/config_parser.cpp`
- `include/utils/config_parser.hpp`

[Document ConfigParser implementation]

### 13.3 Configuration Validation

[Document validation logic for configuration values]

═══════════════════════════════════════════════════════════════════

## 14. Dependencies

### 14.1 System Dependencies

**Required Packages** (Ubuntu 22.04):
```bash
# Core build tools
sudo apt install -y \
    build-essential \
    cmake \
    git \
    pkg-config

# C++ libraries
sudo apt install -y \
    nlohmann-json3-dev \
    libssl-dev

# USB device access
sudo apt install -y \
    libudev-dev \
    libusb-1.0-0-dev

# Optional: Boost libraries
sudo apt install -y \
    libboost-all-dev

# Optional: GStreamer (for video streaming)
sudo apt install -y \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-rtsp
```

### 14.2 External Libraries

#### nlohmann-json
**Version**: 3.11.2+
**Purpose**: JSON parsing and generation
**License**: MIT
**Homepage**: https://github.com/nlohmann/json
**Usage**: Protocol message parsing/building

#### Sony Camera Remote SDK
**Version**: v2.00.00 (CrSDK_v2.00.00_20250805a_Linux64ARMv8)
**Purpose**: Sony camera control
**License**: Proprietary (http://www.sony.net/CameraRemoteSDK/)
**Location**: `external/sony_sdk/`
**Libraries**:
- libCrAdapter.so
- libCrImageDataBlock.so

#### Gremsy gSDK (if used)
**Version**: [Document version]
**Purpose**: Gremsy gimbal control
**License**: [Document license]
**Repository**: https://github.com/Gremsy/gSDK
**Location**: `external/gremsy_sdk/`

#### SimpleBGC Serial API (if used)
**Version**: [Document version]
**Purpose**: SimpleBGC gimbal control
**License**: [Document license]
**Repository**: https://github.com/basecamelectronics/sbgc32-serial-api
**Location**: `external/simplebgc_api/`

### 14.3 Dependency Table

| Library | Version | Purpose | License | Included |
|---------|---------|---------|---------|----------|
| nlohmann-json | 3.11.2+ | JSON parsing | MIT | System package |
| Sony Camera SDK | v2.00.00 | Camera control | Proprietary | External |
| Gremsy gSDK | [ver] | Gimbal control | [lic] | External |
| SimpleBGC API | [ver] | Gimbal control | [lic] | External |
| libusb | 1.0 | USB access | LGPL | System package |
| libudev | [ver] | Device detection | GPL | System package |
| [Others] | | | | |

═══════════════════════════════════════════════════════════════════

## 15. Build System

### 15.1 CMake Configuration

**Root CMakeLists.txt**:
```cmake
# Document ACTUAL CMakeLists.txt content
cmake_minimum_required(VERSION 3.16)
project(DPM_AirSide VERSION 1.0.0 LANGUAGES CXX)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Find packages
find_package(nlohmann_json 3.2.0 REQUIRED)
find_package(Threads REQUIRED)
# ... find all packages

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/external/sony_sdk/include
    # ... all include dirs
)

# Source files
set(SOURCES
    src/main.cpp
    src/payload_manager.cpp
    src/network/tcp_server.cpp
    src/network/udp_broadcaster.cpp
    # ... all source files
)

# Main executable
add_executable(payload_manager ${SOURCES})

# Link libraries
target_link_libraries(payload_manager
    PRIVATE
    nlohmann_json::nlohmann_json
    Threads::Threads
    ${CMAKE_SOURCE_DIR}/external/sony_sdk/lib/libCrAdapter.so
    ${CMAKE_SOURCE_DIR}/external/sony_sdk/lib/libCrImageDataBlock.so
    # ... all libraries
)

# Install rules
install(TARGETS payload_manager DESTINATION /usr/local/bin)
install(FILES config/payload_manager.conf DESTINATION /etc/dpm)
```

### 15.2 Build Instructions

**Standard Build**:
```bash
# From sbc/ directory
mkdir -p build
cd build
cmake ..
make -j$(nproc)

# Output: build/payload_manager
```

**Debug Build**:
```bash
mkdir -p build-debug
cd build-debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)
```

**Release Build**:
```bash
mkdir -p build-release
cd build-release
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

**Clean Build**:
```bash
rm -rf build
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 15.3 Build Targets

**Main Targets**:
- `payload_manager` - Main executable
- `install` - Install to system
- `clean` - Clean build artifacts

**Test Targets** (if defined):
- `tests` - Build test suite
- `test` - Run tests

### 15.4 Cross-Compilation (Optional)

**For Development PC → Raspberry Pi**:
```bash
# Install cross-compiler on Ubuntu PC
sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# Create toolchain file: toolchain-arm64.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)
set(CMAKE_FIND_ROOT_PATH /usr/aarch64-linux-gnu)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

# Build with toolchain
cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-arm64.cmake ..
make -j$(nproc)

# Copy to Raspberry Pi
scp payload_manager pi@10.0.1.20:/home/pi/
```

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read existing document for consistency
✅ Append sections (don't overwrite)
✅ Use ACTUAL code and configurations
✅ Document memory management thoroughly
✅ Document error handling strategies
✅ Document configuration system
✅ List ALL dependencies with details
✅ Document complete CMake setup
✅ Include actual build commands
✅ Keep under 20,000 tokens

Update status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-5: Executive Summary, Project Structure, Architecture Overview, Core Components, Network Layer | ✅ Complete |
| **Phase 2** | 6-10: Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model | ✅ Complete |
| **Phase 3** | 11-15: Memory Management, Error Handling, Configuration System, Dependencies, Build System | ✅ **COMPLETE** |
| **Phase 4** | 16-21: Testing, Code Conventions, Deployment, Performance, Known Issues, Future Roadmap | ⏳ Pending |

**Next Action**: Run Phase 4 to complete documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Air-Side (SBC) architecture documentation - Phase 3 (Sections 11-15)"
```

---

## 🚀 Phase 4: Operations & Future (Sections 16-21)

### Task for Claude Code

```
Task: Complete SBC_ARCHITECTURE.md - Phase 4 of 4 (FINAL)

IMPORTANT: APPEND to existing file: sbc/docs/SBC_ARCHITECTURE.md
(Read ENTIRE document to ensure consistency, then append final sections)

Generate SECTIONS 16-21:

═══════════════════════════════════════════════════════════════════

## 16. Testing

### 16.1 Test Structure

**Test Directory**: `sbc/tests/`

**Test Files** (list actual test files):
```
tests/
├── CMakeLists.txt
├── test_network.cpp
├── test_protocol.cpp
├── test_camera.cpp
├── test_gimbal.cpp
└── [list all test files]
```

### 16.2 Unit Testing

**Framework**: [Document if using Google Test, Catch2, etc., or manual tests]

**Example Test** (if tests exist):
```cpp
// Document actual test code
#include "network/tcp_server.hpp"
#include <gtest/gtest.h>

TEST(TcpServerTest, InitializeAndShutdown) {
    TcpServer server(5000);
    EXPECT_TRUE(server.start());
    EXPECT_TRUE(server.is_running());
    server.stop();
    EXPECT_FALSE(server.is_running());
}
```

[If no tests yet: "To be implemented"]

### 16.3 Integration Testing

**Hardware-in-Loop Tests**:
- Camera connection test
- Gimbal connection test
- Network communication test
- End-to-end command test

[Document test procedures]

### 16.4 Memory Leak Testing

**Valgrind**:
```bash
# Run service under valgrind
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         --log-file=valgrind.log \
         ./payload_manager -c config/test.conf

# Check for leaks
cat valgrind.log | grep "definitely lost"
# Should show: "0 bytes in 0 blocks"
```

**AddressSanitizer** (ASan):
```bash
# Build with ASan
cmake -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_FLAGS="-fsanitize=address -g" ..
make

# Run (ASan will detect memory errors immediately)
./payload_manager
```

### 16.5 Performance Testing

**Throughput Test**:
- Commands per second
- Status broadcast latency
- Network bandwidth usage

**Load Test**:
- Multiple simultaneous commands
- Stress test (continuous operation 8+ hours)
- Memory usage over time

[Document test procedures and results]

═══════════════════════════════════════════════════════════════════

## 17. Code Conventions

### 17.1 C++ Style Guide

**Based On**: [Google C++ Style Guide / Custom conventions]

### 17.2 Formatting

**Indentation**: 4 spaces (no tabs)

**Brace Style**: Attached (K&R style)
```cpp
void function() {
    if (condition) {
        // code
    } else {
        // code
    }
}

class MyClass {
public:
    void method() {
        // code
    }
};
```

**Line Length**: 100 characters (soft limit)

### 17.3 Naming Conventions

**Files**:
- Headers: `snake_case.hpp`
- Sources: `snake_case.cpp`
- Example: `tcp_server.hpp`, `tcp_server.cpp`

**Classes/Structs**:
- Format: `PascalCase`
- Example: `TcpServer`, `CameraController`, `PayloadManager`

**Functions/Methods**:
- Format: `snake_case`
- Example: `send_command()`, `get_status()`, `initialize_camera()`

**Variables**:
- Local: `snake_case`
- Member: `snake_case_` (trailing underscore)
- Example: `int port_number;`, `std::string server_ip_;`

**Constants**:
- Format: `UPPER_SNAKE_CASE`
- Example: `const int MAX_BUFFER_SIZE = 4096;`

**Namespaces**:
- Format: `lowercase` or `snake_case`
- Example: `namespace dpm`, `namespace camera_control`

**Enums**:
- Enum name: `PascalCase`
- Enum values: `PascalCase` or `UPPER_SNAKE_CASE`
```cpp
enum class GimbalMode {
    Follow,
    Lock,
    Home
};

// Or
enum LogLevel {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
};
```

### 17.4 Header Guards

**Use**: `#pragma once` (preferred, simpler)

```cpp
#pragma once

class MyClass {
    // ...
};
```

**Alternative**: Traditional include guards (if needed for compatibility)
```cpp
#ifndef DPM_TCP_SERVER_HPP
#define DPM_TCP_SERVER_HPP

class TcpServer {
    // ...
};

#endif  // DPM_TCP_SERVER_HPP
```

### 17.5 Include Order

```cpp
// 1. Corresponding header (for .cpp files)
#include "tcp_server.hpp"

// 2. C system headers
#include <sys/socket.h>
#include <netinet/in.h>

// 3. C++ standard library
#include <iostream>
#include <memory>
#include <string>

// 4. Third-party libraries
#include <nlohmann/json.hpp>

// 5. Project headers
#include "network/network_utils.hpp"
#include "utils/logger.hpp"
```

### 17.6 Comments and Documentation

**File Headers**:
```cpp
/**
 * @file tcp_server.hpp
 * @brief TCP server for receiving commands from ground station
 * @author DPM Team
 * @date 2025-10-25
 */
```

**Class Documentation**:
```cpp
/**
 * @brief TCP server for handling command connections
 * 
 * Listens on port 5000 for incoming TCP connections from the
 * H16 ground station. Spawns a handler thread for each connection.
 * Messages use length-prefixed JSON format.
 */
class TcpServer {
    // ...
};
```

**Function Documentation**:
```cpp
/**
 * @brief Send a command to the camera
 * 
 * @param command The JSON command object
 * @return true if command sent successfully, false otherwise
 * 
 * @note This function is thread-safe
 * @throws std::runtime_error if camera not connected
 */
bool send_command(const json& command);
```

**Inline Comments**:
```cpp
// Use inline comments to explain WHY, not WHAT
// Good:
// Check heartbeat every second to detect disconnection
if (/* condition */) { }

// Bad (obvious from code):
// Increment counter by 1
counter++;
```

### 17.7 Modern C++ Features

**Use**:
- `auto` for type inference (when type is obvious)
- Range-based for loops
- Smart pointers
- `nullptr` (not `NULL`)
- `override` and `final`
- `constexpr` for compile-time constants
- Uniform initialization `{}`

**Examples**:
```cpp
// auto
auto camera = std::make_unique<SonyCamera>();

// Range-based for
for (const auto& item : collection) {
    // ...
}

// Smart pointers
std::unique_ptr<TcpServer> server;
std::shared_ptr<CameraController> camera;

// nullptr
if (ptr == nullptr) { }

// override
class Derived : public Base {
    void method() override { }
};

// constexpr
constexpr int MAX_CONNECTIONS = 10;

// Uniform initialization
std::vector<int> numbers{1, 2, 3, 4, 5};
```

═══════════════════════════════════════════════════════════════════

## 18. Deployment

### 18.1 Installation on Raspberry Pi

**Prerequisites**:
- Raspberry Pi 4 (4GB or 8GB RAM)
- Ubuntu 22.04 LTS ARM64 installed
- Internet connection for dependencies
- Sony camera connected via USB
- Gimbal connected via serial (if applicable)

**Step 1: Install System Dependencies**:
```bash
# Run installation script
cd sbc
sudo ./scripts/install_dependencies.sh

# Or manually:
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git \
    nlohmann-json3-dev libusb-1.0-0-dev libudev-dev
```

**Step 2: Install Sony SDK**:
```bash
# Sony SDK must be obtained from Sony
# Extract to sbc/external/sony_sdk/
cd sbc/external
# (Assuming SDK zip is in Downloads)
cp ~/Downloads/CrSDK_v2.00.00_*.tar.gz .
tar -xzf CrSDK_v2.00.00_*.tar.gz
mv CrSDK_v2.00.00_* sony_sdk/

# Verify libraries
ls sony_sdk/lib/
# Should see: libCrAdapter.so, libCrImageDataBlock.so
```

**Step 3: Configure USB Permissions**:
```bash
# Allow non-root access to Sony camera USB
sudo nano /etc/udev/rules.d/99-sony-camera.rules

# Add this line (Sony USB vendor ID is 054c):
SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Verify camera is detected
lsusb | grep Sony
```

**Step 4: Build Application**:
```bash
cd sbc
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)

# Verify executable
ls -lh payload_manager
./payload_manager --version
```

**Step 5: Install System-Wide**:
```bash
sudo make install

# This installs:
# - /usr/local/bin/payload_manager (executable)
# - /etc/dpm/payload_manager.conf (config)

# Verify installation
which payload_manager
cat /etc/dpm/payload_manager.conf
```

**Step 6: Create systemd Service**:
```bash
sudo nano /etc/systemd/system/dpm-airside.service
```

**systemd Service File**:
```ini
[Unit]
Description=DPM Air-Side Payload Manager Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi
ExecStart=/usr/local/bin/payload_manager -c /etc/dpm/payload_manager.conf
Restart=on-failure
RestartSec=5s

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dpm-airside

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

**Step 7: Enable and Start Service**:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable dpm-airside.service

# Start service
sudo systemctl start dpm-airside.service

# Check status
sudo systemctl status dpm-airside.service

# View logs
sudo journalctl -u dpm-airside.service -f
```

### 18.2 Configuration

**Edit Configuration**:
```bash
sudo nano /etc/dpm/payload_manager.conf

# Adjust network settings for your environment
# - TCP port (default 5000)
# - UDP ports (default 5001, 5002)
# - Target IP (H16 ground station IP)
# - Camera settings
# - Gimbal settings
```

**Restart After Config Change**:
```bash
sudo systemctl restart dpm-airside.service
```

### 18.3 Service Management

**Common Commands**:
```bash
# Start service
sudo systemctl start dpm-airside.service

# Stop service
sudo systemctl stop dpm-airside.service

# Restart service
sudo systemctl restart dpm-airside.service

# Check status
sudo systemctl status dpm-airside.service

# View logs (real-time)
sudo journalctl -u dpm-airside.service -f

# View logs (last 100 lines)
sudo journalctl -u dpm-airside.service -n 100

# Disable auto-start
sudo systemctl disable dpm-airside.service

# Enable auto-start
sudo systemctl enable dpm-airside.service
```

### 18.4 Network Configuration

**Set Static IP** (recommended for air-side):
```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

**Netplan Config**:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 10.0.1.20/24
      # Gateway typically not needed for point-to-point
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

**Apply Network Config**:
```bash
sudo netplan apply

# Verify IP
ip addr show eth0
```

### 18.5 Firewall Configuration (if needed)

**UFW Rules**:
```bash
# Allow DPM ports
sudo ufw allow 5000/tcp  # Commands
sudo ufw allow 5001/udp  # Status
sudo ufw allow 5002/udp  # Heartbeat

# Allow SSH (for remote access)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 18.6 Troubleshooting

**Service Won't Start**:
```bash
# Check logs for errors
sudo journalctl -u dpm-airside.service -n 50

# Common issues:
# - Configuration file not found
# - Camera not connected/permissions
# - Network interface not ready
# - Sony SDK libraries not found
```

**Camera Not Detected**:
```bash
# Check USB connection
lsusb | grep Sony

# Check udev rules
cat /etc/udev/rules.d/99-sony-camera.rules

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check permissions
ls -l /dev/bus/usb/*/*  # Look for Sony device
```

**Network Issues**:
```bash
# Check IP configuration
ip addr show

# Test connectivity to H16
ping 10.0.1.11

# Check if service is listening
sudo netstat -tulpn | grep payload_manager

# Test TCP port
nc -zv 10.0.1.20 5000
```

═══════════════════════════════════════════════════════════════════

## 19. Performance Optimization

### 19.1 Performance Metrics

**Target Performance**:
- Command response time: < 100ms
- Status broadcast rate: 5 Hz (200ms interval)
- Heartbeat rate: 1 Hz
- CPU usage: < 40% (one core)
- Memory usage: < 200 MB
- Camera capture latency: < 500ms
- Gimbal command latency: < 50ms

**Actual Performance** (document if measured):
[List actual performance metrics]

### 19.2 CPU Profiling

**Using gprof**:
```bash
# Build with profiling enabled
cmake -DCMAKE_BUILD_TYPE=Debug \
      -DCMAKE_CXX_FLAGS="-pg" ..
make

# Run application
./payload_manager

# Generate profile report
gprof payload_manager gmon.out > profile.txt

# Analyze hotspots
cat profile.txt | head -50
```

**Using perf**:
```bash
# Run with perf
sudo perf record -g ./payload_manager

# View report
sudo perf report
```

### 19.3 Memory Profiling

**Using Valgrind (Massif)**:
```bash
# Profile memory usage
valgrind --tool=massif \
         --massif-out-file=massif.out \
         ./payload_manager

# Visualize with ms_print
ms_print massif.out
```

### 19.4 Optimization Strategies

**Network**:
- Use pre-allocated buffers for send/receive
- Minimize JSON serialization overhead
- Batch status updates when possible

**Camera**:
- Cache property values to avoid SDK calls
- Use async operations where possible

**Threading**:
- Minimize mutex contention
- Use thread-local storage for frequent operations
- Avoid thread creation/destruction (use thread pool)

**Memory**:
- Pre-allocate buffers
- Object pools for frequently created objects
- Avoid unnecessary copies (use move semantics)

### 19.5 Raspberry Pi 4 Specific

**CPU Governor**:
```bash
# Set performance governor for max CPU speed
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
```

**Disable Unnecessary Services**:
```bash
# Disable Bluetooth (if not needed)
sudo systemctl disable bluetooth.service

# Disable WiFi (if using Ethernet)
sudo systemctl disable wpa_supplicant.service
```

═══════════════════════════════════════════════════════════════════

## 20. Known Issues & Technical Debt

### 20.1 Current Limitations

**Network**:
- [List network-related limitations]
- Example: "TCP reconnection on disconnect not yet implemented"

**Camera**:
- [List camera-related limitations]
- Example: "Some Sony camera models not yet tested"

**Gimbal**:
- [List gimbal-related limitations]
- Example: "SimpleBGC calibration not yet implemented"

**Video Streaming**:
- [List video-related limitations]
- Example: "RTSP streaming not yet implemented"

**Performance**:
- [List performance concerns]
- Example: "Status broadcast may jitter under heavy CPU load"

### 20.2 Technical Debt

**Code Quality**:
- [ ] Add unit tests for all modules
- [ ] Add integration tests
- [ ] Improve error handling in [specific module]
- [ ] Add KDoc comments to public APIs
- [List other code quality items]

**Architecture**:
- [ ] Consider message queue for command processing
- [ ] Refactor [module] for better testability
- [ ] Implement connection pooling for TCP
- [List architecture improvements]

**Build System**:
- [ ] Add automated build script
- [ ] Add cross-compilation support
- [ ] Package as .deb for easier installation
- [List build improvements]

### 20.3 Known Bugs

**Bug List** (if any):
1. [Bug description]
   - Workaround: [If available]
   - Priority: High/Medium/Low
   - Target fix: [Version/phase]

[List all known bugs with details]

### 20.4 Compatibility Issues

**Sony Camera Compatibility**:
- Tested: [List tested camera models]
- Known issues: [List model-specific issues]

**Gimbal Compatibility**:
- Gremsy: [Compatibility status]
- SimpleBGC: [Compatibility status]

**Raspberry Pi Compatibility**:
- Pi 4: ✅ Fully supported
- Pi 3: [Status]
- Pi 5: [Status]

═══════════════════════════════════════════════════════════════════

## 21. Future Roadmap

### 21.1 Phase 2 Features (Planned)

**Camera**:
- [ ] Picture profile control (S-Log, HLG, etc.)
- [ ] Firmware update capability
- [ ] Multiple camera support
- [ ] Advanced focus controls (face detection, tracking)

**Gimbal**:
- [ ] Gimbal calibration
- [ ] Advanced follow modes
- [ ] Virtual joystick control

**Network**:
- [ ] MAVLink integration for flight controller
- [ ] Telemetry overlay on video
- [ ] Mission planning integration

**Storage**:
- [ ] Automatic content download after landing
- [ ] Cloud upload capability
- [ ] RAW image handling

### 21.2 Phase 3 Features (Future)

**Video Streaming**:
- [ ] RTSP server implementation
- [ ] H.264 hardware encoding
- [ ] Multi-bitrate adaptive streaming
- [ ] Recording to local storage

**Advanced Features**:
- [ ] AI-based subject tracking
- [ ] Automatic exposure/focus based on scene
- [ ] HDR video capture
- [ ] Time-lapse and interval shooting

**System**:
- [ ] Web-based configuration interface
- [ ] OTA (Over-The-Air) updates
- [ ] Advanced diagnostics and health monitoring
- [ ] Redundant system support

### 21.3 Planned Refactoring

**Code Quality**:
1. Achieve >80% unit test coverage
2. Add comprehensive integration tests
3. Improve error handling consistency
4. Add performance benchmarks

**Architecture**:
1. Implement dependency injection container
2. Add plugin system for extensibility
3. Modularize for easier testing
4. Improve configuration system (hot-reload)

**Build & Deployment**:
1. Create Debian package (.deb)
2. Add Docker support
3. Automated CI/CD pipeline
4. Cross-platform support (other SBCs)

### 21.4 Performance Goals

**Target Improvements**:
- Reduce command latency to < 50ms
- Increase status rate to 10 Hz
- Reduce memory footprint to < 150 MB
- Support 4K video streaming at 30fps

═══════════════════════════════════════════════════════════════════

## 22. Appendices

### Appendix A: Glossary

**Terms and Abbreviations**:
- **DPM**: Drone Payload Manager
- **SBC**: Single Board Computer (Raspberry Pi)
- **H16**: SkyDroid H16 Ground Control Station
- **R16**: SkyDroid R16 Air Unit
- **UAV**: Unmanned Aerial Vehicle
- **SDK**: Software Development Kit
- **RAII**: Resource Acquisition Is Initialization
- **RTSP**: Real Time Streaming Protocol
- **TCP**: Transmission Control Protocol
- **UDP**: User Datagram Protocol
- **JSON**: JavaScript Object Notation
- **API**: Application Programming Interface
- **GCS**: Ground Control Station
- **MAVLink**: Micro Air Vehicle Link (protocol)
- [All other terms]

### Appendix B: External Resources

**Official Documentation**:
- Sony Camera Remote SDK: http://www.sony.net/CameraRemoteSDK/
- Gremsy gSDK: https://github.com/Gremsy/gSDK
- SimpleBGC API: https://github.com/basecamelectronics/sbgc32-serial-api
- nlohmann-json: https://github.com/nlohmann/json
- CMake Documentation: https://cmake.org/documentation/

**C++ Resources**:
- C++17 Reference: https://en.cppreference.com/w/cpp/17
- Google C++ Style Guide: https://google.github.io/styleguide/cppguide.html
- Modern C++ Tutorial: https://changkun.de/modern-cpp/

**Raspberry Pi**:
- Raspberry Pi Documentation: https://www.raspberrypi.org/documentation/
- Ubuntu on Raspberry Pi: https://ubuntu.com/download/raspberry-pi

**Project Resources**:
- GitHub Repository: https://github.com/unmanned-systems-uk/DPM-V2.git
- Project Summary: `docs/Project_Summary_and_Action_Plan.md`
- Progress Tracker: `sbc/docs/PROGRESS_AND_TODO.md`
- Protocol Specification: `docs/Command_Protocol_Specification_v1.0.md`

**Related Documentation**:
- Android Architecture: `android/docs/ANDROID_ARCHITECTURE.md`
- Ground-Side Implementation: [Link to Android docs]

### Appendix C: Contact & Support

**Development Team**:
- Organization: unmanned-systems-uk
- [Team contact information if applicable]

**Support Channels**:
- GitHub Issues: [Repository URL]/issues
- [Other support channels if applicable]

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status - FINAL

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-5: Executive Summary, Project Structure, Architecture Overview, Core Components, Network Layer | ✅ Complete |
| **Phase 2** | 6-10: Camera Integration, Gimbal Integration, Video Streaming, Protocol Implementation, Threading Model | ✅ Complete |
| **Phase 3** | 11-15: Memory Management, Error Handling, Configuration System, Dependencies, Build System | ✅ Complete |
| **Phase 4** | 16-21: Testing, Code Conventions, Deployment, Performance, Known Issues, Future Roadmap | ✅ **COMPLETE** |

**✅ DOCUMENTATION COMPLETE - ALL 21 SECTIONS GENERATED**

═══════════════════════════════════════════════════════════════════

---

**Document Metadata**

**Title**: DPM Air-Side (SBC) - Complete Architecture Documentation  
**Version**: 1.0  
**Last Updated**: [Date]  
**Generated By**: Claude Code (Phased Generation)  
**Total Sections**: 21  
**File**: `sbc/docs/SBC_ARCHITECTURE.md`  
**Language**: C++17
**Platform**: Raspberry Pi 4 (Ubuntu 22.04 LTS ARM64)

**Generation Summary**:
- Phase 1: Sections 1-5 (Foundation & Core)
- Phase 2: Sections 6-10 (Hardware Integration)
- Phase 3: Sections 11-15 (System Infrastructure)
- Phase 4: Sections 16-21 (Operations & Future)

This document provides comprehensive architecture documentation for the DPM Air-Side C++ application, covering all aspects from high-level architecture to C++ implementation details, Sony SDK integration, threading model, memory management, build system, deployment procedures, and future roadmap.

---

**END OF DOCUMENT**

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read ENTIRE document for consistency
✅ Append final sections
✅ Use actual code and procedures
✅ Document testing thoroughly
✅ Document C++ conventions
✅ Document complete deployment process
✅ Document performance optimization
✅ Document known issues honestly
✅ Document future roadmap
✅ Keep under 20,000 tokens
✅ Mark document as COMPLETE

Git commit message:
"[DOCS] Complete Air-Side (SBC) architecture documentation - Phase 4 (Sections 16-21)

- Add testing structure and procedures
- Add C++ code conventions and style guide
- Add complete deployment procedures for Raspberry Pi
- Add systemd service configuration
- Document performance optimization strategies
- Document known issues and technical debt
- Add future roadmap and planned features
- Add appendices with glossary and resources

✅ All 21 sections complete
✅ Comprehensive C++ architecture documentation finished"
```

---

## 📊 Progress Tracking Template

After each phase, Claude Code should update this status in the document:

```markdown
## 📋 Document Generation Status

| Phase | Sections | Est. Lines | Status | Date |
|-------|----------|------------|--------|------|
| **Phase 1** | 1-5: Foundation & Core | ~600 | ✅ Complete | [date] |
| **Phase 2** | 6-10: Hardware Integration | ~700 | ✅ Complete | [date] |
| **Phase 3** | 11-15: System Infrastructure | ~600 | ✅ Complete | [date] |
| **Phase 4** | 16-21: Operations & Future | ~500 | ✅ Complete | [date] |

**Total Estimated Lines**: ~2400+ lines of documentation
```

---

## ✅ Completion Checklist

After Phase 4, verify:

- [ ] All 21 sections are present and complete
- [ ] All code examples use actual C++ code from codebase
- [ ] Sony SDK integration thoroughly documented
- [ ] Threading model clearly explained
- [ ] Memory management patterns documented
- [ ] Build system completely documented
- [ ] Deployment procedures tested and accurate
- [ ] All dependencies listed with versions
- [ ] All diagrams are clear and accurate
- [ ] Table of contents is complete and linked
- [ ] Document status shows all phases complete
- [ ] Git commits made for each phase
- [ ] File is readable and well-formatted
- [ ] No placeholder text remains
- [ ] Cross-references between sections work

---

## 🚨 Troubleshooting

### If Claude Code Still Hits Token Limit:

**Option 1: Further Break Down Phases**
Split problematic phase into sub-phases:
- Phase 2a: Sections 6-7 (Camera & Gimbal)
- Phase 2b: Sections 8-10 (Video, Protocol, Threading)

**Option 2: Create Separate Files**
Instead of one large file, create:
- `SBC_ARCHITECTURE_MAIN.md` (overview)
- `SBC_CAMERA_INTEGRATION.md` (Sony SDK details)
- `SBC_NETWORK_LAYER.md` (networking details)
- `SBC_THREADING_MODEL.md` (threading details)
- `SBC_BUILD_DEPLOYMENT.md` (build and deployment)
- etc.

**Option 3: Reduce Detail Level**
Ask Claude Code to be more concise:
- Fewer code examples
- Briefer descriptions
- Less duplication

---

## 🎯 Expected Final Output

After completing all 4 phases:

**File**: `sbc/docs/SBC_ARCHITECTURE.md`

**Size**: 2400-3500 lines

**Sections**: 21 complete sections covering:
1. Executive Summary
2. Project Structure
3. Architecture Overview
4. Core Components
5. Network Layer
6. Camera Integration
7. Gimbal Integration
8. Video Streaming
9. Protocol Implementation
10. Threading Model
11. Memory Management
12. Error Handling
13. Configuration System
14. Dependencies
15. Build System
16. Testing
17. Code Conventions
18. Deployment
19. Performance Optimization
20. Known Issues & Technical Debt
21. Future Roadmap
22. Appendices

**Git Commits**: 4 commits (one per phase)

---

**Document Ready**: ✅ This instruction file is complete and ready to use with Claude Code (Air-Side)!

**Start with Phase 1** and work through sequentially to generate complete C++ architecture documentation.

Good luck! 🚀📚🔧
