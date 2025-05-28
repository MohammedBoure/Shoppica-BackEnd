import os
import sys

# Add the parent directory to sys.path to support direct execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ProjectLensConfig
from directory_scanner import DirectoryScanner, Colors
from stats_collector import StatsCollector
from report_generator import ReportGenerator
from file_utils import FileUtils
from cli import parse_arguments

def main():
    """Main function to run ProjectLens."""
    # Parse CLI arguments and update config
    config = ProjectLensConfig()
    args = parse_arguments()
    config.search_path = os.path.abspath(args.path)  # Ensure absolute path
    config.show_file_stats = args.show_stats
    config.show_extended_stats = args.show_extended_stats
    config.save_to_file = args.save_report
    if args.extensions:
        config.included_extensions = args.extensions.split(',')

    stats_collector = StatsCollector()
    scanner = DirectoryScanner(config, stats_collector)
    report_generator = ReportGenerator(config, stats_collector)
    colors = Colors()

    print(f"{colors.BOLD}{config.search_path}{colors.RESET}")

    if not os.path.isdir(config.search_path):
        print(f"{colors.RED}Error: {config.search_path} is not a valid directory{colors.RESET}")
        return

    print(f"{colors.BLUE}{os.path.basename(os.path.abspath(config.search_path))}/{colors.RESET}")

    try:
        entries = os.listdir(config.search_path)
        filtered_entries = [e for e in entries if e not in config.excluded]
        dirs = sorted([d for d in filtered_entries if os.path.isdir(os.path.join(config.search_path, d))])
        files = sorted([f for f in filtered_entries if os.path.isfile(os.path.join(config.search_path, f))])
    except OSError as e:
        print(f"{colors.RED}Error: {e}{colors.RESET}")
        return

    output_lines = []
    max_name_length = max((len(entry) for entry in files), default=0) if files else 0

    for dir_name in dirs:
        dir_path = os.path.join(config.search_path, dir_name)
        output_lines.extend(scanner.print_directory_tree(dir_path, config.excluded))

    for i, file_name in enumerate(files):
        file_path = os.path.join(config.search_path, file_name)
        pointer = "└── " if i == len(files) - 1 else "├── "
        display = f"{pointer}{file_name:<{max_name_length}}"
        display_clean = f"{pointer}{file_name:<{max_name_length}}"
        if config.show_file_stats:
            lines, size, is_test, is_documented = FileUtils.get_file_stats(file_path, config.included_extensions)
            if lines is not None and size is not None:
                stats_collector.update_stats(file_name, lines, size, is_test, is_documented)
                display += f" {colors.GRAY}[{lines} lines, {FileUtils.format_size(size)}]{colors.RESET}"
                display_clean += f" [{lines} lines, {FileUtils.format_size(size)}]"
        print(display)
        output_lines.append(display_clean)

    if config.show_file_stats:
        print(f"\n{stats_collector.get_summary(config.show_extended_stats)}")

    report_generator.save_report(config.search_path, output_lines)

if __name__ == "__main__":
    main()