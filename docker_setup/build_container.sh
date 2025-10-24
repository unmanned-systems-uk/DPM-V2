#!/bin/bash
# build_container.sh - Build the payload manager Docker container
# Usage: ./build_container.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Payload Manager Container Build Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${YELLOW}Warning: Not running on Raspberry Pi${NC}"
    echo -e "${YELLOW}This will build for the current architecture${NC}"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check if Sony SDK exists
if [ ! -d "sony_sdk" ]; then
    echo -e "${RED}Error: sony_sdk directory not found${NC}"
    echo "Please create the directory and copy your Sony SDK files:"
    echo "  mkdir sony_sdk"
    echo "  cp -r /path/to/sony/sdk/* sony_sdk/"
    exit 1
fi

# Check if source directory exists
if [ ! -d "src" ]; then
    echo -e "${YELLOW}Warning: src directory not found, creating it${NC}"
    mkdir -p src
    echo "# Placeholder file" > src/README.md
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo ""

# Build the container
echo -e "${GREEN}Building Docker image...${NC}"
docker build -t payload-manager:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Image: payload-manager:latest"
    echo ""
    echo "Next steps:"
    echo "  1. Run the container:"
    echo "     ./run_container.sh"
    echo ""
    echo "  2. View logs:"
    echo "     docker logs -f payload-manager"
    echo ""
    echo "  3. Access container shell:"
    echo "     docker exec -it payload-manager bash"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Build failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
