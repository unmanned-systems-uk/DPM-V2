"""
Camera Dashboard Tab for DPM Diagnostic Tool
Real-time camera status and property monitoring
Enhanced with Camera Control Testing Panel (Issue #55)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Dict, Any
from datetime import datetime
import json

from utils.logger import logger
from utils.protocol_loader import protocol
from network.protocol import protocol_msg


class CameraDashboardTab(ttk.Frame):
    """Camera Dashboard tab - real-time camera monitoring"""

    def __init__(self, parent):
        super().__init__(parent)

        self.camera_connected = False
        self.camera_properties = {}
        self.auto_refresh_enabled = False
        self.refresh_interval = 5000  # ms

        # Debug mode (Issue #55)
        self.debug_mode_enabled = False
        self.tcp_client = None
        self.last_command_time = None
        self.last_response_time = None

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

        # Debug Mode Section (Issue #55)
        self._create_debug_mode_section()

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

    def _create_debug_mode_section(self):
        """Create debug mode section with camera controls (Issue #55)"""
        # Debug Mode Frame
        debug_frame = ttk.LabelFrame(self, text="Camera Controls (Debug Mode)", padding=10)
        debug_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Debug Mode Toggle
        toggle_frame = ttk.Frame(debug_frame)
        toggle_frame.pack(fill=tk.X, pady=(0, 10))

        self.debug_mode_var = tk.BooleanVar(value=False)
        debug_check = ttk.Checkbutton(toggle_frame, text="Enable Debug Mode",
                                      variable=self.debug_mode_var,
                                      command=self._toggle_debug_mode)
        debug_check.pack(side=tk.LEFT)

        ttk.Label(toggle_frame, text="(Enable to show camera control testing panel)",
                 font=('Arial', 9, 'italic')).pack(side=tk.LEFT, padx=10)

        # Camera Controls Container (hidden by default)
        self.controls_container = ttk.Frame(debug_frame)

        # Create notebook for different control categories
        controls_notebook = ttk.Notebook(self.controls_container)
        controls_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Focus Controls
        focus_tab = ttk.Frame(controls_notebook)
        controls_notebook.add(focus_tab, text="Focus Controls")
        self._create_focus_controls(focus_tab)

        # Tab 2: Camera Settings
        settings_tab = ttk.Frame(controls_notebook)
        controls_notebook.add(settings_tab, text="Camera Settings")
        self._create_settings_controls(settings_tab)

        # Tab 3: Other Controls
        other_tab = ttk.Frame(controls_notebook)
        controls_notebook.add(other_tab, text="Other Controls")
        self._create_other_controls(other_tab)

        # Diagnostics Display (Issue #55 - expandable with copy support)
        diag_frame = ttk.LabelFrame(self.controls_container, text="Diagnostics Output", padding=5)
        diag_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Diagnostics text area - larger, expandable, selectable
        self.diagnostics_text = scrolledtext.ScrolledText(diag_frame, height=20, width=100,
                                                          font=('Consolas', 9), wrap=tk.WORD,
                                                          state='normal')  # Enable text selection
        self.diagnostics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure text tags for colored output
        self.diagnostics_text.tag_config("success", foreground="green")
        self.diagnostics_text.tag_config("error", foreground="red")
        self.diagnostics_text.tag_config("info", foreground="blue")
        self.diagnostics_text.tag_config("warning", foreground="orange")

        # Button frame for diagnostics controls
        diag_button_frame = ttk.Frame(diag_frame)
        diag_button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(diag_button_frame, text="Clear Diagnostics",
                  command=self._clear_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(diag_button_frame, text="Copy All to Clipboard",
                  command=self._copy_diagnostics_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(diag_button_frame, text="Copy Selection to Clipboard",
                  command=self._copy_selection_to_clipboard).pack(side=tk.LEFT, padx=5)

        # Info label
        ttk.Label(diag_button_frame, text="💡 Tip: Select text with mouse to copy",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.RIGHT, padx=5)

    def _create_focus_controls(self, parent):
        """Create focus control buttons"""
        # Focus Near/Far controls
        focus_frame = ttk.LabelFrame(parent, text="Manual Focus", padding=10)
        focus_frame.pack(fill=tk.X, padx=10, pady=10)

        # Speed selector
        speed_frame = ttk.Frame(focus_frame)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(speed_frame, text="Focus Speed:").pack(side=tk.LEFT, padx=5)

        self.focus_speed_var = tk.IntVar(value=2)
        for speed, label in [(1, "Slow (1)"), (2, "Medium (2)"), (3, "Fast (3)")]:
            ttk.Radiobutton(speed_frame, text=label, variable=self.focus_speed_var,
                           value=speed).pack(side=tk.LEFT, padx=5)

        # Focus buttons
        button_frame = ttk.Frame(focus_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Focus Near",
                  command=lambda: self._send_focus_command("near")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Focus Far",
                  command=lambda: self._send_focus_command("far")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Focus Stop",
                  command=lambda: self._send_focus_command("stop")).pack(side=tk.LEFT, padx=5)

        # AF Hold controls
        af_frame = ttk.LabelFrame(parent, text="Auto Focus Hold", padding=10)
        af_frame.pack(fill=tk.X, padx=10, pady=10)

        af_button_frame = ttk.Frame(af_frame)
        af_button_frame.pack(fill=tk.X)

        ttk.Button(af_button_frame, text="AF Hold Press",
                  command=lambda: self._send_af_hold_command("press")).pack(side=tk.LEFT, padx=5)
        ttk.Button(af_button_frame, text="AF Hold Release",
                  command=lambda: self._send_af_hold_command("release")).pack(side=tk.LEFT, padx=5)

    def _create_settings_controls(self, parent):
        """Create camera settings controls"""
        settings_frame = ttk.Frame(parent, padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Property selector
        prop_frame = ttk.LabelFrame(settings_frame, text="Set Camera Property", padding=10)
        prop_frame.pack(fill=tk.X, pady=5)

        # Property dropdown
        select_frame = ttk.Frame(prop_frame)
        select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(select_frame, text="Property:").pack(side=tk.LEFT, padx=5)
        self.property_var = tk.StringVar(value="shutter_speed")
        property_combo = ttk.Combobox(select_frame, textvariable=self.property_var,
                                     values=["shutter_speed", "aperture", "iso",
                                            "white_balance", "focus_mode", "file_format"],
                                     width=20, state='readonly')
        property_combo.pack(side=tk.LEFT, padx=5)

        # Value entry
        ttk.Label(select_frame, text="Value:").pack(side=tk.LEFT, padx=(20, 5))
        self.property_value_var = tk.StringVar()
        value_entry = ttk.Entry(select_frame, textvariable=self.property_value_var, width=20)
        value_entry.pack(side=tk.LEFT, padx=5)

        # Set button
        ttk.Button(select_frame, text="Set Property",
                  command=self._send_set_property_command).pack(side=tk.LEFT, padx=5)

        # Common values helper
        helper_frame = ttk.Frame(prop_frame)
        helper_frame.pack(fill=tk.X, pady=5)

        ttk.Label(helper_frame, text="Quick Values:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        ttk.Label(helper_frame, text="Shutter: 1/125, 1/250, 1/500 | ISO: 100, 200, 400, 800 | Aperture: 2.8, 4, 5.6, 8",
                 font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=5)

    def _create_other_controls(self, parent):
        """Create other control buttons"""
        controls_frame = ttk.Frame(parent, padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True)

        # Camera commands
        camera_frame = ttk.LabelFrame(controls_frame, text="Camera Commands", padding=10)
        camera_frame.pack(fill=tk.X, pady=5)

        button_frame = ttk.Frame(camera_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Take Photo (Single)",
                  command=self._send_capture_command).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Get Properties",
                  command=self._send_get_properties_command).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Get Status",
                  command=self._send_get_status_command).pack(side=tk.LEFT, padx=5, pady=5)

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
        # Helper to convert empty strings to "N/A"
        def get_prop(key, default="N/A"):
            value = properties.get(key, default)
            return value if value and str(value).strip() else "N/A"

        # Exposure triangle
        shutter = get_prop("shutter_speed")
        self.shutter_label.config(text=shutter)

        aperture = get_prop("aperture")
        self.aperture_label.config(text=f"f/{aperture}" if aperture != "N/A" else "N/A")

        iso = get_prop("iso")
        self.iso_label.config(text=iso)

        # Other properties
        wb = get_prop("white_balance")
        self.wb_label.config(text=wb)

        focus = get_prop("focus_mode")
        self.focus_label.config(text=focus)

        file_format = get_prop("file_format")
        self.format_label.config(text=file_format)

        drive = get_prop("drive_mode")
        self.drive_label.config(text=drive)

        exp_mode = get_prop("exposure_mode")
        self.exp_mode_label.config(text=exp_mode)

        flash = get_prop("flash_mode")
        self.flash_label.config(text=flash)

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

    # Debug Mode Methods (Issue #55)

    def set_tcp_client(self, tcp_client):
        """Set TCP client reference for sending commands"""
        self.tcp_client = tcp_client
        logger.debug("Camera tab: TCP client reference set")

    def handle_response(self, message: Dict[str, Any]):
        """Handle response messages from Air-Side (for debug mode)"""
        if not self.debug_mode_enabled:
            return

        msg_type = message.get("message_type", "unknown")

        # Only handle responses in debug mode
        if msg_type == "response":
            payload = message.get("payload", {})
            status = payload.get("status", "unknown")

            if status == "error":
                # Display error response
                error_code = payload.get("error_code", "N/A")
                error_msg = payload.get("message", "Unknown error")

                self._log_diagnostic(f"❌ ERROR RESPONSE from Air-Side:", "error")
                self._log_diagnostic(f"   Status: {status}", "error")
                self._log_diagnostic(f"   Error Code: {error_code}", "error")
                self._log_diagnostic(f"   Message: {error_msg}", "error")
                self._log_diagnostic(f"   Full Response: {json.dumps(message, indent=2)}", "error")

                # Calculate response time
                if self.last_command_time:
                    response_time = (datetime.now() - self.last_command_time).total_seconds() * 1000
                    self._log_diagnostic(f"   Response Time: {response_time:.1f} ms", "info")

            elif status == "success" or status == "ok":
                # Display success response
                self._log_diagnostic(f"✅ SUCCESS RESPONSE from Air-Side:", "success")
                self._log_diagnostic(f"   Status: {status}", "success")

                # Show relevant payload data
                if "property" in payload:
                    self._log_diagnostic(f"   Property: {payload.get('property')}", "success")
                    self._log_diagnostic(f"   Value: {payload.get('value')}", "success")

                self._log_diagnostic(f"   Full Response: {json.dumps(message, indent=2)}", "info")

                # Calculate response time
                if self.last_command_time:
                    response_time = (datetime.now() - self.last_command_time).total_seconds() * 1000
                    self._log_diagnostic(f"   Response Time: {response_time:.1f} ms", "info")
            else:
                # Unknown status
                self._log_diagnostic(f"⚠️ RESPONSE from Air-Side (status: {status}):", "warning")
                self._log_diagnostic(f"   Full Response: {json.dumps(message, indent=2)}", "info")

    def _toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode_enabled = self.debug_mode_var.get()

        if self.debug_mode_enabled:
            logger.info("Camera debug mode ENABLED")
            self.controls_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            self._log_diagnostic("Debug Mode enabled. Camera control testing panel active.", "info")
        else:
            logger.info("Camera debug mode DISABLED")
            self.controls_container.pack_forget()

    def _clear_diagnostics(self):
        """Clear diagnostics output"""
        self.diagnostics_text.delete(1.0, tk.END)
        logger.debug("Camera diagnostics cleared")

    def _copy_diagnostics_to_clipboard(self):
        """Copy all diagnostics text to clipboard"""
        try:
            # Get all text from diagnostics panel
            all_text = self.diagnostics_text.get(1.0, tk.END)

            # Clear clipboard and set new content
            self.clipboard_clear()
            self.clipboard_append(all_text)

            # Update clipboard to make it persistent
            self.update()

            self._log_diagnostic("✓ All diagnostics copied to clipboard", "info")
            logger.info("Diagnostics copied to clipboard (all text)")
        except Exception as e:
            self._log_diagnostic(f"ERROR: Failed to copy to clipboard: {e}", "error")
            logger.error(f"Failed to copy diagnostics to clipboard: {e}")

    def _copy_selection_to_clipboard(self):
        """Copy selected text to clipboard"""
        try:
            # Check if there's a selection
            if self.diagnostics_text.tag_ranges(tk.SEL):
                # Get selected text
                selected_text = self.diagnostics_text.get(tk.SEL_FIRST, tk.SEL_LAST)

                # Clear clipboard and set new content
                self.clipboard_clear()
                self.clipboard_append(selected_text)

                # Update clipboard to make it persistent
                self.update()

                self._log_diagnostic("✓ Selected text copied to clipboard", "info")
                logger.info("Diagnostics copied to clipboard (selection)")
            else:
                self._log_diagnostic("⚠ No text selected. Select text first, then click Copy Selection.", "warning")
                logger.warning("No text selected for clipboard copy")
        except Exception as e:
            self._log_diagnostic(f"ERROR: Failed to copy selection: {e}", "error")
            logger.error(f"Failed to copy selection to clipboard: {e}")

    def _log_diagnostic(self, message: str, level: str = "info"):
        """Log message to diagnostics panel with timestamp and color"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_message = f"[{timestamp}] {message}\n"

        self.diagnostics_text.insert(tk.END, formatted_message, level)
        self.diagnostics_text.see(tk.END)

    def _send_command_with_diagnostics(self, command_name: str, message: str):
        """Send command via TCP with automated diagnostics"""
        if not self.tcp_client or not self.tcp_client.connected:
            self._log_diagnostic("ERROR: TCP not connected to Air-Side", "error")
            logger.warning(f"Cannot send {command_name}: TCP not connected")
            return

        self._log_diagnostic(f"Sending command: {command_name}", "info")
        self._log_diagnostic(f"Command JSON: {message}", "info")

        try:
            self.last_command_time = datetime.now()
            success = self.tcp_client.send_message(message)

            if success:
                self._log_diagnostic("Command sent successfully", "success")
                logger.info(f"Sent {command_name} command")
            else:
                self._log_diagnostic("ERROR: Failed to send command", "error")
                logger.error(f"Failed to send {command_name} command")

        except Exception as e:
            self._log_diagnostic(f"ERROR: Exception sending command: {e}", "error")
            logger.error(f"Exception sending {command_name}: {e}")

    def _send_focus_command(self, action: str):
        """Send camera.focus command"""
        speed = self.focus_speed_var.get()
        self._log_diagnostic(f"=== Focus Command: action={action}, speed={speed} ===", "info")

        message = protocol_msg.create_camera_focus(action, speed)
        self._send_command_with_diagnostics(f"camera.focus({action})", message)

    def _send_af_hold_command(self, state: str):
        """Send camera.auto_focus_hold command"""
        self._log_diagnostic(f"=== AF Hold Command: state={state} ===", "info")

        message = protocol_msg.create_camera_auto_focus_hold(state)
        self._send_command_with_diagnostics(f"camera.auto_focus_hold({state})", message)

    def _send_set_property_command(self):
        """Send camera.set_property command"""
        property_name = self.property_var.get()
        property_value = self.property_value_var.get()

        if not property_value:
            self._log_diagnostic("ERROR: Property value is empty", "error")
            return

        self._log_diagnostic(f"=== Set Property: {property_name} = {property_value} ===", "info")

        message = protocol_msg.create_camera_set_property(property_name, property_value)
        self._send_command_with_diagnostics(f"camera.set_property({property_name})", message)

    def _send_capture_command(self):
        """Send camera.capture command"""
        self._log_diagnostic("=== Capture Photo Command ===", "info")

        message = protocol_msg.create_camera_capture("single")
        self._send_command_with_diagnostics("camera.capture", message)

    def _send_get_properties_command(self):
        """Send camera.get_properties command"""
        self._log_diagnostic("=== Get Properties Command ===", "info")

        # Request all common properties
        properties = ["shutter_speed", "aperture", "iso", "white_balance",
                     "focus_mode", "file_format", "drive_mode", "exposure_mode"]

        message = protocol_msg.create_camera_get_properties(properties)
        self._send_command_with_diagnostics("camera.get_properties", message)

    def _send_get_status_command(self):
        """Send system.get_status command"""
        self._log_diagnostic("=== Get Status Command ===", "info")

        message = protocol_msg.create_system_get_status()
        self._send_command_with_diagnostics("system.get_status", message)
