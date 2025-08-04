from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from app.utils.validators import InputValidator
from pydantic import BaseModel, Field, field_validator


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: str
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str = Field(..., min_length=1, max_length=100)
    stream: bool = Field(default=True)

    @field_validator("message", mode="after")
    @classmethod
    def sanitize_message_content(cls, value: str) -> str:
        return InputValidator.sanitize_message_content(value)


class ChatResponse(BaseModel):
    message_id: str
    content: str
    session_id: str
    has_artifacts: bool = False
    artifacts: Optional[List[str]] = None
    timestamp: datetime


class StreamChunk(BaseModel):
    chunk: str
    message_id: str
    session_id: str
    is_complete: bool = False
    has_artifacts: bool = False
    artifacts: Optional[List[str]] = None


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
