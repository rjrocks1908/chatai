from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ArtifactType(str, Enum):
    CODE = "code"
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    REACT = "react"
    MARKDOWN = "markdown"
    JSON = "json"
    OTHER = "other"


class CodeArtifact(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    type: ArtifactType
    language: str
    content: str
    session_id: str
    message_id: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    is_runnable: bool = False
    preview_url: Optional[str] = None


class ArtifactRequest(BaseModel):
    session_id: str
    message_id: str


class ArtifactResponse(BaseModel):
    artifacts: list[CodeArtifact]
    total: int