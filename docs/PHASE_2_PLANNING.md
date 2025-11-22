# Phase 2 Planning - DPM-V2

**Date:** 2025-11-19
**Status:** Draft - Awaiting Domain Input
**PM Coordinator:** CC-PM

---

## Phase 1 Status: ✅ 100% COMPLETE

**Completion Date:** 2025-11-19
**Total Effort:** ~40 hours across 3 domains
**End-to-End Validation:** ✅ Complete

### Phase 1 Achievements:
- ✅ Structured Logging (Air-Side, Ground-Side, SystemTools)
- ✅ Health Monitoring (Broadcasts, Analytics, Threshold Alerts)
- ✅ Configuration Management (Bidirectional flow validated)
- ✅ Multi-domain coordination framework established

---

## Phase 2 Overview

**Strategic Goal:** Quality, Reliability, and Feature Delivery

**Estimated Duration:** 4-6 weeks
**Total Effort:** 60-80 hours across 3 domains

---

## Phase 2 Structure

### Phase 2A: Critical Blockers & Protocol Compliance (Week 1-2)
**Priority:** 🔴 CRITICAL - Must complete before other work
**Effort:** 15-20 hours

### Phase 2B: Official Quality Gates (Week 2-3)
**Priority:** 🟡 HIGH - Core Phase 2 deliverables
**Effort:** 20-25 hours
**Reference:** Issue #70

### Phase 2C: High-Value Features (Week 3-6)
**Priority:** 🟢 MEDIUM - User-facing enhancements
**Effort:** 25-35 hours

---

## Phase 2A: Critical Blockers & Protocol Compliance

**Timeline:** Days 1-10
**Goal:** Resolve blocking issues and protocol violations

### Task 1: Ground-Side StructuredLogger Protocol Compliance
**Issue:** #164
**Priority:** 🔴 CRITICAL
**Assignee:** CC-Ground-Side
**Effort:** 4-6 hours

**Problem:**
- Missing 3 log contexts (HEALTH, CONFIG, DISCOVERY)
- 223 raw Log.d/i/w/e() violations
- Hardcoded enum instead of protocol-driven

**Deliverables:**
- [ ] Add missing contexts to LogContext enum
- [ ] Migrate 223 raw Log calls to Timber/StructuredLogger
- [ ] Verify cross-domain log filtering works
- [ ] Document Ground-Side logging architecture

**Success Criteria:**
- 0 protocol violations
- All logs flow through StructuredLogger
- SystemTools can filter all Ground-Side contexts

---

### Task 2: SystemTools Protocol-Compliant Logger
**Issue:** #162
**Priority:** 🔴 CRITICAL
**Assignee:** CC-SystemTools
**Effort:** 3-4 hours

**Problem:**
- No log context enforcement
- Plain logger usage instead of ProtocolLogger wrapper

**Deliverables:**
- [ ] Implement ProtocolLogger wrapper (already designed)
- [ ] Enforce context parameter for all logs
- [ ] Add CONFIG and DISCOVERY contexts
- [ ] Migrate existing code to use ProtocolLogger

**Success Criteria:**
- All SystemTools logs have context tags
- Matches Air-Side/Ground-Side logging standards
- No hardcoded context strings

---

### Task 3: TCP Connection Validation
**Issue:** #45
**Priority:** 🔴 CRITICAL
**Assignee:** CC-Ground-Side
**Effort:** 3-4 hours

**Problem:**
- Silent command failures when connection drops
- No connection health validation before sending

**Deliverables:**
- [ ] Add TCP connection health check
- [ ] Implement connection state validation
- [ ] Add error reporting for failed sends
- [ ] Add retry logic with exponential backoff

**Success Criteria:**
- No silent failures on disconnect
- User sees clear error messages
- Commands retry automatically when connection restored

---

### Task 4: Camera Disconnection Investigation
**Issue:** #54
**Priority:** 🔴 BLOCKER
**Assignee:** CC-Air-Side
**Effort:** 4-6 hours

**Problem:**
- Oct 31 code reports camera disconnected despite physical connection
- May be blocking manual focus (#2, #40, #42, #48, #129)

**Deliverables:**
- [ ] Reproduce camera disconnection issue
- [ ] Identify root cause (SDK, USB, state machine)
- [ ] Implement fix or workaround
- [ ] Verify camera stays connected under load

**Success Criteria:**
- Camera remains connected during normal operation
- No false disconnection reports
- Manual focus unblocked

---

**Phase 2A Total:** 14-20 hours

---

## Phase 2B: Official Quality Gates (Issue #70)

**Timeline:** Days 8-20
**Goal:** Implement validation and error recovery

### Gap 4: Command Validation & Sanitization Layer
**Priority:** 🟡 HIGH
**Effort:** 10-12 hours

#### Air-Side Implementation (6-8h)
**Assignee:** CC-Air-Side

**Deliverables:**
- [ ] Create CommandValidator class
- [ ] Implement JSON parsing layer (strict mode)
- [ ] Implement JSON Schema validation
- [ ] Implement rate limiting (global + per-command)
- [ ] Implement queue depth checking (max 50)
- [ ] Implement state validation layer
- [ ] Create validation config files
- [ ] Add metrics tracking

**Config Files:**
- `sbc/config/validation/schemas.json`
- `sbc/config/validation/rate_limits.json`
- `sbc/config/validation/rules.json`

#### Ground-Side Implementation (2-3h)
**Assignee:** CC-Ground-Side

**Deliverables:**
- [ ] Create CommandResponse.kt with failure types
- [ ] Implement error banner UI
- [ ] Add color-coded severity display
- [ ] Show verbose validation errors

#### Testing (2h)
**All Domains**

**Test Cases:**
- [ ] Malformed JSON rejection
- [ ] Schema validation failures
- [ ] Rate limiting enforcement
- [ ] Queue depth limit
- [ ] State validation (e.g., focus command when disconnected)
- [ ] Verbose error messages displayed

**Success Criteria:**
- Invalid commands rejected before execution
- Clear error messages for all failure modes
- Rate limiting prevents flooding
- System stays stable under invalid input

---

### Gap 5: Enhanced Error Recovery Framework
**Priority:** 🟡 HIGH
**Effort:** 12-15 hours

#### Air-Side Implementation (8-10h)
**Assignee:** CC-Air-Side

**Deliverables:**
- [ ] Create Watchdog class with component monitoring
- [ ] Implement escalating recovery delays (500ms→5s, max 6 attempts)
- [ ] Create SystemModeManager (NORMAL/DEGRADED/EMERGENCY/SHUTDOWN)
- [ ] Implement Sony SDK timeout wrapper (10s)
- [ ] Add recovery actions (USB reset, network reconnect)
- [ ] Create recovery.json config file

**System Modes:**
- **NORMAL:** All systems operational
- **DEGRADED:** Non-critical components failed, core functions working
- **EMERGENCY:** Manual intervention required
- **SHUTDOWN:** Safe shutdown in progress

#### Ground-Side Implementation (2-3h)
**Assignee:** CC-Ground-Side

**Deliverables:**
- [ ] Create SystemModeIndicator status bar widget
- [ ] Add system mode card in Health Dashboard
- [ ] Add "Resume Normal Mode" button for EMERGENCY
- [ ] Display watchdog component status

#### Testing (2h)
**All Domains**

**Test Cases:**
- [ ] Simulate camera thread hang
- [ ] Simulate network disconnect
- [ ] Test escalating recovery delays
- [ ] Test EMERGENCY mode transition
- [ ] Test manual recovery from EMERGENCY
- [ ] Verify graceful degradation

**Success Criteria:**
- System auto-recovers from transient failures
- Escalating delays prevent thrashing
- EMERGENCY mode protects system
- Manual recovery works reliably

---

**Phase 2B Total:** 22-27 hours

---

## Phase 2C: High-Value Features

**Timeline:** Days 15-40
**Goal:** Deliver user-facing functionality

### Feature 1: Image Transfer POC
**Issue:** #139
**Priority:** 🟢 MEDIUM-HIGH
**Assignee:** CC-Air-Side
**Effort:** 6-8 hours

**Deliverables:**
- [ ] Implement single file transfer (Camera SD → SBC)
- [ ] Test with JPEG and ARW formats
- [ ] Measure transfer speeds
- [ ] Document transfer process

**Success Criteria:**
- Single image transfers successfully
- Transfer time < 2 seconds for JPEG
- Transfer time < 10 seconds for ARW

---

### Feature 2: Sony SDK Image Transfer (4 Modes)
**Issue:** #137
**Priority:** 🟢 MEDIUM
**Assignee:** CC-Air-Side
**Effort:** 12-16 hours

**Transfer Modes:**
1. **Mode 1:** Camera SD → SBC (during/after capture)
2. **Mode 2:** Camera SD → SBC (bulk transfer)
3. **Mode 3:** SBC → Ground-Side (via network)
4. **Mode 4:** End-to-end (Camera → SBC → Ground)

**Deliverables:**
- [ ] Implement all 4 transfer modes
- [ ] Add transfer progress reporting
- [ ] Add transfer queue management
- [ ] Create Ground-Side UI for image browsing
- [ ] Optimize network transfer bandwidth

**Success Criteria:**
- All 4 modes operational
- Transfer progress visible in UI
- Network bandwidth controlled
- Images viewable on H16

---

### Feature 3: Data-Link Health Check & Auto-Recovery
**Issue:** #91
**Priority:** 🟢 MEDIUM
**Assignee:** CC-Air-Side
**Effort:** 6-8 hours

**Deliverables:**
- [ ] Implement network link monitoring
- [ ] Add connection quality metrics
- [ ] Implement auto-reconnect logic
- [ ] Add health check heartbeats
- [ ] Create network status UI indicator

**Success Criteria:**
- Network disconnects detected within 5 seconds
- Auto-reconnect without user intervention
- Connection quality visible in UI

---

### Feature 4: UI State Tracking & Sync Rate Control
**Issue:** #68
**Priority:** 🟢 MEDIUM
**Assignee:** CC-Ground-Side
**Effort:** 6-8 hours

**Deliverables:**
- [ ] Track UI state changes (focus, ISO, shutter, etc.)
- [ ] Implement sync rate limiting
- [ ] Add UI update debouncing
- [ ] Optimize network traffic

**Success Criteria:**
- UI updates throttled to prevent network flooding
- Smooth UI experience without lag
- Network bandwidth reduced by 30-50%

---

### Feature 5: FishSemi AirControl SDK Integration
**Issue:** #167
**Priority:** 🟢 LOW-MEDIUM
**Assignee:** CC-Ground-Side
**Effort:** 8-12 hours

**Deliverables:**
- [ ] Integrate AirControl SDK for H16 hardware input
- [ ] Map joystick axes to camera controls
- [ ] Map buttons to functions
- [ ] Add hardware input configuration UI

**Success Criteria:**
- Physical joysticks control camera
- Hardware buttons trigger commands
- Input mapping configurable

---

### Feature 6: Standalone Tri-Domain Log Viewer
**Issue:** #107
**Priority:** 🟢 MEDIUM
**Assignee:** CC-SystemTools
**Effort:** 10-14 hours

**Deliverables:**
- [ ] Create standalone PyQt/Tkinter log viewer
- [ ] Support real-time log streaming
- [ ] Add advanced filtering (regex, context, domain)
- [ ] Add log export functionality
- [ ] Professional UI design

**Success Criteria:**
- Standalone executable (no DPM Management System)
- Real-time log updates
- Advanced filtering works
- Logs exportable to file

---

### Feature 7: Performance Analytics Enhancements
**Issue:** #130
**Priority:** 🟢 LOW-MEDIUM
**Assignee:** CC-SystemTools
**Effort:** 4-6 hours

**Deliverables:**
- [ ] Add trend analysis graphs
- [ ] Add anomaly detection improvements
- [ ] Add export to CSV/JSON
- [ ] Add custom time range selection

**Success Criteria:**
- Trends visible over time
- Anomalies highlighted clearly
- Data exportable for external analysis

---

**Phase 2C Total:** 52-72 hours (select subset based on priorities)

---

## Phase 2 Timeline Recommendation

### Week 1-2: Critical Blockers (Phase 2A)
**Focus:** Fix what's broken
- Ground-Side: Issue #164 StructuredLogger compliance
- SystemTools: Issue #162 Protocol logger
- Ground-Side: Issue #45 TCP validation
- Air-Side: Issue #54 Camera disconnection

**Goal:** 0 critical bugs, 100% protocol compliance

---

### Week 2-3: Quality Gates (Phase 2B)
**Focus:** Robustness and reliability
- Air-Side: Command validation layer
- Air-Side: Error recovery framework
- Ground-Side: Validation UI and system mode indicator
- All: Integration testing

**Goal:** System handles errors gracefully

---

### Week 3-6: High-Value Features (Phase 2C)
**Focus:** User value delivery
**Select 2-3 features based on user priorities:**

**Option A - Camera Features:**
- Image Transfer POC (#139)
- Sony SDK Image Transfer (#137)
- Manual Focus fixes (unblocked by #54)

**Option B - System Robustness:**
- Data-Link Health Check (#91)
- UI State Tracking (#68)
- Performance Analytics (#130)

**Option C - Developer Tools:**
- Standalone Log Viewer (#107)
- Performance Analytics (#130)
- Connection Monitor (#28)

---

## Dependencies & Blockers

**Phase 2A must complete before Phase 2B:**
- Error recovery depends on working camera connection (#54)
- Command validation needs protocol-compliant logging (#164, #162)

**Phase 2B must complete before Phase 2C:**
- Image transfer needs error recovery framework
- UI features need validation layer

---

## Success Criteria - Phase 2 Complete

**Protocol Compliance:**
- [ ] 0 protocol violations across all domains
- [ ] All logs use protocol-defined contexts
- [ ] All config uses protocol-defined parameters

**Robustness:**
- [ ] System recovers from camera disconnects
- [ ] System recovers from network disconnects
- [ ] Invalid commands rejected with clear errors
- [ ] System mode visible in UI

**Features:**
- [ ] At least 2 high-value features delivered
- [ ] User can perform primary workflows end-to-end
- [ ] Performance meets targets

**Documentation:**
- [ ] All ADRs created (ADR-020, ADR-021)
- [ ] User guide updated
- [ ] Architecture docs current

---

## Risk Assessment

**High Risk:**
- Issue #54 (Camera disconnection) may be deep SDK issue - allocate contingency time
- Image transfer may require significant optimization for performance

**Medium Risk:**
- Error recovery testing requires simulation framework
- Command validation schema design needs careful review

**Low Risk:**
- Protocol compliance is well-understood, just time-consuming
- TCP validation is straightforward implementation

---

## Resource Allocation

**Air-Side:** 35-45 hours
- Phase 2A: 4-6h (#54 camera)
- Phase 2B: 14-18h (validation + recovery)
- Phase 2C: 17-21h (image transfer + features)

**Ground-Side:** 17-25 hours
- Phase 2A: 7-10h (#164 compliance + #45 TCP)
- Phase 2B: 4-6h (validation UI + mode indicator)
- Phase 2C: 6-9h (UI features)

**SystemTools:** 8-12 hours
- Phase 2A: 3-4h (#162 protocol logger)
- Phase 2C: 5-8h (log viewer + analytics)

---

## Next Steps

**Immediate Actions (PM):**
1. ✅ Distribute Phase 2 planning to all domains
2. ⏳ Gather domain input on priorities
3. ⏳ Finalize Phase 2 schedule
4. ⏳ Create Phase 2 tracking issues
5. ⏳ Update Issue #70 with detailed plan
6. ⏳ Close Issue #170 (Phase 1 complete)

**Domain Actions:**
1. Review Phase 2 plan
2. Rank priorities for your domain
3. Identify any concerns or dependencies
4. Provide time estimates for selected work

---

## Notes from Planning Session

**User Preferences:**
- Keep current camera format (connected=bool, model=string) - Do not change to Issue #169 simplified format
- DPM Management System error handling is critical - all errors must show GUI popups

**Lessons from Phase 1:**
- Cross-domain coordination works well
- Protocol compliance must be enforced early
- Silent errors are unacceptable
- End-to-end testing is essential

**PM Observations:**
- Phase 1 took ~40h (estimated 35-42h) - good accuracy
- Bug fixing added 6-8h unplanned time
- Domain collaboration is highly effective
- Real-time tmux monitoring invaluable

---

**Status:** 📝 Draft - Awaiting domain input and user approval

**PM:** CC-PM
**Date:** 2025-11-19
**Version:** 1.0
