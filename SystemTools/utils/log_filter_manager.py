"""
LogFilterManager - Dynamic log filter management from JSON configuration

WHO: CC-Dev-Tools
Issue: #147 - JSON-Based Dynamic Filter System
Purpose: Eliminate freeze bug (#146) and provide better filter UX
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class LogFilterManager:
    """Manages dynamic log filter labels and presets from JSON configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LogFilterManager

        Args:
            config_path: Path to log_filter_labels.json (default: SystemTools/config/log_filter_labels.json)
        """
        if config_path is None:
            # Default path relative to SystemTools directory
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "log_filter_labels.json"

        self.config_path = Path(config_path)
        self.config = {}
        self.load()

    def load(self) -> bool:
        """
        Load filter configuration from JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            print(f"ERROR: Failed to load filter config from {self.config_path}: {e}")
            self.config = self._get_default_config()
            return False

    def refresh(self) -> bool:
        """
        Refresh filter configuration from disk

        Returns:
            True if successful, False otherwise
        """
        return self.load()

    def get_log_contexts(self) -> List[Dict]:
        """
        Get list of log context definitions

        Returns:
            List of context dicts with label, description, color, enabled, priority
        """
        contexts = self.config.get('log_contexts', [])
        # Filter enabled only and sort by priority
        enabled_contexts = [c for c in contexts if c.get('enabled', True)]
        return sorted(enabled_contexts, key=lambda x: x.get('priority', 999))

    def get_log_levels(self) -> List[Dict]:
        """
        Get list of log level definitions

        Returns:
            List of level dicts with label, description, color, enabled, priority
        """
        levels = self.config.get('log_levels', [])
        # Filter enabled only and sort by priority
        enabled_levels = [l for l in levels if l.get('enabled', True)]
        return sorted(enabled_levels, key=lambda x: x.get('priority', 999))

    def get_filter_presets(self) -> List[Dict]:
        """
        Get list of filter preset definitions

        Returns:
            List of preset dicts with name, description, contexts, levels, logic
        """
        return self.config.get('filter_presets', [])

    def get_ui_settings(self) -> Dict:
        """
        Get UI configuration settings

        Returns:
            Dict with UI settings
        """
        return self.config.get('ui_settings', {
            'default_logic': 'OR',
            'auto_refresh_on_tab_open': True,
            'show_count_badges': True,
            'max_visible_buttons': 15,
            'button_style': 'pill',
            'enable_tooltips': True
        })

    def get_refresh_triggers(self) -> Dict:
        """
        Get refresh trigger configuration

        Returns:
            Dict with refresh trigger settings
        """
        return self.config.get('refresh_triggers', {
            'app_start': True,
            'tab_open': True,
            'user_button_click': True,
            'file_watch': False,
            'interval_seconds': 0
        })

    def apply_preset(self, preset_name: str) -> Dict:
        """
        Get filter configuration for a named preset

        Args:
            preset_name: Name of the preset

        Returns:
            Dict with 'contexts', 'levels', 'logic' or empty dict if not found
        """
        presets = self.get_filter_presets()
        for preset in presets:
            if preset.get('name') == preset_name:
                return {
                    'contexts': preset.get('contexts', []),
                    'levels': preset.get('levels', []),
                    'logic': preset.get('logic', 'OR')
                }
        return {}

    def _get_default_config(self) -> Dict:
        """
        Get default configuration if JSON file fails to load

        Returns:
            Minimal default configuration
        """
        return {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'log_contexts': [
                {'label': 'COMMAND', 'description': 'Command processing', 'color': '#4CAF50', 'enabled': True, 'priority': 1},
                {'label': 'NETWORK', 'description': 'Network events', 'color': '#2196F3', 'enabled': True, 'priority': 2},
                {'label': 'CAMERA', 'description': 'Camera operations', 'color': '#9C27B0', 'enabled': True, 'priority': 3},
                {'label': 'SYSTEM', 'description': 'System operations', 'color': '#607D8B', 'enabled': True, 'priority': 4},
            ],
            'log_levels': [
                {'label': 'ERROR', 'description': 'Error messages', 'color': '#F44336', 'enabled': True, 'priority': 1},
                {'label': 'WARNING', 'description': 'Warning messages', 'color': '#FF9800', 'enabled': True, 'priority': 2},
                {'label': 'INFO', 'description': 'Info messages', 'color': '#2196F3', 'enabled': True, 'priority': 3},
                {'label': 'DEBUG', 'description': 'Debug messages', 'color': '#9E9E9E', 'enabled': True, 'priority': 4},
            ],
            'filter_presets': [
                {'name': 'Everything', 'description': 'Show all logs', 'contexts': [], 'levels': [], 'logic': 'OR'},
            ],
            'ui_settings': {
                'default_logic': 'OR',
                'auto_refresh_on_tab_open': True,
                'show_count_badges': False,
                'max_visible_buttons': 15,
                'button_style': 'pill',
                'enable_tooltips': True
            },
            'refresh_triggers': {
                'app_start': True,
                'tab_open': True,
                'user_button_click': True,
                'file_watch': False,
                'interval_seconds': 0
            }
        }


# Example usage and testing
if __name__ == "__main__":
    print("LogFilterManager Test")
    print("=" * 50)

    manager = LogFilterManager()

    print(f"\nContexts ({len(manager.get_log_contexts())}):")
    for ctx in manager.get_log_contexts():
        print(f"  [{ctx['label']}] {ctx['description']} (color: {ctx['color']})")

    print(f"\nLevels ({len(manager.get_log_levels())}):")
    for lvl in manager.get_log_levels():
        print(f"  [{lvl['label']}] {lvl['description']} (color: {lvl['color']})")

    print(f"\nPresets ({len(manager.get_filter_presets())}):")
    for preset in manager.get_filter_presets():
        print(f"  [{preset['name']}] {preset['description']}")
        print(f"    Contexts: {preset['contexts']}, Levels: {preset['levels']}, Logic: {preset['logic']}")

    print(f"\nUI Settings:")
    for key, value in manager.get_ui_settings().items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 50)
    print("LogFilterManager Test Complete")
