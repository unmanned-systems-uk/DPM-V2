# Sony CrSDK API Reference Guide
*Air-Side Camera Implementation Reference*
*Last Updated: 2025-11-07*

## 🎯 Purpose

This guide helps Air-Side Claude Code instances effectively use the Sony Camera Remote SDK (CrSDK) API documentation when implementing camera functions.

**🔴 CRITICAL RULE:** ALWAYS check the SDK documentation BEFORE implementing any camera function. Don't guess the API - verify it.

---

## 📚 Documentation Location

### In This Repository
```
docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/
├── index.html          # Start here - main index
├── search/             # Search functionality
├── classes/            # Class documentation
├── functions/          # Function reference
└── ...                 # 2000+ pages of docs
```

### On Air-Side Pi 5
```
~/sony_sdk/             # SDK installation (outside git)
└── docs/               # SDK documentation (if available)
```

**How to open:**
```bash
# From project root
cd docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/html/
xdg-open index.html     # Linux (Air-Side Pi 5)
open index.html         # macOS
start index.html        # Windows

# Or from anywhere in project
xdg-open docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/html/index.html
```

---

## 🚨 When to Use SDK Documentation

### ALWAYS Reference SDK Docs When:

1. **Implementing NEW camera function**
   - Check if function exists in SDK
   - Verify function signature
   - Check parameter types and ranges
   - Review example code

2. **Getting unexpected SDK errors**
   - Look up error code in documentation
   - Check common error causes
   - Review error handling examples

3. **Camera property not behaving as expected**
   - Verify property name (case-sensitive!)
   - Check if property is read-only or read-write
   - Verify supported camera models
   - Check mode dependencies (AF vs MF, etc.)

4. **Implementing focus/zoom/exposure control**
   - These are complex - MUST reference docs
   - Multiple related functions
   - Mode-dependent behavior
   - Range validation required

5. **Working with camera callbacks**
   - Callback signatures must match exactly
   - Threading considerations
   - Lifetime management

---

## 📖 How to Use the Documentation

### Method 1: Index Search (Fastest)

1. Open `index.html` in browser
2. Use browser's Find function (Ctrl+F / Cmd+F)
3. Search for function/class name
4. Example: Search for "focus" finds all focus-related functions

### Method 2: Browse by Category

**Main Categories:**
- **Classes** - Camera, Device, Property classes
- **Functions** - All SDK functions
- **Enumerations** - Constants and enums
- **Callbacks** - Event handlers
- **Error Codes** - Return value meanings

### Method 3: Search Function (Built-in)

1. Open `index.html`
2. Click "Search" in navigation
3. Enter search term
4. Filter by category if needed

---

## 🔍 Common Lookups

### Focus Distance
**Search for:** `GetFocusPosition`, `SetFocusPosition`, `focus distance`

**Key Functions:**
- `SDK::CrDeviceProperty::CrDeviceProperty_FocusPosition`
- `SDK::CrFocusPositionInfo`
- Check: Mode dependencies (Manual focus only?)
- Check: Valid range per lens

### Focus Mode
**Search for:** `FocusMode`, `AF`, `MF`

**Key Properties:**
- `SDK::CrDeviceProperty::CrDeviceProperty_FocusMode`
- `SDK::CrFocusMode`
- Values: `CrFocusMode_AF`, `CrFocusMode_MF`, etc.

### Shutter Speed
**Search for:** `ShutterSpeed`, `Exposure`

**Key Properties:**
- `SDK::CrDeviceProperty::CrDeviceProperty_ShutterSpeed`
- Check: Valid values (camera-specific)
- Check: Mode dependencies (Manual mode?)

### Zoom Control
**Search for:** `Zoom`, `ZoomPosition`

**Key Functions:**
- `SDK::CrDeviceProperty::CrDeviceProperty_Zoom_Position`
- Check: Optical vs Digital zoom
- Check: Speed control

---

## ⚠️ Common Pitfalls (From Lessons Learned)

### 1. Property Name Case Sensitivity
```cpp
// ❌ Wrong - lowercase
camera->getProperty("focusposition");

// ✅ Correct - exact case from SDK
camera->getProperty(SDK::CrDeviceProperty::CrDeviceProperty_FocusPosition);
```

**Always:** Use the exact constant from SDK documentation.

### 2. Mode Dependencies
```cpp
// ❌ Wrong - doesn't check mode
auto distance = camera->getFocusDistance();

// ✅ Correct - check mode first
auto mode = camera->getFocusMode();
if (mode == SDK::CrFocusMode_MF) {
    auto distance = camera->getFocusDistance();
}
```

**From SDK docs:** Many properties only work in specific modes.

### 3. Assuming Property Availability
```cpp
// ❌ Wrong - assumes property exists
camera->setProperty(property, value);

// ✅ Correct - check availability first
if (camera->isPropertyAvailable(property)) {
    camera->setProperty(property, value);
}
```

**From SDK docs:** Properties vary by camera model and current state.

### 4. Ignoring Error Codes
```cpp
// ❌ Wrong - ignores return value
camera->setProperty(property, value);

// ✅ Correct - check return code
SDK::CrError result = camera->setProperty(property, value);
if (result != SDK::CrError_None) {
    LOG_ERROR("Set property failed: " << getErrorString(result));
    // Look up error code in SDK docs
}
```

**From SDK docs:** Error codes have specific meanings and solutions.

### 5. Not Checking Value Ranges
```cpp
// ❌ Wrong - sends arbitrary value
camera->setZoomPosition(9999);  // Will fail!

// ✅ Correct - check valid range first
SDK::CrZoomRange range = camera->getZoomRange();
int validValue = std::clamp(desiredZoom, range.min, range.max);
camera->setZoomPosition(validValue);
```

**From SDK docs:** Each property has valid range, documented per camera model.

---

## 📋 SDK Documentation Workflow

### Before Implementing ANY Camera Function:

1. **Search SDK documentation**
   ```bash
   # Open index.html and search for function
   ```

2. **Read function documentation**
   - Function signature
   - Parameters and types
   - Return values
   - Error codes
   - Example code

3. **Check prerequisites**
   - Camera mode requirements
   - Property availability
   - Related functions (getters/setters)
   - Threading considerations

4. **Note constraints**
   - Valid value ranges
   - Supported camera models
   - Timing considerations
   - Callback requirements

5. **Document in issue comment**
   ```markdown
   **WHO:** CC-Air-Side

   Checked Sony SDK documentation:
   - Function: SDK::CrDeviceProperty::CrDeviceProperty_FocusPosition
   - Requirements: Manual focus mode only
   - Valid range: 0-65535 (lens-dependent)
   - Returns: CrError_None on success

   Implementation approach: [describe based on SDK docs]
   ```

---

## 🔗 Quick Reference Links

**Key SDK Sections to Bookmark:**

1. **Class List** - All SDK classes
2. **Function List** - All SDK functions
3. **Enumeration List** - All constants
4. **CrDeviceProperty** - ALL camera properties (most important!)
5. **CrError** - Error code meanings
6. **Examples** - Working code samples

---

## 🎓 Learning from Past Issues

### Issue #1, #2, #10: Focus Distance
**Problem:** Didn't reference SDK docs, tried wrong functions

**From SDK docs we learned:**
- `GetFocusPosition` returns position, not distance
- Must use `CrDeviceProperty_FocusPosition` property
- Manual focus mode required
- Range is lens-specific

**Lesson:** 30 minutes reading SDK docs saved 4 hours of trial-and-error.

### Issue #22: Manual Focus Commands
**Problem:** Commands not working, didn't check SDK for requirements

**From SDK docs we learned:**
- Mode must be Manual Focus first
- Property must be writable (check with `isPropertyWritable()`)
- Valid range must be queried before setting

**Lesson:** SDK docs specify prerequisites that aren't obvious from code.

---

## 🚀 SDK Documentation Best Practices

### Do's ✅

1. **Always open docs BEFORE implementing**
   - Don't guess the API
   - Don't assume based on similar functions
   - Verify everything

2. **Search multiple related terms**
   - If "focus distance" finds nothing, try "focus position"
   - Related terms often reveal the right API

3. **Read the ENTIRE function documentation**
   - Not just signature - read description
   - Check "See also" sections
   - Review example code

4. **Check supported camera models**
   - Not all functions work on all cameras
   - Document model-specific behavior

5. **Note version information**
   - SDK version: v2.00.00
   - Check if camera firmware affects API

### Don'ts ❌

1. **Don't skip SDK docs**
   - "I'll just try this function name" = ❌
   - Always verify first = ✅

2. **Don't assume from other SDKs**
   - Sony SDK is unique
   - Similar cameras may have different APIs

3. **Don't trust old code without verification**
   - SDK may have been updated
   - Check if better API exists now

4. **Don't ignore warnings/notes in docs**
   - Red boxes = important limitations
   - Yellow boxes = common pitfalls

5. **Don't forget to document what you learned**
   - Add to LESSONS_LEARNED.md
   - Help future sessions

---

## 🛠️ Troubleshooting with SDK Docs

### When Function Doesn't Work:

1. **Check error code meaning**
   - Look up exact error code in SDK docs
   - Each code has specific cause and solution

2. **Verify prerequisites**
   - Camera mode correct?
   - Property available?
   - Value in valid range?

3. **Check threading requirements**
   - Some functions require specific threads
   - Callbacks must not block

4. **Review example code**
   - SDK includes working examples
   - Compare your code to example

### When Property Returns Unexpected Value:

1. **Check property type**
   - Integer? String? Enum?
   - Correct parsing?

2. **Check mode dependencies**
   - Some properties only valid in certain modes
   - Example: AF vs MF focus properties

3. **Check camera state**
   - Recording? Idle?
   - Some properties change based on state

---

## 📞 When to Ask for Help

**After checking SDK docs, if still stuck:**

1. **Document what you checked**
   ```markdown
   **WHO:** CC-Air-Side

   Stuck on implementing [function].

   SDK documentation checked:
   - Function: [exact name from docs]
   - Verified: [what I verified]
   - Tried: [what I tried]
   - Error: [error code and meaning from docs]

   Request: [what help needed]
   ```

2. **Include SDK doc references**
   - Link to relevant SDK documentation section
   - Copy relevant documentation text
   - Shows you did your homework

3. **Ask user or create issue**
   - User may have hardware-specific insights
   - Other domains may have related solutions
   - Historical search may find similar issues

---

## 🎯 Summary

**Golden Rule:** ALWAYS check SDK documentation FIRST when implementing camera functions.

**Benefits:**
- Saves hours of trial-and-error
- Avoids wrong APIs
- Catches mode dependencies
- Validates parameter ranges
- Provides working examples

**Location:**
```
docs/AIR_SIDE/CrSDK_API_Reference_v2.00.00/index.html
```

**When stuck:**
1. Search SDK docs
2. Read full documentation
3. Check examples
4. Verify prerequisites
5. Document findings

**Result:** Faster, more reliable Air-Side implementations.

---

**See Also:**
- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Sony SDK lessons section
- `docs/CC_READ_THIS_FIRST.md` - Air-Side quick commands
- `sbc/src/camera/camera_sony.cpp` - Air-Side implementation reference

---

*This guide ensures Air-Side Claude Code never forgets to check the SDK documentation.*

**WHO:** CC-Project-Manager (created 2025-11-07)
