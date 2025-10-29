"""
Protocol Message Formatting for DPM Diagnostic Tool
Creates and parses DPM protocol messages
"""

import json
import time
from typing import Dict, Any, Optional, List


class ProtocolMessage:
    """DPM Protocol message builder and parser"""

    def __init__(self):
        self.sequence_id = 0

    def _next_sequence(self) -> int:
        """Get next sequence ID"""
        self.sequence_id += 1
        return self.sequence_id

    def _create_base_message(self, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create base message structure"""
        return {
            "message_type": message_type,
            "sequence_id": self._next_sequence(),
            "timestamp": int(time.time() * 1000),  # milliseconds
            "payload": payload
        }

    def create_handshake(self, client_id: str = "WindowsDiagnosticTool",
                         client_version: str = "1.0.0") -> str:
        """Create handshake message"""
        payload = {
            "client_id": client_id,
            "client_version": client_version,
            "requested_features": ["camera", "gimbal", "status", "content"]
        }
        message = self._create_base_message("handshake", payload)
        return json.dumps(message)

    def create_command(self, command: str, parameters: Dict[str, Any] = None) -> str:
        """Create command message"""
        payload = {
            "command": command,
            "parameters": parameters or {}
        }
        message = self._create_base_message("command", payload)
        return json.dumps(message)

    def create_heartbeat(self) -> str:
        """Create heartbeat message"""
        payload = {
            "status": "alive",
            "timestamp": int(time.time() * 1000)
        }
        message = self._create_base_message("heartbeat", payload)
        return json.dumps(message)

    def create_disconnect(self) -> str:
        """Create disconnect message"""
        payload = {
            "reason": "User disconnect"
        }
        message = self._create_base_message("disconnect", payload)
        return json.dumps(message)

    # Quick command builders
    def create_camera_capture(self, mode: str = "single") -> str:
        """Create camera.capture command"""
        return self.create_command("camera.capture", {"mode": mode})

    def create_camera_set_property(self, property_name: str, value: Any) -> str:
        """Create camera.set_property command"""
        return self.create_command("camera.set_property", {
            "property": property_name,
            "value": value
        })

    def create_camera_get_properties(self, properties: List[str]) -> str:
        """Create camera.get_properties command"""
        return self.create_command("camera.get_properties", {
            "properties": properties
        })

    def create_system_get_status(self) -> str:
        """Create system.get_status command"""
        return self.create_command("system.get_status", {})

    # Parsing
    def parse_message(self, json_str: str) -> Optional[Dict[str, Any]]:
        """Parse JSON message string"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None

    def is_response(self, message: Dict[str, Any]) -> bool:
        """Check if message is a response"""
        return message.get("message_type") == "response"

    def is_status(self, message: Dict[str, Any]) -> bool:
        """Check if message is a status broadcast"""
        return message.get("message_type") == "status"

    def is_heartbeat(self, message: Dict[str, Any]) -> bool:
        """Check if message is a heartbeat"""
        return message.get("message_type") == "heartbeat"

    def is_error(self, message: Dict[str, Any]) -> bool:
        """Check if response is an error"""
        if not self.is_response(message):
            return False
        payload = message.get("payload", {})
        return payload.get("status") == "error"

    def get_error_message(self, message: Dict[str, Any]) -> Optional[str]:
        """Extract error message from response"""
        if not self.is_error(message):
            return None
        payload = message.get("payload", {})
        return payload.get("message", "Unknown error")

    def get_error_code(self, message: Dict[str, Any]) -> Optional[int]:
        """Extract error code from response"""
        if not self.is_error(message):
            return None
        payload = message.get("payload", {})
        return payload.get("error_code")


# Global singleton instance
protocol_msg = ProtocolMessage()
