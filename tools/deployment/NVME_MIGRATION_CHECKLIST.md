# NVMe Migration Checklist
## DPM-V2 Air-Side - Raspberry Pi 5

**Migration Date:** _______________
**Performed By:** _______________
**NVMe Model:** _______________

---

## Pre-Migration (Current SD Card System)

### 1. Pre-Flight Checks
- [ ] Air-Side payload-manager is running
- [ ] Camera is connected via USB
- [ ] H16 Ground-Side can communicate with Air-Side
- [ ] No critical operations in progress
- [ ] Recent git commits are pushed to remote

**Commands to verify:**
```bash
docker ps | grep payload-manager
lsusb | grep Sony
ping 192.168.144.11  # Test H16 connectivity
git status
```

### 2. Run Backup Script
- [ ] Execute backup script: `sudo ~/DPM-V2/tools/deployment/backup-air-side.sh`
- [ ] Backup completed without errors
- [ ] Note backup location: _______________________
- [ ] Verify backup size (should be several GB): `du -sh /path/to/backup`

**Backup location:** `/home/dpm/air-side-backup-YYYYMMDD-HHMMSS`

### 3. Copy Backup to External Storage
- [ ] USB drive or external SSD connected
- [ ] Copy backup directory to external storage
- [ ] Verify copy completed: compare file counts
- [ ] **Keep external backup safe - this is your recovery option!**

**Copy command:**
```bash
rsync -av --progress /home/dpm/air-side-backup-* /media/usb-drive/
```

### 4. Document Current Network State
- [ ] Record current IP addresses:
  - eth0 (VXLAN): _______________  (should be 192.168.144.10)
  - wlan0 (WiFi): _______________ (management access)
- [ ] Record WiFi SSID: _______________
- [ ] Test H16 connectivity: `ping 192.168.144.11`

### 5. Stop Docker Container
- [ ] Stop payload-manager gracefully: `docker stop payload-manager`
- [ ] Verify container stopped: `docker ps -a`

### 6. Shutdown System
- [ ] Safe shutdown: `sudo shutdown -h now`
- [ ] Wait for Pi to power off completely (LEDs off)

---

## Hardware Migration

### 7. Install NVMe SSD
- [ ] Pi 5 powered off and unplugged
- [ ] NVMe SSD installed in Pi 5 M.2 slot (bottom of board)
- [ ] Secure with screw
- [ ] NVMe properly seated

### 8. Update Pi 5 Boot Configuration (if needed)
- [ ] Check if Pi 5 firmware supports NVMe boot
- [ ] Update bootloader if necessary (`sudo rpi-eeprom-update`)
- [ ] Set boot order to NVMe first

---

## Migration Path Selection

Choose ONE migration path:

### **Option A: SD Card Clone** (Fastest, but may fail)
- [ ] Boot from SD card
- [ ] Clone SD to NVMe using tool (e.g., `dd`, Raspberry Pi Imager)
- [ ] Shutdown and remove SD card
- [ ] Boot from NVMe
- [ ] **Go to "Post-Migration Verification"**

**Clone command (if using dd):**
```bash
# CAUTION: Verify device names carefully!
sudo dd if=/dev/mmcblk0 of=/dev/nvme0n1 bs=4M status=progress
sync
```

### **Option B: Fresh OS Install** (More reliable, takes longer)
- [ ] Download Raspberry Pi OS 64-bit (Debian bookworm or later)
- [ ] Flash OS to NVMe using Raspberry Pi Imager
- [ ] Boot Pi 5 from NVMe
- [ ] Complete OS setup wizard (username: dpm, password: your choice)
- [ ] **Go to "Fresh Install Deployment"**

---

## Fresh Install Deployment (Option B only)

### 9. Run Deployment Script
- [ ] SSH into fresh Pi 5 system
- [ ] Copy deployment script to Pi
- [ ] Make executable: `chmod +x deploy-air-side.sh`
- [ ] Run deployment: `sudo ./deploy-air-side.sh`
- [ ] Deployment completed without errors
- [ ] **REBOOT SYSTEM:** `sudo reboot`

### 10. Restore Project Files
After reboot:

- [ ] Copy backup to Pi (from external storage)
- [ ] Restore DPM-V2 project:
  ```bash
  cd /home/dpm
  rsync -av /path/to/backup/project/DPM-V2/ ~/DPM-V2/
  ```
- [ ] Restore Sony SDK:
  ```bash
  cd /home/dpm
  tar -xzf /path/to/backup/sdk/CrSDK*.tar.gz
  ```
- [ ] Set ownership: `chown -R dpm:dpm ~/DPM-V2 ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8`

### 11. Restore User Configurations
- [ ] Restore SSH keys:
  ```bash
  cp -r /path/to/backup/config/.ssh ~/
  chmod 700 ~/.ssh
  chmod 600 ~/.ssh/*
  ```
- [ ] Restore .bashrc, .gitconfig, etc:
  ```bash
  cp /path/to/backup/config/.bashrc ~/
  cp /path/to/backup/config/.gitconfig ~/
  ```

---

## Post-Migration Verification (Both Options)

### 12. Verify Network Configuration
- [ ] Check eth0 has static IP: `ip addr show eth0`
  - Should show: `inet 192.168.144.10/24`
- [ ] Check wlan0 is connected: `ip addr show wlan0`
- [ ] Test routing: `ip route show`
- [ ] **Test H16 connectivity:** `ping 192.168.144.11`
  - ⚠️ H16 must be powered on and connected for this to work

**If network issues:**
```bash
sudo systemctl restart dhcpcd
sudo systemctl status dhcpcd
cat /etc/dhcpcd.conf | grep -A 3 "interface eth0"
```

### 13. Verify Docker Installation
- [ ] Docker installed: `docker --version`
- [ ] User in docker group: `groups | grep docker`
- [ ] Docker service running: `sudo systemctl status docker`
- [ ] Test Docker: `docker run hello-world`

### 14. Build and Run Payload Manager Container
- [ ] Navigate to project: `cd ~/DPM-V2/sbc`
- [ ] Build Docker image:
  ```bash
  docker build -t payload-manager:latest .
  ```
- [ ] Run container:
  ```bash
  docker run -d \
      --name payload-manager \
      --restart unless-stopped \
      --network host \
      --device /dev/bus/usb:/dev/bus/usb \
      -v $(pwd)/logs:/app/logs:rw \
      payload-manager:latest
  ```
- [ ] Container running: `docker ps | grep payload-manager`

### 15. Verify Camera Connection
- [ ] Camera connected via USB
- [ ] Camera in PC Remote mode (check LCD)
- [ ] USB device detected: `lsusb | grep Sony`
- [ ] Check Docker logs:
  ```bash
  docker logs -f payload-manager
  ```
- [ ] Look for: "Camera fully connected and ready!"
- [ ] No enumeration errors (0x34563)

### 16. Verify Air-Side Functionality
- [ ] TCP server listening: `netstat -tlnp | grep 5000`
- [ ] UDP broadcaster active: Check logs
- [ ] Camera properties readable: Check UDP status messages
- [ ] No errors in Docker logs

### 17. Test Ground-Side Communication
- [ ] Power on H16 Ground-Side
- [ ] H16 connects to Air-Side TCP (check logs)
- [ ] H16 receives UDP status broadcasts
- [ ] Manual focus commands work (if camera connected)
- [ ] Camera property changes reflected in H16 app

---

## Performance Verification

### 18. NVMe Performance Check
- [ ] Check NVMe is detected: `lsblk | grep nvme`
- [ ] Check disk usage: `df -h`
- [ ] Test read speed:
  ```bash
  sudo hdparm -t /dev/nvme0n1
  ```
  Expected: >400 MB/sec
- [ ] Test write speed:
  ```bash
  dd if=/dev/zero of=~/test.tmp bs=1M count=1024 oflag=direct
  ```
  Expected: >400 MB/sec
- [ ] Remove test file: `rm ~/test.tmp`

### 19. System Health Check
- [ ] CPU temperature acceptable: `vcgencmd measure_temp` (should be <70°C)
- [ ] Memory usage: `free -h`
- [ ] Disk space: `df -h /` (should have plenty free on NVMe)
- [ ] Docker resource usage: `docker stats --no-stream`

---

## Cleanup and Documentation

### 20. Document Migration
- [ ] Record NVMe model and size: _______________
- [ ] Record final eth0 IP: _______________
- [ ] Record any issues encountered: _______________
- [ ] Update project documentation if needed

### 21. Backup New NVMe System
- [ ] Run backup script again on NVMe system
- [ ] Store NVMe backup for future reference
- [ ] **Keep SD card backup safe as emergency recovery**

### 22. Cleanup Old Backup
- [ ] Backup files copied to safe location
- [ ] External storage backup verified
- [ ] Temporary files cleaned up

---

## Rollback Plan (If Migration Fails)

### Emergency Rollback to SD Card
1. Power off Pi 5
2. Remove NVMe SSD
3. Insert original SD card
4. Boot from SD card
5. System should work as before migration

### If SD Card Won't Boot
1. Use external backup
2. Flash fresh OS to new SD card
3. Run deployment script
4. Restore from backup on external storage

---

## Success Criteria

### ✅ Migration Successful If:
- [ ] Pi 5 boots from NVMe
- [ ] Network configuration correct (eth0: 192.168.144.10/24)
- [ ] Docker running and container operational
- [ ] Camera connects and responds to commands
- [ ] H16 can communicate with Air-Side
- [ ] No functionality lost from SD card system
- [ ] NVMe performance gains visible (faster boot, file operations)

---

## Notes and Issues

Use this space to record any problems encountered and solutions:

```
Date/Time | Issue | Resolution
---------|-------|------------
         |       |
         |       |
         |       |
```

---

## Post-Migration Tasks

### Optional Improvements (After successful migration)
- [ ] Set up automatic backups
- [ ] Configure log rotation for Docker logs
- [ ] Set up monitoring/alerting
- [ ] Test camera file transfer from camera to NVMe
- [ ] Benchmark file transfer speeds vs SD card

---

## Sign-off

**Migration completed by:** _______________
**Date:** _______________
**Verification completed:** ☐ Yes ☐ No
**System operational:** ☐ Yes ☐ No
**Issues remaining:** _______________

---

**For assistance, refer to:**
- Deployment script: `~/DPM-V2/tools/deployment/deploy-air-side.sh`
- Backup script: `~/DPM-V2/tools/deployment/backup-air-side.sh`
- Restoration guide: `(backup directory)/docs/RESTORATION_GUIDE.md`
- Deployment summary: `~/DEPLOYMENT_SUMMARY.txt`
