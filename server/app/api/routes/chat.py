from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
import logging

from app.core.database import get_db
from app.models.user import User, ConversationHistory, UserSession
from app.agents.base import AgentContext, AgentMessage
from app.agents.planning.master_planner import MasterPlannerAgent
from app.agents.financial.financial_assistant import FinancialAssistant
from app.services.orchestration.agent_manager import AgentManager
from app.api.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    metadata: Optional[Dict[str, Any]] = None
    conversation_id: str
    session_id: str

class ConversationHistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]
    total_count: int

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the AI agent system"""
    try:
        # Get or create session
        session_id = str(uuid.uuid4())
        
        # Create agent context
        context = AgentContext(
            user_id=str(current_user.id),
            session_id=session_id,
            user_preferences=current_user.preferences or {},
            financial_profile={
                "risk_tolerance": current_user.risk_tolerance,
                "investment_experience": current_user.investment_experience,
                "financial_goals": current_user.financial_goals
            },
            context_data=chat_message.context or {}
        )
        
        # Get recent conversation history
        recent_conversations = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == str(current_user.id)
        ).order_by(ConversationHistory.created_at.desc()).limit(10).all()
        
        # Add to context
        for conv in reversed(recent_conversations):
            context.conversation_history.append(
                AgentMessage(
                    content=conv.content,
                    message_type=conv.message_type,
                    metadata=conv.extra_data or {}
                )
            )
        
        # Initialize agent manager and get response
        agent_manager = AgentManager()
        response = await agent_manager.process_message(chat_message.message, context)
        
        # Generate conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Store conversation in background
        background_tasks.add_task(
            store_conversation,
            db, 
            str(current_user.id),
            session_id,
            chat_message.message,
            response.content,
            response.metadata,
            response.agent_id
        )
        
        return ChatResponse(
            response=response.content,
            agent_used=response.agent_id or "unknown",
            metadata=response.metadata,
            conversation_id=conversation_id,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
        )

@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history for the current user"""
    try:
        conversations = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == str(current_user.id)
        ).order_by(
            ConversationHistory.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        total_count = db.query(ConversationHistory).filter(
            ConversationHistory.user_id == str(current_user.id)
        ).count()
        
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                "id": conv.id,
                "content": conv.content,
                "message_type": conv.message_type,
                "agent_type": conv.agent_type,
                "created_at": conv.created_at.isoformat(),
                "metadata": conv.extra_data
            })
        
        return ConversationHistoryResponse(
            conversations=formatted_conversations,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving conversation history"
        )

@router.delete("/history/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific conversation"""
    try:
        conversation = db.query(ConversationHistory).filter(
            ConversationHistory.id == conversation_id,
            ConversationHistory.user_id == str(current_user.id)
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting conversation"
        )

@router.post("/clear-history")
async def clear_conversation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all conversation history for the current user"""
    try:
        db.query(ConversationHistory).filter(
            ConversationHistory.user_id == str(current_user.id)
        ).delete()
        db.commit()
        
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error clearing conversation history"
        )

@router.get("/agents/status")
async def get_agent_status(current_user: User = Depends(get_current_user)):
    """Get status of all available agents"""
    try:
        agent_manager = AgentManager()
        status = agent_manager.get_all_agent_status()
        
        return {
            "agents": status,
            "total_agents": len(status),
            "available_agents": len([a for a in status if a.get("status") == "idle"])
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving agent status"
        )

async def store_conversation(
    db: Session,
    user_id: str,
    session_id: str,
    user_message: str,
    agent_response: str,
    metadata: Optional[Dict[str, Any]],
    agent_type: Optional[str]
):
    """Background task to store conversation in database"""
    try:
        # Store user message
        user_conv = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            message_type="user",
            content=user_message,
            extra_data=metadata,
            agent_type=agent_type
        )
        db.add(user_conv)
        
        # Store agent response
        agent_conv = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            message_type="assistant",
            content=agent_response,
            extra_data=metadata,
            agent_type=agent_type
        )
        db.add(agent_conv)
        
        db.commit()
        logger.info(f"Stored conversation for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing conversation: {e}")
        db.rollback() 