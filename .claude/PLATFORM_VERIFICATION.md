# Platform Verification System

**Issue:** #83
**Status:** Approved and Implemented
**Version:** 1.0

---

## Overview

All domain agents (Air-Side, Ground-Side, SystemTools) MUST verify they are running on the correct platform during session initialization and report mismatches immediately.

---

## Platform Requirements

| Domain | Expected Platform | Detection Method |
|--------|------------------|------------------|
| **Air-Side** | Raspberry Pi 5 Model B Rev 1.1 | `/proc/device-tree/model` |
| **Ground-Side** | Android H16 (SkyDroid) | `adb shell getprop ro.product.model` |
| **SystemTools** | Development Machine (Linux x86_64) | `uname -m` |
| **PM** | Development Machine (any) | No verification required |

---

## Session Start Protocol

### Step 1: Platform Detection

**Air-Side Detection:**
```bash
cat /proc/device-tree/model
# Expected: "Raspberry Pi 5 Model B Rev 1.1"
```

**Ground-Side Detection:**
```bash
adb shell getprop ro.product.model
# Expected: "H16" or similar
adb shell getprop ro.product.manufacturer
# Expected: "skydroid" (case-insensitive)
```

**SystemTools Detection:**
```bash
uname -m
# Expected: "x86_64" or "aarch64"
hostname
# Expected: Development machine name (not "dpm" or android device)
```

---

### Step 2: Report Current Status

**Every domain MUST report during session start:**

```markdown
Current Status:
- Location: /home/dpm/DPM-V2 (or actual path)
- Latest changes pulled: [X files changed, X insertions, X deletions]
- Open issues: [X total]
- WHO: CC-[Domain]
- System: [Detected platform]
- Platform Match: ✅ CORRECT or ❌ MISMATCH
```

**Example - Air-Side on Correct Platform:**
```markdown
Current Status:
- Location: /home/dpm/DPM-V2
- Latest changes pulled: Already up to date
- Open issues: 30 total
- WHO: CC-Air-Side
- System: Raspberry Pi 5 Model B Rev 1.1
- Platform Match: ✅ CORRECT
```

**Example - Air-Side on Wrong Platform:**
```markdown
Current Status:
- Location: /home/anthony/DPM-V2
- Latest changes pulled: Already up to date
- Open issues: 30 total
- WHO: CC-Air-Side
- System: x86_64 Linux (DEV-PC-Ubuntu)
- Platform Match: ❌ MISMATCH

⚠️ WARNING: I am WHO=CC-Air-Side but running on wrong system!
Expected: Raspberry Pi 5 Model B Rev 1.1
Actual: x86_64 Linux development machine

This may cause deployment issues. Please verify you want to continue.
```

---

### Step 3: User Confirmation (if mismatch)

If platform mismatch detected, agent MUST:
1. Report the mismatch clearly
2. Explain expected vs actual platform
3. Ask user: "Do you want me to continue anyway? (Y/N)"
4. Wait for explicit user approval before proceeding

---

## WHO Command Enhancement

When user sends `WHO` command, agent MUST respond with:

```markdown
WHO: CC-[Domain]
System: [Detected platform]
Working on: [Current issue or task]
Platform Status: ✅ CORRECT or ❌ MISMATCH ([Expected] vs [Actual])
```

**Example:**
```markdown
WHO: CC-Air-Side
System: Raspberry Pi 5 Model B Rev 1.1
Working on: Issue #72 - Phase 1 Foundation Infrastructure
Platform Status: ✅ CORRECT
```

---

## Platform Detection Commands Reference

### Air-Side (Raspberry Pi 5)

**Primary Detection:**
```bash
cat /proc/device-tree/model
```

**Fallback Detection:**
```bash
# Check architecture
uname -m  # Should be: aarch64

# Check hostname (usually "dpm" or similar)
hostname

# Check for Pi-specific files
ls /boot/firmware/config.txt 2>/dev/null && echo "Pi detected"
```

**Expected Output:**
- Model: `Raspberry Pi 5 Model B Rev 1.1` (may have null terminator)
- Architecture: `aarch64`
- Hostname: `dpm` or similar

---

### Ground-Side (Android H16)

**Primary Detection:**
```bash
adb shell getprop ro.product.model
```

**Additional Properties:**
```bash
adb shell getprop ro.product.manufacturer  # skydroid
adb shell getprop ro.product.device        # H16
adb shell getprop ro.build.version.sdk     # Android SDK version
```

**Expected Output:**
- Model: Contains "H16"
- Manufacturer: "skydroid" (case-insensitive)

---

### SystemTools (Development Machine)

**Primary Detection:**
```bash
uname -m  # x86_64 or aarch64
hostname  # Not "dpm", not android device
```

**Verification (should fail on Pi/Android):**
```bash
# NOT a Raspberry Pi
cat /proc/device-tree/model 2>/dev/null || echo "Not Pi: OK"

# NOT connected via ADB to itself
adb devices 2>/dev/null | grep -v "List of devices" | wc -l  # 0 = OK
```

**Expected Output:**
- Architecture: `x86_64` (or `aarch64` if Jetson)
- Hostname: Development machine name (e.g., "DEV-PC-Ubuntu")
- NOT a Raspberry Pi
- NOT an Android device

---

## Implementation Checklist

- [x] Platform detection commands identified
- [ ] Add platform verification to Air-Side session start
- [ ] Add platform verification to Ground-Side session start
- [ ] Add platform verification to SystemTools session start
- [ ] Update `docs/CC_READ_THIS_FIRST.md` with platform verification step
- [ ] Add WHO command enhancement to all domain agents
- [ ] Test platform verification on all three systems
- [ ] Document platform mismatch handling procedure

---

## Edge Cases

**Case 1: Jetson Orin NX (Future Dual-Platform Support)**
- Issue #52 implements dual-platform support
- When implemented, Air-Side should accept BOTH:
  - Raspberry Pi 5 Model B Rev 1.1
  - Jetson Orin NX (via platform detection logic)

**Case 2: Development Testing on Wrong Platform**
- User may intentionally test Air-Side code on dev machine
- Platform verification warns but allows continuation with explicit approval
- This is acceptable for development/testing purposes

**Case 3: Missing Detection Files**
- If `/proc/device-tree/model` doesn't exist, report as "Unknown Platform"
- Treat as mismatch and ask for user confirmation

---

## Success Criteria

✅ All domain agents report platform during session start
✅ Platform mismatches are detected and reported
✅ User is warned and asked for confirmation on mismatch
✅ WHO command includes platform information
✅ Documentation updated

---

**WHO:** CC-PM
**Last Updated:** 2025-11-13
