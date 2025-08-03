from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json
import asyncio

from app.schemas import ChatRequest, ChatResponse, StreamChunk
from app.agents.coding_agent import CodingAgent
from app.core.deps import get_coding_agent
from app.utils.validators import InputValidator
from app.core.exceptions import InvalidRequestException, APIException

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, agent: CodingAgent = Depends(get_coding_agent)
) -> ChatResponse:
    """Send a message to the coding agent (non-streaming)"""
    try:
        # Validate request
        InputValidator.validate_chat_request(request.dict())

        # Sanitize input
        sanitized_message = InputValidator.sanitize_message_content(request.message)

        # Process message
        result = await agent.process_message(
            message=sanitized_message, session_id=request.session_id
        )

        return ChatResponse(
            message_id=result["message_id"],
            content=result["content"],
            session_id=result["session_id"],
            has_artifacts=result["has_artifacts"],
            artifacts=result["artifacts"],
            timestamp=result["timestamp"],
        )

    except InvalidRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except APIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest, agent: CodingAgent = Depends(get_coding_agent)
):
    """Send a message to the coding agent with streaming response"""
    try:
        # Validate request
        InputValidator.validate_chat_request(request.dict())

        # Sanitize input
        sanitized_message = InputValidator.sanitize_message_content(request.message)

        async def generate_stream():
            """Generate streaming response"""
            try:
                async for chunk_data in agent.stream_response(
                    message=sanitized_message, session_id=request.session_id
                ):
                    chunk = StreamChunk(**chunk_data)
                    yield f"data: {chunk.json()}\n\n"

                # Send end marker
                yield "data: [DONE]\n\n"

            except Exception as e:
                error_chunk = StreamChunk(
                    chunk=f"Error: {str(e)}",
                    message_id="error",
                    session_id=request.session_id,
                    is_complete=True,
                    has_artifacts=False,
                )
                yield f"data: {error_chunk.json()}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )

    except InvalidRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.websocket("/chat/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    agent: CodingAgent = Depends(get_coding_agent),
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        # Validate session ID
        if not InputValidator.validate_session_id(session_id):
            await websocket.send_json(
                {"type": "error", "message": "Invalid session ID"}
            )
            await websocket.close()
            return

        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                if data.get("type") != "message":
                    continue

                message = data.get("message", "")
                if not message:
                    await websocket.send_json(
                        {"type": "error", "message": "Empty message"}
                    )
                    continue

                # Validate and sanitize message
                if not InputValidator.validate_message_content(message):
                    await websocket.send_json(
                        {"type": "error", "message": "Invalid message content"}
                    )
                    continue

                sanitized_message = InputValidator.sanitize_message_content(message)

                # Send acknowledgment
                await websocket.send_json(
                    {"type": "message_received", "session_id": session_id}
                )

                # Stream response
                async for chunk_data in agent.stream_response(
                    message=sanitized_message, session_id=session_id
                ):
                    await websocket.send_json({"type": "stream_chunk", **chunk_data})

                # Send completion message
                await websocket.send_json(
                    {"type": "stream_complete", "session_id": session_id}
                )

            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Error processing message: {str(e)}"}
                )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json(
                {"type": "error", "message": f"WebSocket error: {str(e)}"}
            )
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str, limit: int = 50, agent: CodingAgent = Depends(get_coding_agent)
):
    """Get conversation history for a session"""
    try:
        # Validate session ID
        if not InputValidator.validate_session_id(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID")

        # Get conversation history
        history = agent.memory_service.get_conversation_history(session_id, limit=limit)

        return {
            "session_id": session_id,
            "messages": [msg.dict() for msg in history],
            "total": len(history),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.delete("/sessions/{session_id}")
async def clear_session(
    session_id: str, agent: CodingAgent = Depends(get_coding_agent)
):
    """Clear a conversation session"""
    try:
        # Validate session ID
        if not InputValidator.validate_session_id(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID")

        # Clear session
        agent.memory_service.clear_session(session_id)

        return {
            "message": f"Session {session_id} cleared successfully",
            "session_id": session_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to clear session: {str(e)}"
        )


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(
    session_id: str, agent: CodingAgent = Depends(get_coding_agent)
):
    """Get statistics for a session"""
    try:
        # Validate session ID
        if not InputValidator.validate_session_id(session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID")

        # Get session stats
        stats = agent.memory_service.get_session_stats(session_id)

        # Add artifact stats
        artifacts = agent.get_session_artifacts(session_id)
        stats["artifacts"] = {"total": len(artifacts), "by_type": {}, "by_language": {}}

        for artifact in artifacts:
            # Count by type
            type_name = artifact.type.value
            stats["artifacts"]["by_type"][type_name] = (
                stats["artifacts"]["by_type"].get(type_name, 0) + 1
            )

            # Count by language
            language = artifact.language
            stats["artifacts"]["by_language"][language] = (
                stats["artifacts"]["by_language"].get(language, 0) + 1
            )

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get session stats: {str(e)}"
        )
