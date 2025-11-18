"""
Anomaly Detection - Identify unusual patterns in health metrics
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from utils.logger import logger
from .statistics import StatisticsEngine


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Anomaly detection alert"""
    timestamp: datetime
    severity: AlertSeverity
    metric_name: str
    metric_value: float
    threshold_value: Optional[float]
    message: str
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/display"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'threshold_value': self.threshold_value,
            'message': self.message,
            'recommendation': self.recommendation
        }


class AnomalyDetector:
    """Detect anomalies in health metrics using multiple algorithms"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize anomaly detector

        Args:
            config: Configuration dictionary with thresholds
        """
        self.config = config
        self.alerts: List[Alert] = []
        self.max_alerts = 100  # Keep last 100 alerts

        logger.info("AnomalyDetector initialized")

    def check_threshold(
        self,
        metric_name: str,
        value: float,
        warn_threshold: Optional[float],
        critical_threshold: Optional[float],
        check_type: str = "above"
    ) -> Optional[Alert]:
        """
        Check if value exceeds warn/critical thresholds

        Args:
            metric_name: Human-readable metric name
            value: Current metric value
            warn_threshold: Warning threshold
            critical_threshold: Critical threshold
            check_type: "above" or "below" (default: "above")

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if value is None:
            return None

        try:
            # Check critical threshold first
            if critical_threshold is not None:
                if check_type == "above" and value >= critical_threshold:
                    alert = Alert(
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.CRITICAL,
                        metric_name=metric_name,
                        metric_value=value,
                        threshold_value=critical_threshold,
                        message=f"{metric_name}: {value:.1f} (critical threshold: {critical_threshold:.1f})",
                        recommendation=self._get_recommendation(metric_name, "critical")
                    )
                    self._add_alert(alert)
                    return alert

                elif check_type == "below" and value <= critical_threshold:
                    alert = Alert(
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.CRITICAL,
                        metric_name=metric_name,
                        metric_value=value,
                        threshold_value=critical_threshold,
                        message=f"{metric_name}: {value:.1f} (critical threshold: {critical_threshold:.1f})",
                        recommendation=self._get_recommendation(metric_name, "critical")
                    )
                    self._add_alert(alert)
                    return alert

            # Check warning threshold
            if warn_threshold is not None:
                if check_type == "above" and value >= warn_threshold:
                    alert = Alert(
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.WARNING,
                        metric_name=metric_name,
                        metric_value=value,
                        threshold_value=warn_threshold,
                        message=f"{metric_name}: {value:.1f} (warning threshold: {warn_threshold:.1f})",
                        recommendation=self._get_recommendation(metric_name, "warning")
                    )
                    self._add_alert(alert)
                    return alert

                elif check_type == "below" and value <= warn_threshold:
                    alert = Alert(
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.WARNING,
                        metric_name=metric_name,
                        metric_value=value,
                        threshold_value=warn_threshold,
                        message=f"{metric_name}: {value:.1f} (warning threshold: {warn_threshold:.1f})",
                        recommendation=self._get_recommendation(metric_name, "warning")
                    )
                    self._add_alert(alert)
                    return alert

            return None

        except Exception as e:
            logger.error(f"Failed to check threshold for {metric_name}: {e}")
            return None

    def check_z_score(
        self,
        metric_name: str,
        value: float,
        mean: float,
        std_dev: float,
        threshold: float = 3.0
    ) -> Optional[Alert]:
        """
        Check if value is an outlier using Z-score

        Args:
            metric_name: Human-readable metric name
            value: Current metric value
            mean: Population mean
            std_dev: Population standard deviation
            threshold: Z-score threshold (default: 3.0 = 99.7% confidence)

        Returns:
            Alert if outlier detected, None otherwise
        """
        if value is None or mean is None or std_dev is None:
            return None

        if std_dev == 0:
            return None  # Cannot calculate Z-score

        try:
            z_score = StatisticsEngine.calculate_z_score(value, mean, std_dev)

            if z_score is None:
                return None

            if abs(z_score) >= threshold:
                alert = Alert(
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.INFO,
                    metric_name=metric_name,
                    metric_value=value,
                    threshold_value=None,
                    message=f"{metric_name} outlier detected: {value:.1f} (Z-score: {z_score:.2f})",
                    recommendation="Monitor for repeated occurrences"
                )
                self._add_alert(alert)
                return alert

            return None

        except Exception as e:
            logger.error(f"Failed to check Z-score for {metric_name}: {e}")
            return None

    def check_rate_of_change(
        self,
        metric_name: str,
        current_value: float,
        previous_value: float,
        time_delta_sec: float,
        threshold_percent: float = 30.0
    ) -> Optional[Alert]:
        """
        Check for sudden changes (spikes) in metric value

        Args:
            metric_name: Human-readable metric name
            current_value: Current metric value
            previous_value: Previous metric value
            time_delta_sec: Time difference in seconds
            threshold_percent: Percentage change threshold (default: 30%)

        Returns:
            Alert if sudden change detected, None otherwise
        """
        if current_value is None or previous_value is None or time_delta_sec <= 0:
            return None

        if previous_value == 0:
            return None  # Cannot calculate percent change

        try:
            # Calculate percent change
            percent_change = abs((current_value - previous_value) / previous_value) * 100

            if percent_change >= threshold_percent:
                alert = Alert(
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.WARNING,
                    metric_name=metric_name,
                    metric_value=current_value,
                    threshold_value=previous_value,
                    message=f"{metric_name} spike: {previous_value:.1f} → {current_value:.1f} ({percent_change:.0f}% in {time_delta_sec:.0f}s)",
                    recommendation=f"Investigate {metric_name} activity at this timestamp"
                )
                self._add_alert(alert)
                return alert

            return None

        except Exception as e:
            logger.error(f"Failed to check rate of change for {metric_name}: {e}")
            return None

    def analyze_snapshot(
        self,
        snapshot: Dict[str, Any],
        previous_snapshot: Optional[Dict[str, Any]] = None,
        stats: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[Alert]:
        """
        Comprehensive anomaly analysis of a health snapshot

        Args:
            snapshot: Current health snapshot
            previous_snapshot: Previous snapshot for rate-of-change detection (optional)
            stats: Pre-calculated statistics for Z-score detection (optional)

        Returns:
            List of detected alerts
        """
        alerts = []

        try:
            # Threshold-based checks
            thresholds = self.config.get('alert_thresholds', {})

            # CPU check
            cpu = snapshot.get('cpu_percent')
            if cpu is not None:
                alert = self.check_threshold(
                    "CPU Usage",
                    cpu,
                    thresholds.get('cpu_warn'),
                    thresholds.get('cpu_critical'),
                    check_type="above"
                )
                if alert:
                    alerts.append(alert)

            # Memory check
            memory_used = snapshot.get('memory_used_mb')
            if memory_used is not None:
                alert = self.check_threshold(
                    "Memory Used",
                    memory_used,
                    thresholds.get('memory_warn_mb'),
                    thresholds.get('memory_critical_mb'),
                    check_type="above"
                )
                if alert:
                    alerts.append(alert)

            # Camera latency check
            camera_latency = snapshot.get('camera_latency_ms')
            if camera_latency is not None:
                alert = self.check_threshold(
                    "Camera SDK Latency",
                    camera_latency,
                    thresholds.get('camera_latency_warn_ms'),
                    thresholds.get('camera_latency_critical_ms'),
                    check_type="above"
                )
                if alert:
                    alerts.append(alert)

            # Queue depth check
            queue_depth = snapshot.get('queue_depth')
            if queue_depth is not None:
                alert = self.check_threshold(
                    "Command Queue Depth",
                    queue_depth,
                    thresholds.get('queue_depth_warn'),
                    thresholds.get('queue_depth_critical'),
                    check_type="above"
                )
                if alert:
                    alerts.append(alert)

            # Rate of change checks (if previous snapshot available)
            if previous_snapshot:
                # Calculate time delta
                current_ts = snapshot.get('timestamp')
                prev_ts = previous_snapshot.get('timestamp')

                if current_ts and prev_ts:
                    if isinstance(current_ts, str):
                        current_ts = datetime.fromisoformat(current_ts.replace('Z', '+00:00'))
                    if isinstance(prev_ts, str):
                        prev_ts = datetime.fromisoformat(prev_ts.replace('Z', '+00:00'))

                    time_delta = (current_ts - prev_ts).total_seconds()

                    # CPU spike check
                    prev_cpu = previous_snapshot.get('cpu_percent')
                    if cpu is not None and prev_cpu is not None:
                        alert = self.check_rate_of_change(
                            "CPU Usage",
                            cpu,
                            prev_cpu,
                            time_delta,
                            threshold_percent=30.0
                        )
                        if alert:
                            alerts.append(alert)

            # Z-score checks (if statistics available)
            if stats:
                anomaly_config = self.config.get('anomaly_detection', {})
                z_threshold = anomaly_config.get('z_score_threshold', 3.0)

                # CPU Z-score
                if cpu is not None and 'cpu_percent' in stats:
                    cpu_stats = stats['cpu_percent']['descriptive']
                    alert = self.check_z_score(
                        "CPU Usage",
                        cpu,
                        cpu_stats.get('mean'),
                        cpu_stats.get('std_dev'),
                        threshold=z_threshold
                    )
                    if alert:
                        alerts.append(alert)

            return alerts

        except Exception as e:
            logger.error(f"Failed to analyze snapshot: {e}")
            return alerts

    def _add_alert(self, alert: Alert):
        """Add alert to history (FIFO with max limit)"""
        self.alerts.append(alert)

        # Keep only last N alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]

        logger.debug(f"Alert added: {alert.severity.value} - {alert.message}")

    def _get_recommendation(self, metric_name: str, severity: str) -> Optional[str]:
        """Get recommendation for a metric threshold breach"""
        recommendations = {
            ("CPU Usage", "critical"): "Investigate high CPU processes, consider optimization",
            ("CPU Usage", "warning"): "Monitor CPU usage trends",
            ("Memory Used", "critical"): "Memory exhaustion imminent, restart may be needed",
            ("Memory Used", "warning"): "Monitor memory usage, check for leaks",
            ("Camera SDK Latency", "critical"): "Check USB connection or restart camera",
            ("Camera SDK Latency", "warning"): "Monitor camera latency, may indicate USB issues",
            ("Command Queue Depth", "critical"): "Command queue critically deep, system may be unresponsive",
            ("Command Queue Depth", "warning"): "Command queue building up, investigate"
        }

        return recommendations.get((metric_name, severity))

    def get_recent_alerts(self, limit: int = 20) -> List[Alert]:
        """Get most recent alerts"""
        return self.alerts[-limit:] if self.alerts else []

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        logger.info("Alerts cleared")

    def get_alert_summary(self) -> Dict[str, int]:
        """Get count of alerts by severity"""
        summary = {
            'critical': 0,
            'warning': 0,
            'info': 0,
            'total': len(self.alerts)
        }

        for alert in self.alerts:
            summary[alert.severity.value] += 1

        return summary
