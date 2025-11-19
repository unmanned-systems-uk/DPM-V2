"""
Air-Side Controller
===================

Programmatic interface for Air-Side operations (Raspberry Pi 5 + PayloadManager).

Provides:
- Status monitoring (heartbeat, performance metrics)
- Configuration management
- Command execution
- Log retrieval
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from network.tcp_client import TCPClient
from network.ssh_client import SSHClient
from network.protocol import protocol_msg
from utils.protocol_logger import logger
from utils.config import config
from .response import APIResponse


class AirSideController:
    """
    Air-Side programmatic control interface

    Example:
        controller = AirSideController()
        controller.connect()

        # Get status
        result = controller.get_status()
        if result['success']:
            print(result['data'])

        # Send command
        result = controller.send_command('camera.capture', {'quality': 95})

        controller.disconnect()
    """

    def __init__(self, tcp_client: Optional[TCPClient] = None, ssh_client: Optional[SSHClient] = None):
        """
        Initialize Air-Side controller

        Args:
            tcp_client: Existing TCP client instance (optional, created on connect if not provided)
            ssh_client: Existing SSH client instance (optional, created on connect if not provided)
        """
        self.tcp_client = tcp_client
        self.ssh_client = ssh_client
        self._last_status = None
        self._last_status_time = None

        logger.debug("SYSTEM", "AirSideController initialized")

    def connect(
        self,
        host: Optional[str] = None,
        tcp_port: Optional[int] = None,
        ssh_port: Optional[int] = None,
        timeout: float = 5.0
    ) -> APIResponse:
        """
        Connect to Air-Side (TCP + SSH)

        Args:
            host: Air-Side IP address (default: from config)
            tcp_port: TCP port (default: from config)
            ssh_port: SSH port (default: 22)
            timeout: Connection timeout in seconds

        Returns:
            APIResponse with connection status
        """
        try:
            # Use config defaults if not provided
            host = host or config.get('air_side_ip', '10.0.1.53')
            tcp_port = tcp_port or config.get('tcp_port', 5001)
            ssh_port = ssh_port or 22

            # Create TCP client if not exists
            if not self.tcp_client:
                self.tcp_client = TCPClient(host, tcp_port)

            # Connect TCP
            if not self.tcp_client.connect(host, tcp_port):
                return APIResponse.error_response(
                    error="Failed to establish TCP connection",
                    domain="air-side",
                    operation="connect"
                )

            logger.info("NETWORK", f"API: TCP connected to {host}:{tcp_port}")

            # Note: SSH connection requires credentials, handle separately
            return APIResponse.success_response(
                data={
                    "tcp_connected": True,
                    "host": host,
                    "tcp_port": tcp_port
                },
                domain="air-side",
                operation="connect"
            )

        except Exception as e:
            logger.error("NETWORK", f"API: Failed to connect to Air-Side: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="connect"
            )

    def disconnect(self) -> APIResponse:
        """
        Disconnect from Air-Side

        Returns:
            APIResponse with disconnection status
        """
        try:
            if self.tcp_client:
                self.tcp_client.disconnect()

            if self.ssh_client and self.ssh_client.is_connected():
                self.ssh_client.disconnect()

            logger.info("NETWORK", "API: Disconnected from Air-Side")

            return APIResponse.success_response(
                data={"disconnected": True},
                domain="air-side",
                operation="disconnect"
            )

        except Exception as e:
            logger.error("NETWORK", f"API: Error during disconnect: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="disconnect"
            )

    def is_connected(self) -> bool:
        """Check if connected to Air-Side"""
        return self.tcp_client and self.tcp_client.is_connected()

    def get_status(self, timeout: float = 2.0) -> APIResponse:
        """
        Get current Air-Side status (performance metrics, camera status, etc.)

        Args:
            timeout: Response timeout in seconds

        Returns:
            APIResponse with status data
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Air-Side",
                domain="air-side",
                operation="get_status"
            )

        try:
            # Send status.get command
            command_msg = protocol_msg("status.get", {})
            self.tcp_client.send_command(command_msg)

            # Wait for response (simplified - in production would use proper response handling)
            time.sleep(timeout)

            # Return cached status if available
            if self._last_status:
                return APIResponse.success_response(
                    data=self._last_status,
                    domain="air-side",
                    operation="get_status"
                )
            else:
                return APIResponse.error_response(
                    error="No status received",
                    domain="air-side",
                    operation="get_status"
                )

        except Exception as e:
            logger.error("COMMAND", f"API: Failed to get status: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="get_status"
            )

    def send_command(
        self,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: float = 5.0
    ) -> APIResponse:
        """
        Send command to Air-Side

        Args:
            command: Command name (e.g., "camera.capture", "camera.start_recording")
            parameters: Command parameters
            timeout: Response timeout in seconds

        Returns:
            APIResponse with command result
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Air-Side",
                domain="air-side",
                operation="send_command"
            )

        try:
            parameters = parameters or {}

            # Build protocol message
            command_msg = protocol_msg(command, parameters)

            # Send command
            success = self.tcp_client.send_command(command_msg)

            if success:
                logger.info("COMMAND", f"API: Sent command {command}")
                return APIResponse.success_response(
                    data={
                        "command": command,
                        "parameters": parameters,
                        "sent": True
                    },
                    domain="air-side",
                    operation="send_command"
                )
            else:
                return APIResponse.error_response(
                    error="Failed to send command",
                    domain="air-side",
                    operation="send_command",
                    data={"command": command, "parameters": parameters}
                )

        except Exception as e:
            logger.error("COMMAND", f"API: Failed to send command {command}: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="send_command",
                data={"command": command, "parameters": parameters}
            )

    def get_configuration(self) -> APIResponse:
        """
        Get current Air-Side configuration

        Returns:
            APIResponse with configuration data
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Air-Side",
                domain="air-side",
                operation="get_configuration"
            )

        try:
            # Send config.get command
            command_msg = protocol_msg("config.get", {})
            self.tcp_client.send_command(command_msg)

            # TODO: Implement proper response handling
            logger.info("CONFIG", "API: Requested configuration")

            return APIResponse.success_response(
                data={"requested": True},
                domain="air-side",
                operation="get_configuration"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to get configuration: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="get_configuration"
            )

    def set_configuration(self, config_key: str, config_value: Any) -> APIResponse:
        """
        Set Air-Side configuration value

        Args:
            config_key: Configuration key
            config_value: Configuration value

        Returns:
            APIResponse with operation result
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Air-Side",
                domain="air-side",
                operation="set_configuration"
            )

        try:
            # Send config.set command
            command_msg = protocol_msg("config.set", {
                "key": config_key,
                "value": config_value
            })

            success = self.tcp_client.send_command(command_msg)

            if success:
                logger.info("CONFIG", f"API: Set config {config_key}={config_value}")
                return APIResponse.success_response(
                    data={
                        "key": config_key,
                        "value": config_value,
                        "applied": True
                    },
                    domain="air-side",
                    operation="set_configuration"
                )
            else:
                return APIResponse.error_response(
                    error="Failed to set configuration",
                    domain="air-side",
                    operation="set_configuration",
                    data={"key": config_key, "value": config_value}
                )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to set configuration: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="set_configuration",
                data={"key": config_key, "value": config_value}
            )

    def execute_ssh_command(self, command: str, timeout: float = 10.0) -> APIResponse:
        """
        Execute SSH command on Air-Side

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds

        Returns:
            APIResponse with command output
        """
        if not self.ssh_client.is_connected():
            return APIResponse.error_response(
                error="SSH not connected",
                domain="air-side",
                operation="execute_ssh_command"
            )

        try:
            stdout, stderr, exit_code = self.ssh_client.execute_command(command, timeout=timeout)

            logger.info("SYSTEM", f"API: Executed SSH command: {command}")

            return APIResponse.success_response(
                data={
                    "command": command,
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": exit_code,
                    "success": exit_code == 0
                },
                domain="air-side",
                operation="execute_ssh_command"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: SSH command failed: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="execute_ssh_command",
                data={"command": command}
            )

    def get_docker_logs(self, lines: int = 100) -> APIResponse:
        """
        Get Docker container logs from Air-Side

        Args:
            lines: Number of log lines to retrieve

        Returns:
            APIResponse with log data
        """
        if not self.ssh_client.is_connected():
            return APIResponse.error_response(
                error="SSH not connected",
                domain="air-side",
                operation="get_docker_logs"
            )

        try:
            command = f"docker logs payload-manager --tail {lines}"
            result = self.execute_ssh_command(command)

            if result.success:
                return APIResponse.success_response(
                    data={
                        "logs": result.data['stdout'],
                        "lines": lines
                    },
                    domain="air-side",
                    operation="get_docker_logs"
                )
            else:
                return result  # Forward error response

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to get Docker logs: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="get_docker_logs"
            )

    def update_status_cache(self, status: Dict[str, Any]):
        """
        Update cached status (called by response handlers)

        Args:
            status: Status data from Air-Side
        """
        self._last_status = status
        self._last_status_time = datetime.utcnow()
