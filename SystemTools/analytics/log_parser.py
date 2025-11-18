"""
Air-Side Log Parser - Extract health snapshots from air-side.jsonl files
Issue #138 - Import historical logs into Performance Analytics
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from utils.logger import logger


class AirSideLogParser:
    """
    Parser for air-side.jsonl files to extract health snapshots.

    Supports:
    - JSON Lines format (one JSON object per line)
    - Multiple file parsing (rotated logs)
    - Health snapshot extraction
    - Chronological merging
    - Duplicate detection by timestamp
    """

    def __init__(self):
        """Initialize log parser"""
        self.health_contexts = ['HEALTH', 'HEALTHBROADCAST', 'HEALTH_BROADCAST']
        self.health_messages = ['health snapshot', 'health broadcast', 'health data']

    def parse_jsonl_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        Parse a single air-side.jsonl file and extract health snapshots.

        Args:
            file_path: Path to .jsonl file

        Returns:
            Tuple of (health_snapshots, total_lines, parse_errors)
        """
        health_snapshots = []
        total_lines = 0
        parse_errors = 0

        try:
            path = Path(file_path)

            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return ([], 0, 1)

            logger.info(f"Parsing {path.name}...")

            with open(path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    total_lines += 1

                    # Skip empty lines
                    if not line.strip():
                        continue

                    try:
                        # Parse JSON line
                        log_entry = json.loads(line)

                        # Try to extract health snapshot
                        snapshot = self.extract_health_snapshot(log_entry)

                        if snapshot:
                            health_snapshots.append(snapshot)

                    except json.JSONDecodeError as e:
                        parse_errors += 1
                        logger.warning(f"JSON parse error in {path.name} line {line_num}: {e}")
                    except Exception as e:
                        parse_errors += 1
                        logger.warning(f"Error processing line {line_num} in {path.name}: {e}")

            logger.info(f"Parsed {path.name}: {len(health_snapshots)} health snapshots from {total_lines} lines ({parse_errors} errors)")

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            parse_errors += 1

        return (health_snapshots, total_lines, parse_errors)

    def extract_health_snapshot(self, log_entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract health snapshot data from a log entry.

        Expected log format:
        {
            "timestamp": "2025-11-17T14:30:00.123Z",
            "domain": "AIR",
            "level": "INFO",
            "context": "HEALTH",
            "message": "Health snapshot",
            "metadata": {
                "cpu_percent": 35.2,
                "memory_used_mb": 4800,
                "camera_latency_ms": 25,
                ...
            }
        }

        Args:
            log_entry: Parsed JSON log entry

        Returns:
            Health snapshot dict compatible with PerformanceDatabase.insert_snapshot(),
            or None if not a health entry
        """
        try:
            # Check if this is a health log entry
            context = log_entry.get('context', '').upper()
            message = log_entry.get('message', '').lower()

            is_health = False

            # Check context field
            if context in self.health_contexts:
                is_health = True

            # Check message field
            if any(health_msg in message for health_msg in self.health_messages):
                is_health = True

            if not is_health:
                return None

            # Extract metadata
            metadata = log_entry.get('metadata', {})

            if not metadata:
                # Some logs might have health data at top level
                # Try to extract directly
                metadata = log_entry

            # Extract timestamp
            timestamp_str = log_entry.get('timestamp')

            if not timestamp_str:
                logger.warning("Health entry missing timestamp, skipping")
                return None

            # Build snapshot dict compatible with PerformanceDatabase.insert_snapshot()
            snapshot = {
                'timestamp': timestamp_str,  # Will be parsed by database
            }

            # Extract system metrics
            # Support both flat and nested structure
            if 'system' in metadata:
                system = metadata['system']
            else:
                system = metadata

            snapshot['cpu_percent'] = system.get('cpu_percent')
            snapshot['memory_used_mb'] = system.get('memory_used_mb')
            snapshot['memory_total_mb'] = system.get('memory_total_mb')
            snapshot['disk_used_mb'] = system.get('disk_used_mb')
            snapshot['disk_total_mb'] = system.get('disk_total_mb')
            snapshot['network_rx_mbps'] = system.get('network_rx_mbps')
            snapshot['network_tx_mbps'] = system.get('network_tx_mbps')

            # Extract camera metrics
            if 'camera' in metadata:
                camera = metadata['camera']
            else:
                camera = metadata

            snapshot['camera_connected'] = camera.get('camera_connected') or camera.get('connected')
            snapshot['sdk_latency_ms'] = camera.get('sdk_latency_ms') or camera.get('camera_latency_ms')
            snapshot['usb_traffic_mbps'] = camera.get('usb_traffic_mbps') or camera.get('camera_usb_traffic_mbps')
            snapshot['error_count'] = camera.get('error_count') or camera.get('camera_error_count')

            # Extract network metrics
            if 'network' in metadata:
                network = metadata['network']
            else:
                network = metadata

            snapshot['tcp_connected'] = network.get('tcp_connected')
            snapshot['tcp_latency_ms'] = network.get('tcp_latency_ms')
            snapshot['udp_loss_percent'] = network.get('udp_loss_percent')
            snapshot['command_queue_depth'] = network.get('command_queue_depth') or network.get('queue_depth')

            # Extract sync metrics
            if 'sync' in metadata:
                sync = metadata['sync']
            else:
                sync = metadata

            snapshot['exposure_rate_hz'] = sync.get('exposure_rate_hz')
            snapshot['health_rate_hz'] = sync.get('health_rate_hz')
            snapshot['property_reads_sec'] = sync.get('property_reads_sec')

            return snapshot

        except Exception as e:
            logger.warning(f"Failed to extract health snapshot from log entry: {e}")
            return None

    def parse_multiple_files(self, file_paths: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse multiple jsonl files and merge results.

        Args:
            file_paths: List of paths to .jsonl files

        Returns:
            Tuple of (merged_snapshots, import_stats)
        """
        all_snapshots = []
        stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_lines': 0,
            'parse_errors': 0,
            'snapshots_found': 0,
            'duplicates_removed': 0
        }

        # Parse each file
        for file_path in file_paths:
            snapshots, lines, errors = self.parse_jsonl_file(file_path)

            if snapshots or lines > 0:
                stats['files_processed'] += 1
                all_snapshots.extend(snapshots)
                stats['total_lines'] += lines
                stats['parse_errors'] += errors
            else:
                stats['files_failed'] += 1

        stats['snapshots_found'] = len(all_snapshots)

        # Merge and deduplicate
        merged_snapshots = self.merge_and_deduplicate(all_snapshots)

        stats['duplicates_removed'] = len(all_snapshots) - len(merged_snapshots)

        logger.info(f"Parsed {stats['files_processed']} files: {len(merged_snapshots)} unique snapshots")

        return (merged_snapshots, stats)

    def merge_and_deduplicate(self, snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge snapshots from multiple files and remove duplicates by timestamp.

        Args:
            snapshots: List of health snapshots (possibly with duplicates)

        Returns:
            Deduplicated list sorted by timestamp
        """
        if not snapshots:
            return []

        # Use timestamp as key for deduplication
        unique_snapshots = {}

        for snapshot in snapshots:
            timestamp = snapshot.get('timestamp')

            if timestamp:
                # Use timestamp as unique key
                # If duplicate, keep the one with more data (more non-None values)
                if timestamp not in unique_snapshots:
                    unique_snapshots[timestamp] = snapshot
                else:
                    # Count non-None values
                    existing_count = sum(1 for v in unique_snapshots[timestamp].values() if v is not None)
                    new_count = sum(1 for v in snapshot.values() if v is not None)

                    # Keep snapshot with more data
                    if new_count > existing_count:
                        unique_snapshots[timestamp] = snapshot

        # Convert back to list and sort by timestamp
        merged = list(unique_snapshots.values())

        # Sort chronologically
        try:
            merged.sort(key=lambda s: s.get('timestamp', ''))
        except Exception as e:
            logger.warning(f"Failed to sort snapshots by timestamp: {e}")

        return merged

    def validate_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Validate that a snapshot has minimum required data.

        Args:
            snapshot: Health snapshot dict

        Returns:
            True if valid, False otherwise
        """
        # Must have timestamp
        if not snapshot.get('timestamp'):
            return False

        # Must have at least one metric (besides timestamp)
        metric_count = sum(1 for k, v in snapshot.items() if k != 'timestamp' and v is not None)

        return metric_count > 0


def create_sample_jsonl_for_testing():
    """
    Create a sample air-side.jsonl file for testing.
    This function is for development/testing only.
    """
    sample_logs = [
        {
            "timestamp": "2025-11-17T14:30:00.123Z",
            "domain": "AIR",
            "level": "INFO",
            "context": "HEALTH",
            "message": "Health snapshot",
            "metadata": {
                "system": {
                    "cpu_percent": 35.2,
                    "memory_used_mb": 4800,
                    "memory_total_mb": 8192,
                    "disk_used_mb": 12000,
                    "disk_total_mb": 32000,
                    "network_rx_mbps": 0.5,
                    "network_tx_mbps": 1.2
                },
                "camera": {
                    "connected": True,
                    "sdk_latency_ms": 25.5,
                    "usb_traffic_mbps": 15.0,
                    "error_count": 0
                },
                "network": {
                    "tcp_connected": True,
                    "tcp_latency_ms": 5.2,
                    "udp_loss_percent": 0.1,
                    "command_queue_depth": 3
                },
                "sync": {
                    "exposure_rate_hz": 5.0,
                    "health_rate_hz": 5.0,
                    "property_reads_sec": 10
                }
            }
        },
        {
            "timestamp": "2025-11-17T14:30:01.123Z",
            "domain": "AIR",
            "level": "INFO",
            "context": "HEALTH",
            "message": "Health snapshot",
            "metadata": {
                "system": {
                    "cpu_percent": 36.0,
                    "memory_used_mb": 4850,
                    "memory_total_mb": 8192
                },
                "camera": {
                    "connected": True,
                    "sdk_latency_ms": 26.0
                }
            }
        }
    ]

    output_path = Path("test_air-side.jsonl")

    with open(output_path, 'w', encoding='utf-8') as f:
        for log in sample_logs:
            f.write(json.dumps(log) + '\n')

    print(f"Created sample file: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    # Test the parser
    print("Testing AirSideLogParser...")

    # Create sample file
    sample_file = create_sample_jsonl_for_testing()

    # Parse it
    parser = AirSideLogParser()
    snapshots, lines, errors = parser.parse_jsonl_file(sample_file)

    print(f"\nResults:")
    print(f"  Total lines: {lines}")
    print(f"  Parse errors: {errors}")
    print(f"  Health snapshots found: {len(snapshots)}")

    if snapshots:
        print(f"\nFirst snapshot:")
        for key, value in snapshots[0].items():
            print(f"  {key}: {value}")
