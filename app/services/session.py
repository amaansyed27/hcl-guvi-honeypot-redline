"""
Session Management Service

Handles conversation session storage and retrieval.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from app.config import get_settings
from app.agents.intelligence_extractor import ExtractedIntelligence

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ConversationSession:
    """Represents a conversation session with a scammer."""
    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[dict] = field(default_factory=list)
    scam_detected: bool = False
    scam_type: str = "unknown"
    confidence_level: float = 0.0
    intelligence: Optional[ExtractedIntelligence] = None
    agent_notes: str = ""
    callback_sent: bool = False
    persona_type: str = "elderly"
    
    @property
    def message_count(self) -> int:
        return len(self.messages)
    
    @property
    def duration_seconds(self) -> int:
        """Calculate engagement duration in seconds."""
        if not self.messages:
            return 0
        return int((self.updated_at - self.created_at).total_seconds())
    
    def add_message(self, sender: str, text: str, timestamp = None):
        """Add a message to the conversation."""
        # Handle epoch milliseconds (int) or datetime
        if timestamp is None:
            ts = datetime.utcnow()
        elif isinstance(timestamp, int):
            # Convert epoch milliseconds to datetime
            ts = datetime.utcfromtimestamp(timestamp / 1000)
        else:
            ts = timestamp
        
        self.messages.append({
            "sender": sender,
            "text": text,
            "timestamp": ts.isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        expiry_time = self.updated_at + timedelta(seconds=settings.session_timeout)
        return datetime.utcnow() > expiry_time
    
    def should_send_callback(self) -> bool:
        """Determine if callback should be sent."""
        return self.scam_detected


class SessionStore:
    """
    In-memory session storage.
    
    For production, replace with Redis implementation.
    """
    
    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}
        logger.info("Initialized in-memory session store")
    
    def get(self, session_id: str) -> Optional[ConversationSession]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        
        if session and session.is_expired():
            logger.info(f"Session {session_id} has expired")
            self.delete(session_id)
            return None
            
        return session
    
    def create(self, session_id: str, persona_type: str = "elderly") -> ConversationSession:
        """Create a new session."""
        session = ConversationSession(
            session_id=session_id,
            persona_type=persona_type
        )
        self._sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session
    
    def get_or_create(self, session_id: str, persona_type: str = "elderly") -> ConversationSession:
        """Get existing session or create new one."""
        session = self.get(session_id)
        if session is None:
            session = self.create(session_id, persona_type)
        return session
    
    def update(self, session: ConversationSession):
        """Update a session."""
        session.updated_at = datetime.utcnow()
        self._sessions[session.session_id] = session
    
    def delete(self, session_id: str):
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    def cleanup_expired(self):
        """Remove all expired sessions."""
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            self.delete(sid)
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
    
    def count(self) -> int:
        """Get total number of active sessions."""
        return len(self._sessions)


# Global session store instance
session_store = SessionStore()


# Redis implementation (optional, for production)
class RedisSessionStore:
    """
    Redis-based session storage for production use.
    
    Requires redis package and REDIS_URL environment variable.
    """
    
    def __init__(self, redis_url: str):
        import redis
        self._client = redis.from_url(redis_url)
        self._prefix = "honeypot:session:"
        logger.info(f"Connected to Redis session store")
    
    def _key(self, session_id: str) -> str:
        return f"{self._prefix}{session_id}"
    
    def get(self, session_id: str) -> Optional[ConversationSession]:
        import json
        data = self._client.get(self._key(session_id))
        if data:
            return self._deserialize(json.loads(data))
        return None
    
    def create(self, session_id: str, persona_type: str = "elderly") -> ConversationSession:
        session = ConversationSession(
            session_id=session_id,
            persona_type=persona_type
        )
        self._save(session)
        return session
    
    def get_or_create(self, session_id: str, persona_type: str = "elderly") -> ConversationSession:
        session = self.get(session_id)
        if session is None:
            session = self.create(session_id, persona_type)
        return session
    
    def update(self, session: ConversationSession):
        self._save(session)
    
    def _save(self, session: ConversationSession):
        import json
        data = self._serialize(session)
        self._client.setex(
            self._key(session.session_id),
            settings.session_timeout,
            json.dumps(data)
        )
    
    def _serialize(self, session: ConversationSession) -> dict:
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": session.messages,
            "scam_detected": session.scam_detected,
            "scam_type": session.scam_type,
            "confidence_level": session.confidence_level,
            "intelligence": session.intelligence.to_dict() if session.intelligence else {},
            "agent_notes": session.agent_notes,
            "callback_sent": session.callback_sent,
            "persona_type": session.persona_type
        }
    
    def _deserialize(self, data: dict) -> ConversationSession:
        return ConversationSession(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            messages=data["messages"],
            scam_detected=data["scam_detected"],
            scam_type=data["scam_type"],
            confidence_level=data.get("confidence_level", 0.0),
            intelligence=ExtractedIntelligence(**data["intelligence"]),
            agent_notes=data["agent_notes"],
            callback_sent=data["callback_sent"],
            persona_type=data["persona_type"]
        )
    
    def delete(self, session_id: str):
        self._client.delete(self._key(session_id))
    
    def count(self) -> int:
        keys = self._client.keys(f"{self._prefix}*")
        return len(keys)


def get_session_store() -> SessionStore:
    """
    Get the appropriate session store based on configuration.
    
    Returns Redis store if REDIS_URL is configured, otherwise in-memory.
    """
    global session_store
    
    if settings.redis_url:
        try:
            return RedisSessionStore(settings.redis_url)
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Using in-memory store.")
    
    return session_store
