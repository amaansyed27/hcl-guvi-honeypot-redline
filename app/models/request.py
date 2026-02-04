"""
Pydantic Request Models

Defines the structure for incoming API requests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime


class Message(BaseModel):
    """A single message in the conversation."""
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Union[int, datetime] = Field(..., description="Timestamp (epoch ms or ISO-8601)")


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    channel: Optional[str] = Field(default="SMS", description="Communication channel: SMS/WhatsApp/Email/Chat")
    language: Optional[str] = Field(default="English", description="Language used")
    locale: Optional[str] = Field(default="IN", description="Country or region code")


class HoneypotRequest(BaseModel):
    """
    Incoming request to the honeypot API.
    
    Each request represents one incoming message in a conversation.
    """
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="The latest incoming message")
    conversationHistory: List[Message] = Field(
        default_factory=list,
        description="Previous messages in the conversation (empty for first message)"
    )
    metadata: Optional[Metadata] = Field(default=None, description="Optional conversation metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "wertyu-dfghj-ertyui",
                "message": {
                    "sender": "scammer",
                    "text": "Your bank account will be blocked today. Verify immediately.",
                    "timestamp": "2026-01-21T10:15:30Z"
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
        }
