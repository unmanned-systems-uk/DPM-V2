"""
Performance Database - SQLite storage for system health metrics
Stores health snapshots with 7-day retention for statistical analysis
"""

import sqlite3
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.logger import logger


class PerformanceDatabase:
    """SQLite database for storing and querying system health metrics"""

    def __init__(self, db_path: str = "data/performance.db"):
        """
        Initialize performance database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.lock = threading.Lock()

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Connect and create tables
        self._connect()
        self.create_tables()

        logger.info(f"PerformanceDatabase initialized: {db_path}")

    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            logger.debug(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def create_tables(self):
        """Create health_snapshots table if it doesn't exist"""
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Create health_snapshots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS health_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,

                        -- System metrics
                        cpu_percent REAL,
                        memory_used_mb INTEGER,
                        memory_total_mb INTEGER,
                        disk_used_mb INTEGER,
                        disk_total_mb INTEGER,
                        network_rx_mbps REAL,
                        network_tx_mbps REAL,

                        -- Camera metrics
                        camera_connected BOOLEAN,
                        camera_latency_ms REAL,
                        camera_usb_traffic_mbps REAL,
                        camera_error_count INTEGER,

                        -- Network metrics
                        tcp_connected BOOLEAN,
                        tcp_latency_ms REAL,
                        udp_loss_percent REAL,
                        queue_depth INTEGER,

                        -- Sync metrics
                        exposure_rate_hz REAL,
                        health_rate_hz REAL,
                        property_reads_sec INTEGER
                    )
                ''')

                # Create index on timestamp for fast queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp
                    ON health_snapshots(timestamp)
                ''')

                self.conn.commit()
                logger.debug("Database tables created/verified")

            except Exception as e:
                logger.error(f"Failed to create tables: {e}")
                raise

    def insert_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Insert a health snapshot into the database

        Args:
            snapshot: Health data dictionary from Air-Side broadcast

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Extract timestamp (ISO 8601 string or datetime object)
                timestamp = snapshot.get('timestamp')
                if isinstance(timestamp, str):
                    # Parse ISO 8601 timestamp
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif timestamp is None:
                    timestamp = datetime.utcnow()

                # Extract metrics - support both flat and nested structure
                # Flat structure: {'cpu_percent': 0.0, 'memory_used_mb': 746, ...}
                # Nested structure: {'system': {'cpu_percent': 0.0}, 'camera': {...}, ...}
                system = snapshot.get('system', {}) if 'system' in snapshot else snapshot
                camera = snapshot.get('camera', {}) if 'camera' in snapshot else snapshot
                network = snapshot.get('network', {}) if 'network' in snapshot else snapshot
                sync = snapshot.get('sync', {}) if 'sync' in snapshot else snapshot

                # Insert record
                cursor.execute('''
                    INSERT INTO health_snapshots (
                        timestamp,
                        cpu_percent, memory_used_mb, memory_total_mb,
                        disk_used_mb, disk_total_mb,
                        network_rx_mbps, network_tx_mbps,
                        camera_connected, camera_latency_ms,
                        camera_usb_traffic_mbps, camera_error_count,
                        tcp_connected, tcp_latency_ms,
                        udp_loss_percent, queue_depth,
                        exposure_rate_hz, health_rate_hz, property_reads_sec
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    system.get('cpu_percent'),
                    system.get('memory_used_mb'),
                    system.get('memory_total_mb'),
                    system.get('disk_used_mb'),
                    system.get('disk_total_mb'),
                    system.get('network_rx_mbps'),
                    system.get('network_tx_mbps'),
                    camera.get('camera_connected') or camera.get('connected'),
                    camera.get('sdk_latency_ms'),
                    camera.get('usb_traffic_mbps'),
                    camera.get('error_count'),
                    network.get('tcp_connected'),
                    network.get('tcp_latency_ms'),
                    network.get('udp_loss_percent'),
                    network.get('command_queue_depth'),
                    sync.get('exposure_rate_hz'),
                    sync.get('health_rate_hz'),
                    sync.get('property_reads_sec')
                ))

                self.conn.commit()
                logger.debug(f"Inserted snapshot at {timestamp}")
                return True

            except Exception as e:
                logger.error(f"Failed to insert snapshot: {e}")
                return False

    def query_time_range(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Query health snapshots within a time range

        Args:
            start: Start datetime (inclusive)
            end: End datetime (inclusive)

        Returns:
            List of health snapshot dictionaries
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                cursor.execute('''
                    SELECT * FROM health_snapshots
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                ''', (start, end))

                rows = cursor.fetchall()

                # Convert rows to dictionaries
                snapshots = []
                for row in rows:
                    snapshot = dict(row)
                    snapshots.append(snapshot)

                logger.debug(f"Queried {len(snapshots)} snapshots from {start} to {end}")
                return snapshots

            except Exception as e:
                logger.error(f"Failed to query time range: {e}")
                return []

    def query_latest(self, limit: int = 360) -> List[Dict[str, Any]]:
        """
        Query the most recent health snapshots

        Args:
            limit: Maximum number of snapshots to retrieve (default: 360 = 30 min @ 5 Hz)

        Returns:
            List of health snapshot dictionaries (newest first)
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                cursor.execute('''
                    SELECT * FROM health_snapshots
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

                rows = cursor.fetchall()

                # Convert rows to dictionaries
                snapshots = []
                for row in rows:
                    snapshot = dict(row)
                    snapshots.append(snapshot)

                logger.debug(f"Queried latest {len(snapshots)} snapshots")
                return snapshots

            except Exception as e:
                logger.error(f"Failed to query latest snapshots: {e}")
                return []

    def cleanup_old_data(self, retention_days: int = 7) -> int:
        """
        Delete health snapshots older than retention period

        Args:
            retention_days: Number of days to retain (default: 7)

        Returns:
            Number of records deleted
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                cutoff = datetime.utcnow() - timedelta(days=retention_days)

                cursor.execute('''
                    DELETE FROM health_snapshots
                    WHERE timestamp < ?
                ''', (cutoff,))

                deleted_count = cursor.rowcount
                self.conn.commit()

                logger.info(f"Cleaned up {deleted_count} old snapshots (retention: {retention_days} days)")
                return deleted_count

            except Exception as e:
                logger.error(f"Failed to cleanup old data: {e}")
                return 0

    def get_record_count(self) -> int:
        """Get total number of health snapshots in database"""
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM health_snapshots')
                count = cursor.fetchone()[0]
                return count
            except Exception as e:
                logger.error(f"Failed to get record count: {e}")
                return 0

    def get_date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the date range of stored data

        Returns:
            Tuple of (oldest_timestamp, newest_timestamp) or (None, None) if empty
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                cursor.execute('''
                    SELECT MIN(timestamp), MAX(timestamp)
                    FROM health_snapshots
                ''')

                row = cursor.fetchone()
                if row[0] is None or row[1] is None:
                    return (None, None)

                oldest = datetime.fromisoformat(row[0])
                newest = datetime.fromisoformat(row[1])

                return (oldest, newest)

            except Exception as e:
                logger.error(f"Failed to get date range: {e}")
                return (None, None)

    def clear_all_snapshots(self) -> int:
        """
        Clear all health snapshots from the database

        Returns:
            Number of snapshots deleted
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Get count before deleting
                cursor.execute('SELECT COUNT(*) FROM health_snapshots')
                count = cursor.fetchone()[0]

                # Delete all snapshots
                cursor.execute('DELETE FROM health_snapshots')
                self.conn.commit()

                logger.info(f"Cleared {count} snapshots from database")
                return count

            except Exception as e:
                logger.error(f"Failed to clear snapshots: {e}")
                return 0

    def close(self):
        """Close database connection"""
        with self.lock:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
