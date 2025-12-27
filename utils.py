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

import hashlib

def get_file_hash(file_path: Path) -> str:
    """Returns the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file {file_path}: {e}")
        return None

def safe_move(source_path: Path, dest_folder: Path, dry_run: bool = False):
    """
    Moves a file to the destination folder.
    Smart Deduplication:
    - If file exists AND content is identical (hash match) -> Delete source (Duplicate Assassin).
    - If file exists AND content is different -> Rename to file_1.ext.
    """
    if not dest_folder.exists():
        if not dry_run:
            dest_folder.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"[DRY-RUN] Create directory: {dest_folder}")

    dest_path = dest_folder / source_path.name

    # Check for collision
    if dest_path.exists():
        source_hash = get_file_hash(source_path)
        dest_hash = get_file_hash(dest_path)
        
        # DUPLICATE ASSASSIN LOGIC 🔪
        if source_hash and dest_hash and source_hash == dest_hash:
            if dry_run:
                logger.info(f"[DRY-RUN] 🔪 Duplicate Assassin: '{source_path.name}' is identical to target. Would DELETE.")
            else:
                try:
                    os.remove(source_path)
                    logger.info(f"🔪 Duplicate Assassin: Deleted '{source_path.name}' (Exact copy found).")
                except Exception as e:
                    logger.error(f"Failed to delete duplicate '{source_path.name}': {e}")
            return # Stop here, don't move anything

        # Content different, so rename
        counter = 1
        stem = source_path.stem
        suffix = source_path.suffix
        
        while dest_path.exists():
            dest_path = dest_folder / f"{stem}_{counter}{suffix}"
            counter += 1

    if dry_run:
        logger.info(f"[DRY-RUN] Move: '{source_path.name}' -> '{dest_path}'")
        return dest_path
    else:
        try:
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved: '{source_path.name}' -> '{dest_path}'")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to move '{source_path.name}': {e}")
            return None
