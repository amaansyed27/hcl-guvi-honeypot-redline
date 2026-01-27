"""
Agents Package

Simple AI agents using Google Gemini API (google-genai SDK).
No complex frameworks - just clean, direct API calls.
"""

from app.agents.scam_detector import detect_scam, ScamAnalysis
from app.agents.honeypot_persona import generate_response, get_fallback_response, PERSONAS
from app.agents.intelligence_extractor import (
    extract_intelligence,
    generate_notes,
    extract_with_regex,
    ExtractedIntelligence
)

__all__ = [
    # Scam Detection
    "detect_scam",
    "ScamAnalysis",
    # Honeypot Persona
    "generate_response",
    "get_fallback_response",
    "PERSONAS",
    # Intelligence Extraction
    "extract_intelligence",
    "generate_notes",
    "extract_with_regex",
    "ExtractedIntelligence",
]
