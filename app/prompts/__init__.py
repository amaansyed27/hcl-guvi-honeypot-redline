"""
Prompts Package

Contains system prompts for all honeypot agents.
"""

from app.prompts.persona import (
    ELDERLY_PERSONA,
    YOUNG_PROFESSIONAL_PERSONA,
    WORRIED_PARENT_PERSONA,
    PERSONAS,
    DEFAULT_PERSONA,
    get_persona
)

from app.prompts.detection import (
    SCAM_DETECTION_PROMPT,
    SCAM_TYPES
)

from app.prompts.extraction import (
    INTELLIGENCE_EXTRACTION_PROMPT,
    CONVERSATION_ANALYSIS_PROMPT
)

__all__ = [
    # Personas
    "ELDERLY_PERSONA",
    "YOUNG_PROFESSIONAL_PERSONA", 
    "WORRIED_PARENT_PERSONA",
    "PERSONAS",
    "DEFAULT_PERSONA",
    "get_persona",
    # Detection
    "SCAM_DETECTION_PROMPT",
    "SCAM_TYPES",
    # Extraction
    "INTELLIGENCE_EXTRACTION_PROMPT",
    "CONVERSATION_ANALYSIS_PROMPT"
]
