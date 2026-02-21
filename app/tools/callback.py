"""
GUVI Callback Tool

Sends final intelligence results to the GUVI evaluation endpoint.
"""

import httpx
import logging
from typing import Optional, Union
from app.config import get_settings
from app.agents.intelligence_extractor import ExtractedIntelligence

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_guvi_callback(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence,  # ExtractedIntelligence from agents or model
    agent_notes: str,
    engagement_duration_seconds: int = 0,
    scam_type: str = "unknown",
    confidence_level: float = 0.95
) -> dict:
    """
    Send final results to GUVI evaluation endpoint.
    
    This is MANDATORY for scoring. Must be called after:
    1. Scam intent is confirmed (scam_detected = True)
    2. AI Agent has completed sufficient engagement
    3. Intelligence extraction is finished
    
    Args:
        session_id: Unique session ID from the platform
        scam_detected: Whether scam intent was confirmed
        total_messages: Total messages exchanged in session
        intelligence: Extracted intelligence object (has to_dict method)
        agent_notes: Summary of scammer behavior
        engagement_duration_seconds: Duration of engagement in seconds
        scam_type: Type of scam detected
        confidence_level: Confidence in scam detection (0-1)
        
    Returns:
        Dictionary with callback status and response
    """
    # Convert intelligence to dict
    if hasattr(intelligence, 'to_dict'):
        intel_dict = intelligence.to_dict()
    elif isinstance(intelligence, dict):
        intel_dict = intelligence
    else:
        intel_dict = {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "engagementDurationSeconds": engagement_duration_seconds,
        "extractedIntelligence": intel_dict,
        "agentNotes": agent_notes,
        "scamType": scam_type,
        "confidenceLevel": confidence_level
    }
    
    logger.info(f"Sending GUVI callback for session {session_id}")
    logger.debug(f"Callback payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.guvi_callback_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ GUVI callback successful for session {session_id}")
                return {
                    "status": "success",
                    "message": "Callback sent successfully",
                    "response_code": response.status_code
                }
            else:
                logger.error(f"❌ GUVI callback failed: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Callback failed with status {response.status_code}",
                    "response_code": response.status_code,
                    "response_text": response.text
                }
                
    except httpx.TimeoutException:
        logger.error(f"⏰ GUVI callback timeout for session {session_id}")
        return {
            "status": "error",
            "message": "Callback request timed out"
        }
    except Exception as e:
        logger.error(f"💥 GUVI callback error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


def send_guvi_callback_sync(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str,
    engagement_duration_seconds: int = 0,
    scam_type: str = "unknown",
    confidence_level: float = 0.95
) -> dict:
    """
    Synchronous version of GUVI callback for use in ADK tools.
    """
    import asyncio
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        send_guvi_callback(
            session_id=session_id,
            scam_detected=scam_detected,
            total_messages=total_messages,
            intelligence=intelligence,
            agent_notes=agent_notes,
            engagement_duration_seconds=engagement_duration_seconds,
            scam_type=scam_type,
            confidence_level=confidence_level
        )
    )
