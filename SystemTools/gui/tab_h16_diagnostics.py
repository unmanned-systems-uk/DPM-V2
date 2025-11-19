"""
H16 ADB Diagnostics Tab for DPM Diagnostic Tool
Comprehensive ADB diagnostic features for H16 Ground Station
Based on Cheat_Sheet_ADB_H16.md and Cheat_Sheet_ADB_LOG_ANALYSIS.md
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Optional
import threading
import subprocess
import re
from datetime import datetime

from utils.protocol_logger import logger
from utils.config import config
from network.diagnostic_client import DiagnosticClient


class H16DiagnosticsTab(ttk.Frame):
    """H16 ADB Diagnostics tab - comprehensive H16 diagnostic features"""

    def __init__(self, parent):
        super().__init__(parent)

        self.adb_connected = False
        self.h16_ip = config.get('network', 'h16_ip', '10.0.1.92')
        self.adb_port = "5555"

        # Logcat filter state
        self.logcat_search_var = tk.StringVar()
        self.logcat_filter_mode_var = tk.BooleanVar(value=False)
        self.raw_logcat_output = ""  # Store raw output for filtering

        self._create_ui()
        self._check_adb_available()

        logger.debug("SYSTEM", "H16 Diagnostics tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Connection & Status
        conn_frame = ttk.LabelFrame(self, text="H16 ADB Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Connection controls
        conn_controls = ttk.Frame(conn_frame)
        conn_controls.pack(fill=tk.X)

        ttk.Label(conn_controls, text="H16 IP:").pack(side=tk.LEFT, padx=5)
        self.ip_entry = ttk.Entry(conn_controls, width=15)
        self.ip_entry.insert(0, self.h16_ip)
        self.ip_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(conn_controls, text="Port:").pack(side=tk.LEFT, padx=(20, 5))
        self.port_entry = ttk.Entry(conn_controls, width=8)
        self.port_entry.insert(0, self.adb_port)
        self.port_entry.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(conn_controls, text="Connect ADB",
                                      command=self._connect_adb)
        self.connect_btn.pack(side=tk.LEFT, padx=10)

        self.disconnect_btn = ttk.Button(conn_controls, text="Disconnect",
                                         command=self._disconnect_adb,
                                         state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(conn_controls, text="Check Devices",
                  command=self._check_devices).pack(side=tk.LEFT, padx=5)

        # Connection status indicator
        self.conn_status_label = ttk.Label(conn_controls, text="● Disconnected",
                                           foreground="gray", font=('Arial', 10, 'bold'))
        self.conn_status_label.pack(side=tk.RIGHT, padx=10)

        # Quick Diagnostics
        quick_frame = ttk.LabelFrame(self, text="Quick Diagnostics", padding=10)
        quick_frame.pack(fill=tk.X, padx=10, pady=5)

        quick_info = ttk.Frame(quick_frame)
        quick_info.pack(fill=tk.X, pady=5)

        ttk.Label(quick_info, text="Automated diagnostic tests from Cheat Sheets",
                 font=('Arial', 8, 'italic'), foreground="gray").pack(side=tk.LEFT, padx=5)

        quick_btns = ttk.Frame(quick_frame)
        quick_btns.pack(fill=tk.X, pady=5)

        # Prominent Smart Diagnostic button
        self.smart_diagnostic_btn = ttk.Button(quick_frame, text="🔍 Run Smart Diagnostic",
                                              command=self._run_smart_diagnostic,
                                              style='Accent.TButton')
        self.smart_diagnostic_btn.pack(pady=5)

        ttk.Label(quick_frame, text="Automated H16 health check with comprehensive analysis and recommendations",
                 font=('Arial', 8, 'italic'), foreground="gray").pack()

        ttk.Separator(quick_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Individual diagnostic buttons
        quick_btns_row = ttk.Frame(quick_frame)
        quick_btns_row.pack(fill=tk.X, pady=5)

        ttk.Button(quick_btns_row, text="📊 System Info",
                  command=self._run_full_diagnostic,
                  width=20).pack(side=tk.LEFT, padx=5)

        ttk.Button(quick_btns_row, text="📡 Network Check",
                  command=self._run_network_diagnostic,
                  width=20).pack(side=tk.LEFT, padx=5)

        ttk.Button(quick_btns_row, text="🔗 Air-Side Test",
                  command=self._run_airside_connectivity,
                  width=20).pack(side=tk.LEFT, padx=5)

        # Diagnostic Categories (Notebook)
        self.diagnostic_notebook = ttk.Notebook(self)
        self.diagnostic_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create sub-tabs
        self._create_protocol_diagnostics_tab()  # NEW: Protocol-based diagnostics
        self._create_troubleshooting_tab()
        self._create_network_tab()
        self._create_logcat_tab()
        self._create_system_tab()
        self._create_commands_tab()

        # Output display
        output_frame = ttk.LabelFrame(self, text="Diagnostic Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                     font=('Courier', 9), height=12)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for colored output
        self.output_text.tag_config("command", foreground="blue", font=('Courier', 9, 'bold'))
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("info", foreground="gray")
        self.output_text.tag_config("warning", foreground="orange")

        # Bottom controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(bottom_frame, text="Clear Output",
                  command=self._clear_output).pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Copy Output",
                  command=self._copy_output).pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Copy Selected",
                  command=self._copy_selected).pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Save Report",
                  command=self._save_report).pack(side=tk.LEFT, padx=5)

        # Status
        self.status_label = ttk.Label(bottom_frame, text="Ready - Connect ADB to begin",
                                     font=('Arial', 9, 'italic'))
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Initialize diagnostic client
        self.diagnostic_client = DiagnosticClient()
        self.auto_refresh_enabled = False
        self.last_system_info = None
        self.last_app_status = None

    def _create_protocol_diagnostics_tab(self):
        """Create Protocol Diagnostics sub-tab (ADB-free diagnostics via TCP)"""
        diag_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(diag_tab, text="🔬 Protocol Diagnostics")

        # Info label
        info_frame = ttk.Frame(diag_tab)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="H16 system diagnostics via protocol (no ADB required) - Issue #36",
                 font=('Arial', 9, 'italic'), foreground="gray").pack(anchor=tk.W)

        # Quick Diagnostics Section
        quick_frame = ttk.LabelFrame(diag_tab, text="Quick Diagnostics", padding=10)
        quick_frame.pack(fill=tk.X, padx=10, pady=5)

        quick_btns_row1 = ttk.Frame(quick_frame)
        quick_btns_row1.pack(fill=tk.X, pady=2)

        ttk.Button(quick_btns_row1, text="🏓 Ping H16",
                  command=self._protocol_ping_h16,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(quick_btns_row1, text="📊 Get System Info",
                  command=self._protocol_get_system_info,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(quick_btns_row1, text="📱 Get App Status",
                  command=self._protocol_get_app_status,
                  width=25).pack(side=tk.LEFT, padx=5)

        quick_btns_row2 = ttk.Frame(quick_frame)
        quick_btns_row2.pack(fill=tk.X, pady=2)

        ttk.Button(quick_btns_row2, text="🔍 Run Full Diagnostics",
                  command=self._protocol_run_full_diagnostics,
                  width=25).pack(side=tk.LEFT, padx=5)

        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_check = ttk.Checkbutton(quick_btns_row2, text="Auto-refresh (5s)",
                                            variable=self.auto_refresh_var,
                                            command=self._toggle_auto_refresh)
        auto_refresh_check.pack(side=tk.LEFT, padx=20)

        # System Health Panel
        health_frame = ttk.LabelFrame(diag_tab, text="System Health", padding=10)
        health_frame.pack(fill=tk.X, padx=10, pady=5)

        # Battery
        battery_frame = ttk.Frame(health_frame)
        battery_frame.pack(fill=tk.X, pady=2)
        ttk.Label(battery_frame, text="Battery:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_battery_label = ttk.Label(battery_frame, text="---", font=('Arial', 10, 'bold'), foreground='gray')
        self.diag_battery_label.pack(side=tk.LEFT, padx=5)

        # CPU Usage
        cpu_frame = ttk.Frame(health_frame)
        cpu_frame.pack(fill=tk.X, pady=2)
        ttk.Label(cpu_frame, text="CPU Usage:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_cpu_label = ttk.Label(cpu_frame, text="---", font=('Arial', 10), foreground='gray')
        self.diag_cpu_label.pack(side=tk.LEFT, padx=5)

        # Memory
        memory_frame = ttk.Frame(health_frame)
        memory_frame.pack(fill=tk.X, pady=2)
        ttk.Label(memory_frame, text="Memory:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_memory_label = ttk.Label(memory_frame, text="---", font=('Arial', 10), foreground='gray')
        self.diag_memory_label.pack(side=tk.LEFT, padx=5)

        # Storage
        storage_frame = ttk.Frame(health_frame)
        storage_frame.pack(fill=tk.X, pady=2)
        ttk.Label(storage_frame, text="Storage:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_storage_label = ttk.Label(storage_frame, text="---", font=('Arial', 10), foreground='gray')
        self.diag_storage_label.pack(side=tk.LEFT, padx=5)

        # Uptime
        uptime_frame = ttk.Frame(health_frame)
        uptime_frame.pack(fill=tk.X, pady=2)
        ttk.Label(uptime_frame, text="Uptime:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_uptime_label = ttk.Label(uptime_frame, text="---", font=('Arial', 10), foreground='gray')
        self.diag_uptime_label.pack(side=tk.LEFT, padx=5)

        # Last Updated
        updated_frame = ttk.Frame(health_frame)
        updated_frame.pack(fill=tk.X, pady=2)
        ttk.Label(updated_frame, text="Last Updated:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        self.diag_updated_label = ttk.Label(updated_frame, text="Never", font=('Arial', 9, 'italic'), foreground='gray')
        self.diag_updated_label.pack(side=tk.LEFT, padx=5)

    def _create_troubleshooting_tab(self):
        """Create ADB Troubleshooting sub-tab"""
        troubleshoot_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(troubleshoot_tab, text="🔧 ADB Troubleshooting")

        # Info label
        info_frame = ttk.Frame(troubleshoot_tab)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text="Comprehensive ADB troubleshooting tools based on Cheat_Sheet_ADB_H16.md",
                 font=('Arial', 9, 'italic'), foreground="gray").pack(anchor=tk.W)

        # Connection Diagnostics Section
        conn_diag_frame = ttk.LabelFrame(troubleshoot_tab, text="Connection Diagnostics", padding=10)
        conn_diag_frame.pack(fill=tk.X, padx=10, pady=5)

        conn_btns_row1 = ttk.Frame(conn_diag_frame)
        conn_btns_row1.pack(fill=tk.X, pady=2)

        ttk.Button(conn_btns_row1, text="🔍 Ping H16",
                  command=self._troubleshoot_ping,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(conn_btns_row1, text="🔌 Test Port 5555",
                  command=self._troubleshoot_port,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(conn_btns_row1, text="📋 Check ADB Devices",
                  command=self._check_devices,
                  width=25).pack(side=tk.LEFT, padx=5)

        conn_btns_row2 = ttk.Frame(conn_diag_frame)
        conn_btns_row2.pack(fill=tk.X, pady=2)

        ttk.Button(conn_btns_row2, text="🔍 Check Local Port 5555",
                  command=self._troubleshoot_local_port,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(conn_btns_row2, text="📡 Check ADB Server",
                  command=self._troubleshoot_adb_server,
                  width=25).pack(side=tk.LEFT, padx=5)

        # ADB Server Management Section
        server_frame = ttk.LabelFrame(troubleshoot_tab, text="ADB Server Management", padding=10)
        server_frame.pack(fill=tk.X, padx=10, pady=5)

        server_btns = ttk.Frame(server_frame)
        server_btns.pack(fill=tk.X, pady=2)

        ttk.Button(server_btns, text="🔄 Reconnect ADB",
                  command=self._troubleshoot_reconnect,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(server_btns, text="🛑 Kill ADB Server",
                  command=self._troubleshoot_kill_server,
                  width=25).pack(side=tk.LEFT, padx=5)

        ttk.Button(server_btns, text="▶️ Start ADB Server",
                  command=self._troubleshoot_start_server,
                  width=25).pack(side=tk.LEFT, padx=5)

        # Full Reset Section
        reset_frame = ttk.LabelFrame(troubleshoot_tab, text="Quick Fixes", padding=10)
        reset_frame.pack(fill=tk.X, padx=10, pady=5)

        reset_btns = ttk.Frame(reset_frame)
        reset_btns.pack(fill=tk.X, pady=2)

        ttk.Button(reset_btns, text="🔧 Full ADB Reset & Reconnect",
                  command=self._troubleshoot_full_reset,
                  width=35).pack(side=tk.LEFT, padx=5)

        ttk.Button(reset_btns, text="🏥 Complete Diagnostic",
                  command=self._troubleshoot_complete_diagnostic,
                  width=35).pack(side=tk.LEFT, padx=5)

        # H16-Side Diagnostics Section
        h16_diag_frame = ttk.LabelFrame(troubleshoot_tab, text="H16-Side Diagnostics (via ADB Shell)", padding=10)
        h16_diag_frame.pack(fill=tk.X, padx=10, pady=5)

        h16_info = ttk.Frame(h16_diag_frame)
        h16_info.pack(fill=tk.X, pady=2)

        ttk.Label(h16_info, text="Run diagnostics directly on H16 to check if ADB issue is on device side",
                 font=('Arial', 8, 'italic'), foreground="gray").pack(anchor=tk.W, padx=5)

        h16_btns = ttk.Frame(h16_diag_frame)
        h16_btns.pack(fill=tk.X, pady=5)

        ttk.Button(h16_btns, text="📱 Run H16 Diagnostics",
                  command=self._troubleshoot_h16_diagnostics,
                  width=35).pack(side=tk.LEFT, padx=5)

        ttk.Button(h16_btns, text="📋 Generate Termux Script",
                  command=self._troubleshoot_generate_termux_script,
                  width=35).pack(side=tk.LEFT, padx=5)

        # Firewall Check Section (Windows specific)
        firewall_frame = ttk.LabelFrame(troubleshoot_tab, text="Windows Firewall & Security", padding=10)
        firewall_frame.pack(fill=tk.X, padx=10, pady=5)

        firewall_info = ttk.Frame(firewall_frame)
        firewall_info.pack(fill=tk.X, pady=2)

        ttk.Label(firewall_info, text="Note: Norton Security or Windows Firewall may block ADB connections",
                 font=('Arial', 8), foreground="orange").pack(anchor=tk.W, padx=5)

        ttk.Label(firewall_info, text="If connection fails, check firewall settings manually",
                 font=('Arial', 8), foreground="gray").pack(anchor=tk.W, padx=5)

    def _create_network_tab(self):
        """Create Network Diagnostics sub-tab"""
        network_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(network_tab, text="Network Diagnostics")

        # VXLAN Tunnel Section
        vxlan_frame = ttk.LabelFrame(network_tab, text="VXLAN Tunnel Status", padding=10)
        vxlan_frame.pack(fill=tk.X, padx=10, pady=5)

        vxlan_btns = ttk.Frame(vxlan_frame)
        vxlan_btns.pack(fill=tk.X)

        ttk.Button(vxlan_btns, text="Check br-vxlan Interface",
                  command=lambda: self._run_adb_command("ip addr show br-vxlan")).pack(side=tk.LEFT, padx=5)

        ttk.Button(vxlan_btns, text="Check VXLAN Tunnel (vxlan1)",
                  command=lambda: self._run_adb_command("ip -d link show vxlan1")).pack(side=tk.LEFT, padx=5)

        ttk.Button(vxlan_btns, text="Show Routing Table",
                  command=lambda: self._run_adb_command("ip route show")).pack(side=tk.LEFT, padx=5)

        # Air-Side Connectivity
        airside_frame = ttk.LabelFrame(network_tab, text="Air-Side Connectivity", padding=10)
        airside_frame.pack(fill=tk.X, padx=10, pady=5)

        airside_info = ttk.Frame(airside_frame)
        airside_info.pack(fill=tk.X, pady=2)

        ttk.Label(airside_info, text="192.168.144.10 - Raspberry Pi 4 (Air-Side SBC / Payload Server)",
                 font=('Arial', 8)).pack(anchor=tk.W, padx=5)
        ttk.Label(airside_info, text="192.168.144.11 - H16 br-vxlan (This Device)",
                 font=('Arial', 8)).pack(anchor=tk.W, padx=5)

        airside_btns = ttk.Frame(airside_frame)
        airside_btns.pack(fill=tk.X, pady=5)

        ttk.Button(airside_btns, text="Ping Air-Side Pi (.10)",
                  command=lambda: self._run_adb_command("ping -c 4 192.168.144.10")).pack(side=tk.LEFT, padx=5)

        ttk.Button(airside_btns, text="Test Port 5000 on Air-Side",
                  command=lambda: self._run_adb_command("nc -zv 192.168.144.10 5000 || echo 'Connection test'")).pack(side=tk.LEFT, padx=5)

        ttk.Button(airside_btns, text="Check Route to Air-Side",
                  command=lambda: self._run_adb_command("ip route get 192.168.144.10")).pack(side=tk.LEFT, padx=5)

        # Ports & Services
        ports_frame = ttk.LabelFrame(network_tab, text="DPM Ports & Services", padding=10)
        ports_frame.pack(fill=tk.X, padx=10, pady=5)

        ports_btns = ttk.Frame(ports_frame)
        ports_btns.pack(fill=tk.X)

        ttk.Button(ports_btns, text="Check All DPM Ports (5000/5001/5002)",
                  command=lambda: self._run_adb_command("netstat -an | grep -E '(5000|5001|5002)'")).pack(side=tk.LEFT, padx=5)

        ttk.Button(ports_btns, text="Check Listening Ports",
                  command=lambda: self._run_adb_command("netstat -ln")).pack(side=tk.LEFT, padx=5)

        ttk.Button(ports_btns, text="Show All Connections",
                  command=lambda: self._run_adb_command("netstat -an")).pack(side=tk.LEFT, padx=5)

    def _create_logcat_tab(self):
        """Create Logcat Monitoring sub-tab"""
        logcat_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(logcat_tab, text="Logcat & Logs")

        # Search/Filter controls
        search_frame = ttk.LabelFrame(logcat_tab, text="Search & Filter Logcat Output", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        search_controls = ttk.Frame(search_frame)
        search_controls.pack(fill=tk.X, pady=2)

        ttk.Label(search_controls, text="Search:").pack(side=tk.LEFT, padx=5)

        self.logcat_search_entry = ttk.Entry(search_controls, textvariable=self.logcat_search_var, width=40)
        self.logcat_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.logcat_search_var.trace('w', lambda *args: self._apply_logcat_filter())

        ttk.Button(search_controls, text="Clear Search",
                  command=self._clear_logcat_search).pack(side=tk.LEFT, padx=5)

        # Filter options
        filter_options = ttk.Frame(search_frame)
        filter_options.pack(fill=tk.X, pady=2)

        ttk.Checkbutton(filter_options, text="Filter Mode (only show matching lines)",
                       variable=self.logcat_filter_mode_var,
                       command=self._apply_logcat_filter).pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_options, text="Tip: Use & for AND (e.g., \"camera & set_property\" or \"192.168.144.11 & focus\")",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Logcat controls
        logcat_ctrl_frame = ttk.LabelFrame(logcat_tab, text="Logcat Monitoring", padding=10)
        logcat_ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

        logcat_row1 = ttk.Frame(logcat_ctrl_frame)
        logcat_row1.pack(fill=tk.X, pady=5)

        ttk.Button(logcat_row1, text="Live DPM Logs",
                  command=lambda: self._run_logcat("grep -E 'DPM|NetworkClient|Camera'")).pack(side=tk.LEFT, padx=5)

        ttk.Button(logcat_row1, text="Errors Only",
                  command=lambda: self._run_logcat("grep -E 'ERROR|FATAL'")).pack(side=tk.LEFT, padx=5)

        ttk.Button(logcat_row1, text="Last 100 Lines",
                  command=lambda: self._run_logcat_raw("logcat -d -t 100")).pack(side=tk.LEFT, padx=5)

        ttk.Button(logcat_row1, text="Clear Logcat",
                  command=lambda: self._run_adb_command("logcat -c")).pack(side=tk.LEFT, padx=5)

        # Specific filters
        filters_frame = ttk.LabelFrame(logcat_tab, text="Quick Load Logcat", padding=10)
        filters_frame.pack(fill=tk.X, padx=10, pady=5)

        filters_btns = ttk.Frame(filters_frame)
        filters_btns.pack(fill=tk.X)

        ttk.Button(filters_btns, text="All Logcat (Last 200)",
                  command=lambda: self._run_logcat_raw("logcat -d -t 200")).pack(side=tk.LEFT, padx=5)

        ttk.Button(filters_btns, text="Last 500 Lines",
                  command=lambda: self._run_logcat_raw("logcat -d -t 500")).pack(side=tk.LEFT, padx=5)

        ttk.Button(filters_btns, text="Last 1000 Lines",
                  command=lambda: self._run_logcat_raw("logcat -d -t 1000")).pack(side=tk.LEFT, padx=5)

        ttk.Label(filters_frame, text="Load logcat first, then use search box above to filter (e.g., \"camera & set_property\")",
                 font=('Arial', 8, 'italic'), foreground='blue').pack(anchor=tk.W, padx=5, pady=2)

    def _create_system_tab(self):
        """Create System Information sub-tab"""
        system_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(system_tab, text="System Info")

        # Device Info
        device_frame = ttk.LabelFrame(system_tab, text="Device Information", padding=10)
        device_frame.pack(fill=tk.X, padx=10, pady=5)

        device_btns = ttk.Frame(device_frame)
        device_btns.pack(fill=tk.X)

        ttk.Button(device_btns, text="Android Version",
                  command=lambda: self._run_adb_command("getprop ro.build.version.release")).pack(side=tk.LEFT, padx=5)

        ttk.Button(device_btns, text="Device Model",
                  command=lambda: self._run_adb_command("getprop ro.product.model")).pack(side=tk.LEFT, padx=5)

        ttk.Button(device_btns, text="All Properties",
                  command=lambda: self._run_adb_command("getprop")).pack(side=tk.LEFT, padx=5)

        # Resource Monitoring
        resources_frame = ttk.LabelFrame(system_tab, text="Resource Monitoring", padding=10)
        resources_frame.pack(fill=tk.X, padx=10, pady=5)

        resources_btns = ttk.Frame(resources_frame)
        resources_btns.pack(fill=tk.X)

        ttk.Button(resources_btns, text="Top Processes",
                  command=lambda: self._run_adb_command("top -n 1 | head -20")).pack(side=tk.LEFT, padx=5)

        ttk.Button(resources_btns, text="Memory Info",
                  command=lambda: self._run_adb_command("cat /proc/meminfo | head -10")).pack(side=tk.LEFT, padx=5)

        ttk.Button(resources_btns, text="Disk Usage",
                  command=lambda: self._run_adb_command("df -h")).pack(side=tk.LEFT, padx=5)

        ttk.Button(resources_btns, text="Battery Status",
                  command=lambda: self._run_adb_command("dumpsys battery")).pack(side=tk.LEFT, padx=5)

        ttk.Button(resources_btns, text="Uptime",
                  command=lambda: self._run_adb_command("uptime")).pack(side=tk.LEFT, padx=5)

    def _create_commands_tab(self):
        """Create Custom Commands sub-tab"""
        commands_tab = ttk.Frame(self.diagnostic_notebook)
        self.diagnostic_notebook.add(commands_tab, text="Custom Commands")

        # Command input
        cmd_frame = ttk.LabelFrame(commands_tab, text="Execute Custom ADB Shell Command", padding=10)
        cmd_frame.pack(fill=tk.X, padx=10, pady=10)

        cmd_input_frame = ttk.Frame(cmd_frame)
        cmd_input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cmd_input_frame, text="adb shell").pack(side=tk.LEFT, padx=5)

        self.custom_cmd_entry = ttk.Entry(cmd_input_frame, font=('Courier', 10))
        self.custom_cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.custom_cmd_entry.bind('<Return>', lambda e: self._run_custom_command())

        ttk.Button(cmd_input_frame, text="Execute",
                  command=self._run_custom_command).pack(side=tk.LEFT, padx=5)

        # Common commands quick access
        common_frame = ttk.LabelFrame(commands_tab, text="Common Commands Quick Access", padding=10)
        common_frame.pack(fill=tk.X, padx=10, pady=5)

        common_row1 = ttk.Frame(common_frame)
        common_row1.pack(fill=tk.X, pady=2)

        ttk.Button(common_row1, text="List Interfaces",
                  command=lambda: self._run_adb_command("ip addr show")).pack(side=tk.LEFT, padx=5)

        ttk.Button(common_row1, text="WiFi Status",
                  command=lambda: self._run_adb_command("dumpsys wifi | grep -E 'SSID|RSSI|mNetworkInfo'")).pack(side=tk.LEFT, padx=5)

        ttk.Button(common_row1, text="Running Processes",
                  command=lambda: self._run_adb_command("ps | grep dpm")).pack(side=tk.LEFT, padx=5)

        common_row2 = ttk.Frame(common_frame)
        common_row2.pack(fill=tk.X, pady=2)

        ttk.Button(common_row2, text="Network Stats",
                  command=lambda: self._run_adb_command("cat /proc/net/dev")).pack(side=tk.LEFT, padx=5)

        ttk.Button(common_row2, text="Check lmi40",
                  command=lambda: self._run_adb_command("ip addr show lmi40")).pack(side=tk.LEFT, padx=5)

        ttk.Button(common_row2, text="Bridge FDB",
                  command=lambda: self._run_adb_command("bridge fdb show dev vxlan1")).pack(side=tk.LEFT, padx=5)

    def _check_adb_available(self):
        """Check if ADB is available on system"""
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("SYSTEM", "ADB is available")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("SYSTEM", "ADB not found in PATH")
            self._append_output("⚠️  WARNING: ADB not found in system PATH\n", "warning")
            self._append_output("Please install Android Debug Bridge (ADB) and add to PATH\n", "info")
            return False

    def _connect_adb(self):
        """Connect to H16 via ADB"""
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if not ip:
            messagebox.showwarning("Invalid Input", "Please enter H16 IP address")
            return

        self.status_label.config(text=f"Connecting to {ip}:{port}...")
        self._append_output(f"\n$ adb connect {ip}:{port}\n", "command")

        def connect():
            try:
                result = subprocess.run(
                    ['adb', 'connect', f'{ip}:{port}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                output = result.stdout + result.stderr
                self.after(0, lambda: self._handle_connect_result(result.returncode, output, ip, port))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._append_output("ERROR: Connection timeout\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Connection timeout"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"ERROR: {str(e)}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Connection failed"))

        threading.Thread(target=connect, daemon=True).start()

    def _handle_connect_result(self, exit_code, output, ip, port):
        """Handle ADB connection result"""
        self._append_output(output + "\n", "success" if exit_code == 0 else "error")

        if "connected" in output.lower():
            self.adb_connected = True
            self.conn_status_label.config(text="● Connected", foreground="green")
            self.status_label.config(text=f"Connected to {ip}:{port}")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            logger.info("NETWORK", f"ADB connected to {ip}:{port}")
        else:
            self.adb_connected = False
            self.conn_status_label.config(text="● Connection Failed", foreground="red")
            self.status_label.config(text="Connection failed")

    def _disconnect_adb(self):
        """Disconnect ADB"""
        self._run_adb_command_direct(['adb', 'disconnect'])
        self.adb_connected = False
        self.conn_status_label.config(text="● Disconnected", foreground="gray")
        self.status_label.config(text="Disconnected")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)

    def _check_devices(self):
        """Check connected ADB devices"""
        self._run_adb_command_direct(['adb', 'devices', '-l'])

    def _run_adb_command(self, shell_command: str):
        """Run ADB shell command"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self.status_label.config(text=f"Executing: {shell_command[:50]}...")
        self._append_output(f"\n$ adb shell {shell_command}\n", "command")

        def run():
            try:
                result = subprocess.run(
                    ['adb', 'shell', shell_command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"

                self.after(0, lambda: self._append_output(output + "\n", "success"))
                self.after(0, lambda: self.status_label.config(text="Command completed"))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._append_output("ERROR: Command timeout\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Command timeout"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"ERROR: {str(e)}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Command failed"))

        threading.Thread(target=run, daemon=True).start()

    def _run_adb_command_direct(self, cmd_list):
        """Run ADB command directly (not shell)"""
        self._append_output(f"\n$ {' '.join(cmd_list)}\n", "command")

        def run():
            try:
                result = subprocess.run(
                    cmd_list,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                output = result.stdout + result.stderr
                self.after(0, lambda: self._append_output(output + "\n", "success"))

            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"ERROR: {str(e)}\n", "error"))

        threading.Thread(target=run, daemon=True).start()

    def _run_custom_command(self):
        """Run custom ADB shell command from entry"""
        command = self.custom_cmd_entry.get().strip()
        if command:
            self._run_adb_command(command)
            # Add to history (could implement command history here)

    def _run_logcat(self, filter_cmd):
        """Run logcat with specific filter"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        full_cmd = f"logcat -d | {filter_cmd}"
        self._run_adb_command(full_cmd)

    def _run_logcat_raw(self, shell_command: str):
        """Run logcat command and store raw output for filtering"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self.status_label.config(text=f"Loading logcat...")
        self._append_output(f"\n$ adb shell {shell_command}\n", "command")

        def run():
            try:
                result = subprocess.run(
                    ['adb', 'shell', shell_command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"

                # Store raw output for filtering
                self.raw_logcat_output = output

                # Apply current filter if any
                self.after(0, lambda: self._display_logcat_output(output))
                self.after(0, lambda: self.status_label.config(text=f"Logcat loaded ({len(output.splitlines())} lines)"))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._append_output("ERROR: Command timeout\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Command timeout"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"ERROR: {str(e)}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Command failed"))

        threading.Thread(target=run, daemon=True).start()

    def _display_logcat_output(self, output: str):
        """Display logcat output, applying filter if needed"""
        search_text = self.logcat_search_var.get().strip()
        filter_mode = self.logcat_filter_mode_var.get()

        if search_text and filter_mode:
            # Apply filtering
            filtered = self._filter_logcat(output, search_text)
            num_matching = len(filtered.splitlines())
            num_total = len(output.splitlines())
            self._append_output(f"Showing {num_matching} of {num_total} lines (filter: '{search_text}')\n\n", "info")
            self._append_output(filtered + "\n", "success")
        elif search_text:
            # Highlight mode - just show all with info about search
            self._append_output(f"Loaded {len(output.splitlines())} lines (search active but filter mode off)\n", "info")
            self._append_output(f"Enable 'Filter Mode' to show only matching lines\n\n", "info")
            self._append_output(output + "\n", "success")
        else:
            # No filter
            self._append_output(output + "\n", "success")

    def _filter_logcat(self, output: str, search_text: str) -> str:
        """Filter logcat output - supports AND logic with &"""
        filtered_lines = []

        # Check if AND logic is requested (using & separator)
        if '&' in search_text:
            # Split by & and trim whitespace
            search_terms = [term.strip().lower() for term in search_text.split('&') if term.strip()]

            # Filter lines that contain ALL search terms (AND logic)
            for line in output.splitlines():
                line_lower = line.lower()
                if all(term in line_lower for term in search_terms):
                    filtered_lines.append(line)
        else:
            # Single term search
            search_lower = search_text.lower()
            for line in output.splitlines():
                if search_lower in line.lower():
                    filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _apply_logcat_filter(self):
        """Apply current search filter to displayed logcat output"""
        if not self.raw_logcat_output:
            return  # Nothing loaded yet

        # Clear output and re-display with current filter
        self._clear_output()
        self._append_output("=== Filtered Logcat Output ===\n\n", "command")
        self._display_logcat_output(self.raw_logcat_output)

    def _clear_logcat_search(self):
        """Clear logcat search box"""
        self.logcat_search_var.set("")
        self.logcat_filter_mode_var.set(False)
        if self.raw_logcat_output:
            self._apply_logcat_filter()

    def _run_smart_diagnostic(self):
        """Run comprehensive SMART diagnostic with analysis and recommendations"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  H16 SMART DIAGNOSTIC REPORT\n", "command")
        self._append_output("  Automated Health Check with Intelligent Analysis\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        self.status_label.config(text="Running Smart Diagnostic...")
        self.smart_diagnostic_btn.config(state=tk.DISABLED)

        def run_diagnostics():
            try:
                issues_found = []
                warnings_found = []

                # 1. System Information
                self.after(0, lambda: self._append_output("📱 H16 SYSTEM INFORMATION\n", "command"))

                # Android version
                exit_code, stdout, stderr = self._run_adb_sync("getprop ro.build.version.release")
                if exit_code == 0:
                    android_ver = stdout.strip()
                    self.after(0, lambda v=android_ver: self._append_output(f"  ✅ Android Version: {v}\n", "success"))

                # Device model
                exit_code, stdout, stderr = self._run_adb_sync("getprop ro.product.model")
                if exit_code == 0:
                    model = stdout.strip()
                    self.after(0, lambda m=model: self._append_output(f"  ✅ Device Model: {m}\n", "success"))

                # Battery
                exit_code, stdout, stderr = self._run_adb_sync("dumpsys battery | grep level")
                if exit_code == 0 and 'level:' in stdout:
                    try:
                        battery = int(stdout.split('level:')[1].split()[0])
                        if battery < 20:
                            warnings_found.append(f"Low battery: {battery}%")
                            self.after(0, lambda b=battery: self._append_output(f"  ⚠️  Battery: {b}% (LOW)\n", "warning"))
                        else:
                            self.after(0, lambda b=battery: self._append_output(f"  ✅ Battery: {b}%\n", "success"))
                    except:
                        pass

                self.after(0, lambda: self._append_output("\n", None))

                # 2. Network Health
                self.after(0, lambda: self._append_output("🌐 NETWORK HEALTH\n", "command"))

                # Check br-vxlan interface
                exit_code, stdout, stderr = self._run_adb_sync("ip addr show br-vxlan")
                if exit_code == 0:
                    if "192.168.144.11" in stdout and "state UP" in stdout:
                        self.after(0, lambda: self._append_output("  ✅ br-vxlan Interface: 192.168.144.11 (UP)\n", "success"))
                    elif "192.168.144.11" in stdout:
                        warnings_found.append("br-vxlan interface is DOWN")
                        self.after(0, lambda: self._append_output("  ⚠️  br-vxlan Interface: 192.168.144.11 (DOWN)\n", "warning"))
                    else:
                        issues_found.append("br-vxlan not configured correctly")
                        self.after(0, lambda: self._append_output("  ❌ br-vxlan Interface: Not configured\n", "error"))
                else:
                    issues_found.append("Cannot check br-vxlan interface")
                    self.after(0, lambda: self._append_output("  ❌ br-vxlan Interface: Error\n", "error"))

                # Check VXLAN tunnel
                exit_code, stdout, stderr = self._run_adb_sync("ip -d link show vxlan1")
                if exit_code == 0:
                    if "vxlan id 1" in stdout and "state" in stdout:
                        self.after(0, lambda: self._append_output("  ✅ VXLAN Tunnel: Configured\n", "success"))
                    else:
                        warnings_found.append("VXLAN tunnel may be misconfigured")
                        self.after(0, lambda: self._append_output("  ⚠️  VXLAN Tunnel: Check configuration\n", "warning"))
                else:
                    issues_found.append("VXLAN tunnel not found")
                    self.after(0, lambda: self._append_output("  ❌ VXLAN Tunnel: Not found\n", "error"))

                # WiFi status
                exit_code, stdout, stderr = self._run_adb_sync("dumpsys wifi | grep 'SSID\\|RSSI'")
                if exit_code == 0:
                    lines = stdout.strip().split('\n')
                    for line in lines[:2]:  # First 2 lines
                        if 'SSID' in line or 'RSSI' in line:
                            self.after(0, lambda l=line: self._append_output(f"  ℹ️  WiFi: {l.strip()}\n", "info"))

                self.after(0, lambda: self._append_output("\n", None))

                # 3. Air-Side Connectivity
                self.after(0, lambda: self._append_output("🔗 AIR-SIDE CONNECTIVITY\n", "command"))

                # Ping Air-Side Pi
                exit_code, stdout, stderr = self._run_adb_sync("ping -c 4 -W 2 192.168.144.10")
                if exit_code == 0 and "0% packet loss" in stdout:
                    # Extract time
                    if "time=" in stdout:
                        times = [float(t.split('time=')[1].split()[0]) for t in stdout.split('\n') if 'time=' in t]
                        if times:
                            avg_time = sum(times) / len(times)
                            if avg_time > 100:
                                warnings_found.append(f"High latency to Air-Side: {avg_time:.1f}ms")
                                self.after(0, lambda t=avg_time: self._append_output(f"  ⚠️  Air-Side Pi (.10): Reachable (HIGH LATENCY: {t:.1f}ms)\n", "warning"))
                            else:
                                self.after(0, lambda t=avg_time: self._append_output(f"  ✅ Air-Side Pi (.10): Reachable ({t:.1f}ms avg)\n", "success"))
                    else:
                        self.after(0, lambda: self._append_output("  ✅ Air-Side Pi (.10): Reachable\n", "success"))
                else:
                    issues_found.append("Cannot reach Air-Side Pi at 192.168.144.10")
                    self.after(0, lambda: self._append_output("  ❌ Air-Side Pi (.10): UNREACHABLE\n", "error"))

                # Check route
                exit_code, stdout, stderr = self._run_adb_sync("ip route get 192.168.144.10")
                if exit_code == 0 and "dev br-vxlan" in stdout:
                    self.after(0, lambda: self._append_output("  ✅ Route to Air-Side: via br-vxlan\n", "success"))
                else:
                    warnings_found.append("Route to Air-Side may be incorrect")
                    self.after(0, lambda: self._append_output("  ⚠️  Route to Air-Side: Check routing\n", "warning"))

                self.after(0, lambda: self._append_output("\n", None))

                # 4. DPM Application Status
                self.after(0, lambda: self._append_output("📱 DPM APPLICATION STATUS\n", "command"))

                # Check DPM app running
                exit_code, stdout, stderr = self._run_adb_sync("ps | grep dpm")
                if exit_code == 0 and stdout.strip():
                    self.after(0, lambda: self._append_output("  ✅ DPM App: Running\n", "success"))
                else:
                    warnings_found.append("DPM app may not be running")
                    self.after(0, lambda: self._append_output("  ⚠️  DPM App: Not detected\n", "warning"))

                # Check UDP ports
                exit_code, stdout, stderr = self._run_adb_sync("netstat -anu | grep -E '(5001|5002)'")
                if exit_code == 0:
                    port_5001 = '5001' in stdout
                    port_5002 = '5002' in stdout

                    if port_5001:
                        self.after(0, lambda: self._append_output("  ✅ UDP Port 5001: Listening (Status broadcasts)\n", "success"))
                    else:
                        warnings_found.append("UDP port 5001 not listening")
                        self.after(0, lambda: self._append_output("  ⚠️  UDP Port 5001: NOT listening\n", "warning"))

                    if port_5002:
                        self.after(0, lambda: self._append_output("  ✅ UDP Port 5002: Listening (Heartbeat)\n", "success"))
                    else:
                        warnings_found.append("UDP port 5002 not listening")
                        self.after(0, lambda: self._append_output("  ⚠️  UDP Port 5002: NOT listening\n", "warning"))
                else:
                    warnings_found.append("Could not check UDP ports")

                # Check TCP connection to Air-Side
                exit_code, stdout, stderr = self._run_adb_sync("netstat -ant | grep 192.168.144.10:5000")
                if exit_code == 0 and "ESTABLISHED" in stdout:
                    self.after(0, lambda: self._append_output("  ✅ TCP Connection: ESTABLISHED to Air-Side:5000\n", "success"))
                else:
                    warnings_found.append("No active TCP connection to Air-Side port 5000")
                    self.after(0, lambda: self._append_output("  ⚠️  TCP Connection: Not connected to Air-Side:5000\n", "warning"))

                self.after(0, lambda: self._append_output("\n", None))

                # 5. Recent Errors
                self.after(0, lambda: self._append_output("📝 RECENT DPM ERRORS\n", "command"))

                exit_code, stdout, stderr = self._run_adb_sync("logcat -d | grep -E 'DPM|NetworkClient' | grep -E 'ERROR|FATAL' | tail -10")
                if exit_code == 0 and stdout.strip():
                    error_lines = [l for l in stdout.strip().split('\n') if l.strip()]
                    if error_lines:
                        warnings_found.append(f"{len(error_lines)} errors found in DPM logs")
                        self.after(0, lambda c=len(error_lines): self._append_output(f"  ⚠️  Found {c} recent errors in logs\n", "warning"))
                        for line in error_lines[:3]:  # Show first 3
                            self.after(0, lambda l=line: self._append_output(f"     {l[:80]}...\n", "info"))
                    else:
                        self.after(0, lambda: self._append_output("  ✅ No recent errors in DPM logs\n", "success"))
                else:
                    self.after(0, lambda: self._append_output("  ✅ No recent errors in DPM logs\n", "success"))

                self.after(0, lambda: self._append_output("\n", None))

                # 6. Resource Usage
                self.after(0, lambda: self._append_output("💾 RESOURCE USAGE\n", "command"))

                # Storage
                exit_code, stdout, stderr = self._run_adb_sync("df -h /data | tail -1")
                if exit_code == 0:
                    parts = stdout.strip().split()
                    if len(parts) >= 5:
                        try:
                            usage_pct = int(parts[4].rstrip('%'))
                            available = parts[3]
                            if usage_pct >= 90:
                                issues_found.append(f"Storage critically low: {usage_pct}% used")
                                self.after(0, lambda u=usage_pct, a=available: self._append_output(
                                    f"  ❌ Storage: {u}% used (CRITICAL - {a} free)\n", "error"))
                            elif usage_pct >= 80:
                                warnings_found.append(f"Storage running low: {usage_pct}% used")
                                self.after(0, lambda u=usage_pct, a=available: self._append_output(
                                    f"  ⚠️  Storage: {u}% used (LOW - {a} free)\n", "warning"))
                            else:
                                self.after(0, lambda u=usage_pct, a=available: self._append_output(
                                    f"  ✅ Storage: {u}% used ({a} free)\n", "success"))
                        except:
                            pass

                # Memory
                exit_code, stdout, stderr = self._run_adb_sync("cat /proc/meminfo | grep -E 'MemTotal|MemAvailable'")
                if exit_code == 0:
                    lines = stdout.strip().split('\n')
                    if len(lines) >= 2:
                        try:
                            total_kb = int([l for l in lines if 'MemTotal' in l][0].split()[1])
                            avail_kb = int([l for l in lines if 'MemAvailable' in l][0].split()[1])
                            usage_pct = ((total_kb - avail_kb) / total_kb) * 100

                            if usage_pct >= 90:
                                warnings_found.append(f"Memory usage high: {usage_pct:.0f}%")
                                self.after(0, lambda u=usage_pct: self._append_output(
                                    f"  ⚠️  Memory: {u:.0f}% used (HIGH)\n", "warning"))
                            else:
                                self.after(0, lambda u=usage_pct: self._append_output(
                                    f"  ✅ Memory: {u:.0f}% used\n", "success"))
                        except:
                            pass

                self.after(0, lambda: self._append_output("\n", None))

                # GENERATE SUMMARY
                self.after(0, lambda: self._append_output("=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("  DIAGNOSTIC SUMMARY\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n\n", "info"))

                # Calculate health score
                issues_weight = len(issues_found) * 20
                warnings_weight = len(warnings_found) * 10
                health_score = max(0, 100 - issues_weight - warnings_weight)

                # Display score
                if health_score >= 80:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ✅ EXCELLENT\n\n", "success"))
                elif health_score >= 60:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ⚠️  FAIR\n\n", "warning"))
                else:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ❌ POOR\n\n", "error"))

                # Display issues
                if issues_found:
                    self.after(0, lambda: self._append_output("  ❌ CRITICAL ISSUES FOUND:\n", "error"))
                    for issue in issues_found:
                        self.after(0, lambda i=issue: self._append_output(f"     • {i}\n", "error"))
                    self.after(0, lambda: self._append_output("\n", None))

                if warnings_found:
                    self.after(0, lambda: self._append_output("  ⚠️  WARNINGS:\n", "warning"))
                    for warning in warnings_found:
                        self.after(0, lambda w=warning: self._append_output(f"     • {w}\n", "warning"))
                    self.after(0, lambda: self._append_output("\n", None))

                if not issues_found and not warnings_found:
                    self.after(0, lambda: self._append_output("  ✅ No issues detected. H16 system is healthy!\n\n", "success"))

                # RECOMMENDATIONS
                if issues_found or warnings_found:
                    self.after(0, lambda: self._append_output("  💡 RECOMMENDATIONS:\n", "command"))

                    if any("unreachable" in i.lower() for i in issues_found):
                        self.after(0, lambda: self._append_output(
                            "     • Check Air-Side Pi is powered on and connected\n", "info"))
                        self.after(0, lambda: self._append_output(
                            "     • Verify VXLAN tunnel configuration\n", "info"))

                    if any("br-vxlan" in i.lower() for i in issues_found):
                        self.after(0, lambda: self._append_output(
                            "     • Restart H16 networking services\n", "info"))
                        self.after(0, lambda: self._append_output(
                            "     • Check H16 network configuration\n", "info"))

                    if any("storage" in w.lower() for w in warnings_found + issues_found):
                        self.after(0, lambda: self._append_output(
                            "     • Clear app caches and old log files\n", "info"))
                        self.after(0, lambda: self._append_output(
                            "     • Remove unused apps or media\n", "info"))

                    if any("battery" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Charge H16 battery before continuing\n", "info"))

                    if any("latency" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Check WiFi signal strength\n", "info"))
                        self.after(0, lambda: self._append_output(
                            "     • Reduce network congestion\n", "info"))

                    if any("udp" in w.lower() or "tcp" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Restart DPM application on H16\n", "info"))
                        self.after(0, lambda: self._append_output(
                            "     • Verify DPM app has network permissions\n", "info"))

                    if any("error" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Check DPM app logs in Logcat tab for details\n", "info"))

                self.after(0, lambda: self._append_output("\n" + "=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("Smart Diagnostic complete!\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n", "info"))

                # Update status
                self.after(0, lambda: self.status_label.config(text="Smart Diagnostic completed"))
                self.after(0, lambda: self.smart_diagnostic_btn.config(state=tk.NORMAL))

            except Exception as e:
                logger.exception(f"Error running smart diagnostic: {e}")
                self.after(0, lambda e=e: self._append_output(f"\n❌ Diagnostic failed: {str(e)}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Diagnostic failed"))
                self.after(0, lambda: self.smart_diagnostic_btn.config(state=tk.NORMAL))

        threading.Thread(target=run_diagnostics, daemon=True).start()

    def _run_adb_sync(self, shell_command: str, timeout=10):
        """Run ADB command synchronously and return results"""
        try:
            result = subprocess.run(
                ['adb', 'shell', shell_command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    def _run_full_diagnostic(self):
        """Run comprehensive system diagnostic"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  H16 FULL SYSTEM DIAGNOSTIC\n", "command")
        self._append_output("  Based on Cheat_Sheet_ADB_LOG_ANALYSIS.md\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        diagnostics = [
            ("1. Check br-vxlan Interface", "ip addr show br-vxlan | grep inet"),
            ("2. Ping Air-Side Pi (.10)", "ping -c 4 192.168.144.10"),
            ("3. Check DPM Ports", "netstat -an | grep -E '(5000|5001|5002)'"),
            ("4. Check VXLAN Tunnel", "ip -d link show vxlan1"),
            ("5. Check Route to Air-Side", "ip route get 192.168.144.10"),
            ("6. Recent DPM Errors", "logcat -d | grep -E 'DPM|NetworkClient' | grep ERROR | tail -20"),
        ]

        self._run_diagnostic_sequence(diagnostics)

    def _run_network_diagnostic(self):
        """Run network-specific diagnostic"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  H16 NETWORK HEALTH CHECK\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        diagnostics = [
            ("Network Interfaces", "ip addr show"),
            ("Routing Table", "ip route show"),
            ("VXLAN Tunnel Status", "ip -d link show vxlan1"),
            ("Bridge Configuration", "bridge link show"),
            ("WiFi Status", "dumpsys wifi | grep -E 'SSID|RSSI'"),
        ]

        self._run_diagnostic_sequence(diagnostics)

    def _run_airside_connectivity(self):
        """Run Air-Side connectivity tests"""
        if not self.adb_connected:
            messagebox.showwarning("Not Connected", "Please connect to H16 via ADB first")
            return

        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  AIR-SIDE CONNECTIVITY TEST\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        diagnostics = [
            ("Raspberry Pi Air-Side (192.168.144.10)", "ping -c 4 192.168.144.10"),
            ("Check Route to Air-Side", "ip route get 192.168.144.10"),
            ("Test TCP Port 5000", "nc -zv 192.168.144.10 5000 2>&1 || echo 'Port test complete'"),
            ("Check Active Connections to Air-Side", "netstat -an | grep 192.168.144.10"),
            ("Recent Connection Logs", "logcat -d | grep -E '192.168.144|Connection' | tail -10"),
        ]

        self._run_diagnostic_sequence(diagnostics)

    def _run_diagnostic_sequence(self, diagnostics):
        """Run sequence of diagnostic commands"""
        def run_sequence():
            for i, (name, command) in enumerate(diagnostics, 1):
                self.after(0, lambda n=name: self._append_output(f"\n{n}:\n", "command"))

                try:
                    result = subprocess.run(
                        ['adb', 'shell', command],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )

                    output = result.stdout
                    if result.returncode == 0:
                        self.after(0, lambda o=output: self._append_output(o + "\n", "success"))
                    else:
                        self.after(0, lambda o=output: self._append_output(o + "\n", "warning"))

                except Exception as e:
                    self.after(0, lambda e=e: self._append_output(f"ERROR: {str(e)}\n", "error"))

            self.after(0, lambda: self._append_output("\n" + "=" * 80 + "\n", "info"))
            self.after(0, lambda: self._append_output("Diagnostic complete!\n", "command"))
            self.after(0, lambda: self.status_label.config(text="Diagnostic complete"))

        self.status_label.config(text="Running diagnostic sequence...")
        threading.Thread(target=run_sequence, daemon=True).start()

    def _append_output(self, text: str, tag: Optional[str] = None):
        """Append text to output display"""
        self.output_text.config(state=tk.NORMAL)
        if tag:
            self.output_text.insert(tk.END, text, tag)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _clear_output(self):
        """Clear output display"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _copy_output(self):
        """Copy output to clipboard"""
        try:
            output = self.output_text.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(output)
            self.update()
            messagebox.showinfo("Success", "Output copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            # Check if there's a selection
            if self.output_text.tag_ranges(tk.SEL):
                selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.update()
                messagebox.showinfo("Success", "Selected text copied to clipboard!")
            else:
                messagebox.showwarning("No Selection", "Please select text to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _save_report(self):
        """Save diagnostic report to file"""
        try:
            output = self.output_text.get(1.0, tk.END).strip()

            if not output:
                messagebox.showwarning("No Content", "No diagnostic output to save")
                return

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"h16_diagnostic_{timestamp}.txt"

            file_path = filedialog.asksaveasfilename(
                title="Save H16 Diagnostic Report",
                defaultextension=".txt",
                initialfile=default_filename,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)

                messagebox.showinfo("Success", f"Report saved successfully!\n\n{file_path}")
                logger.info("SYSTEM", f"H16 diagnostic report saved to: {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{e}")
            logger.exception(f"Error saving H16 diagnostic report: {e}")

    # Troubleshooting Methods

    def _troubleshoot_ping(self):
        """Test H16 reachability with ping"""
        self._clear_output()
        self._append_output("=== Testing H16 Connectivity (Ping) ===\n\n", "command")
        self.status_label.config(text="Pinging H16...")

        def run_ping():
            try:
                h16_ip = self.ip_entry.get()
                result = subprocess.run(
                    ["ping", h16_ip, "-n", "4"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                self.after(0, lambda: self._append_output(result.stdout, "info"))

                if result.returncode == 0:
                    self.after(0, lambda: self._append_output("\n✅ H16 is reachable!\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="Ping successful"))
                else:
                    self.after(0, lambda: self._append_output("\n❌ H16 is NOT reachable!\n", "error"))
                    self.after(0, lambda: self.status_label.config(text="Ping failed"))
            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Ping error"))

        threading.Thread(target=run_ping, daemon=True).start()

    def _troubleshoot_port(self):
        """Test if port 5555 is open on H16 using PowerShell"""
        self._clear_output()
        self._append_output("=== Testing ADB Port 5555 on H16 ===\n\n", "command")
        self.status_label.config(text="Testing port 5555...")

        def run_port_test():
            try:
                h16_ip = self.ip_entry.get()
                cmd = f'powershell "Test-NetConnection {h16_ip} -Port 5555"'

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=20
                )

                self.after(0, lambda: self._append_output(result.stdout, "info"))

                if "TcpTestSucceeded       : True" in result.stdout:
                    self.after(0, lambda: self._append_output("\n✅ Port 5555 is OPEN and accepting connections!\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="Port 5555 is open"))
                else:
                    self.after(0, lambda: self._append_output("\n❌ Port 5555 is CLOSED or unreachable!\n", "error"))
                    self.after(0, lambda: self._append_output("This could be:\n", "warning"))
                    self.after(0, lambda: self._append_output("  - ADB not running on H16\n", "info"))
                    self.after(0, lambda: self._append_output("  - Firewall blocking the connection\n", "info"))
                    self.after(0, lambda: self._append_output("  - H16 ADB set to USB only mode\n", "info"))
                    self.after(0, lambda: self.status_label.config(text="Port 5555 is closed"))
            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Port test error"))

        threading.Thread(target=run_port_test, daemon=True).start()

    def _troubleshoot_local_port(self):
        """Check if local port 5555 is in use"""
        self._clear_output()
        self._append_output("=== Checking Local Port 5555 Usage ===\n\n", "command")
        self.status_label.config(text="Checking local ports...")

        def run_local_check():
            try:
                result = subprocess.run(
                    ["netstat", "-an"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                lines = [line for line in result.stdout.split('\n') if ':5555' in line]

                if lines:
                    self.after(0, lambda: self._append_output("Port 5555 connections found:\n\n", "success"))
                    for line in lines:
                        self.after(0, lambda l=line: self._append_output(f"{l}\n", "info"))

                    established = [l for l in lines if 'ESTABLISHED' in l]
                    if established:
                        self.after(0, lambda: self._append_output(f"\n✅ {len(established)} ESTABLISHED connection(s) to port 5555\n", "success"))
                    else:
                        self.after(0, lambda: self._append_output("\n⚠️  Port 5555 connections exist but none are ESTABLISHED\n", "warning"))
                else:
                    self.after(0, lambda: self._append_output("❌ No connections found on port 5555\n", "error"))
                    self.after(0, lambda: self._append_output("\nThis means ADB is not connected to any device on this port.\n", "info"))

                self.after(0, lambda: self.status_label.config(text="Port check complete"))
            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Port check error"))

        threading.Thread(target=run_local_check, daemon=True).start()

    def _troubleshoot_adb_server(self):
        """Check if ADB server is running"""
        self._clear_output()
        self._append_output("=== Checking ADB Server Status ===\n\n", "command")
        self.status_label.config(text="Checking ADB server...")

        def run_server_check():
            try:
                # Check if port 5037 is listening (ADB server port)
                result = subprocess.run(
                    ["netstat", "-an"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                adb_server_found = False
                for line in result.stdout.split('\n'):
                    if ':5037' in line and 'LISTENING' in line:
                        adb_server_found = True
                        self.after(0, lambda l=line: self._append_output(f"ADB Server port:\n{l}\n\n", "info"))
                        break

                if adb_server_found:
                    self.after(0, lambda: self._append_output("✅ ADB server is RUNNING (port 5037 listening)\n", "success"))

                    # Check ADB version
                    version_result = subprocess.run(
                        ["adb", "version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if version_result.returncode == 0:
                        self.after(0, lambda: self._append_output(f"\n{version_result.stdout}", "info"))
                else:
                    self.after(0, lambda: self._append_output("❌ ADB server is NOT running!\n", "error"))
                    self.after(0, lambda: self._append_output("\nTry: Click 'Start ADB Server' button\n", "info"))

                self.after(0, lambda: self.status_label.config(text="ADB server check complete"))
            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Server check error"))

        threading.Thread(target=run_server_check, daemon=True).start()

    def _troubleshoot_reconnect(self):
        """Quick reconnect to H16"""
        self._clear_output()
        self._append_output("=== Quick ADB Reconnect ===\n\n", "command")
        self.status_label.config(text="Reconnecting...")

        def run_reconnect():
            try:
                h16_ip = self.ip_entry.get()
                h16_port = self.port_entry.get()
                device_addr = f"{h16_ip}:{h16_port}"

                # Disconnect
                self.after(0, lambda: self._append_output("Disconnecting...\n", "info"))
                subprocess.run(["adb", "disconnect", device_addr], capture_output=True, timeout=5)

                # Wait briefly
                import time
                time.sleep(1)

                # Reconnect
                self.after(0, lambda: self._append_output(f"Connecting to {device_addr}...\n", "info"))
                result = subprocess.run(
                    ["adb", "connect", device_addr],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                self.after(0, lambda: self._append_output(f"{result.stdout}\n", "info"))

                # Check devices
                self.after(0, lambda: self._append_output("\nChecking devices...\n", "info"))
                devices_result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                self.after(0, lambda: self._append_output(f"{devices_result.stdout}\n", "info"))

                if "device" in devices_result.stdout and device_addr in devices_result.stdout:
                    self.after(0, lambda: self._append_output("\n✅ Reconnect successful!\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="Reconnected successfully"))
                else:
                    self.after(0, lambda: self._append_output("\n❌ Reconnect failed!\n", "error"))
                    self.after(0, lambda: self.status_label.config(text="Reconnect failed"))

            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Reconnect error"))

        threading.Thread(target=run_reconnect, daemon=True).start()

    def _troubleshoot_kill_server(self):
        """Kill ADB server"""
        self._clear_output()
        self._append_output("=== Killing ADB Server ===\n\n", "command")
        self.status_label.config(text="Killing ADB server...")

        def run_kill():
            try:
                result = subprocess.run(
                    ["adb", "kill-server"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                self.after(0, lambda: self._append_output("ADB server killed.\n", "success"))
                self.after(0, lambda: self._append_output("\nNote: Server will auto-start on next ADB command.\n", "info"))
                self.after(0, lambda: self.status_label.config(text="ADB server killed"))

            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Kill server error"))

        threading.Thread(target=run_kill, daemon=True).start()

    def _troubleshoot_start_server(self):
        """Start ADB server"""
        self._clear_output()
        self._append_output("=== Starting ADB Server ===\n\n", "command")
        self.status_label.config(text="Starting ADB server...")

        def run_start():
            try:
                result = subprocess.run(
                    ["adb", "start-server"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                self.after(0, lambda: self._append_output(f"{result.stdout}\n", "info"))

                if result.returncode == 0:
                    self.after(0, lambda: self._append_output("\n✅ ADB server started successfully!\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="ADB server started"))
                else:
                    self.after(0, lambda: self._append_output(f"\n❌ Failed to start server:\n{result.stderr}\n", "error"))
                    self.after(0, lambda: self.status_label.config(text="Start server failed"))

            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Start server error"))

        threading.Thread(target=run_start, daemon=True).start()

    def _troubleshoot_full_reset(self):
        """Full ADB reset and reconnect sequence"""
        self._clear_output()
        self._append_output("=== Full ADB Reset & Reconnect ===\n\n", "command")
        self.status_label.config(text="Running full ADB reset...")

        def run_full_reset():
            try:
                h16_ip = self.ip_entry.get()
                h16_port = self.port_entry.get()
                device_addr = f"{h16_ip}:{h16_port}"

                import time

                # Step 1: Disconnect all
                self.after(0, lambda: self._append_output("Step 1/4: Disconnecting all devices...\n", "info"))
                subprocess.run(["adb", "disconnect"], capture_output=True, timeout=5)
                time.sleep(0.5)

                # Step 2: Kill server
                self.after(0, lambda: self._append_output("Step 2/4: Killing ADB server...\n", "info"))
                subprocess.run(["adb", "kill-server"], capture_output=True, timeout=5)
                time.sleep(2)

                # Step 3: Start server
                self.after(0, lambda: self._append_output("Step 3/4: Starting ADB server...\n", "info"))
                result = subprocess.run(["adb", "start-server"], capture_output=True, text=True, timeout=10)
                self.after(0, lambda r=result: self._append_output(f"{r.stdout}\n", "info"))
                time.sleep(1)

                # Step 4: Connect to H16
                self.after(0, lambda: self._append_output(f"Step 4/4: Connecting to {device_addr}...\n", "info"))
                connect_result = subprocess.run(
                    ["adb", "connect", device_addr],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                self.after(0, lambda r=connect_result: self._append_output(f"{r.stdout}\n", "info"))
                time.sleep(1)

                # Check final status
                self.after(0, lambda: self._append_output("\nFinal Status:\n", "command"))
                devices_result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
                self.after(0, lambda r=devices_result: self._append_output(f"{r.stdout}\n", "info"))

                if "device" in devices_result.stdout and device_addr in devices_result.stdout and "offline" not in devices_result.stdout:
                    self.after(0, lambda: self._append_output("\n✅ Full reset successful! ADB connected.\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="Full reset successful"))
                else:
                    self.after(0, lambda: self._append_output("\n⚠️  Reset completed but connection may need attention.\n", "warning"))
                    self.after(0, lambda: self.status_label.config(text="Reset completed - check connection"))

            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Full reset error"))

        threading.Thread(target=run_full_reset, daemon=True).start()

    def _troubleshoot_complete_diagnostic(self):
        """Run complete troubleshooting diagnostic"""
        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  COMPLETE ADB TROUBLESHOOTING DIAGNOSTIC\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")
        self.status_label.config(text="Running complete diagnostic...")

        def run_complete():
            try:
                h16_ip = self.ip_entry.get()
                h16_port = self.port_entry.get()
                device_addr = f"{h16_ip}:{h16_port}"

                issues = []
                warnings = []

                # Test 1: Ping
                self.after(0, lambda: self._append_output("1. NETWORK CONNECTIVITY TEST\n", "command"))
                ping_result = subprocess.run(["ping", h16_ip, "-n", "2"], capture_output=True, text=True, timeout=10)
                if ping_result.returncode == 0:
                    self.after(0, lambda: self._append_output("   ✅ H16 is reachable via ping\n", "success"))
                else:
                    issues.append("H16 not reachable via ping")
                    self.after(0, lambda: self._append_output("   ❌ H16 is NOT reachable via ping\n", "error"))

                # Test 2: Port 5555
                self.after(0, lambda: self._append_output("\n2. ADB PORT TEST\n", "command"))
                try:
                    port_result = subprocess.run(
                        f'powershell "Test-NetConnection {h16_ip} -Port 5555 -InformationLevel Quiet"',
                        capture_output=True,
                        text=True,
                        shell=True,
                        timeout=15
                    )
                    if "True" in port_result.stdout:
                        self.after(0, lambda: self._append_output("   ✅ Port 5555 is open\n", "success"))
                    else:
                        issues.append("Port 5555 is closed")
                        self.after(0, lambda: self._append_output("   ❌ Port 5555 is closed or blocked\n", "error"))
                except:
                    warnings.append("Could not test port 5555")
                    self.after(0, lambda: self._append_output("   ⚠️  Could not test port\n", "warning"))

                # Test 3: ADB Server
                self.after(0, lambda: self._append_output("\n3. ADB SERVER STATUS\n", "command"))
                netstat_result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, timeout=5)
                if ':5037' in netstat_result.stdout and 'LISTENING' in netstat_result.stdout:
                    self.after(0, lambda: self._append_output("   ✅ ADB server is running\n", "success"))
                else:
                    issues.append("ADB server not running")
                    self.after(0, lambda: self._append_output("   ❌ ADB server is NOT running\n", "error"))

                # Test 4: ADB Devices
                self.after(0, lambda: self._append_output("\n4. ADB DEVICE CONNECTION\n", "command"))
                devices_result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
                self.after(0, lambda r=devices_result: self._append_output(f"   {r.stdout}\n", "info"))

                if device_addr in devices_result.stdout:
                    if "offline" in devices_result.stdout:
                        warnings.append("Device is offline")
                        self.after(0, lambda: self._append_output("   ⚠️  Device connected but OFFLINE\n", "warning"))
                    elif "device" in devices_result.stdout:
                        self.after(0, lambda: self._append_output("   ✅ Device connected and online\n", "success"))
                    else:
                        warnings.append("Device connection status unclear")
                        self.after(0, lambda: self._append_output("   ⚠️  Device connection unclear\n", "warning"))
                else:
                    issues.append("Device not in ADB devices list")
                    self.after(0, lambda: self._append_output("   ❌ Device NOT in ADB devices list\n", "error"))

                # Test 5: Local connections
                self.after(0, lambda: self._append_output("\n5. LOCAL PORT 5555 CONNECTIONS\n", "command"))
                port_lines = [l for l in netstat_result.stdout.split('\n') if ':5555' in l]
                if port_lines:
                    established = [l for l in port_lines if 'ESTABLISHED' in l]
                    self.after(0, lambda: self._append_output(f"   Found {len(port_lines)} connection(s), {len(established)} ESTABLISHED\n", "info"))
                    if established:
                        self.after(0, lambda: self._append_output("   ✅ Active connection on port 5555\n", "success"))
                    else:
                        warnings.append("Port 5555 connections exist but not established")
                        self.after(0, lambda: self._append_output("   ⚠️  Port 5555 connections not established\n", "warning"))
                else:
                    issues.append("No port 5555 connections")
                    self.after(0, lambda: self._append_output("   ❌ No connections on port 5555\n", "error"))

                # Summary
                self.after(0, lambda: self._append_output("\n" + "=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("DIAGNOSTIC SUMMARY\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n\n", "info"))

                if not issues and not warnings:
                    self.after(0, lambda: self._append_output("✅ All tests passed! ADB connection appears healthy.\n", "success"))
                    self.after(0, lambda: self.status_label.config(text="All tests passed"))
                else:
                    if issues:
                        self.after(0, lambda: self._append_output(f"❌ {len(issues)} ISSUE(S) FOUND:\n", "error"))
                        for issue in issues:
                            self.after(0, lambda i=issue: self._append_output(f"   • {i}\n", "error"))
                    if warnings:
                        self.after(0, lambda: self._append_output(f"\n⚠️  {len(warnings)} WARNING(S):\n", "warning"))
                        for warning in warnings:
                            self.after(0, lambda w=warning: self._append_output(f"   • {w}\n", "warning"))

                    self.after(0, lambda: self._append_output("\nRECOMMENDATIONS:\n", "command"))
                    if "H16 not reachable" in str(issues):
                        self.after(0, lambda: self._append_output("   • Check H16 is powered on and on the same network\n", "info"))
                    if "Port 5555 is closed" in str(issues):
                        self.after(0, lambda: self._append_output("   • Enable 'ADB over Network' in H16 Developer Options\n", "info"))
                    if "ADB server not running" in str(issues):
                        self.after(0, lambda: self._append_output("   • Click 'Start ADB Server' button\n", "info"))
                    if "Device not in ADB devices list" in str(issues) or "Device is offline" in str(warnings):
                        self.after(0, lambda: self._append_output("   • Click 'Full ADB Reset & Reconnect' button\n", "info"))

                    self.after(0, lambda: self.status_label.config(text="Diagnostic complete - issues found"))

            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Diagnostic error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Diagnostic error"))

        threading.Thread(target=run_complete, daemon=True).start()

    def _troubleshoot_h16_diagnostics(self):
        """Run H16-side diagnostics via ADB shell"""
        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  H16-SIDE DIAGNOSTIC REPORT (via ADB Shell)\n", "command")
        self._append_output("  Running diagnostics directly on H16 Android device\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")
        self.status_label.config(text="Running H16-side diagnostics...")

        def run_h16_diagnostics():
            try:
                h16_ip = self.ip_entry.get()
                h16_port = self.port_entry.get()
                device_addr = f"{h16_ip}:{h16_port}"

                # First check if ADB is connected
                devices_result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
                if device_addr not in devices_result.stdout or "offline" in devices_result.stdout:
                    self.after(0, lambda: self._append_output("❌ ADB not connected to H16!\n", "error"))
                    self.after(0, lambda: self._append_output("\nPlease connect ADB first using 'Full ADB Reset & Reconnect' button.\n", "warning"))
                    self.after(0, lambda: self.status_label.config(text="ADB not connected"))
                    return

                # Test 1: Check adbd status
                self.after(0, lambda: self._append_output("1. CHECKING ADB DAEMON (adbd)\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "ps -A | grep adbd"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.after(0, lambda: self._append_output("   ✅ adbd is running\n", "success"))
                    self.after(0, lambda r=result: self._append_output(f"   {r.stdout.strip()}\n", "info"))
                else:
                    self.after(0, lambda: self._append_output("   ⚠️  adbd status unclear\n", "warning"))

                # Test 2: Check network interfaces
                self.after(0, lambda: self._append_output("\n2. NETWORK INTERFACES\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "ip addr show | grep 'inet 10.0.1'"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.after(0, lambda: self._append_output("   ✅ Network interface found\n", "success"))
                    for line in result.stdout.strip().split('\n'):
                        self.after(0, lambda l=line: self._append_output(f"   {l}\n", "info"))
                else:
                    self.after(0, lambda: self._append_output("   ⚠️  Could not get network info\n", "warning"))

                # Test 3: Check port 5555 status
                self.after(0, lambda: self._append_output("\n3. PORT 5555 STATUS\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "netstat -anp 2>/dev/null | grep 5555"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.after(0, lambda: self._append_output("   ✅ Port 5555 found\n", "success"))
                    for line in result.stdout.strip().split('\n')[:5]:  # Limit to 5 lines
                        self.after(0, lambda l=line: self._append_output(f"   {l}\n", "info"))

                    # Check for ESTABLISHED connections
                    if "ESTABLISHED" in result.stdout:
                        self.after(0, lambda: self._append_output("   ✅ Has ESTABLISHED connection(s)\n", "success"))
                    else:
                        self.after(0, lambda: self._append_output("   ⚠️  No ESTABLISHED connections\n", "warning"))
                else:
                    self.after(0, lambda: self._append_output("   ❌ Port 5555 not in use\n", "error"))

                # Test 4: Check ADB TCP port setting
                self.after(0, lambda: self._append_output("\n4. ADB TCP PORT SETTING\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "getprop service.adb.tcp.port"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    port = result.stdout.strip()
                    if port == "5555":
                        self.after(0, lambda p=port: self._append_output(f"   ✅ ADB over network ENABLED (port {p})\n", "success"))
                    elif port == "-1":
                        self.after(0, lambda: self._append_output("   ❌ ADB over network DISABLED (USB only mode)\n", "error"))
                    else:
                        self.after(0, lambda p=port: self._append_output(f"   ⚠️  ADB port set to {p}\n", "warning"))

                # Test 5: Check ADB daemon service status
                self.after(0, lambda: self._append_output("\n5. ADB DAEMON SERVICE\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "getprop init.svc.adbd"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    status = result.stdout.strip()
                    if status == "running":
                        self.after(0, lambda: self._append_output("   ✅ adbd service is running\n", "success"))
                    else:
                        self.after(0, lambda s=status: self._append_output(f"   ⚠️  adbd service is {s}\n", "warning"))

                # Test 6: Check Developer Options
                self.after(0, lambda: self._append_output("\n6. DEVELOPER OPTIONS\n", "command"))

                # Check each setting
                settings_to_check = [
                    ("development_settings_enabled", "Developer Options"),
                    ("adb_enabled", "USB Debugging"),
                    ("adb_wifi_enabled", "ADB WiFi")
                ]

                for setting, name in settings_to_check:
                    result = subprocess.run(
                        ["adb", "-s", device_addr, "shell", f"settings get global {setting}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        value = result.stdout.strip()
                        if value == "1":
                            self.after(0, lambda n=name: self._append_output(f"   ✅ {n}: Enabled\n", "success"))
                        elif value == "0":
                            self.after(0, lambda n=name: self._append_output(f"   ❌ {n}: Disabled\n", "error"))
                        else:
                            self.after(0, lambda n=name, v=value: self._append_output(f"   ⚠️  {n}: {v}\n", "warning"))

                # Test 7: Ping PC from H16
                self.after(0, lambda: self._append_output("\n7. CONNECTIVITY TEST (H16 → PC)\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "ping -c 2 10.0.1.37 2>/dev/null"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and "0% packet loss" in result.stdout:
                    self.after(0, lambda: self._append_output("   ✅ H16 can reach PC (10.0.1.37)\n", "success"))
                else:
                    self.after(0, lambda: self._append_output("   ⚠️  H16 cannot ping PC or network issue\n", "warning"))

                # Test 8: Check DPM app status
                self.after(0, lambda: self._append_output("\n8. DPM APP STATUS\n", "command"))
                result = subprocess.run(
                    ["adb", "-s", device_addr, "shell", "pidof com.uksystems.payloadmanager"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    pid = result.stdout.strip()
                    self.after(0, lambda p=pid: self._append_output(f"   ✅ DPM app is running (PID: {p})\n", "success"))
                else:
                    self.after(0, lambda: self._append_output("   ❌ DPM app is NOT running\n", "error"))

                # Summary
                self.after(0, lambda: self._append_output("\n" + "=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("H16-SIDE DIAGNOSTIC COMPLETE\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("\nThis diagnostic ran commands directly on H16 via 'adb shell'\n", "info"))
                self.after(0, lambda: self._append_output("If issues found, try fixing on H16 side using Termux commands\n", "info"))
                self.after(0, lambda: self.status_label.config(text="H16 diagnostic complete"))

            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._append_output("\n❌ Diagnostic timed out\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Diagnostic timeout"))
            except Exception as e:
                self.after(0, lambda: self._append_output(f"\n❌ Diagnostic error: {e}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Diagnostic error"))

        threading.Thread(target=run_h16_diagnostics, daemon=True).start()

    def _troubleshoot_generate_termux_script(self):
        """Generate H16 diagnostic script for manual execution in Termux"""
        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  H16 TERMUX DIAGNOSTIC SCRIPT\n", "command")
        self._append_output("  Copy and paste this into Termux on H16\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        script = '''#!/bin/bash
# H16 ADB Diagnostic Script
# Run this in Termux on H16 to diagnose ADB issues

echo "======================================"
echo "H16 ADB Diagnostic Report"
echo "======================================"

echo -e "\\n1. ADB Daemon Status:"
ps -A | grep adbd || echo "  [!] adbd not running!"

echo -e "\\n2. Network Interfaces:"
ip addr show | grep -E "inet |wlan0|eth0"

echo -e "\\n3. Port 5555 Status:"
netstat -anp 2>/dev/null | grep 5555 || echo "  [!] Port 5555 not in use!"

echo -e "\\n4. ADB TCP Port Setting:"
PORT=$(getprop service.adb.tcp.port)
if [ "$PORT" = "5555" ]; then
  echo "  [✓] ADB over network enabled (port $PORT)"
else
  echo "  [!] ADB over network DISABLED (port $PORT)"
fi

echo -e "\\n5. ADB Daemon Service:"
STATUS=$(getprop init.svc.adbd)
if [ "$STATUS" = "running" ]; then
  echo "  [✓] adbd is running"
else
  echo "  [!] adbd is $STATUS"
fi

echo -e "\\n6. Developer Settings:"
DEV=$(settings get global development_settings_enabled)
ADB=$(settings get global adb_enabled)
WIFI=$(settings get global adb_wifi_enabled)
echo "  Developer Options: $DEV (1=enabled, 0=disabled)"
echo "  USB Debugging: $ADB (1=enabled, 0=disabled)"
echo "  ADB WiFi: $WIFI (1=enabled, 0=disabled)"

echo -e "\\n7. Test Ping to PC (10.0.1.37):"
ping -c 2 10.0.1.37 2>/dev/null && echo "  [✓] PC reachable" || echo "  [!] PC unreachable"

echo -e "\\n8. Active Connections:"
netstat -ant 2>/dev/null | grep ESTABLISHED | head -5

echo -e "\\n9. DPM App Status:"
if pidof com.uksystems.payloadmanager > /dev/null; then
  echo "  [✓] DPM app is running"
else
  echo "  [!] DPM app is NOT running"
fi

echo -e "\\n======================================"
echo "Diagnostic Complete"
echo "======================================"

echo -e "\\n--- QUICK FIXES ---"
echo "To enable ADB over network:"
echo "  settings put global adb_enabled 1"
echo "  settings put global adb_wifi_enabled 1"
echo ""
echo "To restart ADB:"
echo "  settings put global adb_wifi_enabled 0"
echo "  sleep 2"
echo "  settings put global adb_wifi_enabled 1"
'''

        self._append_output(script, "info")

        self._append_output("\n\n" + "=" * 80 + "\n", "info")
        self._append_output("HOW TO USE:\n", "command")
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("1. Select all text above (Ctrl+A in output window or use 'Copy Output' button)\n", "info")
        self._append_output("2. Copy to clipboard (Ctrl+C)\n", "info")
        self._append_output("3. On H16, open Termux app\n", "info")
        self._append_output("4. Paste and run: bash <(cat)\n", "info")
        self._append_output("5. Paste the script, then press Ctrl+D\n", "info")
        self._append_output("\nOr save to file and run:\n", "warning")
        self._append_output("1. In Termux: nano h16-diag.sh\n", "info")
        self._append_output("2. Paste the script\n", "info")
        self._append_output("3. Save with Ctrl+X, Y, Enter\n", "info")
        self._append_output("4. Make executable: chmod +x h16-diag.sh\n", "info")
        self._append_output("5. Run: ./h16-diag.sh\n", "info")

        self.status_label.config(text="Termux script generated - ready to copy")

    # Protocol Diagnostics Methods

    def _protocol_ping_h16(self):
        """Ping H16 via protocol"""
        self._append_output("\n🏓 Pinging H16 via protocol...\n", "command")

        def ping_thread():
            try:
                start_time = time.time()
                result = self.diagnostic_client.ping_h16()
                elapsed_ms = (time.time() - start_time) * 1000

                if result:
                    self.after(0, lambda: self._append_output(f"✅ H16 is alive and responding ({elapsed_ms:.0f}ms)\n", "success"))
                else:
                    self.after(0, lambda: self._append_output("❌ H16 not responding\n", "error"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"❌ Error: {e}\n", "error"))

        threading.Thread(target=ping_thread, daemon=True).start()

    def _protocol_get_system_info(self):
        """Get H16 system information via protocol"""
        self._append_output("\n📊 Querying H16 system info...\n", "command")

        def get_info_thread():
            try:
                response = self.diagnostic_client.get_system_info()

                if response['success']:
                    data = response['data']
                    self.last_system_info = data

                    # Display results
                    self.after(0, lambda: self._append_output("✅ System Info Retrieved:\n", "success"))
                    self.after(0, lambda: self._append_output(f"  Battery: {data.get('battery_percent', 'N/A')}%\n", "info"))
                    self.after(0, lambda: self._append_output(f"  CPU Usage: {data.get('cpu_usage_percent', 'N/A')}%\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Memory: {data.get('memory_available_mb', 'N/A')} MB / {data.get('memory_total_mb', 'N/A')} MB available\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Storage: {data.get('storage_available_gb', 'N/A')} GB / {data.get('storage_total_gb', 'N/A')} GB available\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Uptime: {self._format_uptime(data.get('uptime_seconds', 0))}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Android: {data.get('android_version', 'N/A')}\n", "info"))

                    # Update System Health panel
                    self.after(0, lambda: self._update_system_health_panel(data))
                else:
                    error_msg = response.get('error_message', 'Unknown error')
                    self.after(0, lambda e=error_msg: self._append_output(f"❌ Error: {e}\n", "error"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"❌ Exception: {e}\n", "error"))

        threading.Thread(target=get_info_thread, daemon=True).start()

    def _protocol_get_app_status(self):
        """Get H16 app status via protocol"""
        self._append_output("\n📱 Querying H16 app status...\n", "command")

        def get_app_thread():
            try:
                response = self.diagnostic_client.get_app_status()

                if response['success']:
                    data = response['data']
                    self.last_app_status = data

                    # Display results
                    self.after(0, lambda: self._append_output("✅ App Status Retrieved:\n", "success"))
                    self.after(0, lambda: self._append_output(f"  App Running: {data.get('app_running', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Version: {data.get('app_version', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  State: {data.get('app_state', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  PID: {data.get('pid', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Uptime: {self._format_uptime(data.get('uptime_seconds', 0))}\n", "info"))

                    connections = data.get('active_connections', {})
                    self.after(0, lambda: self._append_output(f"  Air-Side Connected: {connections.get('air_side_connected', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Camera Connected: {connections.get('camera_connected', 'N/A')}\n", "info"))
                    self.after(0, lambda: self._append_output(f"  Gimbal Connected: {connections.get('gimbal_connected', 'N/A')}\n", "info"))

                    self.after(0, lambda: self._append_output(f"  Memory Usage: {data.get('memory_usage_mb', 'N/A')} MB\n", "info"))
                else:
                    error_msg = response.get('error_message', 'Unknown error')
                    self.after(0, lambda e=error_msg: self._append_output(f"❌ Error: {e}\n", "error"))
            except Exception as e:
                self.after(0, lambda e=e: self._append_output(f"❌ Exception: {e}\n", "error"))

        threading.Thread(target=get_app_thread, daemon=True).start()

    def _protocol_run_full_diagnostics(self):
        """Run all diagnostic commands"""
        self._append_output("\n🔍 Running full H16 diagnostics...\n\n", "command")

        # Run all diagnostics in sequence
        self._protocol_ping_h16()
        self.after(1000, self._protocol_get_system_info)
        self.after(2000, self._protocol_get_app_status)
        self.after(3000, lambda: self._append_output("\n✅ Full diagnostics complete\n", "success"))

    def _update_system_health_panel(self, data):
        """Update System Health panel with diagnostic data"""
        # Battery (color-coded)
        battery = data.get('battery_percent', -1)
        if battery >= 0:
            battery_text = f"{battery}%"
            if battery > 50:
                battery_color = "green"
            elif battery > 20:
                battery_color = "orange"
            else:
                battery_color = "red"
            self.diag_battery_label.config(text=battery_text, foreground=battery_color)

        # CPU Usage
        cpu = data.get('cpu_usage_percent', -1)
        if cpu >= 0:
            self.diag_cpu_label.config(text=f"{cpu:.1f}%", foreground="blue")

        # Memory
        mem_avail = data.get('memory_available_mb', -1)
        mem_total = data.get('memory_total_mb', -1)
        if mem_avail >= 0 and mem_total > 0:
            mem_percent = (mem_avail / mem_total) * 100
            mem_text = f"{mem_avail} MB / {mem_total} MB ({mem_percent:.0f}% free)"
            mem_color = "green" if mem_percent > 20 else "orange"
            self.diag_memory_label.config(text=mem_text, foreground=mem_color)

        # Storage
        stor_avail = data.get('storage_available_gb', -1)
        stor_total = data.get('storage_total_gb', -1)
        if stor_avail >= 0 and stor_total > 0:
            stor_percent = (stor_avail / stor_total) * 100
            stor_text = f"{stor_avail:.1f} GB / {stor_total:.1f} GB ({stor_percent:.0f}% free)"
            stor_color = "green" if stor_percent > 10 else "orange"
            self.diag_storage_label.config(text=stor_text, foreground=stor_color)

        # Uptime
        uptime = data.get('uptime_seconds', 0)
        if uptime > 0:
            self.diag_uptime_label.config(text=self._format_uptime(uptime), foreground="blue")

        # Last Updated
        now = datetime.now().strftime("%H:%M:%S")
        self.diag_updated_label.config(text=now, foreground="green")

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh of diagnostics"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.auto_refresh_enabled:
            self._append_output("🔄 Auto-refresh enabled (5 seconds)\n", "info")
            self._auto_refresh_loop()
        else:
            self._append_output("⏸️  Auto-refresh disabled\n", "info")

    def _auto_refresh_loop(self):
        """Auto-refresh loop for diagnostics"""
        if not self.auto_refresh_enabled:
            return

        # Refresh system info
        def refresh_thread():
            try:
                response = self.diagnostic_client.get_system_info()
                if response['success']:
                    self.after(0, lambda d=response['data']: self._update_system_health_panel(d))
            except:
                pass  # Silent fail for auto-refresh

        threading.Thread(target=refresh_thread, daemon=True).start()

        # Schedule next refresh
        self.after(5000, self._auto_refresh_loop)

    def _format_uptime(self, seconds):
        """Format uptime seconds as human-readable string"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
