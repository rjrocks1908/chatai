import re
from typing import Dict, Any
from app.core.exceptions import InvalidRequestException


class InputValidator:
    """Utility class for validating user inputs"""

    @staticmethod
    def sanitize_message_content(content: str) -> str:
        """Sanitize message content"""
        if not content:
            return ""

        # Remove potentially harmful content
        content = content.strip()

        # Remove excessive whitespace
        content = re.sub(r"\s+", " ", content)

        # Remove control characters except newlines and tabs
        content = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", content)

        return content

    @staticmethod
    def validate_code_content(code: str, language: str) -> Dict[str, Any]:
        """Validate and analyze code content"""
        result = {"is_valid": True, "issues": [], "warnings": [], "metrics": {}}

        if not code or not isinstance(code, str):
            result["is_valid"] = False
            result["issues"].append("Code content is empty or invalid")
            return result

        # Basic metrics
        lines = code.split("\n")
        result["metrics"]["line_count"] = len(lines)
        result["metrics"]["character_count"] = len(code)
        result["metrics"]["non_empty_lines"] = len(
            [line for line in lines if line.strip()]
        )

        # Check for extremely long lines
        max_line_length = max(len(line) for line in lines) if lines else 0
        if max_line_length > 500:
            result["warnings"].append(
                f"Very long line detected ({max_line_length} characters)"
            )

        # Language-specific validation
        if language == "python":
            result.update(InputValidator._validate_python_code(code))
        elif language in ["javascript", "jsx"]:
            result.update(InputValidator._validate_javascript_code(code))
        elif language == "html":
            result.update(InputValidator._validate_html_code(code))

        return result

    @staticmethod
    def _validate_python_code(code: str) -> Dict[str, Any]:
        """Validate Python code"""
        issues = []
        warnings = []

        # Check for basic Python syntax patterns
        if "import os" in code and any(
            dangerous in code for dangerous in ["system(", "exec(", "eval("]
        ):
            warnings.append("Potentially dangerous system operations detected")

        # Check for proper indentation
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip() and line.startswith(" "):
                # Check if indentation is consistent (multiples of 2 or 4)
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 2 != 0:
                    warnings.append(f"Inconsistent indentation on line {i}")
                    break

        return {"issues": issues, "warnings": warnings}

    @staticmethod
    def _validate_javascript_code(code: str) -> Dict[str, Any]:
        """Validate JavaScript code"""
        issues = []
        warnings = []

        # Check for potentially dangerous patterns
        dangerous_patterns = ["eval(", "innerHTML =", "document.write("]
        for pattern in dangerous_patterns:
            if pattern in code:
                warnings.append(f"Potentially unsafe pattern detected: {pattern}")

        # Check for missing semicolons (basic check)
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if (
                line
                and not line.endswith((";", "{", "}", ")", "]"))
                and not line.startswith(
                    ("if", "for", "while", "function", "const", "let", "var", "//")
                )
            ):
                warnings.append(f"Possible missing semicolon on line {i}")
                break  # Only report first occurrence

        return {"issues": issues, "warnings": warnings}

    @staticmethod
    def _validate_html_code(code: str) -> Dict[str, Any]:
        """Validate HTML code"""
        issues = []
        warnings = []

        # Check for script tags with potentially dangerous content
        if "<script" in code.lower():
            if any(
                dangerous in code.lower()
                for dangerous in ["document.cookie", "eval(", "innerhtml"]
            ):
                warnings.append("Potentially unsafe JavaScript detected in HTML")

        # Basic HTML structure check
        if "<html" in code.lower() and "</html>" not in code.lower():
            issues.append("HTML document missing closing </html> tag")

        return {"issues": issues, "warnings": warnings}

    @staticmethod
    def validate_artifact_request(data: Dict[str, Any]) -> None:
        """Validate artifact request data"""
        required_fields = ["session_id", "message_id"]

        for field in required_fields:
            if field not in data:
                raise InvalidRequestException(f"Missing required field: {field}")

            if not data[field] or not isinstance(data[field], str):
                raise InvalidRequestException(f"Invalid {field}")

        # Validate session_id format
        if not InputValidator.validate_session_id(data["session_id"]):
            raise InvalidRequestException("Invalid session_id format")
