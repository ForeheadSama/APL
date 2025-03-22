import ply.lex as lex

# Reserved words definition - updated to include data types and if statement keywords
reserved = {
    # Core Command Keywords
    'book': 'BOOK',
    'cancel': 'CANCEL',
    'list': 'LIST',
    'check': 'CHECK',
    'pay': 'PAY',
    'display': 'DISPLAY',
    'accept': 'ACCEPT',
    
    # Prepositions and Conjunctions
    'for': 'FOR',
    'on': 'ON',
    'event': 'EVENT',

    # Objects and Topics
    'ticket': 'TICKET',
    'tickets': 'TICKETS',
    'events': 'EVENTS',
    'availability': 'AVAILABILITY',
    'price': 'PRICE',
    
    # Data Types
    'string': 'STRING_TYPE',
    'int': 'INT_TYPE',
    'date': 'DATE_TYPE',
    
    # Control Flow
    'if': 'IF',
    'else': 'ELSE'
}

# Token list definition - updated to include new symbols and types
tokens = [
    'NUMBER',         # e.g., 123
    'STRING_LITERAL', # e.g., "Hello, World!"
    'DATE_VAL',       # e.g., "February 17, 2025"
    'IDENTIFIER',     # Variable names
    'DOT',            # . (end of sentence)
    'LPAREN',         # (
    'RPAREN',         # )
    'LBRACKET',       # [
    'RBRACKET',       # ]
    'EQUALS',         # =
    'GT',             # >
    'LT',             # <
    'GE',             # >=
    'LE',             # <=
    'EQ',             # ==
    'NE',             # !=
] + list(reserved.values())

# Simple token rules
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_GT = r'>'
t_LT = r'<'
t_GE = r'>='
t_LE = r'<='
t_EQ = r'=='
t_NE = r'!='
t_EQUALS = r'='

# Modified date rule
def t_DATE_VAL(t):
    r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|' \
    r'January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}' \
    r'|\d{1,2}/\d{1,2}/\d{4}'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\"\"\"(.|\n)*?\"\"\"|\"[^\"]*\"'
    t.value = t.value.strip('"')
    return t

# Identifier rule - must come after reserved keywords
def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')  # Case-insensitive matching
    return t

# Comment rules - updated to handle code blocks
def t_COMMENT(t):
    r'\$\$.*'
    t.lexer.lineno += t.value.count('\n')
    pass  # Token discarded

# Ignore Whitespace
t_ignore = ' \t'

# Newline handling
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling
errors = []
def t_error(t):
    error_msg = (
        f"[Lexical Error] Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}\n"
        "  • Why it’s an error: This character is not part of the valid syntax.\n"
        "  • Suggestion: Check for typos, misplaced punctuation, or unsupported characters."
    )
    errors.append(error_msg)
    print(error_msg)
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def tokenize(source_code, output_file="lexer_output.txt"):
    """
    Tokenize the given source code and write the tokens to an output file.
    
    Args:
        source_code (str): The source code to tokenize
        output_file (str): Path to the output file where tokens will be written
    
    Returns:
        list: A list of the tokens found in the source code
    """
    lexer.input(source_code)
    tokens = []
    try:
        with open(output_file, "w") as f:
            while True:
                tok = lexer.token()
                if not tok:
                    break
                f.write(f"{tok.type}, Value: {tok.value}, Line: {tok.lineno}\n")
                tokens.append(tok)
    except IOError:
        print(f"Warning: Could not write to output file {output_file}")
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok)
    
    return tokens