# fi_fastapi_client.py
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
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
from financial_advisor.sub_agents.financial_assistant import data_analyst_agent
from financial_advisor.sub_agents.financial_advisor import financial_advisor_agent
from financial_advisor.sub_agents.optimizer_assistant import optimizer_agent
from financial_advisor.sub_agents.clarifying_agent import clarifying_agent
from financial_advisor.sub_agents.triage_assistant import triage_assitant
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
    # SseConnectionParams  # Optional, if needed
)
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
                "use this tool to get user new worth - fetch_net_worthtool"
                "When a user question arrives, it first delegates to a triage agent to determine the type of query: "
                "(1) General finance knowledge, (2) Related to user's current investments, or (3) Focused on future financial goals. "
                "If no clarification is needed, route the query to the financial assistant. "
                "If clarification is needed, it engages the clarifying agent to collect additional inputs from the user, "
                "then forwards the enriched query to the financial advisor. "
                "Finally, it invokes the optimizer agent to enhance the recommendation. "
                "Returns a comprehensive response including direct insights and optimized financial strategies."
            ),
            instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
            output_key="master_financial_planner_output",
            tools=[
                AgentTool(agent=triage_assitant),
                AgentTool(agent=clarifying_agent),
                AgentTool(agent=data_analyst_agent),
                AgentTool(agent=financial_advisor_agent),
                AgentTool(agent=optimizer_agent),
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
    global fi_agent, fi_toolset
    
    # Startup
    logger.info("Initializing Fi MCP client...")
    try:
        fi_agent, fi_toolset = await get_agent_async()
        logger.info("Fi MCP client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Fi MCP client: {e}")
        raise
    
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
@app.post("/chat")
async def chat(user_message: str) -> dict:
    """Get a response from the Fi financial assistant agent."""
    global fi_agent
    
    if not fi_agent:
        raise HTTPException(status_code=503, detail="Fi agent not initialized")
    
    try:
        app_name, user_id, session_id = "fi_mcp_app", "user_123", "session_1"
        
        # Create or get session
        session = await session_service.create_session(
            state={}, 
            app_name=app_name, 
            user_id=user_id
        )
        
        logger.info(f"User Query: '{user_message}'")
        
        # Create runner
        runner = Runner(
            app_name=app_name,
            agent=fi_agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )
        
        # Prepare user message
        content = types.Content(role='user', parts=[types.Part(text=user_message)])
        
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
        updated_session = session_service.get_session(
            app_name=app_name, 
            user_id=user_id, 
            session_id=session.id
        )
        
        return {
            "response": response_text,
            "session_id": session.id,
            "user_id": user_id
        }
        
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