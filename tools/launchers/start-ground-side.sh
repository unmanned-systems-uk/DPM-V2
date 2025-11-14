#!/bin/bash
# DPM-V2 Ground-Side Session Launcher
# Opens terminal with tmux session, navigates to android directory, starts Claude Code

set -e

SESSION_NAME="Ground-Side"
PROJECT_DIR="/home/anthony/DPM-V2/android"

echo "Starting Ground-Side session..."

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
echo "Navigating to Ground-Side directory..."
tmux send-keys -t "$SESSION_NAME" "cd $PROJECT_DIR" C-m

# Wait for directory change
sleep 1

echo "Starting Claude Code..."
tmux send-keys -t "$SESSION_NAME" "claude-code" C-m

# Wait for Claude to start
sleep 2

echo "Sending /start-ground command..."
tmux send-keys -t "$SESSION_NAME" "/start-ground" C-m

# Attach to session
echo "Attaching to session..."
tmux attach-session -t "$SESSION_NAME"
