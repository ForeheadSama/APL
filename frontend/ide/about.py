import tkinter as tk
from tkinter import ttk, font
import os

class AboutWindow:
    def __init__(self, parent, theme):
        # Create the about window
        self.about_dialog = tk.Toplevel(parent)
        self.about_dialog.title("About APBL IDE")
        self.about_dialog.geometry("700x800")
        self.about_dialog.resizable(False, False)
        self.about_dialog.transient(parent)
        self.about_dialog.configure(bg=theme['bg_main'])
        
        # Center the window on the screen
        self.center_window(parent)
        
        # Create a frame with padding
        main_frame = tk.Frame(self.about_dialog, bg=theme['bg_main'], padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo or title
        title_label = tk.Label(
            main_frame, 
            text="APBL IDE", 
            font=("Courier", 24, "bold"),
            bg=theme['bg_main'],
            fg=theme['fg_main']
        )
        title_label.pack(pady=(0, 5))
        
        # Version
        version_label = tk.Label(
            main_frame, 
            text="Professional Edition v1.0", 
            font=("Arial", 12),
            bg=theme['bg_main'],
            fg=theme['highlight_line']
        )
        version_label.pack(pady=(0, 20))
        
        # Create a scrollable text widget for the description
        desc_frame = tk.Frame(main_frame, bg=theme['bg_main'])
        desc_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar for the description
        canvas = tk.Canvas(desc_frame, bg=theme['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=canvas.yview)
        
        desc_inner_frame = tk.Frame(canvas, bg=theme['bg_main'])
        
        # Configure scrollbar and canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create window in canvas and configure scrolling
        canvas_frame = canvas.create_window((0, 0), window=desc_inner_frame, anchor="nw")
        
        # Create heading and section styles
        heading_font = font.Font(family="Arial", size=12, weight="bold")
        section_font = font.Font(family="Courier", size=10, weight="bold")
        text_font = font.Font(family="Arial", size=9)
        
        # Project Description
        heading = tk.Label(
            desc_inner_frame,
            text="Advanced Programming for Booking Language (APBL)",
            font=heading_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w"
        )
        heading.pack(fill=tk.X, pady=(0, 10))
        
        # Overview Section
        overview_label = tk.Label(
            desc_inner_frame,
            text="Overview",
            font=section_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify='center',
            anchor="w"
        )
        overview_label.pack(fill=tk.X, pady=(5, 5), anchor="center")
        
        overview_text = (
            "APBL is a domain-specific programming language (DSL) designed to facilitate "
            "ticket booking applications. It allows developers to create programs that handle "
            "user registration, ticket reservations, and booking confirmations with minimal complexity. "
            "It is specifically designed to facilitate ticket booking operations through a natural "
            "language interface."
        )
        
        overview_content = tk.Label(
            desc_inner_frame,
            text=overview_text,
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w",
            wraplength=550
        )
        overview_content.pack(fill=tk.X, pady=(0, 10))
        
        # Language Features Section
        features_label = tk.Label(
            desc_inner_frame,
            text="Language Features",
            font=section_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify='center',
            anchor="w"
        )
        features_label.pack(fill=tk.X, pady=(5, 5), anchor="center")
        
        features_text = (
            "Unlike general-purpose languages, which are intended for a broad range of applications, "
            "this language is tailored to address the particular needs of users within the ticket booking domain. "
            "It enables users to interact with a system for tasks such as reserving tickets, user registration, "
            "and querying available options, providing a streamlined and efficient approach to these "
            "domain-specific requirements.\n\n"
            "Furthermore, the language is considered a high-level language. High-level languages are designed "
            "to be closer to human languages, with simplified syntax and abstraction from the underlying hardware. "
            "This characteristic is evident in the developed language, which is built to be user-friendly and intuitive, "
            "enabling users to easily express ticket booking operations. The language abstracts away complex "
            "system-level operations, focusing instead on the logic and tasks the user intends to perform, "
            "making it accessible even for those with minimal programming experience."
        )
        
        features_content = tk.Label(
            desc_inner_frame,
            text=features_text,
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w",
            wraplength=550
        )
        features_content.pack(fill=tk.X, pady=(0, 10))
        
        # Compiler Implementation Section
        compiler_label = tk.Label(
            desc_inner_frame,
            text="Compiler Implementation",
            font=section_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify='center',
            anchor="w"
        )
        compiler_label.pack(fill=tk.X, pady=(5, 5), anchor="center")
        
        compiler_text = (
            "The APBL compiler was developed using PLY (Python Lex-Yacc), a Python-based tool "
            "for lexing and parsing. PLY provides functionality similar to traditional compiler "
            "tools like Lex and Yacc but within a Python environment. It was chosen for its flexibility "
            "in defining grammar rules and handling syntax analysis efficiently. The compiler consists of:"
        )
        
        compiler_content = tk.Label(
            desc_inner_frame,
            text=compiler_text,
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w",
            wraplength=550
        )
        compiler_content.pack(fill=tk.X, pady=(0, 5))
        
        # Compiler Phases
        phases_frame = tk.Frame(desc_inner_frame, bg=theme['bg_main'], padx=20)
        phases_frame.pack(fill=tk.X, pady=(0, 10))
        
        phases_text = (
            "• Lexical Analysis: Tokenizing APBL code into meaningful components.\n"
            "• Syntax Analysis: Constructing an Abstract Syntax Tree (AST) based on predefined grammar rules.\n"
            "• Semantic Analysis: Ensuring correct interpretation of booking-related operations.\n"
            "• Intermediate Code Generation: Translates APBL code into a simplified version of the code that retains its logical structure but is easier to process in later stages.\n"
            "• Code Generation and Execution: Generate executable Python code from the APBL commands. This Python code is then executed to interact with the ticket booking system, performing actions such as user registration, querying available tickets, and booking reservations."
        )
        
        phases_content = tk.Label(
            phases_frame,
            text=phases_text,
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w",
            wraplength=530
        )
        phases_content.pack(fill=tk.X)
        
        # Developers Section
        developers_label = tk.Label(
            desc_inner_frame,
            text="Developers",
            font=section_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify='center',
            anchor="w"
        )
        developers_label.pack(fill=tk.X, pady=(5, 5), anchor="center")
        
        developers_text = (
            "Britney Vassell\n"
            "Alex-Ann Burrell\n"
            "Tanea Baccas\n"
            "Sanoya Gordon\n\n"
            "Students at the University of Technology, Jamaica."
        )
        
        developers_content = tk.Label(
            desc_inner_frame,
            text=developers_text,
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['fg_main'],
            justify=tk.LEFT,
            anchor="w"
        )
        developers_content.pack(fill=tk.X, pady=(0, 10))
        
        # Copyright info
        copyright_label = tk.Label(
            desc_inner_frame, 
            text="©2025 All Rights Reserved", 
            font=text_font,
            bg=theme['bg_main'],
            fg=theme['highlight_line'],
            justify='center'
        )
        copyright_label.pack(fill=tk.X, pady=(10, 0), anchor="center")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        desc_inner_frame.bind("<Configure>", configure_scroll_region)
        
        # Make canvas expand with the window
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind("<Configure>", configure_canvas)
        
        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Close button
        close_btn = tk.Button(
            main_frame, 
            text="Close", 
            command=self.about_dialog.destroy,
            bg=theme['bg_linenumbers'],
            fg=theme['fg_main'],
            width=10,
            height=1,
            relief=tk.FLAT
        )
        close_btn.pack(pady=(20, 0))
    
    def center_window(self, parent):
        """Center the window on the screen relative to parent."""
        parent.update_idletasks()
        
        # Get parent window position and dimensions
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_x()
        py = parent.winfo_y()
        
        # Get about dialog dimensions
        w = 650
        h = 550
        
        # Calculate position
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        
        # Set position
        self.about_dialog.geometry(f"{w}x{h}+{x}+{y}")