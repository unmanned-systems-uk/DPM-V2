# Ground-Side Value Format Reference
**Quick Guide for Android Implementation**

**Date:** October 25, 2025
**Status:** Phase 1 - 8 Properties Implemented on Air-Side

---

## ✅ Implemented Properties (Air-Side Ready)

All 8 Phase 1 properties are now implemented and ready for ground-side UI implementation.

---

## 📋 Value Formats to Send

### 1. **shutter_speed**
**Send as:** Human-readable string
**Control Type:** Dropdown

**Valid Values:**
```
"auto", "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250",
"1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "1/2", "1", "2",
"4", "8", "15", "30"
```

**Example:**
```kotlin
networkClient.setCameraProperty("shutter_speed", "1/250")
```

---

### 2. **aperture**
**Send as:** Human-readable string with "f/" prefix
**Control Type:** Dropdown

**Valid Values:**
```
"auto", "f/1.4", "f/2.0", "f/2.8", "f/4.0", "f/5.6", "f/8.0",
"f/11", "f/16", "f/22"
```

**Example:**
```kotlin
networkClient.setCameraProperty("aperture", "f/2.8")
```

---

### 3. **iso**
**Send as:** String (not integer!)
**Control Type:** Dropdown

**Valid Values:**
```
"auto", "100", "200", "400", "800", "1600", "3200", "6400",
"12800", "25600", "51200", "102400"
```

**Example:**
```kotlin
networkClient.setCameraProperty("iso", "800")  // String, not integer!
```

---

### 4. **white_balance**
**Send as:** Preset name string
**Control Type:** Dropdown

**Valid Values:**
```
"auto", "daylight", "shade", "cloudy", "tungsten",
"fluorescent_warm", "fluorescent_cool", "fluorescent_day",
"fluorescent_daylight", "flash", "temperature", "custom"
```

**Example:**
```kotlin
networkClient.setCameraProperty("white_balance", "daylight")
```

---

### 5. **white_balance_temperature**
**Send as:** Kelvin value as string
**Control Type:** Slider (2500-9900 in 100K steps)

**Valid Range:** 2500 to 9900
**Dependency:** white_balance must be set to "temperature" first

**Example:**
```kotlin
// First set WB mode to temperature
networkClient.setCameraProperty("white_balance", "temperature")
// Then set temperature
networkClient.setCameraProperty("white_balance_temperature", "5500")
```

---

### 6. **focus_mode**
**Send as:** Mode name string
**Control Type:** Segmented Control / Radio Group

**Valid Values:**
```
"af_s"    // Single AF
"af_c"    // Continuous AF
"af_a"    // Automatic AF
"dmf"     // Direct Manual Focus
"manual"  // Manual Focus
```

**Example:**
```kotlin
networkClient.setCameraProperty("focus_mode", "af_s")
```

---

### 7. **file_format**
**Send as:** Format name string
**Control Type:** Segmented Control / Radio Group

**Valid Values:**
```
"jpeg"      // JPEG only
"raw"       // RAW only
"jpeg_raw"  // JPEG + RAW
```

**Example:**
```kotlin
networkClient.setCameraProperty("file_format", "jpeg_raw")
```

---

### 8. **drive_mode**
**Send as:** Mode name string
**Control Type:** Dropdown

**Valid Values:**
```
"single"          // Single shot
"continuous_lo"   // Continuous low speed
"continuous_hi"   // Continuous high speed
"self_timer_10s"  // Self timer 10 seconds
"self_timer_2s"   // Self timer 2 seconds
"bracket"         // Bracket shooting
```

**Example:**
```kotlin
networkClient.setCameraProperty("drive_mode", "continuous_hi")
```

---

## 🎯 Key Points for Implementation

1. **All values are strings** - Even numeric values like ISO must be sent as strings ("800" not 800)

2. **Use exact strings** - Values are case-sensitive and must match exactly

3. **Validation is optional** - Air-side validates all values, but client-side validation improves UX

4. **Get values from JSON** - Load dropdown values from `camera_properties.json` validation section

5. **Dependencies matter** - white_balance_temperature requires white_balance="temperature" first

---

## ✅ Implementation Checklist

### For Each Property:

- [ ] Create UI control based on `ui_hints.control_type` in camera_properties.json
- [ ] Load valid values from `validation.values` section
- [ ] Send values as strings using exact format shown above
- [ ] Test end-to-end with air-side before marking as implemented
- [ ] Update camera_properties.json `ground_side: true` after testing

---

## 📖 See Also

- `docs/protocol/camera_properties.json` - Full property definitions
- `docs/protocol/PROTOCOL_VALUE_MAPPING.md` - Complete mapping tables
- `docs/protocol/PROTOCOL_VALUE_MAPPING_QUICK_REF.md` - Quick reference guide

---

**Maintained by:** DPM Team
**Last Updated:** October 25, 2025
**Air-Side Status:** ✅ All 8 Phase 1 properties implemented
