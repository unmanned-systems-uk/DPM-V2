# Lessons Learned: Manual Focus Debugging Session
## November 10, 2025

---

## Executive Summary

**Incident**: Manual focus control failure (Issues #48, #49)
**Time Spent**: ~6+ hours of active debugging
**Root Cause**: Environmental/camera configuration change (NOT code regression)
**Key Learning**: Need snapshot/comparison tools to identify configuration drift
**Outcome**: Created Camera Property Snapshot System (Issue #57) to prevent future incidents

---

## Timeline of Events

### Initial Problem (Nov 9-10)
- Manual focus was working on November 1st
- By November 9th, manual focus completely broken
- SDK error 0x8402 (`CrError_Api_InvalidCalled`) on all focus operations
- User confirmed: Same lens, same camera settings, Sony Remote app DOES work

### Debugging Attempts

#### Attempt 1: Restore Diagnostic Check (Commit d6943f7)
- **Action**: Restored FocalDistanceInMeter availability check
- **Hypothesis**: Recent code cleanup removed necessary validation
- **Result**: FAILED - Still getting 0x8402 error
- **Time**: ~1 hour

#### Attempt 2: Restore LiveView Enable (Commit 04d4e13)
- **Action**: Restored LiveView enable code from Oct 31
- **Hypothesis**: LiveView must be enabled for manual focus
- **Result**: FAILED - LiveView enable itself failed with 0x8402
- **Time**: ~1.5 hours

#### Attempt 3: Fix LiveView API (Commit 4a89385)
- **Action**: Changed from `SetDeviceProperty()` to `SetDeviceSetting()`
- **Discovery**: Used wrong API for LiveView enable
- **Result**: PARTIAL SUCCESS - LiveView now enables, but FocalDistanceInMeter still unavailable
- **Time**: ~1 hour

#### Attempt 4: Git Rollback Investigation (Branch manual-focus-investigation)
- **Action**: Rollback to Oct 31 commit (943d13a) - last known working state
- **Hypothesis**: Code regression between Oct 31 and Nov 10
- **Result**: CRITICAL FINDING - Oct 31 code has IDENTICAL failure
- **Conclusion**: NOT a code issue - camera/environment changed
- **Time**: ~2 hours

### Total Debugging Time: 6+ hours
### Actual Code Issue: None - environmental change

---

## What We Learned

### 1. Code Rollback Testing Is Invaluable

**What We Did Right:**
- Created separate investigation branch
- Built and deployed Oct 31 "known working" code
- Tested with actual hardware
- Definitively proved it's NOT a code regression

**Lesson**: When users report "it worked before," rollback testing can save hours of code debugging

### 2. We Lack Visibility Into Camera State

**The Problem:**
- No way to see what camera properties were set on Nov 1st (working)
- No way to see what changed between Nov 1st and Nov 10th (broken)
- No baseline to compare against

**Analogy**: Debugging without logs - we're flying blind

**Lesson**: Configuration state is as important as code state

### 3. Environmental Changes Are Invisible

**What Changed Between Nov 1st and Nov 10th:**
- Unknown - could be:
  - Camera menu settings changed
  - Lens firmware
  - Camera firmware
  - Power cycle behavior
  - USB connection mode
  - LiveView settings on camera body

**The Reality**: Sony Remote app works = camera/lens are capable, we're just missing configuration

**Lesson**: Code testing alone doesn't catch environmental drift

### 4. SDK Errors Are Often Misleading

**Error 0x8402: "Invalid Called"**
- Doesn't tell us WHY it's invalid
- Doesn't tell us WHAT property is missing
- Doesn't tell us HOW to fix it

**Better Error**: "FocalDistanceInMeter property not available - check camera LiveView settings"

**Lesson**: Defensive diagnostics are critical for black-box SDKs

### 5. Git History ≠ Configuration History

**We Have**:
- Perfect git history of all code changes
- Commit messages, diffs, rollback capability

**We DON'T Have**:
- History of camera property states
- Baseline of "known good" configuration
- Change detection for settings

**Lesson**: Version control for code, but no version control for hardware state

---

## Process Improvements

### 1. Establish Baseline Snapshots

**New Process**:
- Capture camera property snapshot when system is CONFIRMED WORKING
- Tag snapshots: "Baseline - All Features Working"
- Store in version control or persistent location
- Reference during debugging

**Benefit**: Instant comparison point

### 2. Capture State Before/After Changes

**New Process**:
- Before firmware update → capture snapshot
- After firmware update → capture snapshot + auto-compare
- Before lens change → capture snapshot
- After code deployment → capture snapshot

**Benefit**: Isolate exactly what changed

### 3. Automated Configuration Drift Detection

**New Process** (Issue #57 Phase 3):
- On every Air-Side startup
- Compare current camera properties to baseline
- If differences detected → warn user IMMEDIATELY
- Prevent flying with unknown configuration changes

**Example Warning**:
```
⚠️  CAMERA CONFIGURATION CHANGED
3 properties changed since last known good state:
❌ FocalDistanceInMeter: available → unavailable
⚠️  ExposureMode: Manual → Auto
```

**Benefit**: Catch issues before they become blockers

### 4. Multi-Domain Diagnostic Tools

**New Process** (Issue #55):
- TOOLS Dashboard: Mimic ALL Ground-Side controls
- Automated diagnostics on button press
- Cross-check Air-Side logs, camera state, protocol messages
- Self-service debugging for users

**Benefit**: Reduce dependency on code-level debugging

---

## Technical Learnings

### 1. Sony SDK API Subtleties

**Discovery**: Different APIs for different property types
- `SetDeviceProperty()` - For device properties (focus, ISO, etc.)
- `SetDeviceSetting()` - For system settings (LiveView enable, PC Remote)

**Lesson**: RTFM - Sony SDK documentation has critical distinctions

**Documentation Gap**: Our code doesn't document which API to use for which operation

**Action**: Add comments documenting API usage patterns

### 2. Property Dependencies Are Complex

**Discovery**: Manual focus requires:
1. LiveView must be enabled (Setting)
2. FocalDistanceInMeter must be available (Property)
3. Focus mode must be Manual (Property)
4. Camera must be in correct shooting mode (?)
5. Unknown other prerequisites

**Lesson**: Dependencies are not documented - need empirical testing

**Action**: Camera Property Snapshot System will capture all prerequisites

### 3. LiveView Enable Is Non-Obvious

**Wrong Code**:
```cpp
SDK::CrDeviceProperty lv_prop;
lv_prop.SetCode(CrDeviceProperty_LiveViewStatus);
lv_prop.SetCurrentValue(0x01);
SDK::SetDeviceProperty(device_handle_, &lv_prop);  // FAILS
```

**Correct Code**:
```cpp
SDK::SetDeviceSetting(device_handle_, Setting_Key_EnableLiveView, 1);  // WORKS
```

**Lesson**: LiveView is a "setting" not a "property" in Sony SDK terminology

**Documentation Action**: Add to Air-Side developer docs

### 4. Error 0x8402 Has Multiple Causes

**Observed Causes**:
1. Property not available (FocalDistanceInMeter)
2. Wrong API used (SetDeviceProperty vs SetDeviceSetting)
3. Camera in wrong state (LiveView disabled)
4. Camera in wrong mode (unknown)

**Lesson**: Generic error codes require contextual diagnostics

**Action**: Add property availability checks before all operations

---

## What Worked Well

### 1. Systematic Approach
- Created clear issues for tracking (#53, #54, #55)
- Separate investigation branch for rollback testing
- Documented all attempts in git commits
- Used git history effectively

### 2. User Communication
- User provided clear feedback on each test
- User identified that Sony Remote app works (key insight)
- User suggested git rollback investigation (excellent idea)
- User requested snapshot system (transformative enhancement)

### 3. Building Blocks for Future
- Created Issue #57 (Camera Property Snapshot System)
- Created Issue #55 (Camera Control Testing Panel)
- Identified need for better diagnostic tools
- Learned API subtleties for future reference

---

## What Didn't Work

### 1. Assumption: Code Regression
- Spent hours debugging code
- Multiple build/deploy cycles
- All based on assumption that code changed
- **Reality**: Code was fine, environment changed

**Better Approach**: Rollback test FIRST before code debugging

### 2. Lack of Diagnostics
- Couldn't see camera property states
- Couldn't compare before/after
- Relied on trial-and-error

**Better Approach**: Snapshot system would have identified issue in 10 seconds

### 3. SDK Error Messages Insufficient
- Error 0x8402 doesn't explain root cause
- Had to guess what's wrong
- No guidance on how to fix

**Better Approach**: Wrap SDK calls with contextual error messages

---

## Preventive Measures (Future)

### 1. Camera Property Snapshot System (Issue #57)

**Phase 1: Capture & Store**
- Snapshot all camera properties on startup
- Snapshot on SDK errors
- Snapshot on user request
- Store with timestamps and tags

**Phase 2: Compare & Analyze**
- TOOLS UI for snapshot comparison
- Visual diff showing changed properties
- Filter by category (focus, exposure, etc.)
- Export for team sharing

**Phase 3: Automatic Change Detection** ⭐
- On power-up: compare current vs baseline
- Warn user if configuration changed
- Show exactly what changed
- Allow user to accept or investigate

**Phase 4: Historical Tracking**
- Timeline of property changes
- Identify when specific property changed
- Audit trail of configurations

**Benefit**: Issues like today's would be solved in **10 seconds** instead of **6 hours**

### 2. Camera Control Testing Panel (Issue #55)

**Purpose**: Self-service debugging from TOOLS Dashboard

**Features**:
- Buttons mimicking ALL Ground-Side controls
- Uses exact same protocol commands
- Automated diagnostics on button press
- Cross-checks logs and camera state
- Identifies root cause automatically

**Benefit**: Users can debug without Air-Side code access

### 3. Baseline Management Process

**Process**:
1. Capture "golden baseline" when ALL features working
2. Tag: "Baseline - 2025-11-01 - All Features Working"
3. Store in `/app/baselines/` and git repository
4. Reference during all debugging sessions
5. Update baseline after verified changes

**Benefit**: Always have known-good state to compare against

### 4. Pre-Flight Configuration Check

**Process**:
1. User powers on system
2. Air-Side captures current camera properties
3. Compares to baseline automatically
4. If changes detected → WARNING shown
5. User must acknowledge or fix before flight

**Benefit**: Catch configuration drift before it causes failures

---

## Recommendations

### Immediate (This Week)

1. **Fix Phase 1 Compilation Errors** (~2 hours)
   - Fix `camera_id_` member issue
   - Verify Sony SDK property codes
   - Complete stashed implementation

2. **Deploy Basic Snapshot Functionality** (~1 hour)
   - Build and test
   - Capture baseline snapshot
   - Document snapshot locations

3. **Investigate Camera Settings** (~2-4 hours)
   - Systematically test camera menu settings
   - Identify what enables FocalDistanceInMeter
   - Document findings
   - Fix manual focus

### Short-term (This Month)

4. **Complete Phase 2 TOOLS Integration** (~6-8 hours)
   - Snapshot management UI
   - Comparison tool
   - Property filtering

5. **Implement Phase 3 Power-Up Detection** (~8-10 hours)
   - Startup comparison logic
   - Ground-Side notifications
   - TOOLS warning banner

6. **Complete Issue #55 Camera Control Panel** (~6-8 hours)
   - Mimic Ground-Side controls
   - Automated diagnostics
   - Self-service debugging

### Long-term (Next Quarter)

7. **Phase 4 Historical Tracking** (~4-6 hours)
   - Timeline visualization
   - Export reports
   - Team collaboration features

8. **Comprehensive Air-Side Developer Docs**
   - Sony SDK API usage patterns
   - Property vs Setting distinction
   - Known prerequisites for operations
   - Common error codes and fixes

9. **Automated Testing with Camera Simulator**
   - Mock Sony SDK responses
   - Test all camera operations
   - Catch regressions before deployment

---

## Key Metrics

### Debugging Session Metrics
- **Total Time**: 6+ hours
- **Code Commits**: 3 (all unnecessary - no code issue)
- **Build/Deploy Cycles**: 4
- **Issues Created**: 4 (#53, #54, #55, #57)
- **Root Cause**: Environmental change (not code)

### With Snapshot System (Projected)
- **Time to Identify Issue**: 10 seconds
- **Code Commits**: 0
- **Build/Deploy Cycles**: 0
- **User Frustration**: Minimal

### ROI Analysis
- **Investment**: ~20-30 hours (all 4 phases)
- **Savings per incident**: 6+ hours
- **Break-even**: After 3-5 similar incidents
- **Additional benefits**:
  - Prevents issues before they occur (power-up detection)
  - Enables self-service debugging (Issue #55)
  - Builds institutional knowledge (baselines)
  - Faster onboarding (snapshot examples)

---

## Quotes from Session

> "I am dispaired how this is broken now, this is a new issue."
> — User, after manual focus failure

> "Is it not possible to look at Git history from the 1st (Was working then) and compare what has changed?"
> — User, suggesting rollback investigation (excellent idea)

> "Should we / can we implement a system that reads all camera properties and logs them. This way if and when we get issues like this we can compare a ALL WORKING properties to the NOW NOT Working properties?"
> — User, proposing snapshot system (transformative idea)

> "When user powers up system, Air-Side pulls cameras properties, if not = last known properties then inform user, warning camera property xyz changed on camera since last use."
> — User, proposing automatic change detection (game-changing enhancement)

---

## Conclusion

This debugging session was **frustrating but valuable**:

### What We Lost
- 6+ hours of development time
- User confidence in system stability
- Clear path to resolution (still investigating camera settings)

### What We Gained
- **Critical insight**: We need configuration state visibility
- **Transformative enhancement**: Camera Property Snapshot System (Issue #57)
- **Self-service debugging**: Camera Control Testing Panel (Issue #55)
- **Process improvement**: Rollback testing methodology
- **Technical knowledge**: Sony SDK API distinctions

### The Big Picture

**This incident exposed a fundamental gap**: We have excellent version control for CODE but zero visibility into HARDWARE STATE.

The Camera Property Snapshot System isn't just a debugging tool—it's **configuration version control for hardware**. It will:

1. **Prevent incidents** (power-up change detection)
2. **Solve incidents 100x faster** (instant comparison)
3. **Enable self-service** (users can debug without developer)
4. **Build knowledge** (baselines become documentation)

**Today's pain = Tomorrow's prevention**

---

## Action Items

- [ ] Fix Phase 1 compilation errors
- [ ] Deploy basic snapshot functionality
- [ ] Capture baseline snapshot
- [ ] Investigate camera settings to fix manual focus
- [ ] Complete Phase 2 TOOLS integration
- [ ] Implement Phase 3 power-up detection
- [ ] Complete Issue #55 Camera Control Panel
- [ ] Document Sony SDK API usage patterns
- [ ] Update Air-Side developer documentation

---

**Document Created**: 2025-11-10
**Session Duration**: ~6 hours
**Issues Created**: #53, #54, #55, #57
**Commits Made**: d6943f7, 04d4e13, 4a89385
**Branches Created**: manual-focus-investigation

**Status**: Manual focus still broken (environmental issue) - Camera Property Snapshot System will prevent future occurrences
