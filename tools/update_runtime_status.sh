#!/bin/bash
# DPM Runtime Status Updater
# Updates RUNTIME_STATUS.json files for state persistence
# Can be run manually or via systemd timer
# Usage: ./update_runtime_status.sh [domain]
#   domain: air-side, ground-side, systemtools, or all (default)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date -Iseconds)

update_air_side() {
    echo "Updating Air-Side runtime status..."

    # Check if this is Air-Side system
    if [ ! -f "$PROJECT_ROOT/sbc/src/main.cpp" ]; then
        echo "  Skipping: Not Air-Side system"
        return
    fi

    # Get Docker container status
    CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' payload-manager 2>/dev/null || echo "not running")
    CONTAINER_UPTIME="unknown"
    if [ "$CONTAINER_STATUS" = "running" ]; then
        START_TIME=$(docker inspect -f '{{.State.StartedAt}}' payload-manager)
        CONTAINER_UPTIME="$START_TIME"
    fi

    # Get system uptime
    UPTIME_SECONDS=$(cat /proc/uptime | cut -d' ' -f1 | cut -d'.' -f1)

    # Get network interfaces
    AIR_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' || echo "unknown")

    # Create status file
    cat > "$PROJECT_ROOT/sbc/RUNTIME_STATUS.json" << EOF
{
  "last_updated": "$TIMESTAMP",
  "container_name": "payload-manager",
  "container_status": "$CONTAINER_STATUS",
  "container_started": "$CONTAINER_UPTIME",
  "system_uptime_seconds": $UPTIME_SECONDS,
  "network": {
    "air_side_ip": "$AIR_IP",
    "ground_side_ip": "10.0.1.92",
    "health_broadcast_port": 5004,
    "log_stream_port": 5005,
    "systemtools_log_port": 5007
  }
}
EOF

    echo "  ✓ Air-Side status updated"
}

update_ground_side() {
    echo "Updating Ground-Side runtime status..."

    # Check if this is development machine with android project
    if [ ! -f "$PROJECT_ROOT/android/build.gradle" ]; then
        echo "  Skipping: Not Ground-Side environment"
        return
    fi

    # Check ADB connection
    ADB_CONNECTED=false
    if adb devices 2>/dev/null | grep -q "10.0.1.92"; then
        ADB_CONNECTED=true
    fi

    # Create status file
    cat > "$PROJECT_ROOT/android/RUNTIME_STATUS.json" << EOF
{
  "last_updated": "$TIMESTAMP",
  "device_ip": "10.0.1.92",
  "adb_connected": $ADB_CONNECTED,
  "development_machine": "$(hostname)",
  "phase1_components": {
    "health_dashboard": "implemented",
    "structured_logger": "implemented",
    "advanced_settings": "implemented",
    "log_viewer": "pending"
  }
}
EOF

    echo "  ✓ Ground-Side status updated"
}

update_systemtools() {
    echo "Updating SystemTools runtime status..."

    # Check if SystemTools directory exists
    if [ ! -d "$PROJECT_ROOT/SystemTools" ]; then
        echo "  Skipping: SystemTools directory not found"
        return
    fi

    # Check if log_aggregator is running
    LOG_AGG_RUNNING=false
    LOG_AGG_PID="null"
    LOG_AGG_START="null"
    if pgrep -f "log_aggregator.py" > /dev/null; then
        LOG_AGG_RUNNING=true
        LOG_AGG_PID=$(pgrep -f "log_aggregator.py")
        LOG_AGG_START=$(ps -o lstart= -p "$LOG_AGG_PID" | xargs -I {} date -d "{}" -Iseconds)
    fi

    # Create status file
    cat > "$PROJECT_ROOT/SystemTools/RUNTIME_STATUS.json" << EOF
{
  "last_updated": "$TIMESTAMP",
  "log_aggregator": {
    "running": $LOG_AGG_RUNNING,
    "pid": $LOG_AGG_PID,
    "start_time": "$LOG_AGG_START",
    "udp_port": 5007,
    "tcp_port": 5008
  },
  "development_machine": "$(hostname)"
}
EOF

    echo "  ✓ SystemTools status updated"
}

commit_status_files() {
    echo "Committing status files to git..."

    cd "$PROJECT_ROOT"

    # Add status files
    git add -f sbc/RUNTIME_STATUS.json 2>/dev/null || true
    git add -f android/RUNTIME_STATUS.json 2>/dev/null || true
    git add -f SystemTools/RUNTIME_STATUS.json 2>/dev/null || true

    # Commit if there are changes
    if ! git diff --staged --quiet 2>/dev/null; then
        git commit -m "[AUTO] Update runtime status - $(date +'%Y-%m-%d %H:%M:%S')"
        echo "  ✓ Status files committed"
    else
        echo "  ℹ No changes to commit"
    fi
}

# Main execution
DOMAIN="${1:-all}"

echo "=================================="
echo " DPM Runtime Status Updater"
echo " Time: $(date)"
echo "=================================="
echo ""

case "$DOMAIN" in
    air-side)
        update_air_side
        ;;
    ground-side)
        update_ground_side
        ;;
    systemtools)
        update_systemtools
        ;;
    all)
        update_air_side
        update_ground_side
        update_systemtools
        ;;
    *)
        echo "Error: Unknown domain '$DOMAIN'"
        echo "Usage: $0 [air-side|ground-side|systemtools|all]"
        exit 1
        ;;
esac

echo ""
commit_status_files

echo ""
echo "=================================="
echo " Status Update Complete"
echo "=================================="
