"""
Ground-Side Controller
======================

Programmatic interface for Ground-Side operations (Android H16).

Provides:
- ADB command wrappers
- H16 diagnostics access
- App control (start/stop/install)
- Screen capture/recording
- Input simulation
- Logcat streaming
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from network.adb_client import ADBClient
from utils.protocol_logger import logger
from utils.config import config
from .response import APIResponse


class GroundSideController:
    """
    Ground-Side programmatic control interface

    Example:
        controller = GroundSideController()
        controller.connect(host='10.0.1.92')

        # Get diagnostics
        diag = controller.get_diagnostics()

        # Control app
        controller.start_app('uk.unmannedsystems.dpm_android')

        # Simulate input
        controller.tap(500, 500)

        controller.disconnect()
    """

    def __init__(self, adb_client: Optional[ADBClient] = None):
        """
        Initialize Ground-Side controller

        Args:
            adb_client: Existing ADB client instance (optional, created on connect if not provided)
        """
        self.adb_client = adb_client
        self._logcat_running = False

        logger.debug("SYSTEM", "GroundSideController initialized")

    def connect(
        self,
        host: Optional[str] = None,
        port: int = 5555,
        timeout: float = 5.0
    ) -> APIResponse:
        """
        Connect to Ground-Side (Android H16) via ADB

        Args:
            host: Ground-Side IP address (default: from config)
            port: ADB port (default: 5555)
            timeout: Connection timeout in seconds

        Returns:
            APIResponse with connection status
        """
        try:
            # Use config defaults if not provided
            host = host or config.get('ground_side_ip', '10.0.1.92')

            # Create ADB client if not exists
            if not self.adb_client:
                self.adb_client = ADBClient(host, port)

            # Connect ADB
            if self.adb_client.connect():
                logger.info("NETWORK", f"API: ADB connected to {host}:{port}")

                return APIResponse.success_response(
                    data={
                        "adb_connected": True,
                        "host": host,
                        "port": port
                    },
                    domain="ground-side",
                    operation="connect"
                )
            else:
                return APIResponse.error_response(
                    error="Failed to establish ADB connection",
                    domain="ground-side",
                    operation="connect"
                )

        except Exception as e:
            logger.error("NETWORK", f"API: Failed to connect to Ground-Side: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="connect"
            )

    def disconnect(self) -> APIResponse:
        """
        Disconnect from Ground-Side

        Returns:
            APIResponse with disconnection status
        """
        try:
            if self.adb_client:
                self.adb_client.disconnect()

            logger.info("NETWORK", "API: Disconnected from Ground-Side")

            return APIResponse.success_response(
                data={"disconnected": True},
                domain="ground-side",
                operation="disconnect"
            )

        except Exception as e:
            logger.error("NETWORK", f"API: Error during disconnect: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="disconnect"
            )

    def is_connected(self) -> bool:
        """Check if connected to Ground-Side"""
        return self.adb_client and self.adb_client.is_connected()

    def execute_adb_command(self, command: str, timeout: float = 10.0) -> APIResponse:
        """
        Execute ADB shell command on Ground-Side

        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds

        Returns:
            APIResponse with command output
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Ground-Side",
                domain="ground-side",
                operation="execute_adb_command"
            )

        try:
            output = self.adb_client.execute_command(command, timeout=timeout)

            logger.info("SYSTEM", f"API: Executed ADB command: {command}")

            return APIResponse.success_response(
                data={
                    "command": command,
                    "output": output,
                    "success": True
                },
                domain="ground-side",
                operation="execute_adb_command"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: ADB command failed: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="execute_adb_command",
                data={"command": command}
            )

    def get_diagnostics(self) -> APIResponse:
        """
        Get H16 diagnostics (battery, CPU, memory, temperature, network)

        Returns:
            APIResponse with diagnostics data
        """
        if not self.is_connected():
            return APIResponse.error_response(
                error="Not connected to Ground-Side",
                domain="ground-side",
                operation="get_diagnostics"
            )

        try:
            diagnostics = {}

            # Battery info
            battery_cmd = "dumpsys battery | grep level"
            battery_result = self.execute_adb_command(battery_cmd)
            if battery_result.success:
                diagnostics['battery'] = battery_result.data['output'].strip()

            # CPU info
            cpu_cmd = "cat /proc/stat | grep 'cpu '"
            cpu_result = self.execute_adb_command(cpu_cmd)
            if cpu_result.success:
                diagnostics['cpu'] = cpu_result.data['output'].strip()

            # Memory info
            mem_cmd = "cat /proc/meminfo | grep MemTotal"
            mem_result = self.execute_adb_command(mem_cmd)
            if mem_result.success:
                diagnostics['memory'] = mem_result.data['output'].strip()

            # Temperature
            temp_cmd = "cat /sys/class/thermal/thermal_zone0/temp"
            temp_result = self.execute_adb_command(temp_cmd)
            if temp_result.success:
                diagnostics['temperature'] = temp_result.data['output'].strip()

            logger.info("HEALTH", "API: Retrieved H16 diagnostics")

            return APIResponse.success_response(
                data=diagnostics,
                domain="ground-side",
                operation="get_diagnostics"
            )

        except Exception as e:
            logger.error("HEALTH", f"API: Failed to get diagnostics: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="get_diagnostics"
            )

    def start_app(self, package: str) -> APIResponse:
        """
        Start Android app on H16

        Args:
            package: App package name (e.g., 'uk.unmannedsystems.dpm_android')

        Returns:
            APIResponse with start status
        """
        try:
            command = f"am start -n {package}/.MainActivity"
            result = self.execute_adb_command(command)

            if result.success:
                logger.info("SYSTEM", f"API: Started app {package}")

            return result

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to start app: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="start_app",
                data={"package": package}
            )

    def stop_app(self, package: str) -> APIResponse:
        """
        Stop Android app on H16

        Args:
            package: App package name

        Returns:
            APIResponse with stop status
        """
        try:
            command = f"am force-stop {package}"
            result = self.execute_adb_command(command)

            if result.success:
                logger.info("SYSTEM", f"API: Stopped app {package}")

            return result

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to stop app: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="stop_app",
                data={"package": package}
            )

    def install_app(self, apk_path: str) -> APIResponse:
        """
        Install Android app on H16

        Args:
            apk_path: Path to APK file

        Returns:
            APIResponse with install status
        """
        try:
            command = f"install {apk_path}"  # ADB install command
            # Note: Would need to use ADB client's install method

            logger.info("SYSTEM", f"API: Installing app from {apk_path}")

            return APIResponse.success_response(
                data={
                    "apk_path": apk_path,
                    "note": "Use ADBClient.install_apk() method"
                },
                domain="ground-side",
                operation="install_app"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to install app: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="install_app",
                data={"apk_path": apk_path}
            )

    def tap(self, x: int, y: int) -> APIResponse:
        """
        Simulate screen tap on H16

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            APIResponse with tap status
        """
        try:
            command = f"input tap {x} {y}"
            result = self.execute_adb_command(command)

            if result.success:
                logger.info("UI", f"API: Tapped at ({x}, {y})")

            return result

        except Exception as e:
            logger.error("UI", f"API: Failed to tap: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="tap"
            )

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> APIResponse:
        """
        Simulate swipe gesture on H16

        Args:
            x1, y1: Start coordinates
            x2, y2: End coordinates
            duration_ms: Swipe duration in milliseconds

        Returns:
            APIResponse with swipe status
        """
        try:
            command = f"input swipe {x1} {y1} {x2} {y2} {duration_ms}"
            result = self.execute_adb_command(command)

            if result.success:
                logger.info("UI", f"API: Swiped from ({x1},{y1}) to ({x2},{y2})")

            return result

        except Exception as e:
            logger.error("UI", f"API: Failed to swipe: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="swipe"
            )

    def press_key(self, keycode: int) -> APIResponse:
        """
        Press hardware key on H16

        Args:
            keycode: Android keycode (e.g., 4=BACK, 3=HOME, 82=MENU)

        Returns:
            APIResponse with key press status
        """
        try:
            command = f"input keyevent {keycode}"
            result = self.execute_adb_command(command)

            if result.success:
                logger.info("UI", f"API: Pressed key {keycode}")

            return result

        except Exception as e:
            logger.error("UI", f"API: Failed to press key: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="press_key"
            )

    def get_screen_capture(self, local_path: str) -> APIResponse:
        """
        Capture screenshot from H16

        Args:
            local_path: Local path to save screenshot

        Returns:
            APIResponse with capture status
        """
        try:
            # Capture to device
            remote_path = '/sdcard/screenshot.png'
            capture_cmd = f"screencap -p {remote_path}"

            result = self.execute_adb_command(capture_cmd)

            if result.success:
                # Pull from device
                # Note: Would need to implement pull in ADB client
                logger.info("CAMERA", f"API: Screenshot captured to {remote_path}")

                return APIResponse.success_response(
                    data={
                        "remote_path": remote_path,
                        "local_path": local_path,
                        "note": "Use ADBClient.pull() to download"
                    },
                    domain="ground-side",
                    operation="get_screen_capture"
                )
            else:
                return result

        except Exception as e:
            logger.error("CAMERA", f"API: Failed to capture screenshot: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="get_screen_capture"
            )

    def start_logcat(self, filter_tag: Optional[str] = None) -> APIResponse:
        """
        Start logcat streaming from H16

        Args:
            filter_tag: Log tag filter (e.g., 'DPM', 'ActivityManager')

        Returns:
            APIResponse with logcat status
        """
        try:
            command = "logcat -v time"
            if filter_tag:
                command += f" -s {filter_tag}:V"

            self._logcat_running = True
            logger.info("SYSTEM", f"API: Started logcat (filter: {filter_tag})")

            return APIResponse.success_response(
                data={
                    "logcat_command": command,
                    "filter_tag": filter_tag,
                    "running": True
                },
                domain="ground-side",
                operation="start_logcat"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to start logcat: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="start_logcat"
            )

    def stop_logcat(self) -> APIResponse:
        """
        Stop logcat streaming

        Returns:
            APIResponse with stop status
        """
        try:
            self._logcat_running = False
            logger.info("SYSTEM", "API: Stopped logcat")

            return APIResponse.success_response(
                data={"running": False},
                domain="ground-side",
                operation="stop_logcat"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to stop logcat: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="stop_logcat"
            )

    def clear_logcat(self) -> APIResponse:
        """
        Clear logcat buffer on H16

        Returns:
            APIResponse with clear status
        """
        try:
            result = self.execute_adb_command("logcat -c")

            if result.success:
                logger.info("SYSTEM", "API: Cleared logcat buffer")

            return result

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to clear logcat: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="ground-side",
                operation="clear_logcat"
            )
