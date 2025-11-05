# Phase 1 Quick Reference Summary

**Project:** Drone Payload Manager  
**Phase:** 1 - Sony Camera Integration  
**Date:** October 19, 2025

---

## 📦 What's IN Phase 1

### Camera Control
- ✅ Exposure control (Shutter, Aperture, ISO)
- ✅ Focus control (Mode, Manual in/out, **Area selection**)
- ✅ **White balance** (Presets, Manual temperature, Fine-tune)
- ✅ **File format** (JPEG, RAW, JPEG+RAW, Quality settings)
- ✅ Capture modes (Still, Video, Burst)
- ✅ Camera status monitoring
- ✅ **Content download** (Images & videos to SBC)
- ✅ **Storage management** (Auto-cleanup, space monitoring)

### Connectivity
- ✅ USB-3 connection
- ✅ Ethernet connection (wired)
- ✅ WiFi connection
- ✅ Auto-detection of connection type

### Gimbal Integration
- ✅ Gremsy support (all models via gSDK)
- ✅ SimpleBGC support (all models via Serial API)
- ✅ Pan/tilt/roll control
- ✅ Mode control (follow, lock, home)
- ✅ Parameter configuration
- ❌ Calibration procedures (not needed)

### Control Interfaces
- ✅ Standalone Android app
- ✅ Mavlink integration (QGC, Mission Planner)
- ✅ Flight controller control (Ardupilot)
- ✅ Dual simultaneous operation

### Video
- ✅ HDMI via SiYi MK32 (primary, low latency)
- ✅ SDK Live View (secondary, GCS preview)

---

## 🔄 What's DEFERRED

- ❌ Picture profiles / Color modes → **Phase 3**
- ❌ Firmware updates → **Phase 2**
- ❌ Multiple cameras → **Phase 2**
- ❌ Gimbal calibration → **Future**

---

## 🛠️ Key Technical Details

### Platform
- **SBC:** Raspberry Pi 4 (4GB+ recommended)
- **OS:** Ubuntu Server 22.04 LTS ARM64
- **SDK:** Sony CrSDK v2.00.00 Linux64ARMv8
- **IDE:** VS Code with Remote-SSH

### Connectivity
```
Camera ← USB/Ethernet/WiFi → Raspberry Pi 4
                                    ↓
                              Serial → Flight Controller
                                    ↓
                              Ethernet → SiYi MK32 → Ground Station
                                    ↓
                              Serial → Gimbal
```

### Storage Structure
```
/home/ubuntu/payload_data/
├── images/          # Downloaded still images
├── videos/          # Downloaded video files
└── metadata/        # Download logs
```

### Gimbal APIs
- **Gremsy:** https://github.com/Gremsy/gSDK
- **SimpleBGC:** https://github.com/basecamelectronics/sbgc32-serial-api

---

## 📅 Timeline: 17 Weeks

| Weeks | Focus | Key Deliverables |
|-------|-------|------------------|
| 1-3 | Core Infrastructure | SDK integration, property system, **download** |
| 4-6 | Mavlink Integration | Message handlers, command parsing, routing |
| 7-10 | Android App | UI, controls, **WB/format/focus area**, download UI |
| 11-12 | Gimbal Integration | Gremsy & SimpleBGC support |
| 13-15 | Integration & Testing | Full system, HIL testing, optimization |
| 16-17 | Documentation & Deployment | Manuals, deployment, handover |

---

## ✅ Success Criteria

### Must Pass:
- [ ] Camera control from Android app ✓
- [ ] Camera control from GCS ✓
- [ ] All camera controls working (incl. WB, format, focus area) ✓
- [ ] Download images/videos to SBC ✓
- [ ] Storage management operational ✓
- [ ] Both gimbals supported ✓
- [ ] Control latency < 200ms ✓
- [ ] 8-hour stability test passed ✓
- [ ] QGC and Mission Planner compatibility ✓

---

## 📊 Key Metrics

### Performance Targets:
- **Control latency:** < 200ms
- **Status updates:** ≥ 1Hz
- **Download speed:** > 2MB/s
- **System uptime:** > 99% (1-hour test)
- **No memory leaks:** 8-hour continuous operation

### Storage:
- **Min free space:** 10GB
- **Retention period:** 7 days (configurable)
- **Auto-cleanup:** Enabled by default

---

## 🔗 Important Resources

- **Sony SDK License:** http://www.sony.net/CameraRemoteSDK/
- **Gremsy gSDK:** https://github.com/Gremsy/gSDK
- **SimpleBGC API:** https://github.com/basecamelectronics/sbgc32-serial-api
- **Mavlink Protocol:** https://mavlink.io/
- **Ardupilot:** https://ardupilot.org/

---

## 📋 Development Checklist

### Environment Setup
- [ ] Raspberry Pi 4 configured with Ubuntu Server
- [ ] Sony SDK downloaded and extracted
- [ ] VS Code Remote-SSH configured
- [ ] USB permissions configured (udev rules)
- [ ] Serial ports configured for gimbal/FC
- [ ] Mavlink router installed and configured

### Hardware Needed
- [ ] Raspberry Pi 4 (4GB or 8GB)
- [ ] Sony camera (SDK v2.00.00 compatible)
- [ ] USB cable (camera-specific)
- [ ] Gimbal (Gremsy or SimpleBGC)
- [ ] Flight controller (Ardupilot)
- [ ] SiYi MK32 data-link (or ethernet for lab)
- [ ] Android device for app testing

### Software Dependencies
- [ ] build-essential, cmake, git
- [ ] libusb-1.0-0-dev
- [ ] libssh2-1-dev
- [ ] libssl-dev
- [ ] mavlink-router
- [ ] Sony CrSDK v2.00.00

---

## 🎯 Priority Order

1. **Week 1-3:** Core camera control (highest priority)
2. **Week 4-6:** Mavlink integration
3. **Week 7-10:** Android app development
4. **Week 11-12:** Gimbal integration
5. **Week 13-15:** Testing and optimization
6. **Week 16-17:** Documentation

---

## 🚨 Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Storage fills up | High | Auto-cleanup, monitoring, alerts |
| Download interruption | Medium | Resume capability, retry, verification |
| Control latency during download | Medium | Bandwidth allocation, QoS, throttling |
| SDK compatibility issues | High | Early testing, SDK version verification |
| Gimbal protocol differences | Low | Unified abstraction, both SDKs documented |

---

## 📞 Next Actions

1. **Review & Approve** this scope
2. **Acquire Hardware** (Pi 4, Camera, Gimbal)
3. **Setup Development Environment**
4. **Download SDKs** (Sony, Gremsy, SimpleBGC)
5. **Begin Week 1** implementation
6. **Schedule Weekly Reviews**

---

**Status:** ✅ Ready for Development  
**Last Updated:** October 19, 2025
