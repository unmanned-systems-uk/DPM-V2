#!/usr/bin/env python3
"""
Test script to verify Tkinter color tag functionality
"""
import tkinter as tk
from tkinter import scrolledtext

def test_colors():
    root = tk.Tk()
    root.title("Tkinter Color Test")
    root.geometry("800x600")

    text = scrolledtext.ScrolledText(root, font=('Courier New', 10), wrap=tk.WORD)
    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Configure color tags
    text.tag_config("red", foreground="#FF0000")
    text.tag_config("green", foreground="#00FF00")
    text.tag_config("blue", foreground="#0080FF")
    text.tag_config("magenta", foreground="#FF00FF")
    text.tag_config("orange", foreground="#FFA500")
    text.tag_config("gray", foreground="#808080")
    text.tag_config("highlight", background="#FFFF00", foreground="#000000")

    # Insert test lines
    text.insert(tk.END, "Plain text - should be black/default\n")

    text.insert(tk.END, "RED text - should be red\n")
    text.tag_add("red", "2.0", "2.end")

    text.insert(tk.END, "GREEN text - should be green\n")
    text.tag_add("green", "3.0", "3.end")

    text.insert(tk.END, "BLUE text - should be blue\n")
    text.tag_add("blue", "4.0", "4.end")

    text.insert(tk.END, "MAGENTA text - should be magenta\n")
    text.tag_add("magenta", "5.0", "5.end")

    text.insert(tk.END, "ORANGE text - should be orange\n")
    text.tag_add("orange", "6.0", "6.end")

    text.insert(tk.END, "GRAY text - should be gray\n")
    text.tag_add("gray", "7.0", "7.end")

    text.insert(tk.END, "HIGHLIGHTED text - should have yellow background\n")
    text.tag_add("highlight", "8.0", "8.end")

    text.insert(tk.END, "\nOverlapping tags test:\n")
    text.insert(tk.END, "This line has BLUE domain color\n")
    text.tag_add("blue", "10.0", "10.end")

    text.insert(tk.END, "This line has BLUE + RED (error should win)\n")
    text.tag_add("blue", "11.0", "11.end")
    text.tag_add("red", "11.0", "11.end")

    # Raise red tag priority
    text.tag_raise("red")

    text.insert(tk.END, "\nAfter tag_raise('red'), line 11 should now be RED\n")

    text.config(state=tk.DISABLED)

    print("\n" + "="*60)
    print("Tkinter Color Test")
    print("="*60)
    print("\nIf you see colors in the window, tkinter color support works!")
    print("If all text is the same color (black), there may be a theme issue.")
    print("\nCheck the window and close it to continue...")
    print("="*60 + "\n")

    root.mainloop()

if __name__ == "__main__":
    test_colors()
