"""
Utility helper functions for the Mental Wellness Companion.
"""

import sys
from loguru import logger


def setup_logging(level: str = "INFO"):
    """
    Setup loguru logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Remove default handler
    logger.remove()
    
    # Add custom handler with format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # Also log to file
    logger.add(
        "logs/wellness_{time}.log",
        rotation="1 day",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info(f"Logging initialized at {level} level")


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "1m 30s" or "45s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if remaining_seconds > 0:
        return f"{minutes}m {remaining_seconds:.0f}s"
    return f"{minutes}m"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text_for_tts(text: str) -> str:
    """
    Clean text for TTS synthesis.
    Removes or replaces characters that may cause issues.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Replace common problematic characters
    replacements = {
        '"': '',
        '"': '',
        '"': '',
        ''': "'",
        ''': "'",
        '—': '-',
        '–': '-',
        '…': '...',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()