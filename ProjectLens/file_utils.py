import os
from typing import Tuple, Optional

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
    def get_file_stats(file_path: str) -> Tuple[Optional[int], Optional[int], bool, bool, str]:
        """Return number of lines, size, test/documentation status, and module type."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                line_count = len(lines)
                size = os.path.getsize(file_path)
                # Test file detection
                is_test_file = ('test_' in os.path.basename(file_path).lower() or
                               os.path.basename(file_path).lower().endswith('_test.py') or
                               '/tests/' in file_path.lower())
                # Documentation detection
                is_documented = any('"""' in line or "'''" in line for line in lines) if file_path.endswith('.py') else False
                # Module type detection
                module_type = "other"
                if file_path.endswith('.py') and not is_test_file:
                    content = ''.join(lines).lower()
                    if any(keyword in content for keyword in ['@app.', 'route', 'endpoint', 'flask', 'fastapi']):
                        module_type = "api"
                    elif any(keyword in content for keyword in ['sqlalchemy', 'model', 'table', 'session', 'query']):
                        module_type = "database"
                return line_count, size, is_test_file, is_documented, module_type
        except Exception:
            return None, None, False, False, "other"