"""
Camera Events Sub-Tab for Log Inspector
Shows camera connect/disconnect events
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List

from utils.log_parser import CameraEvent, LogParser


class CameraEventsTab(ttk.Frame):
    """Camera Events sub-tab"""

    def __init__(self, parent, log_parser: LogParser):
        super().__init__(parent)
        self.log_parser = log_parser

        self._create_ui()

    def _create_ui(self):
        """Create UI elements"""
        # Statistics at top
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.connect_count_label = ttk.Label(stats_frame, text="Connects: 0", font=('Arial', 10, 'bold'))
        self.connect_count_label.pack(side=tk.LEFT, padx=10)

        self.disconnect_count_label = ttk.Label(stats_frame, text="Disconnects: 0", font=('Arial', 10, 'bold'))
        self.disconnect_count_label.pack(side=tk.LEFT, padx=10)

        self.current_status_label = ttk.Label(stats_frame, text="Current: Unknown")
        self.current_status_label.pack(side=tk.LEFT, padx=20)

        # Events list
        list_frame = ttk.LabelFrame(self, text="Camera Connection Events", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # TreeView
        columns = ("timestamp", "event", "details")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)

        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("event", text="Event")
        self.tree.heading("details", text="Details")

        self.tree.column("timestamp", width=180)
        self.tree.column("event", width=120)
        self.tree.column("details", width=600)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure tags for coloring
        self.tree.tag_configure("connected", foreground="green")
        self.tree.tag_configure("disconnected", foreground="red")

    def update_events(self):
        """Update events from log parser"""
        events = self.log_parser.get_camera_events()

        # Clear tree
        self.tree.delete(*self.tree.get_children())

        # Count events
        connect_count = sum(1 for e in events if e.event_type == "connected")
        disconnect_count = sum(1 for e in events if e.event_type == "disconnected")

        # Determine current status
        if events:
            last_event = events[-1]
            current_status = "Connected" if last_event.event_type == "connected" else "Disconnected"
            status_color = "green" if last_event.event_type == "connected" else "red"
        else:
            current_status = "Unknown"
            status_color = "gray"

        # Update labels
        self.connect_count_label.config(text=f"Connects: {connect_count}")
        self.disconnect_count_label.config(text=f"Disconnects: {disconnect_count}")
        self.current_status_label.config(text=f"Current: {current_status}", foreground=status_color)

        # Add events to tree
        for event in events:
            timestamp_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            tag = "connected" if event.event_type == "connected" else "disconnected"

            self.tree.insert("", tk.END,
                           values=(timestamp_str, event.event_type.capitalize(), event.details),
                           tags=(tag,))

        # Auto-scroll to bottom
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])
