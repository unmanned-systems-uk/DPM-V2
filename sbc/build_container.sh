#!/bin/bash
# build_container.sh - Build the C++ payload manager Docker container
# Usage: ./build_container.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Payload Manager Container Build Script${NC}"
echo -e "${GREEN}(C++ Implementation)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo -e "${GREEN}✓ Detected: $MODEL${NC}"
else
    echo -e "${YELLOW}Warning: Not running on Raspberry Pi${NC}"
    echo -e "${YELLOW}This will build for the current architecture${NC}"
fi
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install Docker with: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check if Sony SDK exists
SONY_SDK_PATH="/home/dpm/SonySDK/CrSDK_v2.00.00_20250805a_Linux64ARMv8"
if [ ! -d "$SONY_SDK_PATH" ]; then
    echo -e "${RED}Error: Sony SDK not found at $SONY_SDK_PATH${NC}"
    echo "Please ensure Sony SDK is installed at the expected location"
    exit 1
fi

# Check if source directory exists
if [ ! -d "src" ]; then
    echo -e "${RED}Error: src directory not found${NC}"
    echo "Make sure you're in the /home/dpm/DPM/sbc directory"
    exit 1
fi

# Check if CMakeLists.txt exists
if [ ! -f "CMakeLists.txt" ]; then
    echo -e "${RED}Error: CMakeLists.txt not found${NC}"
    exit 1
fi

# Check if Dockerfile.prod exists
if [ ! -f "Dockerfile.prod" ]; then
    echo -e "${RED}Error: Dockerfile.prod not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"
echo -e "${GREEN}✓ Sony SDK found at: $SONY_SDK_PATH${NC}"
echo -e "${GREEN}✓ Source code found${NC}"
echo ""

# Build the container (from parent directory to access Sony SDK)
echo -e "${GREEN}Building Docker image for C++ payload_manager...${NC}"
echo "Build context: /home/dpm/DPM/"
echo "Dockerfile: sbc/Dockerfile.prod"
echo ""
cd /home/dpm/DPM
docker build -f sbc/Dockerfile.prod -t payload-manager:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Image: payload-manager:latest"
    echo "Binary: C++ payload_manager"
    echo ""
    echo "Next steps:"
    echo "  1. Run the container:"
    echo "     ./run_container.sh prod"
    echo ""
    echo "  2. View logs:"
    echo "     docker logs -f payload-manager"
    echo ""
    echo "  3. Access container shell:"
    echo "     docker exec -it payload-manager bash"
    echo ""
    echo "  4. Test camera:"
    echo "     docker exec payload-manager lsusb | grep Sony"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Build failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
