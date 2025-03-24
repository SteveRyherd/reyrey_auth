import os

class AuthConfig:
    """Configuration for the Reynolds & Reynolds authentication module"""
    
    def __init__(self):
        """Initialize with default configuration"""
        # Default to user's home directory
        self.token_directory = os.environ.get('REYREY_TOKEN_DIR', os.path.expanduser('~/.reyrey'))
        
        # Database path
        self.db_path = os.environ.get('REYREY_DB_PATH', os.path.join(self.token_directory, 'tokens.db'))
        
        # JSON token file path
        self.json_path = os.environ.get('REYREY_JSON_PATH', os.path.join(self.token_directory, 'current_token.json'))
        
        # API provider base URL
        self.api_base_url = os.environ.get('REYREY_API_URL', 'http://localhost:5000')
        
        # Playwright settings
        self.headless = os.environ.get('REYREY_HEADLESS', 'true').lower() == 'true'
        
        # Ensure directory exists
        os.makedirs(self.token_directory, exist_ok=True)

# Global config instance
config = AuthConfig()

def configure(token_dir=None, db_path=None, json_path=None, api_base_url=None, headless=None):
    """
    Configure paths and settings for token storage and authentication
    
    Args:
        token_dir: Directory to store token files
        db_path: Path to SQLite database for token storage
        json_path: Path to JSON file for token storage
        api_base_url: Base URL for API provider
        headless: Whether to run Playwright in headless mode
    """
    global config
    
    if token_dir:
        config.token_directory = token_dir
        os.makedirs(config.token_directory, exist_ok=True)
        
    if db_path:
        config.db_path = db_path
        
    if json_path:
        config.json_path = json_path
        
    if api_base_url:
        config.api_base_url = api_base_url
        
    if headless is not None:
        config.headless = headless
