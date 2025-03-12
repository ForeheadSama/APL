# -----------------------------------------------------------------------------
# parser_mod.py - Modified Parser module for the language
# -----------------------------------------------------------------------------
import ply.yacc as yacc  # Import PLY's Yacc for parsing

# Import necessary modules
from lexer_module.lexer import tokens  # Import token definitions from the lexer

# -----------------------------------------------------------------------------
# Precedence Rules
# -----------------------------------------------------------------------------
precedence = (
    ('left', 'OR'),  # Lowest precedence
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'EQ', 'NEQ'),  # Equality operators
    ('left', 'LT', 'LE', 'GT', 'GE'),  # Relational operators
    ('left', 'PLUS', 'MINUS'),  # Addition and subtraction
    ('left', 'TIMES', 'DIVIDE'),  # Multiplication and division
    ('right', 'ELSE'),  # Resolve "dangling else" problem
    ('nonassoc', 'IF_PREC'),  # Precedence for resolving "dangling else"
)

# -----------------------------------------------------------------------------
# Token Stream Wrapper
# -----------------------------------------------------------------------------
class TokenStream:
    """
    A simple wrapper that accepts a list of tokens and provides
    the token() method required by yacc.
    Also keeps track of the current line number for error reporting.
    """
    def __init__(self, tokens):
        self.tokens = tokens                    # Store the list of tokens
        self.index = 0                          # Initialize index to track the current token
        self.current_line = 1 if tokens else 0  # Track the current line number
        
    def token(self):
        """Returns the next token in the list."""
        if self.index < len(self.tokens):       # Ensure we haven't reached the end
            tok = self.tokens[self.index]       # Get the current token
            self.current_line = getattr(tok, 'lineno', self.current_line)  # Update line number
            self.index += 1                     # Move to the next token
            return tok                          # Return the current token
        return None                             # Return None when all tokens are processed
    
    @property
    def lineno(self):
        """Returns the current line number for error reporting."""
        if self.index < len(self.tokens):       # Ensure we haven't reached the end
            return getattr(self.tokens[self.index], 'lineno', self.current_line)  # Get line number from token
        return self.current_line                # Return the last known line number

    @property
    def lexpos(self):
        """Returns the current position in the input stream."""
        if self.index < len(self.tokens):       # Ensure we haven't reached the end
            return getattr(self.tokens[self.index], 'lexpos', 0)  # Get position from token
        return 0                                # Return 0 if no tokens are left

# Abstract Syntax Tree (AST) Node Creation
def create_node(node_type, lineno=None, **kwargs):
    """Create an AST node with line number information."""
    return {'type': node_type, 'lineno': lineno, **kwargs}

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
                      | statement'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''statement : declaration_stmt
                 | assignment_stmt
                 | function_call_stmt
                 | if_stmt
                 | while_stmt
                 | return_stmt
                 | function_def_stmt
                 | break_stmt
                 | continue_stmt
                 | foreach_stmt
                 | until_stmt
                 | then_stmt
                 | builtin_function_stmt'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# BUILT-IN FUNCTION RULES
# -------------------------------------------------------------------------------
def p_builtin_function_stmt(p):
    '''builtin_function_stmt : BOOK LPAREN arg_list RPAREN EOL
                            | CANCEL LPAREN arg_list RPAREN EOL
                            | LIST_EVENTS LPAREN arg_list RPAREN EOL
                            | CHECK_AVAILABILITY LPAREN arg_list RPAREN EOL
                            | MAKE_PAYMENT LPAREN arg_list RPAREN EOL
                            | REG LPAREN arg_list RPAREN EOL
                            | DISPLAY LPAREN arg_list RPAREN EOL
                            | ACCEPT LPAREN arg_list RPAREN EOL'''
    
    # Special handling for built-in functions
    p[0] = create_node('builtin_function_call', 
                       lineno=p.lineno(1),
                       name=p[1].lower(),  # Store the function name in lowercase
                       arguments=p[3])

def p_builtin_function_call(p):
    '''builtin_function_call : BOOK LPAREN arg_list RPAREN
                            | CANCEL LPAREN arg_list RPAREN
                            | LIST_EVENTS LPAREN arg_list RPAREN
                            | CHECK_AVAILABILITY LPAREN arg_list RPAREN
                            | MAKE_PAYMENT LPAREN arg_list RPAREN
                            | REG LPAREN arg_list RPAREN
                            | DISPLAY LPAREN arg_list RPAREN
                            | ACCEPT LPAREN arg_list RPAREN'''
    
    p[0] = create_node('builtin_function_call', 
                       lineno=p.lineno(1),
                       name=p[1].lower(),  # Store the function name in lowercase
                       arguments=p[3])
# -------------------------------------------------------------------------------
# DECLARATION RULES
# -------------------------------------------------------------------------------
def p_declaration_stmt(p):
    '''declaration_stmt : type_specifier IDENTIFIER EQUALS expression EOL
                       | type_specifier IDENTIFIER EQUALS function_call EOL
                       | type_specifier IDENTIFIER EQUALS builtin_function_call EOL'''

    p[0] = create_node('declaration', 
                      lineno=p.lineno(1),
                      var_type=p[1], 
                      name=p[2], 
                      value=p[4])

# -------------------------------------------------------------------------------
# TYPE SPECIFIER RULES
# -------------------------------------------------------------------------------
def p_type_specifier(p):
    '''type_specifier : INT_TYPE
                      | FLOAT_TYPE
                      | STRING_TYPE
                      | BOOL_TYPE
                      | DATE_TYPE
                      | TIME_TYPE
                      | VOID'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# ASSIGNMENT RULES
# -------------------------------------------------------------------------------
def p_assignment_stmt(p):
    '''assignment_stmt : IDENTIFIER EQUALS expression EOL
                       | IDENTIFIER EQUALS function_call EOL
                       | IDENTIFIER EQUALS builtin_function_call EOL'''
    p[0] = create_node('assignment', 
                      lineno=p.lineno(1),
                      target=p[1], 
                      value=p[3])

# -------------------------------------------------------------------------------
# FUNCTION CALL RULES (for user-defined functions)
# -------------------------------------------------------------------------------
def p_function_call_stmt(p):
    '''function_call_stmt : function_call EOL
                         | builtin_function_call EOL'''
    p[0] = p[1]

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN arg_list RPAREN'''
    # Only for user-defined functions (not built-in functions)
    if p[1].lower() not in ['book', 'cancel', 'list_events', 'check_availability', 
                           'make_payment', 'reg', 'display', 'accept']:
        p[0] = create_node('function_call', 
                          lineno=p.lineno(1),
                          name=p[1], 
                          arguments=p[3])
    else:
        # This will be handled by the builtin_function_call rule
        p[0] = create_node('function_call', 
                          lineno=p.lineno(1),
                          name=p[1], 
                          arguments=p[3])

def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
                | expression
                | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]

# -------------------------------------------------------------------------------
# CONTROL FLOW RULES
# -------------------------------------------------------------------------------
def p_if_stmt(p):
    '''if_stmt : IF LPAREN expression RPAREN block_stmt %prec IF_PREC
               | IF LPAREN expression RPAREN block_stmt ELSE block_stmt'''
    if len(p) == 6:
        p[0] = create_node('if', 
                          lineno=p.lineno(1),
                          condition=p[3], 
                          then_block=p[5])
    else:
        p[0] = create_node('if', 
                          lineno=p.lineno(1),
                          condition=p[3], 
                          then_block=p[5], 
                          else_block=p[7])

def p_while_stmt(p):
    '''while_stmt : WHILE LPAREN expression RPAREN block_stmt'''
    p[0] = create_node('while', 
                      lineno=p.lineno(1),
                      condition=p[3], 
                      body=p[5])

def p_block_stmt(p):
    '''block_stmt : LBRACKET statement_list RBRACKET '''
    p[0] = create_node('block', 
                      lineno=p.lineno(1),
                      statements=p[2])

def p_return_stmt(p):
    '''return_stmt : RETURN expression EOL'''
    p[0] = create_node('return', 
                      lineno=p.lineno(1),
                      value=p[2])

# -------------------------------------------------------------------------------
# EXPRESSION RULES
# -------------------------------------------------------------------------------
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = create_node('binary_op', 
                      lineno=p.lineno(2),
                      op=p[2], 
                      left=p[1], 
                      right=p[3])

def p_expression_relop(p):
    '''expression : expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression EQ expression
                  | expression NEQ expression'''
    p[0] = create_node('relational_op', 
                      lineno=p.lineno(2),
                      op=p[2], 
                      left=p[1], 
                      right=p[3])

def p_expression_logical(p):
    '''expression : expression AND expression
                  | expression OR expression
                  | NOT expression'''
    if len(p) == 4:
        if p[2] == 'and':
            p[0] = create_node('logical_and', 
                              lineno=p.lineno(2),
                              left=p[1], 
                              right=p[3])
        elif p[2] == 'or':
            p[0] = create_node('logical_or', 
                              lineno=p.lineno(2),
                              left=p[1], 
                              right=p[3])
    else:  # NOT case
        p[0] = create_node('logical_not', 
                          lineno=p.lineno(1),
                          expr=p[2])

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]
    # Keep the line number but don't change the structure

def p_expression_atom(p):
    '''expression : NUMBER
                  | FLOAT_NUM
                  | STRING_LITERAL
                  | BOOLEAN_VAL
                  | DATE_VAL
                  | TIME_VAL
                  | IDENTIFIER'''
    p[0] = create_node('literal', 
                      lineno=p.lineno(1),
                      value=p[1])

def p_expression_function_call(p):
    '''expression : function_call
                  | builtin_function_call'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# CONTROL FLOW RULES
# -------------------------------------------------------------------------------
def p_break_stmt(p):
    '''break_stmt : BREAK EOL'''
    p[0] = create_node('break', lineno=p.lineno(1))

def p_continue_stmt(p):
    '''continue_stmt : CONTINUE EOL'''
    p[0] = create_node('continue', lineno=p.lineno(1))

# -------------------------------------------------------------------------------
# FUNCTION DEFINITION RULES
# -------------------------------------------------------------------------------
def p_function_def_stmt(p):
    '''function_def_stmt : FUNCTION type_specifier IDENTIFIER LPAREN param_list RPAREN block_stmt'''
    
    p[0] = create_node('function_def', 
                      lineno=p.lineno(1),
                      return_type=p[2], 
                      name=p[3], 
                      params=p[5], 
                      body=p[7])

def p_param_list(p):
    '''param_list : param_list COMMA param
                  | param
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]

def p_param(p):
    '''param : type_specifier IDENTIFIER'''
    p[0] = create_node('parameter', 
                      lineno=p.lineno(1),
                      param_type=p[1], 
                      name=p[2])

# -------------------------------------------------------------------------------
# LOOP RULES
# -------------------------------------------------------------------------------
def p_foreach_stmt(p):
    '''foreach_stmt : FOREACH LPAREN IDENTIFIER IN expression RPAREN block_stmt'''
    p[0] = create_node('foreach', 
                      lineno=p.lineno(1),
                      iterator=p[3], 
                      iterable=p[5], 
                      body=p[7])

def p_until_stmt(p):
    '''until_stmt : UNTIL LPAREN expression RPAREN block_stmt'''
    p[0] = create_node('until', 
                      lineno=p.lineno(1),
                      condition=p[3], 
                      body=p[5])

def p_then_stmt(p):
    '''then_stmt : THEN block_stmt'''
    p[0] = create_node('then', 
                      lineno=p.lineno(1),
                      body=p[2])

# -------------------------------------------------------------------------------
def p_empty(p):
    'empty :'
    p[0] = None

# -----------------------------------------------------------------------------
# Error function
# -----------------------------------------------------------------------------
def p_error(p):
    print(".")
    
# -----------------------------------------------------------------------------
# Build the Parser
# -----------------------------------------------------------------------------
parser = yacc.yacc(debug=True, optimize=False, errorlog=yacc.NullLogger())  # Build the parser with debugging enabled

# -----------------------------------------------------------------------------
# Parse Function
# -----------------------------------------------------------------------------
def parse(token_list):
    """
    Accepts a list of tokens (produced by the lexer) and returns the AST and any syntax errors.
    
    Args:
        token_list: List of tokens from the lexer
        
    Returns:
        tuple: (AST, list of errors)
    """
    
    # Initialize or reset the error list
    parser.errors = []
    
    try:
        # Create a token stream wrapper around the token list
        ts = TokenStream(token_list)
        
        # Store the token stream in the parser for error handling purposes
        parser.token_stream = ts
        
        # Parse the input token stream and generate an AST
        ast = parser.parse(lexer=ts, tracking=True)
        
        # Check if there were any errors during parsing
        errors = getattr(parser, 'errors', [])
        
        # If we get a valid AST but also have errors, we still want to report those errors
        return ast, errors
    
    except Exception as e:
        # Add the exception message to errors
        error_msg = f"Parser exception: {str(e)}"
        
        if hasattr(parser, 'errors'):
            parser.errors.append(error_msg)
        else:
            parser.errors = [error_msg]
        
        # Return None as AST and the list of errors
        return None, parser.errors