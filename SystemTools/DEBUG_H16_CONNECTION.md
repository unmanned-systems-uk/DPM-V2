# H16 → SystemTools Connection Debug Guide

**WHO:** CC-Dev-Tools
**Date:** 2025-11-15
**Issue:** #99 - H16 not connecting to SystemTools on port 5008

## Status Summary

✅ **SystemTools (10.0.1.83) is listening on port 5008**
✅ **H16 (10.0.1.92) is configured to connect to 10.0.1.83:5008**
✅ **Network connectivity verified (ping successful)**
❓ **H16 not connecting - need to verify H16-side status**

---

## 1. Verify H16 App is Running

### Check via ADB:
```bash
adb connect 10.0.1.92:5555
adb shell dumpsys activity activities | grep -i dpm
```

**Expected:** Should show DPM app is running

---

## 2. Check H16 NetworkSink Status

### View H16 Logs:
```bash
adb logcat -s DPM:V NetworkSink:V
```

**Look for:**
- `"NetworkSink initialized"` - Sink created
- `"Connecting to <host>:<port>"` - Connection attempts
- `"Connected successfully"` - Connection established
- `"Connection failed"` or socket errors - Connection issues

---

## 3. Verify H16 Settings

The H16 NetworkSink reads settings from SettingsRepository:
- **Host:** Should be `10.0.1.83` (your dev machine)
- **Port:** Should be `5008`
- **Enabled:** Should be `true` (DEBUG builds only)

### Check Settings via Logcat:
```bash
adb logcat -s DPM:D | grep -i "systemtools"
```

**Look for:** Log messages showing the configured host/port

---

## 4. Test H16 → SystemTools Connection Manually

### From H16 (via ADB shell):
```bash
adb shell
# Try to connect to SystemTools from H16
nc -v 10.0.1.83 5008
# OR
telnet 10.0.1.83 5008
```

**Expected:** Should connect successfully
**If fails:** Network/firewall issue between H16 and SystemTools

---

## 5. Monitor SystemTools for Connection Attempts

### Watch SystemTools logs in real-time:
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 log_viewer_gui.py
# Click "Start" button
# Watch console output for:
# [GroundSideListener] TCP server listening on 0.0.0.0:5008
# [GroundSideListener] Waiting for Ground-Side (H16) to connect...
# [GroundSideListener] Client connected from <H16_IP>:<PORT>
```

### Alternative - Use test script:
```bash
cd /home/anthony/DPM-V2/SystemTools
python3 test_tcp_server.py
# Leave this running
# Then trigger H16 connection
```

---

## 6. Check for Firewall Issues

### SystemTools (Linux) Firewall:
```bash
sudo ufw status
# If active, allow port 5008:
sudo ufw allow 5008/tcp
```

### H16 (Android) - Usually no firewall, but check:
- Android doesn't typically block outgoing connections
- Check if H16 has any firewall/security apps installed

---

## 7. Force H16 Reconnection

The NetworkSink may be in a retry backoff state. To force reconnection:

### Option A - Restart DPM App:
```bash
adb shell am force-stop uk.unmannedsystems.dpm_android
adb shell am start -n uk.unmannedsystems.dpm_android/.MainActivity
```

### Option B - Toggle NetworkSink in Settings:
- If the app has a settings UI, disable/enable SystemTools logging

---

## 8. Check NetworkSink Implementation

The H16 NetworkSink should:
1. **Auto-connect** on app start (if enabled)
2. **Auto-reconnect** every 5 seconds on disconnect
3. **Queue logs** (up to 1000) when disconnected

### Source: `/home/anthony/DPM-V2/android/app/src/main/java/uk/unmannedsystems/dpm_android/logging/sinks/NetworkSink.kt`

**Reconnection Logic:**
- Initial retry: 5 seconds
- Backoff: 10 seconds max

---

## 9. Common Issues

### Issue: "Connection refused" from H16
**Cause:** SystemTools not listening on port 5008
**Fix:** Start log_viewer_gui.py and click "Start"

### Issue: "No route to host" from H16
**Cause:** Network/firewall blocking
**Fix:** Check firewall rules, verify IP addresses

### Issue: "Connection timeout" from H16
**Cause:** H16 can't reach SystemTools IP
**Fix:** Verify 10.0.1.83 is the correct IP, check routing

### Issue: H16 connecting to wrong IP
**Cause:** Old settings cached
**Fix:** Check H16 settings, force app restart

### Issue: NetworkSink disabled
**Cause:** Release build or setting disabled
**Fix:** Use DEBUG build, check `systemToolsLogEnabled` setting

---

## 10. Quick Test Sequence

```bash
# Terminal 1 (SystemTools):
cd /home/anthony/DPM-V2/SystemTools
python3 test_tcp_server.py

# Terminal 2 (H16 via ADB):
adb connect 10.0.1.92:5555
adb shell am force-stop uk.unmannedsystems.dpm_android
adb shell am start -n uk.unmannedsystems.dpm_android/.MainActivity
adb logcat -s DPM:V NetworkSink:V

# Watch Terminal 1 for: "CLIENT CONNECTED from 10.0.1.92:xxxxx"
# Watch Terminal 2 for: "Connected successfully" or error messages
```

---

## Expected Console Output (Success)

### SystemTools Console:
```
[GroundSideListener] TCP server listening on 0.0.0.0:5008
[GroundSideListener] Waiting for Ground-Side (H16) to connect...
[GroundSideListener] Client connected from 10.0.1.92:45678
[GROUND] [INFO] [STARTUP] DPM Application started
[GROUND] [INFO] [NETWORK] NetworkSink connected
```

### H16 Logcat:
```
D/NetworkSink: NetworkSink initialized (host=10.0.1.83, port=5008, enabled=true)
D/NetworkSink: Connecting to 10.0.1.83:5008...
I/NetworkSink: Connected successfully to 10.0.1.83:5008
D/NetworkSink: Sent log entry: {...}
```

---

## Next Steps

1. **Start log_viewer_gui.py** (if not already running) and click "Start"
2. **Run H16 app** and check logcat for NetworkSink status
3. **Check this debug guide** for specific error messages
4. **Report findings** - What error messages do you see on H16 side?

---

**Last Updated:** 2025-11-15 15:35 UTC
**Status:** SystemTools server confirmed listening, awaiting H16 connection attempts
