import tkinter as tk
from tkinter import ttk
from frontend.ide import APBLIDE

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    
    # Apply ttk style
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TPanedwindow", background='#1e1e1e')  # Use the theme's main background color
    
    # Create IDE instance
    ide = APBLIDE(root)
    
    # Main window config
    root.update()
    root.minsize(800, 600)
    
    # Center the window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1200
    window_height = 800
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()