import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.genai.types import Content, Part
from backend.agent import root_agent
from backend.session_manager import session_manager
from typing import Optional, Dict, Any

app = FastAPI(title="Financial Advisor API", version="1.0.0")

class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None  # If None, create new session
    new_message: dict

class SessionCreateRequest(BaseModel):
    user_id: str

class SessionUpdateRequest(BaseModel):
    session_id: str
    state_updates: Dict[str, Any]

@app.post("/session/create")
async def create_session(request: SessionCreateRequest) -> dict:
    """Create a new conversation session."""
    try:
        session = session_manager.create_session(request.user_id)
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str) -> dict:
    """Get session information and context."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat(),
        "last_updated": session.last_updated.isoformat(),
        "conversation_stage": session.state.conversation_stage,
        "message_count": len(session.conversation_history),
        "context_summary": session.get_context_summary()
    }

@app.post("/session/update")
async def update_session(request: SessionUpdateRequest) -> dict:
    """Update session state with new information."""
    success = session_manager.update_session_state(
        request.session_id, 
        **request.state_updates
    )
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "updated", "session_id": request.session_id}

@app.get("/user/{user_id}/sessions")
async def get_user_sessions(user_id: str) -> dict:
    """Get all sessions for a user."""
    sessions = session_manager.get_user_sessions(user_id)
    return {
        "user_id": user_id,
        "session_count": len(sessions),
        "sessions": [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat(),
                "last_updated": s.last_updated.isoformat(),
                "stage": s.state.conversation_stage,
                "message_count": len(s.conversation_history)
            }
            for s in sessions
        ]
    }

@app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """Main chat endpoint with session management."""
    try:
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = session_manager.create_session(request.user_id)
        
        # Extract user message
        user_message_text = request.new_message["parts"][0]["text"]
        
        # Add user message to session
        session_manager.add_conversation_message(
            session.session_id, 
            "user", 
            user_message_text
        )
        
        # Get conversation context for the agent
        context = session_manager.get_conversation_context(session.session_id)
        
        # Prepare conversation history for the agent
        history = []
        for msg in session.conversation_history[-10:]:  # Last 10 messages for context
            role = "user" if msg["role"] == "user" else "model"
            history.append(Content(role=role, parts=[Part(text=msg["content"])]))
        
        # Add current user message
        history.append(Content(role="user", parts=[Part(text=user_message_text)]))
        
        # Add context to the agent's prompt if available
        if context:
            context_message = f"Previous conversation context:\n{context}\n\nUser message: {user_message_text}"
            history[-1] = Content(role="user", parts=[Part(text=context_message)])
        
        # Get response from agent
        response_text = ""
        try:
            response = root_agent.run(history)
            response_text = response["output"]
            
            # Add agent response to session
            session_manager.add_conversation_message(
                session.session_id,
                "assistant",
                response_text,
                {"agent": "root_agent"}
            )
            
            # Update session state based on response
            # You can enhance this to parse agent responses and update state accordingly
            session_manager.update_session_state(
                session.session_id,
                last_interaction=user_message_text
            )
            
        except Exception as e:
            response_text = f"Error: {e}"
            session_manager.add_conversation_message(
                session.session_id,
                "assistant",
                response_text,
                {"error": True}
            )

        return {
            "session_id": session.session_id,
            "new_events": [{"content": {"parts": [{"text": response_text}]}}],
            "conversation_stage": session.state.conversation_stage,
            "context_available": bool(context)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.post("/session/{session_id}/archive")
async def archive_session(session_id: str) -> dict:
    """Archive a completed session."""
    success = session_manager.archive_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "archived", "session_id": session_id}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "financial-advisor"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 

