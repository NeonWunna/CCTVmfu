"""
Helper Functions
Utility functions used across the application.
"""
from datetime import datetime
from typing import Optional
import uuid


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object to format. Defaults to current time if None.
        format_str: Format string for the output.
    
    Returns:
        Formatted datetime string.
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def generate_unique_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        UUID4 string.
    """
    return str(uuid.uuid4())


def validate_ip_address(ip: str) -> bool:
    """
    Validate an IP address format.
    
    Args:
        ip: IP address string to validate.
    
    Returns:
        True if valid, False otherwise.
    """
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    
    return True


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize and truncate a string.
    
    Args:
        value: String to sanitize.
        max_length: Maximum length of the output string.
    
    Returns:
        Sanitized string.
    """
    return value.strip()[:max_length] if value else ""
