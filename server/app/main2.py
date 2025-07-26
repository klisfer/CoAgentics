# fi_fastapi_client.py
import os
import uvicorn
import logging
import asyncio

from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import Optional


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

from financial_advisor import prompt
# from financial_advisor.sub_agents.financial_assistant import data_analyst_agent
# from financial_advisor.sub_agents.financial_advisor import financial_advisor_agent
# from financial_advisor.sub_agents.optimizer_assistant import optimizer_agent
# from financial_advisor.sub_agents.clarifying_agent import clarifying_agent
# from financial_advisor.sub_agents.triage_assistant import triage_assitant

from financial_advisor.sub_agents.tax_assistant import tax_consultant_agent
from financial_advisor.sub_agents.investment_assistant import investment_advisor_agent
from financial_advisor.sub_agents.insurance_assistant import insurance_advisor_agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
    # SseConnectionParams  # Optional, if needed
)
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

APP_NAME = os.environ.get("GOOGLE_CLOUD_PROJECT")


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

async def get_agent_async():
    """Creates an ADK Agent equipped with tools from the Fi MCP Server."""
    try:
        # Option 1: For Fi MCP server with SSE endpoint
        # Try this first if your Fi server supports Server-Sent Events
        # connection_params = SseConnectionParams(
        #     url="http://localhost:8080/mcp/stream"  # Changed from /mcp/stream to /sse
        # )
        connection_params = StreamableHTTPConnectionParams(
            url="http://localhost:8080/mcp/stream"
        )
        
        # Option 2: For Fi MCP server with streamable HTTP
        # Uncomment this if the SSE option doesn't work
        # connection_params = StreamableHTTPConnectionParams(
        #     url="http://localhost:8080/mcp/stream"  # Your original URL
        # )
        
        # Create the MCPToolset
        toolset = MCPToolset(
            connection_params=connection_params,
            tool_filter=None  # Optional: can filter specific tools like ['get_networth', 'get_transactions']
        )
        
        # Get tools from the toolset
        tools = await toolset.get_tools()
        
        logger.info(f"Successfully fetched {len(tools)} tools from Fi MCP server.")
        


        financial_coordinator = LlmAgent(
            name="master_financial_planner",
            model=MODEL,
            description=(
                "Acts as the central decision-maker coordinating between specialized finance agents. "
                "use the below tools first to get information related to user finances:"
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
                toolset
            ],
        )
        return financial_coordinator, toolset
        
    except Exception as e:
        logger.error(f"Failed to connect to Fi MCP server: {e}")
        logger.error("Try switching between SseConnectionParams and StreamableHTTPConnectionParams")
        raise



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""

    # Startup
    print("Application starting up...")

    global fi_agent, fi_toolset
    
    # Startup
    logger.info("Initializing Fi MCP client...")
    try:
        fi_agent, fi_toolset = await get_agent_async()
        logger.info("Fi MCP client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Fi MCP client: {e}")
        raise

    
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
 
    print("Application shutting down...")

    yield
    
    # Shutdown
    logger.info("Shutting down Fi MCP client...")
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

# --- Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Get a response from the Fi financial assistant agent."""
    global fi_agent
    
    if not fi_agent:
        raise HTTPException(status_code=503, detail="Fi agent not initialized")
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

        app_name, user_id, session_id = "fi_mcp_app", "user_123", "session_1"
        
        # Create or get session
        session = await session_service.create_session(
            state={}, 
            app_name=app_name, 
            user_id=user_id
        )
        
        logger.info(f"User Query: '{request.user_message}'")
        
        # Create runner
        runner = Runner(
            app_name=app_name,
            agent=fi_agent,
            artifact_service=artifacts_service,
            # session_service=session_service,        
            session_service=vertex_ai_manager.get_session_service(),
            memory_service=vertex_ai_manager.get_memory_service(),
        )
        
        # Prepare user message
        content = types.Content(role='user', parts=[types.Part(text=request.user_message)])
        
        # Run agent and collect response
        logger.info("Running Fi agent...")
        events_async = runner.run_async(
            session_id=session.id,
            user_id=user_id,
            new_message=content
        )
        
        response_text = ""
        async for event in events_async:
            logger.info(f"Event received: {event}")
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                if event.content.parts and hasattr(event.content.parts[0], 'text'):
                    response_text = event.content.parts[0].text
        
        # Get updated session state
        # updated_session = session_service.get_session(
        #     app_name=app_name, 
        #     user_id=user_id, 
        #     session_id=session.id
        # )

        updated_session = await session_service.get_session(
            app_name=APP_NAME, user_id=request.user_id, session_id=session_id
        )
        await memory_service.add_session_to_memory(updated_session)

        return ChatResponse(session_id=session_id, response_text=response_text)
        
        # return {
        #     "response": response_text,
        #     "session_id": session.id,
        #     "user_id": user_id
        # }
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "agent_initialized": fi_agent is not None,
        "toolset_available": fi_toolset is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Fi Financial Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat - POST - Send a message to the financial assistant",
            "health": "/health - GET - Check API health status"
        }
    }

# --- Server Startup ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)