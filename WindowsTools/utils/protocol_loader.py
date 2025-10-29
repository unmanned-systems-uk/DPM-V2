"""
Protocol Loader for DPM Diagnostic Tool
Loads command and camera property definitions from JSON files
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProtocolLoader:
    """Loads and provides access to protocol definitions"""

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

        # Protocol files are in ../protocol/ relative to WindowsTools/
        protocol_dir = Path(__file__).parent.parent.parent / "protocol"

        self.commands_file = protocol_dir / "commands.json"
        self.properties_file = protocol_dir / "camera_properties.json"

        self.commands: Dict[str, Any] = {}
        self.properties: Dict[str, Any] = {}

        self.load()

    def load(self) -> bool:
        """Load protocol definitions from JSON files"""
        success = True

        # Load commands
        try:
            if self.commands_file.exists():
                with open(self.commands_file, 'r') as f:
                    data = json.load(f)
                    self.commands = data.get("commands", {})
                print(f"Loaded {len(self.commands)} command definitions")
            else:
                print(f"Warning: Commands file not found: {self.commands_file}")
                success = False
        except Exception as e:
            print(f"Error loading commands: {e}")
            success = False

        # Load camera properties
        try:
            if self.properties_file.exists():
                with open(self.properties_file, 'r') as f:
                    data = json.load(f)
                    self.properties = data.get("properties", {})
                print(f"Loaded {len(self.properties)} property definitions")
            else:
                print(f"Warning: Properties file not found: {self.properties_file}")
                success = False
        except Exception as e:
            print(f"Error loading properties: {e}")
            success = False

        return success

    def get_command(self, command_name: str) -> Optional[Dict[str, Any]]:
        """Get command definition by name"""
        return self.commands.get(command_name)

    def get_all_commands(self) -> List[str]:
        """Get list of all command names"""
        return list(self.commands.keys())

    def get_property(self, property_name: str) -> Optional[Dict[str, Any]]:
        """Get property definition by name"""
        return self.properties.get(property_name)

    def get_all_properties(self) -> List[str]:
        """Get list of all property names"""
        return list(self.properties.keys())

    def get_property_validation(self, property_name: str) -> Optional[Dict[str, Any]]:
        """Get validation rules for a property"""
        prop = self.get_property(property_name)
        if prop:
            return prop.get("validation")
        return None

    def get_property_values(self, property_name: str) -> Optional[List]:
        """Get valid values for an enum property"""
        validation = self.get_property_validation(property_name)
        if validation and validation.get("type") == "enum":
            return validation.get("values", [])
        return None

    def get_property_range(self, property_name: str) -> Optional[Dict[str, Any]]:
        """Get min/max/step for a range property"""
        validation = self.get_property_validation(property_name)
        if validation and validation.get("type") == "range":
            return {
                "min": validation.get("min"),
                "max": validation.get("max"),
                "step": validation.get("step"),
                "default": validation.get("default")
            }
        return None

    def validate_property_value(self, property_name: str, value: Any) -> bool:
        """Validate a property value against its definition"""
        validation = self.get_property_validation(property_name)
        if not validation:
            return True  # No validation rules = accept anything

        val_type = validation.get("type")

        if val_type == "enum":
            values = validation.get("values", [])
            return value in values

        elif val_type == "range":
            try:
                num_value = float(value)
                min_val = validation.get("min", float('-inf'))
                max_val = validation.get("max", float('inf'))
                return min_val <= num_value <= max_val
            except:
                return False

        return True  # Unknown validation type = accept


# Global singleton instance
protocol = ProtocolLoader()
