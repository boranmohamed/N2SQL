"""
Factory for creating Vanna AI clients (local vs remote).
"""
import os
from typing import Union

from .vanna_client import VannaClientRepository
from .local_vanna_client import LocalVannaClientRepository
from .config import settings
from loguru import logger


def create_vanna_client(use_local: bool = None) -> Union[VannaClientRepository, LocalVannaClientRepository]:
    """
    Create a Vanna AI client instance.
    
    Args:
        use_local: If True, use local server. If False, use remote. If None, use config setting.
        
    Returns:
        VannaClientRepository or LocalVannaClientRepository
    """
    # Use config setting if not specified
    if use_local is None:
        use_local = settings.use_local_vanna
    
    if use_local:
        logger.info("🏠 Creating LOCAL Vanna AI client")
        return LocalVannaClientRepository()
    else:
        logger.info("☁️ Creating REMOTE Vanna AI client")
        return VannaClientRepository()


def get_vanna_client_from_env() -> Union[VannaClientRepository, LocalVannaClientRepository]:
    """
    Get Vanna client based on configuration settings.
    
    Returns:
        Configured Vanna client instance
    """
    return create_vanna_client()
