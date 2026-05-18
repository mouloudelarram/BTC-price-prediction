"""
Logging configuration for the Mood Analysis API.
Provides structured logging with both file and console output.
"""

import logging
import logging.handlers
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Configure application logging."""
    
    # Create logger
    logger = logging.getLogger("mood_api")
    logger.setLevel(getattr(logging, settings.log_level))
    
    # Ensure log directory exists
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=10_485_760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, settings.log_level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialize logger
logger = setup_logging()
