"""
ADB Client for DPM Diagnostic Tool
Connects to H16 Android device for diagnostics and log viewing
"""

import subprocess
import threading
from typing import Optional, Callable
from utils.protocol_logger import logger


class ADBClient:
    """ADB client for H16 Android device connection"""

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADB client

        Args:
            device_id: Specific device ID (optional, will auto-detect if None)
        """
        self.device_id = device_id
        self.connected = False

        # Callbacks
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    def _run_adb_command(self, command: list[str], timeout: int = 10) -> tuple[int, str, str]:
        """
        Run an ADB command

        Args:
            command: Command as list (e.g., ['adb', 'devices'])
            timeout: Timeout in seconds

        Returns:
            (exit_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (-1, "", f"Command timed out after {timeout}s")
        except FileNotFoundError:
            return (-1, "", "ADB not found - please install Android SDK Platform Tools")
        except Exception as e:
            return (-1, "", str(e))

    def is_adb_available(self) -> bool:
        """Check if ADB is available on the system"""
        exit_code, stdout, stderr = self._run_adb_command(['adb', 'version'], timeout=5)
        return exit_code == 0

    def get_devices(self) -> list[str]:
        """
        Get list of connected Android devices

        Returns:
            List of device IDs
        """
        exit_code, stdout, stderr = self._run_adb_command(['adb', 'devices'])

        if exit_code != 0:
            logger.error("NETWORK", f"ADB: Failed to get devices: {stderr}")
            return []

        # Parse output
        # Format:
        # List of devices attached
        # device_id    device
        devices = []
        for line in stdout.splitlines()[1:]:  # Skip header
            line = line.strip()
            if line and '\t' in line:
                device_id, status = line.split('\t', 1)
                if status == 'device':  # Only include properly connected devices
                    devices.append(device_id)

        return devices

    def connect(self, device_id: Optional[str] = None) -> bool:
        """
        Connect to H16 Android device

        Args:
            device_id: Specific device ID (optional, will use first available if None)
                      Can be network address (e.g., "10.0.1.92:5555") or USB device ID

        Returns:
            True if connected successfully
        """
        try:
            logger.info("NETWORK", "ADB: Checking connection...")

            # Check if ADB is available
            if not self.is_adb_available():
                error_msg = "ADB not found - please install Android SDK Platform Tools"
                logger.error("NETWORK", f"ADB: {error_msg}")
                if self.on_error:
                    self.on_error(error_msg)
                return False

            # If device_id is provided and looks like a network address (contains colon),
            # first establish network connection with adb connect
            if device_id and ':' in device_id:
                logger.info("NETWORK", f"ADB: Network device detected, connecting to {device_id}...")
                exit_code, stdout, stderr = self._run_adb_command(['adb', 'connect', device_id], timeout=10)

                if exit_code != 0:
                    error_msg = f"Failed to connect to network device {device_id}: {stderr}"
                    logger.error("NETWORK", f"ADB: {error_msg}")
                    if self.on_error:
                        self.on_error(error_msg)
                    return False

                # Check if connection succeeded
                if "connected" not in stdout.lower() and "already connected" not in stdout.lower():
                    error_msg = f"Network connection failed: {stdout}"
                    logger.error("NETWORK", f"ADB: {error_msg}")
                    if self.on_error:
                        self.on_error(error_msg)
                    return False

                logger.info("NETWORK", f"ADB: Network connection established: {stdout.strip()}")
                self.device_id = device_id

            # Get available devices
            devices = self.get_devices()

            if not devices:
                error_msg = "No Android devices connected via ADB"
                logger.warning("NETWORK", f"ADB: {error_msg}")
                if self.on_error:
                    self.on_error(error_msg)
                return False

            # Select device
            if device_id:
                if device_id not in devices:
                    error_msg = f"Device {device_id} not found in device list. Available: {devices}"
                    logger.error("NETWORK", f"ADB: {error_msg}")
                    if self.on_error:
                        self.on_error(error_msg)
                    return False
                self.device_id = device_id
            else:
                # Use first available device
                self.device_id = devices[0]

            # Temporarily mark as connected to allow test command to run
            self.connected = True

            # Test connection with a simple command
            exit_code, stdout, stderr = self.execute_command('echo ADB_TEST')

            if exit_code == 0 and 'ADB_TEST' in stdout:
                logger.info("NETWORK", f"ADB: Connected to device {self.device_id}")

                if self.on_connected:
                    self.on_connected()

                return True
            else:
                # Test failed, mark as not connected
                self.connected = False
                error_msg = f"Failed to communicate with device {self.device_id}"
                logger.error("NETWORK", f"ADB: {error_msg}")
                if self.on_error:
                    self.on_error(error_msg)
                return False

        except Exception as e:
            error_msg = f"Connection failed: {e}"
            logger.error("NETWORK", f"ADB: {error_msg}")
            if self.on_error:
                self.on_error(error_msg)
            return False

    def disconnect(self):
        """Disconnect from H16 (no actual disconnect needed for ADB)"""
        self.connected = False
        logger.info("NETWORK", "ADB: Disconnected")

        if self.on_disconnected:
            self.on_disconnected()

    def execute_command(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """
        Execute shell command on H16

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds

        Returns:
            (exit_code, stdout, stderr)
        """
        if not self.connected:
            logger.error("NETWORK", "ADB: Not connected")
            return (-1, "", "Not connected to device")

        # Build ADB command
        adb_cmd = ['adb']
        if self.device_id:
            adb_cmd.extend(['-s', self.device_id])
        adb_cmd.extend(['shell', command])

        logger.debug("NETWORK", f"ADB: Executing command: {command}")

        return self._run_adb_command(adb_cmd, timeout=timeout)

    def get_device_info(self) -> dict:
        """
        Get device information

        Returns:
            Dictionary with device info (model, android_version, etc.)
        """
        if not self.connected:
            return {}

        info = {}

        # Get model
        exit_code, stdout, stderr = self.execute_command('getprop ro.product.model')
        if exit_code == 0:
            info['model'] = stdout.strip()

        # Get Android version
        exit_code, stdout, stderr = self.execute_command('getprop ro.build.version.release')
        if exit_code == 0:
            info['android_version'] = stdout.strip()

        # Get device name
        exit_code, stdout, stderr = self.execute_command('getprop ro.product.device')
        if exit_code == 0:
            info['device_name'] = stdout.strip()

        # Get serial number
        if self.device_id:
            info['serial'] = self.device_id

        return info

    def get_logcat(self, filter_tag: Optional[str] = None,
                    tail: Optional[int] = None) -> tuple[int, str, str]:
        """
        Get logcat output (one-time fetch)

        Args:
            filter_tag: Filter by tag (e.g., "NetworkClient")
            tail: Number of lines from end

        Returns:
            (exit_code, stdout, stderr)
        """
        command = 'logcat -d'  # -d = dump and exit

        if tail:
            command += f' -t {tail}'

        if filter_tag:
            command += f' -s {filter_tag}'

        return self.execute_command(command, timeout=60)

    def clear_logcat(self) -> bool:
        """Clear logcat buffer"""
        exit_code, stdout, stderr = self.execute_command('logcat -c')
        return exit_code == 0

    def is_app_running(self, package_name: str) -> bool:
        """
        Check if an app is running

        Args:
            package_name: Package name (e.g., "com.uksystems.payloadmanager")

        Returns:
            True if app is running
        """
        if not self.connected:
            return False

        exit_code, stdout, stderr = self.execute_command(f'pidof {package_name}')
        return exit_code == 0 and stdout.strip() != ''

    def is_connected(self) -> bool:
        """Check if ADB is connected"""
        return self.connected and self.device_id is not None

    def connect_async(self) -> threading.Thread:
        """Connect to ADB in background thread"""
        def connect_thread():
            self.connect()

        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
        return thread

    def get_network_info(self) -> dict:
        """
        Get network information from H16

        Returns:
            Dictionary with IP addresses, WiFi status, etc.
        """
        if not self.connected:
            return {}

        info = {}

        # Get WiFi IP address
        exit_code, stdout, stderr = self.execute_command('ip addr show wlan0 | grep "inet " | awk \'{print $2}\' | cut -d/ -f1')
        if exit_code == 0 and stdout.strip():
            info['wifi_ip'] = stdout.strip()

        # Get WiFi SSID
        exit_code, stdout, stderr = self.execute_command('dumpsys wifi | grep "mWifiInfo SSID" | awk \'{print $4}\'')
        if exit_code == 0 and stdout.strip():
            info['wifi_ssid'] = stdout.strip().strip('"')

        return info

    def ping_host(self, host: str, count: int = 3) -> tuple[bool, float]:
        """
        Ping a host from H16

        Args:
            host: IP address or hostname
            count: Number of pings

        Returns:
            (success, avg_latency_ms)
        """
        if not self.connected:
            return (False, 0.0)

        exit_code, stdout, stderr = self.execute_command(f'ping -c {count} {host}', timeout=count + 5)

        if exit_code != 0:
            return (False, 0.0)

        # Parse output for average latency
        # Example: rtt min/avg/max/mdev = 1.234/5.678/9.012/2.345 ms
        for line in stdout.splitlines():
            if 'rtt min/avg/max' in line or 'round-trip min/avg/max' in line:
                try:
                    # Extract avg value
                    parts = line.split('=')[1].strip().split('/')
                    avg_latency = float(parts[1])
                    return (True, avg_latency)
                except (IndexError, ValueError):
                    pass

        # If we got here, parsing failed but ping succeeded
        return (True, 0.0)
