# DPM-V2 Agent Spawn Helper
**Created:** 2025-11-20
**Purpose:** Quick reference for spawning DPM agents with tmux

---

## Quick Spawn Commands

### With Permission Override (Auto-Approve)
```bash
# Spawn all agents with auto-approve
tmux new-session -d -s DPM-Air "cd ~/DPM-V2 && claude --dangerously-skip-permissions /start-dpm-air"
tmux new-session -d -s DPM-Ground "cd ~/DPM-V2 && claude --dangerously-skip-permissions /start-dpm-ground"
tmux new-session -d -s DPM-Tools "cd ~/DPM-V2 && claude --dangerously-skip-permissions /start-dpm-tools"
```

### With Standard Permissions (User Approval Required)
```bash
# Spawn all agents with user approval per action
tmux new-session -d -s DPM-Air "cd ~/DPM-V2 && claude /start-dpm-air"
tmux new-session -d -s DPM-Ground "cd ~/DPM-V2 && claude /start-dpm-ground"
tmux new-session -d -s DPM-Tools "cd ~/DPM-V2 && claude /start-dpm-tools"
```

---

## Agent Status Check

```bash
# List all DPM tmux sessions
tmux list-sessions | grep DPM-

# Check specific agent
tmux has-session -t DPM-Air 2>/dev/null && echo "✅ Air-Side ready" || echo "❌ Air-Side offline"
tmux has-session -t DPM-Ground 2>/dev/null && echo "✅ Ground-Side ready" || echo "❌ Ground-Side offline"
tmux has-session -t DPM-Tools 2>/dev/null && echo "✅ SystemTools ready" || echo "❌ SystemTools offline"
```

---

## Attach to Agent Sessions

```bash
# Attach to specific agent
tmux attach -t DPM-Air
tmux attach -t DPM-Ground
tmux attach -t DPM-Tools

# Detach: Ctrl+B, then D
```

---

## Send Commands to Agents

```bash
# Send task to agent
tmux send-keys -t DPM-Air "Read GitHub issue #123 and implement UDP broadcast fix" C-m

# Check agent output
tmux capture-pane -t DPM-Air -p | tail -30
```

---

## Kill Agent Sessions

```bash
# Kill specific agent
tmux kill-session -t DPM-Air

# Kill all DPM agents
tmux kill-session -t DPM-Air
tmux kill-session -t DPM-Ground
tmux kill-session -t DPM-Tools
```

---

## Available Start Commands

- `/start-dpm-master` or `/start-dpm-pm` - Master/PM orchestrator
- `/start-dpm-air` - Air-Side agent (Pi 5, C++)
- `/start-dpm-ground` - Ground-Side agent (H16, Kotlin)
- `/start-dpm-tools` - SystemTools agent (Python)

---

**Pattern:** All DPM agents use `DPM-` prefix for tmux sessions, matching CCPM's `ccpm-` pattern.
