#!/bin/bash
# install-claude-settings.sh
# Installs Claude Code custom instructions in all three locations

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=============================================="
echo "  DPM Claude Code Settings Installation"
echo "=============================================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo ""

# Function to backup existing settings
backup_if_exists() {
    local file=$1
    if [ -f "$file" ]; then
        local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "  📦 Backing up existing file to: $backup"
        cp "$file" "$backup"
    fi
}

# Function to install settings file
install_settings() {
    local source=$1
    local dest_dir=$2
    local label=$3
    
    echo "Installing $label settings..."
    
    # Create directory if it doesn't exist
    mkdir -p "$dest_dir"
    
    # Backup existing file
    backup_if_exists "$dest_dir/settings.local.json"
    
    # Copy new settings
    cp "$source" "$dest_dir/settings.local.json"
    
    echo "  ✅ Installed: $dest_dir/settings.local.json"
    echo ""
}

# Check if source files exist
echo "Checking source files..."

if [ ! -f "$SCRIPT_DIR/sbc-settings.local.json" ]; then
    echo "❌ Error: sbc-settings.local.json not found in $SCRIPT_DIR"
    echo "   Please ensure all downloaded files are in the tools/ directory"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/android-settings.local.json" ]; then
    echo "❌ Error: android-settings.local.json not found in $SCRIPT_DIR"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/root-settings.local.json" ]; then
    echo "❌ Error: root-settings.local.json not found in $SCRIPT_DIR"
    exit 1
fi

echo "  ✅ All source files found"
echo ""

# Install Air-Side settings
install_settings \
    "$SCRIPT_DIR/sbc-settings.local.json" \
    "$PROJECT_ROOT/sbc/.claude" \
    "Air-Side (C++)"

# Install Ground-Side settings
install_settings \
    "$SCRIPT_DIR/android-settings.local.json" \
    "$PROJECT_ROOT/android/.claude" \
    "Ground-Side (Android)"

# Install Root-level settings
install_settings \
    "$SCRIPT_DIR/root-settings.local.json" \
    "$PROJECT_ROOT/.claude" \
    "Root (Documentation/Protocol)"

echo "=============================================="
echo "  ✅ Installation Complete!"
echo "=============================================="
echo ""
echo "Claude Code will now:"
echo "  • Read CC_READ_THIS_FIRST.md at session start"
echo "  • Execute protocol sync checks"
echo "  • Check for hardcoded values"
echo "  • Enforce specification-first architecture"
echo ""
echo "Test your installation:"
echo "  cd $PROJECT_ROOT/sbc"
echo "  claude-code"
echo "  # Should automatically execute session start checklist"
echo ""
echo "Settings installed in:"
echo "  • $PROJECT_ROOT/.claude/settings.local.json"
echo "  • $PROJECT_ROOT/sbc/.claude/settings.local.json"
echo "  • $PROJECT_ROOT/android/.claude/settings.local.json"
echo ""
echo "Backups (if any) saved with .backup.TIMESTAMP extension"
echo ""
