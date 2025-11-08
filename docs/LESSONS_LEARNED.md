# Lessons Learned - DPM-V2 Development

**Last Updated:** 2025-11-07
**Document Version:** 1.0.0

This document captures critical lessons learned during DPM-V2 development to prevent future issues and inform deployment decisions.

---

## Table of Contents

1. [Critical Issues](#critical-issues)
2. [Deployment & Infrastructure](#deployment--infrastructure)
3. [Docker & Containerization](#docker--containerization)
4. [Sony SDK Integration](#sony-sdk-integration)
5. [Network Configuration](#network-configuration)

---

## Critical Issues

### 1. Sony SDK Camera Enumeration Failure (Error 0x34563)

**Date Discovered:** 2025-11-07
**Severity:** 🔴 **CRITICAL** - Complete camera failure
**Error Code:** `0x34563` - "No adapters available"

#### Problem Description

After Docker container restarts or rebuilds, camera enumeration fails with error 0x34563, preventing all camera operations. The camera is physically connected and visible via `lsusb`, but the Sony SDK cannot enumerate it.

#### Root Cause

**Missing `CrAdapter/` directory in the build output folder.**

The Sony Camera Remote SDK requires adapter libraries (`libCr_PTP_USB.so`, `libCr_PTP_IP.so`) to be present in a `CrAdapter/` subdirectory relative to the executable. These adapters are responsible for camera enumeration over USB and network.

**Directory Structure Required:**
```
/app/sbc/build/
├── payload_manager           # Executable
└── CrAdapter/                 # REQUIRED - Adapters directory
    ├── libCr_PTP_USB.so       # USB adapter
    ├── libCr_PTP_IP.so        # Network adapter
    ├── libusb-1.0.so
    └── libssh2.so
```

**What Happens Without CrAdapter:**
- Sony SDK initializes successfully (v2.0.0)
- `SDK::EnumCameraObjects()` returns 0x34563
- No cameras enumerated even though physically connected
- All camera commands fail with "Camera not connected"

#### Timeline of Discovery

1. **18:03** - Camera working fine, fully connected
2. **18:13** - Docker container restarted
3. **18:13** - Camera enumeration begins failing with 0x34563
4. **23:30** - Issue persists through multiple restart attempts
5. **23:42** - Root cause identified: Missing `CrAdapter/` directory
6. **23:42** - Fixed by: `cp -r /app/sdk/external/crsdk/CrAdapter /app/sbc/build/`
7. **23:45** - Camera reconnects successfully

#### Solution

**Production Dockerfile (Dockerfile.prod) - ALREADY INCLUDES FIX:**

Lines 42-43 in `sbc/Dockerfile.prod`:
```dockerfile
mkdir -p CrAdapter && \
cp -r /app/sdk/external/crsdk/CrAdapter/* CrAdapter/
```

**Manual Fix (if needed):**
```bash
# Inside running container
docker exec payload-manager cp -r /app/sdk/external/crsdk/CrAdapter /app/sbc/build/

# Then restart
docker restart payload-manager
```

**For Fresh Builds:**
```bash
# Use production Dockerfile
cd ~/DPM-V2
docker build -f sbc/Dockerfile.prod -t payload-manager:latest .

# Verify CrAdapter exists
docker exec payload-manager ls /app/sbc/build/CrAdapter/
```

#### Prevention

**✅ DO:**
- Always use `Dockerfile.prod` for production builds
- Verify CrAdapter directory exists after build: `docker exec <container> ls /app/sbc/build/CrAdapter/`
- Include CrAdapter copy step in any custom build scripts
- Document CrAdapter requirement in deployment guides

**❌ DON'T:**
- Use development Dockerfile for production containers
- Manually rebuild inside container without copying adapters
- Delete or move CrAdapter directory

#### Impact

**Before Fix:**
- Camera enumeration: ❌ FAIL (0x34563)
- All camera operations: ❌ BLOCKED
- System uptime since last build: CRITICAL

**After Fix:**
- Camera enumeration: ✅ SUCCESS
- Camera operations: ✅ WORKING
- Deployment reliability: ✅ IMPROVED

#### Related Issues

- Issue #33: NVMe Migration - Deployment scripts must use `Dockerfile.prod`
- Previous occurrence documented in `sbc/docs/DOCKER_SETUP.md:393-408`

---

## Deployment & Infrastructure

### 2. USB Permissions for Sony Camera

**Date Discovered:** 2025-11-07
**Severity:** 🟡 **HIGH** - Camera connection failure

#### Problem

Camera enumeration fails after fresh OS install or system updates even when physically connected and in PC Remote mode.

#### Root Cause

Missing udev rules for Sony camera USB permissions. Without proper permissions (0666, plugdev group), the Docker container cannot access the USB device.

#### Solution

**Create udev rules file:**
```bash
sudo tee /etc/udev/rules.d/99-sony-camera.rules << 'EOF'
# Sony Camera USB permissions for DPM-V2
# Allows Docker container to access Sony camera via USB
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="*", MODE="0666", GROUP="plugdev"
EOF

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Verification:**
```bash
lsusb | grep Sony
# Bus 004 Device 019: ID 054c:0d1c Sony Corp. ILCE-1

ls -l /dev/bus/usb/004/019
# crw-rw-rw- 1 root plugdev 189, 402 Nov  7 23:30 /dev/bus/usb/004/019
```

**Included In:**
- ✅ NVMe deployment script: `tools/deployment/deploy-air-side.sh` (lines 108-117)
- ✅ Production Dockerfile: USB device passed with `--device /dev/bus/usb:/dev/bus/usb`

---

## Docker & Containerization

### 3. Container Restart Persistence

**Lesson:** Docker container restarts can lose runtime changes made inside container.

**Impact:**
- Binary rebuilt inside container: ❌ Lost on restart
- CrAdapter manually copied: ❌ Lost on restart
- Adapter files in image: ✅ Persistent

**Best Practice:**
- Always rebuild Docker image for code changes
- Never rely on `docker exec` modifications for permanent changes
- Use volumes for logs and data, not binaries

---

## Sony SDK Integration

### 4. AF Hold in Manual Focus Mode

**Date Discovered:** 2025-11-07
**Error Code:** `0x8402` - `CrError_Api_InvalidCalled`

#### Finding

**AF Hold (Push Auto Focus) is NOT supported in Manual Focus mode.**

Even though the Sony SDK includes `TouchFunctionInMF` property suggesting AF should work in MF mode, calling `SetDeviceProperty(CrDeviceProperty_PushAutoFocus)` while in Manual Focus returns error 0x8402.

**Test Results:**
- Camera in Manual Focus (focus_mode = 0x1)
- AF Hold PRESS command sent
- Result: `0x8402 - CrError_Api_InvalidCalled`

**Conclusion:** This is a Sony SDK/camera limitation, not a code issue. Users must switch to AF-S, AF-C, or AF-A mode to use AF Hold.

**Related:** Issue #2

---

## Network Configuration

### 5. Static IP Requirement for VXLAN Bridge

**Critical:** Air-Side MUST have static IP `192.168.144.10/24` on eth0 for VXLAN bridge to H16 Ground-Side.

**Configuration:** `/etc/dhcpcd.conf`
```bash
interface eth0
static ip_address=192.168.144.10/24
noipv6
```

**Included In:**
- ✅ NVMe deployment script: `tools/deployment/deploy-air-side.sh` (lines 95-102)
- ✅ Deployment checklist: `tools/deployment/NVME_MIGRATION_CHECKLIST.md`

**Verification:**
```bash
ip addr show eth0
# Should show: inet 192.168.144.10/24

ping 192.168.144.11  # H16 Ground-Side
```

---

## Appendix

### Error Code Reference

| Error Code | Meaning | Typical Cause |
|------------|---------|---------------|
| 0x34563 | No adapters available | Missing CrAdapter/ directory |
| 0x8402 | CrError_Api_InvalidCalled | Operation not valid in current camera mode |
| 0x8208 | Connection timeout | OnConnected callback timeout |

### Useful Diagnostic Commands

```bash
# Check camera USB connection
lsusb | grep Sony

# Check USB device permissions
ls -l /dev/bus/usb/004/<device_number>

# Check Docker container CrAdapter
docker exec payload-manager ls /app/sbc/build/CrAdapter/

# Check camera connection in logs
docker logs payload-manager | grep "Camera fully connected"

# Check for enumeration errors
docker logs payload-manager | grep "0x34563"
```

---

**Document Maintenance:**
- Add new lessons as critical issues are discovered
- Update with resolution details when fixes are deployed
- Reference related GitHub issues
- Keep error code reference up to date

