"""
DPM SystemTools - Log Contexts Protocol Loader
==============================================

Loads log contexts and levels from protocol/log_contexts.json at runtime.
This ensures SystemTools is always in sync with the protocol definition.

Single Source of Truth: protocol/log_contexts.json

Usage:
    from utils.log_contexts import LogContexts

    # Get all context IDs
    contexts = LogContexts.get_context_ids()  # ['CAMERA', 'NETWORK', ...]

    # Get context with color
    camera = LogContexts.get_context('CAMERA')
    # Returns: {'id': 'CAMERA', 'color': '#4CAF50', 'description': '...', ...}

    # Get context color
    color = LogContexts.get_context_color('NETWORK')  # '#2196F3'

    # Get contexts for UI (with ALL option)
    ui_contexts = LogContexts.get_contexts_for_ui()  # ['ALL', 'CAMERA', 'NETWORK', ...]
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import logger

class LogContexts:
    """
    Singleton-style class for loading and accessing log contexts from protocol definition
    """
    _protocol_data: Optional[Dict] = None
    _protocol_path: Optional[Path] = None

    @classmethod
    def _load_protocol(cls) -> Dict:
        """
        Load protocol/log_contexts.json file

        Returns:
            Protocol data dict

        Raises:
            FileNotFoundError: If protocol file not found
            json.JSONDecodeError: If protocol file is invalid JSON
        """
        if cls._protocol_data is not None:
            return cls._protocol_data

        # Find protocol file (go up from SystemTools to DPM-V2 root)
        systemtools_dir = Path(__file__).parent.parent
        project_root = systemtools_dir.parent
        protocol_file = project_root / "protocol" / "log_contexts.json"

        if not protocol_file.exists():
            raise FileNotFoundError(
                f"Protocol file not found: {protocol_file}\n"
                f"Expected at: {protocol_file.absolute()}\n"
                "Please ensure protocol/log_contexts.json exists in the project root."
            )

        try:
            with open(protocol_file, 'r') as f:
                cls._protocol_data = json.load(f)
                cls._protocol_path = protocol_file
                logger.info(f"[SYSTEM] Loaded log contexts protocol from {protocol_file}")
                logger.debug(f"[SYSTEM] Protocol version: {cls._protocol_data.get('version')}")
                logger.debug(f"[SYSTEM] Found {len(cls._protocol_data.get('contexts', []))} contexts")
                return cls._protocol_data

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in protocol file {protocol_file}: {e.msg}",
                e.doc, e.pos
            )

    @classmethod
    def get_contexts(cls) -> List[Dict]:
        """
        Get all context definitions

        Returns:
            List of context dicts with keys: id, description, domains, color, examples
        """
        protocol = cls._load_protocol()
        return protocol.get('contexts', [])

    @classmethod
    def get_context_ids(cls) -> List[str]:
        """
        Get list of all context IDs

        Returns:
            List of context ID strings (e.g., ['CAMERA', 'NETWORK', 'COMMAND', ...])
        """
        return [ctx['id'] for ctx in cls.get_contexts()]

    @classmethod
    def get_context(cls, context_id: str) -> Optional[Dict]:
        """
        Get specific context definition by ID

        Args:
            context_id: Context ID (e.g., 'CAMERA', 'NETWORK')

        Returns:
            Context dict or None if not found
        """
        for ctx in cls.get_contexts():
            if ctx['id'] == context_id:
                return ctx
        return None

    @classmethod
    def get_context_color(cls, context_id: str) -> str:
        """
        Get color for specific context

        Args:
            context_id: Context ID (e.g., 'CAMERA')

        Returns:
            Hex color string (e.g., '#4CAF50') or default gray if not found
        """
        ctx = cls.get_context(context_id)
        return ctx['color'] if ctx else '#9E9E9E'

    @classmethod
    def get_context_description(cls, context_id: str) -> str:
        """
        Get description for specific context

        Args:
            context_id: Context ID

        Returns:
            Description string or empty string if not found
        """
        ctx = cls.get_context(context_id)
        return ctx['description'] if ctx else ''

    @classmethod
    def get_contexts_for_ui(cls, include_all: bool = True) -> List[str]:
        """
        Get context IDs suitable for UI dropdowns

        Args:
            include_all: Whether to prepend 'ALL' option (default: True)

        Returns:
            List of context ID strings, optionally with 'ALL' as first item
        """
        context_ids = cls.get_context_ids()
        if include_all:
            return ['ALL'] + context_ids
        return context_ids

    @classmethod
    def get_contexts_for_domain(cls, domain: str) -> List[str]:
        """
        Get contexts applicable to specific domain

        Args:
            domain: Domain name ('air-side', 'ground-side', or 'systemtools')

        Returns:
            List of context IDs applicable to this domain
        """
        return [
            ctx['id']
            for ctx in cls.get_contexts()
            if domain in ctx.get('domains', [])
        ]

    @classmethod
    def get_levels(cls) -> List[Dict]:
        """
        Get all log level definitions

        Returns:
            List of level dicts with keys: id, value, description, enabled_in, color
        """
        protocol = cls._load_protocol()
        return protocol.get('levels', [])

    @classmethod
    def get_level_ids(cls) -> List[str]:
        """
        Get list of all level IDs

        Returns:
            List of level ID strings (e.g., ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        """
        return [level['id'] for level in cls.get_levels()]

    @classmethod
    def get_level(cls, level_id: str) -> Optional[Dict]:
        """
        Get specific level definition by ID

        Args:
            level_id: Level ID (e.g., 'INFO', 'ERROR')

        Returns:
            Level dict or None if not found
        """
        for level in cls.get_levels():
            if level['id'] == level_id:
                return level
        return None

    @classmethod
    def get_level_color(cls, level_id: str) -> str:
        """
        Get color for specific level

        Args:
            level_id: Level ID (e.g., 'ERROR')

        Returns:
            Hex color string (e.g., '#F44336') or default gray if not found
        """
        level = cls.get_level(level_id)
        return level['color'] if level else '#9E9E9E'

    @classmethod
    def get_levels_for_ui(cls, include_all: bool = True) -> List[str]:
        """
        Get level IDs suitable for UI dropdowns

        Args:
            include_all: Whether to prepend 'ALL' option (default: True)

        Returns:
            List of level ID strings, optionally with 'ALL' as first item
        """
        level_ids = cls.get_level_ids()
        if include_all:
            return ['ALL'] + level_ids
        return level_ids

    @classmethod
    def get_protocol_version(cls) -> str:
        """
        Get protocol version

        Returns:
            Version string (e.g., '1.0')
        """
        protocol = cls._load_protocol()
        return protocol.get('version', 'unknown')

    @classmethod
    def get_protocol_path(cls) -> Optional[Path]:
        """
        Get path to loaded protocol file

        Returns:
            Path object or None if not loaded yet
        """
        if cls._protocol_data is None:
            cls._load_protocol()
        return cls._protocol_path

    @classmethod
    def reload(cls):
        """
        Force reload of protocol file

        Useful if protocol file changes during runtime
        """
        cls._protocol_data = None
        cls._protocol_path = None
        logger.info("[SYSTEM] Reloading log contexts protocol...")
        cls._load_protocol()


# Convenience functions for common operations
def get_all_contexts() -> List[str]:
    """Get all context IDs (without ALL)"""
    return LogContexts.get_context_ids()

def get_context_color(context_id: str) -> str:
    """Get color for context"""
    return LogContexts.get_context_color(context_id)

def get_contexts_for_filter() -> List[str]:
    """Get contexts for filter UI (with ALL)"""
    return LogContexts.get_contexts_for_ui(include_all=True)

def get_level_color(level_id: str) -> str:
    """Get color for level"""
    return LogContexts.get_level_color(level_id)

def get_levels_for_filter() -> List[str]:
    """Get levels for filter UI (with ALL)"""
    return LogContexts.get_levels_for_ui(include_all=True)


# Test/debug function
if __name__ == '__main__':
    """Test the log contexts loader"""
    print("=== DPM Log Contexts Protocol ===\n")

    # Protocol info
    print(f"Protocol version: {LogContexts.get_protocol_version()}")
    print(f"Protocol file: {LogContexts.get_protocol_path()}\n")

    # Contexts
    print(f"Contexts ({len(LogContexts.get_contexts())}):")
    for ctx in LogContexts.get_contexts():
        print(f"  • {ctx['id']:10s} {ctx['color']:8s} - {ctx['description'][:60]}")
        print(f"             Domains: {', '.join(ctx['domains'])}")

    print(f"\nContext IDs: {', '.join(LogContexts.get_context_ids())}")
    print(f"For UI: {', '.join(LogContexts.get_contexts_for_ui())}")

    # Levels
    print(f"\nLevels ({len(LogContexts.get_levels())}):")
    for level in LogContexts.get_levels():
        print(f"  • {level['id']:10s} {level['color']:8s} - {level['description'][:60]}")

    print(f"\nLevel IDs: {', '.join(LogContexts.get_level_ids())}")
    print(f"For UI: {', '.join(LogContexts.get_levels_for_ui())}")

    # Domain-specific contexts
    print(f"\nAir-Side contexts: {', '.join(LogContexts.get_contexts_for_domain('air-side'))}")
    print(f"Ground-Side contexts: {', '.join(LogContexts.get_contexts_for_domain('ground-side'))}")
    print(f"SystemTools contexts: {', '.join(LogContexts.get_contexts_for_domain('systemtools'))}")
