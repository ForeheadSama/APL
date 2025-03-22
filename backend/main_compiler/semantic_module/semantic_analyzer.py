import os
import json

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = {}  # Symbol table to track variables and their types
        self.errors = []  # List to store semantic errors
        self.output = []  # Store semantic output for saving to file

    def analyze(self):
        """
        Perform semantic analysis on the AST.
        """
        self._traverse_ast(self.ast)
        self._save_output()  # Save semantic output to file
        self._save_errors()  # Save semantic errors to file
        return self.errors

    def _save_output(self):
        """
        Save semantic output to a JSON file.
        """
        output_file = "backend/main_compiler/semantic_module/semantic_output.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure directory exists
        with open(output_file, "w") as f:
            json.dump(self.output, f, indent=4)

    def _save_errors(self):
        """
        Save semantic errors to a text file.
        """
        errors_file = "backend/main_compiler/semantic_module/semantic_errors.txt"
        os.makedirs(os.path.dirname(errors_file), exist_ok=True)  # Ensure directory exists
        with open(errors_file, "w") as f:
            for error in self.errors:
                f.write(error + "\n")

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
            elif node.get('type') == 'expression':
                self._check_expression(node)
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
        value = node.get('value')
        
        if var_name in self.symbol_table:
            self.errors.append(f"Error: Variable '{var_name}' already declared.")
        else:
            self.symbol_table[var_name] = var_type
            self.output.append({"type": "declaration", "var_name": var_name, "var_type": var_type, "value": value})

    def _check_if_statement(self, node):
        """
        Validate if statements.
        """
        condition = node.get('condition')

        if not self._is_valid_condition(condition):
            self.errors.append(f"Error: Invalid condition in if statement: {condition}.")
        self._traverse_ast(node.get('if_body', []))

        if 'else_body' in node:
            self._traverse_ast(node.get('else_body', []))

    def _is_valid_condition(self, condition):
        """
        Check if a condition is valid (e.g., it is a comparison or logical expression).
        Also ensure that any variables in the condition are declared.
        """
        if isinstance(condition, dict):
            if condition.get('type') == 'condition':
                left = condition.get('left')
                right = condition.get('right')
                
                # Check if left and right are valid expressions
                left_valid = self._is_valid_expression(left)
                right_valid = self._is_valid_expression(right)
                
                # Ensure both sides are valid and of the same type
                if left_valid and right_valid:
                    left_type = self._get_expression_type(left)
                    right_type = self._get_expression_type(right)
                    return left_type == right_type
                else:
                    return False
            elif condition.get('type') == 'expression':
                return self._is_valid_expression(condition)
        return False

    def _is_valid_expression(self, expr):
        """
        Check if an expression is valid and ensure that any variables are declared.
        """
        if isinstance(expr, dict):
            if expr.get('type') == 'variable':
                var_name = expr.get('name')
                if var_name not in self.symbol_table:
                    self.errors.append(f"Error: Variable '{var_name}' used in condition but not declared.")
                    return False
                return True
            elif expr.get('type') == 'literal':
                return True
            elif expr.get('type') == 'binary_operation':
                left_valid = self._is_valid_expression(expr.get('left'))
                right_valid = self._is_valid_expression(expr.get('right'))
                return left_valid and right_valid
        return False

    def _check_condition(self, node):
        """
        Validate condition expressions.
        """
        left_type = self._get_expression_type(node.get('left'))
        right_type = self._get_expression_type(node.get('right'))
        if left_type != right_type:
            self.errors.append(f"Type mismatch in condition: {left_type} != {right_type}")

    def _check_expression(self, node):
        """
        Validate expressions and perform type checking.
        """
        if node.get('type') == 'variable':
            var_name = node.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' not declared.")
        elif node.get('type') == 'literal':
            pass  # Literals are always valid
        elif node.get('type') == 'binary_operation':
            left_type = self._get_expression_type(node.get('left'))
            right_type = self._get_expression_type(node.get('right'))
            if left_type != right_type:
                self.errors.append(f"Type mismatch in binary operation: {left_type} != {right_type}")

    def _get_expression_type(self, expr):
        """
        Determine the type of an expression.
        """
        if isinstance(expr, dict):
            if expr.get('type') == 'variable':
                return self.symbol_table.get(expr.get('name'), 'unknown')
            elif expr.get('type') == 'literal':
                return expr.get('lit_type')
            elif expr.get('type') == 'binary_operation':
                left_type = self._get_expression_type(expr.get('left'))
                right_type = self._get_expression_type(expr.get('right'))
                if left_type == right_type:
                    return left_type
                else:
                    return "unknown"
        return "unknown"

    def _check_book_command(self, node):
        """
        Validate booking commands and resolve variable.
        """
        quantity = node.get('quantity')
        customer = node.get('customer')
        date = node.get('date')
        event = node.get('event')

        # Resolve variables if possible
        resolved_quantity = self._resolve_variable(quantity)
        resolved_customer = self._resolve_variable(customer)
        resolved_date = self._resolve_variable(date)
        resolved_event = self._resolve_variable(event)

        # Validate quantity (can be a literal or variable)
        if quantity.get('type') == 'variable':
            var_name = quantity.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in book command but not declared.")

        # Validate customer (can be a literal or variable)
        if customer.get('type') == 'variable':
            var_name = customer.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in book command but not declared.")

        # Validate date (can be a literal or variable)
        if date.get('type') == 'variable':
            var_name = date.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in book command but not declared.")

        # Validate event (can be a literal or variable)
        if event.get('type') == 'variable':
            var_name = event.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in book command but not declared.")

        self.output.append({
        "type": "book_command", 
        "quantity": resolved_quantity, 
        "customer": resolved_customer, 
        "date": resolved_date, 
        "event": resolved_event
    })

    def _check_cancel_command(self, node):
        """
        Validate cancellation commands.
        """
        customer = node.get('customer')
        event = node.get('event')

        # Resolve variables if possible
        resolved_customer = self._resolve_variable(customer)
        resolved_event = self._resolve_variable(event)

        # Validate customer (can be a literal or variable)
        if customer.get('type') == 'variable':
            var_name = customer.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in cancel command but not declared.")

        # Validate event (can be a literal or variable)
        if event.get('type') == 'variable':
            var_name = event.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in cancel command but not declared.")

        self.output.append({
            "type": "cancel_command", 
            "customer": resolved_customer, 
            "event": resolved_event
        })

    def _check_list_command(self, node):
        """
        Validate list commands.
        """
        date = node.get('date')  # Date can be None if not provided
        event = node.get('event')  # Event is mandatory

        # Resolve variables if possible
        resolved_date = self._resolve_variable(date)
        resolved_event = self._resolve_variable(event)

        # Validate event (can be a literal or variable)
        if event is None:
            self.errors.append("Error: 'event' is required in the list command.")
        else:
            if event.get('type') == 'variable':
                var_name = event.get('name')
                if var_name not in self.symbol_table:
                    self.errors.append(f"Error: Variable '{var_name}' used in list command but not declared.")

        # Validate date (can be a literal or variable, but optional)
        if date is not None:
            if date.get('type') == 'variable':
                var_name = date.get('name')
                if var_name not in self.symbol_table:
                    self.errors.append(f"Error: Variable '{var_name}' used in list command but not declared.")

        # Append the validated command to the output
        self.output.append({
            "type": "list_command",
            "date": resolved_date,
            "event": resolved_event
        })

    def _check_check_command(self, node):
        """
        Validate check commands.
        """
        check_type = node.get('check_type')
        event = node.get('event')
        date = node.get('date')

        # Resolve variables if possible
        resolved_check_type = self._resolve_variable(check_type)
        resolved_date = self._resolve_variable(date)
        resolved_event = self._resolve_variable(event)

        # Validate event (can be a literal or variable)
        if event.get('type') == 'variable':
            var_name = event.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in check command but not declared.")

        # Validate date (can be a literal or variable)
        if date.get('type') == 'variable':
            var_name = date.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in check command but not declared.")

        self.output.append({
            "type": "check_command", 
            "check_type": resolved_check_type, 
            "event": resolved_event, 
            "date": resolved_date
        })

    def _check_pay_command(self, node):
        """
        Validate payment commands.
        """
        event = node.get('event')
        customer = node.get('customer')

        # Resolve variables if possible
        resolved_customer = self._resolve_variable(customer)
        resolved_event = self._resolve_variable(event)

        # Validate event (can be a literal or variable)
        if event.get('type') == 'variable':
            var_name = event.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in pay command but not declared.")

        # Validate customer (can be a literal or variable)
        if customer.get('type') == 'variable':
            var_name = customer.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in pay command but not declared.")

        self.output.append({
            "type": "pay_command", 
            "event": resolved_event, 
            "customer": resolved_customer
        })

    def _check_display_command(self, node):
        """
        Validate display commands.
        """
        message = node.get('message')
        
        if isinstance(message, dict) and message.get('type') == 'variable':
            var_name = message.get('name')
            if var_name not in self.symbol_table:
                self.errors.append(f"Error: Variable '{var_name}' used in display command but not declared.")

        self.output.append({
            "type": "display_command", 
            "message": message
        })

    def _check_accept_command(self, node):
        """Validate accept commands."""
        var_name = node.get('variable')
        var_type = node.get('var_type', 'string')  # Get type or default to string
        

        if var_name not in self.symbol_table:
            # Add it to the symbol table
            self.symbol_table[var_name] = var_type
            warning = f"Implicit declaration of variable '{var_name}' with type '{var_type}'."
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

    def _resolve_variable(self, node):
        """
        Resolve a variable node to its actual value based on the symbol table.
        Returns either the resolved value or the original node if it can't be resolved.
        """
        if isinstance(node, dict) and node.get('type') == 'variable':
            var_name = node.get('name')
            # If variable exists in symbol table, return its value
            if var_name in self.symbol_table:
                # Find the value in declarations
                for item in self.output:
                    if item.get('type') == 'declaration' and item.get('var_name') == var_name:
                        # Create a new literal node with the variable's value
                        return {
                            'type': 'literal',
                            'value': item.get('value'),
                            'lit_type': self.symbol_table[var_name]
                        }
        # Return original node if we can't resolve
        return node