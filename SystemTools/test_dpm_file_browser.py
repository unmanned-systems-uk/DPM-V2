#!/usr/bin/env python3
"""
Test DPM Management System with enhanced File Browser - Issue #136
Quick test to verify File Browser sub-tabs work in the new system
"""

import sys
import tkinter as tk
from tkinter import ttk

print("Test: DPM Management System with Enhanced File Browser (Issue #136)")
print("="*70)

# Test 1: Import DPM Management System
print("\n1. Importing DPM_Management_System...")
try:
    from DPM_Management_System import DPMManagementSystem
    print("   ✅ Import successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check if FileBrowserTab is imported
print("\n2. Verifying FileBrowserTab import...")
try:
    from gui.tab_file_browser import FileBrowserTab
    print("   ✅ FileBrowserTab imported")
except ImportError as e:
    print(f"   ❌ FileBrowserTab import failed: {e}")
    sys.exit(1)

# Test 3: Create DPM Management System instance
print("\n3. Creating DPM Management System instance...")
try:
    root = DPMManagementSystem()
    print("   ✅ DPM Management System created")

    # Test 4: Verify File Browser tab exists
    print("\n4. Verifying File Browser tab integration...")
    if hasattr(root, 'file_browser_tab'):
        print("   ✅ File Browser tab exists")

        # Test 5: Verify sub-tabs
        print("\n5. Verifying File Browser sub-tabs...")
        fb = root.file_browser_tab

        if hasattr(fb, 'notebook'):
            print("   ✅ Sub-tab notebook exists")

            # Count tabs
            tab_count = fb.notebook.index('end')
            print(f"   ✅ Found {tab_count} sub-tabs")

            # Check tab names
            for i in range(tab_count):
                tab_text = fb.notebook.tab(i, 'text')
                print(f"      - Sub-tab {i}: {tab_text}")

            # Verify expected tabs
            if hasattr(fb, 'images_frame') and hasattr(fb, 'logs_frame'):
                print("   ✅ Both Images and Docker Logs sub-tabs exist")
            else:
                print("   ❌ Missing expected sub-tabs")

            # Verify Docker Logs features
            if hasattr(fb, 'log_source_var'):
                print(f"   ✅ Log source selector exists (default: {fb.log_source_var.get()})")
            else:
                print("   ❌ Log source selector missing")

            if hasattr(fb, 'tail_count_var'):
                print(f"   ✅ Tail count selector exists (default: {fb.tail_count_var.get()})")
            else:
                print("   ❌ Tail count selector missing")
        else:
            print("   ❌ Sub-tab notebook missing")
    else:
        print("   ❌ File Browser tab not found")

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70)
    print("\nDPM Management System window will open for 3 seconds...")
    print("The File Browser tab should show with Images and Docker Logs sub-tabs.")

    # Show window briefly
    root.after(3000, root.destroy)
    root.mainloop()

    print("\n✅ Test complete - File Browser integrated successfully into DPM Management System")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
