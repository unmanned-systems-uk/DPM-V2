"""
Command Sender Tab for DPM Diagnostic Tool
Manual command testing and protocol experimentation
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import time
from typing import Optional

from utils.logger import logger
from utils.protocol_loader import protocol
from network.tcp_client import TCPClient
from network.protocol import protocol_msg


class CommandSenderTab(ttk.Frame):
    """Command Sender tab"""

    def __init__(self, parent):
        super().__init__(parent)

        self.tcp_client: Optional[TCPClient] = None
        self.last_response = None
        self.last_response_time = 0

        self._create_ui()

        logger.debug("Command Sender tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Left panel: Quick commands and property setter
        left_panel = ttk.Frame(self)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Quick Commands
        self._create_quick_commands(left_panel)

        # Camera Property Setter
        self._create_property_setter(left_panel)

        # Custom Command Builder
        self._create_custom_command(left_panel)

        # Right panel: Response display
        right_panel = ttk.Frame(self)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._create_response_display(right_panel)

    def _create_quick_commands(self, parent):
        """Create quick command buttons"""
        frame = ttk.LabelFrame(parent, text="Quick Commands", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # Handshake
        ttk.Button(frame, text="Handshake", command=self._send_handshake, width=20).pack(pady=2)

        # camera.capture
        ttk.Button(frame, text="Camera Capture", command=self._send_capture, width=20).pack(pady=2)

        # system.get_status
        ttk.Button(frame, text="System Get Status", command=self._send_system_status, width=20).pack(pady=2)

        # camera.get_properties (all)
        ttk.Button(frame, text="Camera Get All Properties", command=self._send_get_properties, width=20).pack(pady=2)

        # Disconnect
        ttk.Button(frame, text="Disconnect", command=self._send_disconnect, width=20).pack(pady=2)

    def _create_property_setter(self, parent):
        """Create camera property setter"""
        frame = ttk.LabelFrame(parent, text="Camera Property Setter", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # Property selector
        ttk.Label(frame, text="Property:").pack(anchor='w')
        self.property_var = tk.StringVar()
        self.property_combo = ttk.Combobox(frame, textvariable=self.property_var, state="readonly", width=30)
        self.property_combo.pack(fill=tk.X, pady=2)
        self.property_combo.bind("<<ComboboxSelected>>", self._on_property_selected)

        # Value input (create BEFORE loading properties)
        ttk.Label(frame, text="Value:").pack(anchor='w', pady=(5,0))
        self.value_var = tk.StringVar()
        self.value_combo = ttk.Combobox(frame, textvariable=self.value_var, width=30)
        self.value_combo.pack(fill=tk.X, pady=2)

        # Set button
        ttk.Button(frame, text="Set Property", command=self._send_set_property).pack(pady=5)

        # Load properties (after all widgets are created)
        self._load_properties()

    def _create_custom_command(self, parent):
        """Create custom command builder"""
        frame = ttk.LabelFrame(parent, text="Custom Command Builder", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # JSON editor
        self.command_text = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD)
        self.command_text.pack(fill=tk.BOTH, expand=True)

        # Pre-fill with template
        template = {
            "message_type": "command",
            "sequence_id": 1,
            "timestamp": int(time.time() * 1000),
            "payload": {
                "command": "camera.capture",
                "parameters": {}
            }
        }
        self.command_text.insert(1.0, json.dumps(template, indent=2))

        # Send button
        ttk.Button(frame, text="Send Custom Command", command=self._send_custom).pack(pady=5)

    def _create_response_display(self, parent):
        """Create response display area"""
        # Last command sent
        cmd_frame = ttk.LabelFrame(parent, text="Last Command Sent", padding=5)
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.command_display = scrolledtext.ScrolledText(cmd_frame, height=8, wrap=tk.WORD)
        self.command_display.pack(fill=tk.BOTH, expand=True)

        # Last response received
        resp_frame = ttk.LabelFrame(parent, text="Last Response Received", padding=5)
        resp_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Response time and status
        status_frame = ttk.Frame(resp_frame)
        status_frame.pack(fill=tk.X, pady=2)

        ttk.Label(status_frame, text="Response Time:").pack(side=tk.LEFT)
        self.response_time_label = ttk.Label(status_frame, text="N/A", font=('Arial', 9, 'bold'))
        self.response_time_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=(20,0))
        self.response_status_label = ttk.Label(status_frame, text="N/A")
        self.response_status_label.pack(side=tk.LEFT, padx=5)

        self.response_display = scrolledtext.ScrolledText(resp_frame, height=8, wrap=tk.WORD)
        self.response_display.pack(fill=tk.BOTH, expand=True)

    def set_tcp_client(self, client: TCPClient):
        """Set TCP client for sending commands"""
        self.tcp_client = client

        # Set callback for responses
        if client:
            original_callback = client.on_message_received

            def response_callback(message):
                self._handle_response(message)
                if original_callback:
                    original_callback(message)

            client.on_message_received = response_callback

    def _load_properties(self):
        """Load camera properties from protocol definitions"""
        properties = protocol.get_all_properties()
        self.property_combo['values'] = properties

        if properties:
            self.property_combo.current(0)
            self._on_property_selected()

    def _on_property_selected(self, event=None):
        """Handle property selection"""
        property_name = self.property_var.get()

        # Get valid values for this property
        values = protocol.get_property_values(property_name)

        if values:
            # Enum property - show dropdown
            self.value_combo['values'] = values
            self.value_combo['state'] = "readonly"
            if values:
                self.value_combo.current(0)
        else:
            # Range or other property - allow text input
            self.value_combo['values'] = []
            self.value_combo['state'] = "normal"
            self.value_combo.set("")

    def _check_connection(self) -> bool:
        """Check if TCP client is connected"""
        if not self.tcp_client or not self.tcp_client.is_connected():
            messagebox.showerror("Not Connected", "Please connect to Air-Side first")
            return False
        return True

    def _send_command(self, message_str: str):
        """Send command and display it"""
        if not self._check_connection():
            return

        # Display command
        self.command_display.delete(1.0, tk.END)
        self.command_display.insert(1.0, message_str)

        # Send
        self.tcp_client.send_message(message_str)

        # Record send time
        self.last_response_time = time.time()

        logger.info(f"Command sent: {message_str[:100]}...")

    def _send_handshake(self):
        """Send handshake command"""
        message = protocol_msg.create_handshake()
        self._send_command(message)

    def _send_capture(self):
        """Send camera.capture command"""
        message = protocol_msg.create_camera_capture()
        self._send_command(message)

    def _send_system_status(self):
        """Send system.get_status command"""
        message = protocol_msg.create_system_get_status()
        self._send_command(message)

    def _send_get_properties(self):
        """Send camera.get_properties for all properties"""
        properties = protocol.get_all_properties()
        message = protocol_msg.create_camera_get_properties(properties)
        self._send_command(message)

    def _send_disconnect(self):
        """Send disconnect message"""
        message = protocol_msg.create_disconnect()
        self._send_command(message)

    def _send_set_property(self):
        """Send camera.set_property command"""
        if not self._check_connection():
            return

        property_name = self.property_var.get()
        value = self.value_var.get()

        if not property_name or not value:
            messagebox.showerror("Missing Data", "Please select property and value")
            return

        # Validate value
        if not protocol.validate_property_value(property_name, value):
            messagebox.showerror("Invalid Value", f"Invalid value for property {property_name}")
            return

        # Create and send command
        message = protocol_msg.create_camera_set_property(property_name, value)
        self._send_command(message)

    def _send_custom(self):
        """Send custom command"""
        if not self._check_connection():
            return

        # Get command text
        command_str = self.command_text.get(1.0, tk.END).strip()

        # Validate JSON
        try:
            json.loads(command_str)  # Check if valid JSON
        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", f"Command is not valid JSON:\n{e}")
            return

        # Send
        self._send_command(command_str)

    def _handle_response(self, message: dict):
        """Handle received response"""
        # Calculate response time
        response_time = (time.time() - self.last_response_time) * 1000  # ms

        # Display response
        self.response_display.delete(1.0, tk.END)
        formatted = json.dumps(message, indent=2)
        self.response_display.insert(1.0, formatted)

        # Update response time
        self.response_time_label.config(text=f"{response_time:.0f} ms")

        # Update status
        if protocol_msg.is_response(message):
            if protocol_msg.is_error(message):
                self.response_status_label.config(text="ERROR", foreground="red")
            else:
                self.response_status_label.config(text="SUCCESS", foreground="green")
        else:
            self.response_status_label.config(text=message.get("message_type", "unknown"))
