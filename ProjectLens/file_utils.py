import os
from typing import List, Tuple, Optional

class FileUtils:
    """Utility functions for file operations."""
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Convert size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"

    @staticmethod
    def get_file_stats(file_path: str, included_extensions: List[str]) -> Tuple[Optional[int], Optional[int], bool, bool]:
        """Return number of lines, size, test/documentation status."""
        try:
            # Check if file extension is included
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in [e.lower() for e in included_extensions]:
                return None, None, False, False

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                line_count = len(lines)
                size = os.path.getsize(file_path)
                # Test file detection
                is_test_file = ('test_' in os.path.basename(file_path).lower() or
                               os.path.basename(file_path).lower().endswith('_test.py') or
                               '/tests/' in file_path.lower())
                # Documentation detection (for code files only)
                is_documented = False
                if ext.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                    is_documented = any('"""' in line or "'''" in line or '//' in line or '/*' in line for line in lines)
                return line_count, size, is_test_file, is_documented
        except (OSError, UnicodeDecodeError):
            return None, None, False, False