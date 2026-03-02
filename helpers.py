"""
Helper utility functions for the attendance system.
"""

from datetime import datetime
import os


def get_current_timestamp():
    """
    Get current timestamp in readable format.
    
    Returns:
        str: Current timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date():
    """
    Get current date in YYYY-MM-DD format.
    
    Returns:
        str: Current date
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time():
    """
    Get current time in HH:MM:SS format.
    
    Returns:
        str: Current time
    """
    return datetime.now().strftime("%H:%M:%S")


def validate_roll_number(roll_number):
    """
    Validate roll number format.
    
    Args:
        roll_number (str): Roll number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(roll_number and roll_number.strip())


def validate_name(name):
    """
    Validate name format.
    
    Args:
        name (str): Name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(name and name.strip() and len(name) >= 2)


def format_date(date_str):
    """
    Format date string to readable format.
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        str: Formatted date
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str


def ensure_directory(directory):
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory (str): Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✓ Created directory: {directory}")
