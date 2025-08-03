from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.schemas import ConversationMemory, MemoryState
from app.schemas import ChatMessage, MessageRole
from app.core.exceptions import MemoryException, SessionNotFoundException


class MemoryService:
    def __init__(self, max_conversations: int = 100):
        self.conversations: Dict[str, ConversationMemory] = {}
        self.max_conversations = max_conversations
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new conversation session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id in self.conversations:
            return session_id
        
        now = datetime.utcnow()
        self.conversations[session_id] = ConversationMemory(
            session_id=session_id,
            messages=[],
            created_at=now,
            updated_at=now
        )
        
        # Clean up old conversations if we exceed max
        if len(self.conversations) > self.max_conversations:
            self._cleanup_old_conversations()
        
        return session_id
    
    def get_session(self, session_id: str) -> ConversationMemory:
        """Get a conversation session"""
        if session_id not in self.conversations:
            raise SessionNotFoundException(session_id)
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to the conversation"""
        if session_id not in self.conversations:
            self.create_session(session_id)
        
        try:
            self.conversations[session_id].add_message(message)
        except Exception as e:
            raise MemoryException(f"Failed to add message: {str(e)}")
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get conversation history for a session"""
        if session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id].messages
        if limit:
            return messages[-limit:]
        return messages
    
    def get_memory_state(self, session_id: str) -> MemoryState:
        """Get the current memory state for LangGraph"""
        conversation = self.get_session(session_id)
        
        # Extract artifacts from conversation
        artifacts_generated = []
        for msg in conversation.messages:
            if msg.metadata and msg.metadata.get("has_artifacts"):
                artifacts_generated.extend(msg.metadata.get("artifacts", []))
        
        return MemoryState(
            conversation_history=conversation.messages,
            current_context=conversation.context,
            artifacts_generated=artifacts_generated,
            session_metadata={
                "session_id": session_id,
                "created_at": conversation.created_at.isoformat(),
                "message_count": len(conversation.messages)
            }
        )
    
    def update_context(self, session_id: str, context_update: Dict) -> None:
        """Update the conversation context"""
        if session_id not in self.conversations:
            self.create_session(session_id)
        
        self.conversations[session_id].context.update(context_update)
        self.conversations[session_id].updated_at = datetime.utcnow()
    
    def clear_session(self, session_id: str) -> None:
        """Clear a conversation session"""
        if session_id in self.conversations:
            self.conversations[session_id].clear()
    
    def delete_session(self, session_id: str) -> None:
        """Delete a conversation session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def _cleanup_old_conversations(self) -> None:
        """Remove oldest conversations to stay within limits"""
        if len(self.conversations) <= self.max_conversations:
            return
        
        # Sort by last updated time and keep the most recent ones
        sorted_sessions = sorted(
            self.conversations.items(),
            key=lambda x: x[1].updated_at,
            reverse=True
        )
        
        # Keep only the most recent conversations
        sessions_to_keep = dict(sorted_sessions[:self.max_conversations])
        self.conversations = sessions_to_keep
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs"""
        return list(self.conversations.keys())
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        if session_id not in self.conversations:
            raise SessionNotFoundException(session_id)
        
        conversation = self.conversations[session_id]
        user_messages = sum(1 for msg in conversation.messages if msg.role == MessageRole.USER)
        assistant_messages = sum(1 for msg in conversation.messages if msg.role == MessageRole.ASSISTANT)
        
        return {
            "session_id": session_id,
            "total_messages": len(conversation.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "context_keys": list(conversation.context.keys())
        }