import os
import shutil
import logging
from pathlib import Path

def setup_logger(name="DexFileManager"):
    """Sets up a console logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

logger = setup_logger()

def safe_move(source_path: Path, dest_folder: Path, dry_run: bool = False):
    """
    Moves a file to the destination folder.
    If a file with the same name exists, it appends a counter to the filename.
    e.g., file.txt -> file_1.txt
    """
    if not dest_folder.exists():
        if not dry_run:
            dest_folder.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"[DRY-RUN] Create directory: {dest_folder}")

    dest_path = dest_folder / source_path.name

    # Handle duplicates
    counter = 1
    stem = source_path.stem
    suffix = source_path.suffix
    
    while dest_path.exists():
        # Ideally, check if content is identical (future enhancement), but for now just rename
        dest_path = dest_folder / f"{stem}_{counter}{suffix}"
        counter += 1

    if dry_run:
        logger.info(f"[DRY-RUN] Move: '{source_path.name}' -> '{dest_path}'")
    else:
        try:
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved: '{source_path.name}' -> '{dest_path}'")
        except Exception as e:
            logger.error(f"Failed to move '{source_path.name}': {e}")
