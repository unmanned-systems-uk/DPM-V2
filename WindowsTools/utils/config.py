"""
Configuration Manager for DPM Diagnostic Tool
Handles settings persistence and defaults
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


class ConfigManager:
    """Singleton configuration manager"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.config_file = Path(__file__).parent.parent / "config.json"
        self._config = self._get_defaults()
        self.load()

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "network": {
                "air_side_ip": "10.0.1.53",
                "tcp_port": 5000,
                "udp_status_port": 5001,
                "udp_heartbeat_port": 5002,
                "h16_ip": "10.0.1.92",
                "connection_timeout_ms": 5000,
                "retry_attempts": 3
            },
            "ssh": {
                "host": "10.0.1.53",
                "port": 22,
                "username": "dpm",
                "password": "",  # Will be set by user
                "save_password": False
            },
            "ui": {
                "auto_connect_on_startup": True,
                "auto_refresh_camera_interval_ms": 5000,
                "auto_refresh_system_interval_ms": 5000,
                "theme": "light",  # "light" or "dark"
                "font_size": 10,
                "enable_audio_alerts": False
            },
            "data": {
                "log_directory": str(Path(__file__).parent.parent / "logs"),
                "message_capture_file": str(Path(__file__).parent.parent / "logs" / "messages.json"),
                "auto_save_settings": True
            }
        }

    def load(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    self._merge_config(self._config, loaded)
                return True
        except Exception as e:
            print(f"Error loading config: {e}")
        return False

    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_config(self, base: dict, overlay: dict):
        """Recursively merge overlay into base"""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, section: str, key: str, default=None) -> Any:
        """Get configuration value"""
        try:
            return self._config.get(section, {}).get(key, default)
        except:
            return default

    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

        if self.get("data", "auto_save_settings", True):
            self.save()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})

    def set_section(self, section: str, values: Dict[str, Any]):
        """Set entire configuration section"""
        self._config[section] = values

        if self.get("data", "auto_save_settings", True):
            self.save()

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self._get_defaults()
        self.save()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()


# Global singleton instance
config = ConfigManager()
