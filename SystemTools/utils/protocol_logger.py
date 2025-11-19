"""
Protocol-Compliant Logger for SystemTools
==========================================

Enforces protocol/log_contexts.json compliance by requiring context parameter.
Validates all contexts against the protocol single source of truth.

Usage:
    from utils.protocol_logger import logger

    logger.debug("NETWORK", "TCP client connected")
    logger.info("COMMAND", f"Processing command: {cmd}")
    logger.error("CAMERA", "Failed to initialize Sony SDK")

Air-Side Equivalent:
    LOG_INFO(LogContext::NETWORK, "TCP client connected");
"""

import logging
from typing import Optional
from .logger import Logger
from .log_contexts import LogContexts


class ProtocolLogger:
    """
    Protocol-enforcing logger wrapper that validates contexts against protocol.

    This ensures SystemTools follows the same structured logging protocol as
    Air-Side (C++) and Ground-Side (Kotlin).
    """

    def __init__(self):
        """Initialize protocol logger with base logger and context validator"""
        self._base_logger = Logger()
        self._contexts = LogContexts()

        # Validate that protocol loaded successfully
        valid_contexts = self._contexts.get_context_ids()
        if not valid_contexts:
            raise RuntimeError("Failed to load log contexts from protocol/log_contexts.json")

        self.info("SYSTEM", f"ProtocolLogger initialized with {len(valid_contexts)} contexts: {', '.join(valid_contexts)}")

    def _validate_context(self, context: str) -> None:
        """
        Validate context against protocol/log_contexts.json

        Args:
            context: Log context ID (e.g., "NETWORK", "COMMAND")

        Raises:
            ValueError: If context is not defined in protocol
        """
        valid_contexts = self._contexts.get_context_ids()

        if context not in valid_contexts:
            raise ValueError(
                f"Invalid log context '{context}'. "
                f"Must be one of: {', '.join(valid_contexts)}. "
                f"Update protocol/log_contexts.json to add new contexts."
            )

    def _format_message(self, context: str, message: str) -> str:
        """
        Format message with context tag for structured logging

        Args:
            context: Validated log context
            message: Log message

        Returns:
            Formatted message: "[CONTEXT] message"
        """
        return f"[{context}] {message}"

    def debug(self, context: str, message: str) -> None:
        """
        Log debug message with protocol-compliant context

        Args:
            context: Log context from protocol (e.g., "NETWORK", "CAMERA")
            message: Log message

        Raises:
            ValueError: If context is invalid
        """
        self._validate_context(context)
        formatted = self._format_message(context, message)
        self._base_logger.debug(formatted)

    def info(self, context: str, message: str) -> None:
        """
        Log info message with protocol-compliant context

        Args:
            context: Log context from protocol (e.g., "NETWORK", "COMMAND")
            message: Log message

        Raises:
            ValueError: If context is invalid
        """
        self._validate_context(context)
        formatted = self._format_message(context, message)
        self._base_logger.info(formatted)

    def warning(self, context: str, message: str) -> None:
        """
        Log warning message with protocol-compliant context

        Args:
            context: Log context from protocol (e.g., "SYSTEM", "HEALTH")
            message: Log message

        Raises:
            ValueError: If context is invalid
        """
        self._validate_context(context)
        formatted = self._format_message(context, message)
        self._base_logger.warning(formatted)

    def error(self, context: str, message: str) -> None:
        """
        Log error message with protocol-compliant context

        Args:
            context: Log context from protocol (e.g., "NETWORK", "CAMERA")
            message: Log message

        Raises:
            ValueError: If context is invalid
        """
        self._validate_context(context)
        formatted = self._format_message(context, message)
        self._base_logger.error(formatted)

    def exception(self, context: str, message: str) -> None:
        """
        Log exception with traceback and protocol-compliant context

        Args:
            context: Log context from protocol (e.g., "SYSTEM", "NETWORK")
            message: Log message

        Raises:
            ValueError: If context is invalid
        """
        self._validate_context(context)
        formatted = self._format_message(context, message)
        self._base_logger.exception(formatted)


# Global singleton instance
logger = ProtocolLogger()
