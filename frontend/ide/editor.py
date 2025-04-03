# # Text editor components

import tkinter as tk
from tkinter import scrolledtext
import re
from .theme import THEME, SYNTAX_COLORS, RESERVED_CATEGORIES

class LineNumbersText(tk.Canvas):
    """Enhanced line number widget that syncs with the text editor."""
    
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.config(width=50)
        
        # Configure appearance
        self.configure(
            bg=THEME['bg_linenumbers'],
            highlightthickness=0,
            bd=0
        )
        
        # Bind text widget events to redraw line numbers
        text_widget.bind('<KeyRelease>', self.redraw)
        text_widget.bind('<ButtonRelease-1>', self.redraw)
        text_widget.bind('<Configure>', self.redraw)
        
        # Synchronize scrolling
        text_widget.bind('<MouseWheel>', self.on_scroll)
        text_widget.bind('<Button-4>', self.on_scroll)
        text_widget.bind('<Button-5>', self.on_scroll)
        
    def redraw(self, event=None):
        """Redraw line numbers when text widget changes."""
        self.delete("all")
        
        # Get visible range of lines
        first_line = int(self.text_widget.index("@0,0").split('.')[0])
        last_line = int(self.text_widget.index(f"@0,{self.text_widget.winfo_height()}").split('.')[0])
        
        # Get font metrics for proper alignment
        font = self.text_widget.cget("font")
        # Use a safer approach to get line height
        line_height = self.text_widget.tk.call("font", "metrics", font, "-linespace")
        
        # Draw line numbers
        for i in range(first_line, last_line + 1):
            # Get y-coordinate of each line
            dline = self.text_widget.dlineinfo(f"{i}.0")
            if dline:
                y = dline[1]
                self.create_text(
                    40, y, 
                    anchor="ne", 
                    text=str(i), 
                    fill=THEME['fg_linenumbers'],
                    font=self.text_widget.cget("font")
                )
    
    def on_scroll(self, event=None):
        """Synchronize scrolling with text widget."""
        self.redraw()
        return "break"  # Let the event continue to the text widget

class EditorComponent:
    """Text editor component with syntax highlighting and line numbers."""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_editor()
        
    def setup_editor(self):
        """Set up the text editor with line numbers."""
        # Create editor container
        editor_container = tk.Frame(self.parent_frame, bg=THEME['bg_main'])
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Text editor
        self.text_editor = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=("Consolas", 12),
            bg=THEME['bg_editor'],
            fg=THEME['fg_main'],
            insertbackground=THEME['cursor_color'],
            selectbackground=THEME['select_bg'],
            undo=True,
            bd=0,
            padx=5,
            pady=5
        )
        
        # Configure tags for syntax highlighting
        for category, color in SYNTAX_COLORS.items():
            self.text_editor.tag_configure(category, foreground=color)
        
        # Create line numbers
        self.line_numbers = LineNumbersText(
            editor_container,
            self.text_editor,
            width=50
        )
        
        # Pack widgets
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.text_editor.bind("<KeyRelease>", self.on_text_change)
        self.text_editor.bind("<FocusIn>", self.on_text_change)
        
        # Current line highlighting
        self.text_editor.bind("<KeyRelease>", self.highlight_current_line)
        self.text_editor.bind("<ButtonRelease-1>", self.highlight_current_line)
        self.text_editor.tag_configure("current_line", background=THEME['highlight_line'])

    def on_text_change(self, event=None):
        """Handle text changes and update line numbers and syntax highlighting."""
        self.highlight_syntax()
        self.line_numbers.redraw()
        self.highlight_current_line()
    
    def highlight_current_line(self, event=None):
        """Highlight the current line."""
        self.text_editor.tag_remove("current_line", "1.0", tk.END)
        current_line = self.text_editor.index(tk.INSERT).split('.')[0]
        self.text_editor.tag_add("current_line", f"{current_line}.0", f"{current_line}.end+1c")
    
    def highlight_syntax(self):
        """Apply professional syntax highlighting to the text editor."""
        # Remove all existing tags
        for tag in SYNTAX_COLORS.keys():
            self.text_editor.tag_remove(tag, "1.0", tk.END)
        
        # Get the entire content of the text editor (excluding the trailing newline)
        text_content = self.text_editor.get("1.0", tk.END).rstrip("\n")
        
        # Highlight reserved words
        for word, category in RESERVED_CATEGORIES.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.finditer(pattern, text_content)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_editor.tag_add(category, start, end)
        
        # Highlight comments (lines starting with $$)
        for line_num, line in enumerate(text_content.splitlines(), start=1):
            if line.strip().startswith("$$"):
                self.text_editor.tag_add('comment', f"{line_num}.0", f"{line_num}.end")
        
        # Highlight strings (text inside quotes)
        string_pattern = r'"[^"]*"'
        matches = re.finditer(string_pattern, text_content)
        for match in matches:
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add('string', start, end)
        
        # Highlight numbers
        number_pattern = r'\b\d+\b'
        matches = re.finditer(number_pattern, text_content)
        for match in matches:
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add('number', start, end)
    
    def find_text(self, find_query):
        """Find the next occurrence of the given text."""
        if not find_query:
            return False
        
        # Remove previous highlights
        self.text_editor.tag_remove("search", "1.0", tk.END)
        
        # Start search from current position
        start_pos = self.text_editor.index(tk.INSERT)
        pos = self.text_editor.search(find_query, start_pos, stopindex=tk.END, nocase=1)
        
        if not pos:
            # If not found from current position, start from beginning
            pos = self.text_editor.search(find_query, "1.0", stopindex=tk.END, nocase=1)
        
        if pos:
            # Highlight the found text
            end_pos = f"{pos}+{len(find_query)}c"
            self.text_editor.tag_add("search", pos, end_pos)
            self.text_editor.tag_config("search", background="#565656", foreground="#ffffff")
            
            # Move cursor and see the found text
            self.text_editor.mark_set(tk.INSERT, end_pos)
            self.text_editor.see(pos)
            return True
        return False