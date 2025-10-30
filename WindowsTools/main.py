"""
DPM Diagnostic Tool - Main Entry Point
Windows diagnostic and testing tool for DPM Payload Manager

Usage:
    python main.py

Version: 1.0.0 - Phase 2
Date: October 2025
"""

import sys
from pathlib import Path

# Add WindowsTools to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger
from utils.config import config
from utils.protocol_loader import protocol

# Network components
from network.tcp_client import TCPClient
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


class DiagnosticApp:
    """Main application class that manages all components"""

    def __init__(self):
        self.window = None
        self.tcp_client = None
        self.status_listener = None
        self.heartbeat_listener = None
        self.heartbeat_sender = None

        # Tabs
        self.config_tab = None
        self.connection_tab = None
        self.protocol_tab = None
        self.command_tab = None
        self.camera_tab = None
        self.system_tab = None
        self.log_tab = None

    def initialize(self):
        """Initialize all components"""
        logger.info("=" * 60)
        logger.info("DPM Diagnostic Tool v1.0 (Phase 2) Starting...")
        logger.info("=" * 60)

        # Load protocol definitions
        logger.info("Loading protocol definitions...")
        if protocol.load():
            logger.info(f"  - Loaded {len(protocol.get_all_commands())} commands")
            logger.info(f"  - Loaded {len(protocol.get_all_properties())} properties")
        else:
            logger.warning("  - Failed to load some protocol definitions")

        # Load configuration
        logger.info("Loading configuration...")
        config.load()
        air_side_ip = config.get('network', 'air_side_ip')
        tcp_port = config.get('network', 'tcp_port')
        status_port = config.get('network', 'udp_status_port', 5001)
        heartbeat_port = config.get('network', 'udp_heartbeat_port', 5002)

        logger.info(f"  - Air-Side IP: {air_side_ip}")
        logger.info(f"  - TCP Port: {tcp_port}")
        logger.info(f"  - UDP Status Port: {status_port}")
        logger.info(f"  - UDP Heartbeat Port: {heartbeat_port}")

        # Create network components
        logger.info("Creating network components...")
        self._create_network_components(air_side_ip, tcp_port, status_port, heartbeat_port)

        # Create main window
        logger.info("Creating main window...")
        self.window = MainWindow()

        # Create tabs
        logger.info("Creating tabs...")
        self._create_tabs()

        # Wire everything together
        logger.info("Wiring components...")
        self._wire_components()

        # Update status bar
        self.window.update_status_bar(False, f"Air-Side: {air_side_ip}:{tcp_port}")

        logger.info("=" * 60)
        logger.info("Application ready!")
        logger.info("=" * 60)

    def _create_network_components(self, air_side_ip, tcp_port, status_port, heartbeat_port):
        """Create network components"""
        # TCP Client
        self.tcp_client = TCPClient(air_side_ip, tcp_port)

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

        # Add tabs to window (in display order)
        tabs = {
            "Connection Monitor": self.connection_tab,
            "Protocol Inspector": self.protocol_tab,
            "Command Sender": self.command_tab,
            "Camera Dashboard": self.camera_tab,
            "System Monitor": self.system_tab,
            "Log Inspector": self.log_tab,
            "Configuration": self.config_tab,
        }

        self.window.set_tabs(tabs)

    def _wire_components(self):
        """Wire all components together with callbacks"""
        # Give connection tab reference to TCP client
        # This sets up the connection tab's callbacks
        self.connection_tab.set_tcp_client(self.tcp_client)

        # Save the connection tab's callbacks so we can chain them
        connection_tab_on_connected = self.tcp_client.on_connected
        connection_tab_on_disconnected = self.tcp_client.on_disconnected
        connection_tab_on_message = self.tcp_client.on_message_received

        # Give command sender tab reference to TCP client
        self.command_tab.set_tcp_client(self.tcp_client)

        # Wire TCP client callbacks (chaining with connection tab callbacks)
        def on_tcp_message(message):
            """Handle TCP message received"""
            # Call connection tab's callback first
            if connection_tab_on_message:
                connection_tab_on_message(message)

            # Add to protocol inspector
            self.protocol_tab.add_message(message, "received")

        def on_tcp_connected():
            """Handle TCP connected"""
            # Call connection tab's callback first
            if connection_tab_on_connected:
                connection_tab_on_connected()

            logger.info("TCP connected - starting UDP listeners and heartbeat sender")

            # Start UDP listeners
            self.status_listener.start()
            self.heartbeat_listener.start()

            # Start heartbeat sender
            self.heartbeat_sender.start()

            # Update status bar
            air_side_ip = config.get('network', 'air_side_ip')
            tcp_port = config.get('network', 'tcp_port')
            self.window.update_status_bar(True, f"Connected: {air_side_ip}:{tcp_port}")

        def on_tcp_disconnected():
            """Handle TCP disconnected"""
            # Call connection tab's callback first
            if connection_tab_on_disconnected:
                connection_tab_on_disconnected()

            logger.info("TCP disconnected - stopping UDP listeners and heartbeat sender")

            # Stop UDP listeners
            if self.status_listener:
                self.status_listener.stop()
            if self.heartbeat_listener:
                self.heartbeat_listener.stop()

            # Stop heartbeat sender
            if self.heartbeat_sender:
                self.heartbeat_sender.stop()

            # Update status bar
            air_side_ip = config.get('network', 'air_side_ip')
            tcp_port = config.get('network', 'tcp_port')
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

            # Update log inspector camera comparison tab
            if "camera" in message:
                camera_connected = message["camera"].get("connected", False)
                logger.debug(f"Camera status from UDP: {camera_connected}")
                try:
                    self.window.root.after_idle(lambda conn=camera_connected: self.log_tab.update_udp_camera_status(conn))
                except Exception as e:
                    logger.error(f"Error updating log inspector camera status: {e}")

        self.status_listener.on_message_received = on_status_message

        # Wire UDP Heartbeat listener callback
        def on_heartbeat_message(message):
            """Handle UDP heartbeat - called from background thread"""
            # Schedule GUI updates on main thread using after_idle()
            self.window.root.after_idle(lambda: self.protocol_tab.add_message(message, "received"))

            # Update connection tab with heartbeat stats
            # (Connection tab would need enhancement to display this)

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
            logger.info("Interrupted by user")
        except Exception as e:
            logger.exception(f"Fatal error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup on shutdown"""
        logger.info("Cleaning up...")

        # Stop network components
        if self.tcp_client and self.tcp_client.is_connected():
            self.tcp_client.disconnect()

        if self.status_listener and self.status_listener.is_running():
            self.status_listener.stop()

        if self.heartbeat_listener and self.heartbeat_listener.is_running():
            self.heartbeat_listener.stop()

        if self.heartbeat_sender and self.heartbeat_sender.is_running():
            self.heartbeat_sender.stop()

        # Cleanup SSH connection in Log Inspector
        if self.log_tab:
            self.log_tab.cleanup()

        logger.info("Application shutdown complete")


def main():
    """Main application entry point"""
    app = DiagnosticApp()
    app.initialize()
    app.run()


if __name__ == "__main__":
    main()
