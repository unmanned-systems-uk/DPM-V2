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

from utils.logger import logger
from utils.config import config


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

        logger.debug("H16 Diagnostics tab initialized")

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
                logger.info("ADB is available")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("ADB not found in PATH")
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
            logger.info(f"ADB connected to {ip}:{port}")
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
                logger.info(f"H16 diagnostic report saved to: {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{e}")
            logger.exception(f"Error saving H16 diagnostic report: {e}")
