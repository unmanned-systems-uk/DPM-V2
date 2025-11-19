"""
TCP Client for DPM Diagnostic Tool
Handles TCP command communication with Air-Side
"""

import socket
import threading
import time
import queue
import json
from typing import Optional, Callable, Dict, Any

from utils.protocol_logger import logger
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
            logger.info("NETWORK", f"Connecting to {self.host}:{self.port}...")

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

            self.connected = True
            self.running = True

            logger.info("NETWORK", f"Connected to {self.host}:{self.port}")

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            if self.on_connected:
                self.on_connected()

            return True

        except socket.timeout:
            logger.error("NETWORK", f"Connection timeout to {self.host}:{self.port}")
            if self.on_error:
                self.on_error(f"Connection timeout")
            return False

        except Exception as e:
            logger.error("NETWORK", f"Connection error: {e}")
            if self.on_error:
                self.on_error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Air-Side"""
        logger.info("NETWORK", "Disconnecting...")

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

        logger.info("NETWORK", "Disconnected")

    def send_message(self, message: str) -> bool:
        """Send JSON message to Air-Side"""
        if not self.connected or not self.socket:
            logger.error("COMMAND", "Not connected - cannot send message")
            return False

        try:
            # Parse message to extract command details for logging
            try:
                msg_dict = json.loads(message)
                msg_type = msg_dict.get("message_type", "unknown")

                # Log command details with COMMAND context
                if msg_type == "command":
                    payload = msg_dict.get("payload", {})
                    command_name = payload.get("command", "unknown")
                    parameters = payload.get("parameters", {})

                    # Sanitize parameters (avoid logging sensitive data)
                    sanitized_params = self._sanitize_parameters(parameters)

                    logger.info("COMMAND", f"Sending command to {self.host}:{self.port}")
                    logger.info("COMMAND", f"  Command: {command_name}")
                    logger.info("COMMAND", f"  Parameters: {sanitized_params}")
                    logger.info("COMMAND", f"  Sequence ID: {msg_dict.get('sequence_id', 'N/A')}")
                else:
                    logger.debug("COMMAND", f"Sending {msg_type} message to {self.host}:{self.port}")

            except json.JSONDecodeError:
                logger.warning("COMMAND", f"Sending non-JSON message to {self.host}:{self.port}")

            # Add newline delimiter
            data = message.encode() + b'\n'
            self.socket.sendall(data)
            logger.debug("NETWORK", f"Sent: {message[:100]}...")
            return True

        except Exception as e:
            logger.error("COMMAND", f"Send error: {e}")
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
                    logger.warning("NETWORK", "Connection closed by remote host")
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
                    logger.error("NETWORK", f"Receive error: {e}")
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

            logger.debug("NETWORK", f"Received: {message_str[:100]}...")

            # Log response details with COMMAND context
            msg_type = message.get("message_type", "unknown")
            if msg_type == "response":
                payload = message.get("payload", {})
                status = payload.get("status", "unknown")
                original_command = payload.get("command", "unknown")

                logger.info("COMMAND", f"Received response from {self.host}:{self.port}")
                logger.info("COMMAND", f"  Original Command: {original_command}")
                logger.info("COMMAND", f"  Status: {status}")
                logger.info("COMMAND", f"  Sequence ID: {message.get('sequence_id', 'N/A')}")

                # Log error details if present
                if status == "error":
                    error_code = payload.get("error_code", "N/A")
                    error_msg = payload.get("message", "No error message")
                    logger.error("COMMAND", f"  Error Code: {error_code}")
                    logger.error("COMMAND", f"  Error Message: {error_msg}")

            # Add to response queue
            self.response_queue.put(message)

            # Call callback
            if self.on_message_received:
                self.on_message_received(message)

        except Exception as e:
            logger.error("COMMAND", f"Error handling message: {e}")

    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected

    def _sanitize_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for logging (remove sensitive data)"""
        if not parameters:
            return {}

        sanitized = {}
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'auth']

        for key, value in parameters.items():
            # Check if key contains sensitive keywords
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                # Limit long values to prevent log spam
                if isinstance(value, str) and len(value) > 100:
                    sanitized[key] = f"{value[:100]}... (truncated)"
                else:
                    sanitized[key] = value

        return sanitized
