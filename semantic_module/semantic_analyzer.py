import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}  # fresh symbol table
        self.errors = []
        self.output = []  # Store semantic output for saving to file

        # Load API key from .env file
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("API key not found in .env file.")

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Use the correct model

    def analyze(self):
        """
        Perform semantic analysis on the AST.
        """
        self._traverse_ast(self.ast)
        self._save_output()  # Save semantic output to file
        return self.errors

    def _save_output(self):
        """
        Save semantic output to a JSON file.
        """
        output_file = "semantic_module/semantic_output.json"
        with open(output_file, "w") as f:
            json.dump(self.output, f, indent=4)
        print(f"Semantic output saved to {output_file}")

    def _traverse_ast(self, node):
        """
        Recursively traverse the AST and perform semantic checks.
        Handles both AST nodes and lists of nodes.
        """
        if isinstance(node, list):  # Handle lists of nodes
            for item in node:
                self._traverse_ast(item)
        elif isinstance(node, dict):  # Handle AST nodes (dictionaries)
            if node.get('type') == 'program':
                for statement in node.get('statements', []):
                    self._traverse_ast(statement)
            elif node.get('type') == 'declaration':
                self._check_declaration(node)
            elif node.get('type') == 'if_statement':
                self._check_if_statement(node)
            elif node.get('type') == 'book_command':
                self._check_book_command(node)
            elif node.get('type') == 'cancel_command':
                self._check_cancel_command(node)
            elif node.get('type') == 'list_command':
                self._check_list_command(node)
            elif node.get('type') == 'check_command':
                self._check_check_command(node)
            elif node.get('type') == 'pay_command':
                self._check_pay_command(node)
            elif node.get('type') == 'display_command':
                self._check_display_command(node)
            elif node.get('type') == 'accept_command':
                self._check_accept_command(node)
            elif node.get('type') == 'condition':
                self._check_condition(node)
            else:
                self.errors.append(f"Unsupported node type: {node.get('type')}")
        else:
            self.errors.append(f"Invalid node: {node}")

    def _check_declaration(self, node):
        """
        Validate variable declarations.
        """
        var_name = node.get('var_name')
        var_type = node.get('var_type')
        if var_name in self.symbol_table:
            self.errors.append(f"Error: Variable '{var_name}' already declared.")
        else:
            self.symbol_table[var_name] = var_type
            self.output.append({"type": "declaration", "var_name": var_name, "var_type": var_type})

    def _get_variable_value(self, var_name):
        """
        Retrieve a variable's value from the symbol table.
        For demonstration, we'll return a placeholder value based on the variable type.
        In a real system, you would retrieve the actual value.
        """
        if var_name not in self.symbol_table:
            return f"[{var_name}]"  # Placeholder if variable doesn't exist
        
        var_type = self.symbol_table[var_name]
        if var_type == "string":
            return f"[String value for {var_name}]"
        elif var_type == "int":
            return "[number]"
        elif var_type == "date":
            return "[YYYY-MM-DD]"
        else:
            return f"[Value of {var_name}]"

    def _check_book_command(self, node):
        """
        Validate booking commands and fetch real-time data from Gemini.
        """
        quantity = node.get('quantity')
        customer = node.get('customer')
        date = node.get('date')
        event = node.get('event')

        # Get real variable names (strings) instead of nodes
        quantity_name = quantity if isinstance(quantity, str) else None
        customer_name = customer if isinstance(customer, str) else None
        date_name = date if isinstance(date, str) else None
        event_name = event if isinstance(event, str) else None

        # Validate that variables exist in symbol table
        for var_name, label in [(quantity_name, "quantity"), (customer_name, "customer"), 
                               (date_name, "date"), (event_name, "event")]:
            if var_name and var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in book command but not declared.")
        
        # Format the details correctly with variable names
        details = node.get('details', "")
        
        # Add to output with correct formatting
        self.output.append({
            "type": "book_command", 
            "event": event_name, 
            "date": date_name, 
            "quantity": quantity_name, 
            "customer": customer_name,
            "details": details
        })

    def _check_cancel_command(self, node):
        """
        Validate cancellation commands.
        """
        event = node.get('event')
        customer = node.get('customer')

        # Get real variable names (strings) instead of nodes
        event_name = event if isinstance(event, str) else None
        customer_name = customer if isinstance(customer, str) else None

        # Validate that variables exist in symbol table
        for var_name, label in [(event_name, "event"), (customer_name, "customer")]:
            if var_name and var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in cancel command but not declared.")
        
        # Format the details with variable references preserved
        details = node.get('details', "")
        
        self.output.append({
            "type": "cancel_command", 
            "event": event_name, 
            "customer": customer_name, 
            "details": details
        })

    def _check_list_command(self, node):
        """
        Validate list commands and fetch real-time data from Gemini.
        """
        item_type = node.get('item_type')
        details = node.get('details', "")
        
        self.output.append({
            "type": "list_command", 
            "item_type": item_type, 
            "details": details
        })

    def _check_check_command(self, node):
        """
        Validate check commands and fetch real-time data from Gemini.
        """
        event = node.get('event')
        date = node.get('date')
        check_type = node.get('check_type')

        # Get real variable names (strings) instead of nodes
        event_name = event if isinstance(event, str) else None
        date_name = date if isinstance(date, str) else None

        # Validate that variables exist in symbol table
        for var_name, label in [(event_name, "event"), (date_name, "date")]:
            if var_name and var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in check command but not declared.")

        # Format details with variable references preserved
        details = node.get('details', "")
                
        self.output.append({
            "type": "check_command", 
            "check_type": check_type, 
            "event": event_name, 
            "date": date_name, 
            "details": details
        })

    def _check_pay_command(self, node):
        """
        Validate payment commands.
        """
        event = node.get('event')
        customer = node.get('customer')

        # Get real variable names (strings) instead of nodes
        event_name = event if isinstance(event, str) else None
        customer_name = customer if isinstance(customer, str) else None

        # Validate that variables exist in symbol table
        for var_name, label in [(event_name, "event"), (customer_name, "customer")]:
            if var_name and var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in pay command but not declared.")
        
        # Format details with variable references preserved
        details = node.get('details', "")
        
        self.output.append({
            "type": "pay_command", 
            "event": event_name, 
            "customer": customer_name, 
            "details": details
        })

    def _check_display_command(self, node):
        """
        Validate display commands.
        """
        message = node.get('message')
        
        # If message is a variable name, validate it exists
        if isinstance(message, str) and message in self.symbol_table:
            message_text = message  # Keep the variable name
        else:
            message_text = message  # Use the literal message
            
        self.output.append({"type": "display_command", "message": message_text})

    def _check_accept_command(self, node):
        """
        Validate accept commands.
        """
        var_name = node.get('variable')
        if var_name not in self.symbol_table:
            self.symbol_table[var_name] = 'string'  # Default to string type
            warning = f"Implicit declaration of variable '{var_name}'."
            self.output.append({
                "type": "accept_command", 
                "variable": var_name, 
                "warning": warning
            })
        else:
            self.output.append({
                "type": "accept_command", 
                "variable": var_name
            })

    def _check_if_statement(self, node):
        """
        Validate if statements.
        """
        self._traverse_ast(node.get('condition'))
        self._traverse_ast(node.get('if_body', []))  # Handle if_body as a list
        if 'else_body' in node:
            self._traverse_ast(node.get('else_body', []))  # Handle else_body as a list

    def _check_condition(self, node):
        """
        Validate condition expressions.
        """
        left = node.get('left')
        right = node.get('right')
        operator = node.get('operator')
        
        # If left/right are strings, they might be variable names
        if isinstance(left, str) and left not in self.symbol_table:
            self.errors.append(f"Error: Variable '{left}' used in condition but not declared.")
        
        if isinstance(right, str) and right not in self.symbol_table:
            self.errors.append(f"Error: Variable '{right}' used in condition but not declared.")
        
        # Add condition to output with the original values
        self.output.append({
            "type": "condition", 
            "left": left, 
            "operator": operator, 
            "right": right
        })
    
    def _node_to_string(self, node):
        """
        Extract meaningful information from node for output.
        This is kept for backward compatibility but modified to handle string inputs.
        """
        if isinstance(node, str):
            return node  # Return variable name directly if it's already a string
        
        if isinstance(node, dict):
            if node.get('type') == 'variable':
                return node.get('name')
            elif node.get('type') == 'literal':
                return node.get('value')
        
        return str(node)