"""
Intelligence Extraction Models

Defines the structure for extracted scam intelligence.
"""

from pydantic import BaseModel, Field
from typing import List


class ExtractedIntelligence(BaseModel):
    """
    Intelligence extracted from scam conversations.
    
    Contains bank accounts, UPI IDs, phishing links, phone numbers,
    and suspicious keywords identified during the engagement.
    """
    bankAccounts: List[str] = Field(
        default_factory=list,
        description="Bank account numbers extracted from conversation"
    )
    upiIds: List[str] = Field(
        default_factory=list,
        description="UPI IDs extracted (format: user@bank)"
    )
    phishingLinks: List[str] = Field(
        default_factory=list,
        description="Suspicious URLs and phishing links"
    )
    phoneNumbers: List[str] = Field(
        default_factory=list,
        description="Phone numbers mentioned by scammer"
    )
    suspiciousKeywords: List[str] = Field(
        default_factory=list,
        description="Keywords indicating scam tactics"
    )
    
    def is_empty(self) -> bool:
        """Check if any intelligence has been extracted."""
        return (
            len(self.bankAccounts) == 0 and
            len(self.upiIds) == 0 and
            len(self.phishingLinks) == 0 and
            len(self.phoneNumbers) == 0 and
            len(self.suspiciousKeywords) == 0
        )
    
    def merge(self, other: "ExtractedIntelligence") -> "ExtractedIntelligence":
        """Merge intelligence from another extraction."""
        return ExtractedIntelligence(
            bankAccounts=list(set(self.bankAccounts + other.bankAccounts)),
            upiIds=list(set(self.upiIds + other.upiIds)),
            phishingLinks=list(set(self.phishingLinks + other.phishingLinks)),
            phoneNumbers=list(set(self.phoneNumbers + other.phoneNumbers)),
            suspiciousKeywords=list(set(self.suspiciousKeywords + other.suspiciousKeywords))
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for GUVI callback."""
        return {
            "bankAccounts": self.bankAccounts,
            "upiIds": self.upiIds,
            "phishingLinks": self.phishingLinks,
            "phoneNumbers": self.phoneNumbers,
            "suspiciousKeywords": self.suspiciousKeywords
        }


class ScamAnalysis(BaseModel):
    """Result of scam detection analysis."""
    is_scam: bool = Field(..., description="Whether the message is a scam")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    indicators: List[str] = Field(
        default_factory=list,
        description="Scam indicators found in the message"
    )
    scam_type: str = Field(
        default="unknown",
        description="Type of scam: bank_fraud, upi_fraud, phishing, fake_offer, unknown"
    )
