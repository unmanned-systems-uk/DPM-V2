"""
TCP Client for DPM Diagnostic Tool
Handles TCP command communication with Air-Side
"""

import socket
import threading
import time
import queue
from typing import Optional, Callable, Dict, Any

from utils.logger import logger
from network.protocol import protocol_msg


class TCPClient:
    """TCP client for command communication"""

    def __init__(self, host: str, port: int, timeout_ms: int = 5000):
        self.host = host
        self.port = port
        self.timeout = timeout_ms / 1000.0  # Convert to seconds

        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False

        self.receive_thread: Optional[threading.Thread] = None
        self.response_queue = queue.Queue()

        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_message_received: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    def connect(self) -> bool:
        """Connect to Air-Side TCP server"""
        try:
            logger.info(f"Connecting to {self.host}:{self.port}...")

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

            self.connected = True
            self.running = True

            logger.info(f"Connected to {self.host}:{self.port}")

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            if self.on_connected:
                self.on_connected()

            return True

        except socket.timeout:
            logger.error(f"Connection timeout to {self.host}:{self.port}")
            if self.on_error:
                self.on_error(f"Connection timeout")
            return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            if self.on_error:
                self.on_error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Air-Side"""
        logger.info("Disconnecting...")

        self.running = False

        if self.socket:
            try:
                # Send disconnect message
                disconnect_msg = protocol_msg.create_disconnect()
                self.socket.sendall(disconnect_msg.encode() + b'\n')
            except:
                pass

            try:
                self.socket.close()
            except:
                pass

        self.socket = None
        self.connected = False

        if self.on_disconnected:
            self.on_disconnected()

        logger.info("Disconnected")

    def send_message(self, message: str) -> bool:
        """Send JSON message to Air-Side"""
        if not self.connected or not self.socket:
            logger.error("Not connected")
            return False

        try:
            # Add newline delimiter
            data = message.encode() + b'\n'
            self.socket.sendall(data)
            logger.debug(f"Sent: {message[:100]}...")
            return True

        except Exception as e:
            logger.error(f"Send error: {e}")
            if self.on_error:
                self.on_error(f"Send error: {e}")
            self.disconnect()
            return False

    def send_command(self, command: str, parameters: Dict[str, Any] = None) -> bool:
        """Send command and return success"""
        msg = protocol_msg.create_command(command, parameters)
        return self.send_message(msg)

    def send_handshake(self) -> bool:
        """Send handshake message"""
        msg = protocol_msg.create_handshake()
        return self.send_message(msg)

    def wait_for_response(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Wait for a response message"""
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _receive_loop(self):
        """Background thread to receive messages"""
        buffer = b''

        while self.running and self.connected:
            try:
                # Receive data
                data = self.socket.recv(4096)

                if not data:
                    logger.warning("Connection closed by remote host")
                    break

                buffer += data

                # Process complete messages (newline-delimited)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)

                    if line:
                        self._handle_message(line.decode('utf-8'))

            except socket.timeout:
                continue  # Normal timeout, keep trying

            except Exception as e:
                if self.running:  # Only log if not intentionally disconnecting
                    logger.error(f"Receive error: {e}")
                break

        # Clean up on exit
        self.connected = False
        if self.on_disconnected:
            self.on_disconnected()

    def _handle_message(self, message_str: str):
        """Handle received message"""
        try:
            message = protocol_msg.parse_message(message_str)

            if not message:
                return

            logger.debug(f"Received: {message_str[:100]}...")

            # Add to response queue
            self.response_queue.put(message)

            # Call callback
            if self.on_message_received:
                self.on_message_received(message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected
