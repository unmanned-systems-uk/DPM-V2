# System Dependencies - DPM-V2 Air-Side
**Version:** 1.0
**Created:** 2025-11-09
**Platform:** Raspberry Pi 5 / Ubuntu 25.10 ARM64

---

## Overview

Complete list of system dependencies required for DPM-V2 Air-Side Payload Manager. Use this for fresh installations or system recovery.

---

## Operating System

**Required:**
- Ubuntu 25.10 "Questing" ARM64 (recommended)
- Ubuntu 22.04+ ARM64 (minimum)
- Kernel 6.17.0+ (for Raspberry Pi 5 support)

**Current Installation:**
```
OS: Ubuntu 25.10 (Questing)
Kernel: 6.17.0-1004-raspi
Architecture: aarch64 (ARM64v8)
```

---

## System Packages (APT)

### Core Development Tools

```bash
sudo apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    git \
    curl \
    wget
```

**Versions (installed):**
- build-essential: 12.12ubuntu1
- cmake: 3.31.6-2ubuntu6
- g++: 4:15.2.0-4ubuntu1
- gcc: 4:15.2.0-4ubuntu4
- git: 1:2.51.0-1ubuntu1

### Network & System Tools

```bash
sudo apt-get install -y \
    net-tools \
    iputils-ping \
    usbutils \
    ca-certificates \
    gnupg \
    vim \
    htop
```

### Libraries (Docker Container Only)

**Note:** These are installed inside Docker container, NOT on host system.

```bash
# Inside Dockerfile.prod (Ubuntu 22.04 base)
apt-get install -y \
    libxml2 \
    libxml2-dev \
    nlohmann-json3-dev \
    libudev-dev \
    libusb-1.0-0 \
    libusb-1.0-0-dev
```

**Why Docker uses Ubuntu 22.04:**
- Sony SDK `libCr_Core.so` compiled against libxml2 2.9.x
- Ubuntu 25.10 has libxml2 16.x (incompatible)
- Ubuntu 22.04 provides libxml2 2.9.13 (compatible)

---

## Docker

### Installation

```bash
# Official Docker installation script
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# IMPORTANT: Log out and log back in
exit
```

### Versions (installed)

```
Docker Engine: 28.5.1
Docker Compose: 2.40.2
Docker Buildx Plugin: 0.29.1
```

### Docker Plugins

Automatically installed with Docker:
- docker-buildx-plugin: 0.29.1-1
- docker-compose-plugin: 2.40.2-1
- docker-ce-rootless-extras: 28.5.1-1

---

## External Dependencies

### Sony Camera Remote SDK

**Version:** CrSDK_v2.00.00_20250805a_Linux64ARMv8

**Location:** `/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8`

**Installation:** See `sbc/docs/SONY_SDK_INSTALLATION.md`

**Libraries Required:**
- libCr_Core.so (core SDK)
- CrAdapter/libCr_PTP_USB.so (USB transport)
- CrAdapter/libCr_PTP_IP.so (IP transport)

**Dependencies:**
- libxml2.so.2 (version 2.9.x)
- libpthread.so.0
- libc.so.6
- libusb-1.0.so.0

---

## Python Packages

**Status:** NOT REQUIRED for Air-Side C++ implementation

**Note:** SystemTools (Dev-Side) uses Python, but Air-Side is pure C++.

---

## Build Tools

### CMake

**Required Version:** 3.16+
**Installed Version:** 3.31.6
**Purpose:** Build system for C++ payload_manager

### GCC/G++ Compiler

**Required Version:** C++17 support (GCC 7+)
**Installed Version:** 15.2.0
**Standard:** C++17
**Purpose:** Compile payload_manager and dependencies

### Make

**Installed:** Included with build-essential
**Purpose:** CMake build backend

---

## Runtime Dependencies

### USB Support

**Packages:**
- usbutils (lsusb command)
- libusb-1.0-0 (USB device access)

**Kernel Parameters:**
```bash
# Required for Sony SDK camera communication
usbcore.usbfs_memory_mb=150
```

**Configuration File:** `/boot/firmware/cmdline.txt`

### Network

**Packages:**
- net-tools (ifconfig, netstat)
- iputils-ping (ping command)

**Ports Used:**
- TCP 5000 (command interface)
- UDP 5001 (status broadcasts)
- UDP 5002 (heartbeat)

---

## Container Dependencies

### Base Image

**Dockerfile.prod:**
```dockerfile
FROM ubuntu:22.04
```

**Why Ubuntu 22.04:**
- Compatible libxml2 2.9.x for Sony SDK
- Stable LTS release
- ARM64 support

### Container Packages

**Build dependencies:**
```
build-essential
cmake
g++
```

**Runtime dependencies:**
```
libxml2
libxml2-dev
nlohmann-json3-dev
libudev-dev
libusb-1.0-0
libusb-1.0-0-dev
usbutils
net-tools
iputils-ping
```

### Container Environment

```bash
LD_LIBRARY_PATH=/app/sdk/external/crsdk:/app/sdk/external/crsdk/CrAdapter:$LD_LIBRARY_PATH
```

---

## Optional Dependencies

### Development Tools

```bash
# Not required for production, but useful
sudo apt-get install -y \
    gdb \
    valgrind \
    strace \
    ncdu \
    iotop \
    nload \
    tcpdump
```

### Documentation Tools

```bash
# For viewing SDK documentation
sudo apt-get install -y \
    doxygen \
    graphviz
```

---

## Verification Commands

### Check Installed Packages

```bash
# Check specific package
dpkg -l | grep build-essential

# Check Docker
docker --version
docker compose version

# Check GCC/G++
gcc --version
g++ --version
cmake --version

# Check Git
git --version
```

### Check Library Dependencies

```bash
# Check Sony SDK dependencies
cd ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/external/crsdk
ldd libCr_Core.so

# Should show all dependencies resolved
```

### Check USB Configuration

```bash
# Check USB buffer
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Should be: 150

# Check boot config
grep usbcore /boot/firmware/cmdline.txt
# Should contain: usbcore.usbfs_memory_mb=150
```

---

## Dependency Installation Script

**Quick install all dependencies:**

```bash
#!/bin/bash
# Install DPM-V2 Air-Side dependencies
# Run as: sudo ./install_dependencies.sh

set -e

echo "Installing core development tools..."
apt-get update
apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    git \
    curl \
    wget \
    vim \
    htop

echo "Installing network and USB tools..."
apt-get install -y \
    net-tools \
    iputils-ping \
    usbutils \
    ca-certificates \
    gnupg

echo "Installing Docker..."
curl -fsSL https://get.docker.com | sh

echo "Adding user to docker group..."
usermod -aG docker $SUDO_USER

echo "Enabling Docker service..."
systemctl enable docker
systemctl start docker

echo "Dependencies installed successfully!"
echo "IMPORTANT: Log out and log back in for Docker group membership."
```

---

## Troubleshooting

### Missing Package

```bash
# Search for package
apt search <package-name>

# Install package
sudo apt-get install <package-name>
```

### Docker Permission Denied

```bash
# Check user in docker group
groups $USER

# If not in docker group:
sudo usermod -aG docker $USER
# Log out and log back in
```

### libxml2 Version Mismatch

**Error:** `libxml2.so.2: version LIBXML2_2.9.0 not found`

**Solution:** Run payload_manager in Docker container (Ubuntu 22.04 base)

```bash
# Check libxml2 version on host
dpkg -l | grep libxml2

# Container has correct version (2.9.x)
docker run -it --rm payload-manager:latest ldd /app/sdk/external/crsdk/libCr_Core.so | grep libxml2
```

---

## Dependency Tree

```
DPM-V2 Air-Side Payload Manager
│
├── Operating System
│   └── Ubuntu 25.10 ARM64 (kernel 6.17.0+)
│
├── Build Tools
│   ├── GCC/G++ 15.2.0 (C++17)
│   ├── CMake 3.31.6
│   └── Make (build-essential)
│
├── Docker
│   ├── Docker Engine 28.5.1
│   ├── Docker Compose 2.40.2
│   └── Docker Buildx 0.29.1
│
├── Sony Camera Remote SDK
│   ├── libCr_Core.so
│   ├── CrAdapter/libCr_PTP_USB.so
│   └── CrAdapter/libCr_PTP_IP.so
│       │
│       └── Requires libxml2 2.9.x
│           └── Ubuntu 22.04 (in container)
│
├── System Libraries (container)
│   ├── libxml2 2.9.13
│   ├── libusb-1.0-0
│   ├── nlohmann-json3-dev
│   └── libudev-dev
│
└── USB Configuration
    └── usbcore.usbfs_memory_mb=150
```

---

## Backup Recommendations

**Package List Backup:**
```bash
# Save current package list
dpkg -l > ~/dpkg-list-backup-$(date +%Y%m%d).txt
```

**Docker Image Backup:**
```bash
# Save Docker image
docker save payload-manager:latest > ~/payload-manager-image-backup.tar
```

**Configuration Backup:**
```bash
# Backup boot config
sudo cp /boot/firmware/cmdline.txt ~/cmdline.txt.backup
```

---

## Additional Resources

**Documentation:**
- Fresh Install Guide: `sbc/docs/FRESH_INSTALL_GUIDE.md`
- Sony SDK Installation: `sbc/docs/SONY_SDK_INSTALLATION.md`
- Progress Tracking: `sbc/docs/PROGRESS_AND_TODO.md`

**Package Sources:**
- Ubuntu Packages: https://packages.ubuntu.com/
- Docker: https://docs.docker.com/engine/install/ubuntu/
- Sony SDK: https://support.d-imaging.sony.co.jp/app/sdk/en/

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Maintained By:** CC-Air-Side
**Status:** Production
