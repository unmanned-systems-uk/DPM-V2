# DPM-V2 (Drone Payload Manager) Project Overview
*Executive briefing for Claude Desktop - Project Management*

## 🎯 Project Mission

**Build a professional drone camera payload management system** that enables remote camera control, live monitoring, and intelligent edge processing for commercial drone operations.

## 🏗️ System Architecture

### Three-Domain Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DPM-V2 SYSTEM                           │
├─────────────────────┬──────────────────┬──────────────────┤
│     AIR-SIDE        │   GROUND-SIDE    │ DEVELOPMENT-SIDE │
│   (Edge Device)     │  (Control Station)│  (Dev Tools)    │
├─────────────────────┼──────────────────┼──────────────────┤
│ Raspberry Pi 5 SBC  │  H16 Android Tab  │ Cross-Platform  │
│ C++ / Sony SDK      │  Java/Kotlin      │ Python Tools    │
│ Camera Control      │  User Interface   │ Diagnostics     │
│ Edge Processing     │  Mission Control  │ Testing/Debug   │
└─────────────────────┴──────────────────┴──────────────────┘
```

### Key Components

| Component | Platform | Purpose | Status |
|-----------|----------|---------|--------|
| **Air-Side Controller** | Pi 5 SBC | Direct camera control via Sony SDK | 70% Complete |
| **Ground-Side App** | H16 Android | Touch UI for operators | 65% Complete |
| **DevTools Suite** | Windows/Linux | Diagnostic & testing tools | 85% Complete |
| **Protocol Layer** | JSON specs | Standardized communication | 90% Complete |

## 📊 Project Status Summary

### Overall Progress: **73% Complete**

#### By Domain:
- 🔹 **Air-Side**: 70% - Core camera control working, advanced features in progress
- 🔹 **Ground-Side**: 65% - Basic UI complete, advanced controls being added
- 🔹 **Dev-Side**: 85% - Diagnostic tools operational, modes implemented

### Current Phase: **Phase 2 - Feature Implementation**
- ✅ Phase 1: Core Infrastructure (Complete)
- 🔄 Phase 2: Feature Implementation (Current)
- ⏳ Phase 3: Advanced Features (Upcoming)
- ⏳ Phase 4: Production Ready (Q1 2025)

## 💼 Business Context

### Target Market
- **Primary**: Commercial drone operators
- **Secondary**: Industrial inspection services
- **Tertiary**: Search and rescue operations

### Key Differentiators
1. **Professional Sony camera integration** (not typical drone cameras)
2. **Edge AI processing** on Pi 5 (reduce bandwidth needs)
3. **Rugged Android control** via H16 military-spec tablet
4. **Real-time telemetry** with <100ms latency

### Deployment Scenarios
- 🏗️ Construction site monitoring
- 🌉 Infrastructure inspection
- 🚨 Emergency response
- 🎬 Professional cinematography
- 🔍 Industrial surveys

## 🛠️ Technical Stack

### Air-Side (Drone Payload)
```
Hardware: Raspberry Pi 5 (8GB)
OS: Raspberry Pi OS (64-bit)
Language: C++17
SDK: Sony Camera Remote SDK
Build: CMake
Container: Docker
Network: TCP commands, UDP telemetry
```

### Ground-Side (Control Station)
```
Hardware: H16 Rugged Android Tablet
OS: Android 11+
Language: Kotlin/Java
Framework: Android Native
Network: WiFi/4G dual mode
UI: Material Design 3
```

### Development Tools
```
Platform: Cross-platform (Windows/Linux/Mac)
Language: Python 3.9+
UI: Tkinter (GUI) / CLI
Modes: Development/Deployment
Testing: Automated test suites
```

## 🔄 Current Sprint Focus

### Week of Nov 4-10, 2025

#### High Priority Tasks
1. **Complete focus control implementation** (Air-Side)
2. **Implement gimbal control UI** (Ground-Side)
3. **Add recording controls** (Both sides)
4. **Stabilize network reconnection** (Protocol)

#### Technical Debt
- Refactor callback patterns in DevTools
- Optimize Docker container size
- Improve error handling in network layer
- Add comprehensive logging

## 📁 Project Structure

```
D:\DPM\DPM-V2\
├── sbc\                 # Air-Side: C++ drone payload code
│   ├── src\            # Source files
│   ├── include\        # Headers
│   └── build\          # CMake output
│
├── android\            # Ground-Side: Android app
│   ├── app\           # Application module
│   └── gradle\        # Build config
│
├── SystemTools\       # Dev-Side: Diagnostic tools
│   ├── gui\          # GUI components
│   ├── network\      # Network modules
│   └── utils\        # Utilities
│
├── protocol\         # Single source of truth
│   ├── commands.json      # Command definitions
│   └── camera_properties.json  # Property specs
│
└── docs\            # Documentation
    ├── ALL_DOMAINS\     # Cross-domain docs
    ├── AIR_SIDE\        # Pi 5 specific
    ├── GROUND_SIDE\     # Android specific
    └── DEVELOPMENT_SIDE\ # Tools docs
```

## 🚦 Key Metrics & KPIs

### Performance Targets
- **Latency**: <100ms command response
- **Video**: 1080p @ 30fps minimum
- **Telemetry**: 10Hz status updates
- **Reliability**: 99.9% uptime
- **Range**: 2km line of sight

### Development Metrics
- **Code Coverage**: Target 80%
- **Build Time**: <5 minutes
- **Deploy Time**: <10 minutes
- **Bug Resolution**: <48 hours critical

## 🔗 Integration Points

### External Systems
1. **Sony Camera API** - Direct camera control
2. **Android ADB** - Development/debugging
3. **Docker Hub** - Container deployment
4. **GitHub** - Version control (private repo)
5. **H16 Hardware** - Rugged tablet interface

### Network Architecture
```
Air-Side (Pi 5) <--TCP/UDP--> Ground-Side (H16)
       |                            |
       v                            v
   Sony Camera                Touch Display
       |                            |
       v                            v
   Edge Processing            User Controls
```

## 📈 Roadmap

### Q4 2024 (Completed)
- ✅ Basic infrastructure
- ✅ Protocol design
- ✅ Initial camera integration

### Q1 2025 (Current)
- 🔄 Advanced camera features
- 🔄 Gimbal integration
- 🔄 Recording controls
- ⏳ AI edge processing

### Q2 2025 (Planned)
- ⏳ Multi-camera support
- ⏳ Autonomous flight modes
- ⏳ Cloud integration
- ⏳ Production deployment

### Q3 2025 (Future)
- ⏳ ML model deployment
- ⏳ Fleet management
- ⏳ Analytics dashboard
- ⏳ Enterprise features

## 🚀 Recent Achievements

### Last Week (Oct 28 - Nov 3)
- ✅ Implemented LiveView streaming
- ✅ Fixed focus control via SDK
- ✅ Added property mapping system
- ✅ Stabilized UDP telemetry
- ✅ Created diagnostic tool tabs

### This Week (Nov 4-10)
- ✅ Optimized documentation (93% reduction)
- ✅ Implemented Git protocol automation
- ✅ Added DevTools deployment modes
- ✅ Created domain-based architecture
- 🔄 Testing across all platforms

## 🔧 Development Workflow

### Git Protocol
```bash
# Commit format enforced by hooks
[DOMAIN][TYPE] Component: Description

# Domains: [AIR], [GROUND], [TOOLS], [DOCS]
# Types: [FEATURE], [FIX], [PROTOCOL], [TEST]
```

### Quick Commands
```bash
# Start development session
START AIR        # Air-Side work
START GROUND     # Ground-Side work
START TOOLS      # DevTools work

# Build and deploy
cd sbc && ./build.sh              # Air-Side
cd android && ./gradlew build     # Ground-Side
cd SystemTools && python main.py   # DevTools
```

## 🎓 Knowledge Requirements

### To Work on Air-Side
- C++ proficiency
- Linux/embedded systems
- Sony SDK understanding
- Docker knowledge

### To Work on Ground-Side
- Android development
- Kotlin/Java
- Material Design
- Network programming

### To Work on Dev-Side
- Python programming
- GUI development
- Network protocols
- Testing frameworks

## 📞 Stakeholders

### Project Team
- **Lead Developer**: Anthony (you)
- **Claude Code**: AI development assistant
- **Claude Desktop**: Project management support

### Key Decisions Needed
1. Edge AI model selection
2. Cloud service provider
3. Production hardware specs
4. Certification requirements
5. Deployment timeline

## 🎯 Success Criteria

### Technical Success
- ✅ All domains communicate reliably
- ✅ Camera control fully functional
- ✅ UI intuitive and responsive
- ✅ System meets performance targets

### Business Success
- 🎯 Deployable product by Q2 2025
- 🎯 Competitive with DJI solutions
- 🎯 Scalable architecture
- 🎯 maintainable codebase

## 💡 Risk Factors

### Technical Risks
- Sony SDK limitations
- Network reliability in field
- H16 hardware constraints
- Pi 5 thermal management

### Mitigation Strategies
- Extensive field testing
- Redundant communication paths
- Thermal design optimization
- Comprehensive error handling

## 📝 Documentation Status

### Recently Optimized (Nov 4, 2025)
- **Before**: 5,700+ lines causing context overload
- **After**: 2,100 lines with clear structure
- **Benefit**: 93% reduction in main file size
- **Result**: Efficient Claude Code operations

### Key Documents
- `CC_READ_THIS_FIRST.md` - Entry point (140 lines)
- `GIT_PROTOCOL_GUIDE.md` - Git standards
- Domain-specific PROGRESS.md files
- Domain-specific TODO.md files

## 🔄 Next Actions

### Immediate (This Week)
1. Complete focus control testing
2. Implement gimbal commands
3. Add recording UI
4. Test network recovery

### Short Term (Next 2 Weeks)
1. Integrate all camera properties
2. Complete UI polish
3. Field testing setup
4. Performance optimization

### Long Term (Next Month)
1. Edge AI implementation
2. Multi-camera support
3. Production preparation
4. Documentation finalization

---

## Quick Reference for Claude Desktop

### When Managing Tasks
- Check domain-specific TODO.md files
- Review PROGRESS.md for completed items
- Monitor BLOCKERS.md for issues
- Update MASTER_STATUS.md weekly

### When Planning Sprints
- Air-Side: Focus on camera/SDK features
- Ground-Side: Focus on UI/UX
- Dev-Side: Focus on testing/diagnostics
- Protocol: Keep all domains synchronized

### When Reviewing Progress
- Git commits show [DOMAIN][TYPE] tags
- Each domain has progress tracking
- DevTools can run automated tests
- Documentation is optimized for AI assistance

---

*This overview provides Claude Desktop with comprehensive project context for effective project management support.*