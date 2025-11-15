#!/usr/bin/env python3
"""
Test log_viewer_gui.py with fake log data injection
This bypasses network listeners and directly injects test log entries
"""
from collections import deque
from datetime import datetime
import time

# Import the GUI class
from log_viewer_gui import LogViewerGUI

def inject_fake_logs(app):
    """Inject fake log entries to test color display"""
    print("\n" + "="*60)
    print("Injecting fake log data in 3 seconds...")
    print("="*60)

    # Wait for GUI to initialize
    app.after(3000, lambda: _inject_logs(app))

def _inject_logs(app):
    """Actually inject the logs"""
    fake_entries = [
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'AIR',
            'level': 'INFO',
            'context': 'CAMERA',
            'message': 'Camera system initialized - THIS SHOULD BE GREEN'
        },
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'AIR',
            'level': 'DEBUG',
            'context': 'NETWORK',
            'message': 'Network heartbeat sent - THIS SHOULD BE GRAY'
        },
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'AIR',
            'level': 'WARNING',
            'context': 'SYSTEM',
            'message': 'Low memory warning - THIS SHOULD BE ORANGE'
        },
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'AIR',
            'level': 'ERROR',
            'context': 'COMMAND',
            'message': 'Command execution failed - THIS SHOULD BE RED AND BOLD'
        },
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'GROUND',
            'level': 'INFO',
            'context': 'UI',
            'message': 'UI updated successfully - THIS SHOULD BE GREEN'
        },
        {
            'timestamp': datetime.now().isoformat() + 'Z',
            'domain': 'GROUND',
            'level': 'ERROR',
            'context': 'NETWORK',
            'message': 'Connection lost - THIS SHOULD BE RED AND BOLD'
        },
    ]

    print(f"\nInjecting {len(fake_entries)} fake log entries...")

    # Add to queue
    for entry in fake_entries:
        app.log_queue.append(entry)
        print(f"  Injected: {entry['domain']} {entry['level']} - {entry['message'][:40]}")

    # Trigger GUI update
    app._update_display()

    print("\nLogs injected. Check the GUI window:")
    print("  - Lines should have different colors based on level")
    print("  - ERROR: RED and BOLD")
    print("  - WARNING: ORANGE")
    print("  - INFO: GREEN")
    print("  - DEBUG: GRAY")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\nStarting log viewer with fake data injection...")
    print("Do NOT click 'Start' - data will be injected automatically.\n")

    app = LogViewerGUI()
    inject_fake_logs(app)
    app.mainloop()
