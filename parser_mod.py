import ply.yacc as yacc
from lexer_module.lexer import tokens, lexer  # Import token definitions from the lexer
import os
from parser_module.custom_error_hander import CustomErrorHandler  # Import CustomErrorHandler from the appropriate module
from parser_module.user_input_handler import UserInputHandler  # Import UserInputHandler from the appropriate module

# Symbol table for tracking variables and their types
symbol_table = {}

# Create error handler instance and input handler instance
# Error handler instance is created with the symbol table
error_handler = CustomErrorHandler()
input_handler = UserInputHandler(symbol_table)

# Token Stream Wrapper
class TokenStream:
    """
    A wrapper for token streams that provides an interface compatible with PLY's lexer.
    This allows us to use a pre-tokenized list as input to the parser.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_line = 1 if tokens else 0

    def token(self):
        if self.index < len(self.tokens):
            tok = self.tokens[self.index]
            self.current_line = getattr(tok, 'lineno', self.current_line)
            self.index += 1
            return tok
        return None

    @property
    def lineno(self):
        if self.index < len(self.tokens):
            return getattr(self.tokens[self.index], 'lineno', self.current_line)
        return self.current_line

    @property
    def lexpos(self):
        if self.index < len(self.tokens):
            return getattr(self.tokens[self.index], 'lexpos', 0)
        return 0

# -------------------------------------------------------------------------------
# AST NODE CLASS
# -------------------------------------------------------------------------------
class Node:
    """
    A class representing nodes in the abstract syntax tree.
    """
    def __init__(self, node_type, lineno=None, **kwargs):
        """
        Initialize a new node with type, line number, and other attributes.
        """
        self.type = node_type
        self.lineno = lineno
        
        # Add all other attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __str__(self):
        """
        String representation with each attribute on a new line.
        """
        lines = []
        lines.append("{")
        lines.append(f"  'type': '{self.type}',")
        if hasattr(self, 'lineno') and self.lineno is not None:
            lines.append(f"  'lineno': {self.lineno},")
        
        # Add all other attributes
        for key, value in self.__dict__.items():
            if key not in ['type', 'lineno']:
                # Format the value appropriately
                if isinstance(value, str):
                    formatted_value = f"'{value}'"
                else:
                    formatted_value = str(value)
                lines.append(f"  '{key}': {formatted_value},")
        
        lines.append("}")
        
        # Join with newlines
        return "\n".join(lines)
    
    def __repr__(self):
        """
        Use the same representation as str for debugging.
        """
        return self.__str__()
    
    def get(self, key, default=None):
        """
        Get an attribute with a default value, similar to dictionary behavior.
        """
        return getattr(self, key, default)
    
    def __getitem__(self, key):
        """
        Allow dictionary-style access to attributes.
        """
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        """
        Allow dictionary-style setting of attributes.
        """
        setattr(self, key, value)
    
    def __contains__(self, key):
        """
        Allow 'in' operator to check for attributes.
        """
        return hasattr(self, key)

# -------------------------------------------------------------------------------
# AST NODE CREATION
# -------------------------------------------------------------------------------
def create_node(node_type, lineno=None, **kwargs):
    """
    Create an AST node with the given type and attributes.
    """
    return Node(node_type, lineno, **kwargs)

# -------------------------------------------------------------------------------
# TYPE CHECKING
# -------------------------------------------------------------------------------
def type_check(var_name, expected_type, lineno):
    """
    Check if a variable has the expected type.
    """
    return error_handler.check_type_mismatch(var_name, expected_type, lineno)

# GRAMMAR RULES
# -------------------------------------------------------------------------------
def p_program(p):
    '''program : statement_list'''
    p[0] = create_node('program', lineno=p.lineno(1), statements=p[1])

# -------------------------------------------------------------------------------
# STATEMENT RULES
# -------------------------------------------------------------------------------
def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement
                      | '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_statement(p):
    '''statement : command_stmt EOL
                 | declaration_stmt EOL
                 | if_stmt'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# DECLARATION STATEMENTS
# -------------------------------------------------------------------------------
def p_declaration_stmt(p):
    '''declaration_stmt : STRING_TYPE IDENTIFIER EQUALS STRING_LITERAL
                        | INT_TYPE IDENTIFIER EQUALS NUMBER
                        | DATE_TYPE IDENTIFIER EQUALS DATE_VAL'''

    var_name = p[2]
    var_type = p[1]
    symbol_table[var_name] = var_type
    error_handler.set_symbol_table(symbol_table)

    p[0] = create_node('declaration', lineno=p.lineno(1),
                        var_name=var_name,
                        var_type=var_type)

# -------------------------------------------------------------------------------
# IF STATEMENTS
# -------------------------------------------------------------------------------
def p_if_stmt(p):
    '''if_stmt : if_then_stmt
               | if_then_else_stmt'''
    p[0] = p[1]

def p_if_then_stmt(p):
    '''if_then_stmt : IF LPAREN condition RPAREN LBRACKET statement_list RBRACKET'''
    # Check if statement completeness
    error_handler.check_if_statement_completeness(p.slice[1], p[3], p[6])
    
    p[0] = create_node('if_statement',
                        lineno=p.lineno(1),
                        condition=p[3],
                        if_body=p[6])

def p_if_then_else_stmt(p):
    '''if_then_else_stmt : IF LPAREN condition RPAREN LBRACKET statement_list RBRACKET ELSE LBRACKET statement_list RBRACKET'''
    # Check if statement completeness
    error_handler.check_if_statement_completeness(p.slice[1], p[3], p[6], p[10])
    
    p[0] = create_node('if_statement',
                        lineno=p.lineno(1),
                        condition=p[3],
                        if_body=p[6],
                        else_body=p[10])

def p_condition(p):
    '''condition : expression GT expression
                 | expression LT expression
                 | expression GE expression
                 | expression LE expression
                 | expression EQ expression
                 | expression NE expression'''

    p[0] = create_node('condition', lineno=p.lineno(2),
                        left=p[1],
                        operator=p[2],
                        right=p[3])

def p_expression(p):
    '''expression : IDENTIFIER
                 | NUMBER
                 | STRING_LITERAL
                 | DATE_VAL'''

    if p.slice[1].type == 'IDENTIFIER':
        if p[1] in symbol_table:
            p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type=symbol_table[p[1]])
        else:
            # Error will be reported by the error handler
            p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='unknown')
    elif p.slice[1].type == 'NUMBER':
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='int')
    elif p.slice[1].type == 'STRING_LITERAL':
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='string')
    else:
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='date')

# -------------------------------------------------------------------------------
# COMMAND STATEMENTS
# -------------------------------------------------------------------------------
def p_command_stmt(p):
    '''command_stmt : book_cmd
                     | cancel_cmd
                     | list_cmd
                     | check_cmd
                     | pay_cmd
                     | display_cmd
                     | accept_cmd'''
    p[0] = p[1]

# Booking Commands
def p_book_cmd(p):
    '''book_cmd : BOOK quantity TICKETS FOR customer ON date FOR event'''
    quantity = p[2]
    customer = p[4]
    date = p[6]
    event = p[8]

    p[0] = create_node('book_command', lineno=p.lineno(1),
                        quantity=quantity,
                        customer=customer,
                        date=date,
                        event=event)

def p_quantity(p):
    '''quantity : NUMBER
                | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        error = type_check(p[1], 'int', p.lineno(1))
        if error:
            p[0] = create_node('error', lineno=p.lineno(1), message=f"Error at line {p.lineno(1)}: Invalid quantity")
            return
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='int')
    else:
        p[0] = p[1]

def p_customer(p):
    '''customer : STRING_LITERAL
                | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        error = type_check(p[1], 'string', p.lineno(1))
        if error:
            p[0] = create_node('error', lineno=p.lineno(1), message=f"Error at line {p.lineno(1)}: Invalid customer")
            return
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = p[1]

def p_date(p):
    '''date : DATE_VAL
            | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        error = type_check(p[1], 'date', p.lineno(1))
        if error:
            p[0] = create_node('error', lineno=p.lineno(1), message=f"Error at line {p.lineno(1)}: Invalid date")
            return
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='date')
    else:
        p[0] = p[1]

def p_event(p):
    '''event : STRING_LITERAL
             | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        error = type_check(p[1], 'string', p.lineno(1))
        if error:
            p[0] = create_node('error', lineno=p.lineno(1), message=f"Error at line {p.lineno(1)}: Invalid event")
            return
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = p[1]

# Cancel Commands
def p_cancel_cmd(p):
    '''cancel_cmd : CANCEL ticket_or_tickets FOR customer EVENT event'''
    p[0] = create_node('cancel_command', lineno=p.lineno(1),
                        customer=p[4],
                        event=p[6])

def p_ticket_or_tickets(p):
    '''ticket_or_tickets : TICKET
                          | TICKETS'''
    p[0] = p[1]

# List Commands
def p_list_cmd(p):
    '''list_cmd : LIST EVENTS ON date
                  | LIST EVENTS FOR event'''

    attrs = {'item_type': p[2]}

    if p[3] == 'ON':
        attrs['date'] = p[4]
    elif p[3] == 'FOR':
        attrs['event'] = p[4]

    p[0] = create_node('list_command',
                        lineno=p.lineno(1),
                        **attrs)

# Check Commands
def p_check_cmd(p):
    '''check_cmd : CHECK AVAILABILITY FOR event ON date
                  | CHECK PRICE FOR event ON date'''

    p[0] = create_node('check_command', lineno=p.lineno(1),
                        check_type=p[2],
                        event=p[4],
                        date=p[6])

# Pay Commands
def p_pay_cmd(p):
    '''pay_cmd : PAY FOR event customer'''

    p[0] = create_node('pay_command', lineno=p.lineno(1),
                        event=p[3],
                        customer=p[4])

# Display Commands
def p_display_cmd(p):
    '''display_cmd : DISPLAY message'''

    p[0] = create_node('display_command',
                        lineno=p.lineno(1),
                        message=p[2])

def p_message(p):
    '''message : STRING_LITERAL
               | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        error = type_check(p[1], 'string', p.lineno(1))
        if error:
            p[0] = create_node('error', lineno=p.lineno(1), message=f"Error at line {p.lineno(1)}: Invalid message")
            return
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = p[1]

# Accept Commands
def p_accept_cmd(p):
    '''accept_cmd : ACCEPT IDENTIFIER'''

    var_name = p[2]
    
    # Handle implicitly declared variables from the accept command
    if var_name not in symbol_table:
        # Default to string type for user input
        symbol_table[var_name] = 'string'
        # Notify the error handler for a warning
        error_handler.handle_implicit_declaration(var_name, p.lineno(2))
    
    # Register this variable with the user input handler
    var_type = symbol_table[var_name]
    
    p[0] = create_node('accept_command', lineno=p.lineno(1),
                       variable=var_name, 
                       var_type=var_type)

# -------------------------------------------------------------------------------
# End of line (EOL) -
# -------------------------------------------------------------------------------
def p_EOL(p):
    '''EOL : DOT'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# Error function - Now using our custom error handler
# -------------------------------------------------------------------------------
def p_error(p):
    if p:
        error_msg = (
            f"[Syntax Error] Unexpected token '{p.value}' (type: {p.type}) at line {p.lineno}\n"
            "  • Why it’s an error: This token does not match any valid grammar rule here.\n"
            "  • Suggestion: Double-check the structure of your command or statement.\n"
            "    → For example, ensure commands end with a period and follow the format like:\n"
            "      book 2 tickets for \"John\" on March 15, 2025 for \"Jazz Fest\"."
        )
    else:
        error_msg = (
            "[Syntax Error] Unexpected end of input (EOF).\n"
            "  • Why it’s an error: The parser expected more tokens to complete the statement.\n"
            "  • Suggestion: You might be missing a closing bracket, parenthesis, or period."
        )
    print(error_msg)

# -------------------------------------------------------------------------------
# Build the Parser
# -------------------------------------------------------------------------------
parser = yacc.yacc(debug=True)

# -------------------------------------------------------------------------------
# Parse Function
# -------------------------------------------------------------------------------
def parse(token_list):
    """
    Parse a list of tokens into an abstract syntax tree (AST).
    """
    global symbol_table
    symbol_table = {}  # Reset symbol table for each parse
    
    # Clear errors from previous runs
    error_handler.clear_errors()
    
    # Set up token stream
    ts = TokenStream(token_list)
    parser.token_stream = ts # Set the token stream for error tracking

    error_handler.set_token_stream(ts) # Set the token stream for error handling
    error_handler.set_symbol_table(symbol_table) # Set the symbol table for type checking

    # Initialize user input handler
    input_handler = UserInputHandler(symbol_table)

    try:
        ast = parser.parse(lexer=ts, tracking=True) # Parse the token stream
        
        # Add user input handler information to the AST
        if ast:
            ast.input_handler = input_handler
            
        # Check for unclosed brackets at the end of parsing
        error_handler.check_final_bracket_state()
        
        # Write any errors to file
        has_errors = error_handler.write_errors_to_file()
        
        return ast, has_errors
    except Exception as e:
        # Handle any unexpected exceptions
        error_handler.errors.append(f"Parsing error: {str(e)}")
        error_handler.write_errors_to_file()
        return None, True