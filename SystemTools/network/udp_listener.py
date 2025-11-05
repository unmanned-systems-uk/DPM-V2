"""
UDP Listeners for DPM Diagnostic Tool
Receives status broadcasts and heartbeat messages from Air-Side
"""

import socket
import threading
import json
from typing import Optional, Callable, Dict, Any

from utils.logger import logger


class UDPListener:
    """UDP listener for receiving broadcasts"""

    def __init__(self, port: int, name: str = "UDP"):
        self.port = port
        self.name = name
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_message_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # Statistics
        self.messages_received = 0
        self.last_message_time = 0

    def start(self) -> bool:
        """Start listening for UDP messages"""
        try:
            logger.info(f"{self.name}: Starting listener on port {self.port}...")

            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to port (listen on all interfaces)
            self.socket.bind(('', self.port))

            # Set timeout for clean shutdown
            self.socket.settimeout(1.0)

            self.running = True

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            logger.info(f"{self.name}: Listener started on port {self.port}")
            return True

        except Exception as e:
            logger.error(f"{self.name}: Failed to start listener: {e}")
            if self.on_error:
                self.on_error(f"Failed to start {self.name} listener: {e}")
            return False

    def stop(self):
        """Stop listening"""
        logger.info(f"{self.name}: Stopping listener...")

        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        self.socket = None

        logger.info(f"{self.name}: Listener stopped")

    def _receive_loop(self):
        """Background thread to receive UDP messages"""
        while self.running:
            try:
                # Receive data
                data, addr = self.socket.recvfrom(4096)

                if data:
                    self._handle_message(data.decode('utf-8'), addr)

            except socket.timeout:
                continue  # Normal timeout, keep trying

            except Exception as e:
                if self.running:  # Only log if not intentionally stopping
                    logger.debug(f"{self.name}: Receive error: {e}")

    def _handle_message(self, message_str: str, addr: tuple):
        """Handle received message"""
        try:
            # Parse JSON
            message = json.loads(message_str)

            # Update statistics
            self.messages_received += 1
            import time
            self.last_message_time = time.time()

            logger.debug(f"{self.name}: Received from {addr[0]}:{addr[1]}")

            # Call callback
            if self.on_message_received:
                self.on_message_received(message)

        except json.JSONDecodeError as e:
            logger.warning(f"{self.name}: Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"{self.name}: Error handling message: {e}")

    def is_running(self) -> bool:
        """Check if listener is running"""
        return self.running

    def get_stats(self) -> Dict[str, Any]:
        """Get listener statistics"""
        return {
            "messages_received": self.messages_received,
            "last_message_time": self.last_message_time,
            "running": self.running
        }


class StatusListener(UDPListener):
    """UDP listener for status broadcasts (5 Hz)"""

    def __init__(self, port: int = 5001):
        super().__init__(port, "Status")


class HeartbeatListener(UDPListener):
    """UDP listener for heartbeat messages (1 Hz)"""

    def __init__(self, port: int = 5002):
        super().__init__(port, "Heartbeat")
