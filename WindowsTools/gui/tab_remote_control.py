"""
Remote Control Tab for DPM Diagnostic Tool
Execute common SSH commands on Air-Side SBC with one-click buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Optional
import threading
from datetime import datetime

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

        # Smart Diagnostic Button (prominent)
        diagnostic_frame = ttk.Frame(self)
        diagnostic_frame.pack(fill=tk.X, padx=10, pady=10)

        self.diagnostic_btn = ttk.Button(diagnostic_frame, text="🔍 Run Smart Diagnostic",
                                        command=self._run_smart_diagnostic)
        self.diagnostic_btn.pack(pady=5)

        ttk.Label(diagnostic_frame, text="Automated system health check with comprehensive analysis",
                 font=('Arial', 8, 'italic'), foreground="gray").pack()

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

        # Docker Service Control - Note: Service control commands require sudo privileges
        service_frame = ttk.LabelFrame(self, text="Docker Service Information", padding=10)
        service_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(service_frame, text="Docker Service Status",
                  command=lambda: self._execute_command("systemctl status docker --no-pager",
                                                       "Checking Docker service status...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(service_frame, text="Docker Version Info",
                  command=lambda: self._execute_command("docker version",
                                                       "Checking Docker version...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(service_frame, text="Docker Info",
                  command=lambda: self._execute_command("docker info",
                                                       "Getting Docker system info...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(service_frame, text="(Service restart requires sudo access)",
                 font=('Arial', 8, 'italic'), foreground="gray").pack(side=tk.LEFT, padx=10)

        # Network Diagnostics
        network_frame = ttk.LabelFrame(self, text="Network Diagnostics", padding=10)
        network_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(network_frame, text="Check Network Interfaces",
                  command=lambda: self._execute_command("ip addr show",
                                                       "Checking network interfaces...")).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(network_frame, text="Check Open Ports",
                  command=lambda: self._execute_command("ss -tuln",
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

        ttk.Button(bottom_frame, text="Copy Selected",
                  command=self._copy_selected).pack(side=tk.LEFT, padx=5)

        ttk.Button(bottom_frame, text="Save Report",
                  command=self._save_report).pack(side=tk.LEFT, padx=5)

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
            "This will disconnect all services and restart the system.\n\n"
            "NOTE: This requires sudo privileges and may fail if not configured.",
            icon='warning'
        )
        if result:
            self._execute_command("reboot", "Rebooting SBC...")

    def _run_smart_diagnostic(self):
        """Run comprehensive automated diagnostic checks"""
        # Get current SSH client
        ssh_client = self.log_inspector_tab.ssh_client if self.log_inspector_tab else None

        if not ssh_client or not ssh_client.is_connected():
            messagebox.showwarning("Not Connected",
                                  "SSH connection required.\nPlease connect in Log Inspector tab first.")
            return

        # Clear output and show header
        self._clear_output()
        self._append_output("=" * 80 + "\n", "info")
        self._append_output("  SMART DIAGNOSTIC REPORT\n", "command")
        self._append_output("  Automated System Health Check\n", "command")
        self._append_output("=" * 80 + "\n\n", "info")

        # Update status and disable button
        self.status_label.config(text="Running Smart Diagnostic...")
        self.diagnostic_btn.config(state=tk.DISABLED)

        # Run diagnostics in background thread
        def run_diagnostics():
            try:
                report = []
                issues_found = []
                warnings_found = []

                # 1. System Health Check
                self.after(0, lambda: self._append_output("📊 SYSTEM HEALTH\n", "command"))

                # Uptime and load
                exit_code, stdout, stderr = ssh_client.execute_command("uptime", timeout=10)
                if exit_code == 0:
                    uptime_info = stdout.strip()
                    report.append(("Uptime", uptime_info, "ok"))
                    self.after(0, lambda: self._append_output(f"  ✅ Uptime: {uptime_info}\n", "success"))
                else:
                    issues_found.append("Could not check uptime")
                    self.after(0, lambda: self._append_output(f"  ❌ Uptime: Failed\n", "error"))

                # Disk space
                exit_code, stdout, stderr = ssh_client.execute_command("df -h / | tail -1", timeout=10)
                if exit_code == 0:
                    disk_info = stdout.strip().split()
                    if len(disk_info) >= 5:
                        available = disk_info[3]
                        usage_percent = disk_info[4].rstrip('%')
                        try:
                            usage_int = int(usage_percent)
                            if usage_int >= 90:
                                issues_found.append(f"Disk usage critical: {usage_percent}%")
                                self.after(0, lambda u=usage_percent, a=available: self._append_output(
                                    f"  ❌ Disk Space: {u}% used (CRITICAL - only {a} available)\n", "error"))
                            elif usage_int >= 80:
                                warnings_found.append(f"Disk usage high: {usage_percent}%")
                                self.after(0, lambda u=usage_percent, a=available: self._append_output(
                                    f"  ⚠️  Disk Space: {u}% used (WARNING - {a} available)\n", "info"))
                            else:
                                self.after(0, lambda u=usage_percent, a=available: self._append_output(
                                    f"  ✅ Disk Space: {u}% used ({a} available)\n", "success"))
                        except:
                            pass

                # Memory
                exit_code, stdout, stderr = ssh_client.execute_command("free -h | grep Mem:", timeout=10)
                if exit_code == 0:
                    mem_info = stdout.strip().split()
                    if len(mem_info) >= 3:
                        total = mem_info[1]
                        used = mem_info[2]
                        self.after(0, lambda t=total, u=used: self._append_output(
                            f"  ✅ Memory: {u} / {t} used\n", "success"))

                self.after(0, lambda: self._append_output("\n", None))

                # 2. Docker Health Check
                self.after(0, lambda: self._append_output("🐳 DOCKER HEALTH\n", "command"))

                # Docker service status
                exit_code, stdout, stderr = ssh_client.execute_command("systemctl is-active docker", timeout=10)
                if exit_code == 0 and "active" in stdout.lower():
                    self.after(0, lambda: self._append_output("  ✅ Docker Service: Active\n", "success"))
                else:
                    issues_found.append("Docker service not running")
                    self.after(0, lambda: self._append_output("  ❌ Docker Service: Not Active\n", "error"))

                # payload-manager status
                exit_code, stdout, stderr = ssh_client.execute_command(
                    "docker ps --filter name=payload-manager --format '{{.Status}}'", timeout=10)
                if exit_code == 0 and stdout.strip():
                    status = stdout.strip()
                    if "Up" in status:
                        self.after(0, lambda s=status: self._append_output(
                            f"  ✅ payload-manager: {s}\n", "success"))
                    else:
                        warnings_found.append(f"payload-manager not running: {status}")
                        self.after(0, lambda s=status: self._append_output(
                            f"  ⚠️  payload-manager: {s}\n", "info"))
                else:
                    issues_found.append("payload-manager container not found")
                    self.after(0, lambda: self._append_output("  ❌ payload-manager: Not Found\n", "error"))

                # Container restart count
                exit_code, stdout, stderr = ssh_client.execute_command(
                    "docker inspect payload-manager --format '{{.RestartCount}}' 2>/dev/null", timeout=10)
                if exit_code == 0 and stdout.strip():
                    restart_count = stdout.strip()
                    try:
                        count = int(restart_count)
                        if count > 5:
                            warnings_found.append(f"Container restarted {count} times")
                            self.after(0, lambda c=count: self._append_output(
                                f"  ⚠️  Container Restarts: {c} times (HIGH)\n", "info"))
                        elif count > 0:
                            self.after(0, lambda c=count: self._append_output(
                                f"  ✅ Container Restarts: {c} times\n", "success"))
                        else:
                            self.after(0, lambda: self._append_output("  ✅ Container Restarts: None\n", "success"))
                    except:
                        pass

                self.after(0, lambda: self._append_output("\n", None))

                # 3. Network Health
                self.after(0, lambda: self._append_output("🌐 NETWORK HEALTH\n", "command"))

                # Check critical ports
                critical_ports = ["5000", "50001", "50002"]
                exit_code, stdout, stderr = ssh_client.execute_command("ss -tuln", timeout=10)
                if exit_code == 0:
                    for port in critical_ports:
                        if f":{port}" in stdout:
                            self.after(0, lambda p=port: self._append_output(
                                f"  ✅ Port {p}: Listening\n", "success"))
                        else:
                            warnings_found.append(f"Port {port} not listening")
                            self.after(0, lambda p=port: self._append_output(
                                f"  ⚠️  Port {p}: Not Listening\n", "info"))

                self.after(0, lambda: self._append_output("\n", None))

                # 4. Log Analysis
                self.after(0, lambda: self._append_output("📝 LOG ANALYSIS (Last 100 lines)\n", "command"))

                # Count errors and warnings in recent logs
                exit_code, stdout, stderr = ssh_client.execute_command(
                    "docker logs --tail 100 payload-manager 2>&1 | grep -i 'error\\|warning\\|fail' | wc -l", timeout=15)
                if exit_code == 0:
                    error_count = stdout.strip()
                    try:
                        count = int(error_count)
                        if count > 10:
                            warnings_found.append(f"{count} errors/warnings in recent logs")
                            self.after(0, lambda c=count: self._append_output(
                                f"  ⚠️  Errors/Warnings: {c} found in last 100 lines\n", "info"))
                        elif count > 0:
                            self.after(0, lambda c=count: self._append_output(
                                f"  ✅ Errors/Warnings: {c} found (normal)\n", "success"))
                        else:
                            self.after(0, lambda: self._append_output("  ✅ Errors/Warnings: None found\n", "success"))
                    except:
                        pass

                # Check for camera connection issues
                exit_code, stdout, stderr = ssh_client.execute_command(
                    "docker logs --tail 100 payload-manager 2>&1 | grep -i 'camera.*disconnect' | wc -l", timeout=15)
                if exit_code == 0:
                    disconnect_count = stdout.strip()
                    try:
                        count = int(disconnect_count)
                        if count > 3:
                            warnings_found.append(f"{count} camera disconnections detected")
                            self.after(0, lambda c=count: self._append_output(
                                f"  ⚠️  Camera Disconnects: {c} detected\n", "info"))
                        elif count > 0:
                            self.after(0, lambda c=count: self._append_output(
                                f"  ✅ Camera Disconnects: {c} (acceptable)\n", "success"))
                        else:
                            self.after(0, lambda: self._append_output("  ✅ Camera Disconnects: None\n", "success"))
                    except:
                        pass

                self.after(0, lambda: self._append_output("\n", None))

                # Generate Summary
                self.after(0, lambda: self._append_output("=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("  SUMMARY\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n\n", "info"))

                # Calculate health score
                total_checks = len(report) + len(critical_ports) + 5  # Approximate
                issues_weight = len(issues_found) * 20
                warnings_weight = len(warnings_found) * 10
                health_score = max(0, 100 - issues_weight - warnings_weight)

                # Display score
                if health_score >= 80:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ✅ GOOD\n\n", "success"))
                elif health_score >= 60:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ⚠️  FAIR\n\n", "info"))
                else:
                    self.after(0, lambda s=health_score: self._append_output(
                        f"  Overall Health Score: {s}/100 ❌ POOR\n\n", "error"))

                # Display issues
                if issues_found:
                    self.after(0, lambda: self._append_output("  ❌ CRITICAL ISSUES FOUND:\n", "error"))
                    for issue in issues_found:
                        self.after(0, lambda i=issue: self._append_output(f"     • {i}\n", "error"))
                    self.after(0, lambda: self._append_output("\n", None))

                if warnings_found:
                    self.after(0, lambda: self._append_output("  ⚠️  WARNINGS:\n", "info"))
                    for warning in warnings_found:
                        self.after(0, lambda w=warning: self._append_output(f"     • {w}\n", "info"))
                    self.after(0, lambda: self._append_output("\n", None))

                if not issues_found and not warnings_found:
                    self.after(0, lambda: self._append_output("  ✅ No issues detected. System is healthy!\n\n", "success"))

                # Recommendations
                if issues_found or warnings_found:
                    self.after(0, lambda: self._append_output("  💡 RECOMMENDATIONS:\n", "command"))
                    if any("disk" in i.lower() for i in issues_found + warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Consider cleaning up old logs and temporary files\n", "info"))
                    if any("docker" in i.lower() or "container" in i.lower() for i in issues_found):
                        self.after(0, lambda: self._append_output(
                            "     • Restart Docker service or payload-manager container\n", "info"))
                    if any("restart" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Investigate logs for crash causes\n", "info"))
                    if any("camera" in w.lower() for w in warnings_found):
                        self.after(0, lambda: self._append_output(
                            "     • Check camera USB connection and power\n", "info"))

                self.after(0, lambda: self._append_output("\n" + "=" * 80 + "\n", "info"))
                self.after(0, lambda: self._append_output("Diagnostic complete!\n", "command"))
                self.after(0, lambda: self._append_output("=" * 80 + "\n", "info"))

                # Update status
                self.after(0, lambda: self.status_label.config(text="Smart Diagnostic completed"))
                self.after(0, lambda: self.diagnostic_btn.config(state=tk.NORMAL))

            except Exception as e:
                logger.exception(f"Error running smart diagnostic: {e}")
                self.after(0, lambda: self._append_output(f"\n❌ Diagnostic failed: {str(e)}\n", "error"))
                self.after(0, lambda: self.status_label.config(text="Diagnostic failed"))
                self.after(0, lambda: self.diagnostic_btn.config(state=tk.NORMAL))

        threading.Thread(target=run_diagnostics, daemon=True).start()

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

    def _copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            # Check if there's a selection
            if self.output_text.tag_ranges(tk.SEL):
                selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.update()
                messagebox.showinfo("Success", "Selected text copied to clipboard!")
            else:
                messagebox.showwarning("No Selection", "Please select text to copy.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _save_report(self):
        """Save diagnostic report to file"""
        try:
            # Get output content
            output = self.output_text.get(1.0, tk.END).strip()

            if not output:
                messagebox.showwarning("No Content", "No report to save. Run Smart Diagnostic first.")
                return

            # Generate default filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            default_filename = f"diagnostic_report_{timestamp}.txt"

            # Open save file dialog
            file_path = filedialog.asksaveasfilename(
                title="Save Diagnostic Report",
                defaultextension=".txt",
                initialfile=default_filename,
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)

                messagebox.showinfo("Success", f"Report saved successfully!\n\n{file_path}")
                logger.info(f"Diagnostic report saved to: {file_path}")
                self.status_label.config(text=f"Report saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{e}")
            logger.exception(f"Error saving diagnostic report: {e}")
