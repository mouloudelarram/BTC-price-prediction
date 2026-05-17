"""Logging configuration for Correlation Engine."""

import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_DIR


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)

    # File handler
    log_file = LOG_DIR / f"{name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(console_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
