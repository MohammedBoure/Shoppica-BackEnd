# ProjectLens

ProjectLens is a Python-based tool designed to analyze and visualize the structure of a project directory. It generates a detailed report of the directory tree, including file and folder counts, line counts, file sizes, file type statistics, largest files, test coverage estimates, and API documentation coverage. The output is displayed in the console and saved as a markdown file for easy reference.

## Features

- **Directory Tree Visualization**: Displays a hierarchical view of the project directory, excluding specified files/folders.
- **File Statistics**: Provides line counts and file sizes for each file (optional).
- **Project Metrics**:
  - Total number of files and folders.
  - Breakdown of file types (e.g., `.py`, `.md`, `.db`) with their counts, lines, and sizes.
  - Top 3 largest files by size.
  - Test coverage estimate based on the presence of test files (e.g., files starting with `test_`).
  - API documentation coverage estimate based on docstrings in Python files.
- **Markdown Report**: Saves a comprehensive report in the `project_snapshots` directory with a timestamped filename.
- **Customizable Configuration**: Allows excluding specific files/folders and toggling file statistics or report saving.

## Installation

### Prerequisites
- Python 3.6 or higher.
- Write permissions in the directory where the `project_snapshots` folder will be created.

### Setup
1. Clone or download the `ProjectLens` directory to your project folder (e.g., `/home/pluto/Desktop/Shoppica/BackEnd`).
2. Ensure the following files are in the `ProjectLens` directory:
   ```
   ProjectLens/
   ├── __init__.py
   ├── __main__.py
   ├── config.py
   ├── file_utils.py
   ├── directory_scanner.py
   ├── stats_collector.py
   ├── report_generator.py
   ├── main.py
   ```
3. No external dependencies are required beyond the Python standard library.

## Usage

ProjectLens can be run in two ways:

### 1. As a Python Module
From the parent directory containing the `ProjectLens` folder (e.g., `/home/pluto/Desktop/Shoppica/BackEnd`), run:
```bash
python -m ProjectLens
```

### 2. As a Script
From the parent directory, run:
```bash
python ProjectLens/main.py
```

### Output
- **Console**: Displays a colored directory tree with file statistics (if enabled) and a summary of project metrics.
- **Markdown Report**: Saves a file (e.g., `project_snapshots/2025-05-24_111415.md`) containing:
  - Directory structure.
  - Project statistics, including total files/folders, file type breakdown, largest files, test coverage, and documentation coverage.

## Configuration

The configuration is defined in `ProjectLens/config.py`. Key settings include:

- **search_path**: The directory to analyze (default: `/home/pluto/Desktop/Shoppica/BackEnd`).
- **excluded**: List of files/folders to ignore (e.g., `["flask", ".git", ".venv", "__pycache__", "project_snapshots", "ProjectLens"]`).
- **show_file_stats**: Toggle to show line counts and file sizes (default: `True`).
- **save_to_file**: Toggle to save the markdown report (default: `True`).
- **snapshot_folder**: Directory for saving reports (default: `project_snapshots`).
- **output_filename**: Timestamped markdown file name (e.g., `2025-05-24_111415.md`).

To customize, edit `config.py` or extend the tool to accept command-line arguments (future enhancement).

## Example Output

### Console Output
```
/home/pluto/Desktop/Shoppica/BackEnd
BackEnd/
├── apis/
│   ├── base.py [150 lines, 13.1KB]
│   ├── category_discounts.py [120 lines, 11.1KB]
│   └── (2 files, 270 lines, 24.2KB)
├── shop.db [167 lines, 144.0KB]
└── (1 files, 167 lines, Demographic data is only available with a paid subscription
Total folders: 7
Total files: 69
File types:
- .py: 48 files (7,000 lines, 300.0KB)
- .md: 18 files (4,800 lines, 140.0KB)
- .db: 1 file (167 lines, 144.0KB)
Top 3 largest files:
- shop.db: 144.0KB
- base.py: 13.1KB
- category_discounts.py: 11.1KB
Test coverage (by file presence): 12/31 modules (38.7%)
API Documentation coverage: 13/15 (87.0%)
Report saved to project_snapshots/2025-05-24_111415.md
```

### Markdown Report
The markdown report includes the directory structure and statistics in a formatted structure:
```markdown
# Directory Report: /home/pluto/Desktop/Shoppica/BackEnd

*Generated on 2025-05-24 11:14:15*

## Directory Structure
```
/home/pluto/Desktop/Shoppica/BackEnd
BackEnd/
├── apis/
│   ├── base.py [150 lines, 13.1KB]
│   ├── category_discounts.py [120 lines, 11.1KB]
│   └── (2 files, 270 lines, 24.2KB)
├── shop.db [167 lines, 144.0KB]
└── (1 files, 167 lines, 144.0KB)
```

## Project Statistics
```
Total folders: 7
Total files: 69
Total lines: 7,967
Total size: 584.0KB
...
```

## Project Structure

The tool is organized into modular components for scalability and maintainability:
- `config.py`: Configuration settings.
- `file_utils.py`: File-related utilities (e.g., size formatting, stats collection).
- `directory_scanner.py`: Directory traversal and tree printing.
- `stats_collector.py`: Project statistics collection.
- `report_generator.py`: Markdown report generation.
- `main.py`: Core logic orchestration.
- `__main__.py`: Entry point for module execution.
- `__init__.py`: Marks the directory as a Python package.

## Future Enhancements
- Support for command-line arguments to customize configuration.
- Additional output formats (e.g., HTML, JSON).
- Enhanced test coverage analysis using test framework parsing.
- Visualization of directory structure as a diagram.

## Contributing
Contributions are welcome! Please submit issues or pull requests to the repository.

## License
This project is licensed under the MIT License.