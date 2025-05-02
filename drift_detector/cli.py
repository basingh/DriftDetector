"""
Command-line interface for the drift detector application.
"""
import argparse
import logging
import os
import sys

from drift_detector.get_state import run_get_state
from drift_detector.get_drift import run_get_drift

def setup_logging(verbose):
    """Configure logging based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def validate_path(path):
    """Validate if the provided path exists."""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Path '{path}' does not exist")
    return path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tool for managing cartography state files and detecting infrastructure drift"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Get-State command
    get_state_parser = subparsers.add_parser(
        "get-state", 
        help="Get cartography state files"
    )
    get_state_parser.add_argument(
        "--path", 
        type=validate_path,
        required=True,
        help="Path to the parent directory containing 'drift-detect' folder"
    )
    
    # Get-Drift command
    get_drift_parser = subparsers.add_parser(
        "get-drift", 
        help="Detect drift in cartography state files"
    )
    get_drift_parser.add_argument(
        "--path", 
        type=validate_path,
        required=True,
        help="Path to the parent directory containing 'drift-detect' folder"
    )
    get_drift_parser.add_argument(
        "--output", 
        type=str,
        help="Output file path to save consolidated drift data (JSON format)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified. Use --help for available commands.")
        return 1
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        if args.command == "get-state":
            logger.info("Running Get-State module")
            run_get_state(args.path)
            logger.info("Get-State operation completed successfully")
            
        elif args.command == "get-drift":
            logger.info("Running Get-Drift module")
            drift_data = run_get_drift(args.path)
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(drift_data, f, indent=2)
                logger.info(f"Drift data saved to {args.output}")
            else:
                import json
                print(json.dumps(drift_data, indent=2))
            
            logger.info("Get-Drift operation completed successfully")
            
        return 0
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    sys.exit(main())
