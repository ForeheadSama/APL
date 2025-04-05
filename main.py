
"""
Main entry point for the APBL application :P
"""

import os
import sys
from app import create_app

if __name__ == "__main__":
    # Add project root to Python path to ensure imports work
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Create and run the application
    apbl = create_app()
    apbl.run(port=5000)