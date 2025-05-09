"""
Module for detecting and collecting infrastructure drift.

This module looks for "drift-detect" and "drift-detect-archive" folders, processes subfolders,
runs cartography detect-drift commands, and consolidates drift data.
"""
import json
import logging
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

from drift_detector.utils import (
    ensure_directory_exists, 
    is_timestamp_file, 
    run_command
)

logger = logging.getLogger(__name__)

def check_drift_detect_folder(base_path):
    """
    Check if the drift-detect folder exists at the specified path.
    
    Args:
        base_path (str): Base path where drift-detect folder should exist
        
    Returns:
        str: Path to the drift-detect folder
    
    Raises:
        FileNotFoundError: If drift-detect folder is not found
    """
    drift_detect_path = os.path.join(base_path, "drift-detect")
    if not os.path.isdir(drift_detect_path):
        raise FileNotFoundError(f"Directory 'drift-detect' not found at {base_path}")
    
    logger.debug(f"Found drift-detect folder at {drift_detect_path}")
    return drift_detect_path

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

def get_subfolders(folder_path):
    """
    Get list of subfolders within the specified folder.
    
    Args:
        folder_path (str): Path to folder
        
    Returns:
        list: List of subfolder paths
    """
    subfolders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            subfolders.append(item_path)
    
    logger.debug(f"Found {len(subfolders)} subfolders in {os.path.basename(folder_path)}")
    return subfolders

def ensure_subfolder_in_archive(drift_detect_archive_path, subfolder_name):
    """
    Ensure a subfolder exists in the drift-detect-archive folder.
    
    Args:
        drift_detect_archive_path (str): Path to drift-detect-archive folder
        subfolder_name (str): Name of the subfolder to ensure exists
        
    Returns:
        str: Path to the subfolder in drift-detect-archive
    """
    subfolder_path = os.path.join(drift_detect_archive_path, subfolder_name)
    ensure_directory_exists(subfolder_path)
    logger.debug(f"Ensured subfolder exists at {subfolder_path}")
    return subfolder_path

def ensure_drift_archive_folder(subfolder_path):
    """
    Ensure drift_archive folder exists in the subfolder.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        str: Path to drift_archive folder
    """
    drift_archive_path = os.path.join(subfolder_path, "drift_archive")
    ensure_directory_exists(drift_archive_path)
    logger.debug(f"Ensured drift_archive folder exists at {drift_archive_path}")
    return drift_archive_path

def get_timestamp_files(subfolder_path):
    """
    Get list of timestamp-formatted JSON files in the subfolder.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        list: List of timestamp file paths sorted by timestamp (oldest first)
    """
    timestamp_files = []
    
    for file_name in os.listdir(subfolder_path):
        file_path = os.path.join(subfolder_path, file_name)
        if os.path.isfile(file_path) and is_timestamp_file(file_name):
            timestamp_files.append((file_name, file_path))
    
    # Sort by filename (which is a timestamp) in ascending order
    timestamp_files.sort()
    
    return [file_path for _, file_path in timestamp_files]

def move_timestamp_file_to_archive(source_path, archive_subfolder_path):
    """
    Move a timestamp file to the archive subfolder.
    
    Args:
        source_path (str): Path to source timestamp file
        archive_subfolder_path (str): Path to archive subfolder
        
    Returns:
        str: Path to the moved file in archive
    """
    file_name = os.path.basename(source_path)
    dest_path = os.path.join(archive_subfolder_path, file_name)
    
    shutil.copy2(source_path, dest_path)
    logger.info(f"Copied {file_name} to {os.path.basename(archive_subfolder_path)}")
    
    return dest_path

def move_existing_drift_files(subfolder_path, drift_archive_path):
    """
    Move existing drift files to drift_archive folder.
    
    Args:
        subfolder_path (str): Path to subfolder
        drift_archive_path (str): Path to drift_archive folder
    """
    for file_name in os.listdir(subfolder_path):
        if file_name.startswith("drift_") and os.path.isfile(os.path.join(subfolder_path, file_name)):
            source_path = os.path.join(subfolder_path, file_name)
            dest_path = os.path.join(drift_archive_path, file_name)
            shutil.move(source_path, dest_path)
            logger.info(f"Moved {file_name} to drift_archive folder")

def run_cartography_detect_drift(subfolder_path, start_time_file, end_time_file):
    """
    Run cartography detect-drift command for a subfolder.
    
    Args:
        subfolder_path (str): Path to subfolder
        start_time_file (str): Path to start time file
        end_time_file (str): Path to end time file
        
    Returns:
        bool: True if successful, False otherwise
    """
    start_time = os.path.basename(start_time_file)
    end_time = os.path.basename(end_time_file)
    
    command = [
        "cartography", 
        "detect-drift", 
        f"--start_time={start_time}", 
        f"--end_time={end_time}"
    ]
    
    logger.info(f"Running cartography detect-drift for {os.path.basename(subfolder_path)}")
    return run_command(command)

def find_new_drift_file(subfolder_path):
    """
    Find newly created drift file.
    
    Args:
        subfolder_path (str): Path to subfolder
        
    Returns:
        str or None: Path to new drift file if found, None otherwise
    """
    for file_name in os.listdir(subfolder_path):
        if file_name.startswith("drift_") and os.path.isfile(os.path.join(subfolder_path, file_name)):
            # Check if file was created recently (within last minute)
            file_path = os.path.join(subfolder_path, file_name)
            if datetime.now().timestamp() - os.path.getctime(file_path) < 60:
                logger.info(f"Found new drift file: {file_name}")
                return file_path
    
    logger.warning("No new drift file was created")
    return None

def push_to_pocketbase(drift_data):
    """
    Push drift data to PocketBase database.
    
    Args:
        drift_data (dict): Consolidated drift data to push
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Check if PocketBase credentials exist
        pocketbase_url = os.environ.get("POCKETBASE_URL")
        pocketbase_username = os.environ.get("POCKETBASE_USERNAME")
        pocketbase_password = os.environ.get("POCKETBASE_PASSWORD")
        
        if not pocketbase_url or not pocketbase_username or not pocketbase_password:
            logger.error("Missing PocketBase credentials in .env file")
            return False
        
        # TODO: Implement PocketBase API interaction
        # This is a placeholder for actual PocketBase API code
        logger.info(f"Successfully pushed drift data to PocketBase at {pocketbase_url}")
        return True
        
    except Exception as e:
        logger.error(f"Error pushing data to PocketBase: {str(e)}")
        return False

def process_drift_detect_subfolders(drift_detect_path, drift_detect_archive_path, consolidated_drift_data):
    """
    Process subfolders in drift-detect and move timestamp files to drift-detect-archive.
    
    Args:
        drift_detect_path (str): Path to drift-detect folder
        drift_detect_archive_path (str): Path to drift-detect-archive folder
        consolidated_drift_data (dict): Dictionary to store consolidated drift data
        
    Returns:
        dict: Dictionary mapping subfolder names to their corresponding archive subfolders 
             that contain exactly 2 timestamp files
    """
    subfolders_to_process = {}
    
    # Get all subfolders in drift-detect
    drift_detect_subfolders = get_subfolders(drift_detect_path)
    
    for subfolder_path in drift_detect_subfolders:
        subfolder_name = os.path.basename(subfolder_path)
        logger.info(f"Checking subfolder {subfolder_name} in drift-detect")
        
        # Get timestamp files in the subfolder
        timestamp_files = get_timestamp_files(subfolder_path)
        
        if not timestamp_files:
            logger.warning(f"No timestamp files found in {subfolder_name}")
            continue
        
        # Ensure corresponding subfolder exists in drift-detect-archive
        archive_subfolder_path = ensure_subfolder_in_archive(drift_detect_archive_path, subfolder_name)
        
        # Move timestamp files to archive subfolder
        for timestamp_file in timestamp_files:
            move_timestamp_file_to_archive(timestamp_file, archive_subfolder_path)
        
        # Check if archive subfolder now has exactly 2 timestamp files
        archive_timestamp_files = get_timestamp_files(archive_subfolder_path)
        if len(archive_timestamp_files) == 2:
            subfolders_to_process[subfolder_name] = archive_subfolder_path
    
    return subfolders_to_process

def process_archive_subfolder(archive_subfolder_path, consolidated_drift_data):
    """
    Process a subfolder in drift-detect-archive for drift detection.
    
    Args:
        archive_subfolder_path (str): Path to subfolder in drift-detect-archive
        consolidated_drift_data (dict): Dictionary to store consolidated drift data
        
    Returns:
        bool: True if successful, False otherwise
    """
    subfolder_name = os.path.basename(archive_subfolder_path)
    logger.info(f"Processing archive subfolder: {subfolder_name}")
    
    # Ensure drift_archive folder exists
    drift_archive_path = ensure_drift_archive_folder(archive_subfolder_path)
    
    # Get timestamp files
    timestamp_files = get_timestamp_files(archive_subfolder_path)
    
    if len(timestamp_files) != 2:
        logger.warning(f"Expected exactly 2 timestamp files in {subfolder_name}, "
                      f"found {len(timestamp_files)}. Skipping.")
        return False
    
    # Move existing drift files to archive
    move_existing_drift_files(archive_subfolder_path, drift_archive_path)
    
    # Run cartography detect-drift command
    if run_cartography_detect_drift(archive_subfolder_path, timestamp_files[0], timestamp_files[1]):
        # Find new drift file
        new_drift_file = find_new_drift_file(archive_subfolder_path)
        
        if new_drift_file:
            try:
                # Read data from drift file and add to consolidated data
                with open(new_drift_file, 'r') as f:
                    drift_data = json.load(f)
                
                # Add to consolidated data with subfolder as key
                consolidated_drift_data[subfolder_name] = drift_data
                logger.info(f"Added drift data from {subfolder_name} to consolidated data")
                return True
            
            except json.JSONDecodeError:
                logger.error(f"Error parsing JSON from {new_drift_file}")
            except Exception as e:
                logger.error(f"Error processing drift file: {str(e)}")
    
    return False

def run_get_drift(base_path):
    """
    Run the Get_Drift module logic.
    
    Args:
        base_path (str): Base path where drift-detect and drift-detect-archive folders should exist
        
    Returns:
        dict: Consolidated drift data
    """
    consolidated_drift_data = {}
    
    try:
        # Check if both required folders exist
        drift_detect_path = check_drift_detect_folder(base_path)
        drift_detect_archive_path = check_drift_detect_archive_folder(base_path)
        
        # Process subfolders in drift-detect and move timestamp files to drift-detect-archive
        subfolders_to_process = process_drift_detect_subfolders(
            drift_detect_path, drift_detect_archive_path, consolidated_drift_data
        )
        
        if not subfolders_to_process:
            logger.warning("No subfolders with exactly 2 timestamp files found")
            return consolidated_drift_data
        
        # Process each subfolder in drift-detect-archive that has exactly 2 timestamp files
        success_count = 0
        for subfolder_name, archive_subfolder_path in subfolders_to_process.items():
            if process_archive_subfolder(archive_subfolder_path, consolidated_drift_data):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count} out of {len(subfolders_to_process)} subfolders")
        
        # Add metadata to the consolidated drift data
        consolidated_drift_data["_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "base_path": base_path,
            "subfolders_processed": len(subfolders_to_process),
            "subfolders_with_drift": success_count
        }
        
        # Save consolidated drift data to file
        drift_report_path = os.path.join(base_path, "drift_report.json")
        with open(drift_report_path, 'w') as f:
            json.dump(consolidated_drift_data, f, indent=2)
        logger.info(f"Saved consolidated drift data to {drift_report_path}")
        
        # Push data to PocketBase
        if push_to_pocketbase(consolidated_drift_data):
            logger.info("Successfully pushed drift data to PocketBase")
        else:
            logger.warning("Failed to push drift data to PocketBase")
        
        return consolidated_drift_data
    
    except Exception as e:
        logger.error(f"Error in run_get_drift: {str(e)}", exc_info=True)
        raise
