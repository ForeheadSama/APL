import os
import sys
import time
import socket
import pyodbc
import tkinter as tk
from tkinter import ttk
import threading
import queue
import importlib.util

class APBLStartupLoader:
    def __init__(self):
        # Import theme colors
        from frontend.ide.theme import THEME

        self.root = tk.Tk()
        self.root.overrideredirect(True)  # This removes the title bar
        self.root.title("")

        # Make window draggable
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_move)
        
        # Set dimensions and center
        window_width = 500
        window_height = 350
        self.center_window(self.root, window_width, window_height)

        self.root.configure(bg=THEME['bg_main'])

        # Compiler branding
        self.title_label = tk.Label(self.root, text="APBL", font=("Courier", 24, "bold"), 
                                    bg=THEME['bg_main'], fg=THEME['fg_main'])
        self.title_label.pack(pady=(50, 10))

        self.slogan_label = tk.Label(self.root, text="Booking made easy", 
                                     font=("Arial", 12), 
                                     bg=THEME['bg_main'], 
                                     fg=THEME['fg_linenumbers'])
        self.slogan_label.pack(pady=(0, 20))

        # Status message with longer display time
        self.status_label = tk.Label(self.root, text="", 
                                     font=("Arial", 10), 
                                     bg=THEME['bg_main'], 
                                     fg=THEME['fg_main'])
        self.status_label.pack(pady=(0, 10))

        # Detailed error message area
        self.error_details_label = tk.Label(self.root, text="", 
                                            font=("Arial", 10), 
                                            bg=THEME['bg_main'], 
                                            fg=THEME['error_color'], 
                                            wraplength=400)
        self.error_details_label.pack(pady=(0, 10))

        # Restart countdown label
        self.restart_label = tk.Label(self.root, text="", 
                                      font=("Arial", 10), 
                                      bg=THEME['bg_main'], 
                                      fg=THEME['error_color'])
        self.restart_label.pack(pady=(0, 10))

        # Progress bar with VS Code theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Custom.Horizontal.TProgressbar", 
                        background=THEME['select_bg'], 
                        troughcolor=THEME['bg_tabs'])
        
        self.progress = ttk.Progressbar(self.root, 
                                        orient="horizontal", 
                                        length=400, 
                                        mode="determinate", 
                                        style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=(0, 20))

        self.version_label = tk.Label(self.root, text="Version 1.0", 
                                      font=("Arial", 8), 
                                      bg=THEME['bg_main'], 
                                      fg=THEME['fg_linenumbers'])
        self.version_label.pack(side=tk.BOTTOM, pady=10)

        # Required file paths
        self.required_files = [
            'backend/main_compiler/parser_module/parser_errors.txt',
            'backend/main_compiler/parser_module/parser_output.json',
            'backend/main_compiler/parser_module/parser_warnings.txt',
            'backend/main_compiler/parser_module/visual_ast.png',
            'backend/main_compiler/parser_module/symbol_table.json',
            'backend/main_compiler/lexer_module/lexer_output.txt',
            'backend/main_compiler/semantic_module/semantic_errors.txt',
            'backend/main_compiler/intermediate_code_module/intermediate_code.txt',
            'backend/main_compiler/code_generator_module/code_generator_errors.txt'
        ]

        # Threading components
        self.message_queue = queue.Queue()

        # Add custom close button
        from frontend.ide.theme import THEME

        self.close_btn = tk.Button(
            self.root, 
            text="×", 
            font=("Arial", 14), 
            command=self.root.destroy,
            bg=THEME['bg_main'],
            fg=THEME['fg_main'],
            activebackground=THEME['select_bg'],
            activeforeground=THEME['fg_main'],
            borderwidth=0,
            highlightthickness=0
        )
        self.close_btn.place(x=window_width-30, y=10, width=20, height=20)
        
        # Make it look better on hover
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(fg=THEME['error_color']))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(fg=THEME['fg_main']))

        if sys.platform == "win32":
            try:
                import ctypes

                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    33,  # DWMWA_WINDOW_CORNER_PREFERENCE
                    ctypes.byref(ctypes.c_int(2)),  # DWM_WINDOW_CORNER_ROUND
                    ctypes.sizeof(ctypes.c_int)
                )
            except:
                pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def center_window(self, window, width, height):
        """Center the window on screen without title bar"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.update_idletasks()  # Ensure geometry is applied

    def create_required_files(self):
        """Create all required files if they don't exist"""
        for file_path in self.required_files:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                open(file_path, 'w').close()

    def check_network_connectivity(self):
        """Check if we have internet connectivity"""
        try:
            socket.setdefaulttimeout(5)
            hosts_to_check = [
                ("8.8.8.8", 53),      # Google DNS
                ("1.1.1.1", 53),      # Cloudflare DNS
                ("www.google.com", 80)
            ]
            
            for host, port in hosts_to_check:
                try:
                    socket.create_connection((host, port))
                    return True
                except (socket.error, socket.timeout):
                    continue
            
            return False
        except Exception as e:
            print(f"Network check error: {e}")
            return False

    def check_azure_connection(self):
        """Check connection to Azure database"""
        try:
            spec = importlib.util.spec_from_file_location("db_connection", "backend/database/connect.py")            
            db_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(db_module)
            conn = db_module.get_db_connection()
            conn.close()
            return True
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return False

    def startup_process(self):
        """Background thread for startup checks"""
        try:
            # Step 1: Network Connectivity
            self.queue_message(("status", "Checking network connectivity...", 10))
            if not self.check_network_connectivity():
                self.queue_message(("error", "Unable to establish internet connection"))
                return

            # Step 2: Azure Database Connection
            self.queue_message(("status", "Connecting to database...", 30))
            if not self.check_azure_connection():
                self.queue_message(("error", "Failed to connect to Azure database"))
                return

            # Step 3: Create Required Files
            self.queue_message(("status", "Preparing files...", 60))
            self.create_required_files()

            # Step 4: Final Preparation
            self.queue_message(("status", "Initializing environment...", 80))
            time.sleep(2)  # Simulate work

            # Launch IDE
            self.queue_message(("status", "Launching IDE...", 100))
            self.launch_ide()

        except Exception as e:
            self.queue_message(("error", str(e)))

    def launch_ide(self):
        """Launch the main IDE window - fixed version"""
        try:
            # Store reference to loader window
            loader_window = self.root
            
            # Add project root to Python path
            project_root = os.path.dirname(os.path.abspath(__file__))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # Import IDE class
            from frontend.ide.main_ide import APBLIDE
            
            # Create IDE in main thread
            def create_ide():
                ide_root = tk.Tk()
                ide = APBLIDE(ide_root)
                
                # Window configuration
                screen_width = ide_root.winfo_screenwidth()
                screen_height = ide_root.winfo_screenheight()
                ide_root.geometry(f"1200x1000+{(screen_width-1200)//2}+{(screen_height-800)//2}")
                ide_root.minsize(800, 600)
                
                # Hide loader only after IDE is ready
                loader_window.withdraw()
                
                # Proper cleanup when IDE closes
                def on_ide_close():
                    loader_window.destroy()
                    ide_root.destroy()
                    
                ide_root.protocol("WM_DELETE_WINDOW", on_ide_close)
                ide_root.mainloop()

            # Schedule IDE creation in main thread
            self.root.after(0, create_ide)

        except Exception as e:
            print(f"IDE launch error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.queue_message(("error", f"IDE Launch Failed: {str(e)}"))
            self.root.deiconify()

    def queue_message(self, message):
        """Thread-safe message passing to main thread"""
        self.message_queue.put(message)
        self.root.event_generate("<<MessageQueued>>", when="tail")

    def process_messages(self):
        """Handle messages from background thread"""
        try:
            while True:
                msg_type, *content = self.message_queue.get_nowait()
                
                if msg_type == "status":
                    message, progress = content
                    self.status_label.config(text=message)
                    self.progress['value'] = progress
                    self.root.update()
                
                elif msg_type == "error":
                    error_msg = content[0]
                    self.show_error_details(error_msg)
                    self.handle_startup_error(error_msg)
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_messages)

    def show_error_details(self, error_message):
        """Display error message in UI"""
        self.error_details_label.config(text=error_message)
        self.root.update()

    def handle_startup_error(self, error_message):
        """Handle startup errors with countdown"""
        try:
            self.restart_label.config(text="Restarting in:")
            
            for countdown in range(5, 0, -1):

                try:
                    self.restart_label.config(text=f"Restarting in {countdown}...")
                    self.root.update()
                    time.sleep(1)
                except tk.TclError:
                    break

        except Exception as e:
            print(f"Error during shutdown: {e}")
            self.root.destroy()

    def run(self):
        """Start the application with threading support"""
        # Setup message handler
        self.root.bind("<<MessageQueued>>", lambda e: self.process_messages())
        
        # Start background thread
        threading.Thread(
            target=self.startup_process,
            daemon=True
        ).start()
        
        self.root.mainloop()

def main():
    loader = APBLStartupLoader()
    loader.run()

if __name__ == "__main__":
    main()