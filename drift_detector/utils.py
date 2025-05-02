"""
Utility functions for the drift detector application.
"""
import logging
import os
import subprocess
import re

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path):
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to directory to ensure exists
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.debug(f"Created directory: {directory_path}")

def is_timestamp_file(file_name):
    """
    Check if file name matches the Unix datetime timestamp format.
    Example: "2025.3.27.22.5.9.3.86.0"
    
    Args:
        file_name (str): File name to check
        
    Returns:
        bool: True if file name matches timestamp format, False otherwise
    """
    # Pattern matches sequences of numbers separated by dots
    # The extension .json is optional to handle both cases
    pattern = r"^(\d+\.){7,8}\d+(\.\w+)?$"
    return bool(re.match(pattern, file_name))

def run_command(command):
    """
    Run a shell command and handle output.
    
    Args:
        command (list): Command to run as a list of strings
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    try:
        logger.debug(f"Running command: {' '.join(command)}")
        
        # Run the command and capture output
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        logger.debug(f"Command output: {result.stdout}")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {e.stderr}")
        return False
    
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return False
