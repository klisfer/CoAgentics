from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import create_tables
from app.api.routes import chat, tools
from app.services.orchestration.agent_manager import AgentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent manager instance
agent_manager: AgentManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting CoAgentics AI System...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Initialize global agent manager
        global agent_manager
        agent_manager = AgentManager()
        await agent_manager.initialize()
        logger.info("Agent Manager initialized")
        
        logger.info("CoAgentics AI System startup complete!")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down CoAgentics AI System...")
    try:
        if agent_manager:
            await agent_manager.shutdown()
        logger.info("CoAgentics AI System shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CoAgentics AI System - Agentic AI for Financial Intelligence",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Include API routers
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(tools.router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Welcome to CoAgentics AI System!",
        "version": settings.app_version,
        "description": "Agentic AI for Financial Intelligence",
        "docs_url": "/docs",
        "api_prefix": settings.api_prefix,
        "features": [
            "Multi-agent AI orchestration",
            "Financial analysis and advice",
            "Portfolio optimization",
            "Market research and insights",
            "Financial calculations",
            "Web search integration"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Basic system health
        system_health = {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment
        }
        
        # Agent manager health
        if agent_manager:
            agent_health = await agent_manager.health_check()
            system_health.update(agent_health)
        else:
            system_health["agent_manager"] = "not_initialized"
        
        return system_health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/api/info")
async def api_info():
    """API information and capabilities"""
    return {
        "api_version": "v1",
        "base_url": settings.api_prefix,
        "endpoints": {
            "chat": f"{settings.api_prefix}/chat",
            "tools": f"{settings.api_prefix}/tools"
        },
        "features": {
            "agents": [
                "Master Planner - Orchestrates multiple agents",
                "Financial Assistant - General financial advice",
                "Financial Advisor - Advanced financial planning",
                "Optimizer - Portfolio optimization"
            ],
            "tools": [
                "Web Search - Market research and news",
                "Financial Calculator - Various financial calculations"
            ],
            "capabilities": [
                "Natural language financial queries",
                "Multi-agent coordination",
                "Real-time market research",
                "Portfolio analysis",
                "Retirement planning",
                "Investment advice"
            ]
        }
    }

@app.get("/agents/status")
async def get_system_agent_status():
    """Get status of all agents in the system"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        status = agent_manager.get_all_agent_status()
        tools_status = agent_manager.get_tools_status()
        
        return {
            "agents": status,
            "tools": tools_status,
            "summary": {
                "total_agents": len(status),
                "active_agents": len([a for a in status if a.get("enabled", False)]),
                "total_tools": len(tools_status),
                "system_status": "operational"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

@app.post("/demo/quick-chat")
async def demo_quick_chat(message: str):
    """Demo endpoint for quick chat without authentication"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        # Create a basic context for demo
        from app.agents.base import AgentContext
        import uuid
        
        demo_context = AgentContext(
            user_id="demo_user",
            session_id=str(uuid.uuid4()),
            user_preferences={"demo": True},
            financial_profile={
                "risk_tolerance": "moderate",
                "investment_experience": "beginner"
            }
        )
        
        # Process message
        response = await agent_manager.process_message(message, demo_context)
        
        return {
            "message": message,
            "response": response.content,
            "agent_used": response.agent_id or "unknown",
            "demo_mode": True
        }
        
    except Exception as e:
        logger.error(f"Demo chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Demo chat failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.api_host, 
        port=settings.api_port, 
        reload=settings.debug
    ) 