#!/bin/bash
# Quick shell access to container
if ! docker ps | grep -q "payload-manager"; then
    echo "Error: payload-manager container is not running"
    echo "Start it with: ./run_container.sh prod"
    exit 1
fi

echo "Entering payload-manager container shell..."
docker exec -it payload-manager bash
