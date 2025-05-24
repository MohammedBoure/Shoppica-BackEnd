import os
from collections import defaultdict
from typing import Tuple, List
from .file_utils import FileUtils

class StatsCollector:
    """Collects and processes project statistics."""
    def __init__(self):
        self.total_lines = 0
        self.total_size = 0
        self.total_files = 0
        self.total_folders = 0
        self.file_stats = defaultdict(lambda: {'count': 0, 'lines': 0, 'size': 0})
        self.largest_files: List[Tuple[str, int]] = []
        self.test_files = set()
        self.api_endpoints = 0
        self.database_endpoints = 0
        self.documented_endpoints = 0

    def increment_files(self):
        """Increment the file counter."""
        self.total_files += 1

    def increment_folders(self):
        """Increment the folder counter."""
        self.total_folders += 1

    def update_stats(self, file_name: str, lines: int, size: int, is_test: bool, is_documented: bool, module_type: str):
        """Update statistics for a file."""
        self.total_lines += lines
        self.total_size += size
        _, ext = os.path.splitext(file_name)
        self.file_stats[ext]['count'] += 1
        self.file_stats[ext]['lines'] += lines
        self.file_stats[ext]['size'] += size
        self.largest_files.append((file_name, size))
        self.largest_files.sort(key=lambda x: x[1], reverse=True)
        self.largest_files = self.largest_files[:3]
        if is_test:
            self.test_files.add(file_name)
        if file_name.endswith('.py') and not is_test:
            if module_type == "api":
                self.api_endpoints += 1
            elif module_type == "database":
                self.database_endpoints += 1
            if is_documented:
                self.documented_endpoints += 1

    def get_summary(self) -> str:
        """Generate a summary of statistics."""
        summary = f"Total folders: {self.total_folders}\n"
        summary += f"Total files: {self.total_files}\n"
        summary += f"Total lines: {self.total_lines:,}\n"
        summary += f"Total size: {FileUtils.format_size(self.total_size)}\n\n"
        
        summary += f"File types:\n"
        for ext, stats in self.file_stats.items():
            summary += f"- {ext or 'no extension'}: {stats['count']} files ({stats['lines']:,} lines, {FileUtils.format_size(stats['size'])})\n"
        
        summary += f"\nTop 3 largest files:\n"
        for file_name, size in self.largest_files:
            summary += f"- {file_name}: {FileUtils.format_size(size)}\n"
        
        total_modules = self.api_endpoints + self.database_endpoints
        test_coverage = (len(self.test_files) / total_modules * 100) if total_modules > 0 else 0
        api_coverage = (len(self.test_files) / self.api_endpoints * 100) if self.api_endpoints > 0 else 0
        db_coverage = (len(self.test_files) / self.database_endpoints * 100) if self.database_endpoints > 0 else 0
        summary += f"\nTest coverage for APIs: {len(self.test_files)}/{self.api_endpoints} modules ({api_coverage:.1f}%)\n"
        summary += f"Test coverage for Database: {len(self.test_files)}/{self.database_endpoints} modules ({db_coverage:.1f}%)\n"
        summary += f"Total test coverage: {len(self.test_files)}/{total_modules} modules ({test_coverage:.1f}%)\n"
        
        doc_coverage = (self.documented_endpoints / total_modules * 100) if total_modules > 0 else 0
        summary += f"\nAPI Documentation coverage: {self.documented_endpoints}/{total_modules} ({doc_coverage:.1f}%)\n"
        
        return summary