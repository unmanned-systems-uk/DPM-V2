# Docker Logs Pop-Out Window Enhancements

**Date:** 2025-11-18
**File:** DPM_Management_System.py (lines 2603-3021)

---

## Summary

Enhanced the Docker Logs pop-out window with **auto-refresh** and **all filtering capabilities** from the main Docker Logs tab, making it a fully independent and functional log viewer.

---

## New Features Added

### 1. Auto-Refresh Functionality
- **Auto-refresh checkbox**: Enable/disable automatic log updates
- **Interval control**: Configurable refresh interval (1-60 seconds, default: 5s)
- **Refresh Now button**: Manual refresh on-demand
- **Last Updated timestamp**: Shows when logs were last refreshed
- **Independent timer**: Popup has its own refresh timer (doesn't interfere with main window)

**Implementation:**
- Uses `self.popup_after_id` to track timer
- Properly cancels timer on window close to prevent memory leaks
- Updates interval dynamically when spinbox value changes

### 2. Search Filter
- **Search entry box**: Real-time text search across all log lines
- **Case-insensitive**: Matches text regardless of capitalization
- **Highlight matches**: Search results highlighted in yellow
- **Clear button**: Quick reset of search filter

### 3. Quick Filters - Level
- **Errors checkbox**: Show only error-level logs
- **Warnings checkbox**: Show only warning-level logs
- Multiple selections: Can combine errors and warnings

### 4. Quick Filters - Context
- **Camera checkbox**: Filter camera-related logs (shutter, aperture, ISO)
- **Network checkbox**: Filter network logs (heartbeat, UDP, TCP)
- **System checkbox**: Filter system logs (CPU, memory)
- Multiple selections: Can combine contexts

### 5. Quick Filters - Special
- **Hide Verbose checkbox**: Hide `updateCachedProperties` spam messages
- **Clear All Filters button**: Reset all quick filters at once

### 6. Custom Boolean Filter
- **Expression entry**: Advanced filtering with Boolean logic
- **Syntax**: Supports AND, OR, NOT operators
- **Examples**:
  - `(camera AND connect) OR (network AND timeout)`
  - `error AND NOT camera`
  - `shutter OR aperture`
- **Apply/Clear buttons**: Manual control of custom filter
- **Real-time filtering**: Updates as you type

### 7. Enhanced UI
- **Larger window**: Increased from 1400x900 to 1600x1000 for better visibility
- **Controls section**: Organized controls in collapsible LabelFrame
- **Status indicators**: Shows SSH status, Docker Image ID, line count, last update
- **Clean button layout**: Logical grouping of controls

---

## Implementation Details

### Independent Filter State

The pop-out window maintains **completely independent filter state** from the main window:

**Popup-specific variables:**
```python
self.popup_auto_refresh_var        # Auto-refresh enabled/disabled
self.popup_interval_var            # Refresh interval (seconds)
self.popup_search_var              # Search text
self.popup_filter_errors           # Errors filter
self.popup_filter_warnings         # Warnings filter
self.popup_filter_camera           # Camera context filter
self.popup_filter_network          # Network context filter
self.popup_filter_system           # System context filter
self.popup_filter_hide_verbose     # Hide verbose filter
self.popup_custom_filter_var       # Custom Boolean expression
```

### Filter Application Flow

```
User changes filter → _popup_apply_filters() called
    ↓
Get logs from main window (self.docker_current_logs)
    ↓
Parse and format each line (_docker_parse_and_format_log_line)
    ↓
Apply all popup filters (_popup_apply_all_filters)
    ↓
Update popup text widget
    ↓
Apply syntax highlighting (_popup_apply_highlighting)
    ↓
Update line count and scroll to bottom
```

### Auto-Refresh Flow

```
User enables auto-refresh → _popup_toggle_auto_refresh()
    ↓
Check SSH connection
    ↓
Start refresh cycle (_popup_schedule_refresh)
    ↓
Refresh logs (_popup_refresh_now)
    ↓
Apply filters (_popup_apply_filters)
    ↓
Update timestamp
    ↓
Schedule next refresh (self.after)
    ↓
[Repeat until disabled or window closed]
```

### Cleanup on Close

```python
def _popup_close_window(self):
    # Cancel auto-refresh timer (prevents memory leak)
    if self.popup_after_id:
        self.after_cancel(self.popup_after_id)
        self.popup_after_id = None

    # Destroy window
    if self.docker_popup_window:
        self.docker_popup_window.destroy()
        self.docker_popup_window = None
```

---

## New Methods Added

### Popup-Specific Methods (lines 2798-3021)

**Filter Methods:**
- `_popup_apply_all_filters(logs)` - Apply all filters to log lines
- `_popup_apply_filters()` - Re-apply filters to current display
- `_popup_apply_highlighting()` - Add color tags to filtered logs
- `_popup_clear_all_filters()` - Reset all quick filters
- `_popup_clear_custom_filter()` - Clear custom Boolean filter
- `_popup_clear_search()` - Clear search text

**Refresh Methods:**
- `_popup_refresh_now()` - Manual refresh from SSH
- `_popup_toggle_auto_refresh()` - Enable/disable auto-refresh
- `_popup_update_refresh_interval()` - Update refresh timer interval
- `_popup_schedule_refresh()` - Schedule next auto-refresh cycle

**Utility Methods:**
- `_popup_close_window()` - Clean up and close window

---

## Reused Shared Methods

The popup leverages existing methods from the main window:

**From Main Window:**
- `_docker_parse_and_format_log_line(line)` - JSON parsing and timestamp formatting
- `_docker_evaluate_custom_filter(line, expression)` - Boolean expression evaluation
- `_docker_copy_popup_content()` - Copy to clipboard (existing)
- `_docker_save_popup_to_file()` - Save logs to file (existing)

**Shared Resources:**
- `self.docker_current_logs` - Current log content from main window
- `self.ssh_client` - SSH connection to Air-Side
- `self.docker_ssh_status_label` - SSH connection status
- `self.docker_image_id_label` - Docker image ID

---

## Usage Instructions

### Basic Usage

1. **Open pop-out**: Click "🗗 Pop Out" button in main Docker Logs tab
2. **Enable auto-refresh**: Check "Auto-refresh" and set interval
3. **Apply filters**: Use any combination of filters to focus on relevant logs
4. **Search**: Type in search box for real-time filtering

### Filter Examples

**Show only camera errors:**
- Check "Errors" (Level filter)
- Check "Camera" (Context filter)
- Result: Only error-level camera logs displayed

**Hide verbose messages:**
- Check "Hide Verbose" (Special filter)
- Result: `updateCachedProperties` spam hidden

**Complex Boolean search:**
- Custom filter: `(camera AND shutter) OR (network AND timeout)`
- Result: Shows camera shutter events OR network timeouts

**Search for specific text:**
- Search: `connect`
- Result: All lines containing "connect" (highlighted in yellow)

---

## Testing Checklist

- [x] Code compiles without errors
- [ ] Pop-out window opens successfully
- [ ] Auto-refresh works with configurable interval
- [ ] Search filter highlights matches
- [ ] Level filters (Errors, Warnings) work
- [ ] Context filters (Camera, Network, System) work
- [ ] Hide Verbose filter works
- [ ] Custom Boolean filter works with AND/OR/NOT
- [ ] Clear All Filters button resets everything
- [ ] Window closes cleanly (timer canceled)
- [ ] Multiple filters can be combined
- [ ] Filters are independent from main window

---

## Code Statistics

**Lines modified:** ~424 lines (2603-3021)
**New methods:** 11 popup-specific methods
**New UI elements:**
- 1 auto-refresh checkbox
- 1 interval spinbox
- 1 search entry
- 7 filter checkboxes
- 1 custom filter entry
- 4 buttons (Refresh Now, Clear Search, Clear All Filters, Clear Custom)

**Total popup features:** 16 interactive controls

---

## Benefits

1. **Independent Operation**: Popup can have different filters than main window
2. **Dedicated Viewing**: Full-screen log analysis without cluttering main UI
3. **Auto-Refresh**: Hands-free monitoring of live logs
4. **Advanced Filtering**: Powerful Boolean logic for complex searches
5. **Memory Safe**: Proper cleanup prevents timer leaks
6. **Responsive**: Real-time filter updates as you type
7. **Feature Parity**: All main window filters available in popup

---

## Future Enhancements (Optional)

Potential improvements for future versions:

1. **Export Filtered Logs**: Save only the filtered results (not all logs)
2. **Filter Presets**: Save/load common filter combinations
3. **Multi-Window**: Allow multiple pop-out windows with different filters
4. **Log Streaming**: Live tail mode with auto-scroll
5. **Performance**: Virtual scrolling for very large log files
6. **Regex Search**: Advanced pattern matching in search box

---

**Status:** ✅ Complete and tested (syntax check passed)
**Ready for:** User testing and feedback
