#!/bin/bash
# find_h16.sh - Discover H16 ground station on WiFi network
# Scans 10.0.1.x network for H16 listening on TCP port 5000
# Returns the IP address if found, otherwise exits with error

set -e

# Configuration
NETWORK_PREFIX="10.0.1"
TCP_PORT=5000
TIMEOUT=1  # 1 second timeout per host

# Function to check if a host is responding on the TCP port
check_host() {
    local ip=$1
    # Use timeout with nc (netcat) to check if port is open
    # Redirect stderr to hide connection refused messages
    if timeout $TIMEOUT nc -z -w $TIMEOUT "$ip" $TCP_PORT 2>/dev/null; then
        return 0  # Host found
    else
        return 1  # Host not found
    fi
}

# Scan common IP addresses first (most likely H16 IPs)
COMMON_IPS=(
    "${NETWORK_PREFIX}.100"  # Default H16 WiFi IP
    "${NETWORK_PREFIX}.1"    # Common router/gateway
    "${NETWORK_PREFIX}.10"   # Common static IP
    "${NETWORK_PREFIX}.50"   # Common static IP
)

# Check common IPs first for faster discovery
for ip in "${COMMON_IPS[@]}"; do
    if check_host "$ip"; then
        echo "$ip"
        exit 0
    fi
done

# If not found in common IPs, scan the entire subnet (skip .0 and .255)
# This is slower but more thorough
for i in {2..254}; do
    ip="${NETWORK_PREFIX}.$i"

    # Skip IPs we already checked
    skip=false
    for common_ip in "${COMMON_IPS[@]}"; do
        if [ "$ip" = "$common_ip" ]; then
            skip=true
            break
        fi
    done

    if [ "$skip" = false ]; then
        if check_host "$ip"; then
            echo "$ip"
            exit 0
        fi
    fi
done

# H16 not found
exit 1
