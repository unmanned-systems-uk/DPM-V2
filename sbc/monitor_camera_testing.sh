#!/bin/bash
# Camera Testing Monitor
# Displays Android app requests, camera commands, and readback values

echo "=========================================="
echo "  Camera Testing Monitor"
echo "=========================================="
echo "Monitoring payload-manager logs..."
echo ""
echo "This will show:"
echo "  1. Commands received from Android app"
echo "  2. Camera property set operations"
echo "  3. Readback comparison (requested vs actual)"
echo "  4. Heartbeat messages (Ground ↔ Air)"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Follow docker logs and filter for camera-related activity and heartbeats
docker logs -f payload-manager 2>&1 | grep --line-buffered -E \
  "Received from 10.0.1.92.*camera\.|Executing camera\.|Property comparison|camera\.set_property|camera\.get_properties|heartbeat|Heartbeat" \
  | while IFS= read -r line; do
    # Extract timestamp
    timestamp=$(echo "$line" | grep -oP '\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]' || echo "[$(date '+%H:%M:%S')]")

    # Color coding
    if echo "$line" | grep -q "Received from"; then
        # Incoming command from Android app
        echo -e "\n\033[1;36m$timestamp <<<< ANDROID APP REQUEST\033[0m"
        echo "$line" | grep -oP 'Received from 10\.0\.1\.92: \K.*' | jq -C '.' 2>/dev/null || echo "$line"
    elif echo "$line" | grep -q "Executing camera\.set_property"; then
        # Property being set on camera
        echo -e "\033[1;33m$timestamp >>>> SENDING TO CAMERA\033[0m"
        echo "$line" | grep -oP 'Executing camera\.set_property: \K.*'
    elif echo "$line" | grep -q "Property comparison"; then
        # Readback comparison
        echo -e "\033[1;32m$timestamp ==== READBACK COMPARISON\033[0m"
        echo "$line" | grep -oP 'Property comparison - \K.*'
        echo "----------------------------------------"
    elif echo "$line" | grep -q "camera\.get_properties"; then
        # Get properties command
        echo -e "\033[1;35m$timestamp <<<< GET PROPERTIES\033[0m"
        echo "$line" | grep -oP 'camera\.get_properties.*'
    elif echo "$line" | grep -qi "heartbeat"; then
        # Heartbeat messages
        if echo "$line" | grep -q "Received from 10.0.1.92"; then
            # Heartbeat received from Ground Side
            echo -e "\033[1;35m$timestamp ♥ HEARTBEAT FROM GROUND\033[0m"
            echo "$line" | grep -oP 'Received from 10\.0\.1\.92: \K.*' | jq -C '.payload.sender, .payload.uptime_seconds' 2>/dev/null || echo "$line"
        elif echo "$line" | grep -qi "sending.*heartbeat\|heartbeat.*sent"; then
            # Heartbeat sent to Ground Side
            echo -e "\033[0;35m$timestamp ♥ HEARTBEAT TO GROUND\033[0m"
        fi
    fi
done
