#!/bin/bash
# PM Session Startup Script
# Creates all required tmux sessions for PM monitoring

set -e

echo "======================================"
echo "DPM-V2 PM Session Startup"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if session exists
session_exists() {
    tmux has-session -t "$1" 2>/dev/null
    return $?
}

# Function to create or skip session
create_session() {
    local session_name=$1
    local command=$2

    if session_exists "$session_name"; then
        echo -e "${YELLOW}⚠️  Session $session_name already exists - skipping${NC}"
    else
        echo -e "${GREEN}✓${NC} Creating session: $session_name"
        eval "$command"
        sleep 0.5
    fi
}

echo "Creating tmux sessions..."
echo ""

# 1. DPM-SYSTEM (GUI)
echo "1/4 DPM-SYSTEM (DPM Management GUI)"
create_session "DPM-SYSTEM" \
    "tmux new-session -d -s DPM-SYSTEM 'cd /home/anthony/DPM-V2/SystemTools && python3 DPM_Management_System.py; exec bash'"

# 2. DPM-GROUND (Android development)
echo "2/4 DPM-GROUND (Android H16 Development)"
create_session "DPM-GROUND" \
    "tmux new-session -d -s DPM-GROUND 'cd /home/anthony/DPM-V2/android && claude-code; exec bash'"

# 3. DPM-TOOLS (SystemTools development)
echo "3/4 DPM-TOOLS (SystemTools Development)"
create_session "DPM-TOOLS" \
    "tmux new-session -d -s DPM-TOOLS 'cd /home/anthony/DPM-V2/SystemTools && claude-code; exec bash'"

# 4. DPM-AIR (Air-Side C++ development on Pi 5)
echo "4/4 DPM-AIR (Air-Side Pi 5 Development)"
if session_exists "DPM-AIR"; then
    echo -e "${YELLOW}⚠️  Session DPM-AIR already exists - skipping${NC}"
else
    echo -e "${GREEN}✓${NC} Creating session: DPM-AIR"
    echo -e "${YELLOW}   Note: SSH to Pi 5 may require password${NC}"
    tmux new-session -d -s DPM-AIR "ssh dpm@10.0.1.53 -t 'cd ~/DPM-V2/sbc && claude-code; exec bash'; exec bash"
    sleep 0.5
fi

echo ""
echo "======================================"
echo "Session Status:"
echo "======================================"

# List all sessions
tmux list-sessions 2>/dev/null || echo "No sessions found"

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "To attach to a session:"
echo "  tmux attach -t DPM-SYSTEM"
echo "  tmux attach -t DPM-GROUND"
echo "  tmux attach -t DPM-TOOLS"
echo "  tmux attach -t DPM-AIR"
echo ""
echo "To view all sessions:"
echo "  tmux list-sessions"
echo ""
echo "To kill a session:"
echo "  tmux kill-session -t SESSION_NAME"
echo ""
echo -e "${GREEN}✅ Startup complete!${NC}"
echo ""
echo "Return to PM session and type: verify sessions"
echo ""
