# Air-Side RTC Integration Test Plan
**WHO:** CC-PM → CC-Air-Side
**Issue:** #47
**Hardware:** CR1220 RTC battery installed on Pi 5
**Date:** 2025-11-13

---

## 🎯 Objective

Integrate and verify RTC (Real-Time Clock) functionality on Raspberry Pi 5 to enable accurate log timestamps during flight tests without internet connectivity.

---

## 📋 Prerequisites

- ✅ CR1220 battery installed in Pi 5 RTC socket
- ✅ SSH access to Pi 5 (10.0.1.53)
- ✅ Sudo permissions
- ✅ Internet connectivity (for initial NTP sync)

---

## 🔬 Test Phases

### Phase 1: Hardware Verification (5 min)

**Commands:**
```bash
# Connect to Pi 5
ssh dpm@10.0.1.53

# Check RTC device files
ls -l /dev/rtc*
# Expected output:
# lrwxrwxrwx 1 root root 4 Nov 13 XX:XX /dev/rtc -> rtc0
# crw------- 1 root root 251, 0 Nov 13 XX:XX /dev/rtc0

# Check RTC hardware clock
sudo hwclock --show
# Expected: Either current time OR unset time (if new battery)

# Check system time
date
# Note current system time

# Check if times sync
sudo hwclock --systohc  # Write system to hardware
sudo hwclock --show     # Read back hardware time
```

**Success Criteria:**
- [ ] `/dev/rtc0` device exists
- [ ] `hwclock --show` returns a time (not error)
- [ ] No permission errors

**Failure Handling:**
- If `/dev/rtc*` not found → Check battery installation
- If permission errors → Verify sudo access
- If device errors → Check kernel modules: `lsmod | grep rtc`

---

### Phase 2: Boot Configuration (5 min)

**Commands:**
```bash
# Backup existing config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup

# Edit boot config
sudo nano /boot/firmware/config.txt

# Search for existing rtc settings (Ctrl+W, search "rtc")
# If not found, add at end:
dtparam=rtc=on

# Alternative if above doesn't work:
# dtoverlay=i2c-rtc,pcf85063a

# Save and exit (Ctrl+X, Y, Enter)

# Verify change
grep rtc /boot/firmware/config.txt
```

**Success Criteria:**
- [ ] Backup created
- [ ] RTC enabled in config.txt
- [ ] Change verified with grep

**Notes:**
- Change takes effect after reboot (done in Phase 4)
- Pi 5 uses PCF85063A RTC chip

---

### Phase 3: Initial Time Synchronization (10 min)

**Commands:**
```bash
# Verify internet connectivity
ping -c 3 8.8.8.8
# Must succeed for NTP sync

# Check current timedatectl status
timedatectl status

# Enable NTP synchronization
sudo timedatectl set-ntp true

# Wait for NTP sync (check status)
sleep 10
timedatectl status
# Look for "System clock synchronized: yes"

# Verify system time is correct
date
# Should show current time (check against phone/computer)

# Write system time to RTC hardware
sudo hwclock --systohc

# Verify RTC now has correct time
sudo hwclock --show

# Compare times (should match within 1 second)
echo "System time: $(date)"
echo "RTC time: $(sudo hwclock --show)"
```

**Success Criteria:**
- [ ] Internet reachable
- [ ] NTP sync successful
- [ ] System time correct
- [ ] RTC time correct
- [ ] Times match within 1 second

**Troubleshooting:**
- If NTP won't sync: `sudo systemctl restart systemd-timesyncd`
- If times don't match: Repeat `hwclock --systohc`

---

### Phase 4: Reboot Persistence Test (10 min)

**Commands:**
```bash
# Before reboot - record current time
echo "Pre-reboot system: $(date)"
echo "Pre-reboot RTC: $(sudo hwclock --show)"

# Initiate reboot
sudo reboot

# Wait ~60 seconds for Pi to reboot
# ...

# Reconnect via SSH
ssh dpm@10.0.1.53

# Check system time immediately
date

# Check RTC time
sudo hwclock --show

# Compare with expected time (should be ~1-2 min after pre-reboot time)
# Verify NOT reset to 1970 or random date

# Check time synchronization status
timedatectl status
```

**Success Criteria:**
- [ ] Pi reboots successfully
- [ ] System time survived reboot (not reset to epoch)
- [ ] RTC time matches system time
- [ ] Time advanced correctly (matches wall clock)

**Critical Test:**
- System time should be ACCURATE, not 1970-01-01
- If time correct → RTC working!

---

### Phase 5: Docker Container Time Verification (5 min)

**Commands:**
```bash
# Check if payload-manager container running
docker ps | grep payload-manager

# If not running, start it
cd ~/DPM-V2/sbc
docker-compose up -d

# Check container system time
docker exec payload-manager date

# Check host system time
date

# Compare (should match exactly)
echo "Host time: $(date)"
echo "Container time: $(docker exec payload-manager date)"

# Check Docker logs for timestamps
docker logs --tail 20 payload-manager

# Verify log timestamps are current (not from 1970)
```

**Success Criteria:**
- [ ] Container running
- [ ] Container time matches host time
- [ ] Log timestamps accurate (current date/time)
- [ ] No 1970 timestamps in logs

---

### Phase 6: Network-Independent Test (5 min)

**OPTIONAL BUT RECOMMENDED:**

```bash
# Disconnect from network temporarily
# (Skip this if testing remotely via SSH)

# Alternative: Disable NTP only
sudo timedatectl set-ntp false

# Wait 30 seconds
sleep 30

# Generate test log entry
echo "Test log entry at $(date)" | logger

# Check system time still accurate
date

# Check RTC time
sudo hwclock --show

# Re-enable NTP
sudo timedatectl set-ntp true

# Check logs
journalctl -n 10

# Verify test log has accurate timestamp
```

**Success Criteria:**
- [ ] Time remains accurate without NTP
- [ ] RTC maintains time
- [ ] Logs have accurate timestamps

---

## 📊 Final Validation Checklist

- [ ] RTC hardware detected (`/dev/rtc0` exists)
- [ ] Boot config enabled (`dtparam=rtc=on`)
- [ ] Initial time set from NTP
- [ ] Time persists across reboot (not reset to 1970)
- [ ] Docker container uses correct time
- [ ] Application logs have accurate timestamps
- [ ] Time maintained without active internet

---

## 📝 Documentation Required

After testing complete, update issue #47 with:

```markdown
**WHO:** CC-Air-Side

## RTC Integration Test Results

**Date:** 2025-11-13
**Hardware:** Pi 5 with CR1220 RTC battery

### Phase Results

**Phase 1 - Hardware Verification:**
- RTC Device: [PASS/FAIL]
- Output: [paste `ls -l /dev/rtc*`]

**Phase 2 - Boot Config:**
- Config Updated: [PASS/FAIL]
- Setting: [paste grep output]

**Phase 3 - Time Sync:**
- NTP Sync: [PASS/FAIL]
- System Time: [paste date]
- RTC Time: [paste hwclock output]

**Phase 4 - Reboot Test:**
- Time Persisted: [PASS/FAIL]
- Post-reboot time: [paste date]

**Phase 5 - Docker Verification:**
- Container Time: [PASS/FAIL]
- Log Timestamps: [PASS/FAIL]

**Phase 6 - Network Independent:**
- Offline Time Accuracy: [PASS/FAIL]

### Overall Result: [PASS/FAIL]

### Issues Encountered:
[None / List any issues]

### Next Steps:
[Ready for flight test / Needs additional work]
```

---

## 🚨 Common Issues & Solutions

### Issue: `/dev/rtc*` not found
**Solution:**
- Check battery properly seated
- Verify kernel module: `lsmod | grep rtc`
- Load module if needed: `sudo modprobe rtc-pcf85063`

### Issue: Permission denied on hwclock
**Solution:**
- Use sudo: `sudo hwclock --show`
- Check user in required groups: `groups`

### Issue: Time resets after reboot
**Solution:**
- Verify boot config saved: `grep rtc /boot/firmware/config.txt`
- Check battery voltage: Battery might be dead
- Re-run hwclock --systohc after each boot until persists

### Issue: Docker container wrong time
**Solution:**
- Restart container: `docker restart payload-manager`
- Check container timezone: `docker exec payload-manager cat /etc/timezone`
- Verify host time correct first

### Issue: NTP won't sync
**Solution:**
- Check DNS: `nslookup pool.ntp.org`
- Restart timesyncd: `sudo systemctl restart systemd-timesyncd`
- Check firewall: NTP uses UDP port 123

---

## 🎯 Success Definition

**RTC integration successful when:**
1. Pi 5 reboots without internet
2. System time is accurate (current date/time)
3. Docker logs have correct timestamps
4. Time doesn't reset to 1970

**Why this matters:**
- Flight tests often have no internet connectivity
- Accurate timestamps critical for log analysis
- Can correlate logs with flight timeline
- Essential for debugging flight issues

---

## 📞 Support

If issues encountered:
- Post in Issue #47
- Tag @CC-PM for coordination
- User available for physical hardware checks

---

**Estimated Total Time:** 40 minutes
**Priority:** HIGH
**Blocks:** Future flight test log analysis

**Ready to start testing!**
