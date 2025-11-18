"""
File Browser Tab - Issue #136
Enhanced with sub-tabs for Images and Docker Logs
Provides GUI interface for downloading files from Air-Side via SFTP
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading
from datetime import datetime

from network.sftp_client import AirSideSFTPClient
from network.ssh_client import SSHClient
from utils.logger import logger
from utils.config import config


class FileBrowserTab:
    """
    File Browser tab with sub-tabs for Images and Docker Logs.

    Provides GUI interface to:
    - Browse and download camera images via SFTP
    - Download Air-Side logs from 3 sources:
      1. Host-mounted logs (Direct SFTP)
      2. Container-internal structured logs (Docker cp + SFTP)
      3. Docker container logs (SSH streaming)
    """

    def __init__(self, parent):
        """
        Initialize File Browser tab with sub-tabs.

        Args:
            parent: Parent notebook widget
        """
        self.frame = ttk.Frame(parent, padding="10")

        # SFTP and SSH clients
        self.sftp_client: Optional[AirSideSFTPClient] = None
        self.ssh_client: Optional[SSHClient] = None
        self.connected = False

        # File list cache
        self.files: List[Dict[str, Any]] = []

        # Download state
        self.download_in_progress = False

        # Pop-out window
        self.popup_window = None
        self.popup_text = None

        # Create UI with sub-tabs
        self._create_ui()

        logger.info("File Browser tab initialized with sub-tabs")

    def _create_ui(self):
        """Create the File Browser UI with sub-tabs"""
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create sub-tabs
        self._create_images_tab()
        self._create_docker_logs_tab()

    def _create_images_tab(self):
        """Create Images sub-tab (existing camera_images functionality)"""
        self.images_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.images_frame, text="📷 Images")

        # Remote directory for images
        self.images_remote_directory = "/home/dpm/camera_images"

        # Top toolbar
        self._create_images_toolbar()

        # File list TreeView
        self._create_images_file_list()

        # Bottom panel (download controls)
        self._create_images_bottom_panel()

    def _create_images_toolbar(self):
        """Create toolbar for Images tab"""
        toolbar_frame = ttk.Frame(self.images_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # Connect button
        self.images_connect_btn = ttk.Button(
            toolbar_frame,
            text="🔌 Connect",
            command=self._on_images_connect_clicked,
            width=12
        )
        self.images_connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Refresh button
        self.images_refresh_btn = ttk.Button(
            toolbar_frame,
            text="🔄 Refresh",
            command=self._on_images_refresh_clicked,
            state=tk.DISABLED,
            width=12
        )
        self.images_refresh_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Filter label and dropdown
        ttk.Label(toolbar_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))

        self.images_filter_var = tk.StringVar(value="All Files")
        self.images_filter_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.images_filter_var,
            values=["All Files", "Images Only", "Logs Only"],
            state="readonly",
            width=15
        )
        self.images_filter_combo.pack(side=tk.LEFT)
        self.images_filter_combo.bind("<<ComboboxSelected>>", self._on_images_filter_changed)
        self.images_filter_combo.config(state=tk.DISABLED)

        # Remote directory label
        self.images_dir_label = ttk.Label(
            toolbar_frame,
            text=f"📂 {self.images_remote_directory}",
            foreground="gray"
        )
        self.images_dir_label.pack(side=tk.RIGHT, padx=(10, 0))

    def _create_images_file_list(self):
        """Create TreeView for images file listing"""
        # Frame for TreeView and scrollbar
        list_frame = ttk.Frame(self.images_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create TreeView
        columns = ("name", "size", "modified")
        self.images_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )

        # Define column headings
        self.images_tree.heading("name", text="Name", command=lambda: self._sort_images_by_column("name"))
        self.images_tree.heading("size", text="Size (KB)", command=lambda: self._sort_images_by_column("size"))
        self.images_tree.heading("modified", text="Modified", command=lambda: self._sort_images_by_column("modified"))

        # Define column widths
        self.images_tree.column("name", width=300, anchor=tk.W)
        self.images_tree.column("size", width=100, anchor=tk.E)
        self.images_tree.column("modified", width=180, anchor=tk.W)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.images_tree.yview)
        self.images_tree.configure(yscrollcommand=scrollbar.set)

        # Pack TreeView and scrollbar
        self.images_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click to download
        self.images_tree.bind("<Double-1>", lambda e: self._on_images_download_clicked())

    def _create_images_bottom_panel(self):
        """Create bottom panel for Images tab"""
        bottom_frame = ttk.Frame(self.images_frame)
        bottom_frame.pack(fill=tk.X)

        # Download button
        self.images_download_btn = ttk.Button(
            bottom_frame,
            text="📥 Download Selected File",
            command=self._on_images_download_clicked,
            state=tk.DISABLED,
            width=25
        )
        self.images_download_btn.pack(pady=(0, 10))

        # Progress bar
        self.images_progress_var = tk.DoubleVar(value=0.0)
        self.images_progress_bar = ttk.Progressbar(
            bottom_frame,
            variable=self.images_progress_var,
            maximum=100.0,
            mode="determinate"
        )
        self.images_progress_bar.pack(fill=tk.X, pady=(0, 5))

        # Status label
        self.images_status_var = tk.StringVar(value="Not connected")
        self.images_status_label = ttk.Label(
            bottom_frame,
            textvariable=self.images_status_var,
            foreground="gray"
        )
        self.images_status_label.pack(anchor=tk.W)

    def _create_docker_logs_tab(self):
        """Create Docker Logs sub-tab (NEW - Issue #136)"""
        self.logs_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.logs_frame, text="📋 Docker Logs")

        # Top toolbar with log source selector
        self._create_docker_logs_toolbar()

        # File list TreeView (reused for logs)
        self._create_docker_logs_file_list()

        # Bottom panel
        self._create_docker_logs_bottom_panel()

    def _create_docker_logs_toolbar(self):
        """Create toolbar for Docker Logs tab"""
        toolbar_frame = ttk.Frame(self.logs_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # Connect button
        self.logs_connect_btn = ttk.Button(
            toolbar_frame,
            text="🔌 Connect",
            command=self._on_logs_connect_clicked,
            width=12
        )
        self.logs_connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Refresh button
        self.logs_refresh_btn = ttk.Button(
            toolbar_frame,
            text="🔄 Refresh",
            command=self._on_logs_refresh_clicked,
            state=tk.DISABLED,
            width=12
        )
        self.logs_refresh_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Log source selector
        ttk.Label(toolbar_frame, text="Log Source:").pack(side=tk.LEFT, padx=(0, 5))

        self.log_source_var = tk.StringVar(value="Host Logs")
        self.log_source_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.log_source_var,
            values=["Host Logs", "Container Logs", "Docker Output", "System Logs"],
            state="readonly",
            width=18
        )
        self.log_source_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.log_source_combo.bind("<<ComboboxSelected>>", self._on_log_source_changed)
        self.log_source_combo.config(state=tk.DISABLED)

        # Tail count selector (for Docker Output source)
        ttk.Label(toolbar_frame, text="Tail:").pack(side=tk.LEFT, padx=(0, 5))

        self.tail_count_var = tk.StringVar(value="1000")
        self.tail_count_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.tail_count_var,
            values=["100", "500", "1000", "5000", "All"],
            state="readonly",
            width=8
        )
        self.tail_count_combo.pack(side=tk.LEFT)
        self.tail_count_combo.config(state=tk.DISABLED)

    def _create_docker_logs_file_list(self):
        """Create TreeView for Docker logs file listing"""
        # Frame for TreeView and scrollbar
        list_frame = ttk.Frame(self.logs_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create TreeView with Image ID column
        columns = ("name", "size", "source", "image_id")
        self.logs_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )

        # Define column headings
        self.logs_tree.heading("name", text="Log File", command=lambda: self._sort_logs_by_column("name"))
        self.logs_tree.heading("size", text="Size (KB)", command=lambda: self._sort_logs_by_column("size"))
        self.logs_tree.heading("source", text="Source", command=lambda: self._sort_logs_by_column("source"))
        self.logs_tree.heading("image_id", text="Image ID", command=lambda: self._sort_logs_by_column("image_id"))

        # Define column widths
        self.logs_tree.column("name", width=250, anchor=tk.W)
        self.logs_tree.column("size", width=80, anchor=tk.E)
        self.logs_tree.column("source", width=150, anchor=tk.W)
        self.logs_tree.column("image_id", width=120, anchor=tk.W)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=scrollbar.set)

        # Pack TreeView and scrollbar
        self.logs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click to download
        self.logs_tree.bind("<Double-1>", lambda e: self._on_logs_download_clicked())

    def _create_docker_logs_bottom_panel(self):
        """Create bottom panel for Docker Logs tab"""
        bottom_frame = ttk.Frame(self.logs_frame)
        bottom_frame.pack(fill=tk.X)

        # Button row
        button_row = ttk.Frame(bottom_frame)
        button_row.pack(pady=(0, 10))

        # Download button
        self.logs_download_btn = ttk.Button(
            button_row,
            text="📥 Download Selected Log",
            command=self._on_logs_download_clicked,
            state=tk.DISABLED,
            width=25
        )
        self.logs_download_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Pop Out button
        self.logs_popout_btn = ttk.Button(
            button_row,
            text="🗗 Pop Out",
            command=self._pop_out_docker_logs,
            state=tk.DISABLED,
            width=12
        )
        self.logs_popout_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.logs_progress_var = tk.DoubleVar(value=0.0)
        self.logs_progress_bar = ttk.Progressbar(
            bottom_frame,
            variable=self.logs_progress_var,
            maximum=100.0,
            mode="determinate"
        )
        self.logs_progress_bar.pack(fill=tk.X, pady=(0, 5))

        # Status label
        self.logs_status_var = tk.StringVar(value="Not connected")
        self.logs_status_label = ttk.Label(
            bottom_frame,
            textvariable=self.logs_status_var,
            foreground="gray"
        )
        self.logs_status_label.pack(anchor=tk.W)

    # ========== Images Tab Handlers ==========

    def _on_images_connect_clicked(self):
        """Handle Connect button click for Images tab"""
        if self.connected:
            # Disconnect
            self.disconnect()
            self._update_images_status("Disconnected")
            self.images_connect_btn.config(text="🔌 Connect")
            self.images_refresh_btn.config(state=tk.DISABLED)
            self.images_filter_combo.config(state=tk.DISABLED)
            self.images_download_btn.config(state=tk.DISABLED)
            self._clear_images_file_list()
        else:
            # Connect
            self._connect_to_air_side_images()

    def _connect_to_air_side_images(self):
        """Establish SFTP connection to Air-Side for Images tab"""
        try:
            self._update_images_status("Connecting to Air-Side...")

            # Load configuration
            host = config.get('network', 'air_side_ip', '10.0.1.53')
            username = config.get('ssh', 'username', 'dpm')
            password = config.get('ssh', 'password', '2350')

            logger.info(f"Connecting to Air-Side (Images): {username}@{host}")

            # Create SFTP client
            self.sftp_client = AirSideSFTPClient(
                host=host,
                username=username,
                password=password
            )

            # Connect
            if self.sftp_client.connect():
                self.connected = True
                self.images_connect_btn.config(text="🔌 Disconnect")
                self.images_refresh_btn.config(state=tk.NORMAL)
                self.images_filter_combo.config(state="readonly")
                self.images_download_btn.config(state=tk.NORMAL)

                self._update_images_status(f"Connected to {host}")
                logger.info(f"SFTP connection established to {host}")

                # Auto-refresh file list
                self._refresh_images_file_list()
            else:
                raise Exception("Connection failed")

        except Exception as e:
            logger.error(f"SFTP connection failed: {e}")
            messagebox.showerror(
                "Connection Error",
                f"Failed to connect to Air-Side:\n\n{str(e)}\n\nCheck network connection and credentials."
            )
            self._update_images_status("Connection failed")
            self.connected = False

    def _on_images_refresh_clicked(self):
        """Handle Refresh button click for Images tab"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to Air-Side first.")
            return

        self._refresh_images_file_list()

    def _refresh_images_file_list(self):
        """Refresh images file list from Air-Side"""
        try:
            self._update_images_status("Loading file list...")
            self.images_refresh_btn.config(state=tk.DISABLED)

            # Get current filter
            file_filter = self._get_images_file_extension_filter()

            # List files
            self.files = self.sftp_client.list_files(
                self.images_remote_directory,
                file_extension=file_filter
            )

            # Update TreeView
            self._populate_images_file_list()

            file_count = len(self.files)
            self._update_images_status(f"Found {file_count} file{'s' if file_count != 1 else ''}")
            logger.info(f"Loaded {file_count} image files from Air-Side")

        except Exception as e:
            logger.error(f"Failed to list image files: {e}")
            messagebox.showerror(
                "List Error",
                f"Failed to list files:\n\n{str(e)}"
            )
            self._update_images_status("Failed to load files")
        finally:
            if self.connected:
                self.images_refresh_btn.config(state=tk.NORMAL)

    def _get_images_file_extension_filter(self) -> Optional[str]:
        """Get file extension filter for images based on combo box selection"""
        filter_choice = self.images_filter_var.get()

        if filter_choice == "Images Only":
            return None  # Filter in populate method (multiple extensions)
        elif filter_choice == "Logs Only":
            return ".log"
        else:  # "All Files"
            return None

    def _populate_images_file_list(self):
        """Populate TreeView with images file list"""
        # Clear existing items
        self._clear_images_file_list()

        # Get current filter
        filter_choice = self.images_filter_var.get()

        # Filter files
        filtered_files = self.files
        if filter_choice == "Images Only":
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
            filtered_files = [f for f in self.files if f['name'].lower().endswith(image_extensions)]
        elif filter_choice == "Logs Only":
            log_extensions = ('.log', '.txt')
            filtered_files = [f for f in self.files if f['name'].lower().endswith(log_extensions)]

        # Add files to TreeView
        for file_info in filtered_files:
            # Format size in KB
            size_kb = file_info['size'] / 1024.0
            size_str = f"{size_kb:.1f}"

            # Format modified date
            try:
                modified_dt = datetime.fromisoformat(file_info['modified'])
                modified_str = modified_dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                modified_str = file_info['modified']

            # Insert into TreeView
            self.images_tree.insert(
                "",
                tk.END,
                values=(file_info['name'], size_str, modified_str),
                tags=(file_info['path'],)  # Store path in tags
            )

    def _clear_images_file_list(self):
        """Clear images TreeView"""
        for item in self.images_tree.get_children():
            self.images_tree.delete(item)

    def _on_images_filter_changed(self, event=None):
        """Handle filter selection change for Images tab"""
        if not self.connected:
            return

        # Re-populate list with current filter
        self._populate_images_file_list()

        filter_choice = self.images_filter_var.get()
        filtered_count = len(self.images_tree.get_children())
        self._update_images_status(f"Showing {filtered_count} file{'s' if filtered_count != 1 else ''} ({filter_choice})")

    def _sort_images_by_column(self, column: str):
        """Sort Images TreeView by column"""
        # Get all items
        items = [(self.images_tree.set(item, column), item) for item in self.images_tree.get_children('')]

        # Sort items
        if column == "size":
            # Sort numerically for size
            items.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=True)
        else:
            # Sort alphabetically
            items.sort(reverse=False)

        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.images_tree.move(item, '', index)

    def _on_images_download_clicked(self):
        """Handle Download button click for Images tab"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to Air-Side first.")
            return

        # Get selected item
        selected = self.images_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file to download.")
            return

        if self.download_in_progress:
            messagebox.showwarning("Download in Progress", "Please wait for current download to complete.")
            return

        # Get file info
        item = selected[0]
        filename = self.images_tree.item(item, 'values')[0]
        remote_path = self.images_tree.item(item, 'tags')[0]

        # Ask user where to save
        default_download_dir = Path.home() / "Downloads" / "air-side-files" / "images"
        default_download_dir.mkdir(parents=True, exist_ok=True)

        local_path = filedialog.asksaveasfilename(
            title="Save File As",
            initialdir=str(default_download_dir),
            initialfile=filename,
            defaultextension="",
            filetypes=[("All Files", "*.*")]
        )

        if not local_path:
            return  # User cancelled

        # Download in background thread
        self._download_image_file(remote_path, local_path, filename)

    def _download_image_file(self, remote_path: str, local_path: str, filename: str):
        """Download image file in background thread"""
        def download_thread():
            try:
                self.download_in_progress = True
                self._update_images_status(f"Downloading {filename}...")
                self.images_download_btn.config(state=tk.DISABLED)
                self.images_progress_var.set(0.0)

                # Download with progress callback
                def progress_callback(transferred, total):
                    if total > 0:
                        percent = (transferred / total) * 100.0
                        self.frame.after_idle(lambda: self.images_progress_var.set(percent))

                success = self.sftp_client.download_file(
                    remote_path,
                    local_path,
                    progress_callback=progress_callback
                )

                if success:
                    self._update_images_status(f"Downloaded {filename} successfully")
                    self.frame.after_idle(lambda: messagebox.showinfo(
                        "Download Complete",
                        f"File downloaded successfully:\n\n{local_path}"
                    ))
                    logger.info(f"Downloaded {filename} to {local_path}")
                else:
                    raise Exception("Download failed")

            except Exception as e:
                logger.error(f"Download failed: {e}")
                self.frame.after_idle(lambda: messagebox.showerror(
                    "Download Error",
                    f"Failed to download {filename}:\n\n{str(e)}"
                ))
                self._update_images_status(f"Download failed: {filename}")
            finally:
                self.download_in_progress = False
                if self.connected:
                    self.frame.after_idle(lambda: self.images_download_btn.config(state=tk.NORMAL))
                self.frame.after_idle(lambda: self.images_progress_var.set(0.0))

        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def _update_images_status(self, message: str):
        """Update status label for Images tab"""
        self.images_status_var.set(message)
        logger.debug(f"File Browser (Images) status: {message}")

    # ========== Docker Logs Tab Handlers ==========

    def _on_logs_connect_clicked(self):
        """Handle Connect button click for Docker Logs tab"""
        if self.connected:
            # Disconnect
            self.disconnect()
            self._update_logs_status("Disconnected")
            self.logs_connect_btn.config(text="🔌 Connect")
            self.logs_refresh_btn.config(state=tk.DISABLED)
            self.log_source_combo.config(state=tk.DISABLED)
            self.tail_count_combo.config(state=tk.DISABLED)
            self.logs_download_btn.config(state=tk.DISABLED)
            self.logs_popout_btn.config(state=tk.DISABLED)
            self._clear_logs_file_list()
        else:
            # Connect
            self._connect_to_air_side_logs()

    def _connect_to_air_side_logs(self):
        """Establish SSH/SFTP connection to Air-Side for Docker Logs tab"""
        try:
            self._update_logs_status("Connecting to Air-Side...")

            # Load configuration
            host = config.get('network', 'air_side_ip', '10.0.1.53')
            username = config.get('ssh', 'username', 'dpm')
            password = config.get('ssh', 'password', '2350')

            logger.info(f"Connecting to Air-Side (Docker Logs): {username}@{host}")

            # Create SSH client (also provides SFTP)
            self.ssh_client = SSHClient(
                host=host,
                username=username,
                password=password
            )

            # Connect
            if self.ssh_client.connect():
                self.connected = True
                self.logs_connect_btn.config(text="🔌 Disconnect")
                self.logs_refresh_btn.config(state=tk.NORMAL)
                self.log_source_combo.config(state="readonly")
                self.tail_count_combo.config(state="readonly")
                self.logs_download_btn.config(state=tk.NORMAL)
                self.logs_popout_btn.config(state=tk.NORMAL)

                self._update_logs_status(f"Connected to {host}")
                logger.info(f"SSH connection established to {host}")

                # Auto-refresh log list
                self._refresh_logs_file_list()
            else:
                raise Exception("Connection failed")

        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            messagebox.showerror(
                "Connection Error",
                f"Failed to connect to Air-Side:\n\n{str(e)}\n\nCheck network connection and credentials."
            )
            self._update_logs_status("Connection failed")
            self.connected = False

    def _on_logs_refresh_clicked(self):
        """Handle Refresh button click for Docker Logs tab"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to Air-Side first.")
            return

        self._refresh_logs_file_list()

    def _on_log_source_changed(self, event=None):
        """Handle log source selection change"""
        if not self.connected:
            return

        # Refresh log list for new source
        self._refresh_logs_file_list()

    def _refresh_logs_file_list(self):
        """Refresh logs file list based on selected source"""
        try:
            self._update_logs_status("Loading log list...")
            self.logs_refresh_btn.config(state=tk.DISABLED)

            # Clear current list
            self._clear_logs_file_list()

            # Get selected log source
            log_source = self.log_source_var.get()

            if log_source == "Host Logs":
                self._load_host_logs()
            elif log_source == "Container Logs":
                self._load_container_logs()
            elif log_source == "Docker Output":
                self._load_docker_output_entry()
            elif log_source == "System Logs":
                self._load_system_logs()

        except Exception as e:
            logger.error(f"Failed to list logs: {e}")
            messagebox.showerror(
                "List Error",
                f"Failed to list logs:\n\n{str(e)}"
            )
            self._update_logs_status("Failed to load logs")
        finally:
            if self.connected:
                self.logs_refresh_btn.config(state=tk.NORMAL)

    def _load_host_logs(self):
        """Load host-mounted logs (SOURCE 1: Direct SFTP)"""
        try:
            remote_dir = "/home/dpm/DPM-V2/sbc/logs"
            logger.info(f"Listing host logs from {remote_dir}")

            # List directory via SSH
            files = self.ssh_client.list_directory(remote_dir)

            # Filter for .log files
            log_files = [f for f in files if f.endswith('.log')]

            # Add to TreeView
            for filename in log_files:
                remote_path = f"{remote_dir}/{filename}"

                # Get file size via SSH
                exit_code, stdout, stderr = self.ssh_client.execute_command(
                    f"stat -c%s {remote_path}"
                )

                if exit_code == 0:
                    size_bytes = int(stdout.strip())
                    size_kb = size_bytes / 1024.0
                    size_str = f"{size_kb:.1f}"
                else:
                    size_str = "N/A"

                # Insert into TreeView (Host logs don't have Docker image)
                self.logs_tree.insert(
                    "",
                    tk.END,
                    values=(filename, size_str, "Host (SFTP)", "N/A"),
                    tags=(remote_path, "host")
                )

            count = len(log_files)
            self._update_logs_status(f"Found {count} host log file{'s' if count != 1 else ''}")
            logger.info(f"Loaded {count} host log files")

        except Exception as e:
            logger.error(f"Failed to load host logs: {e}")
            self._update_logs_status(f"Error loading host logs: {e}")

    def _load_system_logs(self):
        """Load system logs (SOURCE 4: Direct SFTP from /var/log/)"""
        try:
            remote_dir = "/var/log"
            logger.info(f"Listing system logs from {remote_dir}")

            # List directory via SSH
            files = self.ssh_client.list_directory(remote_dir)

            # Filter for system log files (syslog*, kern.log*, auth.log*, dmesg*)
            system_log_patterns = ['syslog', 'kern.log', 'auth.log', 'dmesg']
            log_files = [f for f in files if any(f.startswith(pattern) for pattern in system_log_patterns)]

            # Add to TreeView
            for filename in log_files:
                remote_path = f"{remote_dir}/{filename}"

                # Get file size via SSH
                exit_code, stdout, stderr = self.ssh_client.execute_command(
                    f"stat -c%s {remote_path}"
                )

                if exit_code == 0:
                    size_bytes = int(stdout.strip())
                    size_kb = size_bytes / 1024.0
                    size_str = f"{size_kb:.1f}"
                else:
                    size_str = "N/A"

                # Insert into TreeView (System logs don't have Docker image)
                self.logs_tree.insert(
                    "",
                    tk.END,
                    values=(filename, size_str, "System (SFTP)", "N/A"),
                    tags=(remote_path, "host")  # Use "host" tag for SFTP download
                )

            count = len(log_files)
            self._update_logs_status(f"Found {count} system log file{'s' if count != 1 else ''}")
            logger.info(f"Loaded {count} system log files")

        except Exception as e:
            logger.error(f"Failed to load system logs: {e}")
            self._update_logs_status(f"Error loading system logs: {e}")

    def _get_docker_image_id(self, container_name="payload-manager"):
        """Get Docker image ID for a container (shortened to 12 chars like docker ps)"""
        try:
            # Get full image ID from docker inspect
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"docker inspect {container_name} --format '{{{{.Image}}}}'"
            )

            if exit_code == 0 and stdout.strip():
                # Extract image ID (format: sha256:abcdef123456...)
                full_id = stdout.strip()

                # Remove 'sha256:' prefix if present
                if full_id.startswith('sha256:'):
                    full_id = full_id[7:]

                # Return first 12 characters (standard Docker short ID)
                return full_id[:12]
            else:
                return "N/A"

        except Exception as e:
            logger.warning(f"Failed to get Docker image ID: {e}")
            return "N/A"

    def _load_container_logs(self):
        """Load container-internal structured logs (SOURCE 2: Docker cp)"""
        try:
            # Check if docker container is running
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                "docker ps --filter name=payload-manager --format '{{.Names}}'"
            )

            if exit_code != 0 or "payload-manager" not in stdout:
                raise Exception("Docker container 'payload-manager' is not running")

            # Get Docker image ID
            image_id = self._get_docker_image_id("payload-manager")

            # List files in container's /var/log/dpm/ directory
            container_log_dir = "/var/log/dpm"
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"docker exec payload-manager ls -la {container_log_dir}"
            )

            if exit_code != 0:
                raise Exception(f"Failed to list container logs: {stderr}")

            # Parse output
            lines = stdout.strip().split('\n')[1:]  # Skip 'total' line

            for line in lines:
                parts = line.split()
                if len(parts) >= 9:
                    # Extract filename (last part)
                    filename = parts[-1]

                    # Skip . and ..
                    if filename in ['.', '..']:
                        continue

                    # Filter for .jsonl files
                    if filename.endswith('.jsonl'):
                        # Extract size (5th column in ls -la)
                        size_bytes = int(parts[4])
                        size_kb = size_bytes / 1024.0
                        size_str = f"{size_kb:.1f}"

                        # Store container path in tags
                        container_path = f"{container_log_dir}/{filename}"

                        # Insert into TreeView with Image ID
                        self.logs_tree.insert(
                            "",
                            tk.END,
                            values=(filename, size_str, "Container (docker cp)", image_id),
                            tags=(container_path, "container")
                        )

            count = len(self.logs_tree.get_children())
            self._update_logs_status(f"Found {count} container log file{'s' if count != 1 else ''}")
            logger.info(f"Loaded {count} container log files")

        except Exception as e:
            logger.error(f"Failed to load container logs: {e}")
            self._update_logs_status(f"Error: {e}")
            messagebox.showerror(
                "Container Logs Error",
                f"Failed to load container logs:\n\n{str(e)}\n\nEnsure Docker container is running."
            )

    def _load_docker_output_entry(self):
        """Load Docker Output entry (SOURCE 3: Docker logs streaming)"""
        try:
            # Check if docker container is running
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                "docker ps --filter name=payload-manager --format '{{.Names}}'"
            )

            if exit_code != 0 or "payload-manager" not in stdout:
                raise Exception("Docker container 'payload-manager' is not running")

            # Get Docker image ID
            image_id = self._get_docker_image_id("payload-manager")

            # Get tail count
            tail_str = self.tail_count_var.get()

            # Add single entry for Docker Output
            display_name = f"docker logs payload-manager (tail={tail_str})"

            self.logs_tree.insert(
                "",
                tk.END,
                values=(display_name, "Stream", "Docker Output", image_id),
                tags=("docker_logs", "docker_output")
            )

            self._update_logs_status("Docker logs ready to download")
            logger.info("Docker Output source ready")

        except Exception as e:
            logger.error(f"Failed to prepare Docker Output: {e}")
            self._update_logs_status(f"Error: {e}")
            messagebox.showerror(
                "Docker Logs Error",
                f"Failed to prepare Docker logs:\n\n{str(e)}\n\nEnsure Docker container is running."
            )

    def _clear_logs_file_list(self):
        """Clear logs TreeView"""
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

    def _sort_logs_by_column(self, column: str):
        """Sort Logs TreeView by column"""
        # Get all items
        items = [(self.logs_tree.set(item, column), item) for item in self.logs_tree.get_children('')]

        # Sort items
        if column == "size":
            # Sort numerically for size
            def get_size(val):
                try:
                    if val == "Stream" or val == "N/A":
                        return 0
                    return float(val)
                except:
                    return 0
            items.sort(key=lambda x: get_size(x[0]), reverse=True)
        else:
            # Sort alphabetically
            items.sort(reverse=False)

        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.logs_tree.move(item, '', index)

    def _on_logs_download_clicked(self):
        """Handle Download button click for Docker Logs tab"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to Air-Side first.")
            return

        # Get selected item
        selected = self.logs_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a log to download.")
            return

        if self.download_in_progress:
            messagebox.showwarning("Download in Progress", "Please wait for current download to complete.")
            return

        # Get log info
        item = selected[0]
        tags = self.logs_tree.item(item, 'tags')

        if len(tags) < 2:
            messagebox.showerror("Error", "Invalid log entry selected.")
            return

        log_path = tags[0]
        log_type = tags[1]

        # Get filename for saving
        filename = self.logs_tree.item(item, 'values')[0]

        # Ask user where to save
        default_download_dir = Path.home() / "Downloads" / "air-side-files" / "logs"
        default_download_dir.mkdir(parents=True, exist_ok=True)

        # Suggest filename based on log type
        if log_type == "docker_output":
            default_filename = f"docker-logs-{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        else:
            default_filename = filename

        local_path = filedialog.asksaveasfilename(
            title="Save Log File As",
            initialdir=str(default_download_dir),
            initialfile=default_filename,
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("JSON Lines", "*.jsonl"), ("All Files", "*.*")]
        )

        if not local_path:
            return  # User cancelled

        # Download based on log type
        if log_type == "host":
            self._download_host_log(log_path, local_path, filename)
        elif log_type == "container":
            self._download_container_log(log_path, local_path, filename)
        elif log_type == "docker_output":
            self._download_docker_output(local_path, filename)
        else:
            messagebox.showerror("Error", f"Unknown log type: {log_type}")

    def _download_host_log(self, remote_path: str, local_path: str, filename: str):
        """Download host log via SFTP (SOURCE 1)"""
        def download_thread():
            try:
                self.download_in_progress = True
                self._update_logs_status(f"Downloading {filename} via SFTP...")
                self.logs_download_btn.config(state=tk.DISABLED)
                self.logs_progress_var.set(0.0)

                # Download with progress callback
                def progress_callback(transferred, total):
                    if total > 0:
                        percent = (transferred / total) * 100.0
                        self.frame.after_idle(lambda: self.logs_progress_var.set(percent))

                success = self.ssh_client.download_file(
                    remote_path,
                    local_path,
                    progress_callback=progress_callback
                )

                if success:
                    self._update_logs_status(f"Downloaded {filename} successfully")
                    self.frame.after_idle(lambda: messagebox.showinfo(
                        "Download Complete",
                        f"Log downloaded successfully:\n\n{local_path}"
                    ))
                    logger.info(f"Downloaded host log {filename} to {local_path}")
                else:
                    raise Exception("SFTP download failed")

            except Exception as e:
                logger.error(f"Host log download failed: {e}")
                self.frame.after_idle(lambda: messagebox.showerror(
                    "Download Error",
                    f"Failed to download {filename}:\n\n{str(e)}"
                ))
                self._update_logs_status(f"Download failed: {filename}")
            finally:
                self.download_in_progress = False
                if self.connected:
                    self.frame.after_idle(lambda: self.logs_download_btn.config(state=tk.NORMAL))
                self.frame.after_idle(lambda: self.logs_progress_var.set(0.0))

        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def _download_container_log(self, container_path: str, local_path: str, filename: str):
        """Download container log via docker cp + SFTP (SOURCE 2)"""
        def download_thread():
            try:
                self.download_in_progress = True
                self._update_logs_status(f"Downloading {filename} from container...")
                self.logs_download_btn.config(state=tk.DISABLED)
                self.logs_progress_var.set(0.0)

                # Step 1: Docker cp to /tmp
                tmp_path = f"/tmp/{filename}"
                docker_cp_cmd = f"docker cp payload-manager:{container_path} {tmp_path}"

                logger.info(f"Running docker cp: {docker_cp_cmd}")
                self.frame.after_idle(lambda: self.logs_progress_var.set(30.0))

                exit_code, stdout, stderr = self.ssh_client.execute_command(docker_cp_cmd)

                if exit_code != 0:
                    raise Exception(f"Docker cp failed: {stderr}")

                # Step 2: Download from /tmp via SFTP
                logger.info(f"Downloading from {tmp_path} to {local_path}")
                self.frame.after_idle(lambda: self.logs_progress_var.set(50.0))

                def progress_callback(transferred, total):
                    if total > 0:
                        # Progress from 50% to 90%
                        percent = 50.0 + ((transferred / total) * 40.0)
                        self.frame.after_idle(lambda: self.logs_progress_var.set(percent))

                success = self.ssh_client.download_file(
                    tmp_path,
                    local_path,
                    progress_callback=progress_callback
                )

                if not success:
                    raise Exception("SFTP download from /tmp failed")

                # Step 3: Cleanup /tmp file
                logger.info(f"Cleaning up {tmp_path}")
                self.frame.after_idle(lambda: self.logs_progress_var.set(95.0))

                cleanup_cmd = f"rm {tmp_path}"
                self.ssh_client.execute_command(cleanup_cmd)

                # Done
                self.frame.after_idle(lambda: self.logs_progress_var.set(100.0))
                self._update_logs_status(f"Downloaded {filename} successfully")
                self.frame.after_idle(lambda: messagebox.showinfo(
                    "Download Complete",
                    f"Container log downloaded successfully:\n\n{local_path}"
                ))
                logger.info(f"Downloaded container log {filename} to {local_path}")

            except Exception as e:
                logger.error(f"Container log download failed: {e}")
                self.frame.after_idle(lambda: messagebox.showerror(
                    "Download Error",
                    f"Failed to download {filename}:\n\n{str(e)}"
                ))
                self._update_logs_status(f"Download failed: {filename}")
            finally:
                self.download_in_progress = False
                if self.connected:
                    self.frame.after_idle(lambda: self.logs_download_btn.config(state=tk.NORMAL))
                self.frame.after_idle(lambda: self.logs_progress_var.set(0.0))

        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def _download_docker_output(self, local_path: str, display_name: str):
        """Download Docker logs output via SSH streaming (SOURCE 3)"""
        def download_thread():
            try:
                self.download_in_progress = True
                self._update_logs_status("Downloading Docker logs output...")
                self.logs_download_btn.config(state=tk.DISABLED)
                self.logs_progress_var.set(0.0)

                # Get tail count
                tail_str = self.tail_count_var.get()
                tail_count = None if tail_str == "All" else int(tail_str)

                # Execute docker logs command
                logger.info(f"Getting Docker logs (tail={tail_count})")
                self.frame.after_idle(lambda: self.logs_progress_var.set(30.0))

                exit_code, stdout, stderr = self.ssh_client.get_docker_logs(
                    container="payload-manager",
                    tail=tail_count
                )

                if exit_code != 0:
                    raise Exception(f"Docker logs failed: {stderr}")

                # Save to local file
                logger.info(f"Saving Docker logs to {local_path}")
                self.frame.after_idle(lambda: self.logs_progress_var.set(70.0))

                with open(local_path, 'w', encoding='utf-8') as f:
                    # Write stdout (docker logs output)
                    f.write(stdout)
                    # Also include stderr if present
                    if stderr:
                        f.write("\n\n=== STDERR ===\n\n")
                        f.write(stderr)

                # Done
                self.frame.after_idle(lambda: self.logs_progress_var.set(100.0))
                self._update_logs_status("Downloaded Docker logs successfully")
                self.frame.after_idle(lambda: messagebox.showinfo(
                    "Download Complete",
                    f"Docker logs saved successfully:\n\n{local_path}\n\nLines: {tail_count or 'All'}"
                ))
                logger.info(f"Downloaded Docker logs to {local_path}")

            except Exception as e:
                logger.error(f"Docker logs download failed: {e}")
                self.frame.after_idle(lambda: messagebox.showerror(
                    "Download Error",
                    f"Failed to download Docker logs:\n\n{str(e)}"
                ))
                self._update_logs_status("Download failed")
            finally:
                self.download_in_progress = False
                if self.connected:
                    self.frame.after_idle(lambda: self.logs_download_btn.config(state=tk.NORMAL))
                self.frame.after_idle(lambda: self.logs_progress_var.set(0.0))

        # Start download thread
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()

    def _update_logs_status(self, message: str):
        """Update status label for Docker Logs tab"""
        self.logs_status_var.set(message)
        logger.debug(f"File Browser (Docker Logs) status: {message}")

    # ========== Common Methods ==========

    def disconnect(self):
        """Close SFTP and SSH connections"""
        try:
            if self.sftp_client:
                self.sftp_client.disconnect()
                logger.info("SFTP connection closed")
                self.sftp_client = None

            if self.ssh_client:
                self.ssh_client.disconnect()
                logger.info("SSH connection closed")
                self.ssh_client = None

            self.connected = False

        except Exception as e:
            logger.error(f"Error disconnecting: {e}")

    def _pop_out_docker_logs(self):
        """Pop out Docker log viewer into a separate window"""
        # Check if a file is selected
        selection = self.logs_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a log file first")
            return

        # If window already exists, bring it to front
        if self.popup_window and self.popup_window.winfo_exists():
            self.popup_window.lift()
            self.popup_window.focus_force()
            logger.debug("Pop-out window brought to front")
            return

        # Get selected log info
        item = self.logs_tree.item(selection[0])
        values = item['values']
        tags = item['tags']

        log_name = values[0]
        log_source = values[2]

        # Create new popup window
        self.popup_window = tk.Toplevel(self.frame)
        self.popup_window.title(f"DPM SystemTools - Docker Log Viewer: {log_name}")
        self.popup_window.geometry("1200x800")

        # Create main frame
        main_frame = ttk.Frame(self.popup_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(main_frame,
                               text=f"📋 Docker Log: {log_name}",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))

        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="Source:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text=log_source, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)

        if len(values) > 1:
            ttk.Label(info_frame, text="Size:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
            ttk.Label(info_frame, text=f"{values[1]} KB", font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        if len(values) > 3 and values[3] != "N/A":
            ttk.Separator(info_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=15, fill=tk.Y)
            ttk.Label(info_frame, text="Image ID:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
            ttk.Label(info_frame, text=values[3], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        # Status label
        popup_status_var = tk.StringVar(value="Loading...")
        popup_status_label = ttk.Label(info_frame,
                                       textvariable=popup_status_var,
                                       font=('Arial', 9),
                                       foreground="blue")
        popup_status_label.pack(side=tk.RIGHT, padx=5)

        # Log display area (scrolled text)
        import tkinter.scrolledtext as scrolledtext
        self.popup_text = scrolledtext.ScrolledText(main_frame,
                                                    font=('Courier New', 9),
                                                    wrap=tk.NONE,
                                                    state='normal',
                                                    bg='#FFFFFF',
                                                    fg='#000000')
        self.popup_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure color tags for different log levels
        self.popup_text.tag_config("error", foreground="#FF0000", font=('Courier New', 9, 'bold'))
        self.popup_text.tag_config("warning", foreground="#FF8C00", font=('Courier New', 9))
        self.popup_text.tag_config("info", foreground="#0000FF")
        self.popup_text.tag_config("debug", foreground="#808080")
        self.popup_text.tag_config("air", foreground="#00008B", font=('Courier New', 9, 'bold'))
        self.popup_text.tag_config("ground", foreground="#006400", font=('Courier New', 9, 'bold'))

        # Bottom button bar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="🔄 Refresh",
                  command=lambda: self._refresh_popup(popup_status_var, tags)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="📋 Copy All",
                  command=lambda: self._copy_popup_content()).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="💾 Save to File",
                  command=lambda: self._save_popup_to_file()).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="❌ Close",
                  command=self.popup_window.destroy).pack(side=tk.RIGHT, padx=5)

        # Load log content
        self._load_popup_content(popup_status_var, tags, log_source)

        logger.info(f"Pop-out log window created for: {log_name}")

    def _load_popup_content(self, status_var, tags, log_source):
        """Load log content into popup window"""
        try:
            status_var.set("Loading log content...")
            self.popup_text.delete(1.0, tk.END)

            # Determine source type from tags
            if "container" in tags:
                # Container logs - download via docker cp
                self._load_popup_container_log(status_var, tags[0])
            elif "docker_output" in tags:
                # Docker output - stream logs
                self._load_popup_docker_output(status_var)
            elif "host" in tags:
                # Host or System logs - download via SFTP
                self._load_popup_sftp_log(status_var, tags[0])
            else:
                status_var.set("Unknown log source")
                self.popup_text.insert(1.0, "Error: Unknown log source type")

        except Exception as e:
            logger.error(f"Failed to load popup content: {e}")
            status_var.set(f"Error: {e}")
            self.popup_text.insert(1.0, f"Error loading log:\n{e}")

    def _load_popup_container_log(self, status_var, container_path):
        """Load container log via docker cp"""
        try:
            import tempfile
            import os

            status_var.set("Copying log from container...")

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
            temp_path = temp_file.name
            temp_file.close()

            # Docker cp to host
            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"docker cp payload-manager:{container_path} /tmp/docker_log_temp.jsonl"
            )

            if exit_code != 0:
                raise Exception(f"docker cp failed: {stderr}")

            # Download via SFTP
            status_var.set("Downloading log file...")
            if self.ssh_client.download_file("/tmp/docker_log_temp.jsonl", temp_path):
                # Read and display
                with open(temp_path, 'r') as f:
                    content = f.read()

                self.popup_text.insert(1.0, content)
                self._apply_log_highlighting()

                line_count = content.count('\n')
                status_var.set(f"Loaded {line_count} lines")

                # Cleanup
                os.unlink(temp_path)
                self.ssh_client.execute_command("rm /tmp/docker_log_temp.jsonl")
            else:
                raise Exception("Failed to download log file")

        except Exception as e:
            logger.error(f"Failed to load container log: {e}")
            status_var.set(f"Error: {e}")
            self.popup_text.insert(1.0, f"Error loading container log:\n{e}")

    def _load_popup_docker_output(self, status_var):
        """Load docker logs output"""
        try:
            tail_str = self.tail_count_var.get()
            tail_arg = "" if tail_str == "All" else f"--tail {tail_str}"

            status_var.set(f"Streaming docker logs (tail={tail_str})...")

            exit_code, stdout, stderr = self.ssh_client.execute_command(
                f"docker logs {tail_arg} payload-manager 2>&1"
            )

            if exit_code == 0:
                self.popup_text.insert(1.0, stdout)
                self._apply_log_highlighting()

                line_count = stdout.count('\n')
                status_var.set(f"Loaded {line_count} lines")
            else:
                raise Exception(f"docker logs failed: {stderr}")

        except Exception as e:
            logger.error(f"Failed to load docker output: {e}")
            status_var.set(f"Error: {e}")
            self.popup_text.insert(1.0, f"Error loading docker logs:\n{e}")

    def _load_popup_sftp_log(self, status_var, remote_path):
        """Load log via SFTP"""
        try:
            import tempfile
            import os

            status_var.set("Downloading log file...")

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log')
            temp_path = temp_file.name
            temp_file.close()

            # Download via SFTP
            if self.ssh_client.download_file(remote_path, temp_path):
                # Read and display
                with open(temp_path, 'r') as f:
                    content = f.read()

                self.popup_text.insert(1.0, content)
                self._apply_log_highlighting()

                line_count = content.count('\n')
                status_var.set(f"Loaded {line_count} lines")

                # Cleanup
                os.unlink(temp_path)
            else:
                raise Exception("Failed to download log file")

        except Exception as e:
            logger.error(f"Failed to load SFTP log: {e}")
            status_var.set(f"Error: {e}")
            self.popup_text.insert(1.0, f"Error loading log:\n{e}")

    def _apply_log_highlighting(self):
        """Apply syntax highlighting to log text in popup"""
        content = self.popup_text.get(1.0, tk.END)
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Error highlighting
            if 'error' in line_lower or 'exception' in line_lower or 'failed' in line_lower:
                self.popup_text.tag_add("error", f"{i}.0", f"{i}.end")
            # Warning highlighting
            elif 'warning' in line_lower or 'warn' in line_lower:
                self.popup_text.tag_add("warning", f"{i}.0", f"{i}.end")
            # Debug highlighting
            elif 'debug' in line_lower:
                self.popup_text.tag_add("debug", f"{i}.0", f"{i}.end")
            # Info highlighting
            elif 'info' in line_lower:
                self.popup_text.tag_add("info", f"{i}.0", f"{i}.end")

            # Domain highlighting
            if '"domain":"AIR"' in line or '"domain": "AIR"' in line:
                self.popup_text.tag_add("air", f"{i}.0", f"{i}.end")
            elif '"domain":"GROUND"' in line or '"domain": "GROUND"' in line:
                self.popup_text.tag_add("ground", f"{i}.0", f"{i}.end")

    def _refresh_popup(self, status_var, tags):
        """Refresh popup window content"""
        selection = self.logs_tree.selection()
        if not selection:
            return

        item = self.logs_tree.item(selection[0])
        log_source = item['values'][2]

        self._load_popup_content(status_var, tags, log_source)
        logger.debug("Pop-out window refreshed")

    def _copy_popup_content(self):
        """Copy all popup content to clipboard"""
        try:
            content = self.popup_text.get(1.0, tk.END)
            self.popup_window.clipboard_clear()
            self.popup_window.clipboard_append(content)
            logger.info("Popup content copied to clipboard")
            messagebox.showinfo("Copied", "Log content copied to clipboard")
        except Exception as e:
            logger.error(f"Error copying popup content: {e}")
            messagebox.showerror("Error", f"Failed to copy:\n{e}")

    def _save_popup_to_file(self):
        """Save popup content to a file"""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                parent=self.popup_window,
                title="Save Log File",
                defaultextension=".log",
                filetypes=[
                    ("Log files", "*.log"),
                    ("JSON Lines", "*.jsonl"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )

            if filename:
                content = self.popup_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)

                logger.info(f"Popup content saved to: {filename}")
                messagebox.showinfo("Saved", f"Log saved to:\n{filename}")

        except Exception as e:
            logger.error(f"Error saving popup content: {e}")
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def cleanup(self):
        """Cleanup resources (called on window close)"""
        logger.info("Cleaning up File Browser tab")
        self.disconnect()
