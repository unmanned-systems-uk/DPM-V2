# DPM Migration Guide: Raspberry Pi 4 to Raspberry Pi 5

**Date:** October 24, 2025
**Current System:** Raspberry Pi 4 Model B Rev 1.4
**Target System:** Raspberry Pi 5
**Project:** DPM Payload Manager - Sony Camera Integration

---

## Table of Contents

1. [Overview](#overview)
2. [OS Selection Considerations](#os-selection-considerations)
3. [Current System Configuration](#current-system-configuration)
4. [Pre-Migration Checklist](#pre-migration-checklist)
5. [Migration Steps](#migration-steps)
6. [Hardware-Specific Configurations](#hardware-specific-configurations)
7. [Docker Migration](#docker-migration)
8. [Post-Migration Verification](#post-migration-verification)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the migration of the DPM Payload Manager project from a Raspberry Pi 4 to a Raspberry Pi 5. The project uses:

- **Sony Camera Remote SDK v2.00.00** for Sony A1 camera control
- **Docker containerization** (Ubuntu 22.04) for libxml2 compatibility
- **USB PTP connection** to Sony ILCE-1 camera
- **Custom payload manager** application for drone integration

### Key Considerations

- The Raspberry Pi 5 has improved USB performance and power delivery
- Both systems use ARM64v8 architecture (no recompilation needed)
- Docker containers and images are portable between Pi 4 and Pi 5
- System-level configurations (USB memory limits, boot parameters) need to be replicated

---

## OS Selection Considerations

### Current OS: Ubuntu 25.04 "Questing"

You're currently running Ubuntu 25.04 on the Raspberry Pi 4. Here are considerations for choosing an OS for the new Raspberry Pi 5:

#### Option 1: Continue with Ubuntu 25.04 (Current Choice)

**Pros:**
- ✅ **No changes needed** - Same workflow, same commands, same configuration
- ✅ **Familiarity** - You already know the system
- ✅ **Cutting-edge packages** - Latest kernel (6.17.0) and system tools
- ✅ **Migration simplicity** - Direct transfer of configurations and scripts
- ✅ **Docker isolation** - Host OS version doesn't impact containerized Sony SDK (still runs Ubuntu 22.04)
- ✅ **ARM64 optimization** - Ubuntu 25.04 includes latest ARM64 optimizations for Pi 5

**Cons:**
- ⚠️ **Bleeding edge** - Potential for undiscovered bugs in newer kernels
- ⚠️ **Less community support** - Fewer Pi-specific guides for Ubuntu 25.04
- ⚠️ **libxml2 compatibility** - Required Docker containerization for Sony SDK (already solved)

**Verdict:** **Recommended to continue with Ubuntu 25.04**
- Your Docker setup already isolates the SDK compatibility issues
- You've proven the system works reliably
- No reason to change if it's working

#### Option 2: Ubuntu 24.04 LTS "Noble Numbat"

**Pros:**
- ✅ **LTS support** - Long-term support until 2029
- ✅ **More stable** - Well-tested packages
- ✅ **Better documentation** - More community guides and support
- ✅ **Docker works identically** - Same containerization approach
- ✅ **5-year security updates** - Extended support lifecycle

**Cons:**
- ⚠️ **Migration effort** - Need to set up new OS instead of direct transfer
- ⚠️ **Older kernel** - May not have latest Pi 5 optimizations (though still very good)
- ⚠️ **Package versions** - Slightly older versions of system tools

**Verdict:** Good choice if you prefer stability over cutting-edge

#### Option 3: Raspberry Pi OS (64-bit)

**Pros:**
- ✅ **Official Pi OS** - Optimized specifically for Raspberry Pi hardware
- ✅ **Excellent Pi 5 support** - Best hardware compatibility and drivers
- ✅ **Large community** - Most tutorials written for Raspberry Pi OS
- ✅ **Pre-configured** - Many Pi-specific optimizations out of the box
- ✅ **Debian-based** - Similar to Ubuntu (apt, systemd, etc.)

**Cons:**
- ⚠️ **Major migration effort** - Different OS requires reconfiguration
- ⚠️ **Package differences** - Some packages may have different names or versions
- ⚠️ **Debian vs Ubuntu differences** - Subtle variations in system configuration
- ⚠️ **Docker works the same** - No advantage for containerized workloads
- ⚠️ **Desktop environment** - May include unnecessary GUI components (unless using Lite version)

**Verdict:** Best for Pi-specific projects, but unnecessary overhead for your use case

#### Option 4: Other Linux Distributions

**Options:** Debian, Fedora, Arch Linux ARM, etc.

**Verdict:** Not recommended - No significant advantages for this project, adds complexity

### Recommendation

**Continue with Ubuntu 25.04** for the following reasons:

1. **Docker Isolation Works** - You've already solved the libxml2 compatibility issue with Docker. The host OS version is largely irrelevant since your critical software runs inside Ubuntu 22.04 container.

2. **Proven Configuration** - Your current setup works. You have:
   - Working Docker configuration
   - Correct USB settings (150MB memory limit)
   - Proper boot parameters
   - Tested camera integration

3. **Simplest Migration** - Moving to the same OS version means:
   - Copy configurations directly
   - No need to relearn system management
   - Same Docker commands and behaviors
   - Identical file paths and system structure

4. **Pi 5 Optimizations** - Ubuntu 25.04 kernel (6.17.0) includes latest ARM64 and Pi 5 optimizations.

5. **Consistency** - Easier to maintain and document when both systems run identical OS.

### If You Decide to Change OS

If you prefer to switch to Ubuntu 24.04 LTS for long-term stability:

**Additional Migration Steps Required:**

```bash
# On new Raspberry Pi 5

# 1. Install Ubuntu 24.04 LTS Server ARM64
# Download from: https://ubuntu.com/download/raspberry-pi

# 2. Follow same migration steps from guide
# All Docker, Sony SDK, and application steps remain identical

# 3. Be aware of minor differences:
# - Kernel version (6.8.x instead of 6.17.x)
# - Package versions slightly older
# - System configuration largely the same
```

**Migration time:** Add 30-60 minutes for OS installation and initial setup.

### System Requirements for Pi 5

Regardless of OS choice, ensure:
- **64-bit ARM OS** (aarch64/ARM64v8) - Required for Sony SDK
- **Kernel 5.15+** - For proper USB 3.0 support
- **Docker support** - Essential for containerized Sony SDK
- **systemd** - For service management (most modern Linux distros)

---

## Current System Configuration

### Hardware
- **Model:** Raspberry Pi 4 Model B Rev 1.4
- **Architecture:** ARM64 (aarch64)
- **OS:** Ubuntu 25.04 "Questing"
- **Kernel:** Linux 6.17.0-1003-raspi
- **Docker:** Version 28.5.1

### Software Stack
- **Sony SDK:** CrSDK_v2.00.00_20250805a_Linux64ARMv8
- **Docker Container:** payload-manager:latest (1.04GB, Ubuntu 22.04 base)
- **C++ Standard:** C++17
- **Build System:** CMake 3.16+

### Critical System Settings

#### 1. USB Memory Limit
**Location:** `/sys/module/usbcore/parameters/usbfs_memory_mb`
**Current Value:** 150 MB
**Purpose:** Increased from default 16MB for high-bandwidth USB camera data transfer

#### 2. Boot Configuration
**Location:** `/boot/firmware/cmdline.txt`
**Current Configuration:**
```
cfg80211.ieee80211_regdom=GB usbcore.usbfs_memory_mb=150
```

**Parameters:**
- `cfg80211.ieee80211_regdom=GB` - WiFi regulatory domain (UK)
- `usbcore.usbfs_memory_mb=150` - USB memory limit (persistent across reboots)

#### 3. Docker Configuration
**Container Name:** `payload-manager`
**Image:** `payload-manager:latest`
**Status:** Running with auto-restart
**USB Access:** Full passthrough via `--privileged` mode

### Network Ports
- **5000/tcp** - TCP command/control interface
- **5001/udp** - UDP discovery/broadcast
- **5002/udp** - UDP data/telemetry

---

## Pre-Migration Checklist

### Data Backup

- [ ] Export Docker container: `docker save payload-manager:latest > payload-manager.tar`
- [ ] Backup source code: `/home/dpm/DPM/` directory
- [ ] Backup Sony SDK: `/home/dpm/SonySDK/` directory (if present on host)
- [ ] Export configuration files: `/boot/firmware/cmdline.txt`
- [ ] Document running container configuration: `docker inspect payload-manager > container-config.json`

### Prepare New Raspberry Pi 5

- [ ] Install Ubuntu 25.04 (or latest Ubuntu Server ARM64)
- [ ] Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Add user to docker group: `sudo usermod -aG docker $USER`
- [ ] Verify architecture: `dpkg --print-architecture` (should be `arm64`)

### Network Preparation

- [ ] Document current network configuration (IP address, hostname)
- [ ] Decide if keeping same hostname/IP or changing
- [ ] Update DNS/network documentation if IP changes

---

## Migration Steps

### Step 1: Prepare Source Files on New Pi 5

```bash
# On new Raspberry Pi 5
ssh dpm@new-pi5

# Create project directory
mkdir -p /home/dpm/DPM
cd /home/dpm

# Transfer source code from old Pi 4
# Option A: Using rsync over network
rsync -avz --progress dpm@old-pi4:/home/dpm/DPM/ /home/dpm/DPM/

# Option B: Using git (if repository is up to date)
git clone https://github.com/unmanned-systems-uk/DPM.git
cd DPM
git checkout main
```

### Step 2: Transfer Sony SDK

```bash
# Sony SDK is large (~500MB), choose appropriate method

# Option A: From old Pi 4 via rsync
rsync -avz --progress dpm@old-pi4:/home/dpm/SonySDK/ /home/dpm/SonySDK/

# Option B: From original download/archive
# (Copy from your backup location)

# Verify SDK structure
ls -la /home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8/
# Should contain: app/, external/, build/, etc.
```

### Step 3: Configure System Settings

#### Set USB Memory Limit (Persistent)

```bash
# Edit boot configuration
sudo nano /boot/firmware/cmdline.txt

# Add or modify to include:
cfg80211.ieee80211_regdom=GB usbcore.usbfs_memory_mb=150

# Save and reboot
sudo reboot

# After reboot, verify setting
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Should output: 150
```

#### Alternative: Temporary USB Setting (for testing)

```bash
# Set until next reboot
sudo sh -c 'echo 150 > /sys/module/usbcore/parameters/usbfs_memory_mb'
```

---

## Docker Migration

### Method 1: Transfer Docker Image (Recommended)

**On old Raspberry Pi 4:**
```bash
# Export the Docker image
docker save payload-manager:latest | gzip > payload-manager.tar.gz

# Transfer to new Pi 5 (via scp, rsync, or USB drive)
scp payload-manager.tar.gz dpm@new-pi5:/home/dpm/
```

**On new Raspberry Pi 5:**
```bash
# Import the Docker image
gunzip -c payload-manager.tar.gz | docker load

# Verify image loaded
docker images | grep payload-manager
# Should show: payload-manager   latest   f20b2b77bc8f   ...   1.04GB
```

### Method 2: Rebuild Container (If modifications needed)

```bash
# On new Raspberry Pi 5
cd /home/dpm/DPM/sbc

# Build using production Dockerfile
docker build -f Dockerfile.prod \
  --build-context SonySDK=/home/dpm/SonySDK \
  --build-context DPM=/home/dpm/DPM \
  -t payload-manager:latest .
```

### Step 4: Run Docker Container

```bash
# Stop any existing container
docker stop payload-manager 2>/dev/null || true
docker rm payload-manager 2>/dev/null || true

# Run container with same configuration as Pi 4
docker run -d \
  --name payload-manager \
  --restart always \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  -p 5000:5000/tcp \
  -p 5001:5001/udp \
  -p 5002:5002/udp \
  payload-manager:latest

# Verify container is running
docker ps | grep payload-manager

# Check logs
docker logs -f payload-manager
```

---

## Post-Migration Verification

### 1. Container Health Check

```bash
# Check container status
docker ps -a

# Expected output:
# CONTAINER ID   IMAGE                    STATUS         NAMES
# xxxxxxxxxx     payload-manager:latest   Up X minutes   payload-manager

# View logs
docker logs payload-manager

# Should show:
# - Payload Manager starting
# - Sony SDK initialized
# - TCP server listening on port 5000
# - UDP broadcaster active
```

### 2. Camera Connection Test

```bash
# Connect Sony A1 camera via USB
# Set camera to "PC Remote" mode

# Verify USB detection
lsusb | grep Sony
# Expected: Bus 00X Device 00X: ID 054c:0d1c Sony Corp. ILCE-1

# Run camera test (inside container)
docker exec payload-manager /app/sbc/build/test_camera

# Expected output:
# *** Sony Camera Connection Test ***
# Sony Remote SDK version: 2.0.0
# Initializing Sony Remote SDK...
# Sony Remote SDK initialized successfully.
# Enumerating connected cameras...
# Found 1 camera(s):
# [1] ILCE-1 (USB)
# ...
# [Callback] Camera connected
# Successfully connected to camera!
```

### 3. Shutter Test

```bash
# Test camera shutter control
docker exec payload-manager /app/sbc/build/test_shutter

# Expected: Photos captured successfully
# (Note: As of Oct 24, 2025, error 0x8208 is under investigation)
```

### 4. Network Connectivity Test

```bash
# From ground control station or another device on the network

# Test UDP broadcast (should receive discovery messages)
nc -u -l 5001

# Test TCP connection
nc -v <pi5-ip-address> 5000
```

### 5. Performance Comparison

```bash
# Test USB bandwidth (optional)
# The Pi 5 should show improved USB performance

# Monitor USB errors
dmesg | grep -i usb

# Monitor Docker resource usage
docker stats payload-manager
```

---

## Hardware-Specific Configurations

### Raspberry Pi 5 Enhancements

The Raspberry Pi 5 offers several improvements over Pi 4:

1. **USB Performance**
   - Dedicated USB controller (not shared with Ethernet)
   - Better sustained bandwidth for camera data transfer
   - May allow reducing `usbfs_memory_mb` if needed (test thoroughly)

2. **Power Delivery**
   - Improved 5V power supply requirements (check PSU is adequate)
   - USB-C power input (different from Pi 4 micro-USB)

3. **Cooling**
   - Active cooling recommended under sustained load
   - Monitor temperature: `vcgencmd measure_temp`

### Potential Optimizations for Pi 5

After successful migration, consider testing:

```bash
# Test with lower USB memory (if Pi 5 handles it better)
# Only test AFTER confirming base functionality works
sudo sh -c 'echo 100 > /sys/module/usbcore/parameters/usbfs_memory_mb'

# Run camera tests to verify no USB errors
docker exec payload-manager /app/sbc/build/test_camera
```

---

## Troubleshooting

### Issue: Docker container won't start

**Symptoms:**
```bash
docker ps -a
# Shows: STATUS = Exited (X) Y minutes ago
```

**Solutions:**
```bash
# Check logs for errors
docker logs payload-manager

# Common issues:
# 1. Sony SDK libraries missing
docker exec payload-manager ls -la /app/sdk/external/crsdk/
# Should show: libCr_Core.so, CrAdapter/

# 2. Wrong architecture
docker exec payload-manager uname -m
# Should show: aarch64

# 3. USB access denied
# Ensure --privileged flag is used
# Verify /dev/bus/usb is mounted
```

### Issue: Camera not detected

**Symptoms:**
```bash
lsusb | grep Sony
# Returns nothing
```

**Solutions:**
```bash
# 1. Check camera is in PC Remote mode
# Camera display should show PC symbol

# 2. Try different USB cable/port
# Use USB 3.0 ports (blue color) for best performance

# 3. Check USB power
dmesg | tail -50 | grep -i usb
# Look for: "over-current" or "cannot enumerate"

# 4. Verify USB memory setting
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Should be: 150
```

### Issue: Error 0x8208 (Connection handshake failure)

**Status:** Known issue under investigation (as of Oct 24, 2025)

**Workaround:** Use `test_camera` for basic connectivity verification

**See:** `/home/dpm/DPM/sbc/docs/SITUATION.MD` for detailed analysis

---

## Rollback Plan

If migration encounters critical issues:

### Quick Rollback to Raspberry Pi 4

1. Keep old Pi 4 powered off but available
2. If issues on Pi 5 are unresolvable:
   ```bash
   # On old Pi 4
   sudo systemctl start docker
   docker start payload-manager
   ```

3. Update network configuration to point back to Pi 4
4. Camera should reconnect immediately

### Debugging Before Rollback

Before rolling back, collect diagnostic information:

```bash
# On new Pi 5
# System info
uname -a > migration-debug.txt
docker --version >> migration-debug.txt
docker images >> migration-debug.txt
docker ps -a >> migration-debug.txt

# Docker logs
docker logs payload-manager > container-logs.txt

# USB info
lsusb >> migration-debug.txt
dmesg | grep -i usb >> migration-debug.txt

# System resources
free -h >> migration-debug.txt
df -h >> migration-debug.txt

# Network
ifconfig >> migration-debug.txt
netstat -tuln >> migration-debug.txt
```

---

## Migration Timeline

**Estimated Time:** 2-4 hours (including verification)

### Recommended Workflow

1. **Preparation (30 min)**
   - Backup current system
   - Prepare new Pi 5
   - Install base OS and Docker

2. **File Transfer (30-60 min)**
   - Transfer source code
   - Transfer Sony SDK
   - Transfer Docker image

3. **Configuration (30 min)**
   - Configure boot parameters
   - Set USB limits
   - Configure network

4. **Container Deployment (15 min)**
   - Load/build Docker image
   - Run container
   - Check initial logs

5. **Verification (30-60 min)**
   - Camera detection
   - Connection tests
   - Network tests
   - Performance validation

6. **Buffer Time (30 min)**
   - Unexpected issues
   - Fine-tuning
   - Documentation updates

---

## Success Criteria

Migration is successful when:

- [ ] Docker container runs continuously without crashes
- [ ] Camera detected via `lsusb` (ID 054c:0d1c)
- [ ] Sony SDK initializes successfully
- [ ] Camera enumeration returns 1 camera (ILCE-1)
- [ ] `test_camera` connects successfully
- [ ] OnConnected callback fires
- [ ] Network ports accessible from ground station
- [ ] System boots correctly after power cycle
- [ ] USB memory limit persists after reboot (150 MB)

---

## Additional Resources

- **Project Repository:** https://github.com/unmanned-systems-uk/DPM
- **Current Issue Tracking:** `/home/dpm/DPM/sbc/docs/SITUATION.MD`
- **Docker Setup Guide:** `/home/dpm/DPM/sbc/docs/DOCKER_SETUP.md`
- **Build Instructions:** `/home/dpm/DPM/sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md`

---

## Post-Migration Tasks

After successful migration:

1. **Update Documentation**
   - Update system architecture docs with new Pi 5 details
   - Document any performance improvements observed
   - Update network diagrams if IP/hostname changed

2. **Performance Testing**
   - Measure camera response times
   - Test sustained USB bandwidth
   - Monitor system temperature under load
   - Benchmark against Pi 4 performance

3. **Repository Updates**
   - Commit any configuration changes
   - Update README with Pi 5 compatibility notes
   - Tag release if significant milestone

4. **Decommission Pi 4**
   - Keep as backup/development system for 1 week
   - Archive final Pi 4 system image (optional)
   - Repurpose or store safely

---

**Document Version:** 1.0
**Last Updated:** October 24, 2025
**Maintained By:** DPM Development Team
**Status:** Ready for use
