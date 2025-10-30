"""
Camera Status Comparison Sub-Tab for Log Inspector
Compares log-derived camera status vs UDP broadcast status
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Optional

from utils.log_parser import LogParser


class CameraComparisonTab(ttk.Frame):
    """Camera Status Comparison sub-tab - detects discrepancies"""

    def __init__(self, parent, log_parser: LogParser):
        super().__init__(parent)
        self.log_parser = log_parser
        self.udp_camera_connected: Optional[bool] = None
        self.udp_last_update: Optional[datetime] = None

        self._create_ui()

    def _create_ui(self):
        """Create UI elements"""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(title_frame, text="Camera Status Comparison",
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)

        # Comparison frame
        comparison_frame = ttk.LabelFrame(self, text="Status Comparison", padding=10)
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create 3 columns: Log Status | UDP Status | Match Indicator
        comparison_frame.grid_columnconfigure(0, weight=1)
        comparison_frame.grid_columnconfigure(1, weight=1)
        comparison_frame.grid_columnconfigure(2, weight=1)

        # Column 1: Log-Derived Status
        log_frame = ttk.LabelFrame(comparison_frame, text="Log-Derived Status", padding=10)
        log_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.log_status_label = ttk.Label(log_frame, text="Unknown",
                                          font=('Arial', 24, 'bold'), foreground="gray")
        self.log_status_label.pack(pady=20)

        self.log_last_event_label = ttk.Label(log_frame, text="Last Event: N/A",
                                              font=('Arial', 10))
        self.log_last_event_label.pack(pady=5)

        self.log_event_time_label = ttk.Label(log_frame, text="Time: N/A",
                                              font=('Arial', 9, 'italic'))
        self.log_event_time_label.pack(pady=5)

        ttk.Separator(log_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.log_connect_count = ttk.Label(log_frame, text="Connects: 0")
        self.log_connect_count.pack()

        self.log_disconnect_count = ttk.Label(log_frame, text="Disconnects: 0")
        self.log_disconnect_count.pack()

        # Column 2: UDP Broadcast Status
        udp_frame = ttk.LabelFrame(comparison_frame, text="UDP Broadcast Status", padding=10)
        udp_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.udp_status_label = ttk.Label(udp_frame, text="Unknown",
                                          font=('Arial', 24, 'bold'), foreground="gray")
        self.udp_status_label.pack(pady=20)

        self.udp_last_update_label = ttk.Label(udp_frame, text="Last Update: N/A",
                                               font=('Arial', 10))
        self.udp_last_update_label.pack(pady=5)

        self.udp_update_time_label = ttk.Label(udp_frame, text="Time: N/A",
                                               font=('Arial', 9, 'italic'))
        self.udp_update_time_label.pack(pady=5)

        ttk.Label(udp_frame, text="", font=('Arial', 9)).pack(pady=5)  # Spacer

        ttk.Separator(udp_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.udp_info_label = ttk.Label(udp_frame, text="Waiting for UDP data...")
        self.udp_info_label.pack()

        # Column 3: Match Indicator
        match_frame = ttk.LabelFrame(comparison_frame, text="Status Match", padding=10)
        match_frame.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        self.match_indicator = tk.Canvas(match_frame, width=80, height=80, highlightthickness=0)
        self.match_indicator.pack(pady=20)

        self.match_label = ttk.Label(match_frame, text="Checking...",
                                     font=('Arial', 14, 'bold'))
        self.match_label.pack(pady=10)

        self.match_detail_label = ttk.Label(match_frame, text="",
                                           font=('Arial', 10), wraplength=200)
        self.match_detail_label.pack(pady=10)

        # Recent discrepancies log
        discrepancy_frame = ttk.LabelFrame(self, text="Recent Discrepancies", padding=5)
        discrepancy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # TreeView for discrepancies
        columns = ("timestamp", "log_status", "udp_status", "details")
        self.discrepancy_tree = ttk.Treeview(discrepancy_frame, columns=columns,
                                            show="headings", height=8)

        self.discrepancy_tree.heading("timestamp", text="Timestamp")
        self.discrepancy_tree.heading("log_status", text="Log Status")
        self.discrepancy_tree.heading("udp_status", text="UDP Status")
        self.discrepancy_tree.heading("details", text="Details")

        self.discrepancy_tree.column("timestamp", width=180)
        self.discrepancy_tree.column("log_status", width=150)
        self.discrepancy_tree.column("udp_status", width=150)
        self.discrepancy_tree.column("details", width=400)

        scrollbar = ttk.Scrollbar(discrepancy_frame, orient=tk.VERTICAL,
                                 command=self.discrepancy_tree.yview)
        self.discrepancy_tree.configure(yscrollcommand=scrollbar.set)

        self.discrepancy_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Track discrepancies
        self.discrepancies = []

    def update_comparison(self, udp_camera_connected: Optional[bool] = None):
        """Update comparison with latest data"""
        # Update UDP data if provided
        if udp_camera_connected is not None:
            self.udp_camera_connected = udp_camera_connected
            self.udp_last_update = datetime.now()

        # Get log-derived status
        camera_events = self.log_parser.get_camera_events()

        if camera_events:
            last_event = camera_events[-1]
            log_connected = (last_event.event_type == "connected")
            log_status_text = "Connected" if log_connected else "Disconnected"
            log_color = "green" if log_connected else "red"

            self.log_status_label.config(text=log_status_text, foreground=log_color)
            self.log_last_event_label.config(text=f"Last Event: {last_event.event_type.capitalize()}")
            self.log_event_time_label.config(text=f"Time: {last_event.timestamp.strftime('%H:%M:%S')}")

            # Count events
            connect_count = sum(1 for e in camera_events if e.event_type == "connected")
            disconnect_count = sum(1 for e in camera_events if e.event_type == "disconnected")
            self.log_connect_count.config(text=f"Connects: {connect_count}")
            self.log_disconnect_count.config(text=f"Disconnects: {disconnect_count}")
        else:
            log_connected = None
            self.log_status_label.config(text="Unknown", foreground="gray")
            self.log_last_event_label.config(text="Last Event: N/A")
            self.log_event_time_label.config(text="Time: N/A")
            self.log_connect_count.config(text="Connects: 0")
            self.log_disconnect_count.config(text="Disconnects: 0")

        # Update UDP status display
        if self.udp_camera_connected is not None:
            udp_status_text = "Connected" if self.udp_camera_connected else "Disconnected"
            udp_color = "green" if self.udp_camera_connected else "red"
            self.udp_status_label.config(text=udp_status_text, foreground=udp_color)

            if self.udp_last_update:
                self.udp_last_update_label.config(text="Last Update: UDP Broadcast")
                self.udp_update_time_label.config(
                    text=f"Time: {self.udp_last_update.strftime('%H:%M:%S')}"
                )

            self.udp_info_label.config(text="Receiving UDP broadcasts")
        else:
            self.udp_status_label.config(text="Unknown", foreground="gray")
            self.udp_last_update_label.config(text="Last Update: N/A")
            self.udp_update_time_label.config(text="Time: N/A")
            self.udp_info_label.config(text="Waiting for UDP data...")

        # Compare statuses
        self._update_match_indicator(log_connected, self.udp_camera_connected)

    def _update_match_indicator(self, log_connected: Optional[bool],
                                udp_connected: Optional[bool]):
        """Update match indicator based on comparison"""
        self.match_indicator.delete("all")

        if log_connected is None or udp_connected is None:
            # Can't compare - insufficient data
            self.match_indicator.create_oval(10, 10, 70, 70, fill="gray", outline="gray")
            self.match_label.config(text="Insufficient Data", foreground="gray")
            self.match_detail_label.config(text="Waiting for both log and UDP status data")
            return

        if log_connected == udp_connected:
            # Match! ✓
            self.match_indicator.create_oval(10, 10, 70, 70, fill="green", outline="darkgreen", width=3)
            self.match_indicator.create_text(40, 40, text="✓", font=('Arial', 40, 'bold'),
                                            fill="white")
            self.match_label.config(text="Status Match", foreground="green")
            self.match_detail_label.config(text="Log and UDP status agree")
        else:
            # Mismatch! ⚠️
            self.match_indicator.create_oval(10, 10, 70, 70, fill="red", outline="darkred", width=3)
            self.match_indicator.create_text(40, 40, text="⚠", font=('Arial', 40, 'bold'),
                                            fill="white")
            self.match_label.config(text="DISCREPANCY", foreground="red")

            log_text = "Connected" if log_connected else "Disconnected"
            udp_text = "Connected" if udp_connected else "Disconnected"
            self.match_detail_label.config(
                text=f"Log shows {log_text} but UDP shows {udp_text}"
            )

            # Log discrepancy
            self._log_discrepancy(log_connected, udp_connected)

    def _log_discrepancy(self, log_connected: bool, udp_connected: bool):
        """Log a discrepancy event"""
        timestamp = datetime.now()
        log_status = "Connected" if log_connected else "Disconnected"
        udp_status = "Connected" if udp_connected else "Disconnected"

        # Check if this is a new discrepancy (not a repeat within 5 seconds)
        if self.discrepancies:
            last_disc = self.discrepancies[-1]
            time_diff = (timestamp - last_disc["timestamp"]).total_seconds()
            if time_diff < 5 and last_disc["log_status"] == log_status and last_disc["udp_status"] == udp_status:
                return  # Skip duplicate

        discrepancy = {
            "timestamp": timestamp,
            "log_status": log_status,
            "udp_status": udp_status,
            "details": f"Log reported {log_status}, UDP reported {udp_status}"
        }

        self.discrepancies.append(discrepancy)

        # Add to tree
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.discrepancy_tree.insert("", 0,  # Insert at top
                                    values=(timestamp_str, log_status, udp_status,
                                           discrepancy["details"]))

        # Limit to last 100 discrepancies
        if len(self.discrepancies) > 100:
            self.discrepancies = self.discrepancies[-100:]
            # Remove oldest from tree
            children = self.discrepancy_tree.get_children()
            if len(children) > 100:
                self.discrepancy_tree.delete(children[-1])
