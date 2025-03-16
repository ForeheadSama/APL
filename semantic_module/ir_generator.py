class IntermediateCodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.intermediate_code = []

    def generate(self):
        """
        Generate intermediate code from the AST.
        """
        self._traverse_ast(self.ast)
        return self.intermediate_code

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
        self.intermediate_code.append(f"DECLARE {var_name} AS {var_type}")

    def _generate_if_statement(self, node):
        """
        Generate intermediate code for if statements.
        """
        condition = self._generate_expression(node.get('condition'))
        self.intermediate_code.append(f"IF {condition} THEN")
        self._traverse_ast(node.get('if_body', []))  # Handle if_body as a list
        if 'else_body' in node:
            self.intermediate_code.append("ELSE")
            self._traverse_ast(node.get('else_body', []))  # Handle else_body as a list
        self.intermediate_code.append("ENDIF")

    def _generate_book_command(self, node):
        """
        Generate intermediate code for booking commands.
        """
        quantity = self._generate_expression(node.get('quantity'))
        customer = self._generate_expression(node.get('customer'))
        date = self._generate_expression(node.get('date'))
        event = self._generate_expression(node.get('event'))
        self.intermediate_code.append(f"BOOK {quantity} TICKETS FOR {customer} ON {date} FOR {event}")

    def _generate_cancel_command(self, node):
        """
        Generate intermediate code for cancellation commands.
        """
        event = self._generate_expression(node.get('event'))
        customer = self._generate_expression(node.get('customer'))
        self.intermediate_code.append(f"CANCEL TICKETS FOR {customer} FOR {event}")

    def _generate_list_command(self, node):
        """
        Generate intermediate code for list commands.
        """
        if 'date' in node:
            date = self._generate_expression(node.get('date'))
            self.intermediate_code.append(f"LIST EVENTS ON {date}")
        elif 'event' in node:
            event = self._generate_expression(node.get('event'))
            self.intermediate_code.append(f"LIST DETAILS FOR {event}")

    def _generate_check_command(self, node):
        """
        Generate intermediate code for check commands.
        """
        event = self._generate_expression(node.get('event'))
        date = self._generate_expression(node.get('date'))
        check_type = node.get('check_type')
        self.intermediate_code.append(f"CHECK {check_type} FOR {event} ON {date}")

    def _generate_pay_command(self, node):
        """
        Generate intermediate code for payment commands.
        """
        event = self._generate_expression(node.get('event'))
        customer = self._generate_expression(node.get('customer'))
        self.intermediate_code.append(f"PAY FOR {event} BY {customer}")

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
                return f"{left} {operator} {right}"
        return str(node)  # Fallback for unexpected node types