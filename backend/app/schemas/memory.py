from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from .chat import ChatMessage


class ConversationMemory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    max_size: int = 50
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to memory and maintain size limit"""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        
        # Keep only the last max_size messages
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
    
    def get_recent_messages(self, count: int = 10) -> List[ChatMessage]:
        """Get the most recent messages"""
        return self.messages[-count:] if self.messages else []
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages = []
        self.context = {}
        self.updated_at = datetime.utcnow()


class MemoryState(BaseModel):
    conversation_history: List[ChatMessage] = []
    current_context: Dict[str, Any] = {}
    artifacts_generated: List[str] = []
    session_metadata: Dict[str, Any] = {}