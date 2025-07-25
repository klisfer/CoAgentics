"""Session management for financial advisor conversations."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

@dataclass
class ConversationState:
    """Manages state within a conversation session."""
    user_profile: Dict[str, Any] = field(default_factory=dict)
    financial_context: Dict[str, Any] = field(default_factory=dict)
    conversation_stage: str = "initial"  # initial, clarifying, analyzing, optimizing
    pending_questions: List[str] = field(default_factory=list)
    agent_responses: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_user_profile(self, key: str, value: Any):
        """Update user profile information."""
        self.user_profile[key] = value
    
    def update_financial_context(self, key: str, value: Any):
        """Update financial context information."""
        self.financial_context[key] = value
    
    def add_pending_question(self, question: str):
        """Add a question that needs user response."""
        self.pending_questions.append(question)
    
    def clear_pending_questions(self):
        """Clear all pending questions."""
        self.pending_questions.clear()
    
    def add_agent_response(self, agent_name: str, response: str, metadata: Dict[str, Any] = None):
        """Record agent response for context."""
        self.agent_responses.append({
            "agent": agent_name,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })

@dataclass
class FinancialSession:
    """Represents a single conversation session with financial context."""
    session_id: str
    user_id: str
    created_at: datetime
    last_updated: datetime
    state: ConversationState
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.last_updated = datetime.now()
    
    def get_context_summary(self) -> str:
        """Generate a context summary for agents."""
        context = []
        
        # User profile context
        if self.state.user_profile:
            context.append("User Profile:")
            for key, value in self.state.user_profile.items():
                context.append(f"  - {key}: {value}")
        
        # Financial context
        if self.state.financial_context:
            context.append("Financial Context:")
            for key, value in self.state.financial_context.items():
                context.append(f"  - {key}: {value}")
        
        # Conversation stage
        context.append(f"Conversation Stage: {self.state.conversation_stage}")
        
        # Previous agent responses
        if self.state.agent_responses:
            context.append("Previous Agent Responses:")
            for response in self.state.agent_responses[-3:]:  # Last 3 responses
                context.append(f"  - {response['agent']}: {response['response'][:100]}...")
        
        return "\n".join(context)

class SessionManager:
    """Manages financial advisor conversation sessions."""
    
    def __init__(self):
        # In-memory storage for development/testing
        # In production, this would use a persistent storage backend
        self.sessions: Dict[str, FinancialSession] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
    
    def create_session(self, user_id: str) -> FinancialSession:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = FinancialSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_updated=now,
            state=ConversationState()
        )
        
        self.sessions[session_id] = session
        
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[FinancialSession]:
        """Retrieve a session by ID."""
        return self.sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[FinancialSession]:
        """Get all sessions for a user."""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    def update_session_state(self, session_id: str, **state_updates) -> bool:
        """Update session state with new information."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        for key, value in state_updates.items():
            if hasattr(session.state, key):
                setattr(session.state, key, value)
            elif key.startswith('user_'):
                session.state.update_user_profile(key[5:], value)
            elif key.startswith('financial_'):
                session.state.update_financial_context(key[10:], value)
        
        session.last_updated = datetime.now()
        return True
    
    def add_conversation_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a message to the conversation."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.add_message(role, content, metadata)
        return True
    
    def get_conversation_context(self, session_id: str) -> Optional[str]:
        """Get formatted context for agent processing."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.get_context_summary()
    
    def archive_session(self, session_id: str) -> bool:
        """Archive a completed session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # In a full implementation, this would save to long-term memory
        # For now, we just mark it as archived
        session.state.conversation_stage = "archived"
        return True

# Global session manager instance
session_manager = SessionManager() 