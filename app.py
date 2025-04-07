"""
APBL - Unified Flask Application
Combines loader and IDE in a single Flask instance
"""

import os
import sys
import time
import socket
import threading
import queue
import importlib.util
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Import IDE components
from frontend.ide.modules.editor import EditorManager
from frontend.ide.modules.console import ConsoleManager
from frontend.ide.modules.insights import InsightsManager
from frontend.ide.modules.toolbar import ToolbarManager
from frontend.ide.modules.status_bar import StatusBarManager

# Set up the path to the backend directory
from backend.main_compiler.compiler_runner import CompilerService

# Configure logging
LOG_FILE = 'apbl_debug.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging configuration
logging.basicConfig(
    filename=os.path.join('logs', LOG_FILE),
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Suppress Matplotlib logs completely
logging.getLogger('matplotlib').disabled = True

flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.WARNING)  # Only show warnings and errors from Flask
flask_logger.propagate = False  # Prevent Flask logs from propagating to your root logger

# Create logger instance
logger = logging.getLogger('APBL')
logger.addHandler(logging.StreamHandler())  # Also log to console

class MainAPBL:
    def __init__(self):
        """Initialize the unified APBL application with Flask"""
        logger.info("Initializing APBL application")
        
        # Get the absolute path to the project directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Base directory: {self.base_dir}")
        
        # Configure paths - adjusted for new structure
        template_path = os.path.join(self.base_dir, 'templates')
        static_path = os.path.join(self.base_dir, 'static')
        logger.debug(f"Template path: {template_path}, Static path: {static_path}")
        
        # Create Flask app
        self.app = Flask(__name__,
                        template_folder=template_path,
                        static_folder=static_path)
        
        # Application state
        self.app_state = "loading"  # "loading" or "ide"
        self.current_file = None
        self.is_modified = False
        logger.debug("Application state initialized")
        
        # Threading components
        self.message_queue = queue.Queue()

        # Initialize compiler service
        self.compiler_service = CompilerService()
        self.current_status = {
            'message': 'Initializing...',
            'progress': 0,
            'error': None,
            'countdown': None
        }

        # Required file paths
        self.required_files = [
            'backend/main_compiler/parser_module/parser_errors.txt',
            'backend/main_compiler/parser_module/parser_output.json',
            'backend/main_compiler/parser_module/parser_warnings.txt',
            'backend/main_compiler/parser_module/visual_ast.png',
            'backend/main_compiler/parser_module/symbol_table.json',
            'backend/main_compiler/lexer_module/lexer_output.txt',
            'backend/main_compiler/semantic_module/semantic_errors.txt',
            'backend/main_compiler/intermediate_code_module/intermediate_code.txt',
            'backend/main_compiler/code_generator_module/code_generator_errors.txt'
        ]
        
        # Initialize startup thread
        self.startup_thread = threading.Thread(
            target=self.startup_process,
            daemon=True
        )
        logger.debug("Startup thread initialized")
        
        # Initialize IDE components
        self.editor = EditorManager()
        self.console = ConsoleManager()
        self.insights = InsightsManager()
        self.toolbar = ToolbarManager(self)
        self.status_bar = StatusBarManager()
        logger.info("IDE components initialized")
        
        # Configure routes
        # Loader routes
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/status', 'get_status', self.get_status, methods=['GET'])
        self.app.add_url_rule('/switch_to_ide', 'switch_to_ide', self.switch_to_ide, methods=['GET'])
        
        # IDE routes
        self.app.add_url_rule('/ide', 'ide', self.ide)
        self.app.add_url_rule('/editor/content', 'get_editor_content', 
                            self.editor.get_content, methods=['GET'])
        self.app.add_url_rule('/editor/content', 'update_editor_content', 
                            self.editor.update_content, methods=['POST'])
        self.app.add_url_rule('/console/output', 'get_console_output', 
                            self.console.get_output, methods=['GET'])
        self.app.add_url_rule('/console/output', 'add_console_output', 
                            self.console.add_output, methods=['POST'])
        self.app.add_url_rule('/insights/data', 'get_insights_data', 
                            self.insights.get_data, methods=['GET'])
        self.app.add_url_rule('/status_bar/update', 'update_status_bar',
                            self.status_bar.update, methods=['POST'])
        self.app.add_url_rule('/status_bar/get', 'get_status_bar',
                            self.status_bar.get_status, methods=['GET'])
        self.app.add_url_rule('/file/new', 'new_file', 
                            self.toolbar.new_file, methods=['POST'])
        self.app.add_url_rule('/file/open', 'open_file', 
                            self.toolbar.open_file, methods=['POST'])
        self.app.add_url_rule('/file/save', 'save_file', 
                            self.toolbar.save_file, methods=['POST'])
        self.app.add_url_rule('/compile', 'compile', 
                            self.compile, methods=['POST'])
        self.app.add_url_rule('/syntax_rules', 'syntax_rules', self.syntax_rules)

        
        logger.info("Routes configured")

        # Verify templates exist
        self.verify_templates()
        
    def verify_templates(self): 
        """Verify all required templates exist"""
        required_templates = {
            'loader': 'startup/loader.html',
            'ide': 'ide/base.html'
        }
        
        for name, path in required_templates.items():
            full_path = os.path.join(self.app.template_folder, path)
            if not os.path.exists(full_path):
                logger.error(f"Missing template: {name} at {full_path}")
                raise FileNotFoundError(f"Required template missing: {path}")
            else:
                logger.debug(f"Found template: {name} at {full_path}")

    def index(self):
        """Route handler for the root URL - shows loader or redirects to IDE"""
        logger.debug(f"Index route called, app_state: {self.app_state}")
        if self.app_state == "loading":
            return render_template('startup/loader.html')
        else:
            return redirect(url_for('ide'))
    
    def switch_to_ide(self):
        """API endpoint to switch the application state to IDE mode"""
        logger.info("Switching to IDE mode")
        self.app_state = "ide"
        # Ensure all required components are ready
        time.sleep(1)  # Small delay to ensure everything is initialized
        return jsonify({
            "status": "success", 
            "redirect": url_for('ide'),
            "state": "ready"
        })

    def get_status(self):
        """Endpoint for AJAX status updates during loading"""
        try:
            logger.debug("Processing status request")
            self.process_messages()
            
            # If loading is complete, indicate we're ready to switch to IDE
            if self.current_status.get('complete'):
                logger.info("Loading complete, redirecting to IDE")
                return jsonify({
                    'status': 'success',
                    'data': self.current_status,
                    'redirect': url_for('ide')
                })
            
            return jsonify({
                'status': 'success',
                'data': self.current_status
            })
        except Exception as e:
            logger.error(f"Error in get_status: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': str(e)
            })

    def ide(self):
        """Render the main IDE interface"""
        logger.debug(f"Ide route called, app_state: {self.app_state}")
        if self.app_state != "ide":
            logger.warning("Attempt to access IDE before loading complete")
            return redirect(url_for('index'))
        
        # Verify template exists
        template_path = os.path.join(self.app.template_folder, 'ide/base.html')
        if not os.path.exists(template_path):
            logger.error(f"IDE template not found at: {template_path}")
            return "IDE template missing", 500
            
        logger.debug("Rendering IDE template")
        return render_template('ide/base.html', 
                            current_file=self.current_file, 
                            is_modified=self.is_modified)

    def compile(self):
        """Handle compilation request from IDE"""
        try:
            logger.info("Compilation requested")
            # Get source code from editor
            source_code = request.json.get('content', '')
            logger.debug(f"Source code length: {len(source_code)} characters")
            
            # Start compilation in background thread
            threading.Thread(target=self._run_compilation, args=(source_code,)).start()
            logger.info("Compilation started in background thread")
            
            return jsonify({'status': 'started'})
        except Exception as e:
            logger.error(f"Error starting compilation: {str(e)}", exc_info=True)
            return jsonify({'status': 'error', 'message': str(e)})
    
    def syntax_rules(self):
        """Render the syntax rules documentation page"""
        return render_template('ide/syntax_rules.html')

    def _run_compilation(self, source_code):
        """Run compilation using CompilerService"""
        with self.app.app_context():
            try:
                logger.info("Starting compilation :D ")

                self.console.clear()
                self.insights.clear()

                # Call the compiler service (compiler_runner) to compile the source code
                success, results = self.compiler_service.compile(source_code)
                
                if not success:
                    # Handle errors
                    for error in results.get('errors', []):
                        self.console.add_output(f"{str(error)}\n", "error")
                    return
                
                # --- Handle successful output ---
                # Display the output in the console
                if 'output' in results and results['output']:
                    self.console.add_output(f"{results['output']}", "success")
                else:
                    self.console.add_output("Code executed with no output.", "normal")
                
                # Update insights with phase completion
                for phase_name, phase_success in results.get('phases', []):
                    self.insights.add_phase_end(
                        phase_name,
                        "Completed successfully" if phase_success else "Failed",
                        is_error=not phase_success
                    )
                
                # Add explanations to insights
                for explanation in results.get('explanations', []):
                    self.insights.add_insight(
                        explanation.get('phase', 'Compiler'),
                        None,  # No code snippet
                        explanation.get('content', 'No explanation available')
                    )
                
            except Exception as e:
                error_msg = f"Compilation pipeline failed: {str(e)}"
                logger.error(error_msg)
                self.console.add_output(error_msg, "error")

    def _handle_successful_compilation(self, results):
        """Update UI for successful compilation"""
        # Process phase results
        for phase_name, phase_success in results.get('phases', []):
            if phase_success:
                self.insights.add_phase_end(phase_name, "Completed successfully")
        
        # Add final success message
        logger.info("[COMPILATION SUCCESSFUL]\n")
        self.insights.add_phase_end("Compilation", "All phases completed")

    def _handle_failed_compilation(self, results):
        """Minimal error display"""
        for error in results.get('errors', []):
            self.console.add_output(f"{str(error)}\n", "error")

    def create_required_files(self):
        """Create all required files if they don't exist"""
        logger.info("Creating required files")
        for file_path in self.required_files:
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        f.write('')  # Create empty file
                    logger.debug(f"Created file: {file_path}")
            except Exception as e:
                logger.error(f"Error creating file {file_path}: {str(e)}", exc_info=True)
                raise

    def check_network_connectivity(self):
        """Check internet with 5 second timeout"""
        logger.debug("Checking network connectivity")
        try:
            socket.setdefaulttimeout(5)
            return any(
                socket.create_connection((host, port), timeout=5)
                for host, port in [
                    ("8.8.8.8", 53),
                    ("1.1.1.1", 53),
                    ("www.google.com", 80)
                ]
            )
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {str(e)}")
            return False

    def check_azure_connection(self):
        """Check DB connection with timeout"""
        logger.debug("Checking Azure database connection")
        try:
            # Use threading-based timeout instead of signal
            result_queue = queue.Queue()

            def db_check():
                try:
                    spec = importlib.util.spec_from_file_location(
                        "db_connection", 
                        "backend/database/connect.py"
                    )
                    db_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(db_module)
                    conn = db_module.get_db_connection()
                    conn.close()
                    result_queue.put(True)
                    logger.debug("Database connection successful")
                except Exception as e:
                    logger.error(f"Database connection failed: {str(e)}", exc_info=True)
                    result_queue.put(False)

            # Start the DB check in a thread
            check_thread = threading.Thread(target=db_check)
            check_thread.daemon = True
            check_thread.start()

            # Wait for 5 seconds
            check_thread.join(timeout=5)

            if check_thread.is_alive():
                logger.warning("Database connection timed out")
                return False

            # Check if we have a result
            try:
                return result_queue.get_nowait()
            except queue.Empty:
                logger.warning("Database check returned no result")
                return False

        except Exception as e:
            logger.error(f"DB check failed: {str(e)}", exc_info=True)
            return False

    def startup_process(self):
        """Background thread for startup checks"""
        try:
            logger.info("Beginning startup checks")
            
            # Network check
            self.queue_message(("status", "Checking network...", 25))
            logger.debug("Checking network connectivity")
            time.sleep(1)  # Short delay to show progress
            if not self.check_network_connectivity():
                error_msg = "Network connection failed"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # DB check
            self.queue_message(("status", "Checking database...", 50))
            logger.debug("Checking database connection")
            time.sleep(1)  # Short delay to show progress
            if not self.check_azure_connection():
                error_msg = "Database connection failed"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # File creation
            self.queue_message(("status", "Preparing files...", 75))
            logger.debug("Creating required files")
            time.sleep(1)  # Short delay to show progress
            self.create_required_files()
            
            # Completion - mark ready to transition to IDE
            self.queue_message(("status", "Starting IDE...", 100))
            logger.info("Startup checks completed successfully")
            time.sleep(1)  # Let user see 100% progress
            
            # Mark the app as ready for IDE mode
            self.app_state = "ide"
            self.queue_message(("complete", "Ready!", 100))
            logger.info("Application ready for IDE mode")
            
        except Exception as e:
            logger.critical(f"Startup process failed: {str(e)}", exc_info=True)
            self.queue_message(("error", str(e)))

    def queue_message(self, message):
        """Thread-safe message passing"""
        logger.debug(f"Queueing message: {message}")
        self.message_queue.put(message)

    def process_messages(self):
        """Handle messages from background thread"""
        try:
            while not self.message_queue.empty():
                msg_type, *content = self.message_queue.get_nowait()
                if msg_type == "status":
                    self.current_status = {
                        'message': content[0],
                        'progress': content[1],
                        'error': None
                    }
                    logger.debug(f"Status update: {content[0]} ({content[1]}%)")
                elif msg_type == "error":
                    self.current_status = {
                        'message': "Error",
                        'progress': 100,
                        'error': content[0]
                    }
                    logger.error(f"Error status: {content[0]}")
                elif msg_type == "complete":
                    self.current_status = {
                        'message': content[0],
                        'progress': 100,
                        'complete': True
                    }
                    logger.info(f"Completion status: {content[0]}")
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing messages: {str(e)}", exc_info=True)

    def run(self, port=5000):
        """Start the application"""
        try:
            logger.info(f"Starting APBL on port {port}")
            self.startup_thread.start()  # Start background thread
            logger.info("Startup thread started")
            
            # Open browser after short delay to ensure server is ready
            def open_browser():
                time.sleep(1)
                import webbrowser
                webbrowser.open_new(f'http://localhost:{port}')
                logger.debug("Browser opened")
            
            threading.Thread(target=open_browser).start()
            
            self.app.run(
                port=port,
                threaded=True,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            logger.critical(f"Failed to start application: {str(e)}", exc_info=True)
            raise

def create_app():
    """Factory function to create the unified APBL application"""
    logger.info("Creating APBL application instance")
    app = MainAPBL()
    return app

if __name__ == "__main__":
    try:
        apbl = MainAPBL()
        apbl.run()
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}", exc_info=True)
        raise