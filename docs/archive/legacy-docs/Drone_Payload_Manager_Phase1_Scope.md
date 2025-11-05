# Drone Payload Manager Project
## Phase 1: Sony Camera Integration - Project Scope Document

**Project Lead:** Anthony Kirk  
**Documentation Support:** Claude Sonnet  
**Development Support:** Claude Code via VS Code  
**Document Version:** 1.0  
**Date:** October 19, 2025

---

## Executive Summary

The Drone Payload Manager is a multiphase project designed to provide comprehensive remote control capabilities for UAV-mounted cameras. Phase 1 focuses on establishing core functionality with Sony camera integration, creating a foundation for future expansion to additional camera systems and advanced AI processing capabilities.

This system enables dual-mode operation: direct standalone control via Android application and Mavlink protocol integration for seamless GCS and flight controller interaction.

---

## Project Overview

### Vision
To create a robust, scalable payload management system that provides professional-grade camera control for UAV operations, with future expansion to thermal imaging, multispectral sensors, and edge AI processing.

### Phase 1 Goals
- Implement full remote control of Sony cameras via their SDK
- Establish reliable communication architecture between airborne and ground systems
- Create intuitive Android-based ground control interface
- Integrate Mavlink protocol for GCS compatibility
- Support gimbal control (Gremsy and SimpleBGC)
- Validate system architecture for future phases

---

## System Architecture

### Hardware Components

#### Airborne System (SBC)
- **Platform:** Raspberry Pi 4
- **Operating System:** Ubuntu Server (Latest LTS)
- **Connectivity:**
  - Serial connection to flight controller
  - Ethernet connection to data-link
  - USB-3/Ethernet/WiFi to Sony camera (auto-detect)
- **Future Upgrade Path:** Nvidia Jetson (for edge AI processing in later phases)

#### Ground Station
- **Data-Link:** SiYi MK32 (initial), expandable to other systems
- **User Interface:** Android Application
- **GCS Integration:** QGroundControl, Mission Planner

#### Camera System
- **Phase 1 Camera:** Sony Camera (SDK-enabled models)
- **Connection Options:** USB-3, Ethernet, or WiFi (automatic detection)
- **Gimbal Support:** 
  - Gremsy gimbal controllers
  - SimpleBGC gimbal controllers

### Software Architecture

#### Development Environment
- **IDE:** Visual Studio Code with SSH remote development
- **Primary Language:** C++
- **Code Generation:** Claude Code integration via VS Code
- **Version Control:** (To be specified)

#### Core Software Components

**Airborne Software Stack:**
- Sony Camera SDK integration layer
- Mavlink Router (message routing daemon)
- Camera control service
- Gimbal control interface
- State management system
- Communication handler

**Ground Station Software:**
- Android application
- Mavlink message generator
- Real-time telemetry display
- Configuration interface

#### Communication Protocols
- **Mavlink:** Primary protocol for GCS and flight controller integration
- **Proprietary Camera Protocol:** Sony SDK native communication
- **Serial:** Flight controller connection (Ardupilot)
- **Ethernet/WiFi:** Data-link and camera connectivity

---

## Phase 1 Functional Requirements

### 1. Dual Control Modes

#### Mode 1: Standalone Direct Control
- Direct camera control via dedicated Android application
- Independent of GCS software
- Full access to all camera features
- Gimbal parameter configuration
- Real-time status monitoring

#### Mode 2: Mavlink Integration
- Camera control through GCS (QGroundControl, Mission Planner)
- Flight controller command capability (Ardupilot)
- Standardized Mavlink camera protocol implementation
- Mission-based automated camera control
- Trigger events from flight controller

### 2. Sony Camera Control Features

#### Primary Camera Controls
The system shall provide remote control of the following camera parameters:

**Operation Mode Management:**
- Mode selection (Auto, Manual, Priority modes)
- Operation mode synchronization and confirmation

**Capture Configuration:**
- Still image capture
- Video recording start/stop
- Capture mode switching

**Exposure Control:**
- Shutter speed adjustment
- Aperture control (F-stop)
- ISO sensitivity setting
- Exposure compensation

**Focus Management:**
- Focus mode selection (Auto, Manual, Continuous)
- Manual focus adjustment (in/out)
- Focus area selection (zone/point selection if supported by camera)
- Touch focus coordinate specification

**White Balance Control:**
- White balance mode (Auto, Daylight, Cloudy, Tungsten, Fluorescent, Flash, Custom)
- Manual white balance setting (color temperature in Kelvin)
- White balance fine-tuning/shift

**Image Quality Settings:**
- Image file format selection (JPEG, RAW, JPEG+RAW)
- JPEG quality level (Fine, Standard, if applicable)
- Image size/resolution selection
- Compression settings

#### Camera Status Monitoring
The system shall continuously monitor and report:

**Power Management:**
- Battery level percentage
- Battery status (charging, critical, normal)
- Estimated remaining time

**Storage Management:**
- SD card total capacity
- SD card remaining capacity
- Available shots/recording time
- Storage health status

**Settings Confirmation:**
- Current camera settings readback
- Mode confirmation
- Parameter synchronization verification
- Error state reporting

#### Image and Video Download
The system shall support downloading content from camera to SBC:

**Download Capabilities:**
- Download captured still images to SBC storage
- Download recorded video files to SBC storage
- Selective download (specific files or all)
- Background download during operation (RemoteTransferMode)
- Download progress monitoring
- Automatic retry on failed downloads

**Storage Management on SBC:**
- Configurable storage location
- Available space monitoring
- Automatic cleanup of old files (configurable)
- File naming and organization

### 3. Gimbal Control Integration

The system shall provide configuration and control for:

**Gremsy Gimbal:**
- Parameter configuration interface
- Stabilization mode settings
- Pan, tilt, roll control
- Home position setting

**SimpleBGC Gimbal:**
- Parameter configuration interface
- PID tuning access
- Control mode settings
- Angle and rate control

**Common Gimbal Functions:**
- Position control commands
- Velocity control commands
- Lock/follow mode switching
- Calibration procedures

### 4. Communication Requirements

#### Reliability
- Automatic reconnection on connection loss
- Message queuing during temporary disconnections
- Heartbeat monitoring
- Timeout handling

#### Performance
- Maximum control latency: < 200ms
- Status update frequency: Minimum 1Hz, target 5Hz
- Video preview streaming capability (future consideration)

#### Data-Link Flexibility
- Initial support: SiYi MK32
- Abstracted interface for future data-link systems
- Automatic data-link detection and configuration

---

## Technical Specifications

### Sony Camera SDK Integration

#### SDK Requirements
- Latest Sony Camera Remote SDK version
- USB, Ethernet, and WiFi connectivity support
- Event callback implementation
- Asynchronous operation support

#### Connection Management
- Automatic camera discovery
- Connection type auto-detection (USB-3/Ethernet/WiFi)
- Multi-camera support architecture (single camera in Phase 1)
- Connection health monitoring

#### Camera Control Layer
- Command queue management
- Response parsing and validation
- Error handling and recovery
- Settings persistence

### Mavlink Protocol Implementation

#### Supported Message Sets
- **MAV_CMD_DO_DIGICAM_CONTROL:** Camera trigger commands
- **MAV_CMD_DO_SET_CAM_TRIGG_DIST:** Distance-based triggering
- **CAMERA_SETTINGS:** Camera parameter messages
- **CAMERA_INFORMATION:** Camera capability reporting
- **CAMERA_CAPTURE_STATUS:** Capture state reporting
- **STORAGE_INFORMATION:** SD card status reporting

#### Command Processing
- Mavlink command parser
- Command validation
- Response generation
- Status broadcasting

#### Routing Configuration
- Mavlink Router daemon integration
- Multiple endpoint support (GCS + Flight Controller)
- Message filtering and prioritization
- Bandwidth management

### Android Application Specifications

#### User Interface Requirements
- Intuitive camera control layout
- Real-time status display
- Connection status indicators
- Settings configuration screens
- Gimbal control interface

#### Functional Modules
- Connection management
- Camera control interface
- Gimbal configuration
- Mavlink message generation
- Telemetry display
- Settings storage

#### Performance Requirements
- Responsive UI (< 100ms touch response)
- Efficient data handling
- Background service for persistent connection
- Low battery consumption

---

## Development Approach

### Current Status
- Basic unoptimized C++ proof-of-concept code completed
- Core viability demonstrated for Sony camera implementation
- Foundation established for structured development

### Phase 1 Development Roadmap

#### Stage 1: Core Infrastructure (Weeks 1-3)
**Objectives:**
- Refactor and optimize existing POC code
- Establish robust Sony SDK integration layer
- Implement connection management framework
- Create modular software architecture

**Deliverables:**
- Optimized camera control library
- Connection handler with auto-detection
- Basic error handling framework
- Unit test framework

#### Stage 2: Mavlink Integration (Weeks 4-6)
**Objectives:**
- Implement Mavlink Router integration
- Develop Mavlink command parser
- Create camera control message handlers
- Establish bidirectional communication

**Deliverables:**
- Mavlink integration layer
- Command processing module
- Status reporting system
- Integration test suite

#### Stage 3: Android Application Development (Weeks 7-10)
**Objectives:**
- Design and implement UI/UX
- Develop camera control interface
- Create connection management
- Implement settings persistence

**Deliverables:**
- Android application (v1.0)
- User documentation
- Application test suite

#### Stage 4: Gimbal Integration (Weeks 11-12)
**Objectives:**
- Implement Gremsy gimbal interface
- Implement SimpleBGC gimbal interface
- Create unified gimbal control abstraction
- Integrate with Android application

**Deliverables:**
- Gimbal control library
- Configuration interfaces
- Updated Android app with gimbal controls

#### Stage 5: System Integration & Testing (Weeks 13-15)
**Objectives:**
- End-to-end system testing
- GCS integration validation (QGroundControl, Mission Planner)
- Flight controller integration testing
- Performance optimization

**Deliverables:**
- Integrated system
- Test reports
- Performance benchmarks
- Bug fixes and refinements

#### Stage 6: Documentation & Deployment (Weeks 16-17)
**Objectives:**
- Complete technical documentation
- Create user manuals
- Prepare deployment packages
- Conduct user training

**Deliverables:**
- Technical documentation
- User manuals
- Installation guides
- Training materials
- Release v1.0

---

## Quality Assurance

### Testing Strategy

#### Unit Testing
- Individual component testing
- Camera SDK function validation
- Mavlink message processing verification
- Error handling validation

#### Integration Testing
- SBC to camera communication
- Mavlink routing verification
- Android app to SBC communication
- Gimbal control integration
- GCS compatibility testing

#### System Testing
- End-to-end workflow testing
- Dual control mode validation
- Failover and recovery testing
- Performance under load
- Extended operation stability

#### Field Testing
- Real-world UAV integration
- Flight controller communication
- Data-link performance
- Environmental condition testing
- User acceptance testing

### Code Quality Standards
- Consistent coding style (C++ and Java/Kotlin)
- Comprehensive code comments
- Modular design principles
- Memory leak prevention
- Resource management best practices

### Documentation Requirements
- Inline code documentation
- API documentation
- System architecture diagrams
- User manuals
- Installation and configuration guides
- Troubleshooting guides

---

## Risk Management

### Technical Risks

#### Risk 1: Sony SDK Limitations
**Description:** SDK may not support all required features or have undocumented limitations  
**Mitigation:**
- Early SDK evaluation and testing
- Maintain communication with Sony developer support
- Document workarounds
- Plan alternative approaches

#### Risk 2: Latency Issues
**Description:** Control latency may exceed acceptable thresholds  
**Mitigation:**
- Implement efficient message queuing
- Optimize communication protocols
- Test with various data-link configurations
- Profile and optimize bottlenecks

#### Risk 3: Raspberry Pi 4 Performance
**Description:** Pi 4 may have insufficient processing power for all requirements  
**Mitigation:**
- Early performance benchmarking
- Code optimization focus
- Resource usage monitoring
- Have Jetson upgrade path ready

#### Risk 4: Mavlink Protocol Compatibility
**Description:** GCS or flight controller may have Mavlink implementation differences  
**Mitigation:**
- Test with multiple GCS versions
- Implement flexible message handling
- Maintain protocol compliance
- Document known compatibility issues

### Project Risks

#### Risk 5: Scope Creep
**Description:** Additional feature requests during Phase 1 development  
**Mitigation:**
- Maintain strict scope definition
- Document future phase features
- Formal change request process
- Regular stakeholder communication

#### Risk 6: Integration Complexity
**Description:** Complexity of integrating multiple systems may cause delays  
**Mitigation:**
- Phased integration approach
- Early identification of integration points
- Buffer time in schedule
- Regular integration testing

---

## Success Criteria

### Phase 1 Completion Criteria

The following criteria must be met for Phase 1 sign-off:

#### Functional Criteria
- ✓ Sony camera control via standalone Android app
- ✓ Sony camera control via Mavlink/GCS
- ✓ All primary camera controls operational
- ✓ Camera status monitoring functional
- ✓ Gimbal configuration capability (Gremsy and SimpleBGC)
- ✓ Dual control modes working simultaneously
- ✓ Automatic camera connection detection

#### Performance Criteria
- ✓ Control latency < 200ms
- ✓ Status updates at minimum 1Hz
- ✓ System uptime > 99% in 1-hour test
- ✓ Successful recovery from connection loss
- ✓ No memory leaks in 8-hour continuous operation

#### Integration Criteria
- ✓ QGroundControl compatibility verified
- ✓ Mission Planner compatibility verified
- ✓ Ardupilot flight controller integration validated
- ✓ SiYi MK32 data-link operation confirmed

#### Documentation Criteria
- ✓ Technical documentation complete
- ✓ User manual published
- ✓ Installation guide available
- ✓ API documentation generated

---

## Future Phases Overview

### Phase 2: Thermal Camera Integration (Workswell)
- Workswell thermal camera SDK integration
- Thermal-specific controls and visualization
- Temperature data overlay and analysis
- Multi-camera switching capability
- **Firmware update capability for all cameras**
- **Multiple simultaneous camera support**

### Phase 3: Multispectral Camera Integration (Micasense)
- Micasense camera range support
- Band-specific controls
- Synchronized multi-camera capture
- Agricultural analysis features
- **Picture profile and color mode management**

### Phase 4: Edge AI Processing
- Upgrade to Nvidia Jetson platform
- Real-time object detection
- Automated target tracking
- Intelligent scene analysis
- On-board data processing and filtering

### Phase 5: Enhanced Data-Link Support
- Additional data-link system integrations
- Redundant communication links
- Adaptive bitrate management
- Long-range communication optimization

---

## Appendices

### Appendix A: Sony Camera SDK Supported Models
(To be populated with specific Sony camera models compatible with the SDK)

### Appendix B: Mavlink Message Reference
(Detailed list of all Mavlink messages implemented in Phase 1)

### Appendix C: Hardware Connection Diagrams
(System wiring and connection diagrams)

### Appendix D: Software Architecture Diagrams
(Detailed software component interaction diagrams)

### Appendix E: Development Environment Setup
(Step-by-step guide for setting up the development environment)

### Appendix F: API Documentation
(Auto-generated API documentation for all public interfaces)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-19 | Anthony Kirk / Claude Sonnet | Initial comprehensive scope document for Phase 1 |

---

## Contact Information

**Project Lead:** Anthony Kirk  
**Technical Support:** Claude Code (via VS Code)  
**Documentation:** Claude Sonnet

---

**Document Classification:** Project Internal  
**Distribution:** Project Team, Stakeholders

---

*This document serves as the authoritative scope definition for Phase 1 of the Drone Payload Manager project. All development activities should align with the requirements and objectives outlined herein.*
