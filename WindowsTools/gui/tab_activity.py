"""
Activity Log Tab for DPM Diagnostic Tool
Real-time log of application events for debugging and monitoring
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Optional
from pathlib import Path

from utils.logger import logger


class ActivityLogTab(ttk.Frame):
    """Activity Log tab - monitors application events"""

    # Event categories
    CATEGORY_TCP = "TCP"
    CATEGORY_UDP = "UDP"
    CATEGORY_CAMERA = "Camera"
    CATEGORY_SYSTEM = "System"
    CATEGORY_GUI = "GUI"
    CATEGORY_ERROR = "Error"
    CATEGORY_INFO = "Info"

    # Category colors
    CATEGORY_COLORS = {
        CATEGORY_TCP: "#0066cc",      # Blue
        CATEGORY_UDP: "#00cc66",      # Green
        CATEGORY_CAMERA: "#cc6600",   # Orange
        CATEGORY_SYSTEM: "#6600cc",   # Purple
        CATEGORY_GUI: "#00cccc",      # Cyan
        CATEGORY_ERROR: "#cc0000",    # Red
        CATEGORY_INFO: "#666666",     # Gray
    }

    def __init__(self, parent):
        super().__init__(parent)

        self.events = []  # Store all events
        self.filter_var = tk.StringVar(value="All")
        self.max_events = 1000  # Keep last 1000 events

        # Performance optimization
        self.pending_events = []
        self.update_scheduled = False

        self._create_ui()

        logger.debug("Activity Log tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter dropdown
        ttk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=5)

        self.filter_combo = ttk.Combobox(
            control_frame,
            textvariable=self.filter_var,
            values=["All", "TCP", "UDP", "Camera", "System", "GUI", "Error", "Info"],
            state="readonly",
            width=15
        )
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # Statistics
        self.stats_label = ttk.Label(control_frame, text="Events: 0")
        self.stats_label.pack(side=tk.RIGHT, padx=10)

        # Event list (TreeView with colored tags)
        list_frame = ttk.LabelFrame(self, text="Activity Events", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create TreeView
        columns = ("time", "category", "event")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)

        # Define headings
        self.tree.heading("time", text="Time")
        self.tree.heading("category", text="Category")
        self.tree.heading("event", text="Event")

        # Define column widths
        self.tree.column("time", width=100)
        self.tree.column("category", width=100)
        self.tree.column("event", width=700)

        # Configure tags for colors
        for category, color in self.CATEGORY_COLORS.items():
            self.tree.tag_configure(category, foreground=color)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Clear All", command=self._clear_events).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export to File...", command=self._export_events).pack(side=tk.LEFT, padx=2)

        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.RIGHT, padx=10)

    def log_event(self, category: str, message: str):
        """Log an event to the activity log"""
        event_data = {
            "timestamp": datetime.now(),
            "category": category,
            "message": message
        }

        self.events.append(event_data)

        # Limit event history
        if len(self.events) > self.max_events:
            excess = len(self.events) - self.max_events
            self.events = self.events[excess:]

        # Queue event for batched GUI update
        self.pending_events.append(event_data)

        # Schedule GUI update if not already scheduled (throttle to 100ms)
        if not self.update_scheduled:
            self.update_scheduled = True
            self.after(100, self._process_pending_events)

    def _process_pending_events(self):
        """Process queued events and update GUI (batched)"""
        if not self.pending_events:
            self.update_scheduled = False
            return

        # Get all pending events
        events_to_process = self.pending_events[:]
        self.pending_events.clear()

        # Process each event with filters
        search_text = self.search_var.get().lower()

        for event_data in events_to_process:
            # Check filter
            if not self._passes_filter(event_data):
                continue

            # Check search
            if search_text:
                if search_text not in event_data["message"].lower():
                    continue

            # Add to tree
            self._add_to_tree(event_data)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll_var.get():
            children = self.tree.get_children()
            if children:
                self.tree.see(children[-1])

        # Update statistics
        self._update_stats()

        # Reset flag
        self.update_scheduled = False

    def _add_to_tree(self, event_data: dict):
        """Add event to TreeView"""
        timestamp = event_data["timestamp"]
        category = event_data["category"]
        message = event_data["message"]

        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]

        # Add to tree with category tag for coloring
        self.tree.insert("", tk.END, values=(time_str, category, message), tags=(category,))

    def _passes_filter(self, event_data: dict) -> bool:
        """Check if event passes current filter"""
        filter_value = self.filter_var.get()

        if filter_value == "All":
            return True

        return event_data["category"] == filter_value

    def _on_filter_changed(self, event=None):
        """Handle filter change"""
        self._rebuild_tree()

    def _on_search_changed(self, event=None):
        """Handle search text change"""
        self._rebuild_tree()

    def _rebuild_tree(self):
        """Rebuild tree with current filters"""
        # Clear tree
        self.tree.delete(*self.tree.get_children())

        # Re-add filtered events
        search_text = self.search_var.get().lower()

        for event_data in self.events:
            # Check filter
            if not self._passes_filter(event_data):
                continue

            # Check search
            if search_text:
                if search_text not in event_data["message"].lower():
                    continue

            # Add to tree
            self._add_to_tree(event_data)

        # Update statistics
        self._update_stats()

    def _update_stats(self):
        """Update statistics label"""
        total = len(self.events)
        visible = len(self.tree.get_children())

        if visible == total:
            self.stats_label.config(text=f"Events: {total}")
        else:
            self.stats_label.config(text=f"Events: {visible} / {total}")

    def _clear_events(self):
        """Clear all events"""
        if messagebox.askyesno("Clear Events", "Clear all activity events?"):
            self.events.clear()
            self.tree.delete(*self.tree.get_children())
            self._update_stats()
            logger.info("Activity events cleared")

    def _export_events(self):
        """Export events to text file"""
        if not self.events:
            messagebox.showinfo("No Data", "No events to export")
            return

        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Export Activity Log",
            initialfile=f"activity_log_{timestamp}.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filepath:
            try:
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("DPM Diagnostic Tool - Activity Log\n")
                    f.write("=" * 80 + "\n\n")

                    for event_data in self.events:
                        timestamp = event_data["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        category = event_data["category"]
                        message = event_data["message"]
                        f.write(f"[{timestamp}] [{category:8s}] {message}\n")

                logger.info(f"Activity log exported to: {filepath}")
                messagebox.showinfo("Success", f"Activity log exported!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error exporting activity log: {e}")
                messagebox.showerror("Error", f"Failed to export:\n{e}")
