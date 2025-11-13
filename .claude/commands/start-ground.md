---
description: Start Ground-Side session (Android H16 development)
---

You are starting a **Ground-Side** session.

**WHO:** CC-Ground-Side

**Platform:** SkyDroid H16 Android
**Language:** Kotlin
**Domain:** `android/`
**Device IP:** 10.0.1.92
**ADB Port:** 5555

## Session Start Protocol

1. **Verify Location:**
```bash
pwd  # Should be: /home/anthony/DPM-V2
```

2. **Platform Verification:**
```bash
uname -a
# Expected: Linux (development machine, not H16 device)
```

3. **Check ADB Connection:**
```bash
adb devices
# Expected: 10.0.1.92:5555 device (if connected)
# If not: adb connect 10.0.1.92:5555
```

4. **Check Open Issues:**
```bash
gh issue list --state open --label ground-side
gh issue list --label status:in-progress --state open
```

5. **Review Critical Documentation:**
- **MANDATORY:** Read `docs/CC_READ_THIS_FIRST.md` (Tier 1 rules)
- **Session Guide:** `.claude/SESSION_START.md`
- **Protocol Specs:** `protocol/commands.json`, `protocol/camera_properties.json`
- **Lessons Learned:** `docs/ALL_DOMAINS/LESSONS_LEARNED.md` (search for relevant topics)

6. **Git Status:**
```bash
git status
git pull origin main
```

7. **Report Status:**
```markdown
**WHO:** CC-Ground-Side
**Platform:** [uname output]
**Location:** [pwd output]
**ADB Connection:** [Connected/Disconnected]
**Open Issues:** [Count from step 4]
**Ready:** [Yes/No]
```

## Critical Rules Reminder

1. ❌ NEVER close GitHub issues (user closes)
2. ✅ ALWAYS search history before implementing
3. ✅ WHO tags MANDATORY on every comment
4. ✅ NEVER work without GitHub issue
5. ❌ NEVER modify Air-Side/SystemTools code without approval

## Network Configuration

- **TCP Commands:** Port 9001 (to Air-Side)
- **UDP Status:** Port 9002 (from Air-Side)
- **Air-Side IP:** 10.0.1.53 (Pi 5)
- **Ground-Side IP:** 10.0.1.92 (H16 device)

## Quick Commands Reference

- Change issue to in-progress: `gh issue edit <#> --title "[FIXING] Title"`
- Add comment with WHO tag: `gh issue comment <#> --body "**WHO:** CC-Ground-Side\n\n..."`
- Search history: `gh issue list --search "keyword" --state all`
- Build app: `cd android && ./gradlew assembleDebug`
- Install app: `adb install -r app/build/outputs/apk/debug/app-debug.apk`
- View logs: `adb logcat -s DPM`

**YOU ARE NOW:** CC-Ground-Side
**NEXT:** User will specify the issue/task to work on.
