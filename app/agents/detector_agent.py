"""
Scam Detector Agent

ADK LlmAgent that analyzes messages for scam intent.
"""

import json
import logging
from typing import Optional
from google.adk.agents import Agent

from app.config import settings
from app.prompts.detection import SCAM_DETECTION_PROMPT
from app.models.intelligence import ScamAnalysis

logger = logging.getLogger(__name__)


def create_detector_agent() -> Agent:
    """
    Create the scam detection agent.
    
    This agent analyzes incoming messages and determines if they are scam attempts.
    It outputs structured analysis including confidence score and indicators.
    """
    
    detector_agent = Agent(
        model=settings.model_name,
        name='scam_detector',
        description='Analyzes messages to detect scam intent and classify scam types',
        instruction=SCAM_DETECTION_PROMPT,
        output_key='scam_analysis'
    )
    
    return detector_agent


def parse_scam_analysis(analysis_text: str) -> ScamAnalysis:
    """
    Parse the detector agent's output into a ScamAnalysis object.
    
    Args:
        analysis_text: Raw text output from detector agent
        
    Returns:
        ScamAnalysis object with parsed data
    """
    try:
        # Try to extract JSON from the response
        # Handle cases where JSON is wrapped in markdown code blocks
        text = analysis_text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(text)
        
        return ScamAnalysis(
            is_scam=data.get("is_scam", False),
            confidence=float(data.get("confidence", 0.0)),
            indicators=data.get("indicators", []),
            scam_type=data.get("scam_type", "unknown")
        )
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(f"Failed to parse scam analysis: {e}")
        # Default to scam detection if parsing fails but text suggests scam
        is_scam = any(word in analysis_text.lower() for word in [
            "scam", "fraud", "suspicious", "urgent", "block", "verify"
        ])
        
        return ScamAnalysis(
            is_scam=is_scam,
            confidence=0.7 if is_scam else 0.3,
            indicators=["parse_error"],
            scam_type="unknown"
        )


async def detect_scam(message: str, conversation_history: str = "") -> ScamAnalysis:
    """
    Analyze a message for scam intent.
    
    Args:
        message: The message to analyze
        conversation_history: Optional previous conversation context
        
    Returns:
        ScamAnalysis with detection results
    """
    detector = create_detector_agent()
    
    # Build the analysis prompt
    if conversation_history:
        prompt = f"""Analyze this conversation for scam intent:

CONVERSATION HISTORY:
{conversation_history}

LATEST MESSAGE:
{message}

Provide your analysis in JSON format."""
    else:
        prompt = f"""Analyze this message for scam intent:

MESSAGE:
{message}

Provide your analysis in JSON format."""
    
    try:
        # Note: In actual ADK usage, you'd use the runner
        # This is a simplified version for the FastAPI integration
        result = detector.run(input=prompt)
        return parse_scam_analysis(result.output)
        
    except Exception as e:
        logger.error(f"Scam detection error: {e}")
        # Default to assuming scam on error (safer for honeypot)
        return ScamAnalysis(
            is_scam=True,
            confidence=0.5,
            indicators=["detection_error"],
            scam_type="unknown"
        )
