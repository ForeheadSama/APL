"""
CompilerService - Interface between Flask app and compiler execution
Facilitates the compilation process for the APBL language
"""

import os
import sys
import threading
import subprocess
from typing import Tuple, Dict, Any, List, Optional

# Import required compiler modules
from backend.main_compiler.lexer_module.lexer import tokenize
from backend.main_compiler.parser_module.parser_mod import parse
from backend.main_compiler.semantic_module.semantic_analyzer import SemanticAnalyzer
from backend.main_compiler.intermediate_code_module.ir_generator import IntermediateCodeGenerator
from backend.main_compiler.code_generator_module.code_generator import CodeGenerator

class CompilerService:
    """
    Service class to handle compilation requests from the Flask application.
    Manages the compilation pipeline and returns structured results.
    """
    
    def __init__(self):
        """Initialize the compiler service"""
        self.logger = self._setup_logger()
        self.logger.info("CompilerService initialized")
        
        # Status tracking variables
        self.current_phase = None
        self.explanations = []
        self.errors = []
        self.phase_results = []
        
    def _setup_logger(self):
        """Set up a logger for the compiler service"""
        import logging

        # suppress Matplotlib logs... mad annoying.
        logging.getLogger('matplotlib').disabled = True

        logger = logging.getLogger('CompilerService')

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        return logger
    
    def get_llm_explanation(self, phase: str, code_snippet: str = None, context: Dict = None) -> str:
        """
        Get an explanation from the Gemini LLM API for the current compilation phase.
        
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
            
            if not GEMINI_API_KEY:
                self.logger.warning("GEMINI_API_KEY not found in environment variables")
                return f"Explanation for {phase} not available (API key missing)"

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
            
            # Add to explanations list
            explanation = response.text
            self.explanations.append({
                'phase': phase,
                'content': explanation
            })
            
            return explanation
                
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return f"Unable to generate explanation for {phase}: {str(e)}"
    
    def compile(self, source_code: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute the full compilation pipeline on the provided source code.
        
        Args:
            source_code (str): Source code to compile
            
        Returns:
            tuple: (success: bool, results: dict)
        """
        self.logger.info("Starting compilation process")
        
        # Reset state for a new compilation
        self.current_phase = None
        self.explanations = []
        self.errors = []
        self.phase_results = []
        
        try:
            # Begin compilation process
            self._set_phase("Compilation", "Starting compilation process")
            
            # Run the lexical analysis phase
            success = self._run_lexical_analysis(source_code)
            if not success:
                return False, {'errors': self.errors, 'explanations': self.explanations}
            
            # Run the generated code
            exec_success, exec_results = self._run_generated_code()
            if not exec_success:
                return False, {'errors': self.errors}
            
            # Compilation was successful
            self.logger.info("Compilation completed successfully")
            return True, {
                'output': exec_results['output'],      # Program output
                'phases': self.phase_results,          # Phase completion status
                'explanations': self.explanations      # LLM insights
            }
            
        except Exception as e:
            self.logger.error(f"Compilation failed with exception: {str(e)}")
            self.errors.append(f"Compilation failed: {str(e)}")
            return False, {'errors': self.errors, 'explanations': self.explanations}
    
    def _set_phase(self, phase_name: str, description: str) -> None:
        """
        Update the current phase of compilation.
        
        Args:
            phase_name (str): Name of the current phase
            description (str): Description of the phase
        """
        self.current_phase = phase_name
        self.logger.info(f"Starting phase: {phase_name} - {description}")
        self.phase_results.append((phase_name, False))  # Add phase with initial failure status
    
    def _complete_phase(self, phase_name: str) -> None:
        """
        Mark the current phase as complete.
        
        Args:
            phase_name (str): Name of the completed phase
        """
        self.logger.info(f"Completed phase: {phase_name}")
        # Update phase status to success
        self.phase_results = [(p, True if p == phase_name else s) for p, s in self.phase_results]
    
    def _run_lexical_analysis(self, source_code: str) -> bool:
        """
        Run the lexical analysis phase of the compiler.
        
        Args:
            source_code (str): Source code to analyze
            
        Returns:
            bool: Success status
        """
        self._set_phase("Lexical Analysis", 
                       self.get_llm_explanation("Lexical Analysis", source_code))
        
        try:
            tokens = tokenize(source_code, "backend/main_compiler/lexer_module/lexer_output.txt")
            
            # Get first few tokens for logging
            token_sample = str(tokens[:5]) if len(tokens) > 5 else str(tokens)
            self.logger.info(f"Lexical analysis complete. Generated {len(tokens)} tokens. Sample: {token_sample}")
            
            self._complete_phase("Lexical Analysis")
            
            # Proceed to parsing phase
            return self._run_parsing_phase(tokens)
            
        except Exception as e:
            self.logger.error(f"Lexical analysis failed: {str(e)}")
            self.errors.append(f"Lexical Analysis Error: {str(e)}")
            return False
    
    def _run_parsing_phase(self, tokens: List) -> bool:
        """
        Run the parsing phase of the compiler.
        
        Args:
            tokens (list): Tokens from lexical analysis
            
        Returns:
            bool: Success status
        """
        self._set_phase("Parsing", 
                       self.get_llm_explanation("Parsing", context=f"Working with {len(tokens)} tokens"))
        
        try:
            ast, symbol_table, syntax_errors = parse(tokens)
            
            if syntax_errors:
                self.logger.error("Syntax errors found during parsing")
                
                # Read and add parser errors
                with open("backend/main_compiler/parser_module/parser_errors.txt", "r") as f:
                    error_content = f.read()
                    self.errors.append(f"Parser Errors: {error_content}")
                
                return False
            
            self.logger.info("Parsing complete. Generated AST and symbol table.")
            self._complete_phase("Parsing")
            
            # Proceed to semantic analysis
            return self._run_semantic_analysis(ast)
        
        except Exception as e:
            self.logger.error(f"Parsing failed: {str(e)}")
            self.errors.append(f"Parsing Error: {str(e)}")
            return False
    
    def _run_semantic_analysis(self, ast: Any) -> bool:
        """
        Run the semantic analysis phase of the compiler.
        
        Args:
            ast: Abstract Syntax Tree
            
        Returns:
            bool: Success status
        """
        self._set_phase("Semantic Analysis", 
                       self.get_llm_explanation("Semantic Analysis"))
        
        try:
            semantic_analyzer = SemanticAnalyzer(ast)
            semantic_errors = semantic_analyzer.analyze()
            
            if semantic_errors:
                self.logger.error("Semantic errors found during analysis")
                
                # Read and add semantic errors
                with open("backend/main_compiler/semantic_module/semantic_errors.txt", "r") as f:
                    error_content = f.read()
                    self.errors.append(f"Semantic Analysis Errors: {error_content}")
                
                return False
            
            self.logger.info("Semantic analysis complete. No errors found.")
            self._complete_phase("Semantic Analysis")
            
            # Proceed to intermediate code generation
            return self._run_intermediate_code_generation(ast)
        
        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {str(e)}")
            self.errors.append(f"Semantic Analysis Error: {str(e)}")
            return False
            
    def _run_intermediate_code_generation(self, ast: Any) -> bool:
        """
        Run the intermediate code generation phase of the compiler.
        
        Args:
            ast: Abstract Syntax Tree
            
        Returns:
            bool: Success status
        """
        self._set_phase("Intermediate Code Generation", 
                       self.get_llm_explanation("Intermediate Code Generation"))
        
        try:
            code_generator = IntermediateCodeGenerator(ast)
            intermediate_code = code_generator.generate()

            self.logger.info("Intermediate code generation complete.")
            self._complete_phase("Intermediate Code Generation")
            
            # Proceed to code generation
            return self._run_code_generation()
        
        except Exception as e:
            self.logger.error(f"Intermediate code generation failed: {str(e)}")
            self.errors.append(f"Intermediate Code Generation Error: {str(e)}")
            return False
    
    def _run_code_generation(self) -> bool:
        """
        Run the code generation phase of the compiler.
        
        Args:
            None
            
        Returns:
            bool: Success status
        """
        self._set_phase("Code Generation", 
                       self.get_llm_explanation("Code Generation"))
        
        try:
            generator = CodeGenerator()
            success = generator.generate()
            
            if not success:
                self.logger.error("Code generation failed")
                self.errors.append("Failed to generate Python code")
                return False

            self.logger.info("Code generation complete.")
            self._complete_phase("Code Generation")
            
            # Run the generated code
            return self._run_generated_code()
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {str(e)}")
            self.errors.append(f"Code Generation Error: {str(e)}")
            return False
    
    def _run_generated_code(self) -> Tuple[bool, Dict]:
        """
        Run the generated Python code and return results.
        
        Returns:
            tuple: (success: bool, results: dict)
        """
        self._set_phase("Execution", self.get_llm_explanation("Execution"))
        
        generated_code_path = "backend/main_compiler/code_generator_module/generated_code.py"

        if not os.path.exists(generated_code_path):
            error_msg = f"Generated code file not found at {generated_code_path}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False, {'output': '', 'error': error_msg}
            
        try:
            result = subprocess.run(
                [sys.executable, generated_code_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stderr:
                self.logger.error(f"Execution error: {result.stderr}")
                self.errors.append(f"Execution Error: {result.stderr}")
                return False, {
                    'output': result.stdout,
                    'error': result.stderr
                }
            
            self.logger.info("Execution successful")
            self._complete_phase("Execution")
            self._complete_phase("Compilation")
            
            return True, {
                'output': result.stdout,
                'error': None
            }
            
        except subprocess.TimeoutExpired:
            error_msg = "Execution timed out after 30 seconds"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False, {
                'output': '',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False, {
                'output': '',
                'error': error_msg
        }