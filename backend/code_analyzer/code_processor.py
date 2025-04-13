import ast
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CodeProcessor:
    def __init__(self, max_chunk_size: int = 8000):
        # Using character count instead of tokens
        # 8000 chars is a reasonable approximation for Gemini models
        self.max_chunk_size = max_chunk_size

  
    def process_code_string(self, code_string: str, language: str = 'python') -> List[Dict[str, Any]]:
        """Process code received as a string directly (e.g., from frontend paste).
        
        This method is designed to be used when code is pasted in the frontend
        and sent to the backend as a string, without being saved as a file.
        
        Args:
            code_string: The code string to process
            language: The programming language of the code ('python' or 'javascript')
        """
        logger.info(f"Processing {language} code string of length {len(code_string)}")
        
        # Sanitize and chunk the code based on language
        sanitized_code = self.sanitize_code(code_string, language)
        
        if language.lower() == 'javascript':
            # Use language-specific chunking for JavaScript
            return self.chunk_javascript_code(sanitized_code)
        else:
            # Default to Python chunking for Python and other languages
            try:
                return self.chunk_python_code(sanitized_code)
            except Exception as e:
                logger.warning(f"Python AST parsing failed: {str(e)}. Falling back to simple chunking.")
                return self.chunk_code_simple(sanitized_code, language)

    def sanitize_code(self, code: str, language: str = 'python') -> str:
        """Sanitize code by removing unnecessary whitespace and comments based on language."""
        if language.lower() == 'javascript':
            # JavaScript-specific sanitization
            # Remove single-line comments
            code = re.sub(r'\/\/.*$', '', code, flags=re.MULTILINE)
            # Remove multi-line comments
            code = re.sub(r'\/\*[\s\S]*?\*\/', '', code, flags=re.DOTALL)
        else:
            # Python-specific sanitization
            # Remove single-line comments
            code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
            # Remove docstrings
            code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
            code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Common sanitization for all languages
        # Remove extra whitespace
        code = re.sub(r'\n\s*\n', '\n', code)
        return code.strip()

    def parse_ast(self, code: str) -> ast.AST:
        """Parse Python code into an AST."""
        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise Exception(f"Syntax error in Python code: {str(e)}")

    def get_node_context(self, node: ast.AST) -> Dict[str, Any]:
        """Extract context information from an AST node."""
        context = {
            'type': type(node).__name__,
            'lineno': getattr(node, 'lineno', None),
            'end_lineno': getattr(node, 'end_lineno', None),
        }
        
        if isinstance(node, ast.FunctionDef):
            context['name'] = node.name
            context['args'] = [arg.arg for arg in node.args.args]
            context['returns'] = ast.unparse(node.returns) if node.returns else None
        elif isinstance(node, ast.ClassDef):
            context['name'] = node.name
            context['bases'] = [ast.unparse(base) for base in node.bases]
        
        return context

    def chunk_python_code(self, code: str) -> List[Dict[str, Any]]:
        """Split Python code into logical chunks using AST parsing."""
        logger.info("Chunking Python code using AST")
        tree = self.parse_ast(code)
        chunks = []
        current_chunk = []
        current_size = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                node_code = ast.unparse(node)
                node_size = len(node_code)  # Using character count instead of token count
                
                if current_size + node_size > self.max_chunk_size and current_chunk:
                    chunks.append({
                        'code': '\n'.join(current_chunk),
                        'context': {
                            'file_name': 'unnamed_code.py',
                            'total_lines': len('\n'.join(current_chunk).split('\n')),
                            'language': 'python'
                        }
                    })
                    current_chunk = []
                    current_size = 0
                
                current_chunk.append(node_code)
                current_size += node_size

        if current_chunk:
            chunks.append({
                'code': '\n'.join(current_chunk),
                'context': {
                    'file_name': 'unnamed_code.py',
                    'total_lines': len('\n'.join(current_chunk).split('\n')),
                    'language': 'python'
                }
            })

        return chunks or [self.create_single_chunk(code, 'python')]

    def chunk_javascript_code(self, code: str) -> List[Dict[str, Any]]:
        """Chunk JavaScript code using regex patterns for functions and classes."""
        logger.info("Chunking JavaScript code using regex patterns")
        
        # Define regex patterns for JavaScript functions and classes
        function_pattern = r'(function\s+\w+\s*\([^)]*\)\s*\{[\s\S]*?\})'
        arrow_function_pattern = r'(const\s+\w+\s*=\s*(\([^)]*\)|[^=]+)\s*=>\s*(\{[\s\S]*?\}|[^;]+))'
        class_pattern = r'(class\s+\w+(\s+extends\s+\w+)?\s*\{[\s\S]*?\})'
        method_pattern = r'(\w+\s*\([^)]*\)\s*\{[\s\S]*?\})'
        
        # Combined pattern
        combined_pattern = f"{function_pattern}|{arrow_function_pattern}|{class_pattern}"
        
        # Find all blocks
        blocks = re.finditer(combined_pattern, code)
        chunks = []
        
        # Process each block
        for block in blocks:
            block_code = block.group(0)
            block_size = len(block_code)
            
            # If this block is bigger than max size, we could split it further
            # but for simplicity, we'll treat it as a single chunk
            chunks.append({
                'code': block_code,
                'context': {
                    'file_name': 'unnamed_code.js',
                    'total_lines': len(block_code.split('\n')),
                    'language': 'javascript'
                }
            })
        
        # If no chunks were found or recognition failed, treat whole code as one chunk
        return chunks or [self.create_single_chunk(code, 'javascript')]

    def chunk_code_simple(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Simple chunking strategy that splits code by size without caring about syntax."""
        logger.info(f"Using simple chunking for {language} code")
        
        # Determine appropriate extension
        file_ext = '.js' if language.lower() == 'javascript' else '.py'
        
        # Split into lines
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for the newline
            
            if current_size + line_size > self.max_chunk_size and current_chunk:
                chunk_code = '\n'.join(current_chunk)
                chunks.append({
                    'code': chunk_code,
                    'context': {
                        'file_name': f'unnamed_code{file_ext}',
                        'total_lines': len(current_chunk),
                        'language': language
                    }
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        if current_chunk:
            chunk_code = '\n'.join(current_chunk)
            chunks.append({
                'code': chunk_code,
                'context': {
                    'file_name': f'unnamed_code{file_ext}',
                    'total_lines': len(current_chunk),
                    'language': language
                }
            })
        
        return chunks

    def create_single_chunk(self, code: str, language: str) -> Dict[str, Any]:
        """Create a single chunk containing all code when other chunking methods fail."""
        file_ext = '.js' if language.lower() == 'javascript' else '.py'
        return {
            'code': code,
            'context': {
                'file_name': f'unnamed_code{file_ext}',
                'total_lines': len(code.split('\n')),
                'language': language
            }
        }

    # Legacy method name for backward compatibility
    def chunk_code(self, code: str) -> List[Dict[str, Any]]:
        """Legacy method that defaults to Python chunking."""
        logger.warning("Using legacy chunk_code method - consider updating to process_code_string")
        return self.chunk_python_code(code)