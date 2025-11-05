"""
Heartbeat Sender for DPM Diagnostic Tool
Sends heartbeat messages to Air-Side at 1 Hz
"""

import socket
import threading
import time
from typing import Optional

from utils.logger import logger
from network.protocol import protocol_msg


class HeartbeatSender:
    """Sends UDP heartbeat messages to Air-Side

    Compliant with protocol/heartbeat_spec.json v1.1.0
    """

    def __init__(self, target_ip: str, target_port: int = 5002):
        self.target_ip = target_ip
        self.target_port = target_port

        self.socket: Optional[socket.socket] = None
        self.running = False
        self.send_thread: Optional[threading.Thread] = None

        # Uptime tracking (required by heartbeat_spec.json v1.1.0)
        self.start_time = time.time()

        # Statistics
        self.heartbeats_sent = 0
        self.last_sent_time = 0

    def start(self) -> bool:
        """Start sending heartbeats"""
        try:
            logger.info(f"Heartbeat: Starting sender to {self.target_ip}:{self.target_port}...")

            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            self.running = True

            # Start send thread
            self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.send_thread.start()

            logger.info(f"Heartbeat: Sender started")
            return True

        except Exception as e:
            logger.error(f"Heartbeat: Failed to start sender: {e}")
            return False

    def stop(self):
        """Stop sending heartbeats"""
        logger.info("Heartbeat: Stopping sender...")

        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        self.socket = None

        logger.info("Heartbeat: Sender stopped")

    def _send_loop(self):
        """Background thread to send heartbeats at 1 Hz

        Compliant with protocol/heartbeat_spec.json v1.1.0:
        - Sends at 1 Hz (1000ms interval)
        - Includes uptime_seconds in each heartbeat
        - Uses client_id = "WPC" (Windows PC)
        - Uses sender = "ground"
        """
        while self.running:
            try:
                # Calculate uptime in seconds
                uptime_seconds = int(time.time() - self.start_time)

                # Create heartbeat message (spec v1.1.0 compliant)
                message = protocol_msg.create_heartbeat(uptime_seconds)

                # Send to Air-Side
                self.socket.sendto(
                    message.encode(),
                    (self.target_ip, self.target_port)
                )

                # Update statistics
                self.heartbeats_sent += 1
                self.last_sent_time = time.time()

                logger.debug(f"Heartbeat: Sent #{self.heartbeats_sent} (uptime: {uptime_seconds}s)")

                # Wait 1 second (1 Hz as per spec)
                time.sleep(1.0)

            except Exception as e:
                if self.running:  # Only log if not intentionally stopping
                    logger.error(f"Heartbeat: Send error: {e}")
                    time.sleep(1.0)  # Wait before retry

    def is_running(self) -> bool:
        """Check if sender is running"""
        return self.running

    def get_stats(self) -> dict:
        """Get sender statistics"""
        return {
            "heartbeats_sent": self.heartbeats_sent,
            "last_sent_time": self.last_sent_time,
            "running": self.running
        }
