# ide.py
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import sys
import os
import json
import re  # Added for regex support
from lexer_module.lexer import tokenize
from parser_module.parser_mod import parse
from semantic_module.semantic_analyzer import SemanticAnalyzer
from intermediate_code_module.ir_generator import IntermediateCodeGenerator
from code_generator_module.code_generator import CodeGenerator  # Import CodeGenerator

# Reserved words and their categories for syntax highlighting
reserved_categories = {
    # Core Command Keywords
    'book': 'command',
    'cancel': 'command',
    'list': 'command',
    'check': 'command',
    'pay': 'command',
    'display': 'command',
    'accept': 'command',
    
    # Prepositions and Conjunctions
    'for': 'preposition',
    'on': 'preposition',
    'event': 'preposition',

    # Objects and Topics
    'ticket': 'object',
    'tickets': 'object',
    'events': 'object',
    'availability': 'object',
    'price': 'object',
    
    # Data Types
    'string': 'datatype',
    'int': 'datatype',
    'date': 'datatype',
    
    # Control Flow
    'if': 'control',
    'else': 'control'
}

# Colors for syntax highlighting
syntax_colors = {
    'command': 'indigo',
    'preposition': 'indigo',
    'object': 'indigo',
    'datatype': 'purple',
    'control': 'blue',
    'comment': 'violet'
}

class APBLIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("APBL IDE - Version 1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5f5")  # Light gray background

        # Create a frame for the text editor and line numbers
        self.editor_frame = tk.Frame(root, bg="#f5f5f5")
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=5, pady=5, wrap=tk.NONE, bg="#e0e0e0", fg="#555555", bd=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.config(state=tk.DISABLED)  # Make line numbers read-only

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(self.editor_frame, wrap=tk.WORD, font=("Courier", 11), bg="#FFFAF0", fg="#333333", insertbackground="#333333", bd=0)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_editor.bind("<KeyRelease>", self.on_text_change)
        self.text_editor.bind("<MouseWheel>", self.on_text_change)
        self.text_editor.bind("<Button-4>", self.on_text_change)
        self.text_editor.bind("<Button-5>", self.on_text_change)

        # Compiler output console
        self.console = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 11), height=10, bg="#FFF8E7", fg="#E23D28", bd=0)
        self.console.pack(fill=tk.BOTH, expand=False)
        self.console.config(state=tk.DISABLED)  # Make console read-only

        # Menu bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Run menu
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.run_menu.add_command(label="Run", command=self.run_compiler)
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)

        # Initialize line numbers
        self.update_line_numbers()

    def on_text_change(self, event=None):
        """
        Handle text changes and update line numbers and syntax highlighting.
        """
        self.update_line_numbers()
        self.highlight_syntax()

    def update_line_numbers(self):
        """
        Update the line numbers in the sidebar.
        """
        # Get the number of lines in the text editor
        lines = self.text_editor.get("1.0", tk.END).count("\n") + 1

        # Update the line numbers widget
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        for line in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{line}\n")
        self.line_numbers.config(state=tk.DISABLED)

    def highlight_syntax(self, event=None):
        """
        Apply syntax highlighting to the text editor based on reserved words and comments.
        Only exact matches are highlighted.
        """
        # Remove all existing tags
        self.text_editor.tag_remove("highlight", "1.0", tk.END)

        # Get the entire content of the text editor
        text_content = self.text_editor.get("1.0", tk.END)

        # Highlight reserved words
        for word, category in reserved_categories.items():
            # Use regex to find all exact matches of the word
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.finditer(pattern, text_content)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_editor.tag_add(category, start, end)

        # Highlight comments (lines starting with $$)
        for line_num, line in enumerate(text_content.splitlines(), start=1):
            if line.strip().startswith("$$"):
                start = f"{line_num}.0"
                end = f"{line_num}.end"
                self.text_editor.tag_add('comment', start, end)

        # Configure tag colors
        for category, color in syntax_colors.items():
            self.text_editor.tag_config(category, foreground=color)

    def open_file(self):
        """
        Open a file and load its content into the text editor.
        """
        file_path = filedialog.askopenfilename(filetypes=[("APBL Files", "*.apbl"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(tk.END, file.read())
            self.on_text_change()

    def save_file(self):
        """
        Save the content of the text editor to a file.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".apbl", filetypes=[("APBL Files", "*.apbl"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_editor.get(1.0, tk.END))

    def run_compiler(self):
        """
        Run the compiler on the code in the text editor and display the output in the console.
        """
        source_code = self.text_editor.get(1.0, tk.END)

        # Clear previous output
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)

        # Tokenize the source code
        print("[1] Tokenizing the source code...")
        try:
            tokens = tokenize(source_code, "lexer_module/lexer_output.txt")
            print("Tokenization complete.\n")
        except Exception as e:
            print(f"{e}\n")
            return

        # Parse the tokens
        print("[2] Parsing the tokens...")
        try:
            ast, symbol_table, syntax_errors = parse(tokens)

            #print ("Symbol Table: ", symbol_table) #DEBUGGING
            if syntax_errors:
                print("Parsing completed with errors. Check parser_errors.txt.\n")
                print("Compilation aborted.")
            else:
                print("Parsing completed successfully.\n")

                # Perform semantic analysis
                print("[3] Performing semantic analysis...")
                try:
                    semantic_analyzer = SemanticAnalyzer(ast)
                    semantic_errors = semantic_analyzer.analyze()

                    if semantic_errors:
                        print("Semantic analysis completed with errors. Check parser_errors.txt.\n")
                        print("Compilation aborted.")
                    else:
                        print("Semantic analysis completed successfully. AST saved to parseroutput.json\n")

            
                        # Generate intermediate code
                        print("\n[4] Generating intermediate code...")
                        try:
                            code_generator = IntermediateCodeGenerator(ast)
                            intermediate_code = code_generator.generate()
                            print("Intermediate code generated successfully.\n")

                            generator = CodeGenerator()
                            success = generator.generate()
                            if success:
                                print("Code generation completed successfully")
                                print("--------------------------------------------------------------------\n")

                                

                            else:
                                print("Code generation failed")
                        except Exception as e:
                            print(f"Intermediate code generation error: {e}\n")
                            self.console.insert("Error during compilation. Compilation aborted.")
                            return

                        print("--------------------------------------------------------------------\n")

                except Exception as e:
                    print("Semantic analysis error: {e}\n")
                    return

                
        except Exception as e:
            print(f"Parsing error: {e}\n")
            return

        
        
        # Display errors from files
        self.display_errors("parser_module/parser_errors.txt", "Parser Errors")
        self.display_errors("semantic_module/semantic_errors.txt", "Semantic Errors")

        self.console.config(state=tk.DISABLED)

    def display_errors(self, file_path, error_type):
        """
        Display errors from a file in the console.
        """
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                errors = file.read()
                if errors:
                    self.console.insert(tk.END, f"{errors}\n")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    ide = APBLIDE(root)
    root.mainloop()