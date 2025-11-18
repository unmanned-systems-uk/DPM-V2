"""
DPM Diagnostic Tool - Version Information
Centralized version, build date, and build information
"""

import datetime
from pathlib import Path

# Version Information
VERSION = "1.11.0"
VERSION_NAME = "DPM Management System - JSON Filters, Config Mgmt, Testing"
BUILD_DATE = "2025-11-18"

# Build metadata
BUILD_INFO = {
    "version": VERSION,
    "version_name": VERSION_NAME,
    "build_date": BUILD_DATE,
    "python_required": "3.x",
    "platform": "Windows 11",
    "protocol_version": "1.1.0",  # Heartbeat spec version
}

# Phase completion status
PHASE_STATUS = {
    "phase_1": "Complete (100%) - Tri-Domain Log Aggregation",
    "phase_2": "Complete (100%) - GUI Integration",
    "phase_3": "Complete (100%) - Config Management (#115, #116)",
    "phase_4": "Complete (100%) - JSON Filter System (#147)",
    "phase_5": "Complete (100%) - Testing Enhancements (#149)",
    "overall_completion": "100%"
}


def get_version_string() -> str:
    """Get formatted version string"""
    return f"v{VERSION} ({VERSION_NAME})"


def get_build_info_string() -> str:
    """Get formatted build information"""
    return f"v{VERSION} - Built {BUILD_DATE}"


def get_full_version_info() -> dict:
    """Get complete version information as dictionary"""
    # Try to get file modification time as build time
    try:
        main_file = Path(__file__).parent / "main.py"
        if main_file.exists():
            mtime = datetime.datetime.fromtimestamp(main_file.stat().st_mtime)
            build_datetime = mtime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            build_datetime = f"{BUILD_DATE} 00:00:00"
    except:
        build_datetime = f"{BUILD_DATE} 00:00:00"

    return {
        **BUILD_INFO,
        "build_datetime": build_datetime,
        "phase_status": PHASE_STATUS
    }


# For quick access
__version__ = VERSION
__build_date__ = BUILD_DATE
