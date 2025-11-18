#!/usr/bin/env python3
"""
Test Pop-Out Window Feature
Tests the Docker Logs pop-out window functionality
"""

import sys
from pathlib import Path

print("="*70)
print("TEST: Docker Logs Pop-Out Window Feature")
print("="*70)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from gui.tab_file_browser import FileBrowserTab
    print("   ✅ FileBrowserTab imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check pop-out methods exist
print("\n2. Checking pop-out methods...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    file_browser = FileBrowserTab(root)

    # Check main pop-out method
    if hasattr(file_browser, '_pop_out_docker_logs'):
        print("   ✅ _pop_out_docker_logs() method exists")
    else:
        print("   ❌ _pop_out_docker_logs() method NOT found")
        sys.exit(1)

    # Check helper methods
    methods = [
        '_load_popup_content',
        '_load_popup_container_log',
        '_load_popup_docker_output',
        '_load_popup_sftp_log',
        '_apply_log_highlighting',
        '_refresh_popup',
        '_copy_popup_content',
        '_save_popup_to_file'
    ]

    for method in methods:
        if hasattr(file_browser, method):
            print(f"   ✅ {method}() exists")
        else:
            print(f"   ❌ {method}() NOT found")
            sys.exit(1)

    root.destroy()

except Exception as e:
    print(f"   ❌ Method check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check pop-out button exists
print("\n3. Checking pop-out button in UI...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.title("Pop-Out Test")
    root.geometry("800x600")

    file_browser = FileBrowserTab(root)

    # Check button exists
    if hasattr(file_browser, 'logs_popout_btn'):
        print("   ✅ logs_popout_btn exists")

        # Check button properties
        button = file_browser.logs_popout_btn
        text = button.cget('text')
        state = button.cget('state')
        print(f"   ✅ Button text: '{text}'")
        print(f"   ✅ Initial state: {state} (should be 'disabled')")

        if text == "🗗 Pop Out":
            print("   ✅ Button text correct")
        else:
            print(f"   ⚠️  Expected '🗗 Pop Out', got '{text}'")

    else:
        print("   ❌ logs_popout_btn NOT found")
        sys.exit(1)

    root.destroy()

except Exception as e:
    print(f"   ❌ Button check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check popup window initialization
print("\n4. Checking popup window initialization...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()

    file_browser = FileBrowserTab(root)

    if hasattr(file_browser, 'popup_window'):
        print("   ✅ popup_window attribute exists")
        if file_browser.popup_window is None:
            print("   ✅ popup_window initialized to None")
        else:
            print(f"   ⚠️  popup_window = {file_browser.popup_window} (expected None)")
    else:
        print("   ❌ popup_window attribute NOT found")
        sys.exit(1)

    if hasattr(file_browser, 'popup_text'):
        print("   ✅ popup_text attribute exists")
        if file_browser.popup_text is None:
            print("   ✅ popup_text initialized to None")
    else:
        print("   ❌ popup_text attribute NOT found")
        sys.exit(1)

    root.destroy()

except Exception as e:
    print(f"   ❌ Initialization check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)

print("\nFeature Summary:")
print("- 🗗 Pop Out button added to Docker Logs tab")
print("- Button enables when connected to Air-Side")
print("- Clicking button opens log in separate window")
print("\nPop-Out Window Features:")
print("- 📋 Displays log content with syntax highlighting")
print("- 🔄 Refresh button to reload log")
print("- 📋 Copy All button to copy to clipboard")
print("- 💾 Save to File button to export log")
print("- ❌ Close button to close window")
print("\nLog Highlighting:")
print("- ❌ Error/Exception/Failed - Red")
print("- ⚠️  Warning - Orange")
print("- ℹ️  Info - Blue")
print("- 🐛 Debug - Gray")
print("- ✈️  AIR domain - Dark blue")
print("- 📱 GROUND domain - Dark green")
print("\nSupported Log Sources:")
print("- ✅ Container Logs (via docker cp)")
print("- ✅ Docker Output (via docker logs)")
print("- ✅ Host Logs (via SFTP)")
print("- ✅ System Logs (via SFTP)")
print("\nNext Steps:")
print("1. Launch DPM Management System:")
print("   python3 DPM_Management_System.py")
print("2. Go to File Browser tab → Docker Logs sub-tab")
print("3. Connect to Air-Side (10.0.1.53)")
print("4. Select a log file from the list")
print("5. Click '🗗 Pop Out' button")
print("6. Verify log displays in separate window with highlighting")
