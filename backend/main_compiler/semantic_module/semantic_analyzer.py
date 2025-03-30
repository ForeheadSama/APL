import os
import json
from typing import List, Dict, Any, Union

class SemanticAnalyzer:
    def __init__(self, ast: Union[Dict[str, Any], List[Dict[str, Any]], str]):
        """
        Initialize semantic analyzer with type-safe checks
        
        Args:
            ast: Can be either:
                - A dictionary node
                - A list of nodes
                - A string (for error cases)
        """
        self.ast = ast
        self.symbol_table: Dict[str, str] = {}  # Maps variable names to types
        self.errors: List[str] = []
        self.output: List[Dict[str, Any]] = []

    def analyze(self) -> List[str]:
        """Main analysis entry point with proper type handling"""
        try:
            self._traverse(self.ast)
            self._save_output()
            self._save_errors()
            return self.errors
        except Exception as e:
            error = f"Critical analysis error: {str(e)}"
            self.errors.append(error)
            return [error]

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

    def _validate_node(self, node):
        """Ensure node is properly structured"""
        if not isinstance(node, dict):
            self.errors.append(f"Invalid node type: {type(node)}. Expected dict")
            return False
        if 'type' not in node:
            self.errors.append("Node missing 'type' attribute")
            return False
        return True

    def _traverse(self, node: Union[Dict[str, Any], List[Any], str, None]) -> None:
        if node is None:
            return
        elif isinstance(node, str):
            self.errors.append(f"Unexpected string node: {node}")
        elif isinstance(node, list):
            for item in node:
                self._traverse(item)
        elif isinstance(node, dict):
            self._process_node(node)
        else:
            self.errors.append(f"Unexpected node type: {type(node)}")

    def _process_node(self, node: Dict[str, Any]) -> None:
        """Process a single AST node with full type safety"""

        if not isinstance(node.get('type'), str):
            self.errors.append("Node missing string 'type'")
            return

        node_type = node['type']
        lineno = node.get('lineno', 'unknown')

        try:
            if node_type == 'program':
                self._traverse(node.get('statements', []))
            elif node_type == 'book_command':
                self._check_book_command(node)
            elif node_type == 'cancel_command':
                self._check_cancel_command(node)
            elif node_type == 'list_command':
                self._check_list_command(node)
            elif node_type == 'check_command':
                self._check_check_command(node)
            elif node_type == 'pay_command':
                self._check_pay_command(node)
            elif node_type == 'display_command':
                self._check_display_command(node)
            elif node_type == 'accept_command':
                self._check_accept_command(node)
            elif node_type == 'declaration':
                self._check_declaration(node)
            elif node_type == 'if_statement':
                self._check_if_statement(node)
            elif node_type == 'condition':
                self._check_condition(node)
            elif node_type == 'expression':
                self._check_expression(node)
            else:
                self.errors.append(f"Unknown node type: {node_type} at line {lineno}")
        except Exception as e:
            self.errors.append(f"Error processing {node_type} at line {lineno}: {str(e)}")

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

    def _check_book_command(self, node: Dict[str, Any]) -> None:
        """Type-safe book command validation"""

        required = {'quantity', 'customer', 'date', 'event'}
        if not all(field in node for field in required):
            missing = required - set(node.keys())
            self.errors.append(f"Book command missing fields: {missing}")
            return

        self._validate_expression(node['quantity'], 'quantity', node.get('lineno'))
        self._validate_expression(node['customer'], 'customer', node.get('lineno'))
        self._validate_expression(node['date'], 'date', node.get('lineno'))
        self._validate_expression(node['event'], 'event', node.get('lineno'))

        if not any(e.startswith("Book command") for e in self.errors):
            self.output.append({
                'type': 'book_command',
                'quantity': self._resolve_variable(node['quantity']),
                'customer': self._resolve_variable(node['customer']),
                'date': self._resolve_variable(node['date']),
                'event': self._resolve_variable(node['event']),
                'lineno': node.get('lineno')
            })

    def _validate_expression(self, expr: Any, context: str, lineno: Union[int, str]) -> bool:
        """Validate any expression with type checking"""
        if not isinstance(expr, dict) or 'type' not in expr:
            self.errors.append(f"Invalid {context} at line {lineno}: expected expression node")
            return False

        if expr['type'] == 'variable':
            var_name = expr.get('name')
            if not isinstance(var_name, str) or var_name not in self.symbol_table:
                self.errors.append(f"Undeclared variable in {context} at line {lineno}")
                return False

        return True

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
        """Safe variable resolution"""
        if not isinstance(node, dict) or node.get('type') != 'variable':
            return node
            
        var_name = node.get('name')

        if var_name in self.symbol_table:
            for item in self.output:

                if item.get('type') == 'declaration' and item.get('var_name') == var_name:
                    return {
                        'type': 'literal',
                        'value': item.get('value'),
                        'lit_type': self.symbol_table[var_name],
                        'lineno': node.get('lineno')
                    }
        return node