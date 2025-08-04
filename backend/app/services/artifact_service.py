import re
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from app.schemas import CodeArtifact, ArtifactType
from app.utils.code_parser import CodeParser
from app.core.exceptions import ArtifactException


class ArtifactService:
    def __init__(self):
        self.artifacts: Dict[str, CodeArtifact] = {}
        self.code_parser = CodeParser()

    def extract_artifacts_from_response(
        self, response: str, session_id: str, message_id: str
    ) -> List[CodeArtifact]:
        """Extract code artifacts from AI response"""
        try:
            # Parse code blocks from response
            code_blocks = self.code_parser.extract_code_blocks(response)
            artifacts = []

            for block in code_blocks:
                artifact = self._create_artifact_from_code_block(
                    block, session_id, message_id
                )
                if artifact:
                    artifacts.append(artifact)
                    self.artifacts[artifact.id] = artifact

            return artifacts

        except Exception as e:
            raise ArtifactException(f"Failed to extract artifacts: {str(e)}")

    def _create_artifact_from_code_block(
        self, code_block: Dict, session_id: str, message_id: str
    ) -> Optional[CodeArtifact]:
        """Create a CodeArtifact from a parsed code block"""
        try:
            language = code_block.get("language", "text").lower()
            content = code_block.get("code", "")

            if not content.strip():
                return None

            # Determine artifact type
            artifact_type = self._determine_artifact_type(language, content)

            # Generate title and description
            title = self._generate_title(language, content)
            description = self._generate_description(content, artifact_type)

            # Check if it's runnable
            is_runnable = self._is_runnable(artifact_type, content)

            artifact = CodeArtifact(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                type=artifact_type,
                language=language,
                content=content,
                session_id=session_id,
                message_id=message_id,
                created_at=datetime.utcnow(),
                is_runnable=is_runnable,
                metadata={
                    "lines_of_code": len(content.split("\n")),
                    "character_count": len(content),
                    "extracted_from_response": True,
                },
            )

            return artifact

        except Exception as e:
            print(f"Error creating artifact: {e}")
            return None

    def _determine_artifact_type(self, language: str, content: str) -> ArtifactType:
        """Determine the artifact type based on language and content"""
        language = language.lower()

        if language in ["html", "htm"]:
            return ArtifactType.HTML
        elif language in ["css"]:
            return ArtifactType.CSS
        elif language in ["javascript", "js"]:
            return ArtifactType.JAVASCRIPT
        elif language in ["python", "py"]:
            return ArtifactType.PYTHON
        elif language in ["jsx", "tsx"] or "react" in language.lower():
            return ArtifactType.REACT
        elif language in ["markdown", "md"]:
            return ArtifactType.MARKDOWN
        elif language in ["json"]:
            return ArtifactType.JSON
        else:
            # Check content for clues
            if "<html" in content.lower() or "<!doctype html" in content.lower():
                return ArtifactType.HTML
            elif "import React" in content or "from React" in content:
                return ArtifactType.REACT
            elif "def " in content or "import " in content:
                return ArtifactType.PYTHON
            elif "function " in content or "const " in content or "let " in content:
                return ArtifactType.JAVASCRIPT
            else:
                return ArtifactType.CODE

    def _generate_title(self, language: str, content: str) -> str:
        """Generate a title for the artifact"""
        # Try to extract title from comments or function names
        lines = content.split("\n")[:5]  # Check first 5 lines

        for line in lines:
            line = line.strip()
            # Check for comments with titles
            if line.startswith("#") or line.startswith("//") or line.startswith("/*"):
                clean_line = re.sub(r"^[#/\*\s]+", "", line).strip()
                if clean_line and len(clean_line) < 50:
                    return clean_line

            # Check for function names
            func_match = re.search(r"(function|def|class)\s+(\w+)", line)
            if func_match:
                return f"{func_match.group(2)} ({language})"

            # Check for React components
            react_match = re.search(r"const\s+(\w+)\s*=.*=>", line)
            if react_match:
                return f"{react_match.group(1)} Component"

        return f"{language.title()} Code"

    def _generate_description(self, content: str, artifact_type: ArtifactType) -> str:
        """Generate a description for the artifact"""
        lines = content.split("\n")
        line_count = len([line for line in lines if line.strip()])

        if artifact_type == ArtifactType.HTML:
            return f"HTML document with {line_count} lines"
        elif artifact_type == ArtifactType.REACT:
            return f"React component with {line_count} lines"
        elif artifact_type == ArtifactType.PYTHON:
            return f"Python code with {line_count} lines"
        elif artifact_type == ArtifactType.JAVASCRIPT:
            return f"JavaScript code with {line_count} lines"
        else:
            return f"Code artifact with {line_count} lines"

    def _is_runnable(self, artifact_type: ArtifactType, content: str) -> bool:
        """Determine if the artifact can be run/previewed"""
        runnable_types = [
            ArtifactType.HTML,
            ArtifactType.JAVASCRIPT,
            ArtifactType.REACT,
            ArtifactType.CSS,
        ]

        if artifact_type in runnable_types:
            return True

        # Check for complete HTML documents
        if "<html" in content.lower() and "</html>" in content.lower():
            return True

        return False

    def get_artifact(self, artifact_id: str) -> Optional[CodeArtifact]:
        """Get an artifact by ID"""
        return self.artifacts.get(artifact_id)

    def get_artifacts_by_session(self, session_id: str) -> List[CodeArtifact]:
        """Get all artifacts for a session"""
        return [
            artifact
            for artifact in self.artifacts.values()
            if artifact.session_id == session_id
        ]

    # def get_artifacts_by_message(self, message_id: str) -> List[CodeArtifact]:
    #     """Get all artifacts for a specific message"""
    #     return [
    #         artifact
    #         for artifact in self.artifacts.values()
    #         if artifact.message_id == message_id
    #     ]

    # def delete_artifact(self, artifact_id: str) -> bool:
    #     """Delete an artifact"""
    #     if artifact_id in self.artifacts:
    #         del self.artifacts[artifact_id]
    #         return True
    #     return False

    # def update_artifact(
    #     self, artifact_id: str, updates: Dict
    # ) -> Optional[CodeArtifact]:
    #     """Update an artifact"""
    #     if artifact_id not in self.artifacts:
    #         return None

    #     artifact = self.artifacts[artifact_id]
    #     for key, value in updates.items():
    #         if hasattr(artifact, key):
    #             setattr(artifact, key, value)

    #     return artifact

    # def get_artifact_stats(self) -> Dict:
    #     """Get statistics about artifacts"""
    #     if not self.artifacts:
    #         return {
    #             "total_artifacts": 0,
    #             "by_type": {},
    #             "by_language": {},
    #             "runnable_count": 0,
    #         }

    #     by_type = {}
    #     by_language = {}
    #     runnable_count = 0

    #     for artifact in self.artifacts.values():
    #         # Count by type
    #         type_name = artifact.type.value
    #         by_type[type_name] = by_type.get(type_name, 0) + 1

    #         # Count by language
    #         language = artifact.language
    #         by_language[language] = by_language.get(language, 0) + 1

    #         # Count runnable
    #         if artifact.is_runnable:
    #             runnable_count += 1

    #     return {
    #         "total_artifacts": len(self.artifacts),
    #         "by_type": by_type,
    #         "by_language": by_language,
    #         "runnable_count": runnable_count,
    #     }
