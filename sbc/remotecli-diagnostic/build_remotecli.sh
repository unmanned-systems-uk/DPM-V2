#!/bin/bash
#
# Build RemoteCli v2 Diagnostic Container
#
# This script builds a Docker container with the enhanced RemoteCli v2
# diagnostic tool that includes comprehensive logging for debugging
# Sony camera connection and control issues.
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "  Building RemoteCli v2 Diagnostic"
echo "========================================="
echo ""

# Check if Sony SDK exists
SDK_SOURCE="$HOME/CrSDK_v2.00.00_20250805a_Linux64ARMv8"
if [ ! -d "$SDK_SOURCE" ]; then
    echo "ERROR: Sony SDK not found at: $SDK_SOURCE"
    echo "Please ensure the Sony SDK is installed."
    exit 1
fi

echo "✓ Found Sony SDK at: $SDK_SOURCE"

# Create temporary build context
BUILD_CONTEXT="/tmp/remotecli_v2_build"
rm -rf "$BUILD_CONTEXT"
mkdir -p "$BUILD_CONTEXT"

echo "✓ Created build context at: $BUILD_CONTEXT"

# Copy RemoteCli v2 source
cp -r remotecli_v2 "$BUILD_CONTEXT/"
echo "✓ Copied RemoteCli v2 source"

# Copy Sony SDK
echo "  Copying Sony SDK (this may take a moment)..."
mkdir -p "$BUILD_CONTEXT/sony_sdk"
cp -r "$SDK_SOURCE/external" "$BUILD_CONTEXT/sony_sdk/"
echo "✓ Copied Sony SDK libraries"

# Copy Dockerfile
cp Dockerfile "$BUILD_CONTEXT/"
echo "✓ Copied Dockerfile"

# Build Docker image
echo ""
echo "Building Docker image: remotecli-v2:latest"
echo "This will take a few minutes..."
echo ""

docker build -t remotecli-v2:latest "$BUILD_CONTEXT"

# Cleanup
echo ""
echo "Cleaning up build context..."
rm -rf "$BUILD_CONTEXT"

echo ""
echo "========================================="
echo "  Build Complete!"
echo "========================================="
echo ""
echo "Docker image: remotecli-v2:latest"
echo ""
echo "To run the diagnostic tool:"
echo "  ./run_remotecli.sh"
echo ""
echo "To run interactively:"
echo "  ./run_remotecli.sh -i"
echo ""
