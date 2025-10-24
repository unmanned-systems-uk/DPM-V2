# Docker Setup for Sony Camera SDK Testing

**Purpose:** Run Sony Camera Remote SDK applications in a compatible Ubuntu environment
**Reason:** Host system (Ubuntu 25.04) has libxml2 v16 incompatible with Sony SDK (requires libxml2 v2.x)
**Status:** ✅ **TESTED AND WORKING** - Container deployed October 24, 2025
**Date:** October 23-24, 2025

---

## ✅ Production Setup (TESTED - October 24, 2025)

**Current Status:**
- ✅ Docker image built: `payload-manager:latest` (1.03GB)
- ✅ Container running in production mode
- ✅ C++ payload_manager compiles and runs successfully
- ✅ USB passthrough configured
- ✅ Host networking enabled (192.168.144.20)
- ✅ Auto-restart enabled
- ✅ Sony SDK fully integrated (CrAdapter/ dynamic loading fixed)
- ✅ test_camera works - enumerates Sony A1 successfully
- ✅ test_shutter builds - tests shutter commands
- ✅ RemoteCli verified working inside container
- 🐛 Debugging connection error 0x8208 in test_shutter
- 🔋 Camera battery recharging

**Quick Commands:**

```bash
# Check container status
sudo docker ps | grep payload-manager

# View logs
sudo docker logs payload-manager

# Access shell
sudo docker exec -it payload-manager bash

# Test USB devices
sudo docker exec payload-manager lsusb

# Restart container
sudo docker restart payload-manager

# Stop container
sudo docker stop payload-manager
```

**Helper Scripts Available:**
- `/home/dpm/DPM/sbc/build_container.sh` - Build Docker image
- `/home/dpm/DPM/sbc/run_container.sh` - Run container (prod/dev)
- `/home/dpm/DPM/sbc/test_camera.sh` - Test camera connection
- `/home/dpm/DPM/sbc/rebuild.sh` - Quick rebuild
- `/home/dpm/DPM/sbc/shell.sh` - Shell access

---

## Problem Summary

The Sony Camera Remote SDK `libCr_Core.so` library was compiled against libxml2 version 2.x (Ubuntu 20.04/22.04 era). Our Raspberry Pi runs Ubuntu 25.04 "Questing" which uses libxml2 version 16.x with a different ABI.

**Symptoms:**
```
/usr/bin/ld: .../external/crsdk/libCr_Core.so: undefined reference to `xmlParseFile@LIBXML2_2.4.30'
/usr/bin/ld: .../external/crsdk/libCr_Core.so: undefined reference to `xmlNewNode@LIBXML2_2.4.30'
... (multiple similar errors)
```

**Solution:** Use Docker container with Ubuntu 22.04 which has compatible libxml2 v2.x

---

## Prerequisites

1. Docker installed on the Raspberry Pi
2. Sony Camera Remote SDK at `/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/`
3. DPM source code at `/home/dpm/DPM/sbc/`
4. Sony A1 camera with USB cable

---

## Production Build Procedure (TESTED)

**This is the actual procedure used successfully on October 24, 2025:**

### 1. Build the Docker Image

```bash
cd /home/dpm/DPM/sbc
./build_container.sh
```

**What this does:**
- Uses `Dockerfile.prod` with Ubuntu 22.04
- Copies Sony SDK from `/home/dpm/SonySDK/`
- Copies SBC source code
- Compiles C++ payload_manager inside container
- Creates `payload-manager:latest` image

**Build time:** ~5 minutes (ARM64 compilation)

### 2. Run the Container

```bash
cd /home/dpm/DPM/sbc
./run_container.sh prod
```

**What this does:**
- Runs container in production mode
- Enables USB passthrough for camera
- Uses host networking (192.168.144.20)
- Auto-restart enabled
- Mounts logs directory

**Verification:**
```bash
sudo docker ps | grep payload-manager
# Should show: payload-manager running
```

### 3. Test Camera (When Battery Charged)

```bash
cd /home/dpm/DPM/sbc
./test_camera.sh
```

Or manually:
```bash
sudo docker exec payload-manager lsusb | grep Sony
```

---

## Development/Testing Setup (Original Guide)

**Note:** The following is the original development setup. For production, use the scripts above.

### 1. Create Dockerfile (Development)

Create `/home/dpm/DPM/sbc/Dockerfile`:

```dockerfile
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libxml2-dev \
    nlohmann-json3-dev \
    libudev-dev \
    libusb-1.0-0-dev \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Create directories for mounted volumes
RUN mkdir -p /workspace/sbc /workspace/sdk

CMD ["/bin/bash"]
```

### 2. Build Docker Image

```bash
cd /home/dpm/DPM/sbc
docker build -t sony-camera-test:ubuntu22.04 .
```

**Expected output:**
```
Successfully built <image-id>
Successfully tagged sony-camera-test:ubuntu22.04
```

### 3. Run Docker Container

**With USB device passthrough (for camera):**

```bash
docker run -it --rm \
  --privileged \
  -v /home/dpm/DPM/sbc:/workspace/sbc \
  -v /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/workspace/sdk \
  -v /dev/bus/usb:/dev/bus/usb \
  --name sony-camera-test \
  sony-camera-test:ubuntu22.04
```

**Flags explained:**
- `-it`: Interactive terminal
- `--rm`: Remove container when done
- `--privileged`: Allow USB device access
- `-v`: Mount volumes (host:container)
- `--name`: Container name

### 4. Verify Environment Inside Container

Once inside the container:

```bash
# Check Ubuntu version
cat /etc/os-release | grep VERSION

# Check libxml2 version
dpkg -l | grep libxml2

# Check mounted directories
ls -la /workspace/sbc
ls -la /workspace/sdk

# Check USB devices (camera must be connected and powered on)
lsusb
```

**Expected USB output (Sony A1):**
```
Bus 001 Device 003: ID 054c:XXXX Sony Corp.
```

### 5. Build test_camera Inside Container

```bash
cd /workspace/sbc
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . --target test_camera -j4
```

**Success indicators:**
- No libxml2 linker errors
- `test_camera` executable created

### 6. Run Camera Test

```bash
./test_camera
```

**Expected output:**
```
*** Sony Camera Connection Test ***

Sony Remote SDK version: 2.0.0

Initializing Sony Remote SDK...
Sony Remote SDK initialized successfully.

Enumerating connected cameras...
Found 1 camera(s):

[1] ILCE-1 (USB)

Auto-selecting the only camera...

=== Camera Information ===
Model: ILCE-1
Connection Type: USB
ID: <serial>
==========================

Connecting to camera...
[Callback] Camera connected
Successfully connected to camera!
Device handle: <handle>

... (property information) ...

Press Enter to disconnect and exit...
```

---

## Building Sony SDK Example (RemoteCli)

To build Sony's own example application:

```bash
cd /workspace/sdk
mkdir -p build && cd build
cmake ..
cmake --build . -j4
```

Run it:
```bash
./RemoteCli
```

---

## Troubleshooting

### Container won't start
**Error:** "docker: command not found"
**Solution:** Install Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### Camera not detected (lsusb shows nothing)
**Checks:**
1. Camera is powered on
2. USB cable connected
3. Camera is in USB mode (not just charging)
4. Check on host first: `lsusb` on Raspberry Pi

### Build fails with "permission denied"
**Solution:** Make sure volumes are mounted with proper permissions
```bash
# Add to docker run command:
-v /home/dpm/DPM/sbc:/workspace/sbc:rw
```

### libxml2 errors persist
**Check:** You're inside the container
```bash
# This should show Ubuntu 22.04
cat /etc/os-release
```

### Camera connection times out
**Possible causes:**
1. Camera firmware needs update
2. Camera not in proper mode
3. USB permissions issue

**Try:**
```bash
# Inside container, give broader USB permissions
chmod 666 /dev/bus/usb/*/*
```

---

## Files Created in This Setup

**Host System:**
- `/home/dpm/DPM/sbc/Dockerfile` - Container definition
- `/home/dpm/DPM/sbc/src/test_camera.cpp` - Standalone camera test
- `/home/dpm/DPM/sbc/docs/DOCKER_SETUP.md` - This file

**Inside Container (volatile, deleted on exit):**
- `/workspace/sbc/build/` - Build artifacts
- `/workspace/sdk/build/` - Sony SDK build artifacts

**Note:** Use `docker run` WITHOUT `--rm` flag to preserve container state between sessions.

---

## Alternative: Persistent Container

To keep the build environment between sessions:

```bash
# Create container (first time only)
docker run -it \
  --privileged \
  -v /home/dpm/DPM/sbc:/workspace/sbc \
  -v /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/workspace/sdk \
  -v /dev/bus/usb:/dev/bus/usb \
  --name sony-camera-persistent \
  sony-camera-test:ubuntu22.04

# Exit container (Ctrl+D or 'exit')

# Restart container later
docker start -ai sony-camera-persistent

# Remove container when done
docker rm sony-camera-persistent
```

---

## Sony SDK Integration Status

### ✅ Completed Steps

1. **Camera enumeration** - ✅ Works (test_camera detects Sony A1)
2. **RemoteCli verification** - ✅ Works (Sony's example app runs successfully)
3. **Critical Fix: Adapter Loading** - ✅ Resolved
   - **Issue:** Error 0x34563 "No adapters available"
   - **Root Cause:** Missing CrAdapter/ directory, static linking of adapters
   - **Fix:**
     - Copy CrAdapter/ directory to build folder
     - Only link `libCr_Core.so` (NOT adapter .so files)
     - Adapters load dynamically from ./CrAdapter/ at runtime
   - **Dockerfile.prod changes (lines 32-38):**
     ```dockerfile
     RUN cd /app/sbc && \
         mkdir -p build && \
         cd build && \
         cmake -DCMAKE_BUILD_TYPE=Release .. && \
         cmake --build . --target payload_manager -j4 && \
         mkdir -p CrAdapter && \
         cp -r /app/sdk/external/crsdk/CrAdapter/* CrAdapter/
     ```
   - **CMakeLists.txt changes:** Only link libCr_Core.so, removed adapter links

### 🐛 Current Issues

1. **Connection Error 0x8208** - Under investigation
   - **File:** src/test_shutter.cpp:195
   - **Symptom:** SDK::Connect() succeeds but OnConnected callback never fires
   - **Impact:** Cannot send shutter commands
   - **Status:** Comparing with RemoteCli implementation

### 📋 Next Steps

1. **Resolve connection error 0x8208** - Priority
2. **Test shutter commands** - After connection fix
3. **Verify photo capture** - Check camera memory card
4. **Query camera properties** - Read battery, model, settings
5. **Integrate with payload_manager** - Replace camera_stub with camera_sony implementation

---

## Future: Production Deployment

**Option 1:** Run entire payload_manager in Docker
- Pros: Consistent environment
- Cons: Added complexity, slight performance overhead

**Option 2:** Request updated Sony SDK from Sony
- Pros: Native performance
- Cons: Depends on Sony support

**Option 3:** Downgrade host OS to Ubuntu 22.04
- Pros: No Docker needed
- Cons: Older system packages

**Recommendation:** Use Docker for development/testing, evaluate options when ready for production.

---

**Document Status:** Ready for use ✅
**Last Updated:** October 23, 2025
**Maintained By:** DPM Project
