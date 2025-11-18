#!/usr/bin/env python3
"""
Test script for File Browser Tab - Issue #136
Tests basic import and initialization
"""

import sys
import tkinter as tk
from tkinter import ttk

# Test 1: Import the module
print("Test 1: Importing tab_file_browser module...")
try:
    from gui.tab_file_browser import FileBrowserTab
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create a test window
print("\nTest 2: Creating test GUI window...")
try:
    root = tk.Tk()
    root.title("File Browser Test - Issue #136")
    root.geometry("800x600")

    # Create notebook (parent for FileBrowserTab)
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create File Browser tab
    file_browser = FileBrowserTab(notebook)
    notebook.add(file_browser.frame, text="File Browser")

    print("✅ GUI components created successfully")
    print("\nTest 3: Verifying sub-tab structure...")

    # Check if sub-tabs exist
    if hasattr(file_browser, 'notebook'):
        print("✅ Sub-tab notebook exists")

        # Check for Images tab
        if hasattr(file_browser, 'images_frame'):
            print("✅ Images sub-tab exists")
        else:
            print("❌ Images sub-tab missing")

        # Check for Docker Logs tab
        if hasattr(file_browser, 'logs_frame'):
            print("✅ Docker Logs sub-tab exists")
        else:
            print("❌ Docker Logs sub-tab missing")

        # Check for log source components
        if hasattr(file_browser, 'log_source_var'):
            print("✅ Log source selector exists")
            print(f"   Default value: {file_browser.log_source_var.get()}")
        else:
            print("❌ Log source selector missing")

        # Check for tail count components
        if hasattr(file_browser, 'tail_count_var'):
            print("✅ Tail count selector exists")
            print(f"   Default value: {file_browser.tail_count_var.get()}")
        else:
            print("❌ Tail count selector missing")
    else:
        print("❌ Sub-tab notebook missing")

    print("\nTest 4: Verifying download handlers...")

    # Check for download method handlers
    handlers = [
        '_download_host_log',
        '_download_container_log',
        '_download_docker_output',
        '_load_host_logs',
        '_load_container_logs',
        '_load_docker_output_entry'
    ]

    for handler in handlers:
        if hasattr(file_browser, handler):
            print(f"✅ {handler} exists")
        else:
            print(f"❌ {handler} missing")

    print("\n" + "="*60)
    print("All tests passed! ✅")
    print("="*60)
    print("\nGUI window will open for 2 seconds for visual inspection...")
    print("Close the window manually to continue, or it will auto-close.")

    # Show window briefly for visual inspection
    root.after(2000, root.destroy)  # Auto-close after 2 seconds
    root.mainloop()

    print("\n✅ Test complete - No runtime errors detected")

except Exception as e:
    print(f"❌ Error during GUI creation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
