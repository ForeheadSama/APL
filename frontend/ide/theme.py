# Theme and style definitions


# Color theme (inspired by vs code dark++
THEME = {
    'bg_main': '#1e1e1e',           # Main background
    'bg_editor': '#1e1e1e',         # Editor background
    'bg_linenumbers': '#252526',    # Line numbers background
    'bg_console': '#1e1e1e',        # Console background
    'bg_tabs': '#2d2d2d',           # Slightly lighter color for tabs
    'fg_main': '#d4d4d4',           # Main text color
    'fg_linenumbers': '#858585',    # Line numbers text color
    'fg_console': '#cccccc',        # Console text color
    'error_color': '#f48771',       # Error text color
    'cursor_color': '#aeafad',      # Cursor color
    'select_bg': '#264f78',         # Selection background
    'highlight_line': '#4a4848'     # Current line highlight
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