"""
SSH Client for DPM Diagnostic Tool
Connects to Air-Side Raspberry Pi for remote command execution and log viewing
"""

import paramiko
import threading
from typing import Optional, Callable
from utils.logger import logger


class SSHClient:
    """SSH client for Air-Side connection"""

    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

        self.client: Optional[paramiko.SSHClient] = None
        self.connected = False

        # Callbacks
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    def connect(self) -> bool:
        """Connect to Air-Side via SSH"""
        try:
            logger.info(f"SSH: Connecting to {self.username}@{self.host}:{self.port}...")

            # Create SSH client
            self.client = paramiko.SSHClient()

            # Auto-add host key (not secure for production, but OK for internal tool)
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )

            self.connected = True
            logger.info(f"SSH: Connected to {self.host}")

            if self.on_connected:
                self.on_connected()

            return True

        except paramiko.AuthenticationException:
            error_msg = "SSH authentication failed - check username/password"
            logger.error(f"SSH: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            return False

        except paramiko.SSHException as e:
            error_msg = f"SSH connection error: {e}"
            logger.error(f"SSH: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            return False

        except Exception as e:
            error_msg = f"Failed to connect: {e}"
            logger.error(f"SSH: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            return False

    def disconnect(self):
        """Disconnect from Air-Side"""
        if self.client:
            try:
                logger.info("SSH: Disconnecting...")
                self.client.close()
                self.connected = False
                logger.info("SSH: Disconnected")

                if self.on_disconnected:
                    self.on_disconnected()

            except Exception as e:
                logger.error(f"SSH: Error during disconnect: {e}")

        self.client = None

    def execute_command(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """
        Execute command on Air-Side

        Returns:
            (exit_code, stdout, stderr)
        """
        if not self.connected or not self.client:
            logger.error("SSH: Not connected")
            return (-1, "", "Not connected to Air-Side")

        try:
            logger.debug(f"SSH: Executing command: {command}")

            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)

            # Read output
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')

            logger.debug(f"SSH: Command exit code: {exit_code}")

            return (exit_code, stdout_str, stderr_str)

        except Exception as e:
            error_msg = f"Command execution failed: {e}"
            logger.error(f"SSH: {error_msg}")
            return (-1, "", str(e))

    def get_docker_logs(self, container: str = "payload-manager",
                        tail: Optional[int] = None,
                        since: Optional[str] = None) -> tuple[int, str, str]:
        """
        Get Docker container logs (one-time fetch)

        Args:
            container: Container name (default: payload-manager)
            tail: Number of lines from end (e.g., 100)
            since: Time duration (e.g., "5m", "1h")

        Returns:
            (exit_code, stdout, stderr)
        """
        command = f"docker logs {container}"

        if tail:
            command += f" --tail {tail}"

        if since:
            command += f" --since {since}"

        return self.execute_command(command, timeout=60)

    def follow_docker_logs(self, container: str = "payload-manager",
                          tail: Optional[int] = None,
                          on_log_line: Optional[Callable[[str], None]] = None,
                          stop_event: Optional[threading.Event] = None):
        """
        Follow Docker container logs in real-time (like docker logs -f)

        Args:
            container: Container name (default: payload-manager)
            tail: Number of initial lines to show
            on_log_line: Callback for each new log line
            stop_event: Event to signal stop following

        This runs in a loop until stop_event is set
        """
        if not self.connected or not self.client:
            logger.error("SSH: Not connected")
            return

        try:
            # Build command
            command = f"docker logs -f {container}"
            if tail:
                command += f" --tail {tail}"

            logger.info(f"SSH: Starting log follow: {command}")

            # Execute command with channel for streaming
            transport = self.client.get_transport()
            channel = transport.open_session()
            channel.exec_command(command)

            # Read output continuously
            while not (stop_event and stop_event.is_set()):
                # Check if channel has data ready
                if channel.recv_ready():
                    # Read available data
                    data = channel.recv(4096).decode('utf-8', errors='replace')
                    if data and on_log_line:
                        # Split by lines and call callback for each
                        for line in data.splitlines():
                            if line.strip():
                                on_log_line(line)

                # Also check stderr
                if channel.recv_stderr_ready():
                    data = channel.recv_stderr(4096).decode('utf-8', errors='replace')
                    if data and on_log_line:
                        for line in data.splitlines():
                            if line.strip():
                                on_log_line(line)

                # Check if channel closed
                if channel.exit_status_ready():
                    break

                # Small delay to prevent CPU spinning
                threading.Event().wait(0.1)

            # Clean up
            channel.close()
            logger.info("SSH: Stopped following logs")

        except Exception as e:
            logger.error(f"SSH: Error following logs: {e}")
            if on_log_line:
                on_log_line(f"ERROR: {e}")

    def is_connected(self) -> bool:
        """Check if SSH is connected"""
        return self.connected and self.client is not None

    def connect_async(self) -> threading.Thread:
        """Connect to SSH in background thread"""
        def connect_thread():
            self.connect()

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
        return thread
