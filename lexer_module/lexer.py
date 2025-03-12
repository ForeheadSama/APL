# lexer.py
#      Load the APBL source code from a file and tokenize it.
#      The tokens are written to a file named 'lexer_output.txt'.
# """

import ply.lex as lex

# Reserved words definition
reserved = {
    # Built-in Functions (these are now reserved keywords)
    'book': 'BOOK',         # For booking a ticket
    'cancel': 'CANCEL',       # For canceling a ticket
    'list_events': 'LIST_EVENTS',  # For listing available events
    'check_availability': 'CHECK_AVAILABILITY',  # For checking ticket availability
    'make_payment': 'MAKE_PAYMENT',  # For making payments
    'reg': 'REG',           # For registering a user     
    'display': 'DISPLAY',   # For displaying output
    'accept': 'ACCEPT',     # For accepting user input
    
    # Control Flow Keywords
    'if': 'IF',
    'while': 'WHILE',
    'foreach': 'FOREACH',
    'until': 'UNTIL',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    
    
    # Data Type Keywords
    'int': 'INT_TYPE',      # Integer type
    'float': 'FLOAT_TYPE',  # Floating-point type
    'string': 'STRING_TYPE',# String type
    'bool': 'BOOL_TYPE',    # Boolean type
    'date': 'DATE_TYPE',    # Date type
    'time': 'TIME_TYPE',    # Time type
    
    # Logical Operators
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    
    # Other Keywords
    'then': 'THEN',
    'else': 'ELSE',
    'function': 'FUNCTION',
    'void': 'VOID',         # Add void type
    'in': 'IN',             # for foreach loops
}

# Token list definition
tokens = [
    'NUMBER',           # e.g., 123
    'FLOAT_NUM',        # e.g., 2.95
    'STRING_LITERAL',   # e.g., "Hello, World!"
    'BOOLEAN_VAL',      # 'true' or 'false'
    'DATE_VAL',         # e.g., "2021-01-01"
    'TIME_VAL',         # e.g., "12:00:00"
    'IDENTIFIER',       # Variable or function names
    'EQUALS',           # =
    'EQ',               # ==
    'NEQ',              # !=
    'LT',               # <
    'GT',               # >
    'LE',               # <=
    'GE',               # >=
    'PLUS',             # +
    'MINUS',            # -
    'TIMES',            # *
    'DIVIDE',           # /
    'LPAREN',           # (
    'RPAREN',           # )
    'LBRACKET',         # '['
    'RBRACKET',         # ']'
    'COMMA',            # ,
    'COLON',            # :
    'EOL',              # .
] + list(set(reserved.values()))  # Use set to eliminate duplicates

# Simple token rules
t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_COLON = r':'

# Complex token rules
def t_EQ(t):
    r'=='
    return t

def t_NEQ(t):
    r'!='
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_LT(t):
    r'<'
    return t

def t_GT(t):
    r'>'
    return t

# EOL token (must come before FLOAT_NUM to avoid ambiguity)
def t_EOL(t):
    r'\.'
    return t

# Literal value rules
def t_FLOAT_NUM(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_BOOLEAN_VAL(t):
    r'True|False'
    t.value = t.value == 'True'
    return t

def t_DATE_VAL(t):
    r'"[0-9]{4}-[0-9]{2}-[0-9]{2}"'
    t.value = t.value[1:-1]
    return t

def t_TIME_VAL(t):
    r'"[0-9]{2}:[0-9]{2}:[0-9]{2}"'
    t.value = t.value[1:-1]
    return t

def t_STRING_LITERAL(t):
    r'"(?:\\.|[^"\\])*"'
    t.value = t.value[1:-1]
    return t

# Identifier rule
def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

# Comment rules
def t_COMMENT(t):
    r'\$\$.*'
    t.lexer.lineno += t.value.count('\n')  # Count newlines in comments
    pass

def t_MLCOMMENT(t):
    r'\$<[\s\S]*?\>\$'
    t.lexer.lineno += t.value.count('\n')  # Count newlines in multiline comments
    pass

# Whitespace handling
def t_whitespace(t):
    r'[ \t]+'
    pass

# Newline handling
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    with open("lexer_module/lexer_output.txt", "w") as f:
        f.write(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def tokenize(source_code, output_file="lexer_output.txt"):
    lexer.input(source_code)  # Pass the source code to the lexer
    tokens = []  # List to store the tokens  

    with open(output_file, "w") as f:  # Open the output file in write mode
        while True:
            tok = lexer.token()  # Get the next token
            if not tok:
                break
            # Write the token to the file
            f.write(f"{tok.type}, Value: {tok.value}, Line: {tok.lineno}\n")
            tokens.append(tok)
    return tokens