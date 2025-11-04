# Ground-Side (Android H16) TODO List
*Last Updated: 2025-11-04*

## 🔴 Critical Issues (Immediate)
- [ ] **Fix focus distance readback**
  - Check UDP status format from Air-Side
  - Verify field name: `focal_distance_m`
  - Update FocusDistanceOverlay display

- [ ] **Fix auto-focus assist in MF mode**
  - Test AF Hold with different camera modes
  - Check Sony SDK documentation
  - Coordinate with Air-Side team

- [ ] **Add build timestamp to System Status UI**
  - Display: "Version 1.0.0 (Built: 2025-11-04 12:34:56 UTC)"
  - Use BuildConfig.BUILD_TIMESTAMP

## 🟡 Short Term (This Week)
### Testing Structure
- [ ] Define comprehensive testing framework
  - [ ] Unit tests for ViewModels
  - [ ] Integration tests for NetworkClient
  - [ ] End-to-end tests with mock server
  - [ ] UI tests with Espresso

### Phase 1 Completion
- [ ] Recalculate MVP completion percentage
- [ ] Account for all discovered features
- [ ] Update project metrics

### Hardware Testing
- [ ] Test on real H16 device
- [ ] Verify all implemented commands
- [ ] Profile performance
- [ ] Test WiFi stability

## 🟢 Phase 3: Remaining Commands
### Camera Commands
- [ ] `camera.start_recording` - Video recording
- [ ] `camera.stop_recording` - Stop video
- [ ] `camera.set_mode` - Photo/Video/etc
- [ ] `camera.format_storage` - Format SD card
- [ ] `camera.get_storage_info` - Storage status

### Gimbal Commands
- [ ] `gimbal.set_angle` - Control gimbal position
- [ ] `gimbal.set_mode` - Configure gimbal behavior
- [ ] `gimbal.center` - Return to home position
- [ ] `gimbal.calibrate` - Calibration routine

### System Commands
- [ ] `system.reboot` - Restart Air-Side
- [ ] `system.update_firmware` - OTA updates
- [ ] `system.get_logs` - Retrieve logs

## 🔵 Phase 4: Advanced Features
### Downloads Screen
- [ ] Design content management UI
- [ ] Implement file listing from Air-Side
- [ ] Add download functionality
- [ ] Create local file browser
- [ ] Add delete/move operations

### Gimbal Control Interface
- [ ] Create gimbal control pad
- [ ] Add angle indicators
- [ ] Implement smooth control
- [ ] Add preset positions

### Video Recording Controls
- [ ] Recording start/stop button
- [ ] Recording time indicator
- [ ] Storage space monitor
- [ ] Quality settings

### Image Preview/Playback
- [ ] Thumbnail gallery view
- [ ] Full-screen image viewer
- [ ] Swipe navigation
- [ ] Metadata display

## 💡 Future Enhancements (v2.0)
- [ ] Mission planning interface
- [ ] Waypoint management
- [ ] Automated capture sequences
- [ ] Multi-drone support
- [ ] Cloud backup integration
- [ ] Advanced telemetry display
- [ ] Custom control layouts
- [ ] Gesture controls
- [ ] Voice commands
- [ ] AR overlay for video feed

## Dependencies & Blockers

### Waiting on Air-Side
- [ ] Focus distance broadcast format
- [ ] AF Hold behavior in MF mode
- [ ] Additional protocol commands
- [ ] File transfer protocol

### Waiting on Hardware
- [ ] H16 device availability
- [ ] Network configuration
- [ ] Performance requirements

## Bug Fixes
- [ ] Video stream reconnection issues
- [ ] Settings not updating immediately
- [ ] Event log scroll performance
- [ ] Dark theme inconsistencies

## Documentation
- [ ] Update ANDROID_ARCHITECTURE.md
- [ ] Create user guide
- [ ] Document PropertyLoader system
- [ ] Add inline code comments
- [ ] Create API documentation

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