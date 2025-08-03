from fastapi import APIRouter
from app.api.v1.endpoints import chat, artifacts

api_router = APIRouter()

# Include chat endpoints
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

# Include artifact endpoints  
api_router.include_router(
    artifacts.router,
    prefix="/artifacts",
    tags=["artifacts"]
)