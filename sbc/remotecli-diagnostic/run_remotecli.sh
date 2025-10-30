#!/bin/bash
#
# Run RemoteCli v2 Diagnostic Container
#
# This script runs the RemoteCli v2 diagnostic tool in a Docker container
# with full USB access for camera connection.
#
# Usage:
#   ./run_remotecli.sh           # Run normally
#   ./run_remotecli.sh -i        # Interactive shell inside container
#

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "  RemoteCli v2 Diagnostic Tool"
echo "========================================="
echo ""

# Check if image exists
if ! docker image inspect remotecli-v2:latest >/dev/null 2>&1; then
    echo "ERROR: Docker image 'remotecli-v2:latest' not found"
    echo ""
    echo "Please build the image first:"
    echo "  ./build_remotecli.sh"
    echo ""
    exit 1
fi

# Create logs directory on host
LOGS_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGS_DIR"

# Check for interactive mode
INTERACTIVE=false
if [ "$1" == "-i" ] || [ "$1" == "--interactive" ]; then
    INTERACTIVE=true
fi

# USB device check
echo "Checking for Sony camera..."
if lsusb | grep -i sony > /dev/null; then
    echo "✓ Sony camera detected on USB"
else
    echo "⚠ WARNING: No Sony camera detected"
    echo "  Please ensure:"
    echo "  1. Camera is powered ON"
    echo "  2. Camera is connected via USB"
    echo "  3. Camera is in PC Remote mode"
    echo ""
fi

# Stop any existing container
if docker ps -a | grep remotecli-diagnostic > /dev/null; then
    echo "Stopping existing container..."
    docker stop remotecli-diagnostic 2>/dev/null || true
    docker rm remotecli-diagnostic 2>/dev/null || true
fi

if [ "$INTERACTIVE" = true ]; then
    echo ""
    echo "Launching interactive shell..."
    echo "To run RemoteCli v2 inside the container:"
    echo "  cd /app/remotecli_v2/build"
    echo "  ./RemoteCli_v2"
    echo ""

    docker run -it --rm \
        --name remotecli-diagnostic \
        --privileged \
        -v /dev/bus/usb:/dev/bus/usb \
        -v "$LOGS_DIR:/app/logs" \
        remotecli-v2:latest \
        /bin/bash
else
    echo ""
    echo "Starting RemoteCli v2..."
    echo "Logs will be saved to: $LOGS_DIR/remotecli_v2.log"
    echo ""
    echo "========================================="
    echo ""

    docker run -it --rm \
        --name remotecli-diagnostic \
        --privileged \
        -v /dev/bus/usb:/dev/bus/usb \
        -v "$LOGS_DIR:/app/logs" \
        remotecli-v2:latest
fi

echo ""
echo "RemoteCli v2 session ended"
echo ""
echo "To view the diagnostic log:"
echo "  cat $LOGS_DIR/remotecli_v2.log"
echo ""
