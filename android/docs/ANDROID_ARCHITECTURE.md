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

---

## 4. Core Components

### 4.1 DPMApplication

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/DPMApplication.kt`

**Purpose**: Custom Application class for app-wide initialization and lifecycle management.

**Class Structure**:
```kotlin
class DPMApplication : Application() {
    private val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    companion object {
        private const val TAG = "DPMApplication"
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "DPM Application starting...")

        // Initialize network on app startup
        applicationScope.launch {
            try {
                // Load saved settings
                val settingsRepository = SettingsRepository(this@DPMApplication)
                val savedSettings = settingsRepository.networkSettingsFlow.first()

                Log.d(TAG, "Loaded settings: ${savedSettings.targetIp}:${savedSettings.commandPort}")

                // Initialize NetworkManager with saved settings
                NetworkManager.initialize(savedSettings)

                // Auto-connect on startup
                Log.d(TAG, "Auto-connecting on app startup...")
                NetworkManager.connect()
            } catch (e: Exception) {
                Log.e(TAG, "Error initializing network on startup", e)
            }
        }
    }
}
```

**Responsibilities**:
- App-wide initialization
- Load persisted settings on startup
- Initialize NetworkManager singleton with saved settings
- Auto-connect to R16 Air Unit on app launch
- Provide application-scoped CoroutineScope for background operations
- Log application lifecycle events

**Lifecycle Management**:
- **onCreate()**: Called when app process starts
  - Creates application CoroutineScope with SupervisorJob
  - Loads settings from DataStore
  - Initializes NetworkManager
  - Triggers auto-connect
- **onTerminate()**: Not implemented (Android may not call this in production)

**Dependencies Used**:
- `SettingsRepository`: Load network settings
- `NetworkManager`: Initialize singleton with settings
- `kotlinx.coroutines`: Background operations

**Configuration**: Declared in `AndroidManifest.xml`:
```xml
<application
    android:name=".DPMApplication"
    ...>
```

### 4.2 MainActivity

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/MainActivity.kt`

**Purpose**: Main entry point and host for Jetpack Compose UI.

**Class Structure**:
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            DPMAndroidTheme {
                DPMAndroidApp()
            }
        }
    }
}
```

**Responsibilities**:
- Activity lifecycle management
- Enable edge-to-edge display
- Set up Jetpack Compose content
- Apply Material Design 3 theme
- Host navigation system

**Lifecycle Management**:
- **onCreate()**: Set up Compose UI tree
- No custom lifecycle methods needed (ViewModels handle state)
- Configuration changes handled by Compose (state survives rotation)

### 4.3 Navigation System

**Implementation**: Drawer-based navigation with enum destinations

**Code Structure**:
```kotlin
@Composable
fun DPMAndroidApp() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.CAMERA) }
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()

    ModalNavigationDrawer(
        drawerState = drawerState,
        drawerContent = {
            ModalDrawerSheet {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("DPM Android", style = MaterialTheme.typography.headlineMedium)

                    AppDestinations.entries.forEach { destination ->
                        NavigationDrawerItem(
                            icon = { Icon(destination.icon, contentDescription = destination.label) },
                            label = { Text(destination.label) },
                            selected = destination == currentDestination,
                            onClick = {
                                currentDestination = destination
                                scope.launch { drawerState.close() }
                            }
                        )
                    }
                }
            }
        }
    ) {
        Scaffold(
            floatingActionButton = {
                FloatingActionButton(onClick = { scope.launch { drawerState.open() } }) {
                    Icon(Icons.Default.Menu, contentDescription = "Menu")
                }
            }
        ) { innerPadding ->
            // Render selected destination
            when (currentDestination) {
                AppDestinations.CAMERA -> CameraControlScreen(Modifier.padding(innerPadding))
                AppDestinations.DOWNLOADS -> PlaceholderScreen(...)
                AppDestinations.SYSTEM_STATUS -> SystemStatusScreen(...)
                AppDestinations.EVENT_LOG -> EventLogScreen(...)
                AppDestinations.SETTINGS -> SettingsScreen(...)
            }
        }
    }
}

enum class AppDestinations(val label: String, val icon: ImageVector) {
    CAMERA("Camera", Icons.Default.CameraAlt),
    DOWNLOADS("Downloads", Icons.Default.Download),
    SYSTEM_STATUS("System Status", Icons.Default.Info),
    EVENT_LOG("Event Log", Icons.Default.List),
    SETTINGS("Settings", Icons.Default.Settings),
}
```

**Navigation Features**:
- Modal drawer navigation (swipe from left or tap FAB)
- 5 destination screens
- State preserved with `rememberSaveable`
- Drawer closes after selection
- Camera screen is default destination

**Navigation Flow**:
```
App Launch
    ↓
MainActivity onCreate()
    ↓
DPMAndroidApp() composable
    ↓
Default: Camera Screen
    ├→ Swipe/Tap Menu
    │   ├→ Camera (default)
    │   ├→ Downloads
    │   ├→ System Status
    │   ├→ Event Log
    │   └→ Settings
    └→ Navigate to selected screen
```

---

## 5. Data Layer

### 5.1 Data Models

The application uses strongly-typed data classes for all state management.

#### 5.1.1 CameraState

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/camera/CameraState.kt`

**Purpose**: Complete state representation of camera settings and status.

**Data Class**:
```kotlin
data class CameraState(
    val mode: CameraMode = CameraMode.MANUAL,
    val shutterSpeed: ShutterSpeed = ShutterSpeed.Speed_1_125,
    val aperture: Aperture = Aperture.F4_0,
    val iso: ISO = ISO.ISO_800,
    val exposureCompensation: Float = 0.0f,
    val whiteBalance: WhiteBalance = WhiteBalance.AUTO,
    val focusMode: FocusMode = FocusMode.AUTO,
    val fileFormat: FileFormat = FileFormat.JPEG,
    val isRecording: Boolean = false,
    val batteryLevel: Int = 100,
    val remainingShots: Int = 999,
    val isConnected: Boolean = false
)
```

**Fields**:
- `mode: CameraMode` - Shooting mode (Manual, Auto, Aperture Priority, Shutter Priority, Program)
- `shutterSpeed: ShutterSpeed` - Shutter speed (1/8000s to 30s)
- `aperture: Aperture` - F-stop value (f/1.4 to f/22)
- `iso: ISO` - ISO sensitivity (100 to 51200)
- `exposureCompensation: Float` - EV compensation (-3.0 to +3.0)
- `whiteBalance: WhiteBalance` - White balance preset
- `focusMode: FocusMode` - Focus mode (Auto, Manual, Continuous)
- `fileFormat: FileFormat` - Image format (JPEG, RAW, JPEG+RAW)
- `isRecording: Boolean` - Video recording status
- `batteryLevel: Int` - Battery percentage (0-100)
- `remainingShots: Int` - Shots remaining on SD card
- `isConnected: Boolean` - Camera connection status

**Supporting Enums**:

```kotlin
enum class ShutterSpeed(val displayValue: String, val seconds: Double) {
    Speed_1_8000("1/8000", 1.0 / 8000),
    Speed_1_4000("1/4000", 1.0 / 4000),
    // ... 19 total values from 1/8000s to 30s
    Speed_30("30\"", 30.0)
}

enum class Aperture(val displayValue: String, val fNumber: Float) {
    F1_4("1.4", 1.4f),
    F1_8("1.8", 1.8f),
    // ... 10 total values from f/1.4 to f/22
    F22_0("22", 22.0f)
}

enum class ISO(val displayValue: String, val value: Int) {
    ISO_100("100", 100),
    ISO_200("200", 200),
    // ... 10 total values from 100 to 51200
    ISO_51200("51200", 51200)
}
```

**Usage**:
- Primary state in `CameraViewModel`
- Observed by `CameraControlScreen` via `StateFlow`
- Immutable (modifications use `.copy()`)

#### 5.1.2 NetworkSettings

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkSettings.kt`

**Purpose**: Network configuration for connecting to R16 Air Unit.

**Data Class**:
```kotlin
data class NetworkSettings(
    val targetIp: String = "192.168.1.10",
    val commandPort: Int = 5000,
    val statusListenPort: Int = 5001,
    val heartbeatPort: Int = 5002,
    val connectionTimeoutMs: Long = 5000,
    val heartbeatIntervalMs: Long = 1000,
    val statusUpdateIntervalMs: Long = 200  // 5Hz
)
```

**Fields**:
- `targetIp`: R16 Air Unit IP address
- `commandPort`: TCP port for commands (5000)
- `statusListenPort`: UDP port for status broadcasts (5001)
- `heartbeatPort`: UDP port for heartbeat (5002)
- `connectionTimeoutMs`: TCP socket timeout
- `heartbeatIntervalMs`: Heartbeat send interval (1 Hz)
- `statusUpdateIntervalMs`: Expected status broadcast interval (5 Hz)

**Usage**:
- Persisted in DataStore by `SettingsRepository`
- Used by `NetworkManager` for socket configuration
- Configurable in Settings screen

#### 5.1.3 VideoStreamSettings

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkSettings.kt`

**Purpose**: Video streaming configuration for RTSP player.

**Data Class**:
```kotlin
data class VideoStreamSettings(
    val enabled: Boolean = true,
    val rtspUrl: String = "rtsp://192.168.1.10:8554/H264Video",
    val aspectRatioMode: AspectRatioMode = AspectRatioMode.FILL,
    val bufferDurationMs: Long = 500
)

enum class AspectRatioMode {
    AUTO,   // Detect from stream
    FILL,   // Fill entire screen
    FIT     // Maintain aspect ratio
}
```

**Fields**:
- `enabled`: Toggle video streaming on/off
- `rtspUrl`: RTSP stream URL
- `aspectRatioMode`: How video fills screen
- `bufferDurationMs`: ExoPlayer buffer size for low latency

**Usage**:
- Persisted in DataStore by `SettingsRepository`
- Used by `VideoPlayerViewModel` for ExoPlayer configuration
- Configurable in Settings screen

#### 5.1.4 Network Protocol Messages

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/network/ProtocolMessages.kt`

**Purpose**: JSON message structures for network protocol.

**Base Message Structure**:
```kotlin
data class BaseMessage(
    val protocolVersion: String = "1.0",
    val messageType: String,  // "handshake", "command", "response", "status", "heartbeat"
    val sequenceId: Int,
    val timestamp: Long,
    val payload: Any
)
```

**Command Payload**:
```kotlin
data class CommandPayload(
    val command: String,      // e.g., "camera.capture", "camera.set_property"
    val parameters: Map<String, Any> = emptyMap()
)
```

**Response Payload**:
```kotlin
data class ResponsePayload(
    val status: String,       // "success" or "error"
    val message: String? = null,
    val data: Map<String, Any>? = null
)
```

**Status Payload** (from UDP broadcasts):
```kotlin
data class StatusPayload(
    val camera: CameraStatusInfo,
    val system: SystemStatus
)

data class CameraStatusInfo(
    val isConnected: Boolean,
    val model: String?,
    val batteryLevel: Int,
    val remainingShots: Int,
    val isRecording: Boolean,
    val currentSettings: Map<String, Any>
)

data class SystemStatus(
    val uptimeSeconds: Long,
    val cpuUsagePercent: Float,
    val memoryUsedMb: Int,
    val memoryTotalMb: Int,
    val diskUsedGb: Float,
    val diskTotalGb: Float,
    val temperatureCelsius: Float
)
```

### 5.2 Repositories

#### 5.2.1 SettingsRepository

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsRepository.kt`

**Purpose**: Abstract settings persistence using DataStore Preferences.

**Implementation**:
```kotlin
class SettingsRepository(private val context: Context) {
    companion object {
        private const val DATASTORE_NAME = "dpm_settings"
    }

    private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(DATASTORE_NAME)

    // DataStore keys
    private val TARGET_IP = stringPreferencesKey("target_ip")
    private val COMMAND_PORT = intPreferencesKey("command_port")
    private val STATUS_PORT = intPreferencesKey("status_listen_port")
    private val HEARTBEAT_PORT = intPreferencesKey("heartbeat_port")
    private val CONNECTION_TIMEOUT = longPreferencesKey("connection_timeout_ms")
    private val HEARTBEAT_INTERVAL = longPreferencesKey("heartbeat_interval_ms")
    private val STATUS_INTERVAL = longPreferencesKey("status_update_interval_ms")

    // Video settings keys
    private val VIDEO_ENABLED = booleanPreferencesKey("video_enabled")
    private val VIDEO_RTSP_URL = stringPreferencesKey("video_rtsp_url")
    private val VIDEO_ASPECT_RATIO = stringPreferencesKey("video_aspect_ratio")
    private val VIDEO_BUFFER_DURATION = longPreferencesKey("video_buffer_duration")

    // Network settings flow
    val networkSettingsFlow: Flow<NetworkSettings> = context.dataStore.data
        .map { preferences ->
            NetworkSettings(
                targetIp = preferences[TARGET_IP] ?: "192.168.1.10",
                commandPort = preferences[COMMAND_PORT] ?: 5000,
                statusListenPort = preferences[STATUS_PORT] ?: 5001,
                heartbeatPort = preferences[HEARTBEAT_PORT] ?: 5002,
                connectionTimeoutMs = preferences[CONNECTION_TIMEOUT] ?: 5000,
                heartbeatIntervalMs = preferences[HEARTBEAT_INTERVAL] ?: 1000,
                statusUpdateIntervalMs = preferences[STATUS_INTERVAL] ?: 200
            )
        }

    // Video settings flow
    val videoSettingsFlow: Flow<VideoStreamSettings> = context.dataStore.data
        .map { preferences ->
            VideoStreamSettings(
                enabled = preferences[VIDEO_ENABLED] ?: true,
                rtspUrl = preferences[VIDEO_RTSP_URL] ?: "rtsp://192.168.1.10:8554/H264Video",
                aspectRatioMode = try {
                    AspectRatioMode.valueOf(preferences[VIDEO_ASPECT_RATIO] ?: "FILL")
                } catch (e: IllegalArgumentException) {
                    AspectRatioMode.FILL
                },
                bufferDurationMs = preferences[VIDEO_BUFFER_DURATION] ?: 500
            )
        }

    // Save network settings
    suspend fun saveNetworkSettings(settings: NetworkSettings) {
        context.dataStore.edit { preferences ->
            preferences[TARGET_IP] = settings.targetIp
            preferences[COMMAND_PORT] = settings.commandPort
            preferences[STATUS_PORT] = settings.statusListenPort
            preferences[HEARTBEAT_PORT] = settings.heartbeatPort
            preferences[CONNECTION_TIMEOUT] = settings.connectionTimeoutMs
            preferences[HEARTBEAT_INTERVAL] = settings.heartbeatIntervalMs
            preferences[STATUS_INTERVAL] = settings.statusUpdateIntervalMs
        }
    }

    // Save video settings
    suspend fun saveVideoSettings(settings: VideoStreamSettings) {
        context.dataStore.edit { preferences ->
            preferences[VIDEO_ENABLED] = settings.enabled
            preferences[VIDEO_RTSP_URL] = settings.rtspUrl
            preferences[VIDEO_ASPECT_RATIO] = settings.aspectRatioMode.name
            preferences[VIDEO_BUFFER_DURATION] = settings.bufferDurationMs
        }
    }

    // Reset to defaults
    suspend fun resetToDefaults() {
        context.dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
```

**Public API**:
- `networkSettingsFlow: Flow<NetworkSettings>` - Observable network settings
- `videoSettingsFlow: Flow<VideoStreamSettings>` - Observable video settings
- `suspend fun saveNetworkSettings(settings: NetworkSettings)` - Persist network config
- `suspend fun saveVideoSettings(settings: VideoStreamSettings)` - Persist video config
- `suspend fun resetToDefaults()` - Clear all settings

**Data Persistence Strategy**:
- Uses DataStore Preferences for key-value storage
- Type-safe keys with `Preferences` API
- Asynchronous read/write operations
- Exposes data via `Flow` for reactive updates
- Settings changes automatically propagate to observers

**Default Values**:
- Defined inline in Flow mapping
- Match production R16 Air Unit configuration
- Fallback to sensible defaults if keys missing

---

## 6. Network Layer

### 6.1 NetworkManager (Singleton)

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkManager.kt`

**Purpose**: Singleton wrapper for NetworkClient providing stable StateFlow and app-wide access.

**Implementation**:
```kotlin
object NetworkManager {
    private var networkClient: NetworkClient? = null
    private val _connectionStatus = MutableStateFlow(NetworkStatus())
    val connectionStatus: StateFlow<NetworkStatus> = _connectionStatus.asStateFlow()

    fun initialize(settings: NetworkSettings) {
        networkClient?.close()
        networkClient = NetworkClient(settings).apply {
            // Forward NetworkClient status to our stable StateFlow
            CoroutineScope(Dispatchers.Main).launch {
                connectionStatus.collect { status ->
                    _connectionStatus.value = status
                }
            }
        }
    }

    fun connect() {
        networkClient?.connect()
    }

    fun disconnect() {
        networkClient?.disconnect()
    }

    suspend fun captureImage(): Result<ResponsePayload> {
        return networkClient?.captureImage() ?: Result.failure(Exception("Not initialized"))
    }

    // ... other command methods
}
```

**Responsibilities**:
- Manage single NetworkClient instance
- Provide stable StateFlow across configuration changes
- Forward commands to NetworkClient
- Initialize with settings from repository

### 6.2 NetworkClient Implementation

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/network/NetworkClient.kt`

**Purpose**: Low-level TCP/UDP client for protocol implementation.

**Architecture**:
```
NetworkClient
    ├── TCP Socket (Port 5000)
    │   ├── Command Sender (PrintWriter)
    │   └── Response Receiver (BufferedReader)
    ├── UDP Socket (Port 5001)
    │   └── Status Listener (DatagramSocket)
    └── UDP Socket (Port 5002)
        └── Heartbeat Sender (DatagramSocket)
```

**Key Methods**:

**Connection Management**:
```kotlin
fun connect() {
    connectJob = scope.launch {
        updateConnectionState(ConnectionState.CONNECTING)
        try {
            connectTcp()               // 1. TCP socket
            sendHandshake()            // 2. Handshake protocol
            startUdpStatusListener()   // 3. UDP status receiver
            startHeartbeat()           // 4. UDP heartbeat sender
            updateConnectionState(ConnectionState.CONNECTED)
        } catch (e: Exception) {
            updateConnectionState(ConnectionState.ERROR, errorMessage = e.message)
        }
    }
}

fun disconnect() {
    sendDisconnect()
    cleanup()  // Close all sockets
    updateConnectionState(ConnectionState.DISCONNECTED)
}
```

**Command Sending (TCP)**:
```kotlin
suspend fun sendCommand(command: String, parameters: Map<String, Any> = emptyMap()): Result<ResponsePayload> {
    return withContext(Dispatchers.IO) {
        try {
            // 1. Create message
            val message = BaseMessage(
                messageType = "command",
                sequenceId = sequenceId.incrementAndGet(),
                timestamp = System.currentTimeMillis() / 1000,
                payload = CommandPayload(command, parameters)
            )

            // 2. Serialize to JSON
            val json = gson.toJson(message)

            // 3. Send via TCP
            tcpWriter?.println(json)
            tcpWriter?.flush()

            // 4. Wait for response
            val response = tcpReader?.readLine()

            // 5. Parse response
            val responseMessage = gson.fromJson(response, BaseMessage::class.java)
            val responsePayload = gson.fromJson(
                gson.toJson(responseMessage.payload),
                ResponsePayload::class.java
            )

            Result.success(responsePayload)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

**Status Listener (UDP Port 5001)**:
```kotlin
private fun startUdpStatusListener() {
    statusListenerJob = scope.launch {
        udpSocket = DatagramSocket(settings.statusListenPort)
        val buffer = ByteArray(4096)

        while (isActive) {
            val packet = DatagramPacket(buffer, buffer.size)
            udpSocket?.receive(packet)  // Block waiting for status

            val json = String(packet.data, 0, packet.length)
            val statusMessage = gson.fromJson(json, BaseMessage::class.java)
            val statusPayload = gson.fromJson(
                gson.toJson(statusMessage.payload),
                StatusPayload::class.java
            )

            // Update state flows
            _cameraStatus.value = statusPayload.camera
            _systemStatus.value = statusPayload.system
        }
    }
}
```

**Heartbeat Sender (UDP Port 5002)**:
```kotlin
private fun startHeartbeat() {
    heartbeatJob = scope.launch {
        heartbeatSocket = DatagramSocket()
        val address = InetAddress.getByName(settings.targetIp)

        while (isActive) {
            val heartbeat = BaseMessage(
                messageType = "heartbeat",
                sequenceId = sequenceId.incrementAndGet(),
                timestamp = System.currentTimeMillis() / 1000,
                payload = HeartbeatPayload(
                    sender = "ground",
                    uptimeSeconds = getUptimeSeconds()
                )
            )

            val json = gson.toJson(heartbeat)
            val bytes = json.toByteArray()
            val packet = DatagramPacket(bytes, bytes.size, address, settings.heartbeatPort)

            heartbeatSocket?.send(packet)

            delay(settings.heartbeatIntervalMs)  // 1 Hz
        }
    }
}
```

**Connection Lifecycle**:
1. `connect()` called
2. TCP socket opened to 192.168.1.10:5000
3. Handshake message sent
4. UDP listener starts on port 5001 (status broadcasts)
5. UDP heartbeat starts sending to port 5002 (1 Hz)
6. Connection state → CONNECTED
7. Status updates received at 5 Hz
8. Commands sent on-demand via TCP
9. `disconnect()` called
10. All sockets closed gracefully

**Error Handling**:
- TCP timeout: 5 seconds (configurable)
- Failed connection: Auto-retry after 2 seconds
- Socket errors: Log and update connection state
- JSON parse errors: Log and skip message
- Missing responses: Return Result.failure()

---

## 7. UI Layer

### 7.1 Jetpack Compose Architecture

**Theme System**

**Color Palette** (`ui/theme/Color.kt`):
```kotlin
// Professional camera UI - Dark theme
val CameraBlack = Color(0xFF0A0A0A)
val CameraDarkGray = Color(0xFF1A1A1A)
val CameraMediumGray = Color(0xFF2D2D2D)
val CameraLightGray = Color(0xFF808080)
val CameraTextPrimary = Color(0xFFFFFFFF)
val CameraTextSecondary = Color(0xFFB0B0B0)

// Accent colors
val CameraAccentRed = Color(0xFFE53935)      // Errors, recording
val CameraAccentOrange = Color(0xFFFF9800)   // Warnings
val CameraAccentGreen = Color(0xFF4CAF50)    // Success
val CameraAccentBlue = Color(0xFF2196F3)     // Primary actions
```

**Theme Configuration** (`ui/theme/Theme.kt`):
```kotlin
private val CameraColorScheme = darkColorScheme(
    primary = CameraAccentBlue,
    secondary = CameraAccentOrange,
    tertiary = CameraAccentGreen,
    background = CameraBlack,
    surface = CameraDarkGray,
    surfaceVariant = CameraMediumGray,
    onPrimary = CameraTextPrimary,
    onSecondary = CameraTextPrimary,
    onBackground = CameraTextPrimary,
    onSurface = CameraTextPrimary,
    error = CameraAccentRed
)

@Composable
fun DPMAndroidTheme(
    darkTheme: Boolean = true,  // Always dark for professional camera app
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = CameraColorScheme,
        typography = Typography,
        content = content
    )
}
```

**Design Rationale**:
- Always dark theme for professional camera operation
- High contrast for outdoor visibility
- Color-coded status indicators (red/orange/green/blue)
- Consistent with professional video/photo equipment UX

### 7.2 Screen Documentation

#### 7.2.1 CameraControlScreen

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/camera/CameraControlScreen.kt`

**Purpose**: Main camera control interface with live video background and overlay controls.

**Layout Structure**:
```
Box (Full Screen)
├── FullScreenVideoPlayer (Background Layer - RTSP Video)
└── Overlay Controls (Foreground Layer)
    ├── ConnectionStatusIndicator (Top-Left)
    ├── MinimizedSettings (Top-Left, below connection)
    │   ├── Shutter Speed
    │   ├── Aperture
    │   └── ISO
    ├── ExpandedSettingDialog (Center, modal)
    ├── Mode Indicator (Top-Right)
    └── Bottom Controls (Row)
        ├── Left: Quick Controls (WB, Format)
        ├── Center: Capture Button
        └── Right: Status Indicators (Battery, Shots)
```

**Code Example**:
```kotlin
@Composable
fun CameraControlScreen(
    viewModel: CameraViewModel = viewModel(),
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    settingsViewModel: SettingsViewModel = viewModel(),
    modifier: Modifier = Modifier
) {
    val cameraState by viewModel.cameraState.collectAsState()
    val videoSettings by settingsViewModel.videoSettings.collectAsState()
    var expandedSetting by rememberSaveable { mutableStateOf(ExpandedSetting.NONE) }

    Box(modifier = modifier.fillMaxSize()) {
        // Full-screen video background
        FullScreenVideoPlayer(
            videoSettings = videoSettings,
            videoPlayerViewModel = videoPlayerViewModel,
            modifier = Modifier.fillMaxSize()
        )

        // Connection indicator
        ConnectionStatusIndicator(
            isConnected = cameraState.isConnected,
            onClick = { if (cameraState.isConnected) viewModel.disconnect() else viewModel.connect() },
            modifier = Modifier.align(Alignment.TopStart)
        )

        // Camera controls overlay...
    }
}
```

**User Interactions**:
- Tap **Capture Button** → `viewModel.captureImage()`
- Tap **Shutter/Aperture/ISO** → Expand setting dialog
- Tap **+/-** in dialog → Increment/decrement value
- Tap **Connection Indicator** → Connect/disconnect
- Tap **Mode Indicator** → Future: Show mode selector

**State Observation**:
```kotlin
val cameraState by viewModel.cameraState.collectAsState()
// Automatically recomposes when state changes
```

#### 7.2.2 SettingsScreen

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsScreen.kt`

**Purpose**: Configure network and video streaming settings.

**Features**:
- Network settings (IP, ports, timeouts)
- Video streaming toggle and RTSP URL
- Aspect ratio selection
- Save/Reset buttons
- Connection controls

**Layout**: Vertical scrollable form with TextField inputs and dropdowns.

#### 7.2.3 SystemStatusScreen

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/system/SystemStatusScreen.kt`

**Purpose**: Display real-time system telemetry from R16 Air Unit.

**Displays**:
- System uptime
- CPU usage percentage
- Memory used/total
- Storage used/total
- Temperature
- Manual refresh button

**Data Source**: UDP status broadcasts parsed by NetworkClient.

### 7.3 Reusable Components

#### FullScreenVideoPlayer

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/video/VideoPlayerView.kt`

**Purpose**: RTSP video player with state overlays.

**Parameters**:
```kotlin
@Composable
fun FullScreenVideoPlayer(
    videoSettings: VideoStreamSettings,
    videoPlayerViewModel: VideoPlayerViewModel = viewModel(),
    modifier: Modifier = Modifier
)
```

**Features**:
- ExoPlayer embedded via AndroidView
- Low-latency RTSP streaming
- State overlays: Disconnected, Connecting, Error, Connected, Disabled
- Aspect ratio modes (FILL, FIT, AUTO)
- Automatic lifecycle management

**Usage**:
```kotlin
FullScreenVideoPlayer(
    videoSettings = videoSettings,
    videoPlayerViewModel = videoPlayerViewModel,
    modifier = Modifier.fillMaxSize()
)
```

#### Camera UI Components

**CameraButtons** (`camera/components/CameraButtons.kt`):
- ControlButton - Generic button with label
- CaptureButton - Large circular capture button
- StatusIndicator - Icon + value display
- ModeSelector - Camera mode picker

**ExposureControl** (`camera/components/ExposureControl.kt`):
- Exposure adjustment dial with +/- buttons
- Large value display
- Increment/decrement callbacks

---

## 8. State Management

### 8.1 State Flow Architecture

The application uses **Kotlin StateFlow** for reactive state management, following these principles:

**Key Principles:**
1. **Single Source of Truth**: Each piece of state has exactly one owner
2. **Unidirectional Data Flow**: Events up, state down
3. **Immutable State**: State objects are immutable `data class` instances
4. **Reactive Updates**: UI automatically recomposes when state changes
5. **Lifecycle Aware**: StateFlow respects lifecycle, preventing leaks

**State Flow Pattern:**
```
User Action (UI Event)
    ↓
Composable calls ViewModel function
    ↓
ViewModel updates MutableStateFlow
    ↓
    _state.update { current -> current.copy(field = newValue) }
    ↓
StateFlow emits new value
    ↓
Composable observes via collectAsState()
    ↓
Compose runtime detects change
    ↓
Recomposition triggered
    ↓
UI displays updated state
```

**StateFlow vs LiveData:**
- **StateFlow**: Kotlin Coroutines-based, better with Compose, type-safe, always has a value
- **LiveData**: Android-specific, lifecycle-aware but older technology
- **Decision**: StateFlow chosen for modern Kotlin-first approach with Jetpack Compose

**Implementation Pattern:**
```kotlin
class ExampleViewModel : ViewModel() {
    // Private mutable state (internal)
    private val _state = MutableStateFlow(InitialState())

    // Public immutable state (exposed to UI)
    val state: StateFlow<InitialState> = _state.asStateFlow()

    // Update state immutably
    fun updateValue(newValue: String) {
        _state.update { current ->
            current.copy(value = newValue)
        }
    }
}
```

### 8.2 ViewModels Documentation

The application uses 5 primary ViewModels for state management.

#### 8.2.1 CameraViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/camera/CameraViewModel.kt`

**Purpose**: Manages all camera state and controls, coordinates with NetworkManager for sending commands to R16 Air Unit.

**State Objects:**
```kotlin
private val _cameraState = MutableStateFlow(CameraState())
val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()
```

**Initialization:**
```kotlin
init {
    // Monitor network connection status from shared NetworkManager
    viewModelScope.launch {
        NetworkManager.connectionStatus.collect { networkStatus ->
            _cameraState.update { state ->
                state.copy(
                    isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                 networkStatus.state == ConnectionState.OPERATIONAL
                )
            }
        }
    }
}
```

**Public API (18 functions):**

**Shutter Speed Control:**
```kotlin
fun incrementShutterSpeed() {
    _cameraState.update { state ->
        val currentOrdinal = state.shutterSpeed.ordinal
        val newOrdinal = (currentOrdinal - 1).coerceAtLeast(0)
        val newShutterSpeed = ShutterSpeed.fromOrdinal(newOrdinal)

        // Send command to air-side
        sendPropertyCommand("shutter_speed", shutterSpeedToProtocol(newShutterSpeed))

        state.copy(shutterSpeed = newShutterSpeed)
    }
}

fun decrementShutterSpeed()  // Similar pattern, increment ordinal
```

**Aperture Control:**
```kotlin
fun incrementAperture()     // Wider aperture (smaller f-number)
fun decrementAperture()     // Narrower aperture (larger f-number)
```

**ISO Control:**
```kotlin
fun incrementISO()          // More sensitive
fun decrementISO()          // Less sensitive
```

**Exposure Compensation:**
```kotlin
fun adjustExposureCompensation(delta: Float) {
    _cameraState.update { state ->
        val newValue = (state.exposureCompensation + delta).coerceIn(-3.0f, 3.0f)
        state.copy(exposureCompensation = newValue)
    }
}
```

**Mode and Settings:**
```kotlin
fun setMode(mode: CameraMode)                      // Manual, Auto, Av, Tv, P
fun setWhiteBalance(whiteBalance: WhiteBalance)    // Auto, Daylight, Cloudy, etc.
fun setFileFormat(format: FileFormat)              // JPEG, RAW, JPEG+RAW
fun setFocusMode(mode: FocusMode)                  // Auto, Manual, Continuous
fun toggleRecording()                               // Toggle video recording
```

**Camera Commands:**
```kotlin
fun captureImage() {
    viewModelScope.launch {
        try {
            Log.d(TAG, "Triggering camera capture...")
            val result = NetworkManager.getClient()?.captureImage()
            result?.fold(
                onSuccess = { response ->
                    Log.d(TAG, "Capture successful: ${response.status}")
                },
                onFailure = { error ->
                    Log.e(TAG, "Capture failed", error)
                }
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error sending capture command", e)
        }
    }
}
```

**Connection Control:**
```kotlin
fun connect()               // Delegate to NetworkManager
fun disconnect()            // Delegate to NetworkManager
```

**Protocol Conversion Helpers (Private):**
```kotlin
private fun shutterSpeedToProtocol(shutter: ShutterSpeed): String
    // Converts ShutterSpeed.Speed_1_125 → "1/125"

private fun apertureToProtocol(aperture: Aperture): String
    // Converts Aperture.F4_0 → "f/4.0"

private fun isoToProtocol(iso: ISO): String
    // Converts ISO.ISO_800 → "800"

private fun whiteBalanceToProtocol(wb: WhiteBalance): String
    // Converts WhiteBalance.DAYLIGHT → "daylight"

private fun focusModeToProtocol(mode: FocusMode): String
    // Converts FocusMode.AUTO → "af_s"

private fun fileFormatToProtocol(format: FileFormat): String
    // Converts FileFormat.JPEG → "jpeg"
```

**Property Command Sending:**
```kotlin
private fun sendPropertyCommand(property: String, value: String) {
    viewModelScope.launch {
        try {
            Log.d(TAG, "Setting camera property: $property = $value")
            val result = NetworkManager.getClient()?.setCameraProperty(property, value)
            result?.fold(
                onSuccess = { response ->
                    Log.d(TAG, "Property set successfully: $property = $value")
                },
                onFailure = { error ->
                    Log.e(TAG, "Failed to set property: $property = $value", error)
                }
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error sending property command", e)
        }
    }
}
```

**State Management Pattern:**
- **Optimistic Updates**: UI updates immediately, then sends command to air-side
- **Fire-and-Forget**: Property commands don't wait for confirmation (status broadcasts provide feedback)
- **Error Logging**: All failures logged but don't revert state (air-side status will correct)

**Dependencies:**
- `NetworkManager`: Send commands, observe connection status
- `viewModelScope`: Coroutine scope for network operations

**Lifecycle:**
- **Initialization**: Starts observing NetworkManager.connectionStatus
- **Cleanup**: viewModelScope automatically cancelled in onCleared()

**Threading:**
- All network operations run in `viewModelScope.launch` (background threads)
- State updates safe from any thread (StateFlow is thread-safe)
- UI observation happens on main thread via `collectAsState()`

**Error Handling:**
- Network errors: Logged, no state revert
- Connection failures: Handled by NetworkManager
- Invalid values: Prevented by `coerceIn()` and `coerceAtLeast()`/`coerceAtMost()`

#### 8.2.2 SettingsViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/settings/SettingsViewModel.kt`

**Purpose**: Manages network and video settings, persists configuration via SettingsRepository.

**State Objects:**
```kotlin
val networkSettings: StateFlow<NetworkSettings> = settingsRepository.networkSettingsFlow
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = NetworkSettings()
    )

val videoSettings: StateFlow<VideoStreamSettings> = settingsRepository.videoSettingsFlow
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = VideoStreamSettings()
    )

val networkStatus: StateFlow<NetworkStatus> = NetworkManager.connectionStatus
```

**Public API:**
```kotlin
fun updateSettings(settings: NetworkSettings) {
    viewModelScope.launch {
        // Disconnect if currently connected
        NetworkManager.disconnect()

        // Save settings to DataStore (will trigger flow and reinitialize)
        settingsRepository.saveNetworkSettings(settings)
    }
}

fun updateVideoSettings(settings: VideoStreamSettings) {
    viewModelScope.launch {
        settingsRepository.saveVideoSettings(settings)
    }
}

fun resetToDefaults() {
    viewModelScope.launch {
        settingsRepository.resetToDefaults()
        // Settings will be updated via the flow which will reinitialize NetworkManager
    }
}

fun connect() {
    NetworkManager.connect()
}

fun disconnect() {
    NetworkManager.disconnect()
}
```

**Initialization:**
```kotlin
init {
    // Monitor settings changes and reinitialize NetworkManager when settings change
    viewModelScope.launch {
        settingsRepository.networkSettingsFlow.collect { savedSettings ->
            // Reinitialize NetworkManager when settings change
            NetworkManager.initialize(savedSettings)
        }
    }
}
```

**Pattern: Settings Flow**
- Settings flow from repository (backed by DataStore)
- UI observes settings via StateFlow
- Save operation triggers DataStore update
- DataStore update triggers Flow emission
- Flow emission triggers NetworkManager re-initialization
- Automatic propagation throughout app

**Dependencies:**
- `SettingsRepository`: Read/write settings
- `NetworkManager`: Re-initialize on settings change

#### 8.2.3 SystemStatusViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/system/SystemStatusViewModel.kt`

**Purpose**: Displays real-time system telemetry from R16 Air Unit, supports manual refresh.

**State Objects:**
```kotlin
private val _uiState = MutableStateFlow(SystemStatusUiState())
val uiState: StateFlow<SystemStatusUiState> = _uiState.asStateFlow()

data class SystemStatusUiState(
    val isConnected: Boolean = false,
    val systemStatus: SystemStatus? = null,
    val isRefreshing: Boolean = false,
    val lastRefreshTime: Long? = null,
    val errorMessage: String? = null
)
```

**Public API:**
```kotlin
fun refreshSystemStatus() {
    viewModelScope.launch {
        _uiState.update { it.copy(isRefreshing = true, errorMessage = null) }

        val result = NetworkManager.getSystemStatus()

        result.fold(
            onSuccess = { response ->
                _uiState.update { state ->
                    state.copy(
                        isRefreshing = false,
                        lastRefreshTime = System.currentTimeMillis()
                    )
                }
            },
            onFailure = { error ->
                _uiState.update { state ->
                    state.copy(
                        isRefreshing = false,
                        errorMessage = "Failed to refresh: ${error.message}"
                    )
                }
            }
        )
    }
}

fun connect()              // Delegate to NetworkManager
fun disconnect()           // Delegate to NetworkManager
fun clearError()           // Clear error message from UI state
```

**Initialization:**
```kotlin
init {
    // Monitor network connection status
    viewModelScope.launch {
        NetworkManager.connectionStatus.collect { networkStatus ->
            _uiState.update { state ->
                state.copy(
                    isConnected = networkStatus.state == ConnectionState.CONNECTED ||
                                 networkStatus.state == ConnectionState.OPERATIONAL
                )
            }
        }
    }

    // Monitor system status updates from UDP broadcasts (5 Hz)
    viewModelScope.launch {
        NetworkManager.systemStatus.collect { systemStatus ->
            _uiState.update { state ->
                state.copy(systemStatus = systemStatus)
            }
        }
    }
}
```

**Pattern: Dual Data Source**
- **Automatic Updates**: UDP broadcasts at 5 Hz (passive observation)
- **Manual Refresh**: User-triggered TCP command (active request)
- **Error Handling**: Shows error in UI, doesn't block automatic updates

#### 8.2.4 EventLogViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/eventlog/EventLogViewModel.kt`

**Purpose**: Application-wide event logging for development diagnostics.

**Pattern: Singleton ViewModel**
```kotlin
object EventLogViewModel : ViewModel() {
    // Singleton pattern allows logging from anywhere in the app
}
```

**State Objects:**
```kotlin
private val _events = MutableStateFlow<List<EventLogEntry>>(emptyList())
val events: StateFlow<List<EventLogEntry>> = _events.asStateFlow()

private val maxEvents = 1000 // Keep last 1000 events

data class EventLogEntry(
    val timestamp: Long = System.currentTimeMillis(),
    val category: EventCategory,
    val level: EventLevel,
    val message: String,
    val details: String? = null
)

enum class EventCategory {
    NETWORK, CAMERA, UI, SYSTEM, ERROR
}

enum class EventLevel {
    DEBUG, INFO, WARNING, ERROR
}
```

**Public API:**
```kotlin
fun logEvent(
    category: EventCategory,
    level: EventLevel,
    message: String,
    details: String? = null
) {
    val event = EventLogEntry(
        timestamp = System.currentTimeMillis(),
        category = category,
        level = level,
        message = message,
        details = details
    )

    _events.value = (_events.value + event).takeLast(maxEvents)
}

fun clearLog()

fun getEventsByCategory(category: EventCategory): List<EventLogEntry>
fun getEventsByLevel(level: EventLevel): List<EventLogEntry>

// Convenience functions
fun logDebug(category: EventCategory, message: String, details: String? = null)
fun logInfo(category: EventCategory, message: String, details: String? = null)
fun logWarning(category: EventCategory, message: String, details: String? = null)
fun logError(category: EventCategory, message: String, details: String? = null)
```

**Usage From Anywhere:**
```kotlin
// From any class in the app
EventLogViewModel.logInfo(EventCategory.NETWORK, "Connection established")
EventLogViewModel.logError(EventCategory.CAMERA, "Capture failed", "Timeout after 5s")
```

**Pattern: Circular Buffer**
- Keeps last 1000 events
- Automatic truncation with `.takeLast(maxEvents)`
- Memory-efficient for long-running app

#### 8.2.5 VideoPlayerViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/video/VideoPlayerViewModel.kt`

**Purpose**: Manages ExoPlayer lifecycle for RTSP video streaming.

**State Objects:**
```kotlin
private val _videoState = MutableStateFlow<VideoState>(VideoState.Disconnected)
val videoState: StateFlow<VideoState> = _videoState.asStateFlow()

sealed class VideoState {
    object Disconnected : VideoState()
    object Connecting : VideoState()
    data class Connected(val resolution: String = "Unknown") : VideoState()
    data class Error(val message: String) : VideoState()
}
```

**Public API:**
```kotlin
fun initializePlayer(context: Context, rtspUrl: String, bufferDurationMs: Long = 500)
fun releasePlayer()
fun reconnect(context: Context, rtspUrl: String, bufferDurationMs: Long = 500)
fun getPlayer(): ExoPlayer?
```

**Lifecycle Management:**
```kotlin
override fun onCleared() {
    super.onCleared()
    Log.d(TAG, "ViewModel cleared, releasing player")
    releasePlayer()
}
```

**Pattern: Resource Management**
- Creates/manages ExoPlayer instance
- Handles RTSP connection
- Cleans up on ViewModel clear
- State updates via Player.Listener callbacks

*See Section 9 for detailed video streaming documentation.*

### 8.3 State Objects Reference

Complete list of all state data classes used in ViewModels:

#### CameraState
**Location**: `camera/CameraState.kt`
**Fields**: 12 fields (mode, shutterSpeed, aperture, iso, exposureCompensation, whiteBalance, focusMode, fileFormat, isRecording, batteryLevel, remainingShots, isConnected)
**Usage**: Primary state in CameraViewModel
**Mutability**: Immutable, updated with `.copy()`

#### NetworkSettings
**Location**: `network/NetworkSettings.kt`
**Fields**: 7 fields (targetIp, commandPort, statusListenPort, heartbeatPort, connectionTimeoutMs, heartbeatIntervalMs, statusUpdateIntervalMs)
**Usage**: Configuration state in SettingsViewModel
**Persistence**: DataStore via SettingsRepository

#### VideoStreamSettings
**Location**: `network/NetworkSettings.kt`
**Fields**: 4 fields (enabled, rtspUrl, aspectRatioMode, bufferDurationMs)
**Usage**: Video configuration in SettingsViewModel
**Persistence**: DataStore via SettingsRepository

#### SystemStatusUiState
**Location**: `system/SystemStatusViewModel.kt`
**Fields**: 5 fields (isConnected, systemStatus, isRefreshing, lastRefreshTime, errorMessage)
**Usage**: UI state in SystemStatusViewModel
**Pattern**: Wrapper around SystemStatus from NetworkManager

#### EventLogEntry
**Location**: `eventlog/EventLogViewModel.kt`
**Fields**: 5 fields (timestamp, category, level, message, details)
**Usage**: Log entries in EventLogViewModel
**Pattern**: Immutable log records

#### VideoState (Sealed Class)
**Location**: `video/VideoPlayerViewModel.kt`
**Variants**: Disconnected, Connecting, Connected(resolution), Error(message)
**Usage**: Video player state in VideoPlayerViewModel
**Pattern**: Type-safe state machine

### 8.4 State Update Patterns

**Pattern 1: Direct Update**
```kotlin
fun updateValue(newValue: String) {
    _state.update { it.copy(value = newValue) }
}
```

**Pattern 2: Computed Update**
```kotlin
fun increment() {
    _state.update { current ->
        val newValue = current.value + 1
        current.copy(value = newValue)
    }
}
```

**Pattern 3: Update with Side Effect**
```kotlin
fun updateAndSync(newValue: String) {
    _state.update { it.copy(value = newValue) }

    viewModelScope.launch {
        sendToAirSide(newValue)
    }
}
```

**Pattern 4: Observing Other StateFlows**
```kotlin
init {
    viewModelScope.launch {
        otherViewModel.state.collect { otherState ->
            _state.update { it.copy(relatedValue = otherState.value) }
        }
    }
}
```

---

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ Complete |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ✅ Complete |
| **Phase 3** | 8: State Management | ✅ **COMPLETE** |
| **Phase 3** | 9-11: Video Streaming, Navigation, Dependencies | ⏳ Pending |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ⏳ Pending |

**Next Action**: Continue Phase 3 with Sections 9-11

---

**Document Metadata**

**Generated**: October 25, 2025
**Phase**: 3 of 4 (In Progress - Section 8 Complete)
**Sections Complete**: 1-8
**Sections Remaining**: 10
**Est. Completion**: After Phase 4

---
