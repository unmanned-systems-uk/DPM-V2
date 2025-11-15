#!/usr/bin/env python3
"""
Test log_viewer_gui.py color configuration
Debug script to check if tags are properly configured
"""
import tkinter as tk
from tkinter import scrolledtext
from utils.log_colors import configure_tkinter_text_tags, get_domain_colors_hex, get_level_colors_hex

def test_log_viewer_colors():
    print("\n" + "="*60)
    print("Log Viewer Color Configuration Test")
    print("="*60)

    # Load colors from config
    domain_colors = get_domain_colors_hex()
    level_colors = get_level_colors_hex()

    print("\nLoaded from config/log_aggregator.json:")
    print(f"  Domain colors: {domain_colors}")
    print(f"  Level colors: {level_colors}")

    # Create window
    root = tk.Tk()
    root.title("Log Viewer Color Test")
    root.geometry("1000x600")

    text = scrolledtext.ScrolledText(root, font=('Courier New', 9), wrap=tk.NONE)
    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Configure tags using the same function as log_viewer_gui.py
    configure_tkinter_text_tags(text)

    # Check tag configuration
    print("\nConfigured Tkinter tags:")
    for tag in ["air", "ground", "error", "warning", "info", "debug", "highlight"]:
        try:
            fg = text.tag_cget(tag, "foreground")
            bg = text.tag_cget(tag, "background")
            font = text.tag_cget(tag, "font")
            print(f"  {tag:10} → fg={fg:8} bg={bg:8} font={font}")
        except tk.TclError as e:
            print(f"  {tag:10} → ERROR: {e}")

    # Insert sample log entries (simulating real log viewer)
    print("\nInserting sample log entries...")

    samples = [
        {"domain": "AIR", "level": "INFO", "line": "23:45:01.123 [AIR   ] [INFO   ] [CAMERA ] Camera initialized successfully"},
        {"domain": "AIR", "level": "DEBUG", "line": "23:45:02.456 [AIR   ] [DEBUG  ] [NETWORK] Heartbeat sent"},
        {"domain": "AIR", "level": "WARNING", "line": "23:45:03.789 [AIR   ] [WARNING] [SYSTEM ] Low memory warning"},
        {"domain": "AIR", "level": "ERROR", "line": "23:45:04.012 [AIR   ] [ERROR  ] [COMMAND] Command execution failed"},
        {"domain": "GROUND", "level": "INFO", "line": "23:45:05.345 [GROUND] [INFO   ] [UI     ] UI updated"},
        {"domain": "GROUND", "level": "DEBUG", "line": "23:45:06.678 [GROUND] [DEBUG  ] [NETWORK] Connection alive"},
        {"domain": "GROUND", "level": "WARNING", "line": "23:45:07.901 [GROUND] [WARNING] [SYSTEM ] Battery low"},
        {"domain": "GROUND", "level": "ERROR", "line": "23:45:08.234 [GROUND] [ERROR  ] [NETWORK] Connection lost"},
    ]

    for i, sample in enumerate(samples, start=1):
        text.insert(tk.END, sample["line"] + "\n")
        line_num = i

        # Apply domain tag
        if sample["domain"] == "AIR":
            text.tag_add("air", f"{line_num}.0", f"{line_num}.end")
        elif sample["domain"] == "GROUND":
            text.tag_add("ground", f"{line_num}.0", f"{line_num}.end")

        # Apply level tag
        level_tag = sample["level"].lower()
        text.tag_add(level_tag, f"{line_num}.0", f"{line_num}.end")

    text.config(state=tk.DISABLED)

    print("\nWindow opened. Check the display:")
    print("  - Lines 1-4: AIR domain (should have blue/level colors)")
    print("  - Lines 5-8: GROUND domain (should have magenta/level colors)")
    print("  - INFO: green, DEBUG: gray, WARNING: orange, ERROR: red (bold)")
    print("\nIf you see NO colors or all black text:")
    print("  - Your desktop theme may be overriding Tkinter colors")
    print("  - Try running: gsettings set org.gnome.desktop.interface color-scheme 'default'")
    print("  - Or check your GTK theme settings")
    print("="*60 + "\n")

    root.mainloop()

if __name__ == "__main__":
    test_log_viewer_colors()
