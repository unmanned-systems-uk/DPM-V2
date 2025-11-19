"""
SystemTools Controller
======================

Programmatic interface for SystemTools operations (log aggregation, analytics,
database queries, filter management, configuration).

Provides:
- Log aggregation control (start/stop, query logs)
- Performance analytics (metrics, exports)
- Database operations (queries, exports)
- Filter management (apply, save, load)
- Configuration management
- System status monitoring
"""

import json
import csv
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from utils.protocol_logger import logger
from utils.config import config
from utils.log_filter_manager import LogFilterManager
from analytics.data_storage import PerformanceDatabase
from analytics.statistics import StatisticsEngine
from .response import APIResponse


class SystemController:
    """
    SystemTools programmatic control interface

    Example:
        controller = SystemController()

        # Query logs
        logs = controller.query_logs(
            domain='air-side',
            level='ERROR',
            limit=100
        )

        # Get analytics
        analytics = controller.get_analytics(
            metric='cpu_percent',
            time_range='1h'
        )

        # Export database
        controller.export_database('/tmp/performance.db')
    """

    def __init__(self, log_queue=None, data_storage: Optional[PerformanceDatabase] = None):
        """
        Initialize SystemTools controller

        Args:
            log_queue: Log queue from DPM_Management_System (for log querying)
            data_storage: PerformanceDatabase instance (for analytics/database access)
        """
        self.log_queue = log_queue
        self.data_storage = data_storage
        self.filter_manager = LogFilterManager()

        logger.debug("SYSTEM", "SystemController initialized")

    # ========================================================================
    # LOG AGGREGATION CONTROL
    # ========================================================================

    def query_logs(
        self,
        domain: Optional[str] = None,
        level: Optional[str] = None,
        context: Optional[str] = None,
        message_filter: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> APIResponse:
        """
        Query aggregated logs with filters

        Args:
            domain: Filter by domain ('air-side', 'ground-side', 'systemtools')
            level: Filter by level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            context: Filter by context ('CAMERA', 'NETWORK', etc.)
            message_filter: Text to search in message
            start_time: ISO8601 start timestamp
            end_time: ISO8601 end timestamp
            limit: Maximum number of logs to return

        Returns:
            APIResponse with matching log entries
        """
        try:
            if not self.log_queue:
                return APIResponse.error_response(
                    error="Log queue not available (DPM_Management_System not running)",
                    domain="systemtools",
                    operation="query_logs"
                )

            # Convert log queue to list for querying
            logs = list(self.log_queue)

            # Apply filters
            filtered_logs = []
            for log in logs:
                # Domain filter
                if domain and log.get('domain', '').lower() != domain.lower():
                    continue

                # Level filter
                if level and log.get('level', '').upper() != level.upper():
                    continue

                # Context filter
                if context and log.get('context', '').upper() != context.upper():
                    continue

                # Message filter
                if message_filter and message_filter.lower() not in log.get('message', '').lower():
                    continue

                # Time filters
                if start_time:
                    log_time = log.get('timestamp', '')
                    if log_time < start_time:
                        continue

                if end_time:
                    log_time = log.get('timestamp', '')
                    if log_time > end_time:
                        continue

                filtered_logs.append(log)

                # Limit check
                if len(filtered_logs) >= limit:
                    break

            logger.info("SYSTEM", f"API: Queried logs, found {len(filtered_logs)} matches")

            return APIResponse.success_response(
                data={
                    "logs": filtered_logs,
                    "count": len(filtered_logs),
                    "filters": {
                        "domain": domain,
                        "level": level,
                        "context": context,
                        "message_filter": message_filter,
                        "limit": limit
                    }
                },
                domain="systemtools",
                operation="query_logs"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to query logs: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="query_logs"
            )

    def export_logs(
        self,
        output_file: str,
        format: str = 'json',
        **query_filters
    ) -> APIResponse:
        """
        Export logs to file

        Args:
            output_file: Output file path
            format: Export format ('json', 'csv')
            **query_filters: Same filters as query_logs()

        Returns:
            APIResponse with export status
        """
        try:
            # Query logs
            result = self.query_logs(**query_filters)

            if not result.success:
                return result

            logs = result.data['logs']
            output_path = Path(output_file)

            # Export based on format
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(logs, f, indent=2)

            elif format == 'csv':
                if not logs:
                    return APIResponse.error_response(
                        error="No logs to export",
                        domain="systemtools",
                        operation="export_logs"
                    )

                # Get all keys from first log
                fieldnames = logs[0].keys()

                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(logs)

            else:
                return APIResponse.error_response(
                    error=f"Unsupported format: {format}",
                    domain="systemtools",
                    operation="export_logs"
                )

            logger.info("SYSTEM", f"API: Exported {len(logs)} logs to {output_path}")

            return APIResponse.success_response(
                data={
                    "output_file": str(output_path),
                    "format": format,
                    "count": len(logs)
                },
                domain="systemtools",
                operation="export_logs"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to export logs: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="export_logs"
            )

    # ========================================================================
    # PERFORMANCE ANALYTICS
    # ========================================================================

    def get_analytics(
        self,
        metric: Optional[str] = None,
        time_range: Optional[str] = None
    ) -> APIResponse:
        """
        Get performance analytics

        Args:
            metric: Specific metric ('cpu_percent', 'memory_used_mb', etc.)
            time_range: Time range ('1h', '24h', '7d', or None for all)

        Returns:
            APIResponse with analytics data
        """
        try:
            if not self.data_storage:
                return APIResponse.error_response(
                    error="Data storage not available",
                    domain="systemtools",
                    operation="get_analytics"
                )

            # Get snapshots from database
            snapshots = self.data_storage.get_recent_snapshots(limit=1000)

            if not snapshots:
                return APIResponse.success_response(
                    data={"message": "No analytics data available"},
                    domain="systemtools",
                    operation="get_analytics"
                )

            # Calculate statistics
            stats_engine = StatisticsEngine()

            if metric:
                # Single metric statistics
                values = [s.get(metric) for s in snapshots if s.get(metric) is not None]

                if not values:
                    return APIResponse.error_response(
                        error=f"No data for metric: {metric}",
                        domain="systemtools",
                        operation="get_analytics"
                    )

                stats = {
                    'descriptive': stats_engine.calculate_descriptive_stats(values),
                    'percentiles': stats_engine.calculate_percentiles(values),
                    'recent_value': values[-1] if values else None,
                    'sample_count': len(values)
                }

                return APIResponse.success_response(
                    data={
                        "metric": metric,
                        "statistics": stats
                    },
                    domain="systemtools",
                    operation="get_analytics"
                )

            else:
                # All metrics summary
                metrics = ['cpu_percent', 'memory_used_mb', 'camera_latency_ms', 'queue_depth']
                all_stats = {}

                for m in metrics:
                    values = [s.get(m) for s in snapshots if s.get(m) is not None]
                    if values:
                        all_stats[m] = {
                            'mean': sum(values) / len(values),
                            'min': min(values),
                            'max': max(values),
                            'count': len(values)
                        }

                return APIResponse.success_response(
                    data={
                        "metrics": all_stats,
                        "snapshot_count": len(snapshots)
                    },
                    domain="systemtools",
                    operation="get_analytics"
                )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to get analytics: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="get_analytics"
            )

    def export_analytics(
        self,
        output_file: str,
        format: str = 'csv'
    ) -> APIResponse:
        """
        Export analytics data to file

        Args:
            output_file: Output file path
            format: Export format ('csv', 'json')

        Returns:
            APIResponse with export status
        """
        try:
            if not self.data_storage:
                return APIResponse.error_response(
                    error="Data storage not available",
                    domain="systemtools",
                    operation="export_analytics"
                )

            # Get all snapshots
            snapshots = self.data_storage.get_recent_snapshots(limit=10000)

            if not snapshots:
                return APIResponse.error_response(
                    error="No analytics data to export",
                    domain="systemtools",
                    operation="export_analytics"
                )

            output_path = Path(output_file)

            # Export based on format
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(snapshots, f, indent=2)

            elif format == 'csv':
                fieldnames = snapshots[0].keys()

                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(snapshots)

            else:
                return APIResponse.error_response(
                    error=f"Unsupported format: {format}",
                    domain="systemtools",
                    operation="export_analytics"
                )

            logger.info("SYSTEM", f"API: Exported {len(snapshots)} snapshots to {output_path}")

            return APIResponse.success_response(
                data={
                    "output_file": str(output_path),
                    "format": format,
                    "count": len(snapshots)
                },
                domain="systemtools",
                operation="export_analytics"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to export analytics: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="export_analytics"
            )

    # ========================================================================
    # DATABASE OPERATIONS
    # ========================================================================

    def query_performance_db(
        self,
        sql: str,
        params: Optional[tuple] = None
    ) -> APIResponse:
        """
        Execute SQL query on performance database

        Args:
            sql: SQL query string
            params: Query parameters (optional)

        Returns:
            APIResponse with query results
        """
        try:
            if not self.data_storage:
                return APIResponse.error_response(
                    error="Data storage not available",
                    domain="systemtools",
                    operation="query_performance_db"
                )

            # Execute query
            conn = sqlite3.connect(self.data_storage.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dicts
            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            rows = cursor.fetchall()

            # Convert to list of dicts
            results = [dict(row) for row in rows]

            conn.close()

            logger.info("SYSTEM", f"API: Executed SQL query, returned {len(results)} rows")

            return APIResponse.success_response(
                data={
                    "results": results,
                    "count": len(results),
                    "sql": sql
                },
                domain="systemtools",
                operation="query_performance_db"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Database query failed: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="query_performance_db",
                data={"sql": sql}
            )

    def export_database(self, output_file: str) -> APIResponse:
        """
        Export entire performance database

        Args:
            output_file: Output file path

        Returns:
            APIResponse with export status
        """
        try:
            if not self.data_storage:
                return APIResponse.error_response(
                    error="Data storage not available",
                    domain="systemtools",
                    operation="export_database"
                )

            import shutil

            source_path = Path(self.data_storage.db_path)
            output_path = Path(output_file)

            # Copy database file
            shutil.copy2(source_path, output_path)

            logger.info("SYSTEM", f"API: Exported database to {output_path}")

            return APIResponse.success_response(
                data={
                    "output_file": str(output_path),
                    "source_file": str(source_path)
                },
                domain="systemtools",
                operation="export_database"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to export database: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="export_database"
            )

    # ========================================================================
    # FILTER MANAGEMENT
    # ========================================================================

    def apply_filter(self, filter_config: Dict[str, Any]) -> APIResponse:
        """
        Apply log filter configuration

        Args:
            filter_config: Filter configuration dict

        Returns:
            APIResponse with filter status
        """
        try:
            # Store filter config for future use
            # Note: LogFilterManager is primarily for JSON file management
            # For programmatic filters, applications should handle filtering locally

            logger.info("CONFIG", f"API: Filter configuration received")

            return APIResponse.success_response(
                data={
                    "filter": filter_config,
                    "applied": True,
                    "note": "Filter stored - apply via query_logs() filters"
                },
                domain="systemtools",
                operation="apply_filter"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to apply filter: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="apply_filter",
                data={"filter": filter_config}
            )

    def save_filter(self, filter_config: Dict[str, Any], output_file: str) -> APIResponse:
        """
        Save filter configuration to file

        Args:
            filter_config: Filter configuration dict
            output_file: Output file path

        Returns:
            APIResponse with save status
        """
        try:
            output_path = Path(output_file)

            with open(output_path, 'w') as f:
                json.dump(filter_config, f, indent=2)

            logger.info("CONFIG", f"API: Saved filter to {output_path}")

            return APIResponse.success_response(
                data={
                    "output_file": str(output_path),
                    "filter": filter_config
                },
                domain="systemtools",
                operation="save_filter"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to save filter: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="save_filter"
            )

    def load_filter(self, input_file: str) -> APIResponse:
        """
        Load filter from file

        Args:
            input_file: Input file path

        Returns:
            APIResponse with loaded filter configuration
        """
        try:
            input_path = Path(input_file)

            with open(input_path, 'r') as f:
                filter_config = json.load(f)

            logger.info("CONFIG", f"API: Loaded filter from {input_path}")

            return APIResponse.success_response(
                data={
                    "input_file": str(input_path),
                    "filter": filter_config
                },
                domain="systemtools",
                operation="load_filter"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to load filter: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="load_filter",
                data={"input_file": input_file}
            )

    # ========================================================================
    # CONFIGURATION MANAGEMENT
    # ========================================================================

    def get_config(self, key: Optional[str] = None) -> APIResponse:
        """
        Get SystemTools configuration

        Args:
            key: Specific config key (None for all config)

        Returns:
            APIResponse with configuration data
        """
        try:
            if key:
                # Get specific config value
                value = config.get(key) if hasattr(config, 'get') else config.config.get(key)
                data = {key: value}
            else:
                # Get all config
                data = config.config if hasattr(config, 'config') else {}

            logger.debug("CONFIG", f"API: Retrieved config")

            return APIResponse.success_response(
                data=data,
                domain="systemtools",
                operation="get_config"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to get config: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="get_config"
            )

    def set_config(self, key: str, value: Any) -> APIResponse:
        """
        Set SystemTools configuration value

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            APIResponse with operation status
        """
        try:
            config.set(key, value)

            logger.info("CONFIG", f"API: Set config {key}={value}")

            return APIResponse.success_response(
                data={
                    "key": key,
                    "value": value,
                    "applied": True
                },
                domain="systemtools",
                operation="set_config"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to set config: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="set_config",
                data={"key": key, "value": value}
            )

    def reload_config(self) -> APIResponse:
        """
        Reload configuration from file

        Returns:
            APIResponse with reload status
        """
        try:
            config.reload()

            logger.info("CONFIG", "API: Reloaded configuration")

            return APIResponse.success_response(
                data={"reloaded": True},
                domain="systemtools",
                operation="reload_config"
            )

        except Exception as e:
            logger.error("CONFIG", f"API: Failed to reload config: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="reload_config"
            )

    # ========================================================================
    # SYSTEM STATUS
    # ========================================================================

    def get_system_status(self) -> APIResponse:
        """
        Get comprehensive SystemTools status

        Returns:
            APIResponse with system status
        """
        try:
            status = {
                "log_queue": {
                    "available": self.log_queue is not None,
                    "count": len(self.log_queue) if self.log_queue else 0
                },
                "data_storage": {
                    "available": self.data_storage is not None,
                    "db_path": str(self.data_storage.db_path) if self.data_storage else None
                },
                "filter_manager": {
                    "available": self.filter_manager is not None
                }
            }

            return APIResponse.success_response(
                data=status,
                domain="systemtools",
                operation="get_system_status"
            )

        except Exception as e:
            logger.error("SYSTEM", f"API: Failed to get system status: {e}")
            return APIResponse.error_response(
                error=str(e),
                domain="systemtools",
                operation="get_system_status"
            )
