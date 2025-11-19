"""
Air-Side Multi-Tab Container
=============================

Consolidates all Air-Side specific functionality into a single organized tab.

Sub-tabs:
- Configuration: Air-Side system configuration
- Docker Logs: Payload Manager container logs
- Camera Dashboard: Sony camera monitoring and control
- Remote Control: Command execution and system control
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from utils.protocol_logger import logger


class AirSideTab:
    """Air-Side operations consolidated into multi-tab interface"""

    def __init__(
        self,
        parent,
        tcp_client=None,
        ssh_client=None,
        on_log_control_change: Optional[Callable] = None,
        discovery_sender=None
    ):
        """
        Initialize Air-Side tab

        Args:
            parent: Parent widget
            tcp_client: TCP client for Air-Side communication
            ssh_client: SSH client for Air-Side access
            on_log_control_change: Callback for log control changes
            discovery_sender: UDP discovery sender
        """
        self.parent = parent
        self.tcp_client = tcp_client
        self.ssh_client = ssh_client
        self.on_log_control_change = on_log_control_change
        self.discovery_sender = discovery_sender

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tabs will be added via set_subtabs()
        self.subtabs = {}

        logger.debug("SYSTEM", "Air-Side multi-tab container initialized")

    def set_subtabs(self, subtabs_dict: dict):
        """
        Set sub-tabs for Air-Side operations

        Args:
            subtabs_dict: Dictionary of {name: widget} for sub-tabs
        """
        self.subtabs = subtabs_dict

        for name, widget in subtabs_dict.items():
            # Get the frame from the widget
            if hasattr(widget, 'frame'):
                frame = widget.frame
            else:
                frame = widget

            self.notebook.add(frame, text=name)

        logger.info("SYSTEM", f"Air-Side: Added {len(subtabs_dict)} sub-tabs")

    def set_tcp_client(self, client):
        """Update TCP client reference"""
        self.tcp_client = client

        # Propagate to sub-tabs that need it
        for subtab in self.subtabs.values():
            if hasattr(subtab, 'set_tcp_client'):
                subtab.set_tcp_client(client)

    def set_ssh_client(self, client):
        """Update SSH client reference"""
        self.ssh_client = client

        # Propagate to sub-tabs that need it
        for subtab in self.subtabs.values():
            if hasattr(subtab, 'set_ssh_client'):
                subtab.set_ssh_client(client)

    def cleanup(self):
        """Cleanup resources"""
        for subtab in self.subtabs.values():
            if hasattr(subtab, 'cleanup'):
                subtab.cleanup()

        logger.debug("SYSTEM", "Air-Side tab cleaned up")
