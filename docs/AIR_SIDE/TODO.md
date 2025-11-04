# Air-Side (Pi 5 SBC) TODO List
*Last Updated: 2025-11-04*

## 🔴 Critical Issues (Immediate)
- [ ] **Fix focus distance readback**
  - Investigate SDK GetDeviceProperty for focus distance
  - Check if property is available in current mode
  - Update UDP status broadcast with actual value
  - Field name: `focal_distance_m` or `focus_distance`

- [ ] **Fix AF Hold in Manual Focus mode**
  - Test with different camera modes
  - Check SDK documentation for MF restrictions
  - Try alternative SDK calls
  - May need camera firmware update

- [ ] **Resolve property read errors**
  - Some properties return 0x8402 (not available)
  - Check camera mode dependencies
  - Implement mode-aware property queries

## 🟡 Phase 10: Optimization (Priority: HIGH)
### Performance Improvements
- [ ] Optimize PropertyLoader caching
- [ ] Reduce JSON parsing overhead
- [ ] Implement connection pooling
- [ ] Add message batching for status

### Memory Management
- [ ] Audit memory allocations
- [ ] Fix potential memory leaks
- [ ] Optimize buffer sizes
- [ ] Implement memory pool

### Error Recovery
- [ ] Improve camera reconnection logic
- [ ] Add automatic retry for failed commands
- [ ] Implement graceful degradation
- [ ] Enhanced error logging

## 🟢 Phase 11: Extended Features (Priority: MEDIUM)
### Video Recording
- [ ] Implement video start/stop commands
- [ ] Add recording status to broadcasts
- [ ] Monitor recording time and size
- [ ] Handle storage switching

### Gimbal Integration
- [ ] Define gimbal control protocol
- [ ] Implement MAVLink for gimbal
- [ ] Add gimbal status to broadcasts
- [ ] Create gimbal calibration routine

### File Transfer
- [ ] Implement file listing command
- [ ] Add thumbnail generation
- [ ] Create file download protocol
- [ ] Implement delete/move operations

### Advanced Camera Features
- [ ] Implement burst mode capture
- [ ] Add intervalometer function
- [ ] Support RAW+JPEG modes
- [ ] Implement custom picture profiles

## 🔵 Testing & Validation (Priority: MEDIUM)
### Unit Tests
- [ ] Create test suite for PropertyLoader
- [ ] Test protocol message parsing
- [ ] Validate camera command handlers
- [ ] Test error conditions

### Integration Tests
- [ ] Multi-client stress testing
- [ ] Network failure recovery
- [ ] Camera disconnect/reconnect
- [ ] Long-duration stability

### Performance Tests
- [ ] Measure command latency
- [ ] Profile CPU/memory usage
- [ ] Network throughput testing
- [ ] Thermal throttling tests

## 💡 Future Enhancements (v2.0)
### AI/ML Features
- [ ] Object detection on edge
- [ ] Auto-framing with AI
- [ ] Scene recognition
- [ ] Intelligent exposure

### Advanced Networking
- [ ] 5G modem integration
- [ ] Cloud backup capability
- [ ] Remote firmware updates
- [ ] VPN support

### Multi-Camera Support
- [ ] Handle multiple cameras
- [ ] Synchronized capture
- [ ] Camera switching
- [ ] Picture-in-picture

### Telemetry Integration
- [ ] MAVLink full integration
- [ ] GPS metadata in images
- [ ] Flight data overlay
- [ ] Waypoint-triggered capture

## Dependencies & Blockers

### Waiting on Sony
- [ ] Focus distance property documentation
- [ ] AF Hold behavior in MF mode
- [ ] New SDK version with fixes

### Waiting on Ground-Side
- [ ] Updated command definitions
- [ ] File transfer protocol agreement
- [ ] Video streaming requirements

### Hardware Dependencies
- [ ] Gimbal hardware for testing
- [ ] 5G modem for connectivity
- [ ] Thermal testing chamber

## Bug Fixes
- [ ] Memory leak in long sessions
- [ ] Occasional TCP connection drops
- [ ] UDP packet loss at high rates
- [ ] Camera callback timing issues

## Documentation
- [ ] Create API documentation
- [ ] Document PropertyLoader system
- [ ] Add code comments
- [ ] Create deployment guide
- [ ] Document Docker setup

## Maintenance
- [ ] Update to latest Sony SDK
- [ ] Upgrade Docker base image
- [ ] Update dependencies
- [ ] Security audit
- [ ] Code refactoring

---
## Quick Capture
*For items discovered during development:*
- [ ] _________________________
- [ ] _________________________
- [ ] _________________________

---
*Progress tracking in PROGRESS.md*
*Current focus in CURRENT_STATUS.md*
*Integration points in docs/ALL_DOMAINS/INTEGRATION_POINTS.md*