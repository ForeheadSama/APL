# parser_module/user_input_handler.py

class UserInputHandler:
    """
    Handler for user input processing in the DSL.
    This class provides utilities for handling various types of user input.
    """
    
    def __init__(self, symbol_table=None):
        """Initialize with a reference to the symbol table."""
        self.symbol_table = symbol_table or {}
        self.input_variables = {}  # Track variables that have received user input
    
    def set_symbol_table(self, symbol_table):
        """Update the symbol table reference."""
        self.symbol_table = symbol_table
    
    def register_input(self, var_name, var_type=None):
        """
        Register a variable as having received user input.
        
        Args:
            var_name (str): The name of the variable receiving input
            var_type (str, optional): The expected type of the input. Defaults to None.
        """
        # If no type is specified, use the type from the symbol table or default to string
        if var_type is None:
            var_type = self.symbol_table.get(var_name, 'string')
        
        self.input_variables[var_name] = var_type
        return var_type
    
    def attempt_type_conversion(self, var_name, input_value):
        """
        Attempt to convert user input to the expected type of the variable.
        
        Args:
            var_name (str): The name of the variable
            input_value (str): The raw input value to convert
            
        Returns:
            tuple: (converted_value, success_flag)
        """
        target_type = self.symbol_table.get(var_name, 'string')
        
        try:
            if target_type == 'int':
                # Attempt to convert to integer
                return int(input_value), True
            elif target_type == 'date':
                # For date, we would need more robust validation here
                # This is a simple placeholder
                if any(month in input_value for month in [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]):
                    return input_value, True
                return input_value, False
            else:  # Default to string
                return input_value, True
        except ValueError:
            return input_value, False
    
    def get_runtime_validation_code(self, var_name):
        """
        Generate code to validate user input at runtime.
        
        Args:
            var_name (str): The name of the variable to validate
            
        Returns:
            str: Code snippet for runtime validation
        """
        var_type = self.symbol_table.get(var_name, 'string')
        
        if var_type == 'int':
            return f"""
            try:
                {var_name} = int({var_name})
            except ValueError:
                print(f"Error: Input for '{var_name}' must be an integer.")
                # Handle error appropriately
            """
        elif var_type == 'date':
            return f"""
            # Simple date validation (would need more robust validation in practice)
            if not any(month in {var_name} for month in [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]):
                print(f"Error: Input for '{var_name}' must be a valid date.")
                # Handle error appropriately
            """
        else:
            return ""  # No validation needed for strings