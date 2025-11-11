# Quick Documentation Update Guide

**Purpose:** Fast reference for developers - "I changed X, what documentation do I update?"

---

## Table of Contents

1. [Quick Decision Tree](#quick-decision-tree)
2. [Common Scenarios](#common-scenarios)
3. [Domain-Specific Updates](#domain-specific-updates)
4. [Validation Checklist](#validation-checklist)
5. [Getting Help](#getting-help)

---

## Quick Decision Tree

```
Did you change code?
├─ YES → Continue below
└─ NO → Only doc changes needed

Which domain did you change?
├─ Air-Side (sbc/) → See "Air-Side Updates"
├─ Ground-Side (android/) → See "Ground-Side Updates"
├─ Protocol (docs/protocol/) → See "Protocol Updates" ⚠️ CRITICAL
├─ Tools (SystemTools/) → See "Tools Updates"
└─ Documentation only → Update cross-references, validate links

Did you add/remove components?
├─ YES → Update C4 diagram + view-logical.md + traceability matrix
└─ NO → Update relevant view documentation only

Did you make an architectural decision?
├─ YES → Create/update ADR
└─ NO → Skip ADR

Did you change protocol or integration?
├─ YES → Update view-integration.md + PropertyLoader (C++ AND Kotlin)
└─ NO → Skip integration docs
```

---

## Common Scenarios

### Scenario 1: "I added a new component in Air-Side"

**Example:** New `GimbalService` class in `sbc/src/gimbal/`

**Update:**
1. **Code comments** - Add C++ header comments to new class
2. **view-logical.md** - Add component to Section 4.2.3 table
   ```markdown
   | Component | Responsibility | Dependencies |
   |-----------|----------------|--------------|
   | GimbalService | Controls gimbal pan/tilt | CameraService, NetworkService |
   ```
3. **c4-level3-air-side-components.puml** - Add component box with relationships
   ```plantuml
   Component(gimbal, "GimbalService", "C++", "Controls gimbal pan/tilt")
   Rel(gimbal, camera, "Uses", "Get camera orientation")
   ```
4. **SAD Section 8.3** - Add row to Component → Code traceability matrix
   ```markdown
   | GimbalService | sbc/src/gimbal/gimbal_service.cpp | ~400 | C++17 |
   ```
5. **Consider ADR** - If gimbal control introduces new pattern, create ADR

**Time:** ~15-20 minutes
**Example PR:** _[To be added after first implementation]_

---

### Scenario 2: "I changed the protocol (added/modified property)"

**Example:** Added `white_balance` property to `camera_properties.json`

**Update:**
1. **docs/protocol/camera_properties.json** - Add new property specification
   ```json
   {
     "name": "white_balance",
     "type": "enum",
     "values": ["auto", "daylight", "cloudy", "tungsten"],
     "sdk_mapping": {...}
   }
   ```
2. **PropertyLoader (C++)** - Update `sbc/src/property_loader.cpp`
   - Load new property from JSON
   - Implement validation logic
   - Add SDK mapping functions
3. **PropertyLoader (Kotlin)** - Update `android/.../PropertyLoader.kt`
   - Load new property from JSON
   - Implement validation logic
   - Add display mapping functions
4. **view-integration.md** - Update Section 5 (protocol patterns)
   - Add property to property table
   - Document any special handling
5. **ADR-002** - Update "Consequences" section if new trade-offs discovered
6. **Test both domains** - Verify Air-Side and Ground-Side sync correctly

**Time:** ~30-45 minutes (includes testing both domains)
**⚠️ CRITICAL:** Protocol changes affect TWO domains - must update both!
**Example PR:** _[Reference Issue #22 - manual focus sync bug]_

---

### Scenario 3: "I made an architectural decision"

**Example:** Decided to use gRPC instead of JSON for future protocol

**Decision Criteria:**
✅ Affects >1 component → YES, create ADR
✅ Long-term impact (>6 months) → YES, create ADR
✅ Evaluated 2+ alternatives → YES, create ADR
✅ New technology introduced → YES, create ADR

**Create New ADR:**
1. Copy template from `docs/architecture/adr/README.md`
2. Number it sequentially (e.g., ADR-016)
3. Fill out sections:
   - **Context:** Why is this decision needed? (performance issues, etc.)
   - **Decision:** What did you decide? (gRPC for protocol)
   - **Alternatives Considered:**
     - Alternative 1: JSON (current - human-readable but verbose)
     - Alternative 2: Protocol Buffers (not gRPC, just serialization)
     - Alternative 3: MessagePack (binary JSON, smaller but still not typed)
   - **Consequences:**
     - ✅ Benefits: Type safety, performance, streaming support
     - ⚠️ Trade-offs: Not human-readable, build complexity, team learning curve
4. **Update view-integration.md** - Reference new ADR
5. **Update SAD Section 5** - Add summary of new ADR

**Time:** ~45-60 minutes for comprehensive ADR
**Template:** `docs/architecture/adr/README.md` (bottom of file)
**Examples:** See `docs/architecture/adr/ADR-*.md`

---

### Scenario 4: "I fixed a bug (no architectural change)"

**Example:** Fixed off-by-one error in status broadcast loop

**Update:**
1. **Code comments** - Explain the fix inline
   ```cpp
   // Fixed: Loop was missing last status update (off-by-one error)
   for (size_t i = 0; i <= count; ++i) {  // Changed < to <=
   ```
2. **LESSONS_LEARNED.md** - Add entry if bug had lessons
3. **No architecture docs needed** - Bug fix within existing design

**Time:** ~5 minutes
**Note:** Most bug fixes don't require architecture doc updates

---

### Scenario 5: "I changed deployment configuration"

**Example:** Updated Dockerfile to use Ubuntu 24.04 instead of 22.04

**Update:**
1. **Dockerfile** - Make the change
2. **view-deployment.md** - Update Section 4 (software deployment)
   ```markdown
   **Base Image:** Ubuntu 24.04 LTS (updated from 22.04)
   ```
3. **ADR-004** - Update "Consequences" if trade-offs changed
4. **c4-level4-deployment.puml** - Update if visualization needed

**Time:** ~15 minutes
**Note:** Document WHY version was updated (security, features, etc.)

---

### Scenario 6: "I added a new UI screen in Ground-Side"

**Example:** New "Advanced Settings" screen

**Update:**
1. **Code comments** - KDoc for new Composable
2. **view-logical.md** - Add screen to Section 4.2.4 (UI layer)
   ```markdown
   **AdvancedSettingsScreen:** Provides access to advanced camera settings
   (white balance, picture profile, etc.)
   ```
3. **c4-level3-ground-side-components.puml** - Add UI component if significant
4. **ADR-013** - Update if new Compose pattern used

**Time:** ~15 minutes
**Note:** Minor UI changes may not need C4 diagram update

---

## Domain-Specific Updates

### Air-Side (C++ in `sbc/`)

| Change Type | Documents to Update | Time |
|-------------|---------------------|------|
| New component | view-logical.md, C4 diagram, traceability matrix | ~20 min |
| Threading change | view-logical.md, ADR-006 | ~15 min |
| Docker config | view-deployment.md, ADR-004 | ~15 min |
| Camera integration | view-logical.md, ADR-012 | ~20 min |
| Network protocol | view-integration.md, ADR-003 | ~25 min |

**Key Files:**
- `docs/architecture/view-logical.md` Section 4.2.3
- `docs/architecture/view-deployment.md`
- `docs/architecture/c4-level3-air-side-components.puml`
- ADRs: 001, 004, 006, 007, 012

---

### Ground-Side (Kotlin in `android/`)

| Change Type | Documents to Update | Time |
|-------------|---------------------|------|
| New ViewModel | view-logical.md, C4 diagram | ~20 min |
| New UI screen | view-logical.md | ~15 min |
| State management | view-logical.md, ADR-005 | ~20 min |
| Network layer | view-logical.md, view-integration.md | ~25 min |
| Compose pattern | ADR-013 | ~15 min |

**Key Files:**
- `docs/architecture/view-logical.md` Section 4.2.4
- `docs/architecture/c4-level3-ground-side-components.puml`
- ADRs: 005, 013, 014

---

### Protocol (JSON in `docs/protocol/`)

| Change Type | Documents to Update | Time |
|-------------|---------------------|------|
| New property | JSON spec, PropertyLoader (C++ AND Kotlin), view-integration.md | ~45 min |
| Property modified | Same as above | ~30 min |
| New command | commands.json, view-integration.md | ~30 min |
| Protocol pattern change | ADR-002, view-integration.md | ~45 min |

**⚠️ CRITICAL UPDATES:**
1. `docs/protocol/*.json` - Specification file
2. `sbc/src/property_loader.cpp` - C++ PropertyLoader
3. `android/.../PropertyLoader.kt` - Kotlin PropertyLoader
4. `docs/architecture/view-integration.md`
5. Test BOTH domains together

**Key Files:**
- `docs/protocol/commands.json`
- `docs/protocol/camera_properties.json`
- `docs/architecture/view-integration.md`
- ADRs: 002, 003, 011

---

### Tools (Python in `SystemTools/`)

| Change Type | Documents to Update | Time |
|-------------|---------------------|------|
| New tool | view-logical.md, C4 diagram, SystemTools/README.md | ~25 min |
| Tool UI change | SystemTools/README.md | ~10 min |
| Tool integration | view-integration.md | ~20 min |

**Key Files:**
- `SystemTools/README.md`
- `docs/architecture/view-logical.md` Section 4.2.5
- `docs/architecture/c4-level3-dev-tools-components.puml`

---

## Validation Checklist

### Before Submitting PR

Run through this checklist:

```bash
# Check 1: Did you update the right view?
# - Component change → view-logical.md
# - Integration change → view-integration.md
# - Deployment change → view-deployment.md
# - Security change → view-security-reliability.md
# - Data model change → view-data.md

# Check 2: Did you update C4 diagram?
# - Air-Side component → c4-level3-air-side-components.puml
# - Ground-Side component → c4-level3-ground-side-components.puml
# - Tools component → c4-level3-dev-tools-components.puml
# - New domain → c4-level2-container.puml

# Check 3: Did you update traceability?
# - New component → SAD Section 8.3 (Component → Code)
# - New ADR → SAD Section 8.4 (Decision → Implementation)

# Check 4: Did you validate?
# - Cross-references work: Check all [links] in markdown
# - PlantUML compiles: Open .puml file and verify (or use plantuml -checkonly)
# - No broken references
```

### Automated Validation

GitHub Actions will check:
- ✅ Documentation modified when code changes
- ✅ PlantUML diagrams compile correctly
- ✅ Markdown links are valid
- ✅ ADR format is correct (if new ADR created)

If automated checks fail, fix and push updates.

---

## Getting Help

### "I'm still unsure what to update"

1. **Review similar PRs** - Look at recent merged PRs for examples
2. **Check CONTRIBUTING.md** - Full documentation requirements
3. **Ask in PR comments** - Tag @maintainers or domain leads
4. **Reference examples:**
   - Component added: _[To be added]_
   - Protocol changed: See Issue #22
   - ADR created: See ADR-001 through ADR-015
   - Deployment changed: See ADR-004

### "My automated checks are failing"

**PlantUML syntax error:**
- Open `.puml` file in PlantUML viewer
- Check for missing closing braces `}`
- Verify relationship syntax: `Rel(from, to, "label")`

**Markdown link broken:**
- Check file paths are correct (case-sensitive)
- Verify linked files exist
- Use relative paths, not absolute

**ADR format error:**
- Verify all required sections present (Context, Decision, Alternatives, Consequences)
- Check markdown heading levels (`##` not `###` for main sections)

### "Do I need to update the consolidated SAD?"

**Usually NO** - The SAD (Software Architecture Document) references detailed docs, so you typically update:
- Architecture views (view-*.md)
- C4 diagrams (c4-*.puml)
- ADRs (adr/ADR-*.md)

**Only update SAD directly if:**
- Adding new major section
- Changing overall structure
- Updating traceability matrices (Section 8)

The SAD summaries stay stable - detailed docs get updates.

---

## Quick Reference Table

| I Changed... | Update These Files | Time | Critical? |
|--------------|-------------------|------|-----------|
| Air-Side component | view-logical.md, C4 Air-Side, traceability | ~20 min | Medium |
| Ground-Side component | view-logical.md, C4 Ground-Side | ~20 min | Medium |
| Protocol spec | JSON spec, PropertyLoader (C++ & Kotlin), view-integration.md | ~45 min | **HIGH** |
| Docker config | view-deployment.md, ADR-004 | ~15 min | Medium |
| New UI screen | view-logical.md | ~15 min | Low |
| Architectural decision | Create ADR, update relevant view | ~60 min | High |
| Bug fix (no arch change) | Code comments, maybe LESSONS_LEARNED.md | ~5 min | Low |
| Tool added | view-logical.md, C4 Tools, SystemTools/README.md | ~25 min | Medium |

---

## Examples Library

**Coming Soon:** Links to example PRs demonstrating documentation updates for:
- [ ] Component addition (Air-Side)
- [ ] Component addition (Ground-Side)
- [ ] Protocol change (property added)
- [ ] New ADR created
- [ ] Deployment configuration change
- [ ] Bug fix with LESSONS_LEARNED entry

_First few PRs after enforcement implementation will be tagged as examples._

---

**Need more help?** See `CONTRIBUTING.md` for comprehensive documentation requirements.

**Found this guide helpful?** Keep it updated as you discover new patterns!
