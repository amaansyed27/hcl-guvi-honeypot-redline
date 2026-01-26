"""
Pytest Configuration and Fixtures
"""

import pytest
from fastapi.testclient import TestClient
import os

# Set test environment variables
os.environ["API_KEY"] = "test-api-key"
os.environ["GOOGLE_API_KEY"] = "test-google-key"

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers with valid API key."""
    return {"x-api-key": "test-api-key"}


@pytest.fixture
def sample_scam_message():
    """Sample scam message request."""
    return {
        "sessionId": "test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Share OTP immediately to verify.",
            "timestamp": "2026-01-27T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }


@pytest.fixture
def sample_legitimate_message():
    """Sample non-scam message request."""
    return {
        "sessionId": "test-session-002",
        "message": {
            "sender": "scammer",
            "text": "Hello, I wanted to ask about your working hours.",
            "timestamp": "2026-01-27T10:15:30Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "Chat",
            "language": "English",
            "locale": "IN"
        }
    }


@pytest.fixture
def sample_conversation_history():
    """Sample conversation with history."""
    return {
        "sessionId": "test-session-003",
        "message": {
            "sender": "scammer",
            "text": "Send money to upi@ybl immediately or account will be frozen.",
            "timestamp": "2026-01-27T10:17:30Z"
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account has suspicious activity.",
                "timestamp": "2026-01-27T10:15:30Z"
            },
            {
                "sender": "user",
                "text": "What? What happened to my account?",
                "timestamp": "2026-01-27T10:16:00Z"
            }
        ],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
