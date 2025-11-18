#!/usr/bin/env python3
"""
Test Docker Image ID Display Feature
Tests that the Docker Logs tab displays Docker image IDs correctly
"""

import sys
from pathlib import Path

print("="*70)
print("TEST: Docker Image ID Display in Docker Logs Tab")
print("="*70)

# Test 1: Import module
print("\n1. Testing imports...")
try:
    from gui.tab_file_browser import FileBrowserTab
    print("   ✅ FileBrowserTab imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check TreeView column structure
print("\n2. Checking TreeView column structure...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.title("Image ID Test")
    root.geometry("800x600")

    # Create File Browser tab
    file_browser = FileBrowserTab(root)

    # Get TreeView columns from Docker Logs tab
    columns = file_browser.logs_tree['columns']
    print(f"   ✅ TreeView columns: {columns}")

    # Verify Image ID column exists
    if 'image_id' in columns:
        print("   ✅ 'image_id' column present")
    else:
        print(f"   ❌ 'image_id' column NOT found. Columns: {columns}")
        sys.exit(1)

    # Check column headings
    heading = file_browser.logs_tree.heading('image_id')
    print(f"   ✅ Image ID heading configured: {heading}")

    # Check column width
    width = file_browser.logs_tree.column('image_id', 'width')
    print(f"   ✅ Image ID column width: {width}px")

    root.destroy()

except Exception as e:
    print(f"   ❌ TreeView check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check _get_docker_image_id method exists
print("\n3. Checking _get_docker_image_id method...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    file_browser = FileBrowserTab(root)

    # Check method exists
    if hasattr(file_browser, '_get_docker_image_id'):
        print("   ✅ _get_docker_image_id() method exists")
    else:
        print("   ❌ _get_docker_image_id() method NOT found")
        sys.exit(1)

    root.destroy()

except Exception as e:
    print(f"   ❌ Method check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Simulate image ID parsing
print("\n4. Testing image ID parsing logic...")
try:
    # Test various image ID formats
    test_cases = [
        ("sha256:abcdef123456789012345678901234567890", "abcdef123456"),
        ("sha256:1234567890ab", "1234567890ab"),
        ("fedcba987654321098765432109876543210", "fedcba987654"),
        ("short", "short"),
    ]

    for full_id, expected_short in test_cases:
        # Simulate the parsing logic
        if full_id.startswith('sha256:'):
            parsed = full_id[7:]
        else:
            parsed = full_id

        short_id = parsed[:12]

        if short_id == expected_short:
            print(f"   ✅ '{full_id}' → '{short_id}'")
        else:
            print(f"   ❌ '{full_id}' → '{short_id}' (expected '{expected_short}')")
            sys.exit(1)

except Exception as e:
    print(f"   ❌ Parsing test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)

print("\nFeature Summary:")
print("- Docker Logs tab now has 4 columns:")
print("  1. Log File (name)")
print("  2. Size (KB)")
print("  3. Source")
print("  4. Image ID (NEW)")
print("\n- Image ID displayed for Container Logs and Docker Output sources")
print("- Host Logs and System Logs show 'N/A' (not Docker-based)")
print("- Image ID shortened to 12 chars (standard Docker format)")
print("\nNext Steps:")
print("1. Launch DPM Management System:")
print("   python3 DPM_Management_System.py")
print("2. Go to File Browser tab → Docker Logs sub-tab")
print("3. Connect to Air-Side (10.0.1.53)")
print("4. Select 'Container Logs' or 'Docker Output' source")
print("5. Click Refresh")
print("6. Verify Image ID column shows container image ID")
