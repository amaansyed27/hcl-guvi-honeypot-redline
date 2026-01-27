"""
Honeypot Pipeline

Orchestrates the full honeypot workflow using ADK SequentialAgent.
"""

import logging
from typing import Tuple
from google.adk.agents import Agent, SequentialAgent

from app.config import settings
from app.prompts.detection import SCAM_DETECTION_PROMPT
from app.prompts.persona import get_persona
from app.prompts.extraction import INTELLIGENCE_EXTRACTION_PROMPT
from app.tools.extraction import EXTRACTION_TOOLS

logger = logging.getLogger(__name__)


def create_honeypot_pipeline(persona_type: str = "elderly") -> SequentialAgent:
    """
    Create the full honeypot pipeline using ADK SequentialAgent.
    
    Pipeline stages:
    1. Scam Detection - Analyze message for scam intent
    2. Honeypot Engagement - Generate believable response
    3. Intelligence Extraction - Extract actionable data
    
    Args:
        persona_type: Type of persona for the honeypot agent
        
    Returns:
        SequentialAgent orchestrating the full workflow
    """
    
    # Stage 1: Scam Detection Agent
    detector_agent = Agent(
        model=settings.model_name,
        name='scam_detector',
        description='Analyzes messages to detect scam intent',
        instruction=SCAM_DETECTION_PROMPT,
        output_key='scam_analysis'
    )
    
    # Stage 2: Honeypot Persona Agent
    persona_prompt = get_persona(persona_type)
    honeypot_agent = Agent(
        model=settings.model_name,
        name='honeypot_persona',
        description='Engages scammers with believable human persona',
        instruction=f"""{persona_prompt}

CONTEXT FROM PREVIOUS ANALYSIS:
Check the scam_analysis from state to understand the scam type and indicators.
Use this information to guide your response strategy without revealing detection.

Generate a response that:
1. Stays in character as the persona
2. Asks questions to extract more information
3. Shows appropriate emotional reactions
4. Never reveals scam detection""",
        tools=EXTRACTION_TOOLS,
        output_key='agent_response'
    )
    
    # Stage 3: Intelligence Extraction Agent
    extractor_agent = Agent(
        model=settings.model_name,
        name='intelligence_extractor',
        description='Extracts intelligence from conversation',
        instruction=f"""{INTELLIGENCE_EXTRACTION_PROMPT}

Use the conversation from state including:
- The original scammer message
- The scam_analysis results
- The agent_response generated

Extract ALL possible intelligence and format as JSON.""",
        output_key='extracted_intelligence'
    )
    
    # Create Sequential Pipeline
    pipeline = SequentialAgent(
        name='honeypot_pipeline',
        sub_agents=[detector_agent, honeypot_agent, extractor_agent],
        description='Full honeypot workflow: detect → engage → extract'
    )
    
    return pipeline


# Alternative: Create individual agents for more control
class HoneypotOrchestrator:
    """
    Orchestrates honeypot agents with custom control flow.
    
    Provides more flexibility than SequentialAgent for handling
    edge cases and custom logic.
    """
    
    def __init__(self, persona_type: str = "elderly"):
        self.persona_type = persona_type
        self.detector = self._create_detector()
        self.honeypot = self._create_honeypot()
        self.extractor = self._create_extractor()
        
    def _create_detector(self) -> Agent:
        return Agent(
            model=settings.model_name,
            name='detector',
            instruction=SCAM_DETECTION_PROMPT,
            output_key='scam_analysis'
        )
    
    def _create_honeypot(self) -> Agent:
        return Agent(
            model=settings.model_name,
            name='honeypot',
            instruction=get_persona(self.persona_type),
            tools=EXTRACTION_TOOLS,
            output_key='agent_response'
        )
    
    def _create_extractor(self) -> Agent:
        return Agent(
            model=settings.model_name,
            name='extractor',
            instruction=INTELLIGENCE_EXTRACTION_PROMPT,
            output_key='intelligence'
        )
    
    async def process_message(
        self,
        message: str,
        conversation_history: list,
        session_id: str
    ) -> Tuple[bool, str, dict]:
        """
        Process a message through the honeypot pipeline.
        
        Args:
            message: The incoming scammer message
            conversation_history: Previous messages
            session_id: Session identifier
            
        Returns:
            Tuple of (is_scam, agent_response, intelligence_dict)
        """
        # Build context
        history_text = "\n".join([
            f"{m.get('sender', 'unknown').upper()}: {m.get('text', '')}"
            for m in conversation_history
        ])
        
        full_context = f"{history_text}\nSCAMMER: {message}" if history_text else f"SCAMMER: {message}"
        
        # Stage 1: Detect scam
        detection_result = self.detector.run(
            input=f"Analyze this conversation:\n{full_context}",
            session_id=f"{session_id}_detect"
        )
        
        is_scam = "is_scam\": true" in detection_result.output.lower() or \
                  "\"is_scam\": true" in detection_result.output.lower()
        
        # Stage 2: Generate response (always engage to gather intel)
        response_result = self.honeypot.run(
            input=f"""Continue this conversation. The scammer just messaged you.

CONVERSATION:
{full_context}

YOUR RESPONSE (stay in character, ask questions to extract info):""",
            session_id=f"{session_id}_respond"
        )
        
        agent_response = response_result.output.strip()
        
        # Stage 3: Extract intelligence
        extraction_result = self.extractor.run(
            input=f"Extract intelligence from:\n{full_context}\n\nYOUR RESPONSE: {agent_response}",
            session_id=f"{session_id}_extract"
        )
        
        # Parse intelligence (simplified)
        intelligence = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }
        
        # Use regex extraction as fallback
        from app.tools.extraction import extract_all_intelligence
        regex_intel = extract_all_intelligence(full_context + " " + agent_response)
        intelligence = regex_intel.to_dict()
        
        return is_scam, agent_response, intelligence


# Export the pipeline creator
root_agent = create_honeypot_pipeline()
