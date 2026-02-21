"""
Pydantic Response Models

Defines the structure for API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.intelligence import ExtractedIntelligence


class EngagementMetrics(BaseModel):
    """Metrics about the honeypot engagement."""
    engagementDurationSeconds: int = Field(
        default=0,
        description="Total engagement time in seconds"
    )
    totalMessagesExchanged: int = Field(
        default=0,
        description="Number of messages exchanged in the session"
    )


class HoneypotResponse(BaseModel):
    """
    Response from the honeypot API.
    
    Returns scam detection status, engagement metrics, and extracted intelligence.
    """
    status: str = Field(default="success", description="Response status: 'success' or 'error'")
    scamDetected: bool = Field(..., description="Whether scam intent was detected")
    agentResponse: Optional[str] = Field(
        default=None,
        description="The honeypot agent's response to continue the conversation"
    )
    reply: Optional[str] = Field(
        default=None,
        description="Compatibility field: agent reply"
    )
    message: Optional[str] = Field(
        default=None,
        description="Compatibility alias for reply"
    )
    text: Optional[str] = Field(
        default=None,
        description="Compatibility alias for reply"
    )
    engagementMetrics: EngagementMetrics = Field(
        default_factory=EngagementMetrics,
        description="Engagement statistics"
    )
    extractedIntelligence: ExtractedIntelligence = Field(
        default_factory=ExtractedIntelligence,
        description="Intelligence extracted from the conversation"
    )
    agentNotes: Optional[str] = Field(
        default=None,
        description="Summary of scammer behavior and tactics observed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "scamDetected": True,
                "agentResponse": "Oh no, what should I do? How do I verify my account?",
                "engagementMetrics": {
                    "engagementDurationSeconds": 420,
                    "totalMessagesExchanged": 18
                },
                "extractedIntelligence": {
                    "bankAccounts": ["XXXX-XXXX-XXXX"],
                    "upiIds": ["scammer@upi"],
                    "phishingLinks": ["http://malicious-link.example"],
                    "phoneNumbers": ["+91XXXXXXXXXX"],
                    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
                },
                "agentNotes": "Scammer used urgency tactics and payment redirection"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field(default="error")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
