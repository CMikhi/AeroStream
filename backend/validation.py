"""
Input validation utilities for the IgniteDemo Chat API.
"""

import re
from typing import Optional


__all__ = ['validate_username', 'validate_room_name', 'validate_message']


def validate_username(username: str) -> Optional[str]:
    """
    Validate username format.
    
    Args:
        username: The username to validate
        
    Returns:
        None if valid, error message if invalid
    """
    if not username or len(username.strip()) == 0:
        return "Username cannot be empty"
    
    if len(username) < 3:
        return "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return "Username must not exceed 50 characters"
    
    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return "Username can only contain letters, numbers, underscores, and hyphens"
    
    return None


def validate_room_name(room_name: str) -> Optional[str]:
    """
    Validate room name format.
    
    Args:
        room_name: The room name to validate
        
    Returns:
        None if valid, error message if invalid
    """
    if not room_name or len(room_name.strip()) == 0:
        return "Room name cannot be empty"
    
    if len(room_name) < 2:
        return "Room name must be at least 2 characters long"
    
    if len(room_name) > 100:
        return "Room name must not exceed 100 characters"
    
    # Allow alphanumeric, spaces, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9 _-]+$', room_name):
        return "Room name can only contain letters, numbers, spaces, underscores, and hyphens"
    
    return None


def validate_message(message: str) -> Optional[str]:
    """
    Validate message content.
    
    Args:
        message: The message content to validate
        
    Returns:
        None if valid, error message if invalid
    """
    if not message or len(message.strip()) == 0:
        return "Message cannot be empty"
    
    if len(message) > 1000:
        return "Message must not exceed 1000 characters"
    
    return None