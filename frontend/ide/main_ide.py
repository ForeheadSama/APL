# Main IDE

import tkinter as tk
from tkinter import ttk
import sys
import os

from frontend.ide.theme import THEME
from frontend.ide.editor import EditorComponent
from frontend.ide.console import ConsoleComponent
from frontend.ide.status_bar import StatusBar
from frontend.ide.execution_insights import ExecutionInsightsPanel
from frontend.ide.toolbar import ToolbarComponent
from frontend.ide.file_manager import FileManager
from frontend.ide.find_dialogue import FindDialog
from backend.main_compiler.compiler_runner import CompilerRunner
from frontend.ide.utils import style_scrollbars, setup_notebook_style

class APBLIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("APBL IDE (Version 1.0)")
        self.root.configure(bg=THEME['bg_main'])
        
        # Initialize all components
        self.init_all_components()
        
        # Set keyboard shortcuts
        self.setup_shortcuts()
    
    def init_all_components(self):
        """Initialize all UI components in proper order."""
        # 1. create basic containers 
        self.configure_scrollbars()
        self.setup_panes()
        
        # 2. Create editor component 
        self.setup_editor()  # This creates self.text_editor
        
        # 3. Create file manager 
        self.file_manager = FileManager(self.root, self.text_editor)
        
        # 4. Create console components 
        self.setup_console()
        
        # 5. Create compiler runner
        self.compiler_runner = CompilerRunner(
            self.text_editor, 
            self.console_component,
            self.execution_insights,
            self.console_notebook
        )
        
        # 6. create toolbaR
        self.toolbar = ToolbarComponent(self.root, self)
        
        # 7. create status bar 
        self.status_bar = StatusBar(self.root, self.text_editor)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Apply scrollbar styling
        style_scrollbars(self.root)

    def configure_scrollbars(self):
        """Configure global scrollbar settings."""
        self.root.option_add("*Scrollbar.background", THEME['bg_linenumbers'])
        self.root.option_add("*Scrollbar.troughColor", THEME['bg_main'])
        self.root.option_add("*Scrollbar.activeBackground", THEME['bg_linenumbers'])
        self.root.option_add("*Scrollbar.highlightBackground", THEME['bg_main'])
        self.root.option_add("*Scrollbar.borderWidth", 0)
        self.root.option_add("*Scrollbar.highlightThickness", 0)
        self.root.option_add("*Scrollbar.elementBorderWidth", 0)
    
    def setup_panes(self):
        """Set up the main paned windows."""
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Create editor and console panes
        self.editor_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.editor_paned, weight=1)
    
    def setup_editor(self):
        """Set up the editor component."""
        # Create the editor frame
        self.editor_frame = tk.Frame(self.editor_paned, bg=THEME['bg_main'])
        self.editor_paned.add(self.editor_frame, weight=3)
        
        # Initialize editor component
        self.editor_component = EditorComponent(self.editor_frame)
        self.text_editor = self.editor_component.text_editor
    
    def setup_console(self):
        """Set up the console component."""
        # Create console frame with tabs for Console and Execution Insights
        self.console_frame = tk.Frame(self.editor_paned, bg=THEME['bg_main'])
        self.editor_paned.add(self.console_frame, weight=1)
        
        # Setup notebook style
        setup_notebook_style()
        
        # Create notebook
        self.console_notebook = ttk.Notebook(self.console_frame)
        self.console_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tab frames
        self.console_tab = ttk.Frame(self.console_notebook, style="TFrame")
        self.insights_tab = ttk.Frame(self.console_notebook, style="TFrame")
        
        # Add tabs to notebook
        self.console_notebook.add(self.console_tab, text="Console")
        self.console_notebook.add(self.insights_tab, text="Execution Insights")
        
        # Initialize console component in console tab
        self.console_component = ConsoleComponent(self.console_tab)
        
        # Initialize execution insights component in insights tab
        self.execution_insights = ExecutionInsightsPanel(self.insights_tab)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda event: self.file_manager.new_file())
        self.root.bind("<Control-o>", lambda event: self.file_manager.open_file())
        self.root.bind("<Control-s>", lambda event: self.file_manager.save_file())
        self.root.bind("<Control-Shift-s>", lambda event: self.file_manager.save_as_file())
        
        self.root.bind("<F5>", lambda event: self.compiler_runner.run_compiler())

        self.root.bind("<Control-f>", lambda event: FindDialog(self.root, self.text_editor).show())
    
    def show_about(self):
        """Show about dialog."""
        from frontend.ide.about import AboutWindow
        about_window = AboutWindow(self.root, THEME)