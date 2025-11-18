#!/usr/bin/env python3
"""
Test script for DPM_Management_System.py
Launches GUI and attempts to connect to Air-Side
"""

import sys
import tkinter as tk
from DPM_Management_System import DPMManagementSystem

def test_connection():
    """Launch GUI and test Air-Side connection"""
    print("=== DPM Management System Test ===")
    print("Launching GUI...")

    app = DPMManagementSystem()

    # Schedule connection attempt after GUI is ready
    def attempt_connection():
        print("\n=== Attempting to connect to Air-Side ===")
        print("Target: 10.0.1.53:5000")

        result = app.connect_to_airside(host='10.0.1.53', port=5000, timeout_ms=5000)

        if result:
            print("✅ Connected to Air-Side successfully!")
            print("Status: Ready for on-demand logging tests")
            print("\nYou can now:")
            print("  1. Click 'Start' to begin passive logging")
            print("  2. Set duration and click 'Request Logs' for on-demand logging")
            print("  3. Watch the countdown timer")
        else:
            print("❌ Failed to connect to Air-Side")
            print("\nTroubleshooting:")
            print("  1. Check Air-Side is running on 10.0.1.53:5000")
            print("  2. Test network: ping 10.0.1.53")
            print("  3. Test TCP port: nc -zv 10.0.1.53 5000")
            print("\nYou can still test passive logging (UDP/TCP listeners)")

    # Schedule connection after 2 seconds (GUI initialization time)
    app.after(2000, attempt_connection)

    print("GUI initialized. Starting main loop...")
    print("(Connection will be attempted in 2 seconds)")

    app.mainloop()

if __name__ == "__main__":
    test_connection()
