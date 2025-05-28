# Changelog

## [v1.0.0] - First Release

### Added
- 🎉 Initial release of **ProjectLens**, a Python-based CLI tool to analyze and document software project structures.
- Directory scanning and hierarchical tree display, excluding common unwanted folders like `.git`, `__pycache__`, etc.
- File statistics collection:
  - Total lines
  - File sizes
  - File type breakdown
- Detection of:
  - Test files (e.g., `test_*.py`)
  - Documentation presence (via docstrings/comments)
- Markdown report generation including:
  - Project tree
  - File count/line count
  - File sizes
  - Test and documentation coverage
  - Largest files list
- Support for custom project paths and file extensions through CLI arguments.
- Optional extended statistics output.
- Smart default: processes the parent folder of the `ProjectLens` module if no path is specified.
- Fully functional without external dependencies (pure standard library).
- Snapshot system: all reports saved in timestamped Markdown files inside the `project_snapshots/` folder.

### Structure
- Modular and clean code structure:
  - `__main__.py` – CLI entry point
  - `main.py` – Program logic
  - `cli.py` – Argument parsing
  - `config.py` – Default settings
  - `file_utils.py` – Line counting, test/doc detection, file sizes
  - `stats_collector.py` – Aggregates statistics
  - `directory_scanner.py` – Traverses and formats the project structure
  - `report_generator.py` – Generates and saves Markdown reports

### Notes
- To run the tool properly, use:
  ```bash
  python -m ProjectLens
