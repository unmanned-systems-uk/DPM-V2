# Phase 1 Requirements Update - October 19, 2025

## Document Purpose
This document captures the refined requirements for Phase 1 based on project discussion and clarifications.

---

## Updated Phase 1 Scope - Confirmed Requirements

### Camera Control Features - PHASE 1

#### ✅ INCLUDED in Phase 1:
1. **Basic Camera Controls**
   - Mode of operation (M, A, S, P, Auto)
   - Capture mode (Still, Video, Burst)
   - Shutter speed
   - Aperture (F-stop)
   - ISO sensitivity
   
2. **Focus Management**
   - Focus mode (Auto, Manual, Continuous)
   - Manual focus adjustment (in/out)
   - **Focus area selection** (zone/point selection)
   - Touch focus coordinate specification
   
3. **White Balance Control** ✨ NEW
   - White balance mode (Auto, Daylight, Cloudy, Tungsten, Fluorescent, Flash, Custom)
   - Manual white balance (color temperature in Kelvin)
   - White balance fine-tuning/shift
   
4. **Image Quality Settings** ✨ NEW
   - **Image file format selection (JPEG, RAW, JPEG+RAW)**
   - JPEG quality level (Fine, Standard)
   - Image size/resolution selection
   - Compression settings

5. **Camera Status Monitoring**
   - Battery status and level
   - SD card capacity and remaining space
   - Settings confirmation
   - Recording status

6. **Content Management** ✨ NEW
   - **Download still images from camera to SBC**
   - **Download video files from camera to SBC**
   - Selective download (specific files or all)
   - Background download during operation (RemoteTransferMode)
   - Download progress monitoring
   - Storage management on SBC

#### ❌ DEFERRED to Later Phases:
1. **Picture Profile / Color Mode Management** → Phase 3
2. **Firmware Update Capability** → Phase 2
3. **Multiple Camera Support** → Phase 2
4. **Advanced Color Grading** → Phase 3

---

## Gimbal Integration - PHASE 1

### Confirmed Approach:

**SDK/API References:**
- **Gremsy gSDK:** https://github.com/Gremsy/gSDK
- **SimpleBGC Serial API:** https://github.com/basecamelectronics/sbgc32-serial-api

**Key Points:**
- All Gremsy gimbal models work with the same gSDK protocol
- All SimpleBGC gimbal models work with the same Serial API protocol
- No model-specific code required
- Unified abstraction layer will support both manufacturers transparently

**Phase 1 Gimbal Features:**
✅ Pan, tilt, roll control (angle and rate)
✅ Control mode switching (follow, lock, home)
✅ Parameter configuration
✅ Status monitoring
❌ Gimbal calibration procedures (deferred - not required for Phase 1)

**Implementation:**
```cpp
// Unified gimbal interface supporting both types
class IGimbalController {
public:
    // Basic control
    virtual void SetAngle(float pitch, float yaw, float roll) = 0;
    virtual void SetRate(float pitch_rate, float yaw_rate) = 0;
    virtual void SetMode(GimbalMode mode) = 0;
    virtual void SetHome() = 0;
    
    // Configuration
    virtual void SetFollowSpeed(float speed) = 0;
    virtual void SetControlGain(float gain) = 0;
    
    // Status
    virtual GimbalStatus GetStatus() = 0;
    virtual void GetAttitude(float& pitch, float& yaw, float& roll) = 0;
};

// Concrete implementations
class GremsyController : public IGimbalController {
    // Uses gSDK from https://github.com/Gremsy/gSDK
};

class SimpleBGCController : public IGimbalController {
    // Uses Serial API from https://github.com/basecamelectronics/sbgc32-serial-api
};
```

---

## Video Streaming Strategy - CONFIRMED

### Hybrid Approach:

**1. Primary Video Feed (Real-time Operations)**
- **Method:** Camera HDMI output → SiYi MK32 HDMI input
- **Latency:** <50ms (hardware dependent)
- **Quality:** Full HD, minimal compression
- **Use Case:** Pilot/operator real-time video feed
- **Advantage:** Lowest latency, independent of control link

**2. Secondary Preview (GCS Monitoring)**
- **Method:** Sony SDK Live View callback
- **Latency:** ~100-300ms
- **Quality:** Compressed JPEG frames, adjustable
- **Use Case:** Ground station monitoring, configuration preview
- **Advantage:** Integrated with camera control, programmatic access

**Benefits of Hybrid Approach:**
- Best real-time performance for flight operations
- Remote monitoring capability for GCS
- Redundancy
- Flexibility for different operational scenarios
- Future-proof for AI processing (can access frames programmatically)

---

## Content Download Implementation

### Sony SDK RemoteTransferMode

The Sony Camera Remote SDK v2.00.00 supports **RemoteTransferMode**, which allows:
- Simultaneous camera control and content transfer
- Download images/videos while maintaining camera operation
- Content deletion from camera

### Implementation Details:

```cpp
// Mode transition
camera.SetConnectionMode(ConnectionMode::RemoteTransferMode);

// List available content on camera
std::vector<ContentHandle> contents = camera.GetContentsList();

// Download specific content
for (auto& content : contents) {
    ContentInfo info = camera.GetContentInfo(content);
    
    if (info.type == ContentType::StillImage) {
        // Download image
        camera.DownloadContent(content, 
            "/home/ubuntu/payload_data/images/", 
            [](int progress) {
                // Progress callback
                std::cout << "Download: " << progress << "%" << std::endl;
            }
        );
    }
    else if (info.type == ContentType::Movie) {
        // Download video
        camera.DownloadContent(content, 
            "/home/ubuntu/payload_data/videos/",
            [](int progress) {
                std::cout << "Download: " << progress << "%" << std::endl;
            }
        );
    }
}

// Optional: Delete content after download
camera.DeleteContent(content);
```

### Storage Management on SBC:

**Storage Structure:**
```
/home/ubuntu/payload_data/
├── images/
│   ├── DSC00001.JPG
│   ├── DSC00001.ARW (RAW)
│   └── ...
├── videos/
│   ├── C0001.MP4
│   └── ...
└── metadata/
    └── download_log.json
```

**Storage Management Features:**
- Configurable storage location
- Available space monitoring (min 10GB free space alert)
- Automatic cleanup of old files (configurable retention period)
- File naming preservation from camera
- Metadata logging (download time, file size, camera settings)

---

## White Balance Control

### Sony SDK White Balance Properties:

```cpp
// White Balance Mode
Property: CrDeviceProperty_WhiteBalance
Values:
- CrWhiteBalance_Auto
- CrWhiteBalance_Daylight
- CrWhiteBalance_Shadow
- CrWhiteBalance_Cloudy
- CrWhiteBalance_Tungsten
- CrWhiteBalance_Fluorescent_WarmWhite
- CrWhiteBalance_Fluorescent_CoolWhite
- CrWhiteBalance_Fluorescent_DayWhite
- CrWhiteBalance_Fluorescent_Daylight
- CrWhiteBalance_Flash
- CrWhiteBalance_ColorTemp (manual temperature)
- CrWhiteBalance_Custom_1
- CrWhiteBalance_Custom_2
- CrWhiteBalance_Custom_3

// Manual Color Temperature
Property: CrDeviceProperty_ColorTemperature
Values: 2500K - 9900K (in 100K increments typically)
Example: 5600 (for 5600K)

// White Balance Shift (fine-tuning)
Property: CrDeviceProperty_WhiteBalanceShift
Format: Green-Magenta shift, Amber-Blue shift
Range: Typically -9 to +9 for each axis
```

### User Interface Considerations:
- Quick presets (Auto, Daylight, Cloudy, Tungsten, etc.)
- Manual temperature slider (2500K-9900K)
- Fine-tune adjustment (G-M, A-B shift)
- Current setting display with visual indicator

---

## Focus Area Selection

### Sony SDK Focus Area Control:

```cpp
// Focus Area Selection Mode
Property: CrDeviceProperty_FocusArea
Values:
- CrFocusArea_Wide
- CrFocusArea_Zone
- CrFocusArea_CenterFix
- CrFocusArea_Flexible_Spot_S
- CrFocusArea_Flexible_Spot_M
- CrFocusArea_Flexible_Spot_L
- CrFocusArea_Expand_Flexible_Spot
- CrFocusArea_Tracking_Wide
- CrFocusArea_Tracking_Zone
- CrFocusArea_Tracking_Center
- CrFocusArea_Tracking_Spot_S
- CrFocusArea_Tracking_Spot_M
- CrFocusArea_Tracking_Spot_L

// Focus Area Position (for spot modes)
Property: CrDeviceProperty_FocusAreaPosition
Format: X, Y coordinates on sensor
Range: Camera-dependent (typically normalized 0.0-1.0 or pixel coordinates)

// Touch Focus
Command: CrCommandId_TouchAF
Parameters: X, Y coordinates where user touched
```

### Implementation Strategy:
1. Query camera for supported focus area modes
2. For spot/zone modes, provide coordinate selection interface
3. For touch focus, map UI touch coordinates to camera sensor coordinates
4. Provide visual feedback of selected focus area

---

## Image File Format Control

### Sony SDK Image Format Properties:

```cpp
// Still Image Format
Property: CrDeviceProperty_StillImageStoreFormat
Values:
- CrStillImageStoreFormat_RAW
- CrStillImageStoreFormat_JPEG
- CrStillImageStoreFormat_RAW_Plus_JPEG
- CrStillImageStoreFormat_HEIF (on supported cameras)

// JPEG Quality
Property: CrDeviceProperty_JPEG_Quality
Values:
- CrJPEG_Quality_Extra_Fine
- CrJPEG_Quality_Fine
- CrJPEG_Quality_Standard

// Image Size
Property: CrDeviceProperty_ImageSize
Values (camera-dependent):
- Large (Full resolution)
- Medium
- Small

// RAW Format (if camera supports multiple)
Property: CrDeviceProperty_RAWFileType
Values:
- CrRAWFileType_Uncompressed
- CrRAWFileType_Compressed
- CrRAWFileType_Lossless_Compressed
```

### User Interface:
- Format selector: JPEG / RAW / JPEG+RAW
- Quality selector (when JPEG selected): Extra Fine / Fine / Standard
- Size selector: Large / Medium / Small
- Visual file size estimate display

---

## Updated Development Timeline

### Adjusted Week-by-Week Plan:

**Weeks 1-3: Core Infrastructure**
- Week 1: Environment setup, SDK integration, basic USB connection
- Week 2: Property management, callback system, connection state machine
- Week 3: Command queue, error handling, **download functionality**

**Weeks 4-6: Mavlink Integration**
- Week 4: Message definitions, parser, camera information/settings messages
- Week 5: Camera control commands, storage information, capture status
- Week 6: Mavlink router integration, end-to-end command testing

**Weeks 7-10: Android Application**
- Week 7: UI framework, connection screen, main control layout
- Week 8: Camera control interface (exposure, focus, **white balance, file format**)
- Week 9: **Focus area selection UI**, status display, download management
- Week 10: Settings screen, testing, refinement

**Weeks 11-12: Gimbal Integration**
- Week 11: Unified gimbal interface, **Gremsy gSDK integration**
- Week 12: **SimpleBGC Serial API integration**, testing both types

**Weeks 13-15: System Integration & Testing**
- Week 13: Full system integration, all components working together
- Week 14: Hardware-in-loop testing, **content download testing**, performance optimization
- Week 15: Extended stability testing, bug fixes, edge case handling

**Weeks 16-17: Documentation & Deployment**
- Week 16: Technical documentation, user manuals, API docs
- Week 17: Deployment procedures, training materials, **storage management setup**, handover

---

## Updated Success Criteria for Phase 1

### Functional Criteria:
- ✓ Sony camera control via standalone Android app
- ✓ Sony camera control via Mavlink/GCS
- ✓ All primary camera controls operational (including **white balance, file format**)
- ✓ **Focus area selection functional**
- ✓ Camera status monitoring functional
- ✓ **Image/video download from camera to SBC operational**
- ✓ **Content management on SBC working (storage, cleanup)**
- ✓ Gimbal configuration capability (Gremsy **and** SimpleBGC)
- ✓ Dual control modes working simultaneously
- ✓ Automatic camera connection detection (USB/Ethernet/WiFi)

### Performance Criteria:
- ✓ Control latency < 200ms
- ✓ Status updates at minimum 1Hz
- ✓ System uptime > 99% in 1-hour test
- ✓ Successful recovery from connection loss
- ✓ No memory leaks in 8-hour continuous operation
- ✓ **Content download speed >2MB/s**
- ✓ **Storage management operates without user intervention**

### Integration Criteria:
- ✓ QGroundControl compatibility verified
- ✓ Mission Planner compatibility verified
- ✓ Ardupilot flight controller integration validated
- ✓ SiYi MK32 data-link operation confirmed
- ✓ **Both Gremsy and SimpleBGC gimbal operation confirmed**

### Documentation Criteria:
- ✓ Technical documentation complete
- ✓ User manual published
- ✓ Installation guide available
- ✓ API documentation generated
- ✓ **Content download user guide included**
- ✓ **Storage management documentation**

---

## Additional Technical Notes

### Content Download Bandwidth Considerations:

**Estimated File Sizes:**
- JPEG (Fine, Full Res): 10-25 MB per image
- RAW: 40-80 MB per image
- JPEG+RAW: 50-105 MB per capture
- 4K Video: 100-600 MB per minute (codec dependent)

**Download Time Estimates (over data-link):**
Assuming 5 Mbps available bandwidth for downloads:
- Single JPEG: 16-40 seconds
- Single RAW: 64-128 seconds
- 1 minute of 4K video: 2.5-15 minutes

**Strategy:**
- Prioritize still image downloads
- Schedule video downloads during idle/stationary periods
- Implement background transfer queue
- Allow user to configure auto-download policies

### Storage Management Policies:

**Default Configuration:**
```json
{
  "storage_root": "/home/ubuntu/payload_data",
  "min_free_space_gb": 10,
  "auto_cleanup_enabled": true,
  "retention_days": 7,
  "auto_download": {
    "images": true,
    "videos": false,
    "delete_after_download": false
  }
}
```

**Cleanup Strategy:**
- Monitor free space every 5 minutes
- When free space < threshold, delete oldest files first
- Respect retention period
- Log all deletions
- Never delete files currently being accessed

---

## Risk Updates

### New Risks Identified:

**Risk: Storage Capacity Management**
- **Description:** SD card on SBC may fill up with downloaded content
- **Mitigation:** 
  - Implement robust storage monitoring
  - Automatic cleanup with configurable policies
  - Alerts when storage critical
  - User-configurable retention periods

**Risk: Download Interruption**
- **Description:** Data-link interruption during large video download
- **Mitigation:**
  - Implement resume capability for interrupted downloads
  - Verify file integrity after download
  - Automatic retry mechanism
  - Download queue persistence across restarts

**Risk: Concurrent Download and Control**
- **Description:** Large downloads may impact control responsiveness
- **Mitigation:**
  - Use RemoteTransferMode for concurrent operations
  - Prioritize control commands over downloads
  - Bandwidth allocation and QoS
  - Throttle download speed if control latency increases

---

## Dependencies and Prerequisites

### External Resources:
1. **Sony Camera Remote SDK v2.00.00**
   - License agreement acceptance required
   - SDK download from Sony developer site
   
2. **Gremsy gSDK**
   - Repository: https://github.com/Gremsy/gSDK
   - License: Check repository for license terms
   
3. **SimpleBGC Serial API**
   - Repository: https://github.com/basecamelectronics/sbgc32-serial-api
   - License: Check repository for license terms
   
4. **Compatible Sony Camera**
   - Must support SDK v2.00.00
   - Verify model in compatibility list
   - Firmware must be up to date

### Development Prerequisites:
- Raspberry Pi 4 (4GB+ RAM)
- Ubuntu Server 22.04 LTS ARM64
- Sony camera with USB cable (USB-A to camera-specific)
- Either Gremsy or SimpleBGC gimbal for testing
- SiYi MK32 data-link (or ethernet switch for lab testing)
- Android development device (phone or tablet)
- Development machine with VS Code

---

## Questions for Clarification (Future Discussion)

1. **Storage Preferences:**
   - Should downloaded content also be forwarded to ground station?
   - Max storage allocation for payload data on SBC?
   
2. **Network Usage:**
   - Priority for live view vs. content download bandwidth?
   - Should downloads pause during critical flight phases?

3. **Content Management:**
   - Should system automatically delete content from camera after successful download?
   - Synchronization strategy with ground station storage?

4. **Android App:**
   - Minimum Android version target? (Recommend Android 8.0+)
   - Tablet-optimized or phone-optimized UI?
   - Offline operation support (when no data-link)?

---

## Summary

This update refines Phase 1 scope with:

✅ **Added Features:**
- White balance control
- Focus area selection and touch focus
- Image file format selection (JPEG/RAW/JPEG+RAW)
- Content download from camera to SBC
- Storage management on SBC

✅ **Confirmed Approach:**
- Hybrid video streaming (HDMI + SDK live view)
- Unified gimbal abstraction supporting both Gremsy and SimpleBGC
- Using official SDKs from GitHub (gSDK and SimpleBGC Serial API)

❌ **Deferred to Later Phases:**
- Picture profiles / color modes → Phase 3
- Firmware update capability → Phase 2
- Multiple camera support → Phase 2
- Gimbal calibration procedures → Future phase

**Next Steps:**
1. Review and approve this updated scope
2. Set up development environment
3. Begin Week 1 implementation
4. Schedule weekly progress reviews

---

**Document Version:** 1.0  
**Date:** October 19, 2025  
**Status:** Ready for Approval
