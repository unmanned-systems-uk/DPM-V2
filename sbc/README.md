# Payload Manager Service - Air Side
## DPM Raspberry Pi Service for Camera Control

**Version:** 1.0.0
**Protocol:** 1.0
**Phase:** 1 - Initial Connectivity (MVP)
**Platform:** Raspberry Pi (Linux ARM64v8)
**Language:** C++17

---

## Overview

The Payload Manager Service runs on the Raspberry Pi (Air Side) and communicates with the DPM Android app (Ground Side) over Ethernet. This service manages camera control, system monitoring, and network communication.

**Phase 1 (Current):** Network connectivity only - TCP command server, UDP status broadcasting, and heartbeat exchange. Camera interface is a stub (no Sony SDK integration yet).

**Phase 2 (Future):** Full Sony Camera SDK integration for actual camera control.

---

## Features (Phase 1)

- ✅ TCP Command Server (port 5000)
  - Handshake exchange
  - system.get_status command
  - JSON-based protocol

- ✅ UDP Status Broadcasting (port 5001)
  - 5 Hz status updates
  - System info (CPU, memory, disk, uptime)
  - Camera status (stub - not connected)

- ✅ Heartbeat Exchange (port 5002)
  - 1 Hz bidirectional heartbeat
  - Connection health monitoring
  - Timeout detection

- ✅ Logging System
  - File-based logging with rotation
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR)
  - Thread-safe operation

- ✅ System Monitoring
  - CPU usage tracking
  - Memory usage monitoring
  - Disk space monitoring
  - Uptime tracking

---

## Network Configuration

**Air Side (Raspberry Pi):**
- IP: 192.168.144.20
- TCP Port: 5000 (command server)
- UDP Port: 5001 (status broadcast - send)
- UDP Port: 5002 (heartbeat - bidirectional)

**Ground Side (Android App):**
- IP: 192.168.144.11

**Connection:** Direct Ethernet cable or network switch

---

## Dependencies

### System Packages

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    cmake \
    g++ \
    nlohmann-json3-dev \
    libudev-dev
```

### Required Versions

- CMake >= 3.16
- GCC >= 9 (C++17 support)
- nlohmann/json >= 3.0

---

## Building

### Debug Build

```bash
cd /home/dpm/DPM/sbc
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . -j4
```

### Release Build

```bash
cd /home/dpm/DPM/sbc
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j4
```

### Verify Build

```bash
./payload_manager --version
ldd ./payload_manager
```

Expected output:
```
Payload Manager v1.0.0
Protocol version: 1.0
Phase 1 - Initial Connectivity (MVP)
```

---

## Running

### Direct Execution

```bash
cd /home/dpm/DPM/sbc/build
./payload_manager
```

The service will start and display:
```
========================================
   DPM Payload Manager Service
   Air Side - Raspberry Pi
========================================
Version: 1.0.0
Protocol: 1.0
Phase: 1 (Initial Connectivity)
========================================

Service started successfully!
TCP server: port 5000
UDP status: 192.168.144.11:5001 (5 Hz)
Heartbeat: 192.168.144.11:5002 (1 Hz)

Press Ctrl+C to stop...
```

### Stop Service

Press `Ctrl+C` to gracefully stop the service.

### Logs

Log file location: `/home/dpm/DPM/sbc/logs/payload_manager.log`

View logs in real-time:
```bash
tail -f /home/dpm/DPM/sbc/logs/payload_manager.log
```

---

## Installation (Optional)

Install to system:

```bash
cd /home/dpm/DPM/sbc/build
sudo cmake --install .
```

This installs the binary to `/usr/local/bin/payload_manager`

Then run from anywhere:
```bash
payload_manager
```

---

## Testing

### Basic Network Tests

**1. Check Port Availability**
```bash
# On Raspberry Pi
sudo netstat -tulpn | grep -E '5000|5001|5002'
```

Expected output shows payload_manager listening on these ports.

**2. Test TCP Connection**
```bash
# From another machine or same machine
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729339200,"payload":{"command":"system.get_status","parameters":{}}}' | nc 192.168.144.20 5000
```

You should receive a JSON response with system status.

**3. Monitor UDP Status Broadcast**
```bash
# On ground machine at 192.168.144.11
nc -u -l 5001
```

You should see JSON status messages arriving every 200ms (5 Hz).

**4. Monitor Heartbeat**
```bash
# On ground machine at 192.168.144.11
nc -u -l 5002
```

You should see heartbeat messages arriving every 1000ms (1 Hz).

### Test Scripts

Python test scripts are available in the test strategy documentation:
- TCP command test client
- UDP status listener
- Heartbeat monitor

See `docs/Connectivity_Test_Strategy.md` for detailed testing procedures.

---

## Troubleshooting

### Service Won't Start

**Problem:** "Failed to bind to port 5000"
**Solution:** Another process is using the port. Find and stop it:
```bash
sudo netstat -tulpn | grep 5000
sudo kill <PID>
```

**Problem:** "Failed to create log file"
**Solution:** Create logs directory:
```bash
mkdir -p /home/dpm/DPM/sbc/logs
chmod 755 /home/dpm/DPM/sbc/logs
```

### No Network Communication

**Problem:** No UDP packets received on ground side
**Solution:** Check network configuration and firewall:
```bash
# Verify IP address
ip addr show eth0

# Verify connectivity
ping 192.168.144.11

# Check firewall
sudo ufw status
```

### High CPU Usage

**Problem:** CPU usage exceeds 30%
**Solution:** Check logs for errors. Reduce log level to INFO:
```cpp
// In src/main.cpp, change:
Logger::setLevel(Logger::Level::INFO);
```

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────┐
│           main.cpp                      │
│  (Entry point, initialization, signals) │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
┌───────▼─────────┐  ┌──────▼────────┐
│  Protocol Layer  │  │  Camera Layer │
│  - TCP Server    │  │  - Stub (P1)  │
│  - UDP Broadcast │  │  - SDK (P2)   │
│  - Heartbeat     │  │               │
└────────┬─────────┘  └───────────────┘
         │
┌────────▼─────────┐
│   Utils Layer    │
│  - Logger        │
│  - System Info   │
└──────────────────┘
```

### Threading Model

- **Main Thread:** Event loop, signal handling
- **TCP Accept Thread:** Listens for incoming TCP connections
- **TCP Client Threads:** One per client connection (detached)
- **UDP Broadcast Thread:** Sends status at 5 Hz
- **Heartbeat Send/Receive Thread:** Bidirectional heartbeat at 1 Hz

### Protocol

All messages use JSON format with this base structure:
```json
{
  "protocol_version": "1.0",
  "message_type": "command|response|status|heartbeat",
  "sequence_id": 12345,
  "timestamp": 1729339200,
  "payload": {
    // Message-specific content
  }
}
```

See `docs/Air_Side_Implementation_Guide.md` for complete protocol specification.

---

## Development

### Project Structure

```
/home/dpm/DPM/sbc/
├── CMakeLists.txt
├── README.md (this file)
├── .gitignore
├── docs/
│   ├── BUILD_AND_IMPLEMENTATION_PLAN.md
│   └── PROGRESS_AND_TODO.md
├── src/
│   ├── main.cpp
│   ├── config.h
│   ├── protocol/
│   │   ├── tcp_server.h/cpp
│   │   ├── udp_broadcaster.h/cpp
│   │   ├── heartbeat.h/cpp
│   │   └── messages.h
│   ├── camera/
│   │   ├── camera_interface.h
│   │   └── camera_stub.cpp
│   └── utils/
│       ├── logger.h/cpp
│       └── system_info.h/cpp
├── build/
│   └── payload_manager (binary)
└── logs/
    └── payload_manager.log
```

### Configuration

All configuration constants are in `src/config.h`:
- Network ports and IPs
- Timing intervals
- Protocol version
- Buffer sizes
- Capabilities

To modify configuration, edit `src/config.h` and rebuild.

### Adding New Commands (Future)

1. Add command handler in `tcp_server.cpp`
2. Add capability string to `config.h`
3. Update protocol documentation
4. Rebuild and test

---

## Phase 2 Roadmap

**Phase 2 will add:**
- Sony Camera SDK integration
- Camera connection and control
- Property get/set (shutter, aperture, ISO, etc.)
- Image capture commands
- Video recording control
- Content download

**Files to be added/modified:**
- `src/camera/camera_sony.cpp` - Real Sony SDK implementation
- `CMakeLists.txt` - Link Sony SDK libraries
- Additional command handlers in `tcp_server.cpp`

---

## Performance

**Targets (Phase 1):**
- CPU Usage: < 30% average
- Memory Usage: < 256 MB
- TCP Latency: < 50ms average
- Status Broadcast: 200ms ± 20ms (5 Hz)
- Heartbeat: 1000ms ± 50ms (1 Hz)

**Actual Performance:**
(To be measured during testing)

---

## Security

**Phase 1 Considerations:**
- No authentication (trusted network)
- No encryption (local Ethernet)
- IP filtering recommended (future)

**Future Enhancements:**
- TLS/SSL for TCP
- Authentication tokens
- IP whitelist
- Rate limiting

---

## License

(TBD - Define project license)

---

## Support

For issues or questions:
1. Check logs: `/home/dpm/DPM/sbc/logs/payload_manager.log`
2. Review documentation in `docs/`
3. Check test strategy: `docs/Connectivity_Test_Strategy.md`

---

**Last Updated:** October 23, 2025
**Status:** Phase 1 Implementation Complete ✅
**Next:** Testing and validation
