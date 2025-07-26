import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Try to import Google ADK components ---
try:
    from google.adk.sessions import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai.types import Content, Part
    from financial_advisor import root_agent as finance_agent
    
    # Initialize Google ADK components
    session_service = InMemorySessionService()
    runner = Runner(
        agent=finance_agent,
        app_name="finance_advisor_app",
        session_service=session_service
    )
    GOOGLE_ADK_AVAILABLE = True
    logger.info("✅ Google ADK components loaded successfully")
    
except ImportError as e:
    GOOGLE_ADK_AVAILABLE = False
    logger.warning(f"⚠️ Google ADK not available: {e}")
    logger.info("Running in fallback mode")

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    user_message: str
    user_id: Optional[str] = "user1"
    session_id: Optional[str] = "session1"

class ChatResponse(BaseModel):
    response: str

# --- FastAPI App ---
def create_app():
    """Create FastAPI app instance."""
    return FastAPI(
        title="Financial Advisor API",
        version="1.0.0",
        description="AI-powered financial advisor API"
    )

app = create_app()

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "Financial Advisor API",
        "google_adk_available": GOOGLE_ADK_AVAILABLE
    }

# --- Chat Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Get a response from the finance advisor agent."""
    
    if not GOOGLE_ADK_AVAILABLE:
        # Fallback response when Google ADK is not available
        return ChatResponse(
            response=f"[Fallback Mode] You asked: '{request.user_message}'. "
                     f"Google ADK is not available. Please check your dependencies."
        )
    
    app_name = "finance_advisor_app"
    
    try:
        # Create or retrieve session
        session = await session_service.create_session(
            app_name=app_name,
            user_id=request.user_id,
            session_id=request.session_id
        )
        logger.info(f"Session created/retrieved for user {request.user_id}")

        # Wrap user input for the agent
        message = Content(role="user", parts=[Part(text=request.user_message)])
        logger.info(f"Processing message: {request.user_message}")

        # Run the agent and capture the final response
        last_text = None
        async for event in runner.run(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=message
        ):
            if event.content and event.content.parts:
                last_text = event.content.parts[0].text
                logger.info(f"Agent response: {last_text}")

        # Verify we got a response
        if not last_text:
            logger.error("No response received from agent")
            raise HTTPException(status_code=500, detail="No response from agent")

        return ChatResponse(response=last_text)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# --- Simple Test Endpoint ---
@app.post("/test")
async def test_endpoint(request: ChatRequest) -> ChatResponse:
    """Simple test endpoint that always works."""
    return ChatResponse(response=f"Test successful! You said: {request.user_message}")

# --- Server Startup ---
if __name__ == "__main__":
    print("🚀 Starting Financial Advisor API...")
    uvicorn.run(
        app,  # Pass the app object directly instead of string
        host="0.0.0.0", 
        port=8001,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )

print("✅ API module loaded successfully")