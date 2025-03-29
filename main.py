import tkinter as tk
import os
import sys

from frontend.startup.startup_loader import APBLStartupLoader

# Main application
if __name__ == "__main__":
    # Initialize the startup loader
    loader = APBLStartupLoader()
    loader.run()