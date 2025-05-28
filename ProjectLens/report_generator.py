import os
from datetime import datetime
from directory_scanner import Colors

class ReportGenerator:
    """Generates and saves markdown reports."""
    def __init__(self, config, stats_collector):
        self.config = config
        self.stats_collector = stats_collector
        self.colors = Colors()

    def save_report(self, search_path: str, output_lines: list):
        """Save the directory report as a markdown file."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Join output_lines outside the f-string to avoid backslash in expression
        output_lines_str = '\n'.join(output_lines)
        full_output = (
            f"# Directory Report: {search_path}\n\n"
            f"*Generated on {now_str}*\n\n"
            f"## Directory Structure\n"
            f"```\n"
            f"{search_path}\n"
            f"{os.path.basename(os.path.abspath(search_path))}/\n"
            f"{output_lines_str}\n"
            f"```\n"
            f"## Project Statistics\n"
            f"{self.stats_collector.get_summary(self.config.show_extended_stats)}\n"
        )

        if self.config.save_to_file:
            try:
                os.makedirs(self.config.snapshot_folder, exist_ok=True)
                with open(self.config.get_output_filepath(), "w", encoding="utf-8") as f:
                    f.write(full_output)
                print(f"\n{self.colors.GREEN}Report saved to {self.config.get_output_filepath()}{self.colors.RESET}")
            except OSError as e:
                print(f"{self.colors.RED}Error saving file: {e}{self.colors.RESET}")