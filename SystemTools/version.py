"""
DPM Diagnostic Tool - Version Information
Centralized version, build date, and build information
Loads from version.json
"""

import json
import datetime
from pathlib import Path

# Load version data from JSON
_version_file = Path(__file__).parent / "version.json"
try:
    with open(_version_file, 'r') as f:
        _version_data = json.load(f)
except FileNotFoundError:
    # Fallback if JSON doesn't exist
    _version_data = {
        "version": "1.0.0",
        "version_name": "DPM Management System",
        "build_date": "Unknown",
        "python_required": "3.x",
        "platform": "Linux",
        "protocol_version": "1.0.0",
        "phase_status": {}
    }

# Version Information (loaded from JSON)
VERSION = _version_data["version"]
VERSION_NAME = _version_data["version_name"]
BUILD_DATE = _version_data["build_date"]

# Build metadata (loaded from JSON)
BUILD_INFO = {
    "version": VERSION,
    "version_name": VERSION_NAME,
    "build_date": BUILD_DATE,
    "python_required": _version_data.get("python_required", "3.x"),
    "platform": _version_data.get("platform", "Linux"),
    "protocol_version": _version_data.get("protocol_version", "1.0.0"),
}

# Phase completion status (loaded from JSON)
PHASE_STATUS = _version_data.get("phase_status", {})


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
