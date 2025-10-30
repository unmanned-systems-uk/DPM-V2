"""
Remote Control Tab for DPM Diagnostic Tool
Execute common SSH commands on Air-Side SBC with one-click buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
import threading

from utils.logger import logger
from utils.config import config


class RemoteControlTab(ttk.Frame):
    """Remote Control tab - execute common SSH commands"""

    def __init__(self, parent, log_inspector_tab):
        super().__init__(parent)

        self.log_inspector_tab = log_inspector_tab  # Reference to Log Inspector tab to access SSH client

        self._create_ui()

        logger.debug("Remote Control tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Instructions
        info_frame = ttk.LabelFrame(self, text="Remote Control Panel", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text="Execute common system commands on Air-Side SBC via SSH",
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        # SSH connection status
        self.ssh_status_label = ttk.Label(info_frame, text="SSH: Not Connected",
                                         foreground="gray", font=('Arial', 9, 'bold'))
        self.ssh_status_label.pack(side=tk.RIGHT, padx=10)

        # Command buttons organized by category
        # Docker Control
        docker_frame = ttk.LabelFrame(self, text="Docker Container Control", padding=10)
        docker_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(docker_frame, text="Restart payload-manager",
                  command=lambda: self._execute_command("docker restart payload-manager",
                                                       "Restarting payload-manager container...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(docker_frame, text="Stop payload-manager",
                  command=lambda: self._execute_command("docker stop payload-manager",
                                                       "Stopping payload-manager container...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(docker_frame, text="Start payload-manager",
                  command=lambda: self._execute_command("docker start payload-manager",
                                                       "Starting payload-manager container...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(docker_frame, text="View Docker Status",
                  command=lambda: self._execute_command("docker ps -a",
                                                       "Checking container status...")).pack(side=tk.LEFT, padx=5, pady=5)

        # System Control
        system_frame = ttk.LabelFrame(self, text="System Control", padding=10)
        system_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(system_frame, text="Reboot SBC",
                  command=self._confirm_reboot,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(system_frame, text="Check System Status",
                  command=lambda: self._execute_command("uptime && df -h / && free -h",
                                                       "Checking system status...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(system_frame, text="View Running Processes",
                  command=lambda: self._execute_command("ps aux | head -20",
                                                       "Fetching top processes...")).pack(side=tk.LEFT, padx=5, pady=5)

        # Docker Service Control
        service_frame = ttk.LabelFrame(self, text="Docker Service Control", padding=10)
        service_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(service_frame, text="Restart Docker Service",
                  command=lambda: self._execute_command("sudo systemctl restart docker",
                                                       "Restarting Docker service...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(service_frame, text="Stop Docker Service",
                  command=lambda: self._execute_command("sudo systemctl stop docker",
                                                       "Stopping Docker service...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(service_frame, text="Start Docker Service",
                  command=lambda: self._execute_command("sudo systemctl start docker",
                                                       "Starting Docker service...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(service_frame, text="Docker Service Status",
                  command=lambda: self._execute_command("sudo systemctl status docker",
                                                       "Checking Docker service status...")).pack(side=tk.LEFT, padx=5, pady=5)

        # Network Diagnostics
        network_frame = ttk.LabelFrame(self, text="Network Diagnostics", padding=10)
        network_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(network_frame, text="Check Network Interfaces",
                  command=lambda: self._execute_command("ip addr show",
                                                       "Checking network interfaces...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(network_frame, text="Check Open Ports",
                  command=lambda: self._execute_command("sudo netstat -tulpn | grep LISTEN",
                                                       "Checking listening ports...")).pack(side=tk.LEFT, padx=5, pady=5)

        # Output display
        output_frame = ttk.LabelFrame(self, text="Command Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD,
                                                     font=('Courier', 9), height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for colored output
        self.output_text.tag_config("command", foreground="blue", font=('Courier', 9, 'bold'))
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("info", foreground="gray")

        # Bottom controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(bottom_frame, text="Clear Output",
                  command=self._clear_output).pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Copy Output",
                  command=self._copy_output).pack(side=tk.LEFT, padx=5)

        # Status
        self.status_label = ttk.Label(bottom_frame, text="Ready",
                                     font=('Arial', 9, 'italic'))
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def update_ssh_status(self, connected: bool):
        """Update SSH connection status indicator"""
        if connected:
            self.ssh_status_label.config(text="SSH: Connected", foreground="green")
        else:
            self.ssh_status_label.config(text="SSH: Not Connected", foreground="gray")

    def _confirm_reboot(self):
        """Confirm before rebooting SBC"""
        result = messagebox.askyesno(
            "Confirm Reboot",
            "Are you sure you want to reboot the Air-Side SBC?\n\n"
            "This will disconnect all services and restart the system.",
            icon='warning'
        )
        if result:
            self._execute_command("sudo reboot", "Rebooting SBC...")

    def _execute_command(self, command: str, status_msg: str):
        """Execute SSH command in background thread"""
        # Get current SSH client from Log Inspector tab
        ssh_client = self.log_inspector_tab.ssh_client if self.log_inspector_tab else None

        if not ssh_client or not ssh_client.is_connected():
            messagebox.showwarning("Not Connected",
                                  "SSH connection required.\nPlease connect in Log Inspector tab first.")
            return

        # Update status
        self.status_label.config(text=status_msg)

        # Display command
        self._append_output(f"\n$ {command}\n", "command")

        # Execute in background thread
        def run_command():
            try:
                exit_code, stdout, stderr = ssh_client.execute_command(command, timeout=30)

                # Schedule UI update on main thread
                self.after(0, lambda: self._display_result(exit_code, stdout, stderr))

            except Exception as e:
                self.after(0, lambda: self._display_error(str(e)))

        threading.Thread(target=run_command, daemon=True).start()

    def _display_result(self, exit_code: int, stdout: str, stderr: str):
        """Display command result"""
        if exit_code == 0:
            self._append_output(stdout, "success")
            if stderr:
                self._append_output(f"\nWarnings:\n{stderr}", "info")
            self.status_label.config(text="Command completed successfully")
        else:
            self._append_output(f"Exit code: {exit_code}\n", "error")
            if stdout:
                self._append_output(stdout, "info")
            if stderr:
                self._append_output(f"\nErrors:\n{stderr}", "error")
            self.status_label.config(text="Command failed")

        self._append_output("\n" + "=" * 80 + "\n", "info")

    def _display_error(self, error_msg: str):
        """Display error message"""
        self._append_output(f"ERROR: {error_msg}\n", "error")
        self._append_output("=" * 80 + "\n", "info")
        self.status_label.config(text="Command failed")

    def _append_output(self, text: str, tag: Optional[str] = None):
        """Append text to output display"""
        self.output_text.config(state=tk.NORMAL)
        if tag:
            self.output_text.insert(tk.END, text, tag)
        else:
            self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _clear_output(self):
        """Clear output display"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_label.config(text="Output cleared")

    def _copy_output(self):
        """Copy output to clipboard"""
        try:
            output = self.output_text.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(output)
            self.update()
            messagebox.showinfo("Success", "Output copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{e}")
