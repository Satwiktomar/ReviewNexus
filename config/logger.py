"""Logging configuration for FoodRank application."""
import logging
import logging.handlers
from pathlib import Path
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT


def setup_logging(name: str = 'foodrank') -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)
    
    # File handler with rotation
    log_file = LOGS_DIR / f'{name}.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
