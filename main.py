import argparse
import time
import sys
from pathlib import Path
from organizer import FileOrganizer
from utils import logger

def main():
    parser = argparse.ArgumentParser(description="DexFileManager: A simple, automatic file organizer.")
    
    parser.add_argument("--source", type=str, default=".", help="Source directory to organize (default: current dir)")
    parser.add_argument("--strategy", type=str, choices=["extension", "date"], help="Organization strategy (overrides config)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without moving files")
    parser.add_argument("--watch", action="store_true", help="Run continuously and watch for changes (every 10 seconds)")
    
    args = parser.parse_args()
    
    source_path = Path(args.source).resolve()
    
    try:
        organizer = FileOrganizer(source_path, dry_run=args.dry_run, strategy=args.strategy)
        
        if args.watch:
            logger.info(f"Watching '{source_path}' for changes... (Press Ctrl+C to stop)")
            try:
                while True:
                    organizer.organize()
                    time.sleep(10) # Simple polling every 10 seconds
            except KeyboardInterrupt:
                logger.info("Stopping watch mode.")
        else:
            organizer.organize()
            logger.info("Done!")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
