#!/bin/bash
# CCPM (Claude Code Project Management) Session Launcher
# Opens terminal with tmux session, navigates to CCPM repo, starts Claude Code

set -e

SESSION_NAME="CCPM"
# Adjust this path if CCPM repo is in a different location
CCPM_DIR="$HOME/cc-project-management"

echo "Starting CCPM session..."

# Check if CCPM directory exists
if [ ! -d "$CCPM_DIR" ]; then
    echo "ERROR: CCPM directory not found at: $CCPM_DIR"
    echo ""
    echo "Please clone the CCPM repository first:"
    echo "  git clone https://github.com/unmanned-systems-uk/cc-project-management.git $CCPM_DIR"
    echo ""
    echo "Or update CCPM_DIR in this script to point to the correct location."
    exit 1
fi

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
echo "Navigating to CCPM directory..."
tmux send-keys -t "$SESSION_NAME" "cd $CCPM_DIR" C-m

# Wait for directory change
sleep 1

echo "Starting Claude Code..."
tmux send-keys -t "$SESSION_NAME" "claude-code" C-m

# Wait for Claude to start
sleep 2

echo "Typing 'START PM' for CCPM session..."
tmux send-keys -t "$SESSION_NAME" "START PM" C-m

# Attach to session
echo "Attaching to session..."
tmux attach-session -t "$SESSION_NAME"
