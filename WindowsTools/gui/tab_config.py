"""
Configuration Tab for DPM Diagnostic Tool
Settings management UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from utils.config import config
from utils.logger import logger
from gui.widgets import LabeledEntry, LabeledSpinbox


class ConfigTab(ttk.Frame):
    """Configuration tab"""

    def __init__(self, parent, on_settings_changed=None):
        super().__init__(parent)
        self.on_settings_changed = on_settings_changed

        self._create_ui()
        self._load_settings()

        logger.debug("Config tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Main container with scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Network Settings
        self._create_network_section()

        # SSH Settings
        self._create_ssh_section()

        # UI Settings
        self._create_ui_section()

        # Buttons
        self._create_buttons()

    def _create_network_section(self):
        """Create network settings section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="Network Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        self.air_ip = LabeledEntry(frame, "Air-Side IP:", width=15)
        self.air_ip.pack(fill=tk.X, pady=2)

        self.tcp_port = LabeledSpinbox(frame, "TCP Port:", 1000, 65535, width=10)
        self.tcp_port.pack(fill=tk.X, pady=2)

        self.status_port = LabeledSpinbox(frame, "UDP Status Port:", 1000, 65535, width=10)
        self.status_port.pack(fill=tk.X, pady=2)

        self.heartbeat_port = LabeledSpinbox(frame, "UDP Heartbeat Port:", 1000, 65535, width=10)
        self.heartbeat_port.pack(fill=tk.X, pady=2)

        self.h16_ip = LabeledEntry(frame, "H16 IP:", width=15)
        self.h16_ip.pack(fill=tk.X, pady=2)

        self.timeout = LabeledSpinbox(frame, "Timeout (ms):", 1000, 60000, width=10)
        self.timeout.pack(fill=tk.X, pady=2)

    def _create_ssh_section(self):
        """Create SSH settings section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="SSH Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        self.ssh_host = LabeledEntry(frame, "SSH Host:", width=15)
        self.ssh_host.pack(fill=tk.X, pady=2)

        self.ssh_port = LabeledSpinbox(frame, "SSH Port:", 1, 65535, width=10)
        self.ssh_port.pack(fill=tk.X, pady=2)

        self.ssh_user = LabeledEntry(frame, "SSH Username:", width=15)
        self.ssh_user.pack(fill=tk.X, pady=2)

        self.ssh_pass = LabeledEntry(frame, "SSH Password:", width=15)
        self.ssh_pass.entry.config(show="*")  # Hide password
        self.ssh_pass.pack(fill=tk.X, pady=2)

        self.save_password = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text="Save password (Warning: stored in plain text)",
                              variable=self.save_password)
        chk.pack(fill=tk.X, pady=2)

    def _create_ui_section(self):
        """Create UI settings section"""
        frame = ttk.LabelFrame(self.scrollable_frame, text="UI Settings", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        self.auto_connect = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text="Auto-connect on startup",
                              variable=self.auto_connect)
        chk.pack(fill=tk.X, pady=2)

        self.font_size = LabeledSpinbox(frame, "Font Size:", 8, 20, width=10)
        self.font_size.pack(fill=tk.X, pady=2)

        self.audio_alerts = tk.BooleanVar()
        chk = ttk.Checkbutton(frame, text="Enable audio alerts",
                              variable=self.audio_alerts)
        chk.pack(fill=tk.X, pady=2)

        # Data/File settings
        data_frame = ttk.LabelFrame(self.scrollable_frame, text="Data & Files", padding=10)
        data_frame.pack(fill=tk.X, padx=10, pady=5)

        # Log save directory
        log_dir_frame = ttk.Frame(data_frame)
        log_dir_frame.pack(fill=tk.X, pady=2)

        ttk.Label(log_dir_frame, text="Log Save Location:", width=15, anchor='w').pack(side=tk.LEFT, padx=5)

        self.log_dir_var = tk.StringVar()
        log_dir_entry = ttk.Entry(log_dir_frame, textvariable=self.log_dir_var, width=30)
        log_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(log_dir_frame, text="Browse...", command=self._browse_log_directory).pack(side=tk.LEFT, padx=5)

    def _create_buttons(self):
        """Create action buttons"""
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(frame, text="Save Settings", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Reset to Defaults", command=self._reset_defaults).pack(side=tk.LEFT, padx=5)

    def _load_settings(self):
        """Load settings from config"""
        # Network
        self.air_ip.set(config.get("network", "air_side_ip", "10.0.1.53"))
        self.tcp_port.set(config.get("network", "tcp_port", 5000))
        self.status_port.set(config.get("network", "udp_status_port", 5001))
        self.heartbeat_port.set(config.get("network", "udp_heartbeat_port", 5002))
        self.h16_ip.set(config.get("network", "h16_ip", "10.0.1.92"))
        self.timeout.set(config.get("network", "connection_timeout_ms", 5000))

        # SSH
        self.ssh_host.set(config.get("ssh", "host", "10.0.1.53"))
        self.ssh_port.set(config.get("ssh", "port", 22))
        self.ssh_user.set(config.get("ssh", "username", "dpm"))
        self.ssh_pass.set(config.get("ssh", "password", ""))
        self.save_password.set(config.get("ssh", "save_password", False))

        # UI
        self.auto_connect.set(config.get("ui", "auto_connect_on_startup", True))
        self.font_size.set(config.get("ui", "font_size", 10))
        self.audio_alerts.set(config.get("ui", "enable_audio_alerts", False))

        # Data
        self.log_dir_var.set(config.get("data", "log_directory", str(Path.home() / "Documents")))

        logger.debug("Settings loaded")

    def _save_settings(self):
        """Save settings to config"""
        # Network
        config.set("network", "air_side_ip", self.air_ip.get())
        config.set("network", "tcp_port", self.tcp_port.get())
        config.set("network", "udp_status_port", self.status_port.get())
        config.set("network", "udp_heartbeat_port", self.heartbeat_port.get())
        config.set("network", "h16_ip", self.h16_ip.get())
        config.set("network", "connection_timeout_ms", self.timeout.get())

        # SSH
        config.set("ssh", "host", self.ssh_host.get())
        config.set("ssh", "port", self.ssh_port.get())
        config.set("ssh", "username", self.ssh_user.get())

        if self.save_password.get():
            config.set("ssh", "password", self.ssh_pass.get())
        else:
            config.set("ssh", "password", "")

        config.set("ssh", "save_password", self.save_password.get())

        # UI
        config.set("ui", "auto_connect_on_startup", self.auto_connect.get())
        config.set("ui", "font_size", self.font_size.get())
        config.set("ui", "enable_audio_alerts", self.audio_alerts.get())

        # Data
        config.set("data", "log_directory", self.log_dir_var.get())

        config.save()

        messagebox.showinfo("Success", "Settings saved successfully!")
        logger.info("Settings saved")

        if self.on_settings_changed:
            self.on_settings_changed()

    def _browse_log_directory(self):
        """Browse for log save directory"""
        current_dir = self.log_dir_var.get()
        if not current_dir or not Path(current_dir).exists():
            current_dir = str(Path.home() / "Documents")

        directory = filedialog.askdirectory(
            title="Select Log Save Directory",
            initialdir=current_dir
        )

        if directory:
            self.log_dir_var.set(directory)
            logger.info(f"Log directory changed to: {directory}")

    def _reset_defaults(self):
        """Reset to default settings"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            config.reset_to_defaults()
            self._load_settings()
            messagebox.showinfo("Success", "Settings reset to defaults!")
            logger.info("Settings reset to defaults")
