#!/bin/bash
# run_container.sh - Run the C++ payload manager Docker container
# Usage: ./run_container.sh [dev|prod] [--test-wifi] [--ground-ip <IP>]
#
# Modes:
#   dev  - Development mode with source mounted as volume
#   prod - Production mode using code baked into image (default)
#
# WiFi Testing:
#   --test-wifi              - Enable WiFi testing mode (uses 10.0.1.x network)
#   --ground-ip <IP>         - Manually specify ground station IP address
#
# Examples:
#   ./run_container.sh                           - Production mode, default ethernet
#   ./run_container.sh dev                       - Development mode, default ethernet
#   ./run_container.sh --test-wifi               - Production mode, WiFi testing
#   ./run_container.sh dev --test-wifi           - Development mode, WiFi testing
#   ./run_container.sh --ground-ip 10.0.1.100    - Custom ground IP
#   ./run_container.sh dev --ground-ip 10.0.1.100 - Dev mode with custom IP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
MODE="prod"
GROUND_IP=""
WIFI_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        dev|prod)
            MODE="$1"
            shift
            ;;
        --test-wifi)
            WIFI_MODE=true
            shift
            ;;
        --ground-ip)
            GROUND_IP="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown argument '$1'${NC}"
            echo "Usage: $0 [dev|prod] [--test-wifi] [--ground-ip <IP>]"
            exit 1
            ;;
    esac
done

# Determine ground IP if not explicitly set
if [ -z "$GROUND_IP" ]; then
    if [ "$WIFI_MODE" = true ]; then
        # WiFi mode - script will help find H16 IP
        echo -e "${BLUE}WiFi testing mode - attempting to discover H16...${NC}"
        # Try to find H16 on 10.0.1.x network (if find_h16.sh exists)
        if [ -f "scripts/find_h16.sh" ]; then
            DISCOVERED_IP=$(bash scripts/find_h16.sh 2>/dev/null || echo "")
            if [ -n "$DISCOVERED_IP" ]; then
                GROUND_IP="$DISCOVERED_IP"
                echo -e "${GREEN}Discovered H16 at: $GROUND_IP${NC}"
            else
                echo -e "${YELLOW}Could not auto-discover H16, using default WiFi IP: 10.0.1.100${NC}"
                GROUND_IP="10.0.1.100"
            fi
        else
            echo -e "${YELLOW}Auto-discovery not available, using default WiFi IP: 10.0.1.100${NC}"
            GROUND_IP="10.0.1.100"
        fi
    else
        # Default ethernet mode
        GROUND_IP="192.168.144.11"
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Payload Manager Container Runner${NC}"
echo -e "${GREEN}(C++ Implementation)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Mode: ${GREEN}$MODE${NC}"
echo -e "Ground Station IP: ${GREEN}$GROUND_IP${NC}"
if [ "$WIFI_MODE" = true ]; then
    echo -e "Network: ${BLUE}WiFi Testing (10.0.1.x)${NC}"
else
    echo -e "Network: ${GREEN}Ethernet (192.168.144.x)${NC}"
fi
echo ""

# Check if image exists
if ! docker images | grep -q "payload-manager"; then
    echo -e "${RED}Error: payload-manager image not found${NC}"
    echo "Build it first with: ./build_container.sh"
    exit 1
fi

# Stop and remove existing container if running
if docker ps -a | grep -q "payload-manager"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    docker stop payload-manager 2>/dev/null || true
    docker rm payload-manager 2>/dev/null || true
fi

echo -e "${GREEN}Starting container in ${MODE} mode...${NC}"
echo ""

if [ "$MODE" = "dev" ]; then
    # Development mode: mount source as volume for live editing
    echo -e "${YELLOW}Development Mode:${NC}"
    echo "  - Source code mounted as volume"
    echo "  - Changes to src/ require rebuild inside container"
    echo "  - To rebuild: docker exec -it payload-manager bash"
    echo "               cd /app/sbc/build && cmake .. && make"
    echo "  - Restart container to reload: docker restart payload-manager"
    echo ""

    docker run -d \
        --name payload-manager \
        --restart unless-stopped \
        --privileged \
        --network host \
        -v /dev/bus/usb:/dev/bus/usb \
        -v $(pwd):/app/sbc:rw \
        -v /home/dpm/CrSDK_v2.00.00_20250805a_Linux64ARMv8:/app/sdk:ro \
        -v $(pwd)/logs:/app/logs:rw \
        -e MODE=development \
        -e DPM_GROUND_IP="$GROUND_IP" \
        -e LD_LIBRARY_PATH=/app/sdk/external/crsdk:/app/sdk/external/crsdk/CrAdapter \
        payload-manager:latest \
        /app/sbc/build/payload_manager

else
    # Production mode: use code baked into image
    echo -e "${GREEN}Production Mode:${NC}"
    echo "  - Using code from Docker image"
    echo "  - Auto-restart enabled"
    echo "  - Persistent logs in ./logs/"
    echo ""

    # Create logs directory if it doesn't exist
    mkdir -p logs

    docker run -d \
        --name payload-manager \
        --restart always \
        --privileged \
        --network host \
        -v /dev/bus/usb:/dev/bus/usb \
        -v $(pwd)/logs:/app/logs:rw \
        -e MODE=production \
        -e DPM_GROUND_IP="$GROUND_IP" \
        payload-manager:latest
fi

# Wait a moment for container to start
sleep 2

# Check if container is running
if docker ps | grep -q "payload-manager"; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Container started successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Container: payload-manager"
    echo "Status: Running"
    echo "Implementation: C++ binary"
    echo ""
    echo "Configuration:"
    echo "  Ground Station IP: $GROUND_IP"
    if [ "$WIFI_MODE" = true ]; then
        echo "  Network Mode: WiFi Testing (10.0.1.x)"
    else
        echo "  Network Mode: Ethernet (192.168.144.x)"
    fi
    echo ""
    echo "Network endpoints:"
    echo "  TCP: 192.168.144.20:5000 (commands)"
    echo "  UDP Status → $GROUND_IP:5001 (5 Hz)"
    echo "  UDP Heartbeat → $GROUND_IP:5002 (1 Hz)"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        docker logs -f payload-manager"
    echo "  Check status:     docker ps | grep payload-manager"
    echo "  Stop container:   docker stop payload-manager"
    echo "  Restart:          docker restart payload-manager"
    echo "  Shell access:     docker exec -it payload-manager bash"
    echo "  Remove:           docker stop payload-manager && docker rm payload-manager"
    echo ""
    echo "Testing camera connection:"
    echo "  docker exec payload-manager lsusb | grep Sony"
    echo ""
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Container failed to start!${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "View logs for details:"
    echo "  docker logs payload-manager"
    exit 1
fi
