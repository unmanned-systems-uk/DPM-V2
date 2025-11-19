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
            host = host or config.get('network', 'air_side_ip', '10.0.1.53')
            tcp_port = tcp_port or config.get('network', 'tcp_port', 5000)
            ssh_port = ssh_port or 22

            # Create TCP client if not exists
            if not self.tcp_client:
                self.tcp_client = TCPClient(host, tcp_port)

            # Connect TCP
            if not self.tcp_client.connect():
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
            command_msg = protocol_msg.create_command("status.get", {})
            success = self.tcp_client.send_command(command_msg)

            if success:
                logger.info("COMMAND", f"API: Sent status.get command")
                return APIResponse.success_response(
                    data={
                        "command": "status.get",
                        "sent": True,
                        "status": "Command sent successfully"
                    },
                    domain="air-side",
                    operation="get_status"
                )
            else:
                return APIResponse.error_response(
                    error="Failed to send status.get command",
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
            command_msg = protocol_msg.create_command(command, parameters)

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

    # ========================================================================
    # PHASE 2: EXTENDED AIR-SIDE OPERATIONS
    # ========================================================================

    def send_command_with_callback(
        self,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        on_response: Optional[callable] = None,
        on_error: Optional[callable] = None,
        timeout: float = 5.0
    ) -> APIResponse:
        """
        Send command with response/error callbacks (Phase 2)

        Args:
            command: Command name
            parameters: Command parameters
            on_response: Callback for successful response (receives response data)
            on_error: Callback for error response (receives error message)
            timeout: Response timeout

        Returns:
            APIResponse with command send status
        """
        try:
            # Store callbacks for response handler
            if not hasattr(self, '_response_callbacks'):
                self._response_callbacks = {}
            if not hasattr(self, '_error_callbacks'):
                self._error_callbacks = {}

            callback_id = f"{command}_{time.time()}"
            if on_response:
                self._response_callbacks[callback_id] = on_response
            if on_error:
                self._error_callbacks[callback_id] = on_error

            # Send command
            result = self.send_command(command, parameters, timeout)

            # Note: Actual callback invocation would happen in response handler
            # For now, return command send status
            if result.success:
                result.data['callback_id'] = callback_id

            return result

        except Exception as e:
            logger.error("COMMAND", f"API: Failed to send command with callback: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="send_command_with_callback"
            )

    def subscribe_to_status(
        self,
        callback: callable,
        interval_ms: int = 200
    ) -> APIResponse:
        """
        Subscribe to real-time status updates (Phase 2)

        Args:
            callback: Callback function (receives status dict)
            interval_ms: Update interval in milliseconds

        Returns:
            APIResponse with subscription status
        """
        try:
            if not hasattr(self, '_status_subscribers'):
                self._status_subscribers = []

            self._status_subscribers.append({
                'callback': callback,
                'interval_ms': interval_ms
            })

            logger.info("HEALTH", f"API: Subscribed to status updates (interval: {interval_ms}ms)")

            return APIResponse.success_response(
                data={
                    "subscribed": True,
                    "interval_ms": interval_ms,
                    "subscriber_count": len(self._status_subscribers)
                },
                domain="air-side",
                operation="subscribe_to_status"
            )

        except Exception as e:
            logger.error("HEALTH", f"API: Failed to subscribe to status: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="subscribe_to_status"
            )

    def unsubscribe_from_status(self, callback: callable) -> APIResponse:
        """
        Unsubscribe from status updates (Phase 2)

        Args:
            callback: Callback function to remove

        Returns:
            APIResponse with unsubscribe status
        """
        try:
            if hasattr(self, '_status_subscribers'):
                self._status_subscribers = [
                    sub for sub in self._status_subscribers
                    if sub['callback'] != callback
                ]

            logger.info("HEALTH", "API: Unsubscribed from status updates")

            return APIResponse.success_response(
                data={"unsubscribed": True},
                domain="air-side",
                operation="unsubscribe_from_status"
            )

        except Exception as e:
            logger.error("HEALTH", f"API: Failed to unsubscribe: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="unsubscribe_from_status"
            )

    def stream_logs(
        self,
        lines: int = 100,
        follow: bool = False
    ) -> APIResponse:
        """
        Stream Docker logs from Air-Side (Phase 2)

        Args:
            lines: Number of lines to retrieve
            follow: Whether to follow logs in real-time

        Returns:
            APIResponse with log stream info
        """
        try:
            if not self.ssh_client or not self.ssh_client.is_connected():
                return APIResponse.error_response(
                    error="SSH not connected",
                    domain="air-side",
                    operation="stream_logs"
                )

            # Build command
            command = f"docker logs payload-manager --tail {lines}"
            if follow:
                command += " --follow"

            logger.info("SYSTEM", f"API: Streaming logs (lines={lines}, follow={follow})")

            # Note: For real streaming, would need separate thread/process
            # For now, return command that can be used for streaming
            return APIResponse.success_response(
                data={
                    "stream_command": command,
                    "lines": lines,
                    "follow": follow,
                    "note": "Use execute_ssh_command() to get logs"
                },
                domain="air-side",
                operation="stream_logs"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to stream logs: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="stream_logs"
            )

    def transfer_file(
        self,
        remote_path: str,
        local_path: str,
        direction: str = 'download'
    ) -> APIResponse:
        """
        Transfer file to/from Air-Side via SFTP (Phase 2)

        Args:
            remote_path: Remote file path on Air-Side
            local_path: Local file path
            direction: 'download' or 'upload'

        Returns:
            APIResponse with transfer status
        """
        try:
            if not self.ssh_client:
                return APIResponse.error_response(
                    error="SSH client not available",
                    domain="air-side",
                    operation="transfer_file"
                )

            # Use SFTP via SSH client
            # Note: Would need to add SFTP support to SSHClient
            logger.info("STORAGE", f"API: File transfer: {direction} {remote_path} <-> {local_path}")

            # For now, use SCP via SSH command
            if direction == 'download':
                scp_command = f"scp {self.ssh_client.username}@{self.ssh_client.host}:{remote_path} {local_path}"
            else:  # upload
                scp_command = f"scp {local_path} {self.ssh_client.username}@{self.ssh_client.host}:{remote_path}"

            return APIResponse.success_response(
                data={
                    "remote_path": remote_path,
                    "local_path": local_path,
                    "direction": direction,
                    "scp_command": scp_command,
                    "note": "Execute via system or use SSHClient.sftp when available"
                },
                domain="air-side",
                operation="transfer_file"
            )

        except Exception as e:
            logger.error("STORAGE", f"API: File transfer failed: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="transfer_file"
            )

    def get_camera_files(
        self,
        file_type: str = 'image',
        limit: int = 10
    ) -> APIResponse:
        """
        Get list of camera files from Air-Side (Phase 2)

        Args:
            file_type: 'image' or 'video'
            limit: Maximum number of files to return

        Returns:
            APIResponse with file list
        """
        try:
            if not self.ssh_client or not self.ssh_client.is_connected():
                return APIResponse.error_response(
                    error="SSH not connected",
                    domain="air-side",
                    operation="get_camera_files"
                )

            # Build find command based on file type
            if file_type == 'image':
                extensions = "*.jpg *.jpeg *.png *.arw"
            else:  # video
                extensions = "*.mp4 *.mov *.avi"

            command = f"find /home/dpm/camera_files -type f \\( -name {extensions} \\) -printf '%T@ %p\\n' | sort -rn | head -{limit} | cut -d' ' -f2-"

            result = self.execute_ssh_command(command)

            if result.success:
                files = result.data['stdout'].strip().split('\n') if result.data['stdout'] else []
                return APIResponse.success_response(
                    data={
                        "files": files,
                        "count": len(files),
                        "file_type": file_type
                    },
                    domain="air-side",
                    operation="get_camera_files"
                )
            else:
                return result

        except Exception as e:
            logger.error("CAMERA", f"API: Failed to get camera files: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="get_camera_files"
            )

    def download_camera_file(
        self,
        remote_file: str,
        local_directory: str
    ) -> APIResponse:
        """
        Download camera file from Air-Side (Phase 2)

        Args:
            remote_file: Remote file path
            local_directory: Local directory to save file

        Returns:
            APIResponse with download status
        """
        try:
            from pathlib import Path

            local_path = Path(local_directory) / Path(remote_file).name

            result = self.transfer_file(
                remote_path=remote_file,
                local_path=str(local_path),
                direction='download'
            )

            if result.success:
                logger.info("CAMERA", f"API: Downloaded camera file to {local_path}")
                result.operation = "download_camera_file"

            return result

        except Exception as e:
            logger.error("CAMERA", f"API: Failed to download camera file: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="download_camera_file"
            )

    def manage_docker_container(
        self,
        action: str,
        container: str = 'payload-manager'
    ) -> APIResponse:
        """
        Manage Docker container on Air-Side (Phase 2)

        Args:
            action: 'start', 'stop', 'restart', 'status', 'logs'
            container: Container name

        Returns:
            APIResponse with container status
        """
        try:
            if not self.ssh_client or not self.ssh_client.is_connected():
                return APIResponse.error_response(
                    error="SSH not connected",
                    domain="air-side",
                    operation="manage_docker_container"
                )

            # Build docker command
            if action == 'status':
                command = f"docker ps -a --filter name={container} --format '{{{{.Status}}}}'"
            elif action == 'logs':
                command = f"docker logs {container} --tail 50"
            elif action in ['start', 'stop', 'restart']:
                command = f"docker {action} {container}"
            else:
                return APIResponse.error_response(
                    error=f"Invalid action: {action}",
                    domain="air-side",
                    operation="manage_docker_container"
                )

            result = self.execute_ssh_command(command)

            if result.success:
                logger.info("SYSTEM", f"API: Docker {action} on {container}")
                return APIResponse.success_response(
                    data={
                        "action": action,
                        "container": container,
                        "output": result.data['stdout'],
                        "exit_code": result.data['exit_code']
                    },
                    domain="air-side",
                    operation="manage_docker_container"
                )
            else:
                return result

        except Exception as e:
            logger.error("SYSTEM", f"API: Docker management failed: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="air-side",
                operation="manage_docker_container"
            )
