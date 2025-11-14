#!/bin/bash
#
# DPM SystemTools - Dependency Installation Script (Linux/macOS)
# =============================================================
#
# Installs Python dependencies required for SystemTools GUI and log aggregator
#
# Usage:
#   chmod +x install_dependencies.sh
#   ./install_dependencies.sh
#

set -e  # Exit on error

echo "========================================"
echo "DPM SystemTools - Dependency Installer"
echo "========================================"
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
PYTHON_CMD=""

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ ERROR: Python not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "   Found: Python $PYTHON_VERSION"

# Check if Python version is 3.8+
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ ERROR: Python 3.8+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "   ✅ Python version OK"
echo ""

# Check pip
echo "[2/4] Checking pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "❌ ERROR: pip not found. Please install pip."
    exit 1
fi

PIP_VERSION=$($PYTHON_CMD -m pip --version | awk '{print $2}')
echo "   Found: pip $PIP_VERSION"
echo "   ✅ pip OK"
echo ""

# Check tkinter (built-in, but needs to be installed on some systems)
echo "[3/4] Checking tkinter..."
if ! $PYTHON_CMD -c "import tkinter" &> /dev/null; then
    echo "⚠️  WARNING: tkinter not found (required for GUI)"
    echo "   Install with: sudo apt-get install python3-tk  (Ubuntu/Debian)"
    echo "   Install with: sudo yum install python3-tkinter  (CentOS/RHEL)"
    echo "   Install with: brew install python-tk  (macOS)"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "   ✅ tkinter OK"
fi
echo ""

# Install dependencies
echo "[4/4] Installing Python dependencies from requirements.txt..."
echo ""

if [ ! -f "requirements.txt" ]; then
    echo "❌ ERROR: requirements.txt not found"
    echo "   Make sure you're running this script from the SystemTools directory"
    exit 1
fi

echo "Installing packages:"
echo "  - paramiko (SSH client)"
echo "  - matplotlib (data visualization)"
echo "  - rich (terminal UI)"
echo ""

$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "========================================"
echo "✅ Installation Complete!"
echo "========================================"
echo ""
echo "You can now run:"
echo "  - GUI application:      $PYTHON_CMD main.py"
echo "  - Log aggregator (CLI): $PYTHON_CMD log_aggregator.py"
echo ""
echo "For help, see: README.md"
echo ""
