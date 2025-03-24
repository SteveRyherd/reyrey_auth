import os
import json
from datetime import datetime, timezone
from .base import TokenProvider
from ..utils.logger import logger
from ..config import config

class JsonFileProvider(TokenProvider):
    """Provider that stores tokens in a JSON file"""
    
    def __init__(self, filename=None):
        """
        Initialize the JSON file provider
        
        Args:
            filename: Path to JSON file (default: from config)
        """
        self.filename = filename or config.json_path
    
    @property
    def name(self):
        return "json_file"
    
    def get_token(self, token_name):
        """
        Get a token from JSON file
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            str: Token value or None if not found
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    if data.get('cookie_name') == token_name:
                        token = data.get('token')
                        if token:
                            logger.info(f"Found token in JSON file: {self.filename}")
                            return token
            except Exception as e:
                logger.warning(f"Error reading token from file: {str(e)}")
        
        return None
    
    def save_token(self, token, token_name, domain):
        """
        Save a token to JSON file
        
        Args:
            token: Token value
            token_name: Name of the token
            domain: Domain the token is for
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            
            with open(self.filename, 'w') as f:
                json.dump({
                    'token': token,
                    'cookie_name': token_name,
                    'domain': domain,
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }, f, indent=2)
            
            logger.info(f"Saved token to {self.filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving token to JSON file: {str(e)}")
            return False
