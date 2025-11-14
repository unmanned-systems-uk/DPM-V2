"""
Log Listeners for DPM SystemTools - Tri-Domain Log Aggregation
===============================================================

Air-Side Listener (UDP 5007) and Ground-Side Listener (TCP 5008 via ADB forward)

Part of Issue #105 - Tri-Domain Log Aggregation GUI Integration
"""

import socket
import json
import threading
from collections import deque
from typing import Callable, Optional
from utils.logger import logger


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
        logger.info(f"AirSideListener starting on UDP {self.host}:{self.port}")

    def _listen(self, log_queue: deque):
        """Listen for UDP packets and add to queue"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(1.0)  # 1 second timeout for graceful shutdown

            logger.info(f"[AirSideListener] Listening on UDP {self.host}:{self.port}")
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
                        logger.warning(f"[AirSideListener] JSON decode error: {e}")
                        print(f"[AirSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"[AirSideListener] Error: {e}")
                        print(f"[AirSideListener] Error: {e}")

        except Exception as e:
            logger.error(f"[AirSideListener] Failed to start: {e}")
            print(f"[AirSideListener] Failed to start: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("[AirSideListener] Stopped")


class GroundSideListener:
    """TCP client for Ground-Side logs (port 5008, via ADB forward)

    ARCHITECTURE (Fixed for Issue #105):
    - ADB forward listens on 127.0.0.1:5008 (server side)
    - This listener CONNECTS to 127.0.0.1:5008 (client side)
    - ADB forward bridges to H16:5008 where Ground-Side app sends logs
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5008, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.sock = None
        self.running = False
        self.thread = None
        self.reconnect_delay = 5.0  # Seconds between reconnection attempts

    def start(self, log_queue: deque):
        """Start the TCP client in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._connect_and_listen, args=(log_queue,), daemon=True)
        self.thread.start()
        logger.info(f"GroundSideListener starting, will connect to TCP {self.host}:{self.port}")

    def _connect_and_listen(self, log_queue: deque):
        """Connect to ADB forward port and listen for logs"""
        logger.info(f"[GroundSideListener] Connecting to TCP {self.host}:{self.port}")
        print(f"[GroundSideListener] Connecting to TCP {self.host}:{self.port}")
        print(f"[GroundSideListener] Ensure ADB forward is active: adb forward tcp:5008 tcp:5008")

        while self.running:
            try:
                # Create socket and connect
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5.0)  # Connection timeout

                logger.info(f"[GroundSideListener] Attempting connection to {self.host}:{self.port}...")
                print(f"[GroundSideListener] Attempting connection to {self.host}:{self.port}...")

                self.sock.connect((self.host, self.port))

                logger.info(f"[GroundSideListener] Connected to {self.host}:{self.port}")
                print(f"[GroundSideListener] Connected to {self.host}:{self.port}")

                # Set socket to blocking mode with 1 second timeout for clean shutdown
                self.sock.settimeout(1.0)

                # Handle incoming data
                self._handle_connection(log_queue)

            except socket.timeout:
                logger.warning(f"[GroundSideListener] Connection timeout to {self.host}:{self.port}")
                print(f"[GroundSideListener] Connection timeout")
            except ConnectionRefusedError:
                logger.warning(f"[GroundSideListener] Connection refused on {self.host}:{self.port} (ADB forward not active?)")
                print(f"[GroundSideListener] Connection refused (check ADB forward)")
            except Exception as e:
                if self.running:
                    logger.error(f"[GroundSideListener] Connection error: {e}")
                    print(f"[GroundSideListener] Connection error: {e}")
            finally:
                if self.sock:
                    self.sock.close()
                    self.sock = None

            # Wait before reconnecting
            if self.running:
                logger.info(f"[GroundSideListener] Will retry in {self.reconnect_delay}s...")
                print(f"[GroundSideListener] Retrying in {self.reconnect_delay}s...")
                import time
                time.sleep(self.reconnect_delay)

    def _handle_connection(self, log_queue: deque):
        """Handle the TCP connection and receive logs"""
        buffer = ""
        try:
            while self.running:
                try:
                    data = self.sock.recv(self.buffer_size)
                    if not data:
                        logger.warning("[GroundSideListener] Connection closed by remote")
                        print("[GroundSideListener] Connection closed by remote")
                        break

                    buffer += data.decode('utf-8')

                    # Process complete JSON objects (newline-delimited)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                log_entry = json.loads(line)
                                log_entry['domain'] = 'GROUND'
                                log_entry['source_addr'] = f"{self.host}:{self.port}"
                                log_queue.append(log_entry)
                            except json.JSONDecodeError as e:
                                logger.warning(f"[GroundSideListener] JSON decode error: {e}")
                                print(f"[GroundSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"[GroundSideListener] Error receiving data: {e}")
                        print(f"[GroundSideListener] Error receiving data: {e}")
                    break
        finally:
            logger.info("[GroundSideListener] Connection handler stopped")

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=3.0)
        logger.info("[GroundSideListener] Stopped")
