# Air-Side (Pi 5 SBC) Current Status
*Last Updated: 2025-11-04 | Active Sprint: Documentation Optimization*

## 🎯 Current Focus
**Documentation migration and focus issue investigation**

### Today's Activities
1. ✅ Migrated to domain-based documentation
2. 🔄 Investigating focus distance property access
3. ⏳ Planning performance optimizations
4. ⏳ Preparing extended feature set

## System Status

### Hardware
- **Platform**: Raspberry Pi 5 (8GB RAM)
- **Camera**: Sony A1 (USB connected)
- **Storage**: 256GB NVMe SSD
- **Network**: Ethernet (1 Gbps)
- **Temperature**: ~45°C (normal)

### Software
- **OS**: Raspberry Pi OS Lite 64-bit
- **Kernel**: 6.1.0-rpi4-rpi-v8
- **Docker**: v24.0.5
- **Container**: payload-manager:latest (1.03GB)
- **SDK**: Sony Camera Remote SDK 1.12.0

### Network Services
```
TCP Server (9001):     ✅ Listening
UDP Broadcast (9002):  ✅ Active @ 5Hz
UDP Broadcast (9003):  ✅ Active @ 5Hz
UDP Heartbeat (5002):  ✅ Active @ 1Hz
SSH Server (22):       ✅ Running
```

## Camera Connection
- **Status**: ✅ Connected
- **Model**: Sony A1
- **Mode**: Manual
- **Live View**: Enabled
- **Properties**: Loading via PropertyLoader

### Current Settings
- **ISO**: 400
- **Aperture**: f/5.6
- **Shutter**: 1/250
- **Focus Mode**: MF (Manual)
- **White Balance**: Auto

## Implementation Status

### ✅ Working Features
- Camera enumeration and connection
- Photo capture
- Property get/set operations
- Live view streaming
- System status monitoring
- Multi-client UDP broadcasting
- Heartbeat protocol v1.1.0
- PropertyLoader architecture

### ⚠️ Known Issues
1. **Focus distance not readable**
   - GetDeviceProperty returns error
   - May need different SDK approach

2. **AF Hold not working in MF**
   - Command accepted but no effect
   - Possible camera limitation

3. **Some properties unavailable**
   - Error 0x8402 in certain modes
   - Mode-dependent availability

## Performance Metrics
```
CPU Usage:        18%
RAM Usage:        147MB / 8GB
Disk Usage:       12GB / 256GB
Network TX:       3.2 Mbps
Network RX:       0.8 Mbps
Uptime:           47 hours
```

## Recent Session Notes

### Session (November 4, 2025)
- Documentation restructured for efficiency
- All features documented in modular format
- Preparing for optimization phase

### Last Dev Session (October 31, 2025)
- Manual focus controls implemented
- Focus issues identified and documented
- Multi-port UDP broadcasting added
- System monitoring enhanced

## Command Implementation Status
| Command | Status | Notes |
|---------|--------|-------|
| handshake | ✅ Working | Protocol v1.0 |
| system.get_status | ✅ Working | All metrics |
| camera.capture | ✅ Working | Photos saved |
| camera.set_property | ✅ Working | Via PropertyLoader |
| camera.get_properties | ✅ Working | Enabled props only |
| camera.focus | ⚠️ Partial | Distance not readable |
| camera.auto_focus_hold | ⚠️ Issues | MF mode problem |

## Immediate Next Steps
1. Debug focus distance property access
2. Test alternative SDK methods for focus
3. Optimize PropertyLoader performance
4. Begin video recording implementation

## Quick Commands
```bash
# Connect to Pi 5
ssh dpm@10.0.1.53

# Enter Docker container
docker exec -it payload-manager bash

# View logs
tail -f /app/logs/payload_manager.log

# Test camera
/app/test_shutter

# Rebuild in container
cd /app && ./rebuild.sh

# Monitor status
watch -n 1 'docker stats payload-manager'
```

## Git Status
- **Branch**: main
- **Last Commit**: 943d13a
- **Changes**: Documentation only
- **Ready**: For optimization phase

## Docker Container
- **Image**: payload-manager:latest
- **Status**: Running
- **Uptime**: 47 hours
- **Restart**: unless-stopped
- **Mounts**: /dev/bus/usb (camera)

---
*Full progress in PROGRESS.md | Pending tasks in TODO.md*