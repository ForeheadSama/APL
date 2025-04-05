"""
Editor Module - Handles code editing functionality
"""

from flask import jsonify, request
import os


class EditorManager:
    def __init__(self):
        self.content = ""
        self.current_file = None
    
    def get_content(self):
        """Get current editor content."""
        return jsonify({
            'content': self.content,
            'file': self.current_file
        })
    
    def update_content(self):
        """Update editor content."""
        data = request.json
        self.content = data.get('content', '')
        return jsonify({'status': 'updated'})
    
    def load_file(self, filepath):
        """Load content from file."""
        try:
            with open(filepath, 'r') as f:
                self.content = f.read()
            self.current_file = filepath
            return True
        except Exception as e:
            return False
    
    def save_to_file(self, filepath):
        """Save content to file."""
        try:
            with open(filepath, 'w') as f:
                f.write(self.content)
            self.current_file = filepath
            return True
        except Exception as e:
            return False