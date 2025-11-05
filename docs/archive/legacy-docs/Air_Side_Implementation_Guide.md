# Air Side (Raspberry Pi) Implementation Guide
## Payload Manager Service for DPM Android App Communication

**Version:** 1.0
**Date:** October 22, 2025
**Purpose:** Complete specification for Claude Code to generate the Raspberry Pi service in C++

---

## Overview

This document provides all necessary information for implementing the Air Side service that runs on the Raspberry Pi to communicate with the DPM Android app running on the H16 Ground Station.

**Implementation Language:** C++17 or later
**Sony Camera SDK:** 100% C++ native implementation CrSDK_v2.00.00_20250805a_Linux64ARMv8
**Sony Camera SDK: reference** CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00
**Sony Camera SDL: reference code** CrSDK_v2.00.00_20250805a_Linux64ARMv8/app
MUST reed references and example code, any knowledge from this reference and example code must override any suggestions below.
MUST reed CrSDK_v2.00.00_20250805a_Linux64ARMv8/README.md
MUST develop build plan and confirm with me before starting any code implementation.

**User Account:** dpm

### System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Raspberry Pi Service                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Payload Manager Service (C++)              │     │
│  │                                                     │     │
│  │  • TCP Server (5000) - Commands                   │     │
│  │  • UDP Broadcaster (5001) - Status Updates        │     │
│  │  • UDP Heartbeat (5002) - Keep-Alive              │     │
│  └────────────────────────────────────────────────────┘     │
│                          ↕                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Sony Camera SDK Interface (C++)            │     │
│  │  • Sony Remote Camera API                          │     │
│  │  • Camera property control                         │     │
│  │  • Image capture                                   │     │
│  │  • Status monitoring                               │     │
│  └────────────────────────────────────────────────────┘     │
│                          ↕                                    │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Gimbal Controller (optional)               │     │
│  │  • Gremsy SDK / MAVLink                            │     │
│  │  • Gimbal angle control                            │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## Network Configuration

### Static IP Configuration

Create `/etc/network/interfaces.d/eth0`:

```bash
auto eth0
iface eth0 inet static
    address 192.168.144.20
    netmask 255.255.255.0
    gateway 192.168.144.1
    dns-nameservers 8.8.8.8 8.8.4.4
```

Or using `nmcli`:

```bash
nmcli con add type ethernet con-name eth0 ifname eth0
nmcli con modify eth0 ipv4.addresses 192.168.144.20/24
nmcli con modify eth0 ipv4.gateway 192.168.144.1
nmcli con modify eth0 ipv4.dns "8.8.8.8 8.8.4.4"
nmcli con modify eth0 ipv4.method manual
nmcli con up eth0
```

### Firewall Configuration

```bash
# Allow incoming connections on required ports
sudo ufw allow 5000/tcp comment 'DPM Command Server'
sudo ufw allow 5001/udp comment 'DPM Status Broadcast'
sudo ufw allow 5002/udp comment 'DPM Heartbeat'
sudo ufw enable
```

---

## Protocol Implementation

### Required Message Types

The service must implement the following message types according to the Command Protocol Specification v1.0:

1. **Handshake Messages** (TCP)
   - Receive handshake from ground
   - Respond with capabilities

2. **Command Messages** (TCP)
   - `camera.set_property`
   - `camera.capture`
   - `camera.get_properties`
   - `camera.record`
   - `gimbal.set_angle` (optional)
   - `system.get_status`

3. **Response Messages** (TCP)
   - Success/error responses for all commands
   - Must match sequence_id from command

4. **Status Messages** (UDP broadcast)
   - Broadcast at 5 Hz (200ms interval)
   - Include system, camera, gimbal status

5. **Heartbeat Messages** (UDP bidirectional)
   - Send/receive at 1 Hz (1000ms interval)
   - Detect connection loss

### Message Format

All messages use JSON format as defined in `Command_Protocol_Specification_v1.0.md`.

**Base Message Structure:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command|status|heartbeat|response",
  "sequence_id": 12345,
  "timestamp": 1729339200,
  "payload": {
    // Message-specific content
  }
}
```

---

## C++ Project Structure

### Recommended Project Layout

```
/home/dpm/payload_manager/
├── CMakeLists.txt             # Build configuration
├── README.md                  # Project documentation
├── src/
│   ├── main.cpp              # Entry point
│   ├── config.h              # Configuration constants
│   ├── protocol/
│   │   ├── tcp_server.h
│   │   ├── tcp_server.cpp    # TCP command server
│   │   ├── udp_broadcaster.h
│   │   ├── udp_broadcaster.cpp  # UDP status broadcaster
│   │   ├── heartbeat.h
│   │   ├── heartbeat.cpp     # Heartbeat handler
│   │   ├── messages.h        # Message structures
│   │   └── json_parser.cpp   # JSON parsing (nlohmann/json)
│   ├── camera/
│   │   ├── sony_camera.h
│   │   ├── sony_camera.cpp   # Sony Camera SDK interface
│   │   ├── camera_state.h
│   │   └── camera_state.cpp  # Camera state management
│   ├── gimbal/
│   │   ├── gimbal_interface.h
│   │   └── gimbal_interface.cpp  # Gimbal control (optional)
│   └── utils/
│       ├── logger.h
│       ├── logger.cpp         # Logging utilities
│       └── system_info.cpp    # System status (CPU, memory, etc.)
├── include/
│   └── sony_camera_sdk/      # Sony Camera SDK headers
├── lib/
│   └── libsonycamera.so      # Sony Camera SDK library
└── build/                     # CMake build directory
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.16)
project(PayloadManager VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Threads REQUIRED)
find_package(nlohmann_json 3.10.0 REQUIRED)  # JSON library

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/include/sony_camera_sdk
)

# Source files
set(SOURCES
    src/main.cpp
    src/protocol/tcp_server.cpp
    src/protocol/udp_broadcaster.cpp
    src/protocol/heartbeat.cpp
    src/protocol/json_parser.cpp
    src/camera/sony_camera.cpp
    src/camera/camera_state.cpp
    src/utils/logger.cpp
    src/utils/system_info.cpp
)

# Executable
add_executable(payload_manager ${SOURCES})

# Link libraries
target_link_libraries(payload_manager
    Threads::Threads
    nlohmann_json::nlohmann_json
    ${CMAKE_SOURCE_DIR}/lib/libsonycamera.so  # Sony SDK
    stdc++fs  # Filesystem library
)

# Install target
install(TARGETS payload_manager DESTINATION /usr/local/bin)
```

---

## Dependencies

### Required Libraries

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install build tools
sudo apt-get install -y build-essential cmake git

# Install C++ JSON library (nlohmann/json)
sudo apt-get install -y nlohmann-json3-dev

# Install system libraries
sudo apt-get install -y libboost-system-dev libboost-thread-dev
```

### Sony Camera SDK

The Sony Camera Remote API SDK is 100% C++ native code.

**Installation:**
```bash
# Assuming SDK is provided as a library
sudo mkdir -p /home/dpm/payload_manager/include/sony_camera_sdk
sudo mkdir -p /home/dpm/payload_manager/lib

# Copy SDK headers
sudo cp -r /path/to/sony_sdk/include/* /home/dpm/payload_manager/include/sony_camera_sdk/

# Copy SDK library
sudo cp /path/to/sony_sdk/lib/libsonycamera.so /home/dpm/payload_manager/lib/
```

---

## Key Implementation Points

### 1. TCP Command Server (Port 5000)

**Requirements:**
- Multi-threaded client handling using std::thread or boost::asio
- JSON parsing and validation using nlohmann/json
- Command routing to appropriate handlers
- Response generation
- Error handling and logging
- Graceful shutdown

**Example Header (tcp_server.h):**
```cpp
#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#include <string>
#include <thread>
#include <vector>
#include <atomic>
#include <memory>

class TCPServer {
public:
    TCPServer(int port);
    ~TCPServer();

    void start();
    void stop();

private:
    void acceptConnections();
    void handleClient(int client_socket);
    void processCommand(const std::string& json_message, std::string& response);

    int server_socket_;
    int port_;
    std::atomic<bool> running_;
    std::vector<std::thread> client_threads_;
};

#endif
```

### 2. UDP Status Broadcaster (Port 5001)

**Requirements:**
- Periodic status gathering (5 Hz / 200ms interval)
- JSON status message generation
- UDP broadcast to 192.168.144.11:5001
- System stats (CPU, memory, storage)
- Camera status (battery, settings, remaining shots)
- Gimbal status (if connected)

**Status Message Example:**
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 54321,
  "timestamp": 1729339200,
  "payload": {
    "system": {
      "uptime_seconds": 3600,
      "cpu_usage_percent": 35.2,
      "memory_usage_percent": 42.8,
      "storage_free_gb": 85.3
    },
    "camera": {
      "connected": true,
      "model": "Sony A1",
      "battery_percent": 85,
      "recording": false,
      "current_settings": {
        "shutter_speed": "1/1000",
        "aperture": "F2.8",
        "iso": 400
      }
    }
  }
}
```

**Example Header (udp_broadcaster.h):**
```cpp
#ifndef UDP_BROADCASTER_H
#define UDP_BROADCASTER_H

#include <string>
#include <thread>
#include <atomic>

class UDPBroadcaster {
public:
    UDPBroadcaster(int port, const std::string& target_ip);
    ~UDPBroadcaster();

    void start();
    void stop();

private:
    void broadcastLoop();
    std::string gatherStatusJson();

    int socket_fd_;
    int port_;
    std::string target_ip_;
    std::atomic<bool> running_;
    std::thread broadcast_thread_;
    int sequence_id_;
};

#endif
```

### 3. Heartbeat Handler (Port 5002)

**Requirements:**
- Receive heartbeat from ground (UDP)
- Send heartbeat to ground (UDP)
- Track last received heartbeat time
- Log warnings if no heartbeat for 10 seconds

**Example Header (heartbeat.h):**
```cpp
#ifndef HEARTBEAT_H
#define HEARTBEAT_H

#include <string>
#include <thread>
#include <atomic>
#include <chrono>

class HeartbeatHandler {
public:
    HeartbeatHandler(int port, const std::string& target_ip);
    ~HeartbeatHandler();

    void start();
    void stop();

private:
    void sendLoop();
    void receiveLoop();

    int socket_fd_;
    int port_;
    std::string target_ip_;
    std::atomic<bool> running_;
    std::thread send_thread_;
    std::thread receive_thread_;
    std::chrono::steady_clock::time_point last_received_;
};

#endif
```

### 4. Sony Camera Interface

The camera interface provides a C++ wrapper around the Sony Camera SDK:

**Example Header (sony_camera.h):**
```cpp
#ifndef SONY_CAMERA_H
#define SONY_CAMERA_H

#include <string>
#include <map>

// Include Sony SDK headers
#include "sony_camera_sdk/camera_api.h"

class SonyCamera {
public:
    SonyCamera();
    ~SonyCamera();

    bool connect();
    void disconnect();

    bool setProperty(const std::string& property, const std::string& value);
    std::string getProperty(const std::string& property);

    bool captureImage(const std::string& mode = "single");
    bool startRecording();
    bool stopRecording();

    int getBatteryLevel();
    std::map<std::string, std::string> getStorageInfo();

    bool isConnected() const { return connected_; }
    std::string getModel() const { return camera_model_; }

private:
    bool connected_;
    std::string camera_model_;

    // Sony SDK objects
    void* camera_handle_;  // Actual SDK handle type
};

#endif
```

**Camera Property Mappings:**

| Protocol Property | Sony API Property | Notes |
|------------------|-------------------|-------|
| shutter_speed | ShutterSpeed | Format: "1/1000" or "2\"" |
| aperture | FNumber | Format: "F2.8" |
| iso | ISO | Integer: 100-51200 |
| white_balance | WhiteBalance | auto, daylight, cloudy, etc. |
| focus_mode | FocusMode | Manual, AF-S, AF-C |
| file_format | ImageFormat | JPEG, RAW, JPEG+RAW |

---

## JSON Parsing with nlohmann/json

### Example Usage

```cpp
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Parse incoming command
void TCPServer::processCommand(const std::string& json_str, std::string& response) {
    try {
        json command = json::parse(json_str);

        std::string message_type = command["message_type"];
        int sequence_id = command["sequence_id"];

        if (message_type == "command") {
            std::string cmd = command["payload"]["command"];

            if (cmd == "camera.set_property") {
                std::string property = command["payload"]["parameters"]["property"];
                std::string value = command["payload"]["parameters"]["value"];

                // Call camera interface
                bool success = camera_->setProperty(property, value);

                // Build response
                json resp = {
                    {"protocol_version", "1.0"},
                    {"message_type", "response"},
                    {"sequence_id", sequence_id},
                    {"timestamp", std::time(nullptr)},
                    {"payload", {
                        {"command", cmd},
                        {"status", success ? "success" : "error"},
                        {"result", {
                            {"property", property},
                            {"value", value},
                            {"confirmed", success}
                        }}
                    }}
                };

                response = resp.dump();
            }
        }
    } catch (const json::exception& e) {
        // Handle JSON parsing error
        Logger::error("JSON parse error: " + std::string(e.what()));
    }
}
```

---

## System Service Setup

### SystemD Service File

Create `/etc/systemd/system/payload-manager.service`:

```ini
[Unit]
Description=DPM Payload Manager Service
After=network.target

[Service]
Type=simple
User=dpm
WorkingDirectory=/home/dpm/payload_manager
ExecStart=/usr/local/bin/payload_manager
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryLimit=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable payload-manager.service
sudo systemctl start payload-manager.service
sudo systemctl status payload-manager.service
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u payload-manager.service -f

# Recent logs
sudo journalctl -u payload-manager.service -n 100

# Logs with timestamps
sudo journalctl -u payload-manager.service --since "1 hour ago"
```

---

## Error Handling

### Error Codes to Implement

```cpp
enum class ErrorCode {
    // Camera Errors (1000-1999)
    INVALID_CAMERA_PROPERTY = 1001,
    CAMERA_NOT_CONNECTED = 1002,
    CAMERA_BUSY = 1003,
    CAMERA_HARDWARE_ERROR = 1004,
    UNSUPPORTED_OPERATION = 1005,

    // Gimbal Errors (2000-2999)
    GIMBAL_NOT_CONNECTED = 2001,
    GIMBAL_COMM_ERROR = 2002,

    // Network Errors (3000-3999)
    NETWORK_TIMEOUT = 3001,
    MESSAGE_TOO_LARGE = 3002,

    // System Errors (4000-4999)
    INSUFFICIENT_STORAGE = 4001,
    FILE_NOT_FOUND = 4002,

    // Protocol Errors (5000-5999)
    INVALID_JSON = 5001,
    MISSING_FIELD = 5002,
    UNKNOWN_COMMAND = 5003,
    PROTOCOL_MISMATCH = 5004
};

std::string getErrorMessage(ErrorCode code) {
    switch (code) {
        case ErrorCode::INVALID_CAMERA_PROPERTY:
            return "Invalid camera property value";
        case ErrorCode::CAMERA_NOT_CONNECTED:
            return "Camera not connected";
        // ... more cases
        default:
            return "Unknown error";
    }
}
```

### Error Response Format

```cpp
json createErrorResponse(int sequence_id, const std::string& command,
                        ErrorCode error_code, const std::string& details = "") {
    return {
        {"protocol_version", "1.0"},
        {"message_type", "response"},
        {"sequence_id", sequence_id},
        {"timestamp", std::time(nullptr)},
        {"payload", {
            {"command", command},
            {"status", "error"},
            {"error", {
                {"code", static_cast<int>(error_code)},
                {"message", getErrorMessage(error_code)},
                {"details", details}
            }}
        }}
    };
}
```

---

## Logging Configuration

### Example Logger Class

```cpp
#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>
#include <mutex>
#include <sstream>
#include <ctime>

enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

class Logger {
public:
    static void init(const std::string& log_file);
    static void setLevel(LogLevel level);

    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warning(const std::string& message);
    static void error(const std::string& message);

private:
    static void log(LogLevel level, const std::string& message);
    static std::string levelToString(LogLevel level);
    static std::string getTimestamp();

    static std::ofstream log_file_;
    static std::mutex mutex_;
    static LogLevel min_level_;
};

#endif
```

**Usage:**
```cpp
Logger::init("/var/log/payload_manager.log");
Logger::setLevel(LogLevel::DEBUG);

Logger::info("Payload Manager starting...");
Logger::debug("TCP server listening on port 5000");
Logger::error("Failed to connect to camera: " + error_msg);
```

---

## Building the Project

### Build Commands

```bash
# Create build directory
cd /home/dpm/payload_manager
mkdir -p build
cd build

# Generate build files
cmake ..

# Compile
make -j4

# Install
sudo make install

# The executable will be installed to /usr/local/bin/payload_manager
```

### Cross-Compilation (Optional)

For cross-compiling on a development machine:

```bash
# Install cross-compiler
sudo apt-get install g++-arm-linux-gnueabihf

# Create toolchain file
cmake -DCMAKE_TOOLCHAIN_FILE=arm-toolchain.cmake ..
make -j4
```

---

## Testing Checklist

Before deploying, verify:

- [ ] TCP server accepts connections on port 5000
- [ ] Handshake exchange works correctly
- [ ] All command types are recognized
- [ ] Camera control commands work (set property, capture, etc.)
- [ ] Status broadcast sends messages at 5 Hz on port 5001
- [ ] Heartbeat is sent/received on port 5002
- [ ] Error responses include correct error codes
- [ ] Service auto-starts on boot
- [ ] Logging works correctly
- [ ] Graceful shutdown on SIGTERM
- [ ] Connection recovery after network interruption
- [ ] Memory usage remains under 512 MB
- [ ] CPU usage remains under 50%

---

## Performance Considerations

### Resource Usage

- **CPU:** Should use < 30% on average
- **Memory:** Should use < 256 MB
- **Network:** ~50 KB/s for status broadcast at 5 Hz

### Optimization Tips

1. Use thread pooling for TCP clients
2. Cache camera properties to reduce SDK calls
3. Implement message queuing for high-frequency commands
4. Use move semantics for large objects
5. Profile with `gprof` or `perf` to identify bottlenecks
6. Monitor system resources and log warnings

### C++ Best Practices

- Use RAII for resource management
- Prefer smart pointers (std::unique_ptr, std::shared_ptr)
- Use const references to avoid copies
- Use std::move for large objects
- Avoid unnecessary allocations in hot paths
- Use std::string_view for string parameters when not storing

---

## Security Considerations

### Network Security

```cpp
// Restrict connections to known IP
const std::vector<std::string> ALLOWED_IPS = {"192.168.144.11"};

bool validateClientIP(const std::string& client_ip) {
    return std::find(ALLOWED_IPS.begin(), ALLOWED_IPS.end(), client_ip)
           != ALLOWED_IPS.end();
}
```

### Input Validation

- Validate all JSON messages
- Check sequence_id ranges
- Validate property values before sending to camera
- Sanitize file paths
- Rate limit commands to prevent DoS

---

## Initial Implementation Priorities

### Phase 1: Basic Connectivity (MVP)
1. TCP server accepting connections
2. Handshake exchange
3. Basic status broadcast (system info only)
4. Heartbeat send/receive
5. Simple logging

### Phase 2: Camera Control
1. Camera connection detection
2. Get camera properties command
3. Set camera property command
4. Capture image command
5. Camera status in broadcast

### Phase 3: Advanced Features
1. Video recording control
2. Content download
3. Gimbal control (if available)
4. Advanced error handling
5. Performance optimization

---

## Example Main Entry Point

```cpp
#include <iostream>
#include <csignal>
#include <memory>

#include "protocol/tcp_server.h"
#include "protocol/udp_broadcaster.h"
#include "protocol/heartbeat.h"
#include "camera/sony_camera.h"
#include "utils/logger.h"

// Global pointers for signal handler
std::unique_ptr<TCPServer> tcp_server;
std::unique_ptr<UDPBroadcaster> udp_broadcaster;
std::unique_ptr<HeartbeatHandler> heartbeat;
std::unique_ptr<SonyCamera> camera;

void signalHandler(int signum) {
    Logger::info("Received shutdown signal: " + std::to_string(signum));

    if (tcp_server) tcp_server->stop();
    if (udp_broadcaster) udp_broadcaster->stop();
    if (heartbeat) heartbeat->stop();
    if (camera) camera->disconnect();

    Logger::info("Payload Manager Service stopped");
    exit(0);
}

int main(int argc, char* argv[]) {
    // Initialize logger
    Logger::init("/var/log/payload_manager.log");
    Logger::setLevel(LogLevel::INFO);
    Logger::info("=== Payload Manager Service Starting ===");

    // Setup signal handlers
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    try {
        // Create components
        tcp_server = std::make_unique<TCPServer>(5000);
        udp_broadcaster = std::make_unique<UDPBroadcaster>(5001, "192.168.144.11");
        heartbeat = std::make_unique<HeartbeatHandler>(5002, "192.168.144.11");
        camera = std::make_unique<SonyCamera>();

        // Start TCP server
        Logger::info("Starting TCP command server on port 5000");
        tcp_server->start();

        // Start UDP broadcaster
        Logger::info("Starting UDP status broadcaster on port 5001");
        udp_broadcaster->start();

        // Start heartbeat
        Logger::info("Starting heartbeat handler on port 5002");
        heartbeat->start();

        // Connect to camera
        Logger::info("Connecting to Sony camera...");
        if (camera->connect()) {
            Logger::info("Camera connected: " + camera->getModel());
        } else {
            Logger::warning("Camera not connected - will retry in background");
        }

        Logger::info("=== Payload Manager Service Running ===");

        // Main loop - keep running
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

    } catch (const std::exception& e) {
        Logger::error("Fatal error: " + std::string(e.what()));
        return 1;
    }

    return 0;
}
```

---

## Next Steps

When implementing the Air Side service:

1. Review this guide and the Command Protocol Specification v1.0
2. Set up the development environment on Raspberry Pi
3. Install C++ build tools and dependencies
4. Integrate Sony Camera SDK (100% C++)
5. Implement Phase 1 (Basic Connectivity) first
6. Test connectivity with the Android app
7. Incrementally add Phase 2 and Phase 3 features
8. Document any deviations or extensions to the protocol

---

**Document Status:** Complete ✅
**Ready for:** C++ Implementation
**Protocol Version:** 1.0
**User Account:** dpm
**Last Updated:** October 22, 2025
