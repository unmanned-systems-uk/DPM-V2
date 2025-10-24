# Docker Solution Briefing for Claude Code

**Date:** October 23, 2025  
**Project:** Drone Payload Manager (DPM)  
**Context:** Sony Camera SDK compatibility issue on Ubuntu 25.04

---

## Executive Summary for Claude Code

This document explains the Docker-based solution we've implemented to solve a critical compatibility issue in the Drone Payload Manager project. The solution allows the Sony Camera Remote SDK to work on Ubuntu 25.04 by running it in an Ubuntu 22.04 Docker container.

---

## The Problem We're Solving

### Technical Issue
The Sony Camera Remote SDK library (`libCr_Core.so`) was compiled against **libxml2 version 2.x** (from Ubuntu 20.04/22.04 era). The Raspberry Pi 4 running the air-side code has been upgraded to **Ubuntu 25.04 "Questing"**, which ships with **libxml2 version 16.x**.

### Symptoms
```
/usr/bin/ld: .../libCr_Core.so: undefined reference to `xmlParseFile@LIBXML2_2.4.30'
/usr/bin/ld: .../libCr_Core.so: undefined reference to `xmlNewNode@LIBXML2_2.4.30'
... (multiple similar linker errors)
```

This is an **ABI (Application Binary Interface) incompatibility** - the symbol versions have changed between libxml2 v2.x and v16.x, making the Sony SDK library unusable on the newer system.

### Why This Matters
Without Sony SDK working:
- ❌ Cannot control Sony A1 camera
- ❌ Cannot capture images/video via API
- ❌ Cannot read camera settings
- ❌ Cannot implement Week 3 camera control features
- ❌ Project blocked at Week 1

---

## The Solution: Docker Container with Ubuntu 22.04

### Architecture

```
┌─────────────────── HOST: Raspberry Pi 4 ─────────────────────┐
│  Ubuntu 25.04 "Questing"                                     │
│  libxml2 v16.x (incompatible)                                │
│                                                               │
│  ┌──────────────── DOCKER CONTAINER ──────────────────┐     │
│  │  Ubuntu 22.04 LTS                                   │     │
│  │  libxml2 v2.x (compatible!)                         │     │
│  │                                                      │     │
│  │  ┌────────────────────────────────────────────┐    │     │
│  │  │  /app/                                      │    │     │
│  │  │  ├── sdk/                                   │    │     │
│  │  │  │   ├── lib/libCr_Core.so (Sony SDK)      │    │     │
│  │  │  │   └── include/                           │    │     │
│  │  │  ├── src/                                   │    │     │
│  │  │  │   ├── payload_server.py (main service)  │    │     │
│  │  │  │   ├── camera_sony.cpp (SDK wrapper)     │    │     │
│  │  │  │   └── test_camera.cpp (testing)         │    │     │
│  │  │  └── logs/                                  │    │     │
│  │  └────────────────────────────────────────────┘    │     │
│  │                                                      │     │
│  │  Network: Host networking (192.168.144.20)          │     │
│  │  Ports: 5000/tcp, 5001/udp, 5002/udp               │     │
│  │  USB: /dev/bus/usb passthrough (camera access)     │     │
│  └──────────────────────────────────────────────────────┘     │
│                          ↕                                     │
│                  [Sony A1 Camera via USB]                     │
└───────────────────────────────────────────────────────────────┘
                           ↕
                [H16 Ground Station - 192.168.144.11]
```

### Key Components

1. **Base Image:** Ubuntu 22.04 LTS (has libxml2 v2.x)
2. **USB Passthrough:** Full camera access via `--privileged` and `/dev/bus/usb` mount
3. **Host Networking:** Container uses host network stack (no NAT overhead)
4. **Volume Mounts:** 
   - Source code mounted for live editing
   - Logs persisted to host
5. **Service Mode:** Runs as background daemon with auto-restart

---

## Project Context

### Overall Project: Drone Payload Manager
- **Air Side:** Raspberry Pi 4 + Sony Camera + Gimbal
- **Ground Side:** SkyDroid H16 Ground Control Station (Android)
- **Link:** R16 digital data-link (up to 10km)
- **Network:** 192.168.144.x internal network



### Repository Structure (Monorepo)
```
/home/dpm/DPM/                          # Git root
├── sbc/                                # Air-side code (Pi)
│   ├── Dockerfile                      # Docker container config
│   ├── build_container.sh              # Build automation
│   ├── run_container.sh                # Runtime management
│   ├── setup_docker_env_monorepo.sh    # Initial setup
│   ├── sony_sdk/                       # Sony SDK (not in Git)
│   │   ├── lib/libCr_Core.so
│   │   └── include/
│   ├── src/
│   │   ├── payload_server.py           # Main TCP/UDP service
│   │   ├── camera_sony.cpp             # Sony SDK wrapper
│   │   └── test_camera.cpp             # Standalone camera test
│   ├── logs/                           # Runtime logs
│   └── build/                          # Build artifacts
│
├── android/                            # Ground station app
│   └── app/                            # UNAFFECTED by Docker
│
├── shared/                             # Shared protocol definitions
└── docs/                               # Documentation
```

### Important: Monorepo Preserved
- ✅ Docker only affects `sbc/` subdirectory
- ✅ Android development completely unchanged
- ✅ Both components in single Git repository
- ✅ No separation needed

---

## Docker Container Details

### Dockerfile Structure

```dockerfile
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libxml2 \
    libusb-1.0-0 \
    python3 \
    python3-pip \
    usbutils

# Copy Sony SDK
COPY sony_sdk/ /app/sdk/

# Copy application code
COPY src/ /app/src/

# Set library path
ENV LD_LIBRARY_PATH=/app/sdk/lib:$LD_LIBRARY_PATH

# Expose network ports
EXPOSE 5000/tcp 5001/udp 5002/udp

# Run service
CMD ["python3", "/app/src/payload_server.py"]
```

### Container Modes

#### Production Mode (Default)
```bash
./run_container.sh prod

# Characteristics:
# - Runs as background daemon (-d)
# - Auto-restart on failure (--restart always)
# - Code baked into image
# - Rebuild required for code changes
# - Stable, production-ready
```

#### Development Mode
```bash
./run_container.sh dev

# Characteristics:
# - Source code mounted as volume (-v src:/app/src)
# - Live code editing (no rebuild needed)
# - Restart container to reload changes
# - Faster iteration during development
```

### Network Configuration
- **Mode:** Host networking (`--network host`)
- **IP:** 192.168.144.20 (H16 internal network)
- **Ports:**
  - `5000/tcp` - Command server (Ground → Air)
  - `5001/udp` - Status broadcast (Air → Ground, 5 Hz)
  - `5002/udp` - Heartbeat (Bidirectional, 1 Hz)

### USB Camera Access
```bash
docker run \
  --privileged \                    # Required for USB access
  -v /dev/bus/usb:/dev/bus/usb \   # USB device passthrough
  ...
```

Camera appears in container exactly as on host:
```bash
# Inside container
lsusb
# Bus 001 Device 003: ID 054c:XXXX Sony Corp.
```

---

## Development Workflows

### Workflow 1: Testing Camera (CC's Approach)
**Purpose:** Test Sony SDK integration, debug camera issues

```bash
# Build test container
docker build -f Dockerfile.test -t dpm-test:latest .

# Run interactively
docker run -it --rm \
  --privileged \
  -v /home/dpm/DPM/sbc:/workspace/sbc:rw \
  -v /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/workspace/sdk:ro \
  -v /dev/bus/usb:/dev/bus/usb \
  --network host \
  dpm-test:latest

# Inside container: build and test
cd /workspace/sbc
mkdir build && cd build
cmake ..
make test_camera
./test_camera
exit
```

**Use for:** Development, debugging, testing new camera features

### Workflow 2: Production Service (My Approach)
**Purpose:** Run payload manager as continuous service

```bash
# Build production image
./build_container.sh

# Run as service
./run_container.sh prod

# Monitor
docker logs -f dpm-service

# Stop/Start/Restart
docker stop dpm-service
docker start dpm-service
docker restart dpm-service
```

**Use for:** Actual drone operations, H16 integration, Week 2+ development

### Workflow 3: Rapid Development
**Purpose:** Quick code iteration during development

```bash
# Run in dev mode
./run_container.sh dev

# Edit code on host (in your IDE)
nano /home/dpm/DPM/sbc/src/payload_server.py

# Restart to reload
docker restart dpm-service

# View logs
docker logs -f dpm-service
```

**Use for:** Week 1-2 protocol implementation, debugging

---

## What Claude Code Needs to Know

### When Working with SBC Code

1. **All Python/C++ code runs INSIDE the container**
   - Don't expect to run `python3 payload_server.py` on host
   - Build/run commands must be in container context

2. **Two build contexts:**
   ```bash
   # On host (outside container):
   cd /home/dpm/DPM/sbc
   docker build -t dpm-service:latest .
   
   # Inside container (for C++ builds):
   docker exec -it dpm-service bash
   cd /workspace/sbc/build
   cmake ..
   make
   ```

3. **File paths differ:**
   ```bash
   # Host:
   /home/dpm/DPM/sbc/src/payload_server.py
   
   # Inside container:
   /app/src/payload_server.py
   # OR (in dev mode):
   /workspace/sbc/src/payload_server.py
   ```

4. **Sony SDK location:**
   ```bash
   # Host:
   /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/
   
   # Inside container:
   /app/sdk/
   # OR (in dev mode):
   /workspace/sdk/
   ```

### When Suggesting Code Changes

**For Python code (payload_server.py):**
```python
# This runs inside container, which has:
# - Python 3.10+ (Ubuntu 22.04)
# - pyserial, requests packages
# - Access to Sony SDK via ctypes/cffi if needed
# - Network ports 5000-5002
# - USB camera access

# Example: Import Sony SDK wrapper
from camera_sony import SonyCamera  # This is C++ wrapped via pybind11 or similar
```

**For C++ code (camera_sony.cpp):**
```cpp
// This compiles inside container, which has:
// - g++ from Ubuntu 22.04
// - Sony SDK headers in /app/sdk/include/
// - Sony SDK library in /app/sdk/lib/libCr_Core.so
// - libxml2 v2.x (compatible!)

#include "CameraRemote_SDK.h"  // Sony SDK header

// Link with: -L/app/sdk/lib -lCr_Core
```

**For CMakeLists.txt:**
```cmake
# Sony SDK paths in container
set(SONY_SDK_DIR "/app/sdk")
include_directories(${SONY_SDK_DIR}/include)
link_directories(${SONY_SDK_DIR}/lib)

add_executable(test_camera test_camera.cpp)
target_link_libraries(test_camera Cr_Core xml2 usb-1.0)
```

### When Debugging Issues

**Check container status:**
```bash
docker ps | grep dpm-service      # Is it running?
docker logs dpm-service           # What's in the logs?
docker exec dpm-service lsusb     # Can it see camera?
```

**Check libxml2 (the original problem):**
```bash
# Inside container - should show v2.x
docker exec dpm-service dpkg -l | grep libxml2

# Inside container - verify SDK links correctly
docker exec dpm-service ldd /app/sdk/lib/libCr_Core.so
# Should show: libxml2.so.2 => ... (NOT libxml2.so.16)
```

**Check network:**
```bash
# Inside container
docker exec dpm-service ip addr
# Should show 192.168.144.20

# Test from H16 (Android)
nc -zv 192.168.144.20 5000
```

**Access shell:**
```bash
docker exec -it dpm-service bash
# Now you're inside container, can debug directly
```

---

## Common Tasks for Claude Code

### Task 1: Modify Payload Server
```bash
# User edits: /home/dpm/DPM/sbc/src/payload_server.py

# If in dev mode:
docker restart dpm-service

# If in prod mode:
cd /home/dpm/DPM/sbc
./build_container.sh
./run_container.sh prod
```

### Task 2: Add New Camera Function
```bash
# User edits: /home/dpm/DPM/sbc/src/camera_sony.cpp

# Rebuild in container:
docker exec -it dpm-service bash
cd /workspace/sbc/build
cmake ..
make
exit

# Or rebuild entire container:
./build_container.sh
./run_container.sh prod
```

### Task 3: Test Camera Connection
```bash
# Run test container
docker run -it --rm \
  --privileged \
  -v /home/dpm/DPM/sbc:/workspace/sbc:rw \
  -v /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/workspace/sdk:ro \
  -v /dev/bus/usb:/dev/bus/usb \
  dpm-test:latest

# Inside:
cd /workspace/sbc/build
./test_camera
```

### Task 4: Debug Network Issue
```bash
# Check if service is listening
docker exec dpm-service netstat -tuln | grep 5000

# Test from host
echo "test" | nc localhost 5000

# Check logs
docker logs -f dpm-service | grep -i error
```

### Task 5: Update Dependencies
```bash
# Edit Dockerfile to add new package:
RUN apt-get install -y new-package

# Rebuild
./build_container.sh
```

---

## Files Claude Code Should Be Aware Of

### In `/home/dpm/DPM/sbc/`:

**Docker Configuration:**
- `Dockerfile` - Production service container
- `Dockerfile.test` - Development/testing container
- `.dockerignore` - Files to exclude from build

**Build Scripts:**
- `setup_docker_env_monorepo.sh` - Initial setup (run once)
- `build_container.sh` - Build Docker image
- `run_container.sh` - Run container (prod/dev modes)
- `rebuild.sh` - Quick rebuild + restart
- `test_camera.sh` - Test camera in container
- `shell.sh` - Quick shell access

**Source Code:**
- `src/payload_server.py` - Main service (Python)
- `src/camera_sony.cpp` - Sony SDK wrapper (C++)
- `src/test_camera.cpp` - Standalone camera test (C++)
- `src/network/` - TCP/UDP server code
- `CMakeLists.txt` - Build configuration

**External (Not in Git):**
- `sony_sdk/` - Sony Camera Remote SDK
- `logs/` - Runtime logs
- `build/` - Build artifacts

### In `/home/dpm/DPM/android/`:
- Completely separate, not affected by Docker
- Standard Android Studio project
- Develops normally, no container needed

---

## Protocol Implementation Context

### Week 1 Goal: TCP Command Server
```python
# payload_server.py (runs in container)

import socket
import json

def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 5000))  # Binds to host IP
    sock.listen(5)
    
    while True:
        conn, addr = sock.accept()
        data = conn.recv(4096)
        
        # Parse command
        cmd = json.loads(data)
        
        # Execute command (e.g., camera control)
        if cmd['command'] == 'camera.capture':
            # Call Sony SDK wrapper
            result = camera.capture()
        
        # Send response
        response = json.dumps({'status': 'ok', 'result': result})
        conn.send(response.encode())
        conn.close()
```

### Week 2 Goal: UDP Status Broadcast
```python
# payload_server.py

import socket
import time

def udp_broadcaster():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        status = {
            'battery': camera.get_battery(),
            'recording': camera.is_recording(),
            'timestamp': time.time()
        }
        
        # Broadcast to H16
        sock.sendto(json.dumps(status).encode(), 
                    ('192.168.144.11', 5001))
        
        time.sleep(0.2)  # 5 Hz
```

---

## Performance Considerations

### Container Overhead
- **CPU:** < 5% idle, < 30% active
- **Memory:** < 200MB
- **Network:** Zero overhead (host networking)
- **USB:** Zero overhead (direct passthrough)
- **Latency:** < 1ms added by container

### Expected Performance
- **Command response:** < 10ms
- **Status broadcast:** Solid 5 Hz
- **Camera control:** Full speed (limited by Sony SDK, not Docker)
- **Image capture:** Full speed
- **USB throughput:** Full speed

### Not a Bottleneck
The Docker container does NOT slow down:
- Camera communication
- Network communication
- USB data transfer
- Image processing

It only provides the correct runtime environment!

---

## Troubleshooting Guide for Claude Code

### Issue: "Container won't start"
```bash
# Check logs
docker logs dpm-service

# Common causes:
# 1. Port already in use
netstat -tuln | grep 5000

# 2. Sony SDK not copied
ls -la /home/dpm/DPM/sbc/sony_sdk/

# 3. Syntax error in payload_server.py
docker exec dpm-service python3 -m py_compile /app/src/payload_server.py
```

### Issue: "Camera not detected"
```bash
# Check on host first
lsusb | grep Sony

# Check in container
docker exec dpm-service lsusb | grep Sony

# Check USB permissions
docker exec dpm-service ls -la /dev/bus/usb/*/*

# Restart container
docker restart dpm-service
```

### Issue: "libxml2 errors persist"
```bash
# Verify container OS
docker exec dpm-service cat /etc/os-release
# Should show: Ubuntu 22.04

# Verify libxml2 version
docker exec dpm-service dpkg -l | grep libxml2
# Should show: 2.x, NOT 16.x

# If wrong version, rebuild container
./build_container.sh
```

### Issue: "Network not accessible"
```bash
# Check container networking
docker exec dpm-service ip addr
# Should show 192.168.144.20

# Check if ports are bound
docker exec dpm-service netstat -tuln
# Should show: 0.0.0.0:5000, 0.0.0.0:5001, etc.

# Test from host
nc -zv localhost 5000
```

### Issue: "Code changes not taking effect"
```bash
# If in prod mode, need to rebuild
./build_container.sh
./run_container.sh prod

# If in dev mode, just restart
docker restart dpm-service
```

---

## Critical Reminders for Claude Code

1. **Always consider container context**
   - Code runs INSIDE container, not on host
   - File paths are different
   - Environment is Ubuntu 22.04, not 25.04

2. **Sony SDK is in container**
   - Not accessible from host directly
   - Use `docker exec` to test SDK commands
   - All camera code must run in container

3. **Network is host mode**
   - Container uses host IP directly
   - No port mapping needed
   - Services bind to 0.0.0.0 but accessible via host IP

4. **USB passthrough is transparent**
   - Camera appears same in container as on host
   - No special code needed for USB in container
   - Just use Sony SDK as normal

5. **Dev mode vs Prod mode**
   - Dev mode: Code mounted, can edit live
   - Prod mode: Code in image, need rebuild
   - Choose based on iteration speed needed

6. **Monorepo structure is preserved**
   - `sbc/` has Docker stuff
   - `android/` is completely separate
   - Don't suggest separating repos!

7. **This is a permanent solution**
   - Not a workaround or temporary fix
   - Production-ready and stable
   - Will serve through entire project

---

## Quick Reference Commands for Claude Code

```bash
# Build container
cd /home/dpm/DPM/sbc && ./build_container.sh

# Run production
./run_container.sh prod

# Run development
./run_container.sh dev

# View logs
docker logs -f dpm-service

# Shell access
docker exec -it dpm-service bash

# Test camera
docker exec dpm-service /app/build/test_camera

# Check status
docker ps | grep dpm-service

# Restart
docker restart dpm-service

# Stop
docker stop dpm-service

# Remove and rebuild
docker stop dpm-service && docker rm dpm-service && ./build_container.sh && ./run_container.sh prod
```

---

## Summary for Claude Code

**What Docker solves:** Sony SDK compatibility (libxml2 v2.x vs v16.x)

**How it works:** Ubuntu 22.04 container with correct libxml2 version

**Where code runs:** Inside container (transparent to development)

**What changes:** Nothing for Android, build/run process for SBC

**Performance impact:** Negligible (< 5% CPU, < 200MB RAM)

**Production ready:** Yes, designed for production use

**Monorepo:** Preserved, Docker in `sbc/` subdirectory only

**Your role:** Help develop code that runs inside container, considering container environment

---

**Document Created:** October 23, 2025  
**Status:** ✅ Complete Briefing for Claude Code  
**Purpose:** Enable Claude Code to work effectively with Docker-based development environment