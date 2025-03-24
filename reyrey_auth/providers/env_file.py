import os
from dotenv import load_dotenv
from .base import TokenProvider
from ..utils.logger import logger

class EnvFileProvider(TokenProvider):
    """Provider that stores tokens in .env file"""
    
    @property
    def name(self):
        return "env_file"
    
    def get_token(self, token_name):
        """
        Get a token from environment variables
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            str: Token value or None if not found
        """
        load_dotenv()
        env_var_name = f"REYREY_TOKEN_{token_name.upper()}"
        token = os.getenv(env_var_name)
        
        if token:
            logger.info(f"Found token in environment variable: {env_var_name}")
        
        return token
    
    def save_token(self, token, token_name, domain):
        """
        Save a token to .env file
        
        Args:
            token: Token value
            token_name: Name of the token
            domain: Domain the token is for
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            env_var_name = f"REYREY_TOKEN_{token_name.upper()}"
            
            # Load current .env file
            env_vars = {}
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            # Update token
            env_vars[env_var_name] = token
            
            # Write back to .env file
            with open('.env', 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"Saved token to .env file as {env_var_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving token to .env file: {str(e)}")
            return False
