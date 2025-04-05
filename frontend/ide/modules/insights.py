"""
Execution Insights Module - Provides compilation insights
"""

from flask import jsonify

class InsightsManager:
    def __init__(self):
        self.phases = []
        self.insights = []
    
    def add_phase(self, name, description):
        """Add a new compilation phase."""
        self.phases.append({
            'name': name,
            'description': description,
            'status': 'running',
            'is_error': False
        })
        return jsonify({'status': 'added'})
    
    def add_phase_end(self, name, result, is_error=False):
        """Mark a phase as completed."""
        for phase in self.phases:
            if phase['name'] == name:
                phase['result'] = result
                phase['status'] = 'completed'
                phase['is_error'] = is_error
                break
        return jsonify({'status': 'updated'})
    
    def add_insight(self, title, code, explanation):
        """Add a detailed insight."""
        self.insights.append({
            'title': title,
            'code': code,
            'explanation': explanation
        })
        return jsonify({'status': 'added'})
    
    def get_data(self):
        """Get all insights data."""
        return jsonify({
            'phases': self.phases,
            'insights': self.insights
        })
    
    def clear(self):
        """Clear all insights."""
        self.phases = []
        self.insights = []
        return jsonify({'status': 'cleared'})