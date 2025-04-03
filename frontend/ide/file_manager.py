import os
import tkinter as tk
from tkinter import filedialog, messagebox

# For all filing components

class FileManager:
    def __init__(self, root, text_editor):
        self.root = root
        self.text_editor = text_editor
        self.current_file = None
        
        # Update the window title
        self.update_title()
    
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
                # Trigger syntax highlighting if editor has this method
                if hasattr(self.text_editor, 'on_text_change'):
                    self.text_editor.on_text_change()
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