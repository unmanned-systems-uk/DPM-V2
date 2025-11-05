"""
Logger for DPM Diagnostic Tool
File and console logging with levels
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class Logger:
    """Application logger with file and console output"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, log_dir: str = None):
        if self._initialized:
            return

        self._initialized = True

        # Set up log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent / "logs"
        else:
            log_dir = Path(log_dir)

        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        log_file = log_dir / f"dpm_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Set up logger
        self.logger = logging.getLogger("DPMDiagnostic")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        self.logger.handlers = []

        # File handler (DEBUG level)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] [%(threadName)-10s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (INFO level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        self.info(f"Logger initialized. Log file: {log_file}")

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def exception(self, message: str):
        """Log exception with traceback"""
        self.logger.exception(message)


# Global singleton instance
logger = Logger()
