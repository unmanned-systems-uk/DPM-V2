"""
Connection Monitor Tab for DPM Diagnostic Tool
Real-time connection status and diagnostics
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime
from pathlib import Path

from utils.logger import logger
from utils.config import config
from gui.widgets import StatusIndicator, ScrolledTextLog
from network.tcp_client import TCPClient


class ConnectionTab(ttk.Frame):
    """Connection Monitor tab"""

    def __init__(self, parent):
        super().__init__(parent)

        self.tcp_client: TCPClient = None
        self.connected = False

        self._create_ui()

        # Set initial status to gray (neutral) - passive mode is normal
        self.status_indicator.set_status("gray")

        logger.debug("Connection tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Connection controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Monitoring Mode Info
        mode_frame = ttk.LabelFrame(control_frame, text="Monitoring Mode", padding=10)
        mode_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 5))

        mode_info = ttk.Frame(mode_frame)
        mode_info.pack(fill=tk.X)

        ttk.Label(mode_info, text="📡 Passive Monitoring:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(mode_info, text="Receiving UDP status broadcasts",
                 font=('Arial', 8), foreground='green').pack(side=tk.LEFT, padx=5)

        mode_info2 = ttk.Frame(mode_frame)
        mode_info2.pack(fill=tk.X, pady=2)

        ttk.Label(mode_info2, text="ℹ️", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(mode_info2, text="TCP connection only needed for sending commands",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=5)

        # UDP Status Indicators
        udp_frame = ttk.LabelFrame(control_frame, text="UDP Listeners (Passive Monitoring)", padding=10)
        udp_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Status port
        status_port_frame = ttk.Frame(udp_frame)
        status_port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(status_port_frame, text="Status Port:").pack(side=tk.LEFT)
        self.udp_status_indicator = StatusIndicator(status_port_frame, size=12)
        self.udp_status_indicator.pack(side=tk.LEFT, padx=5)
        self.udp_status_indicator.set_status("green")  # Assume running when app starts
        ttk.Label(status_port_frame, text=f"{config.get('network', 'udp_status_port', 5001)}",
                 font=('Arial', 8)).pack(side=tk.LEFT)

        # Heartbeat port
        hb_port_frame = ttk.Frame(udp_frame)
        hb_port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hb_port_frame, text="Heartbeat:").pack(side=tk.LEFT)
        self.udp_hb_indicator = StatusIndicator(hb_port_frame, size=12)
        self.udp_hb_indicator.pack(side=tk.LEFT, padx=5)
        self.udp_hb_indicator.set_status("green")  # Assume running when app starts
        ttk.Label(hb_port_frame, text=f"{config.get('network', 'udp_heartbeat_port', 5002)}",
                 font=('Arial', 8)).pack(side=tk.LEFT)

        # Connection info
        info_frame = ttk.LabelFrame(control_frame, text="TCP Connection (Optional - For Commands)", padding=10)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Status indicator
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill=tk.X, pady=2)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_indicator = StatusIndicator(status_frame, size=20)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="Not Connected (Passive Mode)", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # IP and Port
        ttk.Label(info_frame, text="Air-Side IP:").pack(anchor='w')
        self.ip_label = ttk.Label(info_frame, text=config.get("network", "air_side_ip", "10.0.1.53"),
                                  font=('Arial', 9))
        self.ip_label.pack(anchor='w', padx=20)

        ttk.Label(info_frame, text="TCP Port:").pack(anchor='w')
        self.port_label = ttk.Label(info_frame, text=str(config.get("network", "tcp_port", 5000)),
                                    font=('Arial', 9))
        self.port_label.pack(anchor='w', padx=20)

        # Buttons
        button_frame = ttk.LabelFrame(control_frame, text="Actions", padding=10)
        button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self._on_connect)
        self.connect_btn.pack(fill=tk.X, pady=2)

        self.disconnect_btn = ttk.Button(button_frame, text="Disconnect",
                                         command=self._on_disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(fill=tk.X, pady=2)

        self.handshake_btn = ttk.Button(button_frame, text="Send Handshake",
                                        command=self._on_handshake, state=tk.DISABLED)
        self.handshake_btn.pack(fill=tk.X, pady=2)

        # Connection Log
        log_frame = ttk.LabelFrame(self, text="Connection Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log = ScrolledTextLog(log_frame)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Log control buttons
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.pack(pady=5)

        ttk.Button(log_buttons_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text="Save Log...", command=self._save_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text="Copy to Clipboard", command=self._copy_to_clipboard).pack(side=tk.LEFT, padx=2)

    def set_tcp_client(self, client: TCPClient):
        """Set TCP client instance"""
        self.tcp_client = client

        # Set callbacks
        client.on_connected = self._on_connected_callback
        client.on_disconnected = self._on_disconnected_callback
        client.on_message_received = self._on_message_callback
        client.on_error = self._on_error_callback

    def _on_connect(self):
        """Handle connect button"""
        if self.connected:
            self.log.append("Already connected", "WARN")
            return

        # Get connection info from config
        host = config.get("network", "air_side_ip", "10.0.1.53")
        port = config.get("network", "tcp_port", 5000)
        timeout = config.get("network", "connection_timeout_ms", 5000)

        self.log.append(f"Connecting to {host}:{port}...", "INFO")

        # Create TCP client if needed
        if not self.tcp_client:
            self.tcp_client = TCPClient(host, port, timeout)
            self.set_tcp_client(self.tcp_client)

        # Connect in background thread
        def connect_thread():
            success = self.tcp_client.connect()
            if success:
                # Send handshake
                self.tcp_client.send_handshake()

        threading.Thread(target=connect_thread, daemon=True).start()

    def _on_disconnect(self):
        """Handle disconnect button"""
        if not self.connected:
            return

        self.log.append("Disconnecting...", "INFO")

        if self.tcp_client:
            self.tcp_client.disconnect()

    def _on_handshake(self):
        """Handle handshake button"""
        if not self.connected or not self.tcp_client:
            self.log.append("Not connected", "ERROR")
            return

        self.log.append("Sending handshake...", "INFO")
        self.tcp_client.send_handshake()

    def _on_connected_callback(self):
        """Callback when connected"""
        self.connected = True
        self.status_indicator.set_status("green")
        self.status_label.config(text="Connected (Active Control Mode)")
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.handshake_btn.config(state=tk.NORMAL)
        self.log.append("✓ TCP Connected - Active Control Mode enabled", "SUCCESS")
        self.log.append("  You can now send commands to Air-Side", "INFO")

    def _on_disconnected_callback(self):
        """Callback when disconnected"""
        self.connected = False
        self.status_indicator.set_status("gray")
        self.status_label.config(text="Not Connected (Passive Mode)")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.handshake_btn.config(state=tk.DISABLED)
        self.log.append("ℹ️ TCP Disconnected - Passive Monitoring Mode", "INFO")
        self.log.append("  UDP status broadcasts still active", "INFO")

    def _on_message_callback(self, message: dict):
        """Callback when message received"""
        msg_type = message.get("message_type", "unknown")
        self.log.append(f"← Received {msg_type} message", "INFO")

    def _on_error_callback(self, error: str):
        """Callback on error"""
        self.log.append(f"✗ Error: {error}", "ERROR")

    def _clear_log(self):
        """Clear the connection log"""
        if messagebox.askyesno("Clear Log", "Clear all connection log entries?"):
            self.log.clear()
            logger.info("Connection log cleared")

    def _save_log(self):
        """Save connection log to file"""
        # Get default save location from config
        default_dir = config.get("data", "log_directory", str(Path.home() / "Documents"))

        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"connection_log_{timestamp}.txt"

        # Open file dialog
        filepath = filedialog.asksaveasfilename(
            title="Save Connection Log",
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*")
            ]
        )

        if filepath:
            try:
                # Get log content
                log_content = self.log.get_all()

                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("DPM Diagnostic Tool - Connection Log\n")
                    f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(log_content)

                # Update config with last used directory
                config.set("data", "log_directory", str(Path(filepath).parent))

                logger.info(f"Connection log saved to: {filepath}")
                messagebox.showinfo("Success", f"Log saved successfully!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error saving log: {e}")
                messagebox.showerror("Error", f"Failed to save log:\n{e}")

    def _copy_to_clipboard(self):
        """Copy connection log to clipboard"""
        try:
            # Get log content
            log_content = self.log.get_all()

            # Clear clipboard and set new content
            self.clipboard_clear()
            self.clipboard_append(log_content)

            # Update clipboard (required on some systems)
            self.update()

            logger.info("Connection log copied to clipboard")
            messagebox.showinfo("Success", "Log copied to clipboard!")

        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{e}")

    def cleanup(self):
        """Cleanup on exit"""
        if self.tcp_client and self.connected:
            self.tcp_client.disconnect()
