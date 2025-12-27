import os
import yaml
from pathlib import Path
from datetime import datetime
from utils import logger, safe_move

class FileOrganizer:
    def __init__(self, source_dir: str, config_path: str = "config.yaml", dry_run: bool = False, strategy: str = None):
        self.source_dir = Path(source_dir)
        self.dry_run = dry_run
        
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
        logger.info(f"Starting organization in '{self.source_dir}' (Strategy: {self.strategy}, Dry-Run: {self.dry_run})")
        
        if not any(self.source_dir.iterdir()):
             logger.info("Directory is empty.")
             return

        # Helper to ignore project files dynamically if config is missing them
        self.project_files = {'main.py', 'organizer.py', 'utils.py', 'config.yaml', 'requirements.txt', 'README.md'}

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
                    safe_move(file_path, target_path, self.dry_run)
                else:
                    logger.debug(f"Skipping '{file_path.name}' (No mapping found)")

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
