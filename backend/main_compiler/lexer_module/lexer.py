import ply.lex as lex
        
# RESERVED WORDS MAPPED TO THEIR TOKEN NAMES
# THESE INCLUDE COMMANDS, DATA TYPES, AND CONTROL FLOW KEYWORDS
reserved = {
    # CORE COMMAND KEYWORDS FOR BOOKING AND MANAGEMENT
    'book': 'BOOK',
    'cancel': 'CANCEL',
    'list': 'LIST',
    'check': 'CHECK',
    'pay': 'PAY',
    'display': 'DISPLAY',
    'accept': 'ACCEPT',
    
    # PREPOSITIONS AND CONJUNCTIONS USED IN QUERIES
    'for': 'FOR',
    'on': 'ON',
    'event': 'EVENT',

    # OBJECTS RELATED TO BOOKING
    'ticket': 'TICKET',
    'tickets': 'TICKETS',
    'availability': 'AVAILABILITY',
    'price': 'PRICE',
    
    # DATA TYPES SUPPORTED IN THE LANGUAGE
    'string': 'STRING_TYPE',
    'int': 'INT_TYPE',
    'date': 'DATE_TYPE',
    
    # CONTROL FLOW STATEMENTS
    'if': 'IF',
    'else': 'ELSE'
}

# LIST OF TOKENS INCLUDING RESERVED WORDS, SYMBOLS, AND LITERALS
tokens = [
    'NUMBER',         # INTEGER VALUES (E.G., 123)
    'STRING_LITERAL', # TEXT ENCLOSED IN DOUBLE QUOTES (E.G., "HELLO")
    'DATE_VAL',       # DATE VALUES IN A SPECIFIC FORMAT (E.G., "FEBRUARY 17, 2025")
    'IDENTIFIER',     # VARIABLE NAMES OR FUNCTION NAMES
    'DOT',            # PERIOD CHARACTER (.)
    'LPAREN',         # LEFT PARENTHESIS (
    'RPAREN',         # RIGHT PARENTHESIS )
    'LBRACKET',       # LEFT SQUARE BRACKET [
    'RBRACKET',       # RIGHT SQUARE BRACKET ]
    'EQUALS',         # ASSIGNMENT OPERATOR (=)
    'GT',             # GREATER THAN SYMBOL (>)
    'LT',             # LESS THAN SYMBOL (<)
    'GE',             # GREATER THAN OR EQUAL TO (>=)
    'LE',             # LESS THAN OR EQUAL TO (<=)
    'EQ',             # EQUALITY CHECK (==)
    'NE',             # NOT EQUAL (!=)
] + list(reserved.values()) # INCLUDE RESERVED WORDS IN THE TOKEN LIST

# REGULAR EXPRESSIONS FOR SIMPLE TOKEN RULES
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

# TOKEN RULE FOR DATE FORMATTED AS MONTH DAY, YEAR
def t_DATE_VAL(t):
    r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    return t

# TOKEN RULE FOR INTEGER VALUES
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  # CONVERT STRING TO INTEGER
    return t

# TOKEN RULE FOR STRING LITERALS ENCLOSED IN DOUBLE QUOTES
def t_STRING_LITERAL(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # REMOVE SURROUNDING QUOTES
    return t

# TOKEN RULE FOR IDENTIFIERS (VARIABLE NAMES)
def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')  # CHECK IF IDENTIFIER IS A RESERVED WORD
    return t

# TOKEN RULE FOR COMMENTS STARTING WITH $$ - IGNORED BY THE LEXER
def t_COMMENT(t):
    r'\$\$.*'
    t.lexer.lineno += t.value.count('\n')  # UPDATE LINE NUMBER COUNT
    pass  # DISCARD COMMENT TOKEN

# TOKEN RULE FOR WHITESPACE (IGNORED)
def t_WHITESPACE(t):
    r'[ \t]+'
    pass  # DISCARD WHITESPACE TOKEN

# TOKEN RULE FOR NEWLINES - UPDATES LINE NUMBER COUNTER
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # INCREMENT LINE COUNT

# ERROR HANDLING FOR ILLEGAL CHARACTERS
def t_error(t):
    print(f"- Error at line {t.lexer.lineno}: Illegal character '{t.value[0]}'")
    t.lexer.skip(1)  # SKIP THE INVALID CHARACTER

# BUILD THE LEXER
lexer = lex.lex()

# FUNCTION TO TOKENIZE SOURCE CODE AND WRITE TOKENS TO A FILE
def tokenize(source_code, output_file="backend/main_compiler/lexer_module/lexer_output.txt"):
    """
    TOKENIZES THE GIVEN SOURCE CODE AND WRITES THE TOKENS TO AN OUTPUT FILE.
    
    ARGS:
        SOURCE_CODE (STR): THE SOURCE CODE TO TOKENIZE
        OUTPUT_FILE (STR): PATH TO THE OUTPUT FILE WHERE TOKENS WILL BE WRITTEN
    
    RETURNS:
        LIST: A LIST OF THE TOKENS FOUND IN THE SOURCE CODE
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
