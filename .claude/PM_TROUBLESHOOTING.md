# PM Troubleshooting Guide

**Purpose:** Common PM session issues and resolutions

**Referenced by:** `.claude/PM_START.md`

---

## 🔧 Common Issues

### If tmux session not responding

```bash
# Check if session exists
tmux list-sessions

# Check if session frozen
tmux capture-pane -t [session] -p -S -1000

# Reconnect to session
tmux attach -t [session]
```

### If domain appears stuck

```bash
# Get full recent output
tmux capture-pane -t [Domain] -p -S -500 | tail -100

# Check for waiting prompts
tmux capture-pane -t [Domain] -p | grep -E "(\?|waiting|input|press)"

# Notify user for intervention
```

### If network connectivity lost

```bash
# Check Pi 5
ping 10.0.1.53

# Check H16
adb devices

# Reconnect if needed
ssh dpm@10.0.1.53
adb connect 10.0.1.92:5555
```

---

**Last Updated:** 2025-11-21
