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
from utils.protocol_logger import logger


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
        logger.info("NETWORK", f"AirSideListener starting on UDP {self.host}:{self.port}")

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
                        logger.warning("NETWORK", f"[AirSideListener] JSON decode error: {e}")
                        print(f"[AirSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error("NETWORK", f"[AirSideListener] Error: {e}")
                        print(f"[AirSideListener] Error: {e}")

        except Exception as e:
            logger.error("NETWORK", f"[AirSideListener] Failed to start: {e}")
            print(f"[AirSideListener] Failed to start: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("NETWORK", "[AirSideListener] Stopped")


class GroundSideListener:
    """TCP server for Ground-Side logs (port 5008)

    ARCHITECTURE (Fixed for Issue #99):
    - This listener is a TCP SERVER listening on 0.0.0.0:5008
    - Ground-Side NetworkSink (H16) CONNECTS to 10.0.1.83:5008 (this machine)
    - Accepts incoming connections from Ground-Side and receives logs
    - Direct network connection (no ADB required for this architecture)
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5008, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_sock = None
        self.running = False
        self.thread = None

    def start(self, log_queue: deque):
        """Start the TCP server in a separate thread"""
        self.running = True
        self.thread = threading.Thread(target=self._accept_connections, args=(log_queue,), daemon=True)
        self.thread.start()
        logger.info("NETWORK", f"GroundSideListener starting TCP server on {self.host}:{self.port}")

    def _accept_connections(self, log_queue: deque):
        """Start TCP server and accept incoming connections from Ground-Side"""
        try:
            # Create server socket
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen(5)
            self.server_sock.settimeout(1.0)  # Accept timeout for clean shutdown

            logger.info(f"[GroundSideListener] TCP server listening on {self.host}:{self.port}")
            print(f"[GroundSideListener] TCP server listening on {self.host}:{self.port}")
            print(f"[GroundSideListener] Waiting for Ground-Side (H16) to connect...")

            while self.running:
                try:
                    # Accept incoming connection
                    client_sock, client_addr = self.server_sock.accept()
                    logger.info("NETWORK", f"[GroundSideListener] Client connected from {client_addr}")
                    print(f"[GroundSideListener] Client connected from {client_addr}")

                    # Handle client in current thread (single client at a time)
                    self._handle_client(client_sock, client_addr, log_queue)

                except socket.timeout:
                    # Normal timeout, continue accepting
                    continue
                except Exception as e:
                    if self.running:
                        logger.error("NETWORK", f"[GroundSideListener] Accept error: {e}")
                        print(f"[GroundSideListener] Accept error: {e}")

        except Exception as e:
            logger.error("NETWORK", f"[GroundSideListener] Server error: {e}")
            print(f"[GroundSideListener] Server error: {e}")
        finally:
            if self.server_sock:
                self.server_sock.close()
            logger.info("NETWORK", "[GroundSideListener] Server stopped")

    def _handle_client(self, client_sock: socket.socket, client_addr: tuple, log_queue: deque):
        """Handle a connected Ground-Side client and receive logs"""
        buffer = ""
        client_sock.settimeout(1.0)  # Read timeout for clean shutdown

        try:
            while self.running:
                try:
                    data = client_sock.recv(self.buffer_size)
                    if not data:
                        logger.info("NETWORK", f"[GroundSideListener] Client {client_addr} disconnected")
                        print(f"[GroundSideListener] Client {client_addr} disconnected")
                        break

                    buffer += data.decode('utf-8')

                    # Process complete JSON objects (newline-delimited)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                log_entry = json.loads(line)
                                log_entry['domain'] = 'GROUND'
                                log_entry['source_addr'] = f"{client_addr[0]}:{client_addr[1]}"
                                log_queue.append(log_entry)
                            except json.JSONDecodeError as e:
                                logger.warning("NETWORK", f"[GroundSideListener] JSON decode error: {e}")
                                print(f"[GroundSideListener] JSON decode error: {e}")
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error("NETWORK", f"[GroundSideListener] Client error: {e}")
                        print(f"[GroundSideListener] Client error: {e}")
                    break
        finally:
            client_sock.close()
            logger.info("NETWORK", f"[GroundSideListener] Client {client_addr} handler stopped")

    def stop(self):
        """Stop the listener"""
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.close()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=3.0)
        logger.info("NETWORK", "[GroundSideListener] Stopped")
