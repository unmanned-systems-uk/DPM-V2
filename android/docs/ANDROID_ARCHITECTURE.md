# DPM Android Application - Architecture Documentation

**Version**: 1.0
**Date**: October 25, 2025
**Project**: Drone Payload Manager (DPM) - Ground Station Application
**Platform**: Android (Kotlin + Jetpack Compose)
**Package**: `uk.unmannedsystems.dpm_android`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Structure](#2-project-structure)
3. [Architecture Overview](#3-architecture-overview)
4. Core Components - Phase 2
5. Data Layer - Phase 2
6. Network Layer - Phase 2
7. UI Layer - Phase 2
8. State Management - Phase 3
9. Video Streaming - Phase 3
10. Navigation - Phase 3
11. Dependencies - Phase 3
12. Configuration & Settings - Phase 4
13. Testing - Phase 4
14. Build System - Phase 4
15. Code Conventions - Phase 4
16. Deployment - Phase 4
17. Known Issues & Technical Debt - Phase 4
18. Future Roadmap - Phase 4

---

## 1. Executive Summary

### 1.1 Project Overview

**DPM Android** is a professional ground station application designed for the SkyDroid H16 Ground Station, providing real-time control and monitoring of aerial camera payloads on unmanned aerial systems.

**Primary Purpose:**
- Control Sony Alpha cameras mounted on UAV via R16 Air Unit
- Stream live FPV video via RTSP from onboard camera systems
- Monitor system status and telemetry in real-time
- Manage gimbal positioning and camera settings remotely
- Download captured content from air-side to ground station

**Target Users:**
- Professional drone operators
- Aerial cinematographers
- Survey and inspection teams
- UAV payload specialists

**Key Capabilities:**
- Full manual camera control (shutter speed, aperture, ISO, exposure compensation)
- Live RTSP video streaming with low latency (<1 second)
- Real-time bi-directional network communication over WiFi/Ethernet
- Persistent settings management
- System health monitoring

### 1.2 Technology Stack

**Core Technologies:**
- **Language**: Kotlin 2.0.21
- **Build System**: Gradle 8.13.0 with Kotlin DSL
- **UI Framework**: Jetpack Compose (BOM 2024.09.00)
- **Architecture**: MVVM (Model-View-ViewModel)
- **Minimum SDK**: API 24 (Android 7.0)
- **Target SDK**: API 36 (Android 14+)
- **Compile SDK**: API 36

**Major Libraries:**
- **Jetpack Compose**: Modern declarative UI toolkit
  - compose-ui
  - compose-material3
  - compose-material-icons-extended
  - material3-adaptive-navigation-suite
- **Lifecycle & ViewModel**: androidx.lifecycle 2.6.1
  - lifecycle-runtime-ktx
  - lifecycle-viewmodel-compose
- **Coroutines**: kotlinx-coroutines-android 1.7.3
- **Data Persistence**: androidx.datastore-preferences 1.0.0
- **JSON Processing**: Gson 2.10.1
- **Video Streaming**: Media3 (ExoPlayer) 1.2.0
  - media3-exoplayer
  - media3-ui
  - media3-exoplayer-rtsp

**Development Tools:**
- Android Studio (recommended IDE)
- Git version control
- Claude Code for AI-assisted development

### 1.3 Key Features

**Implemented Features (Phase 1 MVP - 70% Complete):**

✅ **Camera Control:**
- Shutter speed control (1/8000s to 30s)
- Aperture control (f/1.4 to f/22)
- ISO control (100 to 25600)
- Exposure compensation (-3 to +3 EV)
- Camera mode selection (Auto, Manual, Aperture Priority, Shutter Priority, Program)
- White balance selection
- File format selection (JPEG, RAW, JPEG+RAW)
- Focus mode selection
- Shutter release command

✅ **Video Streaming:**
- RTSP video player with ExoPlayer
- Full-screen video background with overlay controls (QGroundControl-style)
- Low-latency configuration (500ms buffer)
- Configurable RTSP URL
- Aspect ratio modes (AUTO, FILL, FIT)
- Enable/disable toggle
- State overlays (Disconnected, Connecting, Connected, Error, Disabled)

✅ **Network Communication:**
- TCP command channel (port 5000)
- UDP status receiver (port 5001, 5Hz updates)
- UDP heartbeat sender (port 5002, 1Hz bidirectional)
- JSON protocol implementation
- Connection state management
- Auto-connect on app startup
- Configurable network settings

✅ **Settings Management:**
- Persistent settings via DataStore
- Network configuration (IP, ports, timeouts, intervals)
- Video streaming configuration
- Reset to defaults functionality
- Real-time settings updates

✅ **System Monitoring:**
- System status display (uptime, CPU, memory, storage)
- Real-time connection status indicators
- Battery level monitoring
- Remaining shots counter
- Connection logs with color coding

✅ **User Interface:**
- Material Design 3 implementation
- Navigation drawer with 5 screens
- Dark/light theme support (system default)
- Responsive layouts
- Touch-optimized controls for ground station

**Screens Implemented:**
1. Camera Control Screen - Full camera interface with live video
2. Settings Screen - Network and video configuration
3. System Status Screen - Real-time system monitoring
4. Event Log Screen - Development diagnostics
5. Downloads Screen - Placeholder for Phase 2

### 1.4 Development Status

**Current Phase**: Phase 1 - Active Development
**Overall Completion**: 70% (Phase 1 MVP)

**Progress by Area:**
```
Documentation Review:  ████████████████████████████████ 100% Complete
Project Setup:         ████████████████████████████████ 100% Complete
Network Layer:         ████████████████████████████████ 100% Complete
UI Implementation:     ████████████████████████████░░░░  85% In Progress
Command Protocol:      ████████████░░░░░░░░░░░░░░░░░░░░  40% In Progress
Video Streaming:       ████████████████████████████████ 100% Complete
Testing:               ██████░░░░░░░░░░░░░░░░░░░░░░░░░░  20% Started
Integration:           ████████████████████░░░░░░░░░░░░  60% In Progress
```

**Completed (v1.0):**
- ✅ Network client with TCP/UDP communication
- ✅ Settings persistence with DataStore
- ✅ Camera control UI with all manual controls
- ✅ RTSP video streaming integration
- ✅ System status monitoring
- ✅ Auto-connect on app startup
- ✅ Connection status indicators
- ✅ Event logging system
- ✅ Build system and dependencies

**In Progress:**
- ⏳ End-to-end testing with R16 hardware
- ⏳ Camera property commands (waiting for air-side)
- ⏳ Performance optimization
- ⏳ Error handling improvements

**Planned (Phase 2):**
- Content download management
- Advanced camera controls
- Gimbal control interface
- Video recording controls
- Comprehensive testing suite

### 1.5 Target Hardware

**Primary Device**: SkyDroid H16 Pro Ground Station

**Hardware Specifications:**
- **Processor**: Rockchip RK3566 (Quad-core ARM Cortex-A55)
- **RAM**: 4GB LPDDR4
- **Storage**: 32GB eMMC
- **Display**: 7" 1280×800 touchscreen
- **OS**: Android 11 (API 30)
- **Network**: WiFi 5 (802.11ac), Gigabit Ethernet
- **Battery**: 8000mAh (6-8 hour runtime)

**Application Requirements:**
- **Minimum Android Version**: 7.0 (API 24)
- **Target Android Version**: 14+ (API 36)
- **Recommended RAM**: 2GB minimum, 4GB optimal
- **Storage**: 100MB app size, 500MB for content cache
- **Network**: 100Mbps+ for video streaming

**Compatibility:**
- Optimized for H16 screen size and resolution
- Touch-optimized controls for outdoor use
- Power-efficient for extended operation
- WiFi and Ethernet support for flexible networking

---

## 2. Project Structure

### 2.1 Directory Layout

```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/uk/unmannedsystems/dpm_android/
│   │   │   │   ├── DPMApplication.kt
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── camera/
│   │   │   │   │   ├── CameraControlScreen.kt
│   │   │   │   │   ├── CameraState.kt
│   │   │   │   │   ├── CameraViewModel.kt
│   │   │   │   │   └── components/
│   │   │   │   │       ├── CameraButtons.kt
│   │   │   │   │       └── ExposureControl.kt
│   │   │   │   ├── eventlog/
│   │   │   │   │   ├── EventLogScreen.kt
│   │   │   │   │   └── EventLogViewModel.kt
│   │   │   │   ├── network/
│   │   │   │   │   ├── NetworkClient.kt
│   │   │   │   │   ├── NetworkManager.kt
│   │   │   │   │   ├── NetworkSettings.kt
│   │   │   │   │   └── ProtocolMessages.kt
│   │   │   │   ├── settings/
│   │   │   │   │   ├── SettingsRepository.kt
│   │   │   │   │   ├── SettingsScreen.kt
│   │   │   │   │   └── SettingsViewModel.kt
│   │   │   │   ├── system/
│   │   │   │   │   ├── SystemStatusScreen.kt
│   │   │   │   │   └── SystemStatusViewModel.kt
│   │   │   │   ├── video/
│   │   │   │   │   ├── VideoPlayerView.kt
│   │   │   │   │   └── VideoPlayerViewModel.kt
│   │   │   │   └── ui/
│   │   │   │       └── theme/
│   │   │   │           ├── Color.kt
│   │   │   │           ├── Theme.kt
│   │   │   │           └── Type.kt
│   │   │   ├── res/
│   │   │   │   ├── drawable/
│   │   │   │   ├── mipmap/
│   │   │   │   └── values/
│   │   │   │       ├── colors.xml
│   │   │   │       ├── strings.xml
│   │   │   │       └── themes.xml
│   │   │   └── AndroidManifest.xml
│   │   ├── test/
│   │   │   └── java/uk/unmannedsystems/dpm_android/
│   │   └── androidTest/
│   │       └── java/uk/unmannedsystems/dpm_android/
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/
│   ├── libs.versions.toml
│   └── wrapper/
├── docs/
│   ├── ANDROID_ARCHITECTURE.md (this file)
│   ├── PROGRESS_AND_TODO.MD
│   └── RTSP Video Stream.MD
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── gradlew
└── gradlew.bat
```

### 2.2 Package Structure

**Package**: `uk.unmannedsystems.dpm_android`

#### Root Package
- **Files**: 2
- **Purpose**: Application-level initialization and main activity
- **Key Classes**:
  - `DPMApplication.kt` - Custom Application class for app-wide initialization
  - `MainActivity.kt` - Main activity with navigation drawer

#### `camera` Package
- **Package**: `uk.unmannedsystems.dpm_android.camera`
- **Files**: 3
- **Purpose**: Camera control interface and state management
- **Key Classes**:
  - `CameraControlScreen.kt` - Main camera control composable with video background
  - `CameraViewModel.kt` - Camera state management and network commands
  - `CameraState.kt` - Camera state data model

**Subpackage**: `camera.components`
- **Files**: 2
- **Purpose**: Reusable camera UI components
- **Key Classes**:
  - `CameraButtons.kt` - Control buttons (shutter, capture, format selectors)
  - `ExposureControl.kt` - Exposure adjustment controls

#### `eventlog` Package
- **Package**: `uk.unmannedsystems.dpm_android.eventlog`
- **Files**: 2
- **Purpose**: Development diagnostics and event logging
- **Key Classes**:
  - `EventLogScreen.kt` - Event log display with filtering
  - `EventLogViewModel.kt` - Event log state management

#### `network` Package
- **Package**: `uk.unmannedsystems.dpm_android.network`
- **Files**: 4
- **Purpose**: Network communication and protocol implementation
- **Key Classes**:
  - `NetworkClient.kt` - TCP/UDP client implementation
  - `NetworkManager.kt` - Singleton network manager
  - `NetworkSettings.kt` - Network configuration data models
  - `ProtocolMessages.kt` - Protocol message definitions

#### `settings` Package
- **Package**: `uk.unmannedsystems.dpm_android.settings`
- **Files**: 3
- **Purpose**: Settings management and persistence
- **Key Classes**:
  - `SettingsScreen.kt` - Settings UI with network and video configuration
  - `SettingsViewModel.kt` - Settings state management
  - `SettingsRepository.kt` - Settings persistence with DataStore

#### `system` Package
- **Package**: `uk.unmannedsystems.dpm_android.system`
- **Files**: 2
- **Purpose**: System status monitoring
- **Key Classes**:
  - `SystemStatusScreen.kt` - System status display
  - `SystemStatusViewModel.kt` - System status state management

#### `video` Package
- **Package**: `uk.unmannedsystems.dpm_android.video`
- **Files**: 2
- **Purpose**: RTSP video streaming integration
- **Key Classes**:
  - `VideoPlayerView.kt` - ExoPlayer video player composable
  - `VideoPlayerViewModel.kt` - Video player lifecycle management

#### `ui.theme` Package
- **Package**: `uk.unmannedsystems.dpm_android.ui.theme`
- **Files**: 3
- **Purpose**: Material Design 3 theme configuration
- **Key Classes**:
  - `Color.kt` - Color palette definitions
  - `Theme.kt` - Theme configuration and dark/light mode
  - `Type.kt` - Typography definitions

### 2.3 File Naming Conventions

**Consistent naming patterns throughout the codebase:**

**ViewModels:**
- Pattern: `[Feature]ViewModel.kt`
- Examples: `CameraViewModel.kt`, `SettingsViewModel.kt`, `VideoPlayerViewModel.kt`
- Location: Within feature package

**Screens:**
- Pattern: `[Feature]Screen.kt`
- Examples: `CameraControlScreen.kt`, `SettingsScreen.kt`, `SystemStatusScreen.kt`
- Location: Within feature package
- Contains: `@Composable` functions for full screen layouts

**Data Models:**
- Pattern: `[Entity]State.kt` or `[Entity]Settings.kt` or `[Entity].kt`
- Examples: `CameraState.kt`, `NetworkSettings.kt`, `ProtocolMessages.kt`
- Location: Within relevant feature package
- Contains: `data class` definitions

**Repositories:**
- Pattern: `[Feature]Repository.kt`
- Examples: `SettingsRepository.kt`
- Location: Within feature package
- Contains: Data source abstraction and persistence logic

**UI Components:**
- Pattern: `[Component].kt` or `[ComponentGroup].kt`
- Examples: `CameraButtons.kt`, `ExposureControl.kt`
- Location: `[feature].components` subpackage
- Contains: Reusable `@Composable` functions

**Application & Activity:**
- Pattern: `[Name]Application.kt`, `[Name]Activity.kt`
- Examples: `DPMApplication.kt`, `MainActivity.kt`
- Location: Root package

**Theme Files:**
- Pattern: `[Aspect].kt`
- Examples: `Color.kt`, `Theme.kt`, `Type.kt`
- Location: `ui.theme` package

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│  ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐  │
│  │  Jetpack Compose │  │  Navigation System │  │   MainActivity   │  │
│  │                  │  │                    │  │                  │  │
│  │  • CameraScreen  │  │  • Drawer Nav      │  │  • App Entry     │  │
│  │  • SettingsScreen│  │  • 5 Destinations  │  │  • Theme Setup   │  │
│  │  • StatusScreen  │  │  • State Mgmt      │  │  • Compose Host  │  │
│  │  • EventLog      │  │                    │  │                  │  │
│  └─────────┬────────┘  └─────────┬──────────┘  └────────┬─────────┘  │
│            │                     │                       │            │
│            └─────────────────────┴───────────────────────┘            │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ State Observation
                                     │ Event Callbacks
┌────────────────────────────────────▼───────────────────────────────────┐
│                         VIEWMODEL LAYER                                │
│  ┌────────────────┐  ┌───────────────┐  ┌──────────────────────────┐ │
│  │ CameraViewModel│  │SettingsVM     │  │ VideoPlayerViewModel     │ │
│  │                │  │               │  │                          │ │
│  │ • StateFlow    │  │ • StateFlow   │  │ • StateFlow<VideoState>  │ │
│  │ • Commands     │  │ • Persistence │  │ • ExoPlayer Lifecycle    │ │
│  │ • Status Obs   │  │ • Validation  │  │ • RTSP Connection        │ │
│  └───────┬────────┘  └───────┬───────┘  └────────┬─────────────────┘ │
│          │                   │                    │                   │
│  ┌───────▼────────┐  ┌───────▼───────┐  ┌────────▼─────────────────┐ │
│  │SystemStatusVM  │  │EventLogVM     │  │                          │ │
│  └───────┬────────┘  └───────┬───────┘  │   Business Logic Layer   │ │
│          │                   │          │                          │ │
└──────────┼───────────────────┼──────────┴──────────────────────────────┘
           │                   │
           │ Repository Pattern │
           │ Network Commands   │
┌──────────▼───────────────────▼───────────────────────────────────────┐
│                           DATA LAYER                                 │
│  ┌────────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ NetworkManager     │  │SettingsRepo     │  │  ExoPlayer       │ │
│  │  (Singleton)       │  │                 │  │  (Media3)        │ │
│  │                    │  │ • DataStore     │  │                  │ │
│  │ • NetworkClient    │  │ • Preferences   │  │ • RTSP Client    │ │
│  │ • TCP Port 5000    │  │ • StateFlow     │  │ • Low Latency    │ │
│  │ • UDP Port 5001    │  │                 │  │                  │ │
│  │ • UDP Port 5002    │  │                 │  │                  │ │
│  │ • StateFlow Status │  │                 │  │                  │ │
│  └──────────┬─────────┘  └─────────────────┘  └──────────────────┘ │
│             │                                                        │
└─────────────┼────────────────────────────────────────────────────────┘
              │ TCP/UDP Sockets
              │ JSON Protocol
┌─────────────▼────────────────────────────────────────────────────────┐
│                        EXTERNAL SYSTEMS                              │
│  ┌────────────────────────────┐  ┌──────────────────────────────┐   │
│  │  R16 Air Unit (Pi 4)       │  │  Video Stream                │   │
│  │  IP: 192.168.1.10          │  │  rtsp://192.168.1.10:8554/   │   │
│  │                            │  │  H264Video                   │   │
│  │  • Camera Commands         │  │                              │   │
│  │  • Status Updates (5 Hz)   │  │  • 1080p H.264               │   │
│  │  • Heartbeat (1 Hz)        │  │  • 500ms latency             │   │
│  └────────────────────────────┘  └──────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Design Patterns

#### 3.2.1 MVVM (Model-View-ViewModel)

**Implementation:**
The application strictly follows the MVVM architectural pattern, ensuring clear separation of concerns and testability.

**Pattern Components:**

**Model (Data Layer):**
- Data classes: `CameraState`, `NetworkSettings`, `VideoStreamSettings`
- Repositories: `SettingsRepository`
- Network clients: `NetworkClient`, `NetworkManager`
- Video player: `VideoPlayerViewModel` (manages ExoPlayer)

**View (Presentation Layer):**
- Jetpack Compose `@Composable` functions
- Screens: `CameraControlScreen`, `SettingsScreen`, `SystemStatusScreen`
- UI components: `CameraButtons`, `ExposureControl`
- No business logic in View layer

**ViewModel (Business Logic):**
- `CameraViewModel`, `SettingsViewModel`, `SystemStatusViewModel`
- Manages UI state via `StateFlow`
- Handles user interactions
- Communicates with repositories and network layer

**Data Flow Example:**
```kotlin
// View observes ViewModel state
@Composable
fun CameraControlScreen(
    viewModel: CameraViewModel = viewModel()
) {
    val cameraState by viewModel.cameraState.collectAsState()

    // UI displays state
    Text(text = cameraState.shutterSpeed.displayValue)

    // UI sends events to ViewModel
    Button(onClick = { viewModel.captureImage() }) {
        Text("Capture")
    }
}

// ViewModel manages state and business logic
class CameraViewModel : ViewModel() {
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    fun captureImage() {
        viewModelScope.launch {
            // Business logic
            NetworkManager.captureImage()
        }
    }
}
```

#### 3.2.2 Repository Pattern

**Purpose**: Abstract data sources and provide a clean API to ViewModels.

**Implementation:**

```kotlin
// SettingsRepository abstracts DataStore
class SettingsRepository(context: Context) {
    private val Context.dataStore: DataStore<Preferences> by preferencesDataStore("settings")

    // Expose data via Flow
    val networkSettingsFlow: Flow<NetworkSettings> = context.dataStore.data.map {
        // Transform Preferences to NetworkSettings
    }

    // Write operations
    suspend fun saveNetworkSettings(settings: NetworkSettings) {
        context.dataStore.edit { preferences ->
            preferences[TARGET_IP] = settings.targetIp
            // ... save all settings
        }
    }
}
```

**Benefits:**
- ViewModels don't need to know about DataStore implementation
- Easy to swap data sources (e.g., Room database in future)
- Centralized data transformation logic
- Testable with mock repositories

#### 3.2.3 Single Source of Truth

**Principle**: Each piece of data has exactly one source that the rest of the app observes.

**Implementation:**

**Network Status Example:**
```kotlin
// NetworkManager is the single source of truth for connection status
object NetworkManager {
    private val _connectionStatus = MutableStateFlow<NetworkStatus>(...)
    val connectionStatus: StateFlow<NetworkStatus> = _connectionStatus.asStateFlow()

    // All ViewModels observe this same StateFlow
}

// Multiple ViewModels observe the same source
class CameraViewModel {
    val networkStatus = NetworkManager.connectionStatus // Reference, not copy
}

class SettingsViewModel {
    val networkStatus = NetworkManager.connectionStatus // Same source
}
```

**Benefits:**
- No state synchronization issues
- Consistent state across the app
- Easier debugging
- Memory efficient

#### 3.2.4 Unidirectional Data Flow

**Pattern**: Data flows in one direction, events flow upward, state flows downward.

**Flow Diagram:**
```
User Interaction (Tap Button)
        ↓
Composable Function (View)
        ↓
Event Callback (onClick)
        ↓
ViewModel Function
        ↓
Business Logic / Network Call
        ↓
Update MutableStateFlow
        ↓
StateFlow Emits New Value
        ↓
Composable Observes Change
        ↓
Recomposition Triggered
        ↓
UI Updates with New State
```

**Code Example:**
```kotlin
@Composable
fun CameraScreen(viewModel: CameraViewModel = viewModel()) {
    // State flows DOWN from ViewModel to View
    val shutterSpeed by viewModel.cameraState.collectAsState()

    // Events flow UP from View to ViewModel
    Button(onClick = {
        viewModel.incrementShutterSpeed() // Event up
    }) {
        Text(shutterSpeed.displayValue) // State down
    }
}

class CameraViewModel : ViewModel() {
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    fun incrementShutterSpeed() {
        // Process event, update state
        _cameraState.update { current ->
            current.copy(shutterSpeed = /* next value */)
        }
        // Send to air-side
        NetworkManager.setCameraProperty("shutter_speed", ...)
    }
}
```

**Benefits:**
- Predictable state changes
- Easier to debug (trace events up, state down)
- Testable (mock events, verify state changes)
- Prevents circular dependencies

### 3.3 Layer Responsibilities

#### Presentation Layer (UI)

**Responsibilities:**
- Display UI using Jetpack Compose
- Observe ViewModel state via `collectAsState()`
- Handle user input (taps, gestures, text input)
- Trigger ViewModel functions based on user actions
- Navigate between screens
- No business logic or data manipulation

**Technologies:**
- Jetpack Compose
- Material Design 3
- Compose Navigation (drawer-based)
- AndroidView (for ExoPlayer integration)

**Example Screen Structure:**
```kotlin
@Composable
fun CameraControlScreen(
    viewModel: CameraViewModel = viewModel(),
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    settingsViewModel: SettingsViewModel = viewModel(),
    modifier: Modifier = Modifier
) {
    // Observe state
    val cameraState by viewModel.cameraState.collectAsState()
    val videoSettings by settingsViewModel.videoSettings.collectAsState()

    // Render UI
    Box(modifier = modifier.fillMaxSize()) {
        // Video background
        FullScreenVideoPlayer(
            videoSettings = videoSettings,
            videoPlayerViewModel = videoPlayerViewModel
        )

        // Camera controls overlay
        CameraControlsOverlay(
            cameraState = cameraState,
            onCaptureClick = viewModel::captureImage,
            onShutterChange = viewModel::incrementShutterSpeed
            // ... other callbacks
        )
    }
}
```

#### ViewModel Layer

**Responsibilities:**
- Manage UI state via `StateFlow`
- Handle business logic
- Coordinate between repositories and network layer
- Execute background operations via coroutines
- Expose state to UI layer
- Process user events from UI
- Survive configuration changes
- Clean up resources in `onCleared()`

**Technologies:**
- AndroidX ViewModel
- Kotlin Coroutines
- StateFlow / MutableStateFlow
- viewModelScope

**Example ViewModel:**
```kotlin
class CameraViewModel : ViewModel() {
    // State
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    // Observe network status
    val networkStatus = NetworkManager.connectionStatus

    // Business logic
    fun captureImage() {
        viewModelScope.launch {
            try {
                NetworkManager.captureImage()
                _cameraState.update { it.copy(isCapturing = true) }
            } catch (e: Exception) {
                // Handle error
            }
        }
    }

    fun incrementShutterSpeed() {
        _cameraState.update { current ->
            val nextValue = /* calculate next shutter speed */
            current.copy(shutterSpeed = nextValue)
        }
        // Send to air-side
        viewModelScope.launch {
            NetworkManager.setCameraProperty("shutter_speed", ...)
        }
    }

    override fun onCleared() {
        // Cleanup if needed
        super.onCleared()
    }
}
```

#### Data Layer

**Responsibilities:**
- Network communication (TCP/UDP sockets)
- Data persistence (DataStore Preferences)
- Protocol implementation (JSON serialization/deserialization)
- Video streaming (ExoPlayer/RTSP)
- Error handling and retry logic
- Expose data via Flow/StateFlow
- Abstract implementation details from ViewModels

**Components:**

**NetworkManager (Singleton):**
- Manages single `NetworkClient` instance
- Provides stable `StateFlow` for connection status
- Wrapper methods for commands

**NetworkClient:**
- TCP client for commands (port 5000)
- UDP receiver for status (port 5001)
- UDP sender for heartbeat (port 5002)
- JSON protocol handling
- Coroutine-based async operations

**SettingsRepository:**
- DataStore Preferences for settings persistence
- Exposes settings via `Flow<NetworkSettings>`
- Save/load operations

**VideoPlayerViewModel:**
- ExoPlayer lifecycle management
- RTSP connection handling
- Video state management

### 3.4 Data Flow Diagrams

#### User Action Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Taps "Capture" Button                              │
│    Location: CameraControlScreen composable                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Button's onClick Callback Invoked                       │
│    onClick = { viewModel.captureImage() }                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ViewModel Function Executes                             │
│    fun captureImage() {                                    │
│        viewModelScope.launch {                             │
│            NetworkManager.captureImage()                   │
│        }                                                   │
│    }                                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. NetworkManager Sends Command                            │
│    - Serializes command to JSON                            │
│    - Sends via TCP socket to port 5000                     │
│    - Waits for response                                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Air-Side Processes Command                              │
│    - Receives command                                      │
│    - Triggers camera shutter                               │
│    - Sends response                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Response Received                                       │
│    - NetworkClient parses JSON response                    │
│    - Updates internal state if needed                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. ViewModel Updates State (if needed)                     │
│    _cameraState.update { it.copy(lastCapture = timestamp) }│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. StateFlow Emits New Value                               │
│    cameraState: StateFlow<CameraState>                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. Composable Observes Change                              │
│    val cameraState by viewModel.cameraState.collectAsState()│
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Recomposition Triggered                                │
│     - Compose runtime detects state change                 │
│     - Recomposes affected composables                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. UI Updates                                             │
│     - New capture timestamp displayed                      │
│     - Capture animation/feedback shown                     │
└─────────────────────────────────────────────────────────────┘
```

#### Network Communication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    GROUND STATION (Android App)              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ CameraViewModel                                        │ │
│  │  - User taps capture button                           │ │
│  │  - Calls: NetworkManager.captureImage()              │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │ NetworkManager (Singleton)                            │ │
│  │  - Wrapper for NetworkClient                          │ │
│  │  - Forwards command: networkClient.captureImage()     │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │ NetworkClient                                          │ │
│  │  TCP Channel (Port 5000)                              │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 1. Create Command Message                        │ │ │
│  │  │    {                                             │ │ │
│  │  │      "message_type": "command",                  │ │ │
│  │  │      "sequence_id": 123,                         │ │ │
│  │  │      "payload": {                                │ │ │
│  │  │        "command": "camera.capture"               │ │ │
│  │  │      }                                           │ │ │
│  │  │    }                                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 2. Serialize to JSON                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 3. Send via TCP Socket                           │ │ │
│  │  │    socket.outputStream.write(jsonBytes)          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
└───────────────────────────┼──────────────────────────────────┘
                            │ TCP/IP over WiFi
                            │ 192.168.1.10:5000
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              R16 AIR UNIT (Raspberry Pi 4)                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ NetworkService (C++)                                   │ │
│  │  TCP Server (Port 5000)                               │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 4. Receive TCP Data                              │ │ │
│  │  │    accept(), read()                              │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 5. Parse JSON                                    │ │ │
│  │  │    nlohmann::json::parse()                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 6. Route to CommandHandler                       │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │ CameraService (Sony SDK)                              │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 7. Execute Command                               │ │ │
│  │  │    camera->shutter_half_press()                  │ │ │
│  │  │    camera->shutter_full_press()                  │ │ │
│  │  │    camera->shutter_release()                     │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 8. Camera Takes Photo                            │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │ NetworkService - Response                             │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 9. Create Response                               │ │ │
│  │  │    {                                             │ │ │
│  │  │      "message_type": "response",                 │ │ │
│  │  │      "sequence_id": 123,                         │ │ │
│  │  │      "payload": {                                │ │ │
│  │  │        "status": "success"                       │ │ │
│  │  │      }                                           │ │ │
│  │  │    }                                             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 10. Send Response via TCP                        │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────┬───────────────────────────────┘ │
└───────────────────────────┼──────────────────────────────────┘
                            │ TCP Response
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    GROUND STATION                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ NetworkClient                                          │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 11. Receive Response                             │ │ │
│  │  │     socket.inputStream.read()                    │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 12. Parse JSON Response                          │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ 13. Return Result to Caller                      │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### Parallel Communication Channels

```
Ground Station                        Air-Side (R16)
─────────────                        ───────────────

┌─────────────────┐                 ┌─────────────────┐
│ NetworkClient   │                 │ NetworkService  │
│                 │                 │                 │
│  TCP Port 5000  ├────────────────►│  TCP Port 5000  │
│  (Commands)     │  Command JSON   │  (Command Srv)  │
│                 │◄────────────────┤                 │
│                 │  Response JSON  │                 │
└─────────────────┘                 └─────────────────┘

┌─────────────────┐                 ┌─────────────────┐
│ UDP Listener    │                 │ StatusBroadcast │
│  Port 5001      │◄────────────────┤  Port 5001      │
│  (Status)       │  5Hz broadcasts │  (UDP Sender)   │
│                 │  Camera Status  │                 │
│                 │  System Status  │                 │
└─────────────────┘                 └─────────────────┘

┌─────────────────┐                 ┌─────────────────┐
│ UDP Heartbeat   │                 │ Heartbeat Mon   │
│  Port 5002      ├────────────────►│  Port 5002      │
│  (Send)         │  1Hz keepalive  │  (Receiver)     │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘

┌─────────────────┐                 ┌─────────────────┐
│ ExoPlayer       │                 │ RTSP Server     │
│  (Video)        │◄────────────────┤  Port 8554      │
│                 │  H.264 Stream   │  (mediamtx)     │
└─────────────────┘                 └─────────────────┘
```

---

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ **COMPLETE** |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ⏳ Pending |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ⏳ Pending |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ⏳ Pending |

**Next Action**: Run Phase 2 to continue documentation

---

**Document Metadata**

**Generated**: October 25, 2025
**Phase**: 1 of 4 (Foundation)
**Sections Complete**: 1-3
**Sections Remaining**: 15
**Est. Completion**: After Phase 4

---
