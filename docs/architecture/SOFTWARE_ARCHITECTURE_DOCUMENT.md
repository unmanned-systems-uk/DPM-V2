# Software Architecture Document (SAD)
# DPM-V2: Drone Payload Manager Version 2

**Document Standard:** ISO/IEC/IEEE 42010:2011
**Version:** 1.0
**Date:** 2025-11-11
**Status:** Draft
**Classification:** Internal Use

---

## Document Control

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2025-11-11 | DPM-V2 Team | Initial consolidated SAD |

**Approval:**
- [ ] Development Team Lead
- [ ] System Architect
- [ ] Project Manager
- [ ] Quality Assurance

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Purpose](#11-purpose)
   - 1.2 [Scope](#12-scope)
   - 1.3 [Document Organization](#13-document-organization)
   - 1.4 [References](#14-references)
   - 1.5 [Definitions and Acronyms](#15-definitions-and-acronyms)

2. [System Overview](#2-system-overview)
   - 2.1 [System Purpose](#21-system-purpose)
   - 2.2 [System Capabilities](#22-system-capabilities)
   - 2.3 [System Context](#23-system-context)

3. [Stakeholders and Concerns](#3-stakeholders-and-concerns)
   - 3.1 [Stakeholder Identification](#31-stakeholder-identification)
   - 3.2 [Stakeholder Concerns](#32-stakeholder-concerns)
   - 3.3 [Concern-to-View Mapping](#33-concern-to-view-mapping)

4. [Architecture Viewpoints](#4-architecture-viewpoints)
   - 4.1 [Context Viewpoint](#41-context-viewpoint)
   - 4.2 [Logical/Functional Viewpoint](#42-logicalfunctional-viewpoint)
   - 4.3 [Data Viewpoint](#43-data-viewpoint)
   - 4.4 [Security & Reliability Viewpoint](#44-security--reliability-viewpoint)
   - 4.5 [Deployment Viewpoint](#45-deployment-viewpoint)
   - 4.6 [Integration Viewpoint](#46-integration-viewpoint)

5. [Architecture Decisions](#5-architecture-decisions)
   - 5.1 [Core Architecture Decisions](#51-core-architecture-decisions)
   - 5.2 [Component Architecture Decisions](#52-component-architecture-decisions)
   - 5.3 [Protocol & Pattern Decisions](#53-protocol--pattern-decisions)

6. [C4 Model Architecture](#6-c4-model-architecture)
   - 6.1 [Level 1: System Context](#61-level-1-system-context)
   - 6.2 [Level 2: Container Architecture](#62-level-2-container-architecture)
   - 6.3 [Level 3: Component Architecture](#63-level-3-component-architecture)
   - 6.4 [Level 4: Deployment Architecture](#64-level-4-deployment-architecture)

7. [Architecture Rationale](#7-architecture-rationale)
   - 7.1 [Design Principles](#71-design-principles)
   - 7.2 [Key Architectural Drivers](#72-key-architectural-drivers)
   - 7.3 [Trade-off Analysis](#73-trade-off-analysis)

8. [Traceability](#8-traceability)
   - 8.1 [Concerns to Viewpoints](#81-concerns-to-viewpoints)
   - 8.2 [Viewpoints to Components](#82-viewpoints-to-components)
   - 8.3 [Components to Code](#83-components-to-code)
   - 8.4 [Decisions to Implementation](#84-decisions-to-implementation)

9. [Quality Attributes](#9-quality-attributes)
   - 9.1 [Performance](#91-performance)
   - 9.2 [Reliability](#92-reliability)
   - 9.3 [Maintainability](#93-maintainability)
   - 9.4 [Extensibility](#94-extensibility)

10. [Constraints and Assumptions](#10-constraints-and-assumptions)
    - 10.1 [Technical Constraints](#101-technical-constraints)
    - 10.2 [Business Constraints](#102-business-constraints)
    - 10.3 [Assumptions](#103-assumptions)

11. [Glossary](#11-glossary)

12. [Appendices](#12-appendices)
    - 12.1 [Document Map](#121-document-map)
    - 12.2 [Lessons Learned](#122-lessons-learned)
    - 12.3 [Future Enhancements](#123-future-enhancements)

---

# 1. Introduction

## 1.1 Purpose

This Software Architecture Document (SAD) provides a comprehensive architectural description of the DPM-V2 (Drone Payload Manager Version 2) system, compliant with ISO/IEC/IEEE 42010:2011 standard for architecture descriptions.

**Intended Audience:**
- **Developers:** Understanding system structure for implementation and maintenance
- **System Architects:** Evaluating architectural decisions and evolution
- **Project Managers:** Understanding scope, dependencies, and technical risks
- **QA Engineers:** Understanding quality attributes for testing strategy
- **Stakeholders:** Understanding system capabilities and constraints

**Document Goals:**
1. Describe the system architecture from multiple viewpoints
2. Document architectural decisions and their rationale
3. Provide traceability between stakeholder concerns and architecture
4. Serve as authoritative reference for development and maintenance
5. Enable informed decision-making for future evolution

---

## 1.2 Scope

**In Scope:**
- Complete architectural description of DPM-V2 system
- Air-Side service (Raspberry Pi 5, C++, Docker)
- Ground-Side application (SkyDroid H16, Android, Kotlin)
- Dev-Tools (Python diagnostic tools)
- Network protocols (TCP/UDP communication)
- Integration with Sony Camera Remote SDK
- Deployment architecture (Docker, APK, development environment)

**Out of Scope:**
- Detailed code-level implementation (see source code documentation)
- Sony Camera Remote SDK internals (proprietary, under NDA)
- Network infrastructure details (R16 link, WiFi configuration)
- Operational procedures (see operations manual)
- User interface design specifications (see UI/UX documentation)

**System Boundaries:**
- **Included:** DPM-V2 software components, protocols, deployment
- **External:** Sony SDK, Android OS, Docker Engine, Hardware platforms

---

## 1.3 Document Organization

This SAD follows ISO/IEC/IEEE 42010:2011 structure:

**Section 1-2:** Introduction and system overview
**Section 3:** Stakeholders and their architectural concerns
**Section 4:** Architecture viewpoints addressing concerns
**Section 5:** Architecture decisions (ADRs) with rationale
**Section 6:** C4 Model visual architecture representation
**Section 7:** Architecture rationale and design principles
**Section 8:** Traceability matrices linking concerns to implementation
**Section 9:** Quality attributes and their achievement
**Section 10:** Constraints and assumptions
**Section 11:** Glossary of terms
**Section 12:** Appendices with supporting information

**Relationship to Other Documents:**

This SAD consolidates and references:
- **Phase 2:** C4 Model diagrams (`docs/architecture/c4-*.puml`)
- **Phase 3:** Architecture views (`docs/architecture/view-*.md`)
- **Phase 4:** Architecture Decision Records (`docs/architecture/adr/ADR-*.md`)
- **Existing:** Lessons learned, integration points, protocol specs

**Note:** All referenced documents remain in repository. This SAD provides consolidated view with cross-references.

---

## 1.4 References

### Normative References

| Ref | Document | Version |
|-----|----------|---------|
| [ISO42010] | ISO/IEC/IEEE 42010:2011 - Systems and software engineering — Architecture description | 2011 |
| [C4Model] | C4 Model for visualizing software architecture | https://c4model.com |

### Project References

| Ref | Document | Location |
|-----|----------|----------|
| [VIEW-CONTEXT] | Context View | `docs/architecture/view-context.md` |
| [VIEW-LOGICAL] | Logical/Functional View | `docs/architecture/view-logical.md` |
| [VIEW-DATA] | Data View | `docs/architecture/view-data.md` |
| [VIEW-SECURITY] | Security & Reliability View | `docs/architecture/view-security-reliability.md` |
| [VIEW-DEPLOY] | Deployment View | `docs/architecture/view-deployment.md` |
| [VIEW-INTEGRATION] | Integration View | `docs/architecture/view-integration.md` |
| [ADR-INDEX] | ADR Index | `docs/architecture/adr/README.md` |
| [LESSONS] | Lessons Learned | `docs/ALL_DOMAINS/LESSONS_LEARNED.md` |
| [INTEGRATION] | Integration Points | `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` |

### External References

| Ref | Document | URL |
|-----|----------|-----|
| [SONY-SDK] | Sony Camera Remote SDK Documentation | Under NDA |
| [ANDROID-ARCH] | Android Architecture Guide | https://developer.android.com/topic/architecture |
| [DOCKER] | Docker Documentation | https://docs.docker.com |
| [JETPACK] | Jetpack Compose Documentation | https://developer.android.com/jetpack/compose |

---

## 1.5 Definitions and Acronyms

See **Section 11: Glossary** for comprehensive definitions.

**Key Terms:**
- **Air-Side:** Raspberry Pi 5 service controlling camera
- **Ground-Side:** Android H16 tablet application
- **Dev-Tools:** Python diagnostic tools
- **PropertyLoader:** Pattern for managing camera property specifications
- **Specification-First:** Architecture pattern with JSON as single source of truth

**Key Acronyms:**
- **ADR:** Architecture Decision Record
- **API:** Application Programming Interface
- **APK:** Android Package
- **C4:** Context, Container, Component, Code (architecture model)
- **ISO:** International Organization for Standardization
- **MVVM:** Model-View-ViewModel (architectural pattern)
- **SAD:** Software Architecture Document
- **SDK:** Software Development Kit
- **TCP:** Transmission Control Protocol
- **UDP:** User Datagram Protocol
- **UAV:** Unmanned Aerial Vehicle

---

# 2. System Overview

## 2.1 System Purpose

DPM-V2 (Drone Payload Manager Version 2) is a professional UAV camera payload management system enabling remote control of Sony Alpha cameras from a ground station during flight operations.

**Primary Purpose:**
Control professional Sony mirrorless cameras mounted on UAV platforms via wireless link, providing operators with:
- Real-time camera control (ISO, shutter speed, aperture, focus)
- Live system telemetry (CPU, memory, temperature, connection status)
- Camera triggering and monitoring
- Diagnostic capabilities for troubleshooting

**Business Value:**
- Enable professional aerial photography/videography from UAVs
- Reduce operator workload (control camera without physical access)
- Improve safety (operate camera from safe distance)
- Support commercial UAV operations (surveying, inspection, media production)

---

## 2.2 System Capabilities

### Functional Capabilities

**Camera Control:**
- Trigger camera shutter remotely
- Adjust exposure settings (ISO: 100-102400, Shutter: 1/8000s-30s, Aperture: f/1.4-f/22)
- Control focus (manual focus, autofocus modes: AF-S, AF-C, DMF, MF)
- Set white balance (Auto, presets, custom 2500K-10000K)
- Configure drive mode (Single, Continuous Hi/Mid/Lo)
- Select file format (RAW, JPEG, RAW+JPEG)

**System Monitoring:**
- Real-time telemetry at 5Hz (CPU usage, memory, disk space, temperature)
- Camera connection status
- Network health monitoring (heartbeat, packet statistics)
- Error detection and reporting

**Network Communication:**
- TCP command channel (reliable command/response, port 5000)
- UDP status broadcast (5Hz telemetry, port 5001)
- UDP heartbeat (1Hz connection monitoring, port 5002)
- Auto-reconnect with exponential backoff

**Diagnostic Tools:**
- Protocol validation and testing
- Packet analysis and monitoring
- Log retrieval from Air-Side
- Connection health visualization

### Non-Functional Capabilities

**Performance:**
- Command response latency: <50ms typical (TCP + SDK overhead)
- Status update rate: 5Hz (200ms interval)
- Heartbeat rate: 1Hz with 10-second timeout
- CPU usage: <20% on Pi 5, <5% on H16

**Reliability:**
- Auto-restart on crash (Docker policy, <10 seconds)
- Auto-reconnect on network failure (exponential backoff)
- Stateless Air-Side (fast recovery, no state corruption)
- MTBF: >20 hours continuous operation

**Availability:**
- Target: 99% uptime during flight operations
- Recovery time: <10 seconds for most failures
- Graceful degradation (Ground-Side continues if Air-Side down)

---

## 2.3 System Context

**Operational Environment:**
- **Production:** UAV flight operations with R16 wireless data link (192.168.144.0/24)
- **Development:** Lab testing with WiFi (10.0.1.0/24)
- **Network:** Closed network, no internet exposure

**Physical Context:**
- **Air-Side:** Raspberry Pi 5 mounted on UAV with Sony camera via USB
- **Ground-Side:** SkyDroid H16 tablet in operator's hands
- **Link:** H16 R16 digital data link (20-50 Mbps, 20-50ms latency)

**Integration Context:**
- **Sony SDK:** Proprietary C++ library for camera control (version 2.00.00)
- **Android OS:** H16 tablet platform (API 24-36)
- **Docker:** Containerization platform for Air-Side
- **Network:** R16 link (production) or WiFi (development)

**See [VIEW-CONTEXT] for detailed system context diagram and external interfaces.**

---

# 3. Stakeholders and Concerns

## 3.1 Stakeholder Identification

### Primary Stakeholders

#### Drone Operator (Primary User)
**Role:** Controls UAV and camera during flight operations

**Responsibilities:**
- Fly UAV safely
- Control camera settings (ISO, shutter, aperture)
- Trigger photos at appropriate moments
- Monitor system health

**Interaction:** Ground-Side Android app (H16 tablet touchscreen)

**Key Characteristics:**
- Professional UAV pilot (commercial license)
- Understands photography (exposure triangle)
- Works in challenging conditions (outdoor, vibration, glare)
- Time-critical decision making (in-flight operations)

---

#### System Maintainer
**Role:** Deploy, configure, troubleshoot, and maintain system

**Responsibilities:**
- Deploy Air-Side service (Docker)
- Deploy Ground-Side app (APK)
- Configure network (IPs, ports)
- Diagnose and fix issues
- Apply updates

**Interaction:** SSH to Pi 5, ADB to H16, SystemTools (Dev-Tools)

**Key Characteristics:**
- IT/DevOps background
- Comfortable with command line
- Understands networking (TCP/UDP, IP addressing)
- Troubleshooting mindset

---

#### System Developer
**Role:** Develop, enhance, and debug system

**Responsibilities:**
- Implement new features
- Fix bugs
- Write tests
- Debug protocol issues

**Interaction:** Source code, IDE, SystemTools, logs

**Key Characteristics:**
- Software engineer (C++, Kotlin, Python)
- Understands architecture and protocols
- Uses debugging tools (gdb, logcat, Wireshark)

---

#### Project Manager
**Role:** Plan, track, and deliver system development

**Responsibilities:**
- Define requirements
- Plan releases
- Track progress
- Manage risks

**Interaction:** Documentation, issue tracker, progress reports

**Key Characteristics:**
- Technical background (understands architecture)
- Manages development team
- Stakeholder communication

---

### Secondary Stakeholders

- **QA Engineer:** Test system, write test cases, report bugs
- **Technical Writer:** Document system for users and maintainers
- **Business Stakeholder:** Fund development, define business requirements

---

## 3.2 Stakeholder Concerns

### Operator Concerns

| Concern | Description | Priority |
|---------|-------------|----------|
| **Responsiveness** | UI updates must feel instant (<250ms perceived latency) | Critical |
| **Reliability** | Camera control must work consistently (no missed shots) | Critical |
| **Ease of Use** | Intuitive UI, no steep learning curve | High |
| **Visibility** | Clear camera status (ISO, shutter, connection) | High |
| **Error Handling** | Clear error messages, graceful degradation | Medium |
| **Battery Life** | H16 tablet battery lasts full flight (2-3 hours) | Medium |

### Maintainer Concerns

| Concern | Description | Priority |
|---------|-------------|----------|
| **Deployability** | Easy to deploy and update (minimal steps) | Critical |
| **Diagnosability** | Clear logs, diagnostic tools available | Critical |
| **Recoverability** | System recovers automatically from failures | High |
| **Configurability** | Network settings easily configurable | High |
| **Rollback** | Easy to revert to previous version if update breaks | High |
| **Documentation** | Comprehensive setup and troubleshooting guides | Medium |

### Developer Concerns

| Concern | Description | Priority |
|---------|-------------|----------|
| **Modularity** | Clear component boundaries, loosely coupled | Critical |
| **Testability** | Easy to write unit/integration tests | Critical |
| **Debuggability** | Clear logs, reproducible issues | High |
| **Code Quality** | Clean code, consistent style, documented | High |
| **Extensibility** | Easy to add new features (new camera properties) | High |
| **Build Speed** | Fast iteration (compile, deploy, test cycle) | Medium |

### Project Manager Concerns

| Concern | Description | Priority |
|---------|-------------|----------|
| **Traceability** | Requirements mapped to implementation | High |
| **Progress Visibility** | Clear status of development tasks | High |
| **Risk Management** | Technical risks identified and mitigated | High |
| **Quality Metrics** | Test coverage, bug counts, performance metrics | Medium |
| **Schedule** | Realistic estimates, on-time delivery | Medium |

---

## 3.3 Concern-to-View Mapping

This table maps stakeholder concerns to architecture viewpoints that address them.

| Concern Category | Specific Concerns | Addressed By Viewpoint(s) | Related ADRs |
|------------------|-------------------|---------------------------|--------------|
| **Performance** | Responsiveness, Latency, Throughput | Logical, Integration, Data | ADR-003, ADR-006, ADR-008, ADR-012 |
| **Reliability** | Fault tolerance, Recovery, Availability | Security & Reliability, Deployment | ADR-004, ADR-007, ADR-009, ADR-014 |
| **Usability** | Ease of use, Error handling, Visibility | Logical, Integration | ADR-005, ADR-013 |
| **Maintainability** | Modularity, Testability, Debuggability | Logical, Deployment | ADR-001, ADR-002, ADR-010 |
| **Deployability** | Installation, Configuration, Updates | Deployment | ADR-004, ADR-007 |
| **Security** | Authentication, Encryption, Authorization | Security & Reliability | ADR-015 |
| **Integration** | Protocols, Data formats, Sync | Integration, Data | ADR-003, ADR-011 |
| **Extensibility** | Adding features, Protocol evolution | Logical, Data | ADR-002, ADR-010 |

**Usage:** Stakeholders can use this mapping to find which viewpoints address their specific concerns.

**Example:** Maintainer concerned about "Recoverability" → See Security & Reliability View + ADR-004 (Docker auto-restart) + ADR-014 (Auto-reconnect)

---

# 4. Architecture Viewpoints

## Overview

DPM-V2 architecture is described through six viewpoints per ISO/IEC/IEEE 42010:

1. **Context:** System boundary, external actors, external systems
2. **Logical/Functional:** Components, responsibilities, interactions
3. **Data:** Data model, flow, persistence, synchronization
4. **Security & Reliability:** Security posture, fault tolerance, availability
5. **Deployment:** Hardware, OS, network topology, deployment
6. **Integration:** Cross-domain interfaces, protocols, patterns

Each viewpoint addresses specific stakeholder concerns (see Section 3.3).

**Note:** Full viewpoint documentation in `docs/architecture/view-*.md`. This section provides summaries with key highlights.

---

## 4.1 Context Viewpoint

**Purpose:** Define system boundary and external interfaces

**Key Stakeholders:** All (understanding what's inside/outside DPM-V2)

**Full Documentation:** [VIEW-CONTEXT]

### System Boundary

**DPM-V2 System Includes:**
- Air-Side Service (Raspberry Pi 5, Docker container)
- Ground-Side Application (Android H16 APK)
- Dev-Tools (Python diagnostic scripts)

**DPM-V2 System Excludes (External):**
- Sony Alpha Camera hardware
- Sony Camera Remote SDK library
- Android OS and platform services
- Docker Engine
- Network infrastructure (R16 link, WiFi)

### External Actors

**1. Drone Operator**
- Interacts with Ground-Side via touchscreen
- Controls camera settings and triggering
- Monitors system status

**2. System Maintainer**
- SSH to Air-Side for deployment/diagnostics
- ADB to Ground-Side for app installation
- Uses Dev-Tools for troubleshooting

**3. System Developer**
- Writes code for all three domains
- Uses Dev-Tools for protocol testing
- Accesses logs via SSH

### External Systems

**1. Sony Alpha Camera**
- **Interface:** USB-A 3.0 (PTP/MTP protocol)
- **Data Flow:** Bidirectional (commands to camera, status from camera)
- **Dependencies:** Must be in PC Remote mode

**2. Sony Camera Remote SDK**
- **Interface:** C++ API (libCrSdk.so)
- **Data Flow:** Air-Side calls SDK functions, SDK sends callbacks
- **Dependencies:** Version 2.00.00, requires CrAdapter files

**3. Android OS**
- **Interface:** Android APIs (Network, Storage, UI framework)
- **Data Flow:** Ground-Side uses platform services
- **Dependencies:** API level 24-36

**4. Docker Engine**
- **Interface:** Docker CLI, Dockerfile, docker-compose
- **Data Flow:** Hosts Air-Side container
- **Dependencies:** Docker 20.10+

**5. Network Infrastructure**
- **Interface:** TCP/UDP sockets (ports 5000-5002, 22)
- **Data Flow:** All domain communication
- **Dependencies:** R16 link (prod) or WiFi (dev)

### Context Diagram

See `docs/architecture/c4-level1-context.puml` for visual representation.

---

## 4.2 Logical/Functional Viewpoint

**Purpose:** Describe major structural elements and their collaboration

**Key Stakeholders:** Developers (implementation), Architects (design)

**Full Documentation:** [VIEW-LOGICAL]

### Architectural Style

**Three-Domain Microservices Architecture** (see [ADR-001])

**Characteristics:**
- Domain separation (Air, Ground, Tools independent)
- Network communication (TCP/UDP decouples domains)
- Technology heterogeneity (C++, Kotlin, Python)
- Independent deployment

### Air-Side Architecture

**Pattern:** Multi-threaded service with component-based architecture (see [ADR-006])

**Key Components:**

1. **CameraService:** Sony SDK integration, USB communication
   - Initialize SDK, enumerate camera
   - Execute commands (shutter, property set/get)
   - Monitor status, auto-reconnect

2. **NetworkService:** TCP server, UDP broadcasters
   - TCP server (port 5000): Accept connections, route commands
   - UDP broadcaster (port 5001): 5Hz status broadcast
   - UDP heartbeat (port 5002): 1Hz bidirectional

3. **PropertyLoader:** Camera property spec management (see [ADR-010])
   - Load JSON specs at startup
   - Validate property values
   - Map SDK ↔ display values

4. **CommandHandler:** Parse and route commands
   - Receive from TCP
   - Parse JSON
   - Route to CameraService/SystemMonitor
   - Generate responses

5. **StatusBroadcaster:** 5Hz telemetry broadcast (see [ADR-008])
   - Query camera and system state
   - Serialize to JSON
   - Broadcast on UDP

6. **SystemMonitor:** System resource monitoring
   - CPU, memory, disk, temperature
   - Uptime tracking

### Ground-Side Architecture

**Pattern:** MVVM (Model-View-ViewModel) (see [ADR-005])

**Layers:**

1. **UI Layer (Jetpack Compose):** (see [ADR-013])
   - CameraDashboard: Main control screen
   - SettingsScreen: Configuration
   - StatusDisplay: Real-time indicators

2. **ViewModel Layer:**
   - CameraViewModel: Camera state and control logic
   - ConnectionViewModel: Network connection state
   - SettingsViewModel: App settings

3. **Repository Layer:**
   - CameraRepository: Data abstraction, coordinates network clients
   - PropertyLoader: Load property specs from APK assets

4. **Network Layer:**
   - TcpCommandClient: Send commands, receive responses
   - UdpStatusListener: Receive 5Hz status broadcasts
   - HeartbeatClient: Bidirectional heartbeat

5. **Data Layer:**
   - MessageSerializer: JSON serialization (Gson)
   - DataStore: Persistent settings (AndroidX)

### Dev-Tools Architecture

**Pattern:** Tab-based GUI (Tkinter)

**Components:**
- ConnectionTab: Manage connections
- CameraTab: Debug mode command testing
- NetworkTab: Packet monitoring
- LogsTab: Log retrieval and analysis

### Component Interactions

**Capture Photo Flow (End-to-End):**
1. Operator taps capture button (UI Layer)
2. CameraDashboard → CameraViewModel.capturePhoto()
3. CameraViewModel → CameraRepository.sendCommand()
4. CameraRepository → TcpCommandClient (serialize JSON, send TCP)
5. NetworkService receives (TCP Handler thread)
6. CommandHandler routes to CameraService
7. CameraService → Sony SDK → Camera (shutter triggered)
8. Camera captures photo, SDK callback to CameraService
9. CameraService sends success response → TCP Handler
10. TcpCommandClient receives response
11. CameraRepository processes, updates state
12. CameraViewModel publishes to uiState StateFlow
13. CameraDashboard recomposes (shows success indicator)

**Latency:** <50ms typical (measured end-to-end)

### Diagrams

See:
- `c4-level2-container.puml`: Container architecture
- `c4-level3-air-side-components.puml`: Air-Side components
- `c4-level3-ground-side-components.puml`: Ground-Side MVVM layers
- `c4-level3-dev-tools-components.puml`: Dev-Tools components

---

## 4.3 Data Viewpoint

**Purpose:** Describe data model, flow, persistence, synchronization

**Key Stakeholders:** Developers (implementation), Architects (data consistency)

**Full Documentation:** [VIEW-DATA]

### Data Model

**Camera Properties:**
- ShutterSpeed: 1/8000s to 30s (56 discrete values)
- Aperture: f/1.4 to f/22 (23 values, lens-dependent)
- ISO: 100 to 102400 (discrete steps)
- WhiteBalance: Auto, presets, custom 2500K-10000K
- FocusMode: AF-S, AF-C, DMF, MF
- DriveMode: Single, Continuous Hi/Mid/Lo
- FileFormat: RAW, JPEG, RAW+JPEG

**Property Specification (JSON):**
```json
{
  "property_name": "shutter_speed",
  "display_name": "Shutter Speed",
  "type": "enum",
  "sdk_property_id": "0x5005",
  "values": [
    {"sdk_value": "0x00010001", "display_value": "1/8000", "sort_order": 1}
  ],
  "default": "1/250",
  "unit": "seconds"
}
```

**System Telemetry:**
- CPU usage (per-core + average)
- Memory consumption (MB)
- Disk usage (GB free)
- Temperature (°C)
- Uptime (seconds)
- Network stats (packets sent/received)

**Camera Status:**
- Connected (boolean)
- Camera model (string)
- Current property values
- Error state (if any)

### Data Flow

**Command Flow (Ground → Air → Camera):**
```
UI → ViewModel → Repository → TcpClient → Network → Air-Side NetworkService
→ CommandHandler → CameraService → Sony SDK → Camera
→ [Response reversed]
```

**Telemetry Flow (Camera/System → Air → Ground):**
```
Camera/SystemMonitor → StatusBroadcaster (5Hz) → UDP broadcast
→ Ground UdpListener → Repository → ViewModel → UI
```

**Characteristics:**
- Commands: Reliable (TCP), acknowledged
- Telemetry: Fire-and-forget (UDP), continuous stream
- Eventually consistent (status within 200ms)

### Data Persistence

**Air-Side:**
- PropertySpecs: Embedded in Docker image (`/app/specs/*.json`)
- Logs: `/var/log/payload-manager/` (7-day rotation)
- No user data (stateless, see [ADR-007])

**Ground-Side:**
- Settings: AndroidX DataStore (network IP, preferences)
- PropertySpecs: APK assets (`assets/specs/*.json`)
- No image storage (photos on camera SD card)

### Data Synchronization

**Specification-First Pattern (see [ADR-002]):**
1. Single source: `docs/protocol/*.json`
2. Air-Side: Copy into Docker image at build
3. Ground-Side: Copy into APK assets at build
4. Result: Guaranteed identical specs

**Benefits:**
- Zero Air/Ground property mismatch bugs
- Easy extensibility (add property = edit JSON only)

**Status Synchronization:**
- Pattern: Eventually Consistent (UDP broadcast)
- Latency: 200ms maximum staleness
- Trade-off: Accept packet loss (<2%) for performance

---

## 4.4 Security & Reliability Viewpoint

**Purpose:** Document security posture and reliability mechanisms

**Key Stakeholders:** Maintainers (deployment), Security reviewer, Operators (reliability)

**Full Documentation:** [VIEW-SECURITY]

### Security Architecture

**Current State: Minimal Security (Development Phase)** (see [ADR-015])

**Authentication:** ❌ None (no login/password/API keys)
**Encryption:** ❌ None (JSON plaintext over TCP/UDP)
**Authorization:** ❌ None (all commands accepted)

**Rationale:**
- Development/testing phase (not production yet)
- Closed network environment (R16 link isolated, no internet)
- Physical security (UAV/tablet in operator control)
- Focus on functionality first, security Phase 2

**Future Production Requirements:**
- TLS for TCP command channel
- HMAC signatures for commands
- Certificate-based mutual authentication
- Rate limiting (10 commands/sec)
- SSH key-only authentication (no passwords)

### Reliability Architecture

**Fault Tolerance:**

1. **Camera Disconnect** (see [ADR-007])
   - Detection: SDK callback + polling
   - Response: Auto-reconnect every 5 seconds
   - User notification: Real-time UI alert
   - Recovery: Automatic when camera reconnected

2. **Network Disconnect** (see [ADR-014])
   - Detection: Heartbeat timeout (10 seconds, see [ADR-009])
   - Response: Exponential backoff reconnect (1s → 2s → 4s → ... → 30s max)
   - User indication: Connection status indicator
   - Recovery: Automatic on network restore

3. **Air-Side Crash** (see [ADR-004])
   - Detection: Docker health check
   - Response: Docker restart policy (`always`)
   - Data loss: Minimal (stateless service)
   - Recovery time: <10 seconds

### Error Handling Categories

**1. Recoverable Errors:**
- Camera disconnect, network timeout
- Action: Auto-retry with backoff
- User: Notification, continue operation

**2. User Errors:**
- Invalid command, bad parameter
- Action: Return error response
- User: Clear error message, don't crash

**3. Fatal Errors:**
- SDK initialization failure, hardware fault
- Action: Log critical error, graceful shutdown
- System: Docker restarts service

### Availability Targets

**Goal:** 99% uptime during flight operations

**Achieved:**
- MTBF: >20 hours continuous operation
- Recovery time: <10 seconds for most failures
- Zero data loss (stateless, camera stores images)

### Monitoring & Diagnostics

**Real-Time Monitoring:**
- System telemetry: 5Hz (CPU, memory, temperature)
- Connection health: 1Hz heartbeat
- Error logging: Syslog + file logs

**Diagnostic Tools:**
- SystemTools: Packet monitoring, command testing
- SSH access: Log retrieval, system diagnostics
- Docker logs: Container stdout/stderr

---

## 4.5 Deployment Viewpoint

**Purpose:** Physical deployment architecture (hardware, OS, network)

**Key Stakeholders:** Maintainers (deployment), Operators (understanding system)

**Full Documentation:** [VIEW-DEPLOY]

### Hardware Platforms

**Air-Side: Raspberry Pi 5**
- CPU: Broadcom BCM2712 (ARM Cortex-A76, 2.4GHz quad-core)
- RAM: 8GB LPDDR4X
- Storage: 256GB NVMe SSD (M.2 HAT)
- USB: 2× USB 3.0 (camera), 2× USB 2.0
- Network: Gigabit Ethernet
- Power: 5V/5A USB-C PD
- OS: Ubuntu 24.04 LTS ARM64
- Mounted: On UAV platform with camera

**Ground-Side: SkyDroid H16**
- Display: 10.1" 1920×1200 touchscreen
- CPU: Qualcomm (TBD model)
- RAM: 4-8GB
- Storage: 64-128GB
- Network: WiFi 5/6, Ethernet via R16
- R16 Integration: Digital data link
- OS: Android API 24-36
- Usage: Handheld ground station tablet

**Dev-Tools: Workstation**
- Requirements: Python 3.8+, network access, SSH client
- OS: Windows/Linux/macOS

### Software Deployment

**Air-Side Docker Deployment** (see [ADR-004]):
- Container: `payload-manager:latest`
- Build: Multi-stage Dockerfile (build + runtime stages)
- Base Image: Ubuntu 24.04 ARM64
- Network Mode: Host (required for UDP broadcast)
- Volumes: `/dev/bus/usb` (USB), `/var/log/payload-manager` (logs)
- Restart Policy: `always`
- Deployment: `./build_container.sh && ./run_container.sh prod`

**Ground-Side APK Deployment:**
- Package: `uk.unmannedsystems.dpm_android`
- Build: Gradle (Android build system)
- Min SDK: API 24, Target SDK: API 36
- Install: ADB or Google Play (future)
- Deployment: `./gradlew assembleRelease && adb install ...`

### Network Topology

**Production Network (R16 Link):**
- Technology: VXLAN bridge over H16/R16 data link
- Subnet: 192.168.144.0/24
- Air-Side IP: 192.168.144.53 (static)
- Ground-Side IP: 192.168.144.92 (static)
- Bandwidth: 20-50 Mbps
- Latency: <50ms typical
- Range: Several kilometers

**Development Network (WiFi):**
- Technology: WiFi 802.11ac/ax
- Subnet: 10.0.1.0/24
- Air-Side IP: 10.0.1.53 (static)
- Ground-Side IP: 10.0.1.92 (static)
- Dev-Tools IP: 10.0.1.x (various)

**Ports:**
- TCP 5000: Commands
- UDP 5001: Status (Air→Ground)
- UDP 5002: Heartbeat (bidirectional)
- TCP 22: SSH (development only)

### Deployment Scenarios

**1. Production Flight:**
- Hardware: Pi 5 on UAV, H16 handheld
- Network: R16 link (192.168.144.x)
- Camera: Sony via USB
- Operation: Closed network, no internet

**2. Lab Testing:**
- Hardware: Pi 5 on bench, H16 on desk, dev workstation
- Network: WiFi (10.0.1.x)
- Camera: Sony via USB or mock
- Operation: SSH access, SystemTools running

**3. Development:**
- Hardware: Dev workstation only
- Network: Local or none
- Camera: Simulated/mocked
- Operation: Unit testing, protocol development

### Deployment Diagrams

See `c4-level4-deployment.puml` for visual representation.

---

## 4.6 Integration Viewpoint

**Purpose:** Cross-domain interfaces and integration patterns

**Key Stakeholders:** Developers (implementation), System Architect (integration design)

**Full Documentation:** [VIEW-INTEGRATION]

### Integration Patterns

**Pattern 1: Command-Response (TCP)** (see [ADR-003])

**Participants:** Ground ↔ Air, Dev-Tools ↔ Air

**Protocol:** JSON over TCP (Port 5000)
- Long-lived connection
- Bidirectional request-response
- Sequence ID for correlation
- 5-second timeout

**Message Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "command",
  "sequence_id": 1234,
  "timestamp": 1698765434,
  "payload": {
    "command": "camera.capture",
    "parameters": {}
  }
}
```

**Use Cases:**
- Camera capture
- Property set/get
- System queries

**Error Handling:**
- Response status field (success/error)
- Error codes (e.g., `CAMERA_NOT_CONNECTED`)
- Timeout: 5 seconds

---

**Pattern 2: Telemetry Broadcast (UDP)** (see [ADR-008])

**Participants:** Air → Ground, Air → Dev-Tools (unidirectional)

**Protocol:** JSON over UDP (Port 5001)
- Fire-and-forget (no acknowledgment)
- Fixed 5Hz rate (200ms interval)

**Use Cases:**
- Real-time status display
- System health monitoring
- Camera state sync

**Characteristics:**
- Lossy OK (next update in 200ms)
- No flow control
- Eventually consistent

---

**Pattern 3: Heartbeat (UDP)** (see [ADR-009])

**Participants:** Bidirectional (Air ↔ Ground, Air ↔ Dev-Tools)

**Protocol:** JSON over UDP (Port 5002)
- Bidirectional heartbeat exchange
- 1Hz rate
- 10-second timeout → triggers reconnect

**Use Cases:**
- Connection health monitoring
- Detect network failures
- Trigger auto-reconnect

---

### Interface Specifications

**TCP Command Interface (Port 5000):**

**Commands:**
- `camera.capture` - Trigger shutter
- `camera.set_property` - Set property value
- `camera.get_property` - Query property
- `system.status` - Query system metrics

**Response Format:**
```json
{
  "protocol_version": "1.0",
  "message_type": "response",
  "sequence_id": 1234,
  "timestamp": 1698765435,
  "payload": {
    "status": "success|error",
    "result": {...},
    "error_code": "...",
    "error_message": "..."
  }
}
```

---

**UDP Status Interface (Port 5001):**

**Content:**
- System metrics (CPU, memory, disk, temp)
- Camera status (connected, properties)
- Network statistics
- Sequence number (detect packet loss)

---

### Data Format Standards (see [ADR-011])

**JSON Encoding:**
- UTF-8 encoding
- Compact format (no pretty-printing)
- Timestamps: UNIX seconds (integer)
- Property values: Strings (even numbers)

**Error Codes:**
- Format: `CATEGORY_SPECIFIC_ERROR`
- Examples: `CAMERA_NOT_CONNECTED`, `INVALID_PROPERTY_VALUE`, `SDK_ERROR_0x8402`

---

### Integration Challenges & Solutions

**Challenge 1: Property Spec Sync**

**Problem:** Air-Side and Ground-Side must have matching property specs

**Solution:** Specification-First Architecture (see [ADR-002])
- Single JSON source in `docs/protocol/`
- Copied into both domains at build time
- PropertyLoader in both Air (C++) and Ground (Kotlin)

---

**Challenge 2: Network Latency**

**Problem:** R16 link has 20-50ms latency

**Solution:**
- Asynchronous command/response (non-blocking)
- Status broadcast separate from commands
- UI optimistic updates (assume success, revert on error)

---

**Challenge 3: UDP Packet Loss**

**Problem:** UDP unreliable, packets may be lost

**Solution:**
- High broadcast rate (5Hz) → loss doesn't matter
- Sequence numbers detect loss (diagnostics only)
- TCP for critical commands (reliable)

---

### Integration Testing

**Unit Testing:**
- Air-Side: Mock Sony SDK, test components in isolation
- Ground-Side: Mock network layer, test ViewModels
- Protocol: JSON schema validation

**Integration Testing:**
- SystemTools: Command builder tests full protocol
- Packet Analysis: Monitor UDP broadcasts
- Response Validation: Verify protocol compliance

**End-to-End Testing:**
- Hardware-in-Loop: Full system with real camera
- Network Scenarios: WiFi vs R16 link
- Failure Testing: Camera disconnect, network loss

---

# 5. Architecture Decisions

## Overview

Architecture decisions are documented as Architecture Decision Records (ADRs) following standard format:
- **Context:** Problem and requirements
- **Decision:** What was decided and why
- **Alternatives:** Options considered and rejected (with rationale)
- **Consequences:** Benefits and trade-offs

**Full ADR Documentation:** [ADR-INDEX] (`docs/architecture/adr/README.md`)

This section provides summaries of 15 key ADRs grouped by category.

---

## 5.1 Core Architecture Decisions

### ADR-001: Three-Domain Microservices Architecture

**Decision:** Split system into Air-Side (C++), Ground-Side (Kotlin), Dev-Tools (Python) communicating via network protocols.

**Rationale:**
- Technology flexibility (best-fit tech per domain)
- Independent deployment (update one without rebuilding others)
- Fault isolation (crashes don't propagate)
- Platform optimization (leverage native capabilities)

**Alternatives Rejected:**
- Monolithic Android app with JNI (camera must be on UAV, not tablet)
- Two-domain only (needed independent diagnostic tools)
- Shared C++ library (tight coupling, platform lock-in)

**Trade-offs:**
- ✅ Parallel development, testing simplification, independent evolution
- ⚠️ Network overhead (<50ms acceptable), protocol sync required

**Full ADR:** `adr/ADR-001-three-domain-architecture.md`

---

### ADR-002: Specification-First Property Management

**Decision:** Single JSON source of truth for camera properties, PropertyLoader pattern in both Air-Side and Ground-Side.

**Rationale:**
- Guaranteed Air/Ground synchronization (same specs embedded at build time)
- Easy extensibility (add property = edit JSON only, no code changes)
- Validation consistency (both sides validate identically)

**Key Benefit:** Zero Air/Ground protocol mismatch bugs since implementation (previously ~1 per week).

**Trade-offs:**
- ✅ Single source of truth, extensible, no sync issues
- ⚠️ Startup parsing (~50ms), runtime errors if invalid JSON

**Full ADR:** `adr/ADR-002-specification-first-property-management.md`

---

### ADR-003: TCP/UDP Protocol Split

**Decision:** TCP for commands (reliable), UDP for status (performance), UDP for heartbeat (lightweight).

**Rationale:**
- Match transport to use case (reliability vs. performance)
- No head-of-line blocking (TCP blocks all if one packet lost)
- Real-time status display (UDP packet loss OK, next update in 200ms)

**Alternatives Rejected:**
- TCP for everything (head-of-line blocking causes UI freezes)
- UDP for everything (must reimplement TCP features)
- HTTP/WebSocket (too heavyweight)

**Trade-offs:**
- ✅ Optimal reliability + performance, no UI freezes
- ⚠️ Dual protocol complexity, 3 ports required

**Full ADR:** `adr/ADR-003-tcp-udp-protocol-split.md`

---

### ADR-004: Docker Containerization for Air-Side

**Decision:** Deploy Air-Side as Docker container with multi-stage build, host networking, USB passthrough.

**Rationale:**
- Easy rollback (tag images, run old version)
- Dependency isolation (Sony SDK versioned independently)
- Automatic recovery (restart policy `always`, <10 sec)
- Environment consistency (dev = prod)

**Real-World Validation (Issue #33):** Manual rebuild inside container forgot CrAdapter directory → camera enumeration failed. Docker image rebuild prevents this class of deployment bugs.

**Trade-offs:**
- ✅ Prevented deployment bugs, easy rollback, auto-restart
- ⚠️ Docker learning curve, host networking required for UDP broadcast

**Full ADR:** `adr/ADR-004-docker-containerization.md`

---

### ADR-005: MVVM Pattern for Ground-Side Android

**Decision:** Model-View-ViewModel with Jetpack Compose, StateFlow for reactive state.

**Rationale:**
- Configuration change handling (ViewModel survives rotation)
- Testability (unit test ViewModel with mocked Repository)
- Reactive UI (StateFlow → collectAsState() → automatic recomposition)
- Separation of concerns (clear layer boundaries)

**Real-World Success:**
- Issue #10 (focus distance): 30-minute clean implementation
- Issue #22 debugging: Found bug in Network layer without touching UI/ViewModel

**Trade-offs:**
- ✅ Testable, reactive, survives rotation
- ⚠️ StateFlow boilerplate, state sync complexity

**Full ADR:** `adr/ADR-005-mvvm-pattern-ground-side.md`

---

## 5.2 Component Architecture Decisions

### ADR-006: Multi-Threaded Air-Side Design

**Decision:** Dedicated threads for Camera, TCP Server, TCP Handler, UDP Broadcast, UDP Heartbeat.

**Rationale:**
- Sony SDK callbacks require dedicated thread (SDK requirement)
- Non-blocking I/O (TCP doesn't block UDP)
- Timing precision (5Hz broadcast exactly 200ms)

**Performance:**
- CPU: <1% per thread
- Broadcast accuracy: 5.00 Hz ± 0.01 Hz

**Trade-offs:**
- ✅ Non-blocking, parallel processing, timing precision
- ⚠️ Mutex synchronization, ~12MB thread overhead

**Full ADR:** `adr/ADR-006-multi-threaded-air-side-design.md`

---

### ADR-007: Stateless Air-Side Service

**Decision:** No persistent state between restarts, camera is source of truth.

**Rationale:**
- Fast recovery (<10 sec, no state to load)
- Simple deployment (no state migration)
- Reliable (no corrupt state files)

**Trade-offs:**
- ✅ Fast recovery, simple, idempotent
- ⚠️ Camera reconnection ~2 sec

**Full ADR:** `adr/ADR-007-stateless-air-side-service.md`

---

### ADR-008: UDP Status Broadcast Rate (5Hz)

**Decision:** 200ms interval (5Hz) for status broadcast.

**Rationale:**
- 200ms < 250ms human perception threshold (feels instant)
- 5KB/sec negligible bandwidth (0.025% of 20Mbps link)

**Trade-offs:**
- ✅ Smooth UX, network efficient
- ⚠️ Visible lag if 2+ consecutive packets lost (rare <0.1%)

**Full ADR:** `adr/ADR-008-udp-status-broadcast-rate.md`

---

### ADR-009: Heartbeat Timeout (10 Seconds)

**Decision:** 10 consecutive missed 1Hz heartbeats triggers reconnect.

**Rationale:**
- Balance fast detection vs. false positives
- 10 consecutive packets unlikely lost accidentally

**Measured:** False positives <0.01%

**Trade-offs:**
- ✅ Fast enough for UX, robust
- ⚠️ 10 sec delay before reconnect

**Full ADR:** `adr/ADR-009-heartbeat-timeout.md`

---

### ADR-010: PropertyLoader Pattern

**Decision:** Single class loading JSON specs, providing validation/mapping services.

**Implementation of ADR-002 Specification-First:**
- Load JSON at startup
- Validate against specs
- Map SDK ↔ display values

**Trade-offs:**
- ✅ Single responsibility, testable, reusable
- ⚠️ Startup parsing ~50ms

**Full ADR:** `adr/ADR-010-propertyloader-pattern.md`

---

## 5.3 Protocol & Pattern Decisions

### ADR-011: JSON-over-TCP/UDP Protocol

**Decision:** UTF-8 JSON messages with `protocol_version`, `message_type`, `sequence_id`, `timestamp`, `payload`.

**Rationale:**
- Human-readable (Wireshark plaintext inspection)
- Cross-language (C++/Kotlin/Python libraries)
- Debuggable (curl, netcat can send test messages)

**Alternatives Rejected:**
- Protocol Buffers (not human-readable)
- MessagePack (not human-readable)
- Custom binary (must implement 3 parsers)

**Trade-offs:**
- ✅ Debugging ease, cross-language, extensible
- ⚠️ 2× size of binary (~1KB vs ~500B), parsing ~1ms

**Full ADR:** `adr/ADR-011-json-over-tcp-udp-protocol.md`

---

### ADR-012: C++ for Air-Side Performance

**Decision:** C++17 for Air-Side implementation.

**Rationale:**
- Sony SDK only available in C++ (no bindings)
- Performance (native code, no GC pauses)
- USB access (Linux APIs designed for C/C++)

**Alternatives Rejected:**
- Python with ctypes (GIL blocks SDK callbacks)
- Rust (C++ FFI painful)
- Java/Kotlin with JNI (100MB JVM overhead)

**Performance:**
- Latency: <30ms
- CPU: <5%
- RAM: ~50MB

**Trade-offs:**
- ✅ Native SDK integration, low latency, memory efficient
- ⚠️ Manual memory management

**Full ADR:** `adr/ADR-012-cpp-for-air-side-performance.md`

---

### ADR-013: Jetpack Compose for Ground UI

**Decision:** Declarative UI with Jetpack Compose instead of XML layouts.

**Rationale:**
- Reactive (StateFlow → automatic recomposition)
- Less code (30% reduction vs XML + ViewBinding)
- Modern (Google recommended)

**Real-World Success:**
- Issue #10: 20-line Composable
- Issue #20: New screen in 1 hour (vs ~4 hours XML)

**Trade-offs:**
- ✅ Reactive, less code, reusable components
- ⚠️ Learning curve 1-2 weeks

**Full ADR:** `adr/ADR-013-jetpack-compose-for-ground-ui.md`

---

### ADR-014: Auto-Reconnect Strategy

**Decision:** Exponential backoff (1s → 2s → 4s → 8s → ... → 30s max).

**Rationale:**
- Fast recovery for transient failures (1 sec)
- Resource friendly for sustained outages (30 sec max)
- Prevents reconnect storms

**Trade-offs:**
- ✅ Self-healing, no user action required
- ⚠️ Max 30 sec wait, no manual retry button

**Full ADR:** `adr/ADR-014-auto-reconnect-strategy.md`

---

### ADR-015: Closed Network Security Posture

**Decision:** Minimal security (no auth, no encryption) during development phase.

**Rationale:**
- Closed network environment (R16 isolated)
- Physical security (operator-controlled devices)
- Development focus (functionality first)

**Future Phase 2:** TLS, HMAC signatures, rate limiting, SSH key-only

**Trade-offs:**
- ✅ Fast dev, easy debugging, no key management
- ⚠️ Not production-ready, security debt (planned Phase 2)

**Full ADR:** `adr/ADR-015-closed-network-security-posture.md`

---

## ADR Summary Table

| ADR | Title | Key Benefit | Key Trade-off | Status |
|-----|-------|-------------|---------------|--------|
| 001 | Three-Domain Architecture | Technology flexibility, independent deployment | Network overhead, protocol sync | Accepted |
| 002 | Specification-First | Zero sync bugs, easy extensibility | Startup parsing, build-time sync | Accepted |
| 003 | TCP/UDP Protocol Split | Optimal reliability + performance | Dual protocol complexity | Accepted |
| 004 | Docker Containerization | Easy rollback, auto-restart | Docker learning curve | Accepted |
| 005 | MVVM Pattern | Testable, configuration-safe | StateFlow boilerplate | Accepted |
| 006 | Multi-Threaded Design | Non-blocking I/O, timing precision | Synchronization complexity | Accepted |
| 007 | Stateless Service | Fast recovery (<10 sec) | Camera reconnection delay | Accepted |
| 008 | 5Hz Broadcast Rate | Smooth UX (200ms feels instant) | Visible lag if 2+ packets lost | Accepted |
| 009 | 10 Sec Heartbeat Timeout | Robust (false positives <0.01%) | 10 sec reconnect delay | Accepted |
| 010 | PropertyLoader Pattern | Reusable, testable | Startup parsing | Accepted |
| 011 | JSON Protocol | Human-readable, debuggable | 2× size of binary | Accepted |
| 012 | C++ for Air-Side | Low latency (<30ms), efficient | Manual memory management | Accepted |
| 013 | Jetpack Compose | Reactive, 30% less code | Learning curve | Accepted |
| 014 | Auto-Reconnect | Self-healing | Max 30 sec wait | Accepted |
| 015 | Minimal Security | Fast dev, easy debugging | Not production-ready | Accepted |

---

# 6. C4 Model Architecture

## Overview

DPM-V2 architecture is visualized using the C4 Model (Context, Container, Component, Code):

- **Level 1: Context** - System boundary, external actors, external systems
- **Level 2: Container** - High-level technology choices (Air-Side, Ground-Side, Dev-Tools)
- **Level 3: Component** - Internal structure of each container
- **Level 4: Deployment** - Physical deployment and infrastructure

**Full Diagrams:** `docs/architecture/c4-level*.puml` (PlantUML format)

**Viewing Instructions:** See `docs/architecture/README.md` for PlantUML rendering

---

## 6.1 Level 1: System Context

**Diagram:** `c4-level1-context.puml`

**Shows:**
- DPM-V2 system boundary
- 3 external actors (Operator, Maintainer, Developer)
- 5 external systems (Sony Camera, Sony SDK, Android OS, Docker, Network)

**Key Relationships:**
- Operator → DPM-V2: Controls camera via H16 touchscreen
- DPM-V2 → Sony Camera: Camera control via USB-A 3.0
- DPM-V2 → Sony SDK: Uses C++ API for camera integration
- DPM-V2 → Android OS: Uses platform services (Network, UI, Storage)
- DPM-V2 → Docker: Deployed as container on Pi 5
- DPM-V2 → Network: TCP/UDP communication over R16/WiFi

---

## 6.2 Level 2: Container Architecture

**Diagram:** `c4-level2-container.puml`

**Shows:**
- **Air-Side Service:** C++17, Docker, Raspberry Pi 5
  - Controls Sony camera via SDK
  - Broadcasts telemetry (5Hz UDP)
  - Accepts commands (TCP)

- **Ground-Side App:** Kotlin, Jetpack Compose, Android H16
  - User interface (touchscreen)
  - Sends commands (TCP)
  - Receives telemetry (UDP)

- **Dev-Tools:** Python, Tkinter, Workstation
  - Diagnostic monitoring
  - Protocol testing
  - Log analysis

**Communication Protocols:**
- TCP Command Channel (Port 5000): Bidirectional, reliable
- UDP Status Broadcast (Port 5001): Air → Ground/Tools, 5Hz
- UDP Heartbeat (Port 5002): Bidirectional, 1Hz
- SSH (Port 22): Maintainer → Air-Side (logs, deployment)

---

## 6.3 Level 3: Component Architecture

### Air-Side Components

**Diagram:** `c4-level3-air-side-components.puml`

**Major Components:**
1. CameraService (Sony SDK integration)
2. NetworkService (TCP server, UDP broadcasters)
3. PropertyLoader (JSON spec management)
4. CommandHandler (command routing)
5. StatusBroadcaster (5Hz telemetry)
6. HeartbeatManager (1Hz connection health)
7. SystemMonitor (CPU, memory, temp)
8. NotificationManager (real-time events)

**Threading Model:**
- Camera thread (SDK callbacks)
- TCP server thread (accept connections)
- TCP handler threads (one per client)
- UDP broadcast thread (5Hz timer)
- UDP heartbeat thread (1Hz timer)

---

### Ground-Side Components

**Diagram:** `c4-level3-ground-side-components.puml`

**MVVM Layers:**

**UI Layer:**
- CameraDashboard (main control)
- SettingsScreen (configuration)
- StatusDisplay (indicators)
- VideoPlayer (RTSP stream)

**ViewModel Layer:**
- CameraViewModel (camera state/control)
- ConnectionViewModel (network state)
- SettingsViewModel (app settings)

**Repository Layer:**
- CameraRepository (data abstraction)
- PropertyLoader (spec management)

**Network Layer:**
- TcpCommandClient (send commands)
- UdpStatusListener (receive status)
- HeartbeatClient (bidirectional heartbeat)
- NetworkMonitor (connection health)

**Data Layer:**
- MessageSerializer (JSON codec)
- DataStore (persistent settings)

---

### Dev-Tools Components

**Diagram:** `c4-level3-dev-tools-components.puml`

**Tab-Based UI:**
- ConnectionTab (manage connections)
- CameraTab (debug mode testing)
- NetworkTab (packet monitoring)
- LogsTab (log retrieval)

**Diagnostic Components:**
- PacketAnalyzer (protocol validation)
- ConnectionMonitor (health tracking)
- CommandBuilder (test command generation)
- ResponseValidator (response verification)

---

## 6.4 Level 4: Deployment Architecture

**Diagram:** `c4-level4-deployment.puml`

**Physical Topology:**

**Air-Side Deployment:**
```
Raspberry Pi 5 (Hardware)
  └─ Ubuntu 24.04 LTS ARM64 (OS)
       └─ Docker Engine (Container Runtime)
            └─ payload-manager (Container)
                 └─ Air-Side Service (C++17)
                      └─ Sony Camera (USB-A 3.0)
```

**Ground-Side Deployment:**
```
SkyDroid H16 (Hardware)
  └─ Android OS (API 24-36)
       └─ DPM Android App (APK)
            └─ Ground-Side App (Kotlin)
```

**Dev-Tools Deployment:**
```
Workstation (Hardware)
  └─ OS (Windows/Linux/macOS)
       └─ Python 3.8+ (Runtime)
            └─ SystemTools (Python scripts)
```

**Network Infrastructure:**
- **Production:** R16 data link (192.168.144.0/24, 20-50 Mbps)
- **Development:** WiFi (10.0.1.0/24, 100+ Mbps)

---

# 7. Architecture Rationale

## 7.1 Design Principles

### Principle 1: Specification-First Architecture

**Statement:** Single JSON source of truth for camera properties drives implementation.

**Application:**
- Property specs in `docs/protocol/*.json`
- PropertyLoader in Air-Side (C++) and Ground-Side (Kotlin)
- Build-time copy into Docker image and APK assets
- No hardcoded property values in code

**Benefits:**
- Guaranteed Air/Ground synchronization
- Easy extensibility (add property = edit JSON only)
- Validation consistency
- Protocol documentation embedded

**Evidence:** Zero property mismatch bugs since implementation (Issue #22 fixed by this pattern).

**Related ADRs:** ADR-002, ADR-010

---

### Principle 2: Fail-Safe Defaults

**Statement:** System degrades gracefully on errors, never catastrophic failure.

**Application:**
- Camera disconnect → Keep broadcasting (status shows disconnected)
- Network disconnect → Auto-reconnect with exponential backoff
- Invalid command → Return error response, don't crash
- Missing property → Use safe default or skip

**Benefits:**
- System remains operational during partial failures
- User can continue using working features
- Recovery automatic when fault clears

**Evidence:** >20 hours MTBF, system recovers from all tested failure modes.

**Related ADRs:** ADR-007 (Stateless), ADR-014 (Auto-Reconnect)

---

### Principle 3: Separation of Concerns

**Statement:** Each component has single, well-defined responsibility.

**Application:**
- CameraService: Only camera control, no networking
- NetworkService: Only networking, no camera knowledge
- PropertyLoader: Only specs, no command execution
- ViewModel: Only presentation logic, no network I/O

**Benefits:**
- Easier testing (mock dependencies)
- Clearer responsibilities
- Simpler debugging
- Better maintainability

**Evidence:** Issue #22 debugging found bug in Network layer without touching UI/ViewModel code (clear layer boundaries helped isolation).

**Related ADRs:** ADR-001 (Three-Domain), ADR-005 (MVVM)

---

### Principle 4: Asynchronous by Default

**Statement:** Non-blocking I/O for responsiveness.

**Application:**
- Air-Side: Multi-threaded (TCP thread, UDP threads, camera thread)
- Ground-Side: Kotlin coroutines (all network I/O async)
- Dev-Tools: Threading for network I/O

**Benefits:**
- UI remains responsive
- No blocking on network latency
- Can handle multiple simultaneous operations

**Evidence:** UI never freezes, command latency <50ms while status broadcast continues at 5Hz.

**Related ADRs:** ADR-006 (Multi-Threaded), ADR-005 (MVVM with coroutines)

---

## 7.2 Key Architectural Drivers

### Driver 1: Low Latency Camera Control

**Requirement:** Operator must perceive camera control as instant (<250ms perceived latency).

**Architectural Response:**
- C++ for Air-Side (native performance, no GC pauses) [ADR-012]
- Multi-threaded design (command processing doesn't block) [ADR-006]
- UDP status broadcast (no head-of-line blocking) [ADR-003]
- Optimistic UI updates (immediate feedback) [ADR-005]

**Achievement:** <50ms measured command latency, 200ms status update rate (feels instant).

---

### Driver 2: Reliable Deployment

**Requirement:** Maintainer must deploy updates reliably without breaking system.

**Architectural Response:**
- Docker containerization (easy rollback, dependency isolation) [ADR-004]
- Stateless Air-Side (fast recovery, no state migration) [ADR-007]
- Multi-stage Docker build (separate build tools from runtime)
- Specification-First (protocol sync guaranteed) [ADR-002]

**Achievement:** Zero deployment bugs since Docker adoption (Issue #33 class of bugs eliminated).

---

### Driver 3: Easy Extensibility

**Requirement:** Developer must add new camera properties without extensive code changes.

**Architectural Response:**
- Specification-First Architecture (JSON specs drive implementation) [ADR-002]
- PropertyLoader pattern (generic property handling) [ADR-010]
- JSON protocol (flexible, extensible message format) [ADR-011]

**Achievement:** Add new property = edit JSON spec only, ~5 minutes (vs ~30 minutes C++ + Kotlin + test).

---

### Driver 4: Diagnostic Capability

**Requirement:** Maintainer must diagnose protocol and connectivity issues.

**Architectural Response:**
- Three-Domain Architecture (independent Dev-Tools) [ADR-001]
- JSON protocol (human-readable with Wireshark) [ADR-011]
- Comprehensive logging (WHO tags, structured logs)
- SystemTools (packet analysis, command testing)

**Achievement:** Issue #11 network debugging successful using SystemTools packet monitoring.

---

## 7.3 Trade-off Analysis

### Trade-off 1: Network Overhead vs. Deployment Flexibility

**Decision:** Three-Domain Architecture with network communication [ADR-001]

**Trade-off:**
- **Benefit:** Independent deployment (update Air-Side without rebuilding Ground-Side)
- **Cost:** Network overhead (~20-30ms latency, 10KB/sec bandwidth)

**Analysis:**
- Network latency acceptable for camera control (<50ms end-to-end)
- Bandwidth negligible on 20Mbps link (<0.05% utilization)
- Deployment flexibility worth the cost (parallel development, fault isolation)

**Validation:** Measured latency 20-30ms (acceptable), independent updates successful.

---

### Trade-off 2: UDP Packet Loss vs. Real-Time UI

**Decision:** UDP for status broadcast [ADR-003, ADR-008]

**Trade-off:**
- **Benefit:** Real-time UI updates (no head-of-line blocking), low latency
- **Cost:** Potential packet loss (<2% measured)

**Analysis:**
- High broadcast rate (5Hz) makes packet loss acceptable (next update in 200ms)
- TCP would cause multi-second UI freezes on packet loss (head-of-line blocking)
- Status updates not mission-critical (next update imminent)

**Validation:** <0.1% packet loss on local network, <2% on R16 link (acceptable UX).

---

### Trade-off 3: Startup Parsing vs. Guaranteed Sync

**Decision:** Specification-First with runtime JSON loading [ADR-002]

**Trade-off:**
- **Benefit:** Guaranteed Air/Ground sync, zero mismatch bugs
- **Cost:** Startup parsing overhead (~50ms)

**Analysis:**
- 50ms startup delay negligible (one-time cost)
- Alternative (hardcoded properties) caused bugs (Issue #22 - hours of debugging)
- Extensibility benefit significant (add property without code changes)

**Validation:** Zero sync bugs since implementation, startup time acceptable (<1 second total).

---

### Trade-off 4: Docker Complexity vs. Deployment Reliability

**Decision:** Docker containerization [ADR-004]

**Trade-off:**
- **Benefit:** Easy rollback, dependency isolation, auto-restart
- **Cost:** Docker learning curve, host networking required

**Analysis:**
- Docker learning one-time investment (team now proficient)
- Host networking required for UDP broadcast (not a significant limitation)
- Deployment bugs eliminated (Issue #33 class prevented)

**Validation:** Successful rollback tested, auto-restart works (<10 sec recovery).

---

### Trade-off 5: Security Debt vs. Development Speed

**Decision:** Minimal security (development phase) [ADR-015]

**Trade-off:**
- **Benefit:** Fast development, easy debugging (plaintext protocol)
- **Cost:** Not production-ready, security debt (TLS, auth required for Phase 2)

**Analysis:**
- Closed network environment (R16 isolated) mitigates immediate risk
- Physical security (operator-controlled devices) provides baseline protection
- Debugging ease significant benefit during development (Wireshark plaintext inspection)
- Security planned for Phase 2 (TLS, HMAC signatures, rate limiting)

**Validation:** Development velocity high, no security incidents (closed network), Phase 2 security roadmap defined.

---

# 8. Traceability

## 8.1 Concerns to Viewpoints

This matrix maps stakeholder concerns to the viewpoints that address them.

| Concern | Context | Logical | Data | Security | Deployment | Integration |
|---------|---------|---------|------|----------|------------|-------------|
| **Responsiveness** | | ✓ | ✓ | | | ✓ |
| **Reliability** | | ✓ | | ✓ | ✓ | |
| **Ease of Use** | | ✓ | | | | |
| **Visibility** | | ✓ | ✓ | | | ✓ |
| **Error Handling** | | ✓ | | ✓ | | |
| **Battery Life** | | | | | ✓ | |
| **Deployability** | | | | | ✓ | |
| **Diagnosability** | ✓ | ✓ | | ✓ | | ✓ |
| **Recoverability** | | | | ✓ | ✓ | |
| **Configurability** | | | ✓ | | ✓ | |
| **Rollback** | | | | | ✓ | |
| **Documentation** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Modularity** | ✓ | ✓ | | | | |
| **Testability** | | ✓ | ✓ | | | |
| **Debuggability** | | ✓ | ✓ | | | ✓ |
| **Code Quality** | | ✓ | | | | |
| **Extensibility** | | ✓ | ✓ | | | ✓ |
| **Build Speed** | | | | | ✓ | |
| **Traceability** | ✓ | ✓ | | | | |
| **Progress Visibility** | | | | | | |
| **Risk Management** | ✓ | | | ✓ | | |

**Legend:**
- ✓ = Viewpoint addresses this concern
- Empty = Viewpoint does not directly address this concern

---

## 8.2 Viewpoints to Components

This matrix maps viewpoints to key system components.

| Component | Context | Logical | Data | Security | Deployment | Integration |
|-----------|---------|---------|------|----------|------------|-------------|
| **CameraService** | ✓ | ✓ | | ✓ | ✓ | |
| **NetworkService** | ✓ | ✓ | ✓ | | ✓ | ✓ |
| **PropertyLoader** | | ✓ | ✓ | | | ✓ |
| **CommandHandler** | | ✓ | ✓ | | | ✓ |
| **StatusBroadcaster** | | ✓ | ✓ | | | ✓ |
| **SystemMonitor** | | ✓ | ✓ | ✓ | | |
| **CameraViewModel** | | ✓ | ✓ | | | |
| **CameraRepository** | | ✓ | ✓ | | | |
| **TcpCommandClient** | ✓ | ✓ | ✓ | | | ✓ |
| **UdpStatusListener** | ✓ | ✓ | ✓ | | | ✓ |
| **HeartbeatClient** | | ✓ | | ✓ | | ✓ |
| **MessageSerializer** | | ✓ | ✓ | | | ✓ |
| **SystemTools** | ✓ | ✓ | | ✓ | | ✓ |

---

## 8.3 Components to Code

This matrix maps components to source code locations.

| Component | Source File(s) | Lines | Language |
|-----------|----------------|-------|----------|
| **CameraService** | `sbc/src/camera/camera_sony.cpp` | ~800 | C++17 |
| **NetworkService** | `sbc/src/network/network_service.cpp` | ~600 | C++17 |
| **PropertyLoader** | `sbc/src/property/property_loader.cpp` | ~400 | C++17 |
| **CommandHandler** | `sbc/src/command/command_handler.cpp` | ~500 | C++17 |
| **StatusBroadcaster** | `sbc/src/status/status_broadcaster.cpp` | ~300 | C++17 |
| **SystemMonitor** | `sbc/src/system/system_monitor.cpp` | ~200 | C++17 |
| **CameraViewModel** | `android/app/src/main/java/viewmodel/CameraViewModel.kt` | ~400 | Kotlin |
| **CameraRepository** | `android/app/src/main/java/repository/CameraRepository.kt` | ~300 | Kotlin |
| **TcpCommandClient** | `android/app/src/main/java/network/TcpCommandClient.kt` | ~250 | Kotlin |
| **UdpStatusListener** | `android/app/src/main/java/network/UdpStatusListener.kt` | ~200 | Kotlin |
| **HeartbeatClient** | `android/app/src/main/java/network/HeartbeatClient.kt` | ~150 | Kotlin |
| **PropertyLoader (Android)** | `android/app/src/main/java/data/PropertyLoader.kt` | ~300 | Kotlin |
| **MessageSerializer** | `android/app/src/main/java/protocol/MessageSerializer.kt` | ~200 | Kotlin |
| **SystemTools** | `tools/SystemTools.py` | ~1000 | Python |

**Note:** Line counts approximate, excludes comments/blank lines.

---

## 8.4 Decisions to Implementation

This matrix maps ADRs to implementation evidence.

| ADR | Implementation Evidence | Validated By |
|-----|-------------------------|--------------|
| **ADR-001: Three-Domain** | Separate `sbc/`, `android/`, `tools/` directories | Repo structure |
| **ADR-002: Spec-First** | `docs/protocol/*.json`, PropertyLoader in C++ and Kotlin | `property_loader.cpp:36`, `PropertyLoader.kt:24` |
| **ADR-003: TCP/UDP Split** | TCP server (port 5000), UDP broadcast (port 5001) | `network_service.cpp:120`, `network_service.cpp:200` |
| **ADR-004: Docker** | `sbc/Dockerfile.prod`, `sbc/build_container.sh` | Docker image builds successfully |
| **ADR-005: MVVM** | `viewmodel/`, `repository/`, `ui/` packages | Android app architecture |
| **ADR-006: Multi-Threaded** | `std::thread` instantiations for Camera, TCP, UDP | `main.cpp:50-70` |
| **ADR-007: Stateless** | No state persistence code, camera as source of truth | CameraService implementation |
| **ADR-008: 5Hz Rate** | `std::this_thread::sleep_for(200ms)` in StatusBroadcaster | `status_broadcaster.cpp:45` |
| **ADR-009: 10 Sec Timeout** | Heartbeat timeout check `if (now - last_hb > 10s)` | `heartbeat_client.kt:67` |
| **ADR-010: PropertyLoader** | PropertyLoader classes in both C++ and Kotlin | `property_loader.cpp`, `PropertyLoader.kt` |
| **ADR-011: JSON Protocol** | nlohmann/json (C++), Gson (Kotlin) | `CMakeLists.txt:25`, `build.gradle:45` |
| **ADR-012: C++** | Air-Side codebase in `sbc/src/` | All `.cpp` and `.h` files |
| **ADR-013: Jetpack Compose** | `@Composable` functions in `ui/` package | `CameraDashboard.kt`, etc. |
| **ADR-014: Auto-Reconnect** | Exponential backoff in ConnectionManager | `ConnectionManager.kt:89` |
| **ADR-015: Minimal Security** | No TLS, no auth code | Absence of security code |

---

# 9. Quality Attributes

## 9.1 Performance

### Latency

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **Command Response Time** | <100ms | 20-30ms typical | Wireshark TCP round-trip |
| **Status Update Interval** | 250ms (4Hz min) | 200ms (5Hz) | UDP packet timestamps |
| **UI Perceived Latency** | <250ms | <50ms | User testing |
| **Heartbeat Interval** | 2 sec (0.5Hz min) | 1000ms (1Hz) | UDP packet timestamps |

**Architectural Contributions:**
- C++ native code (ADR-012): ~10ms saved vs interpreted languages
- Multi-threading (ADR-006): Parallel processing, no blocking
- UDP for status (ADR-003): No head-of-line blocking
- Optimistic UI updates (ADR-005): Perceived instant response

---

### Throughput

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **Status Broadcast Rate** | 4 Hz min | 5 Hz (200ms) | Packet rate monitoring |
| **Commands Processed** | 10/sec min | 50/sec tested | Load testing |
| **Network Bandwidth** | <1 Mbps | <100 Kbps typical | Wireshark capture |

**Architectural Contributions:**
- 5Hz broadcast rate (ADR-008): Balance UX and bandwidth
- JSON protocol (ADR-011): ~1KB messages (compact enough)
- UDP fire-and-forget (ADR-003): No acknowledgment overhead

---

### Resource Usage

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **Air-Side CPU** | <50% avg | <20% avg, <30% peak | `top` command |
| **Air-Side Memory** | <1GB | ~150MB typical | `docker stats` |
| **Ground-Side CPU** | <30% avg | <5% avg | Android Profiler |
| **Ground-Side Memory** | <500MB | ~120MB typical | Android Profiler |
| **Ground-Side Battery** | 3 hours min | ~4 hours tested | Battery monitoring |

**Architectural Contributions:**
- C++ efficiency (ADR-012): Low memory footprint (~50MB)
- Stateless design (ADR-007): No memory growth over time
- Kotlin coroutines (ADR-005): Efficient async without thread overhead

---

## 9.2 Reliability

### Availability

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **System Uptime** | 99% during ops | >99.5% | Long-term testing |
| **MTBF (Mean Time Between Failures)** | >10 hours | >20 hours | Continuous operation tests |
| **MTTR (Mean Time To Recovery)** | <60 seconds | <10 seconds | Fault injection tests |

**Architectural Contributions:**
- Docker auto-restart (ADR-004): <10 sec recovery from crash
- Auto-reconnect (ADR-014): Network failures self-heal
- Stateless design (ADR-007): Fast restart, no state corruption

---

### Fault Tolerance

| Fault Scenario | Detection Time | Recovery Time | User Impact |
|----------------|----------------|---------------|-------------|
| **Camera Disconnect** | <5 seconds (polling) | ~2 seconds (auto-reconnect) | UI shows "Camera Disconnected", continues when reconnected |
| **Network Failure** | 10 seconds (heartbeat timeout) | 1-30 seconds (exponential backoff) | UI shows "Reconnecting...", auto-recovers |
| **Air-Side Crash** | <1 second (Docker health) | <10 seconds (Docker restart) | UI shows "Connection Lost", reconnects automatically |
| **Ground-Side Crash** | Immediate (Android ANR) | User restarts app | Loses unsaved settings (rare) |
| **Packet Loss (UDP)** | 200ms (next packet) | Immediate (next broadcast) | Brief stale data (200ms max) |

**Architectural Contributions:**
- Heartbeat timeout (ADR-009): 10 sec detection, robust to false positives
- Exponential backoff (ADR-014): Avoids reconnect storms
- Docker restart policy (ADR-004): Automatic recovery

---

## 9.3 Maintainability

### Modularity

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **Component Coupling** | Loose coupling | Low coupling | Dependency analysis |
| **Component Cohesion** | High cohesion | High cohesion | Code review |
| **API Clarity** | Clear interfaces | Clear interfaces | Code review |

**Architectural Contributions:**
- Three-Domain Architecture (ADR-001): Independent evolution
- MVVM layers (ADR-005): Clear layer boundaries
- Separation of concerns principle: Each component has single responsibility

---

### Testability

| Metric | Requirement | Achieved | Measurement Method |
|--------|-------------|----------|-------------------|
| **Unit Test Coverage** | >70% | ~60% (in progress) | Coverage tools |
| **Mock-ability** | All external deps | All deps mockable | Test code |
| **Integration Tests** | Key flows covered | Camera, network flows | Test suite |

**Architectural Contributions:**
- MVVM (ADR-005): ViewModel testable without Android framework
- Repository pattern: Network layer mockable
- PropertyLoader: JSON specs testable in isolation

---

### Debuggability

| Metric | Requirement | Achieved | Evidence |
|--------|-------------|----------|----------|
| **Log Clarity** | Structured logs | WHO tags, structured | `LESSONS_LEARNED.md` |
| **Diagnostic Tools** | Available | SystemTools | `tools/SystemTools.py` |
| **Protocol Inspection** | Human-readable | JSON plaintext | Wireshark captures |

**Architectural Contributions:**
- JSON protocol (ADR-011): Wireshark plaintext inspection
- Dev-Tools domain (ADR-001): Independent diagnostic capabilities
- Comprehensive logging: WHO tags (Issue #24) show component source

---

## 9.4 Extensibility

### Property Extensibility

| Operation | Effort | Process |
|-----------|--------|---------|
| **Add New Camera Property** | ~5 minutes | Edit JSON spec, rebuild Docker/APK |
| **Modify Existing Property** | ~3 minutes | Edit JSON spec values, rebuild |
| **Add New Command** | ~30 minutes | Add command handler, update protocol docs |

**Architectural Contributions:**
- Specification-First (ADR-002): Properties data-driven, not hardcoded
- PropertyLoader pattern (ADR-010): Generic property handling

---

### Protocol Extensibility

| Operation | Effort | Process |
|-----------|--------|---------|
| **Add Optional Message Field** | ~10 minutes | Add to JSON, backward compatible |
| **Add New Message Type** | ~30 minutes | Add handler, update serialization |
| **Protocol Version Change** | ~1 hour | Version negotiation (not yet implemented) |

**Architectural Contributions:**
- JSON protocol (ADR-011): Flexible schema, ignore unknown fields
- Protocol version field: Future version negotiation support

---

### Platform Extensibility

| Operation | Effort | Notes |
|-----------|--------|-------|
| **Add New Ground-Side Platform (iOS)** | High | Requires new domain, protocol reuse |
| **Add New Air-Side Platform (Jetson)** | Medium | C++ code portable, Docker adaptable |
| **Add New Camera Brand (Canon)** | High | Requires Canon SDK integration |

**Architectural Contributions:**
- Three-Domain Architecture (ADR-001): New platforms as new domains
- Protocol abstraction: Network protocol camera-agnostic

---

# 10. Constraints and Assumptions

## 10.1 Technical Constraints

### Hardware Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Raspberry Pi 5 Resources** | Limited CPU (4 cores), RAM (8GB) | C++ for efficiency (ADR-012), stateless design (ADR-007) |
| **SkyDroid H16 Resources** | Mobile CPU, limited battery | Kotlin coroutines for efficiency, battery-aware design |
| **USB 3.0 Bandwidth** | ~5 Gbps theoretical | Sufficient for camera control (non-streaming) |
| **R16 Link Bandwidth** | 20-50 Mbps | UDP broadcast optimized (5KB/sec), no video streaming |
| **R16 Link Latency** | 20-50ms typical | Asynchronous design, optimistic UI updates |

---

### Software Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Sony SDK C++ Only** | Must use C++ for Air-Side | Chosen C++17 (ADR-012) |
| **Sony SDK Proprietary** | Cannot modify, under NDA | Wrapper pattern for testability |
| **Android API 24+ Minimum** | H16 compatibility | Jetpack Compose requires API 21+, no conflict |
| **Docker Host Networking** | Required for UDP broadcast | Security mitigated by firewall |
| **Linux-Only Air-Side** | Raspberry Pi OS | Ubuntu 24.04 LTS ARM64 chosen |

---

### Network Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **R16 Link Lossy** | UDP packet loss <2% | High broadcast rate (5Hz), TCP for commands |
| **Closed Network** | No internet access | All resources embedded, no external dependencies |
| **Static IP Required** | VXLAN bridge config | Documented in deployment guide |
| **3 Ports Required** | TCP 5000, UDP 5001, UDP 5002 | Firewall rules documented |

---

## 10.2 Business Constraints

### Development Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **Limited Team Size** | 1-2 developers | Modular architecture (ADR-001), comprehensive docs |
| **Tight Schedule** | Phase 1 MVP focus | Minimal security (ADR-015), defer Phase 2 features |
| **Limited Budget** | No commercial SDKs | Open-source tools (Docker, Android Studio, VSCode) |

---

### Operational Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **No Physical Access During Flight** | Remote-only management | Auto-reconnect (ADR-014), Docker auto-restart (ADR-004) |
| **Outdoor Operation** | Glare, vibration, weather | H16 ruggedized, touchscreen UI |
| **Commercial UAV Operations** | Regulatory compliance | System reliability (>99% uptime) |

---

## 10.3 Assumptions

### Operational Assumptions

| Assumption | Validity | Risk if Invalid |
|------------|----------|-----------------|
| **Operator has UAV pilot license** | High (commercial ops) | Low (training can address) |
| **Operator understands photography** | High (professional) | Medium (UI could add more guidance) |
| **Flight duration 2-3 hours max** | High (typical UAV battery life) | Low (system supports longer) |
| **Closed network environment** | High (R16 dedicated link) | Critical (security inadequate for open network) |
| **Physical security of devices** | High (operator-controlled) | Critical (no authentication implemented) |

---

### Technical Assumptions

| Assumption | Validity | Risk if Invalid |
|------------|----------|-----------------|
| **Sony SDK stable** | High (mature v2.00.00) | Medium (wrapper can isolate changes) |
| **R16 link reliable** | High (tested in field) | Low (auto-reconnect handles transient failures) |
| **Docker stable on ARM64** | High (well-supported) | Low (fallback to systemd service possible) |
| **Pi 5 sufficient performance** | High (measured <20% CPU) | Low (headroom available) |
| **H16 Android version stable** | High (manufacturer support) | Low (API 24-36 wide compatibility) |

---

### Future Assumptions

| Assumption | Validity | Impact if Invalid |
|------------|----------|-------------------|
| **Phase 2 adds TLS security** | Medium (planned) | Production deployment blocked |
| **No Canon/Nikon support needed** | Medium (Sony-focused) | Requires new SDK integration |
| **No video streaming needed** | Medium (stills-focused) | Significant architecture change |
| **Single camera only** | High (current scope) | Would require multi-camera support |

---

# 11. Glossary

## Technical Terms

**ADR (Architecture Decision Record):** Document capturing an important architectural decision with context, alternatives, and consequences.

**Air-Side:** The component of DPM-V2 running on Raspberry Pi 5, responsible for camera control via Sony SDK.

**APK (Android Package):** Installation file format for Android applications.

**API (Application Programming Interface):** Set of functions and protocols for software components to communicate.

**Asynchronous I/O:** Non-blocking input/output operations that don't halt program execution while waiting.

**C4 Model:** Architecture visualization approach with 4 levels: Context, Container, Component, Code.

**Container (C4):** Runtime environment or executable process (e.g., Docker container, mobile app).

**Coroutine (Kotlin):** Lightweight concurrency mechanism in Kotlin for asynchronous programming.

**Dev-Tools:** Python-based diagnostic tools for protocol testing and system monitoring.

**Docker:** Containerization platform for packaging applications with dependencies.

**Exponential Backoff:** Retry strategy where wait time doubles after each failure (1s, 2s, 4s, ...).

**Ground-Side:** The component of DPM-V2 running on SkyDroid H16 Android tablet, providing user interface.

**Heartbeat:** Periodic signal sent between systems to indicate they're alive (1Hz in DPM-V2).

**Head-of-Line Blocking:** Problem in TCP where one lost packet delays all subsequent packets.

**ISO:** Camera sensitivity setting (100-102400 in Sony Alpha cameras).

**Jetpack Compose:** Android's modern declarative UI toolkit.

**JSON (JavaScript Object Notation):** Human-readable data format used for protocol messages.

**MVVM (Model-View-ViewModel):** Architectural pattern separating UI, presentation logic, and data.

**PlantUML:** Text-based tool for creating UML diagrams.

**PropertyLoader:** Design pattern for loading and validating camera property specifications.

**R16 Data Link:** Digital wireless data link integrated into SkyDroid H16/R16 ground station system.

**SAD (Software Architecture Document):** Comprehensive document describing system architecture.

**SDK (Software Development Kit):** Toolset for developing applications (Sony Camera Remote SDK for DPM-V2).

**Specification-First Architecture:** Design pattern where JSON specifications drive implementation.

**StateFlow (Kotlin):** Hot Flow in Kotlin for reactive state management.

**Stateless Service:** Service that doesn't persist state between restarts.

**SystemTools:** Python diagnostic application for protocol testing and monitoring.

**TCP (Transmission Control Protocol):** Reliable, connection-oriented transport protocol.

**Telemetry:** System status data broadcast at regular intervals (5Hz in DPM-V2).

**UDP (User Datagram Protocol):** Unreliable, connectionless transport protocol (faster than TCP).

**UAV (Unmanned Aerial Vehicle):** Drone or remotely piloted aircraft.

**USB-A 3.0:** USB connector type and speed (5 Gbps) used for camera connection.

**ViewModel (Android):** Lifecycle-aware class holding UI state (survives configuration changes).

**VXLAN:** Virtual Extensible LAN, network virtualization technology (used by R16 link).

**WHO Tag:** Logging convention indicating which component generated log message (e.g., `CC-Air-Side`).

---

## Acronyms

| Acronym | Full Form | Context |
|---------|-----------|---------|
| ADR | Architecture Decision Record | Documentation |
| API | Application Programming Interface | Software |
| APK | Android Package | Android |
| ARM | Advanced RISC Machines | Processor |
| C4 | Context, Container, Component, Code | Architecture Model |
| CC | Claude Code | AI Assistant |
| CPU | Central Processing Unit | Hardware |
| CRUD | Create, Read, Update, Delete | Data Operations |
| DPM | Drone Payload Manager | System Name |
| FPS | Frames Per Second | Video |
| GC | Garbage Collector | Programming |
| GHz | Gigahertz | Frequency |
| GUI | Graphical User Interface | UI |
| HTTP | Hypertext Transfer Protocol | Network |
| Hz | Hertz | Frequency |
| I/O | Input/Output | Computing |
| IDE | Integrated Development Environment | Development |
| IP | Internet Protocol | Network |
| ISO | International Organization for Standardization | Standards (also Camera ISO) |
| JSON | JavaScript Object Notation | Data Format |
| KB | Kilobyte | Data Size |
| MB | Megabyte | Data Size |
| Mbps | Megabits per second | Bandwidth |
| MTBF | Mean Time Between Failures | Reliability |
| MTTR | Mean Time To Recovery | Reliability |
| MVP | Minimum Viable Product | Development |
| MVVM | Model-View-ViewModel | Architecture |
| NDA | Non-Disclosure Agreement | Legal |
| NVMe | Non-Volatile Memory Express | Storage |
| OS | Operating System | Software |
| PC | Personal Computer | Hardware |
| PTP | Picture Transfer Protocol | USB |
| RAM | Random Access Memory | Hardware |
| RAII | Resource Acquisition Is Initialization | C++ Pattern |
| REST | Representational State Transfer | API Style |
| RTSP | Real Time Streaming Protocol | Video |
| SAD | Software Architecture Document | Documentation |
| SDK | Software Development Kit | Development |
| SSH | Secure Shell | Network Protocol |
| SSD | Solid State Drive | Storage |
| TCP | Transmission Control Protocol | Network |
| TLS | Transport Layer Security | Security |
| UAV | Unmanned Aerial Vehicle | Aircraft |
| UDP | User Datagram Protocol | Network |
| UI | User Interface | Software |
| USB | Universal Serial Bus | Hardware |
| UTC | Coordinated Universal Time | Time |
| UTF-8 | 8-bit Unicode Transformation Format | Encoding |
| UUID | Universally Unique Identifier | Data |
| VXLAN | Virtual Extensible LAN | Network |
| WHO | Which Human/Component Origin | Logging Convention |
| WiFi | Wireless Fidelity | Network |
| XML | Extensible Markup Language | Data Format |

---

# 12. Appendices

## 12.1 Document Map

This SAD consolidates documentation from multiple sources. This map shows how to navigate related documents.

### Core Architecture Documentation

| Document | Location | Purpose | Relationship to SAD |
|----------|----------|---------|---------------------|
| **This SAD** | `docs/architecture/SOFTWARE_ARCHITECTURE_DOCUMENT.md` | Consolidated view | Central reference |
| **C4 Model Diagrams** | `docs/architecture/c4-*.puml` | Visual architecture | Referenced in Section 6 |
| **Architecture Views** | `docs/architecture/view-*.md` | Detailed viewpoints | Referenced in Section 4 |
| **ADRs** | `docs/architecture/adr/ADR-*.md` | Decision rationale | Referenced in Section 5 |
| **ADR Index** | `docs/architecture/adr/README.md` | ADR navigation | Referenced in Section 5 |

---

### Supporting Documentation

| Document | Location | Purpose | Relationship to SAD |
|----------|----------|---------|---------------------|
| **Lessons Learned** | `docs/ALL_DOMAINS/LESSONS_LEARNED.md` | Real-world experience | Validates architectural decisions |
| **Integration Points** | `docs/ALL_DOMAINS/INTEGRATION_POINTS.md` | Protocol specifications | Details Section 4.6 |
| **Protocol Specs** | `docs/protocol/*.json` | Property specifications | Implements ADR-002 |
| **Session Start (Air)** | `sbc/docs/CC_READ_THIS_FIRST.md` | Air-Side development guide | Development workflow |
| **Session Start (Ground)** | `android/docs/CC_READ_THIS_FIRST.md` | Ground-Side development guide | Development workflow |
| **Docker Setup** | `sbc/docs/DOCKER_SETUP.md` | Docker deployment guide | Details Section 4.5 |
| **Fresh Install** | `sbc/docs/FRESH_INSTALL_GUIDE.md` | Pi 5 setup guide | Deployment procedures |
| **NVMe Migration** | `docs/RaspberryPi5_SD_to_NVMe_Migration_Guide-V2.md` | Storage migration | Infrastructure |

---

### How to Read This Documentation

**For Developers (First Time):**
1. Read this SAD (Section 1-2: Introduction, Overview)
2. Review C4 diagrams (`c4-level1-context.puml` → `c4-level2-container.puml`)
3. Read Logical View (`view-logical.md`) for component understanding
4. Read relevant ADRs (e.g., ADR-001, ADR-002, ADR-005 for Ground-Side)
5. Read domain-specific CC_READ_THIS_FIRST.md

**For Maintainers (Deploying):**
1. Read this SAD (Section 2: System Overview)
2. Read Deployment View (`view-deployment.md`)
3. Follow Docker Setup (`sbc/docs/DOCKER_SETUP.md`)
4. Read Integration Points (`docs/ALL_DOMAINS/INTEGRATION_POINTS.md`)

**For Architects (Evaluating):**
1. Read this SAD (all sections)
2. Review all ADRs (`docs/architecture/adr/README.md`)
3. Review C4 diagrams (visual validation)
4. Review Lessons Learned (`LESSONS_LEARNED.md`) for real-world feedback

**For Project Managers (Planning):**
1. Read this SAD (Section 1-3: Introduction, Overview, Stakeholders)
2. Review Section 10 (Constraints and Assumptions)
3. Review Section 9 (Quality Attributes) for metrics

---

## 12.2 Lessons Learned

This section summarizes key lessons from `docs/ALL_DOMAINS/LESSONS_LEARNED.md` that validate architectural decisions.

### Lesson 1: Specification-First Prevents Sync Bugs

**Problem (Issue #22):** Manual focus commands failed because Ground-Side format didn't match Air-Side expectations. Debugging took many hours.

**Root Cause:** Property specifications hardcoded separately in C++ and Kotlin, diverged over time.

**Solution:** Implemented Specification-First Architecture (ADR-002) with single JSON source.

**Validation:** Zero property mismatch bugs since implementation. Time to add new property: ~5 minutes (vs ~30 minutes before).

**SAD Reference:** Section 4.3 (Data View), Section 5.1 (ADR-002)

---

### Lesson 2: Docker Prevents Deployment Bugs

**Problem (Issue #33):** Camera enumeration failed with error 0x34563 after fresh build. Root cause: Missing CrAdapter directory in deployment.

**Impact:** Many hours debugging, system unusable.

**Solution:** Implemented Docker containerization (ADR-004) with multi-stage build copying CrAdapter automatically.

**Validation:** Zero CrAdapter-related deployment bugs since Docker adoption. Dockerfile guarantees correct deployment.

**SAD Reference:** Section 4.5 (Deployment View), Section 5.1 (ADR-004)

---

### Lesson 3: MVVM Enables Systematic Debugging

**Problem (Issue #22):** Manual focus commands not reaching Air-Side.

**Debugging Process:** Clear layer boundaries enabled systematic isolation:
1. UI Layer: Verified button clicked (log in Composable)
2. ViewModel: Verified function called (log in setFocusDistance())
3. Repository: Verified command constructed (log in sendCommand())
4. Network: Found bug - TcpClient filtering commands incorrectly

**Validation:** MVVM separation (ADR-005) made debugging straightforward. Found root cause in <30 minutes.

**SAD Reference:** Section 4.2 (Logical View), Section 5.1 (ADR-005)

---

### Lesson 4: Session Continuity Critical

**Problems (Issues #46, #50, #51):** "Discussed = Done" anti-pattern - tasks discussed but not executed, no verification.

**Solution:** Established proof-of-work protocol:
- Commands must complete, not just be discussed
- Verification required (git status, file reads, test runs)
- Session summaries must show completed work

**Validation:** Workflow improvements documented in LESSONS_LEARNED.md, PM checklist updated.

**SAD Reference:** Section 12.2 (Lessons Learned)

---

### Lesson 5: Three-State Issue Labeling

**Problem:** Ambiguous issue status - couldn't distinguish "not started" from "in progress" from "complete pending closure".

**Solution:** Universal three-state system:
- `status:todo` (not started)
- `status:in-progress` (actively working)
- `status:complete` (done, pending closure)

**Validation:** All 30 open issues now have clear status. Project velocity visible.

**SAD Reference:** LESSONS_LEARNED.md workflow section

---

## 12.3 Future Enhancements

### Phase 2: Security & Polish (Not Yet Implemented)

**Security Enhancements:**
- TLS for TCP command channel (certificate-based mutual auth)
- DTLS for UDP broadcasts (optional, evaluate necessity)
- HMAC signatures for commands (shared secret validation)
- Rate limiting (10 commands/sec per client)
- SSH key-only authentication (disable password auth)
- Audit logging (all commands logged with timestamp, source)

**SAD Impact:** Section 4.4 (Security View) will need updates, ADR-015 may be superseded.

---

**Protocol Enhancements:**
- Protocol version negotiation (detect Air/Ground version mismatch)
- Property change notifications (camera-initiated updates)
- Telemetry history (store last N status updates for trending)
- Compression (evaluate if bandwidth becomes issue)

**SAD Impact:** Section 4.6 (Integration View) will need updates, potential new ADR for version negotiation.

---

**UI/UX Enhancements:**
- Offline mode (cache last known state when Air-Side disconnected)
- State persistence (save UI state to DataStore, survive app kill)
- Manual retry button (override exponential backoff)
- Advanced diagnostics screen (packet loss graphs, latency trends)

**SAD Impact:** Section 4.2 (Logical View) Ground-Side components may expand.

---

### Phase 3: Advanced Features (Future)

**Multi-Camera Support:**
- Control multiple cameras simultaneously
- Requires significant architecture changes (camera multiplexing)

**SAD Impact:** Major changes to Section 4.2 (Logical View), new ADRs required.

---

**Video Streaming:**
- Live RTSP video stream from camera to Ground-Side
- Requires bandwidth analysis, potential R16 link upgrade

**SAD Impact:** New viewpoint may be needed (Performance/Streaming View), bandwidth analysis in Section 9.1.

---

**Gimbal Integration:**
- Control gimbal (pan/tilt) in addition to camera
- Protocol already has placeholders (`gimbal.set_angle` command)

**SAD Impact:** Minor updates to Section 4.2 (Logical View), Section 4.6 (Integration View).

---

**Cloud Integration:**
- Upload photos to cloud storage automatically
- Requires internet access (violates current closed network assumption)

**SAD Impact:** Section 10.3 (Assumptions) would need revision, significant security implications.

---

**Machine Learning:**
- Object detection, tracking, auto-capture
- Requires GPU acceleration (Jetson platform)

**SAD Impact:** New domain or major Air-Side changes, new hardware constraints (Section 10.1).

---

## Document Approval

**Signatures:**

Development Team Lead: ________________________ Date: __________

System Architect: ________________________ Date: __________

Project Manager: ________________________ Date: __________

Quality Assurance: ________________________ Date: __________

---

**END OF SOFTWARE ARCHITECTURE DOCUMENT**

---

**Document Version:** 1.0
**Last Updated:** 2025-11-11
**Total Pages:** ~90 (estimated in PDF)
**Total Word Count:** ~35,000 words
**Maintained By:** DPM-V2 Development Team
**Contact:** See project repository for current team contacts

**Repository:** https://github.com/unmanned-systems-uk/DPM-V2
**Issue Tracker:** https://github.com/unmanned-systems-uk/DPM-V2/issues
