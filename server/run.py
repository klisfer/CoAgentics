#!/usr/bin/env python3
"""
CoAgentics AI System - Entry Point
A sophisticated agentic AI system for financial intelligence
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting CoAgentics AI System...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🌐 Host: {settings.api_host}:{settings.api_port}")
    print(f"📖 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.main2:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    ) 