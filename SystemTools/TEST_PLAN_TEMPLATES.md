# SystemTools Test Plan Templates

**Version:** 1.0
**Created:** November 7, 2025
**Purpose:** Standardized test plans for SystemTools diagnostic features

---

## Template 1: Connection Feature Test

```markdown
## Test Plan: [Feature Name] Connection

**Issue:** #[number]
**Component:** Connection Management
**Environment:** SystemTools + Air-Side (10.0.1.53) + H16 (10.0.1.92)

### Pre-Test Setup
- [ ] SystemTools running (python main.py)
- [ ] Air-Side powered on and reachable
- [ ] H16 powered on and ADB-enabled
- [ ] Network connectivity verified

### Connection Establishment Tests
- [ ] Connection initiated without errors
- [ ] Connection indicator turns green
- [ ] Connection log shows success message
- [ ] Connection completes within 5 seconds

### Data Transfer Tests
- [ ] Commands sent successfully
- [ ] Responses received correctly
- [ ] Data format matches protocol
- [ ] No data corruption

### Error Handling Tests
- [ ] Handles device offline gracefully
- [ ] Displays clear error messages
- [ ] Allows retry after failure
- [ ] Does not crash on connection loss

### Disconnection Tests
- [ ] Disconnect button works
- [ ] Connection indicator turns gray
- [ ] Resources cleaned up properly
- [ ] Can reconnect after disconnect

### Pass/Fail Criteria
- **PASS:** All items checked, connects reliably
- **FAIL:** Cannot establish connection or crashes
```

---

## Template 2: UI Tab Feature Test

```markdown
## Test Plan: [Tab Name] Tab

**Issue:** #[number]
**Component:** User Interface
**Environment:** SystemTools standalone

### Tab Loading Tests
- [ ] Tab appears in notebook
- [ ] Tab title correct
- [ ] Tab loads without errors
- [ ] No console errors on load

### UI Element Tests
- [ ] All buttons visible and labeled
- [ ] All text readable
- [ ] All indicators render correctly
- [ ] Layout looks professional

### Functionality Tests
- [ ] [Primary feature 1] works
- [ ] [Primary feature 2] works
- [ ] [Primary feature 3] works
- [ ] All controls respond to clicks

### Integration Tests
- [ ] Does not affect other tabs
- [ ] Shares data correctly with other components
- [ ] Respects global settings
- [ ] Updates in real-time when needed

### Usability Tests
- [ ] Feature is intuitive to use
- [ ] Help/tooltips available
- [ ] Error messages clear
- [ ] Workflow makes sense

### Pass/Fail Criteria
- **PASS:** Tab functional, no crashes, intuitive
- **FAIL:** Crashes, major UI bugs, unusable
```

---

## Template 3: Network Protocol Test

```markdown
## Test Plan: [Protocol Feature] Implementation

**Issue:** #[number]
**Component:** Network Protocol
**Environment:** SystemTools + Air-Side + Protocol Inspector

### Protocol Format Tests
- [ ] Messages match protocol/*.json specs
- [ ] All required fields present
- [ ] Field types correct (string/int/bool)
- [ ] JSON valid and parseable

### Send Tests
- [ ] Commands sent successfully
- [ ] Sequence IDs increment correctly
- [ ] Timestamps accurate
- [ ] Payload format correct

### Receive Tests
- [ ] Responses received within timeout
- [ ] Response format validated
- [ ] Response content correct
- [ ] Errors handled properly

### Protocol Inspector Tests
- [ ] Messages appear in Protocol Inspector
- [ ] Message type detected correctly
- [ ] JSON displayed with formatting
- [ ] Search/filter works

### Error Handling Tests
- [ ] Invalid JSON rejected
- [ ] Missing fields detected
- [ ] Timeout errors caught
- [ ] Error messages informative

### Pass/Fail Criteria
- **PASS:** Protocol compliant, reliable communication
- **FAIL:** Protocol violations, unreliable, crashes
```

---

## Template 4: ADB Diagnostic Feature Test

```markdown
## Test Plan: [ADB Feature Name]

**Issue:** #[number]
**Component:** ADB Integration
**Environment:** SystemTools + H16 (10.0.1.92:5555)

### ADB Setup Tests
- [ ] ADB installed and in PATH
- [ ] H16 reachable on network
- [ ] ADB connect succeeds
- [ ] Device appears in `adb devices`

### Feature Tests
- [ ] [Feature function 1] works
- [ ] [Feature function 2] works
- [ ] [Feature function 3] works
- [ ] Output displayed correctly

### H16 Command Tests
- [ ] Shell commands execute
- [ ] Output captured correctly
- [ ] Exit codes handled
- [ ] Timeout handled (if long-running)

### Error Tests
- [ ] ADB not found - shows clear error
- [ ] H16 not connected - shows clear error
- [ ] Network timeout - handled gracefully
- [ ] Invalid command - handled gracefully

### Disconnect Tests
- [ ] Can disconnect from H16
- [ ] Can reconnect after disconnect
- [ ] Multiple connect/disconnect cycles work
- [ ] No resource leaks

### Pass/Fail Criteria
- **PASS:** ADB functions work reliably
- **FAIL:** Cannot connect, crashes, hangs
```

---

## Template 5: SSH Diagnostic Feature Test

```markdown
## Test Plan: [SSH Feature Name]

**Issue:** #[number]
**Component:** SSH Integration
**Environment:** SystemTools + Air-Side (10.0.1.53:22)

### SSH Setup Tests
- [ ] Air-Side SSH server running
- [ ] Credentials correct (dpm/2350)
- [ ] SSH connection succeeds
- [ ] Authentication works

### Feature Tests
- [ ] [Feature function 1] works
- [ ] [Feature function 2] works
- [ ] [Feature function 3] works
- [ ] Output streamed correctly

### Docker Command Tests
- [ ] Can access Docker
- [ ] Can view logs
- [ ] Can check container status
- [ ] Commands execute remotely

### Error Tests
- [ ] SSH not available - clear error
- [ ] Air-Side unreachable - clear error
- [ ] Authentication failure - clear error
- [ ] Connection loss - handled gracefully

### Security Tests
- [ ] Password not logged in plain text
- [ ] Connection encrypted
- [ ] No credential leaks
- [ ] Session cleanup on disconnect

### Pass/Fail Criteria
- **PASS:** SSH functions work securely and reliably
- **FAIL:** Cannot connect, security issues, crashes
```

---

## Template 6: Data Display Feature Test

```markdown
## Test Plan: [Display Feature Name]

**Issue:** #[number]
**Component:** Data Display/Visualization
**Environment:** SystemTools + data source

### Display Tests
- [ ] Data displays correctly
- [ ] Format is readable
- [ ] Colors/indicators appropriate
- [ ] Updates in real-time (if applicable)

### Data Accuracy Tests
- [ ] Values match source data
- [ ] Units displayed correctly
- [ ] Calculations correct (if any)
- [ ] No data loss or corruption

### Performance Tests
- [ ] Handles large data sets
- [ ] Updates smoothly (no flicker)
- [ ] Does not slow down application
- [ ] Memory usage reasonable

### Interaction Tests
- [ ] User can interact with display
- [ ] Selection works (if applicable)
- [ ] Scroll/pan works (if applicable)
- [ ] Export works (if applicable)

### Edge Case Tests
- [ ] Handles empty data
- [ ] Handles very large values
- [ ] Handles very small values
- [ ] Handles invalid data

### Pass/Fail Criteria
- **PASS:** Display accurate, performant, usable
- **FAIL:** Incorrect data, crashes, unusable
```

---

## Template 7: Configuration Feature Test

```markdown
## Test Plan: [Configuration Feature]

**Issue:** #[number]
**Component:** Configuration Management
**Environment:** SystemTools

### Save Tests
- [ ] Settings save to config.json
- [ ] File format valid JSON
- [ ] All settings persisted
- [ ] File permissions correct

### Load Tests
- [ ] Settings load on startup
- [ ] Default values used if missing
- [ ] Invalid values handled
- [ ] Corrupt file handled

### UI Tests
- [ ] Configuration UI displays settings
- [ ] User can modify settings
- [ ] Changes apply immediately
- [ ] Reset to defaults works

### Validation Tests
- [ ] Invalid IP addresses rejected
- [ ] Port numbers in valid range (1-65535)
- [ ] Required fields enforced
- [ ] Helpful error messages

### Integration Tests
- [ ] Other components use new settings
- [ ] Settings change behavior correctly
- [ ] No restart needed (if hot-reload)
- [ ] Settings sync across tabs

### Pass/Fail Criteria
- **PASS:** Settings save/load reliably, validation works
- **FAIL:** Settings lost, corrupted, or crash app
```

---

## Template 8: GitHub Integration Feature Test

```markdown
## Test Plan: GitHub Integration Feature

**Issue:** #[number]
**Component:** GitHub Integration Tab
**Environment:** SystemTools + GitHub API

### Authentication Tests
- [ ] Token entry works
- [ ] Token validation works
- [ ] Invalid token - clear error
- [ ] Unauthenticated mode works (read-only)

### Issue List Tests
- [ ] Issues load from repository
- [ ] Issues display correctly
- [ ] Filter by state works (open/closed/all)
- [ ] Filter by label works
- [ ] Search works

### Issue View Tests
- [ ] Issue details display correctly
- [ ] Comments load and display
- [ ] Markdown rendering works
- [ ] Timestamps display correctly

### Issue Create Tests (Authenticated)
- [ ] Create form validates input
- [ ] Title required, enforced
- [ ] Labels selectable
- [ ] Issue created successfully
- [ ] New issue appears in list

### Comment Tests (Authenticated)
- [ ] Can add comment to issue
- [ ] Comment appears after submission
- [ ] WHO tag automatically added
- [ ] Markdown preview works

### API Rate Limit Tests
- [ ] Rate limit displayed
- [ ] Warning shown when low
- [ ] Graceful handling when exceeded
- [ ] Authenticated = higher limit

### Error Tests
- [ ] Network error - clear message
- [ ] API error - clear message
- [ ] Invalid response - handled
- [ ] Timeout - handled

### Pass/Fail Criteria
- **PASS:** GitHub features work, errors handled
- **FAIL:** Crashes, data loss, cannot use features
```

---

## Quick Test Checklist

For any SystemTools feature, always test:

### Basic Functionality
- [ ] Feature works as described
- [ ] No errors in console
- [ ] No crashes
- [ ] Performance acceptable

### Error Handling
- [ ] Handles missing dependencies
- [ ] Handles network errors
- [ ] Handles invalid input
- [ ] Shows helpful error messages

### Integration
- [ ] Works with other tabs/features
- [ ] Respects configuration
- [ ] Does not break existing features
- [ ] Logs appropriately

### Usability
- [ ] Intuitive to use
- [ ] Clear instructions/labels
- [ ] Responsive UI
- [ ] Professional appearance

---

## Creating a Custom Test Plan

1. Copy appropriate template above
2. Replace [placeholders] with specific details
3. Add feature-specific test items
4. Include environment requirements
5. Define clear pass/fail criteria
6. Post to GitHub issue with [CC-SystemTools] tag

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
