#!/bin/bash
# DPM-V2 Air-Side Session Launcher
# Opens terminal with tmux session, SSH to Pi 5, starts Claude Code

set -e

SESSION_NAME="Air-Side-PI"
PI_HOST="dpm@10.0.1.53"
PROJECT_DIR="~/DPM-V2/sbc"

echo "Starting Air-Side session..."

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists."
    echo "Attaching to existing session..."
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

# Create new tmux session
echo "Creating new tmux session: $SESSION_NAME"
tmux new-session -d -s "$SESSION_NAME"

# Send commands to tmux session
echo "Connecting to Pi 5..."
tmux send-keys -t "$SESSION_NAME" "ssh $PI_HOST" C-m

# Wait for SSH connection
sleep 2

echo "Navigating to Air-Side directory..."
tmux send-keys -t "$SESSION_NAME" "cd $PROJECT_DIR" C-m

# Wait for directory change
sleep 1

echo "Starting Claude Code..."
tmux send-keys -t "$SESSION_NAME" "claude-code" C-m

# Wait for Claude to start
sleep 2

echo "Sending /start-air command..."
tmux send-keys -t "$SESSION_NAME" "/start-air" C-m

# Attach to session
echo "Attaching to session..."
tmux attach-session -t "$SESSION_NAME"
