# # Main IDE class

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os
import subprocess
import re
import time
import threading

from frontend.ide.theme import THEME
from frontend.ide.editor import EditorComponent
from frontend.ide.console import ConsoleComponent
from frontend.ide.status_bar import StatusBar
from frontend.ide.execution_insights import ExecutionInsightsPanel

# Import required compiler modules
from backend.main_compiler.lexer_module.lexer import tokenize
from backend.main_compiler.parser_module.parser_mod import parse
from backend.main_compiler.semantic_module.semantic_analyzer import SemanticAnalyzer
from backend.main_compiler.intermediate_code_module.ir_generator import IntermediateCodeGenerator
from backend.main_compiler.code_generator_module.code_generator import CodeGenerator

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
        
        # Create console frame with tabs for Console and Execution Insights
        self.console_frame = tk.Frame(self.editor_paned, bg=THEME['bg_main'])
        self.editor_paned.add(self.console_frame, weight=1)
        
        # Create notebook (tabbed interface) with custom styling
        style = ttk.Style()
        style.configure("TNotebook", background=THEME['bg_main'])
        style.map("TNotebook.Tab", background=[("selected", THEME['bg_tabs'])], 
                foreground=[("selected", THEME['fg_main'])])
        style.configure("TNotebook.Tab", background=THEME['bg_linenumbers'], 
                        foreground=THEME['fg_main'], padding=[10, 2])
        
        self.console_notebook = ttk.Notebook(self.console_frame)
        self.console_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tab frames
        self.console_tab = tk.Frame(self.console_notebook, bg=THEME['bg_main'])
        self.insights_tab = tk.Frame(self.console_notebook, bg=THEME['bg_main'])
        
        # Add tabs to notebook
        self.console_notebook.add(self.console_tab, text="Console")
        self.console_notebook.add(self.insights_tab, text="Execution Insights")
        
        # Initialize console component in console tab
        self.console_component = ConsoleComponent(self.console_tab)
        
        # Initialize execution insights component in insights tab
        self.execution_insights = ExecutionInsightsPanel(self.insights_tab)
        
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

    def create_toolbar(self):
        """Create a comprehensive toolbar with all functionality."""
        self.toolbar = tk.Frame(self.root, bg=THEME['bg_linenumbers'], bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # File operations
        self.new_btn = tk.Button(self.toolbar, text="New", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.new_file)
        self.new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.open_btn = tk.Button(self.toolbar, text="Open", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.save_btn = tk.Button(self.toolbar, text="Save", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.save_as_btn = tk.Button(self.toolbar, text="Save As", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                    relief=tk.FLAT, command=self.save_as_file)
        self.save_as_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        tk.Frame(self.toolbar, width=2, height=24, bg=THEME['fg_linenumbers']).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Edit operations
        self.undo_btn = tk.Button(self.toolbar, text="Undo", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=lambda: self.text_editor.edit_undo())
        self.undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.redo_btn = tk.Button(self.toolbar, text="Redo", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=lambda: self.text_editor.edit_redo())
        self.redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.find_btn = tk.Button(self.toolbar, text="Find", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.find_text)
        self.find_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        tk.Frame(self.toolbar, width=2, height=24, bg=THEME['fg_linenumbers']).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Help
        self.about_btn = tk.Button(self.toolbar, text="About", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.show_about)
        self.about_btn.pack(side=tk.LEFT, padx=2, pady=2)

         # Run operation
        self.run_btn = tk.Button(self.toolbar, text="Run", bg=THEME['bg_linenumbers'], fg=THEME['fg_main'],
                                relief=tk.FLAT, command=self.run_compiler)
        self.run_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
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
    
    def get_llm_explanation(self, phase, code_snippet=None, context=None):
        """
        Get an explanation from the Gemini LLM API for the current execution step.
        
        Args:
            phase (str): Current compiler phase
            code_snippet (str, optional): Relevant code being processed
            context (dict, optional): Additional context information
            
        Returns:
            str: Explanation from the LLM
        """
        try:
            import google.generativeai as genai
            
            # Configure the API 
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

            # Create a prompt
            prompt = f"""
            Explain the following step in a compiler in a simple, educational way:
            
            Phase: {phase}
            """
            
            if code_snippet:
                prompt += f"""
                Code being processed:
                ```
                {code_snippet}
                ```
                """
                
            if context:
                prompt += f"""
                Additional context:
                {context}
                """
                
            prompt += """
            Keep your explanation concise (2-3 sentences) and focus on what's happening in this specific step.
            """
            
            # Make the API call
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
                
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def run_compiler(self):
        """Run the compiler on the code in the text editor."""
        # Start a new thread for the compilation process
        threading.Thread(target=self._run_compiler_thread).start()

    def _run_compiler_thread(self):
        """Thread target for running the compiler."""

        # Save current file if needed
        if self.current_file and self.text_editor.edit_modified():
            self.save_file()
        
        # Clear console and insights
        self.console_component.clear_console()
        self.execution_insights.clear_insights()
        
        # Show the Execution Insights tab
        self.console_notebook.select(1)
        
        # Get source code
        source_code = self.text_editor.get(1.0, tk.END)
        
        # Start compilation with enhanced insights
        self.execution_insights.add_phase_start("Compilation", 
            "Starting the compilation process for your APBL program.")
        
        # Tokenize the source code
        print("[1] Tokenizing the source code...\n")
        self.execution_insights.add_phase_start("Lexical Analysis", 
            self.get_llm_explanation("Lexical Analysis", source_code))
        
        try:
            tokens = tokenize(source_code, "backend/main_compiler/lexer_module/lexer_output.txt")
            print("Tokenization complete.\n\n")
            
            # Get first few tokens for insight
            token_sample = str(tokens[:5]) if len(tokens) > 5 else str(tokens)
            self.execution_insights.add_phase_end("Lexical Analysis", 
                f"Successfully converted source code into {len(tokens)} tokens.\nFirst few tokens: {token_sample}")
            
        except Exception as e:
            print(f"Error: {e}\n\n")
            self.execution_insights.add_insight("Lexical Analysis Error", 
                source_code, f"Error during tokenization: {e}")
            return
        
        # Parse the tokens
        print("[2] Parsing the tokens...\n")
        self.execution_insights.add_phase_start("Parsing", 
            self.get_llm_explanation("Parsing", context=f"Working with {len(tokens)} tokens"))
        
        try:
            ast, symbol_table, syntax_errors = parse(tokens)
            
            if syntax_errors:
                print("Parsing completed with errors. Check parser_errors.txt.\n\n")
                print("Compilation aborted.\n")
                
                # Display errors from files
                self.display_errors("backend/main_compiler/parser_module/parser_errors.txt", "Parser Errors")
                
                # Add to insights
                with open("backend/main_compiler/parser_module/parser_errors.txt", "r") as f:
                    error_content = f.read()
                self.execution_insights.add_insight("Parsing Errors", 
                    None, f"Syntax errors found during parsing:\n{error_content}")
                return
            else:
                print("Parsing completed successfully.\n\n")
                self.execution_insights.add_phase_end("Parsing", 
                    "Successfully constructed the Abstract Syntax Tree (AST) and Symbol Table.")
                
                # Perform semantic analysis
                print("[3] Performing semantic analysis...\n")
                self.execution_insights.add_phase_start("Semantic Analysis", 
                    self.get_llm_explanation("Semantic Analysis"))
                
                try:
                    semantic_analyzer = SemanticAnalyzer(ast)
                    semantic_errors = semantic_analyzer.analyze()
                    
                    if semantic_errors:
                        print("Semantic analysis completed with errors.\n\n")
                        print("Compilation aborted.\n")
                        
                        # Display errors from files
                        self.display_errors("backend/main_compiler/semantic_module/semantic_errors.txt", "Semantic Errors")
                        
                        # Add to insights
                        with open("backend/main_compiler/semantic_module/semantic_errors.txt", "r") as f:
                            error_content = f.read()
                        self.execution_insights.add_insight("Semantic Analysis Errors", 
                            None, f"Semantic errors found during analysis:\n{error_content}")
                        return
                    else:
                        print("Semantic analysis completed successfully.\n\n")
                        self.execution_insights.add_phase_end("Semantic Analysis", 
                            "Successfully verified program semantics. No type errors or scope issues found.")
                        
                        # Generate intermediate code
                        print("[4] Generating intermediate code...\n")
                        self.execution_insights.add_phase_start("Intermediate Code Generation", 
                            self.get_llm_explanation("Intermediate Code Generation"))
                        
                        try:
                            code_generator = IntermediateCodeGenerator(ast)
                            intermediate_code = code_generator.generate()
                            print("Intermediate code generated successfully.\n\n")
                            self.execution_insights.add_phase_end("Intermediate Code Generation", 
                                "Successfully generated intermediate representation of the program.")
                            
                            # Generate Python code
                            print("[5] Generating Python code...\n")
                            self.execution_insights.add_phase_start("Code Generation", 
                                self.get_llm_explanation("Code Generation"))
                            
                            generator = CodeGenerator()
                            success = generator.generate()
                            if success:
                                print("=== Running Generated Code ===\n\n")
                                self.execution_insights.add_phase_end("Code Generation", 
                                    "Successfully generated Python code from the intermediate representation.")
                                
                                # Run the generated Python code
                                self.execution_insights.add_phase_start("Execution", 
                                    self.get_llm_explanation("Execution"))
                                self.run_generated_code()
                            else:
                                print("Code generation failed.\n")
                                self.execution_insights.add_insight("Code Generation Error", 
                                    None, "Failed to generate Python code from the intermediate representation.")
                                
                        except Exception as e:
                            print(f"Intermediate code generation error: {e}\n\n")
                            self.execution_insights.add_insight("Intermediate Code Generation Error", 
                                None, f"Error during intermediate code generation: {e}")
                            return
                        
                except Exception as e:
                    print(f"Semantic analysis error: {e}\n\n")
                    self.execution_insights.add_insight("Semantic Analysis Error", 
                        None, f"Error during semantic analysis: {e}")
                    return
                
        except Exception as e:
            print(f"Parsing error found: {e}\n\n")
            self.execution_insights.add_insight("Parsing Error", 
                None, f"Error during parsing: {e}")
            return
    
    def run_generated_code(self):
        """Run the generated Python code and display its output in the console."""
        generated_code_path = "backend/main_compiler/code_generator_module/generated_code.py"
        if os.path.exists(generated_code_path):
            try:
                # Get the generated code content for insights
                with open(generated_code_path, "r") as f:
                    generated_code = f.read()
                
                # Run the generated Python code and capture the output
                result = subprocess.run(
                    [sys.executable, generated_code_path],
                    capture_output=True,
                    text=True
                )
                
                # Switch to console tab to show the output
                self.console_notebook.select(0)
                
                # Display the output in the console
                if result.stdout:
                    self.console_component.print_to_console(result.stdout)
                    self.console_component.print_to_console("\n")
                
                if result.stderr:
                    print("Errors:\n", "error")
                    print(result.stderr, "error")
                    print("\n")
                    
                    # Add to insights
                    self.execution_insights.add_insight("Execution Error", 
                        generated_code, f"Error during code execution:\n{result.stderr}")
                
                if not result.stdout and not result.stderr:
                    self.console_component.print_to_console("Program executed with no output.\n")
                
                self.console_component.print_to_console("=== Execution Complete ===\n", "success")
                
                # Complete the execution phase in insights
                output_summary = result.stdout if result.stdout else "No output generated."
                self.execution_insights.add_phase_end("Execution", 
                    f"Program execution completed successfully.\nOutput shown in Console tab.")
                
                # Add final compilation summary
                self.execution_insights.add_insight("Compilation Complete", 
                    None, "All compilation phases completed successfully. The program has been executed.")
                
            except Exception as e:
                print(f"Error running generated code: {e}\n", "error")
                self.execution_insights.add_insight("Execution Error", 
                    None, f"Error running generated code: {e}")
        else:
            print(f"Generated code file not found at {generated_code_path}.\n", "error")
            self.execution_insights.add_insight("Execution Error", 
                None, f"Generated code file not found at {generated_code_path}.")
    
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