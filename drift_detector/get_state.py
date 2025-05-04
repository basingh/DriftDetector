"""
Module for retrieving and managing cartography state files.

This module looks for "drift-detect-archive" folder, checks for subfolders,
handles JSON files with timestamp names, and runs cartography get-state commands.
"""
import logging
import os
import shutil
import subprocess
from datetime import datetime

from drift_detector.utils import (
    ensure_directory_exists, 
    is_timestamp_file, 
    run_command
)

logger = logging.getLogger(__name__)

def check_drift_detect_archive_folder(base_path):
    """
    Check if the drift-detect-archive folder exists at the specified path.
    
    Args:
        base_path (str): Base path where drift-detect-archive folder should exist
        
    Returns:
        str: Path to the drift-detect-archive folder
    
    Raises:
        FileNotFoundError: If drift-detect-archive folder is not found
    """
    drift_detect_archive_path = os.path.join(base_path, "drift-detect-archive")
    if not os.path.isdir(drift_detect_archive_path):
        raise FileNotFoundError(f"Directory 'drift-detect-archive' not found at {base_path}")
    
    logger.debug(f"Found drift-detect-archive folder at {drift_detect_archive_path}")
    return drift_detect_archive_path

def get_subfolders(drift_detect_archive_path):
    """
    Get list of subfolders within the drift-detect-archive folder.
    
    Args:
        drift_detect_archive_path (str): Path to drift-detect-archive folder
        
    Returns:
        list: List of subfolder paths
    """
    subfolders = []
    for item in os.listdir(drift_detect_archive_path):
        item_path = os.path.join(drift_detect_archive_path, item)
        if os.path.isdir(item_path):
            subfolders.append(item_path)
    
    logger.debug(f"Found {len(subfolders)} subfolders in drift-detect-archive")
    return subfolders

def ensure_state_archive_folder(subfolder_path):
    """
    Ensure state-archive folder exists in the subfolder.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        str: Path to state-archive folder
    """
    state_archive_path = os.path.join(subfolder_path, "state-archive")
    ensure_directory_exists(state_archive_path)
    logger.debug(f"Ensured state-archive folder exists at {state_archive_path}")
    return state_archive_path

def handle_existing_timestamp_files(subfolder_path, state_archive_path):
    """
    Check for existing timestamp files and move older ones to state-archive.
    
    Args:
        subfolder_path (str): Path to subfolder
        state_archive_path (str): Path to state-archive folder
    """
    timestamp_files = []
    
    for file_name in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file_name)
        if os.path.isfile(file_path) and is_timestamp_file(file_name):
            timestamp_files.append((file_name, file_path))
    
    # Sort by filename (which is a timestamp) in descending order
    timestamp_files.sort(reverse=True)
    
    # Keep the most recent file, move others to state-archive
    if len(timestamp_files) > 0:
        for i, (file_name, file_path) in enumerate(timestamp_files):
            if i > 0:  # Skip the first (most recent) file
                archive_file_path = os.path.join(state_archive_path, file_name)
                shutil.move(file_path, archive_file_path)
                logger.info(f"Moved {file_name} to state-archive folder")

def run_cartography_get_state(subfolder_path):
    """
    Run cartography get-state command for a subfolder.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        bool: True if successful, False otherwise
    """
    subfolder_name = os.path.basename(subfolder_path)
    command = ["cartography", "get-state", subfolder_name]
    
    logger.info(f"Running cartography get-state for {subfolder_name}")
    return run_command(command)

def check_state_file_created(subfolder_path):
    """
    Check if a new state file with timestamp format was created.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        str or None: Path to new state file if found, None otherwise
    """
    # Get current list of timestamp files
    new_files = []
    for file_name in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file_name)
        if os.path.isfile(file_path) and is_timestamp_file(file_name):
            # Check if file was created recently (within last minute)
            if datetime.now().timestamp() - os.path.getctime(file_path) < 60:
                new_files.append(file_path)
    
    if new_files:
        logger.info(f"Found new state file: {os.path.basename(new_files[0])}")
        return new_files[0]
    else:
        logger.warning("No new state file was created")
        return None

def process_subfolder(subfolder_path):
    """
    Process a single subfolder for get-state operation.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        bool: True if successful, False otherwise
    """
    subfolder_name = os.path.basename(subfolder_path)
    logger.info(f"Processing subfolder: {subfolder_name}")
    
    state_archive_path = ensure_state_archive_folder(subfolder_path)
    handle_existing_timestamp_files(subfolder_path, state_archive_path)
    
    if run_cartography_get_state(subfolder_path):
        new_state_file = check_state_file_created(subfolder_path)
        return new_state_file is not None
    
    return False

def run_get_state(base_path):
    """
    Run the Get_State module logic.
    
    Args:
        base_path (str): Base path where drift-detect-archive folder should exist
        
    Returns:
        bool: True if successful for at least one subfolder, False otherwise
    """
    try:
        drift_detect_archive_path = check_drift_detect_archive_folder(base_path)
        subfolders = get_subfolders(drift_detect_archive_path)
        
        if not subfolders:
            logger.warning("No subfolders found in drift-detect-archive folder")
            return False
        
        success_count = 0
        for subfolder_path in subfolders:
            if process_subfolder(subfolder_path):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count} out of {len(subfolders)} subfolders")
        return success_count > 0
    
    except Exception as e:
        logger.error(f"Error in run_get_state: {str(e)}", exc_info=True)
        raise
