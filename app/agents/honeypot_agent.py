"""
Honeypot Persona Agent

ADK LlmAgent that maintains a believable human persona to engage scammers.
"""

import logging
from typing import List, Optional
from google.adk.agents import Agent

from app.config import settings
from app.prompts.persona import get_persona, DEFAULT_PERSONA
from app.tools.extraction import EXTRACTION_TOOLS

logger = logging.getLogger(__name__)


def create_honeypot_agent(persona_type: str = "elderly") -> Agent:
    """
    Create the honeypot persona agent.
    
    This agent maintains a believable human persona and engages
    scammers in multi-turn conversations to extract intelligence.
    
    Args:
        persona_type: Type of persona ("elderly", "young_professional", "worried_parent")
        
    Returns:
        Configured ADK Agent
    """
    
    persona_prompt = get_persona(persona_type)
    
    honeypot_agent = Agent(
        model=settings.model_name,
        name='honeypot_persona',
        description='Engages scammers with a believable human persona to extract intelligence',
        instruction=persona_prompt,
        tools=EXTRACTION_TOOLS,  # Can use extraction tools during conversation
        output_key='agent_response',
        temperature=settings.agent_temperature  # Slightly creative for natural responses
    )
    
    return honeypot_agent


def build_conversation_context(
    conversation_history: List[dict],
    current_message: str,
    sender: str = "scammer"
) -> str:
    """
    Build conversation context string for the agent.
    
    Args:
        conversation_history: List of previous messages
        current_message: The latest message
        sender: Who sent the current message
        
    Returns:
        Formatted conversation context
    """
    context_parts = []
    
    # Add conversation history
    for msg in conversation_history:
        role = "SCAMMER" if msg.get("sender") == "scammer" else "YOU"
        context_parts.append(f"{role}: {msg.get('text', '')}")
    
    # Add current message
    current_role = "SCAMMER" if sender == "scammer" else "YOU"
    context_parts.append(f"{current_role}: {current_message}")
    
    return "\n".join(context_parts)


async def generate_honeypot_response(
    message: str,
    conversation_history: List[dict],
    persona_type: str = "elderly",
    session_id: str = ""
) -> str:
    """
    Generate a honeypot response to a scammer's message.
    
    Args:
        message: The scammer's latest message
        conversation_history: Previous messages in the conversation
        persona_type: Type of persona to use
        session_id: Session identifier for logging
        
    Returns:
        The honeypot agent's response
    """
    agent = create_honeypot_agent(persona_type)
    
    # Build the full context
    context = build_conversation_context(conversation_history, message, "scammer")
    
    prompt = f"""Continue this conversation as your persona. The scammer just sent you a message.

CONVERSATION SO FAR:
{context}

Generate your response as the persona. Remember:
- Stay in character
- Ask questions to extract information (bank details, UPI IDs, links)
- Show appropriate emotions (confusion, fear, trust)
- Never reveal you're an AI or that you detected a scam
- Keep the conversation going to gather more intelligence

YOUR RESPONSE:"""
    
    try:
        result = agent.run(input=prompt, session_id=session_id)
        response = result.output.strip()
        
        # Clean up any meta-commentary
        if "YOUR RESPONSE:" in response:
            response = response.split("YOUR RESPONSE:")[-1].strip()
        
        logger.info(f"[{session_id}] Generated honeypot response")
        return response
        
    except Exception as e:
        logger.error(f"[{session_id}] Honeypot response error: {e}")
        # Fallback response that stays in character
        return "I am not understanding properly. Can you please explain again slowly?"


# Predefined responses for different scam stages
STAGE_RESPONSES = {
    "initial_contact": [
        "Hello? Who is this? How did you get my number?",
        "Yes, this is speaking. What is the matter?",
        "Oh my god, is everything okay? What happened to my account?"
    ],
    "building_trust": [
        "I see, I see. You are from the bank only? How do I know this is real?",
        "My son told me to be careful about these calls. Can you give me some proof?",
        "Okay, okay. I am trusting you. What should I do now?"
    ],
    "extracting_info": [
        "Yes, I have my ATM card here. What details do you need?",
        "Let me find my passbook... I keep it in the almari. One minute.",
        "You need my UPI ID? I think my grandson set it up. Let me check the app."
    ],
    "stalling": [
        "Wait, wait. I am old, I need time to understand these things.",
        "Can I call you back? My neighbor is at the door.",
        "I am getting confused. Can you explain one more time please?"
    ]
}
