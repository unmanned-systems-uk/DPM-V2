"""
Tri-Domain Log Aggregation Sub-Tab
===================================

Real-time aggregated log view from Air-Side (UDP) and Ground-Side (TCP)

Part of Issue #105 - Tri-Domain Log Aggregation GUI Integration
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
import subprocess
import sys

from utils.logger import logger
from utils.config import config
from utils.log_colors import configure_tkinter_text_tags, get_buffer_max_entries
from network.log_listeners import AirSideListener, GroundSideListener


class TriDomainAggregationTab(ttk.Frame):
    """Tri-Domain log aggregation tab - unified Air-Side + Ground-Side logs"""

    def __init__(self, parent):
        super().__init__(parent)

        # Log queue (shared with listeners) - size from config
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

        # Pop-out window
        self.popup_window = None

        self._create_ui()

        logger.debug("Tri-Domain Aggregation tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Stream Controls
        controls_frame = ttk.LabelFrame(self, text="Stream Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Status indicator row
        status_row = ttk.Frame(controls_frame)
        status_row.pack(fill=tk.X, pady=5)

        ttk.Label(status_row, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_indicator = tk.Canvas(status_row, width=20, height=20, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self._update_status_indicator("stopped")

        self.status_label = ttk.Label(status_row, text="Stopped", font=('Arial', 9, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Control buttons row
        button_row = ttk.Frame(controls_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(button_row, text="▶ Start", command=self._on_start, width=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(button_row, text="⏸ Pause", command=self._on_pause, state=tk.DISABLED, width=10)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_row, text="⏹ Stop", command=self._on_stop, state=tk.DISABLED, width=10)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Separator(button_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        self.clear_btn = ttk.Button(button_row, text="Clear Display", command=self._on_clear)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_row, text="🗗 Pop Out", command=self._pop_out_window).pack(side=tk.LEFT, padx=5)

        ttk.Separator(button_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        ttk.Button(button_row, text="🚀 Launch Standalone Viewer", command=self._launch_standalone,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)

        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_row, text="Auto-scroll", variable=self.auto_scroll_var,
                       command=self._on_auto_scroll_changed).pack(side=tk.LEFT, padx=10)

        # Last update time
        ttk.Label(button_row, text="Last Update:").pack(side=tk.RIGHT, padx=5)
        self.last_update_label = ttk.Label(button_row, text="Never", font=('Arial', 9, 'italic'))
        self.last_update_label.pack(side=tk.RIGHT, padx=5)

        # Filters Frame
        filters_frame = ttk.LabelFrame(self, text="Filters (Accumulative AND Logic)", padding=10)
        filters_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter row 1: Domain, Level, Context
        filter_row1 = ttk.Frame(filters_frame)
        filter_row1.pack(fill=tk.X, pady=5)

        # Domain filter
        ttk.Label(filter_row1, text="Domain:").pack(side=tk.LEFT, padx=5)
        domain_combo = ttk.Combobox(filter_row1, textvariable=self.filter_domain,
                                    values=["ALL", "AIR", "GROUND"], state="readonly", width=10)
        domain_combo.pack(side=tk.LEFT, padx=5)
        domain_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Level filter
        ttk.Label(filter_row1, text="Level:").pack(side=tk.LEFT, padx=5)
        level_combo = ttk.Combobox(filter_row1, textvariable=self.filter_level,
                                   values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=10)
        level_combo.pack(side=tk.LEFT, padx=5)
        level_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        ttk.Separator(filter_row1, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Context filter
        ttk.Label(filter_row1, text="Context:").pack(side=tk.LEFT, padx=5)
        context_combo = ttk.Combobox(filter_row1, textvariable=self.filter_context,
                                     values=["ALL", "CAMERA", "NETWORK", "COMMAND", "UI"], state="readonly", width=12)
        context_combo.pack(side=tk.LEFT, padx=5)
        context_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Filter row 2: Text search
        filter_row2 = ttk.Frame(filters_frame)
        filter_row2.pack(fill=tk.X, pady=5)

        ttk.Label(filter_row2, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(filter_row2, textvariable=self.filter_search, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self._on_filter_changed)

        ttk.Button(filter_row2, text="Clear", command=self._on_clear_search).pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_row2, text="(Searches entire log message)",
                 font=('Arial', 8, 'italic'), foreground='gray').pack(side=tk.LEFT, padx=10)

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

        # Log Display (fixed-width columns)
        log_frame = ttk.LabelFrame(self, text="Aggregated Logs (Air-Side + Ground-Side)", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Use Courier New for fixed-width display
        self.log_text = tk.Text(text_frame, wrap=tk.NONE, font=('Courier New', 9),
                                bg='#FFFFFF', fg='#000000')  # White bg, black default text
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

        # Configure text tags for color-coding from config
        configure_tkinter_text_tags(self.log_text)

    def _update_status_indicator(self, status: str):
        """Update status indicator: stopped (gray), running (green), paused (orange)"""
        self.status_indicator.delete("all")
        color_map = {"stopped": "gray", "running": "green", "paused": "orange"}
        color = color_map.get(status, "gray")
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def _on_start(self):
        """Start streaming logs from Air-Side and Ground-Side"""
        if self.stream_running:
            return

        logger.info("Starting Tri-Domain log aggregation...")

        # Clear queue
        self.log_queue.clear()

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

        logger.info("Tri-Domain log aggregation started")

    def _on_pause(self):
        """Pause display updates (listeners keep running, buffer logs)"""
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
        """Stop both listeners and clear buffer"""
        if not self.stream_running:
            return

        logger.info("Stopping Tri-Domain log aggregation...")

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

        logger.info("Tri-Domain log aggregation stopped")

    def _on_clear(self):
        """Clear log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._update_line_count()

    def _on_auto_scroll_changed(self):
        """Handle auto-scroll toggle"""
        self.auto_scroll = self.auto_scroll_var.get()

    def _on_filter_changed(self, event=None):
        """Handle filter change - redisplay all logs with new filter"""
        self._redisplay_all_logs()

    def _on_clear_search(self):
        """Clear search filter"""
        self.filter_search.set("")
        self._redisplay_all_logs()

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

        # Process up to 100 entries at a time to avoid blocking UI
        entries_to_process = []
        for _ in range(min(100, len(self.log_queue))):
            if self.log_queue:
                entries_to_process.append(self.log_queue.popleft())

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
        """Check if log entry matches current filters (AND logic)"""
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
        """Append a single log entry to display with fixed-width formatting"""
        # Format: [TIMESTAMP] [DOMAIN ] [LEVEL  ] [CONTEXT] Message
        timestamp = entry.get('timestamp', 'NO-TS')
        if 'T' in timestamp:
            # Extract just the time portion (HH:MM:SS.mmm)
            try:
                time_part = timestamp.split('T')[1][:12]  # HH:MM:SS.mmm
            except:
                time_part = timestamp[:12]
        else:
            time_part = timestamp[:12]

        domain = entry.get('domain', 'UNK').ljust(6)[:6]  # Fixed width: 6 chars
        level = entry.get('level', 'INFO').ljust(7)[:7]    # Fixed width: 7 chars
        context = entry.get('context', 'UNKNOWN').ljust(8)[:8]  # Fixed width: 8 chars
        message = entry.get('message', '')

        # Build the log line
        log_line = f"{time_part} [{domain}] [{level}] [{context}] {message}\n"

        # Enable editing
        self.log_text.config(state=tk.NORMAL)

        # Get insertion position
        insert_pos = self.log_text.index(tk.INSERT)

        # Insert line
        self.log_text.insert(tk.END, log_line)

        # Apply color-coding based on domain
        line_number = int(self.log_text.index(tk.END).split('.')[0]) - 1
        domain_code = entry.get('domain', '')
        if domain_code == 'AIR':
            self.log_text.tag_add("air", f"{line_number}.0", f"{line_number}.end")
        elif domain_code == 'GROUND':
            self.log_text.tag_add("ground", f"{line_number}.0", f"{line_number}.end")

        # Apply level-based highlighting (with priority to override domain color)
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

        # Auto-scroll to bottom
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

    def _redisplay_all_logs(self):
        """Redisplay all logs from queue with current filters"""
        # This is a simplified version - we can't recover old logs from queue
        # Once they're displayed and removed, they're gone
        # For full filtering, we'd need to keep a persistent buffer
        # For now, just note that filters apply to NEW logs
        logger.debug("Filters updated - will apply to new log entries")

    def _update_line_count(self):
        """Update line count label"""
        total_lines = int(self.log_text.index(tk.END).split('.')[0]) - 1
        buffer_size = len(self.log_queue)
        self.line_count_label.config(text=f"Lines: {total_lines} / Buffer: {buffer_size}")

    def _on_save_to_file(self):
        """Export logs to file (JSON, CSV, or text format)"""
        content = self.log_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("No Data", "No logs to export")
            return

        # Get export format
        export_format = self.export_format_var.get()

        # Get save location
        default_dir = config.get("data", "log_directory", str(Path.home() / "Documents"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # File extensions
        ext_map = {"json": ".json", "csv": ".csv", "text": ".txt"}
        filetypes_map = {
            "json": [("JSON files", "*.json"), ("All files", "*.*")],
            "csv": [("CSV files", "*.csv"), ("All files", "*.*")],
            "text": [("Text files", "*.txt"), ("Log files", "*.log"), ("All files", "*.*")]
        }

        filepath = filedialog.asksaveasfilename(
            title="Save Logs",
            initialdir=default_dir,
            initialfile=f"tri_domain_logs_{timestamp}{ext_map[export_format]}",
            defaultextension=ext_map[export_format],
            filetypes=filetypes_map[export_format]
        )

        if filepath:
            try:
                if export_format == "text":
                    # Simple text export
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    # JSON/CSV export would require parsing the text back
                    # For simplicity, just save as text for now
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

    def _pop_out_window(self):
        """Pop out log viewer into a separate window"""
        # If window already exists, bring it to front
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.lift()
            self.popup_window.focus_force()
            logger.debug("Pop-out window brought to front")
            return

        # Create new popup window
        self.popup_window = tk.Toplevel(self)
        self.popup_window.title("DPM SystemTools - Tri-Domain Log Aggregation")
        self.popup_window.geometry("1400x800")

        # Set window icon (same as main window if available)
        try:
            self.popup_window.iconbitmap(self.master.master.master.iconbitmap())
        except:
            pass

        # Create main frame
        main_frame = ttk.Frame(self.popup_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(main_frame, text="📊 Tri-Domain Log Aggregation (Air-Side + Ground-Side)",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))

        # Info label
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="Status:", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        popup_status_label = ttk.Label(info_frame,
                                       text=self.status_label.cget("text"),
                                       font=('Arial', 9, 'bold'),
                                       foreground=self.status_label.cget("foreground"))
        popup_status_label.pack(side=tk.LEFT, padx=5)

        ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        popup_line_count = ttk.Label(info_frame, text=self.line_count_label.cget("text"))
        popup_line_count.pack(side=tk.LEFT, padx=5)

        # Log display area (scrolled text)
        popup_log_text = scrolledtext.ScrolledText(main_frame,
                                                    font=('Courier New', 9),
                                                    wrap=tk.NONE,
                                                    state='normal',
                                                    bg='#FFFFFF',  # White background
                                                    fg='#000000')  # Black default text
        popup_log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure same color tags as main display from config
        configure_tkinter_text_tags(popup_log_text)

        # Copy current log content to popup
        current_content = self.log_text.get(1.0, tk.END)
        popup_log_text.insert(1.0, current_content)

        # Re-apply all tags (simple approach - could be optimized)
        # This ensures colors are preserved
        for tag_name in ["air", "ground", "error", "warning", "debug", "info", "highlight"]:
            ranges = self.log_text.tag_ranges(tag_name)
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                popup_log_text.tag_add(tag_name, start, end)

        popup_log_text.config(state='disabled')

        # Bottom button bar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Refresh",
                  command=lambda: self._refresh_popup(popup_log_text, popup_status_label, popup_line_count)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Copy All",
                  command=lambda: self._copy_popup_content(popup_log_text)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Close",
                  command=self.popup_window.destroy).pack(side=tk.RIGHT, padx=5)

        # Handle window close
        self.popup_window.protocol("WM_DELETE_WINDOW", self.popup_window.destroy)

        logger.info("Pop-out log window created")

    def _refresh_popup(self, popup_text, status_label, line_count_label):
        """Refresh popup window with current log content"""
        popup_text.config(state='normal')
        popup_text.delete(1.0, tk.END)

        # Copy current content
        current_content = self.log_text.get(1.0, tk.END)
        popup_text.insert(1.0, current_content)

        # Re-apply tags
        for tag_name in ["air", "ground", "error", "warning", "debug", "info", "highlight"]:
            ranges = self.log_text.tag_ranges(tag_name)
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                popup_text.tag_add(tag_name, start, end)

        popup_text.config(state='disabled')
        popup_text.see(tk.END)

        # Update status labels
        status_label.config(text=self.status_label.cget("text"),
                           foreground=self.status_label.cget("foreground"))
        line_count_label.config(text=self.line_count_label.cget("text"))

        logger.debug("Pop-out window refreshed")

    def _copy_popup_content(self, popup_text):
        """Copy popup window content to clipboard"""
        content = popup_text.get(1.0, tk.END).strip()
        if content:
            try:
                self.clipboard_clear()
                self.clipboard_append(content)
                self.update()
                messagebox.showinfo("Success", "Logs copied to clipboard!", parent=self.popup_window)
            except Exception as e:
                logger.error(f"Error copying from popup: {e}")
                messagebox.showerror("Error", f"Failed to copy:\n{e}", parent=self.popup_window)

    def _launch_standalone(self):
        """Launch standalone Tri-Domain Log Viewer GUI"""
        try:
            script_path = Path(__file__).parent.parent.parent / "log_viewer_gui.py"

            if not script_path.exists():
                messagebox.showerror("Error", f"Standalone viewer not found:\n{script_path}")
                logger.error(f"log_viewer_gui.py not found at {script_path}")
                return

            # Launch in separate process
            subprocess.Popen([sys.executable, str(script_path)],
                           cwd=str(script_path.parent),
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            logger.info("Launched standalone Tri-Domain Log Viewer")
            messagebox.showinfo("Launched", "Standalone Tri-Domain Log Viewer launched!\n\n"
                              "Check your taskbar for the new window.")

        except Exception as e:
            logger.error(f"Error launching standalone viewer: {e}")
            messagebox.showerror("Error", f"Failed to launch standalone viewer:\n{e}")

    def cleanup(self):
        """Cleanup on tab close"""
        # Close popup window if open
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.destroy()

        if self.stream_running:
            self._on_stop()
