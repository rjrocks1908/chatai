from functools import lru_cache
from app.config.settings import get_settings, Settings
from app.services.gemini_service import GeminiService
from app.services.memory_service import MemoryService
from app.services.artifact_service import ArtifactService
from app.agents.coding_agent import CodingAgent


@lru_cache()
def get_gemini_service() -> GeminiService:
    settings = get_settings()
    return GeminiService(api_key=settings.google_api_key)


@lru_cache()
def get_memory_service() -> MemoryService:
    settings = get_settings()
    return MemoryService(max_conversations=settings.max_conversation_history)


@lru_cache()
def get_artifact_service() -> ArtifactService:
    return ArtifactService()


def get_coding_agent() -> CodingAgent:
    """Create a new coding agent instance for each request"""
    gemini_service = get_gemini_service()
    memory_service = get_memory_service()
    artifact_service = get_artifact_service()
    
    return CodingAgent(
        gemini_service=gemini_service,
        memory_service=memory_service,
        artifact_service=artifact_service
    )