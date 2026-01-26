"""
Extraction Tools for ADK Agents

Contains function tools for extracting intelligence from scam conversations.
Uses regex patterns and LLM-assisted extraction.
"""

import re
from typing import List
from app.models.intelligence import ExtractedIntelligence


# ============================================
# REGEX PATTERNS
# ============================================

# Bank Account Patterns (Indian formats)
BANK_ACCOUNT_PATTERNS = [
    r'\b\d{9,18}\b',  # 9-18 digit account numbers
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{0,4}\b',  # Formatted with dashes/spaces
    r'(?:account|a/c|ac)[\s:]*#?[\s]*(\d{9,18})',  # Prefixed with "account"
]

# UPI ID Patterns
UPI_PATTERNS = [
    r'\b[a-zA-Z0-9._-]+@[a-zA-Z]+\b',  # user@bank format
    r'\b[a-zA-Z0-9._-]+@(upi|paytm|gpay|phonepe|okaxis|okhdfcbank|oksbi|ybl|apl|ibl)\b',
]

# Phone Number Patterns (Indian)
PHONE_PATTERNS = [
    r'\+91[\s-]?\d{10}\b',  # +91 format
    r'\b91[\s-]?\d{10}\b',  # 91 prefix
    r'\b0?\d{10}\b',  # 10 digit
    r'\b\d{5}[\s-]?\d{5}\b',  # Formatted with space/dash
]

# URL Patterns
URL_PATTERNS = [
    r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard URLs
    r'www\.[^\s<>"{}|\\^`\[\]]+',  # www. URLs
    r'\b[a-zA-Z0-9-]+\.(com|in|org|net|xyz|tk|ml|ga|cf|gq|top|buzz|click|link|info)[^\s]*',  # Domain patterns
]

# Suspicious Keywords
SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately", "verify", "blocked", "suspended", "otp", 
    "kyc", "update", "expire", "warning", "alert", "confirm",
    "prize", "lottery", "winner", "claim", "reward", "bonus",
    "refund", "cashback", "offer", "limited time", "act now",
    "bank", "account", "transfer", "payment", "upi", "paytm",
    "link", "click", "download", "install", "app",
    "police", "legal", "arrest", "court", "case",
    "tax", "income tax", "gst", "penalty", "fine"
]


# ============================================
# EXTRACTION FUNCTIONS (ADK Tools)
# ============================================

def extract_bank_accounts(text: str) -> dict:
    """
    Extract bank account numbers from text.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        Dictionary with extracted bank account numbers
    """
    accounts = set()
    for pattern in BANK_ACCOUNT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean and validate
            clean = re.sub(r'[\s-]', '', str(match))
            if 9 <= len(clean) <= 18 and clean.isdigit():
                accounts.add(clean)
    
    return {
        "status": "success",
        "bank_accounts": list(accounts),
        "count": len(accounts)
    }


def extract_upi_ids(text: str) -> dict:
    """
    Extract UPI IDs from text.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        Dictionary with extracted UPI IDs
    """
    upi_ids = set()
    for pattern in UPI_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                continue  # Skip group matches
            # Validate UPI format
            if '@' in match:
                upi_ids.add(match.lower())
    
    return {
        "status": "success",
        "upi_ids": list(upi_ids),
        "count": len(upi_ids)
    }


def extract_phone_numbers(text: str) -> dict:
    """
    Extract phone numbers from text.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        Dictionary with extracted phone numbers
    """
    phones = set()
    for pattern in PHONE_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean and format
            clean = re.sub(r'[\s-]', '', str(match))
            # Normalize to +91 format
            if len(clean) == 10:
                clean = "+91" + clean
            elif len(clean) == 12 and clean.startswith("91"):
                clean = "+" + clean
            elif len(clean) == 11 and clean.startswith("0"):
                clean = "+91" + clean[1:]
            
            if len(clean) == 13 and clean.startswith("+91"):
                phones.add(clean)
    
    return {
        "status": "success",
        "phone_numbers": list(phones),
        "count": len(phones)
    }


def extract_urls(text: str) -> dict:
    """
    Extract URLs and potential phishing links from text.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        Dictionary with extracted URLs
    """
    urls = set()
    for pattern in URL_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            url = match.lower()
            # Add http:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            urls.add(url)
    
    return {
        "status": "success",
        "urls": list(urls),
        "count": len(urls)
    }


def extract_suspicious_keywords(text: str) -> dict:
    """
    Extract suspicious keywords indicating scam tactics.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        Dictionary with found suspicious keywords
    """
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    return {
        "status": "success",
        "keywords": found_keywords,
        "count": len(found_keywords)
    }


def extract_all_intelligence(text: str) -> ExtractedIntelligence:
    """
    Extract all intelligence from text in one call.
    
    Args:
        text: The conversation text to analyze
        
    Returns:
        ExtractedIntelligence object with all extracted data
    """
    bank_result = extract_bank_accounts(text)
    upi_result = extract_upi_ids(text)
    phone_result = extract_phone_numbers(text)
    url_result = extract_urls(text)
    keyword_result = extract_suspicious_keywords(text)
    
    return ExtractedIntelligence(
        bankAccounts=bank_result["bank_accounts"],
        upiIds=upi_result["upi_ids"],
        phoneNumbers=phone_result["phone_numbers"],
        phishingLinks=url_result["urls"],
        suspiciousKeywords=keyword_result["keywords"]
    )


# ============================================
# ADK TOOL DEFINITIONS
# ============================================

# These functions are designed to be used directly as ADK tools
# The docstrings are used by Gemini to understand the tool purpose

EXTRACTION_TOOLS = [
    extract_bank_accounts,
    extract_upi_ids,
    extract_phone_numbers,
    extract_urls,
    extract_suspicious_keywords
]
