"""
Log Inspector Tab for DPM Diagnostic Tool
View Air-Side Docker container logs via SSH
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading

from utils.logger import logger
from utils.config import config
from network.ssh_client import SSHClient


class LogInspectorTab(ttk.Frame):
    """Log Inspector tab - view Air-Side logs remotely"""

    def __init__(self, parent):
        super().__init__(parent)

        self.ssh_client: Optional[SSHClient] = None
        self.auto_refresh_enabled = False
        self.refresh_interval = 5000  # ms
        self.current_logs = ""

        # Follow mode (live streaming)
        self.follow_enabled = False
        self.follow_thread: Optional[threading.Thread] = None
        self.follow_stop_event: Optional[threading.Event] = None

        self._create_ui()

        logger.debug("Log Inspector tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: SSH Connection controls
        connection_frame = ttk.LabelFrame(self, text="SSH Connection", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)

        # Connection status
        status_row = ttk.Frame(connection_frame)
        status_row.pack(fill=tk.X, pady=5)

        ttk.Label(status_row, text="Status:").pack(side=tk.LEFT, padx=5)
        self.ssh_status_indicator = tk.Canvas(status_row, width=20, height=20, highlightthickness=0)
        self.ssh_status_indicator.pack(side=tk.LEFT, padx=5)
        self._update_ssh_indicator(False)

        self.ssh_status_label = ttk.Label(status_row, text="Disconnected", font=('Arial', 9, 'bold'))
        self.ssh_status_label.pack(side=tk.LEFT, padx=5)

        # Connect/Disconnect buttons
        button_row = ttk.Frame(connection_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.connect_btn = ttk.Button(button_row, text="Connect SSH", command=self._connect_ssh)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = ttk.Button(button_row, text="Disconnect", command=self._disconnect_ssh, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)

        # SSH info label
        ssh_config = self._get_ssh_config()
        ttk.Label(button_row, text=f"Air-Side: {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}",
                 font=('Arial', 9, 'italic')).pack(side=tk.LEFT, padx=20)

        # Log View Controls
        controls_frame = ttk.LabelFrame(self, text="Log View Options", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # View mode selection
        mode_row = ttk.Frame(controls_frame)
        mode_row.pack(fill=tk.X, pady=5)

        ttk.Label(mode_row, text="View Mode:").pack(side=tk.LEFT, padx=5)

        self.view_mode_var = tk.StringVar(value="tail")
        ttk.Radiobutton(mode_row, text="Last 100 lines", variable=self.view_mode_var,
                       value="tail", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_row, text="Last 500 lines", variable=self.view_mode_var,
                       value="tail_500", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_row, text="All logs", variable=self.view_mode_var,
                       value="all", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)

        # Time filter
        time_row = ttk.Frame(controls_frame)
        time_row.pack(fill=tk.X, pady=5)

        ttk.Label(time_row, text="Time Filter:").pack(side=tk.LEFT, padx=5)

        self.time_filter_var = tk.StringVar(value="none")
        ttk.Radiobutton(time_row, text="None", variable=self.time_filter_var,
                       value="none", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 5 min", variable=self.time_filter_var,
                       value="5m", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 30 min", variable=self.time_filter_var,
                       value="30m", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(time_row, text="Last 1 hour", variable=self.time_filter_var,
                       value="1h", command=self._on_view_mode_changed).pack(side=tk.LEFT, padx=5)

        # Refresh controls
        refresh_row = ttk.Frame(controls_frame)
        refresh_row.pack(fill=tk.X, pady=5)

        ttk.Button(refresh_row, text="Refresh Now", command=self._refresh_logs).pack(side=tk.LEFT, padx=5)

        # Follow logs toggle (real-time streaming)
        self.follow_var = tk.BooleanVar(value=False)
        self.follow_check = ttk.Checkbutton(refresh_row, text="Follow Logs (live)",
                                            variable=self.follow_var,
                                            command=self._toggle_follow)
        self.follow_check.pack(side=tk.LEFT, padx=5)

        ttk.Separator(refresh_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.auto_refresh_check = ttk.Checkbutton(refresh_row, text="Auto-refresh",
                                                   variable=self.auto_refresh_var,
                                                   command=self._toggle_auto_refresh)
        self.auto_refresh_check.pack(side=tk.LEFT, padx=5)

        ttk.Label(refresh_row, text="Interval (sec):").pack(side=tk.LEFT, padx=(20, 5))
        self.interval_var = tk.IntVar(value=5)
        interval_spin = ttk.Spinbox(refresh_row, from_=1, to=60, textvariable=self.interval_var,
                                   width=5, command=self._update_refresh_interval)
        interval_spin.pack(side=tk.LEFT, padx=5)

        # Last update time
        ttk.Label(refresh_row, text="Last Updated:").pack(side=tk.RIGHT, padx=5)
        self.last_update_label = ttk.Label(refresh_row, text="Never", font=('Arial', 9, 'italic'))
        self.last_update_label.pack(side=tk.RIGHT, padx=5)

        # Search bar
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        ttk.Button(search_frame, text="Clear Search", command=self._clear_search).pack(side=tk.LEFT, padx=5)

        # Log display
        log_frame = ttk.LabelFrame(self, text="Docker Logs (payload-manager)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 9))
        self.log_text.config(state=tk.DISABLED)  # Read-only

        # Scrollbars
        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.log_text.xview)
        self.log_text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.log_text.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Configure text tags for highlighting
        self.log_text.tag_config("highlight", background="yellow")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")

        # Bottom controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(bottom_frame, text="Clear Display", command=self._clear_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Save to File...", command=self._save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Copy All", command=self._copy_all).pack(side=tk.LEFT, padx=5)

        # Line count label
        self.line_count_label = ttk.Label(bottom_frame, text="Lines: 0")
        self.line_count_label.pack(side=tk.RIGHT, padx=10)

    def _get_ssh_config(self) -> dict:
        """Get SSH configuration from config"""
        return {
            "host": config.get("network", "air_side_ip", "10.0.1.53"),
            "username": config.get("ssh", "username", "dpm"),
            "password": config.get("ssh", "password", "2350"),
            "port": config.get("ssh", "port", 22)
        }

    def _update_ssh_indicator(self, connected: bool):
        """Update SSH connection indicator"""
        self.ssh_status_indicator.delete("all")
        color = "green" if connected else "gray"
        self.ssh_status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _connect_ssh(self):
        """Connect to Air-Side SSH"""
        logger.info("Connecting SSH to Air-Side...")

        ssh_config = self._get_ssh_config()

        # Create SSH client
        self.ssh_client = SSHClient(
            host=ssh_config["host"],
            username=ssh_config["username"],
            password=ssh_config["password"],
            port=ssh_config["port"]
        )

        # Set callbacks
        self.ssh_client.on_connected = self._on_ssh_connected
        self.ssh_client.on_disconnected = self._on_ssh_disconnected
        self.ssh_client.on_error = self._on_ssh_error

        # Connect in background thread
        self.connect_btn.config(state=tk.DISABLED, text="Connecting...")
        self.ssh_client.connect_async()

    def _disconnect_ssh(self):
        """Disconnect from Air-Side SSH"""
        if self.ssh_client:
            self.ssh_client.disconnect()

    def _on_ssh_connected(self):
        """Callback when SSH connected"""
        # Update UI on main thread
        self.after(0, self._update_ssh_connected_ui)

    def _update_ssh_connected_ui(self):
        """Update UI after SSH connection"""
        self._update_ssh_indicator(True)
        self.ssh_status_label.config(text="Connected", foreground="green")
        self.connect_btn.config(state=tk.DISABLED, text="Connect SSH")
        self.disconnect_btn.config(state=tk.NORMAL)

        logger.info("SSH connected - fetching initial logs")
        self._refresh_logs()

    def _on_ssh_disconnected(self):
        """Callback when SSH disconnected"""
        # Update UI on main thread
        self.after(0, self._update_ssh_disconnected_ui)

    def _update_ssh_disconnected_ui(self):
        """Update UI after SSH disconnection"""
        self._update_ssh_indicator(False)
        self.ssh_status_label.config(text="Disconnected", foreground="gray")
        self.connect_btn.config(state=tk.NORMAL, text="Connect SSH")
        self.disconnect_btn.config(state=tk.DISABLED)

        # Stop auto-refresh
        self.auto_refresh_var.set(False)
        self.auto_refresh_enabled = False

    def _on_ssh_error(self, error_msg: str):
        """Callback when SSH error occurs"""
        # Show error on main thread
        self.after(0, lambda: self._show_ssh_error(error_msg))

    def _show_ssh_error(self, error_msg: str):
        """Show SSH error message"""
        messagebox.showerror("SSH Error", error_msg)
        self._update_ssh_disconnected_ui()

    def _on_view_mode_changed(self, event=None):
        """Handle view mode change"""
        if self.ssh_client and self.ssh_client.is_connected():
            self._refresh_logs()

    def _refresh_logs(self):
        """Refresh logs from Air-Side"""
        if not self.ssh_client or not self.ssh_client.is_connected():
            messagebox.showwarning("Not Connected", "Please connect SSH first")
            return

        # Determine parameters based on view mode
        tail = None
        since = None

        view_mode = self.view_mode_var.get()
        if view_mode == "tail":
            tail = 100
        elif view_mode == "tail_500":
            tail = 500

        time_filter = self.time_filter_var.get()
        if time_filter != "none":
            since = time_filter

        # Fetch logs in background thread
        def fetch_logs():
            exit_code, stdout, stderr = self.ssh_client.get_docker_logs(
                container="payload-manager",
                tail=tail,
                since=since
            )

            if exit_code == 0:
                # Update UI on main thread
                self.after(0, lambda: self._update_log_display(stdout))
            else:
                error_msg = stderr if stderr else "Failed to fetch logs"
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch logs:\n{error_msg}"))

        import threading
        threading.Thread(target=fetch_logs, daemon=True).start()

    def _update_log_display(self, logs: str):
        """Update log text display"""
        self.current_logs = logs

        # Apply search filter if active
        search_text = self.search_var.get().lower()
        if search_text:
            display_logs = self._filter_logs(logs, search_text)
        else:
            display_logs = logs

        # Update text widget
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(1.0, display_logs)

        # Apply syntax highlighting
        self._apply_highlighting()

        self.log_text.config(state=tk.DISABLED)

        # Scroll to bottom
        self.log_text.see(tk.END)

        # Update statistics
        line_count = len(display_logs.splitlines())
        self.line_count_label.config(text=f"Lines: {line_count}")
        self.last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _filter_logs(self, logs: str, search_text: str) -> str:
        """Filter logs by search text"""
        filtered_lines = []
        for line in logs.splitlines():
            if search_text in line.lower():
                filtered_lines.append(line)
        return "\n".join(filtered_lines)

    def _apply_highlighting(self):
        """Apply syntax highlighting to log text"""
        content = self.log_text.get(1.0, tk.END)
        lines = content.splitlines()

        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Highlight errors
            if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower:
                self.log_text.tag_add("error", f"{i}.0", f"{i}.end")

            # Highlight warnings
            elif "warning" in line_lower or "warn" in line_lower:
                self.log_text.tag_add("warning", f"{i}.0", f"{i}.end")

            # Highlight info
            elif "info" in line_lower:
                self.log_text.tag_add("info", f"{i}.0", f"{i}.end")

        # Highlight search matches
        search_text = self.search_var.get()
        if search_text:
            start_idx = "1.0"
            while True:
                start_idx = self.log_text.search(search_text, start_idx, nocase=True, stopindex=tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(search_text)}c"
                self.log_text.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

    def _on_search_changed(self, event=None):
        """Handle search text change"""
        # Re-display with filter
        if self.current_logs:
            self._update_log_display(self.current_logs)

    def _clear_search(self):
        """Clear search filter"""
        self.search_var.set("")
        if self.current_logs:
            self._update_log_display(self.current_logs)

    def _toggle_follow(self):
        """Toggle follow logs (live streaming) on/off"""
        self.follow_enabled = self.follow_var.get()

        if self.follow_enabled:
            if not self.ssh_client or not self.ssh_client.is_connected():
                messagebox.showwarning("Not Connected", "Please connect SSH first")
                self.follow_var.set(False)
                self.follow_enabled = False
                return

            # Disable auto-refresh when following
            if self.auto_refresh_enabled:
                self.auto_refresh_var.set(False)
                self.auto_refresh_enabled = False

            logger.info("Starting to follow Docker logs in real-time...")
            self._start_follow()

        else:
            logger.info("Stopping log follow...")
            self._stop_follow()

    def _start_follow(self):
        """Start following logs in background thread"""
        # Clear current logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Create stop event
        self.follow_stop_event = threading.Event()

        # Get tail parameter from view mode
        tail = None
        view_mode = self.view_mode_var.get()
        if view_mode == "tail":
            tail = 100
        elif view_mode == "tail_500":
            tail = 500

        # Start follow thread
        def follow_worker():
            self.ssh_client.follow_docker_logs(
                container="payload-manager",
                tail=tail,
                on_log_line=self._on_log_line_received,
                stop_event=self.follow_stop_event
            )

        self.follow_thread = threading.Thread(target=follow_worker, daemon=True)
        self.follow_thread.start()

        # Update UI
        self.last_update_label.config(text="Following...")

    def _stop_follow(self):
        """Stop following logs"""
        if self.follow_stop_event:
            self.follow_stop_event.set()

        if self.follow_thread and self.follow_thread.is_alive():
            # Give it a moment to stop
            self.follow_thread.join(timeout=2.0)

        self.follow_thread = None
        self.follow_stop_event = None

        # Update UI
        self.last_update_label.config(text=datetime.now().strftime("%H:%M:%S"))

    def _on_log_line_received(self, line: str):
        """Callback for each new log line (called from follow thread)"""
        # Schedule GUI update on main thread
        self.after(0, lambda: self._append_log_line(line))

    def _append_log_line(self, line: str):
        """Append a log line to the display"""
        # Enable editing
        self.log_text.config(state=tk.NORMAL)

        # Append line
        self.log_text.insert(tk.END, line + "\n")

        # Apply highlighting to the new line
        line_number = int(self.log_text.index(tk.END).split('.')[0]) - 1
        line_lower = line.lower()

        if "error" in line_lower or "exception" in line_lower or "traceback" in line_lower:
            self.log_text.tag_add("error", f"{line_number}.0", f"{line_number}.end")
        elif "warning" in line_lower or "warn" in line_lower:
            self.log_text.tag_add("warning", f"{line_number}.0", f"{line_number}.end")
        elif "info" in line_lower:
            self.log_text.tag_add("info", f"{line_number}.0", f"{line_number}.end")

        # Auto-scroll to bottom
        self.log_text.see(tk.END)

        # Disable editing
        self.log_text.config(state=tk.DISABLED)

        # Update line count
        total_lines = int(self.log_text.index(tk.END).split('.')[0]) - 1
        self.line_count_label.config(text=f"Lines: {total_lines}")

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()

        if self.auto_refresh_enabled:
            if not self.ssh_client or not self.ssh_client.is_connected():
                messagebox.showwarning("Not Connected", "Please connect SSH first")
                self.auto_refresh_var.set(False)
                self.auto_refresh_enabled = False
                return

            # Disable follow mode when auto-refreshing
            if self.follow_enabled:
                self.follow_var.set(False)
                self._stop_follow()
                self.follow_enabled = False

            logger.info(f"Log auto-refresh enabled ({self.interval_var.get()}s)")
            self._schedule_refresh()
        else:
            logger.info("Log auto-refresh disabled")

    def _update_refresh_interval(self):
        """Update refresh interval"""
        self.refresh_interval = self.interval_var.get() * 1000  # Convert to ms
        logger.debug(f"Log refresh interval set to {self.interval_var.get()}s")

    def _schedule_refresh(self):
        """Schedule next auto-refresh"""
        if self.auto_refresh_enabled:
            self._refresh_logs()
            self.after(self.refresh_interval, self._schedule_refresh)

    def _clear_display(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.line_count_label.config(text="Lines: 0")

    def _save_logs(self):
        """Save logs to file"""
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to save")
            return

        # Get save location
        default_dir = config.get("data", "log_directory", str(Path.home() / "Documents"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            initialdir=default_dir,
            initialfile=f"air_side_logs_{timestamp}.log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.current_logs)

                logger.info(f"Logs saved to: {filepath}")
                messagebox.showinfo("Success", f"Logs saved!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error saving logs: {e}")
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _copy_all(self):
        """Copy all logs to clipboard"""
        if not self.current_logs:
            messagebox.showinfo("No Data", "No logs to copy")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(self.current_logs)
            self.update()

            messagebox.showinfo("Success", "Logs copied to clipboard!")

        except Exception as e:
            logger.error(f"Error copying logs: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def cleanup(self):
        """Cleanup on tab close"""
        # Stop following if active
        if self.follow_enabled:
            self._stop_follow()

        # Stop auto-refresh if active
        if self.auto_refresh_enabled:
            self.auto_refresh_enabled = False

        # Disconnect SSH
        if self.ssh_client and self.ssh_client.is_connected():
            self.ssh_client.disconnect()
