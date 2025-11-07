#!/bin/bash
################################################################################
# Air-Side Backup Script for NVMe Migration
# DPM-V2 Project
#
# This script backs up all critical Air-Side configuration and data
# for migration from SD card to NVMe SSD
#
# Usage: sudo ./backup-air-side.sh [backup_dir]
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="${1:-/home/dpm/air-side-backup-$(date +%Y%m%d-%H%M%S)}"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Air-Side Backup Script${NC}"
echo -e "${BLUE}DPM-V2 NVMe Migration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Backup directory: ${BACKUP_DIR}${NC}"
echo -e "${GREEN}Timestamp: ${TIMESTAMP}${NC}"
echo ""

# Create backup directory structure
echo -e "${YELLOW}[1/10] Creating backup directory structure...${NC}"
mkdir -p "${BACKUP_DIR}"/{config,network,docker,project,sdk,system,docs}
echo -e "${GREEN}✓ Directory structure created${NC}"

# Backup network configuration
echo -e "${YELLOW}[2/10] Backing up network configuration...${NC}"
if [ -f /etc/dhcpcd.conf ]; then
    sudo cp /etc/dhcpcd.conf "${BACKUP_DIR}/network/"
    echo "  ✓ Copied /etc/dhcpcd.conf"
fi

# Get current network interface configuration
ip addr show > "${BACKUP_DIR}/network/ip-addr-show.txt"
ip route show > "${BACKUP_DIR}/network/ip-route-show.txt"
echo "  ✓ Saved network interface state"

# Backup DNS configuration
sudo cp /etc/resolv.conf "${BACKUP_DIR}/network/" 2>/dev/null || echo "  ⚠ No /etc/resolv.conf"
sudo cp /etc/hosts "${BACKUP_DIR}/network/" 2>/dev/null || echo "  ⚠ No custom /etc/hosts"

# Check for NetworkManager or systemd-networkd configs
if [ -d /etc/NetworkManager/system-connections ]; then
    sudo cp -r /etc/NetworkManager/system-connections "${BACKUP_DIR}/network/" 2>/dev/null || echo "  ⚠ No NetworkManager configs"
fi

if [ -d /etc/systemd/network ]; then
    sudo cp -r /etc/systemd/network "${BACKUP_DIR}/network/" 2>/dev/null || echo "  ⚠ No systemd-networkd configs"
fi

echo -e "${GREEN}✓ Network configuration backed up${NC}"

# Backup Docker configuration
echo -e "${YELLOW}[3/10] Backing up Docker configuration...${NC}"
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "${BACKUP_DIR}/docker/containers.txt"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" > "${BACKUP_DIR}/docker/images.txt"
docker inspect payload-manager > "${BACKUP_DIR}/docker/payload-manager-inspect.json" 2>/dev/null || echo "  ⚠ payload-manager not running"

# Save Docker run command recreation script
cat > "${BACKUP_DIR}/docker/recreate-payload-manager.sh" << 'DOCKER_EOF'
#!/bin/bash
# Recreate payload-manager container
# This script rebuilds and runs the payload-manager container

cd ~/DPM-V2/sbc

# Stop and remove old container if exists
docker stop payload-manager 2>/dev/null || true
docker rm payload-manager 2>/dev/null || true

# Rebuild image
docker build -t payload-manager:latest .

# Run container
docker run -d \
    --name payload-manager \
    --restart unless-stopped \
    --network host \
    --device /dev/bus/usb:/dev/bus/usb \
    -v $(pwd)/logs:/app/logs:rw \
    payload-manager:latest

echo "Container started. Check logs with: docker logs -f payload-manager"
DOCKER_EOF

chmod +x "${BACKUP_DIR}/docker/recreate-payload-manager.sh"
echo -e "${GREEN}✓ Docker configuration backed up${NC}"

# Backup DPM-V2 project
echo -e "${YELLOW}[4/10] Backing up DPM-V2 project...${NC}"
rsync -av --exclude='*.o' --exclude='build/' --exclude='logs/' \
    /home/dpm/DPM-V2/ "${BACKUP_DIR}/project/DPM-V2/" 2>&1 | grep -v "^$"
echo -e "${GREEN}✓ DPM-V2 project backed up${NC}"

# Backup Sony SDK
echo -e "${YELLOW}[5/10] Backing up Sony Camera Remote SDK...${NC}"
if [ -d /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8 ]; then
    # Only backup SDK if it exists (large files)
    echo "  Sony SDK found - creating archive..."
    tar -czf "${BACKUP_DIR}/sdk/CrSDK_v2.00.00_20250805a_Linux64ARMv8.tar.gz" \
        -C /home/dpm CrSDK_v2.00.00_20250805a_Linux64ARMv8 2>&1 | grep -v "^$"
    echo -e "${GREEN}✓ Sony SDK archived${NC}"
else
    echo -e "${RED}✗ Sony SDK not found at expected location${NC}"
fi

# Backup system configuration
echo -e "${YELLOW}[6/10] Backing up system configuration...${NC}"
dpkg --get-selections > "${BACKUP_DIR}/system/installed-packages.txt"
pip3 list > "${BACKUP_DIR}/system/python-packages.txt" 2>/dev/null || echo "  ⚠ No pip packages"
uname -a > "${BACKUP_DIR}/system/kernel-info.txt"
cat /etc/os-release > "${BACKUP_DIR}/system/os-release.txt"
df -h > "${BACKUP_DIR}/system/disk-usage.txt"
lsblk > "${BACKUP_DIR}/system/block-devices.txt"
echo -e "${GREEN}✓ System configuration backed up${NC}"

# Backup SSH configuration (if exists)
echo -e "${YELLOW}[7/10] Backing up SSH configuration...${NC}"
if [ -d ~/.ssh ]; then
    cp -r ~/.ssh "${BACKUP_DIR}/config/" 2>/dev/null || echo "  ⚠ Could not backup .ssh"
    echo "  ✓ SSH keys and config backed up"
fi

# Backup user configurations
echo -e "${YELLOW}[8/10] Backing up user configurations...${NC}"
cp ~/.bashrc "${BACKUP_DIR}/config/" 2>/dev/null || echo "  ⚠ No .bashrc"
cp ~/.bash_profile "${BACKUP_DIR}/config/" 2>/dev/null || echo "  ⚠ No .bash_profile"
cp ~/.profile "${BACKUP_DIR}/config/" 2>/dev/null || echo "  ⚠ No .profile"
cp ~/.gitconfig "${BACKUP_DIR}/config/" 2>/dev/null || echo "  ⚠ No .gitconfig"
echo -e "${GREEN}✓ User configurations backed up${NC}"

# Create restoration documentation
echo -e "${YELLOW}[9/10] Creating restoration documentation...${NC}"
cat > "${BACKUP_DIR}/docs/RESTORATION_GUIDE.md" << 'DOC_EOF'
# Air-Side Restoration Guide

## Backup Information
- Backup Date: BACKUP_TIMESTAMP
- Source System: Raspberry Pi 5 (SD Card)
- Destination: NVMe SSD

## Critical Network Configuration
**IMPORTANT:** Air-Side requires static IP for VXLAN bridge to H16 Ground-Side

### Ethernet (eth0) - VXLAN Bridge
- IP Address: `192.168.144.10/24`
- No gateway (point-to-point to H16)
- Purpose: High-speed communication with H16 Android device

### WiFi (wlan0) - Management Access
- DHCP assigned (typically 10.0.1.x/24)
- Default gateway for internet access

## Restoration Steps

### Option A: SD Card Clone (Recommended if successful)
1. Use Raspberry Pi Imager or `dd` to clone SD to NVMe
2. Boot from NVMe
3. Verify network configuration
4. Test Docker container

### Option B: Fresh OS Install (If clone fails)
1. Install Raspberry Pi OS 64-bit on NVMe
2. Run deployment script: `sudo ./deploy-air-side.sh`
3. Restore project: `rsync -av project/DPM-V2/ ~/DPM-V2/`
4. Restore Sony SDK: `tar -xzf sdk/CrSDK*.tar.gz -C ~`
5. Configure network (see below)
6. Build and run Docker container

## Network Configuration Command

```bash
# Configure eth0 with static IP (192.168.144.10)
# This MUST be done for Air-Side to communicate with H16

# Edit /etc/dhcpcd.conf and add:
sudo nano /etc/dhcpcd.conf

# Add these lines at the end:
interface eth0
static ip_address=192.168.144.10/24
noipv6

# Restart networking
sudo systemctl restart dhcpcd
```

## Docker Container Recreation

```bash
cd ~/DPM-V2/sbc
sudo docker/recreate-payload-manager.sh
```

## Verification Checklist

- [ ] Network: `ip addr show eth0` shows 192.168.144.10/24
- [ ] Network: `ping 192.168.144.11` reaches H16 (if powered on)
- [ ] Docker: `docker ps` shows payload-manager running
- [ ] USB: `lsusb` shows Sony camera connected
- [ ] Logs: `docker logs payload-manager` shows camera connected
- [ ] Project: `ls ~/DPM-V2/sbc` shows all source files
- [ ] SDK: `ls ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8` exists

## Troubleshooting

### Network Issues
- Check eth0 configuration: `sudo systemctl status dhcpcd`
- Verify routing: `ip route show`
- Test H16 connectivity: `ping 192.168.144.11`

### Docker Issues
- Check container status: `docker ps -a`
- View logs: `docker logs payload-manager`
- Rebuild image: `cd ~/DPM-V2/sbc && docker build -t payload-manager .`

### Camera Issues
- Check USB: `lsusb | grep Sony`
- Check permissions: `ls -l /dev/bus/usb/*/*`
- Check SDK: Camera must be in PC Remote mode

## Important Files Restored

| Component | Location | Purpose |
|-----------|----------|---------|
| DPM-V2 Project | ~/DPM-V2 | Main project codebase |
| Sony SDK | ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8 | Camera control SDK |
| Network Config | /etc/dhcpcd.conf | Static IP configuration |
| Docker Config | ~/DPM-V2/sbc/Dockerfile | Container build |
| Logs | ~/DPM-V2/sbc/logs | Application logs |

DOC_EOF

# Replace timestamp placeholder
sed -i "s/BACKUP_TIMESTAMP/${TIMESTAMP}/g" "${BACKUP_DIR}/docs/RESTORATION_GUIDE.md"
echo -e "${GREEN}✓ Restoration guide created${NC}"

# Create backup manifest
echo -e "${YELLOW}[10/10] Creating backup manifest...${NC}"
cat > "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << EOF
Air-Side Backup Manifest
========================
Backup Date: ${TIMESTAMP}
Backup Location: ${BACKUP_DIR}

Contents:
---------
config/          User configuration files (.bashrc, .ssh, etc)
network/         Network configuration and state
docker/          Docker container configuration
project/         DPM-V2 project files
sdk/             Sony Camera Remote SDK (compressed)
system/          System package lists and info
docs/            Restoration guide and documentation

Key Files Backed Up:
-------------------
$(find "${BACKUP_DIR}" -type f | wc -l) files
$(du -sh "${BACKUP_DIR}" | cut -f1) total size

Critical Components:
-------------------
✓ DPM-V2 Project Source Code
✓ Sony SDK v2.00.00
✓ Docker Container Configuration
✓ Network Configuration (eth0: 192.168.144.10/24)
✓ System Package List
✓ User Configuration Files

Next Steps:
-----------
1. Copy this backup to external storage for safety
2. Review docs/RESTORATION_GUIDE.md before NVMe migration
3. Use deployment script for fresh OS install if needed
4. Verify network configuration after restore

Backup completed successfully at $(date +"%Y-%m-%d %H:%M:%S")
EOF

echo -e "${GREEN}✓ Backup manifest created${NC}"

# Final summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Backup completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Backup location:${NC} ${BACKUP_DIR}"
echo -e "${YELLOW}Backup size:${NC} $(du -sh "${BACKUP_DIR}" | cut -f1)"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Copy backup to external storage: ${BACKUP_DIR}"
echo "  2. Review restoration guide: ${BACKUP_DIR}/docs/RESTORATION_GUIDE.md"
echo "  3. Use deploy-air-side.sh for fresh NVMe setup if needed"
echo ""
echo -e "${GREEN}Backup manifest: ${BACKUP_DIR}/BACKUP_MANIFEST.txt${NC}"
echo ""
