# compiler.py
# Main driver for the APBL compiler

import os
import sys
from lexer_module.lexer import tokenize
from parser_module.parser_mod import parse

def compile_file(source_file):
    """Compile and execute an APBL source file"""
    
    print(f"\n*** Compiling {source_file}...")
    
    # Create necessary directories if they don't exist
    os.makedirs("lexer_module", exist_ok=True)
    os.makedirs("parser_module", exist_ok=True)
    
    # Read the source file
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
        return False
    except Exception as e:
        print(f"Error reading source file: {e}")
        return False
    
    # Lexical analysis
    try:
        tokens = tokenize(source_code, "lexer_module/lexer_output.txt")
        print("==> Lexical analysis completed.")
    except Exception as e:
        print(f"Lexical analysis failed: {e}")
        return False
    
    # Syntax analysis and parsing
    try:
        ast, syntax_errors = parse(tokens)
        
        # Write errors to a file for reference
        if syntax_errors:
            print(f"==> Syntax analysis completed with {len(syntax_errors)} errors. Errors written to parser_module/parser_output.txt")
            return False
        else:
            print("==> Syntax analysis completed successfully.")
        
        if ast is None:
            print("==> Syntax analysis failed: No AST was generated.")
            return False
        
    except Exception as e:
        print(f"==> Syntax analysis failed: {e}")
        return False
    
    # Successfully parsed, continue with your next step (interpretation, etc.)
    print("==> Program parsed successfully.")
    return True
    
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file>")
        return
    
    source_file = sys.argv[1]
    if not source_file.endswith('.apbl'):
        print("Warning: Source file does not have .apbl extension.")
    
    success = compile_file(source_file)
    if success:
        print("Compilation and execution successful!")
    else:
        print("Compilation or execution failed.")

if __name__ == "__main__":
    main()
