"""
Statistics Engine - Calculate descriptive statistics and trends
"""

import numpy as np
import scipy.stats
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from utils.protocol_logger import logger


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
            logger.error("HEALTH", f"Failed to calculate descriptive stats: {e}")
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
            logger.error("HEALTH", f"Failed to calculate percentiles: {e}")
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
            logger.error("HEALTH", f"Failed to calculate moving average: {e}")
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
            logger.error("HEALTH", f"Failed to calculate rate of change: {e}")
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
            logger.error("HEALTH", f"Failed to calculate Z-score: {e}")
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
            logger.error("HEALTH", f"Failed to analyze metric '{metric_path}': {e}")
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

    @staticmethod
    def calculate_baseline(snapshots: List[Dict[str, Any]], metric_key: str, days: int = 7) -> Optional[Dict[str, float]]:
        """
        Calculate performance baseline (7-day rolling average ± 1.5σ)

        Args:
            snapshots: List of health snapshots
            metric_key: Metric to calculate baseline for
            days: Number of days for baseline calculation (default: 7)

        Returns:
            Dictionary with baseline_mean, baseline_std, lower_bound, upper_bound
        """
        if not snapshots or len(snapshots) == 0:
            return None

        try:
            # Extract metric values
            values = []
            for snapshot in snapshots:
                value = snapshot.get(metric_key)
                if value is not None:
                    values.append(float(value))

            if len(values) < 10:  # Need at least 10 points for meaningful baseline
                return None

            # Calculate baseline statistics
            arr = np.array(values)
            baseline_mean = float(np.mean(arr))
            baseline_std = float(np.std(arr))

            # Calculate bounds (mean ± 1.5σ)
            lower_bound = baseline_mean - (1.5 * baseline_std)
            upper_bound = baseline_mean + (1.5 * baseline_std)

            return {
                'baseline_mean': baseline_mean,
                'baseline_std': baseline_std,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'sample_size': len(values)
            }

        except Exception as e:
            logger.error("HEALTH", f"Failed to calculate baseline for {metric_key}: {e}")
            return None

    @staticmethod
    def predict_time_to_threshold(
        snapshots: List[Dict[str, Any]],
        metric_key: str,
        threshold: float
    ) -> Optional[Dict[str, Any]]:
        """
        Predict time until metric reaches threshold using linear regression

        Args:
            snapshots: List of health snapshots (time-ordered)
            metric_key: Metric to predict
            threshold: Threshold value to predict time-to-reach

        Returns:
            Dictionary with prediction info or None if cannot predict
        """
        if not snapshots or len(snapshots) < 10:
            return None

        try:
            # Extract timestamps and values
            times = []
            values = []

            for snapshot in snapshots:
                timestamp = snapshot.get('timestamp')
                value = snapshot.get(metric_key)

                if timestamp is not None and value is not None:
                    # Convert timestamp to datetime if string
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

                    times.append(timestamp)
                    values.append(float(value))

            if len(values) < 10:
                return None

            # Convert times to numeric (seconds since first timestamp)
            first_time = times[0]
            times_numeric = [(t - first_time).total_seconds() for t in times]

            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(times_numeric, values)

            # Check if trend is meaningful (r² > 0.5 and moving toward threshold)
            r_squared = r_value ** 2
            if r_squared < 0.5:
                return None  # Trend not strong enough

            current_value = values[-1]
            current_time = times[-1]

            # Calculate time to threshold
            # threshold = slope * t + intercept
            # t = (threshold - intercept) / slope

            if abs(slope) < 0.0001:  # Essentially flat
                return None

            # Check if trending toward threshold
            if slope > 0 and current_value >= threshold:
                return None  # Already above threshold
            if slope < 0 and current_value <= threshold:
                return None  # Already below threshold
            if slope > 0 and threshold < current_value:
                return None  # Threshold is below current value
            if slope < 0 and threshold > current_value:
                return None  # Threshold is above current value

            # Calculate time to threshold (seconds from first timestamp)
            time_to_threshold_sec = (threshold - intercept) / slope

            # Convert to actual datetime
            predicted_time = first_time + timedelta(seconds=time_to_threshold_sec)

            # Calculate time remaining from now
            time_remaining = predicted_time - current_time

            if time_remaining.total_seconds() < 0:
                return None  # Prediction is in the past

            result = {
                'threshold': threshold,
                'current_value': current_value,
                'predicted_time': predicted_time,
                'time_remaining_seconds': time_remaining.total_seconds(),
                'time_remaining_hours': time_remaining.total_seconds() / 3600,
                'slope': slope,
                'r_squared': r_squared,
                'confidence': 'high' if r_squared > 0.8 else 'medium'
            }

            logger.debug("HEALTH", f"Predicted {metric_key} to reach {threshold} in {result['time_remaining_hours']:.1f} hours")
            return result

        except Exception as e:
            logger.error("HEALTH", f"Failed to predict time to threshold for {metric_key}: {e}")
            return None

    @staticmethod
    def calculate_historical_comparison(
        current_snapshot: Dict[str, Any],
        historical_snapshots: List[Dict[str, Any]],
        metric_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare current metric value to historical data (same time yesterday/last week)

        Args:
            current_snapshot: Current health snapshot
            historical_snapshots: Historical snapshots for comparison
            metric_key: Metric to compare

        Returns:
            Dictionary with comparison data
        """
        if not current_snapshot or not historical_snapshots:
            return None

        try:
            current_value = current_snapshot.get(metric_key)
            if current_value is None:
                return None

            # Calculate average of historical values
            historical_values = []
            for snapshot in historical_snapshots:
                value = snapshot.get(metric_key)
                if value is not None:
                    historical_values.append(float(value))

            if len(historical_values) == 0:
                return None

            historical_avg = float(np.mean(historical_values))
            delta = current_value - historical_avg
            percent_change = (delta / historical_avg * 100) if historical_avg != 0 else 0

            # Determine status color
            if abs(percent_change) < 10:
                status = 'green'  # < 10% change
            elif abs(percent_change) < 25:
                status = 'yellow'  # 10-25% change
            else:
                status = 'red'  # > 25% change

            return {
                'current_value': current_value,
                'historical_avg': historical_avg,
                'delta': delta,
                'percent_change': percent_change,
                'status': status,
                'sample_size': len(historical_values)
            }

        except Exception as e:
            logger.error("HEALTH", f"Failed to calculate historical comparison for {metric_key}: {e}")
            return None
