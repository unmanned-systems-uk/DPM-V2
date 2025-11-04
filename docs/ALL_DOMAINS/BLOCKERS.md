# Cross-Domain Blockers & Issues
*Critical issues affecting multiple domains*
*Last Updated: 2025-11-04*

## 🚨 Critical Blockers (P0)

### 1. Focus Distance Readback Failure
**Severity**: 🔴 HIGH
**Domains Affected**: Air-Side, Ground-Side
**Status**: 🔄 Under Investigation

#### Description
Focus distance cannot be read from Sony camera, causing UI elements to show no data.

#### Technical Details
- **Air-Side**: `GetDeviceProperty(CrDeviceProperty_FocusDistance)` returns error
- **Ground-Side**: `FocusDistanceOverlay` receives null in UDP status
- **Expected**: Distance in meters (e.g., "5.2m" or "∞")
- **Actual**: null/undefined

#### Impact
- Users cannot see current focus distance
- Manual focus operation is "blind"
- Reduces professional usability

#### Investigation Status
- [x] Confirmed SDK call fails
- [x] Checked camera mode dependencies
- [ ] Test with different camera models
- [ ] Contact Sony support
- [ ] Try alternative SDK methods

#### Workarounds
- None currently available

#### Action Items
| Task | Owner | ETA | Status |
|------|-------|-----|--------|
| Test alternative SDK calls | Air-Side | Nov 5 | 🔄 |
| Check Sony documentation | Air-Side | Nov 5 | 🔄 |
| Contact Sony support | PM | Nov 6 | ⏳ |

---

### 2. Auto-Focus Hold in Manual Focus Mode
**Severity**: 🟡 MEDIUM
**Domains Affected**: Air-Side, Ground-Side
**Status**: 🔄 Investigating

#### Description
AF Hold button doesn't work when camera is in Manual Focus mode.

#### Technical Details
- **Command sent**: `camera.auto_focus_hold` with `hold: true`
- **Air-Side**: SDK accepts command but no effect
- **Camera behavior**: No focus adjustment occurs
- **Works in**: AF-S, AF-C modes
- **Fails in**: MF mode

#### Impact
- AF assist unavailable in manual mode
- Reduces focus accuracy
- User frustration

#### Investigation Status
- [x] Confirmed command reaches camera
- [x] Verified works in AF modes
- [ ] Check camera firmware version
- [ ] Test on different camera models
- [ ] Review Sony SDK limitations

#### Workarounds
- Switch to AF-S mode temporarily
- Use focus peaking on camera

#### Action Items
| Task | Owner | ETA | Status |
|------|-------|-----|--------|
| Test with camera firmware update | Air-Side | Nov 6 | ⏳ |
| Document SDK limitations | Air-Side | Nov 5 | 🔄 |
| Add mode detection | Ground-Side | Nov 7 | ⏳ |

---

## ⚠️ Major Issues (P1)

### 3. H16 Hardware Testing Delayed
**Severity**: 🟡 MEDIUM
**Domains Affected**: Ground-Side
**Status**: ⏸️ Blocked

#### Description
Cannot complete end-to-end testing without H16 hardware access.

#### Impact
- Performance metrics unknown
- Touch responsiveness untested
- Network stability unverified

#### Dependencies
- H16 device availability
- Network configuration
- Test environment setup

#### Action Items
| Task | Owner | ETA | Status |
|------|-------|-----|--------|
| Acquire H16 device | PM | Nov 8 | ⏳ |
| Setup test network | IT | Nov 9 | ⏳ |
| Run test suite | QA | Nov 10 | ⏳ |

---

### 4. Property Availability Errors
**Severity**: 🟡 MEDIUM
**Domains Affected**: Air-Side
**Status**: 🔄 Investigating

#### Description
Some camera properties return error 0x8402 (not available) in certain modes.

#### Examples
- White balance temperature in Auto WB mode
- Manual focus distance in AF modes
- Shutter speed in Auto exposure

#### Impact
- Confusing error messages
- UI shows unavailable controls
- User experience degraded

#### Proposed Solution
- Implement mode-aware property queries
- Hide unavailable controls dynamically
- Cache last known values

---

## 🔧 Minor Issues (P2)

### 5. Memory Leak in Long Sessions
**Domains**: Air-Side
**Impact**: Low - requires 48+ hour sessions
**Status**: Monitoring

### 6. UDP Packet Loss at High Rates
**Domains**: All
**Impact**: Low - <0.1% loss rate
**Status**: Acceptable

### 7. Video Stream Reconnection
**Domains**: Ground-Side
**Impact**: Low - manual reconnect works
**Status**: Enhancement planned

---

## 📊 Blocker Metrics

### Issue Resolution Time
| Priority | Target SLA | Current Avg | Status |
|----------|------------|-------------|--------|
| P0 Critical | 24 hours | 72 hours | ❌ |
| P1 Major | 3 days | 5 days | ⚠️ |
| P2 Minor | 1 week | 1 week | ✅ |

### Open Issues by Domain
| Domain | P0 | P1 | P2 | Total |
|--------|-----|-----|-----|-------|
| Air-Side | 2 | 1 | 1 | 4 |
| Ground-Side | 2 | 1 | 1 | 4 |
| Dev-Side | 0 | 0 | 0 | 0 |
| **Total** | **2** | **2** | **3** | **7** |

---

## 🔄 Resolution Process

### Escalation Path
1. **Developer** identifies blocker
2. **Domain Lead** assesses impact
3. **PM** prioritizes resolution
4. **Team** collaborates on fix
5. **QA** validates resolution

### Communication
- **Daily**: Standup blocker review
- **Immediate**: Slack for new P0 issues
- **Weekly**: Blocker review meeting

---

## 📝 Historical Blockers (Resolved)

### Previously Resolved
1. ✅ **libxml2 ABI Incompatibility** - Fixed with Docker (Oct 24)
2. ✅ **Heartbeat Protocol Mismatch** - Fixed with v1.1.0 (Oct 29)
3. ✅ **Client Identification** - Fixed with client_id (Oct 29)
4. ✅ **Multi-client UDP** - Fixed with dual-port (Oct 30)
5. ✅ **Camera Connection Error 0x8208** - Fixed USB buffer (Oct 24)

### Lessons Learned
- Docker solves dependency issues
- Protocol versioning prevents breaking changes
- Early integration testing catches issues
- Sony SDK has undocumented limitations

---

## 🎯 Blocker Prevention

### Strategies
1. **Daily Integration Tests** - Catch issues early
2. **Protocol Versioning** - Prevent breaking changes
3. **Mode-Aware Code** - Handle camera states
4. **Error Recovery** - Graceful degradation
5. **Documentation** - Track known limitations

### Risk Mitigation
- Always have rollback plan
- Test on multiple devices
- Maintain compatibility matrix
- Document workarounds

---
*For integration details, see INTEGRATION_POINTS.md*
*For sync status, see SYNC_STATUS.md*
*For master status, see MASTER_STATUS.md*