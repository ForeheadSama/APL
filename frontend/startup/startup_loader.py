import os
import sys
import time
import socket
import pyodbc
import tkinter as tk
from tkinter import ttk
import threading
import importlib.util

class APBLStartupLoader:
    def __init__(self):
        # Import theme colors
        from frontend.ide.theme import THEME

        self.root = tk.Tk()
        self.root.title("APBL Compiler")
        self.root.geometry("500x350")
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
            'backend/main_compiler/lexer_module/lexer_output.txt',
            'backend/main_compiler/semantic_module/semantic_errors.txt',
            'backend/main_compiler/intermediate_code_module/intermediate_code.txt',
            'backend/main_compiler/code_generator_module/code_generator_errors.txt'
        ]

    def create_required_files(self):
        for file_path in self.required_files:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if not os.path.exists(file_path):
                open(file_path, 'w').close()

    def check_network_connectivity(self):
        try:
            # Multiple network checks for reliability
            socket.setdefaulttimeout(5)
            
            # Check multiple reliable hosts
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
        try:
            # Import the alternative database connection function
            spec = importlib.util.spec_from_file_location("db_connection_alt", "backend/database/connect.py")            
            db_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(db_module)

            # Use the get_db_connection function from the imported module
            conn = db_module.get_db_connection()
            conn.close()
            return True
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            return False

    def startup_process(self):
        try:
            # Step 1: Network Connectivity
            self.update_status("Checking network connectivity...", 0)
            time.sleep(3)  # Longer wait time to see status
            
            if not self.check_network_connectivity():
                self.update_status("Error connecting to network", 0)
                self.show_error_details("Unable to establish internet connection. Please check your network settings.")
                raise Exception("No internet connection.")
            
            self.progress['value'] = 15

            # Step 2: Azure Database Connection
            self.update_status("Establishing database connection...", 15)
            time.sleep(3)  # Longer wait time to see status
            
            if not self.check_azure_connection():
                self.update_status("Error connecting to database", 15)
                self.show_error_details("Failed to connect to Azure database.")
                raise Exception("Azure database connection failed")
            
            self.progress['value'] = 40

            # Step 3: Create Required Files
            self.update_status("Preparing necessary files...", 40)
            time.sleep(3)  # Longer wait time to see status
            self.create_required_files()
            self.progress['value'] = 70

            # Step 4: Final Preparation
            self.update_status("Initializing compiler environment...", 70)
            time.sleep(2)  # Simulate final preparations
            self.progress['value'] = 100

            # Launch IDE
            self.update_status("Launching APBL Compiler IDE...", 100)
            time.sleep(0.5)
            
            # Store a reference to prevent garbage collection
            self.root_copy = self.root
            self.root.withdraw()  # Hide instead of destroy immediately

            try:
                import importlib.util

                spec = importlib.util.spec_from_file_location("main_ide", "frontend/ide/main_ide.py")
                main_ide = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_ide)

                APBLIDE = main_ide.APBLIDE
                                
                # Create main window
                ide_root = tk.Tk()
                ide = APBLIDE(ide_root)
                
                # Window configuration
                ide_root.update()
                ide_root.minsize(800, 600)
                
                # Center the window on screen
                screen_width = ide_root.winfo_screenwidth()
                screen_height = ide_root.winfo_screenheight()
                window_width = 1200
                window_height = 800
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                ide_root.geometry(f"{window_width}x{window_height}+{x}+{y}")
                
                # Now destroy the loader window
                self.root_copy.destroy()
                
                # Start the IDE's main loop
                ide_root.mainloop()

            except Exception as e:
                print(f"Error launching IDE: {e}")

                # Show error and restore visibility of loader window if IDE fails to launch
                self.root_copy.deiconify()
                self.show_error_details(f"Failed to launch IDE. {e}")
                raise

        except Exception as e:
            self.handle_startup_error(str(e))

    def show_error_details(self, error_message):
        self.error_details_label.config(text=error_message)

    def handle_startup_error(self, error_message):
        try:
            self.restart_label.config(text="Restart attempt in:")
            
            countdown = 5
            while countdown > 0:
                # Check if window still exists before updating
                try:
                    self.restart_label.config(text=f"Closing in {countdown}. Please restart.")
                    self.root.update()  # Process any pending events
                    time.sleep(1)
                    countdown -= 1
                except tk.TclError:
                    # Window was destroyed, exit the loop
                    break
            
            # Only try to destroy if window still exists
            try:
                self.root.destroy()
            except tk.TclError:
                pass  # Window already destroyed
        except Exception as e:
            print(f"Error during shutdown: {e}")

    def update_status(self, message, progress_value):
        self.status_label.config(text=message)
        self.progress['value'] = progress_value
        self.root.update()

    def run(self):
        # Start startup process in a separate thread
        startup_thread = threading.Thread(target=self.startup_process)
        startup_thread.start()
        self.root.mainloop()

def main():
    loader = APBLStartupLoader()
    loader.run()

if __name__ == "__main__":
    main()