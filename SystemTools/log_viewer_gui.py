#!/usr/bin/env python3
"""
DPM SystemTools - Tri-Domain Log Viewer GUI
===========================================

Standalone GUI wrapper for the tri-domain log aggregator.
Provides tkinter-based interface with all log_aggregator.py features.

Usage:
    python log_viewer_gui.py

Features:
- Real-time log aggregation from Air-Side (UDP 5007) and Ground-Side (TCP 5008)
- Color-coded display (Blue=AIR, Magenta=GROUND)
- Filters: Domain, Level, Context, Text Search
- Export: JSON, CSV, Text
- Auto-scroll, Pause, Clear
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, Any, Optional
import json
import csv
import threading

from network.log_listeners import AirSideListener, GroundSideListener
from utils.logger import logger
from utils.log_colors import configure_tkinter_text_tags, get_buffer_max_entries


class LogViewerGUI(tk.Tk):
    """Standalone Tri-Domain Log Viewer GUI Application"""

    def __init__(self):
        super().__init__()

        self.title("DPM SystemTools - Tri-Domain Log Viewer")
        self.geometry("1600x900")

        # Log queue (shared with listeners)
        max_entries = get_buffer_max_entries()
        self.log_queue = deque(maxlen=max_entries)

        # Listeners
        self.air_listener: Optional[AirSideListener] = None
        self.ground_listener: Optional[GroundSideListener] = None

        # Stream state
        self.stream_running = False
        self.stream_paused = False

        # Display state
        self.auto_scroll = True
        self.last_update_time = None

        # Filters
        self.filter_domain = tk.StringVar(value="ALL")
        self.filter_level = tk.StringVar(value="ALL")
        self.filter_context = tk.StringVar(value="ALL")
        self.filter_search = tk.StringVar()

        # GUI update thread
        self.gui_update_running = False
        self.gui_update_thread = None

        # Display buffer (for filtering)
        self.display_buffer = []

        self._create_ui()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logger.info("Tri-Domain Log Viewer GUI initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Title and Controls
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill=tk.X)

        ttk.Label(header_frame, text="📊 Tri-Domain Log Aggregation Viewer",
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=10)

        # Stream Controls
        controls_frame = ttk.LabelFrame(self, text="Stream Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Status row
        status_row = ttk.Frame(controls_frame)
        status_row.pack(fill=tk.X, pady=5)

        ttk.Label(status_row, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_indicator = tk.Canvas(status_row, width=20, height=20, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self._update_status_indicator("stopped")

        self.status_label = ttk.Label(status_row, text="Stopped", font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Buttons row
        button_row = ttk.Frame(controls_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(button_row, text="▶ Start", command=self._on_start, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(button_row, text="⏸ Pause", command=self._on_pause, state=tk.DISABLED, width=12)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_row, text="⏹ Stop", command=self._on_stop, state=tk.DISABLED, width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Separator(button_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        ttk.Button(button_row, text="Clear", command=self._on_clear, width=10).pack(side=tk.LEFT, padx=5)

        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_row, text="Auto-scroll", variable=self.auto_scroll_var,
                       command=self._on_auto_scroll_changed).pack(side=tk.LEFT, padx=10)

        # Last update
        ttk.Label(button_row, text="Last Update:").pack(side=tk.RIGHT, padx=5)
        self.last_update_label = ttk.Label(button_row, text="Never", font=('Arial', 9, 'italic'))
        self.last_update_label.pack(side=tk.RIGHT, padx=5)

        # Filters Frame
        filters_frame = ttk.LabelFrame(self, text="Filters (Accumulative AND Logic)", padding=10)
        filters_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter row 1
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row1, text="Domain:").pack(side=tk.LEFT, padx=5)
        domain_combo = ttk.Combobox(filter_row1, textvariable=self.filter_domain,
                                    values=["ALL", "AIR", "GROUND"], state="readonly", width=10)
        domain_combo.pack(side=tk.LEFT, padx=5)
        domain_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Label(filter_row1, text="Level:").pack(side=tk.LEFT, padx=5)
        level_combo = ttk.Combobox(filter_row1, textvariable=self.filter_level,
                                   values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Label(filter_row1, text="Context:").pack(side=tk.LEFT, padx=5)
        context_combo = ttk.Combobox(filter_row1, textvariable=self.filter_context,
                                     values=["ALL", "CAMERA", "NETWORK", "COMMAND", "UI", "SYSTEM"], state="readonly", width=12)
        context_combo.pack(side=tk.LEFT, padx=5)
        context_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Filter row 2: Text search
        filter_row2 = ttk.Frame(filters_frame)
        filter_row2.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row2, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_row2, textvariable=self.filter_search, width=50)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self._on_filter_changed)

        ttk.Button(filter_row2, text="Clear", command=self._on_clear_search).pack(side=tk.LEFT, padx=5)

        # Export/Copy Frame
        export_frame = ttk.Frame(self)
        export_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        ttk.Button(export_frame, text="💾 Save to File...", command=self._on_save_to_file).pack(side=tk.LEFT, padx=5)

        self.export_format_var = tk.StringVar(value="json")
        ttk.Label(export_frame, text="Format:").pack(side=tk.LEFT, padx=(15, 5))
        ttk.Radiobutton(export_frame, text="JSON", variable=self.export_format_var, value="json").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(export_frame, text="CSV", variable=self.export_format_var, value="csv").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(export_frame, text="Text", variable=self.export_format_var, value="text").pack(side=tk.LEFT, padx=2)

        ttk.Separator(export_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        ttk.Button(export_frame, text="📋 Copy All", command=self._on_copy_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="📋 Copy Selected", command=self._on_copy_selected).pack(side=tk.LEFT, padx=5)

        # Line count
        self.line_count_label = ttk.Label(export_frame, text="Lines: 0 / Buffer: 0")
        self.line_count_label.pack(side=tk.RIGHT, padx=10)

        # Log Display
        log_frame = ttk.LabelFrame(self, text="Aggregated Logs (Air-Side + Ground-Side)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Text widget with scrollbar
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.NONE,
                                                   font=('Courier New', 9),
                                                   bg='#FFFFFF',  # White background
                                                   fg='#000000')  # Black default text
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure color tags from config (BEFORE disabling widget)
        configure_tkinter_text_tags(self.log_text)

        # Disable editing (after configuring tags)
        self.log_text.config(state=tk.DISABLED)

    def _update_status_indicator(self, status: str):
        """Update status indicator"""
        self.status_indicator.delete("all")
        color_map = {"stopped": "gray", "running": "green", "paused": "orange"}
        color = color_map.get(status, "gray")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _on_start(self):
        """Start streaming logs"""
        if self.stream_running:
            return

        logger.info("Starting Tri-Domain log streaming...")

        # Clear queue and buffer
        self.log_queue.clear()
        self.display_buffer.clear()

        # Create listeners
        self.air_listener = AirSideListener(host="0.0.0.0", port=5007)
        self.ground_listener = GroundSideListener(host="127.0.0.1", port=5008)

        # Start listeners
        self.air_listener.start(self.log_queue)
        self.ground_listener.start(self.log_queue)

        # Start GUI update thread
        self.gui_update_running = True
        self.gui_update_thread = threading.Thread(target=self._gui_update_worker, daemon=True)
        self.gui_update_thread.start()

        # Update UI
        self.stream_running = True
        self.stream_paused = False
        self._update_status_indicator("running")
        self.status_label.config(text="Running", foreground="green")
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)

        logger.info("Tri-Domain log streaming started")

    def _on_pause(self):
        """Pause/resume display updates"""
        if not self.stream_running:
            return

        self.stream_paused = not self.stream_paused

        if self.stream_paused:
            self._update_status_indicator("paused")
            self.status_label.config(text="Paused", foreground="orange")
            self.pause_btn.config(text="▶ Resume")
            logger.info("Display paused (buffering logs)")
        else:
            self._update_status_indicator("running")
            self.status_label.config(text="Running", foreground="green")
            self.pause_btn.config(text="⏸ Pause")
            logger.info("Display resumed")

    def _on_stop(self):
        """Stop streaming"""
        if not self.stream_running:
            return

        logger.info("Stopping Tri-Domain log streaming...")

        # Stop GUI update thread
        self.gui_update_running = False
        if self.gui_update_thread:
            self.gui_update_thread.join(timeout=2.0)

        # Stop listeners
        if self.air_listener:
            self.air_listener.stop()
            self.air_listener = None

        if self.ground_listener:
            self.ground_listener.stop()
            self.ground_listener = None

        # Clear queue
        self.log_queue.clear()

        # Update UI
        self.stream_running = False
        self.stream_paused = False
        self._update_status_indicator("stopped")
        self.status_label.config(text="Stopped", foreground="gray")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ Pause")
        self.stop_btn.config(state=tk.DISABLED)

        logger.info("Tri-Domain log streaming stopped")

    def _on_clear(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.display_buffer.clear()
        self._update_line_count()

    def _on_auto_scroll_changed(self):
        """Handle auto-scroll toggle"""
        self.auto_scroll = self.auto_scroll_var.get()

    def _on_filter_changed(self, event=None):
        """Handle filter change - redisplay filtered logs"""
        self._redisplay_filtered_logs()

    def _on_clear_search(self):
        """Clear search filter"""
        self.filter_search.set("")
        self._redisplay_filtered_logs()

    def _gui_update_worker(self):
        """Background thread to update GUI with new log entries"""
        while self.gui_update_running:
            try:
                if not self.stream_paused and len(self.log_queue) > 0:
                    # Schedule GUI update on main thread
                    self.after(0, self._process_queue)

                # Update every 100ms
                import time
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in GUI update worker: {e}")

    def _process_queue(self):
        """Process all pending log entries from queue"""
        if not self.gui_update_running or self.stream_paused:
            return

        # Process up to 100 entries at a time
        entries_to_process = []
        for _ in range(min(100, len(self.log_queue))):
            if self.log_queue:
                entry = self.log_queue.popleft()
                entries_to_process.append(entry)
                self.display_buffer.append(entry)  # Keep in buffer for filtering

        if not entries_to_process:
            return

        # Filter and display
        for entry in entries_to_process:
            if self._should_display(entry):
                self._append_log_entry(entry)

        # Update line count
        self._update_line_count()
        self.last_update_time = datetime.now()
        self.last_update_label.config(text=self.last_update_time.strftime("%H:%M:%S"))

    def _should_display(self, entry: Dict[str, Any]) -> bool:
        """Check if log entry matches current filters"""
        # Domain filter
        domain_filter = self.filter_domain.get()
        if domain_filter != "ALL" and entry.get('domain') != domain_filter:
            return False

        # Level filter
        level_filter = self.filter_level.get()
        if level_filter != "ALL" and entry.get('level') != level_filter:
            return False

        # Context filter
        context_filter = self.filter_context.get()
        if context_filter != "ALL":
            entry_context = entry.get('context', '').upper()
            if context_filter not in entry_context:
                return False

        # Text search filter
        search_text = self.filter_search.get().lower()
        if search_text:
            message = entry.get('message', '').lower()
            if search_text not in message:
                return False

        return True

    def _append_log_entry(self, entry: Dict[str, Any]):
        """Append a single log entry to display"""
        # Format: [TIMESTAMP] [DOMAIN ] [LEVEL  ] [CONTEXT] Message
        timestamp = entry.get('timestamp', 'NO-TS')
        if 'T' in timestamp:
            try:
                time_part = timestamp.split('T')[1][:12]
            except:
                time_part = timestamp[:12]
        else:
            time_part = timestamp[:12]

        domain = entry.get('domain', 'UNK').ljust(6)[:6]
        level = entry.get('level', 'INFO').ljust(7)[:7]
        context = entry.get('context', 'UNKNOWN').ljust(8)[:8]
        message = entry.get('message', '')

        log_line = f"{time_part} [{domain}] [{level}] [{context}] {message}\n"

        # Enable editing
        self.log_text.config(state=tk.NORMAL)

        # Insert line
        self.log_text.insert(tk.END, log_line)

        # Get line number
        line_number = int(self.log_text.index(tk.END).split('.')[0]) - 1

        # Apply domain color
        domain_code = entry.get('domain', '')
        if domain_code == 'AIR':
            self.log_text.tag_add("air", f"{line_number}.0", f"{line_number}.end")
        elif domain_code == 'GROUND':
            self.log_text.tag_add("ground", f"{line_number}.0", f"{line_number}.end")

        # Apply level color (overrides domain color)
        level_code = entry.get('level', 'INFO')
        if level_code == 'ERROR':
            self.log_text.tag_add("error", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'WARNING':
            self.log_text.tag_add("warning", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'DEBUG':
            self.log_text.tag_add("debug", f"{line_number}.0", f"{line_number}.end")
        elif level_code == 'INFO':
            self.log_text.tag_add("info", f"{line_number}.0", f"{line_number}.end")

        # Highlight search text
        search_text = self.filter_search.get()
        if search_text:
            self._highlight_search_in_line(line_number, log_line, search_text)

        # Auto-scroll
        if self.auto_scroll:
            self.log_text.see(tk.END)

        # Disable editing
        self.log_text.config(state=tk.DISABLED)

    def _highlight_search_in_line(self, line_number: int, line_text: str, search_text: str):
        """Highlight search text in a specific line"""
        start_idx = 0
        while True:
            idx = line_text.lower().find(search_text.lower(), start_idx)
            if idx == -1:
                break
            start_pos = f"{line_number}.{idx}"
            end_pos = f"{line_number}.{idx + len(search_text)}"
            self.log_text.tag_add("highlight", start_pos, end_pos)
            start_idx = idx + len(search_text)

    def _redisplay_filtered_logs(self):
        """Redisplay all logs from buffer with current filters"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        for entry in self.display_buffer:
            if self._should_display(entry):
                self._append_log_entry(entry)

        self._update_line_count()

    def _update_line_count(self):
        """Update line count label"""
        total_lines = int(self.log_text.index(tk.END).split('.')[0]) - 1
        buffer_size = len(self.display_buffer)
        self.line_count_label.config(text=f"Displayed: {total_lines} / Buffer: {buffer_size}")

    def _on_save_to_file(self):
        """Export logs to file"""
        if not self.display_buffer:
            messagebox.showinfo("No Data", "No logs to export")
            return

        export_format = self.export_format_var.get()
        ext_map = {"json": ".json", "csv": ".csv", "text": ".txt"}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            initialfile=f"tri_domain_logs_{timestamp}{ext_map[export_format]}",
            defaultextension=ext_map[export_format],
            filetypes=[("All files", "*.*")]
        )

        if filepath:
            try:
                # Filter logs that should be displayed
                filtered_logs = [entry for entry in self.display_buffer if self._should_display(entry)]

                if export_format == "json":
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(filtered_logs, f, indent=2)
                elif export_format == "csv":
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        if filtered_logs:
                            writer = csv.DictWriter(f, fieldnames=filtered_logs[0].keys())
                            writer.writeheader()
                            writer.writerows(filtered_logs)
                else:  # text
                    content = self.log_text.get(1.0, tk.END)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                logger.info(f"Logs exported to: {filepath}")
                messagebox.showinfo("Success", f"Logs saved!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error exporting logs: {e}")
                messagebox.showerror("Error", f"Failed to save:\n{e}")

    def _on_copy_all(self):
        """Copy all visible logs to clipboard"""
        content = self.log_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("No Data", "No logs to copy")
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            messagebox.showinfo("Success", "All logs copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying logs: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _on_copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self.update()
                messagebox.showinfo("Success", "Selected text copied to clipboard!")
            else:
                messagebox.showinfo("No Selection", "Please select text to copy")
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please select text to copy")
        except Exception as e:
            logger.error(f"Error copying selection: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _on_closing(self):
        """Handle window close"""
        if self.stream_running:
            self._on_stop()
        self.destroy()


def main():
    """Main entry point"""
    app = LogViewerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
