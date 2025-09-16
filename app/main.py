"""
Main entry point for the Vanna AI Web Application.
"""
import sys
from pathlib import Path

from loguru import logger

from .infrastructure.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
    )
    
    # Add file logger for production
    if not settings.debug:
        log_file = Path("logs/app.log")
        log_file.parent.mkdir(exist_ok=True)
        
        logger.add(
            log_file,
            format=settings.log_format,
            level=settings.log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip",
        )
    
    logger.info("Logging configured successfully")


def main() -> None:
    """Main application entry point."""
    # Setup logging
    setup_logging()
    
    # Log startup information
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Vanna AI Model: {settings.vanna_model}")
    
    # Log frontend information
    templates_path = Path(__file__).parent.parent / "templates"
    if templates_path.exists():
        logger.info(f"Frontend templates found at: {templates_path}")
        logger.info(f"🌐 Frontend will be available at: http://{settings.host}:{settings.port}")
        logger.info(f"📊 API documentation at: http://{settings.host}:{settings.port}/docs")
    else:
        logger.warning(f"Frontend templates not found at: {templates_path}")
    
    # Import and run uvicorn
    import uvicorn
    
    uvicorn.run(
        "app.interface.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=str(settings.log_level).lower(),
    )


if __name__ == "__main__":
    main()
