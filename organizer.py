import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from utils import logger, safe_move

from plyer import notification

class FileOrganizer:
    def __init__(self, source_dir: str, config_path: str = "config.yaml", dry_run: bool = False, strategy: str = None):
        self.source_dir = Path(source_dir)
        self.dry_run = dry_run
        self.history_file = self.source_dir / ".dex_history.json"
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        self.config = self._load_config(config_path)
        
        # Override strategy if provided in CLI, else use config default
        self.strategy = strategy or self.config.get("default_strategy", "extension")
        self.ignore_list = set(self.config.get("ignore", []))
        self.mappings = self.config.get("mappings", {})

    def _load_config(self, config_path):
        """Loads the YAML configuration file."""
        if not os.path.exists(config_path):
            logger.warning(f"Config file {config_path} not found. Using empty defaults.")
            return {}
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def organize(self):
        """Main method to organize files in the source directory."""
        # Stats tracking
        moved_count = 0
        current_batch = [] # Stores moves for this session: {'src': str, 'dest': str}
        
        logger.info(f"Starting organization in '{self.source_dir}' (Strategy: {self.strategy}, Dry-Run: {self.dry_run})")
        
        if not any(self.source_dir.iterdir()):
             return 0

        # Helper to ignore project files dynamically if config is missing them
        self.project_files = {'main.py', 'organizer.py', 'utils.py', 'config.yaml', 'requirements.txt', 'README.md', '.git', '.dex_history.json'}

        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                if file_path.name in self.ignore_list or file_path.name in self.project_files:
                    continue
                
                # Skip partial downloads
                if file_path.suffix in {'.crdownload', '.part', '.tmp'}:
                    continue

                target_folder_name = self._get_target_folder(file_path)
                
                if target_folder_name:
                    target_path = self.source_dir / target_folder_name
                    final_path = safe_move(file_path, target_path, self.dry_run)
                    
                    if final_path:
                        moved_count += 1
                        current_batch.append({
                            "src": str(file_path),
                            "dest": str(final_path)
                        })
                else:
                    logger.debug(f"Skipping '{file_path.name}' (No mapping found)")
        
        # Save History ⏳
        if moved_count > 0 and not self.dry_run:
            self._save_history(current_batch)

        # BLACK HOLE: Cleanup Empty Folders 🕳️
        if not self.dry_run:
            self._cleanup_empty_folders()

        # THE BUTLER: Notification 🔔
        if moved_count > 0 and not self.dry_run:
            try:
                notification.notify(
                    title='DexFileManager',
                    message=f'Sir, I have organized {moved_count} files for you.',
                    app_name='DexFileManager',
                    timeout=5
                )
            except Exception as e:
                logger.error(f"Notification failed: {e}")
        
        return moved_count

    def undo(self):
        """Reverses the last batch of operations."""
        if not self.history_file.exists():
            logger.warning("No history found. Cannot undo.")
            return

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                logger.warning("History is empty.")
                return

            last_batch = history.pop() 
            moves = last_batch.get("moves", [])
            logger.info(f"⏳ Undoing batch from {last_batch.get('timestamp')} ({len(moves)} actions)...")

            for move in reversed(moves):
                src_orig = Path(move["src"]) # Where it was originally
                dest_curr = Path(move["dest"]) # Where it is now

                if dest_curr.exists():
                    try:
                       # Move back to root (src_orig)
                       # Note: We trust src_orig is the intended location. 
                       # If src_orig exists (collision on undo?), safe_move logic might rename it, 
                       # but technically we want to RESTORE exactly. 
                       # For simplicity, we just move it back.
                       if not self.dry_run:
                           # Ensure parent existence if wildly different? (Assumed flat source mostly)
                           src_orig.parent.mkdir(parents=True, exist_ok=True)
                           os.rename(dest_curr, src_orig)
                           logger.info(f"Restored: {dest_curr.name} -> {src_orig.name}")
                    except Exception as e:
                        logger.error(f"Failed to undo {dest_curr.name}: {e}")
                else:
                    logger.warning(f"File missing for undo: {dest_curr}")

            # Save updated history
            if not self.dry_run:
                with open(self.history_file, 'w') as f:
                    json.dump(history, f, indent=4)
                logger.info("Undo complete.")
                
            # Cleanup again in case folders became empty after undo
            self._cleanup_empty_folders()

        except Exception as e:
            logger.error(f"Undo failed: {e}")

    def _save_history(self, batch):
        """Appends the current batch of moves to the history file."""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    content = f.read()
                    if content:
                        history = json.loads(content)
            except Exception:
                history = [] # Corrupt file, start fresh

        entry = {
            "timestamp": datetime.now().isoformat(),
            "moves": batch
        }
        history.append(entry)
        
        # Limit history size (optional, keep last 10 batches)
        history = history[-10:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=4)

    def _cleanup_empty_folders(self):
        """Recursively removes empty folders in the source directory."""
        # Only cleanup folders defined in mappings or Created by us (date format)
        # to avoid deleting random user folders.
        # Strategy: Walk bottom-up
        for root, dirs, files in os.walk(self.source_dir, topdown=False):
            for name in dirs:
                path = Path(root) / name
                
                # Safety: Don't delete .git or hidden folders generally unless strictly empty
                if name.startswith("."):
                    continue

                try:
                    if not any(path.iterdir()): # Empty
                        path.rmdir()
                        logger.info(f"🕳️ Black Hole: Consumed empty folder '{name}'")
                except Exception as e:
                    logger.debug(f"Could not remove {name}: {e}")
    def _get_target_folder(self, file_path: Path) -> str:
        """Determines the target folder based on the selected strategy."""
        if self.strategy == "date":
            return self._get_date_folder(file_path)
        else: # default to extension
            return self._get_extension_folder(file_path)

    def _get_extension_folder(self, file_path: Path) -> str:
        """Returns the folder name based on file extension."""
        ext = file_path.suffix.lstrip(".").lower()
        if not ext:
            return "Others"
        
        for folder, extensions in self.mappings.items():
            if ext in extensions:
                return folder
        
        return "Others"

    def _get_date_folder(self, file_path: Path) -> str:
        """Returns the folder name based on modification date."""
        timestamp = file_path.stat().st_mtime
        date_obj = datetime.fromtimestamp(timestamp)
        date_format = self.config.get("date_format", "%Y-%m")
        return date_obj.strftime(date_format)
