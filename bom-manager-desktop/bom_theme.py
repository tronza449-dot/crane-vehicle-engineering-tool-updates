"""Clean, high-contrast Thai-first Tkinter/ttk design system.

No paid libraries, external fonts, graphics or network access required.
"""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


BG = "#F3F7FC"
PANEL = "#FFFFFF"
TEXT = "#142B46"
MUTED = "#596E85"
NAVY = "#173B60"
PRIMARY = "#1263CE"
PRIMARY_HOVER = "#0A51B2"
BORDER = "#D7E3EF"
FONT = "Leelawadee UI"  # Installed on Windows 10/11; Tk falls back on other OS.


def activate(root):
    """Apply consistent sizes, Thai fonts, accessible contrast and flat controls."""
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
                 "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont"):
        try:
            f = tkfont.nametofont(name)
            f.configure(family=FONT, size=12 if name not in ("TkSmallCaptionFont",) else 11)
        except tk.TclError:
            pass
    root.option_add("*Font", (FONT, 12))
    root.option_add("*background", BG)
    root.configure(bg=BG)

    style.configure(".", font=(FONT, 12))
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 12))
    style.configure("TLabelFrame", background=PANEL, bordercolor=BORDER, borderwidth=1,
                    relief="solid", padding=9)
    style.configure("TLabelFrame.Label", background=BG, foreground=NAVY,
                    font=(FONT, 12, "bold"))
    style.configure("TEntry", font=(FONT, 12), padding=(10, 8),
                    fieldbackground=PANEL, foreground=TEXT, bordercolor=BORDER, relief="solid")
    style.map("TEntry", bordercolor=[("focus", PRIMARY)])
    style.configure("TCombobox", font=(FONT, 12), padding=(8, 7),
                    foreground=TEXT, fieldbackground=PANEL)
    style.configure("TNotebook", background=BG, borderwidth=0, padding=(0, 0))
    style.configure("TNotebook.Tab", font=(FONT, 12, "bold"), padding=(24, 12),
                    background="#E8EFF7", foreground=NAVY, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", PANEL), ("active", "#DFEBFF")],
              foreground=[("selected", PRIMARY), ("active", NAVY)],
              lightcolor=[("selected", PANEL)],
              bordercolor=[("selected", BORDER)])
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                    font=(FONT, 12), rowheight=42, borderwidth=0, relief="flat")
    style.configure("Treeview.Heading", background="#EAF1F9", foreground=NAVY,
                    font=(FONT, 11, "bold"), padding=(12, 13), relief="flat")
    style.map("Treeview", background=[("selected", "#CFE4FF")],
              foreground=[("selected", TEXT)])
    style.map("Treeview.Heading", background=[("active", "#DFEAF7")])
    style.configure("TScrollbar", background="#DEE8F2", arrowcolor=NAVY)
    style.configure("TProgressbar", background=PRIMARY, troughcolor="#E3EBF4",
                    borderwidth=0, thickness=14)
    style.configure("TButton", font=(FONT, 11, "bold"), padding=(15, 9),
                    background=PANEL, foreground=NAVY, borderwidth=1,
                    bordercolor=BORDER, relief="flat")
    style.map("TButton",
              background=[("disabled", "#E5EAF0"), ("pressed", "#C8DAEE"),
                          ("active", "#EBF3FD")],
              foreground=[("disabled", "#8593A3")],
              bordercolor=[("active", "#98BCE7")])
    style.configure("Primary.TButton", font=(FONT, 11, "bold"),
                    background=PRIMARY, foreground=PANEL, bordercolor=PRIMARY,
                    padding=(16, 10), relief="flat")
    style.map("Primary.TButton",
              background=[("disabled", "#CEDBEA"), ("pressed", "#073E88"),
                          ("active", PRIMARY_HOVER)],
              foreground=[("disabled", "#6C8198"), ("active", PANEL)])
    style.configure("Danger.TButton", font=(FONT, 11, "bold"),
                    background="#FFF0F0", foreground="#AC2A3B",
                    bordercolor="#F6D1D7", padding=(13, 9), relief="flat")
    style.map("Danger.TButton", background=[("active", "#FFE2E6")])
    style.configure("Success.TButton", font=(FONT, 11, "bold"),
                    background="#E7F8EE", foreground="#157346",
                    bordercolor="#BDE7CD", padding=(15, 9), relief="flat")
    style.map("Success.TButton", background=[("active", "#D4F1E1")])
    style.configure("Header.TLabel", font=(FONT, 21, "bold"), foreground=NAVY)
    style.configure("Section.TLabel", font=(FONT, 17, "bold"), foreground=NAVY)
    style.configure("Hint.TLabel", font=(FONT, 11), foreground=MUTED)
    style.configure("Metric.TLabel", font=(FONT, 24, "bold"), foreground=PRIMARY)
    style.configure("Footer.TLabel", font=(FONT, 11), foreground=MUTED)
    return style


def paint_stripes(tree, count):
    """Neutral alternate row fills; maintain distinct selection highlight."""
    tree.tag_configure("evenrow", background=PANEL)
    tree.tag_configure("oddrow", background="#F7FAFE")
    for pos, iid in enumerate(tree.get_children()):
        tree.item(iid, tags=("oddrow" if pos % 2 else "evenrow",))
