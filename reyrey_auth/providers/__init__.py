from .base import TokenProvider
from .env_file import EnvFileProvider
from .json_file import JsonFileProvider
from .api import ApiProvider

# Export classes
__all__ = ["TokenProvider", "EnvFileProvider", "JsonFileProvider", "ApiProvider"]

# Default provider registry
_token_providers = {
    'env_file': EnvFileProvider(),
    'json_file': JsonFileProvider(),
    'database': None,  # Lazy loaded
    'api': ApiProvider()
}

# Default provider order
_default_provider_order = ['env_file', 'json_file', 'database', 'api']

def register_provider(provider):
    """
    Register a new token provider
    
    Args:
        provider: Instance of TokenProvider
        
    Raises:
        TypeError: If provider is not an instance of TokenProvider
    """
    from ..utils.logger import logger
    
    if isinstance(provider, TokenProvider):
        _token_providers[provider.name] = provider
        logger.info(f"Registered token provider: {provider.name}")
    else:
        raise TypeError("Provider must be an instance of TokenProvider")

def get_provider(name):
    """
    Get a token provider by name, initializing it if needed
    
    Args:
        name: Name of the provider
        
    Returns:
        TokenProvider: The provider instance or None if not found
    """
    from ..utils.logger import logger
    
    provider = _token_providers.get(name)
    
    # Lazy load database provider to avoid unnecessary dependencies
    if name == 'database' and provider is None:
        try:
            from .database import DatabaseProvider
            _token_providers['database'] = DatabaseProvider()
            provider = _token_providers['database']
        except ImportError as e:
            logger.warning(f"Database provider requires SQLAlchemy: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to initialize database provider: {str(e)}")
    
    return provider

# Export functions
__all__.extend(["register_provider", "get_provider"])
