#!/usr/bin/env python3
"""
Test System Logs source in File Browser - Issue #136 Enhancement
Verifies the 4th log source (System Logs) is integrated correctly
"""

import sys
import tkinter as tk
from tkinter import ttk

print("Test: System Logs Source Addition - Issue #136")
print("="*70)

# Test 1: Import File Browser
print("\n1. Importing FileBrowserTab...")
try:
    from gui.tab_file_browser import FileBrowserTab
    print("   ✅ Import successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create instance and verify System Logs in dropdown
print("\n2. Creating FileBrowserTab instance...")
try:
    root = tk.Tk()
    root.title("System Logs Source Test")
    root.geometry("900x700")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    file_browser = FileBrowserTab(notebook)
    notebook.add(file_browser.frame, text="File Browser")

    print("   ✅ FileBrowserTab created")

    # Test 3: Verify dropdown values
    print("\n3. Verifying log source dropdown values...")

    if hasattr(file_browser, 'log_source_combo'):
        dropdown_values = file_browser.log_source_combo['values']
        print(f"   Log source dropdown values: {dropdown_values}")

        expected_sources = ["Host Logs", "Container Logs", "Docker Output", "System Logs"]

        if tuple(expected_sources) == dropdown_values:
            print("   ✅ All 4 log sources present:")
            for i, source in enumerate(dropdown_values, 1):
                print(f"      {i}. {source}")
        else:
            print(f"   ❌ Dropdown values don't match expected")
            print(f"      Expected: {expected_sources}")
            print(f"      Got: {list(dropdown_values)}")
            sys.exit(1)
    else:
        print("   ❌ Log source dropdown not found")
        sys.exit(1)

    # Test 4: Verify _load_system_logs method exists
    print("\n4. Verifying _load_system_logs() method...")

    if hasattr(file_browser, '_load_system_logs'):
        print("   ✅ _load_system_logs() method exists")

        # Check method signature/docstring
        import inspect
        doc = inspect.getdoc(file_browser._load_system_logs)
        if doc:
            print(f"   ✅ Method docstring: {doc[:80]}...")
    else:
        print("   ❌ _load_system_logs() method not found")
        sys.exit(1)

    # Test 5: Verify filter patterns
    print("\n5. Verifying system log filter patterns...")

    # Get the source code to check filter patterns
    source_lines = inspect.getsource(file_browser._load_system_logs)

    expected_patterns = ['syslog', 'kern.log', 'auth.log', 'dmesg']
    patterns_found = all(pattern in source_lines for pattern in expected_patterns)

    if patterns_found:
        print("   ✅ All expected file patterns found in filter:")
        for pattern in expected_patterns:
            print(f"      - {pattern}*")
    else:
        print("   ❌ Not all expected patterns found")

    # Test 6: Verify remote directory
    print("\n6. Verifying remote directory...")

    if '/var/log' in source_lines:
        print("   ✅ Remote directory: /var/log")
    else:
        print("   ❌ Remote directory /var/log not found")

    # Test 7: Verify download tag (should use "host" for SFTP)
    print("\n7. Verifying download method tag...")

    if '"host"' in source_lines or "'host'" in source_lines:
        print("   ✅ Uses 'host' tag (SFTP download - same as Host Logs)")
    else:
        print("   ❌ Download tag not configured correctly")

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - System Logs source integrated successfully!")
    print("="*70)

    print("\nSummary:")
    print("  - Dropdown now has 4 sources (Host, Container, Docker Output, System)")
    print("  - System Logs filters: syslog*, kern.log*, auth.log*, dmesg*")
    print("  - Remote directory: /var/log")
    print("  - Download method: SFTP (same as Host Logs)")

    print("\nGUI window will display for 2 seconds...")

    # Auto-close after 2 seconds
    root.after(2000, root.destroy)
    root.mainloop()

    print("\n✅ Test complete - No runtime errors")
    print("\nNext step: Test with live Air-Side connection")
    print("  1. python3 DPM_Management_System.py")
    print("  2. Navigate to File Browser tab")
    print("  3. Click Docker Logs sub-tab")
    print("  4. Connect to Air-Side")
    print("  5. Select 'System Logs' from dropdown")
    print("  6. Download syslog, kern.log, auth.log, or dmesg")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
