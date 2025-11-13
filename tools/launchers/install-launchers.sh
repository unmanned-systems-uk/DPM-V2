#!/bin/bash
# DPM-V2 Domain Launchers Installation Script
# Installs desktop launchers to user's application menu

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "==========================================="
echo "  DPM-V2 Domain Launchers Installer"
echo "==========================================="
echo ""

# Create desktop applications directory if it doesn't exist
if [ ! -d "$DESKTOP_DIR" ]; then
    echo "Creating applications directory: $DESKTOP_DIR"
    mkdir -p "$DESKTOP_DIR"
fi

# List of desktop files to install
DESKTOP_FILES=(
    "DPM-Air-Side.desktop"
    "DPM-Ground-Side.desktop"
    "DPM-SystemTools.desktop"
    "DPM-PM.desktop"
    "CCPM.desktop"
)

echo "Installing desktop launchers..."
echo ""

INSTALLED_COUNT=0
for desktop_file in "${DESKTOP_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$desktop_file" ]; then
        echo "  Installing: $desktop_file"
        cp "$SCRIPT_DIR/$desktop_file" "$DESKTOP_DIR/"
        chmod +x "$DESKTOP_DIR/$desktop_file"
        ((INSTALLED_COUNT++))
    else
        echo "  WARNING: $desktop_file not found, skipping"
    fi
done

echo ""
echo "Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
    echo "  Desktop database updated"
else
    echo "  WARNING: update-desktop-database not found"
    echo "  You may need to log out and back in for launchers to appear"
fi

echo ""
echo "==========================================="
echo "  Installation Complete!"
echo "==========================================="
echo ""
echo "Installed $INSTALLED_COUNT launcher(s) to: $DESKTOP_DIR"
echo ""
echo "Launchers installed:"
for desktop_file in "${DESKTOP_FILES[@]}"; do
    if [ -f "$DESKTOP_DIR/$desktop_file" ]; then
        NAME=$(grep "^Name=" "$DESKTOP_DIR/$desktop_file" | cut -d'=' -f2)
        echo "  ✓ $NAME"
    fi
done

echo ""
echo "To use the launchers:"
echo "  1. Open your application menu"
echo "  2. Search for 'DPM' or 'CCPM'"
echo "  3. Click the launcher you want"
echo ""
echo "Or run directly from command line:"
echo "  $SCRIPT_DIR/start-air-side.sh"
echo "  $SCRIPT_DIR/start-ground-side.sh"
echo "  $SCRIPT_DIR/start-systemtools.sh"
echo "  $SCRIPT_DIR/start-pm.sh"
echo "  $SCRIPT_DIR/start-ccpm.sh"
echo ""
echo "For more information, see: $SCRIPT_DIR/README.md"
echo ""
