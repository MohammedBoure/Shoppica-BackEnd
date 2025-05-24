from datetime import datetime
from typing import List, Optional

class ProjectLensConfig:
    """Configuration settings for ProjectLens tool."""
    def __init__(self):
        self.search_path: str = "/home/pluto/Desktop/Shoppica/BackEnd"
        self.excluded: List[str] = [
            "flask", ".git", ".venv", "__pycache__",
            "recursive_directory_printer.py",
            ".pytest_cache",
            "ProjectLens"  # Exclude the ProjectLens package itself
        ]
        self.show_file_stats: bool = True
        self.save_to_file: bool = True
        self.snapshot_folder: str = "project_snapshots"
        self.timestamp: str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        self.output_filename: str = f"{self.timestamp}.md"

    def get_output_filepath(self) -> str:
        """Get the full path for the output file."""
        if self.save_to_file:
            return f"{self.snapshot_folder}/{self.output_filename}"
        return self.output_filename