#!/bin/bash
# run_container.sh - Run the C++ payload manager Docker container
# Usage: ./run_container.sh [dev|prod]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

MODE="${1:-prod}"  # Default to production mode

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Payload Manager Container Runner${NC}"
echo -e "${GREEN}(C++ Implementation)${NC}"
echo -e "${GREEN}========================================${NC}"
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
    echo "Network endpoints:"
    echo "  TCP: 192.168.144.20:5000 (commands)"
    echo "  UDP: 192.168.144.20:5001 (status)"
    echo "  UDP: 192.168.144.20:5002 (heartbeat)"
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
