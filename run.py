#!/usr/bin/env python3
"""
Simple script to run the Vanna AI Web Application with Frontend.
"""
import uvicorn
from pathlib import Path
from app.infrastructure.config import settings

if __name__ == "__main__":
    print("🚀 Starting Vanna AI Web Application...")
    print(f"📡 Backend API: http://{settings.host}:{settings.port}")
    print(f"🌐 Frontend UI: http://{settings.host}:{settings.port}")
    print(f"📊 API Docs: http://{settings.host}:{settings.port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        "app.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=str(settings.log_level).lower(),
    )
