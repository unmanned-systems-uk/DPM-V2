"""
Camera Dashboard Tab for DPM Diagnostic Tool
Real-time camera status and property monitoring
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

from utils.logger import logger
from utils.protocol_loader import protocol


class CameraDashboardTab(ttk.Frame):
    """Camera Dashboard tab - real-time camera monitoring"""

    def __init__(self, parent):
        super().__init__(parent)

        self.camera_connected = False
        self.camera_properties = {}
        self.auto_refresh_enabled = False
        self.refresh_interval = 5000  # ms

        self._create_ui()

        logger.debug("Camera Dashboard tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Camera connection status
        status_frame = ttk.LabelFrame(self, text="Camera Status", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        # Connection indicator
        conn_frame = ttk.Frame(status_frame)
        conn_frame.pack(fill=tk.X)

        ttk.Label(conn_frame, text="Connection:").pack(side=tk.LEFT, padx=5)
        self.conn_indicator = tk.Canvas(conn_frame, width=20, height=20, highlightthickness=0)
        self.conn_indicator.pack(side=tk.LEFT, padx=5)
        self._update_connection_indicator(False)

        self.conn_label = ttk.Label(conn_frame, text="Disconnected", font=('Arial', 9, 'bold'))
        self.conn_label.pack(side=tk.LEFT, padx=5)

        # Camera model
        ttk.Label(conn_frame, text="Model:").pack(side=tk.LEFT, padx=(20, 5))
        self.model_label = ttk.Label(conn_frame, text="N/A")
        self.model_label.pack(side=tk.LEFT, padx=5)

        # Battery and shots
        battery_frame = ttk.Frame(status_frame)
        battery_frame.pack(fill=tk.X, pady=(5, 0))

        # Battery
        ttk.Label(battery_frame, text="Battery:").pack(side=tk.LEFT, padx=5)
        self.battery_var = tk.IntVar(value=0)
        self.battery_progress = ttk.Progressbar(battery_frame, variable=self.battery_var,
                                               maximum=100, length=200, mode='determinate')
        self.battery_progress.pack(side=tk.LEFT, padx=5)
        self.battery_label = ttk.Label(battery_frame, text="0%")
        self.battery_label.pack(side=tk.LEFT, padx=5)

        # Remaining shots
        ttk.Label(battery_frame, text="Remaining Shots:").pack(side=tk.LEFT, padx=(20, 5))
        self.shots_label = ttk.Label(battery_frame, text="N/A")
        self.shots_label.pack(side=tk.LEFT, padx=5)

        # Exposure Triangle (Large Display)
        exposure_frame = ttk.LabelFrame(self, text="Exposure Triangle", padding=10)
        exposure_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create three columns for shutter, aperture, ISO
        exposure_cols = ttk.Frame(exposure_frame)
        exposure_cols.pack(fill=tk.X)

        # Shutter Speed
        shutter_col = ttk.Frame(exposure_cols)
        shutter_col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        ttk.Label(shutter_col, text="Shutter Speed", font=('Arial', 10)).pack()
        self.shutter_label = ttk.Label(shutter_col, text="N/A", font=('Arial', 18, 'bold'))
        self.shutter_label.pack(pady=5)

        # Aperture
        aperture_col = ttk.Frame(exposure_cols)
        aperture_col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        ttk.Label(aperture_col, text="Aperture", font=('Arial', 10)).pack()
        self.aperture_label = ttk.Label(aperture_col, text="N/A", font=('Arial', 18, 'bold'))
        self.aperture_label.pack(pady=5)

        # ISO
        iso_col = ttk.Frame(exposure_cols)
        iso_col.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        ttk.Label(iso_col, text="ISO", font=('Arial', 10)).pack()
        self.iso_label = ttk.Label(iso_col, text="N/A", font=('Arial', 18, 'bold'))
        self.iso_label.pack(pady=5)

        # Other Properties
        props_frame = ttk.LabelFrame(self, text="Camera Properties", padding=10)
        props_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create grid for properties
        props_grid = ttk.Frame(props_frame)
        props_grid.pack(fill=tk.BOTH, expand=True)

        # White Balance
        ttk.Label(props_grid, text="White Balance:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.wb_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.wb_label.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Focus Mode
        ttk.Label(props_grid, text="Focus Mode:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.focus_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.focus_label.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # File Format
        ttk.Label(props_grid, text="File Format:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.format_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.format_label.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Drive Mode
        ttk.Label(props_grid, text="Drive Mode:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.drive_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.drive_label.grid(row=0, column=3, sticky='w', padx=5, pady=5)

        # Exposure Mode
        ttk.Label(props_grid, text="Exposure Mode:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.exp_mode_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.exp_mode_label.grid(row=1, column=3, sticky='w', padx=5, pady=5)

        # Flash Mode
        ttk.Label(props_grid, text="Flash Mode:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.flash_label = ttk.Label(props_grid, text="N/A", font=('Arial', 10))
        self.flash_label.grid(row=2, column=3, sticky='w', padx=5, pady=5)

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

    def _update_connection_indicator(self, connected: bool):
        """Update connection status indicator"""
        self.conn_indicator.delete("all")
        color = "green" if connected else "gray"
        self.conn_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def update_camera_status(self, status_data: Dict[str, Any]):
        """Update camera status from UDP status broadcast"""
        # Handle both direct format and payload-wrapped format
        if "payload" in status_data:
            # UDP format: {"message_type": "status", "payload": {"camera": {...}}}
            payload = status_data["payload"]
            if "camera" not in payload:
                return
            camera = payload["camera"]
        elif "camera" in status_data:
            # Direct format
            camera = status_data["camera"]
        else:
            return

        # Connection status
        self.camera_connected = camera.get("connected", False)
        self._update_connection_indicator(self.camera_connected)

        if self.camera_connected:
            self.conn_label.config(text="Connected", foreground="green")
        else:
            self.conn_label.config(text="Disconnected", foreground="gray")

        # Camera model
        model = camera.get("model", "N/A")
        self.model_label.config(text=model)

        # Battery level
        battery = camera.get("battery_percent", 0)
        self.battery_var.set(battery)
        self.battery_label.config(text=f"{battery}%")

        # Remaining shots
        shots = camera.get("remaining_shots", "N/A")
        self.shots_label.config(text=str(shots))

        # Current properties (called "settings" in status message)
        current_props = camera.get("settings", {})
        self._update_properties(current_props)

        # Update timestamp
        from datetime import datetime
        self.last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _update_properties(self, properties: Dict[str, Any]):
        """Update property displays"""
        # Exposure triangle
        shutter = properties.get("shutter_speed", "N/A")
        self.shutter_label.config(text=str(shutter))

        aperture = properties.get("aperture", "N/A")
        self.aperture_label.config(text=f"f/{aperture}" if aperture != "N/A" else "N/A")

        iso = properties.get("iso", "N/A")
        self.iso_label.config(text=str(iso))

        # Other properties
        wb = properties.get("white_balance", "N/A")
        self.wb_label.config(text=str(wb))

        focus = properties.get("focus_mode", "N/A")
        self.focus_label.config(text=str(focus))

        file_format = properties.get("file_format", "N/A")
        self.format_label.config(text=str(file_format))

        drive = properties.get("drive_mode", "N/A")
        self.drive_label.config(text=str(drive))

        exp_mode = properties.get("exposure_mode", "N/A")
        self.exp_mode_label.config(text=str(exp_mode))

        flash = properties.get("flash_mode", "N/A")
        self.flash_label.config(text=str(flash))

        # Store properties
        self.camera_properties = properties

    def _manual_refresh(self):
        """Manual refresh triggered by button"""
        # This would trigger a camera.get_properties command
        # For now, just log
        logger.info("Manual camera refresh requested")
        # TODO: Send camera.get_properties command via TCP client
        # This will be connected when integrating with main_window

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.auto_refresh_enabled:
            logger.info(f"Camera auto-refresh enabled ({self.interval_var.get()}s)")
            self._schedule_refresh()
        else:
            logger.info("Camera auto-refresh disabled")

    def _update_refresh_interval(self):
        """Update refresh interval"""
        self.refresh_interval = self.interval_var.get() * 1000  # Convert to ms
        logger.debug(f"Camera refresh interval set to {self.interval_var.get()}s")

    def _schedule_refresh(self):
        """Schedule next auto-refresh"""
        if self.auto_refresh_enabled:
            self._manual_refresh()
            self.after(self.refresh_interval, self._schedule_refresh)
