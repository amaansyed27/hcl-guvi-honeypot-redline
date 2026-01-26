"""
Agents Package

Contains all ADK agents for the honeypot system.
"""

from app.agents.detector_agent import (
    create_detector_agent,
    detect_scam,
    parse_scam_analysis
)

from app.agents.honeypot_agent import (
    create_honeypot_agent,
    generate_honeypot_response,
    build_conversation_context
)

from app.agents.extractor_agent import (
    create_extractor_agent,
    extract_intelligence,
    generate_agent_notes
)

from app.agents.pipeline import (
    create_honeypot_pipeline,
    HoneypotOrchestrator,
    root_agent
)

__all__ = [
    # Detector
    "create_detector_agent",
    "detect_scam",
    "parse_scam_analysis",
    # Honeypot
    "create_honeypot_agent",
    "generate_honeypot_response",
    "build_conversation_context",
    # Extractor
    "create_extractor_agent",
    "extract_intelligence",
    "generate_agent_notes",
    # Pipeline
    "create_honeypot_pipeline",
    "HoneypotOrchestrator",
    "root_agent"
]
