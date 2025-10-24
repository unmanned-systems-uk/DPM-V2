#!/bin/bash
# setup_docker_env.sh - Set up Docker environment on Raspberry Pi
# Usage: ./setup_docker_env.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Docker Environment Setup${NC}"
echo -e "${GREEN}For Payload Manager Development${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Error: Do not run this script as root${NC}"
    echo "Run as normal user with sudo privileges"
    exit 1
fi

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

# Step 3: Create directory structure
echo -e "${BLUE}Step 3: Creating directory structure...${NC}"
mkdir -p ~/payload_docker/src
mkdir -p ~/payload_docker/logs
mkdir -p ~/payload_docker/tests
cd ~/payload_docker

echo -e "${GREEN}✓ Directory structure created${NC}"
echo "  ~/payload_docker/"
echo "    ├── src/           (Application code)"
echo "    ├── logs/          (Runtime logs)"
echo "    ├── tests/         (Test scripts)"
echo "    └── sony_sdk/      (Sony SDK - YOU NEED TO COPY THIS)"
echo ""

# Step 4: Check for Sony SDK
echo -e "${BLUE}Step 4: Checking for Sony SDK...${NC}"
if [ -d "sony_sdk" ]; then
    echo -e "${GREEN}✓ Sony SDK found${NC}"
else
    echo -e "${YELLOW}⚠ Sony SDK not found${NC}"
    echo ""
    echo "You need to copy the Sony Camera Remote SDK:"
    echo "  1. Extract the SDK from Sony's package"
    echo "  2. Copy it to: ~/payload_docker/sony_sdk/"
    echo ""
    echo "Expected structure:"
    echo "  ~/payload_docker/sony_sdk/"
    echo "    ├── lib/"
    echo "    │   └── libCr_Core.so"
    echo "    ├── include/"
    echo "    └── samples/"
    echo ""
fi
echo ""

# Step 5: Copy helper scripts
echo -e "${BLUE}Step 5: Creating helper scripts...${NC}"

# Test script
cat > test_camera.sh << 'EOF'
#!/bin/bash
# Test camera connection inside container
echo "Testing camera connection..."
docker exec payload-manager lsusb | grep -i sony || echo "No Sony camera detected"
EOF
chmod +x test_camera.sh

# Quick rebuild script
cat > rebuild.sh << 'EOF'
#!/bin/bash
# Quick rebuild and restart
./build_container.sh && ./run_container.sh prod
EOF
chmod +x rebuild.sh

echo -e "${GREEN}✓ Helper scripts created${NC}"
echo "  - test_camera.sh   (Test USB camera connection)"
echo "  - rebuild.sh       (Quick rebuild + restart)"
echo ""

# Step 6: Create placeholder source files
echo -e "${BLUE}Step 6: Creating placeholder source files...${NC}"

cat > src/payload_server.py << 'EOF'
#!/usr/bin/env python3
"""
Payload Manager TCP Server
Placeholder - replace with actual implementation
"""

import socket
import sys

def main():
    print("Payload Manager Server Starting...")
    print("This is a placeholder - replace with actual implementation")
    print(f"Python version: {sys.version}")
    
    # Simple test server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 5000))
        sock.listen(5)
        print("✓ TCP server listening on port 5000")
        
        while True:
            conn, addr = sock.accept()
            print(f"Connection from {addr}")
            conn.send(b"Placeholder server\n")
            conn.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

echo -e "${GREEN}✓ Placeholder source files created${NC}"
echo ""

# Step 7: Network configuration check
echo -e "${BLUE}Step 7: Checking network configuration...${NC}"
IP_ADDR=$(ip addr show | grep "inet 192.168.144" | awk '{print $2}' | cut -d/ -f1)
if [ -n "$IP_ADDR" ]; then
    echo -e "${GREEN}✓ Found H16 network interface: $IP_ADDR${NC}"
else
    echo -e "${YELLOW}⚠ No 192.168.144.x address found${NC}"
    echo "  This is normal if H16 hardware is not connected yet"
    echo "  Expected address: 192.168.144.20"
fi
echo ""

# Step 8: Create README
cat > README.md << 'EOF'
# Payload Manager Docker Environment

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

## Development Workflow

### Edit Code
Edit files in `src/` directory. In dev mode, changes are live.

### View Logs
```bash
docker logs -f payload-manager
```

### Restart
```bash
docker restart payload-manager
```

### Shell Access
```bash
docker exec -it payload-manager bash
```

### Rebuild
```bash
./rebuild.sh
```

## Directory Structure
```
~/payload_docker/
├── Dockerfile              # Container definition
├── build_container.sh      # Build script
├── run_container.sh        # Run script
├── test_camera.sh          # Test helper
├── rebuild.sh              # Quick rebuild
├── sony_sdk/              # Sony SDK (you provide)
├── src/                   # Application code
│   └── payload_server.py
├── logs/                  # Runtime logs
└── tests/                 # Test scripts
```

## Network Configuration
- Container uses host networking
- Services bind to 192.168.144.20
- Ports: 5000 (TCP), 5001 (UDP), 5002 (UDP)

## Troubleshooting

### Container won't start
```bash
docker logs payload-manager
```

### Camera not detected
```bash
# Check USB devices
docker exec payload-manager lsusb

# Check Sony camera specifically
docker exec payload-manager lsusb | grep Sony
```

### Network issues
```bash
# Check container networking
docker exec payload-manager ip addr

# Test connectivity from H16
# On H16: nc -zv 192.168.144.20 5000
```

### Rebuild from scratch
```bash
docker stop payload-manager
docker rm payload-manager
docker rmi payload-manager:latest
./build_container.sh
./run_container.sh prod
```
EOF

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Copy Sony SDK to this directory:"
echo "   ${GREEN}mkdir sony_sdk${NC}"
echo "   ${GREEN}cp -r /path/to/sony/sdk/* sony_sdk/${NC}"
echo ""
echo "2. Review the directory structure:"
echo "   ${GREEN}ls -la${NC}"
echo ""
echo "3. Add your application code to src/"
echo "   ${GREEN}nano src/payload_server.py${NC}"
echo ""
echo "4. Build the Docker container:"
echo "   ${GREEN}./build_container.sh${NC}"
echo ""
echo "5. Run the container:"
echo "   ${GREEN}./run_container.sh prod${NC}"
echo ""
echo "See README.md for complete documentation"
echo ""
echo "Current location: $(pwd)"
