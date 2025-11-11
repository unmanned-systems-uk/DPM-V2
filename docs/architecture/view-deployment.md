# Deployment View

**Architecture View:** Deployment
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Overview

Physical deployment architecture showing hardware, operating systems, and network topology.

**Visual Reference:** `c4-level4-deployment.puml`

---

## Hardware Platforms

### Air-Side: Raspberry Pi 5

**Specifications:**
- CPU: Broadcom BCM2712 (ARM Cortex-A76, 2.4GHz quad-core)
- RAM: 8GB LPDDR4X
- Storage: 256GB NVMe SSD (M.2 HAT)
- USB: 2× USB 3.0, 2× USB 2.0
- Network: Gigabit Ethernet
- Power: 5V/5A USB-C PD

**OS:** Ubuntu 24.04 LTS ARM64

**Mounted:** On UAV platform with camera

### Ground-Side: SkyDroid H16

**Specifications:**
- Display: 10.1" 1920×1200 touchscreen
- CPU: Qualcomm (exact model TBD)
- RAM: 4-8GB
- Storage: 64-128GB
- Network: WiFi 5/6, Ethernet via R16
- R16 Integration: Digital data link

**OS:** Android (API 24-36)

**Usage:** Handheld ground station tablet

### Dev-Tools: Workstation

**Requirements:**
- Python 3.8+ runtime
- Network access to Air-Side
- SSH client

**OS:** Windows/Linux/macOS

---

## Software Deployment

### Air-Side Docker Deployment

**Container:** payload-manager
- **Build:** Multi-stage Dockerfile (build + runtime)
- **Base Image:** Ubuntu 24.04 ARM64
- **Network:** Host mode (for UDP broadcast)
- **Volumes:**
  - `/usr/local/lib` → Sony SDK libraries
  - `/dev/bus/usb` → USB devices
- **Restart:** Always (auto-restart on failure)
- **Logging:** Docker logs + syslog

**Deployment Process:**
```bash
cd sbc
./build_container.sh
./run_container.sh prod
```

### Ground-Side APK Deployment

**Package:** uk.unmannedsystems.dpm_android
- **Build:** Gradle (Android build system)
- **Min SDK:** API 24 (Android 7.0)
- **Target SDK:** API 36
- **Install:** ADB or Google Play (future)

**Deployment:**
```bash
cd android
./gradlew assembleRelease
adb install app/build/outputs/apk/release/app-release.apk
```

---

## Network Topology

### Production Network (R16 Link)

**Technology:** VXLAN bridge over H16/R16 digital data link
- **Subnet:** 192.168.144.0/24
- **Air-Side IP:** 192.168.144.53 (static)
- **Ground-Side IP:** 192.168.144.92 (static)
- **Bandwidth:** 20-50 Mbps
- **Latency:** <50ms typical
- **Range:** Several kilometers

**Ports:**
- TCP 5000: Commands
- UDP 5001: Status (Air→Ground)
- UDP 5002: Heartbeat (bidirectional)

### Development Network (WiFi)

**Technology:** WiFi 802.11ac/ax
- **Subnet:** 10.0.1.0/24
- **Air-Side IP:** 10.0.1.53 (static)
- **Ground-Side IP:** 10.0.1.92 (static)
- **Dev-Tools IP:** 10.0.1.x (various)

**Additional Ports:**
- TCP 22: SSH to Air-Side

---

## Configuration Management

### Air-Side Config

**Method:** Docker environment variables
- Network IPs
- Port numbers
- Log levels
- Sony SDK paths

### Ground-Side Config

**Method:** AndroidX DataStore
- Network IP (user-configurable)
- User preferences
- Last known settings

---

## Deployment Scenarios

### Scenario 1: Production Flight
- Hardware: Pi 5 on UAV, H16 handheld
- Network: R16 Ethernet link (192.168.144.x)
- Camera: Sony connected via USB
- Operation: Closed network, no internet

### Scenario 2: Lab Testing
- Hardware: Pi 5 on bench, H16 on desk, dev workstation
- Network: WiFi (10.0.1.x)
- Camera: Sony connected via USB or mock
- Operation: SSH access, SystemTools running

### Scenario 3: Development
- Hardware: Dev workstation only (no Pi 5)
- Network: Local or none
- Camera: Simulated/mocked
- Operation: Unit testing, protocol development

---

## Related Documents

- **Visual:** `c4-level4-deployment.puml`
- **Migration Guide:** `docs/RaspberryPi5_SD_to_NVMe_Migration_Guide-V2.md`
- **Docker Setup:** `sbc/docs/DOCKER_SETUP.md`
- **Fresh Install:** `sbc/docs/FRESH_INSTALL_GUIDE.md`
