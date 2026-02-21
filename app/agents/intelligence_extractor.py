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

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ExtractedIntelligence:
    """Intelligence extracted from conversation."""
    bank_accounts: List[str] = field(default_factory=list)
    upi_ids: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)
    phishing_links: List[str] = field(default_factory=list)
    suspicious_keywords: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    case_ids: List[str] = field(default_factory=list)
    policy_numbers: List[str] = field(default_factory=list)
    order_numbers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "bankAccounts": self.bank_accounts,
            "upiIds": self.upi_ids,
            "phoneNumbers": self.phone_numbers,
            "phishingLinks": self.phishing_links,
            "suspiciousKeywords": self.suspicious_keywords,
            "emailAddresses": self.email_addresses,
            "caseIds": self.case_ids,
            "policyNumbers": self.policy_numbers,
            "orderNumbers": self.order_numbers
        }
    
    def merge(self, other: "ExtractedIntelligence") -> "ExtractedIntelligence":
        """Merge with another ExtractedIntelligence, deduplicating."""
        return ExtractedIntelligence(
            bank_accounts=list(set(self.bank_accounts + other.bank_accounts)),
            upi_ids=list(set(self.upi_ids + other.upi_ids)),
            phone_numbers=list(set(self.phone_numbers + other.phone_numbers)),
            phishing_links=list(set(self.phishing_links + other.phishing_links)),
            suspicious_keywords=list(set(self.suspicious_keywords + other.suspicious_keywords)),
            email_addresses=list(set(self.email_addresses + other.email_addresses)),
            case_ids=list(set(self.case_ids + other.case_ids)),
            policy_numbers=list(set(self.policy_numbers + other.policy_numbers)),
            order_numbers=list(set(self.order_numbers + other.order_numbers))
        )
    
    def is_empty(self) -> bool:
        return not any([
            self.bank_accounts,
            self.upi_ids,
            self.phone_numbers,
            self.phishing_links,
            self.suspicious_keywords,
            self.email_addresses,
            self.case_ids,
            self.policy_numbers,
            self.order_numbers
        ])


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
        bank_accounts=list(set(bank_accounts)),
        upi_ids=list(set(upi_ids)),
        phone_numbers=list(set(phone_numbers)),
        phishing_links=list(set(phishing_links)),
        suspicious_keywords=list(set(keywords)),
        email_addresses=list(set(email_addresses)),
        case_ids=list(set(case_ids)),
        policy_numbers=list(set(policy_numbers)),
        order_numbers=list(set(order_numbers))
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
    Generate summary notes about the scam.
    
    Args:
        conversation_history: Full conversation
        intelligence: Extracted intelligence
        scam_type: Detected scam type
        
    Returns:
        Summary string
    """
    # Build conversation text
    conv_text = "\n".join([
        f"{msg.get('sender', 'unknown').upper()}: {msg.get('text', '')}"
        for msg in conversation_history[-15:]  # Last 15 messages
    ])
    
    prompt = NOTES_PROMPT.format(
        conversation=conv_text,
        bank_accounts=intelligence.bank_accounts or "None",
        upi_ids=intelligence.upi_ids or "None",
        phone_numbers=intelligence.phone_numbers or "None",
        links=intelligence.phishing_links or "None"
    )
    
    try:
        notes = await generate_text(
            prompt=prompt,
            model=settings.model_name,
            max_tokens=2500
        )
        
        # Clean up
        notes = notes.strip().replace("\n", " ")
        if len(notes) > 300:
            notes = notes[:297] + "..."
        
        return notes
        
    except Exception as e:
        logger.error(f"Notes generation error: {e}")
        
        # Fallback notes
        tactics = []
        if "urgent" in str(intelligence.suspicious_keywords):
            tactics.append("urgency")
        if intelligence.upi_ids:
            tactics.append("payment request")
        if intelligence.phishing_links:
            tactics.append("phishing links")
        
        return f"{scam_type.replace('_', ' ').title()} scam using {', '.join(tactics) if tactics else 'social engineering'}."
