#!/usr/bin/env python3
"""
Test script for log_aggregator.py

Sends test log entries via UDP (Air-Side) and TCP (Ground-Side) to verify aggregator works.
"""

import socket
import json
import time
from datetime import datetime, timezone


def send_air_side_test_logs():
    """Send test logs via UDP (Air-Side)"""
    print("[Test] Sending Air-Side test logs via UDP...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    test_logs = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "context": "STARTUP",
            "message": "Air-Side system initialized",
            "thread": "main",
            "function": "main",
            "line": 42
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "DEBUG",
            "context": "CAMERA",
            "message": "SDK initialized",
            "thread": "main",
            "sdk_version": "2.00.00"
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO",
            "context": "COMMAND",
            "message": "Command received",
            "command": "SET_APERTURE",
            "value": "f/2.8",
            "latency": 12
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "ERROR",
            "context": "CAMERA",
            "message": "SDK call failed",
            "error": "TIMEOUT",
            "latency": 5000
        }
    ]

    for log in test_logs:
        data = json.dumps(log).encode('utf-8')
        sock.sendto(data, ('localhost', 5007))
        print(f"  Sent: [{log['level']}] [{log['context']}] {log['message']}")
        time.sleep(0.5)

    sock.close()
    print("[Test] Air-Side test logs sent\n")


def send_ground_side_test_logs():
    """Send test logs via TCP (Ground-Side)"""
    print("[Test] Sending Ground-Side test logs via TCP...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5008))

        test_logs = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "INFO",
                "context": "UI",
                "message": "Button pressed",
                "button_id": "set_aperture",
                "value": "f/2.8"
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "DEBUG",
                "context": "VM",
                "message": "ViewModel updated",
                "property": "aperture",
                "value": "f/2.8"
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "INFO",
                "context": "NETWORK",
                "message": "Command sent",
                "command": "SET_APERTURE",
                "latency": 8
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "WARNING",
                "context": "UI",
                "message": "Response timeout",
                "expected_time": 100,
                "actual_time": 250
            }
        ]

        for log in test_logs:
            data = (json.dumps(log) + '\n').encode('utf-8')
            sock.send(data)
            print(f"  Sent: [{log['level']}] [{log['context']}] {log['message']}")
            time.sleep(0.5)

        sock.close()
        print("[Test] Ground-Side test logs sent\n")

    except ConnectionRefusedError:
        print("[Test] ERROR: Could not connect to Ground-Side listener on TCP 5008")
        print("[Test] Make sure log_aggregator.py is running first!\n")


def main():
    """Run test"""
    print("\n" + "=" * 60)
    print("Log Aggregator Test Script")
    print("=" * 60 + "\n")

    print("INSTRUCTIONS:")
    print("1. Start log_aggregator.py in another terminal:")
    print("   python log_aggregator.py")
    print("2. Press Enter to send test logs...")
    print()

    input("Press Enter to continue...")

    # Send test logs
    send_air_side_test_logs()
    time.sleep(1)
    send_ground_side_test_logs()

    print("=" * 60)
    print("Test complete! Check the log_aggregator output.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
