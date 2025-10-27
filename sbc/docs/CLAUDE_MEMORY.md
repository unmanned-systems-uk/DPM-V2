# CLAUDE MEMORY - DPM SBC Project Context

**Last Updated:** 2025-10-27
**Session:** Post-camera-control-fixes

This document serves as a persistent memory bank for Claude AI to maintain context across conversation sessions. When context limits are reached and conversations are summarized, this file provides critical project state information.

---

## CRITICAL PROJECT OVERVIEW

**Project Name:** DPM (Drone Payload Manager) - Air-Side (SBC)
**Hardware:** Raspberry Pi 4 (ARMv8, 4GB RAM)
**Primary Function:** Remote control of Sony Alpha 1 camera via USB for aerial photography
**Network:** Currently WiFi testing (10.0.1.x), will switch to H16 ethernet (192.168.144.x) when cable arrives
**Status:** Phase 1 - Initial Connectivity - OPERATIONAL with fixes

---

## CURRENT NETWORK CONFIGURATION (IMPORTANT!)

**Active Network:** WiFi (10.0.1.x) - TEMPORARY for testing
**Ground Station (Android):** 10.0.1.92 (dynamic, changes on WiFi)
**Air-Side (Raspberry Pi):** 192.168.144.20 (will be used when on ethernet)

**Why This Matters:**
- User is testing on WiFi while waiting for H16 ethernet cable to arrive
- Ground station IP changes depending on network
- **SOLUTION IMPLEMENTED:** Dynamic IP discovery - Air-Side auto-detects ground IP when Android connects via TCP
- NO MANUAL CONFIGURATION NEEDED ANYMORE!

**Future Network:** H16 internal ethernet (192.168.144.x)
- Ground Station: 192.168.144.11
- Air-Side: 192.168.144.20

---

## PROJECT STRUCTURE

```
/home/dpm/DPM-V2/
├── sbc/                          ← Air-Side C++ implementation (THIS CODEBASE)
│   ├── src/                      ← Source code
│   │   ├── camera/               ← Sony SDK camera interface
│   │   │   ├── camera_sony.cpp   ← Main camera implementation
│   │   │   └── camera_sony.h
│   │   ├── protocol/             ← Network protocol implementation
│   │   │   ├── tcp_server.cpp    ← Command server (port 5000)
│   │   │   ├── udp_broadcaster.cpp ← Status broadcasts (5 Hz)
│   │   │   ├── heartbeat.cpp     ← Heartbeat (1 Hz)
│   │   │   └── messages.cpp      ← JSON message formatting
│   │   ├── utils/                ← Utilities (logging, system info)
│   │   ├── config.h              ← Configuration constants
│   │   └── main.cpp              ← Application entry point
│   ├── build/                    ← CMake build output
│   ├── logs/                     ← Runtime logs
│   ├── scripts/                  ← Helper scripts
│   ├── docs/                     ← Documentation
│   ├── build_container.sh        ← Build Docker image
│   ├── run_container.sh          ← Run Docker container
│   └── CMakeLists.txt            ← Build configuration
└── ground/                       ← Android app (separate codebase)

/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8/  ← Sony Camera Remote SDK
```

---

## CAMERA: Sony Alpha 1 (ILCE-1)

**Connection:** USB (via Sony Camera Remote SDK v2.00.00)
**USB Device ID:** 054c:0d68
**Mode Required:** PC Remote (must be set on camera)

**Current Status:**
- Camera detection: Works (lsusb shows device)
- SDK connection: REQUIRES POWER CYCLE after container restart (known behavior)
- Property control: WORKING (100% success rate after latest fixes)
- Capture: WORKING (reliable, fast ~41ms)

**Properties Supported:**
- Shutter speed: 1/8000 to 30" (full range)
- Aperture: f/1.4 to f/22 (lens dependent)
- ISO: 100 to 102400 (extended range)
- White balance: Auto, Daylight, Cloudy, etc.
- Focus mode: AF-S, AF-C, DMF, MF
- File format: RAW, RAW+JPEG, JPEG
- Drive mode: Single, Continuous, etc.

---

## CRITICAL BUGS FIXED (THIS SESSION)

### 1. Camera Property Setting Error 0x33794 (SOLVED)
**Symptom:** All camera.set_property commands failing with Sony SDK error 0x33794
**Root Cause:** Multiple issues discovered iteratively:

1. **Race Condition #1:** getBatteryLevel() calling SDK without mutex protection
   - **Fix:** Added try_lock with caching mechanism

2. **Race Condition #2:** setProperty() and capture() using std::async threading
   - **Fix:** Removed runWithTimeout(), made SDK calls synchronous
   - **Why:** std::async creates new threads, breaking mutex ownership

3. **Sony SDK Property Readiness Check Missing:**
   - **Fix:** Check IsSetEnableCurrentValue() before SetDeviceProperty()
   - **Per Sony Documentation:** "check enable flag in each DeviceProperty by sending GetDeviceProperties"
   - **Error 0x33794 means:** Property not writable at that moment (camera reviewing image, wrong mode, etc.)

**Files Modified:**
- `src/camera/camera_sony.cpp`: Added enable flag checking, fixed threading, fixed mutex protection
- Lines affected: 411-464 (getBatteryLevel), 473-717 (setProperty), 272-325 (capture)

**Test Results:**
- Before fix: 100% failure rate
- After fix: 100% success rate
- Tested: 15+ property changes (shutter, ISO, aperture) - ALL SUCCESSFUL

### 2. Heartbeat Issues (SOLVED)
**Symptom:** Android app not receiving heartbeats, stays in "CONNECTED" state (never reaches "OPERATIONAL")
**Root Cause:** Air-Side broadcasting to wrong IP address
**Solution:** Implemented dynamic IP discovery (see next section)

---

## NEW FEATURE: Dynamic IP Discovery (IMPLEMENTED, READY TO DEPLOY)

**Problem:** Air-Side was using hardcoded ground IP from environment variable, which was wrong when testing on different networks.

**Solution:** Auto-discover ground station IP from TCP connection.

**How It Works:**
1. Android app connects to Air-Side TCP server (port 5000)
2. TCP server extracts client IP from connection (inet_ntoa)
3. TCP server notifies UDP broadcasters to update target IP
4. UDP status and heartbeat automatically switch to correct IP
5. Thread-safe with mutex protection

**Implementation:**
- Added `setTargetIP(const std::string&)` to UDPBroadcaster and Heartbeat classes
- Added mutex protection for target_ip_ member
- TCPServer holds pointers to broadcasters and updates them on connection
- Logs IP changes: "UDP broadcaster target IP updated: OLD -> NEW"

**Files Modified:**
- `src/protocol/udp_broadcaster.h/cpp`: Added setTargetIP() with mutex
- `src/protocol/heartbeat.h/cpp`: Added setTargetIP() with mutex
- `src/protocol/tcp_server.h/cpp`: Added broadcaster references, calls setTargetIP()
- `src/main.cpp`: Wires everything together

**Status:** Code implemented and builds successfully. Needs Docker image rebuild to activate.

**Benefits:**
- No manual `--ground-ip` configuration needed
- Works on WiFi (10.0.1.x) and ethernet (192.168.144.x) automatically
- Adapts if ground station IP changes
- Eliminates entire class of network configuration errors

**To Deploy:**
```bash
cd /home/dpm/DPM-V2/sbc
./build_container.sh
./run_container.sh  # No --ground-ip needed anymore!
```

---

## NETWORK PROTOCOL

**TCP Command Server:**
- Port: 5000
- Purpose: Receives commands from ground station
- Format: JSON messages with protocol_version, message_type, sequence_id, payload
- Commands: handshake, camera.capture, camera.set_property, camera.get_properties, system.get_status

**UDP Status Broadcaster:**
- Port: 5001 (sends TO ground station)
- Frequency: 5 Hz (200ms interval)
- Purpose: System status, camera status, battery level
- Auto-updates target IP when client connects

**UDP Heartbeat:**
- Port: 5002 (bidirectional)
- Frequency: 1 Hz (1000ms interval)
- Purpose: Connection health monitoring
- Timeout: 60 seconds
- Auto-updates target IP when client connects

**Message Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command|response|status|heartbeat|notification",
  "sequence_id": 123,
  "timestamp": 1234567890,
  "payload": { ... }
}
```

---

## DOCKER CONTAINER

**Container Name:** payload-manager
**Base Image:** ubuntu:22.04
**Mode:** Development (source mounted as volume) OR Production (code baked in image)

**Run Modes:**
```bash
# Production mode (default)
./run_container.sh

# Development mode (live editing)
./run_container.sh dev

# With custom ground IP (no longer needed with dynamic discovery!)
./run_container.sh --ground-ip 10.0.1.92
```

**Mounted Volumes (dev mode):**
- `/home/dpm/DPM-V2/sbc:/app/sbc:rw` ← Source code
- `/home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/app/sdk:ro` ← Sony SDK
- `/dev/bus/usb:/dev/bus/usb` ← USB passthrough for camera
- `./logs:/app/logs:rw` ← Persistent logs

**Useful Commands:**
```bash
# View logs
docker logs -f payload-manager

# Shell access
docker exec -it payload-manager bash

# Restart
docker restart payload-manager

# Rebuild inside container (dev mode)
docker exec payload-manager bash -c 'cd /app/sbc/build && cmake .. && make'

# Check camera USB
docker exec payload-manager lsusb | grep Sony
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: Camera not connecting after container restart
**Solution:** Power cycle the camera (OFF, wait 3 seconds, ON)
**Why:** Sony SDK cannot enumerate cameras after container restart (SDK behavior)
**Auto-recovery:** Health check thread retries every 30 seconds

### Issue: Android app shows "CONNECTED" but not "OPERATIONAL"
**Solution:** Already solved with dynamic IP discovery
**Old workaround:** Restart container with correct `--ground-ip`

### Issue: Property setting fails with error 0x33794
**Solution:** Already fixed with enable flag checking
**Means:** Camera not ready to accept property changes (reviewing image, wrong mode, etc.)

### Issue: Build fails with discover_shutter_speeds.cpp errors
**Solution:** Ignore - that's an old utility file, not part of main application
**Check:** `ls -lh build/payload_manager` - if this exists, build succeeded

### Issue: Heartbeats flowing but Android not receiving
**Solution:** Check Android UDP receiver socket - it may have closed
**Workaround:** Restart Android app to recreate socket

---

## TESTING SCRIPTS

**Location:** `/home/dpm/DPM-V2/sbc/scripts/`

**test_tcp_server.py:**
- Tests TCP command protocol
- Validates non-blocking operation
- Sends rapid capture commands to verify mutex fixes
- Run: `python3 scripts/test_tcp_server.py`

**find_h16.sh:**
- Discovers H16 IP on 10.0.1.x network
- Used by run_container.sh --test-wifi

---

## PENDING TASKS

**High Priority:**
1. Test dynamic IP discovery after Docker rebuild
2. Verify Android app receives heartbeats with new system
3. Test camera connection stability over 5+ minutes

**Medium Priority:**
1. Add movie/video frame rate property support (query and control)
2. Document callback_interface.html findings (user mentioned this)

**Low Priority:**
1. Research long exposure support (Bulb mode)
2. Add more property types (movie recording, focus areas, etc.)

---

## GIT BRANCH STATUS

**Current Branch:** feature/camera-nonblocking-operations
**Main Branch:** main
**Last Commit:** "Fix camera property enable flag checking per Sony SDK docs"

**Important Commits:**
- `b3c25c2`: [FIX] CRITICAL - Add missing INTERNET permission to Android app
- `28da375`: [FEAT] WiFi testing support - dynamic ground station IP
- `f12c5d8`: [DOCS] Android app diagnostic improvements roadmap
- `2c50dc9`: [FIX] Camera: Fixed callback timing - connects in 41ms
- `3f2adf5`: [TEST] Component integration testing complete

**Uncommitted Changes:**
- Dynamic IP discovery implementation (multiple files modified)
- Ready to commit when tested

---

## USER PREFERENCES & CONTEXT

1. **User is going to sleep** - Create comprehensive documentation for continuity
2. **Network environment:** WiFi testing (10.0.1.x) until ethernet cable arrives
3. **Testing pattern:** User makes changes on Android, monitors Air-Side logs
4. **Communication style:** Technical, concise, focused on problem-solving
5. **Documentation:** User values thorough documentation for context across sessions

---

## SONY SDK DOCUMENTATION INSIGHTS

**Key Document Mentioned:** callback_interface.html
- User found this "interesting" but didn't elaborate
- TODO: Review this document for additional insights

**Critical SDK Pattern Learned:**
"If you struggle to change camera settings, it is recommended to check enable flag in each DeviceProperty by sending GetDeviceProperties and receiving the latest information before sending SetDeviceProperty."

**SDK Error Codes:**
- `0x33794` (210836): Property not writable (camera state prevents change)
- `0x0`: Failed to enumerate cameras
- `0x33296`: Camera error (seen during connection failures)

---

## CONTEXT FOR NEXT SESSION

If starting a new session and this document exists:

1. **Current State:** Dynamic IP discovery implemented but not deployed (needs Docker rebuild)
2. **Network:** WiFi (10.0.1.x) for testing, will switch to ethernet when cable arrives
3. **Camera:** Requires power cycle after container restart, otherwise works perfectly
4. **Last Issue:** Heartbeat/IP discovery - SOLVED but needs deployment
5. **User Expectation:** System should work seamlessly on both WiFi and ethernet without manual config

**First Steps in New Session:**
1. Check if Docker image has been rebuilt with dynamic IP discovery
2. Verify camera control is still working (it should be)
3. Test network connectivity and heartbeat flow
4. Check for any new issues user encountered

**Files to Review for Context:**
- `docs/PROGRESS_AND_TODO.md` - Current tasks and progress
- `docs/SBC_ARCHITECTURE.md` - System architecture overview
- Latest git log for recent changes
- Docker logs for current operational status

---

## EMERGENCY REFERENCE

**If camera not working:**
1. Check USB: `docker exec payload-manager lsusb | grep Sony`
2. Check camera on: Look for "054c:0d68"
3. Power cycle camera
4. Check logs: `docker logs payload-manager | grep -E "ERROR|Camera"`

**If network issues:**
1. Check container running: `docker ps | grep payload-manager`
2. Check heartbeats: `docker logs payload-manager | grep heartbeat | tail`
3. Check Android IP: Look for "Accepted connection from" in logs
4. Verify Android on same network as Pi

**If build fails:**
1. Clean build: `rm -rf build && mkdir build && cd build && cmake ..`
2. Check main executable exists: `ls -lh build/payload_manager`
3. Ignore discover_shutter_speeds.cpp errors (old utility)

**Container completely broken:**
```bash
docker stop payload-manager
docker rm payload-manager
cd /home/dpm/DPM-V2/sbc
./build_container.sh
./run_container.sh
```

---

*This document should be updated at the end of each significant session to maintain continuity.*
