"""
Scam Detector

Uses Gemini to analyze messages for scam/fraud indicators.
"""

import logging
from typing import List
from dataclasses import dataclass

from app.services.gemini import generate_json
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ScamAnalysis:
    """Result of scam analysis."""
    is_scam: bool
    confidence: float  # 0.0 to 1.0
    scam_type: str
    indicators: List[str]


DETECTION_PROMPT = """You are a scam detection expert. Analyze the following message for scam/fraud indicators.

COMMON SCAM INDICATORS:
- Urgency tactics: "immediately", "urgent", "your account will be blocked"
- Financial requests: OTP, bank details, UPI transfers, card numbers
- Authority impersonation: claiming to be from bank, police, government
- Reward/prize scams: "you won", "cashback", "lottery"
- Fear tactics: "legal action", "arrest warrant", "account suspended"
- Suspicious links or requests for personal information
- Grammar/spelling errors typical of scam messages
- Pressure to act quickly without verification

SCAM TYPES:
- bank_fraud: Fake bank calls, account verification scams
- upi_fraud: UPI/payment app scams
- phishing: Link-based credential theft
- tech_support: Fake tech support scams
- lottery: Lottery/prize scams
- job_scam: Fake job offers
- kyc_fraud: Fake KYC update requests
- other: Other types
- none: Not a scam

MESSAGE TO ANALYZE:
{message}

{history_context}

Respond with ONLY valid JSON (no markdown, no explanation):
{{"is_scam": true/false, "confidence": 0.0-1.0, "scam_type": "type", "indicators": ["list", "of", "indicators"]}}"""


async def detect_scam(
    message: str,
    conversation_history: str = ""
) -> ScamAnalysis:
    """
    Detect if a message is a scam attempt.
    
    Args:
        message: The message to analyze
        conversation_history: Optional conversation context
        
    Returns:
        ScamAnalysis with detection results
    """
    history_context = ""
    if conversation_history:
        history_context = f"\nCONVERSATION CONTEXT:\n{conversation_history}"
    
    prompt = DETECTION_PROMPT.format(
        message=message,
        history_context=history_context
    )
    
    try:
        result = await generate_json(
            prompt=prompt,
            model=settings.model_name,
            temperature=0.1,  # Low temp for consistent detection
            thinking_level="low"  # Simple classification, no deep reasoning needed
        )
        
        analysis = ScamAnalysis(
            is_scam=result.get("is_scam", False),
            confidence=float(result.get("confidence", 0.0)),
            scam_type=result.get("scam_type", "unknown"),
            indicators=result.get("indicators", [])
        )
        
        logger.info(f"Scam detection: is_scam={analysis.is_scam}, "
                   f"confidence={analysis.confidence:.2f}, type={analysis.scam_type}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        # Fallback: keyword-based detection
        scam_keywords = ["urgent", "otp", "blocked", "verify", "bank", "upi", "kyc", "aadhar"]
        is_likely_scam = any(kw in message.lower() for kw in scam_keywords)
        
        return ScamAnalysis(
            is_scam=is_likely_scam,
            confidence=0.6 if is_likely_scam else 0.3,
            scam_type="unknown",
            indicators=["keyword_match"] if is_likely_scam else []
        )
