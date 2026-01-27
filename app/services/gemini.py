"""
Gemini API Service

Simple wrapper around google-genai SDK for all LLM operations.
No complex ADK - just straightforward API calls.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Singleton client
_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    """Get or create the Gemini client (singleton)."""
    global _client
    if _client is None:
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        _client = genai.Client(api_key=api_key)
        logger.info("✅ Gemini client initialized")
    return _client


async def generate_text(
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_instruction: Optional[str] = None
) -> str:
    """
    Generate text using Gemini API.
    
    Args:
        prompt: The user prompt
        model: Model name (default: gemini-2.5-flash)
        temperature: Creativity (0.0 = deterministic, 1.0+ = creative)
        max_tokens: Maximum response length
        system_instruction: Optional system prompt
        
    Returns:
        Generated text response
    """
    client = get_client()
    
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Build contents
        if system_instruction:
            contents = [
                types.Content(role="user", parts=[types.Part(text=system_instruction)]),
                types.Content(role="model", parts=[types.Part(text="Understood. I will follow these instructions.")]),
                types.Content(role="user", parts=[types.Part(text=prompt)])
            ]
        else:
            contents = prompt
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


async def generate_json(
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Generate structured JSON response.
    
    Args:
        prompt: Prompt that requests JSON output
        model: Model name
        temperature: Low for consistent JSON
        
    Returns:
        Parsed JSON dict
    """
    client = get_client()
    
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=1024,
        )
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        text = response.text.strip()
        
        # Clean markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}, raw: {text[:200]}")
        return {}
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {}


class GeminiChat:
    """
    Multi-turn chat session with Gemini.
    Maintains conversation history automatically.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ):
        self.model = model
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.history: List[types.Content] = []
        
        # Add system instruction as first turn if provided
        if system_instruction:
            self.history.append(
                types.Content(role="user", parts=[types.Part(text=f"[System Instruction]\n{system_instruction}")])
            )
            self.history.append(
                types.Content(role="model", parts=[types.Part(text="Understood. I will follow these instructions.")])
            )
    
    async def send_message(self, message: str) -> str:
        """
        Send a message and get response.
        
        Args:
            message: User message
            
        Returns:
            Model's response text
        """
        client = get_client()
        
        # Add user message to history
        self.history.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )
        
        try:
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=1024,
            )
            
            response = client.models.generate_content(
                model=self.model,
                contents=self.history,
                config=config
            )
            
            response_text = response.text
            
            # Add model response to history
            self.history.append(
                types.Content(role="model", parts=[types.Part(text=response_text)])
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            # Remove failed user message from history
            self.history.pop()
            raise
    
    def get_history_text(self) -> str:
        """Get conversation history as text."""
        lines = []
        for content in self.history:
            role = "USER" if content.role == "user" else "MODEL"
            text = content.parts[0].text if content.parts else ""
            # Skip system instruction
            if not text.startswith("[System Instruction]"):
                lines.append(f"{role}: {text}")
        return "\n".join(lines)
    
    def clear_history(self):
        """Clear conversation history (keeps system instruction)."""
        if self.system_instruction:
            self.history = self.history[:2]  # Keep system instruction
        else:
            self.history = []
