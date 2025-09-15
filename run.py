#!/usr/bin/env python3
"""
Simple script to run the Vanna AI Web Application.
"""
import uvicorn
from app.infrastructure.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
