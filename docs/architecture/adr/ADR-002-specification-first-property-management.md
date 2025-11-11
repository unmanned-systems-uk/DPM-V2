# ADR-002: Specification-First Property Management

**Status:** Accepted
**Date:** 2024-11 (PropertyLoader implementation)
**Updated:** 2025-11-11
**Deciders:** Development Team
**Related Issues:** #1, #2, #10, #22
**Related Views:** `view-logical.md`, `view-data.md`

---

## Context

Camera properties (ISO, shutter speed, aperture, white balance, etc.) must be:

1. **Set by Ground-Side UI** (user adjusts sliders/dropdowns)
2. **Validated by Air-Side** (before sending to Sony SDK)
3. **Synchronized** between Air-Side (C++) and Ground-Side (Kotlin)
4. **Mapped** between SDK values (integers/hex) and display values (strings)
5. **Extensible** (easy to add new properties without code changes)

**The Problem:**
- Air-Side validates properties against Sony SDK constraints (valid values per lens/mode)
- Ground-Side UI must show only valid values to prevent errors
- Property specs exist in TWO places (C++ code and Kotlin code)
- **Mismatch Risk:** Air/Ground diverge when adding properties → runtime errors

**Real-World Issue (Issue #22):**
Manual focus commands failed because Ground-Side wasn't aware of Air-Side's expected format. Debugging took many hours.

---

## Decision

**We will adopt a Specification-First Architecture for camera property management:**

1. **Single Source of Truth:** JSON specification files in `docs/protocol/*.json`
2. **PropertyLoader Pattern:** Both Air-Side (C++) and Ground-Side (Kotlin) load specs at startup
3. **Build-Time Sync:** JSON files copied into Docker image and APK assets during build
4. **No Hardcoded Values:** All property metadata comes from JSON specs
5. **UI Auto-Generation:** Ground-Side UI renders controls based on loaded specs

**Key Principle:** "Specification drives implementation, not the reverse"

---

## JSON Specification Format

```json
{
  "property_name": "shutter_speed",
  "display_name": "Shutter Speed",
  "type": "enum",
  "category": "exposure",
  "sdk_property_id": "0x5005",
  "values": [
    {
      "sdk_value": "0x00010001",
      "display_value": "1/8000",
      "sort_order": 1
    },
    {
      "sdk_value": "0x00010002",
      "display_value": "1/6400",
      "sort_order": 2
    }
  ],
  "default": "1/250",
  "unit": "seconds",
  "description": "Camera shutter speed controls exposure time",
  "constraints": {
    "depends_on": ["exposure_mode"],
    "available_when": {
      "exposure_mode": ["M", "S", "A"]
    }
  }
}
```

---

## PropertyLoader Implementation

### Air-Side (C++)

**Location:** `sbc/src/property/property_loader.cpp`

**Responsibilities:**
- Load JSON specs from `/app/specs/*.json` at startup
- Provide validation: `bool isValidValue(property, value)`
- Map values: `string sdkToDisplay(property, sdk_value)`
- Query metadata: `PropertySpec getSpec(property_name)`

**Usage:**
```cpp
// Validate before sending to SDK
if (!propertyLoader.isValidValue("shutter_speed", user_value)) {
    return ErrorResponse("INVALID_PROPERTY_VALUE");
}

// Map display value to SDK value
auto sdk_value = propertyLoader.displayToSdk("shutter_speed", "1/250");
camera->setProperty(sdk_value);
```

### Ground-Side (Kotlin)

**Location:** `android/app/src/main/java/data/PropertyLoader.kt`

**Responsibilities:**
- Load JSON specs from APK assets `assets/specs/*.json` at startup
- Provide UI metadata: `List<String> getValidValues(property)`
- Render controls: `when (spec.type) { "enum" -> Dropdown, "range" -> Slider }`
- Same validation logic as Air-Side (defense in depth)

**Usage:**
```kotlin
// Load specs at app startup
val propertyLoader = PropertyLoader(context)
propertyLoader.loadSpecs()

// Populate dropdown with valid values
val shutterSpeeds = propertyLoader.getValidValues("shutter_speed")
DropdownMenu(items = shutterSpeeds, onSelect = { ... })
```

---

## Build-Time Synchronization

### Air-Side Dockerfile

```dockerfile
# Copy protocol specs into image
COPY docs/protocol/*.json /app/specs/
```

### Ground-Side Gradle

```groovy
// Copy protocol specs into APK assets
android {
    sourceSets {
        main {
            assets.srcDirs += ['../../docs/protocol']
        }
    }
}
```

**Result:** Both domains have identical specs embedded at build time

---

## Alternatives Considered

### Alternative 1: Hardcoded Property Lists

**Approach:** Define valid values in C++ and Kotlin code directly

**Example (C++):**
```cpp
const vector<string> VALID_ISO = {"100", "200", "400", "800", ...};
```

**Example (Kotlin):**
```kotlin
val validIso = listOf("100", "200", "400", "800", ...)
```

**Pros:**
- Simple, no file I/O
- Type-safe at compile time

**Cons:**
- ❌ Duplication: Must update BOTH C++ and Kotlin when adding property
- ❌ Sync Risk: Easy to forget one side → runtime mismatch
- ❌ Not Extensible: Code change required for every new property
- ❌ No Metadata: Can't include descriptions, constraints, units

**Rejection Reason:** Experienced this pain in Issue #22 (manual focus commands failed due to Air/Ground mismatch)

---

### Alternative 2: Air-Side Property Discovery API

**Approach:** Ground-Side queries Air-Side for valid properties at runtime

**Protocol:**
```json
Request:  {"command": "camera.get_valid_values", "property": "shutter_speed"}
Response: {"values": ["1/8000", "1/6400", ...]}
```

**Pros:**
- Single source of truth (Air-Side only)
- No build-time sync required

**Cons:**
- ❌ Network Dependency: Can't render UI until Air-Side responds
- ❌ Latency: Slow initial UI load (20-50ms per property × 15 properties = 750ms)
- ❌ Complexity: Requires additional protocol commands
- ❌ Offline Mode: Ground-Side UI can't work without Air-Side connection

**Rejection Reason:** User experience requires immediate UI responsiveness (no network wait)

---

### Alternative 3: Shared C++ Library

**Approach:** PropertyLoader in C++, Ground-Side uses via JNI

**Pros:**
- True single implementation
- Guaranteed consistency

**Cons:**
- ❌ JNI Complexity: Android ↔ C++ bridge fragile
- ❌ Build Complexity: Must compile C++ for Android (NDK)
- ❌ Platform Lock-In: Dev-Tools (Python) can't use C++ library
- ❌ Android Best Practices: Kotlin ecosystem expects Kotlin data models

**Rejection Reason:** Violates Three-Domain Architecture principle (ADR-001) of platform-native implementations

---

### Alternative 4: Code Generation from Specs

**Approach:** Generate C++ and Kotlin code from JSON specs at build time

**Pros:**
- Type-safe generated classes
- Compile-time validation

**Cons:**
- ❌ Build Complexity: Requires code generator tool
- ❌ Generated Code Maintenance: Large generated files in git
- ❌ Debugging Difficulty: Can't easily inspect generated code
- ❌ Flexibility Loss: Hard to extend generated classes

**Rejection Reason:** Runtime loading simpler and more flexible; performance not critical for startup-time operation

---

## Consequences

### Positive

✅ **Single Source of Truth:** JSON specs are THE definition of properties
- Adding new property: Edit JSON spec only (no code changes)
- Both Air-Side and Ground-Side automatically pick up new property at next build

✅ **Guaranteed Synchronization:** Impossible for Air/Ground to diverge
- Same JSON file embedded in both domains
- Build-time copy ensures identical specs

✅ **Extensibility:** Adding properties is trivial
- Copy existing JSON object, modify values
- No C++ or Kotlin code changes required (PropertyLoader handles generically)

✅ **Metadata-Rich:** Specs include descriptions, units, constraints
- UI can show helpful tooltips (e.g., "Shutter Speed controls exposure time")
- Future: Conditional visibility (e.g., only show ISO when in Manual mode)

✅ **Version Control Friendly:** JSON diffs are human-readable
- Code reviews can easily see property changes
- Git history shows evolution of camera capabilities

✅ **Validation Consistency:** Both sides validate identically
- Defense in depth: Ground-Side prevents invalid input, Air-Side double-checks
- Error messages consistent across domains

✅ **Protocol Documentation:** JSON specs document the protocol
- External developers can see valid values without code inspection
- SystemTools can validate protocol compliance

---

### Negative

⚠️ **Startup Performance:** Must parse JSON at app/container startup
- Mitigation: ~50KB JSON, parses in <50ms (negligible)
- One-time cost, cached in memory thereafter

⚠️ **Runtime Errors:** Invalid JSON causes startup failure (not compile-time error)
- Mitigation: JSON schema validation in CI/CD pipeline (future enhancement)
- Mitigation: Manual testing during development catches issues early

⚠️ **Sync Dependency:** Must rebuild both domains after spec changes
- Mitigation: Normal workflow already rebuilds after protocol changes
- Benefit: Explicit rebuild makes version sync visible

⚠️ **File Management:** JSON files must be maintained separately from code
- Mitigation: Clear location `docs/protocol/*.json`
- Mitigation: Comprehensive documentation in `docs/protocol/README.md`

---

## Implementation Notes

**Specification Files:**
- Location: `docs/protocol/*.json`
- Format: JSON (UTF-8, pretty-printed for readability)
- Naming: `property-{category}.json` (e.g., `property-exposure.json`, `property-focus.json`)

**PropertyLoader Initialization:**
- Air-Side: Load at PayloadManager startup (before camera connection)
- Ground-Side: Load at Application.onCreate() (before UI render)

**Error Handling:**
- Missing spec file → Log error, use safe defaults (ISO 400, 1/250s, f/5.6)
- Invalid JSON → Parse error, fail startup with clear error message
- Unknown property → Ignore gracefully, log warning

**Future Enhancements:**
- JSON schema validation (ajv, Everit JSON Schema)
- Version field in specs → detect Air/Ground version mismatch
- Dynamic property loading (hot-reload without restart)
- Property dependency graph (e.g., ISO range depends on exposure mode)

---

## Validation of Success

**Before Specification-First (Issue #22):**
- Manual focus commands failed
- Debugging took many hours
- Root cause: Air-Side expected format different from Ground-Side sent

**After Specification-First:**
- Focus commands working (Issue #10 CLOSED)
- New properties added without cross-domain bugs
- Protocol changes require spec update only → automatic sync

**Quantitative Impact:**
- Time to add new property: ~5 minutes (edit JSON) vs. ~30 minutes (edit C++ + Kotlin + test)
- Air/Ground protocol mismatch bugs: 0 since implementation (previously ~1 per week)

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (explains why sync is needed)
- **ADR-003:** TCP/UDP Protocol Split (PropertyLoader validates command payloads)
- **ADR-011:** JSON-over-TCP/UDP Protocol (JSON format extends to property specs)

---

## References

- PropertyLoader (C++): `sbc/src/property/property_loader.cpp`
- PropertyLoader (Kotlin): `android/app/src/main/java/data/PropertyLoader.kt`
- Specification Files: `docs/protocol/*.json`
- Data View: `docs/architecture/view-data.md` (Property Specification Sync section)
- LESSONS_LEARNED.md: Protocol Implementation section
