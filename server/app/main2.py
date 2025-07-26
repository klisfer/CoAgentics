# fi_fastapi_client.py
import os
import uvicorn
import logging
import asyncio
import traceback

from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, Dict, Any
from utils.timing import start_request_timing, time_operation, log_timing_summary

from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset, 
    SseConnectionParams,
    StreamableHTTPConnectionParams
)

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
from financial_advisor import prompt
from financial_advisor.sub_agents.tax_assistant import tax_consultant_agent
from financial_advisor.sub_agents.investment_assistant import investment_advisor_agent
from financial_advisor.sub_agents.insurance_assistant import insurance_advisor_agent
from financial_advisor.sub_agents.finance_genie_assistant import web_search_agent
from services.context.vertex_ai_session_manager import vertex_ai_manager, VertexAIManager
from google.adk.runners import Runner

MODEL = "gemini-2.5-flash"

# --- Configuration ---
load_dotenv()
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables for core services only
fi_agent = None
fi_toolset = None
initialization_error = None
artifacts_service = InMemoryArtifactService()

# Single global in-memory session service instance
global_inmemory_session_service = None

APP_NAME = os.environ.get("GOOGLE_CLOUD_PROJECT", "fi_mcp_app")


class UserProfile(BaseModel):
    uid: str
    email: str
    name: str
    age: int
    gender: str
    maritalStatus: str
    employmentStatus: str
    industryType: Optional[str] = None
    monthlyIncome: int
    dependents: Dict[str, bool]
    kidsCount: Optional[int] = None
    location: Dict[str, str]
    insurance: Dict[str, bool]
    insuranceCoverage: Dict[str, int]
    profileCompleted: bool

class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    user_message: str = Field(..., description="The user's message text.")
    user_profile: Optional[UserProfile] = None

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    timing_info: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    user_id: str


def get_session_service_and_app_name():
    """
    Get the appropriate session service and app name.
    Returns tuple of (session_service, app_name, is_vertex_ai).
    Falls back to in-memory if Vertex AI is not available.
    """
    global global_inmemory_session_service
    
    try:
        # Try to use Vertex AI session service
        session_service = vertex_ai_manager.get_session_service()
        app_name = vertex_ai_manager.agent_engine_id or APP_NAME  # Use the reasoning engine ID
        logger.info("Using Vertex AI session service")
        return session_service, app_name, True
    except (RuntimeError, AttributeError) as e:
        # Fall back to in-memory session service
        logger.info(f"Vertex AI not available, using in-memory session service: {str(e)}")
        if global_inmemory_session_service is None:
            global_inmemory_session_service = InMemorySessionService()
            logger.info("Created global in-memory session service")
        return global_inmemory_session_service, APP_NAME, False


async def get_or_create_session(session_service, app_name, user_id, session_id=None):
    """
    Get existing session or create new one.
    Handles both Vertex AI and in-memory session services uniformly.
    """
    try:
        if session_id:
            # Try to get existing session
            logger.info(f"Looking for existing session: {session_id}")
            session = await session_service.get_session(
                app_name=app_name, 
                user_id=user_id, 
                session_id=session_id
            )
            
            if session:
                logger.info(f"Retrieved existing session: {session.id}")
                return session
            else:
                logger.warning(f"Session {session_id} not found, creating new one")
        
        # Create new session
        logger.info("Creating new session")
        session = await session_service.create_session(
            app_name=app_name, 
            user_id=user_id
        )
        logger.info(f"Created new session: {session.id}")
        return session
        
    except Exception as e:
        logger.error(f"Error with session management: {e}")
        # Create new session as fallback
        logger.info("Creating new session due to error")
        session = await session_service.create_session(
            app_name=app_name, 
            user_id=user_id
        )
        logger.info(f"Created fallback session: {session.id}")
        return session


async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the Fi MCP Server."""
    try:
        logger.info("Attempting to connect to Fi MCP server...")
        
        # Try StreamableHTTPConnectionParams first
        connection_params = StreamableHTTPConnectionParams(
            url="http://localhost:8080/mcp/stream"
        )
        
        # Create the MCPToolset with timeout
        toolset = MCPToolset(
            connection_params=connection_params,
            tool_filter=None
        )
        
        # Get tools from the toolset with timeout
        try:
            # Add a timeout to prevent hanging
            tools = await asyncio.wait_for(toolset.get_tools(), timeout=10.0)
            logger.info(f"Successfully fetched {len(tools)} tools from Fi MCP server.")
            
            if not tools:
                logger.warning("No tools were returned from Fi MCP server")
                tools = []
            
            logger.info(f"Successfully fetched {toolset} toolset from Fi MCP server.")
            
        except asyncio.TimeoutError:
            logger.error("Timeout while fetching tools from Fi MCP server")
            tools = []
            toolset = None
        except Exception as e:
            logger.error(f"Error fetching tools from Fi MCP server: {e}")
            tools = []
            toolset = None
        
        # Create the agent with available tools
        # web_search_tool = google_search
        tax_assistant_tool = AgentTool(agent=tax_consultant_agent)
        investment_advisor_tool = AgentTool(agent=investment_advisor_agent)
        insurance_advisor_tool = AgentTool(agent=insurance_advisor_agent)
        web_search_agent_tool = AgentTool(agent=web_search_agent)
        
        # Combine all tools
        all_tools = [
            # web_search_tool,
            tax_assistant_tool, 
            investment_advisor_tool,
            insurance_advisor_tool,
            web_search_agent_tool
        ] + tools  # Add MCP tools if available
        
        # Create the main agent
        fi_agent = LlmAgent(
            model=MODEL,
            name="financial_advisor",
            description="Fi: Your AI-powered financial advisor specializing in comprehensive financial planning.",
            instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
            tools=all_tools
        )
        
        logger.info("Fi agent created successfully")
        return fi_agent, toolset
        
    except Exception as e:
        logger.error(f"Failed to create Fi agent: {e}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global fi_agent, fi_toolset, initialization_error
    logger.info("===== Application startup started =====")
    
    try:
        # Initialize Vertex AI Manager
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if project_id:
            try:
                vertex_ai_manager.initialize(project_id=project_id, location=location)
                logger.info("Vertex AI Manager initialized successfully")
            except Exception as e:
                logger.warning(f"Vertex AI Manager initialization failed: {e}")
                logger.info("Will fall back to in-memory session service")
        else:
            logger.info("No Google Cloud project configured, using in-memory session service")
        
        # Initialize Fi agent
        fi_agent, fi_toolset = await get_agent_async()
        
        logger.info("===== Application startup completed =====")
        logger.info(f"Fi agent available: {fi_agent is not None}")
        logger.info(f"Initialization error: {initialization_error}")
        
    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
        initialization_error = str(e)
        # Don't raise - let FastAPI handle it gracefully
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    if fi_toolset:
        try:
            await fi_toolset.close()
            logger.info("Fi MCP toolset closed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# --- FastAPI App ---
app = FastAPI(
    title="Fi Financial Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Get a response from the Fi financial assistant agent."""
    global fi_agent, initialization_error
    
    # Start timing the entire request
    start_request_timing()
    
    logger.info(f"Chat request started - User: {request.user_id}, Session: {request.session_id}, Message: '{request.user_message[:50]}...'")
    
    if initialization_error:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {initialization_error}")
    
    if not fi_agent:
        raise HTTPException(status_code=503, detail="Fi agent not initialized")
    
    try:
        # Get session service and app name
        with time_operation("session_service_initialization"):
            session_service, app_name, is_vertex_ai = get_session_service_and_app_name()
        
        # Get or create session
        with time_operation("session_management"):
            session = await get_or_create_session(
                session_service=session_service,
                app_name=app_name,
                user_id=request.user_id,
                session_id=request.session_id
            )
        
        logger.info(f"User Query: '{request.user_message}'")
        
        # Log user profile data if provided
        if request.user_profile:
            logger.info(f"User Profile Data received:")
            logger.info(f"  Name: {request.user_profile.name}")
            logger.info(f"  Age: {request.user_profile.age}")
            logger.info(f"  Gender: {request.user_profile.gender}")
            logger.info(f"  Marital Status: {request.user_profile.maritalStatus}")
            logger.info(f"  Employment Status: {request.user_profile.employmentStatus}")
            logger.info(f"  Monthly Income: ₹{request.user_profile.monthlyIncome}")
            logger.info(f"  Industry Type: {request.user_profile.industryType}")
            logger.info(f"  Location: {request.user_profile.location}")
            logger.info(f"  Dependents: {request.user_profile.dependents}")
            logger.info(f"  Kids Count: {request.user_profile.kidsCount}")
            logger.info(f"  Insurance: {request.user_profile.insurance}")
            logger.info(f"  Insurance Coverage: {request.user_profile.insuranceCoverage}")
        else:
            logger.info("No user profile data provided in request")
        
        # Create runner
        with time_operation("runner_initialization"):
            runner = Runner(
                app_name=app_name,
                agent=fi_agent,
                artifact_service=artifacts_service,
                session_service=session_service,
            )
        
        # Prepare user message
        with time_operation("message_preparation"):
            content = types.Content(role='user', parts=[types.Part(text=request.user_message)])
        
        # Run agent with timeout
        logger.info("Running Fi agent...")
        with time_operation("agent_execution"):
            events_async = runner.run_async(
                session_id=session.id,
                user_id=request.user_id,
                new_message=content
            )
            
            response_text = ""
            async for event in events_async:
                logger.info(f"Event received: {type(event)}")
                if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                    if event.content.parts and hasattr(event.content.parts[0], 'text'):
                        response_text = event.content.parts[0].text
            
            if not response_text:
                response_text = "I apologize, but I couldn't generate a response at this time."
        
        # Update session in memory (background task - don't wait for it)
        async def update_session_memory_background():
            """Background task to update session memory without blocking response."""
            try:
                logger.info("Background: Session memory update skipped (memory service disabled)")
            except Exception as e:
                logger.error(f"Background: Error updating session memory: {e}")
        
        # Start background task but don't wait for it
        asyncio.create_task(update_session_memory_background())
        
        # Get timing summary
        timing_info = log_timing_summary()
        logger.info(f"Chat request completed - Total time: {timing_info['total_time']}s")
        
        return ChatResponse(
            session_id=session.id, 
            response_text=response_text,
            timing_info=timing_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if not initialization_error else "unhealthy",
        "agent_initialized": fi_agent is not None,
        "toolset_available": fi_toolset is not None,
        "initialization_error": initialization_error
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fi Financial Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat - POST - Send a message to the financial assistant",
            "health": "/health - GET - Check API health status",
            "docs": "/docs - GET - API documentation"
        }
    }


# --- Server Startup ---
if __name__ == "__main__":
    uvicorn.run("main2:app", host="0.0.0.0", port=8002, reload=True)