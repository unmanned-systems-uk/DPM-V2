#!/usr/bin/env python3
"""
Dump all tag configurations from LogViewerGUI to verify they exist
"""
from log_viewer_gui import LogViewerGUI

print("\n" + "="*60)
print("LogViewerGUI Tag Configuration Dump")
print("="*60)

app = LogViewerGUI()

print("\nChecking tags on app.log_text widget:")
print(f"Widget: {app.log_text}")
print(f"Widget state: {app.log_text.cget('state')}")

# Get all configured tags
all_tags = app.log_text.tag_names()
print(f"\nAll tags: {all_tags}")

# Check specific tags
expected_tags = ["air", "ground", "error", "warning", "info", "debug", "highlight"]
print("\nExpected tag configurations:")
for tag in expected_tags:
    if tag in all_tags:
        fg = app.log_text.tag_cget(tag, "foreground")
        bg = app.log_text.tag_cget(tag, "background")
        font = app.log_text.tag_cget(tag, "font")
        print(f"  ✓ {tag:10} → fg={fg or '(default)':15} bg={bg or '(default)':15} font={font or '(default)'}")
    else:
        print(f"  ✗ {tag:10} → NOT FOUND!")

print("\n" + "="*60)
print("Close the window to exit...")
print("="*60 + "\n")

app.mainloop()
