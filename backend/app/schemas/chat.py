from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


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
    message: str
    session_id: str
    stream: bool = True


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
