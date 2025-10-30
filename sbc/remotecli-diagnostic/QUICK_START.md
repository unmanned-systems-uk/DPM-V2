# RemoteCli v2 - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Build
```bash
cd ~/DPM-V2/sbc/remotecli-diagnostic
./build_remotecli.sh
```
⏱️ Takes ~5-10 minutes

### Step 2: Connect Camera
1. Power ON Sony camera
2. Connect USB cable
3. Set to **PC Remote** mode
4. Verify: `lsusb | grep -i sony`

### Step 3: Run
```bash
./run_remotecli.sh
```

---

## 📝 Common Commands

### Build Container
```bash
./build_remotecli.sh
```

### Run Diagnostic Tool
```bash
./run_remotecli.sh           # Normal mode
./run_remotecli.sh -i        # Interactive shell
```

### View Logs
```bash
cat logs/remotecli_v2.log           # Full log
tail -f logs/remotecli_v2.log       # Follow live
grep ERROR logs/remotecli_v2.log    # Errors only
```

---

## 🔧 Troubleshooting

### No Camera Detected
```bash
# Check USB
lsusb | grep -i sony

# Check USB buffer
cat /sys/module/usbcore/parameters/usbfs_memory_mb
# Should be 150

# Stop other camera processes
docker stop payload-manager
```

### Connection Failed
```bash
# Stop conflicting processes
docker ps
docker stop payload-manager

# Restart camera
# Try again
./run_remotecli.sh
```

### Build Failed
```bash
# Check Sony SDK location
ls ~/CrSDK_v2.00.00_20250805a_Linux64ARMv8

# Check Docker
docker ps

# Check disk space
df -h
```

---

## 📊 Diagnostic Menu

Once connected:
1. **Get camera properties** - View current settings
2. **Take photo** - Test shutter control
3. **Display info** - Check connection status
4. **Test property access** - Diagnose property issues
5. **Disconnect** - Clean exit

---

## 🎯 Quick Diagnostic Workflow

```bash
# 1. Build container (one-time)
./build_remotecli.sh

# 2. Run diagnostic
./run_remotecli.sh

# 3. In menu: select camera
# 4. Test functionality (options 1-4)
# 5. Disconnect (option 5)

# 6. Review logs
cat logs/remotecli_v2.log
```

---

## 📱 When to Use

✅ **Use RemoteCli v2 for:**
- Camera connection issues
- SDK initialization problems
- Property access debugging
- Baseline functionality testing

❌ **Use Payload Manager for:**
- Production operation
- H16 communication
- Network protocol testing
- Continuous service

---

**Full Documentation:** See `README.md`
