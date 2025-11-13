# DPM Runtime Status Updater - Installation Guide

This systemd service automatically updates RUNTIME_STATUS.json files every 5 minutes to enable PM recovery after power cuts.

## Overview

**Purpose:** Persistent state tracking for PM recovery
**Update Frequency:** Every 5 minutes
**Tracks:** Container status, network config, service states
**Why:** Enables PM to reconstruct state after power-cut without manual investigation

## Installation

### For Air-Side (Raspberry Pi 5)

```bash
# 1. Navigate to DPM-V2 project
cd ~/DPM-V2

# 2. Copy service files to systemd directory
sudo cp tools/systemd/dpm-status-updater.service /etc/systemd/system/
sudo cp tools/systemd/dpm-status-updater.timer /etc/systemd/system/

# 3. Replace placeholders in service file
sudo sed -i "s|%USER%|$USER|g" /etc/systemd/system/dpm-status-updater.service
sudo sed -i "s|%GROUP%|$USER|g" /etc/systemd/system/dpm-status-updater.service
sudo sed -i "s|%PROJECT_ROOT%|$PWD|g" /etc/systemd/system/dpm-status-updater.service

# 4. Reload systemd daemon
sudo systemctl daemon-reload

# 5. Enable and start the timer
sudo systemctl enable dpm-status-updater.timer
sudo systemctl start dpm-status-updater.timer

# 6. Verify timer is active
sudo systemctl status dpm-status-updater.timer

# 7. Check that service can run
sudo systemctl start dpm-status-updater.service

# 8. Verify status file was created
ls -la ~/DPM-V2/sbc/RUNTIME_STATUS.json
cat ~/DPM-V2/sbc/RUNTIME_STATUS.json
```

### For Development Machine (Ground-Side & SystemTools)

```bash
# 1. Navigate to DPM-V2 project
cd /home/anthony/DPM-V2

# 2. Copy service files to systemd user directory
mkdir -p ~/.config/systemd/user/
cp tools/systemd/dpm-status-updater.service ~/.config/systemd/user/
cp tools/systemd/dpm-status-updater.timer ~/.config/systemd/user/

# 3. Replace placeholders in service file
sed -i "s|%USER%|$USER|g" ~/.config/systemd/user/dpm-status-updater.service
sed -i "s|%GROUP%|$USER|g" ~/.config/systemd/user/dpm-status-updater.service
sed -i "s|%PROJECT_ROOT%|$PWD|g" ~/.config/systemd/user/dpm-status-updater.service

# 4. Reload user systemd daemon
systemctl --user daemon-reload

# 5. Enable and start the timer
systemctl --user enable dpm-status-updater.timer
systemctl --user start dpm-status-updater.timer

# 6. Enable linger (so service runs even when not logged in)
sudo loginctl enable-linger $USER

# 7. Verify timer is active
systemctl --user status dpm-status-updater.timer

# 8. Check that service can run
systemctl --user start dpm-status-updater.service

# 9. Verify status files were created
ls -la android/RUNTIME_STATUS.json SystemTools/RUNTIME_STATUS.json
cat android/RUNTIME_STATUS.json
cat SystemTools/RUNTIME_STATUS.json
```

## Verification

### Check Timer Status
```bash
# System service (Air-Side)
sudo systemctl list-timers dpm-status-updater.timer

# User service (Development Machine)
systemctl --user list-timers dpm-status-updater.timer
```

### Check Service Logs
```bash
# System service (Air-Side)
sudo journalctl -u dpm-status-updater.service -n 50

# User service (Development Machine)
journalctl --user -u dpm-status-updater.service -n 50
```

### Manual Trigger (Test)
```bash
# System service (Air-Side)
sudo systemctl start dpm-status-updater.service

# User service (Development Machine)
systemctl --user start dpm-status-updater.service

# Check status files
cat sbc/RUNTIME_STATUS.json
cat android/RUNTIME_STATUS.json
cat SystemTools/RUNTIME_STATUS.json
```

### Check Git Commits
```bash
# Status files should be auto-committed every 5 minutes
git log --oneline --grep="AUTO.*runtime status" -10
```

## Troubleshooting

### Timer Not Running
```bash
# Check if timer is enabled
systemctl --user is-enabled dpm-status-updater.timer

# Check timer status
systemctl --user status dpm-status-updater.timer

# Re-enable if needed
systemctl --user enable dpm-status-updater.timer
systemctl --user start dpm-status-updater.timer
```

### Service Failing
```bash
# Check service status
systemctl --user status dpm-status-updater.service

# View detailed logs
journalctl --user -u dpm-status-updater.service -n 100

# Test script manually
cd /home/anthony/DPM-V2
./tools/update_runtime_status.sh
```

### Status Files Not Created
```bash
# Check script permissions
ls -la tools/update_runtime_status.sh

# Make executable if needed
chmod +x tools/update_runtime_status.sh

# Run script manually to see errors
./tools/update_runtime_status.sh all
```

### Git Auto-Commit Failing
```bash
# Check git config
git config user.name
git config user.email

# Set if not configured
git config user.name "DPM Auto-Status"
git config user.email "auto-status@dpm-v2.local"

# Check repository status
git status

# Ensure status files are tracked
git add -f sbc/RUNTIME_STATUS.json
git add -f android/RUNTIME_STATUS.json
git add -f SystemTools/RUNTIME_STATUS.json
```

## Uninstallation

### System Service (Air-Side)
```bash
sudo systemctl stop dpm-status-updater.timer
sudo systemctl disable dpm-status-updater.timer
sudo rm /etc/systemd/system/dpm-status-updater.{service,timer}
sudo systemctl daemon-reload
```

### User Service (Development Machine)
```bash
systemctl --user stop dpm-status-updater.timer
systemctl --user disable dpm-status-updater.timer
rm ~/.config/systemd/user/dpm-status-updater.{service,timer}
systemctl --user daemon-reload
```

## Notes

- **Frequency:** 5 minutes is a balance between state freshness and git commit overhead
- **Git Commits:** Auto-commits are tagged with `[AUTO]` prefix for easy identification
- **Status Files:** Tracked in git for version control and remote backup
- **Security:** Service runs with minimal privileges (PrivateTmp, NoNewPrivileges)
- **Recovery:** PM recovery script (`tools/pm_recovery.sh`) reads these status files

## Related Documentation

- `docs/ALL_DOMAINS/LESSONS_LEARNED.md` - Power-Cut Recovery section
- `.claude/PM_START.md` - PM recovery protocol
- `tools/pm_recovery.sh` - PM recovery script
