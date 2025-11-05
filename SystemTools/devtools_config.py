"""
DevTools Configuration System
Manages development vs deployment modes for the diagnostic tools

Modes:
- Development: Full GUI, verbose logging, all debug features enabled
- Deployment: Optimized, CLI-only option, minimal logging, production settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class DevMode(Enum):
    """DevTools operation modes"""
    DEVELOPMENT = "development"
    DEPLOYMENT = "deployment"


class UIMode(Enum):
    """User interface modes"""
    GUI = "gui"
    CLI = "cli"
    AUTO = "auto"  # Auto-detect based on environment


class DevToolsConfig:
    """DevTools configuration manager with mode support"""

    # Default configuration
    DEFAULT_CONFIG = {
        "mode": DevMode.DEVELOPMENT.value,
        "ui_mode": UIMode.AUTO.value,
        "development": {
            "verbose_logging": True,
            "debug_panels": True,
            "auto_reload": True,
            "show_raw_data": True,
            "enable_mock_data": True,
            "log_level": "DEBUG",
            "save_all_logs": True,
            "show_performance_stats": True,
            "enable_remote_debug": True,
            "max_log_size_mb": 100
        },
        "deployment": {
            "verbose_logging": False,
            "debug_panels": False,
            "auto_reload": False,
            "show_raw_data": False,
            "enable_mock_data": False,
            "log_level": "INFO",
            "save_all_logs": False,
            "show_performance_stats": False,
            "enable_remote_debug": False,
            "max_log_size_mb": 10
        },
        "cli_options": {
            "colored_output": True,
            "compact_display": True,
            "auto_connect": True,
            "show_banner": False,
            "interactive_mode": True
        },
        "gui_options": {
            "theme": "modern",
            "window_size": [1400, 900],
            "auto_arrange": True,
            "show_tooltips": True,
            "enable_animations": True
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize DevTools configuration

        Args:
            config_path: Optional path to config file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.DEFAULT_CONFIG.copy()
        self.current_mode = DevMode.DEVELOPMENT
        self.ui_mode = UIMode.AUTO
        self.load()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return str(Path(__file__).parent / "devtools.json")

    def load(self) -> bool:
        """Load configuration from file

        Returns:
            bool: True if loaded successfully
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)

                # Set current mode
                mode_str = self.config.get("mode", DevMode.DEVELOPMENT.value)
                self.current_mode = DevMode(mode_str)

                # Set UI mode
                ui_str = self.config.get("ui_mode", UIMode.AUTO.value)
                self.ui_mode = UIMode(ui_str)

                print(f"DevTools config loaded: {self.current_mode.value} mode")
                return True

            except Exception as e:
                print(f"Error loading DevTools config: {e}")
                return False
        else:
            # Create default config file
            self.save()
            return True

    def save(self) -> bool:
        """Save current configuration to file

        Returns:
            bool: True if saved successfully
        """
        try:
            # Update mode in config
            self.config["mode"] = self.current_mode.value
            self.config["ui_mode"] = self.ui_mode.value

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving DevTools config: {e}")
            return False

    def set_mode(self, mode: DevMode) -> None:
        """Switch between development and deployment modes

        Args:
            mode: The mode to switch to
        """
        self.current_mode = mode
        print(f"Switched to {mode.value} mode")
        self.save()

    def set_ui_mode(self, ui_mode: UIMode) -> None:
        """Set UI mode (GUI/CLI/AUTO)

        Args:
            ui_mode: The UI mode to use
        """
        self.ui_mode = ui_mode
        print(f"UI mode set to {ui_mode.value}")
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value based on current mode

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        # First check mode-specific settings
        mode_config = self.config.get(self.current_mode.value, {})
        if key in mode_config:
            return mode_config[key]

        # Then check UI-specific settings
        if self.ui_mode == UIMode.CLI:
            cli_config = self.config.get("cli_options", {})
            if key in cli_config:
                return cli_config[key]
        elif self.ui_mode == UIMode.GUI:
            gui_config = self.config.get("gui_options", {})
            if key in gui_config:
                return gui_config[key]

        # Finally check top-level config
        return self.config.get(key, default)

    def get_mode_config(self) -> Dict[str, Any]:
        """Get all configuration for current mode

        Returns:
            dict: Mode-specific configuration
        """
        return self.config.get(self.current_mode.value, {})

    def is_development(self) -> bool:
        """Check if in development mode

        Returns:
            bool: True if in development mode
        """
        return self.current_mode == DevMode.DEVELOPMENT

    def is_deployment(self) -> bool:
        """Check if in deployment mode

        Returns:
            bool: True if in deployment mode
        """
        return self.current_mode == DevMode.DEPLOYMENT

    def should_use_gui(self) -> bool:
        """Determine if GUI should be used

        Returns:
            bool: True if GUI should be used
        """
        if self.ui_mode == UIMode.GUI:
            return True
        elif self.ui_mode == UIMode.CLI:
            return False
        else:  # AUTO mode
            # Check if we're in a terminal that supports GUI
            try:
                import tkinter
                return True
            except ImportError:
                return False

    def get_log_level(self) -> str:
        """Get appropriate log level for current mode

        Returns:
            str: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        return self.get("log_level", "INFO")

    def should_show_debug_info(self) -> bool:
        """Check if debug information should be shown

        Returns:
            bool: True if debug info should be shown
        """
        return self.get("verbose_logging", False) or self.get("show_raw_data", False)

    def __str__(self) -> str:
        """String representation of current configuration"""
        return (
            f"DevTools Config:\n"
            f"  Mode: {self.current_mode.value}\n"
            f"  UI: {self.ui_mode.value}\n"
            f"  Log Level: {self.get_log_level()}\n"
            f"  Debug Info: {self.should_show_debug_info()}\n"
            f"  GUI Enabled: {self.should_use_gui()}"
        )


# Global configuration instance
devtools_config = DevToolsConfig()


# Command-line argument parsing
def parse_args():
    """Parse command-line arguments for mode selection"""
    import argparse

    parser = argparse.ArgumentParser(
        description="DPM DevTools - Diagnostic and Testing Suite"
    )

    parser.add_argument(
        "--mode",
        choices=["development", "dev", "deployment", "deploy"],
        help="Set operation mode"
    )

    parser.add_argument(
        "--ui",
        choices=["gui", "cli", "auto"],
        help="Set UI mode"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )

    args = parser.parse_args()

    # Apply command-line settings
    if args.config:
        global devtools_config
        devtools_config = DevToolsConfig(args.config)

    if args.mode:
        mode = args.mode
        if mode in ["development", "dev"]:
            devtools_config.set_mode(DevMode.DEVELOPMENT)
        elif mode in ["deployment", "deploy"]:
            devtools_config.set_mode(DevMode.DEPLOYMENT)

    if args.ui:
        ui_map = {
            "gui": UIMode.GUI,
            "cli": UIMode.CLI,
            "auto": UIMode.AUTO
        }
        devtools_config.set_ui_mode(ui_map[args.ui])

    if args.verbose:
        # Override verbose logging
        mode_config = devtools_config.config.get(devtools_config.current_mode.value, {})
        mode_config["verbose_logging"] = True
        mode_config["log_level"] = "DEBUG"

    return args


if __name__ == "__main__":
    # Test configuration system
    args = parse_args()

    print("DevTools Configuration System")
    print("-" * 40)
    print(devtools_config)
    print("-" * 40)

    # Show mode-specific settings
    print(f"\n{devtools_config.current_mode.value.title()} Mode Settings:")
    for key, value in devtools_config.get_mode_config().items():
        print(f"  {key}: {value}")

    # Test mode switching
    print("\nTesting mode switch...")
    if devtools_config.is_development():
        print("Currently in DEVELOPMENT mode")
        devtools_config.set_mode(DevMode.DEPLOYMENT)
        print(f"Switched to {devtools_config.current_mode.value}")
        devtools_config.set_mode(DevMode.DEVELOPMENT)
    else:
        print("Currently in DEPLOYMENT mode")