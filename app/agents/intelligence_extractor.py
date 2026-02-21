"""
Intelligence Extractor

Extracts actionable intelligence from scam conversations:
- Bank account numbers
- UPI IDs
- Phone numbers
- Phishing links
- Suspicious keywords
"""

import re
import logging
from typing import List, Dict
from dataclasses import dataclass, field

from app.services.gemini import generate_json, generate_text
from app.config import get_settings
from app.models.intelligence import ExtractedIntelligence

logger = logging.getLogger(__name__)
settings = get_settings()

# Regex patterns for extraction
PATTERNS = {
    "bank_account": r'\b\d{9,18}\b',  # 9-18 digit numbers
    "upi_id": r'\b[\w\.\-]+@(?:ybl|paytm|okaxis|oksbi|okhdfcbank|upi|apl|axl|ibl|sbi|icici|hdfc|axis|kotak|rbl|federal|indus|idbi|pnb|bob|canara|union|ubi|cub|kvb|tmb|iob|dcb|jkb|bandhan|fakebank|fakeupi)\b',
    "phone": r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b',
    "url": r'https?://[^\s<>"\']+|(?:www\.)?[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?',
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
    "id_number": r'\b(?:ID|CASE|REF|POL|ORD|TRK|AWB)[\s\:\-]*[A-Z0-9]{5,15}\b',
}

SCAM_KEYWORDS = [
    "urgent", "immediately", "block", "suspend", "freeze", "verify",
    "otp", "cvv", "pin", "password", "aadhar", "pan", "kyc",
    "transfer", "refund", "cashback", "lottery", "prize", "won",
    "arrest", "police", "legal", "court", "warrant",
    "rbi", "income tax", "customs", "cbi", "irs"
]


def extract_with_regex(text: str) -> ExtractedIntelligence:
    """Extract intelligence using regex patterns."""
    text_lower = text.lower()
    
    # Extract bank accounts (filter out likely non-account numbers)
    bank_accounts = []
    for match in re.findall(PATTERNS["bank_account"], text):
        # Filter: account numbers are usually 11-16 digits
        if 11 <= len(match) <= 16:
            bank_accounts.append(match)
    
    # Extract UPI IDs
    upi_ids = re.findall(PATTERNS["upi_id"], text_lower)
    
    # Extract phone numbers
    phones = re.findall(PATTERNS["phone"], text)
    phone_numbers = [re.sub(r'[\s\-]', '', p) for p in phones]
    
    # Extract URLs
    urls = re.findall(PATTERNS["url"], text)
    phishing_links = [url for url in urls if not any(
        safe in url.lower() for safe in ["google.com", "microsoft.com", "apple.com"]
    )]
    
    # Extract keywords
    keywords = [kw for kw in SCAM_KEYWORDS if kw in text_lower]
    
    # Extract emails
    email_addresses = re.findall(PATTERNS["email"], text)
    
    # Extract IDs (we'll roughly classify them based on prefix, or just lump them if LLM isn't taking over)
    # The LLM will do a better job at specific classifications, but we'll grab them broadly.
    raw_ids = re.findall(PATTERNS["id_number"], text, re.IGNORECASE)
    case_ids = [i for i in raw_ids if any(x in i.upper() for x in ["CASE", "REF"])]
    policy_numbers = [i for i in raw_ids if "POL" in i.upper()]
    order_numbers = [i for i in raw_ids if any(x in i.upper() for x in ["ORD", "TRK", "AWB"])]
    
    return ExtractedIntelligence(
        bankAccounts=list(set(bank_accounts)),
        upiIds=list(set(upi_ids)),
        phoneNumbers=list(set(phone_numbers)),
        phishingLinks=list(set(phishing_links)),
        suspiciousKeywords=list(set(keywords)),
        emailAddresses=list(set(email_addresses)),
        caseIds=list(set(case_ids)),
        policyNumbers=list(set(policy_numbers)),
        orderNumbers=list(set(order_numbers))
    )


EXTRACTION_PROMPT = """Extract ALL scam-related intelligence from this conversation.

CONVERSATION:
{conversation}

Look for:
1. Bank account numbers (10-18 digit numbers that look like account numbers)
2. UPI IDs (format: user@bank like abc@ybl, xyz@paytm, 123@okaxis)
3. Phone numbers (Indian format: 10 digits starting with 6-9)
4. URLs/Links (especially suspicious/phishing links)
5. Suspicious keywords (urgency words, financial terms, threats)
6. Email addresses
7. Case IDs or reference numbers
8. Insurance policy numbers
9. Order or tracking numbers

Respond with ONLY valid JSON (no markdown):
{{"bankAccounts": [], "upiIds": [], "phoneNumbers": [], "phishingLinks": [], "suspiciousKeywords": [], "emailAddresses": [], "caseIds": [], "policyNumbers": [], "orderNumbers": []}}"""


async def extract_intelligence(
    conversation_history: List[Dict],
    current_message: str = "",
    use_llm: bool = True
) -> ExtractedIntelligence:
    """
    Extract intelligence using both regex and LLM.
    
    Args:
        conversation_history: All messages in conversation
        current_message: Latest message
        use_llm: Whether to use LLM extraction (set False for regex-only to save costs)
        
    Returns:
        ExtractedIntelligence with all findings
    """
    # Build full text
    all_text = []
    for msg in conversation_history:
        all_text.append(msg.get("text", ""))
    if current_message:
        all_text.append(current_message)
    
    full_text = "\n".join(all_text)
    
    # Method 1: Regex (fast, reliable, always runs)
    regex_intel = extract_with_regex(full_text)
    
    # Method 2: LLM (catches context-dependent info, only when requested)
    if not use_llm:
        logger.info("⏩ Skipping LLM extraction (regex-only this turn to save costs)")
        return regex_intel
    
    try:
        prompt = EXTRACTION_PROMPT.format(conversation=full_text)
        result = await generate_json(
            prompt=prompt,
            model=settings.model_name,
            thinking_level="low"  # Simple extraction task
        )
        
        llm_intel = ExtractedIntelligence(
            bank_accounts=result.get("bankAccounts", []),
            upi_ids=result.get("upiIds", []),
            phone_numbers=result.get("phoneNumbers", []),
            phishing_links=result.get("phishingLinks", []),
            suspicious_keywords=result.get("suspiciousKeywords", []),
            email_addresses=result.get("emailAddresses", []),
            case_ids=result.get("caseIds", []),
            policy_numbers=result.get("policyNumbers", []),
            order_numbers=result.get("orderNumbers", [])
        )
        
        # Merge both results
        combined = regex_intel.merge(llm_intel)
        
    except Exception as e:
        logger.error(f"LLM extraction error: {e}")
        combined = regex_intel
    
    logger.info(f"Extracted: {len(combined.bank_accounts)} accounts, "
                f"{len(combined.upi_ids)} UPIs, {len(combined.phone_numbers)} phones, "
                f"{len(combined.phishing_links)} links")
    
    return combined


NOTES_PROMPT = """Summarize this scam conversation for law enforcement in 1-2 sentences.

CONVERSATION:
{conversation}

EXTRACTED INTELLIGENCE:
- Bank Accounts: {bank_accounts}
- UPI IDs: {upi_ids}
- Phone Numbers: {phone_numbers}
- Links: {links}

Include: scam type, tactics used, intelligence gathered.
Be brief and factual. No JSON, just plain text summary."""


async def generate_notes(
    conversation_history: List[Dict],
    intelligence: ExtractedIntelligence,
    scam_type: str = "unknown"
) -> str:
    """
    Generate summary notes about the scam deterministically from extracted data.
    No LLM call needed - faster, cheaper, and always accurate.
    """
    parts = []
    
    # Scam type
    scam_label = scam_type.replace("_", " ").title() if scam_type != "unknown" else "Suspected"
    parts.append(f"{scam_label} scam detected.")
    
    # Tactics
    tactics = []
    kw_str = " ".join(intelligence.suspiciousKeywords).lower()
    if "urgent" in kw_str or "immediately" in kw_str:
        tactics.append("urgency pressure")
    if "otp" in kw_str:
        tactics.append("OTP harvesting")
    if "block" in kw_str or "suspend" in kw_str:
        tactics.append("account suspension threats")
    if "verify" in kw_str:
        tactics.append("fake identity verification")
    if intelligence.phishingLinks:
        tactics.append("phishing links")
    if intelligence.upiIds:
        tactics.append("payment redirection")
    if tactics:
        parts.append(f"Tactics: {', '.join(tactics)}.")
    
    # Intelligence gathered
    intel_items = []
    if intelligence.phoneNumbers:
        intel_items.append(f"phone(s): {', '.join(intelligence.phoneNumbers)}")
    if intelligence.bankAccounts:
        intel_items.append(f"bank account(s): {', '.join(intelligence.bankAccounts)}")
    if intelligence.upiIds:
        intel_items.append(f"UPI ID(s): {', '.join(intelligence.upiIds)}")
    if intelligence.emailAddresses:
        intel_items.append(f"email(s): {', '.join(intelligence.emailAddresses)}")
    if intelligence.phishingLinks:
        intel_items.append(f"link(s): {', '.join(intelligence.phishingLinks)}")
    
    if intel_items:
        parts.append(f"Intelligence gathered: {'; '.join(intel_items)}.")
    else:
        parts.append("No specific contact intelligence extracted yet.")
    
    notes = " ".join(parts)
    if len(notes) > 300:
        notes = notes[:297] + "..."
    
    return notes
