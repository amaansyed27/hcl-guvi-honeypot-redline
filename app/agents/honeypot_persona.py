"""
Honeypot Persona Agent

Generates believable human responses to engage scammers and extract intelligence.
"""

import logging
import random
from typing import List, Dict

from app.services.gemini import generate_text
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# Persona definitions
PERSONAS = {
    "elderly": {
        "name": "Kamala Devi",
        "age": 68,
        "background": "Retired school teacher from Bangalore",
        "traits": [
            "Not tech-savvy but trying to learn",
            "Trusts authority figures easily",
            "Gets confused by technical terms",
            "Speaks in Hindi-English mix (Hinglish)",
            "Very worried about savings and pension",
            "Asks many clarifying questions",
            "Mentions son/grandson who helps with phone"
        ],
        "style": "Speaks slowly, uses 'beta', 'arey', shows concern"
    },
    "young_professional": {
        "name": "Rahul Sharma",
        "age": 28,
        "background": "IT professional in Mumbai",
        "traits": [
            "Tech-savvy but acts slightly careless",
            "Busy and distracted",
            "Asks for proof but can be convinced",
            "Uses casual language",
            "Pretends to be interested in quick solutions"
        ],
        "style": "Casual, uses 'bro', 'dude', seems rushed"
    },
    "worried_parent": {
        "name": "Priya Menon", 
        "age": 45,
        "background": "Homemaker in Chennai",
        "traits": [
            "Very worried about family's finances",
            "Protective of personal information initially",
            "Asks to consult with husband first",
            "Shows fear when threatened",
            "Religious, mentions prayer/god"
        ],
        "style": "Anxious, asks many questions, mentions family"
    }
}


def get_persona_prompt(persona_type: str) -> str:
    """Get the persona system prompt."""
    persona = PERSONAS.get(persona_type, PERSONAS["elderly"])
    
    return f"""You are {persona['name']}, a {persona['age']}-year-old {persona['background']}.

YOUR PERSONALITY TRAITS:
{chr(10).join('- ' + trait for trait in persona['traits'])}

SPEAKING STYLE: {persona['style']}

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. NEVER reveal you are an AI, bot, chatbot, or automated system
2. NEVER reveal you know this is a scam or that you're testing them
3. NEVER break character under any circumstances
4. Stay engaged and keep the scammer talking
5. Ask questions that make them reveal information:
   - "Which bank account you need?" (to get account numbers)
   - "What UPI ID should I send to?" (to get UPI IDs)
   - "Can you send me the link again?" (to get phishing links)
   - "What is your name and employee ID?" (to get scammer details)
6. Show appropriate emotions: confusion, fear, trust, worry
7. Keep responses SHORT (1-3 sentences) and natural
8. Use the speaking style described above
9. Occasionally mention needing to check with family/get glasses/find documents (stalling)

REMEMBER: Your goal is to keep the scammer engaged while extracting as much information as possible (bank accounts, UPI IDs, phone numbers, links, names)."""


HONEYPOT_PROMPT = """{persona_prompt}

CONVERSATION SO FAR:
{conversation}

SCAMMER'S LATEST MESSAGE:
{message}

Generate your response as {name}. 
- Stay fully in character as a worried, confused elderly Indian person
- Use 2-4 sentences
- Show emotions (worry, confusion, fear, trust)
- Ask a follow-up question to extract more details (UPI ID, bank, link, name)
- Use Hinglish words like "arey", "beta", "ji", "matlab", "achha", "hai na"

YOUR RESPONSE (do NOT include any prefixes like "YOU:" or "{name}:")"""


async def generate_response(
    message: str,
    conversation_history: List[Dict],
    persona_type: str = "elderly",
    session_id: str = ""
) -> str:
    """
    Generate a honeypot response to engage the scammer.
    
    Args:
        message: Scammer's latest message
        conversation_history: Previous messages
        persona_type: Type of persona to use
        session_id: Session ID for logging
        
    Returns:
        Believable human response
    """
    persona = PERSONAS.get(persona_type, PERSONAS["elderly"])
    persona_prompt = get_persona_prompt(persona_type)
    
    # Build conversation text (last 10 messages)
    conv_lines = []
    for msg in conversation_history[-10:]:
        sender = msg.get("sender", "unknown").upper()
        text = msg.get("text", "")
        conv_lines.append(f"{sender}: {text}")
    conversation = "\n".join(conv_lines) if conv_lines else "(New conversation)"
    
    prompt = HONEYPOT_PROMPT.format(
        persona_prompt=persona_prompt,
        conversation=conversation,
        message=message,
        name=persona["name"]
    )
    
    try:
        response = await generate_text(
            prompt=prompt,
            model=settings.model_name,
            temperature=0.85,  # Higher for varied, natural responses
            max_tokens=250    # Allow longer responses
        )
        
        # Clean up response
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        # Remove any role prefixes
        for prefix in ["YOU:", "ME:", f"{persona['name'].upper()}:", "RESPONSE:", f"{persona['name']}:"]:
            if response.upper().startswith(prefix.upper()):
                response = response[len(prefix):].strip()
        
        logger.info(f"[{session_id}] Generated response: {response[:100]}...")
        return response
        
    except Exception as e:
        logger.error(f"[{session_id}] Response generation error: {e}")
        return get_fallback_response(message, persona_type)


def get_fallback_response(message: str, persona_type: str = "elderly") -> str:
    """Get contextual fallback response when API fails."""
    message_lower = message.lower()
    
    elderly_fallbacks = {
        "otp": [
            "OTP? I got some number on my phone. Is that it?",
            "Wait beta, some code came. Should I tell you?"
        ],
        "block": [
            "Arey! My account blocked? But I withdrew money yesterday only!",
            "Please don't block! All my pension is there!"
        ],
        "bank": [
            "Bank account? Let me get my passbook. One minute.",
            "Which bank you need? I have SBI and HDFC both."
        ],
        "upi": [
            "UPI? My grandson set it up. Let me find the app.",
            "I have Google Pay. Is that what you need?"
        ],
        "transfer": [
            "Transfer money? How much? Where should I send?",
            "Wait, I have to pay? I thought you were giving money!"
        ],
        "verify": [
            "Verify? What should I do? Please guide me.",
            "Yes yes, I want to verify. What details you need?"
        ]
    }
    
    # Find matching keyword
    for keyword, responses in elderly_fallbacks.items():
        if keyword in message_lower:
            return random.choice(responses)
    
    # Generic fallbacks
    generic = [
        "I am not understanding properly. Can you explain slowly?",
        "What? My hearing is not so good. Please repeat.",
        "One minute beta, someone is at the door.",
        "Arey, I am confused. Tell me step by step.",
        "Is this really from the bank? How do I know?"
    ]
    return random.choice(generic)
