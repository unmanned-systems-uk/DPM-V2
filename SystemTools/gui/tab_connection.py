"""
Connection Monitor Tab for DPM Diagnostic Tool
Comprehensive multi-domain connection status dashboard
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
from network.ssh_client import SSHClient
from network.adb_client import ADBClient


class ConnectionTab(ttk.Frame):
    """Smart Connection Monitor tab with comprehensive multi-domain status"""

    def __init__(self, parent):
        super().__init__(parent)

        # Connection clients
        self.tcp_client: TCPClient = None
        self.ssh_client: SSHClient = None
        self.adb_client: ADBClient = None

        # Connection states
        self.tcp_connected = False
        self.ssh_connected = False
        self.adb_connected = False

        # Heartbeat tracking
        self.air_heartbeat_time = None
        self.ground_heartbeat_time = None
        self.camera_properties_time = None
        self.camera_properties_count = 0

        # Pulse animation
        self.pulse_active = False
        self.pulse_thread = None

        self._create_ui()

        # Set initial status to gray (disconnected)
        self._update_all_status_indicators()

        # Start pulse animation thread
        self._start_pulse_animation()

        logger.debug("Connection tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Smart Connect Button (prominent)
        connect_frame = ttk.Frame(self)
        connect_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(connect_frame, text="Smart Connection Dashboard",
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=5)

        self.smart_connect_btn = ttk.Button(connect_frame, text="🔌 Connect All",
                                            command=self._on_smart_connect,
                                            style='Accent.TButton')
        self.smart_connect_btn.pack(side=tk.RIGHT, padx=5)

        self.smart_disconnect_btn = ttk.Button(connect_frame, text="Disconnect All",
                                               command=self._on_smart_disconnect,
                                               state=tk.DISABLED)
        self.smart_disconnect_btn.pack(side=tk.RIGHT, padx=5)

        # Main content: Three status sections
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create three columns
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        middle_column = ttk.Frame(content_frame)
        middle_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Create sections
        self._create_air_side_section(left_column)
        self._create_ground_side_section(middle_column)
        self._create_camera_section(right_column)

        # Bottom: Connection Log (collapsible)
        log_frame = ttk.LabelFrame(self, text="Connection Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log = ScrolledTextLog(log_frame, height=6)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Log control buttons
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.pack(pady=5)

        ttk.Button(log_buttons_frame, text="Clear", command=self._clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text="Save...", command=self._save_log).pack(side=tk.LEFT, padx=2)

    def _create_air_side_section(self, parent):
        """Create Air-Side status section"""
        frame = ttk.LabelFrame(parent, text="🖥️  AIR-SIDE STATUS", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # SSH Connection
        ssh_frame = self._create_status_row(frame, "SSH Connected:")
        self.ssh_indicator = StatusIndicator(ssh_frame, size=14)
        self.ssh_indicator.pack(side=tk.LEFT, padx=5)
        self.ssh_label = ttk.Label(ssh_frame, text="Not Connected", font=('Arial', 9))
        self.ssh_label.pack(side=tk.LEFT)

        # TCP Connection
        tcp_frame = self._create_status_row(frame, "TCP Connected:")
        self.tcp_indicator = StatusIndicator(tcp_frame, size=14)
        self.tcp_indicator.pack(side=tk.LEFT, padx=5)
        self.tcp_label = ttk.Label(tcp_frame, text="Not Connected", font=('Arial', 9))
        self.tcp_label.pack(side=tk.LEFT)

        # Heartbeat
        hb_frame = self._create_status_row(frame, "💓 Heartbeat:")
        self.air_hb_indicator = StatusIndicator(hb_frame, size=14)
        self.air_hb_indicator.pack(side=tk.LEFT, padx=5)
        self.air_hb_label = ttk.Label(hb_frame, text="No heartbeat", font=('Arial', 9))
        self.air_hb_label.pack(side=tk.LEFT)

        # Camera Detection
        cam_frame = self._create_status_row(frame, "📷 Camera:")
        self.air_camera_indicator = StatusIndicator(cam_frame, size=14)
        self.air_camera_indicator.pack(side=tk.LEFT, padx=5)
        self.air_camera_label = ttk.Label(cam_frame, text="Unknown", font=('Arial', 9))
        self.air_camera_label.pack(side=tk.LEFT)

        # Docker Status
        docker_frame = self._create_status_row(frame, "📊 Docker:")
        self.docker_indicator = StatusIndicator(docker_frame, size=14)
        self.docker_indicator.pack(side=tk.LEFT, padx=5)
        self.docker_label = ttk.Label(docker_frame, text="Unknown", font=('Arial', 9))
        self.docker_label.pack(side=tk.LEFT)

        # Manual controls
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X)

        self.ssh_connect_btn = ttk.Button(controls_frame, text="SSH Connect",
                                          command=self._on_ssh_connect, width=12)
        self.ssh_connect_btn.pack(side=tk.LEFT, padx=2)

        self.tcp_connect_btn = ttk.Button(controls_frame, text="TCP Connect",
                                          command=self._on_tcp_connect, width=12)
        self.tcp_connect_btn.pack(side=tk.LEFT, padx=2)

    def _create_ground_side_section(self, parent):
        """Create Ground-Side (H16) status section"""
        frame = ttk.LabelFrame(parent, text="📱 GROUND-SIDE (H16)", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # ADB Connection
        adb_frame = self._create_status_row(frame, "ADB Connected:")
        self.adb_indicator = StatusIndicator(adb_frame, size=14)
        self.adb_indicator.pack(side=tk.LEFT, padx=5)
        self.adb_label = ttk.Label(adb_frame, text="Not Connected", font=('Arial', 9))
        self.adb_label.pack(side=tk.LEFT)

        # Device Info
        device_frame = self._create_status_row(frame, "Device:")
        self.device_label = ttk.Label(device_frame, text="Unknown", font=('Arial', 9))
        self.device_label.pack(side=tk.LEFT)

        # Heartbeat
        hb_frame = self._create_status_row(frame, "💓 Heartbeat:")
        self.ground_hb_indicator = StatusIndicator(hb_frame, size=14)
        self.ground_hb_indicator.pack(side=tk.LEFT, padx=5)
        self.ground_hb_label = ttk.Label(hb_frame, text="No heartbeat", font=('Arial', 9))
        self.ground_hb_label.pack(side=tk.LEFT)

        # Camera Visibility
        cam_frame = self._create_status_row(frame, "📷 Camera:")
        self.ground_camera_indicator = StatusIndicator(cam_frame, size=14)
        self.ground_camera_indicator.pack(side=tk.LEFT, padx=5)
        self.ground_camera_label = ttk.Label(cam_frame, text="Unknown", font=('Arial', 9))
        self.ground_camera_label.pack(side=tk.LEFT)

        # Network Link
        network_frame = self._create_status_row(frame, "📡 Network:")
        self.network_indicator = StatusIndicator(network_frame, size=14)
        self.network_indicator.pack(side=tk.LEFT, padx=5)
        self.network_label = ttk.Label(network_frame, text="Unknown", font=('Arial', 9))
        self.network_label.pack(side=tk.LEFT)

        # Manual controls
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X)

        self.adb_connect_btn = ttk.Button(controls_frame, text="ADB Connect",
                                          command=self._on_adb_connect, width=12)
        self.adb_connect_btn.pack(side=tk.LEFT, padx=2)

        self.h16_test_btn = ttk.Button(controls_frame, text="Test Network",
                                       command=self._on_test_h16_network, width=12)
        self.h16_test_btn.pack(side=tk.LEFT, padx=2)

    def _create_camera_section(self, parent):
        """Create Camera (cross-domain) status section"""
        frame = ttk.LabelFrame(parent, text="📷 CAMERA STATUS", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Air → Camera
        air_cam_frame = self._create_status_row(frame, "Air → Camera:")
        self.air_to_camera_indicator = StatusIndicator(air_cam_frame, size=14)
        self.air_to_camera_indicator.pack(side=tk.LEFT, padx=5)
        self.air_to_camera_label = ttk.Label(air_cam_frame, text="Unknown", font=('Arial', 9))
        self.air_to_camera_label.pack(side=tk.LEFT)

        # Ground → Camera
        ground_cam_frame = self._create_status_row(frame, "Ground → Camera:")
        self.ground_to_camera_indicator = StatusIndicator(ground_cam_frame, size=14)
        self.ground_to_camera_indicator.pack(side=tk.LEFT, padx=5)
        self.ground_to_camera_label = ttk.Label(ground_cam_frame, text="Unknown", font=('Arial', 9))
        self.ground_to_camera_label.pack(side=tk.LEFT)

        # Parameters Status
        param_frame = self._create_status_row(frame, "📸 Parameters:")
        self.param_indicator = StatusIndicator(param_frame, size=14)
        self.param_indicator.pack(side=tk.LEFT, padx=5)
        self.param_label = ttk.Label(param_frame, text="No data", font=('Arial', 9))
        self.param_label.pack(side=tk.LEFT)

        # Camera Details (larger area)
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        details_label = ttk.Label(frame, text="Last Properties:", font=('Arial', 9, 'bold'))
        details_label.pack(anchor='w')

        self.camera_details_text = tk.Text(frame, height=6, font=('Courier', 8),
                                           wrap=tk.WORD, state=tk.DISABLED)
        self.camera_details_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Refresh button
        refresh_btn = ttk.Button(frame, text="Refresh Camera Status",
                                command=self._on_refresh_camera)
        refresh_btn.pack(fill=tk.X)

    def _create_status_row(self, parent, label_text: str) -> ttk.Frame:
        """Create a status row with label and returns frame for content"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=3)

        label = ttk.Label(row_frame, text=label_text, font=('Arial', 9, 'bold'), width=15)
        label.pack(side=tk.LEFT)

        content_frame = ttk.Frame(row_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        return content_frame

    # Connection Management Methods

    def set_tcp_client(self, client: TCPClient):
        """Set TCP client instance"""
        self.tcp_client = client
        client.on_connected = self._on_tcp_connected_callback
        client.on_disconnected = self._on_tcp_disconnected_callback
        client.on_message_received = self._on_tcp_message_callback
        client.on_error = self._on_tcp_error_callback

    def set_ssh_client(self, client: SSHClient):
        """Set SSH client instance"""
        self.ssh_client = client
        client.on_connected = self._on_ssh_connected_callback
        client.on_disconnected = self._on_ssh_disconnected_callback
        client.on_error = self._on_ssh_error_callback

    def set_adb_client(self, client: ADBClient):
        """Set ADB client instance"""
        self.adb_client = client
        client.on_connected = self._on_adb_connected_callback
        client.on_disconnected = self._on_adb_disconnected_callback
        client.on_error = self._on_adb_error_callback

    def _on_smart_connect(self):
        """Smart Connect - establish all connections"""
        self.log.append("🔌 Smart Connect: Establishing all connections...", "INFO")
        self.smart_connect_btn.config(state=tk.DISABLED)

        def connect_all():
            # Connect SSH
            self.log.append("  → Connecting SSH to Air-Side...", "INFO")
            if self.ssh_client:
                self.ssh_client.connect()
            elif self._create_ssh_client():
                self.ssh_client.connect()

            # Connect TCP
            self.log.append("  → Connecting TCP to Air-Side...", "INFO")
            if self.tcp_client:
                success = self.tcp_client.connect()
                if success:
                    self.tcp_client.send_handshake()
            elif self._create_tcp_client():
                success = self.tcp_client.connect()
                if success:
                    self.tcp_client.send_handshake()

            # Connect ADB
            self.log.append("  → Connecting ADB to H16...", "INFO")
            if self.adb_client:
                self.adb_client.connect()
            elif self._create_adb_client():
                self.adb_client.connect()

            # Enable disconnect button
            self.smart_disconnect_btn.config(state=tk.NORMAL)
            self.log.append("✓ Smart Connect complete", "SUCCESS")

        threading.Thread(target=connect_all, daemon=True).start()

    def _on_smart_disconnect(self):
        """Smart Disconnect - disconnect all connections"""
        self.log.append("Disconnecting all connections...", "INFO")

        if self.tcp_client and self.tcp_connected:
            self.tcp_client.disconnect()

        if self.ssh_client and self.ssh_connected:
            self.ssh_client.disconnect()

        if self.adb_client and self.adb_connected:
            self.adb_client.disconnect()

        self.smart_connect_btn.config(state=tk.NORMAL)
        self.smart_disconnect_btn.config(state=tk.DISABLED)
        self.log.append("✓ Disconnected all", "SUCCESS")

    def _create_tcp_client(self) -> bool:
        """Create TCP client if not exists"""
        if self.tcp_client:
            return True

        host = config.get("network", "air_side_ip", "10.0.1.53")
        port = config.get("network", "tcp_port", 5000)
        timeout = config.get("network", "connection_timeout_ms", 5000)

        self.tcp_client = TCPClient(host, port, timeout)
        self.set_tcp_client(self.tcp_client)
        return True

    def _create_ssh_client(self) -> bool:
        """Create SSH client if not exists"""
        if self.ssh_client:
            return True

        host = config.get("network", "air_side_ip", "10.0.1.53")
        username = config.get("ssh", "username", "dpm")
        password = config.get("ssh", "password", "2350")
        port = config.get("ssh", "port", 22)

        self.ssh_client = SSHClient(host, username, password, port)
        self.set_ssh_client(self.ssh_client)
        return True

    def _create_adb_client(self) -> bool:
        """Create ADB client if not exists"""
        if self.adb_client:
            return True

        self.adb_client = ADBClient()
        self.set_adb_client(self.adb_client)
        return True

    # Individual Connection Handlers

    def _on_ssh_connect(self):
        """Connect SSH only"""
        if self.ssh_connected:
            self.log.append("Already connected via SSH", "WARN")
            return

        self.log.append("Connecting SSH...", "INFO")
        if not self.ssh_client:
            self._create_ssh_client()

        threading.Thread(target=self.ssh_client.connect, daemon=True).start()

    def _on_tcp_connect(self):
        """Connect TCP only"""
        if self.tcp_connected:
            self.log.append("Already connected via TCP", "WARN")
            return

        self.log.append("Connecting TCP...", "INFO")
        if not self.tcp_client:
            self._create_tcp_client()

        def connect_and_handshake():
            success = self.tcp_client.connect()
            if success:
                self.tcp_client.send_handshake()

        threading.Thread(target=connect_and_handshake, daemon=True).start()

    def _on_adb_connect(self):
        """Connect ADB only"""
        if self.adb_connected:
            self.log.append("Already connected via ADB", "WARN")
            return

        self.log.append("Connecting ADB...", "INFO")
        if not self.adb_client:
            self._create_adb_client()

        threading.Thread(target=self.adb_client.connect, daemon=True).start()

    def _on_test_h16_network(self):
        """Test H16 network connectivity to Air-Side"""
        if not self.adb_connected or not self.adb_client:
            self.log.append("ADB not connected", "ERROR")
            return

        self.log.append("Testing H16 → Air-Side network...", "INFO")

        def test_network():
            air_ip = config.get("network", "air_side_ip", "10.0.1.53")
            success, latency = self.adb_client.ping_host(air_ip, count=3)

            if success:
                self.log.append(f"✓ H16 can reach Air-Side: {latency:.1f}ms average", "SUCCESS")
                self.network_indicator.set_status("green")
                self.network_label.config(text=f"{latency:.1f}ms")
            else:
                self.log.append("✗ H16 cannot reach Air-Side", "ERROR")
                self.network_indicator.set_status("red")
                self.network_label.config(text="No connection")

        threading.Thread(target=test_network, daemon=True).start()

    def _on_refresh_camera(self):
        """Refresh camera status"""
        self.log.append("Refreshing camera status...", "INFO")

        # This would typically query the camera dashboard tab or send a command
        # For now, just log it
        if self.tcp_connected and self.tcp_client:
            self.tcp_client.send_command("camera.get_properties", {})

    # Callbacks

    def _on_tcp_connected_callback(self):
        """TCP connected"""
        self.tcp_connected = True
        self.tcp_indicator.set_status("green")
        self.tcp_label.config(text="Connected")
        self.log.append("✓ TCP Connected", "SUCCESS")
        self._update_button_states()

    def _on_tcp_disconnected_callback(self):
        """TCP disconnected"""
        self.tcp_connected = False
        self.tcp_indicator.set_status("gray")
        self.tcp_label.config(text="Not Connected")
        self.log.append("TCP Disconnected", "INFO")
        self._update_button_states()

    def _on_tcp_message_callback(self, message: dict):
        """TCP message received"""
        msg_type = message.get("message_type", "unknown")

        # Check for camera status in responses
        if msg_type == "response":
            payload = message.get("payload", {})
            if "camera_connected" in payload:
                camera_connected = payload["camera_connected"]
                if camera_connected:
                    self.air_camera_indicator.set_status("green")
                    self.air_camera_label.config(text=payload.get("camera_model", "Connected"))
                else:
                    self.air_camera_indicator.set_status("red")
                    self.air_camera_label.config(text="Not detected")

    def _on_tcp_error_callback(self, error: str):
        """TCP error"""
        self.log.append(f"TCP Error: {error}", "ERROR")

    def _on_ssh_connected_callback(self):
        """SSH connected"""
        self.ssh_connected = True
        self.ssh_indicator.set_status("green")
        host = config.get("network", "air_side_ip", "10.0.1.53")
        self.ssh_label.config(text=f"{host}:22")
        self.log.append("✓ SSH Connected", "SUCCESS")
        self._update_button_states()

        # Check Docker status
        threading.Thread(target=self._check_docker_status, daemon=True).start()

    def _on_ssh_disconnected_callback(self):
        """SSH disconnected"""
        self.ssh_connected = False
        self.ssh_indicator.set_status("gray")
        self.ssh_label.config(text="Not Connected")
        self.docker_indicator.set_status("gray")
        self.docker_label.config(text="Unknown")
        self.log.append("SSH Disconnected", "INFO")
        self._update_button_states()

    def _on_ssh_error_callback(self, error: str):
        """SSH error"""
        self.log.append(f"SSH Error: {error}", "ERROR")

    def _on_adb_connected_callback(self):
        """ADB connected"""
        self.adb_connected = True
        self.adb_indicator.set_status("green")

        # Get device info
        if self.adb_client:
            info = self.adb_client.get_device_info()
            device_name = info.get('model', 'Unknown')
            self.adb_label.config(text=f"{device_name}")
            self.device_label.config(text=f"{device_name} (Android {info.get('android_version', '?')})")
            self.log.append(f"✓ ADB Connected: {device_name}", "SUCCESS")
        else:
            self.adb_label.config(text="Connected")
            self.log.append("✓ ADB Connected", "SUCCESS")

        self._update_button_states()

        # Test network connection to Air-Side
        threading.Thread(target=self._on_test_h16_network, daemon=True).start()

    def _on_adb_disconnected_callback(self):
        """ADB disconnected"""
        self.adb_connected = False
        self.adb_indicator.set_status("gray")
        self.adb_label.config(text="Not Connected")
        self.device_label.config(text="Unknown")
        self.network_indicator.set_status("gray")
        self.network_label.config(text="Unknown")
        self.log.append("ADB Disconnected", "INFO")
        self._update_button_states()

    def _on_adb_error_callback(self, error: str):
        """ADB error"""
        self.log.append(f"ADB Error: {error}", "ERROR")

    # Status Update Methods

    def _check_docker_status(self):
        """Check Docker container status via SSH"""
        if not self.ssh_client or not self.ssh_connected:
            return

        exit_code, stdout, stderr = self.ssh_client.execute_command("docker ps --filter name=payload-manager --format '{{.Status}}'")

        if exit_code == 0 and stdout.strip():
            # Container is running
            self.docker_indicator.set_status("green")
            status = stdout.strip().split()[0]  # Get first word (Up, Exited, etc.)
            self.docker_label.config(text=f"Running ({status})")
        else:
            # Container not running
            self.docker_indicator.set_status("red")
            self.docker_label.config(text="Not running")

    def on_heartbeat_received(self, sender: str, data: dict):
        """Called when heartbeat is received from Air or Ground"""
        current_time = datetime.now()

        if sender == "air":
            self.air_heartbeat_time = current_time
            self.air_hb_indicator.set_status("green")
            time_str = current_time.strftime("%H:%M:%S")
            self.air_hb_label.config(text=f"{time_str} (just now)")
        elif sender == "ground":
            self.ground_heartbeat_time = current_time
            self.ground_hb_indicator.set_status("green")
            time_str = current_time.strftime("%H:%M:%S")
            self.ground_hb_label.config(text=f"{time_str} (just now)")

    def on_camera_properties_received(self, properties: dict):
        """Called when camera properties are received"""
        self.camera_properties_time = datetime.now()
        self.camera_properties_count = len(properties)

        # Update parameter status
        self.param_indicator.set_status("green")
        time_ago = "just now"
        self.param_label.config(text=f"{self.camera_properties_count} properties ({time_ago})")

        # Update details text
        self.camera_details_text.config(state=tk.NORMAL)
        self.camera_details_text.delete(1.0, tk.END)

        details = []
        # Show key exposure triangle properties
        if "iso" in properties:
            details.append(f"ISO: {properties['iso']}")
        if "shutter_speed" in properties:
            details.append(f"Shutter: {properties['shutter_speed']}")
        if "aperture" in properties:
            details.append(f"Aperture: {properties['aperture']}")

        self.camera_details_text.insert(1.0, "\n".join(details) if details else "No properties available")
        self.camera_details_text.config(state=tk.DISABLED)

        # Update cross-domain indicators
        self.air_to_camera_indicator.set_status("green")
        self.air_to_camera_label.config(text="SDK Connected")

        self.ground_to_camera_indicator.set_status("green")
        self.ground_to_camera_label.config(text="Receiving data")

    def _update_all_status_indicators(self):
        """Update all status indicators based on current state"""
        # SSH
        if self.ssh_connected:
            self.ssh_indicator.set_status("green")
        else:
            self.ssh_indicator.set_status("gray")

        # TCP
        if self.tcp_connected:
            self.tcp_indicator.set_status("green")
        else:
            self.tcp_indicator.set_status("gray")

        # ADB
        if self.adb_connected:
            self.adb_indicator.set_status("green")
        else:
            self.adb_indicator.set_status("gray")

    def _update_button_states(self):
        """Update button states based on connections"""
        any_connected = self.tcp_connected or self.ssh_connected or self.adb_connected

        if any_connected:
            self.smart_disconnect_btn.config(state=tk.NORMAL)
        else:
            self.smart_disconnect_btn.config(state=tk.DISABLED)
            self.smart_connect_btn.config(state=tk.NORMAL)

    def _start_pulse_animation(self):
        """Start pulse animation thread for heartbeat indicators"""
        self.pulse_active = True

        def pulse_loop():
            while self.pulse_active:
                try:
                    # Update heartbeat time-ago labels
                    current_time = datetime.now()

                    if self.air_heartbeat_time:
                        seconds_ago = (current_time - self.air_heartbeat_time).total_seconds()
                        if seconds_ago < 5:
                            time_str = self.air_heartbeat_time.strftime("%H:%M:%S")
                            self.air_hb_label.config(text=f"{time_str} ({int(seconds_ago)}s ago)")
                        elif seconds_ago < 60:
                            self.air_hb_label.config(text=f"{int(seconds_ago)}s ago")
                            self.air_hb_indicator.set_status("yellow")
                        else:
                            self.air_hb_label.config(text="Timeout")
                            self.air_hb_indicator.set_status("red")

                    if self.ground_heartbeat_time:
                        seconds_ago = (current_time - self.ground_heartbeat_time).total_seconds()
                        if seconds_ago < 5:
                            time_str = self.ground_heartbeat_time.strftime("%H:%M:%S")
                            self.ground_hb_label.config(text=f"{time_str} ({int(seconds_ago)}s ago)")
                        elif seconds_ago < 60:
                            self.ground_hb_label.config(text=f"{int(seconds_ago)}s ago")
                            self.ground_hb_indicator.set_status("yellow")
                        else:
                            self.ground_hb_label.config(text="Timeout")
                            self.ground_hb_indicator.set_status("red")

                    if self.camera_properties_time:
                        seconds_ago = (current_time - self.camera_properties_time).total_seconds()
                        if seconds_ago < 5:
                            time_ago = "just now"
                        elif seconds_ago < 60:
                            time_ago = f"{int(seconds_ago)}s ago"
                        else:
                            time_ago = f"{int(seconds_ago / 60)}m ago"

                        self.param_label.config(text=f"{self.camera_properties_count} properties ({time_ago})")

                except Exception as e:
                    logger.error(f"Pulse animation error: {e}")

                time.sleep(1)

        self.pulse_thread = threading.Thread(target=pulse_loop, daemon=True)
        self.pulse_thread.start()

    # Log Management

    def _clear_log(self):
        """Clear the connection log"""
        if messagebox.askyesno("Clear Log", "Clear all connection log entries?"):
            self.log.clear()
            logger.info("Connection log cleared")

    def _save_log(self):
        """Save connection log to file"""
        default_dir = config.get("data", "log_directory", str(Path.home() / "Documents"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"connection_log_{timestamp}.txt"

        filepath = filedialog.asksaveasfilename(
            title="Save Connection Log",
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        )

        if filepath:
            try:
                log_content = self.log.get_all()

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("DPM Diagnostic Tool - Connection Log\n")
                    f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(log_content)

                config.set("data", "log_directory", str(Path(filepath).parent))

                logger.info(f"Connection log saved to: {filepath}")
                messagebox.showinfo("Success", f"Log saved successfully!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error saving log: {e}")
                messagebox.showerror("Error", f"Failed to save log:\n{e}")

    def cleanup(self):
        """Cleanup on exit"""
        self.pulse_active = False

        if self.tcp_client and self.tcp_connected:
            self.tcp_client.disconnect()

        if self.ssh_client and self.ssh_connected:
            self.ssh_client.disconnect()

        if self.adb_client and self.adb_connected:
            self.adb_client.disconnect()
