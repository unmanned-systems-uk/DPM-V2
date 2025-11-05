# Quick Start: Log Download

## 🚀 Immediate Next Steps

### 1. Rebuild Container (5 minutes)

```bash
cd /home/dpm/DPM-V2/sbc
./build_container.sh
docker stop payload-manager && docker rm payload-manager
./run_container.sh prod
```

### 2. Verify Logging Works

```bash
# Check log file exists
ls -lh /home/dpm/DPM-V2/sbc/logs/payload_manager.log

# Watch it grow
tail -f /home/dpm/DPM-V2/sbc/logs/payload_manager.log
```

### 3. Test Download from WindowsTools

1. Open WindowsTools on PC
2. Go to **Log Inspector** tab
3. Click **Connect SSH**
4. Enter: `dpm@192.168.144.10` (password: your password)
5. Click **Download Log File...** button
6. Save to PC

---

## 📋 What Was Changed

### Files Modified:
- ✅ `sbc/src/config.h` - Fixed log path
- ✅ `WindowsTools/network/ssh_client.py` - Added SFTP
- ✅ `WindowsTools/gui/tab_logs.py` - Added download button

### No Rebuild Needed:
- ✅ WindowsTools ready to use immediately
- ⚠️ Air-side needs rebuild for logging to work

---

## 🔧 When RTC Battery Arrives

1. Power off Pi completely
2. Locate J5 connector (near GPIO, labeled "RTC")
3. Plug in JST battery connector
4. Power on with internet (sync time once)
5. Test: Power off → wait 10 min → power on without internet
6. Verify time is correct

**Result:** No more timestamp issues!

---

## 📁 Log File Locations

### On Raspberry Pi:
```
/home/dpm/DPM-V2/sbc/logs/payload_manager.log
```

### After Download (Windows):
```
Documents/payload_manager_YYYYMMDD_HHMMSS.log
```

---

## 🎯 Per-Flight Workflow

### Before Flight:
```bash
# Optional: Archive previous log
cd /home/dpm/DPM-V2/sbc/logs
cp payload_manager.log payload_manager_backup_$(date +%Y%m%d).log

# Optional: Clear for fresh flight log
> payload_manager.log
```

### After Flight:
1. Open WindowsTools on ground PC
2. Connect SSH to Pi
3. Click "Download Log File..."
4. Save as: `flight_YYYYMMDD_location_conditions.log`
5. Document in flight logbook

---

## ❓ Quick Troubleshooting

**"Download Failed"**
→ Check container rebuilt: `docker ps` should show `payload-manager`
→ Check file exists: `ls /home/dpm/DPM-V2/sbc/logs/`

**"Log File Empty"**
→ Container might not be rebuilt yet
→ Check: `docker logs payload-manager | grep "Log file"`

**"Wrong Timestamps"**
→ Normal until RTC battery installed
→ After battery: timestamps will be correct

---

## 📞 See Full Documentation

**Complete Details:** `/home/dpm/DPM-V2/docs/LOG_DOWNLOAD_SOLUTION.md`

**Current Status:**
- ✅ Code changes complete
- ⏳ Awaiting container rebuild
- ⏳ Awaiting RTC battery delivery
