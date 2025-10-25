Instructions for Claude Code: Generate Complete Air-Side (SBC) Architecture Documentation
📋 Overview
Task: Generate comprehensive architecture documentation for the entire DPM Air-Side (Raspberry Pi SBC) C++ application.
Output: sbc/docs/SBC_ARCHITECTURE.md (and supplementary files if needed)
Estimated Time: 4-6 hours
Approach: Systematic analysis of entire C++ codebase, then structured documentation generation.

🎯 Objectives
Create professional-grade documentation that:

Maps entire project structure and organization
Documents all C++ classes, modules, and their interactions
Explains data flow and threading architecture
Describes network communication implementation
Details Sony SDK integration
Documents gimbal control integration
Lists all dependencies and build system
Defines code conventions and patterns
Provides onboarding guide for new C++ developers


📁 Required Output Files
Primary Document
File: sbc/docs/SBC_ARCHITECTURE.md
Contents:

Complete architecture overview
All C++ classes and modules documented
Threading and concurrency model
Memory management patterns
Network protocol implementation
Sony SDK integration details
Build system documentation
~5000-10000 lines

Supplementary Documents (Create if needed)

sbc/docs/CLASS_REFERENCE.md - Detailed class-by-class reference
sbc/docs/MODULE_STRUCTURE.md - Module organization details
sbc/docs/NETWORK_IMPLEMENTATION.md - Network layer deep dive
sbc/docs/SONY_SDK_INTEGRATION.md - Sony SDK usage guide
sbc/docs/THREADING_MODEL.md - Concurrency and threading details
sbc/docs/BUILD_GUIDE.md - Complete build instructions


📐 Documentation Structure Template
markdown# DPM Air-Side (SBC) - Architecture Documentation

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
6. [Camera Integration](#6-camera-integration)
7. [Gimbal Integration](#7-gimbal-integration)
8. [Video Streaming](#8-video-streaming)
9. [Protocol Implementation](#9-protocol-implementation)
10. [Threading Model](#10-threading-model)
11. [Memory Management](#11-memory-management)
12. [Error Handling](#12-error-handling)
13. [Configuration System](#13-configuration-system)
14. [Dependencies](#14-dependencies)
15. [Build System](#15-build-system)
16. [Testing](#16-testing)
17. [Code Conventions](#17-code-conventions)
18. [Deployment](#18-deployment)
19. [Performance Optimization](#19-performance-optimization)
20. [Known Issues & Technical Debt](#20-known-issues--technical-debt)
21. [Future Roadmap](#21-future-roadmap)

---

## 1. Executive Summary

### 1.1 Project Overview
**Purpose**: Real-time payload management service for UAV operations

**Key Responsibilities**:
- Sony camera control via SDK
- Gimbal control (Gremsy/SimpleBGC)
- Network communication with ground station
- Video streaming (RTSP)
- Status monitoring and reporting
- Content management (download/storage)

### 1.2 Technology Stack

**Language**: C++17

**Core Libraries**:
- Sony Camera Remote SDK v2.00.00
- nlohmann-json (JSON parsing)
- POSIX sockets (networking)
- pthreads (threading)
- [List all others]

**Build System**:
- CMake 3.16+
- GCC 11+ / Clang 12+
- Make / Ninja

**Operating System**:
- Ubuntu 22.04 LTS ARM64
- Kernel: [version]

### 1.3 Key Features
- ✅ [Feature 1]
- ✅ [Feature 2]
- 🚧 [In Progress]
- ⏳ [Planned]

### 1.4 Development Status
**Current Phase**: [Phase number and name]

**Completed**:
- [What's done]

**In Progress**:
- [What's being worked on]

**Planned**:
- [What's next]

### 1.5 Target Hardware
- **SBC**: Raspberry Pi 4 (4GB/8GB RAM)
- **Camera**: Sony Alpha series (USB connection)
- **Gimbal**: Gremsy T3V3 or SimpleBGC-based
- **Network**: Ethernet/WiFi to H16 (10.0.1.x)
- **Storage**: microSD card (32GB+)

---

## 2. Project Structure

### 2.1 Directory Layout
```
sbc/
├── CMakeLists.txt                 # Root CMake configuration
├── README.md                      # Project overview
├── LICENSE                        # License information
├── .gitignore                     # Git ignore rules
│
├── src/                           # Source files
│   ├── main.cpp                   # Application entry point
│   ├── payload_manager.cpp        # Main service class
│   │
│   ├── network/                   # Network communication
│   │   ├── tcp_server.cpp         # TCP command server
│   │   ├── udp_broadcaster.cpp    # UDP status broadcaster
│   │   ├── heartbeat_manager.cpp  # Heartbeat mechanism
│   │   └── network_utils.cpp      # Network utilities
│   │
│   ├── protocol/                  # Protocol implementation
│   │   ├── message_handler.cpp    # JSON message parsing
│   │   ├── command_processor.cpp  # Command execution
│   │   └── status_builder.cpp     # Status message creation
│   │
│   ├── camera/                    # Sony camera integration
│   │   ├── sony_camera.cpp        # Sony SDK wrapper
│   │   ├── camera_controller.cpp  # High-level camera control
│   │   ├── sony_live_view.cpp     # Live view integration
│   │   └── content_manager.cpp    # Content download/storage
│   │
│   ├── gimbal/                    # Gimbal control
│   │   ├── gimbal_interface.cpp   # Abstract gimbal interface
│   │   ├── gremsy_gimbal.cpp      # Gremsy gSDK integration
│   │   └── simplebgc_gimbal.cpp   # SimpleBGC integration
│   │
│   ├── video/                     # Video streaming (if implemented)
│   │   ├── stream_manager.cpp     # Video stream coordinator
│   │   ├── rtsp_server.cpp        # RTSP server
│   │   └── video_encoder.cpp      # Video encoding
│   │
│   ├── utils/                     # Utility functions
│   │   ├── logger.cpp             # Logging system
│   │   ├── config_parser.cpp      # Configuration file parsing
│   │   └── error_handler.cpp      # Error handling utilities
│   │
│   └── storage/                   # Storage management
│       ├── storage_manager.cpp    # Disk space management
│       └── file_transfer.cpp      # File transfer utilities
│
├── include/                       # Header files
│   ├── payload_manager.hpp
│   │
│   ├── network/
│   │   ├── tcp_server.hpp
│   │   ├── udp_broadcaster.hpp
│   │   ├── heartbeat_manager.hpp
│   │   └── network_utils.hpp
│   │
│   ├── protocol/
│   │   ├── message_handler.hpp
│   │   ├── command_processor.hpp
│   │   ├── status_builder.hpp
│   │   └── protocol_types.hpp     # Protocol data structures
│   │
│   ├── camera/
│   │   ├── sony_camera.hpp
│   │   ├── camera_controller.hpp
│   │   ├── sony_live_view.hpp
│   │   └── content_manager.hpp
│   │
│   ├── gimbal/
│   │   ├── gimbal_interface.hpp
│   │   ├── gremsy_gimbal.hpp
│   │   └── simplebgc_gimbal.hpp
│   │
│   ├── video/
│   │   ├── stream_manager.hpp
│   │   ├── rtsp_server.hpp
│   │   └── video_encoder.hpp
│   │
│   ├── utils/
│   │   ├── logger.hpp
│   │   ├── config_parser.hpp
│   │   └── error_handler.hpp
│   │
│   └── storage/
│       ├── storage_manager.hpp
│       └── file_transfer.hpp
│
├── tests/                         # Unit and integration tests
│   ├── CMakeLists.txt
│   ├── test_network.cpp
│   ├── test_protocol.cpp
│   ├── test_camera.cpp
│   └── test_gimbal.cpp
│
├── config/                        # Configuration files
│   ├── payload_manager.conf       # Main configuration
│   ├── camera_defaults.json       # Camera default settings
│   └── network.conf               # Network configuration
│
├── scripts/                       # Utility scripts
│   ├── install_dependencies.sh    # Install system dependencies
│   ├── build.sh                   # Build script
│   ├── deploy.sh                  # Deployment script
│   └── run_tests.sh               # Test runner
│
├── docs/                          # Documentation
│   ├── SBC_ARCHITECTURE.md        # This file
│   ├── PROGRESS_AND_TODO.md       # Development progress
│   ├── API_REFERENCE.md           # API documentation
│   └── TROUBLESHOOTING.md         # Common issues
│
├── external/                      # External dependencies
│   ├── sony_sdk/                  # Sony Camera Remote SDK
│   │   ├── include/
│   │   └── lib/
│   ├── gremsy_sdk/                # Gremsy gSDK
│   └── simplebgc_api/             # SimpleBGC Serial API
│
└── build/                         # CMake build directory (gitignored)
    ├── payload_manager            # Main executable
    ├── tests/                     # Test executables
    └── [CMake generated files]
```

### 2.2 Module Organization

#### Network Module (`src/network/`, `include/network/`)
**Purpose**: TCP/UDP communication with ground station

**Files**: [count]

**Key Classes**:
- `TcpServer` - TCP command listener
- `UdpBroadcaster` - UDP status broadcaster
- `HeartbeatManager` - Connection monitoring

**Dependencies**:
- POSIX sockets
- pthreads
- nlohmann-json

---

#### Protocol Module (`src/protocol/`, `include/protocol/`)
**Purpose**: Message parsing and command execution

**Files**: [count]

**Key Classes**:
- `MessageHandler` - JSON message parsing
- `CommandProcessor` - Command execution dispatcher
- `StatusBuilder` - Status message construction

**Dependencies**:
- nlohmann-json
- Camera module
- Gimbal module

---

#### Camera Module (`src/camera/`, `include/camera/`)
**Purpose**: Sony camera control via SDK

**Files**: [count]

**Key Classes**:
- `SonyCamera` - Sony SDK wrapper
- `CameraController` - High-level camera operations
- `SonyCameraLiveView` - Live view streaming
- `ContentManager` - File download/storage

**Dependencies**:
- Sony Camera Remote SDK
- Storage module

---

#### Gimbal Module (`src/gimbal/`, `include/gimbal/`)
**Purpose**: Multi-gimbal support

**Files**: [count]

**Key Classes**:
- `GimbalInterface` - Abstract interface
- `GremsyGimbal` - Gremsy implementation
- `SimpleBGCGimbal` - SimpleBGC implementation

**Dependencies**:
- Gremsy gSDK
- SimpleBGC Serial API

---

#### Video Module (`src/video/`, `include/video/`) [If implemented]
**Purpose**: RTSP video streaming

**Files**: [count]

**Key Classes**:
- `StreamManager` - Video stream coordinator
- `RtspServer` - RTSP server implementation
- `VideoEncoder` - H.264 encoding

**Dependencies**:
- GStreamer or FFmpeg
- Sony SDK live view

---

#### Utils Module (`src/utils/`, `include/utils/`)
**Purpose**: Common utilities

**Files**: [count]

**Key Classes**:
- `Logger` - Logging system
- `ConfigParser` - Configuration management
- `ErrorHandler` - Error handling utilities

**Dependencies**: Standard library

---

### 2.3 File Naming Conventions

**Header Files**: `snake_case.hpp`
- Example: `tcp_server.hpp`, `sony_camera.hpp`

**Source Files**: `snake_case.cpp`
- Example: `tcp_server.cpp`, `sony_camera.cpp`

**Class Names**: `PascalCase`
- Example: `TcpServer`, `SonyCamera`

**Function Names**: `snake_case`
- Example: `send_command()`, `get_status()`

**Constants**: `UPPER_SNAKE_CASE`
- Example: `MAX_BUFFER_SIZE`, `DEFAULT_PORT`

**Namespaces**: `lowercase`
- Example: `namespace dpm`, `namespace network`

---

## 3. Architecture Overview

### 3.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    DPM Air-Side Service                         │
│                   (Raspberry Pi 4 - C++17)                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Main Event Loop                         │ │
│  │              (PayloadManager class)                        │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────┼───────────────────────────────┐ │
│  │         Network Layer     │    (Multi-threaded)           │ │
│  │  ┌────────────┐  ┌────────▼───────┐  ┌─────────────────┐ │ │
│  │  │ TCP Server │  │ UDP Broadcaster│  │ Heartbeat Mgr   │ │ │
│  │  │ Port 5000  │  │ Port 5001      │  │ Port 5002       │ │ │
│  │  │ (Commands) │  │ (Status 5Hz)   │  │ (Heartbeat 1Hz) │ │ │
│  │  └─────┬──────┘  └────────┬───────┘  └────────┬────────┘ │ │
│  └────────┼──────────────────┼───────────────────┼──────────┘ │
│           │                  │                   │             │
│  ┌────────▼──────────────────▼───────────────────▼──────────┐ │
│  │              Protocol Handler                             │ │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐   │ │
│  │  │ Message Parser  │  │  Command Processor           │   │ │
│  │  │ (JSON)          │  │  (Dispatcher)                │   │ │
│  │  └─────────────────┘  └──────────────────────────────┘   │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────┴───────────────────────────────┐ │
│  │                    Control Layer                           │ │
│  │  ┌──────────────────┐  ┌────────────────┐  ┌───────────┐ │ │
│  │  │ Camera Control   │  │ Gimbal Control │  │ Storage   │ │ │
│  │  │                  │  │                │  │ Manager   │ │ │
│  │  └────────┬─────────┘  └───────┬────────┘  └─────┬─────┘ │ │
│  └───────────┼────────────────────┼──────────────────┼───────┘ │
│              │                    │                  │          │
│  ┌───────────▼────────────────────▼──────────────────▼───────┐ │
│  │                Hardware Interface Layer                    │ │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │
│  │  │ Sony SDK     │  │ Gremsy SDK  │  │ File System     │  │ │
│  │  │ (USB Camera) │  │ (Serial)    │  │ (Storage)       │  │ │
│  │  └──────────────┘  └─────────────┘  └─────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ USB / Serial / Network
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        Hardware                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Sony       │  │ Gremsy/    │  │ Network    │  │ Storage  │ │
│  │ Camera     │  │ SimpleBGC  │  │ Interface  │  │ (SD Card)│ │
│  │            │  │ Gimbal     │  │ (eth/WiFi) │  │          │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Design Patterns

#### 3.2.1 RAII (Resource Acquisition Is Initialization)
**Usage**: All resource management (sockets, file handles, SDK objects)

**Example**:
```cpp
class TcpServer {
private:
    int socket_fd_;
    
public:
    TcpServer() {
        socket_fd_ = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_fd_ < 0) {
            throw std::runtime_error("Failed to create socket");
        }
    }
    
    ~TcpServer() {
        if (socket_fd_ >= 0) {
            close(socket_fd_);
        }
    }
    
    // Prevent copy, allow move
    TcpServer(const TcpServer&) = delete;
    TcpServer& operator=(const TcpServer&) = delete;
    TcpServer(TcpServer&&) = default;
    TcpServer& operator=(TcpServer&&) = default;
};
```

---

#### 3.2.2 Dependency Injection
**Usage**: Constructor injection for testability

**Example**:
```cpp
class CommandProcessor {
private:
    std::shared_ptr camera_;
    std::shared_ptr gimbal_;
    
public:
    CommandProcessor(
        std::shared_ptr camera,
        std::shared_ptr gimbal
    ) : camera_(camera), gimbal_(gimbal) {}
    
    void process_command(const Command& cmd) {
        // Use injected dependencies
    }
};
```

---

#### 3.2.3 Strategy Pattern
**Usage**: Gimbal implementations (Gremsy vs SimpleBGC)

**Example**:
```cpp
class GimbalInterface {
public:
    virtual ~GimbalInterface() = default;
    virtual bool set_angle(float pitch, float yaw, float roll) = 0;
    virtual bool set_mode(GimbalMode mode) = 0;
};

class GremsyGimbal : public GimbalInterface {
    // Gremsy-specific implementation
};

class SimpleBGCGimbal : public GimbalInterface {
    // SimpleBGC-specific implementation
};
```

---

#### 3.2.4 Observer Pattern
**Usage**: Status updates, camera events

**Example**:
```cpp
class CameraObserver {
public:
    virtual ~CameraObserver() = default;
    virtual void on_camera_connected() = 0;
    virtual void on_camera_disconnected() = 0;
    virtual void on_capture_complete(const std::string& filename) = 0;
};

class SonyCamera {
private:
    std::vector<std::weak_ptr> observers_;
    
public:
    void add_observer(std::shared_ptr observer) {
        observers_.push_back(observer);
    }
    
    void notify_capture_complete(const std::string& filename) {
        for (auto& weak_obs : observers_) {
            if (auto obs = weak_obs.lock()) {
                obs->on_capture_complete(filename);
            }
        }
    }
};
```

---

#### 3.2.5 Singleton Pattern
**Usage**: Logger, ConfigParser (with care)

**Example**:
```cpp
class Logger {
private:
    Logger() = default;
    
public:
    static Logger& instance() {
        static Logger instance;
        return instance;
    }
    
    // Delete copy/move
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    
    void log(LogLevel level, const std::string& message);
};
```

---

### 3.3 Threading Model
```
┌─────────────────────────────────────────────────────────────┐
│                     Main Thread                             │
│  - Initialization                                           │
│  - Main event loop                                          │
│  - Coordination                                             │
│  - Shutdown                                                 │
└────────────┬────────────────────────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐    ┌────▼──────┐
│ TCP      │    │ UDP       │
│ Server   │    │ Broadcast │
│ Thread   │    │ Thread    │
│          │    │           │
│ Receives │    │ Sends     │
│ Commands │    │ Status    │
│          │    │ @ 5Hz     │
└────┬─────┘    └───────────┘
     │
┌────▼──────────────────────┐
│ Command Processor Thread  │
│ - Queue processing        │
│ - Camera operations       │
│ - Gimbal operations       │
└───────────────────────────┘
```

**Thread Safety**:
- Mutex protection for shared state
- Lock-free queues for command passing
- Atomic operations for flags/counters

---

### 3.4 Data Flow

#### Command Flow (Ground → Air)
```
Ground Station (Android App)
    ↓ TCP Connection
TCP Server Thread (Air-Side)
    ↓ Parse JSON
Message Handler
    ↓ Validate & Queue
Command Processor Thread
    ↓ Execute
Camera/Gimbal Controller
    ↓ SDK Call
Sony SDK / Gimbal SDK
    ↓ Hardware Operation
Camera / Gimbal Hardware
```

#### Status Flow (Air → Ground)
```
Camera/Gimbal State Changes
    ↓ Callback/Polling
Controller Updates Internal State
    ↓ Collect Status
Status Builder (@ 5Hz)
    ↓ Build JSON
UDP Broadcaster Thread
    ↓ UDP Packet
Ground Station (Android App)
```

---

## 4. Core Components

### 4.1 PayloadManager (Main Service Class)

**File**: `src/payload_manager.cpp`, `include/payload_manager.hpp`

**Purpose**: Main application coordinator and lifecycle manager

**Responsibilities**:
- Initialize all subsystems
- Manage main event loop
- Coordinate between modules
- Handle graceful shutdown
- Signal handling

**Class Definition**:
```cpp
// Document actual class structure
class PayloadManager {
public:
    PayloadManager();
    ~PayloadManager();
    
    // Lifecycle
    bool initialize(const std::string& config_file);
    void run();
    void shutdown();
    
    // Status
    bool is_running() const;
    
private:
    // Subsystems
    std::unique_ptr tcp_server_;
    std::unique_ptr udp_broadcaster_;
    std::unique_ptr heartbeat_manager_;
    
    std::unique_ptr command_processor_;
    std::unique_ptr camera_controller_;
    std::unique_ptr gimbal_;
    
    // State
    std::atomic running_;
    std::mutex state_mutex_;
    
    // Configuration
    Config config_;
    
    // Threads
    std::thread tcp_thread_;
    std::thread udp_thread_;
    std::thread command_thread_;
    
    // Private methods
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
// Document actual initialization
bool PayloadManager::initialize(const std::string& config_file) {
    // 1. Load configuration
    // 2. Initialize logger
    // 3. Initialize network subsystems
    // 4. Initialize camera
    // 5. Initialize gimbal
    // 6. Start threads
    // 7. Register signal handlers
}
```

**Main Event Loop**:
```cpp
// Document main loop
void PayloadManager::main_loop() {
    while (running_) {
        // 1. Check heartbeat status
        // 2. Monitor system health
        // 3. Handle periodic tasks
        // 4. Sleep for interval
    }
}
```

**Shutdown Sequence**:
```cpp
// Document shutdown
void PayloadManager::shutdown() {
    // 1. Stop accepting new commands
    // 2. Complete in-flight operations
    // 3. Stop threads (join)
    // 4. Release camera/gimbal
    // 5. Close network connections
    // 6. Flush logs
}
```

---

### 4.2 main.cpp (Entry Point)

**File**: `src/main.cpp`

**Purpose**: Application entry point and command-line interface

**Responsibilities**:
- Parse command-line arguments
- Daemonize (if requested)
- Create PayloadManager instance
- Handle top-level exceptions

**Structure**:
```cpp
// Document actual main()
int main(int argc, char* argv[]) {
    // 1. Parse arguments
    // 2. Setup logging
    // 3. Create PayloadManager
    // 4. Initialize
    // 5. Run
    // 6. Cleanup
    // 7. Exit
}
```

**Command-Line Options**:
```bash
./payload_manager [options]

Options:
  -c, --config     Configuration file path
  -d, --daemon           Run as daemon
  -v, --verbose          Verbose logging
  -h, --help             Show help message
  --version              Show version information
```

---

## 5. Network Layer

### 5.1 Architecture
```
┌─────────────────────────────────────────────────────┐
│              Network Layer Architecture             │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │         TCP Server (Port 5000)              │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Listen Thread                       │   │   │
│  │  │  - Accept connections                │   │   │
│  │  │  - Spawn handler threads             │   │   │
│  │  └──────────────┬───────────────────────┘   │   │
│  │                 │                            │   │
│  │  ┌──────────────▼───────────────────────┐   │   │
│  │  │  Connection Handler Threads          │   │   │
│  │  │  - Receive commands                  │   │   │
│  │  │  - Parse JSON                        │   │   │
│  │  │  - Send responses                    │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │      UDP Broadcaster (Port 5001)            │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Broadcast Thread                    │   │   │
│  │  │  - Collect status @ 5Hz              │   │   │
│  │  │  - Build JSON                        │   │   │
│  │  │  - Send UDP broadcast                │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │     Heartbeat Manager (Port 5002)           │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Send Thread (1Hz outbound)          │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Receive Thread (monitor incoming)   │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Timeout Monitor                     │   │   │
│  │  │  - Detect disconnection              │   │   │
│  │  │  - Trigger reconnection              │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 5.2 TcpServer Class

**File**: `src/network/tcp_server.cpp`, `include/network/tcp_server.hpp`

**Purpose**: Handle TCP command connections from ground station

**Class Definition**:
```cpp
// Document actual class
class TcpServer {
public:
    TcpServer(uint16_t port);
    ~TcpServer();
    
    // Lifecycle
    bool start();
    void stop();
    bool is_running() const;
    
    // Connection handling
    void set_command_handler(
        std::function handler
    );
    
private:
    // Socket
    int server_fd_;
    uint16_t port_;
    
    // Threading
    std::thread accept_thread_;
    std::atomic running_;
    
    // Connection handlers
    std::vector handler_threads_;
    std::mutex handlers_mutex_;
    
    // Callback
    std::function command_handler_;
    
    // Private methods
    void accept_loop();
    void handle_connection(int client_fd);
    std::string receive_message(int fd);
    void send_response(int fd, const std::string& response);
};
```

**Implementation Details**:

**Socket Setup**:
```cpp
// Document actual implementation
bool TcpServer::start() {
    // 1. Create socket (AF_INET, SOCK_STREAM)
    // 2. Set SO_REUSEADDR
    // 3. Bind to port
    // 4. Listen (backlog = 10)
    // 5. Start accept thread
}
```

**Accept Loop**:
```cpp
// Document actual accept loop
void TcpServer::accept_loop() {
    while (running_) {
        // 1. Accept connection (blocking with timeout)
        // 2. Spawn handler thread
        // 3. Add to handler list
    }
}
```

**Message Protocol**:
- **Format**: Length-prefixed JSON
- **Length**: 4 bytes (uint32_t, network byte order)
- **Payload**: UTF-8 JSON string
```cpp
// Receive format
uint32_t length;
recv(fd, &length, 4, MSG_WAITALL);
length = ntohl(length);  // Network to host byte order

std::vector buffer(length);
recv(fd, buffer.data(), length, MSG_WAITALL);

std::string json_str(buffer.begin(), buffer.end());
```

**Error Handling**:
- Connection timeout: 30 seconds
- Receive timeout: 5 seconds
- Socket errors: Log and close connection
- Malformed JSON: Send error response

---

### 5.3 UdpBroadcaster Class

**File**: `src/network/udp_broadcaster.cpp`, `include/network/udp_broadcaster.hpp`

**Purpose**: Broadcast status updates to ground station

**Class Definition**:
```cpp
// Document actual class
class UdpBroadcaster {
public:
    UdpBroadcaster(uint16_t port, const std::string& target_ip);
    ~UdpBroadcaster();
    
    // Lifecycle
    bool start();
    void stop();
    
    // Status updates
    void set_status_provider(
        std::function provider
    );
    
private:
    int socket_fd_;
    uint16_t port_;
    std::string target_ip_;
    
    std::thread broadcast_thread_;
    std::atomic running_;
    
    std::function status_provider_;
    
    void broadcast_loop();
    void send_status(const std::string& status);
};
```

**Broadcast Frequency**: 5 Hz (200ms interval)

**Implementation**:
```cpp
// Document broadcast loop
void UdpBroadcaster::broadcast_loop() {
    using namespace std::chrono;
    auto next_broadcast = steady_clock::now();
    
    while (running_) {
        // 1. Get status from provider
        std::string status = status_provider_();
        
        // 2. Send UDP packet
        send_status(status);
        
        // 3. Sleep until next broadcast (200ms)
        next_broadcast += milliseconds(200);
        std::this_thread::sleep_until(next_broadcast);
    }
}
```

---

### 5.4 HeartbeatManager Class

**File**: `src/network/heartbeat_manager.cpp`, `include/network/heartbeat_manager.hpp`

**Purpose**: Monitor connection health via heartbeat

[Document heartbeat implementation in detail...]

---

## 6. Camera Integration

### 6.1 Sony SDK Integration

**SDK Version**: Sony Camera Remote SDK v2.00.00

**Files**: 
- `src/camera/sony_camera.cpp`
- `include/camera/sony_camera.hpp`

**Purpose**: Low-level Sony SDK wrapper

[Document Sony SDK integration in complete detail...]

### 6.2 CameraController Class

[Document high-level camera control...]

### 6.3 Content Management

[Document file download and storage...]

---

## 7. Gimbal Integration

### 7.1 Gimbal Interface

[Document gimbal abstraction...]

### 7.2 Gremsy Implementation

[Document Gremsy gSDK integration...]

### 7.3 SimpleBGC Implementation

[Document SimpleBGC API integration...]

---

## 8. Video Streaming

[Document RTSP streaming implementation if present...]

---

## 9. Protocol Implementation

### 9.1 Message Format

[Document JSON protocol in detail...]

### 9.2 Command Handling

[Document command processing...]

### 9.3 Status Generation

[Document status message construction...]

---

## 10. Threading Model

### 10.1 Thread Architecture

[Document threading in detail...]

### 10.2 Synchronization

[Document mutexes, condition variables, atomics...]

### 10.3 Thread Safety

[Document thread-safe patterns used...]

---

## 11. Memory Management

### 11.1 Smart Pointers

[Document use of unique_ptr, shared_ptr, weak_ptr...]

### 11.2 RAII Patterns

[Document RAII usage...]

### 11.3 Memory Leak Prevention

[Document strategies and tools (valgrind)...]

---

## 12. Error Handling

### 12.1 Exception Strategy

[Document exception handling approach...]

### 12.2 Error Codes

[Document error code system...]

### 12.3 Logging

[Document logging system...]

---

## 13. Configuration System

### 13.1 Configuration Files

[Document config file format...]

### 13.2 ConfigParser Class

[Document configuration parsing...]

---

## 14. Dependencies

### 14.1 System Dependencies
```bash
# Required packages
sudo apt install -y \
    build-essential \
    cmake \
    git \
    libboost-all-dev \
    libssl-dev \
    nlohmann-json3-dev \
    libudev-dev \
    libusb-1.0-0-dev
```

[Document all dependencies with versions and purposes...]

### 14.2 External Libraries

#### nlohmann-json
**Version**: 3.11.2+
**Purpose**: JSON parsing and generation
**Usage**: Message protocol, configuration

#### Sony Camera Remote SDK
**Version**: v2.00.00
**Purpose**: Camera control
**License**: Proprietary (http://www.sony.net/CameraRemoteSDK/)

[Continue for all dependencies...]

---

## 15. Build System

### 15.1 CMake Configuration

**Root CMakeLists.txt**:
```cmake
# Document actual CMake configuration
cmake_minimum_required(VERSION 3.16)
project(DPM_AirSide VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# [Document all CMake configuration]
```

### 15.2 Build Instructions
```bash
# Standard build
mkdir build && cd build
cmake ..
make -j$(nproc)

# Debug build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j$(nproc)

# Release build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

### 15.3 Build Targets

- `payload_manager` - Main executable
- `tests` - Test suite
- `install` - Install to system

---

## 16. Testing

### 16.1 Test Structure

[Document test organization...]

### 16.2 Unit Tests

[Document unit testing approach...]

### 16.3 Integration Tests

[Document integration testing...]

---

## 17. Code Conventions

### 17.1 C++ Style Guide

**Based on**: [Google C++ Style Guide / Custom conventions]

**Indentation**: 4 spaces (no tabs)

**Braces**: Attached style
```cpp
void function() {
    if (condition) {
        // code
    }
}
```

**Naming Conventions**:
- Classes: `PascalCase`
- Functions: `snake_case()`
- Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Member variables: `trailing_underscore_`

**Header Guards**: `#pragma once`

**includes**: 
```cpp
// Standard library
#include 
#include 

// Third-party
#include <nlohmann/json.hpp>

// Project headers
#include "network/tcp_server.hpp"
```

---

## 18. Deployment

### 18.1 Installation

[Document deployment process...]

### 18.2 Systemd Service

[Document service configuration...]

### 18.3 Auto-Start

[Document auto-start setup...]

---

## 19. Performance Optimization

### 19.1 Profiling

[Document profiling tools and results...]

### 19.2 Optimization Strategies

[Document optimizations made...]

---

## 20. Known Issues & Technical Debt

### 20.1 Current Limitations

[Document known issues...]

### 20.2 Technical Debt

[Document areas needing refactoring...]

---

## 21. Future Roadmap

### 21.1 Planned Features

[Document future plans...]

### 21.2 Refactoring Plans

[Document planned improvements...]

---

**Document End**

🔍 Step-by-Step Analysis Process
Step 1: Initial Project Scan (30 min)
bash# Run these commands in sbc/ directory

# 1. Count files
find ./src -name "*.cpp" | wc -l
find ./include -name "*.hpp" | wc -l

# 2. List all source files
find ./src -name "*.cpp" | sort

# 3. List all header files
find ./include -name "*.hpp" | sort

# 4. Check CMake files
find . -name "CMakeLists.txt"

# 5. Check for documentation
ls -la docs/

# 6. Check for scripts
ls -la scripts/

# 7. Check external dependencies
ls -la external/
Step 2: Analyze CMake Build System (30 min)
bash# Read and document:
# 1. Root CMakeLists.txt - project config
# 2. tests/CMakeLists.txt - test config (if exists)
# 3. Document all targets
# 4. Document all dependencies
# 5. Document compiler flags
# 6. Document install rules
Step 3: Analyze Main Entry Point (20 min)
bash# Read src/main.cpp
# Document:
# 1. Command-line argument parsing
# 2. Initialization sequence
# 3. Signal handling
# 4. Main loop
# 5. Cleanup/shutdown
Step 4: Analyze Core Components (60 min)
For each major class (PayloadManager, NetworkClient, CameraController, etc.):

Open .hpp and .cpp files
Document class purpose and responsibilities
Document all public methods with signatures
Document private members (state)
Document dependencies (what it uses)
Document usage (what uses it)
Include key code snippets
Document threading model (if threaded)

Step 5: Analyze Network Layer (45 min)

Document TcpServer implementation
Document UdpBroadcaster implementation
Document HeartbeatManager implementation
Document message format
Document error handling
Create sequence diagrams (textual)

Step 6: Analyze Camera Integration (60 min)

Document Sony SDK usage patterns
Document callback handling
Document error handling
Document resource management
Document threading (if used)
Document state management

Step 7: Analyze Protocol Implementation (45 min)

Document message parsing
Document command dispatching
Document status building
Document JSON schema
Include example messages

Step 8: Analyze Memory Management (30 min)

Document smart pointer usage
Document RAII patterns
Document potential leak points
Document memory testing (valgrind)

Step 9: Analyze Threading (45 min)

Document all threads and their purposes
Document synchronization primitives
Document thread-safe patterns
Document potential race conditions
Create threading diagram

Step 10: Create Diagrams (45 min)
Create ASCII/textual diagrams for:

Overall architecture
Class relationships
Thread architecture
Data flow (commands and status)
Network protocol
Module dependencies

Step 11: Document Dependencies (30 min)

List all system packages required
List all external libraries
Document versions
Document purpose of each dependency
Document installation process

Step 12: Document Build System (30 min)

Document CMake configuration
Document build commands
Document build targets
Document cross-compilation (if used)
Document toolchain

Step 13: Document Deployment (20 min)

Document installation process
Document systemd service (if used)
Document configuration files
Document startup process

Step 14: Review and Polish (30 min)

Review entire document for completeness
Add cross-references between sections
Verify all code examples are accurate
Check formatting consistency
Add any missing technical details


✅ Completion Checklist
Content Completeness

 Project structure fully documented
 All classes documented (main ones in detail)
 Network layer completely documented
 Camera integration documented
 Gimbal integration documented (if implemented)
 Video streaming documented (if implemented)
 Protocol completely documented
 Threading model documented
 Memory management patterns documented
 All dependencies listed
 Build system documented
 Deployment process documented

Technical Accuracy

 All code examples are from actual codebase
 All class signatures are accurate
 All diagrams are correct
 All dependencies verified
 Build instructions tested

Documentation Quality

 All sections complete (no placeholders)
 Cross-references added
 Table of contents complete
 Formatting consistent
 Technical terms defined
 Readable by new C++ developers

Supplementary Documentation

 Create CLASS_REFERENCE.md if needed
 Create THREADING_MODEL.md if complex
 Create NETWORK_PROTOCOL.md if detailed
 Create SONY_SDK_INTEGRATION.md if helpful

Files Created

 sbc/docs/SBC_ARCHITECTURE.md created
 Any supplementary docs created
 Git commit: [DOCS] Complete Air-Side architecture documentation


📝 Git Workflow
bash# 1. Start documentation task
cd sbc
git checkout -b docs/sbc-architecture

# 2. Create docs directory if needed
mkdir -p docs

# 3. Generate documentation
# (Follow analysis process)

# 4. Review
cat docs/SBC_ARCHITECTURE.md

# 5. Commit
git add docs/
git commit -m "[DOCS] Complete Air-Side (SBC) architecture documentation

- Document entire C++ project structure
- Document all core classes and modules
- Document network layer implementation
- Document Sony SDK integration
- Document gimbal integration (if present)
- Document threading and concurrency model
- Document memory management patterns
- Document protocol implementation
- Document build system and dependencies
- Add architecture diagrams
- Include actual code examples from codebase"

# 6. Push (if using PR workflow)
git push origin docs/sbc-architecture
```

---

## 🎯 Success Criteria

### Documentation Must:
- ✅ Cover 100% of existing C++ codebase
- ✅ Include actual code examples (not pseudo-code)
- ✅ Include clear architecture diagrams
- ✅ Be technically accurate
- ✅ Document threading model clearly
- ✅ Document memory management patterns
- ✅ Explain Sony SDK integration
- ✅ Document build system completely
- ✅ Serve as onboarding guide for C++ developers
- ✅ Serve as reference for debugging/maintenance
- ✅ Be maintainable (easy to update as code evolves)

### Documentation Quality:
- Professional technical writing (C++ focus)
- Consistent formatting
- Clear and precise
- Assumes C++17 knowledge but explains project-specific patterns
- Complete but focused
- Practical for actual development

---

## 🚀 Getting Started

### For Claude Code (Air-Side):

1. **Read this entire instruction document**
2. **Read existing documentation**:
   - `sbc/docs/PROGRESS_AND_TODO.md`
   - `sbc/README.md` (if exists)
3. **Start with Step 1: Initial Project Scan**
4. **Follow analysis process sequentially**
5. **Use template structure provided**
6. **Fill in with actual implementation details**
7. **Test build instructions as you document them**
8. **Review and polish**
9. **Follow Git workflow**

### Expected Output:
```
sbc/docs/
├── SBC_ARCHITECTURE.md (primary, 5000-10000 lines)
├── CLASS_REFERENCE.md (optional, if needed)
├── THREADING_MODEL.md (optional, if complex)
└── SONY_SDK_INTEGRATION.md (optional, if helpful)
Time Estimate:

Analysis: 3-4 hours
Documentation writing: 3-4 hours
Testing build instructions: 30 min
Review and polish: 1 hour
Total: 7-9 hours


💡 Tips for Claude Code (C++ Focus)

Be thorough with C++ details:

Document smart pointer usage
Document RAII patterns
Document move semantics
Document const correctness


Document threading carefully:

All mutex usage
All atomic operations
Thread lifecycle
Potential race conditions


Memory management is critical:

Document ownership semantics
Document resource lifecycle
Document leak prevention strategies
Note valgrind testing


Include actual code:

Real class definitions
Real function signatures
Real CMake snippets
Don't paraphrase C++ code


Build system matters:

Document CMake completely
Test build instructions
Document cross-compilation if used
Document toolchain requirements


Sony SDK is complex:

Document callback patterns
Document SDK object lifecycle
Document error handling
Document threading requirements


Network code is critical:

Document socket handling
Document error conditions
Document timeout handling
Document reconnection logic




📞 Key Questions to Answer
As you document, answer these questions:
Architecture Questions

Why C++17 specifically?
What are the main architectural patterns?
How is concurrency handled?
What are the performance requirements?
How is real-time behavior achieved?

Component Questions

What is each class responsible for?
How do components communicate?
What are the threading boundaries?
Where are the synchronization points?

Sony SDK Questions

How is the SDK initialized?
How are callbacks handled?
How is threading managed?
How are errors propagated?
How is cleanup performed?

Network Questions

How is TCP handled?
How is UDP handled?
How are disconnections detected?
How is reconnection handled?
What are the timeout values?

Memory Management Questions

What smart pointers are used where?
How is ownership transferred?
Are there any raw pointers? Why?
How are leaks prevented?
How is memory tested?

Build System Questions

What are the CMake targets?
What are the dependencies?
How is cross-compilation done?
What compiler flags are used?
How are tests built?