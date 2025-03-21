# Execution insights component to display LLM explanations of code execution

import tkinter as tk
from tkinter import scrolledtext
import time
from .theme import THEME

class ExecutionInsightsPanel:
    """Panel component for displaying LLM explanations of code execution steps."""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_panel()
        self.insights_count = 0
    
    def setup_panel(self):
        """Create the execution insights panel."""
        # Panel header
        header_frame = tk.Frame(self.parent_frame, bg=THEME['bg_linenumbers'], height=25)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        
        # header_label = tk.Label(header_frame, text="Execution Insights", bg=THEME['bg_linenumbers'], 
        #                        fg=THEME['fg_linenumbers'], padx=5, pady=2)
        # header_label.pack(side=tk.LEFT)
        
        clear_btn = tk.Button(header_frame, text="Clear", bg=THEME['bg_linenumbers'], 
                             fg=THEME['fg_linenumbers'], relief=tk.FLAT, 
                             command=self.clear_insights)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Insights text area with syntax highlighting
        self.insights_text = scrolledtext.ScrolledText(
            self.parent_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=THEME['bg_console'],
            fg=THEME['fg_console'],
            bd=0,
            padx=5,
            pady=5
        )
        self.insights_text.pack(fill=tk.BOTH, expand=True)
        self.insights_text.config(state=tk.DISABLED)
        
        # Configure tags for different types of content
        self.insights_text.tag_configure("timestamp", foreground="#569CD6")  # Blue timestamp
        self.insights_text.tag_configure("phase", foreground="#C586C0", font=("Consolas", 10, "bold"))  # Purple for compiler phases
        self.insights_text.tag_configure("llm_explanation", foreground=THEME['fg_console'])  # Normal text for explanations
        self.insights_text.tag_configure("code_snippet", foreground="#CE9178")  # Orange for code
        self.insights_text.tag_configure("header", foreground="#4EC9B0", font=("Consolas", 10, "bold"))  # Teal headers
        self.insights_text.tag_configure("separator", foreground="#6A9955")  # Green separators
    
    def clear_insights(self):
        """Clear the insights panel."""
        self.insights_text.config(state=tk.NORMAL)
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.config(state=tk.DISABLED)
        self.insights_count = 0
    
    def add_insight(self, phase_name, code_snippet=None, llm_explanation=None):
        """
        Add a new insight entry with timestamp, phase name, code snippet, and LLM explanation.
        
        Args:
            phase_name (str): Name of the compiler phase or step
            code_snippet (str, optional): Related code snippet
            llm_explanation (str, optional): Explanation from the LLM
        """
        self.insights_text.config(state=tk.NORMAL)
        
        # Add separator if not the first insight
        if self.insights_count > 0:
            self.insights_text.insert(tk.END, "\n" + "-" * 80 + "\n\n", "separator")
        
        # Add timestamp
        current_time = time.strftime("%H:%M:%S", time.localtime())
        self.insights_text.insert(tk.END, f"[{current_time}] ", "timestamp")
        
        # Add phase name
        self.insights_text.insert(tk.END, f"{phase_name}\n\n", "phase")
        
        # Add code snippet if provided
        if code_snippet:
            self.insights_text.insert(tk.END, "Code Context:\n", "header")
            self.insights_text.insert(tk.END, f"{code_snippet}\n\n", "code_snippet")
        
        # Add LLM explanation if provided
        if llm_explanation:
            self.insights_text.insert(tk.END, "Explanation:\n", "header")
            self.insights_text.insert(tk.END, f"{llm_explanation}\n", "llm_explanation")
        
        self.insights_text.see(tk.END)
        self.insights_text.config(state=tk.DISABLED)
        self.insights_count += 1
    
    def add_phase_start(self, phase_name, description=None):
        """
        Add a phase start entry to indicate the beginning of a compiler phase.
        
        Args:
            phase_name (str): Name of the compiler phase
            description (str, optional): Brief description of the phase
        """
        self.insights_text.config(state=tk.NORMAL)
        
        # Add separator if not the first insight
        if self.insights_count > 0:
            self.insights_text.insert(tk.END, "\n" + "-" * 80 + "\n\n", "separator")
        
        # Add timestamp
        current_time = time.strftime("%H:%M:%S", time.localtime())
        self.insights_text.insert(tk.END, f"[{current_time}] ", "timestamp")
        
        # Add phase start indicator
        self.insights_text.insert(tk.END, f"Starting phase: {phase_name}\n", "phase")
        
        # Add description if provided
        if description:
            self.insights_text.insert(tk.END, f"{description}\n", "llm_explanation")
        
        self.insights_text.see(tk.END)
        self.insights_text.config(state=tk.DISABLED)
        self.insights_count += 1
    
    def add_phase_end(self, phase_name, summary=None):
        """
        Add a phase end entry to indicate the completion of a compiler phase.
        
        Args:
            phase_name (str): Name of the completed compiler phase
            summary (str, optional): Summary of what was accomplished
        """
        self.insights_text.config(state=tk.NORMAL)
        
        # Add timestamp
        current_time = time.strftime("%H:%M:%S", time.localtime())
        self.insights_text.insert(tk.END, f"\n[{current_time}] ", "timestamp")
        
        # Add phase end indicator
        self.insights_text.insert(tk.END, f"Completed phase: {phase_name}\n", "phase")
        
        # Add summary if provided
        if summary:
            self.insights_text.insert(tk.END, f"{summary}\n", "llm_explanation")
        
        self.insights_text.see(tk.END)
        self.insights_text.config(state=tk.DISABLED)
    
    def print_to_insights(self, text, tag=None):
        """
        Print raw text to the insights panel with optional tag.
        Useful for custom formatting or direct output.
        
        Args:
            text (str): Text to display
            tag (str, optional): Tag name for styling
        """
        self.insights_text.config(state=tk.NORMAL)
        if tag:
            self.insights_text.insert(tk.END, text, tag)
        else:
            self.insights_text.insert(tk.END, text)
        self.insights_text.see(tk.END)
        self.insights_text.config(state=tk.DISABLED)