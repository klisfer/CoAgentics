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


MODEL = "gemini-2.5-pro"

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables to store services and agent
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()
fi_agent = None
fi_toolset = None
initialization_error = None

APP_NAME = os.environ.get("GOOGLE_CLOUD_PROJECT", "fi_mcp_app")


class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    new_message: str = Field(..., description="The user's message text.")  # Fixed: was new_message

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    timing_info: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    user_id: str

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
        # try:
        #     # Add a timeout to prevent hanging
        #     tools = await asyncio.wait_for(toolset.get_tools(), timeout=10.0)
        #     logger.info(f"Successfully fetched {len(tools)} tools from Fi MCP server.")
        #     logger.info(f"Successfully fetched {toolset} toolset from Fi MCP server.")
        # except asyncio.TimeoutError:
        #     logger.error("Timeout while fetching tools from MCP server")
        #     raise Exception("MCP server connection timeout")
        
        financial_coordinator = LlmAgent(
            name="master_financial_planner",
            model=MODEL,
            description=(
                "Acts as the central decision-maker coordinating between specialized finance agents. "
                "use the below tools first to get information related to user finances if user question is related to their finance:"
                "1.tool to get user new worth - fetch_net_worthtool"
                "2.tool to get user credit report - fetch_credit_reporttool"
                "3.tool to get user bank transaction - " 
                "4.tool to get user epf details - fetch_epf_detailstool"
                "5.tool to get user mutual fund transactions - fetch_mf_transactionstool"
                "6.tool to get user stock transactions - fetch_stock_transactionstool"
                "First fetch the data from respective tool above based on the question and then use the specific agent with that data, user question to get answer for user question"
                "When a user question arrives, asses for the given question which is the right agent among tax_consultant_agent, investment_advisor_agent and insurance_advisor_agent"
                "Returns a comprehensive response including direct insights and optimized financial strategies."
            ),
            instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
            output_key="master_financial_planner_output",
            tools=[
                AgentTool(agent=tax_consultant_agent),
                AgentTool(agent=investment_advisor_agent),
                AgentTool(agent=insurance_advisor_agent),
                toolset,
                AgentTool(agent=web_search_agent)
            ],
        )
        return financial_coordinator, toolset
        
    except Exception as e:
        logger.error(f"Failed to connect to Fi MCP server: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    global fi_agent, fi_toolset, initialization_error
    
    # Startup
    logger.info("Application starting up...")
    
    try:
        # Load environment variables first
        load_dotenv()
        
        # Check for credentials
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set, trying to continue...")
        
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if not project_id:
            logger.warning("GOOGLE_CLOUD_PROJECT not set, using default")
            project_id = "default-project"
        
        # Initialize Vertex AI Manager
        try:
            vertex_ai_manager.initialize(project_id=project_id, location=location)
            logger.info("Vertex AI Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI Manager: {e}")
            # Continue without it for now
        
        # Initialize Fi MCP client with timeout
        logger.info("Initializing Fi MCP client...")
        try:
            fi_agent, fi_toolset = await asyncio.wait_for(get_agent_async(), timeout=30.0)
            logger.info("Fi MCP client initialized successfully")
        except asyncio.TimeoutError:
            logger.error("Timeout during Fi MCP client initialization")
            initialization_error = "MCP server connection timeout"
        except Exception as e:
            logger.error(f"Failed to initialize Fi MCP client: {e}")
            initialization_error = str(e)
            # Don't raise - let the app start but mark as unhealthy
        
        logger.info("Application startup completed")
        
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
    
    logger.info(f"🚀 Chat request started - User: {request.user_id}, Session: {request.session_id}, Message: '{request.new_message[:50]}...'")
    
    if initialization_error:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {initialization_error}")
    
    if not fi_agent:
        raise HTTPException(status_code=503, detail="Fi agent not initialized")
    
    try:
        # Use vertex AI manager services
        with time_operation("vertex_ai_service_initialization"):
            session_service = vertex_ai_manager.get_session_service()
            memory_service = vertex_ai_manager.get_memory_service()
        
        session_id = request.session_id
        
        # Get or create session
        with time_operation("session_management"):
            if session_id:
                try:
                    logger.info(f"🔍 Getting existing session: {session_id}")
                    session = await session_service.get_session(
                        app_name=APP_NAME, user_id=request.user_id, session_id=session_id
                    )
                    if not session:
                        raise HTTPException(status_code=404, detail="Session not found.")
                    logger.info(f"✅ Retrieved existing session: {session.id}")
                except Exception as e:
                    logger.error(f"❌ Error getting session: {e}")
                    # Create new session if getting fails
                    logger.info("🔄 Creating new session due to error")
                    session = await session_service.create_session(
                        app_name=APP_NAME, user_id=request.user_id
                    )
                    logger.info(f"✅ Created new session: {session.id}")
            else:
                logger.info("🆕 Creating new session")
                session = await session_service.create_session(
                    app_name=APP_NAME, user_id=request.user_id
                )
                logger.info(f"✅ Created new session: {session.id}")
        
        session_id = session.id
        # Use the actual session variables, don't override them
        user_id = request.user_id
        
        logger.info(f"📝 User Query: '{request.new_message}'")
        
        # Create runner
        with time_operation("runner_initialization"):
            runner = Runner(
                app_name=APP_NAME,
                agent=fi_agent,
                artifact_service=artifacts_service,
                session_service=session_service,
                memory_service=memory_service,
            )
        
        # Prepare user message
        with time_operation("message_preparation"):
            content = types.Content(role='user', parts=[types.Part(text=request.new_message)])
        
        # Run agent with timeout
        logger.info("🤖 Running Fi agent...")
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
        
        # Update session in memory
        with time_operation("memory_update"):
            try:
                logger.info("💾 Updating session memory...")
                updated_session = await session_service.get_session(
                    app_name=APP_NAME, user_id=request.user_id, session_id=session_id
                )
                if updated_session:
                    await memory_service.add_session_to_memory(updated_session)
                    logger.info("✅ Session memory updated")
            except Exception as e:
                logger.error(f"❌ Error updating session memory: {e}")
                # Continue anyway
        
        # Get timing summary
        timing_info = log_timing_summary()
        logger.info(f"🏁 Chat request completed - Total time: {timing_info['total_time']}s")
        
        return ChatResponse(
            session_id=session_id, 
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
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)