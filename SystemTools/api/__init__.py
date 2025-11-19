"""
DPM Remote Control API
=======================

Programmatic interface for DPM Management System - enables PM automation,
automated testing, and remote diagnostics.

Usage:
    from api import DPMController

    # Create controller instance
    controller = DPMController()

    # Access domain-specific controllers
    air_side = controller.air_side
    ground_side = controller.ground_side
    system = controller.system

    # Perform operations
    result = air_side.get_status()
    if result['success']:
        print(result['data'])
"""

from .controller import DPMController
from .air_side_controller import AirSideController
from .response import APIResponse

__all__ = ['DPMController', 'AirSideController', 'APIResponse']
