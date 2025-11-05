# DevTools Mode Guide
*Development and Deployment Configuration*

## Overview

DevTools (formerly SystemTools/WindowsTools) now supports two operation modes:
- **Development Mode**: Full features for development and debugging
- **Deployment Mode**: Optimized for production use

Additionally, DevTools supports both GUI and CLI interfaces, selectable per mode.

## Operating Modes

### Development Mode
Full-featured mode for development and debugging:
- Verbose logging (DEBUG level)
- Debug panels enabled
- Auto-reload functionality
- Raw data display
- Mock data for testing
- Performance statistics
- Remote debugging
- Large log files (100MB max)

### Deployment Mode
Optimized mode for production use:
- Minimal logging (INFO level)
- Debug panels hidden
- No auto-reload
- Clean data display
- No mock data
- Performance monitoring off
- Remote debugging disabled
- Small log files (10MB max)

## UI Modes

### GUI Mode
- Full graphical interface with tabs
- Visual monitoring dashboards
- Interactive controls
- Real-time graphs and charts
- Multi-panel layout

### CLI Mode
- Command-line interface
- Compact text output
- Interactive command prompt
- Colored terminal output
- Scriptable operations

### Auto Mode
- Automatically detects environment
- Uses GUI if display available
- Falls back to CLI if headless

## Usage

### Command Line Arguments

```bash
# Run in development mode with GUI
python main.py --mode development --ui gui

# Run in deployment mode with CLI
python main.py --mode deployment --ui cli

# Run in deployment mode with auto UI detection
python main.py --mode deploy --ui auto

# Short forms
python main.py --mode dev    # Development mode
python main.py --mode deploy # Deployment mode

# Enable verbose output
python main.py --verbose
python main.py -v

# Use custom config file
python main.py --config /path/to/config.json
```

### Configuration File

DevTools creates a `devtools.json` configuration file:

```json
{
  "mode": "development",
  "ui_mode": "auto",
  "development": {
    "verbose_logging": true,
    "debug_panels": true,
    "auto_reload": true,
    "show_raw_data": true,
    "enable_mock_data": true,
    "log_level": "DEBUG",
    "save_all_logs": true,
    "show_performance_stats": true,
    "enable_remote_debug": true,
    "max_log_size_mb": 100
  },
  "deployment": {
    "verbose_logging": false,
    "debug_panels": false,
    "auto_reload": false,
    "show_raw_data": false,
    "enable_mock_data": false,
    "log_level": "INFO",
    "save_all_logs": false,
    "show_performance_stats": false,
    "enable_remote_debug": false,
    "max_log_size_mb": 10
  },
  "cli_options": {
    "colored_output": true,
    "compact_display": true,
    "auto_connect": true,
    "show_banner": false,
    "interactive_mode": true
  },
  "gui_options": {
    "theme": "modern",
    "window_size": [1400, 900],
    "auto_arrange": true,
    "show_tooltips": true,
    "enable_animations": true
  }
}
```

## CLI Mode Commands

When running in CLI mode with interactive mode enabled:

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `connect` | Connect to air-side |
| `disconnect` | Disconnect from air-side |
| `status` | Show current system status |
| `send <cmd>` | Send command to air-side |
| `list` | List available protocol commands |
| `clear` | Clear terminal screen |
| `quit`/`exit` | Exit program |

## Mode Selection Logic

1. **Command line arguments** override all settings
2. **Configuration file** provides defaults
3. **Auto-detection** used when UI mode is "auto"

### Auto-Detection Logic
```
IF display available AND tkinter installed:
    Use GUI mode
ELSE:
    Use CLI mode
```

## Examples

### Development Workstation
```bash
# Full development features with GUI
python main.py --mode development --ui gui
```

### Production Deployment on H16
```bash
# Minimal features, CLI only
python main.py --mode deployment --ui cli
```

### Remote SSH Session
```bash
# Auto-detect headless environment, use CLI
python main.py --mode deployment
```

### Testing Mock Data
```bash
# Development mode with mock data enabled
python main.py --mode dev --verbose
```

## Performance Comparison

| Feature | Development | Deployment |
|---------|------------|------------|
| Startup time | ~2 seconds | <1 second |
| Memory usage | ~150MB | ~50MB |
| Log file size | Up to 100MB | Up to 10MB |
| CPU usage | Moderate | Minimal |
| Network traffic | All data | Essential only |

## 🔴 CRITICAL: Callback Chaining Pattern

**MANDATORY for SystemTools/DevTools Development!**

When working with callbacks in SystemTools, **NEVER replace existing callbacks** as multiple components may be listening. Always use the callback chaining pattern:

### ❌ WRONG - Replaces callback:
```python
# This BREAKS other components!
connection_manager.set_status_callback(my_new_callback)
```

### ✅ CORRECT - Chains callback:
```python
# Get existing callback
existing_callback = connection_manager.status_callback

# Create new callback that calls both
def chained_callback(data):
    # Call existing first (maintains others' functionality)
    if existing_callback:
        existing_callback(data)

    # Then do your work
    my_processing(data)

# Set the chained callback
connection_manager.set_status_callback(chained_callback)
```

### Why This Matters:
- Multiple tabs listen to the same callbacks
- Replacing a callback breaks other components
- Always chain to preserve functionality

### Callback Types in SystemTools:
- `status_callback` - UDP status messages (5 Hz)
- `heartbeat_callback` - UDP heartbeat messages (1 Hz)
- `response_callback` - TCP command responses
- `connection_callback` - TCP connection state changes

## Migration from WindowsTools

The tool has been renamed from WindowsTools → SystemTools → DevTools to reflect:
- Cross-platform support (Windows, Linux, Pi)
- Development/deployment mode support
- Universal usage across all domains

### What Changed
- Added mode configuration system
- Added CLI interface option
- Renamed to DevTools
- Cross-platform compatibility
- Configurable logging levels
- Performance optimizations

### What Stayed the Same
- All existing GUI functionality
- Network protocol support
- Command sending capability
- Status monitoring
- Heartbeat system

## Troubleshooting

### GUI Won't Start
```bash
# Force CLI mode
python main.py --ui cli
```

### Too Much Debug Output
```bash
# Use deployment mode
python main.py --mode deployment
```

### Need Debug Info in Deployment
```bash
# Override with verbose flag
python main.py --mode deployment --verbose
```

### Configuration Not Loading
```bash
# Specify config file explicitly
python main.py --config ./devtools.json
```

## Best Practices

### For Development
1. Use development mode during coding
2. Enable verbose logging for debugging
3. Use GUI for visual monitoring
4. Enable mock data for testing

### For Deployment
1. Use deployment mode in production
2. Use CLI mode on headless systems
3. Disable verbose logging
4. Monitor log file sizes

### For Testing
1. Test both modes before release
2. Verify CLI mode works headless
3. Check memory usage in deployment
4. Validate configuration loading

---

*DevTools Mode System - Flexible diagnostic tools for all environments*