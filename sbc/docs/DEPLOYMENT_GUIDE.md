# Phase 1 Deployment Guide - Raspberry Pi 5

**Issue:** #72 - Phase 1 Foundation Infrastructure
**Target Platform:** Raspberry Pi 5 (8GB), Ubuntu 24.04 LTS ARM64
**Last Updated:** 2025-11-13

---

## 🎯 Prerequisites

### Hardware
- ✅ Raspberry Pi 5 (8GB RAM)
- ✅ Sony ILCE-1 camera connected via USB
- ✅ Network connectivity (Ethernet or WiFi to 192.168.144.x network)

### Software
- ✅ Ubuntu 24.04 LTS ARM64 installed
- ✅ Docker 28.5.1+ installed
- ✅ Git configured
- ✅ Repository cloned: `git clone https://github.com/unmanned-systems-uk/DPM-V2.git`

### Network Configuration
- Air-Side IP: `192.168.144.20`
- Ground-Side IP: `192.168.144.11` (H16 Android device)
- SystemTools IP: `192.168.0.100` (optional, for development)

---

## 📋 Step-by-Step Deployment

### Step 1: Verify Environment

```bash
# SSH into Raspberry Pi 5
ssh pi@192.168.144.20

# Verify Ubuntu version
lsb_release -a
# Expected: Ubuntu 24.04 LTS

# Verify Docker
docker --version
# Expected: Docker version 28.5.1 or higher

# Navigate to project
cd ~/DPM-V2

# Sync with latest code
git pull origin main

# Verify on main branch
git branch --show-current
# Expected: main
```

---

### Step 2: Run Automated Validation Tests

```bash
# Run pre-deployment validation
bash sbc/tests/validate_phase1.sh
```

**Expected Output:**
```
========================================
Phase 1 Validation Tests
Automated checks without Docker/Pi 5
========================================

[All test suites...]

========================================
Test Results Summary
========================================
Total Tests:  34
Passed:       34
Failed:       0

✅ ALL VALIDATION TESTS PASSED!
```

**If any tests fail:** Stop and investigate before proceeding.

---

### Step 3: Build Docker Image

```bash
cd ~/DPM-V2/sbc

# Build the Docker container
./build_container.sh
```

**Expected Output:**
```
========================================
Payload Manager Container Build Script
(C++ Implementation)
========================================

[Build progress...]

✅ Build successful!
Container: payload-manager:latest
Size: ~XXX MB
```

**Build Time:** Approximately 5-10 minutes on Pi 5

**Troubleshooting:**
- If build fails with `nlohmann-json3-dev` error, the package should already be in Dockerfile
- Check `docker images` to verify image created: `payload-manager:latest`

---

### Step 4: Configure Network Settings (Optional)

If your network differs from defaults, edit configuration:

```bash
# Edit development config for your network
nano ~/DPM-V2/sbc/config/development.json
```

**Key settings to verify:**
```json
{
  "network": {
    "ground_ip": "192.168.144.11",  // Your H16 IP
    "air_ip": "192.168.144.20"      // Your Pi 5 IP
  },
  "logging": {
    "network_systemtools_ip": "192.168.0.100",  // Your dev PC IP (optional)
    "network_systemtools_enabled": true          // Set false if no SystemTools
  }
}
```

---

### Step 5: Start Air-Side Service

```bash
cd ~/DPM-V2/sbc

# Start in production mode (default)
./run_container.sh prod

# OR start in development mode (enables SystemTools logging)
# ./run_container.sh dev
```

**Expected Startup Output:**
```
========================================
   DPM Payload Manager Service
   Air Side - Raspberry Pi
========================================
Version: 1.0.0
Protocol: 1.0
Phase: 1 (Initial Connectivity)
========================================

[INFO] Initializing ConfigManager...
[INFO] ConfigManager initialized - config loaded from JSON files
[INFO] Initializing StructuredLogger with sinks...
[INFO] StructuredLogger initialized with 3 sinks (console, file, network)
[INFO] Initializing HealthMonitor...
[INFO] HealthMonitor initialized with 3-tier retention
[INFO] Loading camera property specifications from camera_properties.json...
[INFO] PropertyLoader initialized successfully
[INFO] Creating camera interface (Sony SDK)...
[INFO] Attempting to connect to Sony camera...
[INFO] Sony camera connected successfully!
[INFO] Creating TCP server on port 5000...
[INFO] Creating UDP broadcaster (target: 192.168.144.11:5001)...
[INFO] Creating heartbeat handler (port 5002)...
[INFO] HealthMonitor broadcasting started: 192.168.144.11:5004 (5 Hz)

========================================
Payload Manager Service Running
========================================
TCP Command Server: 0.0.0.0:5000
UDP Status Broadcast: 192.168.144.11:5001 (5 Hz)
Heartbeat: 192.168.144.11:5002 (1 Hz)
Camera: Sony SDK (connected)
========================================
Press Ctrl+C to stop
========================================

Service started successfully!
```

**Service is now running and ready for testing!**

---

### Step 6: Verify Services

**In a new terminal on Pi 5:**

```bash
# Check container is running
docker ps
# Should show: payload-manager container running

# Check listening ports
ss -tulpn | grep -E '5000|5001|5002|5004|5005'
# Expected:
# 5000 - TCP (LISTEN) - Command server
# 5001 - UDP - Status broadcasts
# 5002 - UDP - Heartbeat
# 5004 - UDP - Health broadcasts
# 5005 - UDP - Log streaming

# Check camera connection
lsusb | grep Sony
# Should show: Sony Corporation device

# Monitor logs in real-time
docker logs -f payload-manager
```

---

### Step 7: Test Phase 1 Components

Follow the testing plan:

```bash
# View testing checklist
cat ~/DPM-V2/sbc/docs/PHASE1_TESTING_PLAN.md
```

**Quick Smoke Tests:**

#### Test ConfigManager
```bash
# Check logs for config loading
docker logs payload-manager | grep -i "configmanager"
# Expected: "ConfigManager initialized - config loaded from JSON files"
```

#### Test StructuredLogger
```bash
# Check structured JSON logs
docker logs payload-manager | tail -20
# Expected: JSON-formatted log entries with timestamp, level, context, message
```

#### Test HealthMonitor (from Ground-Side or dev PC)
```bash
# Listen for health broadcasts on UDP 5004
nc -ul 5004
# Expected: JSON health snapshots every 5 seconds with system/camera/network metrics
```

---

## 🧪 Full Testing Sequence

Once services are running, execute full test suite:

1. **Open PHASE1_TESTING_PLAN.md:** `~/DPM-V2/sbc/docs/PHASE1_TESTING_PLAN.md`
2. **Execute each test** from the 6 test suites (13 total tests)
3. **Update results** in the testing plan document
4. **Report results** on Issue #72

---

## 🔧 Troubleshooting

### Container Won't Start
```bash
# Check Docker logs for errors
docker logs payload-manager

# Check if port already in use
ss -tulpn | grep 5000

# Rebuild container
docker stop payload-manager
docker rm payload-manager
cd ~/DPM-V2/sbc && ./build_container.sh
```

### Camera Not Detected
```bash
# Check USB connection
lsusb | grep Sony

# Check camera is on
# Check USB cable is connected

# Restart container
docker restart payload-manager
```

### No UDP Broadcasts Received
```bash
# Verify Ground-Side IP in config
cat ~/DPM-V2/sbc/config/default.json | grep ground_ip

# Check firewall
sudo ufw status
# If active, allow UDP ports: sudo ufw allow 5001:5005/udp

# Verify network connectivity
ping 192.168.144.11
```

### Log Streaming Not Working
```bash
# Check NetworkSink configuration
docker logs payload-manager | grep -i "network"

# Verify SystemTools IP is reachable
ping 192.168.0.100

# Try enabling log streaming via command (see PHASE1_TESTING_PLAN.md)
```

---

## 🛑 Stopping Services

```bash
# Graceful shutdown (Ctrl+C in running terminal)
# OR
docker stop payload-manager

# Remove container
docker rm payload-manager

# Clean up
docker system prune -f
```

---

## 📊 Health Check Commands

```bash
# Quick status check
docker ps | grep payload-manager

# Check CPU/Memory usage
docker stats payload-manager --no-stream

# Check logs for errors
docker logs payload-manager | grep -i error

# Check service uptime
docker inspect payload-manager | grep StartedAt
```

---

## 🎯 Success Criteria

**Air-Side is successfully deployed if:**
- ✅ Container builds without errors
- ✅ Service starts and shows "Payload Manager Service Running"
- ✅ Camera connects (or shows reconnection attempts if camera off)
- ✅ ConfigManager loads without errors
- ✅ StructuredLogger outputs JSON logs
- ✅ HealthMonitor broadcasts UDP packets
- ✅ TCP server listens on port 5000
- ✅ No crashes or errors in logs for 5+ minutes

---

## 🚀 Next Steps After Deployment

1. **Execute full test suite** (PHASE1_TESTING_PLAN.md)
2. **Test Ground-Side integration** (H16 Android app)
3. **Test SystemTools integration** (Python diagnostics)
4. **Verify end-to-end command flow**
5. **Update Issue #72 with test results**
6. **Mark Issue #72 as [TESTED] if all pass**

---

## 📝 Notes

- **Development Mode:** Set `DPM_ENVIRONMENT=development` for SystemTools log streaming
- **Production Mode:** Default, disables SystemTools streaming to save bandwidth
- **Log Files:** Located at `/var/log/dpm/air-side.jsonl` inside container
- **Config Override:** Place `config/local.json` for runtime overrides (not in git)

---

**Deployment Guide Version:** 1.0
**Phase:** 1 - Foundation Infrastructure
**Status:** Ready for Pi 5 deployment
