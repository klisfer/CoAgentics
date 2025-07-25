import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from google.genai.types import Content, Part
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from agent import root_agent
from vertex_ai_manager import vertex_ai_manager, VertexAIManager
from google.adk.runners import Runner
from typing import Optional

# Define an app name for ADK
APP_NAME = "financial_advisor_app"

# --- FastAPI App Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for credentials before initializing
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
        print("Please run 'gcloud auth application-default login' and then set the variable, for example:")
        print("export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json")
        yield
        return

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not project_id:
        print("ERROR: GOOGLE_CLOUD_PROJECT environment variable not set.")
        print("Please create a .env file in the 'backend' directory with the following content:")
        print("GOOGLE_CLOUD_PROJECT=your-gcp-project-id-here")
        # In a real app, you might raise an error or exit
        yield
        return

    try:
        vertex_ai_manager.initialize(project_id=project_id, location=location)
        print("Vertex AI Manager has been initialized.")
    except Exception as e:
        print(f"FATAL: Could not initialize Vertex AI Manager: {e}")
        # In a real app, you might exit or switch to a fallback
    yield
    # Shutdown
    print("Application shutting down...")
    # Clean up resources if necessary, though Vertex AI Agent Engine is managed.

app = FastAPI(
    title="Vertex AI Financial Advisor API",
    version="2.0.0",
    lifespan=lifespan
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    new_message: str = Field(..., description="The user's message text.")

class ChatResponse(BaseModel):
    session_id: str
    response_text: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str

# --- Dependency for ADK Runner ---
def get_runner() -> Runner:
    if not vertex_ai_manager._initialized:
        raise HTTPException(status_code=503, detail="Vertex AI Service is not available.")
    
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=vertex_ai_manager.get_session_service(),
        memory_service=vertex_ai_manager.get_memory_service(),
    )

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, runner: Runner = Depends(get_runner)):
    """Handles a chat turn, managing session and memory with Vertex AI."""
    session_service = vertex_ai_manager.get_session_service()
    memory_service = vertex_ai_manager.get_memory_service()
    session_id = request.session_id
    
    try:
        # 1. Get or create the session
        if session_id:
            session = await session_service.get_session(
                app_name=APP_NAME, user_id=request.user_id, session_id=session_id
            )
            if not session:
                raise HTTPException(status_code=404, detail="Session not found.")
        else:
            session = await session_service.create_session(
                app_name=APP_NAME, user_id=request.user_id
            )
        
        session_id = session.id

        # 2. Run the ADK agent
        content = Content(role='user', parts=[Part(text=request.new_message)])
        events = runner.run(
            user_id=request.user_id, session_id=session_id, new_message=content
        )

        final_response = "Sorry, I encountered an issue and couldn't process your request."
        for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break

        # 3. Add the completed session to the Memory Bank
        # This allows the agent to learn from this conversation in the future
        updated_session = await session_service.get_session(
            app_name=APP_NAME, user_id=request.user_id, session_id=session_id
        )
        await memory_service.add_session_to_memory(updated_session)

        return ChatResponse(session_id=session_id, response_text=final_response)

    except Exception as e:
        # Log the full exception for debugging
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during chat processing.")

@app.post("/create_session", response_model=SessionResponse)
async def create_session(user_id: str):
    """Explicitly creates a new session for a user."""
    session_service = vertex_ai_manager.get_session_service()
    try:
        session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
        return SessionResponse(session_id=session.id, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "financial-advisor-v2", "vertex_ai_initialized": vertex_ai_manager._initialized}

if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("ERROR: The 'GOOGLE_CLOUD_PROJECT' environment variable is required.")
        print("Please create a .env file in the 'backend' directory with:")
        print("GOOGLE_CLOUD_PROJECT=your-gcp-project-id-here")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000) 

