#!/usr/bin/env python3
"""
Quick test to verify UDP listener on port 5007 works
"""
import socket
import time
import threading

def test_udp_listener():
    """Test UDP listener on port 5007"""
    print("Testing UDP listener on port 5007...")

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", 5007))
        print("✅ Successfully bound to UDP 0.0.0.0:5007")
        print("Listening for packets... (Ctrl+C to stop)")

        sock.settimeout(1.0)

        while True:
            try:
                data, addr = sock.recvfrom(4096)
                print(f"\n🎉 Received packet from {addr}")
                print(f"Data: {data[:200]}")  # First 200 bytes
            except socket.timeout:
                print(".", end="", flush=True)
                time.sleep(1)

    except OSError as e:
        print(f"❌ ERROR: {e}")
        print("Port 5007 may already be in use")
        return False
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        sock.close()
        print("Socket closed")

    return True

if __name__ == "__main__":
    test_udp_listener()
