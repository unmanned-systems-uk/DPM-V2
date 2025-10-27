# WiFi Testing Implementation Guide for DPM Air-Side Service

**Document:** WiFi Testing Setup - Ethernet Workaround  
**Date:** October 24, 2025  
**Target Platform:** Raspberry Pi 4 (Air-Side Service)  
**Purpose:** Enable DPM testing via WiFi while awaiting ethernet cable for SkyDroid R16 connection

---

## Executive Summary

While awaiting the ethernet cable to connect the Raspberry Pi to the SkyDroid R16 Air Unit, we can test the complete DPM protocol stack using WiFi connectivity. Both the Raspberry Pi and H16 Ground Station are connected to the same local WiFi network (10.0.1.x subnet), enabling full end-to-end testing of all protocol features.

**Key Benefits:**
- ✅ Test 95% of functionality without hardware dependencies
- ✅ Faster development iteration (no physical cable connections)
- ✅ Realistic wireless latency similar to H16-R16 link
- ✅ Easy transition to production ethernet (configuration change only)

---

## Current Network Topology

### Development/Testing Configuration (WiFi)
```
┌─────────────────────────────────────────────────────┐
│         Local WiFi Network (10.0.1.x/24)            │
│                                                     │
│  ┌──────────────────┐       ┌──────────────────┐  │
│  │  Raspberry Pi 4  │       │  H16 Ground Stn  │  │
│  │                  │       │  (Android)       │  │
│  │  10.0.1.20       │◄─────►│  10.0.1.x        │  │
│  │                  │ WiFi  │                  │  │
│  │  DPM Service     │       │  Test App        │  │
│  │  (Docker)        │       │                  │  │
│  └──────────────────┘       └──────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Production Configuration (Ethernet - Future)
```
┌──────── AIR SIDE ────────┐        ┌───── GROUND SIDE ─────┐
│                          │        │                        │
│  ┌──────────────────┐   │        │   ┌──────────────────┐ │
│  │  Raspberry Pi 4  │   │        │   │  H16 Ground Stn  │ │
│  │                  │   │        │   │  (Android)       │ │
│  │ 192.168.144.20   │   │  H16   │   │ 192.168.144.11   │ │
│  │                  │◄──┼──R16───┼──►│                  │ │
│  │  DPM Service     │   │ Link   │   │  Production App  │ │
│  │  (Docker)        │   │        │   │                  │ │
│  └────────┬─────────┘   │        │   └──────────────────┘ │
│           │ Ethernet    │        │                        │
│      ┌────▼────┐        │        └────────────────────────┘
│      │ R16 Air │        │
│      │  Unit   │        │
│      └─────────┘        │
└──────────────────────────┘
```

---

## Implementation Tasks

### Task 1: Make Ground Station IP Configurable

**Location:** `/home/dpm/DPM-V2/sbc/include/config.h`

**Current Implementation:**
```cpp
// Network configuration
constexpr const char* GROUND_STATION_IP = "192.168.144.11";
constexpr int TCP_PORT = 5000;
constexpr int UDP_STATUS_PORT = 5001;
constexpr int UDP_HEARTBEAT_PORT = 5002;
```

**Required Changes:**

1. **Add environment variable support** (preferred method)
2. **Add command-line argument support** (alternative)
3. **Keep default for production**

#### Option A: Environment Variable (Recommended)

**File:** `sbc/include/config.h`

```cpp
#include <cstdlib>
#include <string>

namespace Config {
    // Network configuration - supports override via environment variable
    inline std::string getGroundStationIP() {
        const char* env_ip = std::getenv("DPM_GROUND_IP");
        if (env_ip != nullptr && env_ip[0] != '\0') {
            return std::string(env_ip);
        }
        return "192.168.144.11";  // Production default
    }
    
    // Port configuration (unchanged)
    constexpr int TCP_PORT = 5000;
    constexpr int UDP_STATUS_PORT = 5001;
    constexpr int UDP_HEARTBEAT_PORT = 5002;
    constexpr int LISTEN_PORT = TCP_PORT;
    
    // Timing configuration (unchanged)
    constexpr int STATUS_BROADCAST_INTERVAL_MS = 200;  // 5 Hz
    constexpr int HEARTBEAT_INTERVAL_MS = 1000;        // 1 Hz
    constexpr int HEARTBEAT_TIMEOUT_MS = 10000;        // 10 seconds
}
```

**File:** `sbc/src/protocol/udp_broadcaster.cpp` (update constructor)

```cpp
#include "config.h"

UdpBroadcaster::UdpBroadcaster(CameraInterface* camera, SystemInfo* sysinfo)
    : camera_(camera), sysinfo_(sysinfo), sequence_id_(0), running_(false) {
    
    // Get ground station IP (supports environment override)
    std::string ground_ip = Config::getGroundStationIP();
    
    // Create UDP socket
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd_ < 0) {
        throw std::runtime_error("Failed to create UDP socket");
    }
    
    // Configure broadcast address
    memset(&broadcast_addr_, 0, sizeof(broadcast_addr_));
    broadcast_addr_.sin_family = AF_INET;
    broadcast_addr_.sin_port = htons(Config::UDP_STATUS_PORT);
    
    if (inet_pton(AF_INET, ground_ip.c_str(), &broadcast_addr_.sin_addr) <= 0) {
        close(sockfd_);
        throw std::runtime_error("Invalid ground station IP address: " + ground_ip);
    }
    
    Logger::getInstance().log(Logger::INFO, 
        "UDP Broadcaster configured for ground station: " + ground_ip + 
        ":" + std::to_string(Config::UDP_STATUS_PORT));
}
```

**File:** `sbc/src/protocol/heartbeat.cpp` (update constructor)

```cpp
#include "config.h"

Heartbeat::Heartbeat()
    : sequence_id_(0), running_(false), last_received_(0) {
    
    // Get ground station IP (supports environment override)
    std::string ground_ip = Config::getGroundStationIP();
    
    // Create UDP socket
    sockfd_ = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd_ < 0) {
        throw std::runtime_error("Failed to create heartbeat socket");
    }
    
    // Configure ground station address
    memset(&ground_addr_, 0, sizeof(ground_addr_));
    ground_addr_.sin_family = AF_INET;
    ground_addr_.sin_port = htons(Config::UDP_HEARTBEAT_PORT);
    
    if (inet_pton(AF_INET, ground_ip.c_str(), &ground_addr_.sin_addr) <= 0) {
        close(sockfd_);
        throw std::runtime_error("Invalid ground station IP address: " + ground_ip);
    }
    
    // Configure listen address (bind to all interfaces)
    memset(&listen_addr_, 0, sizeof(listen_addr_));
    listen_addr_.sin_family = AF_INET;
    listen_addr_.sin_addr.s_addr = INADDR_ANY;
    listen_addr_.sin_port = htons(Config::UDP_HEARTBEAT_PORT);
    
    if (bind(sockfd_, (struct sockaddr*)&listen_addr_, sizeof(listen_addr_)) < 0) {
        close(sockfd_);
        throw std::runtime_error("Failed to bind heartbeat socket");
    }
    
    Logger::getInstance().log(Logger::INFO, 
        "Heartbeat configured for ground station: " + ground_ip + 
        ":" + std::to_string(Config::UDP_HEARTBEAT_PORT));
}
```

#### Option B: Command-Line Argument (Alternative)

**File:** `sbc/src/main.cpp`

```cpp
#include <cstring>

int main(int argc, char* argv[]) {
    // Parse command-line arguments
    std::string ground_ip = "192.168.144.11";  // Default
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--ground-ip") == 0 && i + 1 < argc) {
            ground_ip = argv[i + 1];
            i++;
        } else if (strcmp(argv[i], "--help") == 0) {
            std::cout << "Usage: " << argv[0] << " [options]\n"
                      << "Options:\n"
                      << "  --ground-ip <IP>  Set ground station IP address\n"
                      << "                    (default: 192.168.144.11)\n"
                      << "  --help            Show this help message\n";
            return 0;
        }
    }
    
    // Set environment variable for other components to use
    setenv("DPM_GROUND_IP", ground_ip.c_str(), 1);
    
    Logger::getInstance().log(Logger::INFO, 
        "Starting Payload Manager with ground station: " + ground_ip);
    
    // ... rest of main() ...
}
```

---

### Task 2: Update Docker Run Configuration

**Location:** `/home/dpm/DPM-V2/sbc/run_container.sh`

**Current Script:** (assumedly runs container with default settings)

**Required Changes:**

1. **Add environment variable passing**
2. **Add run mode selection** (testing vs production)
3. **Maintain backward compatibility**

**Updated Script:**

```bash
#!/bin/bash
# run_container.sh - Run DPM payload manager container
# Updated: October 24, 2025 - Added WiFi testing support

set -e

CONTAINER_NAME="payload-manager"
IMAGE_NAME="payload-manager:latest"

# Default configuration
GROUND_IP="192.168.144.11"  # Production default
RUN_MODE="production"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --test-wifi)
            RUN_MODE="testing"
            shift
            ;;
        --ground-ip)
            GROUND_IP="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --test-wifi           Enable WiFi testing mode"
            echo "  --ground-ip <IP>      Set ground station IP address"
            echo "                        (default: 192.168.144.11 for production)"
            echo "  --help                Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Production mode"
            echo "  $0 --test-wifi --ground-ip 10.0.1.50  # WiFi testing mode"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Stop existing container if running
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping existing container..."
    docker stop ${CONTAINER_NAME} >/dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} >/dev/null 2>&1 || true
fi

# Display configuration
echo "=========================================="
echo "DPM Payload Manager - Container Startup"
echo "=========================================="
echo "Mode:              ${RUN_MODE}"
echo "Ground Station IP: ${GROUND_IP}"
echo "Image:             ${IMAGE_NAME}"
echo "Container:         ${CONTAINER_NAME}"
echo "=========================================="

# Run container with appropriate configuration
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart always \
    --network host \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -e DPM_GROUND_IP=${GROUND_IP} \
    -e DPM_RUN_MODE=${RUN_MODE} \
    ${IMAGE_NAME}

# Wait for container to start
sleep 2

# Check container status
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo ""
    echo "✅ Container started successfully!"
    echo ""
    echo "To view logs:"
    echo "  docker logs -f ${CONTAINER_NAME}"
    echo ""
    echo "To access shell:"
    echo "  docker exec -it ${CONTAINER_NAME} /bin/bash"
    echo ""
    if [ "$RUN_MODE" == "testing" ]; then
        echo "⚠️  WiFi TESTING MODE ENABLED"
        echo "   Ground station must be at: ${GROUND_IP}"
        echo "   Listening on all interfaces: 0.0.0.0:5000/5001/5002"
        echo ""
    fi
else
    echo ""
    echo "❌ Container failed to start!"
    echo ""
    echo "Check logs with:"
    echo "  docker logs ${CONTAINER_NAME}"
    exit 1
fi
```

---

### Task 3: Discover H16 WiFi IP Address

**Manual Method:**

1. **On H16 Ground Station:**
   - Go to Settings → Network & Internet → WiFi
   - Tap on connected network name
   - Note the IP address (likely 10.0.1.x)

2. **From Raspberry Pi:**
   ```bash
   # Scan local network for H16
   nmap -sn 10.0.1.0/24
   
   # Or use arp-scan (if installed)
   sudo arp-scan --localnet
   
   # Look for device with Android/SkyDroid identifier
   ```

**Automated Discovery Script:**

Create `/home/dpm/DPM-V2/sbc/scripts/find_h16.sh`:

```bash
#!/bin/bash
# find_h16.sh - Discover H16 Ground Station on local network

echo "Scanning local network for H16 Ground Station..."
echo ""

# Get local subnet
LOCAL_IP=$(ip -4 addr show dev wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
SUBNET=$(echo $LOCAL_IP | cut -d. -f1-3)

echo "Local IP: $LOCAL_IP"
echo "Scanning subnet: $SUBNET.0/24"
echo ""

# Scan for devices with port 5555 open (ADB default)
echo "Checking for ADB-enabled Android devices..."
nmap -p 5555 --open $SUBNET.0/24 | grep -B 4 "5555/tcp open"

echo ""
echo "Checking for devices with port 22 open (SSH)..."
nmap -p 22 --open $SUBNET.0/24 | grep -B 4 "22/tcp open"

echo ""
echo "To connect with ADB:"
echo "  adb connect <IP>:5555"
```

---

### Task 4: Create WiFi Testing Documentation

**Location:** `/home/dpm/DPM-V2/sbc/docs/WIFI_TESTING.md`

```markdown
# WiFi Testing Guide - DPM Air-Side Service

**Purpose:** Test DPM protocol stack using WiFi connectivity while awaiting ethernet cable for SkyDroid R16 connection.

---

## Prerequisites

1. ✅ Raspberry Pi 4 connected to local WiFi (10.0.1.x network)
2. ✅ H16 Ground Station connected to same WiFi network
3. ✅ Docker container built and ready (`payload-manager:latest`)
4. ✅ H16 IP address discovered (see below)

---

## Quick Start

### Step 1: Discover H16 IP Address

**Option A: On H16 Device**
1. Open Settings → Network & Internet → WiFi
2. Tap connected network name
3. Note IP address (e.g., 10.0.1.50)

**Option B: From Raspberry Pi**
```bash
# Scan local network
cd /home/dpm/DPM/sbc/scripts
./find_h16.sh
```

### Step 2: Start DPM in WiFi Testing Mode

```bash
cd /home/dpm/DPM/sbc
./run_container.sh --test-wifi --ground-ip 10.0.1.50
```

Replace `10.0.1.50` with your H16's actual IP address.

### Step 3: Verify Service Started

```bash
# Check container logs
docker logs -f payload-manager

# You should see:
# [INFO] UDP Broadcaster configured for ground station: 10.0.1.50:5001
# [INFO] Heartbeat configured for ground station: 10.0.1.50:5002
# [INFO] TCP server listening on port 5000
```

### Step 4: Test from Development Machine

**Install test tools on development PC:**
```bash
# Install netcat and jq (JSON parser)
sudo apt install netcat jq

# Or on macOS
brew install netcat jq
```

**Test TCP Connection:**
```bash
# From development PC on same WiFi network
echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729800000,"payload":{"command":"handshake","parameters":{}}}' | nc 10.0.1.20 5000 | jq .
```

Expected response:
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1,
  "timestamp": 1729800123,
  "payload": {
    "result": "success",
    "message": "Handshake successful"
  }
}
```

**Test UDP Status Broadcasts:**
```bash
# Listen for status broadcasts
nc -u -l 5001

# You should see JSON status messages at ~5 Hz (every 200ms)
```

**Test Heartbeat:**
```bash
# Send heartbeat to Pi
while true; do
    echo '{"protocol_version":"1.0","message_type":"heartbeat","sequence_id":1,"timestamp":'$(date +%s)'}' | nc -u 10.0.1.20 5002
    sleep 1
done
```

---

## Testing Checklist

### Network Connectivity
- [ ] Raspberry Pi has IP address on WiFi (check with `ip addr`)
- [ ] H16 has IP address on same subnet
- [ ] Can ping H16 from Pi: `ping 10.0.1.50`
- [ ] Can ping Pi from H16: `ping 10.0.1.20`

### Service Operation
- [ ] Docker container starts successfully
- [ ] Logs show correct ground station IP
- [ ] No errors in startup sequence
- [ ] TCP server listening on port 5000
- [ ] UDP status broadcasts starting

### Protocol Testing
- [ ] TCP handshake command succeeds
- [ ] TCP system.get_status command returns data
- [ ] UDP status broadcasts received at ~5 Hz
- [ ] UDP heartbeat exchange works bidirectionally
- [ ] Connection timeout detection works (stop heartbeat)

### Android App Testing (when ready)
- [ ] App connects to Pi TCP server
- [ ] App receives UDP status broadcasts
- [ ] App can send commands successfully
- [ ] App displays camera status (stub data)
- [ ] Connection loss detected properly

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs payload-manager
```

**Common issues:**
- Port already in use (stop other services)
- USB permissions (shouldn't affect WiFi testing)
- Invalid ground IP address

### Can't Connect from H16

**Check firewall on Pi:**
```bash
# Check if firewall is blocking
sudo ufw status

# If enabled, allow DPM ports
sudo ufw allow 5000/tcp
sudo ufw allow 5001/udp
sudo ufw allow 5002/udp
```

**Verify service is listening:**
```bash
# Check if ports are open
sudo netstat -tulpn | grep payload_manager
```

### No UDP Broadcasts Received

**Check network connectivity:**
```bash
# From Pi, send test UDP packet to H16
echo "test" | nc -u 10.0.1.50 5001
```

**Verify ground IP is correct:**
```bash
# Check container environment
docker exec payload-manager env | grep DPM_GROUND_IP
```

---

## Switching to Production (Ethernet)

When ethernet cable arrives:

1. **Connect Pi to R16 Air Unit ethernet port**

2. **Configure static IP:**
   ```bash
   # Edit netplan configuration
   sudo nano /etc/netplan/50-cloud-init.yaml
   
   # Add:
   ethernets:
     eth0:
       addresses:
         - 192.168.144.20/24
   ```

3. **Restart service in production mode:**
   ```bash
   cd /home/dpm/DPM-V2/sbc
   ./run_container.sh
   # (No --test-wifi flag = production mode)
   ```

4. **Verify connection to H16 over wireless link:**
   ```bash
   ping 192.168.144.11
   ```

No code changes required - just configuration!

---

## Performance Notes

**WiFi vs Ethernet Comparison:**

| Metric | WiFi (Testing) | Ethernet (Production) |
|--------|----------------|------------------------|
| Latency | 5-20ms | 1-5ms |
| Bandwidth | 20-50 Mbps | 100 Mbps |
| Reliability | Good | Excellent |
| Range | Limited by WiFi | Limited by R16 link |

WiFi testing provides realistic wireless latency and validates all protocol logic. Only the final physical layer differs from production.

---

**Last Updated:** October 24, 2025
```

---

### Task 5: Update Build Documentation

**Location:** `/home/dpm/DPM-V2/sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md`

**Add Section:**

```markdown
## WiFi Testing Configuration (October 2025 Update)

While awaiting ethernet cable for R16 connection, DPM can be tested using WiFi connectivity.

**Setup:**
1. Ensure Pi and H16 are on same WiFi network (10.0.1.x)
2. Discover H16 IP address (see WIFI_TESTING.md)
3. Run container in testing mode:
   ```bash
   ./run_container.sh --test-wifi --ground-ip <H16_IP>
   ```

**See:** `docs/WIFI_TESTING.md` for complete guide.

**Transition:** When ethernet available, run without flags for production mode.
```

---

## Testing Workflow

### Phase 1: Basic Connectivity (Day 1)

1. **Setup:**
   ```bash
   cd /home/dpm/DPM-V2/sbc
   
   # Discover H16 IP
   ./scripts/find_h16.sh
   
   # Start service
   ./run_container.sh --test-wifi --ground-ip 10.0.1.XX
   ```

2. **Verify startup:**
   ```bash
   docker logs -f payload-manager
   # Look for: "configured for ground station: 10.0.1.XX"
   ```

3. **Test from PC:**
   ```bash
   # TCP handshake
   echo '{"protocol_version":"1.0","message_type":"command","sequence_id":1,"timestamp":1729800000,"payload":{"command":"handshake","parameters":{}}}' | nc 10.0.1.20 5000
   
   # Should return success response
   ```

4. **Test UDP status:**
   ```bash
   # Listen for broadcasts
   nc -u -l 5001
   # Should see JSON messages every 200ms
   ```

### Phase 2: Android App Testing (Day 2-3)

1. **Install test app on H16**
2. **Configure app to connect to 10.0.1.20:5000**
3. **Test full protocol stack**
4. **Verify UI displays status correctly**

### Phase 3: Performance & Stability (Day 4-5)

1. **Measure latency** (should be < 50ms over WiFi)
2. **Verify broadcast frequency** (5 Hz ± 10%)
3. **Test heartbeat timeout** (disconnect detection)
4. **Run 1-hour stability test**
5. **Monitor CPU/memory usage**

---

## Key Differences: WiFi vs Ethernet

| Aspect | WiFi Testing | Ethernet Production |
|--------|--------------|---------------------|
| **IP Address** | 10.0.1.20 (Pi) / 10.0.1.x (H16) | 192.168.144.20 (Pi) / 192.168.144.11 (H16) |
| **Physical Layer** | WiFi (802.11) | Ethernet (Layer 2) |
| **Wireless Link** | Local WiFi router | H16-R16 proprietary link |
| **Configuration** | `--test-wifi --ground-ip X.X.X.X` | Default (no flags) |
| **Range** | WiFi coverage area | Up to 10km (R16 spec) |
| **Latency** | 5-20ms | 1-5ms + wireless link |
| **What's Tested** | ✅ All protocol logic<br>✅ All app features<br>✅ Error handling<br>✅ Performance | Same + physical reliability |
| **What's NOT Tested** | ❌ R16 wireless link<br>❌ Ethernet hardware<br>❌ Final IP config | Everything |

**Critical Point:** WiFi testing validates 95% of functionality. Only the physical transport layer differs from production.

---

## File Modification Summary

| File | Modification | Purpose |
|------|--------------|---------|
| `sbc/include/config.h` | Add `getGroundStationIP()` function | Support environment variable override |
| `sbc/src/protocol/udp_broadcaster.cpp` | Use `Config::getGroundStationIP()` | Dynamic ground IP configuration |
| `sbc/src/protocol/heartbeat.cpp` | Use `Config::getGroundStationIP()` | Dynamic ground IP configuration |
| `sbc/run_container.sh` | Add `--test-wifi` and `--ground-ip` flags | Easy mode switching |
| `sbc/scripts/find_h16.sh` | New file | Network discovery tool |
| `sbc/docs/WIFI_TESTING.md` | New file | Complete testing guide |
| `sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md` | Add WiFi testing section | Update documentation |

---

## Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Implementation** | 2 hours | Code changes + testing |
| **WiFi Testing** | 1-2 days | Protocol validation |
| **Android Development** | 3-5 days | App development + integration |
| **Ethernet Transition** | 30 minutes | Configuration change only |

**Total Time Saved:** ~2 weeks (parallel development while awaiting hardware)

---

## Success Criteria

### Implementation Complete When:
- ✅ `run_container.sh --test-wifi --ground-ip X.X.X.X` works
- ✅ Logs show correct ground IP address
- ✅ Service starts without errors
- ✅ TCP/UDP ports listening correctly

### WiFi Testing Complete When:
- ✅ TCP handshake succeeds from H16
- ✅ UDP status broadcasts received at 5 Hz
- ✅ Heartbeat exchange works bidirectionally
- ✅ Connection timeout detection works
- ✅ Android app can connect and control (when ready)
- ✅ 1-hour stability test passes

### Ready for Production When:
- ✅ All WiFi tests pass
- ✅ Ethernet cable available
- ✅ Static IP configured (192.168.144.20)
- ✅ Service runs in production mode (no flags)
- ✅ Can ping 192.168.144.11 over R16 link

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| WiFi network changes | Low | Medium | Document IP discovery process |
| H16 WiFi incompatibility | Very Low | High | Tested on same Android version |
| Performance differences WiFi vs Ethernet | Low | Low | WiFi latency similar to wireless link |
| Code changes break production | Very Low | High | Environment variable = zero risk |
| Cannot transition to ethernet | Very Low | Critical | Configuration only, no code changes |

---

## Next Actions for Claude Code

### Immediate (Next 2 Hours):

1. **Implement configuration changes:**
   - [ ] Modify `sbc/include/config.h` (add `getGroundStationIP()`)
   - [ ] Update `sbc/src/protocol/udp_broadcaster.cpp`
   - [ ] Update `sbc/src/protocol/heartbeat.cpp`

2. **Update run script:**
   - [ ] Enhance `sbc/run_container.sh` with WiFi testing support

3. **Create documentation:**
   - [ ] Create `sbc/docs/WIFI_TESTING.md`
   - [ ] Create `sbc/scripts/find_h16.sh`
   - [ ] Update `sbc/docs/BUILD_AND_IMPLEMENTATION_PLAN.md`

4. **Test implementation:**
   - [ ] Rebuild Docker container
   - [ ] Start in WiFi mode
   - [ ] Verify logs show correct IP

### Follow-Up (Next 1-2 Days):

5. **Network discovery:**
   - [ ] Run H16 discovery script
   - [ ] Verify connectivity from Pi to H16
   - [ ] Test basic TCP/UDP communication

6. **Protocol validation:**
   - [ ] Test handshake command
   - [ ] Test system.get_status command
   - [ ] Monitor UDP broadcasts
   - [ ] Test heartbeat exchange

7. **Android integration:**
   - [ ] Connect test app to Pi via WiFi
   - [ ] Verify full protocol stack
   - [ ] Run stability tests

---

## Questions & Support

**Common Questions:**

**Q: Will this affect production deployment?**  
A: No. Changes use environment variables with production defaults. Running without `--test-wifi` flag gives identical behavior to current implementation.

**Q: What if H16 IP changes?**  
A: Just restart container with new IP: `./run_container.sh --test-wifi --ground-ip <NEW_IP>`

**Q: Can we test without H16?**  
A: Yes! Use development PC to send test commands to Pi at 10.0.1.20:5000

**Q: How do we switch to ethernet?**  
A: Connect cable, configure static IP, run `./run_container.sh` (no flags). Done!

**Q: What about the camera testing we're doing?**  
A: Camera testing (USB connection, Sony SDK) is independent of network configuration. Both can proceed in parallel.

---

**Document Status:** ✅ Ready for Implementation  
**Priority:** High (unblocks testing while awaiting hardware)  
**Complexity:** Low (configuration changes only)  
**Risk:** Very Low (backward compatible)  
**Estimated Completion:** 2-3 hours

---

## Conclusion

WiFi testing enables immediate validation of the DPM protocol stack without waiting for ethernet hardware. The implementation is low-risk (environment variables with production defaults), requires minimal code changes, and provides 95% functional coverage. Transition to production ethernet requires only configuration changes with zero code modifications.

**Recommendation:** Proceed with WiFi testing implementation immediately to accelerate development timeline.