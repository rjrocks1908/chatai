import asyncio
from typing import Any, AsyncGenerator, Dict, List

import google.generativeai as genai
from app.config.settings import get_settings
from app.core.exceptions import GeminiAPIException
from app.schemas import ChatMessage, MessageRole


class GeminiService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.settings = get_settings()
        genai.configure(api_key=api_key)

        # Configure the model
        self.generation_config = {
            "temperature": self.settings.temperature,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": self.settings.max_tokens,
        }

        self.model = genai.GenerativeModel(
            model_name=self.settings.gemini_model,
            generation_config=self.generation_config,
        )

    def _prepare_history(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert ChatMessage objects to Gemini format"""
        history = []
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                role = "user" if msg.role == MessageRole.USER else "model"
                history.append({"role": role, "parts": [msg.content]})
        return history

    async def generate_streaming_response(
        self, prompt: str, conversation_history: List[ChatMessage] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from Gemini"""
        try:
            # Prepare conversation history
            history = []
            if conversation_history:
                history = self._prepare_history(conversation_history)

            # Start chat session
            chat = self.model.start_chat(history=history)

            # Generate streaming response
            response = await asyncio.to_thread(chat.send_message, prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise GeminiAPIException(f"Failed to generate streaming response: {str(e)}")
