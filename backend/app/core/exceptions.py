from fastapi import HTTPException
from typing import Optional, Dict, Any


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class GeminiAPIException(APIException):
    def __init__(self, detail: str = "Gemini API error occurred"):
        super().__init__(status_code=503, detail=detail)


class MemoryException(APIException):
    def __init__(self, detail: str = "Memory operation failed"):
        super().__init__(status_code=500, detail=detail)


class ArtifactException(APIException):
    def __init__(self, detail: str = "Artifact processing failed"):
        super().__init__(status_code=422, detail=detail)


class SessionNotFoundException(APIException):
    def __init__(self, session_id: str):
        super().__init__(
            status_code=404,
            detail=f"Session {session_id} not found"
        )


class InvalidRequestException(APIException):
    def __init__(self, detail: str = "Invalid request"):
        super().__init__(status_code=400, detail=detail)