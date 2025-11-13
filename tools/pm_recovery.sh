#!/bin/bash
# PM Power-Cut Recovery Protocol
# Reconstructs system state after power loss, reboot, or session termination
# Usage: ./pm_recovery.sh

set -e

echo "=============================================="
echo "   PM POWER-CUT RECOVERY PROTOCOL"
echo "   DPM-V2 State Reconstruction"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")/.." || exit 1

echo -e "${BLUE}[1/8] System Uptime Check${NC}"
echo "─────────────────────────────────────────────"
uptime
echo ""

echo -e "${BLUE}[2/8] Network Connectivity Verification${NC}"
echo "─────────────────────────────────────────────"
echo "Checking Air-Side (Pi 5 - 10.0.1.53)..."
if ping -c 1 10.0.1.53 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Air-Side reachable${NC}"
else
    echo -e "${RED}✗ Air-Side unreachable${NC}"
fi

echo "Checking Ground-Side (H16 - 10.0.1.92)..."
if ping -c 1 10.0.1.92 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ground-Side reachable${NC}"
else
    echo -e "${RED}✗ Ground-Side unreachable${NC}"
fi

echo "Checking Jetson (10.0.1.113)..."
if ping -c 1 10.0.1.113 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Jetson reachable${NC}"
else
    echo -e "${RED}✗ Jetson unreachable${NC}"
fi
echo ""

echo -e "${BLUE}[3/8] Git Repository Status${NC}"
echo "─────────────────────────────────────────────"
echo "Current branch:"
git branch --show-current

echo -e "\nWorking tree status:"
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✓ Clean (no uncommitted changes)${NC}"
else
    echo -e "${YELLOW}⚠ Uncommitted changes present${NC}"
    git status --short
fi

echo -e "\nRecent commits:"
git log --oneline -5
echo ""

echo -e "${BLUE}[4/8] Runtime Status Files${NC}"
echo "─────────────────────────────────────────────"

if [ -f "sbc/RUNTIME_STATUS.json" ]; then
    echo -e "${GREEN}✓ Air-Side status file found${NC}"
    cat sbc/RUNTIME_STATUS.json
else
    echo -e "${YELLOW}⚠ Air-Side status file not found${NC}"
fi
echo ""

if [ -f "android/RUNTIME_STATUS.json" ]; then
    echo -e "${GREEN}✓ Ground-Side status file found${NC}"
    cat android/RUNTIME_STATUS.json
else
    echo -e "${YELLOW}⚠ Ground-Side status file not found${NC}"
fi
echo ""

if [ -f "SystemTools/RUNTIME_STATUS.json" ]; then
    echo -e "${GREEN}✓ SystemTools status file found${NC}"
    cat SystemTools/RUNTIME_STATUS.json
else
    echo -e "${YELLOW}⚠ SystemTools status file not found${NC}"
fi
echo ""

echo -e "${BLUE}[5/8] Running Services Check${NC}"
echo "─────────────────────────────────────────────"

echo "Air-Side (Docker containers on Pi 5):"
if ssh -o ConnectTimeout=5 dpm@10.0.1.53 'docker ps' 2>/dev/null; then
    echo -e "${GREEN}✓ Air-Side Docker services accessible${NC}"
else
    echo -e "${RED}✗ Cannot access Air-Side Docker (SSH failed)${NC}"
fi
echo ""

echo "Ground-Side (ADB connection):"
if adb devices 2>/dev/null | grep -q "10.0.1.92"; then
    echo -e "${GREEN}✓ Ground-Side connected via ADB${NC}"
    adb devices
else
    echo -e "${YELLOW}⚠ Ground-Side not connected via ADB${NC}"
    echo "Run: adb connect 10.0.1.92:5555"
fi
echo ""

echo "SystemTools (log_aggregator):"
if pgrep -f "log_aggregator.py" > /dev/null; then
    echo -e "${GREEN}✓ log_aggregator.py running${NC}"
    ps aux | grep log_aggregator.py | grep -v grep
else
    echo -e "${YELLOW}⚠ log_aggregator.py not running${NC}"
fi
echo ""

echo -e "${BLUE}[6/8] GitHub Issues Status${NC}"
echo "─────────────────────────────────────────────"
echo "Critical issues:"
gh issue list --label priority:critical --state open --limit 5

echo -e "\nIn-progress issues:"
gh issue list --label status:in-progress --state open --limit 5
echo ""

echo -e "${BLUE}[7/8] Uncommitted Work Analysis${NC}"
echo "─────────────────────────────────────────────"
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
else
    echo -e "${YELLOW}⚠ Uncommitted changes detected:${NC}"
    git diff --stat
    git diff --cached --stat
fi
echo ""

echo -e "${BLUE}[8/8] PM State Reconstruction${NC}"
echo "─────────────────────────────────────────────"

# Parse last activity from GitHub issues
LAST_ISSUE=$(gh issue list --label status:in-progress --state open --limit 1 --json number,title,updatedAt --jq '.[0]')
if [ -n "$LAST_ISSUE" ]; then
    echo -e "${GREEN}✓ Last known activity found:${NC}"
    echo "$LAST_ISSUE" | jq '.'

    ISSUE_NUM=$(echo "$LAST_ISSUE" | jq -r '.number')
    echo -e "\nLast comment on issue #${ISSUE_NUM}:"
    gh issue view "$ISSUE_NUM" --json comments --jq '.comments[-1] | {author: .author.login, created: .createdAt, body: .body}' | head -20
else
    echo -e "${YELLOW}⚠ No in-progress issues found${NC}"
fi
echo ""

echo "=============================================="
echo -e "${GREEN}   RECOVERY ASSESSMENT COMPLETE${NC}"
echo "=============================================="
echo ""

# Provide recovery recommendations
echo -e "${BLUE}Recovery Recommendations:${NC}"
echo ""

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}1. Review uncommitted changes and commit if necessary${NC}"
fi

if ! ssh -o ConnectTimeout=5 dpm@10.0.1.53 'docker ps' > /dev/null 2>&1; then
    echo -e "${YELLOW}2. Reconnect to Air-Side: ssh dpm@10.0.1.53${NC}"
fi

if ! adb devices 2>/dev/null | grep -q "10.0.1.92"; then
    echo -e "${YELLOW}3. Reconnect to Ground-Side: adb connect 10.0.1.92:5555${NC}"
fi

if ! pgrep -f "log_aggregator.py" > /dev/null; then
    echo -e "${YELLOW}4. Restart log_aggregator: cd SystemTools && python3 log_aggregator.py${NC}"
fi

if [ -n "$LAST_ISSUE" ]; then
    ISSUE_NUM=$(echo "$LAST_ISSUE" | jq -r '.number')
    echo -e "${YELLOW}5. Review Issue #${ISSUE_NUM} to determine next steps${NC}"
fi

echo ""
echo -e "${GREEN}Use this information to resume work where you left off.${NC}"
echo ""
