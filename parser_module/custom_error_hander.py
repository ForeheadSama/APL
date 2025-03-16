# custom_error_handler.py
import os

class CustomErrorHandler:
    """
    A custom error handler for the PLY parser that checks for various syntax errors.
    """
    def __init__(self):
        self.errors = []
        self.warnings = []  # Added warnings list for non-critical issues
        self.symbol_table = {}
        self.current_token = None
        self.token_stream = None
        self.expected_brackets = []  # Stack to track brackets
        self.error_file = "parser_module/parser_errors.txt"
        self.warning_file = "parser_module/parser_warnings.txt"
        
    def set_token_stream(self, token_stream):
        """Set the token stream for error tracking."""
        self.token_stream = token_stream
        
    def set_symbol_table(self, symbol_table):
        """Set the symbol table for type checking."""
        self.symbol_table = symbol_table
        
    def handle_error(self, p):
        """Main error handler called by PLY when a syntax error is encountered."""
        if p:
             # Try to determine the expected token type
            self._check_for_specific_errors(p)

            error_msg = f"Syntax error at line {p.lineno} near token: '{p.value}'"
            self.errors.append(error_msg)

            
            # Attempt to recover by skipping to the next EOL
            return p
        else:
            error_msg = "Syntax error at EOF - unexpected end of input"
            self.errors.append(error_msg)
            return None
            
    def _check_for_specific_errors(self, p):
        """Check for specific types of errors based on context."""
        # Check for missing EOL (dot)
        self._check_missing_eol(p)
        
        # Check for unmatched brackets
        self._check_unmatched_brackets(p)
        
        # Check for undefined variables
        self._check_undefined_variables(p)
        
        # Check for string literals without quotes
        self._check_string_quotes(p)
    
    def handle_implicit_declaration(self, var_name, lineno):
        """
        Handle an implicit variable declaration from an accept command.
        This adds a warning instead of an error since we're auto-declaring it.
        """
        warning_msg = f"Warning at line {lineno}: Variable '{var_name}' was implicitly declared as 'string' by accept command."
        self.warnings.append(warning_msg)
        
    def _check_missing_eol(self, p):
        """Check if an EOL token (dot) is missing at the end of a statement."""
        # Look ahead to see if we're at what should be the end of a statement
        if p.type in ['IDENTIFIER', 'NUMBER', 'STRING_LITERAL', 'DATE_VAL', 'RBRACKET']:
            # Check if the next token is not DOT when it should be
            next_token = self._peek_next_token(p)
            if next_token and next_token.type != 'DOT' and next_token.type != 'EOL':
                if next_token.type not in ['RPAREN', 'RBRACKET', 'ELSE']:
                    self.errors.append(f"Error at line {p.lineno}: Missing end of statement marker '.' after '{p.value}'")
    
    def _check_unmatched_brackets(self, p):
        """Check for unmatched brackets and parentheses."""
        if p.type == 'LPAREN':
            self.expected_brackets.append(('RPAREN', p.lineno))
        elif p.type == 'LBRACKET':
            self.expected_brackets.append(('RBRACKET', p.lineno))
        elif p.type == 'RPAREN' or p.type == 'RBRACKET':
            if not self.expected_brackets:
                self.errors.append(f"Error at line {p.lineno}: Unexpected '{p.value}' without matching opening bracket")
            else:
                expected, line = self.expected_brackets.pop()
                if p.type != expected:
                    self.errors.append(f"Error at line {p.lineno}: Mismatched brackets. Expected '{expected}' to match opening bracket at line {line}")
    
    def _check_undefined_variables(self, p):
        """Check if variables are used before being declared."""
        if p.type == 'IDENTIFIER':
            # Skip if this is a declaration
            prev_token = self._peek_prev_token(p)
            if prev_token and prev_token.type in ['STRING_TYPE', 'INT_TYPE', 'DATE_TYPE']:
                return
            
            # Skip if this is an accept command (which implicitly declares variables)
            if prev_token and prev_token.type == 'ACCEPT':
                return
                
            # Check if the variable exists in the symbol table
            if p.value not in self.symbol_table:
                self.errors.append(f"Error at line {p.lineno}: Variable '{p.value}' used before declaration")
    
    def _check_string_quotes(self, p):
        """Check for potential string literals without proper quotes."""
        if p.type == 'IDENTIFIER':
            # Check if there are spaces in the identifier which might indicate a missing quoted string
            if ' ' in p.value:
                self.errors.append(f"Error at line {p.lineno}: Possible unquoted string: '{p.value}'. String literals must be enclosed in double quotes.")
    
    def check_type_mismatch(self, var_name, expected_type, lineno):
        """Check for type mismatches when variables are used."""
        if var_name not in self.symbol_table:
            # Special case for accept commands - variable could be implicitly declared
            prev_tokens = self._get_recent_tokens(2)
            if prev_tokens and len(prev_tokens) > 1 and prev_tokens[0].type == 'ACCEPT':
                # This will be handled by implicit declaration
                return False
                
            self.errors.append(f"Error at line {lineno}: Variable '{var_name}' not declared")
            return True
            
        actual_type = self.symbol_table[var_name]
        if actual_type != expected_type:
            self.errors.append(f"Error at line {lineno}: Type mismatch for '{var_name}'. Expected {expected_type}, got {actual_type}")
            return True
            
        return False
        
    def check_final_bracket_state(self):
        """Check if all brackets have been closed at the end of parsing."""
        for expected, line in self.expected_brackets:
            bracket_type = "parenthesis" if expected == 'RPAREN' else "bracket"
            self.errors.append(f"Error: Unclosed {bracket_type} starting at line {line}")
        
        # Reset the bracket stack
        self.expected_brackets = []
    
    def _peek_next_token(self, p):
        """Peek at the next token without consuming it."""
        if not self.token_stream or self.token_stream.index >= len(self.token_stream.tokens):
            return None
            
        return self.token_stream.tokens[self.token_stream.index]
    
    def _peek_prev_token(self, p):
        """Peek at the previous token."""
        if not self.token_stream or self.token_stream.index <= 1:
            return None
            
        return self.token_stream.tokens[self.token_stream.index - 2]  # -2 because index is already incremented
    
    def _get_recent_tokens(self, count):
        """Get the most recent tokens."""
        if not self.token_stream or self.token_stream.index <= count:
            return []
            
        start_idx = max(0, self.token_stream.index - count - 1)
        end_idx = self.token_stream.index - 1
        return self.token_stream.tokens[start_idx:end_idx]
    
    def check_if_statement_completeness(self, if_token, condition, if_body, else_body=None):
        """Check if an if statement is complete with all required components."""
        if not condition:
            self.errors.append(f"Error at line {if_token.lineno}: Missing or invalid condition in if statement")
        
        if not if_body:
            self.errors.append(f"Error at line {if_token.lineno}: Missing code block in if statement")
    
    def write_errors_to_file(self):
        """Write all errors and warnings to their respective files."""
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.error_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
        
        # Write errors to file
        with open(self.error_file, "w") as f:
            if self.errors:
                for error in self.errors:
                    f.write(error + "\n")
            else:
                f.write("No errors detected during parsing.\n")
        
        # Write warnings to file
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
        
        # Create the directories if they don't exist
        os.makedirs(os.path.dirname(self.error_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
        
        # Clear the error and warning files
        with open(self.error_file, "w") as f:
            f.write("")
        
        with open(self.warning_file, "w") as f:
            f.write("")