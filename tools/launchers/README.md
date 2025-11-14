# DPM-V2 Domain Launchers

Desktop launchers for starting Claude Code sessions in all DPM-V2 domains with automatic tmux setup.

## Overview

Each launcher:
1. Creates a tmux session (or attaches if already exists)
2. Navigates to the correct directory
3. Starts Claude Code
4. Sends the appropriate `/start-[domain]` command
5. Attaches you to the session

## Available Launchers

| Launcher | Session Name | Target | Auto-Command |
|----------|--------------|--------|--------------|
| **DPM Air-Side** | `Air-Side-PI` | SSH to Pi 5 (10.0.1.53) | `/start-air` |
| **DPM Ground-Side** | `Ground-Side` | Local `android/` | `/start-ground` |
| **DPM SystemTools** | `SystemTools` | Local `SystemTools/` | `/start-tools` |
| **DPM Project Manager** | `dpm-pm` | Local project root | `/start-pm` |
| **CCPM** | `CCPM` | CCPM repo | `START PM` |

## Installation

### Quick Install (Desktop Integration)

```bash
cd /home/anthony/DPM-V2/tools/launchers
./install-launchers.sh
```

This will:
- Copy .desktop files to `~/.local/share/applications/`
- Update desktop database
- Launchers will appear in your application menu

### Manual Installation

```bash
# Copy desktop files
cp /home/anthony/DPM-V2/tools/launchers/*.desktop ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

## Usage

### GUI (Desktop)

After installation, find launchers in your application menu:
- Search for "DPM"
- Look in Development or Utilities categories
- Double-click to launch

### Command Line

```bash
# Air-Side (SSH to Pi 5)
/home/anthony/DPM-V2/tools/launchers/start-air-side.sh

# Ground-Side (Local Android)
/home/anthony/DPM-V2/tools/launchers/start-ground-side.sh

# SystemTools (Local Python)
/home/anthony/DPM-V2/tools/launchers/start-systemtools.sh

# Project Manager (DPM-V2)
/home/anthony/DPM-V2/tools/launchers/start-pm.sh

# CCPM (Project Management)
/home/anthony/DPM-V2/tools/launchers/start-ccpm.sh
```

## Session Management

### List Active Sessions
```bash
tmux list-sessions
```

Expected sessions when all running:
- `Air-Side-PI` - SSH session to Pi 5
- `Ground-Side` - Local Android development
- `SystemTools` - Local Python tools
- `dpm-pm` - Project Manager

### Attach to Existing Session
```bash
tmux attach-session -t Air-Side-PI
tmux attach-session -t Ground-Side
tmux attach-session -t SystemTools
tmux attach-session -t dpm-pm
tmux attach-session -t CCPM
```

### Detach from Session
Press: `Ctrl+B`, then `D`

### Kill Session
```bash
tmux kill-session -t Air-Side-PI
tmux kill-session -t Ground-Side
tmux kill-session -t SystemTools
tmux kill-session -t dpm-pm
tmux kill-session -t CCPM
```

## What Each Launcher Does

### Air-Side Launcher
1. Creates tmux session: `Air-Side-PI`
2. SSH to Pi 5: `ssh dpm@10.0.1.53`
3. Navigate: `cd ~/DPM-V2/sbc`
4. Start: `claude-code`
5. Execute: `/start-air`

**Result:** Air-Side session with:
- WHO: CC-Air-Side
- Platform verification (Pi 5)
- Critical rules reminder
- Open air-side issues listed

### Ground-Side Launcher
1. Creates tmux session: `Ground-Side`
2. Navigate: `cd /home/anthony/DPM-V2/android`
3. Start: `claude-code`
4. Execute: `/start-ground`

**Result:** Ground-Side session with:
- WHO: CC-Ground-Side
- ADB connection check
- Critical rules reminder
- Open ground-side issues listed

### SystemTools Launcher
1. Creates tmux session: `SystemTools`
2. Navigate: `cd /home/anthony/DPM-V2/SystemTools`
3. Start: `claude-code`
4. Execute: `/start-tools`

**Result:** SystemTools session with:
- WHO: CC-Dev-Tools
- Python environment check
- Critical rules reminder
- Open dev-tools issues listed

### PM Launcher
1. Creates tmux session: `dpm-pm`
2. Navigate: `cd /home/anthony/DPM-V2`
3. Start: `claude-code`
4. Execute: `/start-pm`

**Result:** PM session with:
- WHO: CC-PM
- Power-cut recovery check
- Tmux session verification
- Multi-domain coordination ready

### CCPM Launcher
1. Creates tmux session: `CCPM`
2. Navigate: `cd ~/cc-project-management`
3. Start: `claude-code`
4. Execute: `START PM`

**Result:** CCPM session for project management work

## Troubleshooting

### Launcher Not Found in Menu
```bash
# Re-install
cd /home/anthony/DPM-V2/tools/launchers
./install-launchers.sh

# Manually update database
update-desktop-database ~/.local/share/applications/
```

### Session Already Exists
The launcher will attach to existing session instead of creating new one.

To force new session:
```bash
# Kill existing session first
tmux kill-session -t Air-Side-PI

# Then run launcher
./start-air-side.sh
```

### SSH Connection Fails (Air-Side)
Check Pi 5 connectivity:
```bash
ping 10.0.1.53
ssh dpm@10.0.1.53
```

If SSH fails, launcher will hang. Press `Ctrl+C` to cancel.

### Claude Code Not Found
Ensure Claude Code CLI is installed and in PATH:
```bash
which claude-code
claude-code --version
```

### CCPM Directory Not Found
Edit `start-ccpm.sh` and update `CCPM_DIR` variable:
```bash
CCPM_DIR="$HOME/your-ccpm-location"
```

Or clone CCPM:
```bash
git clone https://github.com/unmanned-systems-uk/cc-project-management.git ~/cc-project-management
```

## PM Multi-Domain Monitoring

For PM to monitor all domains in real-time:

1. Launch all domain sessions:
   - **Air-Side** (creates `Air-Side-PI`)
   - **Ground-Side** (creates `Ground-Side`)
   - **SystemTools** (creates `SystemTools`)

2. Launch PM session (creates `dpm-pm`)

3. PM can now monitor via:
   ```bash
   tmux capture-pane -t Air-Side-PI -p | tail -30
   tmux capture-pane -t Ground-Side -p | tail -30
   tmux capture-pane -t SystemTools -p | tail -30
   ```

See `.claude/PM_START.md` for full PM monitoring protocol.

## Customization

### Change Session Names
Edit the `SESSION_NAME` variable in each `.sh` file:
```bash
SESSION_NAME="Your-Custom-Name"
```

### Change Directories
Edit the `PROJECT_DIR` or `PI_HOST` variables:
```bash
PROJECT_DIR="/your/custom/path"
PI_HOST="user@hostname"
```

### Change Auto-Command
Edit the `tmux send-keys` command that sends the startup command:
```bash
tmux send-keys -t "$SESSION_NAME" "/your-custom-command" C-m
```

## Integration with Power-Cut Recovery

When PM session starts with `/start-pm`:
- Checks for power-cut recovery keywords
- Runs `tools/pm_recovery.sh` if needed
- Reconstructs state from GitHub issues + status files
- Provides recovery recommendations

See `tools/pm_recovery.sh` and `.claude/PM_START.md` for details.

## Files

**Shell Scripts:**
- `start-air-side.sh` - Air-Side launcher
- `start-ground-side.sh` - Ground-Side launcher
- `start-systemtools.sh` - SystemTools launcher
- `start-pm.sh` - PM launcher
- `start-ccpm.sh` - CCPM launcher

**Desktop Files:**
- `DPM-Air-Side.desktop`
- `DPM-Ground-Side.desktop`
- `DPM-SystemTools.desktop`
- `DPM-PM.desktop`
- `CCPM.desktop`

**Installation:**
- `install-launchers.sh` - Automatic installation script
- `README.md` - This file

## Related Documentation

- `.claude/commands/` - Slash commands used by launchers
- `.claude/PM_START.md` - PM startup protocol
- `.claude/SESSION_START.md` - General session guide
- `tools/pm_recovery.sh` - Power-cut recovery script
- `docs/CC_READ_THIS_FIRST.md` - Critical rules and workflows

## Version

- **Version:** 1.0
- **Date:** 2025-11-13
- **Author:** CC-PM
- **Tested:** ✅ All launchers functional
