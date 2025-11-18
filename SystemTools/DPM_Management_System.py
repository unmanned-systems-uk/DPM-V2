#!/usr/bin/env python3
"""
DPM System Management Tool
=========================

Clean management interface for Air-Side and Ground-Side systems.
Built on proven backend infrastructure (network/*, utils/*).

Features (Phase 1 - Issue #118):
- Tri-domain log aggregation (from log_viewer_gui.py base)
- On-demand logging controls (NEW)

Backend Infrastructure (Reused):
- network/tcp_client.py - TCP connection to Air-Side
- network/ssh_client.py - SSH/Docker access
- network/log_listeners.py - UDP/TCP log aggregation
- network/udp_discovery.py - Auto IP detection
- network/protocol.py - DPM protocol message formatting
- utils/* (logger, config, etc.)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, Any, Optional
import json
import csv
import threading
import socket
import time
import logging

# REUSE existing backend (no changes needed!)
from network.tcp_client import TCPClient
from network.ssh_client import SSHClient
from network.adb_client import ADBClient
from network.log_listeners import AirSideListener, GroundSideListener
from network.udp_discovery import UDPDiscoverySender, load_discovery_config
from network.udp_listener import StatusListener, HeartbeatListener
from network.protocol import protocol_msg
from utils.logger import logger
from utils.config import config
from utils.log_colors import configure_tkinter_text_tags, get_buffer_max_entries
from utils.log_contexts import LogContexts
from utils.protocol_loader import protocol
from utils.log_filter_manager import LogFilterManager
from version import get_version_string, get_build_info_string

# Import dashboard tabs from DPM Diagnostics Tool
from gui.widgets import StatusIndicator, ScrolledTextLog
from gui.tab_connection import ConnectionTab
from gui.tab_config import ConfigTab
from gui.tab_remote_control import RemoteControlTab
from gui.tab_camera import CameraDashboardTab
from gui.tab_analytics import PerformanceAnalyticsTab
from gui.tab_file_browser import FileBrowserTab


class SystemToolsLogHandler(logging.Handler):
    """Custom logging handler to capture SystemTools logs and add to display queue"""

    def __init__(self, log_queue: deque):
        """Initialize handler with reference to log queue

        Args:
            log_queue: Deque to add log entries to
        """
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord):
        """Process a log record and add to queue

        Args:
            record: LogRecord from Python logging system
        """
        try:
            # Format log entry to match Air/Ground log structure
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'domain': 'SYSTEMTOOLS',
                'level': record.levelname,
                'context': record.name.upper(),  # Logger name as context
                'message': record.getMessage()
            }

            # Add to queue for display
            self.log_queue.append(log_entry)

        except Exception:
            # Don't let handler errors crash the application
            self.handleError(record)


class DPMManagementSystem(tk.Tk):
    """DPM System Management Tool - Clean GUI rebuild"""

    def __init__(self):
        super().__init__()

        self.title("DPM System Management Tool")
        self.geometry("1600x900")

        # Backend components (reuse existing classes)
        self.tcp_client: Optional[TCPClient] = None  # Created when connecting to Air-Side
        self.ssh_client: Optional[SSHClient] = None  # Created when connecting via SSH
        self.adb_client: Optional[ADBClient] = None  # Created when connecting to H16 (Ground-Side)
        max_entries = get_buffer_max_entries()
        self.log_queue = deque(maxlen=max_entries)

        # Listeners (from log_viewer_gui.py)
        self.air_listener: Optional[AirSideListener] = None
        self.ground_listener: Optional[GroundSideListener] = None
        self.discovery_sender: Optional[UDPDiscoverySender] = None
        self.systemtools_handler: Optional[SystemToolsLogHandler] = None  # For capturing SystemTools logs

        # UDP Listeners for dashboard tabs (from DPM Diagnostics Tool)
        self.status_listener: Optional[StatusListener] = None  # Port 5001 - receives status/camera properties
        self.heartbeat_listener: Optional[HeartbeatListener] = None  # Port 5002 - receives heartbeats

        # Stream state
        self.stream_running = False
        self.stream_paused = False

        # Display state
        self.auto_scroll = True
        self.last_update_time = None

        # Filters
        # Domain filters - checkboxes (all checked = show all domains)
        self.filter_air = tk.BooleanVar(value=True)
        self.filter_ground = tk.BooleanVar(value=True)
        self.filter_systemtools = tk.BooleanVar(value=True)
        self.filter_level = tk.StringVar(value="ALL")
        self.filter_context = tk.StringVar(value="ALL")
        self.filter_search = tk.StringVar()

        # Log Filter Manager (Issue #147 - Dynamic JSON-based filters)
        self.log_filter_manager = LogFilterManager()
        self.selected_filter_contexts = {}  # Track selected context checkboxes
        self.selected_filter_levels = {}  # Track selected level checkboxes
        self.filter_logic = tk.StringVar(value=self.log_filter_manager.get_ui_settings().get('default_logic', 'OR'))

        # GUI update thread
        self.gui_update_running = False
        self.gui_update_thread = None

        # Display buffer (for filtering)
        self.display_buffer = []

        # Config state
        self.original_config = None  # Store original config for change detection

        # Docker Logs pop-out window
        self.docker_popup_window = None
        self.docker_popup_text = None

        # Create GUI
        self._create_ui()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("DPM Management System initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Create tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Log Viewer (with on-demand logging controls)
        self.log_tab = self._create_log_viewer_tab()
        self.notebook.add(self.log_tab, text="Log Viewer")

        # Tab 2: Air-Side Config (Issue #117)
        self.airside_config_tab = self._create_airside_config_tab()
        self.notebook.add(self.airside_config_tab, text="Air-Side Config")

        # Tab 3: Docker Logs (Air-Side payload-manager logs via SSH)
        self.docker_logs_tab = self._create_docker_logs_tab()
        self.notebook.add(self.docker_logs_tab, text="Docker Logs")

        # Tab 4: Connection Monitor (Smart Connection Dashboard from DPM Diagnostics v1.12.1)
        self.connection_tab = ConnectionTab(self.notebook)
        self.notebook.add(self.connection_tab, text="Connection Monitor")

        # Tab 5: Configuration (SystemTools settings management)
        self.config_tab = ConfigTab(self.notebook)
        self.notebook.add(self.config_tab, text="⚙️ Configuration")

        # Tab 6: Camera Dashboard (from DPM Diagnostics v1.12.1)
        self.camera_tab = CameraDashboardTab(self.notebook)
        self.notebook.add(self.camera_tab, text="Camera Dashboard")

        # Tab 7: Performance Analytics (Deep Statistical Analysis - Issue #130)
        self.analytics_tab = PerformanceAnalyticsTab(self.notebook)
        self.notebook.add(self.analytics_tab, text="Performance Analytics")

        # Tab 8: File Browser (SFTP file transfer - Issue #133)
        self.file_browser_tab = FileBrowserTab(self.notebook)
        self.notebook.add(self.file_browser_tab.frame, text="📁 File Browser")

        # Tab 9: Remote Control (SSH command execution panel)
        # Create a simple SSH client accessor for RemoteControlTab
        class SSHClientAccessor:
            """Simple wrapper to provide ssh_client attribute for RemoteControlTab"""
            def __init__(self, parent):
                self.parent = parent

            @property
            def ssh_client(self):
                return self.parent.ssh_client

        self.ssh_accessor = SSHClientAccessor(self)
        self.remote_control_tab = RemoteControlTab(self.notebook, self.ssh_accessor)
        self.remote_control_tab.main_window = self  # Set main window reference for auto-connect
        self.notebook.add(self.remote_control_tab, text="🎮 Air-Side Remote")

        # Wire up clients to dashboard tabs
        self._wire_dashboard_clients()

        # Future tabs:
        # Tab 10: H16 Diagnostics (Issue #XXX)
        # Tab 11: Command Sender (future)
        # etc. - add incrementally

    def _create_log_viewer_tab(self):
        """Create log viewer tab (migrate from log_viewer_gui.py)"""
        frame = ttk.Frame(self.notebook)

        # Top: Title and Connection Status
        header_frame = ttk.Frame(frame, padding=10)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="📊 Tri-Domain Log Aggregation Viewer",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        # Air-Side Connection Status
        connection_frame = ttk.Frame(header_frame)
        connection_frame.pack(side=tk.RIGHT, padx=10)

        ttk.Label(connection_frame, text="Air-Side TCP:").pack(side=tk.LEFT, padx=5)
        self.airside_connection_status = ttk.Label(connection_frame, text="Not Connected",
                                                    foreground="red", font=('Arial', 9, 'bold'))
        self.airside_connection_status.pack(side=tk.LEFT, padx=5)

        # TCP Connect/Disconnect buttons
        ttk.Button(connection_frame, text="Connect", command=self._tcp_connect, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(connection_frame, text="Disconnect", command=self.disconnect_from_airside, width=10).pack(side=tk.LEFT, padx=2)

        # Control panel
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # LEFT SIDE: On-Demand Logging Controls (NEW for Issue #118)
        logging_control = ttk.LabelFrame(control_frame, text="On-Demand Logging", padding=10)
        logging_control.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Air-Side logging
        air_frame = ttk.Frame(logging_control)
        air_frame.pack(fill=tk.X, pady=2)

        ttk.Label(air_frame, text="Air-Side:", width=12).pack(side=tk.LEFT)

        self.air_duration = ttk.Spinbox(air_frame, from_=10, to=3600, width=8)
        self.air_duration.set(600)  # Default 10 minutes
        self.air_duration.pack(side=tk.LEFT, padx=2)

        ttk.Label(air_frame, text="sec").pack(side=tk.LEFT, padx=2)

        self.air_request_btn = ttk.Button(air_frame, text="Request Logs",
                                          command=self._request_air_logs, width=12)
        self.air_request_btn.pack(side=tk.LEFT, padx=2)

        self.air_stop_btn = ttk.Button(air_frame, text="Stop",
                                       command=self._stop_air_logs, width=8, state=tk.DISABLED)
        self.air_stop_btn.pack(side=tk.LEFT, padx=2)

        # Air-Side status
        air_status_frame = ttk.Frame(logging_control)
        air_status_frame.pack(fill=tk.X, pady=2)

        ttk.Label(air_status_frame, text="Status:", width=12).pack(side=tk.LEFT)
        self.air_log_status = ttk.Label(air_status_frame, text="Idle", foreground="gray")
        self.air_log_status.pack(side=tk.LEFT, padx=2)

        # Ground-Side logging (future - Issue #119)
        ground_frame = ttk.Frame(logging_control)
        ground_frame.pack(fill=tk.X, pady=2)

        ttk.Label(ground_frame, text="Ground-Side:", width=12).pack(side=tk.LEFT)
        ttk.Label(ground_frame, text="(Not implemented)", foreground="gray").pack(side=tk.LEFT)

        # RIGHT SIDE: Stream Controls
        stream_controls_frame = ttk.LabelFrame(control_frame, text="Stream Controls", padding=10)
        stream_controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status row
        status_row = ttk.Frame(stream_controls_frame)
        status_row.pack(fill=tk.X, pady=5)

        ttk.Label(status_row, text="Passive Logging:").pack(side=tk.LEFT, padx=5)
        self.status_indicator = tk.Canvas(status_row, width=20, height=20, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self._update_status_indicator("stopped")

        self.status_label = ttk.Label(status_row, text="Stopped", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Buttons row
        button_row = ttk.Frame(stream_controls_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(button_row, text="▶ Start", command=self._on_start, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(button_row, text="⏸ Pause", command=self._on_pause, state=tk.DISABLED, width=12)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_row, text="⏹ Stop", command=self._on_stop, state=tk.DISABLED, width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Separator(button_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        ttk.Button(button_row, text="Clear", command=self._on_clear, width=10).pack(side=tk.LEFT, padx=5)

        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_row, text="Auto-scroll", variable=self.auto_scroll_var,
                       command=self._on_auto_scroll_changed).pack(side=tk.LEFT, padx=10)

        # Filters Frame
        filters_frame = ttk.LabelFrame(frame, text="Filters (Accumulative AND Logic)", padding=10)
        filters_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter row 1
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row1, text="Domain:").pack(side=tk.LEFT, padx=5)
        # Checkbox filters (multi-selection with OR logic)
        ttk.Checkbutton(filter_row1, text="Air-Side", variable=self.filter_air,
                       command=self._on_filter_changed).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(filter_row1, text="Ground-Side", variable=self.filter_ground,
                       command=self._on_filter_changed).pack(side=tk.LEFT, padx=3)
        ttk.Checkbutton(filter_row1, text="SystemTools", variable=self.filter_systemtools,
                       command=self._on_filter_changed).pack(side=tk.LEFT, padx=3)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Label(filter_row1, text="Level:").pack(side=tk.LEFT, padx=5)
        level_combo = ttk.Combobox(filter_row1, textvariable=self.filter_level,
                                   values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Label(filter_row1, text="Context:").pack(side=tk.LEFT, padx=5)
        context_combo = ttk.Combobox(filter_row1, textvariable=self.filter_context,
                                     values=["ALL", "CAMERA", "NETWORK", "COMMAND", "UI", "SYSTEM"], state="readonly", width=12)
        context_combo.pack(side=tk.LEFT, padx=5)
        context_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Filter row 2: Text search
        filter_row2 = ttk.Frame(filters_frame)
        filter_row2.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row2, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_row2, textvariable=self.filter_search, width=50)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self._on_filter_changed)

        ttk.Button(filter_row2, text="Clear", command=self._on_clear_search).pack(side=tk.LEFT, padx=5)

        # Last update
        ttk.Label(filter_row2, text="Last Update:").pack(side=tk.RIGHT, padx=5)
        self.last_update_label = ttk.Label(filter_row2, text="Never", font=('Arial', 9, 'italic'))
        self.last_update_label.pack(side=tk.RIGHT, padx=5)

        # Filter row 3: Dynamic Multi-Select Context Filters (Issue #147)
        filter_row3 = ttk.Frame(filters_frame)
        filter_row3.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row3, text="Log Contexts:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        # Generate context checkboxes from JSON
        for ctx in self.log_filter_manager.get_log_contexts():
            label = ctx['label']
            var = tk.BooleanVar(value=False)
            self.selected_filter_contexts[label] = var
            cb = ttk.Checkbutton(filter_row3, text=label, variable=var,
                                command=lambda: self._on_dynamic_filter_changed())
            cb.pack(side=tk.LEFT, padx=3)

        ttk.Separator(filter_row3, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Button(filter_row3, text="Select All", command=self._select_all_contexts, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_row3, text="Clear All", command=self._clear_all_contexts, width=10).pack(side=tk.LEFT, padx=2)

        # Filter row 4: Dynamic Multi-Select Level Filters
        filter_row4 = ttk.Frame(filters_frame)
        filter_row4.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row4, text="Log Levels:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        # Generate level checkboxes from JSON
        for lvl in self.log_filter_manager.get_log_levels():
            label = lvl['label']
            var = tk.BooleanVar(value=False)
            self.selected_filter_levels[label] = var
            cb = ttk.Checkbutton(filter_row4, text=label, variable=var,
                                command=lambda: self._on_dynamic_filter_changed())
            cb.pack(side=tk.LEFT, padx=3)

        ttk.Separator(filter_row4, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Button(filter_row4, text="Select All", command=self._select_all_levels, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_row4, text="Clear All", command=self._clear_all_levels, width=10).pack(side=tk.LEFT, padx=2)

        # Filter row 5: Filter Logic Toggle
        filter_row5 = ttk.Frame(filters_frame)
        filter_row5.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row5, text="Filter Logic:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_row5, text="OR (show if ANY selected filter matches)",
                       variable=self.filter_logic, value="OR",
                       command=lambda: self._on_dynamic_filter_changed()).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(filter_row5, text="AND (show only if ALL selected filters match)",
                       variable=self.filter_logic, value="AND",
                       command=lambda: self._on_dynamic_filter_changed()).pack(side=tk.LEFT, padx=5)

        ttk.Separator(filter_row5, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Button(filter_row5, text="🔄 Refresh Filters", command=self._refresh_filter_labels, width=15).pack(side=tk.LEFT, padx=5)

        # Filter row 6: Preset Filters
        filter_row6 = ttk.Frame(filters_frame)
        filter_row6.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row6, text="Presets:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        # Generate preset buttons from JSON
        for preset in self.log_filter_manager.get_filter_presets():
            preset_name = preset['name']
            ttk.Button(filter_row6, text=preset_name,
                      command=lambda p=preset_name: self._apply_preset(p),
                      width=15).pack(side=tk.LEFT, padx=2)

        # Filter row 7: Custom Expression (with Apply button - NO real-time filtering)
        filter_row7 = ttk.Frame(filters_frame)
        filter_row7.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row7, text="Custom Expression:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.filter_custom = tk.StringVar()
        custom_filter_entry = ttk.Entry(filter_row7, textvariable=self.filter_custom, width=50)
        custom_filter_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        # NOTE: NO KeyRelease binding! User must click Apply button (prevents Issue #146 freeze)

        ttk.Button(filter_row7, text="Apply", command=self._apply_custom_expression, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_row7, text="Clear", command=self._on_clear_custom_filter, width=10).pack(side=tk.LEFT, padx=2)

        # Log Display
        log_frame = ttk.LabelFrame(frame, text="Aggregated Logs (Air-Side + Ground-Side)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.NONE,
                                                   font=('Courier New', 9),
                                                   bg='#FFFFFF',  # White background
                                                   fg='#000000')  # Black default text
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure color tags from config (BEFORE disabling widget)
        configure_tkinter_text_tags(self.log_text)

        # Disable editing (after configuring tags)
        self.log_text.config(state=tk.DISABLED)

        # Export/Copy Frame
        export_frame = ttk.Frame(frame)
        export_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        ttk.Button(export_frame, text="💾 Save to File...", command=self._on_save_to_file).pack(side=tk.LEFT, padx=5)

        self.export_format_var = tk.StringVar(value="json")
        ttk.Label(export_frame, text="Format:").pack(side=tk.LEFT, padx=(15, 5))
        ttk.Radiobutton(export_frame, text="JSON", variable=self.export_format_var, value="json").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(export_frame, text="CSV", variable=self.export_format_var, value="csv").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(export_frame, text="Text", variable=self.export_format_var, value="text").pack(side=tk.LEFT, padx=2)

        ttk.Separator(export_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        ttk.Button(export_frame, text="📋 Copy All", command=self._on_copy_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📋 Copy Selected", command=self._on_copy_selected).pack(side=tk.LEFT, padx=5)

        # Line count
        self.line_count_label = ttk.Label(export_frame, text="Displayed: 0 / Buffer: 0")
        self.line_count_label.pack(side=tk.RIGHT, padx=10)

        return frame

    def _create_airside_config_tab(self):
        """Create Air-Side configuration management tab (Issue #117)"""
        frame = ttk.Frame(self.notebook)

        # Top: Connection status and instructions
        header_frame = ttk.Frame(frame, padding=10)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="⚙️ Air-Side Configuration Management",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        # Info label
        info_frame = ttk.Frame(frame, padding=5)
        info_frame.pack(fill=tk.X, padx=10)
        ttk.Label(info_frame, text="Manage Air-Side configuration remotely. Changes can be applied at runtime or saved persistently.",
                 font=('Arial', 9), foreground="gray").pack(side=tk.LEFT)

        # Scrollable config area
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Store config widgets for later access
        self.config_widgets = {}

        # Network Configuration Section
        self._create_network_config_section(scrollable_frame)

        # Logging Configuration Section
        self._create_logging_config_section(scrollable_frame)

        # Health Configuration Section
        self._create_health_config_section(scrollable_frame)

        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="📥 Get Config",
                  command=self._get_airside_config, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚡ Apply Changes (Runtime)",
                  command=lambda: self._apply_airside_config(persist=False), width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Save to Default (Persistent)",
                  command=lambda: self._apply_airside_config(persist=True), width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset",
                  command=self._reset_airside_config, width=12).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.airside_config_status = ttk.Label(frame, text="Ready - Click 'Get Config' to load Air-Side configuration",
                                               relief=tk.SUNKEN, padding=5)
        self.airside_config_status.pack(fill=tk.X, padx=10, pady=2)

        return frame

    def _create_network_config_section(self, parent):
        """Network configuration section"""
        section = ttk.LabelFrame(parent, text="🌐 Network Configuration", padding=10)
        section.pack(fill=tk.X, padx=10, pady=5)

        # TCP Port
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="TCP Port:", width=30).pack(side=tk.LEFT)
        self.config_widgets['network.tcp_port'] = ttk.Spinbox(row, from_=1024, to=65535, width=10)
        self.config_widgets['network.tcp_port'].pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Command server port)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # UDP Status Port
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="UDP Status Port:", width=30).pack(side=tk.LEFT)
        self.config_widgets['network.udp_status_port'] = ttk.Spinbox(row, from_=1024, to=65535, width=10)
        self.config_widgets['network.udp_status_port'].pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Health broadcast port)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # Ground IP
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Ground-Side IP:", width=30).pack(side=tk.LEFT)
        self.config_widgets['network.ground_ip'] = ttk.Entry(row, width=20)
        self.config_widgets['network.ground_ip'].pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(H16 Android device)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

    def _create_logging_config_section(self, parent):
        """Logging configuration section"""
        section = ttk.LabelFrame(parent, text="📝 Logging Configuration", padding=10)
        section.pack(fill=tk.X, padx=10, pady=5)

        # Log Level
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Log Level:", width=30).pack(side=tk.LEFT)
        self.config_widgets['logging.level'] = ttk.Combobox(row,
                                                values=["DEBUG", "INFO", "WARNING", "ERROR"],
                                                width=15, state="readonly")
        self.config_widgets['logging.level'].pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Minimum log level)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # SystemTools Logging Enabled (CRITICAL for Issue #118 testing!)
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="SystemTools Passive Logging:", width=30).pack(side=tk.LEFT)
        self.config_widgets['logging.network_systemtools_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(row,
                       variable=self.config_widgets['logging.network_systemtools_enabled']).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Disable to test on-demand logging)", foreground="orange", font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=5)

        # Ground Logging Enabled
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Ground-Side Logging:", width=30).pack(side=tk.LEFT)
        self.config_widgets['logging.network_ground_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(row,
                       variable=self.config_widgets['logging.network_ground_enabled']).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Send logs to H16)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # File Logging Enabled
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="File Logging:", width=30).pack(side=tk.LEFT)
        self.config_widgets['logging.file_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(row,
                       variable=self.config_widgets['logging.file_enabled']).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Write logs to files)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

    def _create_health_config_section(self, parent):
        """Health monitoring configuration section"""
        section = ttk.LabelFrame(parent, text="💊 Health Monitoring Configuration", padding=10)
        section.pack(fill=tk.X, padx=10, pady=5)

        # Broadcast Enabled
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Health Broadcast:", width=30).pack(side=tk.LEFT)
        self.config_widgets['health.broadcast_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(row,
                       variable=self.config_widgets['health.broadcast_enabled']).pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(Enable health status broadcasts)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # Broadcast Interval
        row = ttk.Frame(section)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Broadcast Interval (seconds):", width=30).pack(side=tk.LEFT)
        self.config_widgets['health.broadcast_interval_sec'] = ttk.Spinbox(row, from_=1, to=60, width=10)
        self.config_widgets['health.broadcast_interval_sec'].pack(side=tk.LEFT, padx=5)
        ttk.Label(row, text="(How often to send health)", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

    def _create_docker_logs_tab(self):
        """Create Docker Logs tab for Air-Side payload-manager logs"""
        frame = ttk.Frame(self.notebook)

        # SSH Connection controls
        connection_frame = ttk.LabelFrame(frame, text="SSH Connection", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        # Connection status
        status_row = ttk.Frame(connection_frame)
        status_row.pack(fill=tk.X, pady=5)

        ttk.Label(status_row, text="Status:").pack(side=tk.LEFT, padx=5)
        self.docker_ssh_indicator = tk.Canvas(status_row, width=20, height=20, highlightthickness=0)
        self.docker_ssh_indicator.pack(side=tk.LEFT, padx=5)
        self._update_docker_ssh_indicator(False)

        self.docker_ssh_status_label = ttk.Label(status_row, text="Disconnected", font=('Arial', 9, 'bold'))
        self.docker_ssh_status_label.pack(side=tk.LEFT, padx=5)

        # Docker Image ID display
        ttk.Separator(status_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)
        ttk.Label(status_row, text="Image ID:").pack(side=tk.LEFT, padx=5)
        self.docker_image_id_label = ttk.Label(status_row, text="N/A", font=('Arial', 9))
        self.docker_image_id_label.pack(side=tk.LEFT, padx=5)

        # Connect/Disconnect buttons
        button_row = ttk.Frame(connection_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.docker_connect_btn = ttk.Button(button_row, text="Connect SSH", command=self._docker_connect_ssh)
        self.docker_connect_btn.pack(side=tk.LEFT, padx=5)

        self.docker_disconnect_btn = ttk.Button(button_row, text="Disconnect", command=self._docker_disconnect_ssh, state=tk.DISABLED)
        self.docker_disconnect_btn.pack(side=tk.LEFT, padx=5)

        # SSH info label
        ttk.Label(button_row, text=f"Air-Side: dpm@10.0.1.53:22",
                 font=('Arial', 9, 'italic')).pack(side=tk.LEFT, padx=20)

        # Log View Controls
        controls_frame = ttk.LabelFrame(frame, text="Log View Options", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # View mode selection
        mode_row = ttk.Frame(controls_frame)
        mode_row.pack(fill=tk.X, pady=5)

        ttk.Label(mode_row, text="View Mode:").pack(side=tk.LEFT, padx=5)

        self.docker_view_mode_var = tk.StringVar(value="tail")
        ttk.Radiobutton(mode_row, text="Last 100 lines", variable=self.docker_view_mode_var,
                       value="tail", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_row, text="Last 500 lines", variable=self.docker_view_mode_var,
                       value="tail_500", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_row, text="All logs", variable=self.docker_view_mode_var,
                       value="all", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)

        # Time filter
        time_row = ttk.Frame(controls_frame)
        time_row.pack(fill=tk.X, pady=5)

        ttk.Label(time_row, text="Time Filter:").pack(side=tk.LEFT, padx=5)

        self.docker_time_filter_var = tk.StringVar(value="none")
        ttk.Radiobutton(time_row, text="None", variable=self.docker_time_filter_var,
                       value="none", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 5 min", variable=self.docker_time_filter_var,
                       value="5m", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 30 min", variable=self.docker_time_filter_var,
                       value="30m", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 1 hour", variable=self.docker_time_filter_var,
                       value="1h", command=self._docker_on_view_mode_changed).pack(side=tk.LEFT, padx=5)

        # Refresh controls
        refresh_row = ttk.Frame(controls_frame)
        refresh_row.pack(fill=tk.X, pady=5)

        ttk.Button(refresh_row, text="Refresh Now", command=self._docker_refresh_logs).pack(side=tk.LEFT, padx=5)

        # Follow logs toggle (real-time streaming)
        self.docker_follow_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(refresh_row, text="Follow Logs (live)",
                       variable=self.docker_follow_var,
                       command=self._docker_toggle_follow).pack(side=tk.LEFT, padx=5)

        ttk.Separator(refresh_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Auto-refresh
        self.docker_auto_refresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(refresh_row, text="Auto-refresh",
                       variable=self.docker_auto_refresh_var,
                       command=self._docker_toggle_auto_refresh).pack(side=tk.LEFT, padx=5)

        ttk.Label(refresh_row, text="Interval (sec):").pack(side=tk.LEFT, padx=(20, 5))
        self.docker_interval_var = tk.IntVar(value=5)
        ttk.Spinbox(refresh_row, from_=1, to=60, textvariable=self.docker_interval_var,
                   width=5, command=self._docker_update_refresh_interval).pack(side=tk.LEFT, padx=5)

        # Last update time
        ttk.Label(refresh_row, text="Last Updated:").pack(side=tk.RIGHT, padx=5)
        self.docker_last_update_label = ttk.Label(refresh_row, text="Never", font=('Arial', 9, 'italic'))
        self.docker_last_update_label.pack(side=tk.RIGHT, padx=5)

        # Search bar
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.docker_search_var = tk.StringVar()
        docker_search_entry = ttk.Entry(search_frame, textvariable=self.docker_search_var, width=40)
        docker_search_entry.pack(side=tk.LEFT, padx=5)
        docker_search_entry.bind("<KeyRelease>", self._docker_on_search_changed)

        ttk.Button(search_frame, text="Clear", command=self._docker_clear_search).pack(side=tk.LEFT, padx=5)

        # Pre-defined Filters
        predefined_filter_frame = ttk.LabelFrame(controls_frame, text="Quick Filters", padding=5)
        predefined_filter_frame.pack(fill=tk.X, pady=5)

        # Row 1: Level filters
        filter_row1 = ttk.Frame(predefined_filter_frame)
        filter_row1.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row1, text="Level:", width=10).pack(side=tk.LEFT, padx=5)
        self.docker_filter_errors = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row1, text="Errors", variable=self.docker_filter_errors,
                       command=self._docker_apply_filters).pack(side=tk.LEFT, padx=3)
        self.docker_filter_warnings = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row1, text="Warnings", variable=self.docker_filter_warnings,
                       command=self._docker_apply_filters).pack(side=tk.LEFT, padx=3)

        # Row 2: Context filters - dynamically generated from protocol
        filter_row2 = ttk.Frame(predefined_filter_frame)
        filter_row2.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row2, text="Context:", width=10).pack(side=tk.LEFT, padx=5)

        # Create BooleanVar and Checkbutton for each context from protocol
        self.docker_context_filters = {}
        for context_id in LogContexts.get_context_ids():
            var = tk.BooleanVar(value=False)
            self.docker_context_filters[context_id] = var
            ttk.Checkbutton(filter_row2, text=context_id.capitalize(), variable=var,
                           command=self._docker_apply_filters).pack(side=tk.LEFT, padx=3)

        # Row 3: Special filters
        filter_row3 = ttk.Frame(predefined_filter_frame)
        filter_row3.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row3, text="Special:", width=10).pack(side=tk.LEFT, padx=5)
        self.docker_filter_hide_verbose = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row3, text="Hide Verbose", variable=self.docker_filter_hide_verbose,
                       command=self._docker_apply_filters).pack(side=tk.LEFT, padx=3)
        ttk.Label(filter_row3, text="(hides updateCachedProperties)", font=('Arial', 8, 'italic'),
                 foreground='gray').pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_row3, text="Clear All Filters", command=self._docker_clear_all_filters).pack(side=tk.RIGHT, padx=5)

        # User-Definable Filter with AND/OR logic
        custom_filter_frame = ttk.LabelFrame(controls_frame, text="Custom Filter (Boolean Logic)", padding=5)
        custom_filter_frame.pack(fill=tk.X, pady=5)

        filter_help_row = ttk.Frame(custom_filter_frame)
        filter_help_row.pack(fill=tk.X, pady=2)
        ttk.Label(filter_help_row, text="Syntax: Use AND, OR, NOT. Example: (camera AND connect) OR (network AND timeout)",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        custom_filter_input_row = ttk.Frame(custom_filter_frame)
        custom_filter_input_row.pack(fill=tk.X, pady=2)

        ttk.Label(custom_filter_input_row, text="Expression:").pack(side=tk.LEFT, padx=5)
        self.docker_custom_filter_var = tk.StringVar()
        docker_custom_entry = ttk.Entry(custom_filter_input_row, textvariable=self.docker_custom_filter_var, width=60)
        docker_custom_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        docker_custom_entry.bind("<KeyRelease>", lambda e: self._docker_apply_filters())

        ttk.Button(custom_filter_input_row, text="Apply", command=self._docker_apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_filter_input_row, text="Clear", command=self._docker_clear_custom_filter).pack(side=tk.LEFT, padx=5)

        # Bottom controls
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        ttk.Button(bottom_frame, text="Clear Display", command=self._docker_clear_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Save to File...", command=self._docker_save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Copy All", command=self._docker_copy_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="🗗 Pop Out", command=self._docker_pop_out_logs).pack(side=tk.LEFT, padx=5)

        # Line count label
        self.docker_line_count_label = ttk.Label(bottom_frame, text="Lines: 0")
        self.docker_line_count_label.pack(side=tk.RIGHT, padx=10)

        # Log display
        log_frame = ttk.LabelFrame(frame, text="Docker Logs (payload-manager)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.docker_log_text = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 9))
        self.docker_log_text.config(state=tk.DISABLED)  # Read-only

        # Scrollbars
        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.docker_log_text.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.docker_log_text.xview)
        self.docker_log_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.docker_log_text.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Configure text tags for highlighting
        self.docker_log_text.tag_config("highlight", background="yellow")
        self.docker_log_text.tag_config("error", foreground="red")
        self.docker_log_text.tag_config("warning", foreground="orange")
        self.docker_log_text.tag_config("info", foreground="blue")

        # Initialize state variables
        self.docker_current_logs = ""
        self.docker_auto_refresh_enabled = False
        self.docker_refresh_interval = 5000  # ms
        self.docker_follow_enabled = False
        self.docker_follow_thread = None
        self.docker_follow_stop_event = None

        return frame

    # ========== Connection Management (Helper Methods) ==========

    def _tcp_connect(self):
        """TCP Connect button handler - connects to Air-Side with default settings"""
        self.connect_to_airside(host="10.0.1.53", port=5000, timeout_ms=5000)

    def connect_to_airside(self, host: str = "10.0.1.53", port: int = 5000, timeout_ms: int = 5000):
        """Connect to Air-Side TCP server

        Args:
            host: Air-Side IP address (default: 10.0.1.53)
            port: TCP port (default: 5000)
            timeout_ms: Connection timeout in milliseconds (default: 5000)

        Returns:
            bool: True if connected successfully
        """
        try:
            # Create TCPClient if not exists
            if self.tcp_client:
                # Disconnect existing connection
                self.tcp_client.disconnect()

            self.tcp_client = TCPClient(host, port, timeout_ms)

            # Connect
            if self.tcp_client.connect():
                self.airside_connection_status.config(text=f"Connected to {host}:{port}", foreground="green")
                logger.info(f"Connected to Air-Side at {host}:{port}")
                return True
            else:
                self.airside_connection_status.config(text="Connection Failed", foreground="red")
                logger.error(f"Failed to connect to Air-Side at {host}:{port}")
                return False

        except Exception as e:
            self.airside_connection_status.config(text="Connection Error", foreground="red")
            logger.error(f"Error connecting to Air-Side: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to Air-Side:\n{e}")
            return False

    def disconnect_from_airside(self):
        """Disconnect from Air-Side"""
        if self.tcp_client:
            self.tcp_client.disconnect()
            self.tcp_client = None
            self.airside_connection_status.config(text="Not Connected", foreground="red")
            logger.info("Disconnected from Air-Side")

    def _get_local_ip(self) -> str:
        """Get local IP address on the 10.0.1.x subnet

        Returns:
            str: Local IP address (e.g., "10.0.1.83"), or "10.0.1.83" as fallback
        """
        try:
            # Create a socket connection to Air-Side to determine which interface to use
            # This doesn't actually send data, just determines routing
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.0.1.53", 80))  # Air-Side IP
            local_ip = s.getsockname()[0]
            s.close()
            logger.debug(f"Detected local IP: {local_ip}")
            return local_ip
        except Exception as e:
            logger.warning(f"Failed to auto-detect local IP: {e}, using fallback 10.0.1.83")
            return "10.0.1.83"  # Fallback to known SystemTools IP

    # ========== Air-Side Config Management Methods (Issue #117) ==========

    def _get_airside_config(self):
        """Fetch configuration from Air-Side via system.get_config command"""
        # Auto-connect if not connected
        if not self.tcp_client or not self.tcp_client.is_connected():
            logger.info("Not connected - attempting auto-connect to Air-Side...")
            success = self.connect_to_airside(host="10.0.1.53", port=5000, timeout_ms=5000)
            if not success:
                messagebox.showerror("Connection Failed",
                                   "Could not connect to Air-Side.\n\n" +
                                   "Please ensure Air-Side is running at 10.0.1.53:5000")
                return

        self.airside_config_status.config(text="Fetching config from Air-Side...")

        def fetch_config():
            try:
                # Use existing TCPClient backend (no changes needed!)
                message = protocol_msg.create_command("system.get_config", {})
                success = self.tcp_client.send_message(message)

                if not success:
                    raise Exception("Failed to send command")

                # Wait for response
                response = self.tcp_client.wait_for_response(timeout=5.0)

                # Check response format
                if not response:
                    raise Exception('No response from Air-Side (timeout)')

                # Debug: Log full response structure
                logger.debug(f"Received response: {response}")

                msg_type = response.get('message_type')
                if msg_type == 'response':
                    payload = response.get('payload', {})
                    logger.debug(f"Response payload: {payload}")

                    if payload.get('command') == 'system.get_config':
                        result = payload.get('result', {})
                        logger.debug(f"Result from response: {result}")

                        config_data = result.get('config', {})
                        logger.info(f"Extracted config_data with {len(config_data)} sections: {list(config_data.keys())}")

                        if not config_data:
                            logger.warning("Config data is empty! Full result structure:")
                            logger.warning(f"  result keys: {list(result.keys())}")
                            logger.warning(f"  result content: {result}")

                        # Update UI with config data
                        self.after(0, lambda: self._populate_config_ui(config_data))
                        self.after(0, lambda: self.airside_config_status.config(
                            text=f"✅ Config loaded at {datetime.now().strftime('%H:%M:%S')}"))
                    else:
                        raise Exception(f"Unexpected command in response: {payload.get('command')}")
                elif msg_type == 'error':
                    error_msg = response.get('payload', {}).get('error_message', 'Unknown error')
                    raise Exception(error_msg)
                else:
                    raise Exception(f"Unexpected message type: {msg_type}")

            except Exception as e:
                logger.error(f"Failed to get config: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to get config:\n{e}"))
                self.after(0, lambda: self.airside_config_status.config(text="❌ Error fetching config"))

        threading.Thread(target=fetch_config, daemon=True).start()

    def _populate_config_ui(self, config_data):
        """Populate UI widgets with config data"""
        # Network section
        if 'network' in config_data:
            net = config_data['network']
            if 'tcp_port' in net:
                self.config_widgets['network.tcp_port'].set(net['tcp_port'])
            if 'udp_status_port' in net:
                self.config_widgets['network.udp_status_port'].set(net['udp_status_port'])
            if 'ground_ip' in net:
                self.config_widgets['network.ground_ip'].delete(0, tk.END)
                self.config_widgets['network.ground_ip'].insert(0, net['ground_ip'])

        # Logging section
        if 'logging' in config_data:
            log = config_data['logging']
            if 'level' in log:
                level_value = log['level']
                logger.debug(f"Setting logging.level combobox to: '{level_value}' (type: {type(level_value)})")
                logger.debug(f"Combobox values: {self.config_widgets['logging.level']['values']}")
                logger.debug(f"Combobox state: {self.config_widgets['logging.level']['state']}")
                self.config_widgets['logging.level'].set(level_value)
                logger.debug(f"After .set(), combobox get() returns: '{self.config_widgets['logging.level'].get()}'")
            if 'network_systemtools_enabled' in log:
                self.config_widgets['logging.network_systemtools_enabled'].set(
                    log['network_systemtools_enabled'])
            if 'network_ground_enabled' in log:
                self.config_widgets['logging.network_ground_enabled'].set(
                    log['network_ground_enabled'])
            if 'file_enabled' in log:
                self.config_widgets['logging.file_enabled'].set(log['file_enabled'])

        # Health section
        if 'health' in config_data:
            health = config_data['health']
            if 'broadcast_enabled' in health:
                self.config_widgets['health.broadcast_enabled'].set(health['broadcast_enabled'])
            if 'broadcast_interval_sec' in health:
                self.config_widgets['health.broadcast_interval_sec'].set(health['broadcast_interval_sec'])

        # Store original config for change detection
        self.original_config = config_data
        logger.info(f"Config UI populated with {len(config_data)} sections")

    def _apply_airside_config(self, persist=False):
        """Apply config changes to Air-Side"""
        if not self.tcp_client or not self.tcp_client.is_connected():
            messagebox.showerror("Not Connected", "Please connect to Air-Side first.")
            return

        # Collect changes from UI
        updates = self._collect_config_changes()

        if not updates:
            messagebox.showinfo("No Changes", "No configuration changes to apply")
            return

        # Confirm if persisting
        if persist:
            changes_summary = "\n".join([f"  - {section}.{key}: {value}"
                                        for section, items in updates.items()
                                        for key, value in items.items()])
            result = messagebox.askyesno("Confirm Persist",
                                         "Save changes to local.json?\n" +
                                         "This will persist across Air-Side restarts.\n\n" +
                                         "Changed values:\n" + changes_summary)
            if not result:
                return

        action_text = "Saving to default..." if persist else "Applying changes..."
        self.airside_config_status.config(text=action_text)

        def apply_config():
            try:
                # Use existing TCPClient backend
                message = protocol_msg.create_command("system.update_config", {
                    "updates": updates,
                    "persist": persist
                })
                success = self.tcp_client.send_message(message)

                if not success:
                    raise Exception("Failed to send command")

                # Wait for response
                response = self.tcp_client.wait_for_response(timeout=5.0)

                # Check response
                if not response:
                    raise Exception('No response from Air-Side (timeout)')

                msg_type = response.get('message_type')
                if msg_type == 'response':
                    payload = response.get('payload', {})
                    if payload.get('command') == 'system.update_config':
                        result = payload.get('result', {})
                        msg = "✅ Config updated successfully"
                        if result.get('persisted'):
                            msg += " and saved to local.json"
                        if result.get('restart_required'):
                            msg += "\n\n⚠️ NOTE: Some changes require Air-Side restart"

                        self.after(0, lambda: messagebox.showinfo("Success", msg))
                        self.after(0, lambda: self.airside_config_status.config(
                            text=f"✅ Config applied at {datetime.now().strftime('%H:%M:%S')}"))

                        # Refresh config to get latest state
                        self.after(1000, self._get_airside_config)
                    else:
                        raise Exception(f"Unexpected command in response: {payload.get('command')}")
                elif msg_type == 'error':
                    error_msg = response.get('payload', {}).get('error_message', 'Unknown error')
                    raise Exception(error_msg)
                else:
                    raise Exception(f"Unexpected message type: {msg_type}")

            except Exception as e:
                logger.error(f"Failed to apply config: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to apply config:\n{e}"))
                self.after(0, lambda: self.airside_config_status.config(text="❌ Error applying config"))

        threading.Thread(target=apply_config, daemon=True).start()

    def _collect_config_changes(self):
        """Collect changed values from UI - returns flat dotted-key format per protocol/commands.json line 376"""
        if not self.original_config:
            # No original config to compare against, collect all values
            messagebox.showwarning("No Baseline", "Please click 'Get Config' first to establish a baseline")
            return {}

        updates = {}

        # Network changes - use flat dotted keys
        if 'network' in self.original_config:
            net_orig = self.original_config['network']

            tcp_port = int(self.config_widgets['network.tcp_port'].get())
            if tcp_port != net_orig.get('tcp_port'):
                updates['network.tcp_port'] = tcp_port

            udp_port = int(self.config_widgets['network.udp_status_port'].get())
            if udp_port != net_orig.get('udp_status_port'):
                updates['network.udp_status_port'] = udp_port

            ground_ip = self.config_widgets['network.ground_ip'].get()
            if ground_ip != net_orig.get('ground_ip'):
                updates['network.ground_ip'] = ground_ip

        # Logging changes - use flat dotted keys
        if 'logging' in self.original_config:
            log_orig = self.original_config['logging']

            level = self.config_widgets['logging.level'].get()
            if level and level != log_orig.get('level'):
                updates['logging.level'] = level

            systemtools_enabled = self.config_widgets['logging.network_systemtools_enabled'].get()
            if systemtools_enabled != log_orig.get('network_systemtools_enabled'):
                updates['logging.network_systemtools_enabled'] = systemtools_enabled

            ground_enabled = self.config_widgets['logging.network_ground_enabled'].get()
            if ground_enabled != log_orig.get('network_ground_enabled'):
                updates['logging.network_ground_enabled'] = ground_enabled

            file_enabled = self.config_widgets['logging.file_enabled'].get()
            if file_enabled != log_orig.get('file_enabled'):
                updates['logging.file_enabled'] = file_enabled

        # Health changes - use flat dotted keys
        if 'health' in self.original_config:
            health_orig = self.original_config['health']

            broadcast_enabled = self.config_widgets['health.broadcast_enabled'].get()
            if broadcast_enabled != health_orig.get('broadcast_enabled'):
                updates['health.broadcast_enabled'] = broadcast_enabled

            interval = int(self.config_widgets['health.broadcast_interval_sec'].get())
            if interval != health_orig.get('broadcast_interval_sec'):
                updates['health.broadcast_interval_sec'] = interval

        return updates

    def _reset_airside_config(self):
        """Reset config UI to last fetched values"""
        if not self.original_config:
            messagebox.showinfo("Nothing to Reset", "Please click 'Get Config' first")
            return

        # Re-populate UI with original config
        self._populate_config_ui(self.original_config)
        self.airside_config_status.config(text="🔄 Reset to last fetched config")
        logger.info("Config UI reset to original values")

    # ========== Docker Logs Tab Methods ==========

    def _update_docker_ssh_indicator(self, connected: bool):
        """Update Docker SSH connection indicator"""
        self.docker_ssh_indicator.delete("all")
        color = "green" if connected else "gray"
        self.docker_ssh_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _docker_connect_ssh(self):
        """Connect to Air-Side SSH for Docker logs"""
        logger.info("Connecting SSH to Air-Side for Docker logs...")

        # Check if already connected
        if self.ssh_client and self.ssh_client.is_connected():
            logger.info("SSH already connected - reusing existing connection")
            self._docker_on_ssh_connected()
            return

        # Create SSH client
        self.ssh_client = SSHClient(
            host="10.0.1.53",
            username="dpm",
            password="2350",
            port=22
        )

        # Set callbacks
        self.ssh_client.on_connected = self._docker_on_ssh_connected
        self.ssh_client.on_disconnected = self._docker_on_ssh_disconnected
        self.ssh_client.on_error = self._docker_on_ssh_error

        # Connect in background thread
        self.docker_connect_btn.config(state=tk.DISABLED, text="Connecting...")
        self.ssh_client.connect_async()

    def _docker_disconnect_ssh(self):
        """Disconnect from Air-Side SSH"""
        if self.ssh_client:
            self.ssh_client.disconnect()

    def _docker_on_ssh_connected(self):
        """Callback when SSH connected"""
        self.after(0, self._docker_update_ssh_connected_ui)

    def _docker_update_ssh_connected_ui(self):
        """Update UI after SSH connection"""
        self._update_docker_ssh_indicator(True)
        self.docker_ssh_status_label.config(text="Connected", foreground="green")
        self.docker_connect_btn.config(state=tk.DISABLED, text="Connect SSH")
        self.docker_disconnect_btn.config(state=tk.NORMAL)

        # Update Remote Control tab SSH status
        if hasattr(self, 'remote_control_tab'):
            self.remote_control_tab.update_ssh_status(True)

        # Fetch Docker Image ID
        self._docker_fetch_image_id()

        logger.info("SSH connected - fetching initial Docker logs")
        self._docker_refresh_logs()

    def _docker_on_ssh_disconnected(self):
        """Callback when SSH disconnected"""
        self.after(0, self._docker_update_ssh_disconnected_ui)

    def _docker_update_ssh_disconnected_ui(self):
        """Update UI after SSH disconnection"""
        self._update_docker_ssh_indicator(False)
        self.docker_ssh_status_label.config(text="Disconnected", foreground="gray")
        self.docker_connect_btn.config(state=tk.NORMAL, text="Connect SSH")
        self.docker_disconnect_btn.config(state=tk.DISABLED)

        # Update Remote Control tab SSH status
        if hasattr(self, 'remote_control_tab'):
            self.remote_control_tab.update_ssh_status(False)

        # Stop auto-refresh
        self.docker_auto_refresh_var.set(False)
        self.docker_auto_refresh_enabled = False

    def _docker_on_ssh_error(self, error_msg: str):
        """Callback when SSH error occurs"""
        self.after(0, lambda: self._docker_show_ssh_error(error_msg))

    def _docker_show_ssh_error(self, error_msg: str):
        """Show SSH error message"""
        messagebox.showerror("SSH Error", error_msg)
        self._docker_update_ssh_disconnected_ui()

    def _docker_on_view_mode_changed(self, event=None):
        """Handle view mode change"""
        if self.ssh_client and self.ssh_client.is_connected():
            self._docker_refresh_logs()

    def _docker_refresh_logs(self):
        """Refresh logs from Air-Side Docker"""
        if not self.ssh_client or not self.ssh_client.is_connected():
            messagebox.showwarning("Not Connected", "Please connect SSH first")
            return

        # Determine parameters based on view mode
        tail = None
        since = None

        view_mode = self.docker_view_mode_var.get()
        if view_mode == "tail":
            tail = 100
        elif view_mode == "tail_500":
            tail = 500

        time_filter = self.docker_time_filter_var.get()
        if time_filter != "none":
            since = time_filter

        # Fetch logs in background thread
        def fetch_logs():
            exit_code, stdout, stderr = self.ssh_client.get_docker_logs(
                container="payload-manager",
                tail=tail,
                since=since
            )

            if exit_code == 0:
                # Combine stdout and stderr (Docker logs outputs to both)
                combined_logs = stdout + stderr

                # Update UI on main thread
                self.after(0, lambda: self._docker_update_log_display(combined_logs))
            else:
                error_msg = stderr if stderr else "Failed to fetch logs"
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch logs:\n{error_msg}"))

        threading.Thread(target=fetch_logs, daemon=True).start()

    def _docker_parse_and_format_log_line(self, line: str) -> str:
        """Parse JSON log line and format with timestamp column

        Args:
            line: Raw log line (possibly JSON)

        Returns:
            Formatted string with timestamp column
        """
        try:
            # Try to parse as JSON
            log_data = json.loads(line)

            # Extract fields
            timestamp_str = log_data.get('timestamp', '')
            level = log_data.get('level', 'INFO')
            message = log_data.get('message', line)

            # Format timestamp
            if timestamp_str:
                try:
                    # Parse ISO format: 2025-11-16T21:46:58.621Z
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    # Format as HH:MM:SS
                    time_str = dt.strftime('%H:%M:%S')
                except Exception:
                    # Fallback to first 8 chars of timestamp
                    time_str = timestamp_str[11:19] if len(timestamp_str) > 19 else '??:??:??'
            else:
                time_str = '??:??:??'

            # Format with columns: "HH:MM:SS | [LEVEL] message"
            formatted = f"{time_str} | [{level:7s}] {message}"
            return formatted

        except json.JSONDecodeError:
            # Not JSON - return as-is
            return line
        except Exception as e:
            # Parse error - return original line
            logger.debug(f"Error parsing Docker log line: {e}")
            return line

    def _docker_update_log_display(self, logs: str):
        """Update log text display"""
        self.docker_current_logs = logs

        # Parse and format logs (JSON → timestamp | level message)
        formatted_lines = []
        for line in logs.splitlines():
            if line.strip():
                formatted_line = self._docker_parse_and_format_log_line(line)
                formatted_lines.append(formatted_line)

        formatted_logs = '\n'.join(formatted_lines)

        # Apply all filters (pre-defined + custom + search)
        display_logs = self._docker_apply_all_filters(formatted_logs)

        # Update text widget
        self.docker_log_text.config(state=tk.NORMAL)
        self.docker_log_text.delete(1.0, tk.END)
        self.docker_log_text.insert(1.0, display_logs)

        # Apply syntax highlighting
        self._docker_apply_highlighting()

        self.docker_log_text.config(state=tk.DISABLED)

        # Scroll to bottom
        self.docker_log_text.see(tk.END)

        # Update statistics
        line_count = len(display_logs.splitlines())
        self.docker_line_count_label.config(text=f"Lines: {line_count}")
        self.docker_last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _docker_filter_logs(self, logs: str, search_text: str) -> str:
        """Filter logs by search text"""
        filtered_lines = []
        for line in logs.splitlines():
            if search_text in line.lower():
                filtered_lines.append(line)
        return "\n".join(filtered_lines)

    def _docker_evaluate_custom_filter(self, line: str, expression: str) -> bool:
        """Evaluate custom filter expression with AND/OR/NOT logic

        Args:
            line: Formatted log line (lowercase for case-insensitive matching)
            expression: Boolean expression (e.g., "(camera AND connect) OR (network AND timeout)")

        Returns:
            True if line matches expression, False otherwise
        """
        try:
            # Convert expression to lowercase for case-insensitive matching
            expr = expression.lower()
            line_lower = line.lower()

            # Replace AND, OR, NOT with Python operators
            # Use word boundaries to avoid replacing parts of words
            import re
            expr = re.sub(r'\bAND\b', ' and ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bOR\b', ' or ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bNOT\b', ' not ', expr, flags=re.IGNORECASE)

            # Find all word tokens (not operators or parentheses)
            tokens = re.findall(r'\b(?!and\b|or\b|not\b)\w+\b', expr)

            # Build a safe evaluation context
            # Replace each token with: "'token' in line_lower"
            eval_expr = expr
            for token in set(tokens):
                # Escape the token for regex safety
                token_pattern = r'\b' + re.escape(token) + r'\b'
                replacement = f"('{token}' in line_lower)"
                eval_expr = re.sub(token_pattern, replacement, eval_expr)

            # Evaluate the expression safely
            result = eval(eval_expr, {"__builtins__": {}}, {"line_lower": line_lower})
            return bool(result)

        except Exception as e:
            # Parse error - don't filter
            logger.debug(f"Custom filter parse error: {e}")
            return True  # Show line if filter expression is invalid

    def _docker_apply_all_filters(self, logs: str) -> str:
        """Apply all filters: pre-defined + custom + search

        Args:
            logs: Formatted log lines

        Returns:
            Filtered log lines
        """
        filtered_lines = []

        for line in logs.splitlines():
            # Parse JSON from original line to get context/level (for pre-defined filters)
            # Extract from formatted line: "HH:MM:SS | [LEVEL] message"
            # The original line is in self.docker_current_logs
            line_lower = line.lower()

            # 1. Pre-defined filters (Level)
            filter_errors = self.docker_filter_errors.get()
            filter_warnings = self.docker_filter_warnings.get()

            level_match = False
            if filter_errors or filter_warnings:
                # At least one level filter is active
                if filter_errors and '[error' in line_lower:
                    level_match = True
                if filter_warnings and '[warning' in line_lower:
                    level_match = True

                if not level_match:
                    continue  # Skip this line

            # 2. Pre-defined filters (Context) - dynamically check all protocol contexts
            # Check if any context filter is active
            any_context_active = any(var.get() for var in self.docker_context_filters.values())

            if any_context_active:
                # At least one context filter is active
                # Try to extract context from JSON, or infer from content
                context_match = False

                # Try JSON parsing first
                try:
                    json_start = line.find('{')
                    if json_start != -1:
                        json_data = json.loads(line[json_start:])
                        log_context = json_data.get('context', '').upper()
                        if log_context and self.docker_context_filters.get(log_context, tk.BooleanVar()).get():
                            context_match = True
                except:
                    pass

                # If no JSON context, infer from content keywords
                if not context_match:
                    for context_id, var in self.docker_context_filters.items():
                        if var.get():
                            # Simple keyword matching for each context
                            context_lower = context_id.lower()
                            if context_lower in line_lower:
                                context_match = True
                                break

                if not context_match:
                    continue  # Skip this line

            # 3. Special filter: Hide verbose
            if self.docker_filter_hide_verbose.get():
                if 'updatecachedproperties' in line_lower:
                    continue  # Skip verbose messages

            # 4. Custom filter (Boolean logic)
            custom_expr = self.docker_custom_filter_var.get().strip()
            if custom_expr:
                if not self._docker_evaluate_custom_filter(line, custom_expr):
                    continue  # Skip this line

            # 5. Search text filter
            search_text = self.docker_search_var.get().strip().lower()
            if search_text:
                if search_text not in line_lower:
                    continue  # Skip this line

            # Line passed all filters - include it
            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _docker_apply_filters(self):
        """Re-apply all filters to current logs"""
        if self.docker_current_logs:
            self._docker_update_log_display(self.docker_current_logs)

    def _docker_clear_all_filters(self):
        """Clear all pre-defined filters"""
        self.docker_filter_errors.set(False)
        self.docker_filter_warnings.set(False)
        # Clear all dynamic context filters
        for var in self.docker_context_filters.values():
            var.set(False)
        self.docker_filter_hide_verbose.set(False)
        self._docker_apply_filters()

    def _docker_clear_custom_filter(self):
        """Clear custom filter"""
        self.docker_custom_filter_var.set("")
        self._docker_apply_filters()

    def _docker_apply_highlighting(self):
        """Apply syntax highlighting to log text"""
        content = self.docker_log_text.get(1.0, tk.END)
        lines = content.splitlines()

        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Highlight errors
            if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower:
                self.docker_log_text.tag_add("error", f"{i}.0", f"{i}.end")

            # Highlight warnings
            elif "warning" in line_lower or "warn" in line_lower:
                self.docker_log_text.tag_add("warning", f"{i}.0", f"{i}.end")

            # Highlight info
            elif "info" in line_lower:
                self.docker_log_text.tag_add("info", f"{i}.0", f"{i}.end")

        # Highlight search matches
        search_text = self.docker_search_var.get()
        if search_text:
            start_idx = "1.0"
            while True:
                start_idx = self.docker_log_text.search(search_text, start_idx, nocase=True, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(search_text)}c"
                self.docker_log_text.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

    def _docker_on_search_changed(self, event=None):
        """Handle search text change"""
        if self.docker_current_logs:
            self._docker_update_log_display(self.docker_current_logs)

    def _docker_clear_search(self):
        """Clear search filter"""
        self.docker_search_var.set("")
        if self.docker_current_logs:
            self._docker_update_log_display(self.docker_current_logs)

    def _docker_toggle_follow(self):
        """Toggle follow logs (live streaming) on/off"""
        self.docker_follow_enabled = self.docker_follow_var.get()

        if self.docker_follow_enabled:
            if not self.ssh_client or not self.ssh_client.is_connected():
                messagebox.showwarning("Not Connected", "Please connect SSH first")
                self.docker_follow_var.set(False)
                self.docker_follow_enabled = False
                return

            # Disable auto-refresh when following
            if self.docker_auto_refresh_enabled:
                self.docker_auto_refresh_var.set(False)
                self.docker_auto_refresh_enabled = False

            logger.info("Starting to follow Docker logs in real-time...")
            self._docker_start_follow()

        else:
            logger.info("Stopping Docker log follow...")
            self._docker_stop_follow()

    def _docker_start_follow(self):
        """Start following logs in background thread"""
        # Clear current logs
        self.docker_log_text.config(state=tk.NORMAL)
        self.docker_log_text.delete(1.0, tk.END)
        self.docker_log_text.config(state=tk.DISABLED)

        # Create stop event
        self.docker_follow_stop_event = threading.Event()

        # Get tail parameter from view mode
        tail = None
        view_mode = self.docker_view_mode_var.get()
        if view_mode == "tail":
            tail = 100
        elif view_mode == "tail_500":
            tail = 500

        # Start follow thread
        def follow_worker():
            self.ssh_client.follow_docker_logs(
                container="payload-manager",
                tail=tail,
                on_log_line=self._docker_on_log_line_received,
                stop_event=self.docker_follow_stop_event
            )

        self.docker_follow_thread = threading.Thread(target=follow_worker, daemon=True)
        self.docker_follow_thread.start()

        # Update UI
        self.docker_last_update_label.config(text="Following...")

    def _docker_stop_follow(self):
        """Stop following logs"""
        if self.docker_follow_stop_event:
            self.docker_follow_stop_event.set()

        if self.docker_follow_thread and self.docker_follow_thread.is_alive():
            self.docker_follow_thread.join(timeout=2.0)

        self.docker_follow_thread = None
        self.docker_follow_stop_event = None

        # Update UI
        self.docker_last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _docker_on_log_line_received(self, line: str):
        """Callback for each new log line (called from follow thread)"""
        self.after(0, lambda: self._docker_append_log_line(line))

    def _docker_should_display_line(self, formatted_line: str) -> bool:
        """Check if a formatted log line should be displayed based on all active filters

        Args:
            formatted_line: Formatted log line (HH:MM:SS | [LEVEL] message)

        Returns:
            True if line should be displayed, False if filtered out
        """
        try:
            line_lower = formatted_line.lower()

            # 1. Pre-defined filters (Level)
            filter_errors = self.docker_filter_errors.get()
            filter_warnings = self.docker_filter_warnings.get()

            if filter_errors or filter_warnings:
                # At least one level filter is active
                level_match = False
                if filter_errors and '[error' in line_lower:
                    level_match = True
                if filter_warnings and '[warning' in line_lower:
                    level_match = True
                if not level_match:
                    return False  # Doesn't match any selected level

            # 2. Pre-defined filters (Context)
            filter_camera = self.docker_filter_camera.get()
            filter_network = self.docker_filter_network.get()
            filter_system = self.docker_filter_system.get()

            if filter_camera or filter_network or filter_system:
                # At least one context filter is active
                context_match = False
                if filter_camera and 'camera' in line_lower:
                    context_match = True
                if filter_network and ('network' in line_lower or 'heartbeat' in line_lower):
                    context_match = True
                if filter_system and ('system' in line_lower or 'cpu' in line_lower):
                    context_match = True
                if not context_match:
                    return False  # Doesn't match any selected context

            # 3. Special filters (Hide Verbose)
            filter_hide_verbose = self.docker_filter_hide_verbose.get()
            if filter_hide_verbose:
                if 'updatecachedproperties' in line_lower:
                    return False  # Hide verbose spam

            # 4. Custom filter (Boolean logic)
            custom_expr = self.docker_custom_filter_var.get().strip()
            if custom_expr:
                if not self._docker_evaluate_custom_filter(formatted_line, custom_expr):
                    return False  # Doesn't match custom expression

            # 5. Search text filter
            search_text = self.docker_search_var.get().strip().lower()
            if search_text:
                if search_text not in line_lower:
                    return False  # Doesn't match search text

            # Line passed all filters
            return True

        except Exception as e:
            # If any error in filter evaluation, default to showing the line
            logger.debug(f"Error in _docker_should_display_line: {e}")
            return True

    def _docker_append_log_line(self, line: str):
        """Append a log line to the display"""
        # Parse and format line (JSON → timestamp | level message)
        formatted_line = self._docker_parse_and_format_log_line(line)

        # Apply all filters (pre-defined + custom + search)
        if not self._docker_should_display_line(formatted_line):
            return  # Skip this line

        # Enable editing
        self.docker_log_text.config(state=tk.NORMAL)

        # Append formatted line
        self.docker_log_text.insert(tk.END, formatted_line + "\n")

        # Apply highlighting to the new line
        line_number = int(self.docker_log_text.index(tk.END).split('.')[0]) - 1
        formatted_lower = formatted_line.lower()

        if "error" in formatted_lower or "exception" in formatted_lower or "traceback" in formatted_lower:
            self.docker_log_text.tag_add("error", f"{line_number}.0", f"{line_number}.end")
        elif "warning" in formatted_lower or "warn" in formatted_lower:
            self.docker_log_text.tag_add("warning", f"{line_number}.0", f"{line_number}.end")
        elif "info" in formatted_lower:
            self.docker_log_text.tag_add("info", f"{line_number}.0", f"{line_number}.end")

        # Auto-scroll to bottom
        self.docker_log_text.see(tk.END)

        # Disable editing
        self.docker_log_text.config(state=tk.DISABLED)

        # Update line count
        total_lines = int(self.docker_log_text.index(tk.END).split('.')[0]) - 1
        self.docker_line_count_label.config(text=f"Lines: {total_lines}")

    def _docker_toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.docker_auto_refresh_enabled = self.docker_auto_refresh_var.get()

        if self.docker_auto_refresh_enabled:
            if not self.ssh_client or not self.ssh_client.is_connected():
                messagebox.showwarning("Not Connected", "Please connect SSH first")
                self.docker_auto_refresh_var.set(False)
                self.docker_auto_refresh_enabled = False
                return

            # Disable follow mode when auto-refreshing
            if self.docker_follow_enabled:
                self.docker_follow_var.set(False)
                self._docker_stop_follow()
                self.docker_follow_enabled = False

            logger.info(f"Docker log auto-refresh enabled ({self.docker_interval_var.get()}s)")
            self._docker_schedule_refresh()
        else:
            logger.info("Docker log auto-refresh disabled")

    def _docker_update_refresh_interval(self):
        """Update refresh interval"""
        self.docker_refresh_interval = self.docker_interval_var.get() * 1000  # Convert to ms
        logger.debug(f"Docker log refresh interval set to {self.docker_interval_var.get()}s")

    def _docker_schedule_refresh(self):
        """Schedule next auto-refresh"""
        if self.docker_auto_refresh_enabled:
            self._docker_refresh_logs()
            self.after(self.docker_refresh_interval, self._docker_schedule_refresh)

    def _docker_clear_display(self):
        """Clear log display"""
        self.docker_log_text.config(state=tk.NORMAL)
        self.docker_log_text.delete(1.0, tk.END)
        self.docker_log_text.config(state=tk.DISABLED)
        self.docker_line_count_label.config(text="Lines: 0")

    def _docker_save_logs(self):
        """Save logs to file"""
        if not self.docker_current_logs:
            messagebox.showinfo("No Data", "No logs to save")
            return

        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Save Docker Logs",
            initialfile=f"payload_manager_logs_{timestamp}.log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.docker_current_logs)

                logger.info(f"Docker logs saved to: {filepath}")
                messagebox.showinfo("Success", f"Logs saved!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error saving Docker logs: {e}")
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _docker_copy_all(self):
        """Copy all logs to clipboard"""
        if not self.docker_current_logs:
            messagebox.showinfo("No Data", "No logs to copy")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(self.docker_current_logs)
            self.update()

            messagebox.showinfo("Success", "Logs copied to clipboard!")

        except Exception as e:
            logger.error(f"Error copying Docker logs: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    # ========== On-Demand Logging Methods (NEW for Issue #118) ==========

    def _request_air_logs(self):
        """Request Air-Side logs on-demand"""
        if not self.tcp_client or not self.tcp_client.is_connected():
            messagebox.showerror("Not Connected", "Please connect to Air-Side first.\n\n" +
                               "To connect from Python console:\n" +
                               "app.connect_to_airside(host='10.0.1.53', port=5000)\n\n" +
                               "Or wait for Connection tab (Issue #117).")
            return

        # Auto-start UDP listener if not running (Issue #118 UX fix)
        # Without this, logs are requested but not received (no listener = lost packets)
        if not self.stream_running:
            logger.info("UDP listener not running - auto-starting for on-demand logs")
            self._on_start()
            # Brief delay to ensure listener is fully initialized
            time.sleep(0.5)

        duration = int(self.air_duration.get())

        self.air_log_status.config(text=f"Requesting {duration}s...", foreground="orange")
        self.air_request_btn.config(state=tk.DISABLED)

        def send_request():
            try:
                # Get local IP for destination parameter (Issue #118 - PM approved format)
                local_ip = self._get_local_ip()

                # Create command with explicit destination parameters
                message = protocol_msg.create_command("logging.enable_streaming", {
                    "destination_ip": local_ip,      # SystemTools IP (auto-detected)
                    "destination_port": 5007,         # UDP listener port
                    "duration_sec": duration          # User-specified duration
                })

                # DEBUG: Show exact message being sent to Air-Side (Issue #118 debug)
                print(f'DEBUG: Sending message: {message}')
                logger.info(f'DEBUG: Sending message: {message}')

                success = self.tcp_client.send_message(message)

                if not success:
                    raise Exception("Failed to send command")

                # Wait for response
                response = self.tcp_client.wait_for_response(timeout=5.0)

                # Debug: Log the actual response
                logger.info(f"Air-Side response: {response}")

                # Check Air-Side response format
                # Success response: {"message_type": "response", "payload": {"command": "...", "result": {...}}}
                # Error response: {"message_type": "error", "payload": {"error_message": "..."}}
                if not response:
                    raise Exception('No response from Air-Side (timeout)')

                msg_type = response.get('message_type')
                if msg_type == 'response':
                    # Success - check which command this response is for
                    payload = response.get('payload', {})
                    cmd = payload.get('command')

                    if cmd == 'logging.enable_streaming':
                        result = payload.get('result', {})
                        actual_duration = result.get('duration_sec', duration)
                        logger.info(f"Air-Side confirmed streaming for {actual_duration}s")
                        # Success - start countdown
                        self.after(0, lambda: self._start_air_log_countdown(actual_duration))
                    elif cmd == 'logging.disable_streaming':
                        # User clicked Stop before response arrived - this is OK
                        logger.info("Received disable_streaming response (user cancelled request)")
                        self.after(0, lambda: self.air_log_status.config(text="Cancelled", foreground="gray"))
                        self.after(0, lambda: self.air_request_btn.config(state=tk.NORMAL))
                        # Don't start countdown - streaming was cancelled
                    else:
                        raise Exception(f"Unexpected command in response: {cmd}")
                elif msg_type == 'error':
                    # Error response
                    error_msg = response.get('payload', {}).get('error_message', 'Unknown error')
                    raise Exception(error_msg)
                else:
                    raise Exception(f"Unexpected message type: {msg_type}")

            except Exception as e:
                logger.error(f"Failed to request Air-Side logs: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to request logs:\n{e}"))
                self.after(0, lambda: self.air_log_status.config(text="Error", foreground="red"))
                self.after(0, lambda: self.air_request_btn.config(state=tk.NORMAL))

        threading.Thread(target=send_request, daemon=True).start()

    def _start_air_log_countdown(self, duration):
        """Start countdown timer for Air-Side logging"""
        self.air_log_end_time = datetime.now().timestamp() + duration
        self.air_stop_btn.config(state=tk.NORMAL)
        self._update_air_log_countdown()

    def _update_air_log_countdown(self):
        """Update countdown display"""
        if not hasattr(self, 'air_log_end_time'):
            return

        remaining = int(self.air_log_end_time - datetime.now().timestamp())

        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            self.air_log_status.config(
                text=f"Streaming ({mins:02d}:{secs:02d} remaining)",
                foreground="green"
            )
            # Update every second
            self.after(1000, self._update_air_log_countdown)
        else:
            # Streaming stopped
            self.air_log_status.config(text="Idle", foreground="gray")
            self.air_request_btn.config(state=tk.NORMAL)
            self.air_stop_btn.config(state=tk.DISABLED)
            delattr(self, 'air_log_end_time')

    def _stop_air_logs(self):
        """Manually stop Air-Side log streaming"""
        if not self.tcp_client or not self.tcp_client.is_connected():
            return

        self.air_log_status.config(text="Stopping...", foreground="orange")

        def send_stop():
            try:
                # Use existing TCPClient backend
                message = protocol_msg.create_command("logging.disable_streaming", {})
                success = self.tcp_client.send_message(message)

                if success:
                    # Stop countdown
                    self.after(0, lambda: self._stop_air_log_countdown())
                else:
                    raise Exception("Failed to send command")

            except Exception as e:
                logger.error(f"Failed to stop Air-Side logs: {e}")
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to stop logs:\n{e}"))

        threading.Thread(target=send_stop, daemon=True).start()

    def _stop_air_log_countdown(self):
        """Stop the countdown timer"""
        if hasattr(self, 'air_log_end_time'):
            delattr(self, 'air_log_end_time')

        self.air_log_status.config(text="Stopped", foreground="gray")
        self.air_request_btn.config(state=tk.NORMAL)
        self.air_stop_btn.config(state=tk.DISABLED)

        # Update to Idle after 2 seconds
        self.after(2000, lambda: self.air_log_status.config(text="Idle"))

    # ========== Passive Logging Methods (from log_viewer_gui.py) ==========

    def _update_status_indicator(self, status: str):
        """Update status indicator"""
        self.status_indicator.delete("all")
        color_map = {"stopped": "gray", "running": "green", "paused": "orange"}
        color = color_map.get(status, "gray")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _on_start(self):
        """Start streaming logs (passive listeners)"""
        if self.stream_running:
            return

        logger.info("Starting Tri-Domain log streaming...")

        # Clear queue and buffer
        self.log_queue.clear()
        self.display_buffer.clear()

        # Start UDP discovery sender (for Air-Side auto-configuration)
        discovery_config = load_discovery_config()
        if discovery_config.get('enabled', True):
            self.discovery_sender = UDPDiscoverySender(
                target_host=discovery_config['target_host'],
                target_port=discovery_config['target_port'],
                interval_seconds=discovery_config['interval_seconds'],
                payload=discovery_config['payload']
            )
            self.discovery_sender.start()
            logger.info("UDP discovery sender started")

        # Create listeners
        self.air_listener = AirSideListener(host="0.0.0.0", port=5007)
        self.ground_listener = GroundSideListener(host="0.0.0.0", port=5008)  # TCP server on all interfaces

        # Start listeners
        self.air_listener.start(self.log_queue)
        self.ground_listener.start(self.log_queue)

        # Create and add SystemTools logging handler
        self.systemtools_handler = SystemToolsLogHandler(self.log_queue)
        self.systemtools_handler.setLevel(logging.DEBUG)  # Capture all levels
        logger.logger.addHandler(self.systemtools_handler)  # logger.logger is the actual logging.Logger
        logger.info("SystemTools log handler added - SystemTools logs now visible in viewer")

        # Start GUI update thread
        self.gui_update_running = True
        self.gui_update_thread = threading.Thread(target=self._gui_update_worker, daemon=True)
        self.gui_update_thread.start()

        # Update UI
        self.stream_running = True
        self.stream_paused = False
        self._update_status_indicator("running")
        self.status_label.config(text="Running", foreground="green")
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        logger.info("Tri-Domain log streaming started")

    def _on_pause(self):
        """Pause/resume display updates"""
        if not self.stream_running:
            return

        self.stream_paused = not self.stream_paused

        if self.stream_paused:
            self._update_status_indicator("paused")
            self.status_label.config(text="Paused", foreground="orange")
            self.pause_btn.config(text="▶ Resume")
            logger.info("Display paused (buffering logs)")
        else:
            self._update_status_indicator("running")
            self.status_label.config(text="Running", foreground="green")
            self.pause_btn.config(text="⏸ Pause")
            logger.info("Display resumed")

    def _on_stop(self):
        """Stop streaming"""
        if not self.stream_running:
            return

        logger.info("Stopping Tri-Domain log streaming...")

        # Stop GUI update thread
        self.gui_update_running = False
        if self.gui_update_thread:
            self.gui_update_thread.join(timeout=2.0)

        # Stop discovery sender
        if self.discovery_sender:
            self.discovery_sender.stop()
            self.discovery_sender = None

        # Stop listeners
        if self.air_listener:
            self.air_listener.stop()
            self.air_listener = None

        if self.ground_listener:
            self.ground_listener.stop()
            self.ground_listener = None

        # Remove SystemTools logging handler
        if self.systemtools_handler:
            logger.logger.removeHandler(self.systemtools_handler)  # logger.logger is the actual logging.Logger
            self.systemtools_handler = None
            logger.info("SystemTools log handler removed")

        # Clear queue
        self.log_queue.clear()

        # Update UI
        self.stream_running = False
        self.stream_paused = False
        self._update_status_indicator("stopped")
        self.status_label.config(text="Stopped", foreground="gray")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ Pause")
        self.stop_btn.config(state=tk.DISABLED)

        logger.info("Tri-Domain log streaming stopped")

    def _on_clear(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.display_buffer.clear()
        self._update_line_count()

    def _on_auto_scroll_changed(self):
        """Handle auto-scroll toggle"""
        self.auto_scroll = self.auto_scroll_var.get()

    def _on_filter_changed(self, event=None):
        """Handle filter change - redisplay filtered logs"""
        self._redisplay_filtered_logs()

    def _on_clear_search(self):
        """Clear search filter"""
        self.filter_search.set("")
        self._redisplay_filtered_logs()

    def _gui_update_worker(self):
        """Background thread to update GUI with new log entries"""
        while self.gui_update_running:
            try:
                if not self.stream_paused and len(self.log_queue) > 0:
                    # Schedule GUI update on main thread
                    self.after(0, self._process_queue)

                # Update every 100ms
                import time
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in GUI update worker: {e}")

    def _process_queue(self):
        """Process all pending log entries from queue"""
        if not self.gui_update_running or self.stream_paused:
            return

        # Process up to 100 entries at a time
        entries_to_process = []
        for _ in range(min(100, len(self.log_queue))):
            if self.log_queue:
                entry = self.log_queue.popleft()
                entries_to_process.append(entry)
                self.display_buffer.append(entry)  # Keep in buffer for filtering

                # Check if this is a heartbeat message and forward to Connection Monitor
                # Method 1: Protocol heartbeat (message_type == 'heartbeat')
                # Method 2: Log heartbeat (context contains 'heartbeat' or 'HEARTBEAT')
                message_type = entry.get('message_type', '')
                context = entry.get('context', '').upper()
                is_heartbeat = (message_type == 'heartbeat') or ('HEARTBEAT' in context)

                # Heartbeat and camera properties now come via separate UDP listeners
                # (HeartbeatListener on port 5002, StatusListener on port 5001)
                # No need to extract from log messages

                # Also print to console for real-time visibility
                domain = entry.get('domain', 'UNKNOWN')
                level = entry.get('level', 'INFO')
                category = entry.get('category', '')
                message = entry.get('message', '')
                print(f"[{domain}] [{level}] [{category}] {message}")

        if not entries_to_process:
            return

        # Filter and display
        for entry in entries_to_process:
            if self._should_display(entry):
                self._append_log_entry(entry)

        # Update line count
        self._update_line_count()
        self.last_update_time = datetime.now()
        self.last_update_label.config(text=self.last_update_time.strftime("%H:%M:%S"))

    def _should_display(self, entry: Dict[str, Any]) -> bool:
        """Check if log entry matches current filters (Issue #147 - Dynamic filters)"""
        # Domain filter - checkbox multi-selection with OR logic
        # If all unchecked = show all; if any checked = show only matching domains
        air_checked = self.filter_air.get()
        ground_checked = self.filter_ground.get()
        systemtools_checked = self.filter_systemtools.get()

        # If at least one domain is checked, filter by checked domains
        if air_checked or ground_checked or systemtools_checked:
            entry_domain = entry.get('domain', '').upper()
            domain_match = False

            if air_checked and entry_domain == 'AIR':
                domain_match = True
            if ground_checked and entry_domain == 'GROUND':
                domain_match = True
            if systemtools_checked and entry_domain == 'SYSTEMTOOLS':
                domain_match = True

            if not domain_match:
                return False
        # If all unchecked, show all domains (no filtering)

        # ========== Issue #147: Dynamic Context/Level Filter with AND/OR Logic ==========
        # Collect selected contexts and levels
        selected_contexts = [ctx for ctx, var in self.selected_filter_contexts.items() if var.get()]
        selected_levels = [lvl for lvl, var in self.selected_filter_levels.items() if var.get()]

        # Get entry context and level
        entry_context = entry.get('context', '').upper()
        entry_level = entry.get('level', '').upper()

        # Apply filter based on what's selected
        if selected_contexts and selected_levels:
            # Both contexts and levels selected - apply AND/OR logic
            context_match = entry_context in selected_contexts
            level_match = entry_level in selected_levels

            logic = self.filter_logic.get()
            if logic == "AND":
                # Both must match
                if not (context_match and level_match):
                    return False
            else:  # OR (default)
                # At least one must match
                if not (context_match or level_match):
                    return False

        elif selected_contexts:
            # Only contexts selected - filter by contexts only
            if entry_context not in selected_contexts:
                return False

        elif selected_levels:
            # Only levels selected - filter by levels only
            if entry_level not in selected_levels:
                return False
        # If neither selected, show all (no filtering)

        # OLD Level filter (combobox) - still supported for backwards compatibility
        level_filter = self.filter_level.get()
        if level_filter != "ALL" and entry.get('level') != level_filter:
            return False

        # OLD Context filter (combobox) - still supported for backwards compatibility
        context_filter = self.filter_context.get()
        if context_filter != "ALL":
            entry_context = entry.get('context', '').upper()
            if context_filter not in entry_context:
                return False

        # Text search filter
        search_text = self.filter_search.get().lower()
        if search_text:
            message = entry.get('message', '').lower()
            if search_text not in message:
                return False

        # Custom filter (Boolean logic)
        custom_expr = self.filter_custom.get().strip()
        if custom_expr:
            # Build a searchable text from the log entry
            entry_text = f"{entry.get('domain', '')} {entry.get('level', '')} {entry.get('context', '')} {entry.get('message', '')}"
            if not self._evaluate_custom_filter(entry_text, custom_expr):
                return False

        return True

    def _evaluate_custom_filter(self, text: str, expression: str) -> bool:
        """Evaluate custom filter expression with AND/OR/NOT logic

        Args:
            text: Searchable text (domain + level + context + message)
            expression: Boolean expression (e.g., "(camera AND error) OR (network AND timeout)")

        Returns:
            True if text matches expression, False otherwise
        """
        try:
            # Convert expression to lowercase for case-insensitive matching
            expr = expression.lower()
            text_lower = text.lower()

            # Replace AND, OR, NOT with Python operators
            # Use word boundaries to avoid replacing parts of words
            import re
            expr = re.sub(r'\bAND\b', ' and ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bOR\b', ' or ', expr, flags=re.IGNORECASE)
            expr = re.sub(r'\bNOT\b', ' not ', expr, flags=re.IGNORECASE)

            # Find all word tokens (not operators or parentheses)
            tokens = re.findall(r'\b(?!and\b|or\b|not\b)\w+\b', expr)

            # Build a safe evaluation context
            # Replace each token with: "'token' in text_lower"
            eval_expr = expr
            for token in set(tokens):
                # Escape the token for regex safety
                token_pattern = r'\b' + re.escape(token) + r'\b'
                replacement = f"('{token}' in text_lower)"
                eval_expr = re.sub(token_pattern, replacement, eval_expr)

            # Evaluate the expression safely
            result = eval(eval_expr, {"__builtins__": {}}, {"text_lower": text_lower})
            return bool(result)

        except Exception as e:
            # Parse error - don't filter
            logger.debug(f"Custom filter parse error: {e}")
            return True  # Show entry if filter expression is invalid

    def _on_clear_custom_filter(self):
        """Clear custom filter"""
        self.filter_custom.set("")
        self._on_filter_changed()

    # ========== Issue #147: Dynamic Filter Handlers ==========

    def _on_dynamic_filter_changed(self):
        """Handle dynamic filter checkbox changes (context/level multi-select)"""
        # Apply filters immediately when checkboxes change
        self._on_filter_changed()

    def _select_all_contexts(self):
        """Select all context checkboxes"""
        for var in self.selected_filter_contexts.values():
            var.set(True)
        self._on_dynamic_filter_changed()

    def _clear_all_contexts(self):
        """Clear all context checkboxes"""
        for var in self.selected_filter_contexts.values():
            var.set(False)
        self._on_dynamic_filter_changed()

    def _select_all_levels(self):
        """Select all level checkboxes"""
        for var in self.selected_filter_levels.values():
            var.set(True)
        self._on_dynamic_filter_changed()

    def _clear_all_levels(self):
        """Clear all level checkboxes"""
        for var in self.selected_filter_levels.values():
            var.set(False)
        self._on_dynamic_filter_changed()

    def _refresh_filter_labels(self):
        """Refresh filter labels from JSON (reload configuration)"""
        logger.info("Refreshing filter labels from JSON...")
        success = self.log_filter_manager.refresh()
        if success:
            messagebox.showinfo("Filters Refreshed",
                               "Filter configuration reloaded from JSON.\n\n"
                               "Note: To see updated buttons, restart the application.")
            logger.info("Filter labels refreshed successfully")
        else:
            messagebox.showerror("Refresh Failed",
                                "Failed to reload filter configuration.\n"
                                "Check logs for details.")

    def _apply_preset(self, preset_name: str):
        """Apply a preset filter configuration"""
        logger.info(f"Applying preset filter: {preset_name}")
        preset_config = self.log_filter_manager.apply_preset(preset_name)

        if not preset_config:
            messagebox.showwarning("Preset Not Found",
                                  f"Preset '{preset_name}' not found in configuration.")
            return

        # Clear all current selections
        self._clear_all_contexts()
        self._clear_all_levels()

        # Apply preset contexts
        for context in preset_config.get('contexts', []):
            if context in self.selected_filter_contexts:
                self.selected_filter_contexts[context].set(True)

        # Apply preset levels
        for level in preset_config.get('levels', []):
            if level in self.selected_filter_levels:
                self.selected_filter_levels[level].set(True)

        # Apply preset logic
        logic = preset_config.get('logic', 'OR')
        self.filter_logic.set(logic)

        # Apply filter
        self._on_dynamic_filter_changed()
        logger.info(f"Preset '{preset_name}' applied: {len(preset_config.get('contexts', []))} contexts, "
                   f"{len(preset_config.get('levels', []))} levels, logic={logic}")

    def _apply_custom_expression(self):
        """Apply custom filter expression (with Apply button - no real-time filtering)"""
        expression = self.filter_custom.get().strip()
        if expression:
            logger.info(f"Applying custom filter expression: {expression}")
            self._on_filter_changed()
        else:
            logger.info("Custom filter expression is empty, clearing filter")
            self._on_filter_changed()

    # ========== End Issue #147 Handlers ==========

    def _append_log_entry(self, entry: Dict[str, Any]):
        """Append a single log entry to display"""
        # Format: [TIMESTAMP] [DOMAIN ] [LEVEL  ] [CONTEXT] Message
        timestamp = entry.get('timestamp', 'NO-TS')
        if 'T' in timestamp:
            try:
                time_part = timestamp.split('T')[1][:12]
            except:
                time_part = timestamp[:12]
        else:
            time_part = timestamp[:12]

        domain = entry.get('domain', 'UNK').ljust(6)[:6]
        level = entry.get('level', 'INFO').ljust(7)[:7]
        context = entry.get('context', 'UNKNOWN').ljust(8)[:8]
        message = entry.get('message', '')

        log_line = f"{time_part} [{domain}] [{level}] [{context}] {message}\n"

        # Enable editing
        self.log_text.config(state=tk.NORMAL)

        # Insert line
        self.log_text.insert(tk.END, log_line)

        # Get line number
        line_number = int(self.log_text.index(tk.END).split('.')[0]) - 1

        # Apply domain color
        domain_code = entry.get('domain', '')
        if domain_code == 'AIR':
            self.log_text.tag_add("air", f"{line_number}.0", f"{line_number}.end")
        elif domain_code == 'GROUND':
            self.log_text.tag_add("ground", f"{line_number}.0", f"{line_number}.end")

        # Apply level color (overrides domain color)
        level_code = entry.get('level', 'INFO')
        if level_code == 'ERROR':
            self.log_text.tag_add("error", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'WARNING':
            self.log_text.tag_add("warning", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'DEBUG':
            self.log_text.tag_add("debug", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'INFO':
            self.log_text.tag_add("info", f"{line_number}.0", f"{line_number}.end")

        # Highlight search text
        search_text = self.filter_search.get()
        if search_text:
            self._highlight_search_in_line(line_number, log_line, search_text)

        # Auto-scroll
        if self.auto_scroll:
            self.log_text.see(tk.END)

        # Disable editing
        self.log_text.config(state=tk.DISABLED)

    def _highlight_search_in_line(self, line_number: int, line_text: str, search_text: str):
        """Highlight search text in a specific line"""
        start_idx = 0
        while True:
            idx = line_text.lower().find(search_text.lower(), start_idx)
            if idx == -1:
                break
            start_pos = f"{line_number}.{idx}"
            end_pos = f"{line_number}.{idx + len(search_text)}"
            self.log_text.tag_add("highlight", start_pos, end_pos)
            start_idx = idx + len(search_text)

    def _redisplay_filtered_logs(self):
        """Redisplay all logs from buffer with current filters"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        for entry in self.display_buffer:
            if self._should_display(entry):
                self._append_log_entry(entry)

        self._update_line_count()

    def _update_line_count(self):
        """Update line count label"""
        total_lines = int(self.log_text.index(tk.END).split('.')[0]) - 1
        buffer_size = len(self.display_buffer)
        self.line_count_label.config(text=f"Displayed: {total_lines} / Buffer: {buffer_size}")

    def _on_save_to_file(self):
        """Export logs to file"""
        if not self.display_buffer:
            messagebox.showinfo("No Data", "No logs to export")
            return

        export_format = self.export_format_var.get()
        ext_map = {"json": ".json", "csv": ".csv", "text": ".txt"}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            initialfile=f"tri_domain_logs_{timestamp}{ext_map[export_format]}",
            defaultextension=ext_map[export_format],
            filetypes=[("All files", "*.*")]
        )

        if filepath:
            try:
                # Filter logs that should be displayed
                filtered_logs = [entry for entry in self.display_buffer if self._should_display(entry)]

                if export_format == "json":
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(filtered_logs, f, indent=2)
                elif export_format == "csv":
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        if filtered_logs:
                            writer = csv.DictWriter(f, fieldnames=filtered_logs[0].keys())
                            writer.writeheader()
                            writer.writerows(filtered_logs)
                else:  # text
                    content = self.log_text.get(1.0, tk.END)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                logger.info(f"Logs exported to: {filepath}")
                messagebox.showinfo("Success", f"Logs saved!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error exporting logs: {e}")
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _on_copy_all(self):
        """Copy all visible logs to clipboard"""
        content = self.log_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("No Data", "No logs to copy")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            messagebox.showinfo("Success", "All logs copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying logs: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _on_copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.update()
                messagebox.showinfo("Success", "Selected text copied to clipboard!")
            else:
                messagebox.showinfo("No Selection", "Please select text to copy")
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please select text to copy")
        except Exception as e:
            logger.error(f"Error copying selection: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _wire_dashboard_clients(self):
        """Wire up TCP/SSH/ADB clients to Connection Monitor and Camera Dashboard tabs"""
        # The Connection Monitor and Camera Dashboard expect to manage their own clients,
        # but we can share the TCP and SSH clients when they're created.

        # Set up camera properties callback to update both tabs
        # This will be called when camera.get_properties response is received
        def on_camera_properties(properties: dict):
            """Forward camera properties to both Connection Monitor and Camera Dashboard"""
            try:
                # Update Connection Monitor tab
                if hasattr(self, 'connection_tab'):
                    self.connection_tab.on_camera_properties_received(properties)

                # Update Camera Dashboard tab with full status message format
                if hasattr(self, 'camera_tab'):
                    # Wrap properties in status message format expected by update_camera_status
                    status_message = {
                        'payload': {
                            'camera': properties
                        }
                    }
                    self.camera_tab.update_camera_status(status_message)
            except Exception as e:
                logger.error(f"Error updating camera properties in dashboards: {e}")

        # Store the callback for later use
        self.camera_properties_callback = on_camera_properties

        # Set up heartbeat callback to update Connection Monitor
        def on_heartbeat(sender: str, data: dict):
            """Forward heartbeat to Connection Monitor"""
            try:
                if hasattr(self, 'connection_tab'):
                    self.connection_tab.on_heartbeat_received(sender, data)
            except Exception as e:
                logger.error(f"Error updating heartbeat in Connection Monitor: {e}")

        # Store the callback for later use
        self.heartbeat_callback = on_heartbeat

        # Create and wire UDP listeners for heartbeat and status (like main.py)
        # Get port numbers from configuration
        status_port = config.get('network', 'udp_status_port', 5001)
        heartbeat_port = config.get('network', 'udp_heartbeat_port', 5002)

        logger.info(f"Creating UDP listeners - Status Port: {status_port}, Heartbeat Port: {heartbeat_port}")

        # Create listeners
        self.status_listener = StatusListener(status_port)
        self.heartbeat_listener = HeartbeatListener(heartbeat_port)

        # Wire StatusListener callback to forward camera properties and health data
        def on_status_message(message):
            """Handle UDP status broadcast - called from background thread"""
            # Schedule GUI updates on main thread using after_idle()
            # Update camera tab with full message (like main.py line 419)
            self.after_idle(lambda: self.camera_tab.update_camera_status(message))

            # Update connection tab with camera properties if present (like main.py lines 427-432)
            payload = message.get("payload", {})
            if "camera" in payload and isinstance(payload["camera"], dict):
                camera_props = payload["camera"]
                if camera_props:  # If camera data is not empty
                    self.after_idle(lambda props=camera_props:
                        self.connection_tab.on_camera_properties_received(props))

            # Update Performance Analytics tab with health snapshot (Issue #130)
            # Extract full health snapshot from status message
            health_snapshot = {}
            if "system" in payload:
                health_snapshot.update(payload["system"])
            if "camera" in payload:
                health_snapshot.update(payload["camera"])
            if "network" in payload:
                health_snapshot.update(payload["network"])
            if "sync" in payload:
                health_snapshot.update(payload["sync"])

            if health_snapshot:
                self.after_idle(lambda snapshot=health_snapshot:
                    self.analytics_tab.update_with_snapshot(snapshot))

        self.status_listener.on_message_received = on_status_message

        # Wire HeartbeatListener callback to forward heartbeat
        def on_heartbeat_message(message):
            """Handle UDP heartbeat - called from background thread"""
            # Schedule GUI updates on main thread using after_idle()
            payload = message.get("payload", {})
            sender = payload.get("sender", "unknown")  # "air" or "ground"
            self.after_idle(lambda s=sender, d=payload:
                self.heartbeat_callback(s, d))

        self.heartbeat_listener.on_message_received = on_heartbeat_message

        # Start UDP listeners immediately (they run in background threads)
        logger.info("Starting UDP listeners for heartbeat and camera status")
        self.status_listener.start()
        self.heartbeat_listener.start()

        # Periodically check if Connection Monitor has created a TCP client
        # and share it with the Camera Dashboard
        def check_and_share_tcp_client():
            """Check if Connection Monitor has a TCP client and share with Camera Dashboard"""
            try:
                if hasattr(self, 'connection_tab') and hasattr(self.connection_tab, 'tcp_client'):
                    if self.connection_tab.tcp_client and hasattr(self, 'camera_tab'):
                        # Share the TCP client with Camera Dashboard
                        self.camera_tab.set_tcp_client(self.connection_tab.tcp_client)

                        # Also hook into the TCP client's message callback to forward camera properties
                        original_callback = self.connection_tab.tcp_client.on_message_received

                        def enhanced_callback(message: dict):
                            # Call original callback
                            if original_callback:
                                original_callback(message)

                            # Check if this is a camera.get_properties response
                            if message.get('message_type') == 'response':
                                payload = message.get('payload', {})
                                if 'iso' in payload or 'shutter_speed' in payload:
                                    # This looks like camera properties
                                    self.camera_properties_callback(payload)

                        self.connection_tab.tcp_client.on_message_received = enhanced_callback
                        logger.info("TCP client shared with Camera Dashboard and callbacks configured")
                        return  # Done

                # Check again in 500ms
                self.after(500, check_and_share_tcp_client)
            except Exception as e:
                logger.error(f"Error in check_and_share_tcp_client: {e}")

        # Start periodic check
        self.after(100, check_and_share_tcp_client)

        logger.info("Dashboard tabs wired up successfully")

    def _on_closing(self):
        """Handle window close"""
        if self.stream_running:
            self._on_stop()

        # Cleanup dashboard tabs
        try:
            if hasattr(self, 'connection_tab') and hasattr(self.connection_tab, 'cleanup'):
                self.connection_tab.cleanup()
            if hasattr(self, 'camera_tab') and hasattr(self.camera_tab, 'cleanup'):
                self.camera_tab.cleanup()
            if hasattr(self, 'analytics_tab') and hasattr(self.analytics_tab, 'cleanup'):
                logger.info("Cleaning up Performance Analytics tab")
                self.analytics_tab.cleanup()
            if hasattr(self, 'file_browser_tab') and hasattr(self.file_browser_tab, 'cleanup'):
                logger.info("Cleaning up File Browser tab")
                self.file_browser_tab.cleanup()
        except Exception as e:
            logger.error(f"Error during dashboard cleanup: {e}")

        # Stop UDP listeners
        try:
            if hasattr(self, 'status_listener') and self.status_listener:
                logger.info("Stopping UDP status listener")
                self.status_listener.stop()
            if hasattr(self, 'heartbeat_listener') and self.heartbeat_listener:
                logger.info("Stopping UDP heartbeat listener")
                self.heartbeat_listener.stop()
        except Exception as e:
            logger.error(f"Error stopping UDP listeners: {e}")

        self.destroy()
    def _docker_fetch_image_id(self):
        """Fetch Docker container image ID and display it"""
        try:
            if not self.ssh_client or not self.ssh_client.is_connected():
                return

            # Get Docker image ID from payload-manager container
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                "docker inspect payload-manager --format '{{.Image}}'"
            )

            if exit_code == 0 and stdout.strip():
                # Extract image ID (format: sha256:abcdef123456...)
                full_id = stdout.strip()

                # Remove 'sha256:' prefix if present
                if full_id.startswith('sha256:'):
                    full_id = full_id[7:]

                # Return first 12 characters (standard Docker short ID)
                short_id = full_id[:12]

                # Update label
                self.docker_image_id_label.config(text=short_id, foreground="blue")
                logger.info(f"Docker Image ID: {short_id}")
            else:
                self.docker_image_id_label.config(text="N/A", foreground="gray")
                logger.warning(f"Failed to get Docker image ID: {stderr}")

        except Exception as e:
            logger.error(f"Error fetching Docker image ID: {e}")
            self.docker_image_id_label.config(text="Error", foreground="red")

    def _docker_pop_out_logs(self):
        """Pop out live log viewer into a separate window with full filtering capabilities"""
        # If window already exists, bring it to front
        if self.docker_popup_window and self.docker_popup_window.winfo_exists():
            self.docker_popup_window.lift()
            self.docker_popup_window.focus_force()
            logger.debug("Pop-out window brought to front")
            return

        # Create new popup window
        self.docker_popup_window = tk.Toplevel(self)
        self.docker_popup_window.title("DPM SystemTools - Live Docker Logs Viewer")
        self.docker_popup_window.geometry("1600x1000")

        # Create main frame
        main_frame = ttk.Frame(self.docker_popup_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(main_frame,
                               text="📋 Live Docker Logs - payload-manager",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))

        # Info frame with Docker Image ID
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="Status:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.popup_status_label = ttk.Label(info_frame,
                                       text=self.docker_ssh_status_label.cget("text"),
                                       font=('Arial', 9),
                                       foreground=self.docker_ssh_status_label.cget("foreground"))
        self.popup_status_label.pack(side=tk.LEFT, padx=5)

        ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        ttk.Label(info_frame, text="Image ID:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.popup_image_id_label = ttk.Label(info_frame,
                                         text=self.docker_image_id_label.cget("text"),
                                         font=('Arial', 9),
                                         foreground=self.docker_image_id_label.cget("foreground"))
        self.popup_image_id_label.pack(side=tk.LEFT, padx=5)

        ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        self.popup_line_count = ttk.Label(info_frame, text=self.docker_line_count_label.cget("text"))
        self.popup_line_count.pack(side=tk.LEFT, padx=5)

        ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        # Last update label
        ttk.Label(info_frame, text="Last Updated:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        self.popup_last_update_label = ttk.Label(info_frame, text="Never", font=('Arial', 9, 'italic'))
        self.popup_last_update_label.pack(side=tk.LEFT, padx=5)

        # ===== CONTROLS SECTION =====
        controls_frame = ttk.LabelFrame(main_frame, text="Controls & Filters", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Auto-refresh controls
        refresh_row = ttk.Frame(controls_frame)
        refresh_row.pack(fill=tk.X, pady=5)

        self.popup_auto_refresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(refresh_row, text="Auto-refresh",
                       variable=self.popup_auto_refresh_var,
                       command=self._popup_toggle_auto_refresh).pack(side=tk.LEFT, padx=5)

        ttk.Label(refresh_row, text="Interval (sec):").pack(side=tk.LEFT, padx=(20, 5))
        self.popup_interval_var = tk.IntVar(value=5)
        ttk.Spinbox(refresh_row, from_=1, to=60, textvariable=self.popup_interval_var,
                   width=5, command=self._popup_update_refresh_interval).pack(side=tk.LEFT, padx=5)

        ttk.Button(refresh_row, text="🔄 Refresh Now",
                  command=self._popup_refresh_now).pack(side=tk.LEFT, padx=20)

        # Search bar
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.popup_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.popup_search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self._popup_apply_filters())

        ttk.Button(search_frame, text="Clear", command=self._popup_clear_search).pack(side=tk.LEFT, padx=5)

        # Quick Filters
        quick_filters_frame = ttk.LabelFrame(controls_frame, text="Quick Filters", padding=5)
        quick_filters_frame.pack(fill=tk.X, pady=5)

        # Row 1: Level filters
        filter_row1 = ttk.Frame(quick_filters_frame)
        filter_row1.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row1, text="Level:", width=10).pack(side=tk.LEFT, padx=5)
        self.popup_filter_errors = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row1, text="Errors", variable=self.popup_filter_errors,
                       command=self._popup_apply_filters).pack(side=tk.LEFT, padx=3)
        self.popup_filter_warnings = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row1, text="Warnings", variable=self.popup_filter_warnings,
                       command=self._popup_apply_filters).pack(side=tk.LEFT, padx=3)

        # Row 2: Context filters - dynamically generated from protocol
        filter_row2 = ttk.Frame(quick_filters_frame)
        filter_row2.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row2, text="Context:", width=10).pack(side=tk.LEFT, padx=5)

        # Create BooleanVar and Checkbutton for each context from protocol
        self.popup_context_filters = {}
        for context_id in LogContexts.get_context_ids():
            var = tk.BooleanVar(value=False)
            self.popup_context_filters[context_id] = var
            ttk.Checkbutton(filter_row2, text=context_id.capitalize(), variable=var,
                           command=self._popup_apply_filters).pack(side=tk.LEFT, padx=3)

        # Row 3: Special filters
        filter_row3 = ttk.Frame(quick_filters_frame)
        filter_row3.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row3, text="Special:", width=10).pack(side=tk.LEFT, padx=5)
        self.popup_filter_hide_verbose = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row3, text="Hide Verbose", variable=self.popup_filter_hide_verbose,
                       command=self._popup_apply_filters).pack(side=tk.LEFT, padx=3)
        ttk.Label(filter_row3, text="(hides updateCachedProperties)", font=('Arial', 8, 'italic'),
                 foreground='gray').pack(side=tk.LEFT, padx=5)

        ttk.Button(filter_row3, text="Clear All Filters", command=self._popup_clear_all_filters).pack(side=tk.RIGHT, padx=5)

        # Custom Boolean filter
        custom_filter_frame = ttk.LabelFrame(controls_frame, text="Custom Filter (Boolean Logic)", padding=5)
        custom_filter_frame.pack(fill=tk.X, pady=5)

        filter_help_row = ttk.Frame(custom_filter_frame)
        filter_help_row.pack(fill=tk.X, pady=2)
        ttk.Label(filter_help_row, text="Syntax: Use AND, OR, NOT. Example: (camera AND connect) OR (network AND timeout)",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        custom_filter_input_row = ttk.Frame(custom_filter_frame)
        custom_filter_input_row.pack(fill=tk.X, pady=2)

        ttk.Label(custom_filter_input_row, text="Expression:").pack(side=tk.LEFT, padx=5)
        self.popup_custom_filter_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_filter_input_row, textvariable=self.popup_custom_filter_var, width=60)
        custom_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        custom_entry.bind("<KeyRelease>", lambda e: self._popup_apply_filters())

        ttk.Button(custom_filter_input_row, text="Apply", command=self._popup_apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_filter_input_row, text="Clear", command=self._popup_clear_custom_filter).pack(side=tk.LEFT, padx=5)

        # ===== LOG DISPLAY AREA =====
        self.docker_popup_text = scrolledtext.ScrolledText(main_frame,
                                                           font=('Courier New', 9),
                                                           wrap=tk.NONE,
                                                           state='normal',
                                                           bg='#FFFFFF',
                                                           fg='#000000')
        self.docker_popup_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure color tags for different log levels
        self.docker_popup_text.tag_config("error", foreground="#FF0000", font=('Courier New', 9, 'bold'))
        self.docker_popup_text.tag_config("warning", foreground="#FF8C00", font=('Courier New', 9))
        self.docker_popup_text.tag_config("info", foreground="#0000FF")
        self.docker_popup_text.tag_config("highlight", background="#FFFF00")

        # Initialize popup state
        self.popup_auto_refresh_enabled = False
        self.popup_refresh_interval = 5000  # ms
        self.popup_after_id = None

        # Copy current log content to popup (with filters applied)
        self._popup_refresh_now()

        # Bottom button bar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="📋 Copy All",
                  command=self._docker_copy_popup_content).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="💾 Save to File",
                  command=self._docker_save_popup_to_file).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="❌ Close",
                  command=self._popup_close_window).pack(side=tk.RIGHT, padx=5)

        # Cleanup handler
        self.docker_popup_window.protocol("WM_DELETE_WINDOW", self._popup_close_window)

        logger.info("Pop-out live logs window created with full filtering")

    # ===== POPUP-SPECIFIC FILTER METHODS =====

    def _popup_apply_all_filters(self, logs: str) -> str:
        """Apply all popup filters: pre-defined + custom + search

        Args:
            logs: Formatted log lines

        Returns:
            Filtered log lines
        """
        filtered_lines = []

        for line in logs.splitlines():
            line_lower = line.lower()

            # 1. Pre-defined filters (Level)
            filter_errors = self.popup_filter_errors.get()
            filter_warnings = self.popup_filter_warnings.get()

            level_match = False
            if filter_errors or filter_warnings:
                # At least one level filter is active
                if filter_errors and '[error' in line_lower:
                    level_match = True
                if filter_warnings and '[warning' in line_lower:
                    level_match = True

                if not level_match:
                    continue  # Skip this line

            # 2. Pre-defined filters (Context) - dynamically check all protocol contexts
            # Check if any context filter is active
            any_context_active = any(var.get() for var in self.popup_context_filters.values())

            if any_context_active:
                # At least one context filter is active
                # Try to extract context from JSON, or infer from content
                context_match = False

                # Try JSON parsing first
                try:
                    json_start = line.find('{')
                    if json_start != -1:
                        json_data = json.loads(line[json_start:])
                        log_context = json_data.get('context', '').upper()
                        if log_context and self.popup_context_filters.get(log_context, tk.BooleanVar()).get():
                            context_match = True
                except:
                    pass

                # If no JSON context, infer from content keywords
                if not context_match:
                    for context_id, var in self.popup_context_filters.items():
                        if var.get():
                            # Simple keyword matching for each context
                            context_lower = context_id.lower()
                            if context_lower in line_lower:
                                context_match = True
                                break

                if not context_match:
                    continue  # Skip this line

            # 3. Special filter: Hide verbose
            if self.popup_filter_hide_verbose.get():
                if 'updatecachedproperties' in line_lower:
                    continue  # Skip verbose messages

            # 4. Custom filter (Boolean logic)
            custom_expr = self.popup_custom_filter_var.get().strip()
            if custom_expr:
                if not self._docker_evaluate_custom_filter(line, custom_expr):
                    continue  # Skip this line

            # 5. Search text filter
            search_text = self.popup_search_var.get().strip().lower()
            if search_text:
                if search_text not in line_lower:
                    continue  # Skip this line

            # Line passed all filters - include it
            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _popup_apply_filters(self):
        """Re-apply all filters to popup display"""
        if not self.docker_popup_text or not self.docker_current_logs:
            return

        try:
            # Get formatted logs from main window's current logs
            formatted_lines = []
            for line in self.docker_current_logs.splitlines():
                if line.strip():
                    formatted_line = self._docker_parse_and_format_log_line(line)
                    formatted_lines.append(formatted_line)

            formatted_logs = '\n'.join(formatted_lines)

            # Apply popup filters
            display_logs = self._popup_apply_all_filters(formatted_logs)

            # Update popup display
            self.docker_popup_text.delete(1.0, tk.END)
            self.docker_popup_text.insert(1.0, display_logs)

            # Apply syntax highlighting
            self._popup_apply_highlighting()

            # Scroll to bottom
            self.docker_popup_text.see(tk.END)

            # Update statistics
            line_count = len(display_logs.splitlines())
            self.popup_line_count.config(text=f"Lines: {line_count}")

        except Exception as e:
            logger.error(f"Error applying popup filters: {e}")

    def _popup_apply_highlighting(self):
        """Apply syntax highlighting to popup text"""
        content = self.docker_popup_text.get(1.0, tk.END)
        lines = content.splitlines()

        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Highlight errors
            if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower:
                self.docker_popup_text.tag_add("error", f"{i}.0", f"{i}.end")

            # Highlight warnings
            elif "warning" in line_lower or "warn" in line_lower:
                self.docker_popup_text.tag_add("warning", f"{i}.0", f"{i}.end")

            # Highlight info
            elif "info" in line_lower:
                self.docker_popup_text.tag_add("info", f"{i}.0", f"{i}.end")

        # Highlight search matches
        search_text = self.popup_search_var.get()
        if search_text:
            start_idx = "1.0"
            while True:
                start_idx = self.docker_popup_text.search(search_text, start_idx, nocase=True, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(search_text)}c"
                self.docker_popup_text.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

    def _popup_clear_all_filters(self):
        """Clear all popup pre-defined filters"""
        self.popup_filter_errors.set(False)
        self.popup_filter_warnings.set(False)
        # Clear all dynamic context filters
        for var in self.popup_context_filters.values():
            var.set(False)
        self.popup_filter_hide_verbose.set(False)
        self._popup_apply_filters()

    def _popup_clear_custom_filter(self):
        """Clear popup custom filter"""
        self.popup_custom_filter_var.set("")
        self._popup_apply_filters()

    def _popup_clear_search(self):
        """Clear popup search filter"""
        self.popup_search_var.set("")
        self._popup_apply_filters()

    def _popup_refresh_now(self):
        """Manually refresh popup window content from SSH"""
        if not self.ssh_client or not self.ssh_client.is_connected():
            messagebox.showwarning("Not Connected", "Please connect SSH first in the main window", parent=self.docker_popup_window)
            return

        # Update status indicators from main window
        self.popup_status_label.config(
            text=self.docker_ssh_status_label.cget("text"),
            foreground=self.docker_ssh_status_label.cget("foreground")
        )
        self.popup_image_id_label.config(
            text=self.docker_image_id_label.cget("text"),
            foreground=self.docker_image_id_label.cget("foreground")
        )

        # Fetch latest logs and apply filters
        self._popup_apply_filters()

        # Update timestamp
        self.popup_last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

        logger.debug("Pop-out window manually refreshed")

    def _popup_toggle_auto_refresh(self):
        """Toggle popup auto-refresh on/off"""
        self.popup_auto_refresh_enabled = self.popup_auto_refresh_var.get()

        if self.popup_auto_refresh_enabled:
            if not self.ssh_client or not self.ssh_client.is_connected():
                messagebox.showwarning("Not Connected", "Please connect SSH first in the main window", parent=self.docker_popup_window)
                self.popup_auto_refresh_var.set(False)
                self.popup_auto_refresh_enabled = False
                return

            logger.info(f"Popup auto-refresh enabled ({self.popup_interval_var.get()}s)")
            self._popup_schedule_refresh()
        else:
            logger.info("Popup auto-refresh disabled")
            if self.popup_after_id:
                self.after_cancel(self.popup_after_id)
                self.popup_after_id = None

    def _popup_update_refresh_interval(self):
        """Update popup refresh interval"""
        self.popup_refresh_interval = self.popup_interval_var.get() * 1000  # Convert to ms

    def _popup_schedule_refresh(self):
        """Schedule next popup auto-refresh"""
        if self.popup_auto_refresh_enabled:
            self._popup_refresh_now()
            self.popup_after_id = self.after(self.popup_refresh_interval, self._popup_schedule_refresh)

    def _popup_close_window(self):
        """Clean up and close popup window"""
        # Cancel auto-refresh if active
        if self.popup_after_id:
            self.after_cancel(self.popup_after_id)
            self.popup_after_id = None

        # Destroy window
        if self.docker_popup_window:
            self.docker_popup_window.destroy()
            self.docker_popup_window = None

        logger.info("Pop-out window closed")

    def _docker_copy_popup_content(self):
        """Copy all popup content to clipboard"""
        try:
            if not self.docker_popup_text:
                return

            content = self.docker_popup_text.get(1.0, tk.END)
            self.docker_popup_window.clipboard_clear()
            self.docker_popup_window.clipboard_append(content)
            logger.info("Popup content copied to clipboard")
            messagebox.showinfo("Copied", "Log content copied to clipboard", parent=self.docker_popup_window)
        except Exception as e:
            logger.error(f"Error copying popup content: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}", parent=self.docker_popup_window)

    def _docker_save_popup_to_file(self):
        """Save popup content to a file"""
        try:
            if not self.docker_popup_text:
                return

            filename = filedialog.asksaveasfilename(
                parent=self.docker_popup_window,
                title="Save Log File",
                defaultextension=".log",
                filetypes=[
                    ("Log files", "*.log"),
                    ("JSON Lines", "*.jsonl"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                content = self.docker_popup_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)

                logger.info(f"Popup content saved to: {filename}")
                messagebox.showinfo("Saved", f"Log saved to:\n{filename}", parent=self.docker_popup_window)

        except Exception as e:
            logger.error(f"Error saving popup content: {e}")
            messagebox.showerror("Error", f"Failed to save:\n{e}", parent=self.docker_popup_window)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info(f"DPM Management System {get_version_string()} Starting...")
    logger.info(f"Build: {get_build_info_string()}")
    logger.info("=" * 60)

    app = DPMManagementSystem()
    app.mainloop()


if __name__ == "__main__":
    main()
