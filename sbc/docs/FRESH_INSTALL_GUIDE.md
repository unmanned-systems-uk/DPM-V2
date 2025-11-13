# Fresh Install Guide - DPM-V2 Air-Side Payload Manager
**Version:** 1.0
**Created:** 2025-11-09
**Purpose:** Complete system rebuild instructions for SSD migration recovery

---

## Overview

This guide provides step-by-step instructions to rebuild the DPM-V2 Air-Side Payload Manager system from scratch on a fresh Raspberry Pi 5 installation. Use this if:
- SSD migration fails and requires fresh install
- Replacing hardware
- Setting up additional Air-Side unit
- System corruption recovery

**Estimated Time:** 2-3 hours
**Skill Level:** Intermediate Linux

---

## Prerequisites

### Hardware Required
- Raspberry Pi 5 Model B (8GB RAM recommended, 4GB minimum)
- MicroSD card (32GB+ for boot) or NVMe SSD (see migration guide)
- Sony Camera Remote SDK compatible camera (e.g., Sony ILCE-1)
- USB cable for camera connection
- Network connection (Ethernet or WiFi)
- Power supply (27W USB-C PD recommended)

### Software Required
- Ubuntu 25.10 "Questing" ARM64 (or Ubuntu 22.04+ ARM64)
- Internet connection for package downloads

### Before You Begin
- Backup any existing data
- Have GitHub credentials ready
- Obtain Sony Camera Remote SDK (see Section 3)

---

## Section 1: Base System Setup

### 1.1 Install Operating System

**Recommended:** Ubuntu 25.10 "Questing" ARM64 for Raspberry Pi

```bash
# Flash Ubuntu image to SD card or NVMe using Raspberry Pi Imager
# Boot system and complete initial setup
# Update system
sudo apt-get update
sudo apt-get upgrade -y
```

### 1.2 System Configuration

```bash
# Set hostname (optional but recommended)
sudo hostnamectl set-hostname air-side-pi5

# Set timezone
sudo timedatectl set-timezone UTC

# Verify system
uname -a
# Expected: Linux air-side-pi5 6.17.0-... aarch64 GNU/Linux
```

### 1.3 Create User (if not already created)

```bash
# DPM-V2 expects user 'dpm'
sudo adduser dpm
sudo usermod -aG sudo dpm
```

### 1.4 RTC (Real-Time Clock) Configuration

**Purpose:** Enable accurate timestamps in logs during flight operations without network connectivity

**Hardware:** CR1220 battery for Pi 5 RTC slot (optional but highly recommended for flight operations)

**Why needed:** During flight operations, the Pi may not have internet access. Without RTC battery, system time resets on every boot. RTC maintains accurate time even when powered off.

#### 1.4.1 Verify RTC Detection

```bash
# Check if RTC device exists
ls -l /dev/rtc*
# Expected: /dev/rtc -> rtc0

# Check RTC name
cat /sys/class/rtc/rtc0/name
# Expected: rpi-rtc soc@107c000000:rpi_rtc

# Check RTC time
cat /sys/class/rtc/rtc0/date && cat /sys/class/rtc/rtc0/time
```

#### 1.4.2 RTC Configuration

**Note:** Pi 5 with Ubuntu 24.04+ handles RTC automatically. No manual configuration needed in `/boot/firmware/config.txt`.

**Verify RTC is working:**
```bash
# Check RTC kernel module
lsmod | grep rtc
# Expected: rtc_rpi module loaded

# Check time synchronization status
timedatectl status
# Expected: "RTC time" should show current time
```

#### 1.4.3 Set Initial Time (One-Time, When Internet Available)

```bash
# System should auto-sync from NTP when internet available
timedatectl status
# Verify "System clock synchronized: yes"
```

#### 1.4.4 Create RTC Boot Verification Service (Optional)

**This service logs RTC time at boot for debugging:**

```bash
# Create service file
sudo tee /etc/systemd/system/rtc-read-on-boot.service > /dev/null <<'EOF'
[Unit]
Description=Read RTC time on boot for flight logging
Documentation=https://github.com/unmanned-systems-uk/DPM-V2/issues/47
DefaultDependencies=no
Before=sysinit.target
After=systemd-modules-load.service
Conflicts=shutdown.target
ConditionPathExists=/dev/rtc0

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo "RTC Boot Check: $(date)" && echo "RTC Hardware: $(cat /sys/class/rtc/rtc0/date) $(cat /sys/class/rtc/rtc0/time)"'
StandardOutput=journal
StandardError=journal
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable rtc-read-on-boot.service
sudo systemctl start rtc-read-on-boot.service

# Verify service status
sudo systemctl status rtc-read-on-boot.service

# View RTC boot logs
journalctl -u rtc-read-on-boot.service
```

#### 1.4.5 Test RTC Persistence

**During initial setup (with network):**
```bash
# Check time sync
timedatectl status
# Verify: "System clock synchronized: yes"

# Check RTC time matches system time
date && cat /sys/class/rtc/rtc0/date && cat /sys/class/rtc/rtc0/time
# Times should match within a few seconds
```

**During flight operations (without network):**
- System will maintain accurate time from RTC
- Logs will have correct timestamps
- No internet required

**Benefits:**
- ✅ Accurate timestamps in flight logs
- ✅ Correlate events with flight timeline
- ✅ Debug offline issues with proper time references
- ✅ Professional logging (no "Jan 1 1970" timestamps)

**Reference:** Issue #47 - RTC Integration Testing

---

## Section 2: Install System Dependencies

### 2.1 Development Tools

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools \
    iputils-ping \
    usbutils \
    ca-certificates \
    gnupg
```

**Versions installed (reference):**
- GCC: 15.2.0
- CMake: 3.31.6
- Git: 2.51.0

### 2.2 Install Docker

```bash
# Official Docker installation
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# IMPORTANT: Log out and log back in for group membership to take effect
exit
# (log back in)

# Verify Docker installation
docker --version
# Expected: Docker version 28.5.1, build e180ab8

docker compose version
# Expected: Docker Compose version v2.40.2
```

---

## Section 3: Sony Camera Remote SDK Installation

### 3.1 Obtain SDK

**Source:** Sony Developer Portal or existing backup

**Required Version:** `CrSDK_v2.00.00_20250805a_Linux64ARMv8`

**Where to obtain:**
1. **From backup:** If you have a backup of previous system
2. **From Sony:** Contact Sony Developer support for SDK access
3. **From existing system:** Before migration, copy SDK directory

### 3.2 Install SDK

```bash
# Copy SDK to home directory
# Assuming SDK is in ~/Downloads/
cd ~
cp -r /path/to/CrSDK_v2.00.00_20250805a_Linux64ARMv8 ~/

# Verify SDK structure
ls ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/
# Expected directories: external/, app/, doc/, include/, lib/

# Set permissions
chmod -R 755 ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8
```

**Critical Files:**
- `external/crsdk/libCr_Core.so` - Core SDK library
- `external/crsdk/CrAdapter/` - Dynamic adapter libraries
- `app/RemoteCli` - Example application for testing

### 3.3 Verify SDK

```bash
# Check library dependencies
cd ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/external/crsdk
ldd libCr_Core.so
# Should show all dependencies resolved

# Test with RemoteCli (if camera connected)
cd ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/app
./RemoteCli
# Should enumerate camera if connected
```

---

## Section 4: USB Configuration for Camera

### 4.1 Increase USB Buffer (CRITICAL)

**Why:** Sony SDK requires 150MB USB buffer for reliable camera communication. Default is 16MB.

```bash
# Check current setting
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Default: 16

# Set runtime (temporary, lost on reboot)
echo 150 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb

# Make permanent - edit boot config
sudo nano /boot/firmware/cmdline.txt
```

**Add to kernel command line (single line, no line breaks):**
```
usbcore.usbfs_memory_mb=150
```

**Example (add at END of existing line):**
```
console=serial0,115200 console=tty1 root=PARTUUID=... rootfstype=ext4 ... usbcore.usbfs_memory_mb=150
```

**Save and reboot:**
```bash
sudo reboot
```

**After reboot, verify:**
```bash
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Should show: 150
```

### 4.2 USB Device Permissions (Optional)

```bash
# Create udev rule for Sony cameras
sudo nano /etc/udev/rules.d/99-sony-camera.rules
```

**Add:**
```
# Sony Camera USB permissions
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", MODE="0666", GROUP="plugdev"
```

**Apply rules:**
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## Section 5: Clone DPM-V2 Repository

### 5.1 Setup Git

```bash
# Configure Git (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Setup GitHub authentication (if using SSH)
# Generate SSH key if needed
ssh-keygen -t ed25519 -C "your.email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add public key to GitHub: Settings → SSH and GPG keys
```

### 5.2 Clone Repository

```bash
cd ~
git clone https://github.com/unmanned-systems-uk/DPM-V2.git
cd DPM-V2

# Verify branch
git branch --show-current
# Should be: main

# Check repository status
git log --oneline -5
# Should show recent commits
```

---

## Section 6: Build Docker Container

### 6.1 Build Process

```bash
cd ~/DPM-V2/sbc

# Run build script
./build_container.sh
```

**Build script does:**
1. Copies DPM-V2 repository to parent directory
2. Copies Sony SDK to parent directory
3. Builds Docker image: `payload-manager:latest`
4. Compiles C++ payload_manager inside container
5. Includes Sony SDK libraries

**Expected output:**
```
Building Docker image: payload-manager:latest
Step 1/10 : FROM ubuntu:22.04
...
Successfully built c75ad76645e9
Successfully tagged payload-manager:latest
```

**Build time:** 5-10 minutes (depends on system)

### 6.2 Verify Build

```bash
# Check Docker image
docker images | grep payload
# Expected: payload-manager   latest   c75ad76645e9   X minutes ago   1.48GB

# Inspect image
docker image inspect payload-manager:latest | grep -A 5 "Created"
```

---

## Section 7: Network Configuration

### 7.1 WiFi Setup (Development/Testing)

```bash
# Connect to WiFi network
nmcli dev wifi connect "YourSSID" password "YourPassword"

# Verify connection
ip addr show wlan0
# Expected: inet 10.0.1.53/24 (or your network's DHCP assignment)

# Test connectivity
ping 8.8.8.8
ping google.com
```

### 7.2 Ethernet Setup (Production)

**For H16 VXLAN bridge (if applicable):**
```bash
# Static IP configuration
sudo nano /etc/netplan/01-netcfg.yaml
```

**Example:**
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.144.20/24
      routes:
        - to: default
          via: 192.168.144.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```

**Apply:**
```bash
sudo netplan apply
ip addr show eth0
```

### 7.3 Ground Station IP

**Default Ground IPs:**
- **Ethernet (Production):** 192.168.144.11 (H16 via VXLAN)
- **WiFi (Testing):** 10.0.1.100 (or H16's WiFi IP)

**Configure Ground IP when running container (Section 8)**

---

## Section 8: Run Payload Manager Container

### 8.1 Production Mode (Recommended)

```bash
cd ~/DPM-V2/sbc

# Run with default ethernet ground IP (192.168.144.11)
./run_container.sh prod

# OR run with WiFi testing mode
./run_container.sh prod --test-wifi

# OR specify custom ground IP
./run_container.sh prod --ground-ip 10.0.1.100
```

### 8.2 Development Mode (For Testing)

```bash
# Mount source code as volume for live editing
./run_container.sh dev

# Changes to src/ require rebuild inside container:
docker exec -it payload-manager bash
cd /app/sbc/build && cmake .. && make
exit
docker restart payload-manager
```

### 8.3 Verify Container Running

```bash
# Check container status
docker ps | grep payload
# Expected: payload-manager ... Up X seconds ...

# Check logs
docker logs payload-manager
# Should show:
# [INFO] Logger initialized
# [INFO] Sony SDK initialized
# [INFO] TCP server listening on port 5000
# [INFO] UDP broadcaster started (5 Hz to 192.168.144.11:5001)
# [INFO] Heartbeat started (1 Hz to 192.168.144.11:5002)
```

### 8.4 Container Management Commands

```bash
# View live logs
docker logs -f payload-manager

# Stop container
docker stop payload-manager

# Start container
docker start payload-manager

# Restart container
docker restart payload-manager

# Remove container (stops first if running)
docker stop payload-manager && docker rm payload-manager

# Shell access
docker exec -it payload-manager bash
```

---

## Section 9: Verification & Testing

### 9.1 Camera Connection Test

```bash
# Connect Sony camera via USB
# Set camera to PC Remote mode

# Check USB detection
lsusb | grep Sony
# Expected: Bus 005 Device 003: ID 054c:XXXX Sony Corp. ILCE-1

# Check container can see camera
docker exec payload-manager lsusb | grep Sony

# Check payload manager logs
docker logs payload-manager | grep -i camera
# Expected:
# [INFO] Enumerating cameras...
# [INFO] Camera connected: Sony ILCE-1
# [INFO] Camera status: Ready
```

### 9.2 Network Services Test

```bash
# Test TCP server (from another machine or Pi)
echo '{"protocol_version":"1.2.0","message_type":"command","sequence_id":1,"timestamp":1698000000,"payload":{"command":"system.handshake","parameters":{"client_version":"1.0"}}}' | nc 192.168.144.20 5000

# Expected response:
# {"protocol_version":"1.2.0","message_type":"response",...}

# Test UDP status reception (on ground station or PC)
# Use SystemTools or custom listener on port 5001

# Test heartbeat (on ground station or PC)
# Listen on UDP port 5002
```

### 9.3 Manual Focus Test (CRITICAL)

**This verifies the Oct 31 focus fix is working:**

```bash
# From Ground-Side app or manual command:
# Send camera.focus command:
echo '{"protocol_version":"1.2.0","message_type":"command","sequence_id":2,"timestamp":1698000000,"payload":{"command":"camera.focus","parameters":{"direction":"near","speed":1}}}' | nc 192.168.144.20 5000

# Check logs for focus command execution
docker logs payload-manager | grep -i focus
# Should NOT see error 0x8402
# Should see: [INFO] Focus control: near, speed: 1
```

---

## Section 10: Apply Critical Fixes

### 10.1 Sony SDK Focus Fix (Oct 31 Breakthrough)

**STATUS:** This fix is already in `main` branch (commit 706786b and later)

**What it does:**
- Validates `FocalDistanceInMeter` property is enabled before querying
- Queries and respects camera's focus speed range
- Adds 50ms delay after property queries
- Adds 100ms delay after focus commands
- Prevents SDK error 0x8402

**Verify fix is applied:**
```bash
cd ~/DPM-V2/sbc/src/camera
grep -n "IsSetEnableCurrentValue" camera_sony.cpp
# Should find validation code in handleFocusControl()

grep -n "std::this_thread::sleep_for" camera_sony.cpp
# Should find timing delays
```

**If using older branch or code:**
```bash
git checkout main
git pull origin main
# Rebuild container
cd ~/DPM-V2/sbc
./build_container.sh
./run_container.sh prod
```

**Reference:**
- Full fix details: `docs/archive/legacy-docs/FOCUS_FIX_SUMMARY.md`
- Commits: 706786b, b60ecf5, 085f0f2

---

## Section 11: Environment Variables (Optional)

**Container automatically sets:**
- `MODE=production` or `MODE=development`
- `DPM_GROUND_IP` - Ground station IP
- `LD_LIBRARY_PATH` - Sony SDK library path

**No manual environment configuration required.**

---

## Section 12: Troubleshooting

### 12.1 Docker Build Fails

**Error:** `Cannot find Sony SDK`
```bash
# Verify SDK location
ls -la ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8
# Must exist and contain external/crsdk/
```

**Error:** `libxml2 compatibility`
```bash
# Verify Dockerfile.prod uses Ubuntu 22.04
grep "FROM ubuntu" ~/DPM-V2/sbc/Dockerfile.prod
# Must be: FROM ubuntu:22.04
```

### 12.2 Camera Not Connecting

**Check 1:** USB Buffer
```bash
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Must be: 150
# If not, see Section 4.1
```

**Check 2:** Camera Mode
- Camera must be in **PC Remote mode**
- Not in sleep/standby mode
- USB cable connected

**Check 3:** USB Detection
```bash
lsusb | grep Sony
# Should show camera
# If not, try different USB port
```

**Check 4:** Container Logs
```bash
docker logs payload-manager | grep -i error
# Look for SDK errors or connection failures
```

### 12.3 SDK Error 0x8402 (Focus Commands)

**This error means:** `CrError_Api_InvalidCalled`

**Solution:** Verify focus fix applied (Section 10.1)

**Manual check:**
```bash
docker exec payload-manager bash -c "grep -c 'IsSetEnableCurrentValue' /app/sbc/src/camera/camera_sony.cpp"
# Should be > 0 (fix includes validation)
```

### 12.4 Network Timeout Issues

**UDP broadcasts not received:**
```bash
# Verify Ground IP is correct
docker inspect payload-manager | grep DPM_GROUND_IP
# Should match your ground station IP

# Restart with correct IP
docker stop payload-manager
docker rm payload-manager
./run_container.sh prod --ground-ip <CORRECT_IP>
```

**Firewall blocking:**
```bash
# On Air-Side Pi:
sudo ufw status
# If active, allow ports:
sudo ufw allow 5000/tcp
sudo ufw allow 5001/udp
sudo ufw allow 5002/udp
```

### 12.5 Container Won't Start

```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs for specific error
docker logs payload-manager

# Try manual docker run
docker run -it --rm \
  --privileged \
  --network host \
  -v /dev/bus/usb:/dev/bus/usb \
  payload-manager:latest \
  /bin/bash
# Inside container:
/app/sbc/build/payload_manager
# See exact error
```

---

## Section 13: Post-Installation Tasks

### 13.1 Enable Auto-Start

**Container already has `--restart always` in production mode**

Verify:
```bash
docker inspect payload-manager | grep -i restart
# Should show: "RestartPolicy": {"Name": "always"}
```

### 13.2 Configure Logging

```bash
# Logs location
ls -la ~/DPM-V2/sbc/logs/
# payload_manager.log updated in real-time

# Rotate logs (if needed)
# Add to crontab or logrotate
```

### 13.3 Backup Docker Image

```bash
# Save image to tar file
mkdir -p ~/backups
docker save payload-manager:latest > ~/backups/payload-manager_$(date +%Y%m%d).tar

# Restore later:
docker load < ~/backups/payload-manager_YYYYMMDD.tar
```

---

## Section 14: Quick Reference

### Build & Run
```bash
cd ~/DPM-V2/sbc
./build_container.sh               # Build image
./run_container.sh prod            # Run production
./run_container.sh dev             # Run development
```

### Docker Commands
```bash
docker ps                          # List running containers
docker logs -f payload-manager     # View live logs
docker stop payload-manager        # Stop container
docker start payload-manager       # Start container
docker restart payload-manager     # Restart container
```

### Debugging
```bash
docker exec -it payload-manager bash       # Shell access
lsusb | grep Sony                          # Check camera USB
cat /sys/module/usbcore/parameters/usbfs_memory_mb  # Check USB buffer
docker inspect payload-manager | grep IP  # Check network config
```

### Testing
```bash
# Test TCP command
echo '{"protocol_version":"1.2.0",...}' | nc 192.168.144.20 5000

# Check logs for errors
docker logs payload-manager | grep ERROR

# Test camera connection
docker exec payload-manager lsusb | grep Sony
```

---

## Section 15: System Specifications (Reference)

**Hardware:**
- Platform: Raspberry Pi 5 Model B Rev 1.1
- CPU: ARM Cortex-A76 (quad-core, 2.4 GHz)
- RAM: 8GB LPDDR4X-4267
- Storage: SD card or NVMe SSD

**Software:**
- OS: Ubuntu 25.10 "Questing" ARM64
- Kernel: 6.17.0-1004-raspi
- Docker: 28.5.1
- Docker Compose: 2.40.2
- GCC: 15.2.0
- CMake: 3.31.6

**Sony SDK:**
- Version: v2.00.00_20250805a
- Platform: Linux64ARMv8
- Libraries: libCr_Core.so, CrAdapter/

**DPM-V2:**
- Language: C++17
- Build System: CMake
- Container Base: Ubuntu 22.04 (for libxml2 compatibility)

---

## Section 16: Additional Resources

**Documentation:**
- Air-Side Architecture: `docs/AIR_SIDE/AIR_SIDE_ARCHITECTURE.md`
- Progress Tracking: `sbc/docs/PROGRESS_AND_TODO.md`
- Sony SDK Reference: `docs/AIR_SIDE/SONY_SDK_REFERENCE.md`
- Migration Guide: `docs/RaspberryPi5_SD_to_NVMe_Migration_Guide-V2.md`

**Scripts:**
- Build script: `sbc/build_container.sh`
- Run script: `sbc/run_container.sh`
- Test scripts: `sbc/test_camera.sh`, `sbc/test_shutter.sh`

**GitHub:**
- Repository: https://github.com/unmanned-systems-uk/DPM-V2
- Issues: https://github.com/unmanned-systems-uk/DPM-V2/issues
- Protocol Specs: `protocol/commands.json`, `protocol/camera_properties.json`

---

## Success Criteria

✅ System boots and runs stable
✅ Docker container starts automatically
✅ Camera detected via `lsusb`
✅ Payload manager connects to camera
✅ TCP server responds on port 5000
✅ UDP status broadcasts at 5 Hz
✅ Heartbeat sends at 1 Hz
✅ Manual focus commands work (no 0x8402 errors)
✅ Logs show no critical errors
✅ Ground station receives status updates

---

## Maintenance

### Regular Tasks
- Monitor disk space: `df -h`
- Check logs for errors: `docker logs payload-manager | grep ERROR`
- Update system packages: `sudo apt-get update && sudo apt-get upgrade`
- Backup Docker image weekly
- Pull latest code from GitHub: `git pull origin main`

### Updates
```bash
# Update DPM-V2 code
cd ~/DPM-V2
git pull origin main

# Rebuild container
cd sbc
./build_container.sh

# Restart with new image
docker stop payload-manager
docker rm payload-manager
./run_container.sh prod
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Maintained By:** CC-Air-Side
**Status:** Production Ready
