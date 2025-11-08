# DPM-V2 Lessons Learned Registry
*Maintained by: CC-Project-Manager*
*Last Updated: 2025-11-08*
*Version: 1.1*

## 🎯 Purpose

This document serves as a **centralized knowledge base** capturing lessons learned from completed issues, failed attempts, and successful implementations across the DPM-V2 project. It enables future Claude Code sessions and developers to learn from history and avoid repeating mistakes.

**Integrated with:**
- Issue #21: Historical Learning System
- Issue #24: WHO Tag System
- `.github/scripts/search-history.sh` - Historical issue search

---

## 📚 Table of Contents
1. [How to Use This Document](#how-to-use-this-document)
2. [Quick Reference Index](#quick-reference-index)
3. [Focus & Camera Control](#focus--camera-control)
4. [Network & Communication](#network--communication)
5. [Protocol Implementation](#protocol-implementation)
6. [Cross-Domain Coordination](#cross-domain-coordination)
7. [Build & Deployment](#build--deployment)
8. [Testing & Quality Assurance](#testing--quality-assurance)
9. [Workflow & Process](#workflow--process)
10. [Anti-Patterns](#anti-patterns)
11. [Success Patterns](#success-patterns)

---

## How to Use This Document

### For Claude Code Sessions

**BEFORE starting any implementation:**
1. Search this document for relevant keywords
2. Read the related issues referenced
3. Note what failed and why
4. Build on successful patterns

**AFTER completing an issue:**
1. Extract key lessons from the issue
2. Add entry to appropriate section
3. Link back to source issue
4. Update Quick Reference Index

### For Human Developers

- Use as pre-implementation checklist
- Reference when debugging similar issues
- Contribute lessons from manual debugging
- Review quarterly for pattern recognition

---

## Quick Reference Index

### By Topic
- **Focus Distance Issues:** → [Focus & Camera Control](#focus-distance)
- **Manual Focus Problems:** → [Focus & Camera Control](#manual-focus)
- **AF Hold in MF Mode:** → [Focus & Camera Control](#resolved---af-hold-not-supported-in-manual-focus)
- **UDP Packet Issues:** → [Network & Communication](#udp-packets)
- **Cross-Domain Bugs:** → [Cross-Domain Coordination](#cross-domain-handoffs)
- **Sony SDK Integration:** → [Focus & Camera Control](#sony-sdk)
- **Protocol Sync Issues:** → [Protocol Implementation](#sync-failures)
- **Camera Enumeration Failure (0x34563):** → [Build & Deployment](#critical-sony-sdk-camera-enumeration-failure-error-0x34563)
- **USB Permissions:** → [Build & Deployment](#usb-permissions-for-sony-camera)
- **Docker Container Restarts:** → [Build & Deployment](#docker-container-issues)
- **Static IP Configuration:** → [Network & Communication](#critical-static-ip-requirement-for-vxlan-bridge)

### By Issue Number
- Issue #1: Focus distance readback → [Focus Distance](#focus-distance)
- Issue #2: AF Hold in Manual Focus (RESOLVED) → [Manual Focus](#resolved---af-hold-not-supported-in-manual-focus)
- Issue #10: Focus Distance Parsing (SOLVED) → [Focus Distance](#focus-distance)
- Issue #21: Historical Learning System → [Workflow & Process](#historical-learning)
- Issue #22: Manual Focus Commands Not Reaching Air-Side → [Manual Focus](#manual-focus)
- Issue #24: WHO Tag Enhancement → [Workflow & Process](#who-tag-system)
- Issue #33: NVMe Migration → [Build & Deployment](#critical-sony-sdk-camera-enumeration-failure-error-0x34563)

---

## Focus & Camera Control

### Focus Distance

**Related Issues:** #1, #2, #10, #22

#### ❌ Failed Approaches

**Attempt 1: Use getAvailableProperties() to discover focus**
- **Issue:** #1
- **WHO:** CC-Air-Side
- **What:** Tried to enumerate focus-related properties using Sony SDK getAvailableProperties()
- **Why it failed:** Sony SDK doesn't list all properties - many are hidden/undocumented
- **Lesson:** Don't rely on property enumeration for Sony cameras
- **Alternative:** Use specific SDK functions directly

**Attempt 2: Query property without checking focus mode**
- **Issue:** #1, #2
- **WHO:** CC-Air-Side
- **What:** Called getFocalDistanceMeters() without checking if camera is in MF/AF mode
- **Why it failed:** Different camera modes support different queries
- **Lesson:** ALWAYS check camera mode before querying focus-related properties
- **Code Pattern:**
  ```cpp
  // Wrong:
  auto distance = camera->getFocalDistanceMeters();

  // Right:
  auto focusMode = camera->getFocusMode();
  if (focusMode == FocusMode::Manual) {
      auto distance = camera->getFocalDistanceMeters();
  }
  ```

**Attempt 3: Hard-code focus distance values**
- **Issue:** #2
- **WHO:** CC-Air-Side
- **What:** Sent fixed focus distance values to camera
- **Why it failed:** Camera rejects values outside its valid range, which varies by lens
- **Lesson:** Query camera's valid range first, validate values before sending
- **Alternative:** Use camera->getFocusDistanceRange() before setting values

#### ✅ Successful Approach

**Solution: Sony SDK specific focus functions + mode checking**
- **Issue:** #10 (CLOSED - contains working implementation)
- **WHO:** CC-Ground-Side
- **What:**
  1. Air-Side: Used `camera->getFocalDistanceMeters()` with mode checking
  2. Ground-Side: Parsed `focal_distance_meters` field from UDP status
  3. UI: DisplayedView with LiveData updates
- **Why it worked:**
  - Used correct Sony SDK function
  - Checked focus mode before querying
  - Proper error handling for unsupported modes
  - Clean cross-domain handoff with documentation
- **Code References:**
  - Air: `sbc/src/camera/camera_sony.cpp:683` (getFocalDistanceMetersLocked)
  - Ground: `android/app/src/main/java/protocol/ProtocolMessages.kt:156`
  - Ground: `android/app/src/main/java/viewmodel/CameraViewModel.kt:289`

**Key Insights:**
1. Sony SDK has hidden/undocumented functions - check SDK headers directly
2. Focus-related queries are mode-dependent (AF vs MF)
3. Ground-Side parsing is simpler than expected - just extract field from JSON
4. LiveData updates handle UI refresh automatically

---

### Manual Focus

**Related Issues:** #2, #22

#### ❌ Failed Approaches

**Attempt 1: Send manual focus commands without Ground-Side routing**
- **Issue:** #22
- **WHO:** CC-Ground-Side
- **What:** UI sent manual focus commands but they never reached Air-Side
- **Why it failed:** Command routing bug in NetworkClient.kt - commands filtered incorrectly
- **Lesson:** Always test full end-to-end path for new commands
- **Debugging tip:** Check both send and receive logs: `adb logcat -s NetworkClient` + `docker logs payload_manager`

#### ✅ Resolved - AF Hold Not Supported in Manual Focus

**Issue #2 - RESOLVED**
**Date Discovered:** 2025-11-07
**Error Code:** `0x8402` - `CrError_Api_InvalidCalled`

**Finding:**
**AF Hold (Push Auto Focus) is NOT supported in Manual Focus mode** - this is a Sony SDK/camera limitation, not a code bug.

**Test Results:**
- Camera in Manual Focus (focus_mode = 0x1)
- AF Hold PRESS command sent via `SetDeviceProperty(CrDeviceProperty_PushAutoFocus)`
- Result: `0x8402 - CrError_Api_InvalidCalled`

**Root Cause:**
Even though the Sony SDK includes `TouchFunctionInMF` property suggesting AF should work in MF mode, the camera firmware rejects AF Hold commands when in Manual Focus mode.

**Resolution:**
Users must switch to AF-S, AF-C, or AF-A mode to use AF Hold functionality. This is documented behavior, not a bug.

**Lesson:** Not all Sony SDK properties work in all camera modes - always test and document mode dependencies.

---

### Sony SDK

**🔴 CRITICAL: Sony SDK API Reference Documentation**

**Location:** `docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html`
**Size:** 2000+ pages of comprehensive API documentation
**Quick Guide:** `docs/AIR_SIDE/SONY_SDK_REFERENCE.md`

**ALWAYS CHECK SDK DOCS BEFORE implementing ANY camera function!**

**Why:**
- Saves hours of trial-and-error
- Avoids wrong APIs and incorrect assumptions
- Documents prerequisites and constraints
- Provides valid parameter ranges
- Includes working example code

**How to use:**
1. Open `index.html` in browser
2. Search for function/property name
3. Read full documentation (not just signature)
4. Check prerequisites and constraints
5. Verify parameter types and ranges
6. Review example code
7. Document findings in issue comment

**See:** `docs/AIR_SIDE/SONY_SDK_REFERENCE.md` for complete workflow guide.

---

**General Lessons:**

#### ✅ Best Practices

0. **ALWAYS reference SDK documentation FIRST** ⭐ MOST IMPORTANT
   - **Why:** Prevents all the failures documented below
   - **How:** See `docs/AIR_SIDE/SONY_SDK_REFERENCE.md`
   - **Result:** Saves 2-4 hours per implementation
   - **Example:** Issue #1, #2 - would have been solved instantly with SDK docs

1. **Always check camera connection before SDK calls**
   - **Why:** SDK calls on disconnected camera crash the application
   - **Pattern:**
     ```cpp
     if (!camera || !camera->isConnected()) {
         LOG_ERROR("Camera not connected");
         return ErrorCode::NOT_CONNECTED;
     }
     ```

2. **Query supported features before using them**
   - **Why:** Not all Sony cameras support all features
   - **Pattern:**
     ```cpp
     if (camera->supportsFeature(Feature::FocalDistance)) {
         auto distance = camera->getFocalDistanceMeters();
     }
     ```

3. **Handle SDK errors gracefully**
   - **Why:** SDK errors are common and recoverable
   - **Anti-pattern:** Crash on SDK error
   - **Best practice:** Log error, return error code, continue operation

#### ❌ Anti-Patterns

1. **Calling SDK functions in tight loops**
   - **Why:** Some SDK calls are slow (100-500ms)
   - **Lesson:** Cache values, use reasonable polling intervals (1-2 seconds)

2. **Ignoring SDK return codes**
   - **Why:** Silent failures lead to confusing bugs
   - **Lesson:** ALWAYS check return codes, log failures

---

## Network & Communication

### UDP Packets

**Related Issues:** Multiple (documented in ISSUE_PREFIX_TAXONOMY.md)

#### ❌ Failed Approaches

**Attempt 1: Send large UDP packets (> 1KB)**
- **What:** Tried to send full camera status in single UDP packet
- **Why it failed:** Fragmentation causes packet loss on poor networks
- **Lesson:** Keep UDP packets under 1KB, use TCP for large data
- **Alternative:** Split data across multiple packets or use TCP for bulk transfers

**Attempt 2: Compress UDP data**
- **What:** Added compression to reduce packet size
- **Why it failed:** Compression added latency (20-50ms), defeated purpose of UDP
- **Lesson:** If data too large for UDP, use TCP instead of compressing

#### ✅ Successful Approach

**Solution: Keep UDP under 1KB, prioritize critical data**
- **Pattern:** Include only essential telemetry in UDP status packets
- **Result:** Reliable delivery even on poor networks
- **Data priority:**
  1. Critical: Camera connection status, focus mode, recording state
  2. Important: Focus distance, exposure settings
  3. Optional: Battery level, temperature (send less frequently)

---

### TCP Commands

#### ✅ Best Practices

1. **Command acknowledgment pattern**
   - Ground sends command → Air executes → Air sends ACK → Ground confirms
   - Prevents lost commands
   - Enables retry logic

2. **Timeout handling**
   - Set reasonable timeouts (5-10 seconds)
   - Log timeout events
   - Allow user retry

---

### Network Configuration

#### 🔴 CRITICAL: Static IP Requirement for VXLAN Bridge

**Severity:** 🔴 **CRITICAL** - Air-Side to Ground-Side communication
**Date Documented:** 2025-11-07

**Requirement:**
Air-Side MUST have static IP `192.168.144.10/24` on eth0 for VXLAN bridge to H16 Ground-Side.

**Configuration File:** `/etc/dhcpcd.conf`
```bash
interface eth0
static ip_address=192.168.144.10/24
noipv6
```

**Why Critical:**
- VXLAN bridge requires consistent IP addressing
- Ground-Side (H16) expects Air-Side at `192.168.144.10`
- DHCP changes would break UDP/TCP communication

**Included In:**
- ✅ NVMe deployment script: `tools/deployment/deploy-air-side.sh` (lines 95-102)
- ✅ Deployment checklist: `tools/deployment/NVME_MIGRATION_CHECKLIST.md`

**Verification:**
```bash
ip addr show eth0
# Should show: inet 192.168.144.10/24

ping 192.168.144.11  # H16 Ground-Side
```

**Lesson:** Network configuration is part of the deployment checklist - always verify after fresh OS install or NVMe migration.

---

## Protocol Implementation

### Sync Failures

**Related Issues:** #10, protocol changes

#### ❌ Common Mistake

**Implementing protocol on one side only**
- **What:** Air-Side adds field to status packet, forgets to update Ground-Side parser
- **Why it fails:** Ground-Side silently ignores unknown fields, feature appears broken
- **Lesson:** Protocol changes ALWAYS require both sides + protocol.json update

#### ✅ Correct Process

**Cross-domain protocol implementation:**
1. Update `protocol/*.json` with new field
2. Implement Air-Side (data source)
3. Document message format in Air-Side commit
4. Create Ground-Side issue with parsing instructions
5. Ground-Side implements parser
6. Update `protocol/*.json` implemented flags
7. Integration test

**Checklist:**
- [ ] `protocol/*.json` updated
- [ ] Air-Side implemented
- [ ] Ground-Side implemented
- [ ] `implemented` flags set to `true`
- [ ] Integration test passed
- [ ] PROGRESS_AND_TODO.md updated

---

## Cross-Domain Coordination

### Cross-Domain Handoffs

**Related Issues:** #1, #2, #10, #22

#### ❌ Failures

**Failure 1: No handoff documentation (Issue #10)**
- **What:** Air-Side completed, didn't document what Ground-Side needs
- **Result:** Ground-Side session had to reverse-engineer Air-Side changes
- **Time wasted:** 2-4 hours
- **Lesson:** ALWAYS provide detailed handoff instructions

**Failure 2: Assuming other domain will "figure it out"**
- **What:** Air-Side changed message format without documentation
- **Result:** Ground-Side used old parser, feature broke silently
- **Lesson:** Breaking changes need explicit coordination

#### ✅ Success Pattern

**Effective cross-domain handoff (Issue #24):**
- **WHO:** CC-Air-Side completes implementation
- **Action:** Posts detailed comment with:
  - What was implemented
  - What changed (file:line references)
  - What Ground-Side needs to do
  - Code examples for Ground-Side
  - Testing instructions
- **WHO:** CC-Ground-Side reads comment, implements, confirms
- **Result:** Smooth handoff, no confusion, fast implementation

**Template:**
```markdown
**WHO:** CC-Air-Side

Air-Side implementation complete.

**Changes:**
- File: sbc/src/camera/camera_sony.cpp:683
- Function: getFocalDistanceMetersLocked()
- Message field added: `focal_distance_meters` (double)

**Ground-Side TODO:**
1. Update ProtocolMessages.kt to parse `focal_distance_meters`
2. Add LiveData field in CameraViewModel.kt
3. Display in CameraScreen.kt

**Example parsing code:**
\`\`\`kotlin
val focalDistance = statusData.optDouble("focal_distance_meters", 0.0)
_focalDistance.postValue(focalDistance)
\`\`\`

**Testing:**
After Ground-Side implementation, focus distance should display in real-time.
```

---

## Build & Deployment

### 🔴 CRITICAL: Sony SDK Camera Enumeration Failure (Error 0x34563)

**Date Discovered:** 2025-11-07
**Severity:** 🔴 **CRITICAL** - Complete camera failure
**Error Code:** `0x34563` - "No adapters available"
**Related:** Issue #33 (NVMe Migration)

#### Problem Description

After Docker container restarts or rebuilds, camera enumeration fails with error 0x34563, preventing all camera operations. The camera is physically connected and visible via `lsusb`, but the Sony SDK cannot enumerate it.

#### Root Cause

**Missing `CrAdapter/` directory in the build output folder.**

The Sony Camera Remote SDK requires adapter libraries (`libCr_PTP_USB.so`, `libCr_PTP_IP.so`) to be present in a `CrAdapter/` subdirectory relative to the executable. These adapters are responsible for camera enumeration over USB and network.

**Directory Structure Required:**
```
/app/sbc/build/
├── payload_manager           # Executable
└── CrAdapter/                 # REQUIRED - Adapters directory
    ├── libCr_PTP_USB.so       # USB adapter
    ├── libCr_PTP_IP.so        # Network adapter
    ├── libusb-1.0.so
    └── libssh2.so
```

**What Happens Without CrAdapter:**
- Sony SDK initializes successfully (v2.0.0)
- `SDK::EnumCameraObjects()` returns 0x34563
- No cameras enumerated even though physically connected
- All camera commands fail with "Camera not connected"

#### Timeline of Discovery

1. **18:03** - Camera working fine, fully connected
2. **18:13** - Docker container restarted
3. **18:13** - Camera enumeration begins failing with 0x34563
4. **23:30** - Issue persists through multiple restart attempts
5. **23:42** - Root cause identified: Missing `CrAdapter/` directory
6. **23:42** - Fixed by: `cp -r /app/sdk/external/crsdk/CrAdapter /app/sbc/build/`
7. **23:45** - Camera reconnects successfully

#### Solution

**Production Dockerfile (Dockerfile.prod) - ALREADY INCLUDES FIX:**

Lines 42-43 in `sbc/Dockerfile.prod`:
```dockerfile
mkdir -p CrAdapter && \
cp -r /app/sdk/external/crsdk/CrAdapter/* CrAdapter/
```

**Manual Fix (if needed):**
```bash
# Inside running container
docker exec payload-manager cp -r /app/sdk/external/crsdk/CrAdapter /app/sbc/build/

# Then restart
docker restart payload-manager
```

**For Fresh Builds:**
```bash
# Use production Dockerfile
cd ~/DPM-V2
docker build -f sbc/Dockerfile.prod -t payload-manager:latest .

# Verify CrAdapter exists
docker exec payload-manager ls /app/sbc/build/CrAdapter/
```

#### Prevention

**✅ DO:**
- Always use `Dockerfile.prod` for production builds
- Verify CrAdapter directory exists after build: `docker exec <container> ls /app/sbc/build/CrAdapter/`
- Include CrAdapter copy step in any custom build scripts
- Document CrAdapter requirement in deployment guides

**❌ DON'T:**
- Use development Dockerfile for production containers
- Manually rebuild inside container without copying adapters
- Delete or move CrAdapter directory

#### Impact

**Before Fix:**
- Camera enumeration: ❌ FAIL (0x34563)
- All camera operations: ❌ BLOCKED
- System uptime since last build: CRITICAL

**After Fix:**
- Camera enumeration: ✅ SUCCESS
- Camera operations: ✅ WORKING
- Deployment reliability: ✅ IMPROVED

---

### USB Permissions for Sony Camera

**Date Discovered:** 2025-11-07
**Severity:** 🟡 **HIGH** - Camera connection failure

#### Problem

Camera enumeration fails after fresh OS install or system updates even when physically connected and in PC Remote mode.

#### Root Cause

Missing udev rules for Sony camera USB permissions. Without proper permissions (0666, plugdev group), the Docker container cannot access the USB device.

#### Solution

**Create udev rules file:**
```bash
sudo tee /etc/udev/rules.d/99-sony-camera.rules << 'EOF'
# Sony Camera USB permissions for DPM-V2
# Allows Docker container to access Sony camera via USB
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="*", MODE="0666", GROUP="plugdev"
EOF

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Verification:**
```bash
lsusb | grep Sony
# Bus 004 Device 019: ID 054c:0d1c Sony Corp. ILCE-1

ls -l /dev/bus/usb/004/019
# crw-rw-rw- 1 root plugdev 189, 402 Nov  7 23:30 /dev/bus/usb/004/019
```

**Included In:**
- ✅ NVMe deployment script: `tools/deployment/deploy-air-side.sh` (lines 108-117)
- ✅ Production Dockerfile: USB device passed with `--device /dev/bus/usb:/dev/bus/usb`

---

### Docker Container Issues

#### ❌ Common Issues

**Issue 1: Library path not set**
- **Symptom:** Sony SDK library not found at runtime
- **Solution:** Set `LD_LIBRARY_PATH` in container or run script
- **Prevention:** Include in Dockerfile ENV or startup script

**Issue 2: Container cache prevents rebuild**
- **Symptom:** Code changes not reflected in running container
- **Solution:** `docker-compose build --no-cache`
- **Lesson:** Always rebuild after C++ changes

**Issue 3: Container Restart Persistence**
- **Lesson:** Docker container restarts can lose runtime changes made inside container
- **Impact:**
  - Binary rebuilt inside container: ❌ Lost on restart
  - CrAdapter manually copied: ❌ Lost on restart
  - Adapter files in image: ✅ Persistent
- **Best Practice:**
  - Always rebuild Docker image for code changes
  - Never rely on `docker exec` modifications for permanent changes
  - Use volumes for logs and data, not binaries

---

## Testing & Quality Assurance

### Integration Testing

#### ✅ Best Practices

1. **Test cross-domain features end-to-end**
   - Don't assume individual components work together
   - Test full user workflow

2. **Test on actual hardware**
   - Simulators hide timing issues
   - Sony camera behavior differs from mocks

3. **Document test results in issues**
   - **WHO:** User (Anthony) confirms testing
   - Provides confidence for closure

---

## Workflow & Process

### Historical Learning

**Related Issue:** #21

#### ✅ Success

**Historical search prevented repeated failures:**
- **Example:** Issue #1 search found Issue #10 with working Ground-Side solution
- **Time saved:** 2-4 hours of re-implementation
- **ROI:** 2 minutes searching = 120x return

**Best Practice:**
```bash
# Always search before implementing
.github/scripts/search-history.sh "focus"
gh issue view 10 --comments
```

---

### WHO Tag System

**Related Issue:** #24

#### ✅ Success

**WHO tags enable clear attribution:**
- Know which CC instance (Air/Ground/Tools/PM) worked on what
- Track cross-domain handoffs
- Search by domain: `gh issue list --search "WHO: CC-Air-Side"`

**Lesson:** Standardized WHO tags transform GitHub issues into searchable knowledge base

---

## Anti-Patterns

### Code Anti-Patterns

1. **❌ Silent failure**
   - Ignoring errors, returning success when failed
   - **Fix:** Log errors, return error codes, alert user

2. **❌ Hardcoded values**
   - Magic numbers, hardcoded IPs, fixed timeouts
   - **Fix:** Use configuration files, protocol specs

3. **❌ Tight coupling**
   - Air-Side assumes Ground-Side implementation details
   - **Fix:** Use protocol as contract, document assumptions

### Workflow Anti-Patterns

1. **❌ Implementing without historical search**
   - Repeats failed attempts from previous issues
   - **Fix:** ALWAYS search first (Rule #1)

2. **❌ Not updating GitHub issues**
   - User has no visibility, work gets duplicated
   - **Fix:** Update issue immediately when starting work

3. **❌ Closing issues without user confirmation**
   - Premature closure, feature might not work
   - **Fix:** Wait for user testing confirmation

---

## Success Patterns

### Implementation Patterns

1. **✅ Protocol-first development**
   - Define protocol change in `protocol/*.json`
   - Implement both sides against spec
   - Update sync flags

2. **✅ Cross-domain handoff documentation**
   - Detailed instructions for next domain
   - Code examples, file references
   - Testing criteria

3. **✅ Incremental testing**
   - Test at each layer (SDK → UDP → parsing → UI)
   - Isolate failures quickly

### Workflow Patterns

1. **✅ Historical search workflow**
   - Search → Read → Learn → Implement differently
   - Document new lessons

2. **✅ WHO tag discipline**
   - Every comment starts with WHO tag
   - Clear attribution and tracking

3. **✅ PM coordination for complex features**
   - Use PM role for multi-domain features
   - Create coordination plan
   - Track dependencies

---

## Maintenance

### PM Responsibilities

**WHO:** CC-Project-Manager

**After each closed issue:**
1. Review issue for lessons learned
2. Extract key insights
3. Add to appropriate section
4. Update Quick Reference Index
5. Link back to source issue

**Monthly:**
1. Review all closed issues from past month
2. Identify patterns across issues
3. Add new sections if needed
4. Archive outdated lessons

**Quarterly:**
1. Comprehensive review with user
2. Identify systemic issues
3. Update workflow governance
4. Refine lessons learned structure

---

## How to Contribute

### Claude Code Instances

When closing an issue:
```bash
# Extract lessons and add to this doc
# 1. Identify what failed and why
# 2. Identify what worked and why
# 3. Add to appropriate section
# 4. Link back to issue number
```

### Human Developers

- Add lessons from manual debugging
- Correct inaccurate lessons
- Suggest new categories
- Review for clarity

---

## Appendix

### Sony SDK Error Code Reference

| Error Code | Hex | Meaning | Typical Cause | Solution |
|------------|-----|---------|---------------|----------|
| 0x34563 | 0x34563 | No adapters available | Missing CrAdapter/ directory | Copy CrAdapter libs to build folder |
| 0x8402 | 0x8402 | CrError_Api_InvalidCalled | Operation not valid in current camera mode | Check camera mode, switch to AF for AF Hold |
| 0x8208 | 0x8208 | Connection timeout | OnConnected callback timeout | Check USB connection, camera mode |

### Useful Diagnostic Commands

```bash
# Check camera USB connection
lsusb | grep Sony

# Check USB device permissions
ls -l /dev/bus/usb/004/<device_number>

# Check Docker container CrAdapter
docker exec payload-manager ls /app/sbc/build/CrAdapter/

# Check camera connection in logs
docker logs payload-manager | grep "Camera fully connected"

# Check for enumeration errors
docker logs payload-manager | grep "0x34563"

# Verify static IP configuration
ip addr show eth0

# Test VXLAN bridge connectivity
ping 192.168.144.11  # H16 Ground-Side
```

---

## Version History

| Version | Date | Changes | WHO |
|---------|------|---------|-----|
| 1.0 | 2025-11-07 | Initial creation | CC-Project-Manager |
| 1.1 | 2025-11-08 | Merged Air-Side deployment lessons (CrAdapter, USB, Static IP, AF Hold) | CC-Project-Manager |

---

*This document is a living registry. Update frequently. Search often. Learn continuously.*

**Related Documents:**
- `docs/CC_READ_THIS_FIRST.md` - Main workflow guide
- `docs/ALL_DOMAINS/WHO_TAG_GUIDE.md` - WHO tag system
- `docs/ISSUE_PREFIX_TAXONOMY.md` - Issue taxonomy
- `.github/scripts/search-history.sh` - Historical search tool
- `docs/AIR_SIDE/SONY_SDK_REFERENCE.md` - Sony SDK documentation guide
