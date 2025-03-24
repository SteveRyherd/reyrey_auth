import os
from datetime import datetime, timezone
from .base import TokenProvider
from ..utils.logger import logger
from ..config import config

class DatabaseProvider(TokenProvider):
    """Provider that stores tokens in a SQLite database"""
    
    def __init__(self, db_path=None):
        """
        Initialize the database provider
        
        Args:
            db_path: Path to SQLite database (default: from config)
        """
        self.db_path = db_path or config.db_path
        self._init_db()
    
    @property
    def name(self):
        return "database"
    
    def _init_db(self):
        """Initialize the database schema if needed"""
        try:
            from sqlalchemy import create_engine, Column, Integer, String, DateTime
            from sqlalchemy.orm import declarative_base, sessionmaker
            
            Base = declarative_base()
            
            class TokenStorage(Base):
                __tablename__ = 'token_storage'
                
                id = Column(Integer, primary_key=True)
                token_name = Column(String(50), nullable=False)
                token_value = Column(String(500), nullable=False)
                domain = Column(String(100), nullable=False)
                updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            engine = create_engine(f"sqlite:///{self.db_path}")
            Base.metadata.create_all(engine)
            
            # Store for later use
            self.Base = Base
            self.TokenStorage = TokenStorage
            self.engine = engine
            self.Session = sessionmaker(bind=engine)
            
            logger.debug("Database initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            # Re-raise exception if SQLAlchemy isn't available
            if "No module named 'sqlalchemy'" in str(e):
                raise ImportError("SQLAlchemy is required for the database provider") from e
    
    def get_token(self, token_name):
        """
        Get a token from database
        
        Args:
            token_name: Name of the token to retrieve
            
        Returns:
            str: Token value or None if not found
        """
        try:
            from sqlalchemy import desc
            
            session = self.Session()
            
            token_record = session.query(self.TokenStorage).filter_by(
                token_name=token_name
            ).order_by(desc(self.TokenStorage.updated_at)).first()
            
            if token_record:
                token = token_record.token_value
                logger.info(f"Found token in database")
                return token
        except Exception as e:
            logger.warning(f"Error reading token from database: {str(e)}")
        
        return None
    
    def save_token(self, token, token_name, domain):
        """
        Save a token to database
        
        Args:
            token: Token value
            token_name: Name of the token
            domain: Domain the token is for
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            session = self.Session()
            
            # Check if token already exists
            existing_token = session.query(self.TokenStorage).filter_by(
                token_name=token_name, 
                domain=domain
            ).first()
            
            if existing_token:
                # Update existing token
                existing_token.token_value = token
                existing_token.updated_at = datetime.now(timezone.utc)
            else:
                # Create new token record
                new_token = self.TokenStorage(
                    token_name=token_name,
                    token_value=token,
                    domain=domain
                )
                session.add(new_token)
            
            session.commit()
            logger.info("Saved token to database")
            return True
        except Exception as e:
            logger.error(f"Error saving token to database: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return False
