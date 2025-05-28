from datetime import datetime
from typing import List, Optional

class ProjectLensConfig:
    """Configuration settings for ProjectLens tool."""
    def __init__(self):
        self.search_path: str = "./"  # Default to current directory
        self.excluded: List[str] = [
            ".git", ".venv", "__pycache__",
            ".pytest_cache", "ProjectLens"  # Exclude ProjectLens package
        ]
        self.included_extensions: List[str] = [  # Extensions to analyze
            ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rb",
            ".html", ".css", ".md", ".txt"
        ]
        self.show_file_stats: bool = True
        self.show_extended_stats: bool = False  # Control extended stats display
        self.save_to_file: bool = True
        self.snapshot_folder: str = "project_snapshots"
        self.timestamp: str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        self.output_filename: str = f"{self.timestamp}.md"

    def get_output_filepath(self) -> str:
        """Get the full path for the output file."""
        if self.save_to_file:
            return f"{self.snapshot_folder}/{self.output_filename}"
        return self.output_filename