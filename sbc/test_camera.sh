#!/bin/bash
# Test camera connection inside container
echo "Testing USB camera connection..."
echo ""

if ! docker ps | grep -q "payload-manager"; then
    echo "Error: payload-manager container is not running"
    echo "Start it with: ./run_container.sh prod"
    exit 1
fi

echo "Checking USB devices in container..."
docker exec payload-manager lsusb

echo ""
echo "Checking for Sony camera..."
if docker exec payload-manager lsusb | grep -i sony; then
    echo "✓ Sony camera detected!"
else
    echo "⚠ No Sony camera detected"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure camera is powered on"
    echo "  2. Check USB cable connection"
    echo "  3. Verify camera is in USB mode (not just charging)"
    echo "  4. Check on host: lsusb | grep Sony"
fi
