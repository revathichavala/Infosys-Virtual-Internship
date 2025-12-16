"""
Logger Module - Centralized logging for AI Smart Quiz application
"""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Log file with date
LOG_FILE = os.path.join(LOGS_DIR, f'smartquiz_{datetime.now().strftime("%Y%m%d")}.log')

# Custom formatter with colors for console
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Pre-configured loggers for each module
def get_app_logger():
    """Logger for main application (app.py)"""
    return setup_logger('SmartQuiz.App')

def get_generator_logger():
    """Logger for question generator"""
    return setup_logger('SmartQuiz.Generator')

def get_engine_logger():
    """Logger for quiz engine"""
    return setup_logger('SmartQuiz.Engine')

def get_analytics_logger():
    """Logger for analytics"""
    return setup_logger('SmartQuiz.Analytics')

def get_database_logger():
    """Logger for database operations"""
    return setup_logger('SmartQuiz.Database')

def get_utils_logger():
    """Logger for utilities"""
    return setup_logger('SmartQuiz.Utils')
