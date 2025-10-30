"""
Protocol Inspector Tab for DPM Diagnostic Tool
Captures and displays all protocol messages
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from utils.logger import logger
from utils.config import config


class ProtocolInspectorTab(ttk.Frame):
    """Protocol Inspector tab - captures all messages"""

    def __init__(self, parent):
        super().__init__(parent)

        self.messages = []  # Store all messages
        self.filter_var = tk.StringVar(value="All")

        # Performance optimization for high-frequency messages
        self.MAX_MESSAGES = 500  # Keep only last 500 messages
        self.pending_updates = []  # Queue for batched GUI updates
        self.update_scheduled = False  # Flag to prevent multiple update schedules

        self._create_ui()

        logger.debug("Protocol Inspector tab initialized")

    def _create_ui(self):
        """Create UI elements"""
        # Top: Controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filter dropdown
        ttk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=5)

        self.filter_combo = ttk.Combobox(control_frame, textvariable=self.filter_var,
                                         values=["All", "Commands", "Responses", "Status", "Heartbeat"],
                                         state="readonly", width=15)
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # Statistics
        self.stats_label = ttk.Label(control_frame, text="Messages: 0")
        self.stats_label.pack(side=tk.RIGHT, padx=10)

        # Message list (TreeView)
        list_frame = ttk.LabelFrame(self, text="Message List", padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create TreeView
        columns = ("time", "type", "direction", "summary")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Define headings
        self.tree.heading("time", text="Time")
        self.tree.heading("type", text="Type")
        self.tree.heading("direction", text="Direction")
        self.tree.heading("summary", text="Summary")

        # Define column widths
        self.tree.column("time", width=100)
        self.tree.column("type", width=120)
        self.tree.column("direction", width=80)
        self.tree.column("summary", width=600)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_message_selected)

        # Message detail pane
        detail_frame = ttk.LabelFrame(self, text="Message Detail (JSON)", padding=5)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.detail_text = tk.Text(detail_frame, height=10, wrap=tk.WORD)
        detail_scroll = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scroll.set)

        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Clear All", command=self._clear_messages).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Export to JSON...", command=self._export_messages).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Copy Selected", command=self._copy_selected).pack(side=tk.LEFT, padx=2)

        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.RIGHT, padx=10)

    def add_message(self, message: Dict[str, Any], direction: str):
        """Add a message to the inspector (batched for performance)"""
        # Store message with metadata
        msg_data = {
            "timestamp": datetime.now(),
            "message": message,
            "direction": direction  # "sent", "received"
        }

        self.messages.append(msg_data)

        # Limit message history to prevent memory issues
        if len(self.messages) > self.MAX_MESSAGES:
            # Remove oldest messages beyond limit
            excess = len(self.messages) - self.MAX_MESSAGES
            self.messages = self.messages[excess:]

        # Queue message for batched GUI update
        self.pending_updates.append(msg_data)

        # Schedule GUI update if not already scheduled (throttle to 200ms)
        if not self.update_scheduled:
            self.update_scheduled = True
            self.after(200, self._process_pending_updates)

    def _process_pending_updates(self):
        """Process queued messages and update GUI (batched)"""
        if not self.pending_updates:
            self.update_scheduled = False
            return

        # Get all pending messages
        messages_to_process = self.pending_updates[:]
        self.pending_updates.clear()

        # Process each message with filters
        search_text = self.search_var.get().lower()

        for msg_data in messages_to_process:
            # Check filter
            if not self._passes_filter(msg_data):
                continue

            # Check search
            if search_text:
                msg_str = json.dumps(msg_data["message"]).lower()
                if search_text not in msg_str:
                    continue

            # Add to tree
            self._add_to_tree(msg_data)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll_var.get():
            children = self.tree.get_children()
            if children:
                self.tree.see(children[-1])

        # Update statistics
        self._update_stats()

        # Reset flag
        self.update_scheduled = False

    def _add_to_tree(self, msg_data: Dict[str, Any]):
        """Add message to TreeView"""
        message = msg_data["message"]
        timestamp = msg_data["timestamp"]
        direction = msg_data["direction"]

        # Extract message info
        msg_type = message.get("message_type", "unknown")
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]

        # Create summary
        summary = self._create_summary(message)

        # Direction symbol
        dir_symbol = "→" if direction == "sent" else "←"

        # Add to tree
        self.tree.insert("", tk.END, values=(time_str, msg_type, dir_symbol, summary))

    def _create_summary(self, message: Dict[str, Any]) -> str:
        """Create a one-line summary of the message"""
        msg_type = message.get("message_type", "unknown")
        payload = message.get("payload", {})

        if msg_type == "command":
            command = payload.get("command", "?")
            return f"Command: {command}"

        elif msg_type == "response":
            status = payload.get("status", "?")
            return f"Response: {status}"

        elif msg_type == "status":
            # Extract camera/system status
            camera = payload.get("camera", {})
            system = payload.get("system", {})
            return f"Status: Camera={camera.get('connected', '?')}, CPU={system.get('cpu_usage_percent', '?')}%"

        elif msg_type == "heartbeat":
            status = payload.get("status", "?")
            return f"Heartbeat: {status}"

        else:
            return str(payload)[:100]

    def _passes_filter(self, msg_data: Dict[str, Any]) -> bool:
        """Check if message passes current filter"""
        filter_value = self.filter_var.get()

        if filter_value == "All":
            return True

        msg_type = msg_data["message"]["message_type"]

        if filter_value == "Commands" and msg_type == "command":
            return True
        if filter_value == "Responses" and msg_type == "response":
            return True
        if filter_value == "Status" and msg_type == "status":
            return True
        if filter_value == "Heartbeat" and msg_type == "heartbeat":
            return True

        return False

    def _on_filter_changed(self, event=None):
        """Handle filter change"""
        # Rebuild tree with new filter
        self._rebuild_tree()

    def _on_search_changed(self, event=None):
        """Handle search text change"""
        # Rebuild tree with search filter
        self._rebuild_tree()

    def _rebuild_tree(self):
        """Rebuild tree with current filters"""
        # Clear tree
        self.tree.delete(*self.tree.get_children())

        # Re-add filtered messages
        search_text = self.search_var.get().lower()

        for msg_data in self.messages:
            # Check filter
            if not self._passes_filter(msg_data):
                continue

            # Check search
            if search_text:
                msg_str = json.dumps(msg_data["message"]).lower()
                if search_text not in msg_str:
                    continue

            # Add to tree
            self._add_to_tree(msg_data)

    def _on_message_selected(self, event=None):
        """Handle message selection"""
        selection = self.tree.selection()
        if not selection:
            return

        # Get selected index
        item = selection[0]
        index = self.tree.index(item)

        # Get corresponding message (accounting for filters)
        # This is simplified - in production would track indices
        if index < len(self.messages):
            msg_data = self.messages[index]
            message = msg_data["message"]

            # Display formatted JSON
            self.detail_text.delete(1.0, tk.END)
            formatted = json.dumps(message, indent=2)
            self.detail_text.insert(1.0, formatted)

    def _update_stats(self):
        """Update statistics label"""
        total = len(self.messages)
        visible = len(self.tree.get_children())

        if visible == total:
            self.stats_label.config(text=f"Messages: {total}")
        else:
            self.stats_label.config(text=f"Messages: {visible} / {total}")

    def _clear_messages(self):
        """Clear all messages"""
        if messagebox.askyesno("Clear Messages", "Clear all captured messages?"):
            self.messages.clear()
            self.tree.delete(*self.tree.get_children())
            self.detail_text.delete(1.0, tk.END)
            self._update_stats()
            logger.info("Protocol messages cleared")

    def _export_messages(self):
        """Export messages to JSON file"""
        if not self.messages:
            messagebox.showinfo("No Data", "No messages to export")
            return

        # Get save location
        default_dir = config.get("data", "log_directory", str(Path.home() / "Documents"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filepath = filedialog.asksaveasfilename(
            title="Export Messages",
            initialdir=default_dir,
            initialfile=f"protocol_messages_{timestamp}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                # Convert to serializable format
                export_data = []
                for msg_data in self.messages:
                    export_data.append({
                        "timestamp": msg_data["timestamp"].isoformat(),
                        "direction": msg_data["direction"],
                        "message": msg_data["message"]
                    })

                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2)

                logger.info(f"Messages exported to: {filepath}")
                messagebox.showinfo("Success", f"Messages exported!\n\n{filepath}")

            except Exception as e:
                logger.error(f"Error exporting messages: {e}")
                messagebox.showerror("Error", f"Failed to export:\n{e}")

    def _copy_selected(self):
        """Copy selected message to clipboard"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a message first")
            return

        try:
            # Get selected message
            item = selection[0]
            index = self.tree.index(item)

            if index < len(self.messages):
                msg_data = self.messages[index]
                message = msg_data["message"]

                # Format as JSON
                formatted = json.dumps(message, indent=2)

                # Copy to clipboard
                self.clipboard_clear()
                self.clipboard_append(formatted)
                self.update()

                messagebox.showinfo("Success", "Message copied to clipboard!")

        except Exception as e:
            logger.error(f"Error copying message: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")
