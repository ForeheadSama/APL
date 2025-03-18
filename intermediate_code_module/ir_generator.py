# ir_generator.py
# generates intermediate code, saves to file

class IntermediateCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.intermediate_code = []  # List to store intermediate code
        self.temp_counter = 0  # Counter for generating temporary variables

    def generate(self):
        """
        Generate intermediate code from the AST.
        """
        self._traverse_ast(self.ast)
        self._save_to_file(self.intermediate_code)
        return self.intermediate_code

    def _save_to_file(self, intermediate_code):
        """
        Save the intermediate code to a file.
        """
        with open("intermediate_code_module/intermediate_code.txt", 'w') as f:
            # Join the list items with newlines before writing to file
            f.write('\n'.join(intermediate_code) + '\n')

    def _traverse_ast(self, node):
        """
        Recursively traverse the AST and generate intermediate code.
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
                self._generate_declaration(node)
            elif node.get('type') == 'if_statement':
                self._generate_if_statement(node)
            elif node.get('type') == 'book_command':
                self._generate_book_command(node)
            elif node.get('type') == 'cancel_command':
                self._generate_cancel_command(node)
            elif node.get('type') == 'list_command':
                self._generate_list_command(node)
            elif node.get('type') == 'check_command':
                self._generate_check_command(node)
            elif node.get('type') == 'pay_command':
                self._generate_pay_command(node)
            elif node.get('type') == 'display_command':
                self._generate_display_command(node)
            elif node.get('type') == 'accept_command':
                self._generate_accept_command(node)
            else:
                print(f"Warning: Unsupported node type '{node.get('type')}'")
        else:
            print(f"Warning: Invalid node '{node}'")

    def _generate_declaration(self, node):
        """
        Generate intermediate code for variable declarations.
        """
        var_name = node.get('var_name')
        var_type = node.get('var_type')
        var_value = node.get('value')
        self.intermediate_code.append(f"DECLARE {var_name} AS {var_type} WITH VALUE {var_value}")

    def _generate_if_statement(self, node):
        """
        Generate intermediate code for if statements.
        """
        condition = self._generate_expression(node.get('condition'))
        label_else = self._new_label()
        label_end = self._new_label()

        # Jump to else block if condition is false
        self.intermediate_code.append(f"IF NOT {condition} GOTO {label_else}")

        # Generate code for if body
        self._traverse_ast(node.get('if_body', []))

        # Jump to end of if statement
        self.intermediate_code.append(f"GOTO {label_end}")

        # Generate code for else body (if it exists)
        self.intermediate_code.append(f"LABEL {label_else}")
        if 'else_body' in node:
            self._traverse_ast(node.get('else_body', []))

        # End of if statement
        self.intermediate_code.append(f"LABEL {label_end}")

    def _generate_book_command(self, node):
        """
        Generate intermediate code for booking commands.
        """
        quantity = self._generate_expression(node.get('quantity'))
        customer = self._generate_expression(node.get('customer'))
        date = self._generate_expression(node.get('date'))
        event = self._generate_expression(node.get('event'))

        # Use a function call to represent the booking operation
        self.intermediate_code.append(f"CALL book_tickets({quantity}, {customer}, {date}, {event})")

    def _generate_cancel_command(self, node):
        """
        Generate intermediate code for cancellation commands.
        """
        event = self._generate_expression(node.get('event'))
        customer = self._generate_expression(node.get('customer'))

        # Use a function call to represent the cancellation operation
        self.intermediate_code.append(f"CALL cancel_tickets({customer}, {event})")

    def _generate_list_command(self, node):
        """
        Generate intermediate code for list commands.
        """
        if 'date' in node:
            date = self._generate_expression(node.get('date'))
            self.intermediate_code.append(f"CALL list_events_on_date({date})")
        elif 'event' in node:
            event = self._generate_expression(node.get('event'))
            self.intermediate_code.append(f"CALL list_event_details({event})")

    def _generate_check_command(self, node):
        """
        Generate intermediate code for check commands.
        """
        event = self._generate_expression(node.get('event'))
        date = self._generate_expression(node.get('date'))
        check_type = node.get('check_type')

        # Use a function call to represent the check operation
        self.intermediate_code.append(f"CALL check_{check_type}({event}, {date})")

    def _generate_pay_command(self, node):
        """
        Generate intermediate code for payment commands.
        """
        event = self._generate_expression(node.get('event'))
        customer = self._generate_expression(node.get('customer'))

        # Use a function call to represent the payment operation
        self.intermediate_code.append(f"CALL pay_for_event({event}, {customer})")

    def _generate_display_command(self, node):
        """
        Generate intermediate code for display commands.
        """
        message = self._generate_expression(node.get('message'))
        self.intermediate_code.append(f"DISPLAY {message}")

    def _generate_accept_command(self, node):
        """
        Generate intermediate code for accept commands.
        """
        var_name = node.get('variable')
        self.intermediate_code.append(f"ACCEPT INPUT INTO {var_name}")

    def _generate_expression(self, node):
        """
        Generate intermediate code for expressions.
        """
        if isinstance(node, dict):
            if node.get('type') == 'variable':
                return node.get('name')
            elif node.get('type') == 'literal':
                return node.get('value')
            elif node.get('type') == 'condition':
                left = self._generate_expression(node.get('left'))
                right = self._generate_expression(node.get('right'))
                operator = node.get('operator')
                temp = self._new_temp()
                self.intermediate_code.append(f"{temp} = {left} {operator} {right}")
                return temp
        return str(node)  # Fallback for unexpected node types

    def _new_temp(self):
        """
        Generate a new temporary variable.
        """
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def _new_label(self):
        """
        Generate a new label for control flow.
        """
        self.temp_counter += 1
        return f"L{self.temp_counter}"