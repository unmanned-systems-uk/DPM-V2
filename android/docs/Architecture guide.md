Architecture guide.md
Instructions for Claude Code: Generate Complete Android Architecture Documentation
📋 Overview
Task: Generate comprehensive architecture documentation for the entire DPM Android application.
Output: android/docs/ANDROID_ARCHITECTURE.md (and supplementary files if needed)
Estimated Time: 4-6 hours
Approach: Systematic analysis of entire codebase, then structured documentation generation.

🎯 Objectives
Create professional-grade documentation that:

Maps entire project structure and organization
Documents all components, classes, and their interactions
Explains data flow and state management
Describes network communication architecture
Details UI/UX structure and navigation
Lists all dependencies and their purposes
Defines code conventions and patterns
Provides onboarding guide for new developers


📁 Required Output Files
Primary Document
File: android/docs/ANDROID_ARCHITECTURE.md
Contents:

Complete architecture overview
All components documented
Data flow diagrams
Code examples
~5000-10000 lines

Supplementary Documents (Create if needed)

android/docs/CLASS_REFERENCE.md - Detailed class-by-class reference
android/docs/PACKAGE_STRUCTURE.md - Package organization details
android/docs/NETWORK_PROTOCOL.md - Network communication details
android/docs/UI_COMPONENTS.md - Composable component catalog


📐 Documentation Structure Template
markdown# DPM Android Application - Architecture Documentation

**Version**: 1.0  
**Date**: [Generation Date]  
**Project**: Drone Payload Manager (DPM) - Ground Station Application  
**Platform**: Android (Kotlin + Jetpack Compose)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Structure](#2-project-structure)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Components](#4-core-components)
5. [Data Layer](#5-data-layer)
6. [Network Layer](#6-network-layer)
7. [UI Layer](#7-ui-layer)
8. [State Management](#8-state-management)
9. [Video Streaming](#9-video-streaming)
10. [Navigation](#10-navigation)
11. [Dependencies](#11-dependencies)
12. [Configuration & Settings](#12-configuration--settings)
13. [Testing](#13-testing)
14. [Build System](#14-build-system)
15. [Code Conventions](#15-code-conventions)
16. [Deployment](#16-deployment)
17. [Known Issues & Technical Debt](#17-known-issues--technical-debt)
18. [Future Roadmap](#18-future-roadmap)

---

## 1. Executive Summary

### 1.1 Project Overview
[Brief description of DPM, its purpose, and goals]

### 1.2 Technology Stack
[List all major technologies, frameworks, versions]

### 1.3 Key Features
[Bullet list of main features]

### 1.4 Development Status
[Current phase, what's complete, what's in progress]

### 1.5 Target Hardware
- SkyDroid H16 Ground Station
- Android 7.1.2 (API 25)
- [Other specs]

---

## 2. Project Structure

### 2.1 Directory Layout
```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/dpm/
│   │   │   │   ├── [List all packages]
│   │   │   ├── res/
│   │   │   │   ├── [List resource directories]
│   │   │   └── AndroidManifest.xml
│   │   ├── test/
│   │   └── androidTest/
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
└── docs/
    └── ANDROID_ARCHITECTURE.md (this file)
```

### 2.2 Package Structure
[For each package, document:]
- Package name: `com.dpm.[package]`
- Purpose: [Brief description]
- Number of files: [count]
- Key classes: [List]

### 2.3 File Naming Conventions
- ViewModels: `[Feature]ViewModel.kt`
- Screens: `[Feature]Screen.kt`
- Repositories: `[Feature]Repository.kt`
- Data Models: `[Entity].kt` or `[Entity]Data.kt`
- [Continue...]

---

## 3. Architecture Overview

### 3.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Screens    │  │  Composables │  │ Navigation│ │
│  │ (Jetpack     │  │  (UI Comp.)  │  │           │ │
│  │  Compose)    │  │              │  │           │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
└─────────┼─────────────────┼─────────────────┼───────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────┐
│                   ViewModel Layer                    │
│  ┌──────────────────────────────────────────────┐   │
│  │  ViewModels (State Management + Business)    │   │
│  │  - StateFlow / LiveData                      │   │
│  │  - UI State Objects                          │   │
│  └──────────────────┬───────────────────────────┘   │
└─────────────────────┼───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                    Data Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Repositories │  │  DataStore   │  │  Network  │ │
│  │              │  │  (Settings)  │  │  Client   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │    Air-Side (Pi/Camera)    │
         │  TCP/UDP Communication     │
         └────────────────────────────┘
```

### 3.2 Design Patterns

#### 3.2.1 MVVM (Model-View-ViewModel)
[Explain how MVVM is used in the project]

#### 3.2.2 Repository Pattern
[Explain repository pattern usage]

#### 3.2.3 Single Source of Truth
[Explain data flow and state management]

#### 3.2.4 Unidirectional Data Flow
[Explain UI event -> ViewModel -> State -> UI cycle]

### 3.3 Layer Responsibilities

#### Presentation Layer
- Displays UI using Jetpack Compose
- Observes ViewModel state
- Handles user interactions
- Navigation between screens

#### ViewModel Layer
- Manages UI state
- Handles business logic
- Coordinates between repositories
- Exposes state via StateFlow

#### Data Layer
- Network communication
- Settings persistence
- Data transformation
- Error handling

---

## 4. Core Components

### 4.1 Activity

#### MainActivity.kt
**File**: `app/src/main/java/com/dpm/MainActivity.kt`

**Purpose**: [Description]

**Responsibilities**:
- [List responsibilities]

**Code Structure**:
```kotlin
// Include actual code structure
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Document what happens here
    }
}
```

**Lifecycle**:
[Describe lifecycle management]

### 4.2 Navigation

#### Navigation Graph
[Document navigation structure]

**Routes**:
- `/camera` - Camera control screen
- `/settings` - Settings screen
- [List all routes]

**Navigation Flow**:
```
Splash/Launch
    ↓
Camera Screen (default)
    ├→ Settings Screen
    ├→ [Other screens]
    └→ [Other screens]
```

### 4.3 Application Class
[If exists, document it]

---

## 5. Data Layer

### 5.1 Data Models

#### Camera State
**File**: `app/src/main/java/com/dpm/data/CameraState.kt`
```kotlin
// Include actual data class definition
data class CameraState(
    val shutter: String = "1/125",
    val aperture: String = "f/4.0",
    // ... document all fields
)
```

**Fields**:
- `shutter: String` - [Description]
- `aperture: String` - [Description]
- [Document all fields]

**Usage**:
- Used by: [List ViewModels/Screens]

[Continue for ALL data models...]

### 5.2 Repositories

#### SettingsRepository
**File**: `app/src/main/java/com/dpm/data/SettingsRepository.kt`

**Purpose**: [Description]

**Data Sources**:
- DataStore Preferences
- [Others]

**Public API**:
```kotlin
// Document all public functions
suspend fun saveSettings(settings: Settings)
fun getSettings(): Flow
```

**Implementation Details**:
[Describe key implementation aspects]

[Continue for ALL repositories...]

### 5.3 DataStore

#### Settings Persistence
**Keys Used**:
```kotlin
private val SERVER_IP = stringPreferencesKey("server_ip")
private val SERVER_PORT = intPreferencesKey("server_port")
// ... list ALL keys
```

**Data Structure**:
[Describe how settings are organized]

---

## 6. Network Layer

### 6.1 Architecture
```
┌────────────────────────────────────┐
│       ViewModel Layer              │
│  ┌──────────────────────────────┐  │
│  │   CameraViewModel            │  │
│  │   - Sends commands           │  │
│  │   - Receives status updates  │  │
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
    │   Port 5000 (TCP)    │
    │   Port 5001 (UDP)    │
    │   Port 5002 (UDP HB) │
    └──────────────────────┘
```

### 6.2 Protocol Implementation

#### TCP Command Client
**File**: `[path]`

**Purpose**: [Description]

**Connection Management**:
```kotlin
// Document connection logic
```

**Command Sending**:
```kotlin
// Document command sending
```

**Error Handling**:
[Describe error handling strategy]

#### UDP Status Listener
**File**: `[path]`

**Purpose**: [Description]

**Implementation**:
```kotlin
// Document UDP listening logic
```

#### Heartbeat Manager
[Document heartbeat implementation]

### 6.3 Protocol Specification

#### Message Format
```json
{
    "protocol_version": "1.0",
    "message_type": "command|status|response|heartbeat",
    "sequence_id": 12345,
    "timestamp": 1729339200,
    "payload": { }
}
```

#### Command Examples
[List and document key commands]

#### Status Updates
[Document status message structure]

---

## 7. UI Layer

### 7.1 Compose Architecture

#### Theme
**File**: `app/src/main/java/com/dpm/ui/theme/Theme.kt`

**Colors**:
```kotlin
// Document color scheme
```

**Typography**:
```kotlin
// Document typography
```

**Shapes**:
```kotlin
// Document shapes
```

### 7.2 Screens

#### Camera Screen
**File**: `app/src/main/java/com/dpm/ui/screens/CameraScreen.kt`

**Purpose**: [Description]

**Layout Structure**:
```
Box (Full Screen)
├── FullScreenVideoPlayer (Background)
└── CameraControlsOverlay
    ├── CameraSettingsPanel (Top-Left)
    ├── Title (Top-Center)
    ├── CaptureButton (Center-Bottom)
    ├── FileFormatButtons (Bottom-Left)
    └── StatusIndicators (Bottom-Right)
```

**Composable Hierarchy**:
```kotlin
@Composable
fun CameraScreen() {
    // Document structure
}

@Composable
fun CameraControlsOverlay() {
    // Document structure
}
```

**User Interactions**:
- [Action] → [Effect]
- [Action] → [Effect]

[Continue for ALL screens...]

### 7.3 Reusable Components

#### Component Catalog
[Document all reusable composables]

##### FullScreenVideoPlayer
**File**: `[path]`
**Purpose**: [Description]
**Parameters**:
- `rtspUrl: String` - [Description]
- [Others]

**Usage Example**:
```kotlin
FullScreenVideoPlayer(
    rtspUrl = "rtsp://...",
    modifier = Modifier.fillMaxSize()
)
```

[Continue for ALL reusable components...]

---

## 8. State Management

### 8.1 State Flow Architecture
```
User Action (UI Event)
    ↓
ViewModel Function
    ↓
State Update
    ↓
StateFlow Emission
    ↓
UI Recomposition
```

### 8.2 ViewModels

#### CameraViewModel
**File**: `app/src/main/java/com/dpm/viewmodel/CameraViewModel.kt`

**State Objects**:
```kotlin
private val _cameraState = MutableStateFlow(CameraState())
val cameraState: StateFlow = _cameraState.asStateFlow()

private val _connectionState = MutableStateFlow(ConnectionState.Disconnected)
val connectionState: StateFlow = _connectionState.asStateFlow()
```

**State Management Pattern**:
```kotlin
// Document how state is updated
fun updateShutter(value: String) {
    _cameraState.update { it.copy(shutter = value) }
    // Send to air-side
}
```

**Public API**:
```kotlin
// Document all public functions
fun captureImage()
fun updateShutter(value: String)
fun updateISO(value: Int)
// ... all others
```

**Dependencies**:
- NetworkClient
- SettingsRepository
- [Others]

**Error Handling**:
[Describe error handling approach]

[Continue for ALL ViewModels...]

### 8.3 State Objects

[Document all state data classes and their purposes]

---

## 9. Video Streaming

### 9.1 Architecture
```
R16 Air Unit (RTSP Server)
    ↓ RTSP Stream
Android App (ExoPlayer Client)
    ↓
PlayerView (AndroidView)
    ↓
FullScreenVideoPlayer Composable
    ↓
CameraScreen
```

### 9.2 ExoPlayer Integration

#### VideoPlayerViewModel
**File**: `[path]`

[Document video player implementation in detail]

#### Player Lifecycle
[Document initialization, playback, cleanup]

### 9.3 Video Settings
[Document video configuration options]

---

## 10. Navigation

### 10.1 Navigation Implementation
[Document how navigation is implemented]

### 10.2 Routes and Destinations
[List all navigation routes]

### 10.3 Navigation Flow
[Describe typical user navigation paths]

---

## 11. Dependencies

### 11.1 Gradle Dependencies

#### Core Dependencies
```kotlin
// From build.gradle.kts
implementation("androidx.core:core-ktx:1.x.x")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.x.x")
// ... LIST ALL
```

#### Compose Dependencies
```kotlin
implementation(platform("androidx.compose:compose-bom:2023.xx.xx"))
// ... LIST ALL
```

#### ExoPlayer Dependencies
```kotlin
implementation("androidx.media3:media3-exoplayer:1.2.0")
// ... LIST ALL
```

#### Network Dependencies
```kotlin
// LIST ANY network libraries
```

#### Other Dependencies
```kotlin
// LIST ALL other dependencies
```

### 11.2 Plugins
```kotlin
// From build.gradle.kts
id("com.android.application")
id("org.jetbrains.kotlin.android")
// ... LIST ALL
```

### 11.3 Dependency Versions
[Create table of all versions used]

---

## 12. Configuration & Settings

### 12.1 Build Configuration

#### Build Types
```kotlin
buildTypes {
    release {
        // Document release config
    }
    debug {
        // Document debug config
    }
}
```

#### Build Variants
[Document any variants]

### 12.2 Application Settings

#### Default Values
[List all default settings values]

#### Settings Schema
[Describe complete settings structure]

---

## 13. Testing

### 13.1 Test Structure
[Document test organization]

### 13.2 Unit Tests
[List unit tests if they exist]

### 13.3 Integration Tests
[List integration tests if they exist]

### 13.4 UI Tests
[List UI tests if they exist]

---

## 14. Build System

### 14.1 Gradle Configuration
[Document key Gradle configs]

### 14.2 Build Process
[Describe build steps]

### 14.3 Release Process
[Document release build process]

---

## 15. Code Conventions

### 15.1 Kotlin Style Guide
- [Convention 1]
- [Convention 2]

### 15.2 Compose Conventions
- [Convention 1]
- [Convention 2]

### 15.3 Naming Conventions
[Document naming patterns]

### 15.4 Documentation Standards
[Document how code should be documented]

---

## 16. Deployment

### 16.1 APK Generation
[Steps to build APK]

### 16.2 Signing Configuration
[Document signing setup]

### 16.3 Release Checklist
- [ ] [Item 1]
- [ ] [Item 2]

---

## 17. Known Issues & Technical Debt

### 17.1 Current Limitations
- [Limitation 1]
- [Limitation 2]

### 17.2 Areas for Improvement
- [Area 1]
- [Area 2]

### 17.3 Technical Debt
- [Debt item 1]
- [Debt item 2]

---

## 18. Future Roadmap

### 18.1 Planned Features
- [Feature 1]
- [Feature 2]

### 18.2 Potential Refactoring
- [Refactor 1]
- [Refactor 2]

---

## Appendix

### A. Class Reference
[Link to detailed class reference document]

### B. Package Structure Details
[Link to package structure document]

### C. Network Protocol Details
[Link to protocol documentation]

### D. UI Component Catalog
[Link to UI components documentation]

---

**Document End**

🔍 Step-by-Step Analysis Process
Step 1: Initial Project Scan (30 min)
bash# Run these commands to understand project structure

# 1. Count files
find ./app/src/main/java -name "*.kt" | wc -l
find ./app/src/main/res -name "*.xml" | wc -l

# 2. List all packages
find ./app/src/main/java -type d | sort

# 3. List all Kotlin files
find ./app/src/main/java -name "*.kt" | sort

# 4. List all ViewModels
find ./app/src/main/java -name "*ViewModel.kt"

# 5. List all Screens
find ./app/src/main/java -name "*Screen.kt"

# 6. List all data models
find ./app/src/main/java -path "*/data/*" -name "*.kt"

# 7. List all repositories
find ./app/src/main/java -name "*Repository.kt"
Step 2: Analyze Build Configuration (20 min)
bash# Read and document:
# 1. app/build.gradle.kts - all dependencies
# 2. settings.gradle.kts - project structure
# 3. gradle.properties - configuration properties
Step 3: Analyze Each Package (60 min)
For each package in com.dpm.*:

List all files in the package
Determine package purpose from file names/content
Identify key classes (most important files)
Document relationships between classes
Note dependencies on other packages

Step 4: Deep Dive - ViewModels (60 min)
For each ViewModel file:

Open the file
Document class name and file path
List all StateFlow/LiveData properties
Document all public functions
Identify dependencies (repositories, etc.)
Note which screens use this ViewModel
Document state update patterns
Include code snippets for key functions

Step 5: Deep Dive - Screens (60 min)
For each Screen composable:

Open the file
Document composable name and file path
List ViewModel dependencies
Map out UI component hierarchy
Document user interactions
List navigation connections
Include layout diagrams (ASCII art)
Document state observation patterns

Step 6: Deep Dive - Data Layer (45 min)
For each data class, repository, and data source:

Document data models completely
Explain repository pattern usage
Document DataStore keys and structure
Explain network client implementation
Document error handling approaches

Step 7: Deep Dive - Network Layer (45 min)

Document TCP client implementation
Document UDP listener implementation
Document heartbeat mechanism
Document protocol message format
Document command/response patterns
Include sequence diagrams (textual)

Step 8: Deep Dive - Video Streaming (30 min)

Document ExoPlayer integration
Document VideoPlayerViewModel
Document FullScreenVideoPlayer composable
Document video settings
Document player lifecycle

Step 9: Create Diagrams (45 min)
Create ASCII/textual diagrams for:

Overall architecture
Data flow
Navigation flow
Network communication
State management
Component hierarchy for each screen

Step 10: Document Dependencies (30 min)

List all Gradle dependencies with versions
Explain purpose of each major dependency
Document any custom/internal dependencies
Create dependency graph (textual)

Step 11: Document Conventions (20 min)

Identify naming patterns used
Document code style patterns
Document common design patterns
Document file organization principles

Step 12: Review and Polish (30 min)

Review entire document for completeness
Add cross-references between sections
Verify all code examples are accurate
Add table of contents links
Check formatting consistency
Add any missing details


✅ Completion Checklist
Content Completeness

 All packages documented
 All ViewModels documented
 All Screens documented
 All data models documented
 All repositories documented
 Network layer completely documented
 Video streaming documented
 Navigation documented
 All dependencies listed
 Build system documented
 Code conventions documented

Quality Checks

 All code examples are actual code from project
 All diagrams are clear and accurate
 All cross-references work
 Table of contents is complete
 No placeholder text remains
 Formatting is consistent
 Technical accuracy verified

Documentation Files

 ANDROID_ARCHITECTURE.md created
 Any supplementary docs created
 Files placed in android/docs/
 Git commit created: [DOCS] Complete Android architecture documentation


📝 Git Workflow
bash# 1. Start documentation task
git checkout -b docs/android-architecture

# 2. Create docs directory if needed
mkdir -p android/docs

# 3. Generate documentation
# (Follow analysis process above)

# 4. Review generated documentation
cat android/docs/ANDROID_ARCHITECTURE.md

# 5. Commit
git add android/docs/
git commit -m "[DOCS] Complete Android architecture documentation

- Document entire project structure
- Document all ViewModels, Screens, and components
- Document data layer and repositories
- Document network communication
- Document video streaming integration
- Document dependencies and build system
- Add architecture diagrams
- Add code examples from actual codebase"

# 6. If using PR workflow
git push origin docs/android-architecture
# Create pull request
```

---

## 🎯 Success Criteria

### Documentation Must:
- ✅ Cover 100% of existing codebase
- ✅ Include actual code examples (not pseudo-code)
- ✅ Include clear diagrams
- ✅ Be technically accurate
- ✅ Be well-organized and navigable
- ✅ Serve as onboarding guide for new developers
- ✅ Serve as reference for current developers
- ✅ Be maintainable (easy to update)

### Documentation Quality:
- Professional technical writing
- Consistent formatting
- Clear and concise
- No assumptions about reader knowledge
- Complete but not verbose
- Practical and useful

---

## 🚀 Getting Started

### For Claude Code:

1. **Read this entire instruction document**
2. **Review existing project documentation** (if any)
3. **Start with Step 1: Initial Project Scan**
4. **Follow analysis process sequentially**
5. **Use template structure provided above**
6. **Fill in actual details from codebase**
7. **Review and polish before committing**
8. **Follow Git workflow for committing**

### Expected Output:
```
android/docs/
├── ANDROID_ARCHITECTURE.md (primary, 5000-10000 lines)
└── [Any supplementary docs if needed]
Time Estimate:

Analysis: 3-4 hours
Documentation writing: 2-3 hours
Review and polish: 1 hour
Total: 6-8 hours


💡 Tips for Claude Code

Be thorough - Document everything, even if it seems obvious
Use actual code - Copy real code snippets, don't paraphrase
Be specific - Include file paths, line numbers where relevant
Cross-reference - Link related sections together
Think like a new developer - What would they need to know?
Stay organized - Follow the template structure
Verify accuracy - Double-check technical details
Keep it maintainable - Make it easy to update later


📞 Questions to Consider
As you document, answer these questions:
Architecture Questions

What design patterns are used and why?
How does data flow through the application?
How is state managed across components?
What are the key architectural decisions?

Component Questions

What is the purpose of each component?
How do components interact?
What are the dependencies between components?
What are the public APIs?

Code Organization Questions

Why is code organized this way?
What are the naming conventions?
What are the package responsibilities?
How should new code be added?

Developer Experience Questions

How does a new developer get started?
What are common tasks and how to do them?
What are the gotchas or tricky parts?
Where would someone look for X functionality?Instructions for Claude Code: Generate Complete Android Architecture Documentation
📋 Overview
Task: Generate comprehensive architecture documentation for the entire DPM Android application.
Output: android/docs/ANDROID_ARCHITECTURE.md (and supplementary files if needed)
Estimated Time: 4-6 hours
Approach: Systematic analysis of entire codebase, then structured documentation generation.

🎯 Objectives
Create professional-grade documentation that:

Maps entire project structure and organization
Documents all components, classes, and their interactions
Explains data flow and state management
Describes network communication architecture
Details UI/UX structure and navigation
Lists all dependencies and their purposes
Defines code conventions and patterns
Provides onboarding guide for new developers


📁 Required Output Files
Primary Document
File: android/docs/ANDROID_ARCHITECTURE.md
Contents:

Complete architecture overview
All components documented
Data flow diagrams
Code examples
~5000-10000 lines

Supplementary Documents (Create if needed)

android/docs/CLASS_REFERENCE.md - Detailed class-by-class reference
android/docs/PACKAGE_STRUCTURE.md - Package organization details
android/docs/NETWORK_PROTOCOL.md - Network communication details
android/docs/UI_COMPONENTS.md - Composable component catalog


📐 Documentation Structure Template
markdown# DPM Android Application - Architecture Documentation

**Version**: 1.0  
**Date**: [Generation Date]  
**Project**: Drone Payload Manager (DPM) - Ground Station Application  
**Platform**: Android (Kotlin + Jetpack Compose)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Structure](#2-project-structure)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Components](#4-core-components)
5. [Data Layer](#5-data-layer)
6. [Network Layer](#6-network-layer)
7. [UI Layer](#7-ui-layer)
8. [State Management](#8-state-management)
9. [Video Streaming](#9-video-streaming)
10. [Navigation](#10-navigation)
11. [Dependencies](#11-dependencies)
12. [Configuration & Settings](#12-configuration--settings)
13. [Testing](#13-testing)
14. [Build System](#14-build-system)
15. [Code Conventions](#15-code-conventions)
16. [Deployment](#16-deployment)
17. [Known Issues & Technical Debt](#17-known-issues--technical-debt)
18. [Future Roadmap](#18-future-roadmap)

---

## 1. Executive Summary

### 1.1 Project Overview
[Brief description of DPM, its purpose, and goals]

### 1.2 Technology Stack
[List all major technologies, frameworks, versions]

### 1.3 Key Features
[Bullet list of main features]

### 1.4 Development Status
[Current phase, what's complete, what's in progress]

### 1.5 Target Hardware
- SkyDroid H16 Ground Station
- Android 7.1.2 (API 25)
- [Other specs]

---

## 2. Project Structure

### 2.1 Directory Layout
```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/dpm/
│   │   │   │   ├── [List all packages]
│   │   │   ├── res/
│   │   │   │   ├── [List resource directories]
│   │   │   └── AndroidManifest.xml
│   │   ├── test/
│   │   └── androidTest/
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
└── docs/
    └── ANDROID_ARCHITECTURE.md (this file)
```

### 2.2 Package Structure
[For each package, document:]
- Package name: `com.dpm.[package]`
- Purpose: [Brief description]
- Number of files: [count]
- Key classes: [List]

### 2.3 File Naming Conventions
- ViewModels: `[Feature]ViewModel.kt`
- Screens: `[Feature]Screen.kt`
- Repositories: `[Feature]Repository.kt`
- Data Models: `[Entity].kt` or `[Entity]Data.kt`
- [Continue...]

---

## 3. Architecture Overview

### 3.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────┐
│                  Presentation Layer                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Screens    │  │  Composables │  │ Navigation│ │
│  │ (Jetpack     │  │  (UI Comp.)  │  │           │ │
│  │  Compose)    │  │              │  │           │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
└─────────┼─────────────────┼─────────────────┼───────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────┐
│                   ViewModel Layer                    │
│  ┌──────────────────────────────────────────────┐   │
│  │  ViewModels (State Management + Business)    │   │
│  │  - StateFlow / LiveData                      │   │
│  │  - UI State Objects                          │   │
│  └──────────────────┬───────────────────────────┘   │
└─────────────────────┼───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                    Data Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Repositories │  │  DataStore   │  │  Network  │ │
│  │              │  │  (Settings)  │  │  Client   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │    Air-Side (Pi/Camera)    │
         │  TCP/UDP Communication     │
         └────────────────────────────┘
```

### 3.2 Design Patterns

#### 3.2.1 MVVM (Model-View-ViewModel)
[Explain how MVVM is used in the project]

#### 3.2.2 Repository Pattern
[Explain repository pattern usage]

#### 3.2.3 Single Source of Truth
[Explain data flow and state management]

#### 3.2.4 Unidirectional Data Flow
[Explain UI event -> ViewModel -> State -> UI cycle]

### 3.3 Layer Responsibilities

#### Presentation Layer
- Displays UI using Jetpack Compose
- Observes ViewModel state
- Handles user interactions
- Navigation between screens

#### ViewModel Layer
- Manages UI state
- Handles business logic
- Coordinates between repositories
- Exposes state via StateFlow

#### Data Layer
- Network communication
- Settings persistence
- Data transformation
- Error handling

---

## 4. Core Components

### 4.1 Activity

#### MainActivity.kt
**File**: `app/src/main/java/com/dpm/MainActivity.kt`

**Purpose**: [Description]

**Responsibilities**:
- [List responsibilities]

**Code Structure**:
```kotlin
// Include actual code structure
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Document what happens here
    }
}
```

**Lifecycle**:
[Describe lifecycle management]

### 4.2 Navigation

#### Navigation Graph
[Document navigation structure]

**Routes**:
- `/camera` - Camera control screen
- `/settings` - Settings screen
- [List all routes]

**Navigation Flow**:
```
Splash/Launch
    ↓
Camera Screen (default)
    ├→ Settings Screen
    ├→ [Other screens]
    └→ [Other screens]
```

### 4.3 Application Class
[If exists, document it]

---

## 5. Data Layer

### 5.1 Data Models

#### Camera State
**File**: `app/src/main/java/com/dpm/data/CameraState.kt`
```kotlin
// Include actual data class definition
data class CameraState(
    val shutter: String = "1/125",
    val aperture: String = "f/4.0",
    // ... document all fields
)
```

**Fields**:
- `shutter: String` - [Description]
- `aperture: String` - [Description]
- [Document all fields]

**Usage**:
- Used by: [List ViewModels/Screens]

[Continue for ALL data models...]

### 5.2 Repositories

#### SettingsRepository
**File**: `app/src/main/java/com/dpm/data/SettingsRepository.kt`

**Purpose**: [Description]

**Data Sources**:
- DataStore Preferences
- [Others]

**Public API**:
```kotlin
// Document all public functions
suspend fun saveSettings(settings: Settings)
fun getSettings(): Flow
```

**Implementation Details**:
[Describe key implementation aspects]

[Continue for ALL repositories...]

### 5.3 DataStore

#### Settings Persistence
**Keys Used**:
```kotlin
private val SERVER_IP = stringPreferencesKey("server_ip")
private val SERVER_PORT = intPreferencesKey("server_port")
// ... list ALL keys
```

**Data Structure**:
[Describe how settings are organized]

---

## 6. Network Layer

### 6.1 Architecture
```
┌────────────────────────────────────┐
│       ViewModel Layer              │
│  ┌──────────────────────────────┐  │
│  │   CameraViewModel            │  │
│  │   - Sends commands           │  │
│  │   - Receives status updates  │  │
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
    │   Port 5000 (TCP)    │
    │   Port 5001 (UDP)    │
    │   Port 5002 (UDP HB) │
    └──────────────────────┘
```

### 6.2 Protocol Implementation

#### TCP Command Client
**File**: `[path]`

**Purpose**: [Description]

**Connection Management**:
```kotlin
// Document connection logic
```

**Command Sending**:
```kotlin
// Document command sending
```

**Error Handling**:
[Describe error handling strategy]

#### UDP Status Listener
**File**: `[path]`

**Purpose**: [Description]

**Implementation**:
```kotlin
// Document UDP listening logic
```

#### Heartbeat Manager
[Document heartbeat implementation]

### 6.3 Protocol Specification

#### Message Format
```json
{
    "protocol_version": "1.0",
    "message_type": "command|status|response|heartbeat",
    "sequence_id": 12345,
    "timestamp": 1729339200,
    "payload": { }
}
```

#### Command Examples
[List and document key commands]

#### Status Updates
[Document status message structure]

---

## 7. UI Layer

### 7.1 Compose Architecture

#### Theme
**File**: `app/src/main/java/com/dpm/ui/theme/Theme.kt`

**Colors**:
```kotlin
// Document color scheme
```

**Typography**:
```kotlin
// Document typography
```

**Shapes**:
```kotlin
// Document shapes
```

### 7.2 Screens

#### Camera Screen
**File**: `app/src/main/java/com/dpm/ui/screens/CameraScreen.kt`

**Purpose**: [Description]

**Layout Structure**:
```
Box (Full Screen)
├── FullScreenVideoPlayer (Background)
└── CameraControlsOverlay
    ├── CameraSettingsPanel (Top-Left)
    ├── Title (Top-Center)
    ├── CaptureButton (Center-Bottom)
    ├── FileFormatButtons (Bottom-Left)
    └── StatusIndicators (Bottom-Right)
```

**Composable Hierarchy**:
```kotlin
@Composable
fun CameraScreen() {
    // Document structure
}

@Composable
fun CameraControlsOverlay() {
    // Document structure
}
```

**User Interactions**:
- [Action] → [Effect]
- [Action] → [Effect]

[Continue for ALL screens...]

### 7.3 Reusable Components

#### Component Catalog
[Document all reusable composables]

##### FullScreenVideoPlayer
**File**: `[path]`
**Purpose**: [Description]
**Parameters**:
- `rtspUrl: String` - [Description]
- [Others]

**Usage Example**:
```kotlin
FullScreenVideoPlayer(
    rtspUrl = "rtsp://...",
    modifier = Modifier.fillMaxSize()
)
```

[Continue for ALL reusable components...]

---

## 8. State Management

### 8.1 State Flow Architecture
```
User Action (UI Event)
    ↓
ViewModel Function
    ↓
State Update
    ↓
StateFlow Emission
    ↓
UI Recomposition
```

### 8.2 ViewModels

#### CameraViewModel
**File**: `app/src/main/java/com/dpm/viewmodel/CameraViewModel.kt`

**State Objects**:
```kotlin
private val _cameraState = MutableStateFlow(CameraState())
val cameraState: StateFlow = _cameraState.asStateFlow()

private val _connectionState = MutableStateFlow(ConnectionState.Disconnected)
val connectionState: StateFlow = _connectionState.asStateFlow()
```

**State Management Pattern**:
```kotlin
// Document how state is updated
fun updateShutter(value: String) {
    _cameraState.update { it.copy(shutter = value) }
    // Send to air-side
}
```

**Public API**:
```kotlin
// Document all public functions
fun captureImage()
fun updateShutter(value: String)
fun updateISO(value: Int)
// ... all others
```

**Dependencies**:
- NetworkClient
- SettingsRepository
- [Others]

**Error Handling**:
[Describe error handling approach]

[Continue for ALL ViewModels...]

### 8.3 State Objects

[Document all state data classes and their purposes]

---

## 9. Video Streaming

### 9.1 Architecture
```
R16 Air Unit (RTSP Server)
    ↓ RTSP Stream
Android App (ExoPlayer Client)
    ↓
PlayerView (AndroidView)
    ↓
FullScreenVideoPlayer Composable
    ↓
CameraScreen
```

### 9.2 ExoPlayer Integration

#### VideoPlayerViewModel
**File**: `[path]`

[Document video player implementation in detail]

#### Player Lifecycle
[Document initialization, playback, cleanup]

### 9.3 Video Settings
[Document video configuration options]

---

## 10. Navigation

### 10.1 Navigation Implementation
[Document how navigation is implemented]

### 10.2 Routes and Destinations
[List all navigation routes]

### 10.3 Navigation Flow
[Describe typical user navigation paths]

---

## 11. Dependencies

### 11.1 Gradle Dependencies

#### Core Dependencies
```kotlin
// From build.gradle.kts
implementation("androidx.core:core-ktx:1.x.x")
implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.x.x")
// ... LIST ALL
```

#### Compose Dependencies
```kotlin
implementation(platform("androidx.compose:compose-bom:2023.xx.xx"))
// ... LIST ALL
```

#### ExoPlayer Dependencies
```kotlin
implementation("androidx.media3:media3-exoplayer:1.2.0")
// ... LIST ALL
```

#### Network Dependencies
```kotlin
// LIST ANY network libraries
```

#### Other Dependencies
```kotlin
// LIST ALL other dependencies
```

### 11.2 Plugins
```kotlin
// From build.gradle.kts
id("com.android.application")
id("org.jetbrains.kotlin.android")
// ... LIST ALL
```

### 11.3 Dependency Versions
[Create table of all versions used]

---

## 12. Configuration & Settings

### 12.1 Build Configuration

#### Build Types
```kotlin
buildTypes {
    release {
        // Document release config
    }
    debug {
        // Document debug config
    }
}
```

#### Build Variants
[Document any variants]

### 12.2 Application Settings

#### Default Values
[List all default settings values]

#### Settings Schema
[Describe complete settings structure]

---

## 13. Testing

### 13.1 Test Structure
[Document test organization]

### 13.2 Unit Tests
[List unit tests if they exist]

### 13.3 Integration Tests
[List integration tests if they exist]

### 13.4 UI Tests
[List UI tests if they exist]

---

## 14. Build System

### 14.1 Gradle Configuration
[Document key Gradle configs]

### 14.2 Build Process
[Describe build steps]

### 14.3 Release Process
[Document release build process]

---

## 15. Code Conventions

### 15.1 Kotlin Style Guide
- [Convention 1]
- [Convention 2]

### 15.2 Compose Conventions
- [Convention 1]
- [Convention 2]

### 15.3 Naming Conventions
[Document naming patterns]

### 15.4 Documentation Standards
[Document how code should be documented]

---

## 16. Deployment

### 16.1 APK Generation
[Steps to build APK]

### 16.2 Signing Configuration
[Document signing setup]

### 16.3 Release Checklist
- [ ] [Item 1]
- [ ] [Item 2]

---

## 17. Known Issues & Technical Debt

### 17.1 Current Limitations
- [Limitation 1]
- [Limitation 2]

### 17.2 Areas for Improvement
- [Area 1]
- [Area 2]

### 17.3 Technical Debt
- [Debt item 1]
- [Debt item 2]

---

## 18. Future Roadmap

### 18.1 Planned Features
- [Feature 1]
- [Feature 2]

### 18.2 Potential Refactoring
- [Refactor 1]
- [Refactor 2]

---

## Appendix

### A. Class Reference
[Link to detailed class reference document]

### B. Package Structure Details
[Link to package structure document]

### C. Network Protocol Details
[Link to protocol documentation]

### D. UI Component Catalog
[Link to UI components documentation]

---

**Document End**

🔍 Step-by-Step Analysis Process
Step 1: Initial Project Scan (30 min)
bash# Run these commands to understand project structure

# 1. Count files
find ./app/src/main/java -name "*.kt" | wc -l
find ./app/src/main/res -name "*.xml" | wc -l

# 2. List all packages
find ./app/src/main/java -type d | sort

# 3. List all Kotlin files
find ./app/src/main/java -name "*.kt" | sort

# 4. List all ViewModels
find ./app/src/main/java -name "*ViewModel.kt"

# 5. List all Screens
find ./app/src/main/java -name "*Screen.kt"

# 6. List all data models
find ./app/src/main/java -path "*/data/*" -name "*.kt"

# 7. List all repositories
find ./app/src/main/java -name "*Repository.kt"
Step 2: Analyze Build Configuration (20 min)
bash# Read and document:
# 1. app/build.gradle.kts - all dependencies
# 2. settings.gradle.kts - project structure
# 3. gradle.properties - configuration properties
Step 3: Analyze Each Package (60 min)
For each package in com.dpm.*:

List all files in the package
Determine package purpose from file names/content
Identify key classes (most important files)
Document relationships between classes
Note dependencies on other packages

Step 4: Deep Dive - ViewModels (60 min)
For each ViewModel file:

Open the file
Document class name and file path
List all StateFlow/LiveData properties
Document all public functions
Identify dependencies (repositories, etc.)
Note which screens use this ViewModel
Document state update patterns
Include code snippets for key functions

Step 5: Deep Dive - Screens (60 min)
For each Screen composable:

Open the file
Document composable name and file path
List ViewModel dependencies
Map out UI component hierarchy
Document user interactions
List navigation connections
Include layout diagrams (ASCII art)
Document state observation patterns

Step 6: Deep Dive - Data Layer (45 min)
For each data class, repository, and data source:

Document data models completely
Explain repository pattern usage
Document DataStore keys and structure
Explain network client implementation
Document error handling approaches

Step 7: Deep Dive - Network Layer (45 min)

Document TCP client implementation
Document UDP listener implementation
Document heartbeat mechanism
Document protocol message format
Document command/response patterns
Include sequence diagrams (textual)

Step 8: Deep Dive - Video Streaming (30 min)

Document ExoPlayer integration
Document VideoPlayerViewModel
Document FullScreenVideoPlayer composable
Document video settings
Document player lifecycle

Step 9: Create Diagrams (45 min)
Create ASCII/textual diagrams for:

Overall architecture
Data flow
Navigation flow
Network communication
State management
Component hierarchy for each screen

Step 10: Document Dependencies (30 min)

List all Gradle dependencies with versions
Explain purpose of each major dependency
Document any custom/internal dependencies
Create dependency graph (textual)

Step 11: Document Conventions (20 min)

Identify naming patterns used
Document code style patterns
Document common design patterns
Document file organization principles

Step 12: Review and Polish (30 min)

Review entire document for completeness
Add cross-references between sections
Verify all code examples are accurate
Add table of contents links
Check formatting consistency
Add any missing details


✅ Completion Checklist
Content Completeness

 All packages documented
 All ViewModels documented
 All Screens documented
 All data models documented
 All repositories documented
 Network layer completely documented
 Video streaming documented
 Navigation documented
 All dependencies listed
 Build system documented
 Code conventions documented

Quality Checks

 All code examples are actual code from project
 All diagrams are clear and accurate
 All cross-references work
 Table of contents is complete
 No placeholder text remains
 Formatting is consistent
 Technical accuracy verified

Documentation Files

 ANDROID_ARCHITECTURE.md created
 Any supplementary docs created
 Files placed in android/docs/
 Git commit created: [DOCS] Complete Android architecture documentation


📝 Git Workflow
bash# 1. Start documentation task
git checkout -b docs/android-architecture

# 2. Create docs directory if needed
mkdir -p android/docs

# 3. Generate documentation
# (Follow analysis process above)

# 4. Review generated documentation
cat android/docs/ANDROID_ARCHITECTURE.md

# 5. Commit
git add android/docs/
git commit -m "[DOCS] Complete Android architecture documentation

- Document entire project structure
- Document all ViewModels, Screens, and components
- Document data layer and repositories
- Document network communication
- Document video streaming integration
- Document dependencies and build system
- Add architecture diagrams
- Add code examples from actual codebase"

# 6. If using PR workflow
git push origin docs/android-architecture
# Create pull request
```

---

## 🎯 Success Criteria

### Documentation Must:
- ✅ Cover 100% of existing codebase
- ✅ Include actual code examples (not pseudo-code)
- ✅ Include clear diagrams
- ✅ Be technically accurate
- ✅ Be well-organized and navigable
- ✅ Serve as onboarding guide for new developers
- ✅ Serve as reference for current developers
- ✅ Be maintainable (easy to update)

### Documentation Quality:
- Professional technical writing
- Consistent formatting
- Clear and concise
- No assumptions about reader knowledge
- Complete but not verbose
- Practical and useful

---

## 🚀 Getting Started

### For Claude Code:

1. **Read this entire instruction document**
2. **Review existing project documentation** (if any)
3. **Start with Step 1: Initial Project Scan**
4. **Follow analysis process sequentially**
5. **Use template structure provided above**
6. **Fill in actual details from codebase**
7. **Review and polish before committing**
8. **Follow Git workflow for committing**

### Expected Output:
```
android/docs/
├── ANDROID_ARCHITECTURE.md (primary, 5000-10000 lines)
└── [Any supplementary docs if needed]
Time Estimate:

Analysis: 3-4 hours
Documentation writing: 2-3 hours
Review and polish: 1 hour
Total: 6-8 hours


💡 Tips for Claude Code

Be thorough - Document everything, even if it seems obvious
Use actual code - Copy real code snippets, don't paraphrase
Be specific - Include file paths, line numbers where relevant
Cross-reference - Link related sections together
Think like a new developer - What would they need to know?
Stay organized - Follow the template structure
Verify accuracy - Double-check technical details
Keep it maintainable - Make it easy to update later


📞 Questions to Consider
As you document, answer these questions:
Architecture Questions

What design patterns are used and why?
How does data flow through the application?
How is state managed across components?
What are the key architectural decisions?

Component Questions

What is the purpose of each component?
How do components interact?
What are the dependencies between components?
What are the public APIs?

Code Organization Questions

Why is code organized this way?
What are the naming conventions?
What are the package responsibilities?
How should new code be added?

Developer Experience Questions

How does a new developer get started?
What are common tasks and how to do them?
What are the gotchas or tricky parts?
Where would someone look for X functionality?