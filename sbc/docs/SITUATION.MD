# Current Issue: Sony SDK Connection Error 0x8208

**Date:** October 24, 2025
**Status:** BLOCKED - Seeking External Support
**Project:** DPM Payload Manager - Air Side (Raspberry Pi)
**Issue:** OnConnected callback never fires after SDK::Connect() succeeds

---

## Executive Summary

We have successfully integrated the Sony Camera Remote SDK v2.00.00 into a Docker container on a Raspberry Pi to control a Sony A1 camera via USB. Camera enumeration works perfectly, and Sony's own example application (RemoteCli) works flawlessly in the same environment. However, our custom test program experiences a connection handshake failure (error 0x8208) where `SDK::Connect()` returns success but the `OnConnected` callback never fires, preventing us from sending any camera commands.

**Critical Question:** Why does RemoteCli work but our test_shutter.cpp fails with error 0x8208 in identical conditions?

---

## Hardware Setup

### Camera
- **Model:** Sony ILCE-1 (Alpha 1)
- **Connection:** USB cable (Picture Transfer Protocol - PTP)
- **USB Device ID:** `054c:0d1c Sony Corp. ILCE-1`
- **Mode:** PC Remote mode (PC symbol showing on camera display)
- **Firmware:** Current/up-to-date
- **Power:** Battery charged and installed

### Computer Platform
- **Hardware:** Raspberry Pi (ARM64v8 architecture)
- **Host OS:** Ubuntu 25.04 "Questing"
- **Kernel:** Linux 6.17.0-1003-raspi
- **User:** dpm
- **Working Directory:** `/home/dpm/DPM/sbc/`

### USB Connection Verification
```bash
$ lsusb
Bus 002 Device 002: ID 054c:0d1c Sony Corp. ILCE-1
```
✅ Camera is detected and accessible via USB.

---

## Docker Environment

### Why Docker?

**Problem:** Sony Camera Remote SDK libraries were compiled against libxml2 v2.x (Ubuntu 20.04/22.04 era). Our Raspberry Pi runs Ubuntu 25.04 which uses libxml2 v16.x with an incompatible ABI.

**Symptoms without Docker:**
```
/usr/bin/ld: .../external/crsdk/libCr_Core.so: undefined reference to `xmlParseFile@LIBXML2_2.4.30'
/usr/bin/ld: .../external/crsdk/libCr_Core.so: undefined reference to `xmlNewNode@LIBXML2_2.4.30'
... (multiple similar linker errors)
```

**Solution:** Run everything inside Ubuntu 22.04 Docker container with compatible libxml2 v2.9.13.

### Docker Configuration

**Container Details:**
- **Image:** `payload-manager:latest` (1.03GB)
- **Base:** Ubuntu 22.04
- **Container Name:** `payload-manager`
- **Mode:** Production (restart: always)
- **USB Access:** Full passthrough via `--privileged` and `-v /dev/bus/usb:/dev/bus/usb`

**Dockerfile.prod (relevant sections):**
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    g++ \
    libxml2 \
    libxml2-dev \
    nlohmann-json3-dev \
    libudev-dev \
    libusb-1.0-0 \
    libusb-1.0-0-dev \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Copy Sony SDK
COPY SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8 /app/sdk

# Copy source and build
COPY DPM/sbc /app/sbc
RUN cd /app/sbc && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . --target payload_manager -j4 && \
    mkdir -p CrAdapter && \
    cp -r /app/sdk/external/crsdk/CrAdapter/* CrAdapter/

ENV LD_LIBRARY_PATH=/app/sdk/external/crsdk:/app/sdk/external/crsdk/CrAdapter:$LD_LIBRARY_PATH
```

**Inside Container:**
- Sony SDK: `/app/sdk/`
- Test programs: `/app/sbc/build/`
- CrAdapter directory: `/app/sbc/build/CrAdapter/` (dynamically loaded adapters)

---

## Sony Camera Remote SDK Setup

### SDK Information
- **Version:** 2.00.00
- **Platform:** Linux ARM64v8
- **Location (in container):** `/app/sdk/`
- **Headers:** `/app/sdk/app/CRSDK/`
- **Libraries:** `/app/sdk/external/crsdk/`
- **Namespace:** `SCRSDK`

### Critical Fix: Dynamic Adapter Loading

**Issue:** Initially received error 0x34563 "No adapters available".

**Root Cause:** Sony SDK requires adapters (libCr_PTP_USB.so, libCr_PTP_IP.so) to be loaded dynamically from a `CrAdapter/` subdirectory at runtime, NOT statically linked.

**Solution:**
1. Copy `CrAdapter/` directory to build folder
2. Only link `libCr_Core.so` (NOT the adapter libraries)
3. Adapters load automatically from `./CrAdapter/` at runtime

**CMakeLists.txt (lines 163-169):**
```cmake
target_link_libraries(test_shutter
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)
```

**Result:** ✅ Camera enumeration now works. Error 0x34563 resolved.

---

## What Works

### ✅ Sony's RemoteCli Example Application

**Test Command:**
```bash
$ sudo docker exec payload-manager bash -c "cd /app/sdk/build && ./RemoteCli"
```

**Output:**
```
RemoteSampleApp v2.00.00 running...

Remote SDK version: 2.0.00
Initialize Remote SDK...
Working directory: "/app/sdk/build"
Remote SDK successfully initialized.

Enumerate connected camera devices...
Camera enumeration successful. 1 detected.

[1] ILCE-1 (D0552039A5E8)

Connect to camera with input number...
input>
```

**Result:** ✅ RemoteCli successfully:
- Initializes SDK
- Enumerates camera (finds 1 camera)
- Detects camera model correctly
- Can connect and control camera (when provided input)

### ✅ Our test_camera.cpp Program

**Test Command:**
```bash
$ sudo docker exec payload-manager /app/sbc/build/test_camera
```

**Output:**
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
ID: D0552039A5E8
==========================

Connecting to camera...
[Callback] Camera connected
Successfully connected to camera!
Device handle: 187650688120448

... (additional output showing connection success) ...
```

**Result:** ✅ test_camera.cpp successfully:
- Initializes SDK
- Enumerates camera
- Connects to camera
- **OnConnected callback FIRES** ✅
- Camera enters connected state

---

## What Doesn't Work

### ❌ Our test_shutter.cpp Program

**Test Command:**
```bash
$ sudo docker exec payload-manager /app/sbc/build/test_shutter
```

**Output:**
```
=== Sony Camera Shutter Test ===
This will test taking a photo via USB

Sony SDK: 2.0.0
Initializing SDK...
SDK initialized.

Enumerating cameras (5 sec timeout)...
Found 1 camera(s)

Camera: ILCE-1
Type: USB

Connecting to camera...
Connected! Device handle: 187650688120448
Waiting for OnConnected callback...
[Error] 0x8208
  Still waiting... (2s)
  Still waiting... (4s)
  Still waiting... (6s)
  Still waiting... (8s)
ERROR: Connection callback never received after 10 seconds!
Camera is not ready to accept commands.
```

**Result:** ❌ test_shutter.cpp fails:
- ✅ SDK initializes
- ✅ Camera enumeration works
- ✅ `SDK::Connect()` returns SUCCESS (not a failure code)
- ❌ **OnConnected callback NEVER fires**
- ❌ Error 0x8208 appears in `OnError()` callback immediately
- ❌ Cannot send shutter commands (fail with error 0x8402)

---

## Error Code Analysis

### Error 0x8208 (CrError_Connect_SendCommand)

**From Sony SDK Documentation:**
- **Meaning:** "Sending command failed during connection phase"
- **Context:** This error appears during the connection handshake
- **Implication:** Camera connection is not fully established

**When it occurs:** Immediately after `SDK::Connect()` returns, before OnConnected fires.

### Error 0x8402 (CrError_Api_Insufficient)

**From Sony SDK Documentation:**
- **Meaning:** "Incorrect parameter" or "Insufficient API state"
- **Context:** Returned when calling `SDK::SendCommand()` for shutter

**Why it occurs:** Commands sent before OnConnected callback fires are rejected because camera is not ready.

---

## Code Comparison

### test_shutter.cpp (FAILS)

**File:** `/home/dpm/DPM/sbc/src/test_shutter.cpp`

**Callback Implementation:**
```cpp
class ShutterTestCallback : public SDK::IDeviceCallback
{
public:
    ShutterTestCallback() : connected_(false) {}
    ~ShutterTestCallback() {}

    void OnConnected(SDK::DeviceConnectionVersioin version) override {
        std::cout << "[Callback] Camera connected!" << std::endl;
        connected_ = true;
    }

    void OnDisconnected(CrInt32u error) override {
        std::cout << "[Callback] Camera disconnected. Error: 0x"
                  << std::hex << error << std::endl;
        connected_ = false;
    }

    void OnPropertyChanged() override {}
    void OnLvPropertyChanged() override {}

    void OnWarning(CrInt32u warning) override {
        std::cout << "[Warning] 0x" << std::hex << warning << std::endl;
    }

    void OnError(CrInt32u error) override {
        std::cout << "[Error] 0x" << std::hex << error << std::endl;
    }

    bool isConnected() const { return connected_; }

private:
    bool connected_;
};
```

**Connection Code (lines 95-143):**
```cpp
// Create callback and connect
std::cout << "\nConnecting to camera..." << std::endl;
ShutterTestCallback callback;
SDK::CrDeviceHandle device_handle = 0;

auto* non_const_camera_info = const_cast<SDK::ICrCameraObjectInfo*>(camera_info);

auto connect_status = SDK::Connect(
    non_const_camera_info,
    &callback,
    &device_handle,
    SDK::CrSdkControlMode_Remote,
    SDK::CrReconnecting_ON
);

if (CR_FAILED(connect_status)) {
    std::cerr << "ERROR: Failed to connect! Status: 0x"
              << std::hex << connect_status << std::endl;
    camera_list->Release();
    SDK::Release();
    return 1;
}

std::cout << "Connected! Device handle: " << device_handle << std::endl;

// Wait for connection callback
std::cout << "Waiting for OnConnected callback..." << std::endl;
int wait_count = 0;
while (!callback.isConnected() && wait_count < 20) {
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    wait_count++;
    if (wait_count % 4 == 0) {
        std::cout << "  Still waiting... (" << (wait_count / 2) << "s)" << std::endl;
    }
}

if (!callback.isConnected()) {
    std::cerr << "ERROR: Connection callback never received after "
              << (wait_count / 2) << " seconds!" << std::endl;
    std::cerr << "Camera is not ready to accept commands." << std::endl;
    SDK::Disconnect(device_handle);
    camera_list->Release();
    SDK::Release();
    return 1;
}

std::cout << "OnConnected callback received! Camera is ready." << std::endl;

// Give camera a bit more time to fully stabilize
std::cout << "Waiting for camera to fully stabilize..." << std::endl;
std::this_thread::sleep_for(std::chrono::milliseconds(500));

// Now test the shutter!
// ... (shutter commands follow)
```

### RemoteCli (WORKS)

**File (reference):** `/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/app/RemoteCli.cpp`

We know RemoteCli works but haven't identified the specific difference in implementation yet.

---

## Debugging Attempts

### Attempts Made

1. **Increased wait timeout:** 500ms → 10 seconds
   - **Result:** No change, callback still never fires

2. **Restarted Docker container:** Fresh SDK state
   - **Result:** No change

3. **Killed payload_manager:** Avoid potential SDK conflicts
   - **Result:** No change

4. **Added detailed callback logging:** See exactly what callbacks fire
   - **Result:** Only `OnError(0x8208)` fires, never `OnConnected()`

5. **Verified CrAdapter/ directory:** Ensure adapters available
   - **Result:** ✅ Present and accessible

6. **Compared with test_camera.cpp:** Same connection code pattern
   - **Result:** test_camera works, test_shutter doesn't (unclear why)

### Observations

**Differences between test_camera.cpp (works) and test_shutter.cpp (fails):**
- Both use same SDK initialization sequence
- Both use same connection parameters
- Both use same callback pattern
- Both built with same CMakeLists.txt configuration
- Both run in same Docker environment
- test_camera.cpp: OnConnected fires ✅
- test_shutter.cpp: OnConnected never fires, error 0x8208 ❌

**Question:** What is the difference?

---

## Environment Details

### Build Configuration

**CMakeLists.txt (test_shutter target):**
```cmake
# Create test_shutter executable
add_executable(test_shutter src/test_shutter.cpp)

# Add Sony SDK include directories
target_include_directories(test_shutter
    PRIVATE
        ${SONY_SDK_INCLUDE}
)

# Link Sony SDK libraries
target_link_libraries(test_shutter
    PRIVATE
        -Wl,--no-as-needed
        pthread
        ${SONY_SDK_LIB_DIR}/libCr_Core.so
        xml2
        -Wl,--as-needed
)

# Set RPATH for test_shutter
set_target_properties(test_shutter PROPERTIES
    BUILD_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
    INSTALL_RPATH "${SONY_SDK_LIB_DIR}:${SONY_SDK_ADAPTER_DIR}"
)
```

### Library Dependencies

**ldd output (inside container):**
```bash
$ ldd /app/sbc/build/test_shutter
    libCr_Core.so => /app/sdk/external/crsdk/libCr_Core.so
    libxml2.so.2 => /lib/aarch64-linux-gnu/libxml2.so.2
    libpthread.so.0 => /lib/aarch64-linux-gnu/libpthread.so.0
    libstdc++.so.6 => /lib/aarch64-linux-gnu/libstdc++.so.6
    libgcc_s.so.1 => /lib/aarch64-linux-gnu/libgcc_s.so.1
    libc.so.6 => /lib/aarch64-linux-gnu/libc.so.6
    ... (additional dependencies)
```

**CrAdapter directory contents:**
```bash
$ ls /app/sbc/build/CrAdapter/
libCr_PTP_IP.so
libCr_PTP_USB.so
```

---

## Questions for External Support

1. **Why does OnConnected callback never fire in test_shutter.cpp but works in test_camera.cpp and RemoteCli?**

2. **What does error 0x8208 (CrError_Connect_SendCommand) specifically indicate?**
   - What command is failing during connection?
   - Is there additional logging we can enable?

3. **What are the exact requirements for the connection handshake to succeed?**
   - Does camera need to be in a specific state?
   - Are there any camera settings that affect USB connection?
   - Is there a timing requirement we're missing?

4. **Is there a known issue with the connection sequence on ARM64v8 Linux?**

5. **Can you provide a minimal working example of camera connection and shutter control?**
   - Specifically for USB PTP connection
   - That we can compare against our implementation

6. **Are there any SDK debug logging facilities we can enable?**
   - To see what's happening during the connection phase
   - To identify where the handshake is failing

7. **Is the callback being executed on a different thread?**
   - Could there be a threading issue we're missing?
   - Should we be using mutexes or atomics differently?

8. **Is there documentation on the internal connection state machine?**
   - To understand what state transitions are expected
   - What triggers OnConnected vs OnError

---

## Request for Support

We need assistance identifying why our test_shutter.cpp program experiences connection error 0x8208 while RemoteCli and test_camera.cpp work correctly in the identical environment. We have successfully:

✅ Built a working Docker environment
✅ Resolved adapter loading issues
✅ Achieved camera enumeration
✅ Verified USB connectivity
✅ Confirmed RemoteCli works
✅ Confirmed test_camera.cpp connects successfully

But we are blocked on:

❌ Getting OnConnected callback to fire in test_shutter.cpp
❌ Understanding what causes error 0x8208
❌ Sending shutter commands to camera

**Any guidance on resolving this connection handshake issue would be greatly appreciated.**

---

## Contact Information

**Project:** DPM Payload Manager
**Repository:** https://github.com/unmanned-systems-uk/DPM
**Branch:** main
**Commit:** e3173e7 (Sony SDK integration: Camera enumeration working, shutter testing in progress)

**Test Programs:**
- `/home/dpm/DPM/sbc/src/test_camera.cpp` - Works ✅
- `/home/dpm/DPM/sbc/src/test_shutter.cpp` - Fails with 0x8208 ❌

---

**Document Status:** Ready for external support request
**Last Updated:** October 24, 2025
**Priority:** HIGH - Blocking Phase 2 camera integration
