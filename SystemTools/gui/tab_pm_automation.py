"""
PM Automation Dashboard Tab
===========================

Real-time monitoring and control of PM automation workflows.

Features:
- Live domain health status indicators
- One-click workflow execution buttons
- Results display area
- Last run timestamps
- H16 diagnostics display
- Error count monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading
import json
from pathlib import Path

# Import PM automation functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pm_automation import (
    pm_health_check,
    pm_collect_diagnostics,
    pm_check_errors,
    pm_status_report
)


class PMAutomationTab:
    """PM Automation Dashboard for monitoring and controlling automated workflows"""

    def __init__(self, parent):
        """
        Initialize PM Automation Dashboard

        Args:
            parent: Parent notebook widget
        """
        self.parent = parent
        self.frame = ttk.Frame(parent)

        # State tracking
        self.last_health_check = None
        self.last_diagnostics = None
        self.last_errors = None
        self.running_workflow = False

        # Initialize auto-refresh control (BEFORE creating UI)
        self.auto_refresh_enabled = tk.BooleanVar(value=False)

        # Build UI
        self._create_ui()

        # Start auto-refresh loop (every 60 seconds)
        self._auto_refresh_loop()

    def _create_ui(self):
        """Create the dashboard UI"""

        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        main_container.columnconfigure(0, weight=1)

        # === HEADER SECTION ===
        header_frame = ttk.LabelFrame(main_container, text="🤖 PM Automation Dashboard", padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(header_frame, text="Monitor and control PM automation workflows",
                 font=('TkDefaultFont', 10)).grid(row=0, column=0, sticky=tk.W)

        # Auto-refresh control
        refresh_frame = ttk.Frame(header_frame)
        refresh_frame.grid(row=0, column=1, sticky=tk.E)

        ttk.Checkbutton(refresh_frame, text="Auto-refresh (60s)",
                       variable=self.auto_refresh_enabled).pack(side=tk.LEFT, padx=5)

        ttk.Button(refresh_frame, text="🔄 Refresh Now",
                  command=self._manual_refresh).pack(side=tk.LEFT)

        # === STATUS SECTION ===
        status_frame = ttk.LabelFrame(main_container, text="📊 Domain Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Air-Side Status
        air_frame = ttk.Frame(status_frame)
        air_frame.grid(row=0, column=0, padx=10, pady=5)

        ttk.Label(air_frame, text="🚁 Air-Side:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        self.air_status_label = ttk.Label(air_frame, text="Unknown", foreground="gray")
        self.air_status_label.pack(anchor=tk.W)
        self.air_camera_label = ttk.Label(air_frame, text="📷 Camera: --", font=('TkDefaultFont', 8))
        self.air_camera_label.pack(anchor=tk.W)
        self.air_last_check = ttk.Label(air_frame, text="Never checked", foreground="gray", font=('TkDefaultFont', 8))
        self.air_last_check.pack(anchor=tk.W)

        # Ground-Side Status
        ground_frame = ttk.Frame(status_frame)
        ground_frame.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(ground_frame, text="📱 Ground-Side:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        self.ground_status_label = ttk.Label(ground_frame, text="Unknown", foreground="gray")
        self.ground_status_label.pack(anchor=tk.W)
        self.ground_battery_label = ttk.Label(ground_frame, text="Battery: --", font=('TkDefaultFont', 8))
        self.ground_battery_label.pack(anchor=tk.W)

        # SystemTools Status
        system_frame = ttk.Frame(status_frame)
        system_frame.grid(row=0, column=2, padx=10, pady=5)

        ttk.Label(system_frame, text="🛠️ SystemTools:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        self.system_status_label = ttk.Label(system_frame, text="Unknown", foreground="gray")
        self.system_status_label.pack(anchor=tk.W)
        self.system_errors_label = ttk.Label(system_frame, text="Errors: --", font=('TkDefaultFont', 8))
        self.system_errors_label.pack(anchor=tk.W)

        # === WORKFLOW BUTTONS ===
        workflow_frame = ttk.LabelFrame(main_container, text="⚡ Automation Workflows", padding="10")
        workflow_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 10), padx=(10, 0))

        # Health Check Button
        ttk.Button(workflow_frame, text="🏥 Health Check",
                  command=lambda: self._run_workflow('health'),
                  width=20).grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)

        # Diagnostics Button
        ttk.Button(workflow_frame, text="🔍 Collect Diagnostics",
                  command=lambda: self._run_workflow('diagnostics'),
                  width=20).grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)

        # Error Monitoring Button
        ttk.Button(workflow_frame, text="⚠️ Check Errors",
                  command=lambda: self._run_workflow('errors'),
                  width=20).grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)

        # Daily Workflow Button
        ttk.Button(workflow_frame, text="📋 Daily Workflow",
                  command=lambda: self._run_workflow('daily'),
                  width=20).grid(row=3, column=0, pady=5, sticky=tk.W+tk.E)

        # Separator
        ttk.Separator(workflow_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, pady=10, sticky=tk.W+tk.E)

        # Export Reports Button
        ttk.Button(workflow_frame, text="📁 Open Reports Folder",
                  command=self._open_reports_folder,
                  width=20).grid(row=5, column=0, pady=5, sticky=tk.W+tk.E)

        # === RESULTS SECTION ===
        results_frame = ttk.LabelFrame(main_container, text="📄 Workflow Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # Results text display
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=100,
            height=20,
            font=('Courier', 9)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure tags for colored output
        self.results_text.tag_configure("success", foreground="green")
        self.results_text.tag_configure("error", foreground="red")
        self.results_text.tag_configure("warning", foreground="orange")
        self.results_text.tag_configure("info", foreground="blue")
        self.results_text.tag_configure("header", font=('Courier', 10, 'bold'))

        # Initial message
        self._append_result("PM Automation Dashboard Ready\n", "info")
        self._append_result("Click a workflow button above to start monitoring.\n\n", "info")

    def _append_result(self, text, tag=None):
        """Append text to results display"""
        self.results_text.insert(tk.END, text, tag)
        self.results_text.see(tk.END)
        self.results_text.update_idletasks()

    def _clear_results(self):
        """Clear results display"""
        self.results_text.delete('1.0', tk.END)

    def _run_workflow(self, workflow_type):
        """
        Run a PM automation workflow in background thread

        Args:
            workflow_type: 'health', 'diagnostics', 'errors', or 'daily'
        """
        if self.running_workflow:
            messagebox.showwarning("Workflow Running", "Please wait for current workflow to complete")
            return

        # Run in background thread
        thread = threading.Thread(target=self._workflow_thread, args=(workflow_type,), daemon=True)
        thread.start()

    def _workflow_thread(self, workflow_type):
        """Background thread for running workflows"""
        self.running_workflow = True

        try:
            # Clear previous results
            self.results_text.after(0, self._clear_results)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if workflow_type == 'health':
                self._append_result(f"{'='*80}\n", "header")
                self._append_result(f"HEALTH CHECK - {timestamp}\n", "header")
                self._append_result(f"{'='*80}\n\n", "header")

                result = pm_health_check(include_ground_side=True)

                if result.get('success'):
                    self.last_health_check = result
                    self._update_status_displays()

                    overall = result.get('overall_healthy', False)
                    tag = "success" if overall else "error"
                    status_text = "✓ HEALTHY" if overall else "✗ UNHEALTHY"
                    self._append_result(f"\nOverall Status: {status_text}\n\n", tag)

                    # Domain details
                    for domain, status in result.get('domains', {}).items():
                        healthy = status.get('healthy', False)
                        tag = "success" if healthy else "error"
                        self._append_result(f"  {domain}: ", "info")

                        status_text = '✓ HEALTHY' if healthy else '✗ UNHEALTHY'

                        # Add camera status for air_side
                        if domain == 'air_side' and healthy:
                            camera = status.get('camera', {})
                            if camera.get('connected'):
                                model = camera.get('model', 'Unknown')
                                status_text += f" (Camera: ✓ {model})"
                            else:
                                status_text += " (Camera: ✗)"
                                tag = "warning"  # Change to warning color

                        self._append_result(f"{status_text}\n", tag)

                    self._append_result("\n✅ Health check complete\n", "success")
                else:
                    self._append_result(f"❌ Health check failed: {result.get('error', 'Unknown error')}\n", "error")

            elif workflow_type == 'diagnostics':
                self._append_result(f"{'='*80}\n", "header")
                self._append_result(f"DIAGNOSTICS COLLECTION - {timestamp}\n", "header")
                self._append_result(f"{'='*80}\n\n", "header")

                result = pm_collect_diagnostics(include_ground_side=True)
                self.last_diagnostics = result
                self._update_status_displays()

                # Air-Side
                self._append_result("🚁 Air-Side:\n", "info")
                if result['air_side'].get('connected'):
                    self._append_result("  ✓ Connected\n", "success")
                else:
                    self._append_result("  ✗ Not connected\n", "error")

                # Ground-Side
                self._append_result("\n📱 Ground-Side (H16):\n", "info")
                if result['ground_side'].get('connected'):
                    diag = result['ground_side'].get('diagnostics', {})
                    self._append_result("  ✓ Connected\n", "success")
                    self._append_result(f"  Battery: {diag.get('battery', 'N/A')}\n", "info")
                    self._append_result(f"  Memory: {diag.get('memory', 'N/A')}\n", "info")
                    self._append_result(f"  Temperature: {diag.get('temperature', 'N/A')}\n", "info")
                else:
                    self._append_result("  ✗ Not connected\n", "error")

                # SystemTools
                self._append_result("\n🛠️ SystemTools:\n", "info")
                sys_status = result['system']
                self._append_result(f"  Log Queue: {sys_status.get('log_queue', {}).get('available', False)}\n", "info")
                self._append_result(f"  Data Storage: {sys_status.get('data_storage', {}).get('available', False)}\n", "info")

                self._append_result("\n✅ Diagnostics collection complete\n", "success")

            elif workflow_type == 'errors':
                self._append_result(f"{'='*80}\n", "header")
                self._append_result(f"ERROR MONITORING - {timestamp}\n", "header")
                self._append_result(f"{'='*80}\n\n", "header")

                result = pm_check_errors(limit=50)
                self.last_errors = result
                self._update_status_displays()

                total_errors = result.get('total_errors', 0)

                if total_errors == 0:
                    self._append_result("✅ No errors found in recent logs\n", "success")
                else:
                    self._append_result(f"⚠️ Found {total_errors} errors\n\n", "warning")

                    for domain, data in result.get('domains', {}).items():
                        error_count = data.get('error_count', 0)
                        if error_count > 0:
                            self._append_result(f"  {domain}: {error_count} errors\n", "warning")
                            for error in data.get('recent_errors', [])[:3]:
                                msg = error.get('message', 'No message')
                                self._append_result(f"    - {msg}\n", "error")

                self._append_result("\n✅ Error monitoring complete\n", "success")

            elif workflow_type == 'daily':
                self._append_result(f"{'='*80}\n", "header")
                self._append_result(f"DAILY WORKFLOW - {timestamp}\n", "header")
                self._append_result(f"{'='*80}\n\n", "header")

                report_dir = '/tmp/pm_reports'
                timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = Path(report_dir) / f"pm_daily_report_{timestamp_file}.json"

                self._append_result("Step 1/3: Health check...\n", "info")
                result = pm_status_report(output_file=str(report_file))

                overall_healthy = result.get('health_check', {}).get('overall_healthy', False)
                total_errors = result.get('error_summary', {}).get('total_errors', 0)

                if overall_healthy:
                    self._append_result("  ✓ System healthy\n", "success")
                else:
                    self._append_result("  ✗ System unhealthy\n", "error")

                self._append_result(f"  Total errors: {total_errors}\n", "info")
                self._append_result(f"\n📁 Report saved: {report_file}\n\n", "success")

                self._append_result("✅ Daily workflow complete\n", "success")

                # Update all displays
                self.last_health_check = result.get('health_check')
                self.last_diagnostics = result.get('diagnostics')
                self.last_errors = result.get('error_summary')
                self._update_status_displays()

        except Exception as e:
            self._append_result(f"\n❌ Error: {str(e)}\n", "error")
            import traceback
            self._append_result(traceback.format_exc(), "error")

        finally:
            self.running_workflow = False

    def _update_status_displays(self):
        """Update status indicator labels based on last results"""

        # Update Air-Side status
        if self.last_health_check:
            domains = self.last_health_check.get('domains', {})
            air_status = domains.get('air_side', {})

            if air_status.get('healthy'):
                self.air_status_label.config(text="✓ HEALTHY", foreground="green")
            else:
                self.air_status_label.config(text="✗ UNHEALTHY", foreground="red")

            # Update camera status
            camera = air_status.get('camera', {})
            if camera.get('connected'):
                model = camera.get('model', 'Unknown')
                self.air_camera_label.config(text=f"📷 Camera: ✓ {model}", foreground="green")
            else:
                self.air_camera_label.config(text="📷 Camera: ✗ Disconnected", foreground="red")

            timestamp = self.last_health_check.get('timestamp', '')
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                self.air_last_check.config(text=f"Last check: {dt.strftime('%H:%M:%S')}")

        # Update Ground-Side status
        if self.last_diagnostics:
            ground = self.last_diagnostics.get('ground_side', {})

            if ground.get('connected'):
                self.ground_status_label.config(text="✓ ONLINE", foreground="green")

                diag = ground.get('diagnostics', {})
                battery = diag.get('battery', 'N/A')
                if 'level:' in battery:
                    battery = battery.split('level:')[1].strip()
                self.ground_battery_label.config(text=f"Battery: {battery}")
            else:
                self.ground_status_label.config(text="✗ OFFLINE", foreground="red")
                self.ground_battery_label.config(text="Battery: --")

        # Update SystemTools status
        if self.last_errors:
            total_errors = self.last_errors.get('total_errors', 0)

            if total_errors == 0:
                self.system_status_label.config(text="✓ HEALTHY", foreground="green")
                self.system_errors_label.config(text="Errors: 0")
            else:
                self.system_status_label.config(text="⚠️ WARNINGS", foreground="orange")
                self.system_errors_label.config(text=f"Errors: {total_errors}")
        elif self.last_health_check:
            domains = self.last_health_check.get('domains', {})
            sys_status = domains.get('system_tools', {})

            if sys_status.get('healthy'):
                self.system_status_label.config(text="✓ HEALTHY", foreground="green")
            else:
                self.system_status_label.config(text="✗ UNHEALTHY", foreground="red")

    def _manual_refresh(self):
        """Manually trigger health check refresh"""
        self._run_workflow('health')

    def _auto_refresh_loop(self):
        """Auto-refresh loop (every 60 seconds if enabled)"""
        if self.auto_refresh_enabled.get() and not self.running_workflow:
            self._run_workflow('health')

        # Schedule next check
        self.frame.after(60000, self._auto_refresh_loop)  # 60 seconds

    def _open_reports_folder(self):
        """Open the PM reports folder in file manager"""
        import subprocess
        import platform

        report_dir = Path('/tmp/pm_reports')
        report_dir.mkdir(parents=True, exist_ok=True)

        system = platform.system()
        try:
            if system == 'Linux':
                subprocess.Popen(['xdg-open', str(report_dir)])
            elif system == 'Darwin':  # macOS
                subprocess.Popen(['open', str(report_dir)])
            elif system == 'Windows':
                subprocess.Popen(['explorer', str(report_dir)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    def cleanup(self):
        """Cleanup when tab is closed"""
        self.auto_refresh_enabled.set(False)
