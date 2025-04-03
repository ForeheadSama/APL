import tkinter as tk
from tkinter import ttk
from frontend.ide.theme import THEME

def style_scrollbars(widget):
    """Recursively style all scrollbars in the application."""
    if isinstance(widget, tk.Scrollbar):
        widget.config(
            bg=THEME['bg_linenumbers'],
            troughcolor=THEME['bg_main'],
            activebackground=THEME['bg_linenumbers'],
            highlightbackground=THEME['bg_main'],
            highlightthickness=1,
            borderwidth=0,
            relief=tk.FLAT
        )
    
    # Recursively process children
    for child in widget.winfo_children():
        style_scrollbars(child)

def setup_notebook_style():
    """Configure the notebook (tabbed interface) style."""
    style = ttk.Style()

    # Configure the notebook itself
    style.configure("TNotebook", background=THEME['bg_main'])
    
    # Configure the tabs
    style.configure("TNotebook.Tab", 
                   background=THEME['bg_linenumbers'], 
                   foreground=THEME['fg_main'], 
                   padding=[10, 2])
    
    # Style the selected tab
    style.map("TNotebook.Tab", 
              background=[("selected", THEME['bg_linenumbers'])],
              foreground=[("selected", THEME['fg_main'])])

    # Configure the client area (the area inside the tabs)
    style.configure("TFrame", background=THEME['bg_main'])

    # Configure vertical scrollbars
    style.configure("Vertical.TScrollbar", 
                    background=THEME['bg_linenumbers'], 
                    troughcolor=THEME['bg_main'], 
                    arrowcolor=THEME['fg_main'])
    
    # Map scrollbar states for hover effects
    style.map("Vertical.TScrollbar", 
              background=[("active", '#000000')],
              troughcolor=[("active", THEME['bg_main'])])
    