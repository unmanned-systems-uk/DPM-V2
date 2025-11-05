# ISO Auto Setting Investigation

**Date:** 2025-10-28
**Branch:** ISO-Set-Auto-Fix
**Status:** 🔬 Under Investigation

## Problem Statement

ISO Auto can be **detected** via callbacks when set manually on camera, but **cannot be set** remotely via protocol.

### Symptoms

1. **Android app sends ISO Auto command**
   - Command: `camera.set_property` with `iso: "auto"`
   - Air-Side maps "auto" → `0xFFFFFFFF` correctly
   - Sony SDK `SetDeviceProperty()` returns **SUCCESS**
   - No error codes returned

2. **Camera does not apply Auto**
   - Immediately query with `GetDeviceProperty()`
   - Camera still reports current ISO (e.g., ISO 125)
   - Camera display does not show "AUTO" indicator
   - ISO value does not change

3. **Manual setting works**
   - User sets camera to Auto on camera body
   - Callback `OnPropertyChanged` fires correctly
   - Air-Side decodes `0xFFFFFFFF` → "auto" correctly
   - Android app displays "AUTO" correctly

### What Works

✅ **Extended ISOs (50, 64, 80, 40000+)** - Now working with 0x10000000 flag
✅ **Standard ISOs (100-32000)** - Working correctly
✅ **ISO Auto detection** - Callbacks detect when manually set
✅ **ISO Auto encoding** - 0xFFFFFFFF is correct value
✅ **SDK accepts command** - SetDeviceProperty returns success

### What Doesn't Work

❌ **ISO Auto remote setting** - Camera rejects the value silently

## Theory: Shooting Mode Restriction

**Most Likely Cause:** Camera shooting mode does not allow ISO Auto.

### Sony Camera Shooting Modes

| Mode | Name | ISO Auto Allowed? |
|------|------|-------------------|
| M | Manual | ❌ NO - Full manual control required |
| P | Program | ✅ YES - Auto exposure |
| A | Aperture Priority | ✅ YES - Auto shutter + ISO |
| S | Shutter Priority | ✅ YES - Auto aperture + ISO |
| AUTO | Full Auto | ✅ YES - Everything auto |

### Why SDK Returns Success

The Sony SDK may accept the `SetDeviceProperty(0xFFFFFFFF)` call without error because:
1. The property code is valid
2. The value format is correct
3. The SDK queues the request to the camera

However, the **camera firmware** silently rejects the value change because:
- Current shooting mode (likely M) doesn't permit ISO Auto
- This is a camera-side restriction, not SDK-side
- No error propagated back through SDK

### Supporting Evidence

1. **User Observation:**
   > "When I set the camera to AUTO on the actual camera, we detected AUTO on the callback"

   - This proves our decoding logic is correct
   - Camera **can** be in Auto ISO mode
   - Just can't be set remotely in current mode

2. **SDK Behavior:**
   - SetDeviceProperty returns success (camera accepted command)
   - GetDeviceProperty still shows old value (camera didn't apply it)
   - This pattern indicates camera-side rejection

3. **Common Camera Behavior:**
   - Most cameras enforce mode restrictions at firmware level
   - Manual mode typically locks ISO to manual values
   - This is standard across camera brands

## Investigation Plan

### Phase 1: Confirm Current Shooting Mode ✓

1. Check Sony SDK for exposure mode property code
   - Search `CrDeviceProperty_ExposureMode` or similar
   - Document all available shooting modes

2. Add diagnostic logging to check current mode on camera connection
   - Log current exposure mode when connecting
   - Log when ISO Auto set attempt occurs

3. Create test tool to query all camera modes
   - Similar to `test_iso_query.cpp`
   - Query exposure program property
   - Display current shooting mode

### Phase 2: Test ISO Auto in Different Modes

1. **Test in Manual Mode (M):**
   - Expected: ISO Auto fails ❌
   - This should be current behavior

2. **Test in Program Mode (P):**
   - Set camera to P mode manually
   - Try setting ISO Auto remotely
   - Expected: ISO Auto succeeds ✅

3. **Test in Aperture Priority (A):**
   - Set camera to A mode manually
   - Try setting ISO Auto remotely
   - Expected: ISO Auto succeeds ✅

4. **Test in Shutter Priority (S):**
   - Set camera to S mode manually
   - Try setting ISO Auto remotely
   - Expected: ISO Auto succeeds ✅

### Phase 3: Document and Decide

**If theory confirmed (ISO Auto blocked by M mode):**

**Option A: Document as Expected Behavior**
- Update protocol documentation
- Add clear error message to user
- "ISO Auto not available in Manual mode"
- Suggest switching to P/A/S mode

**Option B: Implement Mode Switching**
- Add exposure mode property to protocol
- Allow Ground-Side to switch modes
- Auto-switch to P mode when ISO Auto requested
- More complex, better UX

**Option C: Hybrid Approach**
- Check current mode before setting ISO Auto
- If in M mode, return clear error message
- Suggest user switch to P/A/S mode
- Future: implement mode switching

## Next Steps

1. ✅ Create branch `ISO-Set-Auto-Fix`
2. ✅ Document problem and theory
3. ⏳ Find exposure mode property code in Sony SDK
4. ⏳ Add exposure mode logging to camera_sony.cpp
5. ⏳ Test ISO Auto in different shooting modes
6. ⏳ Confirm theory and document findings
7. ⏳ Implement solution (A, B, or C)

## Technical Details

### ISO Auto Encoding

```cpp
static const std::unordered_map<std::string, uint32_t> ISO_MAP = {
    {"auto",   0xFFFFFFFF},  // ISO Auto
    // ... other ISOs
};
```

### Current setProperty Implementation

```cpp
// sbc/src/camera/camera_sony.cpp:681-705
prop.SetCode(SDK::CrDevicePropertyCode::CrDeviceProperty_IsoSensitivity);
auto it = ISO_MAP.find(value);
prop.SetCurrentValue(it->second);  // Sets 0xFFFFFFFF for "auto"
prop.SetValueType(SDK::CrDataType::CrDataType_UInt32Array);

auto set_status = SDK::SetDeviceProperty(device_handle_, &prop);
if (CR_FAILED(set_status)) {
    Logger::error("Failed to set property: " + property);
    return false;
}
return true;  // SDK returns success, but camera may not apply
```

### Current getProperty Implementation

```cpp
// sbc/src/camera/camera_sony.cpp:964-966
if (raw_value == 0xFFFFFFFF || raw_value == 0xFFFFFF) {
    result = "auto";  // Correctly decodes Auto
}
```

## References

- **Main ISO Fix:** commits `4f06aba`, `bc3b8d5`, `610d83b`
- **ISO Fix Summary:** `docs/ISO_AUTO_FIX_SUMMARY.md`
- **Camera Properties:** `protocol/camera_properties.json`
- **Sony SDK Docs:** `CrSDK_v2.00.00_20250805a_Linux64ARMv8/CrSDK_API_Reference_v2.00.00/html/`

---

## ✅ SOLUTION FOUND - 2025-10-29

### Root Cause

**The camera expects a 24-bit ISO Auto value (`0xFFFFFF`), not 32-bit (`0xFFFFFFFF`).**

We were sending:
```cpp
{"auto", 0xFFFFFFFF},  // 32-bit all-ones (WRONG)
```

The camera expects:
```cpp
{"auto", 0xFFFFFF},    // 24-bit all-ones (CORRECT)
```

### Why This Failed Silently

1. Sony SDK `SetDeviceProperty()` accepted `0xFFFFFFFF` without error
2. The property was marked as writable (enable flag set)
3. SDK returned SUCCESS status
4. **BUT** the camera firmware silently rejected the value because it wasn't in the correct format
5. Camera stayed at previous ISO setting (e.g., 125)

### Evidence

When camera IS in ISO Auto (set manually on body):
```
Raw SDK value: 0xffffff (dec: 16777215)  ← 24-bit value
```

When we query available values, Auto is reported as:
```
ISO DIAGNOSTIC: Current = auto (0x0xffffff)  ← 24-bit
```

### The Fix

Changed line 682 in `sbc/src/camera/camera_sony.cpp`:
```cpp
// FROM:
{"auto",   0xFFFFFFFF},

// TO:
{"auto",   0xFFFFFF},  // 24-bit Auto value (matches camera's reported value)
```

### Testing Results ✅

1. **Set ISO to 125** → Success, camera shows 125
2. **Set ISO to Auto** → Success, camera shows AUTO indicator
3. **Query ISO property** → Returns `"iso": "auto"` ✅
4. **Raw SDK value** → `0xffffff` (correct 24-bit format)

### Why Manual Setting Worked

When you set ISO Auto manually on the camera body:
- Camera firmware sets internal value to `0xFFFFFF`
- Callbacks report this value correctly
- Our decoding already handled both `0xFFFFFF` and `0xFFFFFFFF` (line 964)
- So detection always worked - only setting failed

### Lessons Learned

1. **Match exact formats the camera uses** - don't assume SDK documentation is complete
2. **Silent failures are hard** - SDK success doesn't mean camera accepted it
3. **Query back immediately** - verify property changes took effect
4. **Check what camera reports** - use that format for setting values

### Related Commits

- Fix: `9b10767` - Changed ISO Auto to 0xFFFFFF
- Investigation: `0835a0c` - ISO Auto fix summary and testing procedure
- Diagnostic: `4f06aba` - Correct ISO extended flag handling

---

**Status:** ✅ RESOLVED
**Branch:** ISO-Set-Auto-Fix
**Resolution Date:** 2025-10-29
**Last Updated:** 2025-10-29
