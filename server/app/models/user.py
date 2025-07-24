from sqlalchemy import Column, String, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from typing import Optional, Dict, Any

from .base import BaseModel, SoftDeleteMixin

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel, SoftDeleteMixin):
    """User model for authentication and profile management"""
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    preferences = Column(JSON, nullable=True)  # User preferences as JSON
    profile_data = Column(Text, nullable=True)  # Additional profile data
    
    # Financial profile
    financial_goals = Column(Text, nullable=True)
    risk_tolerance = Column(String(50), nullable=True)  # conservative, moderate, aggressive
    investment_experience = Column(String(50), nullable=True)
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding sensitive data"""
        data = super().to_dict()
        # Remove sensitive fields
        data.pop('hashed_password', None)
        return data

class UserSession(BaseModel):
    """User session model for tracking active sessions"""
    
    user_id = Column(String(255), nullable=False, index=True)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(String(255), nullable=False)
    
    # Session context
    session_data = Column(JSON, nullable=True)  # Store session-specific data
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        from datetime import datetime
        try:
            expires_at = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.utcnow() > expires_at.replace(tzinfo=None)
        except:
            return True
    
    def extend_session(self, minutes: int = 30):
        """Extend session expiration"""
        from datetime import datetime, timedelta
        new_expiry = datetime.utcnow() + timedelta(minutes=minutes)
        self.expires_at = new_expiry.isoformat()

class ConversationHistory(BaseModel):
    """Store conversation history for context"""
    
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    message_type = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extra_data = Column(JSON, nullable=True)  # Store additional context
    
    # Agent information
    agent_type = Column(String(100), nullable=True)  # Which agent processed this
    agent_response_time = Column(String(50), nullable=True)
    
    def to_chat_format(self) -> Dict[str, Any]:
        """Convert to chat format for AI models"""
        return {
            "role": self.message_type,
            "content": self.content,
            "metadata": self.extra_data or {}
        } 