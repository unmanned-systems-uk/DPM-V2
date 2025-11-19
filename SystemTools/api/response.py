"""
API Response Standard Format
=============================

All API responses follow a consistent structure for easy parsing and error handling.
"""

from datetime import datetime
from typing import Any, Optional, Dict
from dataclasses import dataclass, asdict


@dataclass
class APIResponse:
    """
    Standardized API response format

    Attributes:
        success: Whether operation succeeded
        data: Response payload (dict, list, str, etc.)
        error: Error message if operation failed
        timestamp: ISO8601 timestamp of response
        domain: Domain context (air-side, ground-side, systemtools)
        operation: Operation name (e.g., "get_status", "send_command")
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None
    domain: Optional[str] = None
    operation: Optional[str] = None

    def __post_init__(self):
        """Auto-generate timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + 'Z'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def success_response(
        cls,
        data: Any,
        domain: str,
        operation: str
    ) -> 'APIResponse':
        """
        Create success response

        Args:
            data: Response data
            domain: Domain context
            operation: Operation name

        Returns:
            APIResponse with success=True
        """
        return cls(
            success=True,
            data=data,
            domain=domain,
            operation=operation
        )

    @classmethod
    def error_response(
        cls,
        error: str,
        domain: str,
        operation: str,
        data: Optional[Any] = None
    ) -> 'APIResponse':
        """
        Create error response

        Args:
            error: Error message
            domain: Domain context
            operation: Operation name
            data: Optional partial data

        Returns:
            APIResponse with success=False
        """
        return cls(
            success=False,
            error=error,
            data=data,
            domain=domain,
            operation=operation
        )
