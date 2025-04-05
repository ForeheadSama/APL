"""
Toolbar Module - Handles file operations and toolbar functionality
"""

from flask import jsonify, request
import os

class ToolbarManager:
    def __init__(self, ide):
        self.ide = ide
    
    def new_file(self):
        """Create a new file."""
        self.ide.editor.content = ""
        self.ide.editor.current_file = None
        return jsonify({'status': 'created'})
    
    def open_file(self):
        """Open a file."""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        try:
            content = file.read().decode('utf-8')
            self.ide.editor.content = content
            self.ide.editor.current_file = file.filename
            return jsonify({'status': 'opened'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def save_file(self):
        """Save current file."""
        if not self.ide.editor.current_file:
            return jsonify({'error': 'No file selected'}), 400
        
        try:
            with open(self.ide.editor.current_file, 'w') as f:
                f.write(self.ide.editor.content)
            return jsonify({'status': 'saved'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500