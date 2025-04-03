import tkinter as tk
from frontend.ide.theme import THEME

class ToolbarComponent:
    def __init__(self, parent, ide_instance):
        self.parent = parent
        self.ide = ide_instance
        
        # Create the toolbar
        self.toolbar = tk.Frame(self.parent, bg=THEME['bg_linenumbers'], bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Initialize toolbar buttons
        self.create_help_buttons()
        self.create_run_button()

    def create_help_buttons(self):
        """Create help buttons."""
        self.about_btn = self.create_button("About", self.ide.show_about)
    
    def create_run_button(self):
        """Create run button."""
        self.run_btn = self.create_button("Run", self.ide.compiler_runner.run_compiler)
        self.run_btn.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def create_button(self, text, command):
        """Create a styled toolbar button."""
        button = tk.Button(
            self.toolbar, 
            text=text, 
            bg=THEME['bg_linenumbers'], 
            fg=THEME['fg_main'],
            relief=tk.FLAT, 
            command=command
        )
        button.pack(side=tk.LEFT, padx=2, pady=2)
        return button
    
    def create_separator(self):
        """Create a visual separator in the toolbar."""
        separator = tk.Frame(
            self.toolbar, 
            width=2, 
            height=24, 
            bg=THEME['fg_linenumbers']
        )
        separator.pack(side=tk.LEFT, padx=5, pady=2)
        return separator
    
    def create_find_dialog(self):
        """Create a find dialog if it doesn't exist."""
        from frontend.ide.find_dialogue import FindDialog

        self.ide.find_dialog = FindDialog(self.ide.root, self.ide.text_editor)
        self.ide.find_dialog.show()