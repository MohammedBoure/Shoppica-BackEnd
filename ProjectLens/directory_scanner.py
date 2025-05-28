import os
from typing import List
from file_utils import FileUtils

class Colors:
    """ANSI color codes for console output."""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GRAY = '\033[90m'

class DirectoryScanner:
    """Handles directory traversal and tree printing."""
    def __init__(self, config, stats_collector):
        self.config = config
        self.stats_collector = stats_collector
        self.colors = Colors()

    def print_directory_tree(self, startpath: str, excluded_items: List[str], prefix: str = "", is_root: bool = False) -> List[str]:
        """Print directory tree and collect statistics."""
        try:
            real_startpath = os.path.abspath(startpath)
            entries = os.listdir(real_startpath)
            filtered_entries = [e for e in entries if e not in self.config.excluded]
            dirs = sorted([d for d in filtered_entries if os.path.isdir(os.path.join(real_startpath, d))])
            files = sorted([f for f in filtered_entries if os.path.isfile(os.path.join(real_startpath, f))])
            all_entries = dirs + files
            if not is_root:
                self.stats_collector.increment_folders()
        except OSError as e:
            line = f"{prefix}└── [Error: {e}]"
            print(line)
            return [line]

        output_lines = []
        folder_lines = 0
        folder_size = 0
        folder_file_count = 0

        if not is_root:
            pointer = "└── " if len(all_entries) == 0 else "├── "
            line = f"{prefix}{pointer}{self.colors.BLUE}{os.path.basename(real_startpath)}/{self.colors.RESET}"
            print(line)
            output_lines.append(f"{prefix}{pointer}{os.path.basename(real_startpath)}/")
            prefix += "│   " if pointer == "├── " else "    "

        max_name_length = max((len(entry) for entry in all_entries), default=0) if all_entries else 0

        for i, entry in enumerate(all_entries):
            entry_path = os.path.join(real_startpath, entry)
            is_dir = os.path.isdir(entry_path)
            is_last = i == len(all_entries) - 1
            pointer = "└── " if is_last else "├── "

            if is_dir:
                sub_output = self.print_directory_tree(entry_path, excluded_items, prefix, is_root=False)
                output_lines.extend(sub_output)
            else:
                self.stats_collector.increment_files()
                display = f"{prefix}{pointer}{entry:<{max_name_length}}"
                display_clean = f"{prefix}{pointer}{entry:<{max_name_length}}"
                if self.config.show_file_stats:
                    lines, size, is_test, is_documented = FileUtils.get_file_stats(entry_path, self.config.included_extensions)
                    if lines is not None and size is not None:
                        self.stats_collector.update_stats(entry, lines, size, is_test, is_documented)
                        folder_lines += lines
                        folder_size += size
                        folder_file_count += 1
                        display += f" {self.colors.GRAY}[{lines} lines, {FileUtils.format_size(size)}]{self.colors.RESET}"
                        display_clean += f" [{lines} lines, {FileUtils.format_size(size)}]"
                print(display)
                output_lines.append(display_clean)

        if folder_file_count > 0:
            stats_line = (
                f"{prefix}    {self.colors.YELLOW}"
                f"({folder_file_count} files, {folder_lines} lines, {FileUtils.format_size(folder_size)})"
                f"{self.colors.RESET}"
            )
            stats_line_clean = f"{prefix}    ({folder_file_count} files, {folder_lines} lines, {FileUtils.format_size(folder_size)})"
            print(stats_line)
            output_lines.append(stats_line_clean)

        return output_lines