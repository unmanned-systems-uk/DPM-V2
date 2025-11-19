"""
CLI Interface for DevTools
Provides command-line interface for deployment mode
"""

import sys
import time
import threading
from typing import Optional, Dict, Any
from datetime import datetime
import colorama
from colorama import Fore, Style, Back

# Initialize colorama for cross-platform colored output
colorama.init()

from utils.protocol_logger import logger
from utils.config import config
from utils.protocol_loader import protocol
from network.tcp_client import TCPClient
from network.udp_listener import StatusListener, HeartbeatListener
from network.heartbeat import HeartbeatSender
from devtools_config import devtools_config


class CLIInterface:
    """Command-line interface for DevTools"""

    def __init__(self):
        """Initialize CLI interface"""
        self.tcp_client = None
        self.status_listener = None
        self.heartbeat_listener = None
        self.heartbeat_sender = None
        self.running = False
        self.connected = False

        # Thread for background operations
        self.monitor_thread = None

        # Status data
        self.last_status = {}
        self.last_heartbeat = {}
        self.connection_state = "DISCONNECTED"

    def print_banner(self):
        """Print application banner"""
        if devtools_config.get("show_banner", True):
            print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}DPM DevTools - CLI Mode{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Mode: {devtools_config.current_mode.value}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message

        Args:
            message: Message to print
            status: Status type (INFO, SUCCESS, WARNING, ERROR)
        """
        colors = {
            "INFO": Fore.WHITE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA
        }

        color = colors.get(status, Fore.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if devtools_config.get("compact_display", False):
            print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")
        else:
            print(f"{color}[{timestamp}] [{status}] {message}{Style.RESET_ALL}")

    def setup_network(self, air_side_ip: str, tcp_port: int,
                     status_port: int, heartbeat_port: int):
        """Setup network components

        Args:
            air_side_ip: Air-side IP address
            tcp_port: TCP command port
            status_port: UDP status port
            heartbeat_port: UDP heartbeat port
        """
        try:
            # Create TCP client
            self.tcp_client = TCPClient(air_side_ip, tcp_port)

            # Create UDP listeners
            self.status_listener = StatusListener(status_port)
            self.status_listener.status_callback = self.on_status_received

            self.heartbeat_listener = HeartbeatListener(heartbeat_port)
            self.heartbeat_listener.heartbeat_callback = self.on_heartbeat_received

            # Create heartbeat sender
            self.heartbeat_sender = HeartbeatSender(air_side_ip, heartbeat_port)

            self.print_status("Network components created", "SUCCESS")

        except Exception as e:
            self.print_status(f"Failed to setup network: {e}", "ERROR")
            raise

    def connect(self) -> bool:
        """Connect to air-side

        Returns:
            bool: True if connected successfully
        """
        if self.tcp_client:
            if self.tcp_client.connect():
                self.connected = True
                self.connection_state = "CONNECTED"
                self.print_status(f"Connected to air-side", "SUCCESS")

                # Start listeners
                self.status_listener.start()
                self.heartbeat_listener.start()
                self.heartbeat_sender.start()

                return True
            else:
                self.print_status("Failed to connect", "ERROR")
                return False
        return False

    def disconnect(self):
        """Disconnect from air-side"""
        if self.connected:
            # Stop listeners
            if self.status_listener:
                self.status_listener.stop()
            if self.heartbeat_listener:
                self.heartbeat_listener.stop()
            if self.heartbeat_sender:
                self.heartbeat_sender.stop()

            # Disconnect TCP
            if self.tcp_client:
                self.tcp_client.disconnect()

            self.connected = False
            self.connection_state = "DISCONNECTED"
            self.print_status("Disconnected", "INFO")

    def on_status_received(self, data: Dict[str, Any]):
        """Handle received status data

        Args:
            data: Status data dictionary
        """
        self.last_status = data

        if devtools_config.should_show_debug_info():
            self.print_status(f"Status: {data.get('camera_state', 'Unknown')}", "DEBUG")

    def on_heartbeat_received(self, data: Dict[str, Any]):
        """Handle received heartbeat data

        Args:
            data: Heartbeat data dictionary
        """
        self.last_heartbeat = data
        self.connection_state = "CONNECTED"

    def send_command(self, command_name: str, params: Optional[Dict] = None) -> bool:
        """Send command to air-side

        Args:
            command_name: Name of command
            params: Optional command parameters

        Returns:
            bool: True if sent successfully
        """
        if not self.connected:
            self.print_status("Not connected", "ERROR")
            return False

        # Get command definition
        cmd_def = protocol.get_command(command_name)
        if not cmd_def:
            self.print_status(f"Unknown command: {command_name}", "ERROR")
            return False

        # Send command
        success = self.tcp_client.send_command(command_name, params or {})

        if success:
            self.print_status(f"Command sent: {command_name}", "SUCCESS")
        else:
            self.print_status(f"Failed to send command", "ERROR")

        return success

    def monitor_connection(self):
        """Background thread to monitor connection"""
        while self.running:
            # Check heartbeat timeout
            if self.connected:
                # Simple connection check
                if self.connection_state == "CONNECTED":
                    sys.stdout.write(f"\r{Fore.GREEN}● Connected{Style.RESET_ALL}")
                else:
                    sys.stdout.write(f"\r{Fore.RED}● Disconnected{Style.RESET_ALL}")
                sys.stdout.flush()

            time.sleep(1)

    def interactive_mode(self):
        """Run interactive command mode"""
        self.print_status("Entering interactive mode. Type 'help' for commands.", "INFO")

        while self.running:
            try:
                # Show prompt
                prompt = f"{Fore.GREEN}DPM>{Style.RESET_ALL} " if self.connected else f"{Fore.RED}DPM>{Style.RESET_ALL} "
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Parse command
                parts = user_input.split()
                cmd = parts[0].lower()

                # Handle built-in commands
                if cmd == "help":
                    self.show_help()
                elif cmd == "quit" or cmd == "exit":
                    self.running = False
                elif cmd == "connect":
                    if not self.connected:
                        self.connect()
                    else:
                        self.print_status("Already connected", "WARNING")
                elif cmd == "disconnect":
                    if self.connected:
                        self.disconnect()
                    else:
                        self.print_status("Not connected", "WARNING")
                elif cmd == "status":
                    self.show_status()
                elif cmd == "send":
                    if len(parts) > 1:
                        self.send_command(parts[1])
                    else:
                        self.print_status("Usage: send <command>", "ERROR")
                elif cmd == "list":
                    self.list_commands()
                elif cmd == "clear":
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    self.print_status(f"Unknown command: {cmd}", "ERROR")

            except KeyboardInterrupt:
                print()
                self.running = False
            except Exception as e:
                self.print_status(f"Error: {e}", "ERROR")

    def show_help(self):
        """Show help information"""
        print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
        print("  help       - Show this help")
        print("  connect    - Connect to air-side")
        print("  disconnect - Disconnect from air-side")
        print("  status     - Show current status")
        print("  send <cmd> - Send command")
        print("  list       - List available commands")
        print("  clear      - Clear screen")
        print("  quit/exit  - Exit program")
        print()

    def show_status(self):
        """Show current system status"""
        print(f"\n{Fore.CYAN}System Status:{Style.RESET_ALL}")
        print(f"  Connection: {self.connection_state}")

        if self.last_status:
            print(f"  Camera State: {self.last_status.get('camera_state', 'Unknown')}")
            print(f"  Focus Mode: {self.last_status.get('focus_mode', 'Unknown')}")
            print(f"  ISO: {self.last_status.get('iso', 'Unknown')}")

        if self.last_heartbeat:
            print(f"  Last Heartbeat: {self.last_heartbeat.get('timestamp', 'Never')}")
        print()

    def list_commands(self):
        """List available protocol commands"""
        commands = protocol.get_all_commands()
        if commands:
            print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
            for cmd in sorted(commands.keys()):
                cmd_def = commands[cmd]
                desc = cmd_def.get('description', 'No description')
                print(f"  {cmd:<20} - {desc}")
        else:
            print("No commands loaded")
        print()

    def run(self):
        """Main run loop for CLI interface"""
        self.running = True
        self.print_banner()

        # Load configuration
        logger.info("SYSTEM", "Loading configuration...")
        config.load()

        # Load protocol
        logger.info("SYSTEM", "Loading protocol...")
        protocol.load()

        # Setup network
        air_side_ip = config.get('network', 'air_side_ip')
        tcp_port = config.get('network', 'tcp_port')
        status_port = config.get('network', 'udp_status_port', 5001)
        heartbeat_port = config.get('network', 'udp_heartbeat_port', 5002)

        self.setup_network(air_side_ip, tcp_port, status_port, heartbeat_port)

        # Auto-connect if configured
        if devtools_config.get("auto_connect", True):
            self.print_status("Auto-connecting...", "INFO")
            self.connect()

        # Start monitor thread
        self.monitor_thread = threading.Thread(target=self.monitor_connection, daemon=True)
        self.monitor_thread.start()

        # Enter interactive mode
        if devtools_config.get("interactive_mode", True):
            self.interactive_mode()
        else:
            # Just monitor until interrupted
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.running = False

        # Cleanup
        self.print_status("Shutting down...", "INFO")
        self.disconnect()
        self.print_status("Goodbye!", "SUCCESS")


def main():
    """Main entry point for CLI mode"""
    cli = CLIInterface()
    try:
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    # Parse arguments first
    from devtools_config import parse_args
    parse_args()

    # Run CLI
    main()