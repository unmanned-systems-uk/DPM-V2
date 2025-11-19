"""
DPM DevTools - Main Entry Point
Cross-platform diagnostic and testing tool for DPM Payload Manager

Usage:
    python main.py [--mode development|deployment] [--ui gui|cli|auto]

Version: 2.0.0 - DevTools Edition
Date: November 2025
"""

import sys
import subprocess
from pathlib import Path

# Add SystemTools to path
sys.path.insert(0, str(Path(__file__).parent))


# Auto-install missing dependencies
def check_and_install_dependencies():
    """Check for required dependencies and auto-install if missing"""
    required_packages = {
        'paramiko': 'paramiko>=3.4.0',
        'matplotlib': 'matplotlib>=3.8.0',
        'rich': 'rich>=13.7.0'
    }

    missing_packages = []

    # Check each required package
    for package_name, pip_spec in required_packages.items():
        try:
            __import__(package_name)
        except ImportError:
            missing_packages.append((package_name, pip_spec))

    # Check tkinter (special case - can't be pip installed)
    try:
        import tkinter
    except ImportError:
        print("\n" + "="*60)
        print("⚠️  WARNING: tkinter not found (required for GUI)")
        print("="*60)
        print("\ntkinter cannot be installed via pip.")
        print("Please install it using your system package manager:\n")
        if sys.platform.startswith('linux'):
            print("  Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  CentOS/RHEL:   sudo yum install python3-tkinter")
        elif sys.platform == 'darwin':
            print("  macOS:         brew install python-tk")
        elif sys.platform == 'win32':
            print("  Windows:       Reinstall Python and check 'tcl/tk and IDLE'")
        print("\n" + "="*60 + "\n")

        response = input("Continue without GUI support? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    # Auto-install missing pip packages
    if missing_packages:
        print("\n" + "="*60)
        print("📦 Auto-Installing Missing Dependencies")
        print("="*60)
        print("\nThe following packages are required but not installed:")
        for pkg_name, _ in missing_packages:
            print(f"  - {pkg_name}")
        print()

        # Ask for confirmation
        response = input("Auto-install now? (y/n): ")
        if response.lower() != 'y':
            print("\nℹ️  You can manually install dependencies by running:")
            print("   Linux/macOS: ./install_dependencies.sh")
            print("   Windows:     install_dependencies.bat")
            print("   Or: pip install -r requirements.txt\n")
            sys.exit(1)

        print("\nInstalling packages...\n")

        # Upgrade pip first
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass  # Ignore pip upgrade errors

        # Install each missing package
        success = True
        for pkg_name, pip_spec in missing_packages:
            try:
                print(f"  Installing {pkg_name}...", end=' ', flush=True)
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_spec],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅")
            except subprocess.CalledProcessError:
                print("❌")
                success = False

        if not success:
            print("\n❌ Some packages failed to install.")
            print("Try running manually: pip install -r requirements.txt\n")
            sys.exit(1)

        print("\n✅ All dependencies installed successfully!\n")
        print("="*60 + "\n")


# Check dependencies before importing any third-party modules
check_and_install_dependencies()

# Import DevTools configuration first
from devtools_config import devtools_config, parse_args

from utils.protocol_logger import logger
from utils.config import config
from utils.protocol_loader import protocol
from version import get_version_string, get_build_info_string

# Network components
from network.tcp_client import TCPClient
from network.ssh_client import SSHClient
from network.adb_client import ADBClient
from network.udp_listener import StatusListener, HeartbeatListener
from network.heartbeat import HeartbeatSender

# GUI components
from gui.main_window import MainWindow
from gui.tab_config import ConfigTab
from gui.tab_connection import ConnectionTab
from gui.tab_protocol import ProtocolInspectorTab
from gui.tab_command import CommandSenderTab
from gui.tab_camera import CameraDashboardTab
from gui.tab_system import SystemMonitorTab
from gui.tab_logs import LogInspectorTab
from gui.tab_activity import ActivityLogTab
from gui.tab_remote_control import RemoteControlTab
from gui.tab_h16_diagnostics import H16DiagnosticsTab
from gui.tab_github_integration import GitHubIntegrationTab
from gui.tab_git_helper import GitHelperTab


class DiagnosticApp:
    """Main application class that manages all components"""

    def __init__(self):
        self.window = None
        self.tcp_client = None
        self.ssh_client = None
        self.adb_client = None
        self.status_listener = None
        self.heartbeat_listener = None
        self.heartbeat_sender = None
        self._cleanup_done = False

        # Tabs
        self.config_tab = None
        self.connection_tab = None
        self.protocol_tab = None
        self.command_tab = None
        self.camera_tab = None
        self.system_tab = None
        self.log_tab = None
        self.activity_tab = None
        self.remote_control_tab = None
        self.h16_diagnostics_tab = None
        self.github_tab = None

    def initialize(self):
        """Initialize all components"""
        logger.info("SYSTEM", "=" * 60)
        logger.info("SYSTEM", f"DPM Diagnostic Tool {get_version_string()} Starting...")
        logger.info("SYSTEM", f"Build: {get_build_info_string()}")
        logger.info("SYSTEM", "=" * 60)

        # Load protocol definitions
        logger.info("CONFIG", "Loading protocol definitions...")
        if protocol.load():
            logger.info("CONFIG", f"  - Loaded {len(protocol.get_all_commands())} commands")
            logger.info("CONFIG", f"  - Loaded {len(protocol.get_all_properties())} properties")
        else:
            logger.warning("CONFIG", "  - Failed to load some protocol definitions")

        # Load configuration
        logger.info("CONFIG", "Loading configuration...")
        config.load()
        air_side_ip = config.get('network', 'air_side_ip')
        tcp_port = config.get('network', 'tcp_port')
        status_port = config.get('network', 'udp_status_port', 5001)
        heartbeat_port = config.get('network', 'udp_heartbeat_port', 5002)

        logger.info("CONFIG", f"  - Air-Side IP: {air_side_ip}")
        logger.info("CONFIG", f"  - TCP Port: {tcp_port}")
        logger.info("CONFIG", f"  - UDP Status Port: {status_port}")
        logger.info("CONFIG", f"  - UDP Heartbeat Port: {heartbeat_port}")

        # Create network components
        logger.info("NETWORK", "Creating network components...")
        self._create_network_components(air_side_ip, tcp_port, status_port, heartbeat_port)

        # Create main window with cleanup callback
        logger.info("SYSTEM", "Creating main window...")
        self.window = MainWindow(cleanup_callback=self.cleanup)

        # Create tabs
        logger.info("SYSTEM", "Creating tabs...")
        self._create_tabs()

        # Wire everything together
        logger.info("SYSTEM", "Wiring components...")
        self._wire_components()

        # Update status bar
        self.window.update_status_bar(False, f"Air-Side: {air_side_ip}:{tcp_port}")

        logger.info("SYSTEM", "=" * 60)
        logger.info("SYSTEM", "Application ready!")
        logger.info("SYSTEM", "=" * 60)

    def _create_network_components(self, air_side_ip, tcp_port, status_port, heartbeat_port):
        """Create network components"""
        # TCP Client
        self.tcp_client = TCPClient(air_side_ip, tcp_port)

        # SSH Client
        ssh_username = config.get("ssh", "username", "dpm")
        ssh_password = config.get("ssh", "password", "2350")
        ssh_port = config.get("ssh", "port", 22)
        self.ssh_client = SSHClient(air_side_ip, ssh_username, ssh_password, ssh_port)

        # ADB Client
        self.adb_client = ADBClient()

        # UDP Listeners
        self.status_listener = StatusListener(status_port)
        self.heartbeat_listener = HeartbeatListener(heartbeat_port)

        # Heartbeat Sender
        self.heartbeat_sender = HeartbeatSender(air_side_ip, heartbeat_port)

    def _create_tabs(self):
        """Create all GUI tabs"""
        # Connection Monitor tab (Phase 1)
        self.connection_tab = ConnectionTab(self.window.notebook)

        # Configuration tab (Phase 1)
        self.config_tab = ConfigTab(self.window.notebook)

        # Protocol Inspector tab (Phase 2)
        self.protocol_tab = ProtocolInspectorTab(self.window.notebook)

        # Command Sender tab (Phase 2)
        self.command_tab = CommandSenderTab(self.window.notebook)

        # Camera Dashboard tab (Phase 2)
        self.camera_tab = CameraDashboardTab(self.window.notebook)

        # System Monitor tab (Phase 2)
        self.system_tab = SystemMonitorTab(self.window.notebook)

        # Log Inspector tab (Phase 2)
        self.log_tab = LogInspectorTab(self.window.notebook)

        # Remote Control tab (Phase 2) - shares SSH client with Log Inspector
        self.remote_control_tab = RemoteControlTab(self.window.notebook, self.log_tab)

        # Activity Log tab (Phase 2)
        self.activity_tab = ActivityLogTab(self.window.notebook)

        # H16 ADB Diagnostics tab (Phase 3)
        self.h16_diagnostics_tab = H16DiagnosticsTab(self.window.notebook)

        # GitHub Integration tab (Phase 3)
        self.github_tab = GitHubIntegrationTab(self.window.notebook)

        # Git Helper tab - simplified git operations
        self.git_helper_tab = GitHelperTab(self.window.notebook)

        # Add tabs to window (in display order)
        tabs = {
            "Connection Monitor": self.connection_tab,
            "Protocol Inspector": self.protocol_tab,
            "Command Sender": self.command_tab,
            "Camera Dashboard": self.camera_tab,
            "System Monitor": self.system_tab,
            "Log Inspector": self.log_tab,
            "Remote Control": self.remote_control_tab,
            "H16 ADB Diagnostics": self.h16_diagnostics_tab,
            "GitHub Integration": self.github_tab,
            "Git Helper": self.git_helper_tab,
            "Activity Log": self.activity_tab,
            "Configuration": self.config_tab,
        }

        self.window.set_tabs(tabs)

    def _wire_components(self):
        """Wire all components together with callbacks"""
        # Give connection tab references to all network clients
        # This sets up the connection tab's callbacks
        self.connection_tab.set_tcp_client(self.tcp_client)
        self.connection_tab.set_ssh_client(self.ssh_client)
        self.connection_tab.set_adb_client(self.adb_client)

        # Save the connection tab's callbacks so we can chain them
        connection_tab_on_connected = self.tcp_client.on_connected
        connection_tab_on_disconnected = self.tcp_client.on_disconnected
        connection_tab_on_message = self.tcp_client.on_message_received

        # Give command sender tab reference to TCP client
        self.command_tab.set_tcp_client(self.tcp_client)

        # Give camera dashboard tab reference to TCP client (Issue #55)
        self.camera_tab.set_tcp_client(self.tcp_client)

        # Save the command tab's callback so we can chain it
        command_tab_on_message = self.tcp_client.on_message_received

        # Wire Remote Control tab with Log Inspector for SSH status updates
        self.log_tab.remote_control_tab = self.remote_control_tab

        # Wire TCP client callbacks (chaining with connection tab callbacks)
        def on_tcp_message(message):
            """Handle TCP message received"""
            # Call connection tab's callback first
            if connection_tab_on_message:
                connection_tab_on_message(message)

            # Call command tab's callback (this shows responses)
            if command_tab_on_message:
                try:
                    command_tab_on_message(message)
                except Exception as e:
                    logger.error("SYSTEM", f"Error in command tab callback: {e}")

            # Call camera tab's response handler (Issue #55 - show responses in debug panel)
            try:
                self.camera_tab.handle_response(message)
            except Exception as e:
                logger.error("SYSTEM", f"Error in camera tab response handler: {e}")

            # Add to protocol inspector
            self.protocol_tab.add_message(message, "received")

            # Log to activity log
            msg_type = message.get("message_type", "unknown")
            self.activity_tab.log_event(self.activity_tab.CATEGORY_TCP,
                                       f"Received {msg_type} message")

        def on_tcp_connected():
            """Handle TCP connected"""
            # Call connection tab's callback first
            if connection_tab_on_connected:
                connection_tab_on_connected()

            logger.info("NETWORK", "TCP connected - starting UDP listeners and heartbeat sender")

            air_side_ip = config.get('network', 'air_side_ip')
            tcp_port = config.get('network', 'tcp_port')

            # Log to activity log
            self.activity_tab.log_event(self.activity_tab.CATEGORY_TCP,
                                       f"Connected to {air_side_ip}:{tcp_port}")

            # Start UDP listeners
            self.status_listener.start()
            self.heartbeat_listener.start()
            self.activity_tab.log_event(self.activity_tab.CATEGORY_UDP,
                                       "Started UDP listeners (status & heartbeat)")

            # Start heartbeat sender
            self.heartbeat_sender.start()
            self.activity_tab.log_event(self.activity_tab.CATEGORY_INFO,
                                       "Started heartbeat sender")

            # Update status bar
            self.window.update_status_bar(True, f"Connected: {air_side_ip}:{tcp_port}")

        def on_tcp_disconnected():
            """Handle TCP disconnected"""
            # Call connection tab's callback first
            if connection_tab_on_disconnected:
                connection_tab_on_disconnected()

            logger.info("NETWORK", "TCP disconnected - stopping UDP listeners and heartbeat sender")

            air_side_ip = config.get('network', 'air_side_ip')
            tcp_port = config.get('network', 'tcp_port')

            # Log to activity log
            self.activity_tab.log_event(self.activity_tab.CATEGORY_TCP,
                                       f"Disconnected from {air_side_ip}:{tcp_port}")

            # Stop UDP listeners
            if self.status_listener:
                self.status_listener.stop()
            if self.heartbeat_listener:
                self.heartbeat_listener.stop()
            self.activity_tab.log_event(self.activity_tab.CATEGORY_UDP,
                                       "Stopped UDP listeners")

            # Stop heartbeat sender
            if self.heartbeat_sender:
                self.heartbeat_sender.stop()

            # Update status bar
            self.window.update_status_bar(False, f"Disconnected: {air_side_ip}:{tcp_port}")

        # Set TCP callbacks (now chained)
        self.tcp_client.on_message_received = on_tcp_message
        self.tcp_client.on_connected = on_tcp_connected
        self.tcp_client.on_disconnected = on_tcp_disconnected

        # Wire UDP Status listener callback
        def on_status_message(message):
            """Handle UDP status broadcast - called from background thread"""
            # Schedule GUI updates on main thread using after_idle()
            self.window.root.after_idle(lambda: self.protocol_tab.add_message(message, "received"))
            self.window.root.after_idle(lambda: self.camera_tab.update_camera_status(message))
            self.window.root.after_idle(lambda: self.system_tab.update_system_status(message))

            # Log UDP status to activity log
            self.window.root.after_idle(lambda: self.activity_tab.log_event(
                self.activity_tab.CATEGORY_UDP, "Received status broadcast"))

            # Update connection tab with camera properties if present
            payload = message.get("payload", {})
            if "camera" in payload and isinstance(payload["camera"], dict):
                camera_props = payload["camera"]
                if camera_props:  # If camera data is not empty
                    self.window.root.after_idle(lambda props=camera_props:
                        self.connection_tab.on_camera_properties_received(props))

            # Update log inspector camera comparison tab
            # Extract camera status from payload
            camera_data = None
            if "payload" in message and "camera" in message["payload"]:
                camera_data = message["payload"]["camera"]
            elif "camera" in message:
                camera_data = message["camera"]

            if camera_data:
                camera_connected = camera_data.get("connected", False)
                logger.debug("NETWORK", f"Camera status from UDP: {camera_connected}")

                # Log camera status changes to activity log
                status_str = "connected" if camera_connected else "disconnected"
                self.window.root.after_idle(lambda s=status_str: self.activity_tab.log_event(
                    self.activity_tab.CATEGORY_CAMERA, f"Camera status: {s}"))

                try:
                    self.window.root.after_idle(lambda conn=camera_connected: self.log_tab.update_udp_camera_status(conn))
                except Exception as e:
                    logger.error("SYSTEM", f"Error updating log inspector camera status: {e}")

        self.status_listener.on_message_received = on_status_message

        # Wire UDP Heartbeat listener callback
        def on_heartbeat_message(message):
            """Handle UDP heartbeat - called from background thread"""
            # Schedule GUI updates on main thread using after_idle()
            self.window.root.after_idle(lambda: self.protocol_tab.add_message(message, "received"))

            # Log heartbeat to activity log
            payload = message.get("payload", {})
            status = payload.get("status", "unknown")
            self.window.root.after_idle(lambda s=status: self.activity_tab.log_event(
                self.activity_tab.CATEGORY_UDP, f"Heartbeat: {s}"))

            # Update connection tab with heartbeat
            sender = payload.get("sender", "unknown")  # "air" or "ground"
            self.window.root.after_idle(lambda s=sender, d=payload:
                self.connection_tab.on_heartbeat_received(s, d))

        self.heartbeat_listener.on_message_received = on_heartbeat_message

        # Intercept TCP client send to add messages to protocol inspector
        original_send = self.tcp_client.send_message

        def send_with_logging(message):
            """Send message and log to protocol inspector"""
            # Parse message if it's a string
            import json
            try:
                if isinstance(message, str):
                    msg_dict = json.loads(message)
                else:
                    msg_dict = message

                # Add to protocol inspector
                self.protocol_tab.add_message(msg_dict, "sent")

                # Log to activity log
                msg_type = msg_dict.get("message_type", "unknown")
                self.activity_tab.log_event(self.activity_tab.CATEGORY_TCP,
                                           f"Sent {msg_type} message")
            except:
                pass  # Ignore JSON errors

            # Send original message
            return original_send(message)

        self.tcp_client.send_message = send_with_logging

    def run(self):
        """Run the application"""
        try:
            self.window.run()
        except KeyboardInterrupt:
            logger.info("SYSTEM", "Interrupted by user")
            self.cleanup()  # Cleanup on Ctrl+C
        except Exception as e:
            logger.exception("SYSTEM", f"Fatal error: {e}")
            self.cleanup()  # Cleanup on fatal error

    def cleanup(self):
        """Cleanup on shutdown - safe to call multiple times"""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return  # Already cleaned up

        self._cleanup_done = True
        logger.info("SYSTEM", "Cleaning up...")

        # Stop network components
        if self.tcp_client and self.tcp_client.is_connected():
            try:
                self.tcp_client.disconnect()
            except Exception as e:
                logger.error("NETWORK", f"Error disconnecting TCP: {e}")

        if self.status_listener and self.status_listener.is_running():
            try:
                self.status_listener.stop()
            except Exception as e:
                logger.error("NETWORK", f"Error stopping status listener: {e}")

        if self.heartbeat_listener and self.heartbeat_listener.is_running():
            try:
                self.heartbeat_listener.stop()
            except Exception as e:
                logger.error("NETWORK", f"Error stopping heartbeat listener: {e}")

        if self.heartbeat_sender and self.heartbeat_sender.is_running():
            try:
                self.heartbeat_sender.stop()
            except Exception as e:
                logger.error("NETWORK", f"Error stopping heartbeat sender: {e}")

        # Cleanup SSH connection in Log Inspector
        if self.log_tab:
            try:
                self.log_tab.cleanup()
            except Exception as e:
                logger.error("NETWORK", f"Error cleaning up SSH: {e}")

        logger.info("SYSTEM", "Application shutdown complete")


def main():
    """Main application entry point with mode support"""

    # Parse command-line arguments
    args = parse_args()

    # Configure logging based on mode
    import logging
    log_level = getattr(logging, devtools_config.get_log_level())
    logging.basicConfig(level=log_level)

    # Show configuration
    logger.info("SYSTEM", "=" * 60)
    logger.info("SYSTEM", f"DPM DevTools {get_version_string()} Starting...")
    logger.info("SYSTEM", f"Mode: {devtools_config.current_mode.value}")
    logger.info("SYSTEM", f"UI: {devtools_config.ui_mode.value}")
    logger.info("SYSTEM", f"Build: {get_build_info_string()}")
    logger.info("SYSTEM", "=" * 60)

    # Determine which interface to use
    if devtools_config.should_use_gui():
        # Run GUI mode
        logger.info("SYSTEM", "Starting GUI interface...")
        app = DiagnosticApp()
        app.initialize()
        app.run()
    else:
        # Run CLI mode
        logger.info("SYSTEM", "Starting CLI interface...")
        from cli_interface import CLIInterface
        cli = CLIInterface()
        cli.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("SYSTEM", f"Fatal error: {e}")
        sys.exit(1)
