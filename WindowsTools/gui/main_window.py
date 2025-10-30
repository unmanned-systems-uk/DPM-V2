"""
Main Window for DPM Diagnostic Tool
Tabbed interface for all diagnostic functions
"""

import tkinter as tk
from tkinter import ttk, messagebox

from utils.logger import logger
from utils.config import config
from gui.widgets import ConnectionStatusBar
from version import get_version_string, VERSION, VERSION_NAME, BUILD_DATE


class MainWindow:
    """Main application window"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"DPM Diagnostic Tool {get_version_string()}")
        self.root.geometry("1200x800")

        # Set minimum size
        self.root.minsize(1000, 600)

        # Initialize components
        self.tcp_client = None
        self.tabs = {}

        self._create_menu()
        self._create_notebook()
        self._create_status_bar()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        logger.info("Main window initialized")

    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def _create_notebook(self):
        """Create tabbed notebook"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tabs will be added by set_tabs() method
        logger.debug("Notebook created")

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ConnectionStatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        logger.debug("Status bar created")

    def set_tabs(self, tabs_dict: dict):
        """Set tabs from dictionary {name: frame}"""
        self.tabs = tabs_dict

        for name, frame in tabs_dict.items():
            self.notebook.add(frame, text=name)

        logger.info(f"Added {len(tabs_dict)} tabs")

    def update_status_bar(self, connected: bool, info: str = ""):
        """Update status bar"""
        self.status_bar.set_status(connected, info)

    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About DPM Diagnostic Tool",
            f"DPM Diagnostic Tool {get_version_string()}\n"
            f"Build Date: {BUILD_DATE}\n\n"
            "Windows diagnostic and testing tool for DPM Payload Manager.\n\n"
            "Features:\n"
            "- Real-time protocol monitoring\n"
            "- Command testing and debugging\n"
            "- Camera and system monitoring\n"
            "- Docker log viewing\n\n"
            "Created: October 2025"
        )

    def on_closing(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            logger.info("Application closing...")

            # Cleanup (will be handled by tabs)
            if hasattr(self, 'tcp_client') and self.tcp_client:
                if self.tcp_client.is_connected():
                    self.tcp_client.disconnect()

            self.root.destroy()

    def run(self):
        """Start the GUI event loop"""
        logger.info("Starting GUI event loop")
        self.root.mainloop()
