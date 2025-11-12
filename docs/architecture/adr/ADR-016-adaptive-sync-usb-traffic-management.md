# ADR-016: Adaptive Sync for USB Traffic Management

**Status:** Accepted
**Date:** 2025-11-12
**Deciders:** Development Team, Architecture Review
**Related Issues:** #67 (Air-Side implementation), #68 (Ground-Side implementation)
**Related ADRs:** ADR-008 (UDP Status Broadcast Rate), ADR-002 (Specification-First Property Management)
**Related Views:** `view-integration.md`, `view-data.md`, `view-logical.md`

---

## Context

### Problem Statement

As DPM-V2 expands camera control capabilities, we face a critical USB bandwidth management challenge:

**Current State:**
- Exposure triangle (aperture, shutter, ISO): 3 parameters @ 5Hz = 15 param reads/sec
- Control settings broadcast @ 5Hz
- USB ↔ Camera traffic: Constant polling

**Future State (Projected):**
- White balance: 2 params
- Focus modes: 3 params
- Picture profiles: 5 params
- ISO settings: 2 params
- Metering modes: 2 params
- Image stabilization: 2 params
- **Total: 19+ parameters**

**The Problem:**
- Cannot sync 19 parameters @ 5Hz = 95 param reads/sec
- USB bandwidth overflow risk
- Camera performance degraded by constant USB traffic
- Sony SDK processing distracted from primary function (image capture)

**Questions:**
1. How do we scale to many camera parameters without USB bandwidth overflow?
2. How do we minimize camera distraction from USB polling?
3. How do we maintain responsive UX where needed?
4. How do we implement this without Sony SDK change notification support (unknown availability)?

---

## Decision

**Implement Adaptive Sync Strategy with three tiers:**

### Tier 1: Exposure Triangle (High Priority)
- **UI Visible (user actively viewing):** 5Hz sync (200ms updates)
- **UI Not Visible (backgrounded/different screen):** 1Hz sync (1000ms updates)
- **Parameters:** Aperture, Shutter Speed, ISO

**Rationale:** User expects real-time updates when actively monitoring exposure controls, but background sync sufficient when not viewing.

### Tier 2: Critical Health Parameters
- **Always:** 1Hz sync (regardless of UI state)
- **Parameters:** Battery level, SD card space, camera connection status

**Rationale:** Need continuous health monitoring for system reliability, but these change slowly and don't need 5Hz.

### Tier 3: Extended Parameters (On-Demand Only)
- **On-Demand Sync Triggers:**
  1. System startup (get initial state)
  2. User opens parameter screen (fetch when needed)
  3. User changes parameter (send command + confirm)
  4. Stop syncing when UI screen closed
- **No periodic sync**
- **Parameters:** White balance, focus modes, picture profiles, metering, image stabilization, etc.

**Rationale:** Extended parameters change infrequently, only need sync when user actively configuring them.

---

## Alternatives Considered

### Alternative 1: Constant 5Hz Sync (Current + All Parameters)

**Approach:** Sync all 19 parameters @ 5Hz constantly

**Pros:**
- ✅ Simple implementation
- ✅ Always up-to-date
- ✅ No UI state tracking needed

**Cons:**
- ❌ 95 param reads/sec = USB bandwidth overflow risk
- ❌ Camera distracted by constant polling
- ❌ Doesn't scale to more parameters
- ❌ Wasteful (user not viewing most parameters most of the time)

**Rejection Reason:** Does not solve the core problem - bandwidth overflow.

---

### Alternative 2: Event-Driven Sync (Sony SDK Change Notifications)

**Approach:** Sony SDK pushes notifications when parameters change

**Pros:**
- ✅ Zero polling overhead
- ✅ Instant updates on change
- ✅ Scales to unlimited parameters

**Cons:**
- ❌ **Unknown if Sony SDK supports change notifications**
- ❌ Not implementable without SDK feature verification
- ❌ Complex state management (what if notification missed?)
- ❌ Dependency on Sony SDK capabilities

**Rejection Reason:** Cannot implement without knowing SDK capabilities. May revisit in future if SDK supports it.

---

### Alternative 3: Constant 1Hz Sync (All Parameters)

**Approach:** Reduce all parameters to 1Hz sync

**Pros:**
- ✅ Minimal bandwidth (19 param reads/sec)
- ✅ Simple implementation
- ✅ Scalable

**Cons:**
- ❌ 1 second lag feels slow for exposure monitoring
- ❌ Poor UX (fails ADR-008's 200ms instant perception requirement)
- ❌ Doesn't differentiate critical vs. non-critical parameters

**Rejection Reason:** Degrades user experience for active exposure monitoring.

---

### Alternative 4: No Periodic Sync (All On-Demand)

**Approach:** Only sync when user requests (no background sync)

**Pros:**
- ✅ Zero bandwidth when idle
- ✅ Scales to unlimited parameters

**Cons:**
- ❌ No real-time exposure monitoring
- ❌ Battery/SD status not monitored (critical health info)
- ❌ User must manually refresh to see changes
- ❌ Unacceptable UX degradation

**Rejection Reason:** Loses real-time monitoring capability, which is a core feature.

---

## Decision Rationale

**Why Strategy A (Adaptive Sync) is Optimal:**

1. **Solves Bandwidth Problem:**
   - Active monitoring: 17 param reads/sec (exposure 5Hz + health 1Hz)
   - Background: 5 param reads/sec (exposure 1Hz + health 1Hz)
   - Extended params: 0 reads/sec (on-demand only)
   - **80-94% bandwidth reduction vs. constant 5Hz**

2. **Maintains UX Quality:**
   - Real-time feel (5Hz) when user actively viewing exposure controls
   - Slight delay (~200ms) when opening extended param screens (acceptable)
   - Continuous health monitoring (battery, SD)

3. **Implementable Now:**
   - No dependency on unknown Sony SDK features
   - Uses existing polling mechanisms
   - Proven pattern in embedded systems

4. **Scalable:**
   - Add unlimited extended parameters with zero bandwidth impact
   - No performance degradation as parameter count grows

5. **Camera Performance:**
   - Minimal USB distraction (94% reduction in background)
   - Camera can focus on image capture, not constant polling

---

## Consequences

### Positive Consequences

✅ **Bandwidth Efficiency:**
- 80-94% reduction in USB traffic
- Scales to 50+ camera parameters without overflow
- Camera performance not impacted

✅ **Responsive UX:**
- Real-time (5Hz) exposure monitoring when actively viewing
- Acceptable latency (~200ms) for extended parameter screens
- Continuous health monitoring (battery, SD)

✅ **Implementable Immediately:**
- No dependency on unknown SDK features
- Uses existing architecture (ADR-002 PropertyLoader, ADR-008 broadcast patterns)

✅ **Future-Proof:**
- Can add event-driven sync later if Sony SDK supports it
- Adaptive sync can coexist with event notifications

### Negative Consequences

⚠️ **UI State Tracking Complexity:**
- Ground-Side must track which UI screens are visible
- Air-Side must support dynamic sync rate changes
- Mitigation: Simple state machine, clear API contract

⚠️ **Parameter Drift Risk:**
- Extended parameter changed by camera button (not app)
- User opens screen 5 minutes later → sees stale value briefly (~200ms until sync completes)
- Mitigation: Always sync on screen open, show loading indicator, cache last known value

⚠️ **Transition Latency:**
- User opens white balance screen → ~200ms delay before values populate
- Mitigation: Cache + loading indicator, acceptable for non-critical params

⚠️ **Supersedes ADR-008 Alternative 3:**
- ADR-008 rejected "Variable Rate" as premature optimization for status broadcast
- ADR-016 accepts it due to **new context:** 19+ parameters (vs. 3 in ADR-008)
- Bandwidth problem now real, not premature optimization

---

## Implementation Plan

### Phase 1: Air-Side Adaptive Sync Manager

**File:** `sbc/src/sync/adaptive_sync_manager.cpp`

**Responsibilities:**
- Track sync tier for each parameter (exposure/health/extended)
- Accept sync rate commands from Ground-Side (5Hz/1Hz/on-demand)
- Manage polling timers per parameter tier

**API:**
```cpp
class AdaptiveSyncManager {
public:
    enum SyncTier { EXPOSURE, HEALTH, EXTENDED };
    enum SyncRate { RATE_5HZ, RATE_1HZ, ON_DEMAND };

    void setSyncRate(SyncTier tier, SyncRate rate);
    void requestOnDemand(const std::string& parameter);
    void registerParameter(const std::string& param, SyncTier tier);
};
```

**Responsibilities:**
1. Manage three timer threads (exposure 5Hz/1Hz, health 1Hz, on-demand queue)
2. Accept sync rate changes via TCP command from Ground-Side
3. Poll PropertyLoader at appropriate intervals
4. Broadcast updates via UDP status (existing mechanism)

---

### Phase 2: Ground-Side UI State Tracking

**File:** `android/app/src/main/java/com/dpm/viewmodel/SyncRateController.kt`

**Responsibilities:**
- Track which UI screens are visible
- Send sync rate commands to Air-Side
- Prevent rate thrashing (debounce < 2 seconds)

**API:**
```kotlin
class SyncRateController {
    enum class UiState { EXPOSURE_VISIBLE, EXPOSURE_HIDDEN }

    fun updateUiState(state: UiState) {
        val rate = when(state) {
            EXPOSURE_VISIBLE -> SyncRate.RATE_5HZ
            EXPOSURE_HIDDEN -> SyncRate.RATE_1HZ
        }
        airSideConnection.setSyncRate(SyncTier.EXPOSURE, rate)
    }

    suspend fun requestExtendedParameter(param: String): String {
        return airSideConnection.requestOnDemand(param)
    }
}
```

**UI Integration:**
```kotlin
@Composable
fun CameraScreen() {
    val syncController = remember { SyncRateController() }

    DisposableEffect(Unit) {
        syncController.updateUiState(UiState.EXPOSURE_VISIBLE)
        onDispose {
            syncController.updateUiState(UiState.EXPOSURE_HIDDEN)
        }
    }

    // Camera UI...
}
```

---

### Phase 3: Extended Parameter On-Demand Screens

**File:** `android/app/src/main/java/com/dpm/ui/WhiteBalanceScreen.kt`

**Pattern:**
```kotlin
@Composable
fun WhiteBalanceScreen() {
    val viewModel: WhiteBalanceViewModel = viewModel()
    val whiteBalance by viewModel.whiteBalance.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadWhiteBalance() // Triggers on-demand sync
    }

    // UI displays cached value immediately, updates when sync completes
}

class WhiteBalanceViewModel {
    suspend fun loadWhiteBalance() {
        // Show cached (may be stale)
        _whiteBalance.value = cache.getWhiteBalance()

        // Request fresh value
        val current = syncController.requestExtendedParameter("white_balance")

        // Update with fresh value
        _whiteBalance.value = current
        cache.setWhiteBalance(current)
    }
}
```

---

### Phase 4: Protocol Updates

**File:** `docs/protocol/commands.json`

**New Commands:**
```json
{
  "command": "set_sync_rate",
  "parameters": {
    "tier": "exposure|health|extended",
    "rate": "5hz|1hz|on_demand"
  }
}

{
  "command": "request_parameter",
  "parameters": {
    "parameter": "white_balance|focus_mode|..."
  },
  "response": {
    "parameter": "white_balance",
    "value": "auto"
  }
}
```

---

## Performance Metrics

### Bandwidth Analysis

**Current (3 parameters @ 5Hz):**
- 15 param reads/sec
- ~0.5KB/sec USB traffic

**Future Without Adaptive Sync (19 parameters @ 5Hz):**
- 95 param reads/sec
- ~3KB/sec USB traffic
- **Risk:** USB bandwidth overflow, camera distraction

**Future With Adaptive Sync:**

**Active Monitoring (Exposure UI visible):**
- Exposure: 3 params @ 5Hz = 15 reads/sec
- Health: 2 params @ 1Hz = 2 reads/sec
- **Total: 17 reads/sec (~0.6KB/sec)**

**Background (Exposure UI hidden):**
- Exposure: 3 params @ 1Hz = 3 reads/sec
- Health: 2 params @ 1Hz = 2 reads/sec
- **Total: 5 reads/sec (~0.2KB/sec)**

**Savings: 80-94% bandwidth reduction**

---

## Validation

### Success Criteria

**Performance:**
- [ ] USB traffic reduced by >80% in background mode
- [ ] Camera responsiveness maintained (no lag in image capture)
- [ ] Exposure UI updates feel real-time (5Hz when visible)

**Functionality:**
- [ ] Exposure values update in <250ms when UI visible
- [ ] Battery/SD status monitored continuously
- [ ] Extended params load in <300ms when screen opened
- [ ] Sync rate transitions smooth (no glitches)

**Reliability:**
- [ ] No parameter drift (cached values accurate)
- [ ] No race conditions on rate transitions
- [ ] Handles rapid UI switching gracefully

---

## Related Decisions

**Supersedes:**
- **ADR-008 Alternative 3:** "Variable Rate" rejected in 2024-10 as premature optimization
  - **New Context:** 3 parameters (2024) → 19+ parameters (2025) = bandwidth problem now real
  - **Decision:** Accept variable rate for new context

**Extends:**
- **ADR-002:** Specification-First Property Management (PropertyLoader pattern still used)
- **ADR-008:** UDP Status Broadcast Rate (5Hz broadcast maintained when UI visible)

**Future Evolution:**
- If Sony SDK adds change notification support → migrate to event-driven (Alternative 2)
- Adaptive sync can coexist with events (use events when available, polling as fallback)

---

## References

**Architecture Views:**
- `view-integration.md` Section 5: Integration Patterns (Telemetry Broadcast)
- `view-data.md` Section 4: Data Flow (Camera Property Sync)
- `view-logical.md` Section 4.2: Air-Side Components (PropertyLoader)

**Related ADRs:**
- ADR-002: Specification-First Property Management
- ADR-008: UDP Status Broadcast Rate
- ADR-010: PropertyLoader Pattern

**Implementation Issues:**
- Air-Side: Issue #67 - Implement Adaptive Sync Manager for USB Traffic Management
- Ground-Side: Issue #68 - Implement UI State Tracking and Sync Rate Control

---

## Lessons Learned Integration

**From:** `LESSONS_LEARNED.md`

**Relevant Lessons:**
- **Issue #22 (2025-11-05):** PropertyLoader sync bugs
  - Learning: Air/Ground property sync critical, must be reliable
  - Application: Adaptive sync must maintain PropertyLoader contract

- **Issue #33 (2025-11-07):** Docker USB passthrough
  - Learning: USB communication fragile, minimize traffic
  - Application: Adaptive sync reduces USB traffic by 80-94%

---

**Author:** Claude Code (Architecture Review)
**Approved:** [Pending user approval]
**Next Review:** After Phase 1 implementation (Air-Side adaptive sync manager)
