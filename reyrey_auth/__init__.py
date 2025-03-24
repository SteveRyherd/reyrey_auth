"""
Reynolds & Reynolds CRM Authentication Module

A Python module for handling authentication with the Reynolds & Reynolds CRM system.
"""

# Import configuration
from .config import config, configure

# Import providers
from .providers import (
    TokenProvider, 
    register_provider, 
    get_provider
)

# Import auth functions
from .auth import (
    check_token_validity,
    get_token,
    save_token,
    get_auth_headers,
    get_new_token,
    get_authenticated_session
)

# Import utils
from .utils import logger

# Import CLI module
from . import cli

# Package metadata
__version__ = "0.1.0"

# Export public API
__all__ = [
    # Configuration
    "config", 
    "configure",
    
    # Provider classes and functions
    "TokenProvider",
    "register_provider",
    "get_provider",
    
    # Authentication functions
    "check_token_validity",
    "get_token",
    "save_token",
    "get_auth_headers",
    "get_new_token",
    "get_authenticated_session",
    
    # Utils
    "logger"

    # CLI
    "cli",
]
