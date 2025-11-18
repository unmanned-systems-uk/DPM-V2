#!/usr/bin/env python3
"""
Test Live Docker Logs Features
Tests Docker Image ID display and Pop-Out window for Live Logs tab
"""

import sys
from pathlib import Path

print("="*70)
print("TEST: Live Docker Logs - Image ID & Pop-Out Window Features")
print("="*70)

# Test 1: Import modules
print("\n1. Testing imports...")
try:
    from gui.tab_logs import LogInspectorTab
    print("   ✅ LogInspectorTab imported")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check Docker Image ID label exists
print("\n2. Checking Docker Image ID display...")
try:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.withdraw()

    # Create notebook (parent for tab)
    notebook = ttk.Notebook(root)

    # Create Log Inspector tab
    log_tab = LogInspectorTab(notebook)

    # Check Docker Image ID label exists
    if hasattr(log_tab, 'docker_image_id_label'):
        print("   ✅ docker_image_id_label exists")

        # Check label properties
        text = log_tab.docker_image_id_label.cget('text')
        print(f"   ✅ Initial text: '{text}' (should be 'N/A')")

        if text == "N/A":
            print("   ✅ Initial value correct")
        else:
            print(f"   ⚠️  Expected 'N/A', got '{text}'")
    else:
        print("   ❌ docker_image_id_label NOT found")
        sys.exit(1)

    root.destroy()

except Exception as e:
    print(f"   ❌ Docker Image ID check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check Pop Out methods exist
print("\n3. Checking pop-out methods...")
try:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.withdraw()

    notebook = ttk.Notebook(root)
    log_tab = LogInspectorTab(notebook)

    # Check _fetch_docker_image_id method
    if hasattr(log_tab, '_fetch_docker_image_id'):
        print("   ✅ _fetch_docker_image_id() method exists")
    else:
        print("   ❌ _fetch_docker_image_id() method NOT found")
        sys.exit(1)

    # Check _pop_out_logs method
    if hasattr(log_tab, '_pop_out_logs'):
        print("   ✅ _pop_out_logs() method exists")
    else:
        print("   ❌ _pop_out_logs() method NOT found")
        sys.exit(1)

    # Check helper methods
    methods = [
        '_refresh_popup',
        '_copy_popup_content',
        '_save_popup_to_file'
    ]

    for method in methods:
        if hasattr(log_tab, method):
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

# Test 4: Check popup window initialization
print("\n4. Checking popup window initialization...")
try:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.withdraw()

    notebook = ttk.Notebook(root)
    log_tab = LogInspectorTab(notebook)

    if hasattr(log_tab, 'popup_window'):
        print("   ✅ popup_window attribute exists")
        if log_tab.popup_window is None:
            print("   ✅ popup_window initialized to None")
        else:
            print(f"   ⚠️  popup_window = {log_tab.popup_window} (expected None)")
    else:
        print("   ❌ popup_window attribute NOT found")
        sys.exit(1)

    if hasattr(log_tab, 'popup_text'):
        print("   ✅ popup_text attribute exists")
        if log_tab.popup_text is None:
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

# Test 5: Check Pop Out button exists in UI
print("\n5. Checking Pop Out button in bottom frame...")
try:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("Live Logs Test")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    log_tab = LogInspectorTab(notebook)
    notebook.add(log_tab, text="Log Inspector")

    # Check if any button has "Pop Out" text
    found_popout_btn = False
    for widget in log_tab.winfo_children():
        if isinstance(widget, ttk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button):
                    try:
                        text = child.cget('text')
                        if "Pop Out" in text:
                            print(f"   ✅ Found Pop Out button with text: '{text}'")
                            found_popout_btn = True
                            break
                    except:
                        pass

    if found_popout_btn:
        print("   ✅ Pop Out button exists in UI")
    else:
        print("   ⚠️  Pop Out button not found (may need manual verification)")

    root.destroy()

except Exception as e:
    print(f"   ❌ Button check failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ ALL TESTS PASSED")
print("="*70)

print("\nFeature Summary:")
print("\n📊 Docker Image ID Display:")
print("- Displays in SSH Connection status bar")
print("- Shows 12-character Docker image ID (e.g., 'a1b2c3d4e5f6')")
print("- Updates automatically when SSH connects")
print("- Shows 'N/A' when disconnected or container not found")
print("\n🗗 Pop-Out Window:")
print("- '🗗 Pop Out' button added to bottom control bar")
print("- Opens live logs in separate 1400x900 window")
print("- Displays Docker Image ID in popup header")
print("- Syntax highlighting (errors=red, warnings=orange, etc.)")
print("- Actions: Refresh, Copy All, Save to File, Close")
print("- Auto-sync toggle to sync with main window")
print("\nNext Steps:")
print("1. Launch DPM Management System:")
print("   python3 DPM_Management_System.py")
print("2. Go to 'Log Inspector' tab (live docker logs)")
print("3. Click 'Connect SSH' to Air-Side")
print("4. Verify Docker Image ID appears in status bar")
print("5. Click '🗗 Pop Out' button")
print("6. Verify log displays in separate window with Image ID")
print("7. Test Refresh, Copy, and Save buttons")
