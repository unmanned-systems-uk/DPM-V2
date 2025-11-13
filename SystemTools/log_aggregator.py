#!/usr/bin/env python3
"""
DPM SystemTools - Tri-Domain Log Aggregator
============================================

Aggregates logs from Air-Side (UDP) and Ground-Side (TCP) into a unified timeline.

Part of Issue #74 - Phase 1: Foundation Infrastructure
"""

import socket
import json
import threading
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
from pathlib import Path
import csv

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich import box
except ImportError:
    print("ERROR: 'rich' library not installed. Run: pip install rich")
    sys.exit(1)


class AirSideListener:
    """UDP listener for Air-Side logs (port 5007)"""

    def __init__(self, host: str = "0.0.0.0", port: int = 5007, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.sock = None
        self.running = False
        self.thread = None

    def start(self, log_queue: deque):
        """Start the UDP listener in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._listen, args=(log_queue,), daemon=True)
        self.thread.start()

    def _listen(self, log_queue: deque):
        """Listen for UDP packets and add to queue"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(1.0)  # 1 second timeout for graceful shutdown

            print(f"[AirSideListener] Listening on UDP {self.host}:{self.port}")

            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.buffer_size)
                    try:
                        log_entry = json.loads(data.decode('utf-8'))
                        log_entry['domain'] = 'AIR'
                        log_entry['source_addr'] = f"{addr[0]}:{addr[1]}"
                        log_queue.append(log_entry)
                    except json.JSONDecodeError as e:
                        print(f"[AirSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[AirSideListener] Error: {e}")

        except Exception as e:
            print(f"[AirSideListener] Failed to start: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)


class GroundSideListener:
    """TCP listener for Ground-Side logs (port 5008, via ADB forward)"""

    def __init__(self, host: str = "localhost", port: int = 5008, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.sock = None
        self.running = False
        self.thread = None

    def start(self, log_queue: deque):
        """Start the TCP listener in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._listen, args=(log_queue,), daemon=True)
        self.thread.start()

    def _listen(self, log_queue: deque):
        """Listen for TCP connections and add logs to queue"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.sock.settimeout(1.0)  # 1 second timeout for graceful shutdown

            print(f"[GroundSideListener] Listening on TCP {self.host}:{self.port}")
            print("[GroundSideListener] Ensure ADB forward is active: adb forward tcp:5008 tcp:5008")

            while self.running:
                try:
                    conn, addr = self.sock.accept()
                    print(f"[GroundSideListener] Connection from {addr}")
                    self._handle_connection(conn, addr, log_queue)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[GroundSideListener] Error accepting connection: {e}")

        except Exception as e:
            print(f"[GroundSideListener] Failed to start: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def _handle_connection(self, conn: socket.socket, addr: tuple, log_queue: deque):
        """Handle a single TCP connection"""
        buffer = ""
        try:
            conn.settimeout(1.0)
            while self.running:
                try:
                    data = conn.recv(self.buffer_size)
                    if not data:
                        break

                    buffer += data.decode('utf-8')

                    # Process complete JSON objects (newline-delimited)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                log_entry = json.loads(line)
                                log_entry['domain'] = 'GROUND'
                                log_entry['source_addr'] = f"{addr[0]}:{addr[1]}"
                                log_queue.append(log_entry)
                            except json.JSONDecodeError as e:
                                print(f"[GroundSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[GroundSideListener] Error receiving data: {e}")
                    break
        finally:
            conn.close()
            print(f"[GroundSideListener] Connection closed: {addr}")

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)


class LogAggregator:
    """Main log aggregator - merges Air and Ground logs into unified timeline"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.log_queue = deque(maxlen=self.config['buffer']['max_entries'])
        self.air_listener = None
        self.ground_listener = None
        self.console = Console()
        self.running = False

        # Filters
        self.filter_level = None
        self.filter_context = None
        self.filter_domain = None
        self.filter_search = None
        self.filter_since = None
        self.filter_until = None

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "log_aggregator.json"

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"WARNING: Config file not found: {config_path}")
            print("Using default configuration")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "network": {
                "air_side": {"host": "0.0.0.0", "port": 5007, "buffer_size": 4096},
                "ground_side": {"host": "localhost", "port": 5008, "buffer_size": 4096}
            },
            "display": {
                "colors": {"AIR": "blue", "GROUND": "magenta"},
                "show_timestamp": True,
                "show_thread": False,
                "show_function": False,
                "show_line": False,
                "indent_fields": True
            },
            "buffer": {"max_entries": 10000},
            "filtering": {
                "default_level": None,
                "default_context": None,
                "default_domain": None
            },
            "export": {
                "default_format": "json",
                "output_dir": "logs/exports"
            }
        }

    def start(self):
        """Start the log aggregator"""
        self.running = True

        # Start listeners
        air_config = self.config['network']['air_side']
        self.air_listener = AirSideListener(
            host=air_config['host'],
            port=air_config['port'],
            buffer_size=air_config['buffer_size']
        )
        self.air_listener.start(self.log_queue)

        ground_config = self.config['network']['ground_side']
        self.ground_listener = GroundSideListener(
            host=ground_config['host'],
            port=ground_config['port'],
            buffer_size=ground_config['buffer_size']
        )
        self.ground_listener.start(self.log_queue)

        print("\n[LogAggregator] Started - Press Ctrl+C to stop\n")

        # Display logs in real-time
        try:
            self._display_logs()
        except KeyboardInterrupt:
            print("\n[LogAggregator] Stopping...")
        finally:
            self.stop()

    def stop(self):
        """Stop the log aggregator"""
        self.running = False
        if self.air_listener:
            self.air_listener.stop()
        if self.ground_listener:
            self.ground_listener.stop()

    def _display_logs(self):
        """Display logs in real-time with color coding"""
        last_index = 0

        while self.running:
            # Get new logs
            current_logs = list(self.log_queue)

            if len(current_logs) > last_index:
                new_logs = current_logs[last_index:]

                # Sort by timestamp (best effort)
                sorted_logs = self._sort_logs(new_logs)

                # Display each log
                for log_entry in sorted_logs:
                    if self._should_display(log_entry):
                        self._display_log_entry(log_entry)

                last_index = len(current_logs)

            # Small sleep to avoid busy-waiting
            threading.Event().wait(0.1)

    def _sort_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort logs by timestamp"""
        def get_timestamp(log_entry):
            try:
                timestamp_str = log_entry.get('timestamp', '')
                # Try ISO 8601 format
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Fallback to current time if parsing fails
                return datetime.now()

        return sorted(logs, key=get_timestamp)

    def _should_display(self, log_entry: Dict[str, Any]) -> bool:
        """Check if log entry matches filters"""
        # Level filter
        if self.filter_level and log_entry.get('level') != self.filter_level:
            return False

        # Context filter
        if self.filter_context and log_entry.get('context') != self.filter_context:
            return False

        # Domain filter
        if self.filter_domain and log_entry.get('domain') != self.filter_domain:
            return False

        # Text search filter
        if self.filter_search:
            entry_str = json.dumps(log_entry).lower()
            if self.filter_search.lower() not in entry_str:
                return False

        # Time range filter
        if self.filter_since or self.filter_until:
            try:
                timestamp_str = log_entry.get('timestamp', '')
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                if self.filter_since and timestamp < self.filter_since:
                    return False
                if self.filter_until and timestamp > self.filter_until:
                    return False
            except (ValueError, AttributeError):
                pass

        return True

    def _display_log_entry(self, entry: Dict[str, Any]):
        """Display a single log entry with color coding"""
        domain = entry.get('domain', 'UNKNOWN')
        color = self.config['display']['colors'].get(domain, 'white')

        timestamp = entry.get('timestamp', 'NO-TS')
        level = entry.get('level', 'INFO')
        context = entry.get('context', 'UNKNOWN')
        message = entry.get('message', '')

        # Main line
        if self.config['display']['show_timestamp']:
            self.console.print(f"[{color}][{domain}][/{color}] [{level}] [{context}] {message}")
        else:
            self.console.print(f"[{color}][{domain}][/{color}] [{level}] [{context}] {message}")

        # Structured fields (indented)
        if self.config['display']['indent_fields']:
            skip_fields = ['timestamp', 'level', 'context', 'message', 'domain', 'source_addr']

            # Optionally show thread, function, line
            if not self.config['display']['show_thread']:
                skip_fields.append('thread')
            if not self.config['display']['show_function']:
                skip_fields.append('function')
            if not self.config['display']['show_line']:
                skip_fields.append('line')

            for key, value in entry.items():
                if key not in skip_fields:
                    self.console.print(f"  └─ {key}: {value}", style="dim")

    def export_logs(self, output_file: str, format: str = "json"):
        """Export logs to file"""
        logs = list(self.log_queue)
        sorted_logs = self._sort_logs(logs)

        # Create output directory if needed
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(sorted_logs, f, indent=2)
        elif format == "csv":
            self._export_csv(sorted_logs, output_file)
        elif format == "text":
            self._export_text(sorted_logs, output_file)
        else:
            raise ValueError(f"Unknown export format: {format}")

        print(f"[LogAggregator] Exported {len(sorted_logs)} logs to {output_file}")

    def _export_csv(self, logs: List[Dict[str, Any]], output_file: str):
        """Export logs to CSV format"""
        if not logs:
            return

        # Get all unique keys
        all_keys = set()
        for log in logs:
            all_keys.update(log.keys())
        all_keys = sorted(all_keys)

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_keys)
            writer.writeheader()
            writer.writerows(logs)

    def _export_text(self, logs: List[Dict[str, Any]], output_file: str):
        """Export logs to human-readable text format"""
        with open(output_file, 'w') as f:
            for entry in logs:
                domain = entry.get('domain', 'UNKNOWN')
                timestamp = entry.get('timestamp', 'NO-TS')
                level = entry.get('level', 'INFO')
                context = entry.get('context', 'UNKNOWN')
                message = entry.get('message', '')

                f.write(f"{timestamp} [{domain}] [{level}] [{context}] {message}\n")

                # Structured fields
                skip_fields = ['timestamp', 'level', 'context', 'message', 'domain', 'thread', 'function', 'line', 'source_addr']
                for key, value in entry.items():
                    if key not in skip_fields:
                        f.write(f"  └─ {key}: {value}\n")
                f.write("\n")

    def replay_from_file(self, input_file: str):
        """Replay logs from a JSON file"""
        with open(input_file, 'r') as f:
            logs = json.load(f)

        print(f"[LogAggregator] Replaying {len(logs)} logs from {input_file}")

        for log_entry in logs:
            if self._should_display(log_entry):
                self._display_log_entry(log_entry)


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime"""
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DPM SystemTools - Tri-Domain Log Aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start log aggregator (listen on both Air + Ground)
  python log_aggregator.py

  # Filter by level
  python log_aggregator.py --level=ERROR

  # Filter by domain
  python log_aggregator.py --domain=AIR

  # Search for text
  python log_aggregator.py --search="aperture"

  # Export to file
  python log_aggregator.py --export=logs_20251113.json

  # Replay from file
  python log_aggregator.py --replay=logs_20251113.json
        """
    )

    parser.add_argument('--config', type=str, help="Path to config file")
    parser.add_argument('--level', type=str, help="Filter by log level (DEBUG, INFO, WARNING, ERROR)")
    parser.add_argument('--context', type=str, help="Filter by context")
    parser.add_argument('--domain', type=str, choices=['AIR', 'GROUND'], help="Filter by domain")
    parser.add_argument('--search', type=str, help="Search for text in logs")
    parser.add_argument('--since', type=str, help="Filter logs since timestamp (ISO 8601)")
    parser.add_argument('--until', type=str, help="Filter logs until timestamp (ISO 8601)")
    parser.add_argument('--export', type=str, help="Export logs to file (JSON format)")
    parser.add_argument('--export-format', type=str, choices=['json', 'csv', 'text'], default='json', help="Export format")
    parser.add_argument('--replay', type=str, help="Replay logs from JSON file")

    args = parser.parse_args()

    # Create aggregator
    aggregator = LogAggregator(config_path=args.config)

    # Apply filters
    aggregator.filter_level = args.level
    aggregator.filter_context = args.context
    aggregator.filter_domain = args.domain
    aggregator.filter_search = args.search

    if args.since:
        aggregator.filter_since = parse_timestamp(args.since)
    if args.until:
        aggregator.filter_until = parse_timestamp(args.until)

    # Replay mode
    if args.replay:
        aggregator.replay_from_file(args.replay)
        return

    # Start aggregator
    aggregator.start()

    # Export if requested
    if args.export:
        aggregator.export_logs(args.export, format=args.export_format)


if __name__ == "__main__":
    main()
