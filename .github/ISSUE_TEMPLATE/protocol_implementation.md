---
name: Protocol Implementation
about: Track implementation of a protocol command or camera property
title: '[PROTOCOL] Implement '
labels: protocol
assignees: ''

---

## WHO Tag (REQUIRED)
**WHO:** [CC-Air-Side | CC-Ground-Side | CC-Dev-Tools | CC-Project-Manager | User (name)]

## Historical Search (REQUIRED)
**Did you search for similar protocol implementations?**
- [ ] Yes - Found similar: #___, #___
- [ ] Yes - No similar implementations found
- [ ] No - Need to perform search

**Search command used:**
```bash
.github/scripts/search-history.sh "protocol_name"
```

**Related historical issues:**
- Issue #___ - [Brief description of relevance]

## ⚠️ Protocol Compliance Requirements (PM RULE 11)

**CRITICAL: Before ANY implementation, verify:**
- [ ] **Protocol file updated FIRST** (update protocol/*.json BEFORE writing code)
- [ ] **All domains enforce at runtime** (no hardcoded values)
- [ ] **Cross-domain compatibility verified** (all domains use same protocol)

**See:** `.claude/PM_RULES_CRITICAL.md` - PM RULE 11: Protocol Enforcement & Cross-Domain Compliance

---

## Protocol Specification
**Protocol file:**
- [ ] `protocol/commands.json`
- [ ] `protocol/camera_properties.json`
- [ ] `protocol/log_contexts.json` *(if adding/modifying log contexts)*

**Command/Property/Context name:** `___`

**Current specification:**
```json
[Paste relevant section from protocol/*.json]
```

**Current implementation status:**
```bash
# Check command implementation status
cat protocol/commands.json | jq '.commands.COMMAND_NAME.implemented'

# Output:
# {
#   "air_side": false,
#   "ground_side": false
# }
```

**Protocol Change Workflow:**
1. [ ] **STEP 1:** Update protocol/*.json file FIRST
2. [ ] **STEP 2:** Create [PROTOCOL] tagged commit
3. [ ] **STEP 3:** Update ALL domains to match protocol
4. [ ] **STEP 4:** Test cross-domain compatibility

## Implementation Requirements

### Air-Side (C++)
**Status:**
- [ ] Not started
- [ ] In progress
- [ ] Complete
- [ ] Not required for this protocol item

**Required changes:**
- [ ] `sbc/src/camera/camera_sony.cpp` - Sony SDK integration
- [ ] `sbc/src/camera/camera_sony.h` - Header definitions
- [ ] `sbc/src/network/messages.h` - Message structure
- [ ] `sbc/src/network/status_broadcaster.cpp` - Status reporting
- [ ] `sbc/src/command_processor.cpp` - Command handling
- [ ] Other: ___

**Sony SDK API:**
```cpp
// Sony SDK function to use:
// Example: camera->SetShutterSpeed(value)
```

**Implementation notes:**
[Any specific Sony SDK considerations, threading requirements, etc.]

### Ground-Side (Android/Kotlin)
**Status:**
- [ ] Not started
- [ ] In progress
- [ ] Complete
- [ ] Not required for this protocol item

**Required changes:**
- [ ] `android/app/src/main/java/protocol/ProtocolMessages.kt` - Message parsing
- [ ] `android/app/src/main/java/viewmodel/CameraViewModel.kt` - ViewModel updates
- [ ] `android/app/src/main/java/ui/CameraScreen.kt` - UI elements
- [ ] `android/app/src/main/java/network/NetworkClient.kt` - Network handling
- [ ] Other: ___

**UI requirements:**
- [ ] Display only (read-only)
- [ ] User control (input/buttons)
- [ ] Both display and control

**UI mockup/description:**
[Describe or sketch the UI changes needed]

### Dev-Tools (Python)
**Status:**
- [ ] Not started
- [ ] In progress
- [ ] Complete
- [ ] Not required for this protocol item

**Required changes:**
- [ ] `SystemTools/main.py` - Tab integration
- [ ] `SystemTools/tabs/camera_control_tab.py` - Control UI
- [ ] `SystemTools/network/protocol.py` - Protocol definitions
- [ ] Other: ___

**Testing capability:**
- [ ] Can test without camera (mock mode)
- [ ] Requires camera connection

## Implementation Order
**Which domain should implement first?**

**Recommended order:**
1. [ ] Air-Side first (data source)
2. [ ] Ground-Side first (UI/UX testing)
3. [ ] Parallel implementation (independent)

**Rationale:**
[Why this order?]

**Dependencies:**
- Air-Side depends on: [Sony SDK functionality, etc.]
- Ground-Side depends on: [Air-Side data format, etc.]

## Testing Strategy

### Air-Side Testing
**How to verify Air-Side implementation:**
```bash
# Check Air-Side logs for implementation
docker logs payload_manager | grep "protocol_name"
```

**Expected Air-Side behavior:**
- [What should appear in logs]
- [What should be sent via UDP/TCP]

### Ground-Side Testing
**How to verify Ground-Side implementation:**
```bash
# Check Ground-Side logs
adb logcat -s NetworkClient | grep "protocol_name"
```

**Expected Ground-Side behavior:**
- [UI should display...]
- [User interaction should...]

### Integration Testing
**Full end-to-end test:**
1. [Step 1: User action on Ground-Side]
2. [Step 2: Command sent to Air-Side]
3. [Step 3: Air-Side executes]
4. [Step 4: Status returned to Ground-Side]
5. [Expected result: UI updates]

## Protocol Sync Update
**After implementation, update protocol/*.json:**
```json
{
  "implemented": {
    "air_side": true,     // Set to true when Air-Side complete
    "ground_side": true   // Set to true when Ground-Side complete
  }
}
```

**Command to verify sync:**
```bash
# Check unimplemented items
cat protocol/commands.json | jq '.commands | to_entries[] | select(.value.implemented.air_side == false or .value.implemented.ground_side == false) | .key'
```

## Acceptance Criteria
**Implementation is complete when:**
- [ ] Air-Side: Command/property implemented and tested
- [ ] Ground-Side: UI updated and tested
- [ ] Dev-Tools: Monitoring/control added (if applicable)
- [ ] Protocol sync: `implemented` flags updated in protocol/*.json
- [ ] Integration test: End-to-end workflow verified
- [ ] Documentation: PROGRESS_AND_TODO.md updated in relevant domains
- [ ] Logs: Proper error handling and logging in place

### ✅ Protocol Compliance Verification (PM RULE 11)
**Run these checks BEFORE closing issue:**

```bash
# 1. Verify no hardcoded protocol values
# Check Air-Side uses LogContext enum (if log-related)
ssh dpm@10.0.1.53 "grep -r 'LOG_' ~/DPM-V2/sbc/src | grep -v 'LogContext::' | wc -l"
# Expected: 0

# 2. Verify SystemTools uses protocol loader (if log-related)
grep -r 'logger\.\(debug\|info\)(' SystemTools/ --include="*.py" | \
  grep -v '\[COMMAND\]' | grep -v '\[NETWORK\]' | grep -v '\[DISCOVERY\]' | \
  grep -v '\[CONFIG\]' | grep -v '\[SYSTEM\]' | grep -v '\[HEALTH\]' | \
  grep -v '\[CAMERA\]' | grep -v '\[STORAGE\]' | grep -v '\[SYNC\]' | \
  grep -v '\[UI\]' | wc -l
# Expected: 0 (after Issue #162 fixed)

# 3. Verify Ground-Side uses StructuredLogger (if log-related)
grep -r 'Log\.\(d\|i\|w\|e\)(' android/app/src --include="*.kt" | \
  grep -v "StructuredLogger.kt" | grep -v "DPMApplication.kt" | \
  grep -v "logging/" | wc -l
# Expected: 0 (after Issue #164 fixed)

# 4. Verify cross-domain protocol sync
# All domains should have matching protocol definitions
diff <(ssh dpm@10.0.1.53 "cat ~/DPM-V2/protocol/log_contexts.json | jq -S .contexts") \
     <(cat protocol/log_contexts.json | jq -S .contexts)
# Expected: No differences
```

**Checklist:**
- [ ] No hardcoded protocol values found
- [ ] All domains enforce protocol at runtime
- [ ] Cross-domain compatibility verified
- [ ] Protocol compliance checks pass (0 violations)

## Known Issues / Edge Cases
**Potential problems:**
- [Issue 1]: [How to handle]
- [Issue 2]: [How to handle]

**Sony SDK limitations:**
- [Any known Sony SDK quirks or limitations]

## Documentation Requirements
**Update after implementation:**
- [ ] `sbc/docs/PROGRESS_AND_TODO.md` - Air-Side status
- [ ] `android/docs/PROGRESS_AND_TODO.md` - Ground-Side status
- [ ] `SystemTools/PROGRESS_AND_TODO.md` - Dev-Tools status (if applicable)
- [ ] `protocol/commands.json` or `camera_properties.json` - implemented flags

## Cross-Domain Handoff
**If implemented in stages:**

**After Air-Side completes:**
```markdown
**WHO:** CC-Air-Side

Air-Side implementation complete:
- File changes: [list files]
- Message format: [describe UDP/TCP message structure]
- Testing: [results]

Ground-Side TODO:
- Parse message field: `field_name`
- Update UI to display: [what to display]
- See: [documentation reference]
```

**After Ground-Side completes:**
```markdown
**WHO:** CC-Ground-Side

Ground-Side implementation complete:
- File changes: [list files]
- UI changes: [describe]
- Testing: [results]

Integration test with Air-Side: [results]
```

## Related Issues
**Related to:**
- Blocks: #___ (must complete before...)
- Blocked by: #___ (depends on...)
- Related: #___ (similar implementation)

---
**Remember:** Use WHO tags in all comments on this issue!
