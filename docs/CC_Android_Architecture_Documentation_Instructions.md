# Claude Code: Android Architecture Documentation - Phased Approach

## 📋 Overview

**Purpose**: Generate comprehensive Android architecture documentation in 4 phases to avoid API token limits.

**Target File**: `android/docs/ANDROID_ARCHITECTURE.md`

**Total Sections**: 18 sections across 4 phases

**Estimated Time**: 4-6 hours (1-1.5 hours per phase)

**Problem Solved**: Avoids "Claude's response exceeded the 32000 output token maximum" error

---

## 🎯 Why Phased Approach?

Claude Code has a 32,000 output token limit. Generating the entire architecture document (~10,000 lines) in one response exceeds this limit.

**Solution**: Break documentation into 4 manageable phases, each creating 4-5 sections.

---

## 📐 Phase Breakdown

| Phase | Sections | Content | Est. Tokens |
|-------|----------|---------|-------------|
| **1** | 1-3 | Executive Summary, Project Structure, Architecture Overview | ~15,000 |
| **2** | 4-7 | Core Components, Data Layer, Network Layer, UI Layer | ~18,000 |
| **3** | 8-11 | State Management, Video Streaming, Navigation, Dependencies | ~15,000 |
| **4** | 12-18 | Configuration, Testing, Build, Conventions, Deployment, Issues, Roadmap | ~12,000 |

---

## 🚀 Phase 1: Foundation (Sections 1-3)

### Task for Claude Code

```
Task: Create ANDROID_ARCHITECTURE.md - Phase 1 of 4

Create file: android/docs/ANDROID_ARCHITECTURE.md

Generate comprehensive documentation for SECTIONS 1-3 ONLY:

═══════════════════════════════════════════════════════════════════

## 1. Executive Summary

### 1.1 Project Overview
[Brief description of DPM Android app, purpose, and goals]

### 1.2 Technology Stack
List ALL major technologies with versions:
- Kotlin version
- Jetpack Compose version
- Target Android API
- Minimum Android API
- All major libraries

### 1.3 Key Features
Bullet list of implemented features:
- Camera control
- Video streaming
- Network communication
- Settings management
- [All others]

### 1.4 Development Status
Current phase, completed features, in-progress features, planned features

### 1.5 Target Hardware
- SkyDroid H16 Ground Station specs
- Android version
- Hardware capabilities

═══════════════════════════════════════════════════════════════════

## 2. Project Structure

### 2.1 Directory Layout
Complete directory tree showing:
```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/uk/unmannedsystems/dpm_android/
│   │   │   │   ├── [LIST ALL PACKAGES]
│   │   │   │   ├── [WITH SUBPACKAGES]
│   │   │   │   └── [COMPLETE STRUCTURE]
│   │   │   ├── res/
│   │   │   │   ├── [LIST ALL RESOURCE DIRS]
│   │   │   └── AndroidManifest.xml
│   │   ├── test/
│   │   └── androidTest/
│   └── build.gradle.kts
├── gradle/
│   └── libs.versions.toml
├── build.gradle.kts
└── settings.gradle.kts
```

### 2.2 Package Structure
For EACH package found, document:
- Package name: `uk.unmannedsystems.dpm_android.[package]`
- Purpose: [Brief description]
- Number of files: [count]
- Key classes: [List main classes]

Example:
```
Package: uk.unmannedsystems.dpm_android.ui.screens
Purpose: Composable screens for app navigation
Files: 3
Key classes:
- CameraScreen.kt - Main camera control interface
- SettingsScreen.kt - Application settings
- [Others]
```

### 2.3 File Naming Conventions
Document patterns used:
- ViewModels: `[Feature]ViewModel.kt`
- Screens: `[Feature]Screen.kt`
- Repositories: `[Feature]Repository.kt`
- Data models: `[Entity].kt`
- UI components: `[Component].kt`

═══════════════════════════════════════════════════════════════════

## 3. Architecture Overview

### 3.1 High-Level Architecture Diagram

Create ASCII diagram showing:
```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐    │
│  │   Screens    │  │  Composables │  │ Navigation│    │
│  │ (Jetpack     │  │  (UI Comp.)  │  │           │    │
│  │  Compose)    │  │              │  │           │    │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘    │
│         │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────┐
│                  ViewModel Layer                         │
│  [Show ViewModel architecture]                          │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Data Layer                            │
│  [Show repositories, network, storage]                  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Design Patterns

Document each pattern used:

#### 3.2.1 MVVM (Model-View-ViewModel)
- Explain how MVVM is implemented
- Show typical flow: View → ViewModel → Model → ViewModel → View
- Include code example from actual project

#### 3.2.2 Repository Pattern
- Explain repository usage
- Show example from actual code
- Document data source abstraction

#### 3.2.3 Single Source of Truth
- Explain state management approach
- Document how state flows

#### 3.2.4 Unidirectional Data Flow
- Explain UI event → ViewModel → State → UI cycle
- Include diagram

### 3.3 Layer Responsibilities

#### Presentation Layer
- Displays UI using Jetpack Compose
- Observes ViewModel state
- Handles user interactions
- Navigation between screens
- [Details]

#### ViewModel Layer
- Manages UI state
- Handles business logic
- Coordinates repositories
- Exposes state via StateFlow/LiveData
- [Details]

#### Data Layer
- Network communication (TCP/UDP)
- Settings persistence (DataStore)
- Data transformation
- Error handling
- [Details]

### 3.4 Data Flow Diagrams

Create textual diagrams showing:

#### User Action Flow:
```
User Tap Button (UI)
    ↓
Composable calls ViewModel function
    ↓
ViewModel processes request
    ↓
ViewModel updates StateFlow
    ↓
Composable recomposes with new state
    ↓
UI updates
```

#### Network Communication Flow:
```
ViewModel sends command
    ↓
NetworkClient (TCP)
    ↓
Air-Side (Raspberry Pi)
    ↓
[Response/Status flows back]
```

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Use ACTUAL code from the codebase (not pseudo-code)
✅ Include complete package listings from actual project structure
✅ Include ASCII diagrams for architecture
✅ Be comprehensive and detailed
✅ Keep output under 20,000 tokens
✅ Use proper markdown formatting

At the end of Section 3, add this status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ **COMPLETE** |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ⏳ Pending |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ⏳ Pending |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ⏳ Pending |

**Next Action**: Run Phase 2 to continue documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Android architecture documentation - Phase 1 (Sections 1-3)"
```

---

## 🚀 Phase 2: Core Implementation (Sections 4-7)

### Task for Claude Code

```
Task: Continue ANDROID_ARCHITECTURE.md - Phase 2 of 4

IMPORTANT: APPEND to existing file: android/docs/ANDROID_ARCHITECTURE.md
(Do not overwrite - read the file first, then append new sections)

Generate SECTIONS 4-7:

═══════════════════════════════════════════════════════════════════

## 4. Core Components

### 4.1 MainActivity

**File**: `app/src/main/java/uk/unmannedsystems/dpm_android/MainActivity.kt`

**Purpose**: [Description from actual code]

**Code Structure**:
```kotlin
// Include actual MainActivity class structure
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Document what happens
    }
}
```

**Responsibilities**:
- [List actual responsibilities]

**Lifecycle Management**:
- [Document lifecycle handling]

**Dependencies**:
- [List dependencies used]

### 4.2 DPMApplication (if exists)

**File**: [path]

**Purpose**: [Description]

[Document application class completely]

### 4.3 Navigation System

**Implementation**: [Describe navigation approach]

**Routes**: [List all navigation routes]

**Navigation Flow**:
```
App Launch
    ↓
[Default Screen]
    ├→ [Screen 2]
    ├→ [Screen 3]
    └→ [Others]
```

═══════════════════════════════════════════════════════════════════

## 5. Data Layer

### 5.1 Data Models

Document EVERY data class found in the project:

#### CameraState (Example - repeat for all)
**File**: `[actual path]`

```kotlin
// Include actual data class definition
data class CameraState(
    val shutter: String = "1/125",
    val aperture: String = "f/4.0",
    val iso: Int = 800,
    // ... all fields
)
```

**Fields**:
- `shutter: String` - Shutter speed value (e.g., "1/125")
- `aperture: String` - Aperture value (e.g., "f/4.0")
- `iso: Int` - ISO sensitivity value
- [Document ALL fields with descriptions]

**Usage**:
- Used by: [List ViewModels/Screens that use this]
- Purpose: [Explain why this data structure exists]

[REPEAT FOR ALL DATA CLASSES]

### 5.2 Repositories

Document EVERY repository:

#### SettingsRepository (Example - repeat for all)
**File**: `[actual path]`

**Purpose**: [Description]

**Data Sources**:
- DataStore Preferences
- [Others]

**Public API**:
```kotlin
// Include actual function signatures
suspend fun saveSettings(settings: Settings)
fun getSettings(): Flow<Settings>
// ... all public functions
```

**Implementation Details**:
- [Describe how it works]
- [Explain DataStore usage]
- [Error handling approach]

[REPEAT FOR ALL REPOSITORIES]

### 5.3 DataStore Configuration

**Keys Used**:
```kotlin
// List ALL DataStore keys from actual code
private val SERVER_IP = stringPreferencesKey("server_ip")
private val SERVER_PORT = intPreferencesKey("server_port")
// ... ALL keys
```

**Data Persistence Strategy**:
[Explain how settings are persisted]

**Default Values**:
[List all default values]

═══════════════════════════════════════════════════════════════════

## 6. Network Layer

### 6.1 Network Architecture Diagram

```
┌────────────────────────────────────┐
│       ViewModel Layer              │
│  ┌──────────────────────────────┐  │
│  │   CameraViewModel            │  │
│  │   - Sends commands           │  │
│  │   - Receives status          │  │
│  └───────────┬──────────────────┘  │
└──────────────┼─────────────────────┘
               │
┌──────────────▼─────────────────────┐
│       Network Client Layer         │
│  ┌──────────────────────────────┐  │
│  │   NetworkClient              │  │
│  │   - TCP command sender       │  │
│  │   - UDP status listener      │  │
│  │   - Heartbeat manager        │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │   Air-Side (Pi)      │
    │   10.0.1.20:5000     │
    └──────────────────────┘
```

### 6.2 NetworkClient Implementation

**File**: `[actual path]`

**Purpose**: [Description]

**Class Structure**:
```kotlin
// Include actual class structure
class NetworkClient {
    // Document actual implementation
}
```

**TCP Communication**:
- Port: 5000
- Protocol: [Describe]
- Connection management: [Explain]
- Error handling: [Document]

**UDP Communication**:
- Port: 5001 (status)
- Port: 5002 (heartbeat)
- Broadcast handling: [Explain]

**Code Examples**:
```kotlin
// Include actual code snippets for:
// - Sending commands
// - Receiving status
// - Heartbeat mechanism
```

### 6.3 Protocol Implementation

**Message Format**:
```json
{
    "protocol_version": "1.0",
    "message_type": "command",
    "sequence_id": 123,
    "timestamp": 1234567890,
    "payload": { }
}
```

**Command Examples**:
[List actual commands used with examples]

**Status Updates**:
[Document status message structure]

**Error Handling**:
[Explain error handling strategy]

═══════════════════════════════════════════════════════════════════

## 7. UI Layer

### 7.1 Jetpack Compose Architecture

**Theme Configuration**:
**File**: `[path to Theme.kt]`

```kotlin
// Include actual theme code
@Composable
fun DPMTheme() {
    // Actual implementation
}
```

**Colors**:
[List color scheme from actual code]

**Typography**:
[Document typography from actual code]

### 7.2 Screens Documentation

Document EVERY screen:

#### CameraScreen (Example - repeat for all)
**File**: `[actual path]`

**Purpose**: [Description]

**Layout Structure**:
```
Box (Full Screen)
├── FullScreenVideoPlayer (Background Layer)
└── CameraControlsOverlay (Foreground Layer)
    ├── CameraSettingsPanel (Top-Left)
    ├── Title (Top-Center)
    ├── CaptureButton (Center-Bottom)
    ├── FileFormatButtons (Bottom-Left)
    └── StatusIndicators (Bottom-Right)
```

**Code Structure**:
```kotlin
@Composable
fun CameraScreen(
    // Include actual parameters
) {
    // Document structure
}
```

**ViewModel Dependencies**:
- Uses: [List ViewModels]

**User Interactions**:
- [Action 1] → [Effect]
- [Action 2] → [Effect]
- [All interactions]

**State Observation**:
```kotlin
// Show how state is observed
val cameraState by viewModel.cameraState.collectAsState()
```

[REPEAT FOR ALL SCREENS]

### 7.3 Reusable Composable Components

Document EVERY reusable component:

#### FullScreenVideoPlayer (Example)
**File**: `[path]`

**Purpose**: [Description]

**Parameters**:
```kotlin
@Composable
fun FullScreenVideoPlayer(
    rtspUrl: String,
    modifier: Modifier = Modifier,
    // ... all parameters
)
```

**Usage Example**:
```kotlin
// Show actual usage from code
FullScreenVideoPlayer(
    rtspUrl = "rtsp://...",
    modifier = Modifier.fillMaxSize()
)
```

[REPEAT FOR ALL REUSABLE COMPONENTS]

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read existing document first for context
✅ Append sections (don't overwrite)
✅ Use ACTUAL code from codebase
✅ Document EVERY class found
✅ Include code examples
✅ Keep under 20,000 tokens

Update the status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ Complete |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ✅ **COMPLETE** |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ⏳ Pending |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ⏳ Pending |

**Next Action**: Run Phase 3 to continue documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Android architecture documentation - Phase 2 (Sections 4-7)"
```

---

## 🚀 Phase 3: Advanced Features (Sections 8-11)

### Task for Claude Code

```
Task: Continue ANDROID_ARCHITECTURE.md - Phase 3 of 4

IMPORTANT: APPEND to existing file: android/docs/ANDROID_ARCHITECTURE.md
(Read file first to maintain consistency, then append)

Generate SECTIONS 8-11:

═══════════════════════════════════════════════════════════════════

## 8. State Management

### 8.1 State Flow Architecture

**Pattern Used**: [Describe state management pattern]

**Flow Diagram**:
```
User Action (UI Event)
    ↓
Composable calls ViewModel function
    ↓
ViewModel updates MutableStateFlow
    ↓
StateFlow emits new value
    ↓
Composable recomposes
    ↓
UI displays updated state
```

### 8.2 ViewModels Documentation

Document EVERY ViewModel in detail:

#### CameraViewModel (Example - repeat for all)
**File**: `[actual path]`

**Purpose**: [Description]

**State Objects**:
```kotlin
// Include actual StateFlow declarations
private val _cameraState = MutableStateFlow(CameraState())
val cameraState: StateFlow<CameraState> = _cameraState.asStateFlow()

private val _connectionState = MutableStateFlow(ConnectionState.Disconnected)
val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

// ... ALL state objects
```

**State Management Pattern**:
```kotlin
// Show how state is updated (actual code)
fun updateShutter(value: String) {
    _cameraState.update { it.copy(shutter = value) }
    // Network call to air-side
    networkClient.sendCommand(...)
}
```

**Public API**:
```kotlin
// List ALL public functions with signatures
fun captureImage()
fun updateShutter(value: String)
fun updateISO(value: Int)
fun updateAperture(value: String)
// ... ALL functions with descriptions
```

**Dependencies**:
- NetworkClient
- SettingsRepository
- [All dependencies]

**Lifecycle**:
- Initialization: [How ViewModel initializes]
- Cleanup: [How resources are cleaned up]

**Error Handling**:
[Document error handling approach]

**Threading**:
[Document coroutine usage, viewModelScope, etc.]

[REPEAT FOR ALL VIEWMODELS]

### 8.3 State Objects Reference

Complete documentation of ALL state data classes:

[Document each state object with all fields and their purposes]

═══════════════════════════════════════════════════════════════════

## 9. Video Streaming

### 9.1 Video Streaming Architecture

```
R16 Air Unit (RTSP Server)
    ↓ RTSP Stream (rtsp://192.168.1.10:8554/H264Video)
ExoPlayer (Android)
    ↓
PlayerView (AndroidView in Compose)
    ↓
FullScreenVideoPlayer Composable
    ↓
CameraScreen
```

### 9.2 ExoPlayer Integration

**Dependencies**:
```kotlin
// From build.gradle.kts
implementation("androidx.media3:media3-exoplayer:1.2.0")
implementation("androidx.media3:media3-ui:1.2.0")
implementation("androidx.media3:media3-exoplayer-rtsp:1.2.0")
```

**VideoPlayerViewModel**:
**File**: `[actual path]`

```kotlin
// Include actual ViewModel code
class VideoPlayerViewModel : ViewModel() {
    // Complete implementation documentation
}
```

**Video States**:
```kotlin
sealed class VideoState {
    object Disconnected : VideoState()
    object Connecting : VideoState()
    data class Connected(val resolution: String) : VideoState()
    data class Error(val message: String) : VideoState()
}
```

**Player Lifecycle**:
1. Initialization: [Describe]
2. Connection: [Describe]
3. Playback: [Describe]
4. Error handling: [Describe]
5. Cleanup: [Describe]

### 9.3 Video Settings

**Configuration**:
```kotlin
data class VideoStreamSettings(
    val rtspUrl: String,
    val autoConnect: Boolean,
    val aspectRatioMode: AspectRatioMode,
    val lowLatencyMode: Boolean
)
```

**Settings Persistence**:
[Document how video settings are saved/loaded]

**UI Integration**:
[Document how video is displayed on CameraScreen]

═══════════════════════════════════════════════════════════════════

## 10. Navigation

### 10.1 Navigation Implementation

**Approach**: [Describe navigation system used]

**Navigation Graph**:
[Document navigation structure]

### 10.2 Routes and Destinations

**Route Definitions**:
```kotlin
// If using sealed class/enum
sealed class Screen(val route: String) {
    object Camera : Screen("camera")
    object Settings : Screen("settings")
    // ... ALL routes
}
```

**Navigation Flow**:
```
App Launch
    ↓
Splash/Initialize
    ↓
Camera Screen (default destination)
    ├→ Settings Screen
    ├→ [Other screens]
    └→ [Other screens]
```

### 10.3 Navigation Parameters

[Document how parameters are passed between screens]

**Deep Links**: [If supported, document]

═══════════════════════════════════════════════════════════════════

## 11. Dependencies

### 11.1 Gradle Dependencies

#### Core Android Dependencies
```kotlin
// From build.gradle.kts - include ACTUAL versions
implementation("androidx.core:core-ktx:1.x.x")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.x.x")
implementation("androidx.activity:activity-compose:1.x.x")
// ... LIST ALL with actual versions
```

**Purpose of each**:
- `core-ktx`: [Explain]
- `lifecycle-runtime-ktx`: [Explain]
- [All dependencies with explanations]

#### Jetpack Compose Dependencies
```kotlin
implementation(platform("androidx.compose:compose-bom:2023.xx.xx"))
implementation("androidx.compose.ui:ui")
implementation("androidx.compose.material3:material3")
// ... LIST ALL
```

#### ExoPlayer (Video Streaming)
```kotlin
implementation("androidx.media3:media3-exoplayer:1.2.0")
implementation("androidx.media3:media3-ui:1.2.0")
implementation("androidx.media3:media3-exoplayer-rtsp:1.2.0")
```

**Why ExoPlayer**: [Explain choice]

#### Network Dependencies
[List any network libraries used]

#### DataStore
```kotlin
implementation("androidx.datastore:datastore-preferences:1.x.x")
```

**Why DataStore**: [Explain]

#### JSON Processing
[If using Gson, Moshi, kotlinx.serialization, etc.]

#### Other Dependencies
[List ALL other dependencies with versions and purposes]

### 11.2 Gradle Plugins

```kotlin
// From build.gradle.kts
id("com.android.application") version "x.x.x"
id("org.jetbrains.kotlin.android") version "x.x.x"
// ... ALL plugins
```

### 11.3 Dependency Version Management

**Using libs.versions.toml**:
```toml
// Include actual content from libs.versions.toml
[versions]
kotlin = "x.x.x"
compose = "x.x.x"
// ... ALL versions

[libraries]
// ... ALL libraries

[plugins]
// ... ALL plugins
```

### 11.4 Build Configuration

**Compile SDK**: [Version]
**Min SDK**: [Version]  
**Target SDK**: [Version]

**Build Features**:
```kotlin
buildFeatures {
    compose = true
    // ... others
}
```

**Compose Compiler**:
```kotlin
composeOptions {
    kotlinCompilerExtensionVersion = "x.x.x"
}
```

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read existing document for consistency
✅ Append sections (don't overwrite)
✅ Use ACTUAL code and versions
✅ Document EVERY dependency
✅ Explain purpose of each dependency
✅ Keep under 20,000 tokens

Update status tracker:

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ Complete |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ✅ Complete |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ✅ **COMPLETE** |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ⏳ Pending |

**Next Action**: Run Phase 4 to complete documentation

═══════════════════════════════════════════════════════════════════

Git commit message:
"[DOCS] Add Android architecture documentation - Phase 3 (Sections 8-11)"
```

---

## 🚀 Phase 4: Final Sections (Sections 12-18)

### Task for Claude Code

```
Task: Complete ANDROID_ARCHITECTURE.md - Phase 4 of 4 (FINAL)

IMPORTANT: APPEND to existing file: android/docs/ANDROID_ARCHITECTURE.md
(Read entire document to ensure consistency, then append final sections)

Generate SECTIONS 12-18:

═══════════════════════════════════════════════════════════════════

## 12. Configuration & Settings

### 12.1 Build Configuration

**Build Types**:
```kotlin
// From build.gradle.kts
buildTypes {
    release {
        isMinifyEnabled = true
        proguardFiles(...)
        // ... actual configuration
    }
    debug {
        isDebuggable = true
        // ... actual configuration
    }
}
```

### 12.2 Application Settings

**Default Settings Values**:
[List ALL default values from actual code]

**Settings Categories**:
1. Network Settings
   - Server IP: [default]
   - TCP Port: [default]
   - UDP Port: [default]
2. Video Settings
   - RTSP URL: [default]
   - Auto-connect: [default]
3. Camera Settings
   - [All camera defaults]
4. [Other categories]

### 12.3 AndroidManifest.xml

**Key Configurations**:
```xml
<!-- Include relevant parts of actual manifest -->
<uses-permission android:name="android.permission.INTERNET" />
<!-- ... all permissions -->

<application
    android:name=".DPMApplication"
    <!-- ... actual configuration -->
>
```

**Permissions Required**:
- INTERNET: [Why]
- [All other permissions with explanations]

═══════════════════════════════════════════════════════════════════

## 13. Testing

### 13.1 Test Structure

**Test Directories**:
```
app/src/
├── test/              # Unit tests
│   └── [List actual test files if any]
└── androidTest/       # Instrumented tests
    └── [List actual test files if any]
```

### 13.2 Unit Tests

[If tests exist, document them]
[If no tests yet, note: "To be implemented"]

### 13.3 Integration Tests

[Document any integration tests]

### 13.4 UI Tests

[Document any Compose UI tests]

### 13.5 Test Coverage

**Current Coverage**: [If measurable, note it; otherwise "Not yet measured"]

**Testing Strategy**: [Document intended testing approach]

═══════════════════════════════════════════════════════════════════

## 14. Build System

### 14.1 Gradle Build Process

**Build Command**:
```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Install to device
./gradlew installDebug
```

### 14.2 Build Variants

[Document any product flavors or build variants]

### 14.3 ProGuard/R8 Configuration

**Minification**: [Enabled in release? Document rules]

**ProGuard Rules**:
```
# From proguard-rules.pro (if custom rules exist)
[Include relevant rules]
```

### 14.4 Signing Configuration

[Document signing setup - without exposing sensitive info]

═══════════════════════════════════════════════════════════════════

## 15. Code Conventions

### 15.1 Kotlin Style Guide

**Indentation**: 4 spaces

**Naming Conventions**:
- Classes: `PascalCase`
- Functions: `camelCase`
- Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Composables: `PascalCase`

**Examples from actual code**:
```kotlin
// Show examples of naming from project
class CameraViewModel { }
fun updateShutter() { }
val shutterSpeed = "1/125"
const val DEFAULT_PORT = 5000
@Composable fun CameraScreen() { }
```

### 15.2 Compose Conventions

**Composable Structure**:
[Document patterns used]

**State Management**:
[Document state hoisting patterns]

**Modifier Usage**:
[Document modifier conventions]

### 15.3 File Organization

**Package Organization**:
- `ui.screens` - Screen composables
- `ui.components` - Reusable components
- `ui.theme` - Theme definitions
- `viewmodel` - ViewModels
- `data` - Data models and repositories
- `network` - Network clients
- [All packages with purposes]

### 15.4 Documentation Standards

**KDoc Comments**:
```kotlin
/**
 * Example from actual code showing documentation style
 */
```

### 15.5 Git Commit Conventions

**Commit Message Format**:
```
[TYPE] Brief description

Detailed explanation if needed

Examples:
[FEAT] Add video streaming support
[FIX] Resolve TCP connection timeout issue
[REFACTOR] Improve state management in CameraViewModel
[DOCS] Update architecture documentation
[TEST] Add unit tests for NetworkClient
```

═══════════════════════════════════════════════════════════════════

## 16. Deployment

### 16.1 Build for H16 Hardware

**Target Device**: SkyDroid H16 Ground Station
- Android Version: 7.1.2 (API 25)
- Architecture: [ARM/ARM64]

**Build Command**:
```bash
./gradlew assembleRelease
```

**Output Location**:
```
app/build/outputs/apk/release/app-release.apk
```

### 16.2 Installation Methods

**ADB Installation**:
```bash
# Connect H16 via USB
adb devices

# Install APK
adb install app/build/outputs/apk/release/app-release.apk
```

**Wireless ADB** (if supported):
```bash
adb connect <H16_IP>:5555
adb install app-release.apk
```

### 16.3 Release Checklist

Before releasing to H16:
- [ ] Update version in build.gradle.kts
- [ ] Test all features on target hardware
- [ ] Verify network connectivity
- [ ] Test video streaming with actual R16
- [ ] Test camera control with Air-Side
- [ ] Verify settings persistence
- [ ] Check performance/battery usage
- [ ] Sign APK if required
- [ ] Test installation process
- [ ] Document known issues

### 16.4 Version Management

**Current Version**: [From build.gradle.kts]

**Version Naming**:
```kotlin
versionCode = 1
versionName = "1.0.0"
```

**Versioning Strategy**: [Semantic versioning / custom]

═══════════════════════════════════════════════════════════════════

## 17. Known Issues & Technical Debt

### 17.1 Current Limitations

1. **Network**
   - [List any known network issues]
   - Example: "TCP reconnection needs improvement"

2. **Video Streaming**
   - [List video-related limitations]
   - Example: "ExoPlayer latency ~500ms, cannot reduce further"

3. **Camera Control**
   - [List camera-related limitations]

4. **UI/UX**
   - [List UI issues or limitations]

5. **Performance**
   - [List performance concerns]

### 17.2 Technical Debt

Items that need refactoring or improvement:

1. **Code Quality**
   - [ ] Add unit tests for ViewModels
   - [ ] Add integration tests for network layer
   - [ ] Improve error handling in [specific component]
   - [Other items]

2. **Architecture**
   - [ ] Consider dependency injection (Hilt/Koin)
   - [ ] Refactor [specific component] for better testability
   - [Other items]

3. **Documentation**
   - [ ] Add KDoc comments to public APIs
   - [ ] Document network protocol edge cases
   - [Other items]

### 17.3 Known Bugs

[List any known bugs with workarounds if available]

### 17.4 Compatibility Issues

**Android Version Compatibility**:
- Minimum API 25 (Android 7.1.2)
- Tested on: [List tested versions]
- Known issues on: [List any problematic versions]

**Hardware Compatibility**:
- Optimized for: H16 Ground Station
- Other devices: [Status]

═══════════════════════════════════════════════════════════════════

## 18. Future Roadmap

### 18.1 Planned Features

**Phase 2 Features**:
- [ ] Sony SDK live view integration (secondary video source)
- [ ] Video recording functionality
- [ ] Content download from camera to ground station
- [ ] Advanced camera controls (picture profiles, etc.)
- [ ] Firmware update capability
- [Other Phase 2 items]

**Phase 3 Features**:
- [ ] Multiple camera support
- [ ] Advanced gimbal controls (calibration, etc.)
- [ ] Mission planning integration
- [ ] Telemetry overlay on video
- [Other Phase 3 items]

**Future Enhancements**:
- [ ] Offline mode support
- [ ] Advanced settings presets
- [ ] Better error recovery
- [ ] Performance optimizations
- [Other long-term items]

### 18.2 Planned Refactoring

1. **Dependency Injection**
   - Consider Hilt for better dependency management
   - Improve testability

2. **Modularization**
   - Split into feature modules
   - Improve build times

3. **State Management**
   - Consider MVI architecture for complex state
   - Improve state consistency

4. **Testing**
   - Achieve >80% test coverage
   - Add UI tests for all screens
   - Add integration tests for network layer

### 18.3 Performance Optimization

Future optimization targets:
- [ ] Reduce app startup time
- [ ] Optimize video streaming latency
- [ ] Reduce memory footprint
- [ ] Improve battery efficiency
- [ ] Optimize network communication

### 18.4 Documentation Improvements

- [ ] Add API documentation for public interfaces
- [ ] Create developer onboarding guide
- [ ] Add troubleshooting guide
- [ ] Create user manual
- [ ] Add video tutorials

═══════════════════════════════════════════════════════════════════

## 19. Appendices

### Appendix A: Glossary

**Terms and Abbreviations**:
- **DPM**: Drone Payload Manager
- **H16**: SkyDroid H16 Ground Station
- **R16**: SkyDroid R16 Air Unit
- **SBC**: Single Board Computer (Raspberry Pi)
- **RTSP**: Real Time Streaming Protocol
- **SDK**: Software Development Kit
- **API**: Application Programming Interface
- **MVVM**: Model-View-ViewModel
- **UI**: User Interface
- **UX**: User Experience
- [All other terms]

### Appendix B: External Resources

**Official Documentation**:
- Jetpack Compose: https://developer.android.com/jetpack/compose
- ExoPlayer: https://developer.android.com/guide/topics/media/exoplayer
- Kotlin Coroutines: https://kotlinlang.org/docs/coroutines-overview.html
- DataStore: https://developer.android.com/topic/libraries/architecture/datastore

**Project Resources**:
- GitHub Repository: [URL]
- Project Wiki: [URL if exists]
- Issue Tracker: [URL if exists]

**Related Documentation**:
- Air-Side Architecture: `sbc/docs/SBC_ARCHITECTURE.md`
- Protocol Specification: `docs/Command_Protocol_Specification_v1.0.md`
- Project Summary: `docs/Project_Summary_and_Action_Plan.md`

### Appendix C: Contact & Support

**Development Team**:
- [Team contact information if applicable]

**Support Channels**:
- [Support information if applicable]

═══════════════════════════════════════════════════════════════════

## 📋 Document Generation Status - FINAL

| Phase | Sections | Status |
|-------|----------|--------|
| **Phase 1** | 1-3: Executive Summary, Project Structure, Architecture Overview | ✅ Complete |
| **Phase 2** | 4-7: Core Components, Data Layer, Network Layer, UI Layer | ✅ Complete |
| **Phase 3** | 8-11: State Management, Video Streaming, Navigation, Dependencies | ✅ Complete |
| **Phase 4** | 12-18: Configuration, Testing, Build, Conventions, Deployment | ✅ **COMPLETE** |

**✅ DOCUMENTATION COMPLETE - ALL 18 SECTIONS GENERATED**

═══════════════════════════════════════════════════════════════════

---

**Document Metadata**

**Title**: DPM Android Application - Complete Architecture Documentation  
**Version**: 1.0  
**Last Updated**: [Date]  
**Generated By**: Claude Code (Phased Generation)  
**Total Sections**: 18  
**File**: `android/docs/ANDROID_ARCHITECTURE.md`  

**Generation Summary**:
- Phase 1: Sections 1-3 (Foundation)
- Phase 2: Sections 4-7 (Core Implementation)
- Phase 3: Sections 8-11 (Advanced Features)
- Phase 4: Sections 12-18 (Configuration & Future)

This document provides comprehensive architecture documentation for the DPM Android application, covering all aspects from high-level architecture to implementation details, dependencies, and future roadmap.

---

**END OF DOCUMENT**

═══════════════════════════════════════════════════════════════════

REQUIREMENTS:
✅ Read ENTIRE document for consistency
✅ Append final sections
✅ Use actual code and information
✅ Be thorough but concise
✅ Keep under 20,000 tokens
✅ Mark document as COMPLETE

Git commit message:
"[DOCS] Complete Android architecture documentation - Phase 4 (Sections 12-18)

- Add configuration and settings documentation
- Add testing structure and strategy
- Add build system documentation
- Add code conventions and standards
- Add deployment procedures for H16
- Document known issues and technical debt
- Add future roadmap and planned features
- Add appendices with glossary and resources

✅ All 18 sections complete
✅ Comprehensive architecture documentation finished"
```

---

## 📊 Progress Tracking Template

After each phase, Claude Code should update this status in the document:

```markdown
## 📋 Document Generation Status

| Phase | Sections | Est. Lines | Status | Date |
|-------|----------|------------|--------|------|
| **Phase 1** | 1-3: Foundation | ~500 | ✅ Complete | [date] |
| **Phase 2** | 4-7: Core Implementation | ~600 | ✅ Complete | [date] |
| **Phase 3** | 8-11: Advanced Features | ~500 | ✅ Complete | [date] |
| **Phase 4** | 12-18: Final Sections | ~400 | ✅ Complete | [date] |

**Total Estimated Lines**: ~2000+ lines of documentation
```

---

## ✅ Completion Checklist

After Phase 4, verify:

- [ ] All 18 sections are present and complete
- [ ] All code examples are from actual codebase
- [ ] All classes and components are documented
- [ ] All dependencies are listed with versions
- [ ] All diagrams are clear and accurate
- [ ] Table of contents is complete and linked
- [ ] Document status shows all phases complete
- [ ] Git commits made for each phase
- [ ] File is readable and well-formatted
- [ ] No placeholder text remains
- [ ] Cross-references between sections work

---

## 🚨 Troubleshooting

### If Claude Code Still Hits Token Limit:

**Option 1: Further Break Down Phases**
Split problematic phase into 2 sub-phases:
- Phase 2a: Sections 4-5
- Phase 2b: Sections 6-7

**Option 2: Create Separate Files**
Instead of one large file, create:
- `ANDROID_ARCHITECTURE_MAIN.md` (overview)
- `ANDROID_COMPONENTS.md` (detailed components)
- `ANDROID_DATA_LAYER.md` (data layer details)
- `ANDROID_UI_LAYER.md` (UI details)
- etc.

**Option 3: Reduce Detail Level**
Ask Claude Code to be more concise:
- Fewer code examples
- Briefer descriptions
- Less duplication

---

## 🎯 Expected Final Output

After completing all 4 phases:

**File**: `android/docs/ANDROID_ARCHITECTURE.md`

**Size**: 2000-3000 lines

**Sections**: 18 complete sections covering:
1. Executive Summary
2. Project Structure
3. Architecture Overview
4. Core Components
5. Data Layer
6. Network Layer
7. UI Layer
8. State Management
9. Video Streaming
10. Navigation
11. Dependencies
12. Configuration & Settings
13. Testing
14. Build System
15. Code Conventions
16. Deployment
17. Known Issues & Technical Debt
18. Future Roadmap
19. Appendices

**Git Commits**: 4 commits (one per phase)

---

## 📞 Support

If issues persist:
1. Check token limit environment variable
2. Try breaking into smaller phases
3. Consider multiple-file approach
4. Reduce verbosity level

---

**Document Ready**: ✅ This instruction file is complete and ready to use with Claude Code!

**Start with Phase 1** and work through sequentially to generate complete architecture documentation.

Good luck! 🚀📚
