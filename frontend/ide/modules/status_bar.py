"""
Status Bar component for the APBL IDE
"""
from flask import request, jsonify

class StatusBarManager:
    def __init__(self):
        """Initialize the status bar manager"""
        self.status = {
            'message': 'Ready',
            'position': '0:0',
            'file_type': None,
            'encoding': 'UTF-8',
            'line_endings': 'LF'
        }
    
    def update(self):
        """API endpoint to update status bar"""
        for key, value in request.json.items():
            if key in self.status:
                self.status[key] = value
        
        return jsonify({
            'status': 'success',
            'data': self.status
        })
    
    def get_status(self):
        """API endpoint to get status bar info"""
        return jsonify({
            'status': 'success',
            'data': self.status
        })
    
    def set_message(self, message):
        """Programmatically set status message"""
        self.status['message'] = message
    
    def set_position(self, line, column):
        """Set cursor position"""
        self.status['position'] = f"{line}:{column}"