#!/bin/bash
# run_diagnostic.sh - Run payload_manager diagnostics
# Usage: ./run_diagnostic.sh [diagnostic_mode]
#
# Diagnostic Modes:
#   iso              - ISO sensitivity diagnostics
#   exposure-mode    - Exposure mode diagnostics
#   properties       - List all camera properties
#   property-mapping - Test property mapping
#
# Examples:
#   ./run_diagnostic.sh iso
#   ./run_diagnostic.sh exposure-mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No diagnostic mode specified${NC}"
    echo ""
    echo "Usage: $0 [diagnostic_mode]"
    echo ""
    echo "Available diagnostic modes:"
    echo "  iso              - ISO sensitivity diagnostics"
    echo "  exposure-mode    - Exposure mode diagnostics"
    echo "  properties       - List all camera properties"
    echo "  property-mapping - Test property mapping"
    echo ""
    echo "Example:"
    echo "  $0 iso"
    exit 1
fi

DIAGNOSTIC_MODE="$1"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Payload Manager Diagnostic Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Diagnostic Mode: ${GREEN}$DIAGNOSTIC_MODE${NC}"
echo ""

# Check if image exists
if ! docker images | grep -q "payload-manager"; then
    echo -e "${RED}Error: payload-manager image not found${NC}"
    echo "Build it first with: ./build_container.sh"
    exit 1
fi

# Check if payload-manager is running and stop it
if docker ps | grep -q "payload-manager"; then
    echo -e "${YELLOW}Stopping running payload-manager container...${NC}"
    docker stop payload-manager >/dev/null 2>&1
    echo -e "${GREEN}✓ Container stopped${NC}"
    echo ""
    CONTAINER_WAS_RUNNING=true
else
    CONTAINER_WAS_RUNNING=false
fi

echo -e "${GREEN}Running diagnostic...${NC}"
echo ""
echo "=================================================================="
echo ""

# Run diagnostic in temporary container
docker run --rm \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -v /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/app/sdk:ro \
    payload-manager:latest \
    /app/sbc/build/payload_manager --diagnostic=${DIAGNOSTIC_MODE}

DIAGNOSTIC_EXIT_CODE=$?

echo ""
echo "=================================================================="
echo ""

if [ $DIAGNOSTIC_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Diagnostic completed successfully${NC}"
else
    echo -e "${RED}✗ Diagnostic failed with exit code: $DIAGNOSTIC_EXIT_CODE${NC}"
fi

# Restart container if it was running before
if [ "$CONTAINER_WAS_RUNNING" = true ]; then
    echo ""
    echo -e "${YELLOW}Restarting payload-manager container...${NC}"
    docker start payload-manager >/dev/null 2>&1
    sleep 2

    if docker ps | grep -q "payload-manager"; then
        echo -e "${GREEN}✓ payload-manager restarted${NC}"
    else
        echo -e "${RED}✗ Failed to restart payload-manager${NC}"
        echo "Start it manually with: ./run_container.sh"
    fi
fi

echo ""
exit $DIAGNOSTIC_EXIT_CODE
