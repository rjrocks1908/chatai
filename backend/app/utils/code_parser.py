import re
from typing import List, Dict, Optional


class CodeParser:
    """Utility class for parsing code blocks from text"""
    
    def __init__(self):
        # Regex patterns for different code block formats
        self.fenced_code_pattern = re.compile(
            r'```(\w+)?\n(.*?)```', 
            re.DOTALL | re.MULTILINE
        )
        
        self.inline_code_pattern = re.compile(
            r'`([^`]+)`'
        )
        
        # Language aliases mapping
        self.language_aliases = {
            'js': 'javascript',
            'jsx': 'javascript',
            'tsx': 'typescript',
            'ts': 'typescript',
            'py': 'python',
            'sh': 'bash',
            'yml': 'yaml',
            'htm': 'html'
        }
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract all code blocks from text"""
        code_blocks = []
        
        # Find fenced code blocks (```language ... ```)
        for match in self.fenced_code_pattern.finditer(text):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            # Normalize language
            language = self.normalize_language(language)
            
            if code:  # Only add non-empty code blocks
                code_blocks.append({
                    'language': language,
                    'code': code,
                    'type': 'fenced',
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return code_blocks
    
    def extract_inline_code(self, text: str) -> List[Dict[str, str]]:
        """Extract inline code snippets"""
        inline_codes = []
        
        for match in self.inline_code_pattern.finditer(text):
            code = match.group(1).strip()
            if code and len(code) > 3:  # Only meaningful inline code
                inline_codes.append({
                    'code': code,
                    'type': 'inline',
                    'start_pos': match.start(),
                    'end_pos': match.end()
                })
        
        return inline_codes
    
    def normalize_language(self, language: str) -> str:
        """Normalize language names using aliases"""
        language = language.lower().strip()
        return self.language_aliases.get(language, language)
    
    def detect_language_from_content(self, code: str) -> str:
        """Attempt to detect programming language from code content"""
        code = code.strip().lower()
        
        # Python indicators
        if any(keyword in code for keyword in ['def ', 'import ', 'from ', 'class ', 'if __name__']):
            return 'python'
        
        # JavaScript/React indicators
        if any(keyword in code for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'import react']):
            if 'react' in code or 'jsx' in code or '</' in code:
                return 'jsx'
            return 'javascript'
        
        # HTML indicators
        if any(keyword in code for keyword in ['<html', '<!doctype', '<div', '<p>', '<body']):
            return 'html'
        
        # CSS indicators
        if re.search(r'[.#]\w+\s*{.*}', code, re.DOTALL):
            return 'css'
        
        # JSON indicators
        if code.startswith('{') and code.endswith('}') and '"' in code:
            return 'json'
        
        # Shell/Bash indicators
        if any(keyword in code for keyword in ['#!/bin/', 'echo ', 'cd ', 'ls ', 'grep ']):
            return 'bash'
        
        return 'text'
    
    def is_complete_code(self, code: str, language: str) -> bool:
        """Check if code appears to be complete/runnable"""
        code = code.strip()
        
        if language == 'html':
            return '<html' in code.lower() and '</html>' in code.lower()
        
        elif language == 'python':
            # Check for basic structure
            return 'def ' in code or 'class ' in code or len(code.split('\n')) > 2
        
        elif language in ['javascript', 'jsx']:
            return 'function ' in code or '=>' in code or 'const ' in code
        
        elif language == 'css':
            return '{' in code and '}' in code
        
        return len(code) > 10  # Basic length check
    
    def extract_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements from code"""
        imports = []
        lines = code.split('\n')
        
        if language == 'python':
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
        
        elif language in ['javascript', 'jsx', 'typescript']:
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                    imports.append(line)
        
        return imports
    
    def extract_functions(self, code: str, language: str) -> List[Dict[str, str]]:
        """Extract function definitions from code"""
        functions = []
        
        if language == 'python':
            pattern = re.compile(r'def\s+(\w+)\s*\([^)]*\):', re.MULTILINE)
            for match in pattern.finditer(code):
                functions.append({
                    'name': match.group(1),
                    'language': language,
                    'type': 'function'
                })
        
        elif language in ['javascript', 'jsx']:
            # Function declarations
            pattern1 = re.compile(r'function\s+(\w+)\s*\(', re.MULTILINE)
            # Arrow functions
            pattern2 = re.compile(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', re.MULTILINE)
            
            for match in pattern1.finditer(code):
                functions.append({
                    'name': match.group(1),
                    'language': language,
                    'type': 'function'
                })
            
            for match in pattern2.finditer(code):
                functions.append({
                    'name': match.group(1),
                    'language': language,
                    'type': 'arrow_function'
                })
        
        return functions
    
    def clean_code(self, code: str) -> str:
        """Clean code by removing extra whitespace and normalizing"""
        lines = code.split('\n')
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        # Find minimum indentation (excluding empty lines)
        min_indent = float('inf')
        for line in lines:
            if line.strip():  # Skip empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        # Remove common indentation
        if min_indent != float('inf') and min_indent > 0:
            lines = [line[min_indent:] if line.strip() else line for line in lines]
        
        return '\n'.join(lines)