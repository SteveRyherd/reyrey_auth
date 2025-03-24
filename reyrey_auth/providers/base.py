from abc import ABC, abstractmethod

class TokenProvider(ABC):
    """Abstract base class for token providers"""
    
    @property
    @abstractmethod
    def name(self):
        """Return the name of this provider"""
        pass
    
    @abstractmethod
    def get_token(self, token_name):
        """
        Get a token from this provider
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            str: Token value or None if not found
        """
        pass
    
    @abstractmethod
    def save_token(self, token, token_name, domain):
        """
        Save a token using this provider
        
        Args:
            token: Token value
            token_name: Name of the token
            domain: Domain the token is for
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        pass
