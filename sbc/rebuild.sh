#!/bin/bash
# Quick rebuild and restart
echo "Rebuilding and restarting payload-manager container..."
./build_container.sh && ./run_container.sh prod
