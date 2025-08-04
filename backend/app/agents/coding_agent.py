import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.schemas import ChatMessage, CodeArtifact, MessageRole
from app.services.artifact_service import ArtifactService
from app.services.gemini_service import GeminiService
from app.services.memory_service import MemoryService


class CodingAgent:
    """LangGraph-based coding agent for handling user interactions"""

    def __init__(
        self,
        gemini_service: GeminiService,
        memory_service: MemoryService,
        artifact_service: ArtifactService,
    ):
        self.gemini_service = gemini_service
        self.memory_service = memory_service
        self.artifact_service = artifact_service

    async def stream_response(
        self, message: str, session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a message with streaming response"""
        try:
            # Ensure session exists
            self.memory_service.create_session(session_id)

            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=message,
                timestamp=datetime.now(timezone.utc),
            )

            # Add user message to memory
            self.memory_service.add_message(session_id, user_message)

            # Get conversation history
            conversation_history = self.memory_service.get_conversation_history(
                session_id, limit=10
            )

            # Generate message ID for streaming
            message_id = str(uuid.uuid4())
            accumulated_content = ""

            # Stream response from Gemini
            async for chunk in self.gemini_service.generate_streaming_response(
                prompt=message, conversation_history=conversation_history
            ):
                accumulated_content += chunk

                yield {
                    "chunk": chunk,
                    "message_id": message_id,
                    "session_id": session_id,
                    "is_complete": False,
                    "has_artifacts": False,
                    "artifacts": [],
                }

            # Create final AI message
            ai_message = ChatMessage(
                id=message_id,
                role=MessageRole.ASSISTANT,
                content=accumulated_content,
                timestamp=datetime.now(timezone.utc),
            )

            # Extract artifacts from complete response
            artifacts = self.artifact_service.extract_artifacts_from_response(
                response=accumulated_content,
                session_id=session_id,
                message_id=message_id,
            )

            # Update message metadata if artifacts found
            if artifacts:
                ai_message.metadata = {
                    "has_artifacts": True,
                    "artifacts": [artifact.id for artifact in artifacts],
                }

            # Add AI message to memory
            self.memory_service.add_message(session_id, ai_message)

            # Send final completion chunk
            yield {
                "chunk": "",
                "message_id": message_id,
                "session_id": session_id,
                "is_complete": True,
                "has_artifacts": len(artifacts) > 0,
                "artifacts": (
                    [artifact.id for artifact in artifacts] if artifacts else []
                ),
            }

        except Exception as e:
            traceback.print_exc()
            yield {
                "chunk": f"Error: {str(e)}",
                "message_id": str(uuid.uuid4()),
                "session_id": session_id,
                "is_complete": True,
                "has_artifacts": False,
                "artifacts": [],
                "error": True,
            }

    def get_session_artifacts(self, session_id: str) -> List[CodeArtifact]:
        """Get all artifacts for a session"""
        return self.artifact_service.get_artifacts_by_session(session_id)

    def get_artifact(self, artifact_id: str) -> Optional[CodeArtifact]:
        """Get a specific artifact"""
        return self.artifact_service.get_artifact(artifact_id)
