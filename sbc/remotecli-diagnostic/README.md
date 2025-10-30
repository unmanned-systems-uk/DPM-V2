# RemoteCli v2 - Enhanced Diagnostic Tool

**Version:** 2.0
**Created:** October 30, 2025
**Purpose:** Sony Camera Remote SDK diagnostic tool with comprehensive logging

---

## Overview

RemoteCli v2 is an enhanced version of Sony's RemoteCli sample application with comprehensive diagnostic logging capabilities. It's designed specifically for troubleshooting Sony camera connection and control issues on the DPM Air-Side platform.

### Key Features

✅ **Comprehensive Logging**
- Timestamped log entries with millisecond precision
- Dual output: Console and file (`/app/logs/remotecli_v2.log`)
- Detailed SDK call results with error codes
- Connection state tracking
- Property access logging
- Callback event logging

✅ **Enhanced Diagnostics**
- Timing measurements for all SDK operations
- Detailed camera enumeration information
- Connection establishment tracking
- Property read/write diagnostics
- Error code translation

✅ **Docker Containerization**
- Isolated environment with Ubuntu 22.04
- Compatible libxml2 for Sony SDK
- Full USB passthrough for camera access
- Persistent logging to host filesystem

---

## Quick Start

### 1. Build the Container

```bash
cd ~/DPM-V2/sbc/remotecli-diagnostic
./build_remotecli.sh
```

Build time: ~5-10 minutes (first time)

### 2. Connect Your Camera

1. Power ON the Sony camera
2. Connect via USB cable
3. Set camera to **PC Remote** mode
4. Verify detection: `lsusb | grep -i sony`

### 3. Run the Diagnostic Tool

```bash
./run_remotecli.sh
```

The tool will:
- Initialize the Sony SDK
- Enumerate connected cameras
- Allow you to select and connect to a camera
- Provide an interactive diagnostic menu
- Log everything to `logs/remotecli_v2.log`

---

## Usage Examples

### Normal Mode (Recommended)

```bash
./run_remotecli.sh
```

Runs RemoteCli v2 with full logging enabled.

### Interactive Shell Mode

```bash
./run_remotecli.sh -i
```

Drops you into a bash shell inside the container. Useful for:
- Running RemoteCli v2 multiple times
- Inspecting the container environment
- Manual troubleshooting

**Inside the container:**
```bash
cd /app/remotecli_v2/build
./RemoteCli_v2
```

### View Diagnostic Logs

```bash
# View full log
cat logs/remotecli_v2.log

# Follow log in real-time (in another terminal)
tail -f logs/remotecli_v2.log

# View recent errors only
grep ERROR logs/remotecli_v2.log

# View SDK calls
grep SDK logs/remotecli_v2.log
```

---

## Diagnostic Menu

Once connected to a camera, RemoteCli v2 provides an interactive menu:

```
--- RemoteCli v2 Diagnostic Menu ---
  1. Get camera properties
  2. Take photo (shutter)
  3. Display connection info
  4. Test property read/write
  5. Disconnect and exit
```

**Option 1: Get Camera Properties**
- Queries all current camera properties
- Logs property codes and values
- Useful for understanding camera state

**Option 2: Take Photo**
- Executes shutter down/up sequence
- Logs timing and SDK responses
- Verifies basic camera control

**Option 3: Display Connection Info**
- Shows camera model
- Displays connection status
- Confirms remote control mode

**Option 4: Test Property Access**
- Tests reading camera properties
- Useful for diagnosing property access issues

**Option 5: Disconnect and Exit**
- Clean disconnection from camera
- Releases Sony SDK
- Saves all logs

---

## Log Format

### Example Log Entry

```
[2025-10-30 14:23:45.123] [INFO ] [SDK] Sony SDK Version: 2.0.00
[2025-10-30 14:23:45.234] [INFO ] [SDK] SDK Call: SDK::Init -> Result: 0x0 (SUCCESS)
[2025-10-30 14:23:45.567] [INFO ] [CAMERA] Camera[0]: Model=ILCE-1, ID=00000, Connection=USB
[2025-10-30 14:23:46.123] [INFO ] [CAMERA] Successfully connected to camera in 556 ms
```

### Log Components

- **Timestamp:** `[2025-10-30 14:23:45.123]` - Date and time with milliseconds
- **Level:** `[INFO]`, `[WARN]`, `[ERROR]`, `[DEBUG]`
- **Component:** `[SDK]`, `[CAMERA]`, `[MAIN]`, `[MENU]`, `[PROPERTY]`, `[CALLBACK]`
- **Message:** Human-readable description with context

### Log Levels

- **DEBUG:** Detailed diagnostic information
- **INFO:** Normal operation events
- **WARN:** Warning conditions (non-fatal)
- **ERROR:** Error conditions (may be fatal)

---

## Troubleshooting

### Problem: "No cameras detected"

**Checklist:**
1. Camera powered ON?
2. USB cable connected?
3. Camera in PC Remote mode?
4. USB detected by system? `lsusb | grep -i sony`
5. USB buffer configured? Check `/sys/module/usbcore/parameters/usbfs_memory_mb` (should be 150)

**Check logs:**
```bash
grep "Enumerat" logs/remotecli_v2.log
grep "ERROR.*camera" logs/remotecli_v2.log -i
```

### Problem: "Failed to connect to camera"

**Possible causes:**
- Camera already connected by another process
- USB communication issue
- Camera not in correct mode

**Check logs:**
```bash
grep "connect" logs/remotecli_v2.log -i
grep "ERROR" logs/remotecli_v2.log
```

**Try:**
```bash
# Kill any processes using the camera
docker stop payload-manager
pkill RemoteCli

# Restart camera
# Then try RemoteCli v2 again
./run_remotecli.sh
```

### Problem: "SDK initialization failed"

**Check:**
```bash
# Verify Sony SDK is properly mounted
docker run -it --rm remotecli-v2:latest ls -l /sdk/external/crsdk/

# Check for libCr_Core.so
docker run -it --rm remotecli-v2:latest find /sdk -name "libCr_Core.so"
```

### Problem: Container won't build

**Common issues:**
- Sony SDK not found at `~/CrSDK_v2.00.00_20250805a_Linux64ARMv8`
- Insufficient disk space
- Docker permission issues

**Solutions:**
```bash
# Verify SDK location
ls ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8

# Check disk space
df -h

# Check Docker is running
docker ps
```

---

## Comparing with Payload Manager

RemoteCli v2 is a **diagnostic tool**, not a replacement for the payload-manager service.

| Feature | RemoteCli v2 | Payload Manager |
|---------|--------------|-----------------|
| **Purpose** | Diagnostics | Production service |
| **Mode** | Interactive | Background daemon |
| **Logging** | Comprehensive | Operational |
| **Network** | None | TCP/UDP protocol |
| **Use Case** | Troubleshooting | H16 communication |

**When to use RemoteCli v2:**
- Camera connection issues
- SDK initialization problems
- Property access debugging
- Baseline camera functionality testing
- Learning Sony SDK behavior

**When to use Payload Manager:**
- Production operation
- H16 Android app integration
- Network protocol testing
- Multi-client support
- Continuous operation

---

## Files and Structure

```
sbc/remotecli-diagnostic/
├── README.md                          # This file
├── Dockerfile                         # Container definition
├── build_remotecli.sh                 # Build script
├── run_remotecli.sh                   # Run script
├── logs/                              # Log output directory
│   └── remotecli_v2.log              # Diagnostic log (created at runtime)
└── remotecli_v2/                      # Source code
    ├── CMakeLists.txt                 # Build configuration
    └── src/
        ├── DiagnosticLogger.h         # Logging utility (NEW)
        ├── RemoteCli_v2.cpp           # Enhanced main program (NEW)
        ├── CameraDevice.cpp           # Sony SDK wrapper
        ├── CameraDevice.h
        ├── ConnectionInfo.cpp
        ├── ConnectionInfo.h
        ├── CrDebugString.cpp
        ├── CrDebugString.h
        ├── MessageDefine.cpp
        ├── MessageDefine.h
        ├── PropertyValueTable.cpp
        ├── PropertyValueTable.h
        ├── Text.cpp
        ├── Text.h
        └── CRSDK/                     # Sony SDK headers
            └── CameraRemote_SDK.h
```

---

## Advanced Usage

### Running Specific Diagnostic Tests

You can modify RemoteCli_v2.cpp to add custom diagnostic tests:

1. Stop container: `docker stop remotecli-diagnostic`
2. Edit source: `nano remotecli_v2/src/RemoteCli_v2.cpp`
3. Add custom diagnostic code in the menu switch statement
4. Rebuild: `./build_remotecli.sh`
5. Run: `./run_remotecli.sh`

### Analyzing Log Files

```bash
# Count log entries by level
grep -c INFO logs/remotecli_v2.log
grep -c ERROR logs/remotecli_v2.log

# Extract all SDK calls and results
grep "SDK Call:" logs/remotecli_v2.log

# Get timing information
grep "in [0-9]* ms" logs/remotecli_v2.log

# Extract only errors with context
grep -A 2 -B 2 ERROR logs/remotecli_v2.log
```

### Using with Different Camera Models

RemoteCli v2 works with any Sony camera supported by the Remote SDK:
- Alpha series (A1, A7, A9, etc.)
- Cinema line (FX3, FX6, etc.)
- RX series
- ZV series

Simply connect the camera and select it from the enumeration list.

---

## Development Notes

### Enhancement History

**v2.0 (October 30, 2025):**
- Complete rewrite with diagnostic logging
- Timestamped log entries
- SDK call result tracking
- Connection timing measurements
- Property access logging
- Interactive diagnostic menu
- Docker containerization
- Comprehensive documentation

**v1.0 (Sony SDK original):**
- Basic camera connection
- Property access
- Minimal logging

### Future Enhancements

Potential additions:
- [ ] Automated test sequences
- [ ] Property value validation
- [ ] Connection stress testing
- [ ] USB bandwidth monitoring
- [ ] Multi-camera support testing
- [ ] JSON log export
- [ ] Web-based log viewer

---

## Related Documentation

- Sony SDK Documentation: `~/CrSDK_v2.00.00_20250805a_Linux64ARMv8/html/index.html`
- Air-Side Progress: `~/DPM-V2/sbc/docs/PROGRESS_AND_TODO.md`
- Payload Manager Logs: `~/DPM-V2/sbc/logs/payload_manager.log`
- DPM Protocol Spec: `~/DPM-V2/protocol/`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review diagnostic logs in `logs/remotecli_v2.log`
3. Compare with payload-manager behavior
4. Consult Sony SDK documentation

---

**Last Updated:** October 30, 2025
**Version:** 2.0
**Author:** DPM Development Team
