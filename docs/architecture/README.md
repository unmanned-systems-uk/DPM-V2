# DPM-V2 C4 Architecture Diagrams

**Date:** 2025-11-11
**Version:** 1.0
**Standard:** C4 Model (Context → Container → Component → Deployment)
**Format:** PlantUML

---

## Overview

This directory contains the complete C4 Model architecture diagrams for DPM-V2, created as part of the ISO/IEC/IEEE 42010 Software Architecture Document development (Issue #65).

The C4 Model provides a hierarchical set of diagrams that describe the system at different levels of abstraction, making it easy for different audiences (operators, developers, architects) to understand the system structure.

---

## Diagram Files

### Level 1: System Context Diagram
**File:** `c4-level1-context.puml`

**Purpose:** Shows DPM-V2 in its environment with external actors and systems

**Audience:** All stakeholders (operators, managers, developers)

**Shows:**
- System boundary (what's inside/outside DPM-V2)
- External actors (Drone Operator, Maintainer, Developer)
- External systems (Sony Camera, Sony SDK, Android OS, Docker, Network)
- High-level interactions

**Use when:** Explaining what the system does and how it fits in the operational environment

---

### Level 2: Container Diagram
**File:** `c4-level2-container.puml`

**Purpose:** Shows the high-level technology choices and how containers communicate

**Audience:** Technical stakeholders, architects, senior developers

**Shows:**
- Air-Side Service (C++17, Docker)
- Ground-Side App (Kotlin, Jetpack Compose)
- Dev-Tools (Python, Tkinter)
- Communication protocols (TCP, UDP channels)
- Technology stack per container

**Use when:** Explaining the high-level architecture and technology decisions

---

### Level 3: Component Diagrams
**Files:**
- `c4-level3-air-side-components.puml`
- `c4-level3-ground-side-components.puml`
- `c4-level3-dev-tools-components.puml`

**Purpose:** Shows the internal component structure of each container

**Audience:** Developers working on specific domains

#### Air-Side Components
**Shows:**
- CameraService, NetworkService, PropertyLoader
- CommandHandler, StatusBroadcaster, HeartbeatManager
- SystemMonitor, NotificationManager
- Component interactions and data flow

**Use when:** Understanding Air-Side internal architecture or implementing new features

#### Ground-Side Components
**Shows:**
- MVVM architecture (ViewModel, Repository layers)
- UI components (CameraDashboard, SettingsScreen, VideoPlayer)
- Network layer (TcpClient, UdpListener, HeartbeatClient)
- PropertyLoader, MessageSerializer
- Android-specific patterns

**Use when:** Understanding Ground-Side architecture or developing Android UI

#### Dev-Tools Components
**Shows:**
- Tab-based UI structure (Connection, Camera, Network, Logs)
- Diagnostic components (PacketAnalyzer, ConnectionMonitor, CommandBuilder)
- Network layer (TcpClient, UdpListener, ProtocolHandler)
- Log analysis and debugging tools

**Use when:** Understanding diagnostic tools or adding new debugging features

---

### Level 4: Deployment Diagram
**File:** `c4-level4-deployment.puml`

**Purpose:** Shows physical deployment architecture and infrastructure

**Audience:** DevOps, deployment engineers, system administrators

**Shows:**
- Hardware platforms (Raspberry Pi 5, SkyDroid H16, Dev Workstation)
- Operating systems (Ubuntu 24.04 ARM64, Android)
- Network topology (Ethernet R16 link, WiFi development network)
- Docker containers, runtime environments
- IP addressing (192.168.144.x production, 10.0.1.x development)
- Physical connections (USB camera, network links)

**Use when:** Deploying the system, troubleshooting network issues, planning infrastructure

---

## Viewing the Diagrams

### Option 1: PlantUML Online (Quickest)

1. Go to https://www.plantuml.com/plantuml/uml/
2. Copy the contents of any `.puml` file
3. Paste into the text editor
4. View rendered diagram

### Option 2: VS Code with PlantUML Extension

1. Install "PlantUML" extension in VS Code
2. Open any `.puml` file
3. Press `Alt+D` to preview
4. Export as PNG/SVG if needed

### Option 3: Command Line (requires PlantUML installed)

```bash
# Install PlantUML (requires Java)
# On Ubuntu: sudo apt install plantuml

# Generate PNG
plantuml c4-level1-context.puml

# Generate SVG (vector, scalable)
plantuml -tsvg c4-level1-context.puml

# Generate all diagrams
plantuml *.puml
```

### Option 4: Docker (no local installation needed)

```bash
docker run -v $(pwd):/data plantuml/plantuml:latest -tsvg /data/*.puml
```

---

## Editing the Diagrams

### Prerequisites

- Basic understanding of PlantUML syntax
- C4-PlantUML library (included via URL in files)
- Text editor (VS Code recommended)

### C4-PlantUML Syntax Reference

**Elements:**
- `Person(id, "Name", "Description")` - External actor
- `System(id, "Name", "Description")` - System or container
- `System_Ext(id, "Name", "Description")` - External system
- `Container(id, "Name", "Technology", "Description")` - Container
- `Component(id, "Name", "Technology", "Description")` - Component
- `ComponentDb(id, "Name", "Technology", "Description")` - Data store

**Relationships:**
- `Rel(from, to, "Label", "Technology")` - Relationship
- `Rel_Back(from, to, "Label")` - Reverse relationship

**Grouping:**
- `System_Boundary(id, "Name")` - Group systems
- `Container_Boundary(id, "Name")` - Group containers
- `Deployment_Node(id, "Name", "Type")` - Physical node

### Making Changes

1. Edit the `.puml` file in text editor
2. Preview changes (VS Code with PlantUML extension)
3. Verify syntax and rendering
4. Commit changes to git
5. Update this README if adding new diagrams

---

## Diagram Conventions

### Naming
- **IDs:** snake_case (e.g., `camera_service`)
- **Names:** Title Case (e.g., "Camera Service")
- **Files:** `c4-level{N}-{name}.puml`

### Colors
- C4-PlantUML uses standard colors by default
- System boundary: Light gray
- External systems: Gray
- Containers/Components: Blue tones
- Databases/Storage: Green tones

### Notes
- Important architectural details in note boxes
- Technology choices, rationale, specifications
- Deployment details, network configuration

---

## Integration with SAD

These diagrams are part of the complete Software Architecture Document (SAD) being developed in Issue #65.

**SAD Structure:**
1. Introduction (stakeholders, concerns)
2. **Architecture Views** ← These diagrams fit here
   - Context View (uses Level 1)
   - Container View (uses Level 2)
   - Component View (uses Level 3)
   - Deployment View (uses Level 4)
3. Architecture Decisions (ADRs)
4. Glossary

**Usage in SAD:**
- Level 1: System context section
- Level 2: Container architecture section
- Level 3: Component architecture sections (per domain)
- Level 4: Deployment architecture section

---

## Maintenance

### When to Update

**Update diagrams when:**
- Adding new containers (services, applications)
- Adding new components (classes, modules)
- Changing communication protocols
- Modifying deployment architecture
- Changing technology stack

**Don't update for:**
- Minor code refactoring
- Internal implementation details
- Temporary debugging code
- Small bug fixes

### Version Control

- All `.puml` files are in git
- Commit changes with clear messages
- Reference issue numbers in commits
- Generate PNG/SVG for releases if needed

---

## C4 Model Resources

**Official C4 Model:**
- Website: https://c4model.com/
- Abstractions: Context → Container → Component → Code

**PlantUML C4:**
- GitHub: https://github.com/plantuml-stdlib/C4-PlantUML
- Examples: https://github.com/plantuml-stdlib/C4-PlantUML/tree/master/samples

**PlantUML:**
- Website: https://plantuml.com/
- Language Reference: https://plantuml.com/guide

---

## Credits

**Created:** 2025-11-11
**Author:** CC-Project-Manager
**Issue:** #65 - Software Architecture Documentation Development
**Standard:** ISO/IEC/IEEE 42010 with C4 Model
**Tool:** PlantUML with C4-PlantUML library

---

## Questions or Issues

- For diagram corrections: Update `.puml` file and commit
- For SAD-related questions: See Issue #65
- For C4 Model questions: See https://c4model.com/
- For PlantUML syntax: See https://plantuml.com/guide

