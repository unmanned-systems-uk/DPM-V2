"""
Performance Analytics Tab - Real-time statistical analysis and visualization
Deep system statistical analysis with anomaly detection
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from collections import deque
import threading

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter integration
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

from utils.logger import logger
from analytics import PerformanceDatabase, StatisticsEngine, AnomalyDetector, AirSideLogParser
from analytics.anomaly_detection import Alert, AlertSeverity
import json
from pathlib import Path


class PerformanceAnalyticsTab(ttk.Frame):
    """Performance Analytics tab with real-time graphing and statistical analysis"""

    def __init__(self, parent, config_obj=None):
        super().__init__(parent)

        # Load analytics config from log_aggregator.json
        try:
            config_path = Path(__file__).parent.parent / "config" / "log_aggregator.json"
            with open(config_path, 'r') as f:
                full_config = json.load(f)
            self.config = full_config.get('analytics', {})
            logger.debug(f"Loaded analytics config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load analytics config, using defaults: {e}")
            self.config = {
                'database_path': 'data/performance.db',
                'data_retention_days': 7,
                'alert_thresholds': {
                    'cpu_warn': 70,
                    'cpu_critical': 90,
                    'memory_warn_mb': 6000,
                    'memory_critical_mb': 7000,
                    'camera_latency_warn_ms': 40,
                    'camera_latency_critical_ms': 100,
                    'queue_depth_warn': 10,
                    'queue_depth_critical': 50
                },
                'anomaly_detection': {
                    'z_score_threshold': 3.0,
                    'rate_of_change_threshold_percent': 30
                }
            }

        # Initialize analytics components
        db_path = self.config.get('database_path', 'data/performance.db')
        self.db = PerformanceDatabase(db_path)
        self.stats_engine = StatisticsEngine()
        self.detector = AnomalyDetector(self.config)

        # Data buffers (in-memory for real-time graphing)
        self.max_buffer_size = 720  # 1 hour @ 5 Hz
        self.data_buffer = deque(maxlen=self.max_buffer_size)

        # Time window settings
        self.time_windows = {
            "5min": 300,
            "15min": 900,
            "30min": 1800,
            "1hour": 3600
        }
        self.current_time_window = "30min"  # Default

        # Update settings
        self.auto_refresh = tk.BooleanVar(value=True)
        self.update_interval_ms = 5000  # 5 seconds
        self.update_job = None

        # Previous snapshot for rate-of-change detection
        self.previous_snapshot = None

        # Cached statistics (updated periodically)
        self.cached_stats = {}

        self._create_ui()

        logger.info("PerformanceAnalyticsTab initialized")

    def _create_ui(self):
        """Create UI layout"""

        # Top controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Time window selection
        ttk.Label(controls_frame, text="Time Window:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        for window_name in ["5min", "15min", "30min", "1hour"]:
            btn = ttk.Radiobutton(
                controls_frame,
                text=window_name,
                value=window_name,
                command=lambda w=window_name: self._change_time_window(w)
            )
            btn.pack(side=tk.LEFT, padx=2)
            if window_name == self.current_time_window:
                btn.invoke()

        # Auto-refresh checkbox
        ttk.Checkbutton(
            controls_frame,
            text="Auto-refresh",
            variable=self.auto_refresh,
            command=self._toggle_auto_refresh
        ).pack(side=tk.LEFT, padx=20)

        # Manual refresh button
        ttk.Button(
            controls_frame,
            text="Refresh Now",
            command=self._manual_refresh
        ).pack(side=tk.LEFT, padx=5)

        # Import logs button (Issue #138)
        ttk.Button(
            controls_frame,
            text="📂 Import Air-Side Logs",
            command=self._import_logs
        ).pack(side=tk.LEFT, padx=20)

        # Clear data button
        ttk.Button(
            controls_frame,
            text="🗑️ Clear Data",
            command=self._clear_data
        ).pack(side=tk.LEFT, padx=5)

        # Create notebook for different sections
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab 1: Graphs
        self._create_graphs_tab()

        # Tab 2: Statistics
        self._create_statistics_tab()

        # Tab 3: Alerts
        self._create_alerts_tab()

        # Bottom status bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = ttk.Label(
            status_frame,
            text="Waiting for data...",
            font=('Arial', 9, 'italic')
        )
        self.status_label.pack(side=tk.LEFT)

        self.db_status_label = ttk.Label(
            status_frame,
            text="Database: 0 records",
            font=('Arial', 9, 'italic')
        )
        self.db_status_label.pack(side=tk.RIGHT)

        # Start auto-refresh if enabled
        if self.auto_refresh.get():
            self._start_auto_refresh()

    def _create_graphs_tab(self):
        """Create graphs tab with matplotlib charts"""
        graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(graphs_frame, text="📈 Real-Time Graphs")

        # Create matplotlib figure with 5 subplots (stacked vertically)
        self.fig = Figure(figsize=(10, 12), dpi=80, facecolor='white')

        # Subplot 1: CPU Usage
        self.ax_cpu = self.fig.add_subplot(511)
        self.ax_cpu.set_title("CPU Usage (%)", fontsize=10, fontweight='bold')
        self.ax_cpu.set_ylabel("CPU %")
        self.ax_cpu.grid(True, alpha=0.3)

        # Subplot 2: Memory Usage
        self.ax_memory = self.fig.add_subplot(512)
        self.ax_memory.set_title("Memory Usage (MB)", fontsize=10, fontweight='bold')
        self.ax_memory.set_ylabel("Memory (MB)")
        self.ax_memory.grid(True, alpha=0.3)

        # Subplot 3: Disk Usage
        self.ax_disk = self.fig.add_subplot(513)
        self.ax_disk.set_title("Disk Usage (MB)", fontsize=10, fontweight='bold')
        self.ax_disk.set_ylabel("Disk (MB)")
        self.ax_disk.grid(True, alpha=0.3)

        # Subplot 4: Network Traffic
        self.ax_network = self.fig.add_subplot(514)
        self.ax_network.set_title("Network Traffic (Mbps)", fontsize=10, fontweight='bold')
        self.ax_network.set_ylabel("Mbps")
        self.ax_network.grid(True, alpha=0.3)

        # Subplot 5: Camera Connection
        self.ax_camera_conn = self.fig.add_subplot(515)
        self.ax_camera_conn.set_title("Camera Connection Status", fontsize=10, fontweight='bold')
        self.ax_camera_conn.set_ylabel("Connected")
        self.ax_camera_conn.set_xlabel("Time")
        self.ax_camera_conn.set_ylim(-0.2, 1.2)
        self.ax_camera_conn.grid(True, alpha=0.3)

        # Adjust spacing between subplots
        self.fig.tight_layout(pad=1.5)

        # Embed matplotlib figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        logger.debug("Graphs tab created with 5 subplots")

    def _create_statistics_tab(self):
        """Create statistics tab with descriptive stats"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Statistics")

        # Header
        header_frame = ttk.Frame(stats_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            header_frame,
            text="Statistical Summary (Current Time Window)",
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT)

        ttk.Button(
            header_frame,
            text="Export Statistics",
            command=self._export_statistics
        ).pack(side=tk.RIGHT, padx=5)

        # Statistics display (scrolled text)
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            height=25
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure text tags for formatting
        self.stats_text.tag_config("header", font=('Courier', 11, 'bold'), foreground="blue")
        self.stats_text.tag_config("metric", font=('Courier', 10, 'bold'))
        self.stats_text.tag_config("warning", foreground="orange")
        self.stats_text.tag_config("normal", foreground="black")

    def _create_alerts_tab(self):
        """Create alerts tab with anomaly detection results"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="⚠️  Alerts")

        # Header
        header_frame = ttk.Frame(alerts_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            header_frame,
            text="Anomaly Detection Alerts",
            font=('Arial', 11, 'bold')
        ).pack(side=tk.LEFT)

        ttk.Button(
            header_frame,
            text="Clear Alerts",
            command=self._clear_alerts
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            header_frame,
            text="Export Alerts",
            command=self._export_alerts
        ).pack(side=tk.RIGHT, padx=5)

        # Alert summary
        summary_frame = ttk.Frame(alerts_frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.alert_summary_label = ttk.Label(
            summary_frame,
            text="Total: 0  |  🔴 Critical: 0  |  🟡 Warning: 0  |  🔵 Info: 0",
            font=('Arial', 10)
        )
        self.alert_summary_label.pack()

        # Alerts display (scrolled text)
        self.alerts_text = scrolledtext.ScrolledText(
            alerts_frame,
            wrap=tk.WORD,
            font=('Courier', 9),
            height=20
        )
        self.alerts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Configure text tags for color-coded alerts
        self.alerts_text.tag_config("critical", foreground="red", font=('Courier', 9, 'bold'))
        self.alerts_text.tag_config("warning", foreground="orange", font=('Courier', 9, 'bold'))
        self.alerts_text.tag_config("info", foreground="blue", font=('Courier', 9))
        self.alerts_text.tag_config("timestamp", foreground="gray", font=('Courier', 8, 'italic'))
        self.alerts_text.tag_config("recommendation", foreground="green", font=('Courier', 9, 'italic'))

    def _normalize_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Air-Side field names to match analytics database schema

        Air-Side sends: memory_mb, disk_free_gb, disk_total_gb, connected
        We expect: memory_used_mb, disk_used_mb, disk_total_mb, camera_connected
        """
        normalized = {}

        # System metrics - rename and unit conversion
        if 'cpu_percent' in snapshot:
            normalized['cpu_percent'] = snapshot['cpu_percent']

        # Handle memory metrics - support both live and imported formats
        if 'memory_mb' in snapshot:
            # Live data
            normalized['memory_used_mb'] = snapshot['memory_mb']
        elif 'memory_used_mb' in snapshot:
            # Imported data - already in correct format
            normalized['memory_used_mb'] = snapshot['memory_used_mb']

        if 'memory_total_mb' in snapshot:
            normalized['memory_total_mb'] = snapshot['memory_total_mb']

        # Handle disk metrics - support both live data and imported data
        if 'disk_free_gb' in snapshot and 'disk_total_gb' in snapshot:
            # Live data: Convert GB to MB and calculate used
            disk_total_mb = snapshot['disk_total_gb'] * 1024
            disk_free_mb = snapshot['disk_free_gb'] * 1024
            normalized['disk_total_mb'] = int(disk_total_mb)
            normalized['disk_used_mb'] = int(disk_total_mb - disk_free_mb)
        elif 'disk_used_mb' in snapshot:
            # Imported data: Already in correct format
            normalized['disk_used_mb'] = snapshot['disk_used_mb']
            if 'disk_total_mb' in snapshot:
                normalized['disk_total_mb'] = snapshot['disk_total_mb']

        if 'network_rx_mbps' in snapshot:
            normalized['network_rx_mbps'] = snapshot['network_rx_mbps']

        if 'network_tx_mbps' in snapshot:
            normalized['network_tx_mbps'] = snapshot['network_tx_mbps']

        # Camera metrics - support both live and imported formats
        if 'connected' in snapshot:
            # Live data
            normalized['camera_connected'] = snapshot['connected']
        elif 'camera_connected' in snapshot:
            # Imported data - already in correct format
            normalized['camera_connected'] = snapshot['camera_connected']

        # Camera metrics that may be in imported data
        if 'sdk_latency_ms' in snapshot:
            normalized['sdk_latency_ms'] = snapshot['sdk_latency_ms']
        if 'usb_traffic_mbps' in snapshot:
            normalized['usb_traffic_mbps'] = snapshot['usb_traffic_mbps']
        if 'error_count' in snapshot:
            normalized['error_count'] = snapshot['error_count']

        # Network metrics from imported data
        if 'tcp_connected' in snapshot:
            normalized['tcp_connected'] = snapshot['tcp_connected']
        if 'tcp_latency_ms' in snapshot:
            normalized['tcp_latency_ms'] = snapshot['tcp_latency_ms']
        if 'udp_loss_percent' in snapshot:
            normalized['udp_loss_percent'] = snapshot['udp_loss_percent']
        if 'command_queue_depth' in snapshot:
            normalized['command_queue_depth'] = snapshot['command_queue_depth']

        # Sync metrics from imported data
        if 'exposure_rate_hz' in snapshot:
            normalized['exposure_rate_hz'] = snapshot['exposure_rate_hz']
        if 'health_rate_hz' in snapshot:
            normalized['health_rate_hz'] = snapshot['health_rate_hz']
        if 'property_reads_sec' in snapshot:
            normalized['property_reads_sec'] = snapshot['property_reads_sec']

        return normalized

    def update_with_snapshot(self, snapshot: Dict[str, Any]):
        """
        Update analytics with new health snapshot from Air-Side

        Args:
            snapshot: Health snapshot dictionary from StatusListener
        """
        try:
            # Debug: Log what fields we're receiving
            logger.debug(f"Received snapshot with keys: {list(snapshot.keys())}")

            # Normalize field names to match our database schema
            normalized = self._normalize_snapshot(snapshot)
            logger.debug(f"Normalized snapshot: {normalized}")

            # Add timestamp if not present
            if 'timestamp' not in normalized:
                normalized['timestamp'] = datetime.now(timezone.utc)

            # Store in database
            self.db.insert_snapshot(normalized)
            logger.debug(f"Inserted snapshot at {normalized['timestamp']}")

            # Add to in-memory buffer (use normalized version)
            self.data_buffer.append(normalized)

            # Run anomaly detection (use normalized version)
            alerts = self.detector.analyze_snapshot(
                normalized,
                previous_snapshot=self.previous_snapshot,
                stats=self.cached_stats
            )

            # Display new alerts
            if alerts:
                self._display_alerts(alerts)

            # Store as previous for next iteration (use normalized)
            self.previous_snapshot = normalized

            # Update UI if auto-refresh enabled
            if self.auto_refresh.get():
                # UI will be updated by periodic refresh job
                pass

            # Update database status
            self._update_db_status()

        except Exception as e:
            logger.error(f"Failed to update with snapshot: {e}")

    def _update_graphs(self):
        """Update all graphs with current data"""
        try:
            # Get data for current time window
            window_sec = self.time_windows[self.current_time_window]
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=window_sec)

            # Filter data buffer (skip entries with missing timestamps)
            filtered_data = [s for s in self.data_buffer if s.get('timestamp') and s.get('timestamp') >= cutoff_time]

            if len(filtered_data) == 0:
                logger.debug("No data in current time window")
                return

            # Extract timestamps and metrics
            timestamps = []
            cpu_values = []
            memory_values = []
            disk_values = []
            network_rx_values = []
            network_tx_values = []
            camera_conn_values = []

            for snapshot in filtered_data:
                ts = snapshot.get('timestamp')
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))

                timestamps.append(ts)
                cpu_values.append(snapshot.get('cpu_percent'))
                memory_values.append(snapshot.get('memory_used_mb'))
                disk_values.append(snapshot.get('disk_used_mb'))
                network_rx_values.append(snapshot.get('network_rx_mbps', 0.0))
                network_tx_values.append(snapshot.get('network_tx_mbps', 0.0))
                camera_conn_values.append(1 if snapshot.get('camera_connected') else 0)

            # Clear previous plots
            self.ax_cpu.clear()
            self.ax_memory.clear()
            self.ax_disk.clear()
            self.ax_network.clear()
            self.ax_camera_conn.clear()

            # Plot CPU
            self.ax_cpu.plot(timestamps, cpu_values, 'b-', linewidth=1.5, label='CPU %')
            self.ax_cpu.set_title("CPU Usage (%)", fontsize=10, fontweight='bold')
            self.ax_cpu.set_ylabel("CPU %")
            self.ax_cpu.grid(True, alpha=0.3)

            # Add threshold lines (CPU)
            thresholds = self.config.get('alert_thresholds', {})
            cpu_warn = thresholds.get('cpu_warn')
            cpu_crit = thresholds.get('cpu_critical')
            if cpu_warn:
                self.ax_cpu.axhline(y=cpu_warn, color='orange', linestyle='--', linewidth=1, label=f'Warn ({cpu_warn}%)')
            if cpu_crit:
                self.ax_cpu.axhline(y=cpu_crit, color='red', linestyle='--', linewidth=1, label=f'Critical ({cpu_crit}%)')
            self.ax_cpu.legend(loc='upper right', fontsize=8)

            # Plot Memory
            self.ax_memory.plot(timestamps, memory_values, 'g-', linewidth=1.5, label='Memory (MB)')
            self.ax_memory.set_title("Memory Usage (MB)", fontsize=10, fontweight='bold')
            self.ax_memory.set_ylabel("Memory (MB)")
            self.ax_memory.grid(True, alpha=0.3)

            # Add threshold lines (Memory)
            mem_warn = thresholds.get('memory_warn_mb')
            mem_crit = thresholds.get('memory_critical_mb')
            if mem_warn:
                self.ax_memory.axhline(y=mem_warn, color='orange', linestyle='--', linewidth=1, label=f'Warn ({mem_warn}MB)')
            if mem_crit:
                self.ax_memory.axhline(y=mem_crit, color='red', linestyle='--', linewidth=1, label=f'Critical ({mem_crit}MB)')
            self.ax_memory.legend(loc='upper right', fontsize=8)

            # Plot Disk Usage
            self.ax_disk.plot(timestamps, disk_values, 'purple', linewidth=1.5, label='Disk Used (MB)')
            self.ax_disk.set_title("Disk Usage (MB)", fontsize=10, fontweight='bold')
            self.ax_disk.set_ylabel("Disk (MB)")
            self.ax_disk.grid(True, alpha=0.3)
            self.ax_disk.legend(loc='upper right', fontsize=8)

            # Plot Network Traffic
            self.ax_network.plot(timestamps, network_rx_values, 'cyan', linewidth=1.5, label='RX (Mbps)')
            self.ax_network.plot(timestamps, network_tx_values, 'orange', linewidth=1.5, label='TX (Mbps)')
            self.ax_network.set_title("Network Traffic (Mbps)", fontsize=10, fontweight='bold')
            self.ax_network.set_ylabel("Mbps")
            self.ax_network.grid(True, alpha=0.3)
            self.ax_network.legend(loc='upper right', fontsize=8)

            # Plot Camera Connection Status
            self.ax_camera_conn.plot(timestamps, camera_conn_values, 'g-', linewidth=2, marker='o', markersize=3, label='Connected')
            self.ax_camera_conn.set_title("Camera Connection Status", fontsize=10, fontweight='bold')
            self.ax_camera_conn.set_ylabel("Connected")
            self.ax_camera_conn.set_xlabel("Time")
            self.ax_camera_conn.set_ylim(-0.2, 1.2)
            self.ax_camera_conn.set_yticks([0, 1])
            self.ax_camera_conn.set_yticklabels(['Disconnected', 'Connected'])
            self.ax_camera_conn.grid(True, alpha=0.3)
            self.ax_camera_conn.legend(loc='upper right', fontsize=8)

            # Format x-axis (time)
            for ax in [self.ax_cpu, self.ax_memory, self.ax_disk, self.ax_network, self.ax_camera_conn]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                ax.tick_params(axis='x', rotation=45, labelsize=8)

            # Adjust layout
            self.fig.tight_layout(pad=2.0)

            # Redraw canvas
            self.canvas.draw()

            logger.debug(f"Graphs updated with {len(filtered_data)} data points")

        except Exception as e:
            logger.error(f"Failed to update graphs: {e}")

    def _update_statistics(self):
        """Update statistics display"""
        # Guard: Check if widget exists (may be called during initialization)
        if not hasattr(self, 'stats_text') or self.stats_text is None:
            return

        try:
            # Get data for current time window
            window_sec = self.time_windows[self.current_time_window]
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=window_sec)

            # Filter data buffer (skip entries with missing timestamps)
            filtered_data = [s for s in self.data_buffer if s.get('timestamp') and s.get('timestamp') >= cutoff_time]

            if len(filtered_data) == 0:
                self.stats_text.delete('1.0', tk.END)
                self.stats_text.insert('1.0', "No data available for current time window\n")
                return

            # Calculate statistics for each metric
            metrics = [
                ('cpu_percent', 'CPU Usage', '%'),
                ('memory_used_mb', 'Memory Used', 'MB'),
                ('memory_total_mb', 'Memory Total', 'MB'),
                ('disk_used_mb', 'Disk Used', 'MB'),
                ('disk_total_mb', 'Disk Total', 'MB'),
                ('network_rx_mbps', 'Network RX', 'Mbps'),
                ('network_tx_mbps', 'Network TX', 'Mbps'),
                ('camera_connected', 'Camera Connected', ''),
            ]

            # Clear stats display
            self.stats_text.delete('1.0', tk.END)

            # Add header
            self.stats_text.insert(tk.END, f"Statistical Summary - Last {self.current_time_window}\n", "header")
            self.stats_text.insert(tk.END, f"Data Points: {len(filtered_data)}\n", "normal")
            self.stats_text.insert(tk.END, f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n", "normal")

            # Calculate and display stats for each metric
            for metric_key, metric_name, unit in metrics:
                stats = self.stats_engine.analyze_metric(filtered_data, metric_key)

                if stats['valid_points'] == 0:
                    continue  # Skip metrics with no data

                # Store in cache for anomaly detection
                self.cached_stats[metric_key] = stats

                # Format and display
                formatted = self.stats_engine.format_stats_display(stats, metric_name, unit)
                self.stats_text.insert(tk.END, formatted + "\n\n", "metric")

                # Check if P95 approaching threshold (warning)
                desc = stats['descriptive']
                perc = stats['percentiles']
                thresholds = self.config.get('alert_thresholds', {})

                if metric_key == 'camera_latency_ms':
                    warn_threshold = thresholds.get('camera_latency_warn_ms')
                    if warn_threshold and perc['p95'] >= warn_threshold * 0.9:  # Within 90% of threshold
                        self.stats_text.insert(tk.END, f"  ⚠️  P95 approaching warn threshold ({warn_threshold}{unit})\n", "warning")

            logger.debug("Statistics updated")

        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")

    def _display_alerts(self, alerts: List[Alert]):
        """Display new alerts in alerts tab"""
        try:
            for alert in alerts:
                # Format alert
                severity_icon = {
                    AlertSeverity.CRITICAL: "🔴",
                    AlertSeverity.WARNING: "🟡",
                    AlertSeverity.INFO: "🔵"
                }

                icon = severity_icon.get(alert.severity, "⚪")
                timestamp_str = alert.timestamp.strftime("%H:%M:%S")

                # Insert into alerts text widget
                self.alerts_text.insert(tk.END, f"{icon} ", alert.severity.value)
                self.alerts_text.insert(tk.END, f"{alert.severity.value.upper()} ", alert.severity.value)
                self.alerts_text.insert(tk.END, f"({timestamp_str})\n", "timestamp")
                self.alerts_text.insert(tk.END, f"   {alert.message}\n", "normal")

                if alert.recommendation:
                    self.alerts_text.insert(tk.END, f"   → {alert.recommendation}\n", "recommendation")

                self.alerts_text.insert(tk.END, "\n")

            # Auto-scroll to bottom
            self.alerts_text.see(tk.END)

            # Update alert summary
            self._update_alert_summary()

        except Exception as e:
            logger.error(f"Failed to display alerts: {e}")

    def _update_alert_summary(self):
        """Update alert count summary"""
        try:
            summary = self.detector.get_alert_summary()
            text = f"Total: {summary['total']}  |  🔴 Critical: {summary['critical']}  |  🟡 Warning: {summary['warning']}  |  🔵 Info: {summary['info']}"
            self.alert_summary_label.config(text=text)
        except Exception as e:
            logger.error(f"Failed to update alert summary: {e}")

    def _change_time_window(self, window: str):
        """Change time window and refresh graphs"""
        self.current_time_window = window
        logger.info(f"Time window changed to: {window}")
        self._manual_refresh()

    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh.get():
            self._start_auto_refresh()
            logger.info("Auto-refresh enabled")
        else:
            self._stop_auto_refresh()
            logger.info("Auto-refresh disabled")

    def _start_auto_refresh(self):
        """Start periodic auto-refresh"""
        if self.update_job is None:
            self._refresh_ui()  # Initial refresh
            self._schedule_next_refresh()

    def _stop_auto_refresh(self):
        """Stop periodic auto-refresh"""
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None

    def _schedule_next_refresh(self):
        """Schedule next UI refresh"""
        if self.auto_refresh.get():
            self.update_job = self.after(self.update_interval_ms, self._refresh_ui)

    def _refresh_ui(self):
        """Refresh all UI elements"""
        try:
            self._update_graphs()
            self._update_statistics()
            self._update_status()

            # Schedule next refresh if auto-refresh enabled
            self._schedule_next_refresh()

        except Exception as e:
            logger.error(f"Failed to refresh UI: {e}")

    def _manual_refresh(self):
        """Manual refresh button handler - refresh display without loading from database"""
        logger.debug("Manual refresh triggered")
        self._update_graphs()
        self._update_statistics()
        self._update_status()

    def _clear_data(self):
        """Clear all data from buffer and optionally from database"""
        result = messagebox.askyesnocancel(
            "Clear Data",
            "Clear data from:\n\n"
            "• Yes = Clear buffer AND database (permanent)\n"
            "• No = Clear buffer only (temporary)\n"
            "• Cancel = Don't clear anything",
            icon='question'
        )

        if result is None:  # Cancel
            return

        # Clear buffer
        self.data_buffer.clear()
        logger.info("Cleared data buffer")

        # Clear database if user chose "Yes"
        if result is True:
            try:
                count = self.db.clear_all_snapshots()
                logger.info(f"Cleared {count} snapshots from database")
                messagebox.showinfo("Data Cleared", f"Cleared buffer and {count} snapshots from database")
            except Exception as e:
                logger.error(f"Failed to clear database: {e}")
                messagebox.showerror("Error", f"Failed to clear database:\n{e}")
        else:
            messagebox.showinfo("Data Cleared", "Cleared buffer only")

        # Refresh UI to show empty state
        self._update_graphs()
        self._update_statistics()
        self._update_status()
        self._update_db_status()

    def _load_data_from_database(self):
        """Load recent data from database into data_buffer for graphing

        This is called after importing historical logs to populate the buffer
        with database content so graphs can display the imported data.
        """
        try:
            # Query latest snapshots (up to buffer size)
            snapshots = self.db.query_latest(limit=self.max_buffer_size)

            if not snapshots:
                logger.debug("No data in database to load")
                return

            # Clear current buffer
            self.data_buffer.clear()

            # Add snapshots to buffer (reverse order - oldest first)
            for snapshot in reversed(snapshots):
                # Convert timestamp string to datetime if needed
                if isinstance(snapshot.get('timestamp'), str):
                    snapshot['timestamp'] = datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))

                self.data_buffer.append(snapshot)

            logger.info(f"Loaded {len(self.data_buffer)} snapshots from database into buffer")

        except Exception as e:
            logger.error(f"Failed to load data from database: {e}")

    def _update_status(self):
        """Update status bar"""
        # Guard: Check if widget exists (may be called during initialization)
        if not hasattr(self, 'status_label') or self.status_label is None:
            return

        try:
            if len(self.data_buffer) > 0:
                latest = self.data_buffer[-1]
                ts = latest.get('timestamp')
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))

                age = (datetime.now(timezone.utc) - ts).total_seconds()
                self.status_label.config(text=f"Last update: {age:.0f}s ago  |  Buffer: {len(self.data_buffer)} snapshots")
            else:
                self.status_label.config(text="Waiting for data...")

        except Exception as e:
            logger.error(f"Failed to update status: {e}")

    def _update_db_status(self):
        """Update database status label"""
        try:
            count = self.db.get_record_count()
            self.db_status_label.config(text=f"Database: {count} records")
        except Exception as e:
            logger.error(f"Failed to update database status: {e}")

    def _clear_alerts(self):
        """Clear all alerts"""
        if messagebox.askyesno("Clear Alerts", "Clear all anomaly detection alerts?"):
            self.detector.clear_alerts()
            self.alerts_text.delete('1.0', tk.END)
            self._update_alert_summary()
            logger.info("Alerts cleared by user")

    def _export_statistics(self):
        """Export statistics to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Statistics",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if filename:
                stats_content = self.stats_text.get('1.0', tk.END)
                with open(filename, 'w') as f:
                    f.write(stats_content)

                messagebox.showinfo("Export Complete", f"Statistics exported to:\n{filename}")
                logger.info(f"Statistics exported to: {filename}")

        except Exception as e:
            logger.error(f"Failed to export statistics: {e}")
            messagebox.showerror("Export Failed", f"Failed to export statistics:\n{e}")

    def _export_alerts(self):
        """Export alerts to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Alerts",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if filename:
                alerts_content = self.alerts_text.get('1.0', tk.END)
                with open(filename, 'w') as f:
                    f.write(alerts_content)

                messagebox.showinfo("Export Complete", f"Alerts exported to:\n{filename}")
                logger.info(f"Alerts exported to: {filename}")

        except Exception as e:
            logger.error(f"Failed to export alerts: {e}")
            messagebox.showerror("Export Failed", f"Failed to export alerts:\n{e}")

    def _import_logs(self):
        """
        Import historical logs from downloaded air-side.jsonl files.
        Issue #138 - Enable historical log analysis
        """
        try:
            # Open file dialog to select .jsonl files
            default_dir = Path.home() / "Downloads" / "air-side-files" / "logs"

            file_paths = filedialog.askopenfilenames(
                title="Select Air-Side Log Files to Import",
                initialdir=str(default_dir) if default_dir.exists() else None,
                filetypes=[
                    ("JSON Lines files", "*.jsonl"),
                    ("All files", "*.*")
                ]
            )

            if not file_paths:
                return  # User cancelled

            # Confirm import
            file_count = len(file_paths)
            file_list = "\n".join([Path(f).name for f in file_paths[:5]])  # Show first 5
            if file_count > 5:
                file_list += f"\n... and {file_count - 5} more"

            confirm = messagebox.askyesno(
                "Import Air-Side Logs",
                f"Import {file_count} log file{'s' if file_count > 1 else ''}?\n\n{file_list}\n\nThis may take a moment..."
            )

            if not confirm:
                return

            # Show progress dialog
            progress_window = tk.Toplevel(self)
            progress_window.title("Importing Logs")
            progress_window.geometry("500x200")
            progress_window.transient(self)
            progress_window.grab_set()

            ttk.Label(
                progress_window,
                text="Importing Air-Side logs...",
                font=('Arial', 12, 'bold')
            ).pack(pady=10)

            progress_text = scrolledtext.ScrolledText(
                progress_window,
                height=6,
                width=60,
                font=('Arial', 9)
            )
            progress_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

            progress_label = ttk.Label(progress_window, text="Starting import...")
            progress_label.pack(pady=5)

            # Run import in thread to avoid freezing UI
            def import_thread():
                try:
                    progress_text.insert(tk.END, f"Parsing {file_count} file(s)...\n")
                    progress_text.see(tk.END)
                    progress_window.update()

                    # Parse files
                    parser = AirSideLogParser()
                    snapshots, stats = parser.parse_multiple_files(list(file_paths))

                    progress_text.insert(tk.END, f"  Files processed: {stats['files_processed']}\n")
                    progress_text.insert(tk.END, f"  Total lines: {stats['total_lines']}\n")
                    progress_text.insert(tk.END, f"  Health snapshots found: {stats['snapshots_found']}\n")
                    progress_text.insert(tk.END, f"  Duplicates removed: {stats['duplicates_removed']}\n")
                    progress_text.see(tk.END)
                    progress_window.update()

                    if not snapshots:
                        progress_text.insert(tk.END, "\nNo health snapshots found in selected files.\n")
                        progress_label.config(text="Import complete - no data found")
                        progress_text.see(tk.END)
                        return

                    # Import into database
                    progress_text.insert(tk.END, f"\nImporting {len(snapshots)} snapshots into database...\n")
                    progress_text.see(tk.END)
                    progress_window.update()

                    imported_count = 0
                    duplicate_count = 0
                    error_count = 0

                    for i, snapshot in enumerate(snapshots):
                        # Check for duplicate by timestamp
                        timestamp = snapshot.get('timestamp')
                        if not timestamp:
                            error_count += 1
                            continue

                        # Try to insert
                        success = self.db.insert_snapshot(snapshot)

                        if success:
                            imported_count += 1
                        else:
                            # Might be duplicate or error
                            duplicate_count += 1

                        # Update progress every 100 snapshots
                        if (i + 1) % 100 == 0:
                            progress_label.config(text=f"Imported {i + 1}/{len(snapshots)} snapshots...")
                            progress_window.update()

                    # Show results
                    progress_text.insert(tk.END, f"\n✅ Import Complete!\n")
                    progress_text.insert(tk.END, f"  Successfully imported: {imported_count} snapshots\n")
                    if duplicate_count > 0:
                        progress_text.insert(tk.END, f"  Duplicates/errors skipped: {duplicate_count}\n")
                    progress_text.see(tk.END)

                    progress_label.config(text=f"Import complete: {imported_count} snapshots imported")

                    # Load imported data from database into buffer and refresh display
                    self._load_data_from_database()
                    self._update_graphs()
                    self._update_statistics()
                    self._update_status()

                    # Update database status
                    self._update_db_status()

                    logger.info(f"Imported {imported_count} health snapshots from {file_count} files")

                    # Auto-close after 2 seconds
                    progress_window.after(2000, progress_window.destroy)

                except Exception as e:
                    logger.error(f"Import failed: {e}")
                    progress_text.insert(tk.END, f"\n❌ Import failed: {e}\n")
                    progress_label.config(text="Import failed")
                    progress_text.see(tk.END)

            # Start import thread
            thread = threading.Thread(target=import_thread, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"Failed to initiate import: {e}")
            messagebox.showerror("Import Error", f"Failed to import logs:\n{e}")

    def cleanup(self):
        """Cleanup resources on tab close"""
        try:
            # Stop auto-refresh
            self._stop_auto_refresh()

            # Close database
            if self.db:
                self.db.close()

            logger.info("PerformanceAnalyticsTab cleanup complete")

        except Exception as e:
            logger.error(f"Failed to cleanup PerformanceAnalyticsTab: {e}")
