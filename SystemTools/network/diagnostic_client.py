"""
DPM Diagnostic Client
Sends diagnostic commands to H16 via Air-Side TCP server (10.0.1.53:5000)
Air-Side forwards diagnostic commands to H16 and returns responses
"""

import json
import socket
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class DiagnosticClient:
    """Client for sending diagnostic commands to H16 via TCP"""

    def __init__(self, tcp_connection=None):
        """
        Initialize diagnostic client

        Args:
            tcp_connection: Existing TCP connection to reuse, or None to create new
        """
        self.tcp_connection = tcp_connection
        self.sequence_id = 0
        self.pending_requests = {}
        self.lock = threading.Lock()

    def _get_next_sequence_id(self) -> int:
        """Get next sequence ID for request"""
        with self.lock:
            self.sequence_id += 1
            return self.sequence_id

    def send_command(
        self,
        command: str,
        params: Optional[Dict] = None,
        timeout: int = 5,
        host: str = "10.0.1.53",
        port: int = 5000
    ) -> Dict:
        """
        Send diagnostic command and await response

        Args:
            command: Diagnostic command name (e.g., "diagnostics.ping")
            params: Optional command parameters
            timeout: Response timeout in seconds
            host: Air-Side IP address (forwards to H16)
            port: Air-Side TCP port (default 5000)

        Returns:
            Response dictionary with 'success', 'data', 'error_code', 'error_message'

        Raises:
            Exception: On connection or timeout errors
        """
        sequence_id = self._get_next_sequence_id()

        # Build request message per DPM protocol
        request = {
            "protocol_version": "1.0",
            "message_type": "command",
            "sequence_id": sequence_id,
            "timestamp": int(time.time()),
            "payload": {
                "command": command,
                "parameters": params or {}
            }
        }

        logger.debug(f"Sending diagnostic command: {command}")

        try:
            # Connect to Air-Side (which forwards to H16)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Send request
            request_json = json.dumps(request) + "\n"
            sock.sendall(request_json.encode('utf-8'))

            # Receive response
            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                # Check if we have complete JSON
                try:
                    json.loads(response_data.decode('utf-8'))
                    break  # Complete JSON received
                except json.JSONDecodeError:
                    continue  # Need more data

            sock.close()

            # Parse response
            if not response_data:
                raise Exception("No response from Air-Side")

            response = json.loads(response_data.decode('utf-8'))
            logger.debug(f"Received response: {response.get('command', 'unknown')}")

            # Convert to standard format
            return {
                "success": response.get("status") == "success",
                "data": response.get("result", {}),
                "error_code": response.get("error_code", 0),
                "error_message": response.get("error_message", "")
            }

        except socket.timeout:
            logger.error(f"Timeout waiting for response from {command}")
            raise Exception(f"Timeout after {timeout}s")
        except Exception as e:
            logger.error(f"Error sending diagnostic command: {e}")
            raise

    def send_command_async(
        self,
        command: str,
        params: Optional[Dict] = None,
        callback: Optional[Callable] = None,
        timeout: int = 5,
        host: str = "10.0.1.53",
        port: int = 5000
    ):
        """
        Send diagnostic command asynchronously with callback

        Args:
            command: Diagnostic command name
            params: Optional command parameters
            callback: Function to call with response (receives dict)
            timeout: Response timeout in seconds
            host: Air-Side IP address (forwards to H16)
            port: Air-Side TCP port
        """
        def async_send():
            try:
                response = self.send_command(command, params, timeout, host, port)
                if callback:
                    callback(response)
            except Exception as e:
                if callback:
                    callback({
                        "success": False,
                        "data": {},
                        "error_code": 6004,
                        "error_message": str(e)
                    })

        thread = threading.Thread(target=async_send, daemon=True)
        thread.start()

    # Convenience methods for common commands

    def ping_h16(self, host: str = "10.0.1.53", port: int = 5000) -> bool:
        """
        Quick alive check for H16 via Air-Side

        Returns:
            True if H16 responds, False otherwise
        """
        try:
            response = self.send_command("diagnostics.ping", timeout=1, host=host, port=port)
            return response.get("success", False)
        except Exception:
            return False

    def get_system_info(self, host: str = "10.0.1.53", port: int = 5000) -> Dict:
        """
        Get H16 system information (battery, CPU, memory, storage) via Air-Side

        Returns:
            Response dictionary
        """
        return self.send_command("diagnostics.get_system_info", timeout=2, host=host, port=port)

    def get_app_status(self, host: str = "10.0.1.53", port: int = 5000) -> Dict:
        """
        Get H16 app status and health via Air-Side

        Returns:
            Response dictionary
        """
        return self.send_command("diagnostics.get_app_status", timeout=2, host=host, port=port)
