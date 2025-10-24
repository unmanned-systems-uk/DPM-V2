# WiFi Testing Guide

This guide explains how to test the DPM payload manager using WiFi connectivity instead of the SkyDroid R16 ethernet connection.

## Overview

WiFi testing allows you to test the network protocol stack (UDP broadcasts, heartbeats, TCP commands) while the ethernet cable is unavailable. This approach:

- **Tests 95% of functionality** without hardware dependencies
- **Low-risk** - uses environment variables, backward compatible
- **Fast iteration** - no physical cable connections needed
- **Realistic testing** - WiFi latency similar to H16-R16 air link

## Network Setup

### Expected Network Configuration

- **WiFi Network**: 10.0.1.x subnet
- **Raspberry Pi**: 10.0.1.20 (or DHCP assigned)
- **H16 Ground Station**: 10.0.1.100 (default, or auto-discovered)

### Prerequisites

1. Raspberry Pi connected to WiFi network (10.0.1.x)
2. H16 ground station powered on and connected to same WiFi
3. Docker container built and ready to run

## Usage

### Quick Start

**Automatic Discovery (Recommended)**

The easiest way to start WiFi testing is to use the `--test-wifi` flag, which will automatically attempt to discover the H16 on the network:

```bash
cd /home/dpm/DPM-V2/sbc
./run_container.sh --test-wifi
```

This will:
1. Scan the 10.0.1.x network for the H16
2. Attempt to connect to TCP port 5000
3. Use the discovered IP or default to 10.0.1.100

**Manual IP Specification**

If you know the H16's IP address, you can specify it directly:

```bash
./run_container.sh --ground-ip 10.0.1.100
```

### Development Mode

WiFi testing works with both production and development modes:

```bash
# Development mode with WiFi testing
./run_container.sh dev --test-wifi

# Development mode with specific IP
./run_container.sh dev --ground-ip 10.0.1.100
```

## Environment Variable

The WiFi testing feature uses the `DPM_GROUND_IP` environment variable. This is automatically set by `run_container.sh`, but you can also set it manually:

```bash
# Inside the container
DPM_GROUND_IP=10.0.1.100 ./payload_manager

# Or export it
export DPM_GROUND_IP=10.0.1.100
./payload_manager
```

If `DPM_GROUND_IP` is not set, the default ethernet IP (192.168.144.11) is used.

## Network Discovery

### Automatic H16 Discovery

The `scripts/find_h16.sh` script scans the 10.0.1.x network for the H16 ground station:

```bash
cd /home/dpm/DPM-V2/sbc
./scripts/find_h16.sh
```

Output:
- If found: Prints the IP address (e.g., "10.0.1.100")
- If not found: Exits with error code 1

### Manual H16 Discovery

You can also manually check for the H16:

```bash
# Ping test
ping -c 3 10.0.1.100

# TCP port check (requires netcat)
nc -zv 10.0.1.100 5000

# Full network scan (requires nmap)
nmap -p 5000 10.0.1.0/24
```

## Testing Checklist

### Phase 1: Basic Connectivity

- [ ] Raspberry Pi connected to WiFi (10.0.1.x)
- [ ] H16 ground station on same network
- [ ] Can ping H16 from Pi
- [ ] Container starts with `--test-wifi` flag
- [ ] Logs show correct ground station IP

### Phase 2: Protocol Testing

- [ ] UDP status broadcasts sent to H16
- [ ] UDP heartbeats sent to H16
- [ ] TCP command server listening on Pi
- [ ] H16 can connect to TCP server
- [ ] Commands execute correctly

### Phase 3: Camera Integration

- [ ] Camera status included in UDP broadcasts
- [ ] Camera commands work via TCP
- [ ] Camera shutter triggers correctly
- [ ] No USB communication issues

## Monitoring

### View Container Logs

```bash
docker logs -f payload-manager
```

Look for:
```
Creating UDP broadcaster (target: 10.0.1.100:5001)...
Creating heartbeat handler (port 5002)...
UDP Status Broadcast: 10.0.1.100:5001 (5 Hz)
Heartbeat: 10.0.1.100:5002 (1 Hz)
```

### Network Traffic Analysis

Monitor UDP traffic on the Pi:

```bash
# Install tcpdump if not available
sudo apt-get install tcpdump

# Monitor UDP broadcasts
sudo tcpdump -i wlan0 udp port 5001 or udp port 5002
```

Expected output:
```
10.0.1.20.12345 > 10.0.1.100.5001: UDP, length 256  (status broadcast)
10.0.1.20.54321 > 10.0.1.100.5002: UDP, length 128  (heartbeat)
```

## Troubleshooting

### Issue: H16 Not Discovered

**Symptoms:** `find_h16.sh` exits with error

**Solutions:**
1. Verify H16 is powered on and connected to WiFi
2. Check H16 IP address in its network settings
3. Manually specify IP with `--ground-ip`
4. Check firewall rules on H16

### Issue: Container Starts But No Network Traffic

**Symptoms:** Logs show correct IP, but no UDP packets received by H16

**Solutions:**
1. Check WiFi connectivity: `ping 10.0.1.100`
2. Verify UDP ports not blocked by firewall
3. Check H16 is listening on ports 5001 and 5002
4. Monitor with `tcpdump` to verify packets are sent

### Issue: Wrong IP Used

**Symptoms:** Container uses 192.168.144.11 instead of WiFi IP

**Solutions:**
1. Ensure `--test-wifi` or `--ground-ip` flag is used
2. Check container environment: `docker exec payload-manager env | grep DPM_GROUND_IP`
3. Restart container with correct flags

### Issue: Camera Not Working

**Symptoms:** Camera works standalone but fails in WiFi testing mode

**Solutions:**
1. WiFi testing doesn't affect camera - this is a separate issue
2. Check USB connection: `docker exec payload-manager lsusb | grep Sony`
3. Check USB buffer: `cat /sys/module/usbcore/parameters/usbfs_memory_mb`
4. Review camera logs in `/app/logs/payload_manager.log`

## Comparison: WiFi vs Ethernet

| Feature | Ethernet (R16) | WiFi Testing |
|---------|---------------|--------------|
| Ground IP | 192.168.144.11 | 10.0.1.100 |
| Latency | 1-2ms | 5-20ms |
| Bandwidth | 100 Mbps | 50-150 Mbps |
| Reliability | Very High | High |
| Setup Complexity | Requires cable | No cable needed |
| Use Case | Production | Testing |

## Reverting to Ethernet

When the ethernet cable arrives, simply run the container without WiFi flags:

```bash
./run_container.sh
```

Or for development:

```bash
./run_container.sh dev
```

The default ethernet IP (192.168.144.11) will be used automatically.

## Implementation Details

### Files Modified

1. **sbc/src/config.h**
   - Added `getGroundStationIP()` function
   - Reads `DPM_GROUND_IP` environment variable
   - Falls back to default ethernet IP

2. **sbc/src/main.cpp**
   - Uses `config::getGroundStationIP()` instead of hardcoded IP
   - Passes dynamic IP to UDP broadcaster and heartbeat

3. **sbc/run_container.sh**
   - Added `--test-wifi` and `--ground-ip` flags
   - Automatic H16 discovery
   - Sets `DPM_GROUND_IP` environment variable in container

4. **sbc/scripts/find_h16.sh** (NEW)
   - Network scanner for H16 discovery
   - Checks TCP port 5000 on 10.0.1.x subnet

### Backward Compatibility

The implementation is fully backward compatible:

- No environment variable = uses default ethernet IP
- Existing containers continue to work unchanged
- No changes to protocol or message format
- WiFi testing is opt-in via flags

## Next Steps

After successful WiFi testing:

1. **Verify all protocol messages** - Check UDP and TCP communication
2. **Test camera integration** - Ensure camera commands work
3. **Document any issues** - Update PROGRESS_AND_TODO.md
4. **Prepare for ethernet** - WiFi testing validates the code is ready

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review container logs: `docker logs payload-manager`
3. Check network connectivity: `ping`, `tcpdump`, `nc`
4. Verify configuration: Environment variables, IP addresses

## References

- [CC_READ_THIS_FIRST.md](CC_READ_THIS_FIRST.md) - Main development workflow
- [PROGRESS_AND_TODO.md](PROGRESS_AND_TODO.md) - Project status
- [Wifi testing-workaround.md](Wifi%20testing-workaround.md) - Original WiFi testing plan
