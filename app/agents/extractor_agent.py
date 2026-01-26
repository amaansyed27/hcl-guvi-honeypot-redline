"""
Intelligence Extractor Agent

ADK LlmAgent that extracts actionable intelligence from conversations.
"""

import json
import logging
from typing import List, Optional
from google.adk.agents import Agent

from app.config import settings
from app.prompts.extraction import INTELLIGENCE_EXTRACTION_PROMPT, CONVERSATION_ANALYSIS_PROMPT
from app.tools.extraction import extract_all_intelligence
from app.models.intelligence import ExtractedIntelligence

logger = logging.getLogger(__name__)


def create_extractor_agent() -> Agent:
    """
    Create the intelligence extraction agent.
    
    This agent analyzes conversations and extracts:
    - Bank account numbers
    - UPI IDs  
    - Phishing links
    - Phone numbers
    - Suspicious keywords
    """
    
    extractor_agent = Agent(
        model=settings.model_name,
        name='intelligence_extractor',
        description='Extracts actionable intelligence from scam conversations',
        instruction=INTELLIGENCE_EXTRACTION_PROMPT,
        output_key='extracted_intelligence'
    )
    
    return extractor_agent


def create_summary_agent() -> Agent:
    """
    Create the conversation summary agent.
    
    This agent generates agent_notes summarizing scammer behavior.
    """
    
    summary_agent = Agent(
        model=settings.model_name,
        name='conversation_summarizer',
        description='Summarizes scam conversations for reporting',
        instruction=CONVERSATION_ANALYSIS_PROMPT,
        output_key='agent_notes'
    )
    
    return summary_agent


def parse_llm_intelligence(llm_output: str) -> ExtractedIntelligence:
    """
    Parse the LLM's intelligence extraction output.
    
    Args:
        llm_output: Raw text output from extractor agent
        
    Returns:
        ExtractedIntelligence object
    """
    try:
        # Handle JSON in markdown code blocks
        text = llm_output.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(text)
        
        return ExtractedIntelligence(
            bankAccounts=data.get("bankAccounts", []),
            upiIds=data.get("upiIds", []),
            phishingLinks=data.get("phishingLinks", []),
            phoneNumbers=data.get("phoneNumbers", []),
            suspiciousKeywords=data.get("suspiciousKeywords", [])
        )
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse LLM intelligence: {e}")
        return ExtractedIntelligence()


async def extract_intelligence(
    conversation_history: List[dict],
    current_message: str = ""
) -> ExtractedIntelligence:
    """
    Extract intelligence from a conversation using both regex and LLM.
    
    Args:
        conversation_history: All messages in the conversation
        current_message: The latest message to include
        
    Returns:
        Combined ExtractedIntelligence from all methods
    """
    # Build full conversation text
    all_text_parts = []
    
    for msg in conversation_history:
        all_text_parts.append(msg.get("text", ""))
    
    if current_message:
        all_text_parts.append(current_message)
    
    full_text = "\n".join(all_text_parts)
    
    # Method 1: Regex extraction (fast, reliable)
    regex_intel = extract_all_intelligence(full_text)
    
    # Method 2: LLM extraction (catches context-dependent info)
    try:
        extractor = create_extractor_agent()
        
        prompt = f"""Extract all intelligence from this scam conversation:

CONVERSATION:
{full_text}

Provide extracted intelligence in JSON format."""
        
        result = extractor.run(input=prompt)
        llm_intel = parse_llm_intelligence(result.output)
        
        # Merge both results
        combined = regex_intel.merge(llm_intel)
        
    except Exception as e:
        logger.error(f"LLM extraction error: {e}")
        combined = regex_intel
    
    logger.info(f"Extracted: {len(combined.bankAccounts)} accounts, "
                f"{len(combined.upiIds)} UPIs, {len(combined.phishingLinks)} links")
    
    return combined


async def generate_agent_notes(
    conversation_history: List[dict],
    intelligence: ExtractedIntelligence
) -> str:
    """
    Generate summary notes about the scam engagement.
    
    Args:
        conversation_history: Full conversation
        intelligence: Extracted intelligence
        
    Returns:
        Summary string for agent_notes field
    """
    try:
        summarizer = create_summary_agent()
        
        # Build conversation text
        conv_text = "\n".join([
            f"{msg.get('sender', 'unknown').upper()}: {msg.get('text', '')}"
            for msg in conversation_history
        ])
        
        prompt = f"""Summarize this scam conversation for the agent_notes field:

CONVERSATION:
{conv_text}

EXTRACTED INTELLIGENCE:
- Bank Accounts: {intelligence.bankAccounts}
- UPI IDs: {intelligence.upiIds}
- Phishing Links: {intelligence.phishingLinks}
- Phone Numbers: {intelligence.phoneNumbers}
- Keywords: {intelligence.suspiciousKeywords}

Provide a concise 1-2 sentence summary of:
1. The scam technique used
2. Key tactics employed by the scammer
3. Quality of intelligence gathered

OUTPUT (single line, no JSON):"""
        
        result = summarizer.run(input=prompt)
        notes = result.output.strip()
        
        # Clean up any extra formatting
        notes = notes.replace("\n", " ").strip()
        if len(notes) > 500:
            notes = notes[:497] + "..."
            
        return notes
        
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        
        # Generate fallback notes
        tactics = []
        if intelligence.suspiciousKeywords:
            if "urgent" in [k.lower() for k in intelligence.suspiciousKeywords]:
                tactics.append("urgency tactics")
            if any(k in ["bank", "account", "blocked"] for k in intelligence.suspiciousKeywords):
                tactics.append("account threat")
        
        if intelligence.upiIds:
            tactics.append("payment redirection")
        if intelligence.phishingLinks:
            tactics.append("phishing links")
            
        return f"Scammer used {', '.join(tactics) if tactics else 'social engineering'} tactics."
