import ply.yacc as yacc
from lexer_module.lexer import tokens, lexer  # Import token definitions from the lexer
import os
import json
from parser_module.user_input_handler import UserInputHandler  # Import UserInputHandler

# Symbol table for tracking variables and their types
symbol_table = {}

# Create error handler instance and input handler instance
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
        self.current_line = 1 

        for token in self.tokens:
            if hasattr(token, 'lineno'):
                token.lineno = getattr(token, 'lineno', 1)  # Ensure each token has its correct line number


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
# AST NODE CREATION
# -------------------------------------------------------------------------------
def create_node(node_type, lineno=None, **kwargs):
    """
    Create an AST node as a dictionary with the given type and attributes.
    """
    node = {"type": node_type}
    if lineno is not None:
        node["lineno"] = lineno
    for key, value in kwargs.items():
        node[key] = value
    return node

# # -------------------------------------------------------------------------------
# # TYPE CHECKING
# # -------------------------------------------------------------------------------
# def type_check(var_name, expected_type, lineno):
#     """
#     Check if a variable has the expected type.
#     """
#     return error_handler.check_type_mismatch(var_name, expected_type, lineno)

# -------------------------------------------------------------------------------
# GRAMMAR RULES
# -------------------------------------------------------------------------------
def p_program(p):
    '''program : statement_list'''
    p[0] = create_node('program', lineno=p.lineno(1), statements=p[1])

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

    p[0] = create_node('declaration', lineno=p.lineno(1), var_name=p[2], var_type=p[1])

# -------------------------------------------------------------------------------
# IF STATEMENTS
# -------------------------------------------------------------------------------
def p_if_stmt(p):
    '''if_stmt : if_then_stmt
               | if_then_else_stmt'''
    p[0] = p[1]

def p_if_then_stmt(p):
    '''if_then_stmt : IF LPAREN condition RPAREN LBRACKET statement_list RBRACKET'''
    
    p[0] = create_node('if_statement', lineno=p.lineno(1), condition=p[3], if_body=p[6])

def p_if_then_else_stmt(p):
    '''if_then_else_stmt : IF LPAREN condition RPAREN LBRACKET statement_list RBRACKET ELSE LBRACKET statement_list RBRACKET'''
    
    p[0] = create_node('if_statement', lineno=p.lineno(1), condition=p[3], if_body=p[6], else_body=p[10])

def p_condition(p):
    '''condition : expression GT expression
                 | expression LT expression
                 | expression GE expression
                 | expression LE expression
                 | expression EQ expression
                 | expression NE expression'''
    p[0] = create_node('condition', lineno=p.lineno(2), left=p[1], operator=p[2], right=p[3])

def p_expression(p):
    '''expression : IDENTIFIER
                 | NUMBER
                 | STRING_LITERAL
                 | DATE_VAL'''
    if p.slice[1].type == 'IDENTIFIER':
        if p[1] in symbol_table:
            p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type=symbol_table[p[1]])
        else:
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
    p[0] = create_node('book_command', lineno=p.lineno(1), 
                       quantity=p[2], 
                       customer=p[5], 
                       date=p[7], 
                       event=p[9])

def p_quantity(p):
    '''quantity : NUMBER
                | IDENTIFIER'''
    
    p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='int')

def p_customer(p):
    '''customer : STRING_LITERAL
                | IDENTIFIER'''
    
    if p.slice[1].type == 'IDENTIFIER':
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='string')

def p_date(p):
    '''date : DATE_VAL
            | IDENTIFIER'''
    
    if p.slice[1].type == 'IDENTIFIER':
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='date')
    else:
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='date')

def p_event(p):
    '''event : STRING_LITERAL
             | IDENTIFIER'''
    
    if p.slice[1].type == 'IDENTIFIER':
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = create_node('literal', lineno=p.lineno(1), value=p[1], lit_type='string')

# Cancel Commands
def p_cancel_cmd(p):
    '''cancel_cmd : CANCEL ticket_or_tickets FOR customer EVENT event'''
    p[0] = create_node('cancel_command', lineno=p.lineno(1), customer=p[4], event=p[6])

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
    p[0] = create_node('list_command', lineno=p.lineno(1), **attrs)

# Check Commands
def p_check_cmd(p):
    '''check_cmd : CHECK AVAILABILITY FOR event ON date
                  | CHECK PRICE FOR event ON date'''
    p[0] = create_node('check_command', lineno=p.lineno(1), check_type=p[2], event=p[4], date=p[6])

# Pay Commands
def p_pay_cmd(p):
    '''pay_cmd : PAY FOR event customer'''
    p[0] = create_node('pay_command', lineno=p.lineno(1), event=p[3], customer=p[4])

# Display Commands
def p_display_cmd(p):
    '''display_cmd : DISPLAY message'''
    p[0] = create_node('display_command', lineno=p.lineno(1), message=p[2])

def p_message(p):
    '''message : STRING_LITERAL
               | IDENTIFIER'''
    if p.slice[1].type == 'IDENTIFIER':
        p[0] = create_node('variable', lineno=p.lineno(1), name=p[1], var_type='string')
    else:
        p[0] = p[1]

# Accept Commands
def p_accept_cmd(p):
    '''accept_cmd : ACCEPT IDENTIFIER'''

    var_name = p[2]
    p[0] = create_node('accept_command', lineno=p.lineno(1), variable=var_name, var_type=symbol_table[var_name])

# -------------------------------------------------------------------------------
# End of line (EOL)
# -------------------------------------------------------------------------------
def p_EOL(p):
    '''EOL : DOT'''
    p[0] = p[1]

# -------------------------------------------------------------------------------
# Error Handling
# -------------------------------------------------------------------------------

# List to store syntax errors
syntax_errors = []    

def p_error(p):
    if p:
        # Get line number consistently
        lineno = p.lineno 

        # Get the current state of the parser
        state = parser.state

        # Get the production rule for the current state
        production = parser.productions[state]

        # Generate an error message
        error_msg = (
            f"- Syntax error at [{lineno}:{find_column(p)}]:"
            f"\n\tUnexpected token '{p.value}'. "
            f"\n\tExpected token: {get_expected_tokens(state)}. "
        )
    else:
        error_msg = "Syntax error at EOF.\n"

    syntax_errors.append(error_msg)

# Helper function to find the column of the error
def find_column(token):
    last_cr = lexer.lexdata.rfind('\n', 0, token.lexpos) 

    if last_cr < 0:                     
        last_cr = 0

    column = (token.lexpos - last_cr)
    return column

# Helper function to get expected tokens for a state
def get_expected_tokens(state):
    action = parser.action[state] 
    expected_tokens = []

    for token, _ in action.items():
        if token != 'error':
            expected_tokens.append(token)

    return expected_tokens

# -------------------------------------------------------------------------------
# Build the Parser
# -------------------------------------------------------------------------------
parser = yacc.yacc(debug=True)

# -------------------------------------------------------------------------------
# Parse Function
# -------------------------------------------------------------------------------
def parse(token_list):
    """
    Parse a list of tokens into an abstract syntax tree (AST) and return the symbol table.
    Save the AST to a JSON file.
    """
    global symbol_table
    symbol_table = {}  # Reset symbol table for each parse

    global syntax_errors
    syntax_errors = []  # Reset syntax errors for each parse

    lexer.lineno = 1  # Reset the main lexer's line counter

    print(f"Starting parse with lexer.lineno = {lexer.lineno}") #DEBUG
    
    # Set up token stream
    ts = TokenStream(token_list)
    parser.token_stream = ts  # Set the token stream for error tracking

    # Initialize user input handler
    input_handler = UserInputHandler(symbol_table)

    try: 
        # Reset index for actual parsing
        ts.index = 0
            
        ast = parser.parse(lexer=ts, tracking=True)  # Parse the token stream
            
        # Add user input handler information to the AST
        if ast:
            ast["input_handler"] = str(input_handler)  # Convert input_handler to string for JSON serialization

        # Write error to file
        with open("parser_module/parser_errors.txt", "w") as f:
            for error in syntax_errors:
                f.write(error)
            f.close()
        
        has_errors = bool(syntax_errors) # declare

        if syntax_errors is None:
            has_errors = False 

            # Save the AST to a JSON file
            ast_file = "parser_module/parser_output.json"

            os.makedirs(os.path.dirname(ast_file), exist_ok=True)
            with open(ast_file, "w") as f:
                json.dump(ast, f, indent=4)

            print(f"AST saved to {ast_file}")

        return ast, symbol_table, has_errors  # Return AST, symbol table, and error status
    
    except Exception as e:
        # Handle any unexpected exceptions
        print(f"Parsing Error: {str(e)}")
        return None, {}, True  # Return empty symbol table and error status