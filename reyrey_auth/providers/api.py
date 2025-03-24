from datetime import datetime, timezone
from .base import TokenProvider
from ..utils.logger import logger
from ..config import config

class ApiProvider(TokenProvider):
    """Provider that retrieves tokens from the API server"""
    
    def __init__(self, base_url=None):
        """
        Initialize the API provider
        
        Args:
            base_url: Base URL for API (default: from config)
        """
        self.base_url = base_url or config.api_base_url
    
    @property
    def name(self):
        return "api"
    
    def get_token(self, token_name):
        """
        Get a token from API
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            str: Token value or None if not found
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/current_token?token_name={token_name}", timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data:
                    token = data['token']['value']
                    logger.info(f"Found token via API")
                    return token
        except requests.exceptions.RequestException as e:
            logger.warning(f"API server not available: {str(e)}")
        except Exception as e:
            logger.warning(f"Error getting token from API: {str(e)}")
        
        return None
    
    def save_token(self, token, token_name, domain):
        """
        Save a token via API
        
        Args:
            token: Token value
            token_name: Name of the token
            domain: Domain the token is for
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/update_token", 
                json={
                    'token': token,
                    'cookie_name': token_name,
                    'domain': domain,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info(f"Saved token via API")
                    return True
            
            logger.warning(f"API returned error: {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"API server not available: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error saving token via API: {str(e)}")
            return False
