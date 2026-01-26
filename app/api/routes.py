"""
API Route Definitions

Contains the main honeypot API endpoints.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader

from app.config import settings
from app.models.request import HoneypotRequest
from app.models.response import HoneypotResponse, EngagementMetrics, ErrorResponse
from app.models.intelligence import ExtractedIntelligence
from app.services.session import session_store, ConversationSession
from app.agents.detector_agent import detect_scam
from app.agents.honeypot_agent import generate_honeypot_response
from app.agents.extractor_agent import extract_intelligence, generate_agent_notes
from app.tools.callback import send_guvi_callback

logger = logging.getLogger(__name__)

router = APIRouter()
api_key_header = APIKeyHeader(name="x-api-key")


@router.post(
    "/analyze",
    response_model=HoneypotResponse,
    responses={
        200: {"description": "Successful analysis and response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Analyze message and generate honeypot response",
    description="""
    Main honeypot endpoint. Accepts scam messages and:
    1. Detects scam intent
    2. Generates believable human response
    3. Extracts intelligence from conversation
    4. Sends callback to GUVI when engagement is complete
    """
)
async def analyze_message(
    request: HoneypotRequest,
    api_key: str = Depends(api_key_header)
):
    """
    Process an incoming scam message through the honeypot pipeline.
    """
    session_id = request.sessionId
    logger.info(f"[{session_id}] Received message from {request.message.sender}")
    
    try:
        # Get or create session
        session = session_store.get_or_create(session_id)
        
        # Add conversation history if provided (for new sessions)
        if request.conversationHistory and session.message_count == 0:
            for msg in request.conversationHistory:
                session.add_message(
                    sender=msg.sender,
                    text=msg.text,
                    timestamp=msg.timestamp
                )
        
        # Add current message
        session.add_message(
            sender=request.message.sender,
            text=request.message.text,
            timestamp=request.message.timestamp
        )
        
        # Build conversation text for analysis
        conversation_text = "\n".join([
            f"{m['sender'].upper()}: {m['text']}"
            for m in session.messages
        ])
        
        # Step 1: Detect scam intent
        scam_analysis = await detect_scam(
            message=request.message.text,
            conversation_history=conversation_text
        )
        
        session.scam_detected = scam_analysis.is_scam
        session.scam_type = scam_analysis.scam_type
        
        logger.info(f"[{session_id}] Scam detected: {scam_analysis.is_scam} "
                   f"(confidence: {scam_analysis.confidence:.2f}, type: {scam_analysis.scam_type})")
        
        # Step 2: Generate honeypot response
        agent_response = await generate_honeypot_response(
            message=request.message.text,
            conversation_history=session.messages[:-1],  # Exclude current message
            persona_type=session.persona_type,
            session_id=session_id
        )
        
        # Add agent response to session
        session.add_message(
            sender="user",
            text=agent_response
        )
        
        # Step 3: Extract intelligence
        intelligence = await extract_intelligence(
            conversation_history=session.messages,
            current_message=""
        )
        session.merge_intelligence(intelligence)
        
        # Step 4: Generate agent notes
        if session.scam_detected and not session.agent_notes:
            session.agent_notes = await generate_agent_notes(
                conversation_history=session.messages,
                intelligence=session.intelligence
            )
        
        # Step 5: Send GUVI callback if conditions met
        callback_sent = False
        if session.should_send_callback():
            callback_result = await send_guvi_callback(
                session_id=session_id,
                scam_detected=session.scam_detected,
                total_messages=session.message_count,
                intelligence=session.intelligence,
                agent_notes=session.agent_notes
            )
            if callback_result["status"] == "success":
                session.callback_sent = True
                callback_sent = True
                logger.info(f"[{session_id}] GUVI callback sent successfully")
        
        # Update session
        session_store.update(session)
        
        # Build response
        response = HoneypotResponse(
            status="success",
            scamDetected=session.scam_detected,
            agentResponse=agent_response,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=session.duration_seconds,
                totalMessagesExchanged=session.message_count
            ),
            extractedIntelligence=session.intelligence,
            agentNotes=session.agent_notes if session.scam_detected else None
        )
        
        logger.info(f"[{session_id}] Response generated. Messages: {session.message_count}")
        return response
        
    except Exception as e:
        logger.error(f"[{session_id}] Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@router.get(
    "/session/{session_id}",
    summary="Get session details",
    description="Retrieve details of an active conversation session."
)
async def get_session(
    session_id: str,
    api_key: str = Depends(api_key_header)
):
    """Get details of a specific session."""
    session = session_store.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session.session_id,
        "messageCount": session.message_count,
        "durationSeconds": session.duration_seconds,
        "scamDetected": session.scam_detected,
        "scamType": session.scam_type,
        "callbackSent": session.callback_sent,
        "intelligence": session.intelligence.to_dict(),
        "createdAt": session.created_at.isoformat(),
        "updatedAt": session.updated_at.isoformat()
    }


@router.delete(
    "/session/{session_id}",
    summary="End session",
    description="Force end a session and trigger callback if applicable."
)
async def end_session(
    session_id: str,
    api_key: str = Depends(api_key_header)
):
    """End a session and send final callback."""
    session = session_store.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Send callback if not already sent
    if session.scam_detected and not session.callback_sent:
        callback_result = await send_guvi_callback(
            session_id=session_id,
            scam_detected=session.scam_detected,
            total_messages=session.message_count,
            intelligence=session.intelligence,
            agent_notes=session.agent_notes or "Session ended manually"
        )
        session.callback_sent = callback_result["status"] == "success"
    
    # Delete session
    session_store.delete(session_id)
    
    return {
        "status": "success",
        "message": f"Session {session_id} ended",
        "callbackSent": session.callback_sent
    }


@router.post(
    "/callback/test",
    summary="Test GUVI callback",
    description="Send a test callback to verify connectivity with GUVI endpoint."
)
async def test_callback(
    api_key: str = Depends(api_key_header)
):
    """Test the GUVI callback endpoint."""
    test_intelligence = ExtractedIntelligence(
        bankAccounts=["TEST-ACCOUNT"],
        upiIds=["test@upi"],
        suspiciousKeywords=["test"]
    )
    
    result = await send_guvi_callback(
        session_id="test-session",
        scam_detected=True,
        total_messages=1,
        intelligence=test_intelligence,
        agent_notes="Test callback"
    )
    
    return {
        "status": result["status"],
        "message": "Callback test completed",
        "result": result
    }
