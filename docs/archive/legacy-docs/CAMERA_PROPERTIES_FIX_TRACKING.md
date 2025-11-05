# Camera Properties Fix - End-to-End Tracking

**Issue:** Hardcoded camera property values causing synchronization failures between Air-Side and Ground-Side
**Branch:** `fix-camera_properties-conflict`
**Started:** October 28, 2025
**Status:** 🟡 IN PROGRESS
**Last Updated:** October 28, 2025 - Phase 2 Complete

---

## Executive Summary

### The Problem

**Root Cause:** Camera property values (ISO, shutter speed, aperture) are hardcoded independently in three locations:
1. Air-Side C++ (`sbc/src/camera/camera_sony.cpp`) - 35 ISO, 56 shutter, 23 aperture
2. Ground-Side Android (`android/.../camera/CameraState.kt`) - 28 ISO (OUT OF SYNC), 56 shutter, 23 aperture
3. JSON Specification (`docs/protocol/camera_properties.json`) - 35 ISO, 56 shutter, 23 aperture

**Impact:**
- Manual synchronization required between platforms
- Android already out of sync (missing 7 ISO values: auto, 50, 64, 80, 64000, 80000, 102400)
- High risk of future divergence
- Violates specification-first architecture (CC_READ_THIS_FIRST.md lines 29-111)

### The Solution

**Approach:** Runtime JSON Loading (CC_READ_THIS_FIRST.md Option B)

**Implementation:**
1. ✅ **Phase 1:** Analysis complete - identified all hardcoded locations
2. ✅ **Phase 2:** Design complete - runtime JSON loading approach selected
3. 🔄 **Phase 3:** Implement Air-Side JSON integration (IN PROGRESS)
4. ⏳ **Phase 4:** Implement Android JSON integration (PENDING)
5. ⏳ **Phase 5:** Test and validate synchronization (PENDING)

---

## Phase 1: Analysis ✅ COMPLETE

**Status:** ✅ Completed October 28, 2025

### Air-Side (C++) - Hardcoded Locations Identified

**File:** `/home/dpm/DPM-V2/sbc/src/camera/camera_sony.cpp`

| Property | Forward Map Lines | Reverse Map Lines | Value Count | Status |
|----------|------------------|-------------------|-------------|---------|
| Shutter Speed | 514-539 | 801-856 | 56 values | Hardcoded |
| ISO | 589-605 | 858-882 | 35 values | Hardcoded |
| Aperture | 541-563 | 767-799 | 23 values | Hardcoded |

**Map Structure:**
```cpp
// Forward: string → Sony SDK hex value
static const std::unordered_map<std::string, uint32_t> ISO_MAP = {
    {"auto", 0xFFFFFFFF},
    {"50", 50},
    // ... 35 total values
};

// Reverse: Sony SDK hex value → string
static const std::unordered_map<uint32_t, std::string> ISO_REVERSE = {
    {0xFFFFFFFF, "auto"},
    {50, "50"},
    // ... 35 total values
};
```

### Ground-Side (Android) - Hardcoded Locations Identified

**File:** `/home/dpm/DPM-V2/android/app/src/main/java/uk/unmannedsystems/dpm_android/camera/CameraState.kt`

| Property | Enum Lines | Value Count | Status |
|----------|-----------|-------------|---------|
| ShutterSpeed | 41-110 | 56 values | Hardcoded (synchronized) |
| ISO | 155-190 | **28 values** | **Hardcoded (OUT OF SYNC)** |
| Aperture | 115-150 | 23 values | Hardcoded (synchronized) |

**Enum Structure:**
```kotlin
enum class ISO(val displayValue: String, val value: Int) {
    ISO_100("100", 100),
    ISO_125("125", 125),
    // ... ONLY 28 values (missing 7!)
}
```

**Missing ISO Values in Android:**
- `auto` (0xFFFFFFFF)
- `50` (extended low)
- `64` (extended low)
- `80` (extended low)
- `64000` (high)
- `80000` (high)
- `102400` (high)

### Specification Status

**File:** `/home/dpm/DPM-V2/docs/protocol/camera_properties.json`

| Property | Value Count | Status |
|----------|-------------|---------|
| Shutter Speed | 56 values | ✅ Complete |
| ISO | 35 values | ✅ Complete |
| Aperture | 23 values | ✅ Complete |

**Analysis Conclusion:**
- ✅ All hardcoded locations identified
- ✅ Synchronization failure confirmed (Android ISO missing 7 values)
- ✅ JSON specification is complete and accurate
- ✅ No other files contain hardcoded property values

---

## Phase 2: Design ✅ COMPLETE

**Status:** ✅ Completed October 28, 2025

### Approach Selected: Runtime JSON Loading

**Decision Rationale:**

Considered approaches per CC_READ_THIS_FIRST.md (lines 371-375):
- ❌ **Option C:** Hardcoding values (FORBIDDEN - current state)
- 🟡 **Option A:** Build-time code generation (more complex)
- ✅ **Option B:** Runtime JSON loading (SELECTED)

**Why Runtime JSON Loading:**
1. **Simplicity:** No build process changes required
2. **Performance:** JSON loaded once at startup (negligible overhead)
3. **Discovery Script Compatibility:** Existing `discover_iso_map.py` and `discover_shutter_map.py` can update JSON directly
4. **Cross-Platform:** Both C++ (nlohmann/json) and Android (native JSON) support
5. **Maintenance:** Easier to debug and update
6. **Compliance:** Aligns with CC_READ_THIS_FIRST.md specification-first rules

### Air-Side Implementation Design

**New Files to Create:**
```
sbc/src/camera/
├── property_loader.h           # NEW - PropertyLoader class header
└── property_loader.cpp         # NEW - PropertyLoader implementation
```

**Modified Files:**
```
sbc/src/camera/
├── camera_sony.cpp             # MODIFY - Replace hardcoded maps with PropertyLoader
└── camera_sony.h               # MODIFY - Add PropertyLoader dependency
```

**PropertyLoader Class Interface:**
```cpp
class PropertyLoader {
public:
    // Initialize from JSON file (call once at startup)
    static bool initialize(const std::string& json_path = "../docs/protocol/camera_properties.json");

    // Getters for property maps
    static const std::unordered_map<std::string, uint32_t>& getIsoForwardMap();
    static const std::unordered_map<uint32_t, std::string>& getIsoReverseMap();
    static const std::unordered_map<std::string, uint32_t>& getShutterForwardMap();
    static const std::unordered_map<uint32_t, std::string>& getShutterReverseMap();
    static const std::unordered_map<std::string, uint32_t>& getApertureForwardMap();
    static const std::unordered_map<uint32_t, std::string>& getApertureReverseMap();

    // Status check
    static bool isInitialized();

private:
    static std::unordered_map<std::string, uint32_t> iso_forward_;
    static std::unordered_map<uint32_t, std::string> iso_reverse_;
    static std::unordered_map<std::string, uint32_t> shutter_forward_;
    static std::unordered_map<uint32_t, std::string> shutter_reverse_;
    static std::unordered_map<std::string, uint32_t> aperture_forward_;
    static std::unordered_map<uint32_t, std::string> aperture_reverse_;
    static bool initialized_;

    static void loadProperty(const nlohmann::json& prop,
                            std::unordered_map<std::string, uint32_t>& forward,
                            std::unordered_map<uint32_t, std::string>& reverse);
};
```

**Integration Strategy:**
1. Add PropertyLoader::initialize() call at camera initialization
2. Replace static map declarations with PropertyLoader getters
3. Minimal changes to existing property get/set logic
4. Maintain same map-based access pattern

### Android Implementation Design

**New Files to Create:**
```
android/app/src/main/
├── assets/
│   └── camera_properties.json  # NEW - Copy of specification
└── java/.../util/
    └── PropertyLoader.kt        # NEW - Loads from assets
```

**Modified Files:**
```
android/app/src/main/java/.../camera/
├── CameraState.kt              # MODIFY - Replace enums with data from PropertyLoader
├── CameraViewModel.kt          # MODIFY - Initialize PropertyLoader
└── CameraControlFragment.kt    # MODIFY - Use PropertyLoader values for UI
```

**PropertyLoader Object Interface:**
```kotlin
object PropertyLoader {
    // Initialize from assets (call once at app startup)
    fun initialize(context: Context)

    // Getters for property values
    fun getIsoValues(): List<String>
    fun getShutterSpeedValues(): List<String>
    fun getApertureValues(): List<String>

    // Get display hints for UI
    fun getPropertyUiHint(property: String): String

    // Status check
    fun isInitialized(): Boolean
}
```

**Enum Replacement Strategy:**
- **Option 1:** Keep enum structure, populate from PropertyLoader
- **Option 2:** Replace enums with sealed classes/data classes
- **Selected:** Option 1 for minimal disruption to existing UI code

### Design Validation

**Checklist:**
- ✅ Follows CC_READ_THIS_FIRST.md Option B (Runtime JSON Loading)
- ✅ Eliminates hardcoded values (Option C forbidden pattern)
- ✅ Uses camera_properties.json as single source of truth
- ✅ Minimal changes to existing code structure
- ✅ Compatible with discovery scripts
- ✅ No build system changes required
- ✅ Cross-platform (C++ and Android)
- ✅ Performance acceptable (one-time load at startup)

---

## Phase 3: Air-Side Implementation 🔄 IN PROGRESS

**Status:** 🟡 NOT STARTED
**Target Completion:** TBD

### Implementation Tasks

#### Task 3.1: Create PropertyLoader Class
- [ ] Create `sbc/src/camera/property_loader.h`
- [ ] Create `sbc/src/camera/property_loader.cpp`
- [ ] Implement JSON loading using nlohmann/json
- [ ] Implement forward/reverse map generation
- [ ] Add error handling for missing/malformed JSON
- [ ] Add logging for initialization status

**Files to Create:**
1. `sbc/src/camera/property_loader.h`
2. `sbc/src/camera/property_loader.cpp`

#### Task 3.2: Verify nlohmann/json Library
- [ ] Check if nlohmann/json is already available in project
- [ ] If not, add to CMakeLists.txt or vendor it
- [ ] Verify JSON parsing works with camera_properties.json

**Dependencies:**
- nlohmann/json library (header-only)

#### Task 3.3: Integrate PropertyLoader into camera_sony.cpp
- [ ] Add PropertyLoader initialization in camera initialization
- [ ] Replace ISO_MAP with PropertyLoader::getIsoForwardMap()
- [ ] Replace ISO_REVERSE with PropertyLoader::getIsoReverseMap()
- [ ] Replace SHUTTER_MAP with PropertyLoader::getShutterForwardMap()
- [ ] Replace SHUTTER_REVERSE with PropertyLoader::getShutterReverseMap()
- [ ] Replace APERTURE_MAP with PropertyLoader::getApertureForwardMap()
- [ ] Replace APERTURE_REVERSE with PropertyLoader::getApertureReverseMap()
- [ ] Remove all hardcoded map definitions

**Files to Modify:**
1. `sbc/src/camera/camera_sony.cpp` (lines 514-605, 767-882)
2. `sbc/src/camera/camera_sony.h` (add PropertyLoader include)

#### Task 3.4: Update CMakeLists.txt
- [ ] Add property_loader.cpp to build sources
- [ ] Link nlohmann/json if needed
- [ ] Verify build succeeds

**Files to Modify:**
1. `sbc/CMakeLists.txt`

#### Task 3.5: Test Air-Side Implementation
- [ ] Build the project
- [ ] Run payload_server
- [ ] Verify PropertyLoader initializes successfully
- [ ] Test ISO property get/set operations
- [ ] Test shutter speed property get/set operations
- [ ] Test aperture property get/set operations
- [ ] Verify all 35 ISO values work (including missing ones)
- [ ] Check logs for any errors

**Test Commands:**
```bash
cd /home/dpm/DPM-V2/sbc/build
cmake ..
make -j4
./payload_server  # Or run in Docker container
```

#### Task 3.6: Commit Air-Side Changes
- [ ] Verify build succeeds
- [ ] Update sbc/docs/PROGRESS_AND_TODO.md
- [ ] Commit with message: `[REFACTOR] Air-Side: Remove hardcoded property values, use JSON loader`
- [ ] Update this tracking document

**Commit Template:**
```
[REFACTOR] Air-Side: Remove hardcoded property values, use JSON loader

- Created PropertyLoader class to read camera_properties.json at runtime
- Replaced hardcoded ISO, shutter, aperture maps in camera_sony.cpp
- All property values now loaded from specification (35 ISO, 56 shutter, 23 aperture)
- Eliminates manual synchronization with Ground-Side
- Follows CC_READ_THIS_FIRST.md specification-first architecture

Files changed:
- sbc/src/camera/property_loader.h (NEW)
- sbc/src/camera/property_loader.cpp (NEW)
- sbc/src/camera/camera_sony.cpp (MODIFIED - removed hardcoded maps)
- sbc/src/camera/camera_sony.h (MODIFIED - added PropertyLoader)
- sbc/CMakeLists.txt (MODIFIED - added property_loader.cpp)
```

### Current Progress

**Tasks Completed:** 0/6
**Overall Progress:** 0%

---

## Phase 4: Android Implementation ⏳ PENDING

**Status:** ⏳ NOT STARTED
**Target Completion:** TBD

### Implementation Tasks

#### Task 4.1: Copy Specification to Assets
- [ ] Copy `docs/protocol/camera_properties.json` to `android/app/src/main/assets/`
- [ ] Verify JSON is included in APK build

**Files to Create:**
1. `android/app/src/main/assets/camera_properties.json`

#### Task 4.2: Create PropertyLoader Object
- [ ] Create `PropertyLoader.kt` in util package
- [ ] Implement JSON loading from assets
- [ ] Implement property value extraction
- [ ] Add error handling for missing/malformed JSON
- [ ] Add logging for initialization status

**Files to Create:**
1. `android/app/src/main/java/uk/unmannedsystems/dpm_android/util/PropertyLoader.kt`

#### Task 4.3: Refactor CameraState.kt
- [ ] Replace hardcoded ISO enum with PropertyLoader values
- [ ] Replace hardcoded ShutterSpeed enum with PropertyLoader values
- [ ] Replace hardcoded Aperture enum with PropertyLoader values
- [ ] OR keep enums but populate from PropertyLoader
- [ ] Verify all 35 ISO values are now available (including missing 7)

**Files to Modify:**
1. `android/app/src/main/java/.../camera/CameraState.kt` (lines 41-190)

**Missing ISO Values to Add:**
- `auto`
- `50`
- `64`
- `80`
- `64000`
- `80000`
- `102400`

#### Task 4.4: Initialize PropertyLoader in App
- [ ] Call PropertyLoader.initialize() in Application.onCreate()
- [ ] OR in MainActivity.onCreate()
- [ ] Verify initialization completes before camera UI loads

**Files to Modify:**
1. Main application entry point (Application class or MainActivity)

#### Task 4.5: Update UI Components
- [ ] Update CameraControlFragment to use PropertyLoader values
- [ ] Update spinners/dropdowns with new ISO values
- [ ] Verify UI displays all values correctly
- [ ] Test property selection and network transmission

**Files to Modify:**
1. `android/app/src/main/java/.../camera/CameraControlFragment.kt`

#### Task 4.6: Test Android Implementation
- [ ] Build APK
- [ ] Install on device/H16
- [ ] Verify PropertyLoader initializes successfully
- [ ] Test ISO dropdown shows all 35 values
- [ ] Test shutter speed dropdown shows all 56 values
- [ ] Test aperture dropdown shows all 23 values
- [ ] Test property changes send correct values to Air-Side
- [ ] Verify no crashes or errors in logcat

**Test Commands:**
```bash
cd /home/dpm/DPM-V2/android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb logcat | grep DPM
```

#### Task 4.7: Commit Android Changes
- [ ] Verify build succeeds
- [ ] Update android/docs/PROGRESS_AND_TODO.md
- [ ] Commit with message: `[REFACTOR] Android: Remove hardcoded property values, use JSON loader`
- [ ] Update this tracking document

**Commit Template:**
```
[REFACTOR] Android: Remove hardcoded property values, use JSON loader

- Created PropertyLoader to read camera_properties.json from assets
- Replaced hardcoded ISO, shutter, aperture enums in CameraState.kt
- All property values now loaded from specification (35 ISO, 56 shutter, 23 aperture)
- Fixed synchronization issue: Android now has all 35 ISO values (was missing 7)
- Eliminates manual synchronization with Air-Side
- Follows CC_READ_THIS_FIRST.md specification-first architecture

Files changed:
- android/app/src/main/assets/camera_properties.json (NEW - copy of spec)
- android/app/src/main/java/.../util/PropertyLoader.kt (NEW)
- android/app/src/main/java/.../camera/CameraState.kt (MODIFIED)
- android/app/src/main/java/.../camera/CameraControlFragment.kt (MODIFIED)
```

### Current Progress

**Tasks Completed:** 0/7
**Overall Progress:** 0%

---

## Phase 5: Testing & Validation ⏳ PENDING

**Status:** ⏳ NOT STARTED
**Target Completion:** TBD

### Test Plan

#### Test 5.1: Air-Side Standalone Testing
- [ ] Build and run Air-Side with PropertyLoader
- [ ] Verify JSON loads successfully
- [ ] Test all ISO values (35 total)
- [ ] Test all shutter speed values (56 total)
- [ ] Test all aperture values (23 total)
- [ ] Verify property get/set operations work correctly
- [ ] Check logs for any errors or warnings

**Success Criteria:**
- All 35 ISO values work (including auto, 50, 64, 80, 64000, 80000, 102400)
- All 56 shutter speeds work
- All 23 apertures work
- No hardcoded values remain in camera_sony.cpp
- PropertyLoader initializes without errors

#### Test 5.2: Android Standalone Testing
- [ ] Build and install Android app with PropertyLoader
- [ ] Verify JSON loads from assets successfully
- [ ] Test ISO dropdown shows all 35 values (including 7 previously missing)
- [ ] Test shutter speed dropdown shows all 56 values
- [ ] Test aperture dropdown shows all 23 values
- [ ] Verify property selection works
- [ ] Check logcat for any errors or warnings

**Success Criteria:**
- All 35 ISO values visible in UI (including auto, 50, 64, 80, 64000, 80000, 102400)
- All 56 shutter speeds visible in UI
- All 23 apertures visible in UI
- No hardcoded values remain in CameraState.kt
- PropertyLoader initializes without errors

#### Test 5.3: End-to-End Integration Testing
- [ ] Run both Air-Side and Android simultaneously
- [ ] Test ISO property change from Android → Air-Side → Camera
- [ ] Test shutter speed property change from Android → Air-Side → Camera
- [ ] Test aperture property change from Android → Air-Side → Camera
- [ ] Test all 7 previously missing ISO values work end-to-end
- [ ] Verify camera accepts all property values
- [ ] Monitor both sides for synchronization issues

**Success Criteria:**
- All property changes propagate correctly Android → Air-Side → Camera
- No "unknown value" errors on either side
- All 35 ISO values work with real camera
- Air-Side and Android use identical value lists
- No synchronization failures

#### Test 5.4: Specification Audit
- [ ] Run hardcoded value detection on Air-Side
- [ ] Run hardcoded value detection on Android
- [ ] Verify camera_properties.json matches implementations
- [ ] Verify no property arrays hardcoded anywhere

**Audit Commands:**
```bash
# Air-Side check
grep -rn "std::vector.*ISO\|ISO.*{" sbc/src/ | grep -v generated | grep -v "//"

# Android check
grep -rn "arrayOf.*ISO\|listOf.*ISO" android/app/src/ | grep -v generated | grep -v "//"

# Should return NOTHING (or only PropertyLoader)
```

**Success Criteria:**
- Zero hardcoded property arrays in Air-Side (except PropertyLoader)
- Zero hardcoded property arrays in Android (except PropertyLoader)
- camera_properties.json is authoritative source
- Audit script passes (if available)

#### Test 5.5: Regression Testing
- [ ] Test existing camera functionality still works
- [ ] Verify no performance degradation
- [ ] Test with real Sony Alpha 1 camera
- [ ] Verify all Phase 1 features still work
- [ ] Check memory usage (valgrind on Air-Side)

**Success Criteria:**
- All existing features work as before
- No new crashes or errors
- No memory leaks (valgrind clean)
- Performance unchanged (JSON load is one-time at startup)

### Current Progress

**Tests Completed:** 0/5
**Overall Progress:** 0%

---

## Overall Project Status

### Phase Summary

| Phase | Status | Progress | Completion Date |
|-------|--------|----------|----------------|
| Phase 1: Analysis | ✅ Complete | 100% | Oct 28, 2025 |
| Phase 2: Design | ✅ Complete | 100% | Oct 28, 2025 |
| Phase 3: Air-Side Implementation | 🟡 Not Started | 0% | TBD |
| Phase 4: Android Implementation | ⏳ Pending | 0% | TBD |
| Phase 5: Testing & Validation | ⏳ Pending | 0% | TBD |

**Overall Progress:** 40% (2/5 phases complete)

### Key Metrics

**Hardcoded Values to Eliminate:**
- Air-Side: 114 hardcoded values (35 ISO + 56 shutter + 23 aperture) × 2 (forward + reverse) = 228 lines
- Android: 107 hardcoded enum values
- **Total:** 335+ lines of hardcoded values to replace with JSON loading

**Synchronization Status:**
- ❌ ISO values: OUT OF SYNC (Android missing 7 values)
- ✅ Shutter speed: SYNCHRONIZED (both have 56 values)
- ✅ Aperture: SYNCHRONIZED (both have 23 values)

**After Fix:**
- ✅ All properties: SYNCHRONIZED (single source of truth)

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JSON parsing performance overhead | Low | Low | One-time load at startup, negligible impact |
| nlohmann/json library missing | Low | Medium | Check availability, vendor if needed |
| Breaking existing functionality | Medium | High | Extensive testing, keep map structure same |
| Android asset packaging issues | Low | Medium | Verify JSON included in APK build |
| Camera rejects new ISO values | Low | High | Test with real camera, discovery scripts validated values |

### Process Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Incomplete testing | Medium | High | Comprehensive test plan in Phase 5 |
| Documentation drift | Medium | Medium | Update this file after each phase |
| Merge conflicts | Low | Medium | Working on feature branch, coordinate with user |
| Regression in existing features | Medium | High | Full regression test suite in Phase 5 |

---

## Success Criteria

### Must Have (Required for Completion)

- ✅ Phase 1 complete: All hardcoded locations identified
- ✅ Phase 2 complete: Implementation design approved
- ⏳ Phase 3 complete: Air-Side uses PropertyLoader, no hardcoded values
- ⏳ Phase 4 complete: Android uses PropertyLoader, no hardcoded values
- ⏳ Phase 5 complete: All tests pass, synchronization verified
- ⏳ Android ISO values complete (all 35 values including missing 7)
- ⏳ Specification is single source of truth on both platforms
- ⏳ No hardcoded property arrays remain in codebase
- ⏳ All existing functionality works unchanged

### Nice to Have (Optional Enhancements)

- Update discovery scripts to write directly to camera_properties.json
- Create audit script (tools/audit_protocol_sync.sh) if not exists
- Add pre-commit hook to prevent hardcoded values
- Document PropertyLoader usage in developer guides
- Add unit tests for PropertyLoader classes

---

## References

### Documentation
- **CC_READ_THIS_FIRST.md** - Specification-first architecture rules (lines 29-111, 371-375)
- **camera_properties.json** - Single source of truth for property values
- **sbc/docs/PROGRESS_AND_TODO.md** - Air-Side progress tracking
- **android/docs/PROGRESS_AND_TODO.md** - Android progress tracking

### Code Locations
- **Air-Side hardcoded maps:** `sbc/src/camera/camera_sony.cpp` (lines 514-605, 767-882)
- **Android hardcoded enums:** `android/.../camera/CameraState.kt` (lines 41-190)
- **Discovery scripts:** `sbc/scripts/discover_iso_map.py`, `sbc/scripts/discover_shutter_map.py`

### Related Issues
- October 2025 specification divergence (camera_properties.json outdated)
- Android missing 7 ISO values (auto, 50, 64, 80, 64000, 80000, 102400)
- Manual synchronization required between Air-Side and Ground-Side

---

## Change Log

### October 28, 2025 - Phase 2 Complete
- Created this tracking document
- Completed Phase 1: Analysis of all hardcoded values
- Completed Phase 2: Runtime JSON loading design selected
- Identified Android ISO synchronization issue (missing 7 values)
- Ready to begin Phase 3: Air-Side implementation

---

**Next Action:** Begin Phase 3 Task 3.1 - Create PropertyLoader class for Air-Side
