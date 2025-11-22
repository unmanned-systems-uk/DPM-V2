"""
Mission Readiness Scorer - Calculate overall system readiness for drone operation
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
from utils.protocol_logger import logger


class ReadinessScorer:
    """
    Calculate mission readiness score based on system health metrics

    Scores each component (CPU, Memory, Camera, Network, Disk) and provides
    an overall readiness percentage with actionable recommendations.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize readiness scorer

        Args:
            config: Configuration dictionary with alert thresholds
        """
        self.config = config
        self.thresholds = config.get('alert_thresholds', {})

        # Component weights (total = 1.0)
        self.weights = {
            'cpu': 0.15,
            'memory': 0.20,
            'disk': 0.15,
            'camera': 0.30,  # Most critical for drone operation
            'network': 0.20
        }

        logger.debug("HEALTH", "ReadinessScorer initialized")

    def calculate_readiness(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall mission readiness from current health snapshot

        Args:
            snapshot: Current health snapshot

        Returns:
            Dictionary with overall score, component scores, and recommendations
        """
        if not snapshot:
            return {
                'overall_score': 0,
                'overall_status': 'NO DATA',
                'component_scores': {},
                'recommendations': ['No health data available'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        try:
            # Calculate individual component scores
            cpu_score, cpu_status = self._score_cpu(snapshot)
            memory_score, memory_status = self._score_memory(snapshot)
            disk_score, disk_status = self._score_disk(snapshot)
            camera_score, camera_status = self._score_camera(snapshot)
            network_score, network_status = self._score_network(snapshot)

            # Calculate weighted overall score
            overall_score = (
                cpu_score * self.weights['cpu'] +
                memory_score * self.weights['memory'] +
                disk_score * self.weights['disk'] +
                camera_score * self.weights['camera'] +
                network_score * self.weights['network']
            )

            # Determine overall status
            overall_status = self._get_status_label(overall_score)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                snapshot,
                cpu_score, memory_score, disk_score, camera_score, network_score
            )

            result = {
                'overall_score': round(overall_score, 1),
                'overall_status': overall_status,
                'component_scores': {
                    'cpu': {'score': round(cpu_score, 1), 'status': cpu_status},
                    'memory': {'score': round(memory_score, 1), 'status': memory_status},
                    'disk': {'score': round(disk_score, 1), 'status': disk_status},
                    'camera': {'score': round(camera_score, 1), 'status': camera_status},
                    'network': {'score': round(network_score, 1), 'status': network_status}
                },
                'recommendations': recommendations,
                'timestamp': snapshot.get('timestamp', datetime.now(timezone.utc)).isoformat() if isinstance(snapshot.get('timestamp'), datetime) else snapshot.get('timestamp', datetime.now(timezone.utc).isoformat())
            }

            logger.debug("HEALTH", f"Readiness calculated: {overall_score:.1f}% ({overall_status})")
            return result

        except Exception as e:
            logger.error("HEALTH", f"Failed to calculate readiness: {e}")
            return {
                'overall_score': 0,
                'overall_status': 'ERROR',
                'component_scores': {},
                'recommendations': [f'Error calculating readiness: {e}'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _score_cpu(self, snapshot: Dict[str, Any]) -> Tuple[float, str]:
        """Score CPU usage (0-100)"""
        cpu = snapshot.get('cpu_percent')
        if cpu is None:
            return (50.0, 'UNKNOWN')

        cpu_warn = self.thresholds.get('cpu_warn', 70)
        cpu_crit = self.thresholds.get('cpu_critical', 90)

        if cpu >= cpu_crit:
            return (0.0, 'CRITICAL')
        elif cpu >= cpu_warn:
            # Linear scale from warn to crit (100 → 50)
            score = 100 - ((cpu - cpu_warn) / (cpu_crit - cpu_warn) * 50)
            return (max(score, 50.0), 'DEGRADED')
        else:
            # Linear scale from 0 to warn (100 → 100)
            score = 100 - (cpu / cpu_warn * 0)  # Perfect until warning
            return (min(score, 100.0), 'GOOD')

    def _score_memory(self, snapshot: Dict[str, Any]) -> Tuple[float, str]:
        """Score memory usage (0-100)"""
        memory_used = snapshot.get('memory_used_mb')
        if memory_used is None:
            return (50.0, 'UNKNOWN')

        mem_warn = self.thresholds.get('memory_warn_mb', 6000)
        mem_crit = self.thresholds.get('memory_critical_mb', 7000)

        if memory_used >= mem_crit:
            return (0.0, 'CRITICAL')
        elif memory_used >= mem_warn:
            score = 100 - ((memory_used - mem_warn) / (mem_crit - mem_warn) * 50)
            return (max(score, 50.0), 'DEGRADED')
        else:
            score = 100 - (memory_used / mem_warn * 0)
            return (min(score, 100.0), 'GOOD')

    def _score_disk(self, snapshot: Dict[str, Any]) -> Tuple[float, str]:
        """Score disk usage (0-100)"""
        disk_used = snapshot.get('disk_used_mb')
        if disk_used is None:
            return (50.0, 'UNKNOWN')

        disk_warn = self.thresholds.get('disk_warn_mb', 25000)
        disk_crit = self.thresholds.get('disk_critical_mb', 28000)

        if disk_used >= disk_crit:
            return (0.0, 'CRITICAL')
        elif disk_used >= disk_warn:
            score = 100 - ((disk_used - disk_warn) / (disk_crit - disk_warn) * 50)
            return (max(score, 50.0), 'DEGRADED')
        else:
            score = 100 - (disk_used / disk_warn * 0)
            return (min(score, 100.0), 'GOOD')

    def _score_camera(self, snapshot: Dict[str, Any]) -> Tuple[float, str]:
        """Score camera health (0-100)"""
        camera_connected = snapshot.get('camera_connected')
        camera_latency = snapshot.get('camera_latency_ms')

        # Camera must be connected
        if camera_connected is False:
            return (0.0, 'CRITICAL')
        elif camera_connected is None:
            return (50.0, 'UNKNOWN')

        # Check latency if available
        if camera_latency is not None:
            latency_warn = self.thresholds.get('camera_latency_warn_ms', 40)
            latency_crit = self.thresholds.get('camera_latency_critical_ms', 100)

            if camera_latency >= latency_crit:
                return (50.0, 'DEGRADED')
            elif camera_latency >= latency_warn:
                score = 100 - ((camera_latency - latency_warn) / (latency_crit - latency_warn) * 25)
                return (max(score, 75.0), 'DEGRADED')
            else:
                return (100.0, 'GOOD')

        # Connected but no latency data
        return (90.0, 'GOOD')

    def _score_network(self, snapshot: Dict[str, Any]) -> Tuple[float, str]:
        """Score network health (0-100)"""
        tcp_connected = snapshot.get('tcp_connected')
        queue_depth = snapshot.get('queue_depth')

        # TCP must be connected
        if tcp_connected is False:
            return (0.0, 'CRITICAL')
        elif tcp_connected is None:
            return (50.0, 'UNKNOWN')

        # Check queue depth if available
        if queue_depth is not None:
            queue_warn = self.thresholds.get('queue_depth_warn', 10)
            queue_crit = self.thresholds.get('queue_depth_critical', 50)

            if queue_depth >= queue_crit:
                return (50.0, 'DEGRADED')
            elif queue_depth >= queue_warn:
                score = 100 - ((queue_depth - queue_warn) / (queue_crit - queue_warn) * 25)
                return (max(score, 75.0), 'DEGRADED')
            else:
                return (100.0, 'GOOD')

        # Connected but no queue data
        return (90.0, 'GOOD')

    def _get_status_label(self, score: float) -> str:
        """Convert score to status label"""
        if score >= 90:
            return 'MISSION READY'
        elif score >= 75:
            return 'CAUTION'
        elif score >= 50:
            return 'DEGRADED'
        else:
            return 'NOT READY'

    def _generate_recommendations(
        self,
        snapshot: Dict[str, Any],
        cpu_score: float,
        memory_score: float,
        disk_score: float,
        camera_score: float,
        network_score: float
    ) -> List[str]:
        """Generate actionable recommendations based on component scores"""
        recommendations = []

        # CPU recommendations
        if cpu_score < 75:
            cpu = snapshot.get('cpu_percent', 0)
            if cpu >= self.thresholds.get('cpu_critical', 90):
                recommendations.append('CRITICAL: CPU usage extremely high - consider restarting system')
            elif cpu >= self.thresholds.get('cpu_warn', 70):
                recommendations.append('WARNING: CPU usage elevated - monitor for high processes')

        # Memory recommendations
        if memory_score < 75:
            mem = snapshot.get('memory_used_mb', 0)
            if mem >= self.thresholds.get('memory_critical_mb', 7000):
                recommendations.append('CRITICAL: Memory exhaustion imminent - restart required')
            elif mem >= self.thresholds.get('memory_warn_mb', 6000):
                recommendations.append('WARNING: Memory usage high - check for leaks')

        # Disk recommendations
        if disk_score < 75:
            disk = snapshot.get('disk_used_mb', 0)
            if disk >= self.thresholds.get('disk_critical_mb', 28000):
                recommendations.append('CRITICAL: Disk space critically low - clean up immediately')
            elif disk >= self.thresholds.get('disk_warn_mb', 25000):
                recommendations.append('WARNING: Disk space running low - consider cleanup')

        # Camera recommendations
        if camera_score < 75:
            if not snapshot.get('camera_connected'):
                recommendations.append('CRITICAL: Camera disconnected - check USB and Sony SDK')
            else:
                latency = snapshot.get('camera_latency_ms', 0)
                if latency >= self.thresholds.get('camera_latency_critical_ms', 100):
                    recommendations.append('WARNING: Camera latency high - check USB connection')
                elif latency >= self.thresholds.get('camera_latency_warn_ms', 40):
                    recommendations.append('CAUTION: Camera latency elevated - monitor performance')

        # Network recommendations
        if network_score < 75:
            if not snapshot.get('tcp_connected'):
                recommendations.append('CRITICAL: TCP disconnected - check network and Ground-Side')
            else:
                queue = snapshot.get('queue_depth', 0)
                if queue >= self.thresholds.get('queue_depth_critical', 50):
                    recommendations.append('WARNING: Command queue critically deep - system may be unresponsive')
                elif queue >= self.thresholds.get('queue_depth_warn', 10):
                    recommendations.append('CAUTION: Command queue building up - investigate responsiveness')

        # If everything is good
        if not recommendations:
            recommendations.append('All systems nominal - ready for mission')

        return recommendations
