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
        
        # Command structure definitions based on grammar
        self.command_structures = {
            'BOOK': ['BOOK', 'NUMBER/IDENTIFIER', 'TICKETS', 'FOR', 'STRING_LITERAL/IDENTIFIER', 'ON', 'DATE_VAL/IDENTIFIER', 'FOR', 'STRING_LITERAL/IDENTIFIER'],
            'CANCEL': ['CANCEL', 'TICKET/TICKETS', 'FOR', 'STRING_LITERAL/IDENTIFIER', 'EVENT', 'STRING_LITERAL/IDENTIFIER'],
            'LIST': [
                ['LIST', 'EVENTS', 'ON', 'DATE_VAL/IDENTIFIER'],
                ['LIST', 'EVENTS', 'FOR', 'STRING_LITERAL/IDENTIFIER']
            ],
            'CHECK': [
                ['CHECK', 'AVAILABILITY', 'FOR', 'STRING_LITERAL/IDENTIFIER', 'ON', 'DATE_VAL/IDENTIFIER'],
                ['CHECK', 'PRICE', 'FOR', 'STRING_LITERAL/IDENTIFIER', 'ON', 'DATE_VAL/IDENTIFIER']
            ],
            'PAY': ['PAY', 'FOR', 'STRING_LITERAL/IDENTIFIER', 'STRING_LITERAL/IDENTIFIER'],
            'DISPLAY': ['DISPLAY', 'STRING_LITERAL/IDENTIFIER'],
            'ACCEPT': ['ACCEPT', 'IDENTIFIER']
        }
        
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
            
            # Check for incomplete commands
            self._check_incomplete_command(p)
            
            # Check for missing EOL at end of command
            self._check_missing_dot_eol(p)

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
    
    def _check_missing_dot_eol(self, p):
        """Check if a statement is missing the DOT (EOL) at the end."""
        # This function specifically checks for missing dots at the end of commands
        if not self.token_stream:
            return
            
        # Get tokens from current token until the end of the stream or until we find DOT/EOL
        current_pos = self.token_stream.index - 1
        if current_pos < 0:
            return
            
        # Look forward from current position to find missing EOL
        i = current_pos
        has_eol = False
        command_tokens = []
        
        # Collect tokens up to the next DOT or end of input
        while i < len(self.token_stream.tokens):
            token = self.token_stream.tokens[i]
            command_tokens.append(token)
            if token.type == 'DOT' or token.type == 'EOL':
                has_eol = True
                break
            i += 1
        
        # If no EOL found and we're at an end of command token
        if not has_eol and command_tokens:
            last_token = command_tokens[-1]
            if last_token.type in ['IDENTIFIER', 'NUMBER', 'STRING_LITERAL', 'DATE_VAL', 'EVENTS', 
                                  'AVAILABILITY', 'PRICE', 'RBRACKET']:
                error_msg = f"Error at line {last_token.lineno}: Missing end of statement marker '.' after '{last_token.value}'"
                # Only add if not duplicate
                if error_msg not in self.errors:
                    self.errors.append(error_msg)
    
    def _check_incomplete_command(self, p):
        """Check if the current token is part of an incomplete command structure."""
        if not self.token_stream:
            return
            
        # Get the position of the current token
        current_pos = self.token_stream.index - 1
        if current_pos < 0:
            return
            
        # Look backward to find the start of the current command
        command_start = current_pos
        while command_start > 0:
            prev_token = self.token_stream.tokens[command_start - 1]
            if prev_token.type == 'DOT' or prev_token.type == 'EOL':
                break
            command_start -= 1
        
        # Extract the current command tokens
        current_command = self.token_stream.tokens[command_start:current_pos + 1]
        
        # Check if this is empty or just contains a single token
        if not current_command:
            return
            
        # Check for standalone LIST token without required EVENTS keyword
        if len(current_command) == 1 and current_command[0].type == 'LIST':
            error_msg = f"Error at line {current_command[0].lineno}: Incomplete LIST command. Expected 'EVENTS' after 'LIST'."
            if error_msg not in self.errors:
                self.errors.append(error_msg)
            return
            
        # Check if the command starts with a known command keyword
        first_token = current_command[0]
        if first_token.type in self.command_structures:
            # Get the expected structure for this command
            expected_structures = self.command_structures[first_token.type]
            
            # If not a list of lists, convert to one for uniform processing
            if not isinstance(expected_structures[0], list):
                expected_structures = [expected_structures]
                
            # Check each possible structure for this command
            valid_structure_found = False
            for structure in expected_structures:
                if self._check_command_against_structure(current_command, structure):
                    valid_structure_found = True
                    break
                    
            if not valid_structure_found:
                # Find the most specific error to report
                self._report_command_structure_error(current_command, expected_structures)
                
            # Special check for BOOK command with just number (e.g., "book 1.")
            if first_token.type == 'BOOK' and len(current_command) == 2 and current_command[1].type == 'NUMBER':
                error_msg = f"Error at line {first_token.lineno}: Incomplete BOOK command. Expected 'TICKETS' after '{current_command[1].value}'."
                if error_msg not in self.errors:
                    self.errors.append(error_msg)
                    
            # Special check for LIST command (e.g., "list all events.")
            if first_token.type == 'LIST':
                # Check if an invalid word is used (like "all" instead of proper syntax)
                for token in current_command[1:]:
                    if token.type == 'IDENTIFIER' and token.value.lower() not in ['events', 'for', 'on']:
                        error_msg = f"Error at line {token.lineno}: Invalid token '{token.value}' in LIST command. Expected proper syntax like 'LIST EVENTS ON date' or 'LIST EVENTS FOR event'."
                        if error_msg not in self.errors:
                            self.errors.append(error_msg)
                            break

    def _check_command_against_structure(self, command_tokens, expected_structure):
        """Check if the command tokens match the expected structure."""
        # Convert token types to match expected format
        token_types = []
        for token in command_tokens:
            if token.type == 'NUMBER':
                token_types.append('NUMBER/IDENTIFIER')
            elif token.type == 'STRING_LITERAL':
                token_types.append('STRING_LITERAL/IDENTIFIER')
            elif token.type == 'DATE_VAL':
                token_types.append('DATE_VAL/IDENTIFIER')
            elif token.type == 'IDENTIFIER':
                # For identifiers, we need to check what kind of value it might represent
                if len(token_types) > 0 and len(token_types) < len(expected_structure):
                    prev_expected = expected_structure[len(token_types)]
                    if prev_expected == 'NUMBER/IDENTIFIER':
                        token_types.append('NUMBER/IDENTIFIER')
                    elif prev_expected == 'STRING_LITERAL/IDENTIFIER':
                        token_types.append('STRING_LITERAL/IDENTIFIER')
                    elif prev_expected == 'DATE_VAL/IDENTIFIER':
                        token_types.append('DATE_VAL/IDENTIFIER')
                    else:
                        token_types.append(token.type)
                else:
                    token_types.append(token.type)
            else:
                token_types.append(token.type)
        
        # Special case for TICKET/TICKETS
        for i, token_type in enumerate(token_types):
            if token_type == 'TICKET' or token_type == 'TICKETS':
                token_types[i] = 'TICKET/TICKETS'
        
        # Check if the tokens match the structure as far as they go
        structure_match = True
        for i in range(min(len(token_types), len(expected_structure))):
            if token_types[i] != expected_structure[i] and expected_structure[i] not in token_types[i].split('/'):
                structure_match = False
                break
                
        # If there's a match but the command is shorter than expected, it might be incomplete
        if structure_match and len(token_types) < len(expected_structure):
            return True  # It's a valid partial match
            
        # If the length matches and all tokens match, it's a complete valid command
        return structure_match and len(token_types) == len(expected_structure)
    
    def _report_command_structure_error(self, command_tokens, expected_structures):
        """Report the most specific error about command structure."""
        if not command_tokens:
            return
            
        command_type = command_tokens[0].type
        command_lineno = command_tokens[0].lineno
        
        # Convert tokens to a string representation for error message
        command_str = " ".join([token.value for token in command_tokens])
        
        # Find the structure with the most matching tokens at the beginning
        best_match_structure = None
        best_match_count = 0
        
        for structure in expected_structures:
            # Convert token types to match expected format
            token_types = []
            for token in command_tokens:
                if token.type == 'NUMBER':
                    token_types.append('NUMBER/IDENTIFIER')
                elif token.type == 'STRING_LITERAL':
                    token_types.append('STRING_LITERAL/IDENTIFIER')
                elif token.type == 'DATE_VAL':
                    token_types.append('DATE_VAL/IDENTIFIER')
                elif token.type == 'IDENTIFIER':
                    # For identifiers, we need to check what kind of value it might represent
                    if len(token_types) > 0 and len(token_types) < len(structure):
                        prev_expected = structure[len(token_types)]
                        if prev_expected == 'NUMBER/IDENTIFIER':
                            token_types.append('NUMBER/IDENTIFIER')
                        elif prev_expected == 'STRING_LITERAL/IDENTIFIER':
                            token_types.append('STRING_LITERAL/IDENTIFIER')
                        elif prev_expected == 'DATE_VAL/IDENTIFIER':
                            token_types.append('DATE_VAL/IDENTIFIER')
                        else:
                            token_types.append(token.type)
                    else:
                        token_types.append(token.type)
                else:
                    token_types.append(token.type)
            
            # Special case for TICKET/TICKETS
            for i, token_type in enumerate(token_types):
                if token_type == 'TICKET' or token_type == 'TICKETS':
                    token_types[i] = 'TICKET/TICKETS'
            
            # Count how many tokens match at the beginning
            match_count = 0
            for i in range(min(len(token_types), len(structure))):
                if token_types[i] == structure[i] or structure[i] in token_types[i].split('/'):
                    match_count += 1
                else:
                    break
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_match_structure = structure
        
        # Generate error message
        if best_match_structure:
            if best_match_count < len(best_match_structure):
                # This is an incomplete command
                expected_next = best_match_structure[best_match_count]
                expected_desc = expected_next.replace('NUMBER/IDENTIFIER', 'quantity')
                expected_desc = expected_desc.replace('STRING_LITERAL/IDENTIFIER', 'text value')
                expected_desc = expected_desc.replace('DATE_VAL/IDENTIFIER', 'date value')
                expected_desc = expected_desc.replace('TICKET/TICKETS', 'TICKET or TICKETS')
                
                error_msg = f"Error at line {command_lineno}: Incomplete {command_type.lower()} command: '{command_str}'. Expected '{expected_desc}' next."
                self.errors.append(error_msg)
            elif best_match_count == len(best_match_structure):
                # This is a complete command with extra tokens
                if len(command_tokens) > len(best_match_structure):
                    error_msg = f"Error at line {command_lineno}: Extra tokens in {command_type.lower()} command: '{command_str}'."
                    self.errors.append(error_msg)
            else:
                # Fallback generic error
                error_msg = f"Error at line {command_lineno}: Invalid syntax in {command_type.lower()} command: '{command_str}'."
                self.errors.append(error_msg)
        else:
            # Fallback for no match at all
            error_msg = f"Error at line {command_lineno}: Invalid command syntax: '{command_str}'."
            self.errors.append(error_msg)
    
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
            
            # Also check for specific words that should be string literals in certain contexts
            words = p.value.lower().split()
            for word in words:
                if (word in ['john', 'doe', 'carnival', 'march'] or 
                    word.endswith('rd') or word.endswith('th') or 
                    word.endswith('st') or word.endswith('nd')):
                    prev_tokens = self._get_recent_tokens(3)
                    for prev in prev_tokens:
                        if prev.type in ['FOR', 'ON']:
                            self.errors.append(f"Error at line {p.lineno}: '{p.value}' should be a string literal enclosed in double quotes or a declared variable.")
                            break
    
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
            self.errors.append(f"Error at line {lineno}: Type mismatch for variable '{var_name}'. Expected {expected_type}, got {actual_type}")
            return True
            
        return False
    
    def check_end_of_input(self):
        """Check for unfinished commands at the end of input."""
        if not self.token_stream or not self.token_stream.tokens:
            return
            
        last_token = self.token_stream.tokens[-1]
        if last_token.type != 'DOT' and last_token.type != 'EOL':
            self.errors.append(f"Error at line {last_token.lineno}: Incomplete statement at end of input. Missing '.'")
            
        # Check for unclosed brackets at the end of input
        if self.expected_brackets:
            expected, line = self.expected_brackets[-1]
            self.errors.append(f"Error: Unclosed bracket at line {line}. Expected matching '{expected}'")
            
    def _peek_next_token(self, p):
        """Look ahead to the next token in the stream."""
        if not self.token_stream:
            return None
            
        current_pos = self.token_stream.index
        if current_pos < len(self.token_stream.tokens):
            return self.token_stream.tokens[current_pos]
            
        return None
        
    def _peek_prev_token(self, p):
        """Look back to the previous token in the stream."""
        if not self.token_stream:
            return None
            
        current_pos = self.token_stream.index - 2  # -1 for current token, -1 more for previous
        if current_pos >= 0:
            return self.token_stream.tokens[current_pos]
            
        return None
        
    def _get_recent_tokens(self, n=3):
        """Get the most recent N tokens from the stream, including current one."""
        if not self.token_stream:
            return []
            
        current_pos = self.token_stream.index - 1  # Current token position
        start_pos = max(0, current_pos - n + 1)
        return self.token_stream.tokens[start_pos:current_pos + 1]
        
    def _get_surrounding_tokens(self, p, before=2, after=2):
        """Get tokens surrounding the current token."""
        if not self.token_stream:
            return []
            
        # Find the position of p in the token stream
        p_pos = -1
        for i, token in enumerate(self.token_stream.tokens):
            if token == p:
                p_pos = i
                break
                
        if p_pos == -1:
            return []
            
        start_pos = max(0, p_pos - before)
        end_pos = min(len(self.token_stream.tokens), p_pos + after + 1)
        return self.token_stream.tokens[start_pos:end_pos]
        
    def write_errors_to_file(self):
        """Write all collected errors to a file."""
        if not self.errors:
            return
            
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.error_file), exist_ok=True)
        
        # Explicitly truncate the file first
        open(self.error_file, 'w').close()
        
        # Now write the errors
        with open(self.error_file, 'w') as f:
            for error in self.errors:
                f.write(f"{error}\n")
                
    def write_warnings_to_file(self):
        """Write all collected warnings to a file."""
        if not self.warnings:
            return
            
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
        
        with open(self.warning_file, 'w') as f:
            for warning in self.warnings:
                f.write(f"{warning}\n")
    
    def clear_errors(self):
        """Clear all collected errors."""
        self.errors = []
        self.warnings = []  
        self.symbol_table = {}
        self.current_token = None
        self.token_stream = None
        self.expected_brackets = []  # Stack to track brackets

    # def print_errors_and_warnings(self):
    #     """Print all errors and warnings to console."""
    #     if self.errors:
    #         print("\nErrors:")
    #         for error in self.errors:
    #             print(f"  {error}")
                
    #     if self.warnings:
    #         print("\nWarnings:")
    #         for warning in self.warnings:
    #             print(f"  {warning}")