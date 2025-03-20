# # Main IDE class

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
import subprocess
import re

from .theme import THEME
from .editor import EditorComponent
from .console import ConsoleComponent
from .status_bar import StatusBar

# Import required compiler modules
from lexer_module.lexer import tokenize
from parser_module.parser_mod import parse
from semantic_module.semantic_analyzer import SemanticAnalyzer
from intermediate_code_module.ir_generator import IntermediateCodeGenerator
from code_generator_module.code_generator import CodeGenerator

class APBLIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("APBL IDE (Version 1.0)")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME['bg_main'])
        
        # Create the main framework
        self.setup_ui()
        
        # Set initial state
        self.current_file = None
        self.update_title()
        
        # Set keyboard shortcuts
        self.setup_shortcuts()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Create the menu bar
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create the main framework
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Create editor and console panes
        self.editor_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.editor_paned, weight=1)
        
        # Create the editor frame
        self.editor_frame = tk.Frame(self.editor_paned, bg=THEME['bg_main'])
        self.editor_paned.add(self.editor_frame, weight=3)
        
        # Initialize editor component
        self.editor_component = EditorComponent(self.editor_frame)
        self.text_editor = self.editor_component.text_editor
        
        # Create console frame
        self.console_frame = tk.Frame(self.editor_paned, bg=THEME['bg_main'])
        self.editor_paned.add(self.console_frame, weight=1)
        
        # Initialize console component
        self.console_component = ConsoleComponent(self.console_frame)
        
        # Create status bar
        self.status_bar = StatusBar(self.root, self.text_editor)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-s>", lambda event: self.save_as_file())
        self.root.bind("<F5>", lambda event: self.run_compiler())
        self.root.bind("<Control-f>", lambda event: self.find_text())
    
    def create_menu(self):
        """Create the menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=THEME['bg_main'], fg=THEME['fg_main'])
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Alt+F4")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=THEME['bg_main'], fg=THEME['fg_main'])
        self.edit_menu.add_command(label="Undo", command=lambda: self.text_editor.edit_undo(), accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=lambda: self.text_editor.edit_redo(), accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        
        # Run menu
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg=THEME['bg_main'], fg=THEME['fg_main'])
        self.run_menu.add_command(label="Run", command=self.run_compiler, accelerator="F5")
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, bg=THEME['bg_main'], fg=THEME['fg_main'])
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
    def create_toolbar(self):
        """Create a professional toolbar."""
        self.toolbar = tk.Frame(self.root, bg=THEME['bg_linenumbers'], bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # New file button
        self.new_btn = tk.Button(self.toolbar, text="New", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.new_file)
        self.new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Open file button
        self.open_btn = tk.Button(self.toolbar, text="Open", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Save file button
        self.save_btn = tk.Button(self.toolbar, text="Save", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        tk.Frame(self.toolbar, width=2, height=24, bg=THEME['fg_linenumbers']).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Run button
        self.run_btn = tk.Button(self.toolbar, text="Run", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.run_compiler)
        self.run_btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def new_file(self):
        """Create a new file."""
        if self.text_editor.edit_modified():
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save the changes?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                self.save_file()
        
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.edit_modified(False)
        self.current_file = None
        self.update_title()
    
    def open_file(self):
        """Open a file and load its content into the text editor."""
        if self.text_editor.edit_modified():
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save the changes?")
            if response is None:  # Cancel
                return
            if response:  # Yes
                self.save_file()
        
        file_path = filedialog.askopenfilename(
            filetypes=[("APBL Files", "*.apbl"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.text_editor.delete(1.0, tk.END)
                    self.text_editor.insert(tk.END, file.read())
                
                self.current_file = file_path
                self.text_editor.edit_modified(False)
                self.update_title()
                self.editor_component.on_text_change()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the content of the text editor to a file."""
        if self.current_file:
            try:
                with open(self.current_file, "w") as file:
                    file.write(self.text_editor.get(1.0, tk.END))
                self.text_editor.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the content of the text editor to a new file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".apbl",
            filetypes=[("APBL Files", "*.apbl"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as file:
                    file.write(self.text_editor.get(1.0, tk.END))
                
                self.current_file = file_path
                self.text_editor.edit_modified(False)
                self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def update_title(self):
        """Update the window title based on the current file."""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.root.title(f"{filename} - APBL IDE (Version 1.0)")
        else:
            self.root.title("Untitled - APBL IDE (Version 1.0)")
    
    def find_text(self):
        """Open a simple find dialog."""
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.geometry("300x80")
        find_dialog.resizable(False, False)
        find_dialog.transient(self.root)
        
        # Find entry
        find_frame = tk.Frame(find_dialog)
        find_frame.pack(fill=tk.X, padx=10, pady=10)
        
        find_label = tk.Label(find_frame, text="Find:")
        find_label.pack(side=tk.LEFT)
        
        find_entry = tk.Entry(find_frame, width=30)
        find_entry.pack(side=tk.LEFT, padx=5)
        find_entry.focus_set()
        

        # Buttons
        button_frame = tk.Frame(find_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        find_next_btn = tk.Button(
            button_frame, 
            text="Find Next", 
            command=lambda: self.find_next(find_entry.get())
        )
        find_next_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame, 
            text="Cancel", 
            command=find_dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to find_next
        find_entry.bind("<Return>", lambda event: self.find_next(find_entry.get()))
    
    def find_next(self, query):
        """Find the next occurrence of the given text."""
        if not query:
            return
        
        # Remove previous highlights
        self.text_editor.tag_remove("search", "1.0", tk.END)
        
        # Start search from current position
        start_pos = self.text_editor.index(tk.INSERT)
        pos = self.text_editor.search(query, start_pos, stopindex=tk.END, nocase=1)
        
        if not pos:
            # If not found from current position, start from beginning
            pos = self.text_editor.search(query, "1.0", stopindex=tk.END, nocase=1)
        
        if pos:
            # Highlight the found text
            end_pos = f"{pos}+{len(query)}c"
            self.text_editor.tag_add("search", pos, end_pos)
            self.text_editor.tag_config("search", background="#565656", foreground="#ffffff")
            
            # Move cursor and see the found text
            self.text_editor.mark_set(tk.INSERT, end_pos)
            self.text_editor.see(pos)
        else:
            messagebox.showinfo("Find", f"Cannot find '{query}'")
    
    def run_compiler(self):
        """Run the compiler on the code in the text editor."""
        # Save current file if needed
        if self.current_file and self.text_editor.edit_modified():
            self.save_file()
        
        # Clear console
        self.console_component.clear_console()
        
        # Get source code
        source_code = self.text_editor.get(1.0, tk.END)
        
        # Tokenize the source code
        print("[1] Tokenizing the source code...\n")
        try:
            tokens = tokenize(source_code, "lexer_module/lexer_output.txt")
            print("Tokenization complete.\n\n")
        except Exception as e:
            print(f"Error: {e}\n\n")
            return
        
        # Parse the tokens
        print("[2] Parsing the tokens...\n")
        try:
            ast, symbol_table, syntax_errors = parse(tokens)
            
            if syntax_errors:
                print("Parsing completed with errors. Check parser_errors.txt.\n\n")
                print("Compilation aborted.\n")
                
                # Display errors from files
                self.display_errors("parser_module/parser_errors.txt", "Parser Errors")
                return
            else:
                print("Parsing completed successfully.\n\n")
                
                # Perform semantic analysis
                print("[3] Performing semantic analysis...\n")
                try:
                    semantic_analyzer = SemanticAnalyzer(ast)
                    semantic_errors = semantic_analyzer.analyze()
                    
                    if semantic_errors:
                        print("Semantic analysis completed with errors.\n\n")
                        print("Compilation aborted.\n")
                        
                        # Display errors from files
                        self.display_errors("semantic_module/semantic_errors.txt", "Semantic Errors")
                        return
                    else:
                        print("Semantic analysis completed successfully.\n\n")
                        
                        # Generate intermediate code
                        print("[4] Generating intermediate code...\n")
                        try:
                            code_generator = IntermediateCodeGenerator(ast)
                            intermediate_code = code_generator.generate()
                            print("Intermediate code generated successfully.\n\n")
                            
                            # Generate Python code
                            print("[5] Generating Python code...\n")
                            generator = CodeGenerator()
                            success = generator.generate()
                            if success:
                                print("=== Running Generated Code ===\n\n")
                                
                                # Run the generated Python code
                                self.run_generated_code()
                            else:
                                print("Code generation failed.\n")
                        except Exception as e:
                            print(f"Intermediate code generation error: {e}\n\n")
                            return
                except Exception as e:
                    print(f"Semantic analysis error: {e}\n\n")
                    return
        except Exception as e:
            print(f"Parsing error: {e}\n\n")
            return
    
    def run_generated_code(self):
        """Run the generated Python code and display its output in the console."""
        generated_code_path = "code_generator_module/generated_code.py"
        if os.path.exists(generated_code_path):
            try:
                # Run the generated Python code and capture the output
                result = subprocess.run(
                    [sys.executable, generated_code_path],
                    capture_output=True,
                    text=True
                )
                
                # Display the output in the console
                if result.stdout:
                    self.console_component.print_to_console(result.stdout)
                    self.console_component.print_to_console("\n")
                
                if result.stderr:
                    print("Errors:\n", "error")
                    print(result.stderr, "error")
                    print("\n")
                
                if not result.stdout and not result.stderr:
                    self.console_component.print_to_console("Program executed with no output.\n")
                
                self.console_component.print_to_console("=== Execution Complete ===\n", "success")
            except Exception as e:
                print(f"Error running generated code: {e}\n", "error")
        else:
            print(f"Generated code file not found at {generated_code_path}.\n", "error")
    
    def display_errors(self, file_path, error_type):
        """Display errors from a file in the console."""
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                errors = file.read()
                if errors:
                    self.console_component.print_to_console(f"{error_type}:\n", "error")
                    self.console_component.print_to_console(errors, "error")
                    self.console_component.print_to_console("\n")
    
    def show_about(self):
        """Show about dialog."""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About APBL IDE")
        about_dialog.geometry("400x250")
        about_dialog.resizable(False, False)
        about_dialog.transient(self.root)
        about_dialog.configure(bg=THEME['bg_main'])
        
        # Logo or title
        title_label = tk.Label(
            about_dialog, 
            text="APBL IDE", 
            font=("Arial", 18, "bold"),
            bg=THEME['bg_main'],
            fg=THEME['fg_main']
        )
        title_label.pack(pady=(20, 5))
        
        # Version
        version_label = tk.Label(
            about_dialog, 
            text="Professional Edition v1.0", 
            font=("Arial", 10),
            bg=THEME['bg_main'],
            fg=THEME['fg_main']
        )
        version_label.pack(pady=5)
        
        # Description
        desc_label = tk.Label(
            about_dialog, 
            text="An Integrated Development Environment for APBL Language\n"
                 "©2025 All Rights Reserved", 
            font=("Arial", 9),
            bg=THEME['bg_main'],
            fg=THEME['fg_main'],
            justify=tk.CENTER
        )
        desc_label.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(
            about_dialog, 
            text="Close", 
            command=about_dialog.destroy,
            bg=THEME['bg_linenumbers'],
            fg=THEME['fg_main']
        )
        close_btn.pack(pady=20)