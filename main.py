import argparse
import time
import sys
import logging
from pathlib import Path
from organizer import FileOrganizer

# Rich Imports
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.logging import RichHandler
from rich.align import Align

# Configure Rich Logging
logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler(markup=True)])
logger = logging.getLogger("rich")
console = Console()

def make_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="status"),
        Layout(name="log", ratio=2),
    )
    return layout

def main():
    parser = argparse.ArgumentParser(description="DexFileManager: A simple, automatic file organizer.")
    
    parser.add_argument("--source", type=str, default=".", help="Source directory to organize (default: current dir)")
    parser.add_argument("--strategy", type=str, choices=["extension", "date"], help="Organization strategy (overrides config)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without moving files")
    parser.add_argument("--undo", action="store_true", help="Undo the last batch of operations")
    parser.add_argument("--recursive", action="store_true", help="Deep Dive: Recursively organize subfolders")
    parser.add_argument("--watch", action="store_true", help="Run continuously and watch for changes (every 10 seconds)")
    
    args = parser.parse_args()
    source_path = Path(args.source).resolve()

    # God Mode Dashboard
    layout = make_layout()
    layout["header"].update(Panel(Align.center(Text("DexFileManager - World Domination Edition 🌍", style="bold magenta")), style="green"))
    
    stats = {"scans": 0, "files_moved": 0}

    try:
        organizer = FileOrganizer(source_path, dry_run=args.dry_run, strategy=args.strategy, recursive=args.recursive)
        
        if args.undo:
            console.print("[bold yellow]⏳ Time Traveller Logic Activated...[/bold yellow]")
            organizer.undo()
            sys.exit(0)

        if args.watch:
            with Live(layout, refresh_per_second=4) as live:
                while True:
                    # Update Status
                    stats["scans"] += 1
                    status_text = f"""
[bold cyan]Run Mode:[/bold cyan] {'WATCH' if args.watch else 'ONCE'}
[bold cyan]Source:[/bold cyan] {source_path}
[bold cyan]Strategy:[/bold cyan] {args.strategy or 'extension'}
[bold cyan]Dry Run:[/bold cyan] {args.dry_run}

[bold yellow]Stats:[/bold yellow]
Scans: {stats['scans']}
Files Organized: {stats['files_moved']}
                    """
                    layout["status"].update(Panel(status_text, title="System Status", border_style="cyan"))
                    
                    # Run Organize
                    count = organizer.organize()
                    stats["files_moved"] += count
                    
                    if count > 0:
                        layout["log"].update(Panel(f"[green]Moved {count} files.[/green]", title="Live Log", border_style="blue"))
                    else:
                        layout["log"].update(Panel("[dim]No files to move.[/dim]", title="Live Log", border_style="blue"))
                    
                    time.sleep(10) # Simple polling every 10 seconds
        else:
            # One-off run without full dashboard (keep it simple for scripts)
            console.print("[bold green]Running One-Time Organization...[/bold green]")
            count = organizer.organize()
            console.print(f"[bold magenta]Done! Organized {count} files.[/bold magenta]")

    except Exception as e:
        console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()
