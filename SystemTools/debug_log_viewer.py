#!/usr/bin/env python3
"""
Debug version of log_viewer_gui.py with verbose tag application logging
"""
import tkinter as tk
from tkinter import scrolledtext
import sys

from utils.log_colors import configure_tkinter_text_tags

# Create minimal test window
root = tk.Tk()
root.title("Debug Log Viewer - Tag Test")
root.geometry("1000x400")

text = scrolledtext.ScrolledText(root, font=('Courier New', 9), wrap=tk.NONE,
                                  bg='white', fg='black')
text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

print("="*60)
print("Configuring tags...")
configure_tkinter_text_tags(text)

# Verify tags are configured
print("\nVerifying tag configuration:")
for tag in ["air", "ground", "error", "warning", "info", "debug"]:
    fg = text.tag_cget(tag, "foreground")
    print(f"  {tag:8} → foreground={fg}")

# Insert test entry with tag application
print("\nInserting test log entry:")
test_entry = {
    'timestamp': '2025-11-15T23:45:01.123Z',
    'domain': 'AIR',
    'level': 'ERROR',
    'context': 'CAMERA',
    'message': 'Test error message'
}

# Format line (same as log_viewer_gui.py)
timestamp = test_entry.get('timestamp', 'NO-TS')
if 'T' in timestamp:
    time_part = timestamp.split('T')[1][:12]
else:
    time_part = timestamp[:12]

domain = test_entry.get('domain', 'UNK').ljust(6)[:6]
level = test_entry.get('level', 'INFO').ljust(7)[:7]
context = test_entry.get('context', 'UNKNOWN').ljust(8)[:8]
message = test_entry.get('message', '')

log_line = f"{time_part} [{domain}] [{level}] [{context}] {message}\n"

print(f"  Formatted line: {log_line.strip()}")

# Insert
text.config(state=tk.NORMAL)
text.insert(tk.END, log_line)
line_number = int(text.index(tk.END).split('.')[0]) - 1

print(f"  Line number: {line_number}")

# Apply domain tag
domain_code = test_entry.get('domain', '')
if domain_code == 'AIR':
    text.tag_add("air", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'air' to line {line_number}")
elif domain_code == 'GROUND':
    text.tag_add("ground", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'ground' to line {line_number}")

# Apply level tag
level_code = test_entry.get('level', 'INFO')
if level_code == 'ERROR':
    text.tag_add("error", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'error' to line {line_number}")
elif level_code == 'WARNING':
    text.tag_add("warning", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'warning' to line {line_number}")
elif level_code == 'DEBUG':
    text.tag_add("debug", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'debug' to line {line_number}")
elif level_code == 'INFO':
    text.tag_add("info", f"{line_number}.0", f"{line_number}.end")
    print(f"  Applied tag: 'info' to line {line_number}")

# Check what tags are on this line
tags_on_line = text.tag_names(f"{line_number}.0")
print(f"  Tags on line {line_number}: {tags_on_line}")

text.config(state=tk.DISABLED)

print("\n" + "="*60)
print("Window opened. The line should be RED (ERROR level).")
print("If you see BLACK text instead, there's a tag issue.")
print("="*60 + "\n")

root.mainloop()
