# Logical/Functional View

**Architecture View:** Logical/Functional
**Standard:** ISO/IEC/IEEE 42010
**Date:** 2025-11-11
**Version:** 1.0

---

## Overview

The Logical/Functional View describes the major structural elements of DPM-V2, their responsibilities, and how they collaborate to provide system functionality.

**Visual References:**
- `c4-level2-container.puml` - Container architecture
- `c4-level3-air-side-components.puml` - Air-Side components
- `c4-level3-ground-side-components.puml` - Ground-Side components
- `c4-level3-dev-tools-components.puml` - Dev-Tools components

---

## Architectural Style

**Primary Pattern:** Three-Domain Microservices Architecture

**Characteristics:**
- **Domain Separation:** Air-Side, Ground-Side, Dev-Tools are independent containers
- **Communication:** Network protocols (TCP/UDP) decouple domains
- **Technology Heterogeneity:** C++ (Air), Kotlin (Ground), Python (Tools)
- **Independent Deployment:** Each domain can be updated separately
- **Fault Isolation:** Failure in one domain doesn't crash others

**Why Three Domains:**
- **Air-Side:** Performance-critical, hardware-integrated (requires C++)
- **Ground-Side:** UI-rich, user-facing (benefits from modern Android frameworks)
- **Dev-Tools:** Diagnostic/development (Python rapid prototyping)

---

## Domain Architecture

### Air-Side (Performance-Critical Backend)

**Container:** Raspberry Pi 5 Docker service
**Language:** C++17
**Pattern:** Multi-threaded service with component-based architecture

**Primary Responsibilities:**
1. **Camera Control:** Sony SDK integration, USB communication
2. **Network Services:** TCP server, UDP broadcasters, heartbeat
3. **Telemetry:** System monitoring (CPU, memory, temperature)
4. **Property Management:** Load and validate camera property specifications
5. **Error Handling:** Detect and recover from camera disconnects

**Key Components:**

#### CameraService
**Responsibility:** Sony camera control and monitoring

**Functions:**
- Initialize Sony SDK on startup
- Enumerate and connect to camera
- Execute control commands (shutter, property set/get)
- Monitor camera status (connected, mode, settings)
- Auto-reconnect on USB disconnect
- Validate property values against specifications

**Collaborators:**
- Sony SDK (external) for camera API
- PropertyLoader for valid value ranges
- NotificationManager for disconnect events
- CommandHandler for executing commands

**Threading:** Dedicated camera thread for SDK callbacks

---

#### NetworkService
**Responsibility:** All network communication

**Functions:**
- TCP server on port 5000 (command/response)
- UDP broadcaster on port 5001 (status, 5Hz)
- UDP heartbeat on port 5002 (bidirectional, 1Hz)
- Socket management and reconnection
- Message serialization/deserialization

**Collaborators:**
- CommandHandler for routing incoming commands
- StatusBroadcaster for periodic telemetry
- HeartbeatManager for connection health
- MessageSerializer for JSON encoding/decoding

**Threading:** Separate threads for TCP accept, UDP send, UDP receive

---

#### PropertyLoader
**Responsibility:** Camera property specification management

**Functions:**
- Load property definitions from JSON files at startup
- Provide valid value ranges for validation
- Map between SDK values and UI display values
- Support property metadata (units, step size, constraints)

**Design Pattern:** Specification-First Architecture
- Single source of truth (JSON files)
- Shared between Air-Side and Ground-Side
- Version control friendly
- Easy to add new properties

**Collaborators:**
- CameraService for property validation
- CommandHandler for property set operations
- JSON files in `docs/protocol/`

---

#### CommandHandler
**Responsibility:** Parse and route incoming commands

**Functions:**
- Receive commands from TCP channel
- Parse JSON message format
- Route to appropriate handler (camera, system, gimbal)
- Execute command and generate response
- Error handling and timeout management

**Command Types:**
- `camera.capture` → CameraService.triggerShutter()
- `camera.set_property` → CameraService.setProperty()
- `camera.get_property` → CameraService.getProperty()
- `system.status` → SystemMonitor.getStatus()

**Collaborators:**
- NetworkService for I/O
- CameraService for camera commands
- SystemMonitor for system queries

---

#### StatusBroadcaster
**Responsibility:** Periodic system and camera status broadcast

**Functions:**
- Query camera status (5Hz rate)
- Query system metrics (CPU, memory, disk, temp)
- Serialize to JSON
- Broadcast on UDP port 5001
- Increment sequence numbers

**Data Broadcast:**
```json
{
  "protocol_version": "1.0",
  "message_type": "status",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "system": { "cpu_percent": 18.5, "memory_mb": 147 },
    "camera": { "connected": true, "iso": 400, "aperture": "5.6" }
  }
}
```

**Collaborators:**
- CameraService for camera data
- SystemMonitor for system data
- NetworkService for UDP broadcast

---

#### SystemMonitor
**Responsibility:** System resource monitoring

**Functions:**
- Monitor CPU usage (per-core and average)
- Monitor memory consumption
- Monitor disk usage
- Monitor system temperature
- Track uptime

**Implementation:** Uses Linux `/proc` filesystem and system calls

**Update Rate:** On-demand (queried by StatusBroadcaster)

---

#### NotificationManager
**Responsibility:** Real-time event notifications to UI

**Functions:**
- Generate notification messages for critical events
- Send via TCP channel to Ground-Side
- Event types: camera disconnect, error conditions, warnings

**Events:**
- Camera disconnected → Immediate notification
- Camera reconnected → Success notification
- Low battery (future) → Warning notification
- System error → Error notification

---

### Ground-Side (User-Facing Frontend)

**Container:** Android H16 application
**Language:** Kotlin
**Pattern:** MVVM (Model-View-ViewModel)

**Primary Responsibilities:**
1. **User Interface:** Touch-based camera control and monitoring
2. **Network Client:** Connect to Air-Side, send commands, receive telemetry
3. **State Management:** Maintain UI state, handle configuration changes
4. **Settings Persistence:** Save user preferences
5. **Video Playback:** RTSP video streaming (ExoPlayer)

**Architectural Layers:**

#### UI Layer (Composables)
**Technology:** Jetpack Compose
**Pattern:** Declarative UI

**Components:**
- **CameraDashboard:** Main control screen with property sliders/dropdowns
- **SettingsScreen:** Application configuration
- **StatusDisplay:** Real-time status indicators
- **VideoPlayer:** RTSP video stream display

**Characteristics:**
- Stateless composables (state hoisted to ViewModel)
- Reactive UI (observes StateFlow from ViewModel)
- Material 3 design system
- Touch-optimized for 10.1" screen

---

#### ViewModel Layer
**Technology:** AndroidX Lifecycle ViewModel
**Pattern:** MVVM separation of concerns

**Components:**
- **CameraViewModel:** Camera state and control logic
- **ConnectionViewModel:** Network connection state
- **SettingsViewModel:** Application settings

**Responsibilities:**
- Hold UI state (StateFlow)
- Expose functions for UI actions
- Orchestrate repository calls
- Survive configuration changes (screen rotation)
- Lifecycle-aware

**Example (CameraViewModel):**
```kotlin
class CameraViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(CameraUiState())
    val uiState: StateFlow<CameraUiState> = _uiState.asStateFlow()

    fun setShutterSpeed(value: String) {
        viewModelScope.launch {
            repository.sendCommand("camera.set_property", mapOf(
                "property" -> "shutter_speed",
                "value" -> value
            ))
        }
    }
}
```

---

#### Repository Layer
**Technology:** Kotlin coroutines
**Pattern:** Repository pattern (data abstraction)

**Component:** CameraRepository

**Responsibilities:**
- Abstract data sources (network, local)
- Coordinate network client calls
- Cache data where appropriate
- Transform network data to domain models
- Error handling and retry logic

**Data Sources:**
- TcpClient for commands
- UdpListener for status
- PropertyLoader for specifications
- DataStore for settings

---

#### Network Layer
**Technology:** Kotlin coroutines + Java sockets
**Pattern:** Asynchronous I/O

**Components:**
- **TcpCommandClient:** TCP client for command/response
- **UdpStatusListener:** UDP listener for 5Hz status updates
- **HeartbeatClient:** Bidirectional heartbeat management
- **NetworkMonitor:** Connection health and auto-reconnect

**Design:**
- Coroutine-based (non-blocking I/O)
- Auto-reconnect on disconnect
- Command queue for reliability
- Response correlation by sequence ID
- Timeout handling

---

#### Data Layer

**PropertyLoader:**
- Loads property specifications from embedded JSON assets
- Same specs as Air-Side (version sync)
- Provides UI rendering metadata (slider min/max, dropdown options)

**MessageSerializer:**
- JSON serialization/deserialization (Gson)
- Protocol message formatting
- Error handling for malformed messages

**DataStore:**
- Persistent key-value storage (AndroidX Preferences DataStore)
- User settings (network IP, preferences)
- **[ENHANCED 2025-11-18]** SystemTools logging configuration (host, port, enabled)
- Survives app restarts

---

#### Logging Layer (NEW: Tri-Domain Observability - 2025-11-18)

**WHO:** CC-Ground-Side
**DATE:** 2025-11-18
**TIME:** 18:15 UTC
**ISSUES:** #99 (SystemTools Logging Integration), #113 (Timber Coverage Expansion)
**COMMIT:** a2e3bdb

**Technology:** Kotlin + Timber + Custom Sinks
**Pattern:** Multi-sink logging architecture

**Background:**
Ground-Side now participates in tri-domain log aggregation, forwarding both local logs and relayed Air-Side logs to SystemTools for centralized observability and debugging.

**Components:**

**LogHelper:**
- **Purpose:** Unified logging API with dynamic control
- **Technology:** Kotlin wrapper around Android Log + Timber
- **Features:**
  - Parallel operation support (logcat + Timber simultaneously)
  - Runtime enable/disable of each logging channel
  - Consistent API across codebase (`LogHelper.d()`, `LogHelper.i()`, etc.)
  - Gradual migration path from `Log.d()` to `Timber.d()`

**StructuredLogger:**
- **Purpose:** Multi-sink structured logging system
- **Technology:** Timber with custom Tree implementation
- **Sinks:**
  1. **FileSink:** Local file logging with rotation (50MB max, 3 files)
  2. **MemorySink:** Ring buffer for LogViewer UI (1000 entries)
  3. **NetworkSink:** TCP relay to SystemTools (port 5008)
- **Log Levels:** DEBUG, INFO, WARN, ERROR (configurable minimum)
- **Metadata:** Timestamp, level, tag, context, message

**NetworkSink:**
- **Purpose:** Real-time log streaming to SystemTools
- **Technology:** TCP client (Kotlin coroutines)
- **Configuration:**
  - **Host:** `localhost` (default, via ADB reverse) or user-configured IP
  - **Port:** 5008 (SystemTools log aggregator)
  - **Setup:** `adb reverse tcp:5008 tcp:5008` (development mode)
- **Features:**
  - Automatic connection management
  - Graceful degradation (continues if SystemTools unavailable)
  - Settings UI for dynamic configuration
  - Enable/disable via Advanced Settings

**UdpLogReceiver (Enhanced):**
- **Purpose:** Relay Air-Side logs to SystemTools
- **Receives:** UDP logs from Air-Side (port 5005)
- **Processing:**
  - Tags with "AIR-SIDE" context
  - Forwards to Timber → StructuredLogger
  - NetworkSink relays to SystemTools
- **Result:** SystemTools sees both Ground-Side and Air-Side logs in unified view

**AdvancedSettingsScreen (Enhanced):**
- **Purpose:** SystemTools logging configuration UI
- **Settings:**
  - SystemTools host (default: `localhost`)
  - SystemTools port (default: 5008)
  - Enable/disable network logging
- **Persistence:** DataStore flows
- **Reactivity:** Changes applied immediately on save

**AdvancedSettingsViewModel (Enhanced):**
- **Manages:** SystemTools configuration state
- **Functions:**
  - Load/save SystemTools settings
  - Validate configuration
  - Test connection to SystemTools
- **State:** Flows from SettingsRepository

**SettingsRepository (Enhanced):**
- **New Flows:**
  - `systemToolsLogHostFlow: Flow<String>` (default: "localhost")
  - `systemToolsLogPortFlow: Flow<Int>` (default: 5008)
  - `systemToolsLogEnabledFlow: Flow<Boolean>` (default: false)
- **Persistence:** DataStore backend
- **Migration:** Backward compatible (new settings opt-in)

**Logging Flow (Tri-Domain Observability):**
```
Ground-Side Log:
  App Code → LogHelper → Timber → StructuredLogger → NetworkSink → SystemTools (TCP port 5008)
                                                    → FileSink → Local files
                                                    → MemorySink → LogViewer UI

Air-Side Log Relay:
  Air-Side → UDP port 5005 → UdpLogReceiver → LogHelper → Timber → StructuredLogger → NetworkSink → SystemTools
```

**Configuration:**
- **Development Mode:** ADB reverse for localhost connectivity
- **Production Mode:** Direct IP configuration via settings
- **Default:** NetworkSink disabled (opt-in for debugging)

**Benefits:**
- **Centralized Observability:** All logs in SystemTools
- **Real-time Debugging:** Live log streaming
- **Multi-domain Correlation:** See Air/Ground logs together
- **No Code Changes:** Dynamic configuration via UI
- **Backward Compatible:** Existing code unaffected

**Testing:**
- Enable SystemTools logging in Advanced Settings
- Configure host/port (or use default with ADB reverse)
- Observe Ground-Side logs in SystemTools
- Air-Side logs automatically relayed when UDP receiver active

**Future Extensions:**
- Filtering by log level in UI
- Custom log contexts/tags
- Log export/sharing
- Performance metrics integration

---

### Dev-Tools (Diagnostic Support)

**Container:** Python desktop application
**Language:** Python 3.8+
**Pattern:** Tab-based GUI

**Primary Responsibilities:**
1. **Diagnostic Monitoring:** Real-time packet analysis
2. **Command Testing:** Interactive command builder
3. **Protocol Validation:** Response verification
4. **Log Analysis:** Air-Side log retrieval and parsing
5. **Connection Monitoring:** Multi-domain health tracking

**Key Components:**

#### ConnectionTab
- Manage TCP/UDP connections
- Display connection status
- Manual connect/disconnect

#### CameraTab
- Debug mode with manual command testing
- Focus controls, AF Hold, property setter
- Real-time diagnostics output
- Response validation and error analysis

#### NetworkTab
- Packet rate monitoring
- Message type statistics
- Latency measurement
- Protocol compliance checking

#### LogsTab
- SSH log retrieval from Air-Side
- Real-time log parsing
- Error highlighting
- Search and filter

---

## Functional Decomposition

### Primary Use Case: Capture Photo

**Flow:**
1. **Operator:** Taps capture button on H16 screen
2. **UI Layer:** CameraDashboard composable triggers ViewModel
3. **ViewModel:** CameraViewModel.capturePhoto()
4. **Repository:** CameraRepository.sendCommand()
5. **Network (Ground):** TcpCommandClient sends JSON command
6. **Network (Air):** NetworkService receives command
7. **Command Handler:** CommandHandler routes to CameraService
8. **Camera Control:** CameraService.triggerShutter()
9. **SDK:** Sony SDK executes shutter command
10. **Camera:** Sony Alpha captures photo
11. **Response:** CameraService sends success response
12. **Network (Air):** NetworkService sends response
13. **Network (Ground):** TcpCommandClient receives response
14. **Repository:** CameraRepository processes response
15. **ViewModel:** Updates UI state
16. **UI Layer:** CameraDashboard shows success indicator

**End-to-End Latency:** <50ms typical

---

### Secondary Use Case: Monitor Status

**Flow (5Hz continuous):**
1. **StatusBroadcaster:** Queries camera and system every 200ms
2. **Camera/System:** Return current status
3. **StatusBroadcaster:** Serializes to JSON
4. **Network (Air):** UDP broadcast on port 5001
5. **Network (Ground):** UdpListener receives broadcast
6. **Repository:** Deserializes and updates state
7. **ViewModel:** Publishes new state to UI
8. **UI Layer:** StatusDisplay updates indicators

**Continuous, fire-and-forget (no acknowledgment)**

---

## Component Interactions

### Cross-Domain Communication

**Air ↔ Ground:**
- TCP: Bidirectional command/response (Ground initiates)
- UDP Status: Air → Ground unidirectional broadcast
- UDP Heartbeat: Bidirectional health monitoring

**Air ↔ Dev-Tools:**
- TCP: Same protocol as Ground (test commands)
- UDP: Listen-only monitoring
- SSH: Log retrieval, diagnostics

**Ground ↔ Dev-Tools:**
- No direct communication
- Both connect to Air-Side independently

---

### Intra-Domain Communication

**Air-Side:**
- Function calls (same process)
- Thread-safe queues for cross-thread communication
- Mutexes for shared state (camera status)

**Ground-Side:**
- ViewModel observes Repository StateFlow
- UI observes ViewModel StateFlow
- All reactive (no polling)

**Dev-Tools:**
- Tkinter event loop
- Callback-based UI updates
- Thread-safe queues for network→UI

---

## Design Principles

### 1. Specification-First Architecture

**Principle:** Single source of truth for camera properties

**Implementation:**
- JSON specification files in `docs/protocol/`
- PropertyLoader in both Air-Side (C++) and Ground-Side (Kotlin)
- Version-synced between domains
- UI auto-generated from specs

**Benefits:**
- Adding new property only requires spec file update
- No code changes for new properties (if SDK supports)
- Validation consistent Air/Ground
- Documentation embedded in specs

---

### 2. Fail-Safe Defaults

**Principle:** System degrades gracefully on errors

**Implementation:**
- Camera disconnect → Keep broadcasting (status shows disconnected)
- Network disconnect → Auto-reconnect with exponential backoff
- Invalid command → Return error, don't crash
- Missing property → Use safe default or skip

---

### 3. Separation of Concerns

**Principle:** Each component has single, well-defined responsibility

**Examples:**
- CameraService: Only camera control, no networking
- NetworkService: Only networking, no camera knowledge
- PropertyLoader: Only specs, no command execution

**Benefits:**
- Easier testing (mock dependencies)
- Clearer responsibilities
- Simpler debugging
- Better maintainability

---

### 4. Asynchronous by Default

**Principle:** Non-blocking I/O for responsiveness

**Implementation:**
- Air-Side: Multi-threaded (TCP thread, UDP threads, camera thread)
- Ground-Side: Kotlin coroutines (all network I/O async)
- Dev-Tools: Threading for network I/O

**Benefits:**
- UI remains responsive
- No blocking on network latency
- Can handle multiple simultaneous operations

---

## Quality Attributes

### Performance

**Requirements:**
- Command response: <50ms
- Status update rate: 5 Hz (200ms)
- Heartbeat rate: 1 Hz

**Achieved:**
- Average response: 20-30ms (TCP + SDK overhead)
- Status broadcast: Exactly 200ms (timer-based)
- Minimal CPU usage: <20% on Pi 5, <5% on H16

---

### Reliability

**Mechanisms:**
- Auto-reconnect on network/camera disconnect
- Heartbeat timeout detection (10 seconds)
- Docker restart policy (always restart on crash)
- Error logging and diagnostics

**MTBF (Mean Time Between Failures):**
- Target: >10 hours continuous operation
- Achieved: >20 hours in testing

---

### Maintainability

**Factors:**
- Clear component boundaries
- Comprehensive documentation (architecture, code comments)
- Consistent naming conventions
- Property-based testing possible
- Diagnostic tools (SystemTools)

---

### Extensibility

**Extension Points:**
- New camera properties: Add to JSON specs
- New command types: Add to CommandHandler routing
- New UI screens: Add Jetpack Compose composables
- New diagnostic tools: Add tabs to SystemTools

---

## Related Documents

- **Visual:** C4 Level 2-3 diagrams (container and component)
- **Data:** `view-data.md` - Data architecture
- **Integration:** `view-integration.md` - Cross-domain communication
- **Deployment:** `view-deployment.md` - Physical deployment

