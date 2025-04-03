# Theme and style definitions


# Color theme (Light theme inspired by VS Code Light+)
THEME = {
    'bg_main': '#ffffff',           # Main background (white)
    'bg_editor': '#ffffff',         # Editor background (white)
    'bg_linenumbers': '#f3f3f3',    # Line numbers background (light gray)
    'bg_console': '#ffffff',        # Console background (white)
    'bg_tabs': '#e7e7e7',           # Slightly darker shade for tabs
    'fg_main': '#333333',           # Main text color (dark gray)
    'fg_linenumbers': '#888888',    # Line numbers text color (gray)
    'fg_console': '#444444',        # Console text color (darker gray)
    'error_color': '#d32f2f',       # Error text color (red)
    'cursor_color': '#000000',      # Cursor color (black)
    'select_bg': '#d0e7ff',         # Selection background (light blue)
    'highlight_line': '#f0f0f0'     # Current line highlight (very light gray)
}

# Professional syntax highlighting colors
SYNTAX_COLORS = {
    'command': '#569cd6',           # Blue
    'preposition': '#9cdcfe',       # Light blue
    'object': '#4ec9b0',            # Teal
    'datatype': '#c586c0',          # Purple
    'control': '#c586c0',           # Purple
    'comment': '#6a9955',           # Green
    'string': '#ce9178',            # Orange
    'number': '#b5cea8'             # Light green
}

# Reserved words and their categories for syntax highlighting
RESERVED_CATEGORIES = {
    # Core Command Keywords
    'book': 'command',
    'cancel': 'command',
    'list': 'command',
    'check': 'command',
    'pay': 'command',
    'display': 'command',
    'accept': 'command',
    
    # Prepositions and Conjunctions
    'for': 'preposition',
    'on': 'preposition',
    'event': 'preposition',

    # Objects and Topics
    'ticket': 'object',
    'tickets': 'object',
    'events': 'object',
    'availability': 'object',
    'price': 'object',
    
    # Data Types
    'string': 'datatype',
    'int': 'datatype',
    'date': 'datatype',
    
    # Control Flow
    'if': 'control',
    'else': 'control'
}