# Drone Payload Manager - Project Summary & Action Plan (C++ VERSION)

**Date:** October 24, 2025  
**Status:** âœ… Ready to Begin Development  
**Air-Side Language:** ðŸ"¥ **STRICTLY C++** ðŸ"¥

---

## ðŸŽ¯ Project Overview

**Goal:** Create a professional UAV payload management system for Sony camera control via SkyDroid H16 Pro ground control station.

**Architecture:** 
- **Air Side:** Raspberry Pi 4 + Sony Camera + Gimbal (**C++ ONLY**)
- **Ground Side:** SkyDroid H16 Ground Station (Android-based, Kotlin/Java)
- **Link:** H16 R16 digital data-link (up to 10km, low latency)

---

## ðŸ"š Complete Documentation Package

| Document | Purpose | Status |
|----------|---------|--------|
| **Drone_Payload_Manager_Phase1_Scope.md** | Complete project scope | âœ… Final |
| **Phase1_Requirements_Update.md** | Confirmed requirements | âœ… Final |
| **Phase1_Quick_Reference.md** | One-page checklist | âœ… Final |
| **Updated_System_Architecture_H16.md** | H16 system architecture | âœ… Final |
| **Architecture_Comparison_H16.md** | H16 vs generic comparison | âœ… Final |
| **Phase1_Technical_Addendum_Sony_SDK.md** | Sony SDK technical details | âœ… Final |
| **Command_Protocol_Specification_v1.0.md** | Complete protocol spec | âœ… Final |
| **Protocol_Implementation_Quick_Start.md** | Step-by-step implementation | âœ… Final |

---

## âœ… Phase 1 Confirmed Scope

### Included Features:
- âœ… Camera exposure control (Shutter, Aperture, ISO)
- âœ… Focus control (Mode, Manual, Area selection)
- âœ… White balance (Presets, Manual temperature)
- âœ… File format selection (JPEG, RAW, JPEG+RAW)
- âœ… Capture modes (Still, Video, Burst)
- âœ… Camera status monitoring
- âœ… Content download (Images & videos to SBC)
- âœ… Storage management (Auto-cleanup, monitoring)
- âœ… Gimbal control (Gremsy & SimpleBGC)
- âœ… Dual control (Android app + Mavlink/GCS)
- âœ… USB/Ethernet/WiFi camera connectivity

### Video Strategy:
- **Primary:** Camera HDMI â†' R16 Air Unit (low latency)
- **Secondary:** Sony SDK live view (GCS preview)

### Deferred to Later Phases:
- âŒ Picture profiles / color modes â†' Phase 3
- âŒ Firmware updates â†' Phase 2
- âŒ Multiple cameras â†' Phase 2
- âŒ Gimbal calibration â†' Future

---

## ðŸ—ï¸ System Architecture Summary

```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€ AIR SIDE (C++) â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚                                           â"‚
â"‚  [Sony Camera] â†USB/HDMIâ†' [Raspberry Pi] â"‚
â"‚                              â†"            â"‚
â"‚                    [C++ Payload Manager]  â"‚
â"‚                    - Sony SDK (C++)       â"‚
â"‚                    - Network (TCP/UDP)    â"‚
â"‚                    - Gimbal Control       â"‚
â"‚                              â†"            â"‚
â"‚                          [R16 Air Unit]   â"‚
â"‚                              â†"            â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
                               â"‚
                    â•â•â• Digital Link â•â•â•
                               â"‚
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€ GROUND SIDE â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚                               â†"           â"‚
â"‚                      [H16 Ground Station] â"‚
â"‚                      (Built-in Android)   â"‚
â"‚                      - Video display      â"‚
â"‚                      - Custom app         â"‚
â"‚                      - Controls           â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

**Network:** 192.168.144.x (H16 internal network)  
**Pi Address:** 192.168.144.20:5000 (TCP), :5001 (UDP)  
**H16 Address:** 192.168.144.11

---

## ðŸ"Œ Command Protocol Summary

### Transport:
- **TCP (Port 5000):** Commands (Ground â†' Air)
- **UDP (Port 5001):** Status (Air â†' Ground, 5 Hz)
- **UDP (Port 5002):** Heartbeat (Bidirectional, 1 Hz)

### Format:
- **Encoding:** JSON (UTF-8)
- **Structure:** 
  ```json
  {
    "protocol_version": "1.0",
    "message_type": "command|status|response|heartbeat",
    "sequence_id": 12345,
    "timestamp": 1729339200,
    "payload": { /* message-specific content */ }
  }
  ```

### Key Commands:
- `camera.set_property` - Set camera parameters
- `camera.capture` - Capture image
- `camera.record` - Video recording control
- `camera.focus` - Manual focus control
- `camera.set_focus_area` - Focus area selection
- `gimbal.set_angle` - Gimbal position
- `gimbal.set_mode` - Gimbal mode (follow/lock/home)
- `content.list` - List camera content
- `content.download` - Download to SBC

---

## ðŸ"… Development Timeline: 17 Weeks

### Weeks 1-3: Core Infrastructure â­ **START HERE**
**Focus:** Protocol + Basic Camera Control (C++)

**Week 1:**
- âœ… **Task 1.1:** Implement TCP command server on Pi (C++)
- âœ… **Task 1.2:** Implement TCP client in Android app
- âœ… **Task 1.3:** Test basic command/response
- ðŸ"¦ **Deliverable:** Working TCP communication

**Week 2:**
- âœ… **Task 2.1:** Add UDP status broadcaster on Pi (C++)
- âœ… **Task 2.2:** Add UDP receiver in Android app
- âœ… **Task 2.3:** Implement heartbeat system
- ðŸ"¦ **Deliverable:** Real-time status updates

**Week 3:**
- âœ… **Task 3.1:** Integrate Sony Camera SDK on Pi (C++)
- âœ… **Task 3.2:** Implement camera property commands
- âœ… **Task 3.3:** Add camera control UI to Android
- ðŸ"¦ **Deliverable:** Basic camera control working

### Weeks 4-6: Mavlink Integration
- Mavlink message handlers (C++)
- Camera control via GCS
- Status broadcasting to GCS
- Integration with Ardupilot

### Weeks 7-10: Android App Development
- Complete camera control UI
- White balance, focus area, file format controls
- Status display
- Download management UI
- Settings screen

### Weeks 11-12: Gimbal Integration
- Gremsy gSDK integration (C++)
- SimpleBGC Serial API integration (C++)
- Unified gimbal interface
- Gimbal control UI

### Weeks 13-15: Integration & Testing
- Full system integration
- Hardware-in-loop testing
- Performance optimization
- Bug fixes

### Weeks 16-17: Documentation & Deployment
- User manuals
- Deployment procedures
- Training materials
- Final testing

---

## ðŸŽ¬ Immediate Action Plan

### âœ¨ TASK 1: Protocol Implementation (This Week!)

**Day 1-2: Pi TCP Server (C++)**
```bash
# On Raspberry Pi
cd ~
mkdir -p payload_manager/src
cd payload_manager

# Create CMakeLists.txt
nano CMakeLists.txt
# Copy CMake configuration (see below)

# Create main server file
nano src/payload_server.cpp
# Copy C++ server code (see below)

# Build it
mkdir build && cd build
cmake ..
make -j4

# Test it
./payload_server

# Test from another terminal
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"test","parameters":{}}}' | nc localhost 5000
```

**CMakeLists.txt Template:**
```cmake
cmake_minimum_required(VERSION 3.16)
project(PayloadManager VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(nlohmann_json 3.2.0 REQUIRED)
find_package(Threads REQUIRED)

# Add Sony SDK include directories
include_directories(${CMAKE_SOURCE_DIR}/sony_sdk/include)

# Source files
set(SOURCES
    src/payload_server.cpp
    src/network/tcp_server.cpp
    src/network/udp_broadcaster.cpp
    src/protocol/message_handler.cpp
    src/camera/sony_camera.cpp
    src/gimbal/gimbal_interface.cpp
)

# Main executable
add_executable(payload_server ${SOURCES})

# Link libraries
target_link_libraries(payload_server
    PRIVATE
    nlohmann_json::nlohmann_json
    Threads::Threads
    ${CMAKE_SOURCE_DIR}/sony_sdk/lib/libCrImageDataBlock.so
    ${CMAKE_SOURCE_DIR}/sony_sdk/lib/libCrAdapter.so
)

# Install rules
install(TARGETS payload_server DESTINATION /usr/local/bin)
```

**Day 3-4: Android App**
```bash
# On development machine
# 1. Open Android Studio
# 2. Create new project: "PayloadManager"
# 3. Add dependencies to build.gradle:
#    - com.google.code.gson:gson:2.10.1
#    - kotlinx-coroutines-android:1.7.3
# 4. Copy NetworkClient.kt from Quick Start guide
# 5. Create MainActivity with connect/test buttons
# 6. Test connection to Pi
```

**Day 5: Integration Test**
- C++ server running on Pi
- Android app connects
- Send test commands
- Verify responses
- âœ… Celebrate working protocol! ðŸŽ‰

---

## ðŸ› ï¸ Development Environment Setup

### Raspberry Pi Setup (C++ Environment)
```bash
# 1. Flash Ubuntu Server 22.04 LTS ARM64
# 2. Configure network
sudo nano /etc/netplan/50-cloud-init.yaml
# Set: 192.168.144.20/24

# 3. Install C++ development tools and dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git pkg-config
sudo apt install -y libboost-all-dev libssl-dev
sudo apt install -y nlohmann-json3-dev libudev-dev libusb-1.0-0-dev

# 4. Install additional networking libraries
sudo apt install -y libboost-system-dev libboost-thread-dev

# 5. Configure USB permissions for Sony camera
sudo nano /etc/udev/rules.d/99-sony-camera.rules
# Add: SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"
sudo udevadm control --reload-rules

# 6. Download and extract Sony SDK (C++ version)
cd ~
mkdir sony_sdk
# Extract Sony Camera Remote SDK to ~/sony_sdk/
# Verify libraries: libCrAdapter.so, libCrImageDataBlock.so

# 7. Set up C++ project structure
mkdir -p ~/payload_manager/{src,include,build,tests,docs}
mkdir -p ~/payload_manager/src/{network,protocol,camera,gimbal}
mkdir -p ~/payload_manager/include/{network,protocol,camera,gimbal}

# 8. Verify C++ compiler
g++ --version  # Should be GCC 11.x or newer
cmake --version  # Should be 3.16 or newer
```

### C++ Project Structure
```
~/payload_manager/
â"œâ"€â"€ CMakeLists.txt
â"œâ"€â"€ src/
â"‚   â"œâ"€â"€ payload_server.cpp        # Main entry point
â"‚   â"œâ"€â"€ network/
â"‚   â"‚   â"œâ"€â"€ tcp_server.cpp        # TCP command server
â"‚   â"‚   â""â"€â"€ udp_broadcaster.cpp   # UDP status broadcaster
â"‚   â"œâ"€â"€ protocol/
â"‚   â"‚   â""â"€â"€ message_handler.cpp   # JSON message handling
â"‚   â"œâ"€â"€ camera/
â"‚   â"‚   â""â"€â"€ sony_camera.cpp       # Sony SDK wrapper
â"‚   â""â"€â"€ gimbal/
â"‚       â""â"€â"€ gimbal_interface.cpp  # Gimbal control
â"œâ"€â"€ include/
â"‚   â"œâ"€â"€ network/
â"‚   â"œâ"€â"€ protocol/
â"‚   â"œâ"€â"€ camera/
â"‚   â""â"€â"€ gimbal/
â"œâ"€â"€ build/                      # CMake build directory
â"œâ"€â"€ tests/                      # Unit tests
â""â"€â"€ docs/                       # Documentation
```

### Android Development Setup
```bash
# 1. Install Android Studio
# 2. Install SDK Platform 26+ (Android 8.0+)
# 3. Create new project:
#    - Language: Kotlin
#    - Minimum SDK: API 26 (Android 8.0)
#    - Target: API 30 (Android 11, H16 version)
```

### Cross-Compilation Setup (Optional, for faster development)
```bash
# On development PC (Ubuntu/Debian)
# Install ARM64 cross-compiler
sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# Configure CMake for cross-compilation
# Create toolchain-arm64.cmake:
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

# Build for ARM64
cmake -DCMAKE_TOOLCHAIN_FILE=toolchain-arm64.cmake ..
make -j$(nproc)
```

### H16 Testing
```bash
# 1. Enable developer mode on H16
# 2. Connect H16 to development PC via USB
# 3. Enable USB debugging
# 4. Install app via ADB:
adb install payload_manager.apk

# 5. View logs:
adb logcat | grep PayloadManager
```

---

## ðŸ"‹ Pre-Development Checklist

### Hardware Ready?
- [ ] Raspberry Pi 4 (4GB or 8GB recommended for C++)
- [ ] Sony Camera (SDK compatible)
- [ ] USB cable for camera
- [ ] SkyDroid H16 Ground Station
- [ ] SkyDroid R16 Air Unit
- [ ] Gimbal (Gremsy or SimpleBGC)
- [ ] Flight controller (Ardupilot)
- [ ] Power supplies
- [ ] microSD card for Pi (32GB+, Class 10 or better)

### Software Ready?
- [ ] Ubuntu Server 22.04 LTS ARM64 image
- [ ] Sony Camera Remote SDK v2.00.00 (C++ libraries)
- [ ] Android Studio installed
- [ ] VS Code with Remote-SSH and C++ extensions
- [ ] Git for version control
- [ ] CMake 3.16+ installed

### C++ Development Tools Ready?
- [ ] GCC 11+ or Clang 12+ (ARM64)
- [ ] nlohmann-json library
- [ ] Boost libraries (optional, for networking)
- [ ] CMake configured
- [ ] Sony SDK libraries verified (libCrAdapter.so, etc.)

### Network Ready?
- [ ] H16 system configured
- [ ] R16 can connect to Pi via ethernet
- [ ] IP addresses planned (192.168.144.x)
- [ ] Network tested

### Documentation Ready?
- [ ] All 8 specification documents reviewed
- [ ] Protocol specification understood
- [ ] C++ Quick start guide bookmarked
- [ ] Sony SDK C++ examples reviewed

---

## ðŸŽ¯ Success Metrics

### Week 1 Success:
- âœ… C++ server accepts TCP connections
- âœ… Android app can connect to Pi
- âœ… Commands send successfully
- âœ… Responses received correctly
- âœ… JSON parsing works in C++

### Week 2 Success:
- âœ… UDP status broadcasts at 5 Hz from C++
- âœ… Android receives status updates
- âœ… Heartbeat detects disconnection
- âœ… Reconnection works automatically
- âœ… Memory management verified (no leaks)

### Week 3 Success:
- âœ… Sony camera connects to Pi via C++ SDK
- âœ… Basic property commands work
- âœ… Image capture works
- âœ… Android UI shows camera status
- âœ… C++ service runs stably for 1+ hour

### Phase 1 Complete:
- âœ… All camera controls working
- âœ… Both gimbals supported
- âœ… GCS integration working
- âœ… Content download operational
- âœ… 8-hour stability test passed
- âœ… QGC and Mission Planner compatibility verified
- âœ… C++ service stable under load
- âœ… Memory footprint < 100MB

---

## ðŸš¨ Risk Management

### Top Risks & Mitigations:

**Risk 1: H16 Network Configuration Unknown**
- **Impact:** Can't connect Pi to H16
- **Mitigation:** Test R16 ethernet port first, document IP range
- **Status:** Address when hardware arrives

**Risk 2: Sony SDK C++ Integration**
- **Impact:** Delays in camera integration
- **Mitigation:** Start with SDK sample apps, incremental integration
- **C++ Specific:** Use RAII for resource management, smart pointers
- **Status:** Documentation reviewed, ready to start

**Risk 3: C++ Memory Management**
- **Impact:** Memory leaks, crashes in long-running service
- **Mitigation:** Use smart pointers, valgrind testing, ASAN builds
- **Status:** Require memory leak testing from Week 1

**Risk 4: Protocol Design Changes Needed**
- **Impact:** Rework Android app and C++ service
- **Mitigation:** Protocol v1.0 is flexible, JSON allows easy extension
- **Status:** Low risk, well-designed protocol

**Risk 5: C++ Build Complexity**
- **Impact:** Slower development iterations
- **Mitigation:** CMake automation, cross-compilation setup
- **Status:** CMake template prepared

**Risk 6: Development Hardware Delays**
- **Impact:** Can't test full integration
- **Mitigation:** Can develop on emulator/tablet first, easy transition
- **Status:** Hardware confirmed available

---

## ðŸ'¡ Key Design Decisions Made

1. **âœ… Use H16 Ground Station** (not separate tablet)
   - Better performance, professional solution
   
2. **âœ… JSON Protocol** (not binary)
   - Human-readable, easy to debug
   - nlohmann-json library for C++ parsing
   
3. **âœ… TCP for Commands, UDP for Status**
   - Reliable commands, low-latency status
   
4. **âœ… Camera HDMI â†' R16 for Primary Video**
   - Lowest latency, best quality
   
5. **âœ… Protocol-First Development**
   - Defines interface between components
   
6. **âœ… Incremental Implementation**
   - Basic protocol â†' Camera â†' Gimbal â†' Polish

7. **âœ… C++ for Air Side** (MANDATORY)
   - Better performance, lower latency
   - Direct Sony SDK integration
   - Suitable for embedded real-time system
   - Professional UAV development standard

8. **âœ… Modern C++ (C++17)**
   - Smart pointers, RAII
   - std::thread, std::async for concurrency
   - Type safety, compile-time checks

---

## ðŸ"ž Next Actions (Priority Order)

### ðŸ"¥ This Week (High Priority):
1. **Set up Raspberry Pi** with Ubuntu Server ARM64
2. **Configure Pi network** for H16 integration (192.168.144.20)
3. **Install C++ development environment** (GCC, CMake, libraries)
4. **Install Sony SDK C++ libraries** and test sample app
5. **Create CMake project structure** for payload manager
6. **Implement basic TCP server** in C++
7. **Create Android project** and implement TCP client
8. **Test basic command/response** communication

### ðŸ"… Next Week:
9. Add UDP status broadcasting (C++)
10. Implement heartbeat system
11. Add JSON message parsing (nlohmann-json)
12. Test connection reliability
13. Memory leak testing (valgrind)
14. Begin Sony SDK C++ integration

### ðŸŽ¯ Week 3+:
15. Camera control commands (C++)
16. Android UI for camera control
17. Real camera testing
18. Performance profiling
19. Continue per timeline...

---

## ðŸ"§ C++ Libraries & Dependencies

### Required Libraries:
```bash
# JSON parsing
nlohmann-json3-dev (v3.2.0+)

# Sony Camera SDK
libCrAdapter.so
libCrImageDataBlock.so
(Included in Sony Camera Remote SDK v2.00.00)

# System libraries
libusb-1.0-0-dev  # USB device access
libudev-dev       # Device detection
libssl-dev        # Optional: encrypted communications

# Optional: Boost (if using Boost.Asio for networking)
libboost-system-dev
libboost-thread-dev
libboost-filesystem-dev
```

### Build System:
- **CMake 3.16+** - Build configuration
- **Make** or **Ninja** - Build tool
- **GCC 11+** or **Clang 12+** - Compiler

### Development Tools:
- **GDB** - Debugging
- **Valgrind** - Memory leak detection
- **AddressSanitizer** - Runtime error detection
- **clang-tidy** - Static analysis
- **clang-format** - Code formatting

---

## ðŸŽ" Learning Resources

### Sony Camera Remote SDK:
- SDK Documentation: `Sony_CameraRemoteSDK_API-Reference_v2.00.00.pdf`
- **C++ Sample Application**: `RemoteSampleApp_IM_v2_00_00.pdf`
- C++ API Reference included in SDK
- License: http://www.sony.net/CameraRemoteSDK/

### C++ Development:
- Modern C++ Tutorial: https://changkun.de/modern-cpp/
- C++17 Features: https://en.cppreference.com/w/cpp/17
- CMake Tutorial: https://cmake.org/cmake/help/latest/guide/tutorial/
- nlohmann-json: https://github.com/nlohmann/json

### Network Programming in C++:
- POSIX Sockets (Linux): https://beej.us/guide/bgnet/
- Boost.Asio (optional): https://www.boost.org/doc/libs/release/doc/html/boost_asio.html

### Gimbal SDKs:
- Gremsy gSDK (C++): https://github.com/Gremsy/gSDK
- SimpleBGC Serial API (C): https://github.com/basecamelectronics/sbgc32-serial-api

### Android Development:
- Kotlin Coroutines: https://kotlinlang.org/docs/coroutines-guide.html
- Network Programming: Standard Java sockets + Kotlin coroutines

### H16 System:
- SkyDroid website: http://en.siyi.biz/
- (Documentation as available from manufacturer)

---

## ðŸŽ‰ You're Ready to Start!

**You have:**
- âœ… Complete project scope defined
- âœ… Architecture designed for H16 system
- âœ… Protocol specification complete
- âœ… C++ implementation guide ready
- âœ… CMake build system prepared
- âœ… Hardware confirmed available
- âœ… Clear timeline (17 weeks)

**Critical Requirements:**
- ðŸ"¥ **ALL Air-Side code MUST be C++**
- âœ… Use CMake for build system
- âœ… Modern C++17 features
- âœ… Memory-safe practices (smart pointers, RAII)
- âœ… Thread-safe networking
- âœ… Continuous memory leak testing

**First milestone:**  
**Week 1:** Working TCP command/response between Android and Pi (C++ server)

**Let's build this! ðŸš€**

---

## ðŸ"¬ Questions / Support

If you need clarification on any aspect:
- Review the 8 specification documents
- Check the Protocol Quick Start guide (adapt for C++)
- Refer to Sony SDK C++ documentation
- Test incrementally, one feature at a time
- Use valgrind for memory testing
- Profile performance with gprof/perf

**Good luck with the C++ development!** ðŸŽ¯

---

## ðŸ" Appendix: Quick C++ Reference

### Basic TCP Server Template (C++)
```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <nlohmann/json.hpp>
#include <thread>
#include <iostream>

using json = nlohmann::json;

class TcpServer {
public:
    TcpServer(int port) : port_(port) {}
    
    void start() {
        server_fd_ = socket(AF_INET, SOCK_STREAM, 0);
        
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);
        
        bind(server_fd_, (struct sockaddr*)&addr, sizeof(addr));
        listen(server_fd_, 10);
        
        std::cout << "Server listening on port " << port_ << std::endl;
    }
    
private:
    int server_fd_;
    int port_;
};
```

### JSON Message Handling (C++)
```cpp
#include <nlohmann/json.hpp>

void handleCommand(const std::string& msg) {
    auto j = nlohmann::json::parse(msg);
    
    std::string msg_type = j["message_type"];
    int seq_id = j["sequence_id"];
    
    if (msg_type == "command") {
        auto payload = j["payload"];
        std::string cmd = payload["command"];
        
        // Process command...
    }
}
```

---

**Document Status:** âœ… Final C++ Version  
**Date:** October 24, 2025  
**Language:** C++ (Air-Side), Kotlin/Java (Ground-Side)  
**Ready for:** Immediate C++ Development Start