"""
DPM Controller - Main API Entry Point
======================================

Top-level controller providing access to all DPM domains.

Usage:
    from api import DPMController

    # Create controller
    dpm = DPMController()

    # Access Air-Side
    result = dpm.air_side.connect()
    if result.success:
        status = dpm.air_side.get_status()
        print(status.data)

    # Access Ground-Side (future)
    # result = dpm.ground_side.connect()

    # Access SystemTools operations (future)
    # logs = dpm.system.export_logs()
"""

from typing import Optional
from pathlib import Path

from utils.protocol_logger import logger
from utils.config import config
from network.tcp_client import TCPClient
from network.ssh_client import SSHClient
from network.adb_client import ADBClient
from .air_side_controller import AirSideController
from .system_controller import SystemController
from .response import APIResponse


class DPMController:
    """
    Main DPM Remote Control API

    Provides programmatic access to all DPM domains:
    - Air-Side (Raspberry Pi 5 + PayloadManager)
    - Ground-Side (Android H16) - future
    - SystemTools (log aggregation, analytics) - future

    Example:
        dpm = DPMController()

        # Connect to Air-Side
        dpm.air_side.connect()

        # Send command
        result = dpm.air_side.send_command('camera.capture', {'quality': 95})
        if result.success:
            print("Capture initiated")
        else:
            print(f"Error: {result.error}")

        # Get status
        status = dpm.air_side.get_status()

        # Disconnect
        dpm.air_side.disconnect()
    """

    def __init__(
        self,
        tcp_client: Optional[TCPClient] = None,
        ssh_client: Optional[SSHClient] = None,
        adb_client: Optional[ADBClient] = None,
        log_queue = None,
        data_storage = None
    ):
        """
        Initialize DPM Controller

        Args:
            tcp_client: Existing TCP client (optional, creates on-demand if not provided)
            ssh_client: Existing SSH client (optional, creates on-demand if not provided)
            adb_client: Existing ADB client (optional, creates on-demand if not provided)
            log_queue: Log queue from DPM_Management_System (optional)
            data_storage: DataStorage instance (optional)
        """
        # Store clients (will be created on-demand in connect())
        self._tcp_client = tcp_client
        self._ssh_client = ssh_client
        self._adb_client = adb_client

        # Initialize domain controllers
        self._air_side = AirSideController(
            tcp_client=self._tcp_client,
            ssh_client=self._ssh_client
        )

        # SystemTools controller (Phase 4)
        self._system = SystemController(
            log_queue=log_queue,
            data_storage=data_storage
        )

        # Future: Ground-Side controller (Phase 3)
        # self._ground_side = GroundSideController(adb_client=self._adb_client)

        logger.info("SYSTEM", "DPMController initialized (API Mode)")

    @property
    def air_side(self) -> AirSideController:
        """Get Air-Side controller"""
        return self._air_side

    @property
    def system(self) -> SystemController:
        """Get SystemTools controller"""
        return self._system

    # Future properties:
    # @property
    # def ground_side(self) -> GroundSideController:
    #     """Get Ground-Side controller"""
    #     return self._ground_side

    def connect_all(
        self,
        air_side_ip: Optional[str] = None,
        ground_side_ip: Optional[str] = None
    ) -> APIResponse:
        """
        Connect to all domains

        Args:
            air_side_ip: Air-Side IP address (default: from config)
            ground_side_ip: Ground-Side IP address (default: from config)

        Returns:
            APIResponse with connection status for all domains
        """
        results = {}

        # Connect Air-Side
        air_result = self._air_side.connect(host=air_side_ip)
        results['air_side'] = air_result.to_dict()

        # Future: Connect Ground-Side
        # ground_result = self._ground_side.connect(host=ground_side_ip)
        # results['ground_side'] = ground_result.to_dict()

        # Check overall success
        all_success = air_result.success  # and ground_result.success

        if all_success:
            return APIResponse.success_response(
                data=results,
                domain="all",
                operation="connect_all"
            )
        else:
            return APIResponse.error_response(
                error="Failed to connect to one or more domains",
                domain="all",
                operation="connect_all",
                data=results
            )

    def disconnect_all(self) -> APIResponse:
        """
        Disconnect from all domains

        Returns:
            APIResponse with disconnection status
        """
        results = {}

        # Disconnect Air-Side
        air_result = self._air_side.disconnect()
        results['air_side'] = air_result.to_dict()

        # Future: Disconnect Ground-Side
        # ground_result = self._ground_side.disconnect()
        # results['ground_side'] = ground_result.to_dict()

        return APIResponse.success_response(
            data=results,
            domain="all",
            operation="disconnect_all"
        )

    def get_system_status(self) -> APIResponse:
        """
        Get status of all domains

        Returns:
            APIResponse with comprehensive system status
        """
        results = {
            'air_side': {
                'connected': self._air_side.is_connected()
            }
            # Future: Add Ground-Side and SystemTools status
        }

        return APIResponse.success_response(
            data=results,
            domain="all",
            operation="get_system_status"
        )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup connections"""
        self.disconnect_all()
