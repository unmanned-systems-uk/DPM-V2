# Drone Payload Manager - Phase 1 Technical Addendum
## Sony Camera Remote SDK Implementation Details

**Document Version:** 1.1  
**Date:** October 19, 2025  
**SDK Version:** CrSDK v2.00.00 (Linux64 ARMv8)

---

## Executive Summary

This technical addendum provides specific implementation details for Phase 1 of the Drone Payload Manager project, focusing on Sony Camera Remote SDK integration on the Raspberry Pi 4 / Ubuntu Server platform. This document supplements the main Phase 1 Project Scope Document with platform-specific technical requirements and implementation guidance.

---

## Sony Camera Remote SDK Overview

### SDK Version and Platform
- **SDK Version:** CrSDK_v2.00.00_20250805a_Linux64ARMv8
- **Target Platform:** Linux (Ubuntu Server LTS on Raspberry Pi 4)
- **SDK Package:** Linux 64-bit ARMv8 (ARM architecture support confirmed)
- **License:** Sony Camera Remote SDK License Agreement

### SDK Capabilities Relevant to Phase 1

#### Core Functions Available
1. **Camera Discovery and Connection**
   - USB-3 connectivity
   - Ethernet connectivity (wired and wireless)
   - WiFi connectivity
   - Automatic connection type detection
   - SSH authentication support for ethernet connections

2. **Remote Control Mode**
   - Full camera parameter control
   - Live view streaming
   - Still image capture
   - Video recording control
   - Settings management

3. **Remote Transfer Mode** (New in v2.00.00)
   - Content transfer during remote operation
   - Content deletion capability
   - Simultaneous control and transfer operations

4. **Additional Capabilities**
   - OSD (On-Screen Display) image capture
   - Firmware update at remote
   - PTZ camera support (added in v2.00.00)
   - Property monitoring via callbacks

---

## Platform-Specific Implementation Requirements

### Hardware Requirements - Raspberry Pi 4

#### Minimum Specifications
- **Model:** Raspberry Pi 4 Model B
- **RAM:** 4GB minimum (8GB recommended for future AI expansion)
- **Storage:** 32GB microSD minimum (64GB recommended)
- **USB:** USB 3.0 ports for camera connectivity
- **Network:** Gigabit Ethernet port
- **Additional:** USB-C power supply (official recommended)

#### Connectivity Options for Sony Camera
1. **USB-3 Connection**
   - Direct USB connection to Pi 4 USB 3.0 port
   - Highest reliability for control
   - No additional network configuration required
   - Recommended for initial development

2. **Ethernet Connection**
   - Camera connected to Pi 4 via ethernet
   - Requires camera ethernet adapter/support
   - SSH authentication support available in SDK
   - Suitable for certain Sony camera models

3. **WiFi Connection**
   - Camera WiFi to Pi 4 WiFi
   - Additional latency considerations
   - Suitable for specific deployment scenarios

### Operating System Configuration

#### Base System
- **OS:** Ubuntu Server 22.04 LTS (or latest LTS at deployment)
- **Architecture:** ARM64 (aarch64)
- **Kernel:** Linux kernel 5.15 or later
- **Init System:** systemd

#### Required System Packages
```bash
# USB support
libusb-1.0-0
libusb-1.0-0-dev

# SSH support (for ethernet cameras)
libssh2-1
libssh2-1-dev

# SSL/TLS support
libssl3
libssl-dev

# Build tools
build-essential
cmake (3.16 or later)
gcc/g++ (C++14 support minimum)

# Networking
net-tools
iproute2
```

#### Camera Permissions and udev Rules
Create udev rules for Sony camera USB access without root:
```
# /etc/udev/rules.d/99-sony-camera.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"
```

---

## Sony SDK Integration Architecture

### SDK Components

#### Core Libraries (Linux .so files)
1. **libCr_Core.so**
   - Main SDK library
   - Core camera control functions
   - Property management
   - Connection handling

2. **libCr_PTP_IP.so**
   - PTP/IP protocol implementation
   - Ethernet camera connectivity
   - Network camera discovery

3. **libCr_PTP_USB.so**
   - PTP/USB protocol implementation
   - USB camera connectivity
   - USB device enumeration

4. **libusb-1.0.so**
   - USB communication library
   - Open source (LGPL license - comply with license terms)

5. **libssh2.so**
   - SSH2 protocol library
   - Used for authenticated ethernet connections
   - Required for SSH-enabled cameras

6. **libmonitor_protocol.so**
   - Monitoring protocol support
   - OSD image capture
   - Advanced monitoring features

7. **libmonitor_protocol_pf.so**
   - Platform-specific monitoring protocol
   - Platform-dependent implementations

#### SDK Headers (CRSDK folder)
- CameraRemote_SDK.h (Main SDK header)
- CrCommandData.h (Command structures)
- CrDefines.h (Constants and definitions)
- CrDeviceProperty.h (Property definitions)
- CrError.h (Error codes)
- CrImageDataBlock.h (Image data structures)
- CrTypes.h (Type definitions)
- ICrCameraObjectInfo.h (Camera object interface)
- IDeviceCallback.h (Callback interface)

### Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ground Station (Android)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         User Interface & Control Application          │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │ Mavlink / Custom Protocol         │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          │ Ethernet (SiYi MK32 Data-Link)
                          │
┌─────────────────────────┼───────────────────────────────────┐
│  Raspberry Pi 4 (Airborne SBC) - Ubuntu Server             │
│  ┌──────────────────────▼────────────────────────────────┐ │
│  │    Payload Manager Application (C++)                   │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  Mavlink Integration Layer                        │ │ │
│  │  │  - Mavlink Router Interface                       │ │ │
│  │  │  - Command Parser                                 │ │ │
│  │  │  - Status Publisher                               │ │ │
│  │  └──────────────────┬───────────────────────────────┘ │ │
│  │  ┌──────────────────▼───────────────────────────────┐ │ │
│  │  │  Camera Control Service                           │ │ │
│  │  │  - Sony SDK Wrapper                               │ │ │
│  │  │  - Property Manager                               │ │ │
│  │  │  - Command Queue                                  │ │ │
│  │  │  - State Machine                                  │ │ │
│  │  └──────────────────┬───────────────────────────────┘ │ │
│  │  ┌──────────────────▼───────────────────────────────┐ │ │
│  │  │  Sony SDK Integration Layer                       │ │ │
│  │  │  - IDeviceCallback Implementation                 │ │ │
│  │  │  - Connection Manager                             │ │ │
│  │  │  - Property Monitor                               │ │ │
│  │  └──────────────────┬───────────────────────────────┘ │ │
│  └────────────────────┬┴───────────────────────────────┘ │
│                       │                                    │
│  ┌────────────────────▼─────────────────────────────────┐ │
│  │  Sony Camera Remote SDK (libCr_Core.so + adapters)   │ │
│  └────────────────────┬─────────────────────────────────┘ │
└───────────────────────┼───────────────────────────────────┘
                        │ USB-3 / Ethernet / WiFi
                        │
┌───────────────────────▼───────────────────────────────────┐
│                    Sony Camera                             │
│              (SDK-Compatible Model)                        │
└───────────────────────────────────────────────────────────┘
         │                                    │
         │ Serial                             │ PWM/Serial
         ▼                                    ▼
┌──────────────────┐              ┌─────────────────────────┐
│ Flight Controller│              │  Gimbal Controller      │
│   (Ardupilot)    │              │  (Gremsy / SimpleBGC)   │
└──────────────────┘              └─────────────────────────┘
```

---

## Sony SDK Implementation Details

### Connection Management

#### Camera Discovery Process
```cpp
// Pseudo-code for camera discovery
1. SDK_Init()
2. EnumCameraObjects()
   - Returns list of connected cameras
   - Each camera has connection type info
3. For each discovered camera:
   - Get camera info (model, serial, connection type)
   - Store connection details
4. Select target camera
5. Connect(camera_handle)
```

#### Connection Types and Auto-Detection
The SDK automatically detects and reports connection type:
- **USB:** Direct USB-3 connection
- **Ethernet (wired):** IP-based connection via ethernet
- **Ethernet (wireless):** WiFi connection to camera
- **SSH:** Authenticated ethernet connection

#### Connection State Management
```cpp
States:
- Disconnected
- Connecting
- Connected
- RemoteControlMode (normal control)
- RemoteTransferMode (control + content transfer)
- ContentsTransferMode (content only)
- Error

Transitions:
Disconnected -> Connecting -> Connected -> RemoteControlMode
RemoteControlMode <-> RemoteTransferMode (new in v2.00.00)
```

### Property Management System

#### Property Types
The SDK uses a property-based system for camera settings:

1. **Device Properties** (CrDeviceProperty)
   - Shutter Speed
   - Aperture (F-number)
   - ISO Sensitivity
   - Focus Mode
   - Focus Position
   - White Balance
   - Exposure Mode
   - Drive Mode (Single, Continuous, etc.)
   - Still/Movie mode
   - Battery Level
   - Media Status
   - And many more...

2. **Property Access Methods**
   - **Get:** Read current value
   - **Set:** Write new value
   - **GetAvailableValues:** Query valid values for property
   - **GetSupportedProperties:** Determine what camera supports

#### Property Callback System
```cpp
class DeviceCallback : public IDeviceCallback {
public:
    // Called when properties change
    virtual void OnPropertyChanged(CrDeviceProperty property, 
                                  CrPropertyValue value);
    
    // Called when live view data arrives
    virtual void OnLvPropertyChanged(CrLiveViewProperty property);
    
    // Called on connection events
    virtual void OnDisconnected(CrInt32u error);
    
    // Called when content download completes
    virtual void OnCompleteDownload(CrChar* filename, CrError result);
    
    // New in v2.00.00
    virtual void OnNotifyContentsTransfer(CrContentHandle handle, 
                                         CrContentsTransferState state);
};
```

### Live View Streaming

#### Live View Modes
1. **Standard Live View**
   - Viewfinder image stream
   - Typically JPEG frames
   - Frame rate depends on camera settings
   - Moderate latency (100-300ms typical)

2. **OSD Live View** (if supported)
   - Live view with on-screen display overlay
   - Includes camera settings overlaid on image
   - Useful for remote monitoring

#### Live View Implementation Considerations
- Live view data arrives via callback
- Application must handle JPEG decoding
- Consider frame buffering for smooth display
- Network bandwidth consideration for wireless links

#### Alternative: External HDMI Streaming
As noted, the SiYi MK32 provides HDMI connectivity:
- **Advantage:** Lower latency, hardware-based
- **Disadvantage:** Separate from SDK control path
- **Use Case:** Primary video feed for pilot/operator
- **SDK Live View:** Secondary/preview for GCS interface

### Video Streaming Options

#### Option 1: Sony SDK Live View
**Method:** Use SDK's live view callbacks
- **Pros:**
  - Integrated with camera control
  - No additional hardware needed
  - Programmatic access to frames
- **Cons:**
  - Higher latency than HDMI
  - Lower frame rate
  - Bandwidth intensive over data-link

#### Option 2: HDMI via MK32 Data-Link
**Method:** Camera HDMI -> MK32 HDMI input -> Digital transmission
- **Pros:**
  - Low latency
  - High quality
  - Independent of control link
  - Hardware accelerated
- **Cons:**
  - Requires HDMI-capable camera
  - Separate from SDK control
  - MK32-dependent

#### Option 3: Hybrid Approach (Recommended for Phase 1)
- **Primary Video:** HDMI through MK32 for real-time operations
- **Secondary Preview:** SDK live view for GCS monitoring/configuration
- **Benefits:** 
  - Best of both worlds
  - Redundancy
  - Flexibility for future expansion

---

## Camera Control Implementation

### Primary Camera Controls Mapping

#### Mode of Operation
```cpp
Property: CrDeviceProperty_ShootingMode
Values:
- CrShootingMode_Manual (M)
- CrShootingMode_ProgramAuto (P)
- CrShootingMode_Aperture_Priority (A)
- CrShootingMode_Shutter_Priority (S)
- CrShootingMode_Intelligent_Auto
// Plus many more camera-specific modes
```

#### Capture Mode (Still vs Video)
```cpp
Property: CrDeviceProperty_DriveMode
Values for Still:
- CrDriveMode_Single
- CrDriveMode_Continuous_Hi
- CrDriveMode_Continuous_Lo
- CrDriveMode_Continuous_Hi_Plus
// etc.

Property: CrDeviceProperty_Movie_Recording_State
Values for Video:
- CrMovie_Recording_State_Not_Recording
- CrMovie_Recording_State_Recording
- CrMovie_Recording_State_Stopping
```

#### Shutter Speed
```cpp
Property: CrDeviceProperty_ShutterSpeed
Format: Numerator / Denominator (e.g., 1/1000)
Special Values:
- Bulb mode
- Time values (e.g., 1", 2", 30")
API: SetDeviceProperty(CrDeviceProperty_ShutterSpeed, value)
```

#### Aperture (F-Stop)
```cpp
Property: CrDeviceProperty_FNumber
Format: F-number * 100 (e.g., F2.8 = 280)
Examples:
- 140 = F1.4
- 200 = F2.0
- 280 = F2.8
- 560 = F5.6
API: SetDeviceProperty(CrDeviceProperty_FNumber, value)
```

#### ISO Sensitivity
```cpp
Property: CrDeviceProperty_IsoSensitivity
Values:
- CrISO_AUTO
- 50, 64, 80, 100, 125, 160, 200, 250, 320, 400
- 500, 640, 800, 1000, 1250, 1600, 2000, 2500
- 3200, 4000, 5000, 6400, 8000, 10000, 12800
- 16000, 20000, 25600, 32000, 40000, 51200
- (camera-dependent maximum)
API: SetDeviceProperty(CrDeviceProperty_IsoSensitivity, value)
```

#### Focus Mode
```cpp
Property: CrDeviceProperty_FocusMode
Values:
- CrFocusMode_MF (Manual Focus)
- CrFocusMode_AF_S (Single AF)
- CrFocusMode_AF_C (Continuous AF)
- CrFocusMode_AF_A (Automatic AF)
- CrFocusMode_DMF (Direct Manual Focus)
API: SetDeviceProperty(CrDeviceProperty_FocusMode, value)
```

#### Manual Focus Control
```cpp
Property: CrDeviceProperty_FocusPosition
Command: SendCommand(CrCommandId_FocusPosition, direction, speed)
Direction:
- CrFocusDirection_Near
- CrFocusDirection_Far
Speed: 1-7 (camera dependent)

Note: Must be in Manual Focus mode (MF or DMF)
```

### Camera Status Monitoring

#### Battery Status
```cpp
Property: CrDeviceProperty_BatteryLevel
Values: 0-100 (percentage)
Additional: CrDeviceProperty_BatteryRemain (minutes estimate)

Callback: OnPropertyChanged() notifies of battery changes
```

#### SD Card Status
```cpp
Properties:
1. CrDeviceProperty_Media_Capacity
   - Total capacity in KB/MB/GB
   
2. CrDeviceProperty_Media_FreeSpace  
   - Remaining space in KB/MB/GB
   
3. CrDeviceProperty_Media_RecordableTime
   - Estimated recording time remaining (video)
   
4. CrDeviceProperty_Media_NumberOfStillImages
   - Estimated number of still images remaining

Callback: OnPropertyChanged() for real-time updates
```

#### Settings Confirmation
```cpp
Method 1: Poll properties after setting
- Set property via SetDeviceProperty()
- Wait for OnPropertyChanged() callback
- Verify new value matches requested value

Method 2: Get property explicitly
- Call GetDeviceProperty() 
- Compare returned value to expected value

Best Practice: Use callback system for confirmation
```

---

## Gimbal Integration

### Gimbal Control Architecture

The Sony SDK does not directly control gimbals. Gimbal integration requires separate implementation:

```
┌────────────────────────────────────────────────────┐
│  Payload Manager Application                       │
│                                                     │
│  ┌──────────────────┐        ┌─────────────────┐  │
│  │ Sony SDK Layer   │        │ Gimbal Control  │  │
│  │ (Camera Control) │        │ Layer           │  │
│  └──────────────────┘        └─────────────────┘  │
│                                       │            │
└───────────────────────────────────────┼────────────┘
                                        │
                        ┌───────────────┴──────────────┐
                        │                              │
                Serial/UART                      Serial/UART
                        │                              │
                        ▼                              ▼
              ┌──────────────────┐         ┌──────────────────┐
              │ Gremsy Gimbal    │         │ SimpleBGC Gimbal │
              │ (MoVI, T-series) │         │ (Basecam)        │
              └──────────────────┘         └──────────────────┘
```

### Gremsy Gimbal Protocol

#### Connection
- **Interface:** Serial (UART) or USB
- **Baud Rate:** 115200 (typical)
- **Protocol:** Gremsy Serial Protocol (GSP)
- **Control Types:**
  - Angle control (position)
  - Rate control (velocity)
  - Follow mode
  - Lock mode

#### Implementation Requirements
1. **Serial Communication Library**
   - Use termios on Linux
   - Configure port: 115200 8N1
   
2. **Protocol Implementation**
   - Message format: STX + CMD + DATA + CHECKSUM + ETX
   - Implement checksum calculation
   - Handle acknowledgments

3. **Configuration Interface**
   - PID parameters
   - Motor power
   - Follow speed
   - Control mode
   - Home position

### SimpleBGC Gimbal Protocol

#### Connection
- **Interface:** Serial (UART)
- **Baud Rate:** 115200 (typical)
- **Protocol:** SimpleBGC Serial API v2.6+
- **Control Types:**
  - Angle control
  - Speed control
  - RC input control
  - Follow mode configuration

#### Implementation Requirements
1. **Serial Communication**
   - Similar to Gremsy: termios configuration
   - Message format: START_BYTE + CMD + SIZE + HEADER_CS + DATA + DATA_CS
   
2. **Protocol Implementation**
   - Command ID handling
   - Payload size calculation
   - CRC checksum
   - Response parsing

3. **Configuration Interface**
   - Real-time data request
   - Board version info
   - PID tuning
   - Motor configuration
   - Profile management

### Unified Gimbal Control Interface

For the application layer, create a gimbal abstraction:

```cpp
class IGimbalController {
public:
    virtual ~IGimbalController() = default;
    
    // Connection
    virtual bool Connect(const char* port) = 0;
    virtual void Disconnect() = 0;
    virtual bool IsConnected() = 0;
    
    // Control
    virtual void SetMode(GimbalMode mode) = 0;
    virtual void SetAngle(float pitch, float yaw, float roll) = 0;
    virtual void SetRate(float pitch_rate, float yaw_rate) = 0;
    virtual void SetHome() = 0;
    
    // Configuration
    virtual void SetFollowSpeed(float speed) = 0;
    virtual void SetControlGain(float gain) = 0;
    
    // Status
    virtual GimbalStatus GetStatus() = 0;
    virtual void GetAttitude(float& pitch, float& yaw, float& roll) = 0;
};

// Implementations:
class GremsyController : public IGimbalController { ... };
class SimpleBGCController : public IGimbalController { ... };
```

---

## Mavlink Integration Specifics

### Mavlink Camera Protocol Implementation

#### Message Types to Implement

**1. CAMERA_INFORMATION (#259)**
```cpp
Purpose: Inform GCS about camera capabilities
Trigger: On request or connection
Contains:
- Camera model name
- Firmware version
- Focal length
- Sensor size
- Resolution
- Video capabilities
- Flags (capture modes supported)
```

**2. CAMERA_SETTINGS (#260)**
```cpp
Purpose: Current camera settings
Trigger: Periodic or on request
Contains:
- Current mode (photo/video)
- Zoom level (if applicable)
- Focus mode
```

**3. CAMERA_CAPTURE_STATUS (#262)**
```cpp
Purpose: Capture status information
Trigger: Periodic during capture, on status change
Contains:
- Image capture count
- Video recording status
- Available storage
- Recording time elapsed
```

**4. STORAGE_INFORMATION (#261)**
```cpp
Purpose: Storage (SD card) status
Trigger: Periodic or on request
Contains:
- Storage ID
- Total capacity
- Used capacity
- Available capacity
- Read/write speed
- Status flags
```

**5. CAMERA_IMAGE_CAPTURED (#263)**
```cpp
Purpose: Notification that image was captured
Trigger: After each photo capture
Contains:
- Capture time
- GPS coordinates (from flight controller)
- Altitude
- Attitude
- Image index
- File URL (if available)
- Camera ID
```

#### Command Types to Handle

**MAV_CMD_REQUEST_CAMERA_INFORMATION (#521)**
- Requests camera capability information
- Response: CAMERA_INFORMATION message

**MAV_CMD_REQUEST_CAMERA_SETTINGS (#522)**
- Requests current camera settings
- Response: CAMERA_SETTINGS message

**MAV_CMD_REQUEST_CAMERA_CAPTURE_STATUS (#527)**
- Requests capture status
- Response: CAMERA_CAPTURE_STATUS message

**MAV_CMD_REQUEST_STORAGE_INFORMATION (#525)**
- Requests storage information
- Response: STORAGE_INFORMATION message

**MAV_CMD_RESET_CAMERA_SETTINGS (#529)**
- Resets camera to default settings
- Response: Command ACK

**MAV_CMD_SET_CAMERA_MODE (#530)**
- Switch between photo and video mode
- Param1: 0=photo, 1=video
- Response: Command ACK

**MAV_CMD_IMAGE_START_CAPTURE (#2000)**
- Trigger photo capture
- Param2: Interval (for interval shooting)
- Param3: Total images
- Response: Command ACK, then CAMERA_IMAGE_CAPTURED

**MAV_CMD_IMAGE_STOP_CAPTURE (#2001)**
- Stop interval/time-lapse shooting
- Response: Command ACK

**MAV_CMD_VIDEO_START_CAPTURE (#2500)**
- Start video recording
- Response: Command ACK

**MAV_CMD_VIDEO_STOP_CAPTURE (#2501)**
- Stop video recording
- Response: Command ACK

**MAV_CMD_SET_CAMERA_ZOOM (#531)**
- Control camera zoom (if supported)
- Param1: Zoom type (0=step, 1=continuous)
- Param2: Zoom value
- Response: Command ACK

**MAV_CMD_SET_CAMERA_FOCUS (#532)**
- Control camera focus
- Param1: Focus type (0=step, 1=continuous, 2=range)
- Param2: Focus value
- Response: Command ACK

### Mavlink Router Configuration

#### Setup on Raspberry Pi
```bash
# Install mavlink-router
sudo apt install mavlink-router

# Configuration file: /etc/mavlink-router/main.conf
[General]
TcpServerPort=5760
ReportStats=false

# Serial connection to flight controller
[UartEndpoint alpha]
Device=/dev/ttyS0
Baud=57600

# Ethernet connection to ground station (via MK32)
[TcpEndpoint beta]
Address=192.168.144.10
Port=14550

# Local connection for payload manager app
[UartEndpoint gamma]
Device=/dev/ttyACM0
Baud=115200
```

#### Application Integration
```cpp
// Connect to mavlink-router
int mavlink_fd = open("/dev/ttyACM0", O_RDWR | O_NOCTTY);

// Configure serial port
struct termios options;
tcgetattr(mavlink_fd, &options);
cfsetispeed(&options, B115200);
cfsetospeed(&options, B115200);
options.c_cflag |= (CLOCAL | CREAD);
options.c_cflag &= ~PARENB;
options.c_cflag &= ~CSTOPB;
options.c_cflag &= ~CSIZE;
options.c_cflag |= CS8;
tcsetattr(mavlink_fd, TCSANOW, &options);

// Read/write mavlink messages
// Use mavlink C library for message packing/unpacking
```

---

## Development Environment Setup

### Raspberry Pi 4 Setup

#### 1. Operating System Installation
```bash
# Flash Ubuntu Server 22.04 LTS (64-bit) to microSD
# Use Raspberry Pi Imager or dd command

# After first boot, update system
sudo apt update
sudo apt upgrade -y

# Install necessary packages
sudo apt install -y \
    build-essential \
    cmake \
    git \
    libusb-1.0-0-dev \
    libssh2-1-dev \
    libssl-dev \
    net-tools \
    usbutils \
    mavlink-router
```

#### 2. USB Permissions
```bash
# Add udev rule for Sony cameras
sudo tee /etc/udev/rules.d/99-sony-camera.rules << EOF
SUBSYSTEM=="usb", ATTR{idVendor}=="054c", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 3. Serial Port Configuration
```bash
# Disable serial console (if using UART for gimbal/FC)
sudo systemctl disable serial-getty@ttyS0.service

# Enable UART in /boot/firmware/config.txt
echo "enable_uart=1" | sudo tee -a /boot/firmware/config.txt
echo "dtoverlay=uart5" | sudo tee -a /boot/firmware/config.txt

# Reboot to apply
sudo reboot
```

### Development Machine Setup (VS Code Remote)

#### VS Code Extensions
- Remote - SSH
- C/C++ Extension Pack
- CMake Tools
- GitLens

#### SSH Configuration
```bash
# On development machine ~/.ssh/config
Host pi-payload
    HostName 192.168.1.100  # Pi IP address
    User ubuntu
    ForwardAgent yes
```

#### Remote Development Workflow
1. Open VS Code
2. Connect to pi-payload via Remote-SSH
3. Open project folder on Pi
4. Use integrated terminal for building
5. Use VS Code debugging with gdb

### Sony SDK Integration

#### 1. Extract SDK on Raspberry Pi
```bash
# Copy SDK to Pi
scp CrSDK_v2.00.00_20250805a_Linux64ARMv8.zip ubuntu@pi-payload:~/

# SSH to Pi and extract
ssh ubuntu@pi-payload
cd ~
unzip CrSDK_v2.00.00_20250805a_Linux64ARMv8.zip
cd CrSDK_vX.XX.XX_YYYYMMDDx  # Use actual version
```

#### 2. Build Sample Application
```bash
# Create build directory
mkdir build
cd build

# Run CMake
cmake ..

# Build
make

# Test sample app
cd Release
./RemoteCli
```

#### 3. Integrate SDK into Project
```cmake
# CMakeLists.txt for payload manager project
cmake_minimum_required(VERSION 3.16)
project(PayloadManager CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Sony SDK paths
set(CRSDK_PATH "/home/ubuntu/CrSDK_vX.XX.XX_YYYYMMDDx")
set(CRSDK_INCLUDE "${CRSDK_PATH}/CRSDK")
set(CRSDK_LIB_PATH "${CRSDK_PATH}/external/crsdk")

# Include directories
include_directories(${CRSDK_INCLUDE})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
file(GLOB SOURCES "src/*.cpp")

# Create executable
add_executable(payload_manager ${SOURCES})

# Link Sony SDK libraries
target_link_libraries(payload_manager
    ${CRSDK_LIB_PATH}/libCr_Core.so
    ${CRSDK_LIB_PATH}/CrAdapter/libCr_PTP_IP.so
    ${CRSDK_LIB_PATH}/CrAdapter/libCr_PTP_USB.so
    ${CRSDK_LIB_PATH}/CrAdapter/libusb-1.0.so
    ${CRSDK_LIB_PATH}/CrAdapter/libssh2.so
    pthread
)

# Copy SDK libraries to output directory
add_custom_command(TARGET payload_manager POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${CRSDK_LIB_PATH}
    $<TARGET_FILE_DIR:payload_manager>/libs
)
```

---

## Testing Strategy

### Unit Testing

#### SDK Wrapper Tests
```cpp
// Test camera connection
TEST(CameraSDKTest, ConnectionUSB) {
    CameraController camera;
    EXPECT_TRUE(camera.Init());
    EXPECT_TRUE(camera.Connect(ConnectionType::USB));
    EXPECT_TRUE(camera.IsConnected());
    camera.Disconnect();
}

// Test property setting
TEST(CameraSDKTest, SetShutterSpeed) {
    CameraController camera;
    camera.Connect(ConnectionType::USB);
    
    EXPECT_TRUE(camera.SetShutterSpeed(1, 1000)); // 1/1000s
    
    auto shutter = camera.GetShutterSpeed();
    EXPECT_EQ(shutter.numerator, 1);
    EXPECT_EQ(shutter.denominator, 1000);
}

// Test callbacks
TEST(CameraSDKTest, PropertyCallback) {
    CameraController camera;
    bool callback_received = false;
    
    camera.RegisterCallback([&](Property prop, Value val) {
        callback_received = true;
    });
    
    camera.Connect(ConnectionType::USB);
    camera.SetISO(400);
    
    // Wait for callback
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    EXPECT_TRUE(callback_received);
}
```

#### Mavlink Integration Tests
```cpp
TEST(MavlinkTest, CameraInformationMessage) {
    MavlinkHandler handler;
    
    auto msg = handler.CreateCameraInformationMessage();
    
    EXPECT_EQ(msg.msgid, MAVLINK_MSG_ID_CAMERA_INFORMATION);
    EXPECT_STREQ(msg.vendor_name, "Sony");
}

TEST(MavlinkTest, HandleCaptureCommand) {
    MavlinkHandler handler;
    CameraController camera;
    
    mavlink_message_t cmd_msg;
    // Create MAV_CMD_IMAGE_START_CAPTURE message
    
    bool result = handler.HandleCommand(cmd_msg, camera);
    EXPECT_TRUE(result);
    
    // Verify image captured
    EXPECT_TRUE(camera.IsCapturing());
}
```

### Integration Testing

#### End-to-End Camera Control
```bash
#!/bin/bash
# Test script for camera control via Mavlink

# Start payload manager
./payload_manager &
PAYLOAD_PID=$!

# Wait for initialization
sleep 2

# Send Mavlink command to capture image
mavlink_cmd_tool --command=IMAGE_START_CAPTURE

# Wait for capture
sleep 1

# Verify image was captured
if [ -f "/tmp/captured_image.jpg" ]; then
    echo "PASS: Image captured"
else
    echo "FAIL: No image found"
fi

# Cleanup
kill $PAYLOAD_PID
```

#### Gimbal Integration Test
```bash
#!/bin/bash
# Test gimbal control

# Send pan command
echo "Testing gimbal pan..."
./payload_manager_cli gimbal pan 45

# Check gimbal response
# Verify through serial monitor or gimbal feedback

echo "Gimbal test complete"
```

### Hardware-in-Loop (HIL) Testing

#### Test Setup
1. **Equipment:**
   - Raspberry Pi 4 with Ubuntu Server
   - Sony camera (SDK compatible)
   - Gimbal (Gremsy or SimpleBGC)
   - Flight controller (for Mavlink testing)
   - SiYi MK32 data-link (or ethernet switch for simulation)

2. **Test Scenarios:**
   - Camera connection via USB
   - Camera connection via Ethernet
   - All camera controls functional
   - Mavlink commands from GCS
   - Gimbal control integration
   - Long-duration stability test

3. **Automated HIL Test Harness:**
   ```python
   # Python test script for automated HIL testing
   import pymavlink
   import time
   import unittest
   
   class HILTests(unittest.TestCase):
       def setUp(self):
           self.mavlink = pymavlink.mavutil.mavlink_connection(
               'udp:127.0.0.1:14550'
           )
           
       def test_camera_trigger(self):
           # Send trigger command
           self.mavlink.mav.command_long_send(
               1, 1,  # target system, component
               mavlink.MAV_CMD_IMAGE_START_CAPTURE,
               0, 0, 0, 0, 0, 0, 0, 0
           )
           
           # Wait for ACK
           msg = self.mavlink.recv_match(type='COMMAND_ACK', timeout=5)
           self.assertIsNotNone(msg)
           self.assertEqual(msg.result, 
                          mavlink.MAV_RESULT_ACCEPTED)
   ```

---

## Performance Considerations

### Latency Targets

#### Camera Control Commands
- **Command to execution:** < 100ms
- **Settings confirmation:** < 50ms
- **Property query response:** < 50ms

#### Live View Streaming (SDK)
- **Frame latency:** < 300ms (acceptable)
- **Frame rate:** 10-30 fps depending on resolution
- **Image quality:** Compressed JPEG

#### Live View via HDMI (MK32)
- **Frame latency:** < 50ms (hardware dependent)
- **Frame rate:** 30-60 fps
- **Image quality:** Uncompressed/minimally compressed

#### Mavlink Communication
- **Command acknowledgment:** < 100ms
- **Status update frequency:** 1-5 Hz
- **Telemetry packet size:** < 1KB typical

### CPU and Memory Usage

#### Expected Resource Usage
```
Payload Manager Application:
- CPU: 15-25% of single core (steady state)
- CPU: 40-60% during live view processing
- RAM: 100-200 MB
- Network: 1-5 Mbps for SDK live view
           20-50 Mbps for HDMI video (MK32 dependent)

Sony SDK Libraries:
- CPU: 10-20% for camera communication
- RAM: 50-100 MB
```

#### Optimization Strategies
1. **Minimize frame copying**
   - Use zero-copy techniques where possible
   - Shared memory for inter-process communication

2. **Efficient property polling**
   - Use callback system instead of polling
   - Only query necessary properties

3. **Thread management**
   - Separate threads for:
     - Camera control
     - Mavlink communication
     - Live view processing
     - Gimbal control
   - Use thread priorities appropriately

4. **Memory management**
   - Pre-allocate buffers for live view frames
   - Implement frame pool/recycling
   - Monitor and prevent memory leaks

### Network Bandwidth Management

#### Bandwidth Allocation
```
Total Available: ~10 Mbps (typical for SiYi MK32 data-link)

Allocation:
- HDMI Video (via MK32): 20-50 Mbps (separate path if supported)
- SDK Live View: 1-5 Mbps (optional, lower priority)
- Mavlink Telemetry: 50-100 Kbps
- Camera Control: 10-50 Kbps
- Gimbal Control: 5-10 Kbps
- Reserve: 1-2 Mbps for spikes
```

#### Adaptive Quality
- Reduce SDK live view quality/framerate if bandwidth limited
- Prioritize control commands over status updates
- Implement QoS for critical commands

---

## Security Considerations

### SSH Authentication (for Ethernet Cameras)
```cpp
// SSH connection for supported cameras
ConnectionInfo info;
info.connection_type = ConnectionType::Ethernet;
info.ip_address = "192.168.1.100";
info.username = "camera_user";
info.password = "secure_password";  // Or use key-based auth
info.ssh_enabled = true;

camera.Connect(info);
```

**Security Best Practices:**
- Use key-based authentication instead of passwords
- Rotate credentials regularly
- Limit SSH access to specific IP ranges
- Monitor connection attempts

### Network Security
1. **Isolate camera network**
   - Use dedicated network segment for camera
   - Firewall rules to restrict access
   
2. **Encrypt sensitive data**
   - If storing credentials, use encryption
   - Secure storage for SSH keys

3. **Firmware security**
   - Verify firmware integrity before updates
   - Use signed firmware from Sony

### Application Security
- Run application with minimum necessary privileges
- Input validation for all Mavlink commands
- Rate limiting for commands to prevent DOS
- Logging and monitoring for security events

---

## Deployment Considerations

### Installation Procedure

#### 1. Prepare Raspberry Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y build-essential cmake git \
    libusb-1.0-0-dev libssh2-1-dev libssl-dev \
    mavlink-router

# Configure USB permissions
sudo cp 99-sony-camera.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

#### 2. Install Payload Manager Application
```bash
# Copy application package
scp payload_manager.tar.gz ubuntu@pi:~/

# Extract
tar xzf payload_manager.tar.gz
cd payload_manager

# Copy Sony SDK libraries
cp -r libs/* /usr/local/lib/
sudo ldconfig
```

#### 3. Configure Services
```bash
# Install systemd service
sudo cp payload_manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable payload_manager
sudo systemctl start payload_manager
```

#### 4. Configure Mavlink Router
```bash
# Edit mavlink-router configuration
sudo nano /etc/mavlink-router/main.conf

# Restart mavlink-router
sudo systemctl restart mavlink-router
```

### Systemd Service Configuration
```ini
# /etc/systemd/system/payload_manager.service
[Unit]
Description=Drone Payload Manager
After=network.target mavlink-router.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/payload_manager
ExecStart=/home/ubuntu/payload_manager/bin/payload_manager
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Logging and Monitoring

#### Application Logging
```cpp
// Use syslog for system-wide logging
#include <syslog.h>

// Initialize logging
openlog("payload_manager", LOG_PID | LOG_CONS, LOG_USER);

// Log messages
syslog(LOG_INFO, "Camera connected: %s", camera_model);
syslog(LOG_WARNING, "Low battery: %d%%", battery_level);
syslog(LOG_ERR, "Failed to capture image: %s", error_msg);

// Close logging
closelog();
```

#### View Logs
```bash
# View application logs
sudo journalctl -u payload_manager -f

# View system logs
sudo journalctl -xe

# View last 100 lines
sudo journalctl -u payload_manager -n 100
```

### Health Monitoring
```bash
#!/bin/bash
# health_check.sh - Monitor payload manager health

# Check if service is running
systemctl is-active --quiet payload_manager
if [ $? -ne 0 ]; then
    echo "ERROR: Payload manager not running"
    sudo systemctl restart payload_manager
fi

# Check CPU usage
CPU_USAGE=$(top -bn1 | grep payload_manager | awk '{print $9}')
if [ $(echo "$CPU_USAGE > 80" | bc) -eq 1 ]; then
    echo "WARNING: High CPU usage: $CPU_USAGE%"
fi

# Check memory usage
MEM_USAGE=$(ps aux | grep payload_manager | awk '{print $4}')
if [ $(echo "$MEM_USAGE > 50" | bc) -eq 1 ]; then
    echo "WARNING: High memory usage: $MEM_USAGE%"
fi

# Check camera connection
# ... implement camera connectivity check via control socket
```

---

## Appendices

### Appendix A: Supported Sony Camera Models (Partial List)

Based on SDK v2.00.00 documentation, supported cameras include:
- **Alpha Series:** α1, α7R V, α7 IV, α7S III, α7R IV, α7R III, α7 III, α7S II
- **Cinema Line:** FX3, FX30, FX6, FX9
- **PTZ Cameras:** MPC-2610 (monitoring functions)
- **Others:** ZV-E1, ZV-E10

*Note: Full compatibility list should be verified in the latest API reference documentation.*

### Appendix B: Sony SDK Version History Notes

Key improvements in recent versions relevant to this project:
- **v1.04.00:** Added ethernet connectivity support
- **v1.05.00:** Content download from camera
- **v1.06.00:** SSH authentication for ethernet
- **v1.11.00:** Monitoring functions (MPC-2610)
- **v1.12.00:** Wireless ethernet support
- **v1.13.00:** RemoteTransferMode, OSD capture, remote firmware update
- **v2.00.00 (Current):** PTZ camera support, content deletion in RemoteTransferMode

### Appendix C: Reference Links

- Sony Camera Remote SDK: http://www.sony.net/CameraRemoteSDK/
- libusb: http://libusb.info/
- Mavlink Protocol: https://mavlink.io/
- Gremsy Gimbal: https://gremsy.com/
- SimpleBGC: http://www.basecamelectronics.com/
- Ardupilot: https://ardupilot.org/
- SiYi Technology: http://en.siyi.biz/

### Appendix D: Glossary

- **CrSDK:** Camera Remote SDK (Sony)
- **PTP:** Picture Transfer Protocol
- **PTP/IP:** PTP over IP networks
- **OSD:** On-Screen Display
- **PTZ:** Pan-Tilt-Zoom
- **GCS:** Ground Control Station
- **HIL:** Hardware-in-Loop
- **SBC:** Single Board Computer
- **SDK:** Software Development Kit

---

## Summary and Next Steps

### Key Decisions for Phase 1

1. **Video Streaming Strategy:**
   - Primary: HDMI via SiYi MK32 (low latency)
   - Secondary: Sony SDK live view (for GCS preview)
   - Rationale: Best performance + flexibility

2. **Camera Connection:**
   - Initial development: USB-3
   - Production: Auto-detect (USB/Ethernet/WiFi)
   - Rationale: Simplicity for dev, flexibility for deployment

3. **Gimbal Integration:**
   - Separate control layer from Sony SDK
   - Support both Gremsy and SimpleBGC via abstraction
   - Rationale: Modularity and expandability

4. **Development Approach:**
   - VS Code remote development to Raspberry Pi
   - CMake build system
   - Systemd for service management
   - Rationale: Industry standard tools

### Phase 1 Deliverables Checklist

- [ ] Sony SDK integrated and tested
- [ ] Camera control via application functional
- [ ] Mavlink integration complete
- [ ] Android app can control camera
- [ ] GCS (QGC/Mission Planner) can control camera
- [ ] Gimbal control for both Gremsy and SimpleBGC
- [ ] Status monitoring working
- [ ] System stable for 8+ hour continuous operation
- [ ] Documentation complete
- [ ] Unit and integration tests passing

### Recommended Phase 1 Timeline Updates

Based on the technical details:

**Weeks 1-3: Core Infrastructure**
- Week 1: Environment setup, SDK integration, basic connection
- Week 2: Property management, callback system
- Week 3: Command queue, state machine, error handling

**Weeks 4-6: Mavlink Integration**
- Week 4: Message definitions, parser implementation
- Week 5: Camera control commands, status broadcasting
- Week 6: Mavlink router integration, end-to-end testing

**Weeks 7-10: Android Application**
- Week 7-8: UI design and implementation
- Week 9: Network communication, command sending
- Week 10: Testing and refinement

**Weeks 11-12: Gimbal Integration**
- Week 11: Gremsy protocol implementation
- Week 12: SimpleBGC protocol implementation

**Weeks 13-15: System Integration & Testing**
- Week 13: Integration testing with all components
- Week 14: Hardware-in-loop testing, performance optimization
- Week 15: Bug fixes, stability testing

**Weeks 16-17: Documentation & Deployment**
- Week 16: User manuals, API documentation
- Week 17: Deployment procedures, handover

---

**Document End**
