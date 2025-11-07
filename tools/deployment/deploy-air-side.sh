#!/bin/bash
################################################################################
# Air-Side Deployment Script for NVMe Fresh Install
# DPM-V2 Project
#
# This script sets up a fresh Raspberry Pi OS installation on NVMe
# with all Air-Side dependencies and configuration
#
# Usage: sudo ./deploy-air-side.sh
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Air-Side Deployment Script${NC}"
echo -e "${BLUE}DPM-V2 NVMe Fresh Install${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Step 1: System Update
echo -e "${YELLOW}[1/12] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

# Step 2: Install development tools
echo -e "${YELLOW}[2/12] Installing development tools...${NC}"
apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    vim \
    htop \
    rsync \
    net-tools \
    usbutils \
    ca-certificates \
    gnupg \
    lsb-release
echo -e "${GREEN}✓ Development tools installed${NC}"

# Step 3: Install Docker
echo -e "${YELLOW}[3/12] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add user to docker group
    usermod -aG docker dpm
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Step 4: Install Python and pip
echo -e "${YELLOW}[4/12] Installing Python...${NC}"
apt-get install -y python3 python3-pip python3-venv
echo -e "${GREEN}✓ Python installed${NC}"

# Step 5: Configure network - Static IP for eth0
echo -e "${YELLOW}[5/12] Configuring network (eth0: 192.168.144.10/24)...${NC}"

# Backup existing config
if [ -f /etc/dhcpcd.conf ]; then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
fi

# Add static IP configuration for eth0 (VXLAN bridge to H16)
cat >> /etc/dhcpcd.conf << 'NET_EOF'

# Air-Side DPM-V2 Configuration
# Static IP for eth0 - VXLAN bridge to H16 Ground-Side
interface eth0
static ip_address=192.168.144.10/24
noipv6
NET_EOF

echo -e "${GREEN}✓ Network configuration added${NC}"
echo -e "${YELLOW}  NOTE: Network changes require reboot to take effect${NC}"

# Step 6: Configure USB permissions for Sony Camera
echo -e "${YELLOW}[6/12] Configuring USB permissions for Sony Camera...${NC}"
cat > /etc/udev/rules.d/99-sony-camera.rules << 'USB_EOF'
# Sony Camera USB permissions for DPM-V2
# Allows Docker container to access Sony camera via USB
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="*", MODE="0666", GROUP="plugdev"
USB_EOF

udevadm control --reload-rules
echo -e "${GREEN}✓ USB permissions configured${NC}"

# Step 7: Create project directories
echo -e "${YELLOW}[7/12] Creating project directories...${NC}"
mkdir -p /home/dpm/DPM-V2
mkdir -p /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8
chown -R dpm:dpm /home/dpm/DPM-V2
chown -R dpm:dpm /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8
echo -e "${GREEN}✓ Project directories created${NC}"

# Step 8: Configure SSH (if not already done)
echo -e "${YELLOW}[8/12] Configuring SSH...${NC}"
systemctl enable ssh
systemctl start ssh
echo -e "${GREEN}✓ SSH configured${NC}"

# Step 9: Set hostname
echo -e "${YELLOW}[9/12] Setting hostname to 'air-side-pi5'...${NC}"
hostnamectl set-hostname air-side-pi5
echo -e "${GREEN}✓ Hostname set${NC}"

# Step 10: Configure system limits for Docker
echo -e "${YELLOW}[10/12] Configuring system limits...${NC}"
cat >> /etc/security/limits.conf << 'LIMITS_EOF'
# DPM-V2 Air-Side limits
dpm    soft    nofile    65536
dpm    hard    nofile    65536
LIMITS_EOF
echo -e "${GREEN}✓ System limits configured${NC}"

# Step 11: Install additional utilities
echo -e "${YELLOW}[11/12] Installing additional utilities...${NC}"
apt-get install -y \
    ncdu \
    iotop \
    nload \
    tcpdump \
    netcat-openbsd
echo -e "${GREEN}✓ Additional utilities installed${NC}"

# Step 12: Create deployment summary
echo -e "${YELLOW}[12/12] Creating deployment summary...${NC}"
cat > /home/dpm/DEPLOYMENT_SUMMARY.txt << EOF
Air-Side Deployment Summary
===========================
Deployment Date: $(date +"%Y-%m-%d %H:%M:%S")
Hostname: $(hostname)
OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
Kernel: $(uname -r)

Installed Components:
---------------------
✓ System packages updated
✓ Development tools (gcc, g++, cmake, git)
✓ Docker $(docker --version 2>/dev/null || echo "installation pending reboot")
✓ Python $(python3 --version)
✓ Network configured (eth0: 192.168.144.10/24)
✓ USB permissions for Sony camera
✓ SSH enabled and running
✓ Project directories created

Network Configuration:
----------------------
eth0: 192.168.144.10/24 (VXLAN bridge to H16) - REQUIRES REBOOT
wlan0: DHCP (WiFi management access)

Manual Steps Required:
----------------------
1. REBOOT system to apply network configuration
   sudo reboot

2. After reboot, restore DPM-V2 project:
   cd /home/dpm
   rsync -av /path/to/backup/project/DPM-V2/ ~/DPM-V2/

3. Restore Sony SDK:
   cd /home/dpm
   tar -xzf /path/to/backup/sdk/CrSDK*.tar.gz

4. Build and run Docker container:
   cd ~/DPM-V2/sbc
   docker build -t payload-manager:latest .
   docker run -d \\
       --name payload-manager \\
       --restart unless-stopped \\
       --network host \\
       --device /dev/bus/usb:/dev/bus/usb \\
       -v \$(pwd)/logs:/app/logs:rw \\
       payload-manager:latest

5. Verify camera connection:
   lsusb | grep Sony
   docker logs payload-manager

Verification Commands:
----------------------
# Check network
ip addr show eth0
ping 192.168.144.11  # H16 Ground-Side

# Check Docker
docker ps
docker logs payload-manager

# Check USB camera
lsusb | grep Sony

# Check project files
ls -la ~/DPM-V2/sbc
ls -la ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8

Troubleshooting:
----------------
If network doesn't work after reboot:
  sudo systemctl restart dhcpcd
  sudo systemctl status dhcpcd

If Docker permission denied:
  Log out and log back in (user added to docker group)

If camera not detected:
  Check camera is in PC Remote mode
  sudo udevadm control --reload-rules
  Unplug and replug camera USB

Documentation:
--------------
Deployment script: ~/DPM-V2/tools/deployment/deploy-air-side.sh
Backup script: ~/DPM-V2/tools/deployment/backup-air-side.sh
Restoration guide: (in backup directory)/docs/RESTORATION_GUIDE.md

Next Steps:
-----------
☐ Reboot system (sudo reboot)
☐ Verify network (ip addr show eth0)
☐ Restore project files
☐ Restore Sony SDK
☐ Build Docker container
☐ Test camera connection
☐ Verify Ground-Side communication

Deployment completed at $(date +"%Y-%m-%d %H:%M:%S")
EOF

chown dpm:dpm /home/dpm/DEPLOYMENT_SUMMARY.txt
echo -e "${GREEN}✓ Deployment summary created${NC}"

# Final summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: System reboot required for network configuration${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Review deployment summary: cat ~/DEPLOYMENT_SUMMARY.txt"
echo "  2. Reboot system: sudo reboot"
echo "  3. After reboot, restore project files from backup"
echo "  4. Build and run Docker container"
echo ""
echo -e "${GREEN}Deployment summary: /home/dpm/DEPLOYMENT_SUMMARY.txt${NC}"
echo ""
