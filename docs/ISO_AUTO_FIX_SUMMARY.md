# ISO Auto Fix Summary

**Date:** 2025-10-28  
**Branch:** main  
**Status:** ✅ Fixed - Awaiting Android app testing

## Problem

ISO Auto and extended ISO values (50, 64, 80, 40000+) could not be set via the protocol.

## Root Cause

Extended ISO values require the **0x10000000 flag** in the Sony SDK, but the Air-Side code was sending raw decimal values.

### Camera's Expected Format (from diagnostic):
- ISO Auto:  `0xFFFFFFFF` ✓ (was correct)
- ISO 50:    `0x10000032` (was: 50) ✗
- ISO 64:    `0x10000040` (was: 64) ✗  
- ISO 80:    `0x10000050` (was: 80) ✗
- ISO 40000: `0x10009C40` (was: 40000) ✗
- ISO 51200: `0x1000C800` (was: 51200) ✗
- ISO 64000: `0x1000FA00` (was: 64000) ✗
- ISO 80000: `0x10013880` (was: 80000) ✗
- ISO 102400:`0x10019000` (was: 102400) ✗

## Fixes Applied

### 1. setProperty() - Extended ISO Encoding  
**File:** `sbc/src/camera/camera_sony.cpp:681-699`

```cpp
static const std::unordered_map<std::string, uint32_t> ISO_MAP = {
    {"auto",   0xFFFFFFFF},
    // Extended low ISO (need 0x10000000 flag)
    {"50",     0x10000032},    {"64",     0x10000040},    {"80",     0x10000050},
    // Standard ISO range (100-32000) - direct values
    {"100",    100},  ... {"32000",  32000},
    // Extended high ISO (need 0x10000000 flag)
    {"40000",  0x10009C40},   {"51200",  0x1000C800},
    {"64000",  0x1000FA00},   {"80000",  0x10013880},
    {"102400", 0x10019000}
};
```

### 2. getProperty() - Extended ISO Decoding
**File:** `sbc/src/camera/camera_sony.cpp:968-971`

Fixed mask from `0x0000FFFF` to `0x0FFFFFFF` to properly strip the extended flag:

```cpp
else if ((raw_value & 0x10000000) != 0) {
    uint32_t iso_value = raw_value & 0x0FFFFFFF;  // Strip top 4 bits (was 0x0000FFFF - wrong!)
    result = std::to_string(iso_value);
}
```

### 3. Diagnostic Logging
Added `logAvailableIsoValues()` to automatically query and log camera's ISO capabilities on connection.

## Testing Procedure

### From Android App:
1. Connect to camera
2. Set ISO to "auto" - should succeed
3. Set ISO to "50" - should succeed  
4. Set ISO to "102400" - should succeed

### Monitor Air-Side Logs:
```bash
docker logs -f payload-manager | grep -E "(Setting property|iso|0x)"
```

**Expected:** No "Invalid ISO value" errors  
**Expected:** Camera accepts the values

## Verification Commands

```bash
# Check current ISO from camera
docker logs payload-manager 2>&1 | grep "ISO DIAGNOSTIC"

# Monitor set_property commands
docker logs -f payload-manager | grep "set_property"
```

## Commits

- `4f06aba` - [FIX] CRITICAL: Correct ISO extended flag handling
- `bc3b8d5` - [FEAT] ISO diagnostic: Decode extended ISO flag
- `610d83b` - [FEAT] Add ISO diagnostic logging on camera connection

## Next Steps

1. ✅ Fixes committed to main
2. ⏳ Test from Android app
3. ⏳ Verify all 35 ISO values work
4. ⏳ If issues remain, branch to `ISO-FIX-AUTO`

## Camera Capabilities (Confirmed)

**Model:** Sony ILCE-1 (Alpha 1)  
**Available ISO Values:** 35 total
- auto
- 50, 64, 80 (extended low)
- 100-32000 (standard range)
- 40000, 51200, 64000, 80000, 102400 (extended high)

✅ All values now correctly encoded for Sony SDK
