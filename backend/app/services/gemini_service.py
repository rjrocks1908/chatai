import google.generativeai as genai
from typing import AsyncGenerator, List, Dict, Any
import asyncio
from app.core.exceptions import GeminiAPIException
from app.schemas import ChatMessage, MessageRole
from app.config.settings import get_settings


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
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name=self.settings.gemini_model,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def _prepare_history(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Convert ChatMessage objects to Gemini format"""
        history = []
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                role = "user" if msg.role == MessageRole.USER else "model"
                history.append({
                    "role": role,
                    "parts": [msg.content]
                })
        return history
    
    async def generate_response(
        self, 
        prompt: str, 
        conversation_history: List[ChatMessage] = None
    ) -> str:
        """Generate a complete response from Gemini"""
        try:
            # Prepare conversation history
            history = []
            if conversation_history:
                history = self._prepare_history(conversation_history)
            
            # Start chat session
            chat = self.model.start_chat(history=history)
            
            # Generate response
            response = await asyncio.to_thread(chat.send_message, prompt)
            
            return response.text
            
        except Exception as e:
            raise GeminiAPIException(f"Failed to generate response: {str(e)}")
    
    async def generate_streaming_response(
        self, 
        prompt: str, 
        conversation_history: List[ChatMessage] = None
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
            response = await asyncio.to_thread(
                chat.send_message, 
                prompt, 
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise GeminiAPIException(f"Failed to generate streaming response: {str(e)}")
    
    async def analyze_code_request(self, prompt: str) -> Dict[str, Any]:
        """Analyze if the user is requesting code generation"""
        analysis_prompt = f"""
        Analyze this user request and determine if they are asking for code generation.
        
        User request: "{prompt}"
        
        Respond with a JSON object containing:
        - "is_code_request": boolean
        - "language": string (if code is requested, what language/type)
        - "complexity": "simple" | "medium" | "complex"
        - "description": brief description of what they want
        
        Examples of code requests:
        - "Create a React component"
        - "Write a Python function"
        - "Build a web page"
        - "Make a calculator app"
        
        Examples of non-code requests:
        - "What is React?"
        - "Explain how Python works"
        - "Help me debug this error"
        """
        
        try:
            response = await self.generate_response(analysis_prompt)
            # Parse JSON response (simplified - in production, use proper JSON parsing)
            return {
                "is_code_request": "code" in prompt.lower() or "create" in prompt.lower() or "build" in prompt.lower(),
                "language": "unknown",
                "complexity": "medium",
                "description": prompt[:100]
            }
        except Exception:
            # Fallback analysis
            return {
                "is_code_request": any(keyword in prompt.lower() for keyword in ["create", "build", "write", "make", "generate", "code"]),
                "language": "unknown",
                "complexity": "medium",
                "description": prompt[:100]
            }