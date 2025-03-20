# Status bar component

import tkinter as tk
from .theme import THEME

class StatusBar(tk.Frame):
    """Professional status bar that shows line and column information."""
    
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        
        # Configure appearance
        self.configure(
            bg=THEME['bg_linenumbers'],
            height=25,
            bd=1,
            relief=tk.GROOVE
        )
        
        # Status indicators
        self.position_var = tk.StringVar(value="Ln 1, Col 1")
        self.language_var = tk.StringVar(value="APBL")
        self.encoding_var = tk.StringVar(value="UTF-8")
        
        # Add status labels
        self.position_label = tk.Label(
            self, 
            textvariable=self.position_var,
            bg=THEME['bg_linenumbers'],
            fg=THEME['fg_linenumbers'],
            bd=0,
            padx=5
        )
        self.position_label.pack(side=tk.RIGHT)
        
        self.language_label = tk.Label(
            self, 
            textvariable=self.language_var,
            bg=THEME['bg_linenumbers'],
            fg=THEME['fg_linenumbers'],
            bd=0,
            padx=5
        )
        self.language_label.pack(side=tk.RIGHT)
        
        self.encoding_label = tk.Label(
            self, 
            textvariable=self.encoding_var,
            bg=THEME['bg_linenumbers'],
            fg=THEME['fg_linenumbers'],
            bd=0,
            padx=5
        )
        self.encoding_label.pack(side=tk.RIGHT)
        
        # Bind cursor movement to update position
        text_widget.bind("<ButtonRelease-1>", self.update_position)
        text_widget.bind("<KeyRelease>", self.update_position)
    
    def update_position(self, event=None):
        """Update cursor position in status bar."""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, column = cursor_pos.split('.')
            self.position_var.set(f"Ln {line}, Col {int(column) + 1}")
        except:
            pass