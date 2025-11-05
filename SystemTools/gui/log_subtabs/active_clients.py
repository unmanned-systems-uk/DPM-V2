"""
Active Clients Sub-Tab for Log Inspector
Shows connected clients with heartbeat analysis
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List

from utils.log_parser import ClientInfo, LogParser


class ActiveClientsTab(ttk.Frame):
    """Active Clients sub-tab with heartbeat monitoring"""

    def __init__(self, parent, log_parser: LogParser):
        super().__init__(parent)
        self.log_parser = log_parser

        self._create_ui()

    def _create_ui(self):
        """Create UI elements"""
        # Statistics at top
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.client_count_label = ttk.Label(stats_frame, text="Active Clients: 0", font=('Arial', 12, 'bold'))
        self.client_count_label.pack(side=tk.LEFT, padx=10)

        self.fluctuation_warning = ttk.Label(stats_frame, text="", font=('Arial', 10, 'bold'), foreground="red")
        self.fluctuation_warning.pack(side=tk.LEFT, padx=20)

        # Client list
        list_frame = ttk.LabelFrame(self, text="Connected Clients", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # TreeView
        columns = ("ip", "ports", "heartbeats", "last_hb", "avg_interval", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        self.tree.heading("ip", text="Client IP")
        self.tree.heading("ports", text="Ports")
        self.tree.heading("heartbeats", text="Heartbeat Count")
        self.tree.heading("last_hb", text="Last Heartbeat")
        self.tree.heading("avg_interval", text="Avg Interval (s)")
        self.tree.heading("status", text="Status")

        self.tree.column("ip", width=150)
        self.tree.column("ports", width=200)
        self.tree.column("heartbeats", width=120)
        self.tree.column("last_hb", width=180)
        self.tree.column("avg_interval", width=120)
        self.tree.column("status", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure tags for coloring
        self.tree.tag_configure("normal", foreground="green")
        self.tree.tag_configure("fluctuation", foreground="orange")
        self.tree.tag_configure("stale", foreground="red")

        # Heartbeat timeline (simple text view for now)
        timeline_frame = ttk.LabelFrame(self, text="Heartbeat Timeline (Last 10)", padding=5)
        timeline_frame.pack(fill=tk.X, padx=10, pady=5)

        self.timeline_text = tk.Text(timeline_frame, height=5, wrap=tk.WORD, font=('Courier', 9))
        self.timeline_text.pack(fill=tk.BOTH, expand=True)

    def update_clients(self):
        """Update client list from log parser"""
        clients = self.log_parser.get_active_clients()

        # Clear tree
        self.tree.delete(*self.tree.get_children())

        # Update count
        self.client_count_label.config(text=f"Active Clients: {len(clients)}")

        # Check for fluctuations
        fluctuation_count = sum(1 for c in clients if c.fluctuation_detected)
        if fluctuation_count > 0:
            self.fluctuation_warning.config(text=f"⚠️ {fluctuation_count} client(s) with heartbeat fluctuations")
        else:
            self.fluctuation_warning.config(text="")

        # Add clients to tree
        for client in clients:
            # Format ports
            ports_str = ", ".join(str(p) for p in sorted(client.ports))

            # Format last heartbeat
            if client.last_heartbeat:
                last_hb_str = client.last_heartbeat.strftime("%H:%M:%S.%f")[:-3]
                age_seconds = (datetime.now() - client.last_heartbeat).total_seconds()
            else:
                last_hb_str = "Never"
                age_seconds = float('inf')

            # Format average interval
            avg_interval_str = f"{client.avg_interval:.2f}" if client.avg_interval > 0 else "N/A"

            # Determine status and tag
            if age_seconds > 5:
                status = "Stale (>5s)"
                tag = "stale"
            elif client.fluctuation_detected:
                status = "Fluctuating"
                tag = "fluctuation"
            else:
                status = "Active"
                tag = "normal"

            self.tree.insert("", tk.END,
                           values=(client.ip, ports_str, client.heartbeat_count,
                                 last_hb_str, avg_interval_str, status),
                           tags=(tag,))

        # Update timeline (show last 10 heartbeat events)
        self.timeline_text.delete(1.0, tk.END)
        heartbeat_events = self.log_parser.get_heartbeat_events(limit=10)
        if heartbeat_events:
            self.timeline_text.insert(1.0, "Recent Heartbeats:\n")
            for event in reversed(heartbeat_events):  # Most recent first
                timestamp_str = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
                direction_symbol = "←" if event.direction == "received" else "→"
                line = f"{timestamp_str} {direction_symbol} {event.client_ip}:{event.port} (seq={event.sequence})\n"
                self.timeline_text.insert(tk.END, line)
