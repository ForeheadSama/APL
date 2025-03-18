# custom_error_handler.py
import os
import logging

class CustomErrorHandler:
    """
    A custom error handler for the PLY parser that checks for various syntax errors.
    """
    def __init__(self, error_log_file="errors.log"):
        self.errors = []
        self.warnings = []  # Added warnings list for non-critical issues
        self.symbol_table = {}
        self.current_token = None
        self.token_stream = None
        self.expected_brackets = []  # Stack to track brackets
        self.error_file = "parser_module/parser_errors.txt"
        self.warning_file = "parser_module/parser_warnings.txt"
        self.error_log_file = error_log_file
        
        # Set up logging to file
        logging.basicConfig(filename=self.error_log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s - %(message)s')

        # Add a stream handler to also print errors to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter('%(asctime)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # Add the console handler to the logger
        logging.getLogger().addHandler(console_handler)
        
    def set_token_stream(self, token_stream):
        """Set the token stream for error tracking."""
        self.token_stream = token_stream
        
    def set_symbol_table(self, symbol_table):
        """Set the symbol table for type checking."""
        self.symbol_table = symbol_table
        
    def handle_error(self, p):
        """Main error handler called by PLY when a syntax error is encountered."""
        if p is None:
            error_msg = "Syntax error at EOF - unexpected end of input. The code might be missing a closing bracket or statement terminator."
        else:
            try:
                error_msg = self._generate_error_msg(p)
            except AttributeError:
                error_msg = f"Syntax error at unknown location: Invalid token structure."
                
        self.errors.append(error_msg)
        logging.error(error_msg)
        
        return p
        
    def _generate_error_msg(self, p):
        """
        Generate a generalized error message based on the token type and value.
        """
        error_msg = f"Syntax error at line {p.lineno}: Unexpected token '{p.value}' of type '{p.type}'"
        
        if p.type == 'IDENTIFIER':
            if p.value not in self.symbol_table:
                error_msg = f"Error at line {p.lineno}: Undefined variable '{p.value}' used."
        
        elif p.type == 'NUMBER':
            try:
                float(p.value)
            except ValueError:
                error_msg = f"Error at line {p.lineno}: Invalid number format '{p.value}'."
        
        elif p.type == 'STRING_LITERAL':
            if not (p.value.startswith('"') and p.value.endswith('"')):
                error_msg = f"Error at line {p.lineno}: String literal '{p.value}' is not properly enclosed in quotes."
        
        elif p.type in ['RBRACKET', 'RPAREN']:
            if not self.expected_brackets:
                error_msg = f"Error at line {p.lineno}: Unexpected closing '{p.value}' without matching opening bracket."
            else:
                expected, line = self.expected_brackets.pop()
                if p.type != expected:
                    error_msg = f"Error at line {p.lineno}: Mismatched bracket '{p.value}'. Expected '{expected}' at line {line}."
        
        elif p.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
            prev_token = self._peek_prev_token(p)
            next_token = self._peek_next_token(p)
            if not prev_token or not next_token or prev_token.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
                error_msg = f"Error at line {p.lineno}: Misplaced operator '{p.value}'."
        
        # Check for missing full stop (.) at the end of each statement (declaration/assignment).
        elif p.type in ['STRING_LITERAL', 'NUMBER', 'IDENTIFIER']:
            prev_token = self._peek_prev_token(p)
            # Check if the previous token is an assignment or declaration and if it is missing a full stop.
            if prev_token and prev_token.type not in ['RBRACKET', 'RPAREN', 'DOT'] and not self._ends_with_full_stop():
                error_msg = f"Error at line {p.lineno}: Missing statement terminator (.) after '{p.value}'."

        return error_msg
    
    def _ends_with_full_stop(self):
        """Check if the last statement ends with a full stop (.)"""
        if not self.token_stream or not hasattr(self.token_stream, 'tokens'):
            return False  # No tokens to check
        
        last_token = self.token_stream.tokens[-1]  # Get last token
        return last_token.type == 'DOT'  # Ensure it's a period (.)

    
    def _peek_next_token(self, p):
        """Peek at the next token without consuming it, ensuring bounds are checked."""
        #Use hasattr() to check if index exists.
        if not self.token_stream or not hasattr(self.token_stream, 'tokens') or not hasattr(self.token_stream, 'index'):
            return None  # Prevents AttributeError
    
        next_index = self.token_stream.index + 1
        if next_index >= len(self.token_stream.tokens):
            return None  # Prevents IndexError
        
        return self.token_stream.tokens[next_index]
    
    def _peek_prev_token(self, p):
        """Peek at the previous token."""
        #Use hasattr() to check if index exists.
        if not self.token_stream or not hasattr(self.token_stream, 'tokens') or not hasattr(self.token_stream, 'index'):
            return None  # Prevents AttributeError
    
        prev_index = self.token_stream.index - 1
        if prev_index < 0:
            return None  # Prevents IndexError
        
        return self.token_stream.tokens[prev_index] 
    
    def write_errors_to_file(self):
        """Write all errors and warnings to their respective files."""
        os.makedirs(os.path.dirname(self.error_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
        
        with open(self.error_file, "w") as f:
            if self.errors:
                for error in self.errors:
                    f.write(error + "\n")
            else:
                f.write("No errors detected during parsing.\n")
        
        with open(self.warning_file, "w") as f:
            if self.warnings:
                for warning in self.warnings:
                    f.write(warning + "\n")
            else:
                f.write("No warnings during parsing.\n")
        
        return len(self.errors) > 0
    
    def clear_errors(self):
        """Clear all errors, warnings and reset the files."""
        self.errors = []
        self.warnings = []
        self.expected_brackets = []
        
        os.makedirs(os.path.dirname(self.error_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
        
        with open(self.error_file, "w") as f:
            f.write("")
        
        with open(self.warning_file, "w") as f:
            f.write("")