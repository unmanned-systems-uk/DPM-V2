"""
Log Parser for Air-Side Docker Logs
Extracts structured data from payload-manager logs
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class LogEntry:
    """Parsed log entry"""
    timestamp: datetime
    level: str
    thread_id: str
    message: str
    raw_line: str


@dataclass
class HeartbeatEvent:
    """Heartbeat event (sent or received)"""
    timestamp: datetime
    direction: str  # "sent" or "received"
    client_ip: str
    port: int
    sequence: int


@dataclass
class ClientInfo:
    """Connected client information"""
    ip: str
    ports: List[int] = field(default_factory=list)
    last_heartbeat: Optional[datetime] = None
    heartbeat_count: int = 0
    last_sequence: Optional[int] = None
    # Heartbeat timing analysis
    heartbeat_intervals: List[float] = field(default_factory=list)  # seconds between heartbeats
    avg_interval: float = 0.0
    fluctuation_detected: bool = False


@dataclass
class CameraEvent:
    """Camera connection/disconnection event"""
    timestamp: datetime
    event_type: str  # "connected" or "disconnected"
    details: str


@dataclass
class CommandEvent:
    """Camera command event"""
    timestamp: datetime
    command_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "unknown"  # "sent", "success", "failed"


class LogParser:
    """Parser for Air-Side payload-manager logs"""

    # Regex patterns
    LOG_PATTERN = re.compile(
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\] '
        r'\[(\w+)\] '
        r'\[(\d+)\] '
        r'(.+)'
    )

    HEARTBEAT_RECEIVED_PATTERN = re.compile(
        r'Received heartbeat from (?:ground|client) \(seq=(\d+)\)'
    )

    HEARTBEAT_SENT_PATTERN = re.compile(
        r'Sent heartbeat to ([\d.]+):(\d+) \(seq=(\d+)\)'
    )

    UDP_STATUS_PATTERN = re.compile(
        r'Sent UDP status to ([\d.]+):(\d+) \(seq=(\d+), bytes=(\d+)\)'
    )

    CAMERA_CONNECT_PATTERN = re.compile(
        r'[Cc]amera.*(connect|disconnect)',
        re.IGNORECASE
    )

    CAMERA_COMMAND_PATTERN = re.compile(
        r'(shutter|aperture|iso|white.?balance|focus|exposure)',
        re.IGNORECASE
    )

    def __init__(self):
        self.clients: Dict[str, ClientInfo] = {}
        self.heartbeat_events: List[HeartbeatEvent] = []
        self.camera_events: List[CameraEvent] = []
        self.command_events: List[CommandEvent] = []
        self.error_logs: List[LogEntry] = []

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse a single log line"""
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None

        timestamp_str, level, thread_id, message = match.groups()

        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return None

        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            thread_id=thread_id,
            message=message,
            raw_line=line
        )

        # Process based on content
        self._process_entry(entry)

        return entry

    def _process_entry(self, entry: LogEntry):
        """Process log entry to extract structured data"""

        # Check for heartbeat received
        match = self.HEARTBEAT_RECEIVED_PATTERN.search(entry.message)
        if match:
            seq = int(match.group(1))
            # Note: "from ground" doesn't include IP, we'll track by sequence
            event = HeartbeatEvent(
                timestamp=entry.timestamp,
                direction="received",
                client_ip="ground",  # Generic placeholder
                port=0,
                sequence=seq
            )
            self.heartbeat_events.append(event)
            return

        # Check for heartbeat sent
        match = self.HEARTBEAT_SENT_PATTERN.search(entry.message)
        if match:
            ip, port, seq = match.groups()
            event = HeartbeatEvent(
                timestamp=entry.timestamp,
                direction="sent",
                client_ip=ip,
                port=int(port),
                sequence=int(seq)
            )
            self.heartbeat_events.append(event)
            self._update_client_heartbeat(ip, int(port), entry.timestamp, int(seq))
            return

        # Check for UDP status (indicates active clients)
        match = self.UDP_STATUS_PATTERN.search(entry.message)
        if match:
            ip, port, seq, bytes_sent = match.groups()
            self._update_client_status(ip, int(port))
            return

        # Check for camera events
        match = self.CAMERA_CONNECT_PATTERN.search(entry.message)
        if match:
            event_type = "connected" if "connect" in match.group(1).lower() and "disconnect" not in match.group(1).lower() else "disconnected"
            camera_event = CameraEvent(
                timestamp=entry.timestamp,
                event_type=event_type,
                details=entry.message
            )
            self.camera_events.append(camera_event)
            return

        # Check for camera commands
        match = self.CAMERA_COMMAND_PATTERN.search(entry.message)
        if match:
            cmd_type = match.group(1).lower()
            command_event = CommandEvent(
                timestamp=entry.timestamp,
                command_type=cmd_type,
                parameters={},
                status="sent"
            )
            self.command_events.append(command_event)
            return

        # Check for errors
        if entry.level in ['ERROR', 'WARNING']:
            self.error_logs.append(entry)

    def _update_client_heartbeat(self, ip: str, port: int, timestamp: datetime, sequence: int):
        """Update client heartbeat tracking"""
        if ip not in self.clients:
            self.clients[ip] = ClientInfo(ip=ip)

        client = self.clients[ip]

        # Add port if new
        if port not in client.ports:
            client.ports.append(port)

        # Calculate interval if we have previous heartbeat
        if client.last_heartbeat:
            interval = (timestamp - client.last_heartbeat).total_seconds()
            client.heartbeat_intervals.append(interval)

            # Keep only last 10 intervals for average
            if len(client.heartbeat_intervals) > 10:
                client.heartbeat_intervals.pop(0)

            # Calculate average
            client.avg_interval = sum(client.heartbeat_intervals) / len(client.heartbeat_intervals)

            # Detect fluctuation (interval > 20% different from average)
            if len(client.heartbeat_intervals) >= 3:
                if abs(interval - client.avg_interval) > client.avg_interval * 0.2:
                    client.fluctuation_detected = True

        client.last_heartbeat = timestamp
        client.heartbeat_count += 1
        client.last_sequence = sequence

    def _update_client_status(self, ip: str, port: int):
        """Update client status from UDP messages"""
        if ip not in self.clients:
            self.clients[ip] = ClientInfo(ip=ip)

        if port not in self.clients[ip].ports:
            self.clients[ip].ports.append(port)

    def get_active_clients(self) -> List[ClientInfo]:
        """Get list of active clients"""
        return list(self.clients.values())

    def get_camera_events(self, limit: Optional[int] = None) -> List[CameraEvent]:
        """Get camera events"""
        events = self.camera_events
        if limit:
            events = events[-limit:]
        return events

    def get_heartbeat_events(self, client_ip: Optional[str] = None, limit: Optional[int] = None) -> List[HeartbeatEvent]:
        """Get heartbeat events, optionally filtered by client IP"""
        events = self.heartbeat_events
        if client_ip:
            events = [e for e in events if e.client_ip == client_ip]
        if limit:
            events = events[-limit:]
        return events

    def get_error_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        """Get error/warning logs"""
        logs = self.error_logs
        if limit:
            logs = logs[-limit:]
        return logs

    def get_command_stats(self) -> Dict[str, int]:
        """Get command statistics"""
        stats = {}
        for cmd in self.command_events:
            stats[cmd.command_type] = stats.get(cmd.command_type, 0) + 1
        return stats

    def clear(self):
        """Clear all parsed data"""
        self.clients.clear()
        self.heartbeat_events.clear()
        self.camera_events.clear()
        self.command_events.clear()
        self.error_logs.clear()
