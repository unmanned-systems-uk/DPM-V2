# Sony Camera Remote SDK Installation Guide
**Version:** 1.0
**Created:** 2025-11-09
**SDK Version:** CrSDK_v2.00.00_20250805a_Linux64ARMv8

---

## Overview

This document details the installation and configuration of the Sony Camera Remote SDK required for DPM-V2 Air-Side payload manager.

---

## SDK Information

### Current Installation

**Installed Version:** `CrSDK_v2.00.00_20250805a_Linux64ARMv8`
**Installation Path:** `/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8`
**Platform:** Linux ARM64v8 (Raspberry Pi 5)
**Release Date:** 2025-08-05

### Obtaining the SDK

**Source:** Sony Developer Portal

**Access Requirements:**
- Sony Developer Account
- Camera Remote SDK License Agreement

**Where to Request:**
1. Visit: https://support.d-imaging.sony.co.jp/app/sdk/en/
2. Register for developer account
3. Request Camera Remote SDK access
4. Download Linux ARM64 version

**Alternative:** Contact Sony Professional support for SDK access

---

## Installation Procedure

### Step 1: Download SDK

Download the appropriate SDK package:
- **Filename:** `CrSDK_v2.00.00_20250805a_Linux64ARMv8.tar.gz` (or .zip)
- **Size:** Approximately 50-100 MB
- **Checksum:** Verify with Sony-provided hash (if available)

### Step 2: Extract SDK

```bash
# Extract to home directory
cd /home/dpm
tar -xzf CrSDK_v2.00.00_20250805a_Linux64ARMv8.tar.gz

# Or if zip format:
unzip CrSDK_v2.00.00_20250805a_Linux64ARMv8.zip

# Verify extraction
ls -la CrSDK_v2.00.00_20250805a_Linux64ARMv8/
```

**Expected directories:**
```
CrSDK_v2.00.00_20250805a_Linux64ARMv8/
├── app/                    # Example applications
├── doc/                    # SDK documentation
├── external/               # SDK libraries
│   └── crsdk/
│       ├── libCr_Core.so   # Main SDK library
│       ├── CrAdapter/      # Dynamic adapter libraries
│       │   ├── libCr_PTP_USB.so
│       │   └── libCr_PTP_IP.so
│       └── ...
├── include/                # Header files
└── README.md
```

### Step 3: Set Permissions

```bash
# Ensure proper ownership
sudo chown -R dpm:dpm /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8

# Set execute permissions on libraries
chmod -R 755 /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8
```

### Step 4: Verify Installation

```bash
# Check library dependencies
cd /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/external/crsdk
ldd libCr_Core.so
```

**Expected output:**
```
libCr_Core.so => (0x...)
libxml2.so.2 => /lib/aarch64-linux-gnu/libxml2.so.2
libpthread.so.0 => /lib/aarch64-linux-gnu/libpthread.so.0
libc.so.6 => /lib/aarch64-linux-gnu/libc.so.6
...
```

**All dependencies should resolve** - no "not found" errors.

---

## SDK Components

### Libraries

#### Core Library
- **File:** `external/crsdk/libCr_Core.so`
- **Purpose:** Main SDK functionality
- **Size:** ~5-10 MB
- **Dependencies:** libxml2, pthread, libc

#### Adapter Libraries (Dynamic Loading)
- **Directory:** `external/crsdk/CrAdapter/`
- **Files:**
  - `libCr_PTP_USB.so` - USB camera communication
  - `libCr_PTP_IP.so` - Network camera communication
- **Purpose:** Transport layer adapters
- **Loading:** Dynamically loaded by libCr_Core.so at runtime

### Headers

- **Directory:** `include/`
- **Key files:**
  - `CrDeviceProperty.h` - Camera property definitions
  - `CameraRemote_SDK.h` - Main SDK interface
  - `ICrCameraObjectInfo.h` - Camera object interface

### Documentation

- **Directory:** `doc/`
- **Files:**
  - SDK API Reference (HTML or PDF)
  - Release notes
  - Known issues
  - Sample code documentation

### Example Applications

- **Directory:** `app/`
- **RemoteCli:** Command-line example application
- **Purpose:** SDK functionality demonstration and testing

---

## Testing SDK Installation

### Test 1: Library Dependencies

```bash
cd /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/external/crsdk
ldd libCr_Core.so

# Should show all dependencies resolved
# No "not found" errors
```

### Test 2: RemoteCli Example

```bash
# Connect Sony camera via USB
# Set camera to PC Remote mode

cd /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/app
./RemoteCli
```

**Expected output:**
```
RemoteCli v2.00.00
Initializing SDK...
Enumerating cameras...
Found 1 camera(s):
  [0] Sony ILCE-1 (USB)
```

**If errors occur:**
- Check USB buffer setting (should be 150MB)
- Verify camera is in PC Remote mode
- Check USB cable connection

### Test 3: SDK Version Check

```bash
cd /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/app
./RemoteCli --version
```

Should display: `v2.00.00` or similar

---

## Integration with DPM-V2

### Docker Build Integration

The SDK is automatically copied into the Docker container during build:

**In Dockerfile.prod:**
```dockerfile
# Copy Sony SDK from build context
COPY CrSDK_v2.00.00_20250805a_Linux64ARMv8 /app/sdk
```

**Build script (`build_container.sh`) does:**
1. Copies `~/CrSDK_v2.00.00_20250805a_Linux64ARMv8` to parent directory
2. Docker build includes SDK in image
3. Sets `LD_LIBRARY_PATH` to SDK libraries

### Runtime Library Path

**Container environment:**
```bash
LD_LIBRARY_PATH=/app/sdk/external/crsdk:/app/sdk/external/crsdk/CrAdapter:$LD_LIBRARY_PATH
```

### CMake Integration

**In CMakeLists.txt:**
```cmake
# Sony SDK paths
set(SONY_SDK_ROOT "/app/sdk")
set(SONY_SDK_INCLUDE "${SONY_SDK_ROOT}/include")
set(SONY_SDK_LIB "${SONY_SDK_ROOT}/external/crsdk")

# Link against Sony SDK
target_link_libraries(payload_manager
    ${SONY_SDK_LIB}/libCr_Core.so
)

# Copy CrAdapter for dynamic loading
file(COPY ${SONY_SDK_LIB}/CrAdapter
     DESTINATION ${CMAKE_BINARY_DIR})
```

---

## Troubleshooting

### Error: "libxml2.so.2: version LIBXML2_2.9.0 not found"

**Cause:** Host system has incompatible libxml2 version

**Solution:** Use Docker container with Ubuntu 22.04 (provided in Dockerfile.prod)

```bash
# Check libxml2 version in container
docker run -it --rm payload-manager:latest ldd /app/sdk/external/crsdk/libCr_Core.so | grep libxml2
```

### Error: "CrError_Generic - No adapters available (0x34563)"

**Cause:** CrAdapter directory not copied to build directory

**Solution:**
```bash
# Verify CrAdapter exists in build
docker exec payload-manager ls -la /app/sbc/build/CrAdapter/

# If missing, rebuild container
cd ~/DPM-V2/sbc
./build_container.sh
```

### Error: "CrError_Connect_SendCommand (0x8208)"

**Cause:** USB buffer too small (16MB default insufficient)

**Solution:** Increase USB buffer to 150MB (see FRESH_INSTALL_GUIDE.md Section 4.1)

```bash
# Check current setting
cat /sys/module/usbcore/parameters/usbfs_memory_mb

# Should be: 150
# If not, add to /boot/firmware/cmdline.txt:
# usbcore.usbfs_memory_mb=150
```

### Error: Permission denied accessing camera

**Solution:**
```bash
# Run container with --privileged flag (already in run_container.sh)
# OR create udev rule:
sudo nano /etc/udev/rules.d/99-sony-camera.rules
```

**Add:**
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", MODE="0666", GROUP="plugdev"
```

**Reload:**
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## SDK Version History

### v2.00.00 (20250805a)
- **Platform:** Linux ARM64v8
- **Status:** Current (installed)
- **Compatibility:** Raspberry Pi 5
- **Known Issues:** Requires libxml2 2.9.x (Ubuntu 22.04)

---

## Upgrade Procedure

**To upgrade SDK:**

1. Download new SDK version
2. Extract to `/home/dpm/CrSDK_<version>`
3. Update Dockerfile.prod:
   ```dockerfile
   COPY CrSDK_<new_version> /app/sdk
   ```
4. Rebuild Docker container:
   ```bash
   cd ~/DPM-V2/sbc
   ./build_container.sh
   ```
5. Test with RemoteCli
6. Deploy updated container

---

## Backup & Recovery

### Backup SDK

```bash
# Create tar archive
cd /home/dpm
tar -czf CrSDK_v2.00.00_backup_$(date +%Y%m%d).tar.gz CrSDK_v2.00.00_20250805a_Linux64ARMv8

# Copy to safe location
cp CrSDK_v2.00.00_backup_*.tar.gz ~/backups/
```

### Restore SDK

```bash
# Extract from backup
cd /home/dpm
tar -xzf ~/backups/CrSDK_v2.00.00_backup_YYYYMMDD.tar.gz

# Verify
ls -la CrSDK_v2.00.00_20250805a_Linux64ARMv8/
```

---

## License & Legal

**License:** Sony Camera Remote SDK License Agreement
**Restrictions:**
- SDK is proprietary Sony software
- Distribution restricted per license agreement
- Commercial use requires Sony approval

**Contact Sony for licensing questions.**

---

## Additional Resources

**Sony Developer Portal:**
- https://support.d-imaging.sony.co.jp/app/sdk/en/

**SDK Documentation:**
- Installed in: `/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/doc/`
- DPM-V2 reference: `docs/AIR_SIDE/SONY_SDK_REFERENCE.md`

**DPM-V2 Documentation:**
- Fresh Install Guide: `sbc/docs/FRESH_INSTALL_GUIDE.md`
- System Dependencies: `sbc/docs/SYSTEM_DEPENDENCIES.md`
- Progress Tracking: `sbc/docs/PROGRESS_AND_TODO.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Maintained By:** CC-Air-Side
**Status:** Production
