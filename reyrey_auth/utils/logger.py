import os
import sys
from loguru import logger

# Remove default handler
logger.remove()

# Add stderr handler
logger.add(sys.stderr, level="INFO")

# Create logs directory in the user's configured directory
from ..config import config
os.makedirs(os.path.join(config.token_directory, "logs"), exist_ok=True)

# Add file handler
logger.add(
    os.path.join(config.token_directory, "logs", "reyrey_auth_{time}.log"), 
    rotation="10 MB", 
    level="DEBUG"
)

# Export the configured logger
__all__ = ["logger"]
