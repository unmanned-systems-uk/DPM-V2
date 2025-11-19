"""
UDP Discovery Protocol Sender
==============================

Sends periodic UDP discovery heartbeats to Air-Side for automatic IP detection.
Air-Side extracts source IP from UDP packet to auto-configure log streaming.

Protocol:
- Target: Air-Side UDP port 5009
- Interval: 10 seconds (configurable)
- Payload: JSON {"type":"discovery","source":"systemtools"}
"""

import socket
import json
import threading
import time
from typing import Optional, Dict, Any
from utils.logger import logger


class UDPDiscoverySender:
    """
    Sends periodic UDP discovery packets to Air-Side

    Air-Side uses the source IP from these packets to automatically
    configure the destination for log streaming.
    """

    def __init__(self, target_host: str, target_port: int,
                 interval_seconds: int = 10, payload: Optional[Dict[str, Any]] = None):
        """
        Initialize UDP discovery sender

        Args:
            target_host: Air-Side IP address (e.g., "10.0.1.53")
            target_port: Air-Side discovery port (5009)
            interval_seconds: Seconds between heartbeats (default: 10)
            payload: JSON payload to send (default: {"type":"discovery","source":"systemtools"})
        """
        self.target_host = target_host
        self.target_port = target_port
        self.interval_seconds = interval_seconds
        self.payload = payload or {"type": "discovery", "source": "systemtools"}

        self.sock: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None

        logger.info(f"[DISCOVERY] UDPDiscoverySender initialized: {target_host}:{target_port} every {interval_seconds}s")

    def start(self):
        """Start sending discovery heartbeats"""
        if self.running:
            logger.warning("[DISCOVERY] UDPDiscoverySender already running")
            return

        try:
            # Create UDP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Start background thread
            self.running = True
            self.thread = threading.Thread(target=self._discovery_worker, daemon=True)
            self.thread.start()

            logger.info(f"[DISCOVERY] UDPDiscoverySender started → {self.target_host}:{self.target_port}")

        except Exception as e:
            logger.error(f"[DISCOVERY] Failed to start UDPDiscoverySender: {e}")
            self.running = False
            if self.sock:
                self.sock.close()
                self.sock = None

    def stop(self):
        """Stop sending discovery heartbeats"""
        if not self.running:
            return

        logger.info("[DISCOVERY] Stopping UDPDiscoverySender...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        if self.sock:
            self.sock.close()
            self.sock = None

        logger.info("[DISCOVERY] UDPDiscoverySender stopped")

    def _discovery_worker(self):
        """Background worker that sends periodic discovery packets"""
        payload_str = json.dumps(self.payload)
        payload_bytes = payload_str.encode('utf-8')

        logger.info(f"[DISCOVERY] Discovery worker started, sending: {payload_str}")

        while self.running:
            try:
                # Send discovery packet
                self.sock.sendto(payload_bytes, (self.target_host, self.target_port))
                logger.debug(f"[DISCOVERY] Sent discovery packet to {self.target_host}:{self.target_port}")

                # Wait for next interval
                time.sleep(self.interval_seconds)

            except Exception as e:
                logger.error(f"[DISCOVERY] Error sending discovery packet: {e}")
                time.sleep(self.interval_seconds)  # Continue trying

    def send_immediate(self):
        """Send discovery packet immediately (outside regular interval)"""
        if not self.sock:
            logger.warning("[DISCOVERY] Cannot send immediate discovery - socket not initialized")
            return

        try:
            payload_str = json.dumps(self.payload)
            payload_bytes = payload_str.encode('utf-8')
            self.sock.sendto(payload_bytes, (self.target_host, self.target_port))
            logger.info(f"[DISCOVERY] Sent immediate discovery packet to {self.target_host}:{self.target_port}")
        except Exception as e:
            logger.error(f"[DISCOVERY] Error sending immediate discovery packet: {e}")


def load_discovery_config() -> Dict[str, Any]:
    """Load discovery configuration from log_aggregator.json"""
    from pathlib import Path

    config_path = Path(__file__).parent.parent / "config" / "log_aggregator.json"

    if not config_path.exists():
        # Return defaults if config doesn't exist
        return {
            "enabled": True,
            "target_host": "10.0.1.53",
            "target_port": 5009,
            "interval_seconds": 10,
            "payload": {
                "type": "discovery",
                "source": "systemtools"
            }
        }

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config.get("network", {}).get("discovery", {
        "enabled": True,
        "target_host": "10.0.1.53",
        "target_port": 5009,
        "interval_seconds": 10,
        "payload": {"type": "discovery", "source": "systemtools"}
    })
