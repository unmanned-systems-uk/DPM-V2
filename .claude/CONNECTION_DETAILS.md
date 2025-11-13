# DPM-V2 System Connection Details

**Purpose:** Reference for all Claude Code sessions to access DPM-V2 systems
**Last Updated:** 2025-11-13

---

## 🔗 System Access Matrix

| System | IP Address | Port | User | Authentication | Status |
|--------|------------|------|------|----------------|--------|
| **Air-Side (Pi 5)** | 10.0.1.53 | 22 (SSH) | dpm | Password/Key | ✅ Running |
| **Ground-Side (H16)** | 10.0.1.92 | 5555 (ADB) | - | ADB | ✅ Running |
| **SystemTools** | Local | - | anthony | Local user | ✅ Ready |
| **Jetson Orin NX** | 10.0.1.113 | 22 (SSH) | dev | Password/Key | ✅ Setup Complete |

---

## 🔵 Air-Side (Raspberry Pi 5)

### SSH Access
```bash
ssh dpm@10.0.1.53
```

### Docker Commands
```bash
# Check running containers
docker ps

# Access payload-manager container
docker exec -it payload-manager /bin/bash

# View logs
docker logs payload-manager --tail=100 --follow

# Restart container
docker restart payload-manager
```

### Service Verification
```bash
# Check if services are running
docker ps | grep payload-manager

# Check logs for Phase 1 initialization
docker logs payload-manager 2>&1 | grep -E "ConfigManager|StructuredLogger|HealthMonitor"
```

### File Locations (Inside Container)
- **Config:** `/app/config/`
- **Logs:** `/var/log/dpm/air-side.jsonl`
- **Binary:** `/app/payload_manager`

---

## 🟣 Ground-Side (Android H16)

### ADB Connection
```bash
# Connect to device
adb connect 10.0.1.92:5555

# Verify connection
adb devices

# Disconnect
adb disconnect 10.0.1.92:5555
```

### App Control
```bash
# Check if app is running
adb shell "ps | grep uk.unmannedsystems.dpm_android"

# View app logs
adb logcat -s DPM

# Clear app data (reset)
adb shell pm clear uk.unmannedsystems.dpm_android

# Force stop app
adb shell am force-stop uk.unmannedsystems.dpm_android

# Start app
adb shell am start -n uk.unmannedsystems.dpm_android/.MainActivity
```

### Log Access
```bash
# View structured logs
adb logcat -s DPM:* StructuredLogger:*

# Export logs
adb pull /sdcard/Android/data/uk.unmannedsystems.dpm_android/files/logs/
```

### ADB Log Bridge (for SystemTools)
```bash
# Forward local port to device
adb forward tcp:5008 tcp:5008

# Remove forwarding
adb forward --remove tcp:5008
```

### Physical Operations
**User Available For:**
- Starting/stopping the app
- Checking UI displays
- Triggering user interactions
- Verifying visual feedback
- Capturing screenshots

---

## 🟡 SystemTools (Development Machine)

### Log Aggregator

**Location:** `/home/anthony/DPM-V2/SystemTools/`

**Start Log Aggregator:**
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_aggregator.py
```

**With Filters:**
```bash
# Filter by level
python3 log_aggregator.py --level=ERROR

# Filter by domain
python3 log_aggregator.py --domain=AIR

# Export to JSON
python3 log_aggregator.py --export-json=output.json

# Replay from file
python3 log_aggregator.py --replay=output.json
```

**Configuration:**
- **Config File:** `config/log_aggregator.json`
- **UDP Port (Air):** 5007
- **TCP Port (Ground):** 5008

**Testing:**
```bash
# Test UDP listener
python3 test_log_aggregator.py
```

---

## 🟢 Jetson Orin NX (Future Platform)

### SSH Access
```bash
ssh dev@10.0.1.113
```

### Status
- ✅ Setup complete (Issue #80)
- ✅ 457 packages updated
- ✅ CUDA 11.4 configured
- ✅ Docker verified
- ⏳ DPM-V2 deployment pending (Issue #52)

---

## 🌐 Network Ports

### Air-Side (Outbound)
- **5000:** TCP command server (Ground-Side connects)
- **5004:** UDP health broadcast → Ground-Side (5 Hz)
- **5005:** UDP logs on-demand → Ground-Side (when enabled)
- **5007:** UDP logs always-on → SystemTools (dev mode)

### Ground-Side (Inbound)
- **5004:** UDP health receiver (from Air-Side)
- **5005:** UDP log receiver (from Air-Side, on-demand)
- **5008:** TCP log sender → SystemTools (via ADB bridge)

### SystemTools (Inbound)
- **5007:** UDP log receiver (from Air-Side)
- **5008:** TCP log receiver (from Ground-Side via ADB)

---

## 🔧 Prerequisites for Testing

### ADB Installation (if not present)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install adb

# Verify installation
adb --version
```

### Python Requirements (SystemTools)
```bash
cd /home/anthony/DPM-V2/SystemTools
pip3 install -r requirements.txt
```

**Required Packages:**
- rich (terminal UI)
- Standard library only

---

## 🧪 Quick Verification Commands

### Check All Systems Status
```bash
# Air-Side
ssh dpm@10.0.1.53 "docker ps | grep payload"

# Ground-Side
adb connect 10.0.1.92:5555 && adb shell "ps | grep dpm"

# SystemTools
ls -la /home/anthony/DPM-V2/SystemTools/log_aggregator.py
```

### Verify Network Connectivity
```bash
# Ping Air-Side
ping -c 2 10.0.1.53

# Ping Ground-Side
ping -c 2 10.0.1.92

# Check UDP ports (requires netcat)
nc -ul 5007  # Listen for Air-Side logs
```

---

## 📞 When User Assistance Needed

**SSH Password Required:**
- User will provide password for `dpm@10.0.1.53` when needed

**ADB Not Installed:**
- Ask user to install: `sudo apt install adb`
- Or user can execute ADB commands directly

**Physical H16 Operations:**
- App start/stop
- UI verification
- Screenshot capture
- Button presses
- Visual confirmation

---

## 🔐 Security Notes

- **Passwords:** Not stored in repository, provided at runtime
- **SSH Keys:** User's keys in `~/.ssh/` (if configured)
- **ADB:** Requires device authorization (user approves on device)
- **Network:** All systems on local 10.0.1.x subnet (not exposed externally)

---

## 📚 Related Documentation

- **Air-Side Deployment:** `sbc/docs/DEPLOYMENT_GUIDE.md`
- **Pi 5 Session Start:** `sbc/docs/PI5_SESSION_START.md`
- **Phase 1 Testing:** `sbc/docs/PHASE1_TESTING_PLAN.md`
- **SystemTools README:** `SystemTools/README.md`

---

**This file should be read at the start of any testing or deployment session!**
