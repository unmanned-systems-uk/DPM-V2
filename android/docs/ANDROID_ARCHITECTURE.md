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

## 9. Video Streaming Implementation

### 9.1 RTSP Streaming Architecture

The Android app implements real-time video streaming using **RTSP (Real-Time Streaming Protocol)** with ExoPlayer (Media3) as the playback engine. The architecture provides low-latency video display for drone camera operation.

**Key Components**:
1. **VideoPlayerViewModel**: Manages ExoPlayer lifecycle and connection state
2. **FullScreenVideoPlayer**: Jetpack Compose UI for video display
3. **VideoStreamSettings**: Configuration data class for stream parameters
4. **ExoPlayer (Media3)**: Android's recommended media player with RTSP support

**RTSP Stream Configuration**:
- **Default URL**: `rtsp://{groundStationIp}:8554/H264Video`
- **Port**: 8554 (RTSP standard)
- **Video Codec**: H.264
- **Transport**: UDP (for low latency)
- **Buffer Duration**: 500ms (configurable for latency optimization)

**Video Flow**:
```
Air-Side Camera → RTSP Server (Live555) → Network → Android ExoPlayer → Display
```

**Integration Points**:
- Settings screen provides RTSP URL configuration
- CameraControlScreen displays full-screen video background
- VideoPlayerViewModel coordinates with NetworkManager for connection status

---

### 9.2 VideoPlayerViewModel

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/video/VideoPlayerViewModel.kt`

**Purpose**: Manages ExoPlayer lifecycle, RTSP connection, and video playback state.

#### 9.2.1 Initialization

```kotlin
class VideoPlayerViewModel : ViewModel() {
    private val _videoState = MutableStateFlow<VideoState>(VideoState.Disconnected)
    val videoState: StateFlow<VideoState> = _videoState.asStateFlow()

    private var exoPlayer: ExoPlayer? = null
}
```

#### 9.2.2 Video State Machine

**Sealed Class Hierarchy**:
```kotlin
sealed class VideoState {
    object Disconnected : VideoState()
    object Connecting : VideoState()
    data class Connected(val resolution: String = "Unknown") : VideoState()
    data class Error(val message: String) : VideoState()
}
```

**State Transitions**:
```
Disconnected → Connecting (initializePlayer called)
Connecting → Connected (ExoPlayer STATE_READY)
Connecting → Buffering → Connected (ExoPlayer STATE_BUFFERING → STATE_READY)
Any → Error (PlaybackException)
Any → Disconnected (releasePlayer called)
```

#### 9.2.3 Public API

**Primary Functions**:

1. **`initializePlayer(context: Context, rtspUrl: String, bufferDurationMs: Long = 500)`**
   - Initializes ExoPlayer with low-latency configuration
   - Creates RTSP MediaItem from URL
   - Configures buffer durations for minimal latency
   - Starts automatic playback
   - **Default Buffer**: 500ms (configurable via settings)

2. **`releasePlayer()`**
   - Releases ExoPlayer resources
   - Cleans up media streams
   - Transitions to Disconnected state

3. **`reconnect(context: Context, rtspUrl: String, bufferDurationMs: Long = 500)`**
   - Convenience function for reconnection after errors
   - Calls `releasePlayer()` then `initializePlayer()`

4. **`getPlayer(): ExoPlayer?`**
   - Returns ExoPlayer instance for PlayerView binding
   - Used by FullScreenVideoPlayer composable

#### 9.2.4 Low-Latency Configuration

**Buffer Strategy**:
```kotlin
val loadControl = DefaultLoadControl.Builder()
    .setBufferDurationsMs(
        bufferDurationMs.toInt(),          // Min buffer: 500ms
        (bufferDurationMs * 2).toInt(),    // Max buffer: 1000ms
        (bufferDurationMs / 2).toInt(),    // Playback start: 250ms
        bufferDurationMs.toInt()           // Rebuffer: 500ms
    )
    .build()
```

**Design Rationale**:
- **Minimum Buffer (500ms)**: Balances latency vs. stability
- **Maximum Buffer (1000ms)**: Prevents excessive buffering delays
- **Playback Start (250ms)**: Quick startup for responsive feel
- **Rebuffer (500ms)**: Fast recovery from network jitter

**Trade-offs**:
- Lower buffers = lower latency but more stuttering
- Higher buffers = smoother playback but higher latency
- Current settings optimized for WiFi local network (5GHz recommended)

#### 9.2.5 ExoPlayer Listener Implementation

**Player.Listener Callbacks**:
```kotlin
addListener(object : Player.Listener {
    override fun onPlaybackStateChanged(playbackState: Int) {
        when (playbackState) {
            Player.STATE_READY -> {
                val videoFormat = this@apply.videoFormat
                val resolution = "${videoFormat?.width}x${videoFormat?.height}"
                _videoState.value = VideoState.Connected(resolution)
            }
            Player.STATE_BUFFERING -> {
                _videoState.value = VideoState.Connecting
            }
            Player.STATE_ENDED -> { /* RTSP streams don't typically end */ }
            Player.STATE_IDLE -> { /* Initial state */ }
        }
    }

    override fun onPlayerError(error: PlaybackException) {
        _videoState.value = VideoState.Error(error.message ?: "Unknown error")
    }
})
```

**State Tracking**:
- `STATE_READY`: Extracts video resolution (e.g., "1920x1080")
- `STATE_BUFFERING`: Shows loading indicator to user
- `onPlayerError`: Displays error message with troubleshooting hint

#### 9.2.6 Lifecycle Management

**ViewModel Cleanup**:
```kotlin
override fun onCleared() {
    super.onCleared()
    Log.d(TAG, "ViewModel cleared, releasing player")
    releasePlayer()
}
```

**Integration with Compose**:
- ViewModel scoped to Activity (survives configuration changes)
- Player resources released when Activity destroyed
- Automatic cleanup prevents memory leaks

---

### 9.3 FullScreenVideoPlayer Composable

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/video/VideoPlayerView.kt`

**Purpose**: Jetpack Compose UI for full-screen RTSP video with overlay states.

#### 9.3.1 Component Structure

```kotlin
@Composable
fun FullScreenVideoPlayer(
    videoSettings: VideoStreamSettings,
    modifier: Modifier = Modifier,
    videoPlayerViewModel: VideoPlayerViewModel = viewModel()
) {
    val context = LocalContext.current
    val videoState by videoPlayerViewModel.videoState.collectAsState()

    // Player initialization
    LaunchedEffect(videoSettings.rtspUrl, videoSettings.bufferDurationMs) {
        if (videoSettings.enabled) {
            videoPlayerViewModel.initializePlayer(...)
        }
    }

    // Player cleanup
    DisposableEffect(Unit) {
        onDispose { videoPlayerViewModel.releasePlayer() }
    }

    // UI rendering
    Box { /* Video + Overlays */ }
}
```

#### 9.3.2 LaunchedEffect for Initialization

**Purpose**: Initialize player when settings change or composable enters composition.

**Key Behavior**:
- Triggers on `videoSettings.rtspUrl` or `videoSettings.bufferDurationMs` change
- Only initializes if `videoSettings.enabled == true`
- Automatically reconnects if RTSP URL changes in settings

**Use Case**: User changes Ground Station IP → new RTSP URL → auto-reconnect

#### 9.3.3 DisposableEffect for Cleanup

**Purpose**: Release player resources when composable leaves composition.

**Key Behavior**:
- `onDispose` called when composable removed from tree
- Releases ExoPlayer to prevent memory leaks
- Stops network streams and frees buffers

**Use Case**: User navigates away from camera screen → player released

#### 9.3.4 AndroidView Integration

**PlayerView Setup**:
```kotlin
AndroidView(
    factory = { context ->
        PlayerView(context).apply {
            player = videoPlayerViewModel.getPlayer()
            useController = false  // Hide default playback controls
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )

            resizeMode = when (videoSettings.aspectRatioMode) {
                AspectRatioMode.FILL -> AspectRatioFrameLayout.RESIZE_MODE_FILL
                AspectRatioMode.FIT -> AspectRatioFrameLayout.RESIZE_MODE_FIT
                AspectRatioMode.AUTO -> AspectRatioFrameLayout.RESIZE_MODE_FIT
            }
        }
    },
    update = { playerView ->
        playerView.player = videoPlayerViewModel.getPlayer()
        playerView.resizeMode = /* updated from settings */
    }
)
```

**Design Decisions**:
- **`useController = false`**: Camera controls overlay provides UI (no need for play/pause)
- **Resize Modes**:
  - `FILL`: Crop video to fill screen (may cut off edges)
  - `FIT`: Letterbox/pillarbox to show entire video
  - `AUTO`: Intelligent fit based on video dimensions

#### 9.3.5 Overlay States

**State-Driven UI**:
```kotlin
when (val state = videoState) {
    is VideoState.Disconnected -> DisconnectedOverlay()
    is VideoState.Connecting -> ConnectingOverlay()
    is VideoState.Error -> ErrorOverlay(errorMessage = state.message)
    is VideoState.Connected -> { /* No overlay - video visible */ }
}
```

**Overlay Components**:

1. **DisconnectedOverlay**
   - Black background with white text
   - Message: "Video Disconnected / Waiting for stream..."
   - Shown when: Not yet connected or after disconnect

2. **ConnectingOverlay**
   - Semi-transparent black (alpha = 0.7f)
   - CircularProgressIndicator + "Connecting to video stream..."
   - Shown when: Buffering or establishing RTSP connection

3. **ErrorOverlay**
   - Black background
   - Red "Video Error" title
   - Error message from PlaybackException
   - Troubleshooting hint: "Check network connection and RTSP URL in settings"

4. **VideoDisabledOverlay**
   - Black background
   - Message: "Video Stream Disabled / Enable video in Settings to view stream"
   - Shown when: `videoSettings.enabled == false`

**User Experience Flow**:
```
App Start → Disconnected Overlay
  ↓
User Taps "Connect" → Connecting Overlay (spinner)
  ↓
RTSP Connection Success → Connected State (video visible, no overlay)
```

#### 9.3.6 Aspect Ratio Handling

**AspectRatioMode Enum** (from `VideoStreamSettings`):
```kotlin
enum class AspectRatioMode {
    FILL,   // Crop to fill screen
    FIT,    // Letterbox/pillarbox
    AUTO    // Intelligent fit
}
```

**Mapping to ExoPlayer**:
- `FILL` → `AspectRatioFrameLayout.RESIZE_MODE_FILL`
- `FIT` → `AspectRatioFrameLayout.RESIZE_MODE_FIT`
- `AUTO` → `AspectRatioFrameLayout.RESIZE_MODE_FIT` (defaults to FIT)

**Use Cases**:
- **FILL**: Maximize screen usage, accept cropping (e.g., landscape video on landscape screen)
- **FIT**: See entire video frame, accept black bars (e.g., 4:3 video on 16:9 screen)

---

### 9.4 Video Stream Settings

**Data Class** (from Section 5 - Data Layer):
```kotlin
data class VideoStreamSettings(
    val enabled: Boolean = true,
    val rtspUrl: String = "rtsp://192.168.1.10:8554/H264Video",
    val bufferDurationMs: Long = 500,
    val aspectRatioMode: AspectRatioMode = AspectRatioMode.FIT
)
```

**Configuration Management**:
- Stored in DataStore Preferences via SettingsRepository
- Exposed through SettingsViewModel as StateFlow
- User-configurable in Settings screen

**Settings UI Integration** (SettingsScreen.kt):
- Ground Station IP → updates RTSP URL
- Video Enable/Disable toggle
- Buffer duration slider (100ms - 2000ms)
- Aspect ratio mode selector

**Dynamic URL Construction**:
```kotlin
val rtspUrl = "rtsp://${groundStationIp}:8554/H264Video"
```

**Example URLs**:
- Development: `rtsp://192.168.1.10:8554/H264Video`
- Testing: `rtsp://10.0.0.5:8554/H264Video`
- Production: `rtsp://<drone-ip>:8554/H264Video`

---

### 9.5 Performance Optimization

#### 9.5.1 Latency Optimization

**Target Latency**: < 1 second end-to-end (camera → screen)

**Optimizations Implemented**:
1. **Low Buffer Durations**: 500ms minimum (vs. default 15s+)
2. **UDP Transport**: RTSP over UDP for speed (vs. TCP reliability)
3. **H.264 Codec**: Hardware-accelerated decoding on Android
4. **Direct Rendering**: ExoPlayer → SurfaceView (no CPU copy)
5. **No Frame Buffering**: Immediate display when ready

**Latency Breakdown** (estimated):
- Camera encoding: 50-100ms
- Network transmission: 10-50ms (WiFi 5GHz)
- ExoPlayer buffering: 500ms (configurable)
- Rendering: 16-33ms (60fps / 30fps)
- **Total**: ~600-700ms

**Further Optimization Opportunities**:
- Reduce buffer to 200ms (may cause stuttering)
- Use WebRTC instead of RTSP (< 200ms possible)
- Hardware encoder on air-side for lower encoding latency

#### 9.5.2 Network Performance

**WiFi Recommendations**:
- **Band**: 5GHz (less congestion than 2.4GHz)
- **Bandwidth**: 10-20 Mbps for 1080p H.264
- **Range**: < 50m for stable connection
- **Channel**: Non-overlapping (36, 40, 44, 48)

**Bandwidth Requirements**:
- 720p @ 30fps: ~5 Mbps
- 1080p @ 30fps: ~10 Mbps
- 1080p @ 60fps: ~20 Mbps

**Error Handling**:
- ExoPlayer retries RTSP connection automatically
- `reconnect()` function for manual retry
- Error overlay shows troubleshooting instructions

#### 9.5.3 Memory Management

**ExoPlayer Memory Usage**:
- Video buffers: ~10-20 MB (depending on buffer duration)
- Decoder: Hardware-accelerated (no CPU memory overhead)
- Texture surfaces: ~8-12 MB (1080p RGB)

**Resource Cleanup**:
- `releasePlayer()` called on ViewModel destruction
- DisposableEffect ensures cleanup on composable exit
- No memory leaks in normal operation

---

### 9.6 Integration with CameraControlScreen

**Usage** (from `CameraControlScreen.kt`):
```kotlin
Box(modifier = Modifier.fillMaxSize()) {
    // Full-screen video background
    FullScreenVideoPlayer(
        videoSettings = videoSettings,
        videoPlayerViewModel = videoPlayerViewModel,
        modifier = Modifier.fillMaxSize()
    )

    // Camera controls overlay (shutter, ISO, etc.)
    CameraControlContent(...)
}
```

**Layering**:
1. **Background**: FullScreenVideoPlayer (z-index: 0)
2. **Foreground**: Semi-transparent camera controls (z-index: 1)

**User Experience**:
- Real-time video preview while adjusting camera settings
- Connection indicator shows air-side connection status
- Video continues playing during setting adjustments

---

### 9.7 Known Issues and Limitations

**Current MVP Limitations**:
1. **No Recording**: Video playback only, no DVR functionality
2. **No Snapshots**: Cannot capture still frames from video stream
3. **Fixed Codec**: H.264 only (no HEVC/VP9 support)
4. **UDP Only**: No TCP fallback for lossy networks
5. **Single Stream**: No multi-camera support

**Known Issues**:
- RTSP connection may fail on first attempt (ExoPlayer retry handles this)
- Video may freeze briefly during WiFi handoff (no auto-reconnect yet)
- Error overlay doesn't auto-dismiss on recovery (requires manual reconnect)

**Future Improvements** (see Section 18 - Future Roadmap):
- Implement auto-reconnect on network recovery
- Add video recording capability
- Support snapshot capture from live stream
- Add bandwidth adaptation for variable network conditions

---

## 10. Navigation

### 10.1 Navigation Architecture

**Current Implementation**: Single-screen MVP

The DPM Android app currently uses a **simplified single-screen architecture** for Phase 1 MVP. All functionality is accessible from the main `CameraControlScreen` with an embedded `SettingsScreen` accessible via button.

**Why Single-Screen**:
1. **MVP Focus**: Core functionality (camera control + video) in one view
2. **Pilot Workflow**: Quick access to all controls without navigation
3. **Simplicity**: Reduces complexity for initial testing phase

**Navigation Structure**:
```
MainActivity
  └─ CameraControlScreen (default/only screen)
       ├─ Video Background (full-screen)
       ├─ Camera Controls (overlay)
       └─ Settings Button → SettingsScreen (modal/overlay)
```

---

### 10.2 MainActivity Implementation

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/MainActivity.kt`

**Current Implementation** (from Section 4 - Core Components):
```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            DPMAndroidTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    CameraControlScreen()
                }
            }
        }
    }
}
```

**Design**:
- No Jetpack Navigation library used (overkill for single screen)
- Direct composable rendering in `setContent`
- Theme applied at top level

---

### 10.3 Screen Composition

**Layer Structure**:

```
┌─────────────────────────────────────┐
│  CameraControlScreen                │
│  ┌───────────────────────────────┐  │
│  │ FullScreenVideoPlayer (Base)  │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Camera Controls (Overlay)     │  │
│  │  - Connection Status          │  │
│  │  - Shutter/Aperture/ISO       │  │
│  │  - Capture Button             │  │
│  │  - Settings Button            │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ SettingsScreen (Conditional)  │  │ ← Shown when settings button pressed
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**State Management**:
- Settings visibility controlled by local state in CameraControlScreen
- No navigation state persistence needed (always starts on camera screen)

---

### 10.4 Future Navigation Plans

**Phase 2 Navigation Requirements**:

When additional screens are needed (event log, gallery, diagnostics), implement:

1. **Jetpack Navigation Compose**
   ```kotlin
   val navController = rememberNavController()

   NavHost(navController, startDestination = "camera") {
       composable("camera") { CameraControlScreen(navController) }
       composable("settings") { SettingsScreen(navController) }
       composable("eventLog") { EventLogScreen(navController) }
       composable("gallery") { GalleryScreen(navController) }
   }
   ```

2. **Bottom Navigation Bar** (for pilot-friendly navigation)
   ```
   ┌─────────────────────────────────────┐
   │  Screen Content                     │
   ├─────────────────────────────────────┤
   │ [Camera] [Settings] [Log] [Gallery] │ ← Bottom nav bar
   └─────────────────────────────────────┘
   ```

3. **Navigation Drawer** (alternative for desktop/tablet layout)

**Recommended Screens for Phase 2**:
- **Camera**: Main camera control (current CameraControlScreen)
- **Event Log**: Full EventLogScreen with filtering (currently stub)
- **Gallery**: Image/video gallery for captured media
- **System Status**: Detailed system diagnostics
- **Settings**: Full settings screen (move out of overlay)

---

### 10.5 Deep Linking

**Current**: Not implemented (not needed for MVP)

**Future Considerations**:

1. **External Camera Trigger**:
   ```
   dpm://camera/capture
   ```
   Allows external apps to trigger photo capture

2. **Settings Deep Link**:
   ```
   dpm://settings/network
   ```
   Jump directly to network settings

3. **Mission Planning Integration**:
   ```
   dpm://mission?waypoint=5
   ```
   Link to specific mission waypoint

**Implementation Path**:
- Add `<intent-filter>` in AndroidManifest.xml
- Handle deep links in MainActivity
- Parse parameters and navigate to destination

---

### 10.6 Navigation Best Practices

**When to Add Navigation**:
- ✅ **Do**: Add navigation when 3+ distinct screens are needed
- ✅ **Do**: Use navigation for modal flows (login, onboarding)
- ❌ **Don't**: Add navigation prematurely (current MVP approach)
- ❌ **Don't**: Use navigation for simple overlays (settings is fine as overlay)

**Current Approach Assessment**:
- ✅ **Correct for MVP**: Single screen is appropriate for testing core functionality
- ✅ **Easy to Extend**: Can add Jetpack Navigation in Phase 2 without refactoring
- ✅ **Pilot-Friendly**: No navigation complexity during flight operations

---

## 11. Dependencies

### 11.1 Dependency Management

**Build System**: Gradle with Kotlin DSL (`.kts`)

**Version Catalog**: `gradle/libs.versions.toml`

**Benefits**:
- Centralized version management
- Type-safe dependency references
- Easy version upgrades
- Shared versions across modules

---

### 11.2 Complete Dependency List

**From**: `gradle/libs.versions.toml` and `app/build.gradle.kts`

#### 11.2.1 Core Android Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `androidx.core:core-ktx` | 1.10.1 | Kotlin extensions for Android Core |
| `androidx.lifecycle:lifecycle-runtime-ktx` | 2.6.1 | Lifecycle-aware coroutines |
| `androidx.lifecycle:lifecycle-viewmodel-compose` | 2.6.1 | ViewModel integration for Compose |
| `androidx.activity:activity-compose` | 1.8.0 | Compose integration for Activity |

**Usage**:
- `core-ktx`: Kotlin extension functions (e.g., `context.getSystemService<T>()`)
- `lifecycle-runtime-ktx`: `lifecycleScope` for coroutines
- `lifecycle-viewmodel-compose`: `viewModel()` composable function
- `activity-compose`: `ComponentActivity.setContent {}`

---

#### 11.2.2 Jetpack Compose Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `androidx.compose:compose-bom` | 2024.09.00 | Bill of Materials for Compose version management |
| `androidx.compose.ui:ui` | (BOM) | Core Compose UI primitives |
| `androidx.compose.ui:ui-graphics` | (BOM) | Graphics and drawing APIs |
| `androidx.compose.ui:ui-tooling-preview` | (BOM) | Preview annotations |
| `androidx.compose.ui:ui-tooling` | (BOM) | Debug preview renderer |
| `androidx.compose.material3:material3` | (BOM) | Material Design 3 components |
| `androidx.compose.material3:material3-adaptive-navigation-suite` | (BOM) | Adaptive navigation components |
| `androidx.compose.material:material-icons-extended` | (BOM) | Extended Material icon set |

**BOM Benefits**:
- Single version management for all Compose libraries
- Guaranteed compatibility between Compose components
- Automatic version resolution

**Usage**:
- `ui`: `Column`, `Row`, `Box`, `Text`, `@Composable`
- `ui-graphics`: `Color`, `Brush`, `Path`
- `material3`: `MaterialTheme`, `Surface`, `Card`, `Button`
- `material-icons-extended`: Full icon library (Settings, Camera, etc.)

---

#### 11.2.3 Networking and Data

| Dependency | Version | Purpose |
|------------|---------|---------|
| `com.google.code.gson:gson` | 2.10.1 | JSON serialization/deserialization |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.7.3 | Kotlin coroutines for Android |
| `androidx.datastore:datastore-preferences` | 1.0.0 | Type-safe key-value storage |

**Usage**:
- **Gson**: Serialize/deserialize protocol messages (camera commands, system status)
  ```kotlin
  val json = gson.toJson(cameraCommand)
  val response = gson.fromJson(responseJson, SystemStatus::class.java)
  ```

- **Coroutines**: Asynchronous network operations
  ```kotlin
  viewModelScope.launch {
      val result = NetworkManager.sendCommand(command)
  }
  ```

- **DataStore**: Persist user settings (WiFi IP, video settings)
  ```kotlin
  dataStore.edit { preferences ->
      preferences[GROUND_STATION_IP] = "192.168.1.10"
  }
  ```

---

#### 11.2.4 Video Streaming (Media3 - ExoPlayer)

| Dependency | Version | Purpose |
|------------|---------|---------|
| `androidx.media3:media3-exoplayer` | 1.2.0 | Core ExoPlayer media player |
| `androidx.media3:media3-ui` | 1.2.0 | PlayerView UI component |
| `androidx.media3:media3-exoplayer-rtsp` | 1.2.0 | RTSP protocol support |

**Why Media3**:
- ExoPlayer is now part of Jetpack (androidx.media3)
- Official Android media player recommendation
- Superior to MediaPlayer for streaming
- Hardware-accelerated video decoding
- Extensive codec support (H.264, HEVC, VP9)

**Usage**:
- `media3-exoplayer`: Player engine, load control, codec handling
- `media3-ui`: `PlayerView` for video rendering
- `media3-exoplayer-rtsp`: RTSP MediaSource implementation

**Example**:
```kotlin
val exoPlayer = ExoPlayer.Builder(context).build()
val mediaItem = MediaItem.fromUri("rtsp://192.168.1.10:8554/H264Video")
exoPlayer.setMediaItem(mediaItem)
exoPlayer.prepare()
exoPlayer.play()
```

---

#### 11.2.5 Testing Dependencies

| Dependency | Version | Purpose | Scope |
|------------|---------|---------|-------|
| `junit:junit` | 4.13.2 | Unit testing framework | Test |
| `androidx.test.ext:junit` | 1.1.5 | Android JUnit extensions | AndroidTest |
| `androidx.test.espresso:espresso-core` | 3.5.1 | UI testing framework | AndroidTest |
| `androidx.compose.ui:ui-test-junit4` | (BOM) | Compose UI testing | AndroidTest |
| `androidx.compose.ui:ui-test-manifest` | (BOM) | Test manifest for Compose | Debug |

**Usage**:
- **JUnit**: Unit tests for ViewModels, data classes, utilities
- **Espresso**: Integration tests for Activities
- **Compose UI Test**: Composable testing with semantics tree

**Example Test**:
```kotlin
@Test
fun cameraViewModel_incrementShutterSpeed_updatesState() {
    val viewModel = CameraViewModel()
    val initialShutter = viewModel.cameraState.value.shutterSpeed

    viewModel.incrementShutterSpeed()

    assertNotEquals(initialShutter, viewModel.cameraState.value.shutterSpeed)
}
```

---

### 11.3 Build Configuration

**File**: `app/build.gradle.kts`

#### 11.3.1 Android Configuration

```kotlin
android {
    namespace = "uk.unmannedsystems.dpm_android"
    compileSdk = 36

    defaultConfig {
        applicationId = "uk.unmannedsystems.dpm_android"
        minSdk = 24  // Android 7.0 (Nougat)
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
    }
}
```

**SDK Versions**:
- **minSdk 24**: Android 7.0+ (released 2016)
  - Covers 95%+ of active devices
  - Jetpack Compose minimum requirement
- **targetSdk 36**: Latest Android API level
- **compileSdk 36**: Build against latest SDK

#### 11.3.2 Kotlin Configuration

```kotlin
compileOptions {
    sourceCompatibility = JavaVersion.VERSION_11
    targetCompatibility = JavaVersion.VERSION_11
}

kotlinOptions {
    jvmTarget = "11"
}
```

**Java 11 Target**:
- Required for Kotlin 2.0.21
- Modern language features (lambdas, streams)

#### 11.3.3 Compose Configuration

```kotlin
buildFeatures {
    compose = true
}
```

**Compose Compiler**:
- Kotlin Compose Compiler Plugin 2.0.21
- Automatic from `kotlin-compose` plugin

---

### 11.4 Gradle Plugins

**From**: `app/build.gradle.kts`

```kotlin
plugins {
    alias(libs.plugins.android.application)  // com.android.application:8.13.0
    alias(libs.plugins.kotlin.android)       // org.jetbrains.kotlin.android:2.0.21
    alias(libs.plugins.kotlin.compose)       // org.jetbrains.kotlin.plugin.compose:2.0.21
}
```

**Plugin Purposes**:
1. **android.application**: Android app build system
2. **kotlin.android**: Kotlin language support
3. **kotlin.compose**: Compose compiler integration

---

### 11.5 Version Catalog Details

**File**: `gradle/libs.versions.toml`

**Version Block**:
```toml
[versions]
agp = "8.13.0"             # Android Gradle Plugin
kotlin = "2.0.21"          # Kotlin language
composeBom = "2024.09.00"  # Compose Bill of Materials
media3 = "1.2.0"           # ExoPlayer (Media3)
coroutines = "1.7.3"       # Kotlin Coroutines
gson = "2.10.1"            # JSON library
datastore = "1.0.0"        # DataStore Preferences
```

**Benefits of Version Catalog**:
- Change `media3 = "1.2.0"` → all Media3 dependencies update
- Type-safe references: `libs.androidx.media3.exoplayer`
- No version conflicts

---

### 11.6 Dependency Update Strategy

**Current Versions**: Up-to-date as of October 2025

**Update Cadence**:
- **Compose BOM**: Monthly (new features, bug fixes)
- **Kotlin**: Quarterly (language updates)
- **Media3**: As needed (RTSP bug fixes)
- **AndroidX Libraries**: Quarterly (stability focus)

**Testing After Updates**:
1. Run unit tests: `./gradlew test`
2. Run instrumented tests: `./gradlew connectedAndroidTest`
3. Manual testing of video streaming (critical path)
4. Check EventLog for warnings

**Known Compatibility**:
- Compose BOM 2024.09.00 compatible with Kotlin 2.0.21 ✅
- Media3 1.2.0 stable for RTSP ✅
- No known dependency conflicts ✅

---

### 11.7 Dependency Graph Visualization

**High-Level Architecture**:
```
App Layer (Composables)
  ↓
  └─ ViewModels (State Management)
       ↓
       ├─ NetworkManager (TCP/UDP)
       │    └─ Gson (JSON serialization)
       │
       ├─ SettingsRepository (DataStore)
       │    └─ DataStore Preferences
       │
       └─ VideoPlayerViewModel
            └─ ExoPlayer (Media3)
                 └─ Media3 RTSP Extension
```

**Dependency Relationships**:
- **UI Layer**: Depends on Compose + ViewModels
- **ViewModel Layer**: Depends on NetworkManager + Repositories
- **Data Layer**: Depends on Gson + DataStore
- **Video Layer**: Depends on Media3 (independent subsystem)

---

### 11.8 ProGuard Configuration

**File**: `app/proguard-rules.pro`

**Current Status**: Not configured (debug builds only)

**Future Considerations** (for release builds):
- Keep Gson serialization classes
- Keep ExoPlayer reflection classes
- Obfuscate proprietary protocol code
- Remove logging in production

**Example Rules** (for future):
```proguard
# Keep Gson serialization
-keep class uk.unmannedsystems.dpm_android.camera.CameraState { *; }
-keep class uk.unmannedsystems.dpm_android.network.** { *; }

# Keep ExoPlayer
-keep class androidx.media3.** { *; }
```

---

## 12. Configuration & Settings

### 12.1 Android Manifest Configuration

**File**: `app/src/main/AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Network permissions required for DPM protocol communication -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:name=".DPMApplication"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.DPMAndroid">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/app_name"
            android:theme="@style/Theme.DPMAndroid">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

### 12.2 Permissions

#### 12.2.1 Required Permissions

| Permission | Purpose | Justification |
|------------|---------|---------------|
| `INTERNET` | Network communication | Required for TCP/UDP sockets to communicate with air-side |
| `ACCESS_NETWORK_STATE` | Network monitoring | Check WiFi connectivity status |

**Why These Permissions**:
- **INTERNET**: Mandatory for all network operations (TCP commands, UDP status/heartbeat, RTSP streaming)
- **ACCESS_NETWORK_STATE**: Allows app to detect WiFi disconnection and show appropriate UI

**Privacy Considerations**:
- App only communicates with user-configured IP address (default: 192.168.1.10)
- No internet access to external servers
- All network traffic is local WiFi only
- No analytics or telemetry sent externally

#### 12.2.2 Permissions Not Needed

The following permissions are **NOT** requested (unlike many drone apps):
- ❌ `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION`: No GPS tracking needed
- ❌ `CAMERA`: App controls remote camera, not device camera
- ❌ `RECORD_AUDIO`: No audio recording
- ❌ `WRITE_EXTERNAL_STORAGE`: Downloads not yet implemented (Phase 2)
- ❌ `READ_PHONE_STATE`: No phone identity needed

**Result**: Minimal permission footprint for privacy and security

---

### 12.3 Application Configuration

#### 12.3.1 Custom Application Class

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/DPMApplication.kt`

**Purpose**: Initialize NetworkManager on app startup (before any Activity)

**Key Behavior**:
- Extends `Application` - runs before MainActivity
- Loads saved settings from DataStore
- Initializes NetworkManager with settings
- Auto-connects immediately on app launch
- Uses `applicationScope` for proper lifecycle

**Benefits**:
- User sees connection status immediately on launch
- No delay waiting for Settings screen to load
- NetworkManager initialized before any UI
- Proper cleanup on app termination

**Manifest Registration**:
```xml
<application android:name=".DPMApplication" ...>
```

This tells Android to use `DPMApplication` instead of default `Application` class.

#### 12.3.2 Backup Configuration

**Backup Rules** (`res/xml/backup_rules.xml`):
- Android Auto Backup enabled (`android:allowBackup="true"`)
- DataStore preferences backed up by default
- User settings persist across device transfers
- Backup encryption handled by Android

**Data Extraction Rules** (Android 12+):
- `android:dataExtractionRules="@xml/data_extraction_rules"`
- Complies with Android 12+ backup requirements

---

### 12.4 Theme and Resources

#### 12.4.1 Application Theme

**Theme**: `@style/Theme.DPMAndroid`

**Defined In**: `app/src/main/res/values/themes.xml` (generated by Android Studio)

**Characteristics**:
- Material Design 3 (Material You)
- Dark theme always active (see Section 7.1.2)
- Professional camera operation aesthetic
- High contrast for outdoor visibility

**Application-Wide Theme**:
```xml
<application android:theme="@style/Theme.DPMAndroid">
```

**Activity Theme** (same theme):
```xml
<activity android:theme="@style/Theme.DPMAndroid">
```

#### 12.4.2 App Icon

**Icons**:
- `android:icon="@mipmap/ic_launcher"` - Standard icon
- `android:roundIcon="@mipmap/ic_launcher_round"` - Circular adaptive icon

**Adaptive Icon**:
- Supports Android 8.0+ adaptive icons
- Background + foreground layers
- Conforms to device icon shape (circle, square, squircle, etc.)

**Icon Locations**:
- `app/src/main/res/mipmap-*/ic_launcher.png` (various DPIs)
- `app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml` (adaptive)

#### 12.4.3 Application Label

**App Name**: `@string/app_name`

**Defined In**: `app/src/main/res/values/strings.xml`

**Display**: "DPM-Android" (shown in launcher, recent apps, etc.)

---

### 12.5 Activity Configuration

#### 12.5.1 MainActivity Settings

**Export Configuration**:
```xml
android:exported="true"
```
- Required for launcher activity (receives `MAIN`/`LAUNCHER` intent)
- Allows external apps to start MainActivity (if needed for future deep linking)

**Intent Filter**:
```xml
<intent-filter>
    <action android:name="android.intent.action.MAIN" />
    <category android:name="android.intent.category.LAUNCHER" />
</intent-filter>
```
- `MAIN`: Entry point for application
- `LAUNCHER`: Shows app in launcher (home screen)

**Screen Orientation**:
- Not explicitly set → defaults to `sensor` (auto-rotate)
- Allows landscape/portrait based on device orientation
- Camera screen works in both orientations

---

### 12.6 Build Configuration

**Application ID**: `uk.unmannedsystems.dpm_android`

**Namespace**: `uk.unmannedsystems.dpm_android`

**Why Namespace Matters**:
- Unique identifier on Google Play (if published)
- Package name for all app components
- Namespace for generated R.java (resources)

**Version Management** (from `app/build.gradle.kts`):
```kotlin
defaultConfig {
    applicationId = "uk.unmannedsystems.dpm_android"
    versionCode = 1       // Internal version (increment for each release)
    versionName = "1.0"   // User-visible version string
}
```

**Version Strategy**:
- `versionCode`: Integer, must increment for each release (Play Store requirement)
- `versionName`: String, semantic versioning (e.g., "1.0", "1.1", "2.0")

---

### 12.7 RTL Support

**Configuration**:
```xml
android:supportsRtl="true"
```

**Purpose**: Right-to-left language support (Arabic, Hebrew, etc.)

**Current Status**: English only, but infrastructure ready for internationalization

**Future Localization**:
- Add `strings-ar.xml` for Arabic
- Add `strings-he.xml` for Hebrew
- UI automatically mirrors for RTL languages

---

### 12.8 Runtime Configuration

#### 12.8.1 Settings Persistence

**DataStore Preferences** (from Section 5.2):
- Network settings (IP, ports, timeouts)
- Video settings (RTSP URL, buffer duration, aspect ratio)
- Persisted to: `/data/data/uk.unmannedsystems.dpm_android/files/datastore/settings.preferences_pb`

**Default Settings** (hardcoded in `NetworkSettings.kt` and `VideoStreamSettings.kt`):
- Ground Station IP: `192.168.1.10`
- Command Port: `5000`
- Status Port: `5001`
- Heartbeat Port: `5002`
- RTSP URL: `rtsp://192.168.1.10:8554/H264Video`
- Buffer Duration: `500ms`

#### 12.8.2 Configuration Files

**No External Config Files**:
- All configuration via DataStore (user settings)
- No XML/JSON config files loaded at runtime
- Simplifies deployment (no file management needed)

**Advantages**:
- Settings UI is source of truth
- No file permission issues
- Backup/restore handled by Android

---

## 13. Testing

### 13.1 Testing Strategy

**Testing Pyramid**:
```
       E2E Tests (Manual)
      /                  \
   Integration Tests (Instrumented)
  /                                  \
Unit Tests (Fast, Isolated)
```

**Current Status**:
- ✅ Unit tests: Minimal (example test exists)
- ⏸️ Integration tests: Not implemented
- ⏸️ E2E tests: Manual testing only

**Phase 1 MVP Testing Approach**:
- Focus on manual testing with real hardware
- Add automated tests in Phase 2
- Prioritize core functionality (connection, commands, video)

---

### 13.2 Unit Testing

#### 13.2.1 Current Test Coverage

**File**: `app/src/test/java/uk/unmannedsystems/dpm_android/ExampleUnitTest.kt`

```kotlin
package uk.unmannedsystems.dpm_android

import org.junit.Test
import org.junit.Assert.*

class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }
}
```

**Status**: Example test only (not production tests)

**Test Scope**: `test` (runs on JVM, no Android dependencies)

**Framework**: JUnit 4.13.2

#### 13.2.2 Recommended Unit Tests (Future)

**ViewModels**:
```kotlin
class CameraViewModelTest {
    @Test
    fun incrementShutterSpeed_updatesStateCorrectly() {
        val viewModel = CameraViewModel()
        val initial = viewModel.cameraState.value.shutterSpeed

        viewModel.incrementShutterSpeed()

        val updated = viewModel.cameraState.value.shutterSpeed
        assertNotEquals(initial, updated)
    }

    @Test
    fun connect_updatesConnectionStatus() = runTest {
        val viewModel = CameraViewModel()

        viewModel.connect()

        val status = viewModel.cameraState.value.isConnected
        assertTrue(status)
    }
}
```

**Data Models**:
```kotlin
class CameraStateTest {
    @Test
    fun cameraState_defaultValues_areCorrect() {
        val state = CameraState()

        assertEquals(ShutterSpeed.S_1_125, state.shutterSpeed)
        assertEquals(Aperture.F_8_0, state.aperture)
        assertEquals(ISO.ISO_400, state.iso)
        assertFalse(state.isRecording)
    }
}
```

**Utilities**:
```kotlin
class ProtocolHelpersTest {
    @Test
    fun shutterSpeedToProtocol_convertsCorrectly() {
        val result = shutterSpeedToProtocol(ShutterSpeed.S_1_125)
        assertEquals("1/125", result)
    }
}
```

#### 13.2.3 Test Execution

**Command**:
```bash
./gradlew test
```

**Output**: Test reports in `app/build/reports/tests/testDebugUnitTest/index.html`

**CI/CD Integration** (future):
```yaml
# GitHub Actions example
- name: Run unit tests
  run: ./gradlew test
```

---

### 13.3 Instrumented Testing

#### 13.3.1 Instrumented Test Framework

**Scope**: `androidTest`

**Frameworks**:
- AndroidX Test (JUnit 4 extensions)
- Espresso (UI testing)
- Compose UI Test (Composable testing)

**Test Device**: Requires Android emulator or physical device

#### 13.3.2 Recommended Instrumented Tests (Future)

**Compose UI Tests**:
```kotlin
@RunWith(AndroidJUnit4::class)
class CameraControlScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun captureButton_isDisplayed() {
        composeTestRule.setContent {
            DPMAndroidTheme {
                CameraControlScreen()
            }
        }

        composeTestRule.onNodeWithText("Capture").assertIsDisplayed()
    }

    @Test
    fun connectionIndicator_showsRedWhenDisconnected() {
        // Mock ViewModel with disconnected state
        composeTestRule.setContent {
            DPMAndroidTheme {
                ConnectionStatusIndicator(isConnected = false, onClick = {})
            }
        }

        composeTestRule.onNodeWithText("Air-Side Disconnected")
            .assertIsDisplayed()
    }
}
```

**Integration Tests**:
```kotlin
@RunWith(AndroidJUnit4::class)
class NetworkClientIntegrationTest {
    private lateinit var networkClient: NetworkClient

    @Before
    fun setup() {
        val settings = NetworkSettings(targetIp = "192.168.1.10")
        networkClient = NetworkClient(settings, /* ... */)
    }

    @Test
    fun connect_withValidSettings_succeeds() = runTest {
        val result = networkClient.connect()
        assertTrue(result.isSuccess)
    }

    @After
    fun teardown() {
        networkClient.disconnect()
    }
}
```

#### 13.3.3 Test Execution

**Command**:
```bash
./gradlew connectedAndroidTest
```

**Requirements**:
- Android device connected via USB (with USB debugging enabled)
- OR Android emulator running

**Output**: Test reports in `app/build/reports/androidTests/connected/index.html`

---

### 13.4 Manual Testing

#### 13.4.1 Manual Test Plan

**Connection Testing**:
1. [ ] App launches and auto-connects to configured IP
2. [ ] Connection indicator shows GREEN when connected
3. [ ] Connection indicator shows RED when disconnected
4. [ ] Heartbeat sent every 1 second
5. [ ] Status updates received at 5 Hz
6. [ ] Reconnection after network interruption

**Camera Testing**:
1. [ ] Shutter button triggers camera.capture command
2. [ ] Camera settings (shutter, aperture, ISO) send commands
3. [ ] Camera status updates display correctly
4. [ ] Battery level updates in real-time
5. [ ] Remaining shots counter updates

**Video Testing**:
1. [ ] RTSP stream connects and displays video
2. [ ] Video overlay states show correctly (Disconnected, Connecting, Connected, Error)
3. [ ] Video settings (enable/disable, URL, aspect ratio) apply correctly
4. [ ] Video continues playing during camera control adjustments
5. [ ] Video latency < 1 second

**Settings Testing**:
1. [ ] Settings save and persist across app restarts
2. [ ] Reset to Defaults restores default settings
3. [ ] IP address change triggers reconnection
4. [ ] Invalid IP shows error message

**System Status Testing**:
1. [ ] System status screen displays uptime, CPU, memory, storage
2. [ ] Manual refresh button updates status
3. [ ] Status auto-updates from UDP broadcasts

#### 13.4.2 Hardware Test Checklist

**SkyDroid H16 Pro Testing** (when available):
- [ ] Install APK on H16 device
- [ ] Connect to R16 Air Unit WiFi
- [ ] Verify default IP (192.168.1.10) connects
- [ ] Test camera capture with real camera
- [ ] Test video streaming
- [ ] Test connection stability during flight
- [ ] Battery consumption analysis

---

### 13.5 Performance Testing

#### 13.5.1 Performance Metrics

**App Startup**:
- ⏳ Target: < 3 seconds cold start
- ⏳ Target: < 1 second warm start

**Network Latency**:
- ⏳ Target: < 500ms TCP connection
- ⏳ Target: < 50ms command round-trip

**Video Latency**:
- ⏳ Target: < 1 second end-to-end (camera → display)

**Memory Usage**:
- ⏳ Target: < 150 MB RAM usage
- ⏳ Target: No memory leaks (Profiler verification)

**Battery Consumption**:
- ⏳ Target: < 10% battery per hour (screen on, video streaming)

#### 13.5.2 Profiling Tools

**Android Studio Profiler**:
- CPU Profiler: Identify performance bottlenecks
- Memory Profiler: Track memory allocations and leaks
- Network Profiler: Monitor network activity
- Energy Profiler: Measure battery consumption

**LeakCanary** (future):
- Automatic memory leak detection
- Recommended for Phase 2 development

---

### 13.6 Testing Best Practices

**Test Naming Convention**:
```kotlin
// Pattern: methodName_stateUnderTest_expectedBehavior
fun connect_withValidSettings_succeeds()
fun incrementShutterSpeed_whenAtMax_doesNotChange()
```

**Test Organization**:
- One test class per production class (e.g., `CameraViewModelTest` for `CameraViewModel`)
- Group related tests in nested classes
- Use `@Before` for setup, `@After` for cleanup

**Mocking**:
- Use MockK or Mockito for mocking dependencies
- Mock NetworkClient for ViewModel tests
- Mock ViewModel for UI tests

**Continuous Testing**:
- Run tests before every commit
- Add pre-commit hook: `./gradlew test`
- CI/CD pipeline runs all tests on push

---

## 14. Build System

### 14.1 Gradle Configuration

#### 14.1.1 Project Structure

**Multi-Module Project** (potential for future expansion):
```
DPM-Android/
├── app/               # Main application module
├── build.gradle.kts   # Project-level build file
├── settings.gradle.kts # Settings and repositories
└── gradle/
    └── libs.versions.toml # Version catalog
```

**Current**: Single-module app (all code in `:app` module)

**Future Expansion Potential**:
- `:network` module (reusable network layer)
- `:protocol` module (protocol definitions)
- `:ui-components` module (shared UI components)

#### 14.1.2 Settings Configuration

**File**: `settings.gradle.kts`

```kotlin
pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "DPM-Android"
include(":app")
```

**Key Configuration**:

1. **Plugin Repositories**:
   - `google()`: Android Gradle Plugin, AndroidX libraries
   - `mavenCentral()`: Kotlin, Compose, third-party libraries
   - `gradlePluginPortal()`: Gradle community plugins

2. **Content Filters**:
   - `includeGroupByRegex("com\\.android.*")`: Only fetch Android artifacts from Google
   - Improves build performance (fewer repository lookups)

3. **Repository Mode**:
   - `FAIL_ON_PROJECT_REPOS`: Enforce centralized repository management
   - Prevents per-module repository declarations (cleaner builds)

4. **Module Inclusion**:
   - `include(":app")`: Register app module with Gradle

---

### 14.2 Build Variants

#### 14.2.1 Debug vs. Release

**Debug Build**:
- Development builds for testing
- Debuggable: `android:debuggable="true"` (automatic)
- No code obfuscation
- Includes debug symbols
- Faster builds (no optimization)

**Release Build** (future):
```kotlin
buildTypes {
    release {
        isMinifyEnabled = true           // Enable R8 code shrinking
        isShrinkResources = true         // Remove unused resources
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

**Current Status**: Debug builds only (MVP phase)

**Release Build Plan** (Phase 2):
- Enable R8 code shrinking (reduce APK size)
- Configure ProGuard rules for Gson/ExoPlayer
- Add signing configuration for release APKs

#### 14.2.2 Build Type Selection

**Android Studio**: Build Variants panel → "debug" or "release"

**Command Line**:
```bash
./gradlew assembleDebug    # Build debug APK
./gradlew assembleRelease  # Build release APK (not configured yet)
```

---

### 14.3 ProGuard / R8 Configuration

**File**: `app/proguard-rules.pro`

**Current Status**: Default rules only (all commented out)

**Future ProGuard Rules** (for release builds):

```proguard
# Keep Gson serialization classes
-keep class uk.unmannedsystems.dpm_android.camera.CameraState { *; }
-keep class uk.unmannedsystems.dpm_android.network.** { *; }
-keep class uk.unmannedsystems.dpm_android.system.SystemStatus { *; }

# Keep ExoPlayer
-keep class androidx.media3.** { *; }
-dontwarn androidx.media3.**

# Keep DataStore
-keep class androidx.datastore.** { *; }

# Keep Kotlin coroutines
-keep class kotlinx.coroutines.** { *; }

# Keep line numbers for stack traces
-keepattributes SourceFile,LineNumberTable

# Remove logging in production
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}
```

**R8 Benefits**:
- Reduce APK size by 30-50% (code shrinking)
- Remove unused resources (smaller download)
- Obfuscate code (basic security)

**Risks**:
- Gson reflection needs keep rules (or app crashes)
- ExoPlayer may need keep rules for certain features
- Testing required after enabling R8

---

### 14.4 Build Performance

#### 14.4.1 Build Times

**Typical Build Times** (Development Machine):
- Clean build: ~60 seconds
- Incremental build: ~10 seconds
- No-op build (no changes): ~3 seconds

**Factors Affecting Build Speed**:
- CPU: 8+ cores recommended
- RAM: 16 GB+ recommended
- SSD: Significantly faster than HDD
- Gradle daemon: Keeps Gradle in memory (speeds up subsequent builds)

#### 14.4.2 Build Optimization

**Gradle Daemon** (enabled by default):
- Reuses Gradle process across builds
- Speeds up build by 50-70%

**Build Cache**:
- Caches build outputs
- Shares cache across projects
- Configure in `gradle.properties`:
  ```properties
  org.gradle.caching=true
  ```

**Parallel Execution**:
- Builds modules in parallel (when multiple modules exist)
- Configure in `gradle.properties`:
  ```properties
  org.gradle.parallel=true
  ```

**Configuration Cache** (Gradle 7+):
- Caches task configuration
- Faster for clean builds
- Enable in `gradle.properties`:
  ```properties
  org.gradle.configuration-cache=true
  ```

---

### 14.5 Version Control (.gitignore)

**File**: `android/.gitignore`

**Ignored Files**:
```
/build
```

**Why `/build` is Ignored**:
- Build outputs are generated (not source code)
- APKs, compiled classes, intermediate files
- ~500 MB+ of generated files (would bloat repository)

**Other Ignored Files** (typical Android .gitignore):
```
*.iml
.gradle
.idea
local.properties
*.apk
*.ap_
*.dex
captures/
.externalNativeBuild
.cxx
```

**Why These Are Ignored**:
- `.gradle`: Gradle cache (regenerated on build)
- `.idea`: Android Studio IDE settings (machine-specific)
- `local.properties`: Local paths (e.g., `sdk.dir=/Users/name/Android/sdk`)
- `*.apk`: Build outputs (not source code)

**What IS Committed**:
- All source code (`.kt`, `.xml`, `.kts`)
- `gradle/wrapper/gradle-wrapper.jar` (Gradle wrapper)
- `gradle/libs.versions.toml` (dependency versions)
- `build.gradle.kts`, `settings.gradle.kts` (build scripts)

---

### 14.6 APK Output

#### 14.6.1 APK Location

**Debug APK**:
```
app/build/outputs/apk/debug/app-debug.apk
```

**File Size**: ~8-10 MB (estimated, includes ExoPlayer libraries)

**Installation**:
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

#### 14.6.2 APK Contents

**APK Structure** (ZIP file):
```
app-debug.apk
├── AndroidManifest.xml (binary)
├── classes.dex (Dalvik bytecode)
├── resources.arsc (compiled resources)
├── res/ (images, layouts, etc.)
├── lib/ (native libraries for ExoPlayer)
│   ├── arm64-v8a/
│   ├── armeabi-v7a/
│   └── x86_64/
└── META-INF/ (signatures)
```

**Multi-ABI Support**:
- `arm64-v8a`: 64-bit ARM (modern devices)
- `armeabi-v7a`: 32-bit ARM (older devices)
- `x86_64`: 64-bit x86 (emulators, rare devices)

**APK Size Breakdown** (estimated):
- Code (Kotlin + libraries): ~4 MB
- ExoPlayer native libraries: ~3 MB
- Resources (icons, layouts): ~1 MB
- Manifest + metadata: < 1 MB

---

### 14.7 Gradle Commands Reference

**Common Commands**:

| Command | Purpose |
|---------|---------|
| `./gradlew assembleDebug` | Build debug APK |
| `./gradlew installDebug` | Build and install debug APK |
| `./gradlew clean` | Delete build outputs |
| `./gradlew test` | Run unit tests |
| `./gradlew connectedAndroidTest` | Run instrumented tests |
| `./gradlew dependencies` | Show dependency tree |
| `./gradlew tasks` | List all available tasks |

**Advanced Commands**:
- `./gradlew assembleDebug --info`: Verbose build output
- `./gradlew assembleDebug --scan`: Generate build scan (online report)
- `./gradlew assembleDebug --offline`: Build without network

---

## 15. Code Conventions

### 15.1 Kotlin Coding Style

**Style Guide**: Official Kotlin coding conventions

**Reference**: https://kotlinlang.org/docs/coding-conventions.html

#### 15.1.1 Naming Conventions

**Classes and Objects**:
```kotlin
class CameraViewModel      // PascalCase
object NetworkManager      // PascalCase
enum class CameraMode      // PascalCase
data class CameraState     // PascalCase
```

**Functions and Variables**:
```kotlin
fun incrementShutterSpeed()  // camelCase
val isConnected = true       // camelCase
var currentShutter = S_1_125 // camelCase
```

**Constants**:
```kotlin
const val TAG = "CameraViewModel"           // UPPER_SNAKE_CASE
const val DEFAULT_TIMEOUT_MS = 5000         // UPPER_SNAKE_CASE
private const val MAX_RETRY_ATTEMPTS = 3    // UPPER_SNAKE_CASE
```

**Package Names**:
```kotlin
package uk.unmannedsystems.dpm_android.camera  // lowercase, no underscores
```

#### 15.1.2 File Organization

**Class File Structure**:
```kotlin
// 1. Package declaration
package uk.unmannedsystems.dpm_android.camera

// 2. Imports (Android → third-party → project)
import androidx.compose.runtime.*
import androidx.lifecycle.ViewModel
import uk.unmannedsystems.dpm_android.network.NetworkManager

// 3. Class documentation
/**
 * ViewModel for camera control screen
 */
class CameraViewModel : ViewModel() {
    // 4. Companion object (constants)
    companion object {
        private const val TAG = "CameraViewModel"
    }

    // 5. Properties (private → public)
    private val _cameraState = MutableStateFlow(CameraState())
    val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

    // 6. Init block
    init {
        // Initialization code
    }

    // 7. Public methods
    fun incrementShutterSpeed() { /* ... */ }

    // 8. Private methods
    private fun sendPropertyCommand() { /* ... */ }

    // 9. Lifecycle methods
    override fun onCleared() { /* ... */ }
}
```

#### 15.1.3 Formatting

**Indentation**: 4 spaces (no tabs)

**Line Length**: Max 120 characters (soft limit)

**Braces**:
```kotlin
// ✅ Correct
fun foo() {
    if (condition) {
        doSomething()
    }
}

// ❌ Incorrect
fun foo()
{
    if (condition)
    {
        doSomething()
    }
}
```

**Function Declarations**:
```kotlin
// Short function
fun add(a: Int, b: Int): Int = a + b

// Long function signature → break after parameters
fun initializePlayer(
    context: Context,
    rtspUrl: String,
    bufferDurationMs: Long = 500
) {
    // Implementation
}
```

---

### 15.2 Package Structure

**Package Hierarchy**:
```
uk.unmannedsystems.dpm_android/
├── camera/           # Camera control feature
├── eventlog/         # Event logging feature
├── network/          # Network layer (TCP/UDP)
├── settings/         # Settings feature
├── system/           # System status feature
├── video/            # Video streaming feature
├── ui/theme/         # Theme and styling
├── DPMApplication.kt # Application class
└── MainActivity.kt   # Main activity
```

**Package Naming**:
- Feature-based packages (camera, settings, video)
- Shared infrastructure (network, ui)
- Flat structure (no deep nesting)

**Package Dependencies**:
```
UI Layer (camera/, settings/, video/)
  ↓
Business Logic (ViewModels)
  ↓
Data Layer (network/, repositories)
```

**Dependency Rule**: Higher layers depend on lower layers (not vice versa)

---

### 15.3 Documentation Standards

#### 15.3.1 KDoc Comments

**Class Documentation**:
```kotlin
/**
 * ViewModel for managing RTSP video stream playback using ExoPlayer.
 *
 * Handles ExoPlayer lifecycle, connection state, and video playback state.
 * Automatically releases resources when ViewModel is cleared.
 */
class VideoPlayerViewModel : ViewModel() { /* ... */ }
```

**Function Documentation**:
```kotlin
/**
 * Initialize ExoPlayer and connect to RTSP stream.
 *
 * @param context Android context for ExoPlayer initialization
 * @param rtspUrl RTSP stream URL (e.g., rtsp://192.168.1.10:8554/H264Video)
 * @param bufferDurationMs Buffer duration in milliseconds for low-latency tuning
 */
fun initializePlayer(context: Context, rtspUrl: String, bufferDurationMs: Long = 500) {
    // Implementation
}
```

**Property Documentation**:
```kotlin
/**
 * Current video playback state.
 *
 * Emits [VideoState.Disconnected], [VideoState.Connecting],
 * [VideoState.Connected], or [VideoState.Error] based on ExoPlayer state.
 */
val videoState: StateFlow<VideoState> = _videoState.asStateFlow()
```

#### 15.3.2 Comment Guidelines

**When to Comment**:
- ✅ Complex algorithms or business logic
- ✅ Non-obvious design decisions
- ✅ Workarounds or known issues
- ✅ Public APIs

**When NOT to Comment**:
- ❌ Self-explanatory code
- ❌ Obvious statements (e.g., "increment counter")

**Example - Good Comments**:
```kotlin
// Optimistic update: UI updates immediately, then sends command to air-side
_cameraState.update { state ->
    state.copy(shutterSpeed = newShutterSpeed)
}

sendPropertyCommand("shutter_speed", shutterSpeedToProtocol(newShutterSpeed))
```

**Example - Bad Comments**:
```kotlin
// Increment the counter
counter++
```

---

### 15.4 Jetpack Compose Conventions

#### 15.4.1 Composable Naming

**PascalCase for Composables**:
```kotlin
@Composable
fun CameraControlScreen() { /* ... */ }

@Composable
fun ConnectionStatusIndicator() { /* ... */ }
```

**Private Composables**:
```kotlin
@Composable
private fun MinimizedSettings() { /* ... */ }
```

#### 15.4.2 Composable Structure

**Order of Elements**:
```kotlin
@Composable
fun MyScreen(
    // 1. Required parameters
    title: String,

    // 2. Optional parameters with defaults
    showToolbar: Boolean = true,

    // 3. Callbacks
    onBackClick: () -> Unit = {},

    // 4. Modifier (always last)
    modifier: Modifier = Modifier
) {
    // 5. Remember values
    var expanded by rememberSaveable { mutableStateOf(false) }

    // 6. Side effects (LaunchedEffect, DisposableEffect)
    LaunchedEffect(key1) { /* ... */ }

    // 7. UI layout
    Column(modifier = modifier) {
        // Content
    }
}
```

#### 15.4.3 State Management

**State Hoisting**:
```kotlin
// ❌ Don't: State owned by composable
@Composable
fun MyButton() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Clicked $count times")
    }
}

// ✅ Do: State hoisted to caller
@Composable
fun MyButton(
    count: Int,
    onCountChange: (Int) -> Unit
) {
    Button(onClick = { onCountChange(count + 1) }) {
        Text("Clicked $count times")
    }
}
```

**ViewModel Integration**:
```kotlin
@Composable
fun CameraScreen(
    viewModel: CameraViewModel = viewModel()
) {
    val cameraState by viewModel.cameraState.collectAsState()

    CameraContent(
        cameraState = cameraState,
        onCaptureClick = viewModel::captureImage
    )
}
```

---

### 15.5 Error Handling

#### 15.5.1 Result Type Usage

**Prefer Result<T> for Network Calls**:
```kotlin
suspend fun getSystemStatus(): Result<SystemStatus> {
    return try {
        val status = fetchFromAirSide()
        Result.success(status)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

**Consuming Results**:
```kotlin
val result = NetworkManager.getSystemStatus()

result.fold(
    onSuccess = { status -> updateUI(status) },
    onFailure = { error -> showError(error.message) }
)
```

#### 15.5.2 Exception Handling

**Catch Specific Exceptions**:
```kotlin
try {
    connectToNetwork()
} catch (e: SocketTimeoutException) {
    Log.e(TAG, "Connection timeout", e)
} catch (e: IOException) {
    Log.e(TAG, "Network error", e)
}
```

**Log All Exceptions**:
```kotlin
catch (e: Exception) {
    Log.e(TAG, "Failed to perform operation", e)
    EventLogViewModel.logError(EventCategory.NETWORK, "Operation failed: ${e.message}")
}
```

---

### 15.6 Coroutines Best Practices

**Use viewModelScope for ViewModels**:
```kotlin
fun loadData() {
    viewModelScope.launch {
        val data = repository.fetchData()
        _uiState.update { it.copy(data = data) }
    }
}
```

**Use applicationScope for Application-Wide Operations**:
```kotlin
class DPMApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        applicationScope.launch {
            initializeNetworkManager()
        }
    }
}
```

**Handle Cancellation**:
```kotlin
viewModelScope.launch {
    try {
        withTimeout(5000) {
            performLongOperation()
        }
    } catch (e: TimeoutCancellationException) {
        Log.w(TAG, "Operation timed out")
    }
}
```

---

## 16. Deployment

### 16.1 Build Process

#### 16.1.1 Debug Build Generation

**Command**:
```bash
cd /d/DPM/DPM-V2/android
./gradlew assembleDebug
```

**Output**: `app/build/outputs/apk/debug/app-debug.apk`

**Build Time**: ~30-60 seconds (clean build)

**Build Success Indicator**:
```
BUILD SUCCESSFUL in 29s
42 actionable tasks: 42 executed
```

#### 16.1.2 Release Build (Future)

**Prerequisites**:
1. Configure signing in `app/build.gradle.kts`:
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("../keystore/dpm-release.jks")
           storePassword = System.getenv("KEYSTORE_PASSWORD")
           keyAlias = "dpm-key"
           keyPassword = System.getenv("KEY_PASSWORD")
       }
   }
   ```

2. Create signing keystore:
   ```bash
   keytool -genkey -v -keystore dpm-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias dpm-key
   ```

**Build Command**:
```bash
./gradlew assembleRelease
```

**Output**: `app/build/outputs/apk/release/app-release.apk` (signed, optimized)

---

### 16.2 Installation Methods

#### 16.2.1 ADB Installation (Development)

**Via USB**:
```bash
# 1. Enable USB debugging on device (Settings → Developer Options)
# 2. Connect device via USB
# 3. Install APK
adb install app/build/outputs/apk/debug/app-debug.apk

# Or: Build and install in one command
./gradlew installDebug
```

**Via WiFi**:
```bash
# 1. Connect device via USB first
adb tcpip 5555

# 2. Disconnect USB, get device IP
adb shell ip addr show wlan0

# 3. Connect via WiFi
adb connect 192.168.1.100:5555

# 4. Install
adb install app-debug.apk
```

#### 16.2.2 Manual Installation (Field Deployment)

**Transfer APK to Device**:
1. Copy `app-debug.apk` to device (USB, WiFi, SD card, email)
2. On device: Open file manager → tap APK
3. Enable "Install from unknown sources" if prompted
4. Tap "Install"

**Alternative: QR Code**:
- Upload APK to file sharing service
- Generate QR code with download link
- Pilot scans QR code on H16 device
- Downloads and installs APK

---

### 16.3 SkyDroid H16 Pro Deployment

#### 16.3.1 H16 Device Specifications

**Hardware**:
- SoC: Android-capable processor
- RAM: Likely 2-4 GB
- Storage: Likely 16-32 GB
- Screen: 7-10" touchscreen
- OS: Android (likely 7.x - 11.x)

**Compatibility**:
- App minSdk: 24 (Android 7.0+)
- H16 should be compatible (verify exact Android version)

#### 16.3.2 Installation Steps

1. **Prepare APK**:
   ```bash
   ./gradlew assembleDebug
   cp app/build/outputs/apk/debug/app-debug.apk ~/Desktop/dpm-android.apk
   ```

2. **Transfer to H16**:
   - Option A: USB cable → copy to Downloads folder
   - Option B: Email APK to self → download on H16
   - Option C: Upload to cloud (Google Drive, Dropbox) → download on H16

3. **Install on H16**:
   - Open file manager on H16
   - Navigate to APK location
   - Tap APK → Install
   - (May need to enable "Unknown sources" in Settings → Security)

4. **Configure Network**:
   - Connect H16 to R16 Air Unit WiFi
   - Verify IP address (default: 192.168.1.10)
   - If different, update in app Settings

5. **Test Connection**:
   - Launch app on H16
   - Check connection indicator (should turn GREEN)
   - Test camera capture
   - Test video streaming

---

### 16.4 WiFi Configuration

#### 16.4.1 Network Setup

**Scenario 1: Direct Connection (Ad-Hoc)**:
```
R16 Air Unit (192.168.1.10)
  ↓ WiFi Access Point
H16 Ground Station (192.168.1.x)
  ↓ App
DPM Android App
```

**Scenario 2: Router-Based Network**:
```
Router (192.168.1.1)
  ├─ R16 Air Unit (192.168.1.10)
  └─ H16 Ground Station (192.168.1.x)
```

**Configuration**:
- Ensure H16 and R16 on same subnet
- Use static IP for R16 (192.168.1.10) or configure DHCP reservation
- Update app settings if IP changes

#### 16.4.2 WiFi Recommendations

**For Best Performance**:
- **Band**: 5GHz (less congestion, higher bandwidth)
- **Channel**: Non-overlapping (36, 40, 44, 48, 149, 153, 157, 161)
- **Bandwidth**: 40 MHz or 80 MHz (higher throughput)
- **Distance**: < 50 meters (for stable connection)
- **Interference**: Avoid microwave ovens, other WiFi networks

**Troubleshooting**:
- If video stutters: Reduce buffer duration (Settings → Video → Buffer: 200ms)
- If connection drops: Check WiFi signal strength
- If commands slow: Check network latency (Settings → Connection logs)

---

### 16.5 Update Deployment

#### 16.5.1 Update Process

**When New Version Available**:
1. Build new APK with incremented `versionCode`
2. Transfer APK to H16
3. Install (automatically uninstalls old version)
4. Settings persist (DataStore survives reinstall)

**Version Management**:
```kotlin
// app/build.gradle.kts
defaultConfig {
    versionCode = 2      // Increment for each release
    versionName = "1.1"  // Update user-visible version
}
```

**Changelog Communication**:
- Include version notes in commit message
- Document changes in PROGRESS_AND_TODO.MD
- Notify user of major changes via app notification (future)

#### 16.5.2 Rollback

**If Update Causes Issues**:
1. Uninstall problematic version
2. Reinstall previous APK
3. Settings should persist (unless DataStore schema changed)

**Backup Strategy** (future):
- Export settings to JSON file
- User can import settings after rollback
- Implement in Settings screen (Phase 2)

---

### 16.6 Release Checklist

**Pre-Release**:
- [ ] All tests passing (`./gradlew test`)
- [ ] No compilation errors or warnings
- [ ] Version code incremented
- [ ] Version name updated
- [ ] PROGRESS_AND_TODO.MD updated
- [ ] Git committed and pushed

**Build**:
- [ ] Clean build successful (`./gradlew clean assembleDebug`)
- [ ] APK size reasonable (< 15 MB)
- [ ] No ProGuard/R8 errors (if release build)

**Testing**:
- [ ] Manual testing on emulator
- [ ] Manual testing on physical device (if available)
- [ ] Connection to air-side verified
- [ ] Camera commands tested
- [ ] Video streaming tested
- [ ] Settings persistence verified

**Deployment**:
- [ ] APK transferred to H16
- [ ] Installation successful
- [ ] App launches without crashes
- [ ] Connection to R16 successful
- [ ] End-to-end workflow tested

---

## 17. Known Issues & Technical Debt

### 17.1 Active Issues

**Current Active Issues**: None

*This section will be updated as issues are discovered during testing.*

---

### 17.2 Technical Debt

#### 17.2.1 Testing Coverage

**Issue**: Minimal automated testing

**Details**:
- Only example unit test exists
- No integration tests
- No UI tests
- All testing is manual

**Impact**: Medium
- Regression risk when adding features
- Slow feedback loop

**Remediation Plan** (Phase 2):
1. Add unit tests for ViewModels
2. Add integration tests for NetworkClient
3. Add Compose UI tests for critical screens
4. Set up CI/CD pipeline with automated testing

**Priority**: Medium (acceptable for MVP, critical for Phase 2)

#### 17.2.2 Error Handling

**Issue**: Inconsistent error handling patterns

**Details**:
- Some functions use Result<T>, others use try/catch
- Error messages not user-friendly in all cases
- No centralized error handling

**Impact**: Low
- Users may see technical error messages
- Debugging errors can be challenging

**Remediation Plan**:
1. Standardize on Result<T> for all network operations
2. Create user-friendly error message mapping
3. Implement global error handler in DPMApplication

**Priority**: Low (Phase 2)

#### 17.2.3 ProGuard Configuration

**Issue**: ProGuard rules not configured for release builds

**Details**:
- Release builds not tested
- Gson, ExoPlayer, DataStore may break with R8 enabled
- No obfuscation configured

**Impact**: Medium
- Cannot create release builds yet
- APK size not optimized

**Remediation Plan**:
1. Configure ProGuard rules for all libraries
2. Test release build thoroughly
3. Measure APK size reduction

**Priority**: Medium (required before production deployment)

#### 17.2.4 Hardcoded Strings

**Issue**: Some UI strings are hardcoded (not in strings.xml)

**Details**:
- Error messages, labels, hints in composables
- Makes internationalization difficult
- Violates Android best practices

**Impact**: Low
- App only supports English
- Future localization requires refactoring

**Remediation Plan**:
1. Extract all strings to `strings.xml`
2. Use `stringResource()` in composables
3. Add string-lint checks in CI/CD

**Priority**: Low (Phase 2)

---

### 17.3 Resolved Issues

#### 17.3.1 NetworkManager Singleton Pattern

**Issue**: Each ViewModel had separate NetworkClient instances

**Symptoms**:
- Settings screen status not updating on first connect
- Camera screen not showing heartbeat status
- StateFlow references recreated when settings changed

**Root Cause**:
- SettingsViewModel and CameraViewModel created independent NetworkClient instances
- No shared connection state

**Resolution** (October 25, 2025):
- Created `NetworkManager.kt` singleton object
- Single NetworkClient instance app-wide
- Stable StateFlow shared across ViewModels

**Outcome**: ✅ Both screens now show real-time connection status

**Commit**: `fbf382d` - [FIX] NetworkManager singleton pattern

---

#### 17.3.2 Auto-Connect on App Launch

**Issue**: Auto-connect only happened when entering Settings screen

**Symptoms**:
- User stayed on Camera screen → no connection attempt
- Had to open Settings to trigger connection
- Poor user experience

**Root Cause**:
- Auto-connect logic in SettingsViewModel init
- SettingsViewModel only created when Settings screen opened

**Resolution** (October 25, 2025):
- Created `DPMApplication.kt` custom Application class
- Loads settings and initializes NetworkManager on app startup
- Auto-connects before any UI shown

**Outcome**: ✅ Connection starts immediately when app launches

**Commit**: `05ff7e0` - [FIX] Auto-connect now happens on app launch

---

#### 17.3.3 Missing INTERNET Permission

**Issue**: App would crash when attempting network operations

**Symptoms**:
- SecurityException when creating sockets
- App couldn't connect to air-side

**Root Cause**:
- `<uses-permission android:name="android.permission.INTERNET" />` not in AndroidManifest.xml

**Resolution** (October 24, 2025):
- Added INTERNET permission to AndroidManifest.xml
- Added ACCESS_NETWORK_STATE for network monitoring

**Outcome**: ✅ Network operations work correctly

**Commit**: `b3c25c2` - [FIX] CRITICAL - Add missing INTERNET permission

---

#### 17.3.4 Smart Cast Errors in SystemStatusScreen

**Issue**: Kotlin smart cast errors when using sealed class states

**Symptoms**:
- Compilation errors in when expressions
- "Smart cast to 'VideoState.Connected' is impossible"

**Root Cause**:
- Sealed class instance captured in lambda
- Kotlin can't guarantee immutability

**Resolution**:
- Use explicit locals for sealed class instances:
  ```kotlin
  when (val state = videoState) {
      is VideoState.Connected -> { /* use state.resolution */ }
  }
  ```

**Outcome**: ✅ Compilation successful, smart casts work

**Commit**: Included in SystemStatusScreen implementation

---

### 17.4 Future Considerations

**Performance Optimization** (Phase 2):
- Profile app startup time
- Optimize video buffering strategy
- Reduce memory usage
- Battery consumption analysis

**Accessibility** (Phase 2+):
- Add content descriptions for screen readers
- Support larger text sizes
- High contrast mode for outdoor use
- Voice commands for hands-free operation

**Internationalization** (Phase 3+):
- Extract all strings to resources
- Support multiple languages
- RTL layout testing

---

## 18. Future Roadmap

### 18.1 Phase 2: Feature Expansion

**Planned Features** (Next 3-6 months):

#### 18.1.1 Content Management

**Downloads Screen**:
- [ ] List captured images/videos from air-side
- [ ] Thumbnail grid display
- [ ] Download progress indicators
- [ ] Delete functionality
- [ ] Preview/playback functionality

**Implementation**:
- New `content` package
- `content.list` command (query air-side storage)
- `content.download` command (file transfer)
- `content.delete` command (remote deletion)
- Local storage management (MediaStore API)

**Estimated Effort**: 2-3 weeks

---

#### 18.1.2 Gimbal Control

**Gimbal Control Interface**:
- [ ] Joystick/slider for angle control
- [ ] Rate control mode (continuous movement)
- [ ] Mode switching (follow, lock, FPV)
- [ ] Home position button
- [ ] Parameter tuning (PID gains)

**Commands to Implement**:
- `gimbal.set_angle(pitch, yaw, roll)`
- `gimbal.set_rate(pitch_rate, yaw_rate)`
- `gimbal.set_mode(follow/lock/fpv)`
- `gimbal.home()`
- `gimbal.set_parameters(p, i, d)`

**UI Mockup**:
```
┌─────────────────────────────┐
│  Gimbal Control             │
├─────────────────────────────┤
│  Pitch: [======|====] 45°   │
│  Yaw:   [==========|] 0°    │
│  Roll:  [====|======] -10°  │
│                             │
│  Mode: [Follow ▼]           │
│  [Home Position]            │
└─────────────────────────────┘
```

**Estimated Effort**: 1-2 weeks

---

#### 18.1.3 Advanced Camera Features

**Extended Camera Commands**:
- [ ] `camera.focus` - Manual focus control
- [ ] `camera.set_focus_area` - Touch-to-focus
- [ ] `camera.record` - Video recording start/stop
- [ ] `camera.get_properties` - Air-side implementation
- [ ] `camera.set_property` - Air-side implementation

**UI Enhancements**:
- Focus peaking visualization
- Histogram display
- Zebra stripes (overexposure warning)
- Grid overlay (rule of thirds)
- Recording indicator with duration

**Estimated Effort**: 2 weeks

---

#### 18.1.4 Video Enhancements

**Recording Functionality**:
- [ ] Record live RTSP stream to local storage
- [ ] Recording controls (start/stop/pause)
- [ ] Playback of recorded videos
- [ ] Share recorded videos

**Snapshot Capture**:
- [ ] Capture still frame from live video
- [ ] Save to gallery
- [ ] Timestamp overlay

**Implementation**:
- Use ExoPlayer's MediaRecorder API
- Store to MediaStore (Android 10+ scoped storage)
- Background recording service

**Estimated Effort**: 2 weeks

---

### 18.2 Phase 3: Advanced Features

**Planned Features** (6-12 months):

#### 18.2.1 Mission Planning

**Mission Planning Interface**:
- Map view with waypoints
- Autonomous flight paths
- Automated camera triggers at waypoints
- Mission upload/download to drone

**Integration**:
- DJI SDK or open-source flight controller (PX4, ArduPilot)
- MAVLink protocol support
- KML/KMZ import/export

**Estimated Effort**: 4-6 weeks

---

#### 18.2.2 Telemetry Dashboard

**Real-Time Telemetry**:
- GPS position and altitude
- Battery voltage and current
- Flight mode and status
- Signal strength (RC, video)
- Home point and distance

**Visualization**:
- Artificial horizon
- Speed/altitude gauges
- Map with drone position
- Telemetry graphs (battery, altitude over time)

**Estimated Effort**: 3-4 weeks

---

#### 18.2.3 Multi-Device Support

**Tablet/Phone Optimization**:
- Responsive layouts for different screen sizes
- Phone: Compact vertical layout
- Tablet: Expanded horizontal layout with more controls
- Foldable support

**Desktop Support** (Android on Chrome OS):
- Mouse and keyboard controls
- Keyboard shortcuts (Space = capture, R = record, etc.)
- Multi-window support

**Estimated Effort**: 2-3 weeks

---

### 18.3 Phase 4: Enterprise Features

**Planned Features** (12+ months):

#### 18.3.1 Cloud Sync

**Cloud Features**:
- Automatic media upload to cloud (Google Drive, AWS S3)
- Cross-device settings sync
- Flight log cloud storage
- Team collaboration (share missions, media)

**Implementation**:
- Firebase integration (Auth, Storage, Firestore)
- WorkManager for background uploads
- Conflict resolution for settings

**Estimated Effort**: 4-6 weeks

---

#### 18.3.2 Advanced Analytics

**Flight Analytics**:
- Flight time tracking
- Battery usage analytics
- Media storage analytics
- Network performance metrics

**Reporting**:
- PDF flight reports
- CSV data export
- Grafana dashboards (via API)

**Estimated Effort**: 3-4 weeks

---

#### 18.3.3 Safety Features

**Safety Enhancements**:
- Low battery warnings
- Geofence enforcement
- Return-to-home triggers
- Pre-flight checklists
- Emergency stop button

**Regulatory Compliance**:
- Flight log export (regulatory requirements)
- No-fly zone database integration
- Remote ID support (FAA/EASA)

**Estimated Effort**: 4-6 weeks

---

### 18.4 Performance Goals

**Target Metrics for Phase 2**:
- App startup: < 2 seconds (cold start)
- Command latency: < 100ms (ground → air)
- Video latency: < 500ms (camera → display)
- Battery consumption: < 5% per hour (screen on, video streaming)
- Memory usage: < 100 MB RAM

**Optimization Strategies**:
- Use Baseline Profiles for faster startup
- Enable R8 code shrinking for smaller APK
- Profile-guided optimization (PGO)
- Lazy initialization of non-critical components
- Image compression for thumbnails

---

### 18.5 Long-Term Vision

**5-Year Roadmap**:

**Year 1**: Full feature parity with commercial ground stations (DJI Go 4 level)

**Year 2**: Advanced features (mission planning, telemetry, multi-device)

**Year 3**: Enterprise features (cloud sync, analytics, team collaboration)

**Year 4**: AI-powered features (object tracking, intelligent flight modes)

**Year 5**: Autonomous operations (fully automated missions, swarm support)

---

### 18.6 Technology Adoption

**Emerging Technologies to Monitor**:

**WebRTC for Video**:
- Ultra-low latency (< 200ms)
- Better than RTSP for interactive use cases
- Consider migrating in Phase 3

**Jetpack Compose Multiplatform**:
- Share UI code with iOS, desktop, web
- Reduce development effort for multi-platform
- Evaluate when stable (2026+)

**Kotlin Multiplatform Mobile (KMM)**:
- Share business logic with iOS
- Network layer, protocol handling
- ViewModels can be shared

**Edge AI**:
- On-device object detection (TensorFlow Lite)
- Intelligent framing (keep subject centered)
- Gesture control (hand tracking)

---

### 18.7 Community & Open Source

**Open Source Considerations**:

**Potential Open Source Components**:
- DPM protocol client library (reusable by others)
- Camera control UI components (Jetpack Compose library)
- RTSP streaming wrapper (simplified ExoPlayer setup)

**Benefits of Open Source**:
- Community contributions (bug fixes, features)
- Third-party integrations (other ground stations)
- Increased adoption and visibility
- Code review and security audits

**Licensing**:
- Consider MIT or Apache 2.0 for maximum reusability
- Separate proprietary features (cloud sync, enterprise) from open core

---

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ Complete |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ✅ Complete |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ✅ Complete |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ✅ **COMPLETE** |

**🎉 ALL PHASES COMPLETE 🎉**

---

**Document Metadata**

**Generated**: October 25, 2025
**Phase**: 4 of 4 (**COMPLETE**)
**Sections Complete**: 1-18 (100%)
**Total Lines**: ~5,800 lines
**Total Documentation**: Complete Android Architecture Reference

---

**End of Document**

*This comprehensive architecture documentation provides complete coverage of the DPM Android application, from executive summary through future roadmap. All 18 sections document the current implementation, design decisions, and plans for future development.*

**Document Version**: 1.0.0
**Last Updated**: October 25, 2025
**Authors**: Claude Code (AI-assisted documentation generation)
**Maintainers**: DPM Development Team

---
