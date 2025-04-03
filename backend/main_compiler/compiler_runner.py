# Compiler execution logic

import os
import sys
import subprocess
import threading

# Import required compiler modules
from backend.main_compiler.lexer_module.lexer import tokenize
from backend.main_compiler.parser_module.parser_mod import parse
from backend.main_compiler.semantic_module.semantic_analyzer import SemanticAnalyzer
from backend.main_compiler.intermediate_code_module.ir_generator import IntermediateCodeGenerator
from backend.main_compiler.code_generator_module.code_generator import CodeGenerator

class CompilerRunner:
    def __init__(self, text_editor, console_component, execution_insights, console_notebook):
        self.text_editor = text_editor
        self.console_component = console_component
        self.execution_insights = execution_insights
        self.console_notebook = console_notebook
    
    def get_llm_explanation(self, phase, code_snippet=None, context=None):
        """
        Get an explanation from the Gemini LLM API for the current execution step.
        
        Args:
            phase (str): Current compiler phase
            code_snippet (str, optional): Relevant code being processed
            context (dict, optional): Additional context information
            
        Returns:
            str: Explanation from the LLM
        """
        try:
            import google.generativeai as genai
            
            # Configure the API 
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

            # Create a prompt
            prompt = f"""
            Explain the following step in a compiler in a simple, educational way:
            
            Phase: {phase}
            """
            
            if code_snippet:
                prompt += f"""
                Code being processed:
                ```
                {code_snippet}
                ```
                """
                
            if context:
                prompt += f"""
                Additional context:
                {context}
                """
                
            prompt += """
            Keep your explanation concise (2-3 sentences) and focus on what's happening in this specific step.
            """
            
            # Make the API call
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
                
        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"
    
    def run_compiler(self):
        """Run the compiler on the code in the text editor."""
        # Start a new thread for the compilation process
        threading.Thread(target=self._run_compiler_thread).start()

    def _run_compiler_thread(self):
        """Thread target for running the compiler."""
        # Clear console and insights
        self.console_component.clear_console()
        self.execution_insights.clear_insights()
        
        # Show the Execution Insights tab
        self.console_notebook.select(1)
        
        # Get source code
        source_code = self.text_editor.get(1.0, "end")
        
        # Start compilation with enhanced insights
        self.execution_insights.add_phase_start("Compilation", 
            "Starting the compilation process for your APBL program.")
        
        # Run the lexical analysis phase
        self._run_lexical_analysis(source_code)
    
    def _run_lexical_analysis(self, source_code):
        """Run the lexical analysis phase of the compiler."""

        self.execution_insights.add_phase_start("Lexical Analysis", 
            self.get_llm_explanation("Lexical Analysis", source_code))
        
        try:
            tokens = tokenize(source_code, "backend/main_compiler/lexer_module/lexer_output.txt")

            
            # Get first few tokens for insight
            token_sample = str(tokens[:5]) if len(tokens) > 5 else str(tokens)
            self.execution_insights.add_phase_end("Lexical Analysis", 
                f"Successfully converted source code into {len(tokens)} tokens.\nFirst few tokens: {token_sample}")
            
            # Proceed to parsing phase
            self._run_parsing_phase(tokens)
            
        except Exception as e:

            self.execution_insights.add_insight("Lexical Analysis Error", 
                source_code, f"Error during tokenization: {e}")
    
    def _run_parsing_phase(self, tokens):
        """Run the parsing phase of the compiler."""

        self.execution_insights.add_phase_start("Parsing", 
            self.get_llm_explanation("Parsing", context=f"Working with {len(tokens)} tokens"))
        
        try:
            ast, symbol_table, syntax_errors = parse(tokens)
            
            if syntax_errors:
                
                # Display errors from files
                self._display_errors("backend/main_compiler/parser_module/parser_errors.txt", "Parser Errors")
                
                # Add to insights
                with open("backend/main_compiler/parser_module/parser_errors.txt", "r") as f:
                    error_content = f.read()
                self.execution_insights.add_insight("Parsing Errors", 
                    None, f"Syntax errors found during parsing:\n{error_content}")
                return
            else:

                self.execution_insights.add_phase_end("Parsing", 
                    "Successfully constructed the Abstract Syntax Tree (AST) and Symbol Table.")
                
                # Proceed to semantic analysis
                self._run_semantic_analysis(ast)
        
        except Exception as e:

            self.console_notebook.select(0)
            self.execution_insights.add_insight("Parsing Error", 
                None, f"Error during parsing: {e}")
    
    def _run_semantic_analysis(self, ast):
        """Run the semantic analysis phase of the compiler."""

        self.execution_insights.add_phase_start("Semantic Analysis", 
            self.get_llm_explanation("Semantic Analysis"))
        
        try:
            semantic_analyzer = SemanticAnalyzer(ast)
            semantic_errors = semantic_analyzer.analyze()
            
            if semantic_errors:
                
                # Display errors from files
                self._display_errors("backend/main_compiler/semantic_module/semantic_errors.txt", "Semantic Errors")
                
                # Add to insights
                with open("backend/main_compiler/semantic_module/semantic_errors.txt", "r") as f:
                    error_content = f.read()
                self.execution_insights.add_insight("Semantic Analysis Errors", 
                    None, f"Semantic errors found during analysis:\n{error_content}")
                return
            else:

                self.execution_insights.add_phase_end("Semantic Analysis", 
                    "Successfully verified program semantics. No type errors or scope issues found.")
                
                # Proceed to intermediate code generation
                self._run_intermediate_code_generation(ast)
        
        except Exception as e:

            self.console_notebook.select(0)
            self.execution_insights.add_insight("Semantic Analysis Error", 
                None, f"Error during semantic analysis: {e}")
            
    def _run_intermediate_code_generation(self, ast):
        """Run the intermediate code generation phase of the compiler."""

        self.execution_insights.add_phase_start("Intermediate Code Generation", 
            self.get_llm_explanation("Intermediate Code Generation"))
        
        try:
            code_generator = IntermediateCodeGenerator(ast)
            intermediate_code = code_generator.generate()

            self.execution_insights.add_phase_end("Intermediate Code Generation", 
                "Successfully generated intermediate representation of the program.")
            
            # Proceed to code generation
            self._run_code_generation()
        
        except Exception as e:
            self.execution_insights.add_insight("Intermediate Code Generation Error", 
                None, f"Error during intermediate code generation: {e}")
    
    def _run_code_generation(self):
        """Run the code generation phase of the compiler."""

        self.execution_insights.add_phase_start("Code Generation", 
            self.get_llm_explanation("Code Generation"))
        
        generator = CodeGenerator()
        success = generator.generate()
        if success:
            self.execution_insights.add_phase_end("Code Generation", 
                "Successfully generated Python code from the intermediate representation.")
            
            # Run the generated Python code
            self.execution_insights.add_phase_start("Execution", 
                self.get_llm_explanation("Execution"))
            self._run_generated_code()
        else:
            self.execution_insights.add_insight("Code Generation Error", 
                None, "Failed to generate Python code from the intermediate representation.")
    
    def _run_generated_code(self):
        """Run the generated Python code and display its output in the console."""
        generated_code_path = "backend/main_compiler/code_generator_module/generated_code.py"

        if os.path.exists(generated_code_path):
            try:
                # Get the generated code content for insights
                with open(generated_code_path, "r") as f:
                    generated_code = f.read()
                
                # Run the generated Python code and capture the output
                result = subprocess.run(
                    [sys.executable, generated_code_path],
                    capture_output=True,
                    text=True
                )
                
                # Switch to console tab to show the output
                self.console_notebook.select(0)
                
                # Display the output in the console
                if result.stdout:
                    self.console_component.print_to_console(result.stdout)
                    self.console_component.print_to_console("\n")
                
                if result.stderr:
                    
                    # Add to insights
                    self.execution_insights.add_insight("Execution Error", 
                        generated_code, f"Error during code execution:\n{result.stderr}")
                
                if not result.stdout and not result.stderr:
                    self.console_component.print_to_console("Program executed with no output.\n")
                
                self.console_component.print_to_console("=== Execution Complete ===\n", "success")
                
                # Complete the execution phase in insights
                output_summary = result.stdout if result.stdout else "No output generated."
                self.execution_insights.add_phase_end("Execution", 
                    f"Program execution completed successfully.\nOutput shown in Console tab.")
                
                # Add final compilation summary
                self.execution_insights.add_insight("Compilation Complete", 
                    None, "All compilation phases completed successfully. The program has been executed.")
                
                #self.execution_insights.add_phase_start()
                
            except Exception as e:
                self.execution_insights.add_insight("Execution Error", 
                    None, f"Error running generated code: {e}")
        else:
            self.execution_insights.add_insight("Execution Error", 
                None, f"Generated code file not found at {generated_code_path}.")
    
    def _display_errors(self, file_path, error_type):
        """Display errors from a file in the console."""
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                errors = file.read()
                if errors:
                    self.console_component.print_to_console(f"{error_type}:\n", "error")
                    self.console_component.print_to_console(errors, "error")
                    self.console_component.print_to_console("\n")