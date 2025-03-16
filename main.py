#!/usr/bin/env python3
"""
Main module for the APL (Advanced Programming Language) compiler.
This script processes APL source files through the lexer and parser.
"""
import sys
import os

# Configure paths for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from lexer_module.lexer import tokenize
    from parser_module.parser_mod import parse
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure the lexer_module and parser_module directories are in the Python path")
    sys.exit(1)

def main():
    """
    Main function that processes the source code file.
    Reads the file, tokenizes it, and then parses the tokens.
    """
    # Check if a source file was provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    
    # Read the source file
    try:
        with open(source_file, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"\n===> Processing file: {source_file} <===")
    
    # Ensure output directories exist
    os.makedirs("lexer_module", exist_ok=True)
    
    # Tokenize the source code
    try:
        print("Tokenizing source code...")
        tokens = tokenize(source_code, "lexer_module/lexer_output.txt")
        print(f"Tokenization complete. Found {len(tokens)} tokens.")
    except Exception as e:
        print(f"Tokenization error: {e}")
        sys.exit(1)
    
    # Parse the tokens
    try:
        print("\nParsing tokens...")
        ast, errors = parse(tokens)
        if errors:
            print(f"Parsing completed with errors. Written to parser_module/parser_errors.txt")

        if not errors:
            print("Parsing completed successfully.")
            
        # Save AST to file
        with open("parser_module/parser_output.txt", "w") as f:
            f.write(str(ast))
            
        print(f"AST saved to parser_output.txt")
        
    except Exception as e:
        print(f"Parsing error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()