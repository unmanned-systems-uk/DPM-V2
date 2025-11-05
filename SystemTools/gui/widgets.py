"""
Reusable GUI Widgets for DPM Diagnostic Tool
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional


class StatusIndicator(tk.Canvas):
    """Colored status indicator (circle)"""

    def __init__(self, parent, size=16, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, **kwargs)
        self.size = size
        self.circle = None
        self.set_status("gray")

    def set_status(self, status: str):
        """Set status color: green, yellow, red, gray"""
        colors = {
            "green": "#00FF00",
            "yellow": "#FFFF00",
            "red": "#FF0000",
            "gray": "#808080"
        }

        color = colors.get(status.lower(), "#808080")

        if self.circle:
            self.delete(self.circle)

        self.circle = self.create_oval(2, 2, self.size-2, self.size-2,
                                       fill=color, outline="white", width=2)


class LabeledEntry(ttk.Frame):
    """Label with text entry"""

    def __init__(self, parent, label_text: str, default_value: str = "",
                 width: int = 20, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text, width=15, anchor='w')
        self.label.pack(side=tk.LEFT, padx=5)

        self.entry = ttk.Entry(self, width=width)
        self.entry.insert(0, default_value)
        self.entry.pack(side=tk.LEFT, padx=5)

    def get(self) -> str:
        """Get entry value"""
        return self.entry.get()

    def set(self, value: str):
        """Set entry value"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class LabeledSpinbox(ttk.Frame):
    """Label with spinbox (number input)"""

    def __init__(self, parent, label_text: str, from_: int, to: int,
                 default_value: int = 0, width: int = 10, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = ttk.Label(self, text=label_text, width=15, anchor='w')
        self.label.pack(side=tk.LEFT, padx=5)

        self.spinbox = ttk.Spinbox(self, from_=from_, to=to, width=width)
        self.spinbox.set(default_value)
        self.spinbox.pack(side=tk.LEFT, padx=5)

    def get(self) -> int:
        """Get spinbox value"""
        try:
            return int(self.spinbox.get())
        except:
            return 0

    def set(self, value: int):
        """Set spinbox value"""
        self.spinbox.set(value)


class ScrolledTextLog(ttk.Frame):
    """Scrolled text widget for logs with color support"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create text widget with scrollbar
        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10)
        self.text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colors
        self.text.tag_config("ERROR", foreground="#FF0000")
        self.text.tag_config("WARN", foreground="#FFA500")
        self.text.tag_config("INFO", foreground="#00FF00")
        self.text.tag_config("DEBUG", foreground="#808080")
        self.text.tag_config("SUCCESS", foreground="#00FF00")

        # Auto-scroll enabled by default
        self.auto_scroll = True

    def append(self, message: str, tag: Optional[str] = None):
        """Append message with optional color tag"""
        self.text.insert(tk.END, message + "\n", tag)

        if self.auto_scroll:
            self.text.see(tk.END)

    def clear(self):
        """Clear all text"""
        self.text.delete(1.0, tk.END)

    def get_all(self) -> str:
        """Get all text"""
        return self.text.get(1.0, tk.END)

    def set_auto_scroll(self, enabled: bool):
        """Enable/disable auto-scroll"""
        self.auto_scroll = enabled


class ConnectionStatusBar(ttk.Frame):
    """Status bar showing connection info"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Status indicator
        self.indicator = StatusIndicator(self, size=12)
        self.indicator.pack(side=tk.LEFT, padx=5)

        # Status text
        self.status_label = ttk.Label(self, text="Disconnected")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Info text
        self.info_label = ttk.Label(self, text="")
        self.info_label.pack(side=tk.LEFT, padx=5)

    def set_status(self, connected: bool, info_text: str = ""):
        """Update status bar"""
        if connected:
            self.indicator.set_status("green")
            self.status_label.config(text="Connected")
        else:
            self.indicator.set_status("red")
            self.status_label.config(text="Disconnected")

        self.info_label.config(text=info_text)
