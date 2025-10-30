"""
System Monitor Tab for DPM Diagnostic Tool
Real-time Air-Side system resource monitoring
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from utils.logger import logger
from version import get_version_string, get_full_version_info


class SystemMonitorTab(ttk.Frame):
    """System Monitor tab - real-time system resource monitoring"""

    def __init__(self, parent):
        super().__init__(parent)

        self.system_data = {}
        self.auto_refresh_enabled = False
        self.refresh_interval = 5000  # ms

        self._create_ui()

        logger.debug("System Monitor tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: System info
        info_frame = ttk.LabelFrame(self, text="System Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        # Uptime
        uptime_row = ttk.Frame(info_frame)
        uptime_row.pack(fill=tk.X, pady=5)

        ttk.Label(uptime_row, text="Uptime:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.uptime_label = ttk.Label(uptime_row, text="N/A", font=('Arial', 10, 'bold'))
        self.uptime_label.pack(side=tk.LEFT, padx=5)

        # Hostname
        hostname_row = ttk.Frame(info_frame)
        hostname_row.pack(fill=tk.X, pady=5)

        ttk.Label(hostname_row, text="Hostname:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.hostname_label = ttk.Label(hostname_row, text="N/A", font=('Arial', 10))
        self.hostname_label.pack(side=tk.LEFT, padx=5)

        # Resource usage
        resources_frame = ttk.LabelFrame(self, text="Resource Usage", padding=10)
        resources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # CPU Usage
        cpu_frame = ttk.LabelFrame(resources_frame, text="CPU Usage", padding=10)
        cpu_frame.pack(fill=tk.X, pady=5)

        cpu_bar_frame = ttk.Frame(cpu_frame)
        cpu_bar_frame.pack(fill=tk.X, pady=5)

        self.cpu_var = tk.DoubleVar(value=0.0)
        self.cpu_progress = ttk.Progressbar(cpu_bar_frame, variable=self.cpu_var,
                                           maximum=100, length=400, mode='determinate')
        self.cpu_progress.pack(side=tk.LEFT, padx=5)

        self.cpu_label = ttk.Label(cpu_bar_frame, text="0.0%", font=('Arial', 11, 'bold'))
        self.cpu_label.pack(side=tk.LEFT, padx=10)

        # Memory Usage
        mem_frame = ttk.LabelFrame(resources_frame, text="Memory Usage", padding=10)
        mem_frame.pack(fill=tk.X, pady=5)

        mem_bar_frame = ttk.Frame(mem_frame)
        mem_bar_frame.pack(fill=tk.X, pady=5)

        self.mem_var = tk.DoubleVar(value=0.0)
        self.mem_progress = ttk.Progressbar(mem_bar_frame, variable=self.mem_var,
                                           maximum=100, length=400, mode='determinate')
        self.mem_progress.pack(side=tk.LEFT, padx=5)

        self.mem_label = ttk.Label(mem_bar_frame, text="0.0%", font=('Arial', 11, 'bold'))
        self.mem_label.pack(side=tk.LEFT, padx=10)

        # Memory details
        mem_detail_frame = ttk.Frame(mem_frame)
        mem_detail_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mem_detail_frame, text="Used:").pack(side=tk.LEFT, padx=5)
        self.mem_used_label = ttk.Label(mem_detail_frame, text="N/A MB")
        self.mem_used_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(mem_detail_frame, text="Total:").pack(side=tk.LEFT, padx=(20, 5))
        self.mem_total_label = ttk.Label(mem_detail_frame, text="N/A MB")
        self.mem_total_label.pack(side=tk.LEFT, padx=5)

        # Storage (Disk) Usage
        storage_frame = ttk.LabelFrame(resources_frame, text="Storage (Disk)", padding=10)
        storage_frame.pack(fill=tk.X, pady=5)

        storage_bar_frame = ttk.Frame(storage_frame)
        storage_bar_frame.pack(fill=tk.X, pady=5)

        self.storage_var = tk.DoubleVar(value=0.0)
        self.storage_progress = ttk.Progressbar(storage_bar_frame, variable=self.storage_var,
                                               maximum=100, length=400, mode='determinate')
        self.storage_progress.pack(side=tk.LEFT, padx=5)

        self.storage_label = ttk.Label(storage_bar_frame, text="0.0%", font=('Arial', 11, 'bold'))
        self.storage_label.pack(side=tk.LEFT, padx=10)

        # Storage details
        storage_detail_frame = ttk.Frame(storage_frame)
        storage_detail_frame.pack(fill=tk.X, pady=5)

        ttk.Label(storage_detail_frame, text="Free:").pack(side=tk.LEFT, padx=5)
        self.storage_free_label = ttk.Label(storage_detail_frame, text="N/A GB", foreground="green")
        self.storage_free_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(storage_detail_frame, text="Total:").pack(side=tk.LEFT, padx=(20, 5))
        self.storage_total_label = ttk.Label(storage_detail_frame, text="N/A GB")
        self.storage_total_label.pack(side=tk.LEFT, padx=5)

        # Application Version Info
        version_frame = ttk.LabelFrame(resources_frame, text="Application Version", padding=10)
        version_frame.pack(fill=tk.X, pady=5)

        version_info = get_full_version_info()

        # Version and build date
        version_row = ttk.Frame(version_frame)
        version_row.pack(fill=tk.X, pady=2)

        ttk.Label(version_row, text="Version:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(version_row, text=version_info['version'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        ttk.Label(version_row, text="Build Date:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Label(version_row, text=version_info['build_date'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        # Protocol version and build time
        protocol_row = ttk.Frame(version_frame)
        protocol_row.pack(fill=tk.X, pady=2)

        ttk.Label(protocol_row, text="Protocol:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(protocol_row, text=f"v{version_info['protocol_version']}", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        ttk.Label(protocol_row, text="Build Time:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Label(protocol_row, text=version_info['build_datetime'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        # Bottom: Controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Refresh button
        ttk.Button(control_frame, text="Refresh", command=self._manual_refresh).pack(side=tk.LEFT, padx=5)

        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Auto-refresh",
                       variable=self.auto_refresh_var,
                       command=self._toggle_auto_refresh).pack(side=tk.LEFT, padx=5)

        # Refresh interval
        ttk.Label(control_frame, text="Interval (sec):").pack(side=tk.LEFT, padx=(20, 5))
        self.interval_var = tk.IntVar(value=5)
        interval_spin = ttk.Spinbox(control_frame, from_=1, to=60, textvariable=self.interval_var,
                                   width=5, command=self._update_refresh_interval)
        interval_spin.pack(side=tk.LEFT, padx=5)

        # Last update time
        ttk.Label(control_frame, text="Last Updated:").pack(side=tk.RIGHT, padx=5)
        self.last_update_label = ttk.Label(control_frame, text="Never", font=('Arial', 9, 'italic'))
        self.last_update_label.pack(side=tk.RIGHT, padx=5)

    def update_system_status(self, status_data: Dict[str, Any]):
        """Update system status from UDP status broadcast"""
        # Handle both direct format and payload-wrapped format
        if "payload" in status_data:
            # UDP format: {"message_type": "status", "payload": {"system": {...}}}
            payload = status_data["payload"]
            if "system" not in payload:
                return
            system = payload["system"]
        elif "system" in status_data:
            # Direct format
            system = status_data["system"]
        else:
            return

        self.system_data = system

        # Uptime
        uptime_sec = system.get("uptime_seconds", 0)
        uptime_str = self._format_uptime(uptime_sec)
        self.uptime_label.config(text=uptime_str)

        # Hostname (if available)
        hostname = system.get("hostname", "N/A")
        self.hostname_label.config(text=hostname)

        # CPU usage
        cpu_usage = system.get("cpu_percent", 0.0)
        self.cpu_var.set(cpu_usage)
        self.cpu_label.config(text=f"{cpu_usage:.1f}%")

        # Color code CPU usage
        if cpu_usage >= 90:
            self.cpu_label.config(foreground="red")
        elif cpu_usage >= 70:
            self.cpu_label.config(foreground="orange")
        else:
            self.cpu_label.config(foreground="green")

        # Memory usage
        mem_used_mb = system.get("memory_mb", 0)
        mem_total_mb = system.get("memory_total_mb", 0)

        # Calculate memory usage percentage
        mem_usage = 0.0
        if mem_total_mb > 0:
            mem_usage = (mem_used_mb / mem_total_mb) * 100

        self.mem_var.set(mem_usage)
        self.mem_label.config(text=f"{mem_usage:.1f}%")

        # Color code memory usage
        if mem_usage >= 90:
            self.mem_label.config(foreground="red")
        elif mem_usage >= 80:
            self.mem_label.config(foreground="orange")
        else:
            self.mem_label.config(foreground="green")

        # Memory details
        if mem_used_mb > 0:
            self.mem_used_label.config(text=f"{mem_used_mb:.0f} MB")
        if mem_total_mb > 0:
            self.mem_total_label.config(text=f"{mem_total_mb:.0f} MB")

        # Storage (disk) usage
        storage_free_gb = system.get("disk_free_gb", 0.0)
        storage_total_gb = system.get("disk_total_gb", 0.0)

        if storage_total_gb > 0:
            storage_used_percent = ((storage_total_gb - storage_free_gb) / storage_total_gb) * 100
            self.storage_var.set(storage_used_percent)
            self.storage_label.config(text=f"{storage_used_percent:.1f}%")

            # Color code storage
            if storage_free_gb < 5:
                self.storage_free_label.config(foreground="red")
            elif storage_free_gb < 20:
                self.storage_free_label.config(foreground="orange")
            else:
                self.storage_free_label.config(foreground="green")

        self.storage_free_label.config(text=f"{storage_free_gb:.1f} GB")
        self.storage_total_label.config(text=f"{storage_total_gb:.1f} GB")

        # Update timestamp
        from datetime import datetime
        self.last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable format"""
        if seconds == 0:
            return "N/A"

        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def _manual_refresh(self):
        """Manual refresh triggered by button"""
        logger.info("Manual system refresh requested")
        # TODO: Send system.get_status command via TCP client
        # This will be connected when integrating with main_window

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.auto_refresh_enabled:
            logger.info(f"System auto-refresh enabled ({self.interval_var.get()}s)")
            self._schedule_refresh()
        else:
            logger.info("System auto-refresh disabled")

    def _update_refresh_interval(self):
        """Update refresh interval"""
        self.refresh_interval = self.interval_var.get() * 1000  # Convert to ms
        logger.debug(f"System refresh interval set to {self.interval_var.get()}s")

    def _schedule_refresh(self):
        """Schedule next auto-refresh"""
        if self.auto_refresh_enabled:
            self._manual_refresh()
            self.after(self.refresh_interval, self._schedule_refresh)
