"""
Statistics Engine - Calculate descriptive statistics and trends
"""

import numpy as np
from typing import List, Dict, Any, Optional
from utils.logger import logger


class StatisticsEngine:
    """Calculate statistical metrics for performance analysis"""

    @staticmethod
    def calculate_descriptive_stats(data: List[float]) -> Dict[str, Any]:
        """
        Calculate descriptive statistics for a data series

        Args:
            data: List of numeric values

        Returns:
            Dictionary with mean, median, min, max, std_dev, variance
        """
        if not data or len(data) == 0:
            return {
                'mean': None,
                'median': None,
                'min': None,
                'max': None,
                'std_dev': None,
                'variance': None,
                'count': 0
            }

        try:
            arr = np.array(data)

            stats = {
                'mean': float(np.mean(arr)),
                'median': float(np.median(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'std_dev': float(np.std(arr)),
                'variance': float(np.var(arr)),
                'count': len(data)
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to calculate descriptive stats: {e}")
            return {
                'mean': None,
                'median': None,
                'min': None,
                'max': None,
                'std_dev': None,
                'variance': None,
                'count': len(data)
            }

    @staticmethod
    def calculate_percentiles(data: List[float], percentiles: List[int] = [50, 95, 99]) -> Dict[str, float]:
        """
        Calculate percentiles for a data series

        Args:
            data: List of numeric values
            percentiles: List of percentiles to calculate (default: [50, 95, 99])

        Returns:
            Dictionary mapping percentile labels to values (e.g., {'p50': 42.1, 'p95': 78.3})
        """
        if not data or len(data) == 0:
            return {f'p{p}': None for p in percentiles}

        try:
            arr = np.array(data)
            result = {}

            for p in percentiles:
                value = np.percentile(arr, p)
                result[f'p{p}'] = float(value)

            return result

        except Exception as e:
            logger.error(f"Failed to calculate percentiles: {e}")
            return {f'p{p}': None for p in percentiles}

    @staticmethod
    def calculate_moving_average(data: List[float], window_size: int = 5) -> List[float]:
        """
        Calculate simple moving average

        Args:
            data: List of numeric values
            window_size: Number of points to average (default: 5)

        Returns:
            List of moving average values (same length as input, padded with None)
        """
        if not data or len(data) == 0:
            return []

        if len(data) < window_size:
            # Not enough data for moving average
            return [None] * len(data)

        try:
            arr = np.array(data)
            moving_avg = np.convolve(arr, np.ones(window_size)/window_size, mode='valid')

            # Pad the beginning with None to match original length
            padding = [None] * (window_size - 1)
            result = padding + moving_avg.tolist()

            return result

        except Exception as e:
            logger.error(f"Failed to calculate moving average: {e}")
            return [None] * len(data)

    @staticmethod
    def calculate_rate_of_change(current: float, previous: float, time_delta_sec: float) -> Optional[float]:
        """
        Calculate rate of change (derivative)

        Args:
            current: Current value
            previous: Previous value
            time_delta_sec: Time difference in seconds

        Returns:
            Rate of change per second, or None if invalid
        """
        if previous is None or current is None or time_delta_sec <= 0:
            return None

        try:
            rate = (current - previous) / time_delta_sec
            return float(rate)
        except Exception as e:
            logger.error(f"Failed to calculate rate of change: {e}")
            return None

    @staticmethod
    def calculate_z_score(value: float, mean: float, std_dev: float) -> Optional[float]:
        """
        Calculate Z-score (number of standard deviations from mean)

        Args:
            value: Value to calculate Z-score for
            mean: Population mean
            std_dev: Population standard deviation

        Returns:
            Z-score, or None if std_dev is 0 or invalid
        """
        if value is None or mean is None or std_dev is None:
            return None

        if std_dev == 0:
            return None  # Cannot calculate Z-score with zero std dev

        try:
            z_score = (value - mean) / std_dev
            return float(z_score)
        except Exception as e:
            logger.error(f"Failed to calculate Z-score: {e}")
            return None

    @staticmethod
    def analyze_metric(snapshots: List[Dict[str, Any]], metric_path: str) -> Dict[str, Any]:
        """
        Comprehensive statistical analysis of a metric from snapshot list

        Args:
            snapshots: List of health snapshot dictionaries
            metric_path: Dot-notation path to metric (e.g., 'cpu_percent' or 'camera_latency_ms')

        Returns:
            Dictionary with comprehensive statistics
        """
        if not snapshots or len(snapshots) == 0:
            return {
                'metric': metric_path,
                'descriptive': {},
                'percentiles': {},
                'data_points': 0,
                'valid_points': 0
            }

        try:
            # Extract metric values
            values = []
            for snapshot in snapshots:
                value = snapshot.get(metric_path)
                if value is not None:
                    values.append(float(value))

            if len(values) == 0:
                return {
                    'metric': metric_path,
                    'descriptive': {},
                    'percentiles': {},
                    'data_points': len(snapshots),
                    'valid_points': 0
                }

            # Calculate statistics
            descriptive = StatisticsEngine.calculate_descriptive_stats(values)
            percentiles = StatisticsEngine.calculate_percentiles(values, [50, 95, 99])

            result = {
                'metric': metric_path,
                'descriptive': descriptive,
                'percentiles': percentiles,
                'data_points': len(snapshots),
                'valid_points': len(values),
                'current': values[-1] if values else None  # Most recent value
            }

            return result

        except Exception as e:
            logger.error(f"Failed to analyze metric '{metric_path}': {e}")
            return {
                'metric': metric_path,
                'descriptive': {},
                'percentiles': {},
                'data_points': len(snapshots),
                'valid_points': 0
            }

    @staticmethod
    def format_stats_display(stats: Dict[str, Any], metric_name: str, unit: str = "") -> str:
        """
        Format statistics for display in UI

        Args:
            stats: Statistics dictionary from analyze_metric()
            metric_name: Human-readable metric name
            unit: Unit of measurement (e.g., "%", "ms", "MB")

        Returns:
            Formatted multi-line string for display
        """
        if stats['valid_points'] == 0:
            return f"{metric_name}: No data available"

        desc = stats['descriptive']
        perc = stats['percentiles']

        lines = [
            f"{metric_name}:",
            f"  Mean: {desc['mean']:.1f}{unit}   Min: {desc['min']:.1f}{unit}   Max: {desc['max']:.1f}{unit}",
            f"  Std Dev: {desc['std_dev']:.1f}{unit}   P95: {perc['p95']:.1f}{unit}   Current: {stats['current']:.1f}{unit}"
        ]

        return "\n".join(lines)
