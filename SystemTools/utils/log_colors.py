"""
Log Color Configuration Utility
================================

Provides centralized color configuration for log viewers.
Maps rich terminal colors to Tkinter hex colors.

Reads from: config/log_aggregator.json
"""

import json
from pathlib import Path
from typing import Dict


# Rich color name to Tkinter hex color mapping
RICH_TO_HEX_MAP = {
    # Domain colors
    "blue": "#0080FF",      # Bright blue for AIR
    "magenta": "#FF00FF",   # Magenta for GROUND

    # Level colors (not in config but used in code)
    "red": "#FF0000",       # ERROR
    "orange": "#FFA500",    # WARNING
    "green": "#00FF00",     # INFO
    "grey": "#808080",      # DEBUG
    "gray": "#808080",      # DEBUG (alternate spelling)

    # Other colors
    "yellow": "#FFFF00",    # Search highlight
    "cyan": "#00FFFF",      # Timestamps
    "white": "#FFFFFF",     # Default
    "black": "#000000",     # Background/text
}

# Default level colors (can be overridden in config)
DEFAULT_LEVEL_COLORS = {
    "ERROR": "red",
    "WARNING": "orange",
    "INFO": "green",
    "DEBUG": "gray",
}


def load_log_aggregator_config() -> Dict:
    """Load log aggregator configuration from JSON file"""
    config_path = Path(__file__).parent.parent / "config" / "log_aggregator.json"

    if not config_path.exists():
        # Return defaults if config doesn't exist
        return {
            "display": {
                "colors": {
                    "AIR": "blue",
                    "GROUND": "magenta"
                }
            },
            "buffer": {
                "max_entries": 10000
            }
        }

    with open(config_path, 'r') as f:
        return json.load(f)


def get_domain_colors() -> Dict[str, str]:
    """Get domain colors from config (rich color names)"""
    config = load_log_aggregator_config()
    return config.get("display", {}).get("colors", {"AIR": "blue", "GROUND": "magenta"})


def get_domain_colors_hex() -> Dict[str, str]:
    """Get domain colors as hex values for Tkinter"""
    domain_colors = get_domain_colors()
    return {
        domain: RICH_TO_HEX_MAP.get(color.lower(), "#FFFFFF")
        for domain, color in domain_colors.items()
    }


def get_level_colors_hex() -> Dict[str, str]:
    """Get level colors as hex values for Tkinter"""
    config = load_log_aggregator_config()
    level_colors = config.get("display", {}).get("level_colors", DEFAULT_LEVEL_COLORS)

    return {
        level: RICH_TO_HEX_MAP.get(color.lower(), "#FFFFFF")
        for level, color in level_colors.items()
    }


def get_buffer_max_entries() -> int:
    """Get maximum buffer entries from config"""
    config = load_log_aggregator_config()
    return config.get("buffer", {}).get("max_entries", 10000)


def rich_to_hex(rich_color: str) -> str:
    """Convert rich color name to Tkinter hex color"""
    return RICH_TO_HEX_MAP.get(rich_color.lower(), "#FFFFFF")


def configure_tkinter_text_tags(text_widget, domain_colors: Dict[str, str] = None,
                                level_colors: Dict[str, str] = None):
    """
    Configure Tkinter Text widget color tags from configuration

    Args:
        text_widget: Tkinter Text widget
        domain_colors: Optional domain color overrides
        level_colors: Optional level color overrides
    """
    if domain_colors is None:
        domain_colors = get_domain_colors_hex()

    if level_colors is None:
        level_colors = get_level_colors_hex()

    # Configure domain tags
    for domain, color_hex in domain_colors.items():
        text_widget.tag_config(domain.lower(), foreground=color_hex)

    # Configure level tags
    if "ERROR" in level_colors:
        text_widget.tag_config("error", foreground=level_colors["ERROR"],
                             font=('Courier New', 9, 'bold'))

    if "WARNING" in level_colors:
        text_widget.tag_config("warning", foreground=level_colors["WARNING"],
                             font=('Courier New', 9))

    if "INFO" in level_colors:
        text_widget.tag_config("info", foreground=level_colors["INFO"])

    if "DEBUG" in level_colors:
        text_widget.tag_config("debug", foreground=level_colors["DEBUG"])

    # Search highlight (always yellow for visibility)
    text_widget.tag_config("highlight", background="#FFFF00", foreground="#000000")

    # Raise tag priorities (higher priority tags override lower ones)
    # Order: domain < level < highlight
    for domain in domain_colors.keys():
        text_widget.tag_raise(domain.lower())

    for level_tag in ["debug", "info", "warning", "error"]:
        text_widget.tag_raise(level_tag)

    text_widget.tag_raise("highlight")
