# Console output components

import tkinter as tk
from tkinter import scrolledtext
from .theme import THEME

class ConsoleComponent:
    """Console output component for displaying compiler messages."""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_console()
    
    def setup_console(self):
        """Create the output console."""
        # Console header
        header_frame = tk.Frame(self.parent_frame, bg=THEME['bg_linenumbers'], height=25)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        header_label = tk.Label(header_frame, text="Console Output", bg=THEME['bg_linenumbers'], 
                               fg=THEME['fg_linenumbers'], padx=5, pady=2)
        header_label.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(header_frame, text="Clear", bg=THEME['bg_linenumbers'], 
                             fg=THEME['fg_linenumbers'], relief=tk.FLAT, 
                             command=self.clear_console)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Console text area
        self.console = scrolledtext.ScrolledText(
            self.parent_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=THEME['bg_console'],
            fg=THEME['fg_console'],
            bd=0,
            padx=5,
            pady=5
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)
        
        # Configure tags for console
        self.console.tag_configure("error", foreground=THEME['error_color'])
        self.console.tag_configure("success", foreground="#6A9955")
        self.console.tag_configure("info", foreground="#569CD6")
    
    def clear_console(self):
        """Clear the console output."""
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
    
    def print_to_console(self, text, tag=None):
        """Print text to the console with optional tag."""
        self.console.config(state=tk.NORMAL)
        if tag:
            self.console.insert(tk.END, text, tag)
        else:
            self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)