from app.agents.coding_agent import CodingAgent
from app.core.deps import get_coding_agent
from app.core.exceptions import InvalidRequestException
from app.schemas import ChatRequest, StreamChunk
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post("/stream")
async def chat_stream(
    request: ChatRequest, agent: CodingAgent = Depends(get_coding_agent)
):
    """Send a message to the coding agent with streaming response"""
    try:

        async def generate_stream():
            """Generate streaming response"""
            try:
                async for chunk_data in agent.stream_response(
                    message=request.message, session_id=request.session_id
                ):
                    chunk = StreamChunk(**chunk_data)
                    yield f"data: {chunk.model_dump_json()}\n\n"

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
