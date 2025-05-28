import argparse
import os

def parse_arguments():
    """Parse command-line arguments for ProjectLens."""
    # Get the parent directory of the ProjectLens module
    module_path = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.dirname(module_path)  # Parent of ProjectLens directory

    parser = argparse.ArgumentParser(
        description="ProjectLens: A tool to analyze project directory structure and statistics.\n"
                    "Run with 'python -m ProjectLens' to use the parent directory of the ProjectLens module, "
                    "or specify a path with '--path /path/to/project'."
    )
    parser.add_argument(
        "--path",
        default=default_path,
        help="Path to the project directory to analyze (default: parent directory of ProjectLens module)"
    )
    parser.add_argument(
        "--show-stats",
        action="store_true",
        default=True,
        help="Show file statistics (lines, size) (default: True)"
    )
    parser.add_argument(
        "--show-extended-stats",
        action="store_true",
        default=False,
        help="Show extended statistics (test coverage, documentation, largest files)"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        default=True,
        help="Save the report to a file (default: True)"
    )
    parser.add_argument(
        "--extensions",
        help="Comma-separated list of file extensions to analyze (e.g., .py,.js,.java)"
    )
    return parser.parse_args()