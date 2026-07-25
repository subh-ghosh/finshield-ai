"""Standardized logging configuration for the AML Preprocessing Platform."""

import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Configures and returns a logger with a standardized console format.

    Args:
        name: Name of the logger module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Standard output handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger to avoid duplicate log entries
        logger.propagate = False
        
    return logger
