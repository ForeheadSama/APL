"""
Console Module - Handles output console functionality
"""

from flask import jsonify
from collections import deque

class ConsoleManager:
    def __init__(self, max_lines=1000):
        self.output = deque(maxlen=max_lines)
    
    def add_output(self, text, message_type="normal"):
        """Add output to console."""
        self.output.append({
            'text': text,
            'type': message_type
        })
    
    def get_output(self):
        """Get console output."""
        return jsonify({'output': list(self.output)})
    
    def clear(self):
        """Clear console output."""
        self.output.clear()
        return jsonify({'status': 'cleared'})