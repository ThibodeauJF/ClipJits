"""Utility functions for ClipJits."""

import re


def to_snake_case(text: str, max_length: int = 50) -> str:
    """
    Convert text to snake_case with character limit.
    
    Args:
        text: Input text to convert
        max_length: Maximum length of output (default 50)
    
    Returns:
        Snake-cased string
    """
    # Remove special characters and replace spaces/hyphens with underscores
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    # Convert to lowercase
    text = text.lower()
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    # Trim underscores from start and end
    text = text.strip('_')
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rstrip('_')
    return text


def parse_timestamp(timestamp: str) -> float:
    """Parse timestamp string (HH:MM:SS.mmm or MM:SS.mmm) to seconds."""
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    else:
        return float(timestamp)

