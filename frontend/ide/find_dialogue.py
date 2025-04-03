import tkinter as tk

# Find functionality 

class FindDialog:
    def __init__(self, parent, text_editor):
        self.parent = parent
        self.text_editor = text_editor
        self.dialog = None
        
    def show(self):
        """Show the find dialog."""
        # Create dialog if it doesn't exist or has been destroyed
        if self.dialog is None or not self.dialog.winfo_exists():
            self.create_dialog()
        else:
            # If dialog exists, just bring it to front
            self.dialog.lift()
            self.dialog.focus_set()
            
    def create_dialog(self):
        """Create the find dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Find")
        self.dialog.geometry("300x80")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        
        # Find entry
        find_frame = tk.Frame(self.dialog)
        find_frame.pack(fill=tk.X, padx=10, pady=10)
        
        find_label = tk.Label(find_frame, text="Find:")
        find_label.pack(side=tk.LEFT)
        
        self.find_entry = tk.Entry(find_frame, width=30)
        self.find_entry.pack(side=tk.LEFT, padx=5)
        self.find_entry.focus_set()
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        find_next_btn = tk.Button(
            button_frame, 
            text="Find Next", 
            command=self.find_next
        )
        find_next_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to find_next
        self.find_entry.bind("<Return>", lambda event: self.find_next())
        
    def find_next(self):
        """Find the next occurrence of the text in the entry field."""
        query = self.find_entry.get()
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
            tk.messagebox.showinfo("Find", f"Cannot find '{query}'")