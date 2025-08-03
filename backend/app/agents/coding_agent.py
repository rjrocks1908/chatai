import uuid
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.schemas import ChatMessage, MessageRole
from app.schemas import MemoryState
from app.schemas import CodeArtifact
from app.services.gemini_service import GeminiService
from app.services.memory_service import MemoryService
from app.services.artifact_service import ArtifactService
from app.agents.prompts import (
    get_system_prompt,
    get_coding_prompt,
    get_code_generation_prompt,
)
from app.core.exceptions import APIException


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
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Define the state structure
        workflow = StateGraph(MemoryState)

        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("extract_artifacts", self._extract_artifacts)
        workflow.add_node("update_memory", self._update_memory)

        # Define the flow
        workflow.set_entry_point("analyze_request")
        workflow.add_edge("analyze_request", "generate_response")
        workflow.add_edge("generate_response", "extract_artifacts")
        workflow.add_edge("extract_artifacts", "update_memory")
        workflow.add_edge("update_memory", END)

        return workflow.compile()

    async def _analyze_request(self, state: MemoryState) -> Dict[str, Any]:
        """Analyze the user's request to determine the type of response needed"""
        current_message = (
            state.conversation_history[-1] if state.conversation_history else None
        )

        if not current_message or current_message.role != MessageRole.USER:
            state.current_context["analysis"] = {
                "request_type": "general",
                "is_code_request": False,
                "language": "unknown",
                "complexity": "low",
            }
            return state.dict()

        # Analyze the request using Gemini
        try:
            analysis = await self.gemini_service.analyze_code_request(
                current_message.content
            )
            state.current_context["analysis"] = analysis
            state.current_context["original_request"] = current_message.content

        except Exception as e:
            # Fallback analysis
            state.current_context["analysis"] = {
                "request_type": "general",
                "is_code_request": False,
                "language": "unknown",
                "complexity": "medium",
                "error": str(e),
            }

        return state.dict()

    async def _generate_response(self, state: MemoryState) -> Dict[str, Any]:
        """Generate AI response based on the analyzed request"""
        analysis = state.current_context.get("analysis", {})
        session_id = state.session_metadata.get("session_id", "unknown")

        # Prepare conversation history for Gemini
        conversation_history = []

        # Add system message
        system_msg = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.SYSTEM,
            content=get_system_prompt(),
            timestamp=datetime.utcnow(),
        )
        conversation_history.append(system_msg)

        # Add recent conversation history (limit to last 10 messages)
        recent_messages = (
            state.conversation_history[-10:] if state.conversation_history else []
        )
        conversation_history.extend(recent_messages)

        # Get the current user message
        current_request = state.current_context.get("original_request", "")

        # Generate contextual prompt based on analysis
        if analysis.get("is_code_request", False):
            context_prompt = get_coding_prompt(
                session_id=session_id,
                message_count=len(state.conversation_history),
                artifact_count=len(state.artifacts_generated),
                user_message=current_request,
            )
        else:
            context_prompt = get_coding_prompt(
                session_id=session_id,
                message_count=len(state.conversation_history),
                artifact_count=len(state.artifacts_generated),
                user_message=current_request,
            )

        try:
            # Generate response
            response_content = await self.gemini_service.generate_response(
                prompt=context_prompt, conversation_history=conversation_history
            )

            # Create AI message
            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=response_content,
                timestamp=datetime.utcnow(),
                metadata={"analysis": analysis},
            )

            state.current_context["ai_response"] = ai_message
            state.current_context["response_generated"] = True

        except Exception as e:
            # Generate error response
            error_response = f"I apologize, but I encountered an error while generating a response: {str(e)}"

            ai_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=error_response,
                timestamp=datetime.utcnow(),
                metadata={"error": True, "error_message": str(e)},
            )

            state.current_context["ai_response"] = ai_message
            state.current_context["response_generated"] = False

        return state.dict()

    async def _extract_artifacts(self, state: MemoryState) -> Dict[str, Any]:
        """Extract code artifacts from the AI response"""
        ai_response = state.current_context.get("ai_response")
        session_id = state.session_metadata.get("session_id", "unknown")

        if not ai_response:
            return state.dict()

        try:
            # Extract artifacts from the response
            artifacts = self.artifact_service.extract_artifacts_from_response(
                response=ai_response.content,
                session_id=session_id,
                message_id=ai_response.id,
            )

            if artifacts:
                # Update AI message metadata
                ai_response.metadata = ai_response.metadata or {}
                ai_response.metadata["has_artifacts"] = True
                ai_response.metadata["artifacts"] = [
                    artifact.id for artifact in artifacts
                ]

                # Update state
                state.artifacts_generated.extend(
                    [artifact.id for artifact in artifacts]
                )
                state.current_context["extracted_artifacts"] = artifacts
                state.current_context["has_artifacts"] = True
            else:
                state.current_context["has_artifacts"] = False

        except Exception as e:
            state.current_context["artifact_extraction_error"] = str(e)
            state.current_context["has_artifacts"] = False

        return state.dict()

    async def _update_memory(self, state: MemoryState) -> Dict[str, Any]:
        """Update conversation memory with the new messages"""
        session_id = state.session_metadata.get("session_id", "unknown")
        ai_response = state.current_context.get("ai_response")

        if ai_response:
            try:
                # Add AI response to memory
                self.memory_service.add_message(session_id, ai_response)

                # Update conversation history in state
                state.conversation_history.append(ai_response)

                # Update session metadata
                state.session_metadata["last_updated"] = datetime.utcnow().isoformat()
                state.session_metadata["total_messages"] = len(
                    state.conversation_history
                )

            except Exception as e:
                state.current_context["memory_update_error"] = str(e)

        return state.dict()

    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process a user message through the LangGraph workflow"""
        try:
            # Ensure session exists
            self.memory_service.create_session(session_id)

            # Create user message
            user_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.USER,
                content=message,
                timestamp=datetime.utcnow(),
            )

            # Add user message to memory
            self.memory_service.add_message(session_id, user_message)

            # Get current memory state
            memory_state = self.memory_service.get_memory_state(session_id)

            # Process through the graph
            result = await self.graph.ainvoke(memory_state.dict())

            # Extract results
            ai_response = result.get("current_context", {}).get("ai_response")
            artifacts = result.get("current_context", {}).get("extracted_artifacts", [])

            return {
                "message_id": ai_response.id if ai_response else None,
                "content": (
                    ai_response.content if ai_response else "Error generating response"
                ),
                "session_id": session_id,
                "has_artifacts": len(artifacts) > 0,
                "artifacts": (
                    [artifact.id for artifact in artifacts] if artifacts else []
                ),
                "timestamp": (
                    ai_response.timestamp if ai_response else datetime.utcnow()
                ),
                "analysis": result.get("current_context", {}).get("analysis", {}),
            }

        except Exception as e:
            raise APIException(
                status_code=500, detail=f"Failed to process message: {str(e)}"
            )

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
                timestamp=datetime.utcnow(),
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
                timestamp=datetime.utcnow(),
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
