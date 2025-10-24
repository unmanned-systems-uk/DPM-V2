#!/bin/bash
# setup_docker_env_monorepo.sh - Set up Docker in existing monorepo
# Usage: Run from your sbc/ directory in your monorepo

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Docker Environment Setup for Monorepo${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Error: Do not run this script as root${NC}"
    echo "Run as normal user with sudo privileges"
    exit 1
fi

# Detect if we're in a monorepo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '')"

if [ -n "$REPO_ROOT" ]; then
    echo -e "${GREEN}✓ Detected Git repository at: $REPO_ROOT${NC}"
    
    # Check if we're in sbc/ subdirectory
    if [[ "$SCRIPT_DIR" == "$REPO_ROOT/sbc" ]]; then
        echo -e "${GREEN}✓ Running from sbc/ directory - Perfect!${NC}"
    else
        echo -e "${YELLOW}⚠ Not in sbc/ directory${NC}"
        echo "Current: $SCRIPT_DIR"
        echo "Expected: $REPO_ROOT/sbc"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ Not in a Git repository${NC}"
    echo "This is OK, but monorepo workflow recommended"
fi
echo ""

# Step 1: Install Docker
echo -e "${BLUE}Step 1: Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # Add user to docker group
    echo -e "${YELLOW}Adding $USER to docker group...${NC}"
    sudo usermod -aG docker $USER
    
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}IMPORTANT: Log out and back in for group changes to take effect${NC}"
    echo -e "${YELLOW}Then run this script again.${NC}"
    echo -e "${YELLOW}========================================${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker --version
fi
echo ""

# Step 2: Check Docker access
echo -e "${BLUE}Step 2: Checking Docker access...${NC}"
if ! docker ps &> /dev/null; then
    echo -e "${RED}Error: Cannot access Docker${NC}"
    echo "You may need to log out and back in after adding user to docker group"
    echo "Or run: sudo usermod -aG docker $USER"
    exit 1
fi
echo -e "${GREEN}✓ Docker is accessible${NC}"
echo ""

# Step 3: Create directory structure (monorepo-aware)
echo -e "${BLUE}Step 3: Setting up directory structure...${NC}"

# Create subdirectories
mkdir -p src
mkdir -p tests
mkdir -p logs

echo -e "${GREEN}✓ Directory structure created in: $SCRIPT_DIR${NC}"
echo ""
echo "Current structure:"
echo "  $(basename $SCRIPT_DIR)/"
echo "    ├── src/           (Application code)"
echo "    ├── tests/         (Test scripts)"
echo "    ├── logs/          (Runtime logs)"
echo "    └── sony_sdk/      (Sony SDK - YOU NEED TO COPY THIS)"
echo ""

if [ -n "$REPO_ROOT" ]; then
    echo "In your monorepo:"
    echo "  $REPO_ROOT/"
    echo "    ├── sbc/         ← You are here"
    echo "    ├── android/     (Unaffected by Docker)"
    echo "    ├── shared/      (Optional: shared protocol definitions)"
    echo "    └── docs/        (Documentation)"
    echo ""
fi

# Step 4: Check for Sony SDK
echo -e "${BLUE}Step 4: Checking for Sony SDK...${NC}"
if [ -d "sony_sdk" ]; then
    echo -e "${GREEN}✓ Sony SDK found${NC}"
else
    echo -e "${YELLOW}⚠ Sony SDK not found${NC}"
    echo ""
    echo "You need to copy the Sony Camera Remote SDK:"
    echo "  1. Extract the SDK from Sony's package"
    echo "  2. Copy it to: $SCRIPT_DIR/sony_sdk/"
    echo ""
    echo "Command:"
    echo "  mkdir sony_sdk"
    echo "  cp -r /path/to/your/sony/sdk/* sony_sdk/"
    echo ""
fi
echo ""

# Step 5: Check for existing source files
echo -e "${BLUE}Step 5: Checking for existing source files...${NC}"
if [ -f "src/payload_server.py" ]; then
    echo -e "${GREEN}✓ Found existing src/payload_server.py${NC}"
    echo "  Will use existing file (not overwriting)"
else
    echo -e "${YELLOW}⚠ No src/payload_server.py found${NC}"
    echo "  Creating placeholder..."
    
    cat > src/payload_server.py << 'EOF'
#!/usr/bin/env python3
"""
Payload Manager TCP Server
Main entry point for the camera payload manager
"""

import socket
import sys
import json
from datetime import datetime

def main():
    print(f"Payload Manager Server Starting...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    
    # Simple test server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 5000))
        sock.listen(5)
        print("✓ TCP server listening on 0.0.0.0:5000")
        
        while True:
            conn, addr = sock.accept()
            print(f"Connection from {addr}")
            
            # Simple response
            response = {
                "status": "ok",
                "message": "Payload Manager placeholder server",
                "timestamp": datetime.now().isoformat()
            }
            conn.send(json.dumps(response).encode() + b"\n")
            conn.close()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        sock.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
    echo -e "${GREEN}✓ Created placeholder src/payload_server.py${NC}"
fi
echo ""

# Step 6: Create helper scripts
echo -e "${BLUE}Step 6: Creating helper scripts...${NC}"

# Test script
cat > test_camera.sh << 'EOF'
#!/bin/bash
# Test camera connection inside container
echo "Testing camera connection..."
docker exec payload-manager lsusb | grep -i sony || echo "⚠ No Sony camera detected"
EOF
chmod +x test_camera.sh

# Quick rebuild script
cat > rebuild.sh << 'EOF'
#!/bin/bash
# Quick rebuild and restart
./build_container.sh && ./run_container.sh prod
EOF
chmod +x rebuild.sh

# Shell access script
cat > shell.sh << 'EOF'
#!/bin/bash
# Quick shell access to container
docker exec -it payload-manager bash
EOF
chmod +x shell.sh

echo -e "${GREEN}✓ Helper scripts created${NC}"
echo "  - test_camera.sh   (Test USB camera connection)"
echo "  - rebuild.sh       (Quick rebuild + restart)"
echo "  - shell.sh         (Shell access to container)"
echo ""

# Step 7: Update .gitignore (if in Git repo)
echo -e "${BLUE}Step 7: Checking .gitignore...${NC}"
if [ -n "$REPO_ROOT" ]; then
    GITIGNORE="$REPO_ROOT/.gitignore"
    
    # Check if .gitignore exists
    if [ ! -f "$GITIGNORE" ]; then
        echo -e "${YELLOW}Creating new .gitignore...${NC}"
        touch "$GITIGNORE"
    fi
    
    # Add SBC-specific ignores if not present
    if ! grep -q "# SBC Docker artifacts" "$GITIGNORE"; then
        cat >> "$GITIGNORE" << 'EOF'

# SBC Docker artifacts
sbc/sony_sdk/
sbc/logs/
sbc/.env

# Python
sbc/__pycache__/
sbc/**/__pycache__/
sbc/**/*.pyc
sbc/**/*.pyo
sbc/**/*.pyd
sbc/.Python
EOF
        echo -e "${GREEN}✓ Updated .gitignore with SBC exclusions${NC}"
    else
        echo -e "${GREEN}✓ .gitignore already configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Not in Git repo, skipping .gitignore${NC}"
fi
echo ""

# Step 8: Network configuration check
echo -e "${BLUE}Step 8: Checking network configuration...${NC}"
IP_ADDR=$(ip addr show | grep "inet 192.168.144" | awk '{print $2}' | cut -d/ -f1)
if [ -n "$IP_ADDR" ]; then
    echo -e "${GREEN}✓ Found H16 network interface: $IP_ADDR${NC}"
else
    echo -e "${YELLOW}⚠ No 192.168.144.x address found${NC}"
    echo "  This is normal if H16 hardware is not connected yet"
    echo "  Expected address: 192.168.144.20"
fi
echo ""

# Step 9: Create README
cat > README_DOCKER.md << 'EOF'
# Docker Setup for SBC (Air-side)

## Quick Start

1. **Copy Sony SDK:**
   ```bash
   mkdir sony_sdk
   cp -r /path/to/sony/sdk/* sony_sdk/
   ```

2. **Build container:**
   ```bash
   ./build_container.sh
   ```

3. **Run container:**
   ```bash
   # Production mode
   ./run_container.sh prod
   
   # Development mode (live code editing)
   ./run_container.sh dev
   ```

4. **Test camera:**
   ```bash
   ./test_camera.sh
   ```

## Monorepo Structure

This is the SBC (air-side) component of the payload manager.

```
repo_root/
├── sbc/              ← Docker runs here
│   ├── Dockerfile
│   ├── src/          ← Your Python code
│   ├── sony_sdk/     ← Sony SDK (not in Git)
│   └── logs/         ← Runtime logs
└── android/          ← Completely separate, unaffected by Docker
```

## Development Workflow

### SBC Development (This Directory)
```bash
# Edit code
nano src/payload_server.py

# Run in dev mode (live reload)
./run_container.sh dev

# View logs
docker logs -f payload-manager

# Shell access
./shell.sh
```

### Android Development (Separate)
```bash
cd ../android
# Open in Android Studio
# Develop normally - Docker doesn't affect Android at all!
```

## Helper Scripts

- `build_container.sh` - Build Docker image
- `run_container.sh` - Run container (dev/prod)
- `test_camera.sh` - Test camera connection
- `rebuild.sh` - Quick rebuild + restart
- `shell.sh` - Shell access to container

## Network

- Container uses host networking
- Services bind to 192.168.144.20
- Ports: 5000 (TCP), 5001 (UDP), 5002 (UDP)

## Troubleshooting

See main documentation in ../docs/ or SOLUTION_SUMMARY.md
EOF

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Copy Sony SDK:"
echo "   ${GREEN}mkdir sony_sdk${NC}"
echo "   ${GREEN}cp -r /path/to/sony/sdk/* sony_sdk/${NC}"
echo ""
echo "2. Build Docker container:"
echo "   ${GREEN}./build_container.sh${NC}"
echo ""
echo "3. Run container:"
echo "   ${GREEN}./run_container.sh prod${NC}"
echo ""
echo "4. Develop your code:"
echo "   ${GREEN}nano src/payload_server.py${NC}"
echo ""

if [ -n "$REPO_ROOT" ]; then
    echo "Your monorepo structure is preserved:"
    echo "  - SBC code: $SCRIPT_DIR"
    echo "  - Android code: (in ../android/ if it exists)"
    echo "  - Shared code: (in ../shared/ if needed)"
    echo ""
fi

echo "Current location: $SCRIPT_DIR"
echo ""
echo "See README_DOCKER.md for more details"
