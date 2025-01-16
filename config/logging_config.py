import logging
import sys
import os
from datetime import datetime

def setup_logging(name):
    """
    Set up logging configuration for a module
    """
    logger = logging.getLogger(name)

    if not logger.handlers:  # Avoid adding handlers multiple times
        logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )

        # File handler - separate file for each day
        today = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.FileHandler(
            f"{logs_dir}/blog_generator_{today}.log"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
