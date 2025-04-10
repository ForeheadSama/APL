import os
import re
from datetime import datetime
import requests
import json

import os
import re
from datetime import datetime
import requests
import json

class CodeGenerator:
    def __init__(self, intermediate_code_path="backend/main_compiler/intermediate_code_module/intermediate_code.txt",
                 output_path="backend/main_compiler/code_generator_module/generated_code.py",
                 error_path="backend/main_compiler/code_generator_module/code_generator_errors.txt"):
        
        self.intermediate_code_path = intermediate_code_path
        self.output_path = output_path
        self.error_path = error_path
        self.intermediate_code = []
        self.generated_code = [] 
        self.symbol_table = {}  # Store variable names and their types
        self.error_messages = []
        self.label_counter = 0  # Counter for generating unique labels
        self.control_flow_stack = []  # Stack to manage control flow blocks
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        os.makedirs(os.path.dirname(error_path), exist_ok=True)

    def generate(self):
        """Main method to generate code from intermediate representation"""
        try:
            self._read_intermediate_code()
            self._generate_header()
            self._process_intermediate_code()
            self._generate_footer()
            self._write_generated_code()
            return True
        except Exception as e:
            error_msg = f"Error during code generation: {str(e)}"
            self._log_error(error_msg)
            print(error_msg)
            return False

    def _read_intermediate_code(self):
        """Read the intermediate code from file"""
        try:
            with open(self.intermediate_code_path, 'r') as f:
                self.intermediate_code = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise Exception(f"Intermediate code file not found: {self.intermediate_code_path}")
        except Exception as e:
            raise Exception(f"Failed to read intermediate code: {str(e)}")

    def _generate_header(self):
        """Generate the header section of the Python code"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.generated_code.extend([
            "# Generated Python code",
            f"# Generated on: {current_time}",
            "# This file was automatically generated by the compiler's code generator",
            "",
            "import datetime",
            "import sys",
            "from dotenv import load_dotenv",
            "import json",
            "import os",
            "import re",
            "import requests",  # Add requests library for API calls
            "",
            "# Add the project root directory to sys.path",
            "sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))",
            "",
            "from backend.llm_integration.gemini_helper import get_and_format_events",  # Import the Gemini helper file
            "from backend.database.query import check_available_tickets, check_event_price, book_ticket, pay_booking, cancel_bookings",  # Import the database query functions",
            "",
            "# Helper functions for ticket system operations",
            "def check_availability(event_name, date):",
            "    available = check_available_tickets(event_name, date)",
            "    print(f\"Available tickets for event {event_name}: {available}\")",
            "    return available",
            "",
            "def check_price(event_name, date):",
            "    price = check_event_price(event_name, date)",
            "    if price:",
            "        print(f\"Price for event {event_name}: ${price:.2f}\")",
            "    else:",
            "        print(f\"Price information for event {event_name} not available.\")",
            "    return price",
            "",
            "def book_tickets(quantity, user_id, date, event_name):",
            "    success, bookMessage = book_ticket(quantity, user_id, date, event_name)",
            "    return success, bookMessage",
            "",
            "def pay_for_booking(event_name, user_name):",
            "    success, payMessage = pay_booking(event_name, user_name)",
            "    return success, payMessage",
            "",
            "def cancel_booking(quantity, user_name, event_name):",
            "    success, cancelMessage = cancel_bookings(quantity, user_name, event_name)",
            "    return success, cancelMessage",
            "",
           "def list_events_on_date(event_type: str, date_str: str) -> str:",
            "    try:",
            "        today = datetime.datetime.now().date()",
            "        date_obj = datetime.datetime.strptime(date_str, '%B %d, %Y').date()",
            "        if date_obj < today:",
            "            return \"Error: Cannot list events from the past\"",
            "        ",
            "        result = get_and_format_events(event_type=event_type, date=date_str)",
            "        return result",
            "    except ValueError:",
            "        return \"Error: Invalid date format. Use 'Month Day, Year'\"",
            "",
            "def list_event_details(event_name: str) -> str:",
            "    result = get_and_format_events(event_name=event_name)",
            "    return result if result else \"No events found\"",
            "",
            "# Main program starts here",
            "",
            ""
        ])

    def _process_intermediate_code(self):
        """Process each line of intermediate code and generate Python code with proper indentation."""
        indent_level = 0  # Track the current indentation level
        i = 0

        while i < len(self.intermediate_code):
            line = self.intermediate_code[i]

            try:
                # Handle indentation placeholders
                if line == "{INDENT}":
                    indent_level += 1  # Increase indentation level
                    i += 1
                    continue
                elif line == "{DEDENT}":
                    indent_level -= 1  # Decrease indentation level
                    i += 1
                    continue

                # Add indentation to the current line
                indented_line = "    " * indent_level + line

                # Process the line based on its type
                if line.startswith("IF NOT"):
                    self._handle_if_not(indented_line)

                elif line.startswith("GOTO"):
                    self._handle_goto(indented_line)

                elif line.startswith("LABEL"):
                    self._handle_label(indented_line)

                elif line.startswith("DECLARE"):
                    self._handle_declaration(indented_line)

                elif line.startswith("CALL"):
                    self._handle_function_call(indented_line)

                elif line.startswith("DISPLAY"):
                    self._handle_display(indented_line)

                elif line.startswith("ACCEPT"):
                    self._handle_input(indented_line)

                elif "=" in line and not line.startswith(("IF", "DECLARE")):
                    self._handle_assignment(indented_line)
                else:
                    self._log_error(f"Unknown intermediate code: {line}")
                    self.generated_code.append(f"# Unknown operation: {line}")

                i += 1
            except Exception as e:
                self._log_error(f"Error processing line '{line}': {str(e)}")
                self.generated_code.append(f"# Error processing: {line}")
                i += 1

    def _handle_if_not(self, line):
        """Handle IF NOT statements"""
        match = re.match(r"IF NOT\s+(.*)\s+GOTO\s+(L\d+)", line)
        if match:
            condition, label = match.groups()
            # Generate Python code for the if statement
            self.generated_code.append(f"if not {condition}:")
            self.generated_code.append("    " + f"# GOTO {label}")  # Indent the comment
            self.control_flow_stack.append(('if', label))
        else:
            self._log_error(f"Invalid IF NOT format: {line}")

    def _handle_goto(self, line):
        """Handle GOTO statements"""
        match = re.match(r"GOTO\s+(L\d+)", line)
        if match:
            label = match.groups()[0]
            # Generate Python code for the GOTO statement
            self.generated_code.append(f"    # GOTO {label}")  # Indent the comment
            self.control_flow_stack.append(('goto', label))
        else:
            self._log_error(f"Invalid GOTO format: {line}")

    def _handle_label(self, line):
        """Handle LABEL statements"""
        match = re.match(r"LABEL\s+(L\d+)", line)
        if match:
            label = match.groups()[0]
            # Generate Python code for the label
            self.generated_code.append(f"{label}:")  # Labels should not be indented
        else:
            self._log_error(f"Invalid LABEL format: {line}")

    def _handle_declaration(self, line):
        """Handle variable declarations"""
        match = re.match(r"DECLARE\s+(\w+)\s+AS\s+(\w+)\s+WITH VALUE\s+(.+)", line)
        if match:
            var_name, var_type, var_value = match.groups()
            self.symbol_table[var_name] = var_type.lower()

            # Generate Python code for the declaration
            if var_type.lower() == "int":
                self.generated_code.append(f"{var_name} = {var_value}  # Integer declaration")
            elif var_type.lower() == "string":
                self.generated_code.append(f"{var_name} = \"{var_value}\"  # String declaration")
            elif var_type.lower() == "date":
                self.generated_code.append(f"{var_name} = \"{var_value}\"  # Date declaration")
            else:
                self.generated_code.append(f"{var_name} = None  # {var_type} declaration")
        else:
            self._log_error(f"Invalid declaration format: {line}")

    from datetime import datetime

    def _handle_function_call(self, line):
        match = re.match(r"CALL\s+(\w+)\((.*)\)", line)
        if match:
            func_name, args_str = match.groups()
            
            # Parse arguments with comma handling
            processed_args = []
            in_quotes = False
            current_arg = ""
            i = 0
            
            while i < len(args_str):
                char = args_str[i]
                
                if char == '"' and (i == 0 or args_str[i-1] != '\\'):
                    in_quotes = not in_quotes
                    current_arg += char
                elif char == ',' and not in_quotes:
                    processed_args.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char
                
                i += 1
                    
            if current_arg.strip():
                processed_args.append(current_arg.strip())
            
            # Process arguments
            for j in range(len(processed_args)):
                arg = processed_args[j]
                if arg in self.symbol_table or re.match(r"t\d+", arg) or re.match(r"^\d+(\.\d+)?$", arg):
                    continue
                elif (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    continue
                else:
                    processed_args[j] = f'"{arg}"'
            
            # Generate proper code for each function
            if func_name == "list_events_on_date":
                if len(processed_args) == 2:
                    self.generated_code.append(f"result = list_events_on_date({processed_args[0]}, {processed_args[1]})")
                    self.generated_code.append("print(result)")
                else:
                    self._log_error(f"list_events_on_date requires 2 arguments (type, date), got {len(processed_args)}")
            
            elif func_name == "list_event_details":
                if len(processed_args) == 1:
                    self.generated_code.append(f"result = list_event_details({processed_args[0]})")
                    self.generated_code.append("print(result)")
                else:
                    self._log_error(f"list_event_details requires 1 argument (event_name), got {len(processed_args)}")
            
            # good
            elif func_name == "check_availability":
                if len(processed_args) == 2:  # Updated to require event_name and date
                    self.generated_code.append(f"available = check_availability({processed_args[0]}, {processed_args[1]})")
                else:
                    self._log_error(f"check_availability requires 2 arguments (event_name, date), got {len(processed_args)}")
            
            elif func_name == "check_price":
                if len(processed_args) == 2:  # Updated to require event_name and date
                    self.generated_code.append(f"price = check_price({processed_args[0]}, {processed_args[1]})")
                else:
                    self._log_error(f"check_price requires 2 arguments (event_name, date), got {len(processed_args)}")
            
            elif func_name == "book_tickets":
                if len(processed_args) == 4:  
                    quantity = processed_args[0]
                    user_name = processed_args[1] if processed_args[1].startswith('"') else f'"{processed_args[1]}"'
                    event_date = processed_args[2]
                    event_name = processed_args[3] if processed_args[2].startswith('"') else f'"{processed_args[2]}"'

                    self.generated_code.append(f"success, bookMessage = book_tickets({quantity}, {user_name}, {event_date}, {event_name})")
                    self.generated_code.append("print(bookMessage)")

            elif func_name == "pay_for_booking":
                if len(processed_args) == 2:
                    self.generated_code.append(f"success, payMessage = pay_for_booking({processed_args[0]}, {processed_args[1]})")
                    self.generated_code.append("print(payMessage)")
                else:
                    self._log_error(f"pay_for_booking requires 2 arguments (event_name, user_name), got {len(processed_args)}")

            elif func_name == "cancel_booking":
                if len(processed_args) == 3:
                    # Ensure proper quoting for string arguments
                    quantity = processed_args[0]
                    user_name = processed_args[1] if processed_args[1].startswith('"') else f'"{processed_args[1]}"'
                    event_name = processed_args[2] if processed_args[2].startswith('"') else f'"{processed_args[2]}"'
                    
                    self.generated_code.append(f"success, cancelMessage = cancel_booking({quantity}, {user_name}, {event_name})")
                    self.generated_code.append("print(cancelMessage)")
                else:
                    self._log_error(f"cancel_booking requires 3 arguments (quantity, user_name, event_name), got {len(processed_args)}")
            else:
                # Default handling for unrecognized functions
                self.generated_code.append(f"result = {func_name}({', '.join(processed_args)})")
                self.generated_code.append("if result is not None: print(result)") 
        else:
            self._log_error(f"Invalid function call format: {line}")
            
    def _handle_display(self, line):
        """Handle display/print statements"""
        match = re.match(r"DISPLAY\s+(.*)", line)
        if match:
            message = match.groups()[0]
            self.generated_code.append(f"\nprint('{message}')")
        else:
            self._log_error(f"Invalid display format: {line}")

    def _handle_input(self, line):
        """Handle input statements"""
        match = re.match(r"ACCEPT\s+INPUT\s+INTO\s+(\w+)", line)
        if match:
            var_name = match.groups()[0]
            self.generated_code.append(f"{var_name} = input(\"Enter value for {var_name}: \")")
        else:
            self._log_error(f"Invalid input format: {line}")

    def _handle_assignment(self, line):
        """Handle assignment operations"""
        parts = line.split('=', 1)
        if len(parts) == 2:
            left, right = parts[0].strip(), parts[1].strip()
            self.generated_code.append(f"{left} = {right}")
        else:
            self._log_error(f"Invalid assignment format: {line}")

    def _generate_footer(self):
        """Generate the footer section of the Python code"""
        self.generated_code.extend([
            "",
            "# By Alex-Ann Burrell :P",  
            "# == End of generated code == ",
        ])

    def _write_generated_code(self):
        """Write the generated code to the output file"""
        try:
            with open(self.output_path, 'w') as f:
                f.write('\n'.join(self.generated_code))
        except Exception as e:
            raise Exception(f"Failed to write generated code: {str(e)}")

    def _log_error(self, message):
        """Log an error message to the error file and console"""
        self.error_messages.append(message)
        try:
            with open(self.error_path, 'a') as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Failed to write to error log: {str(e)}")
        print(message)