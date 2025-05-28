# ProjectLens

**ProjectLens** is a Python-based tool designed to analyze the directory structure and collect detailed statistics about files and folders in any software project. It generates Markdown reports summarizing the project structure, file counts, line counts, file sizes, test coverage, and documentation coverage. The tool is flexible, supporting multiple file types (e.g., Python, JavaScript, Java, C++, etc.) and is suitable for a wide range of projects.

## Features

- **Directory Scanning**: Displays a hierarchical directory tree, excluding unwanted files/folders (e.g., `.git`, `__pycache__`).
- **File Statistics**: Collects data on line counts, file sizes, and file types.
- **Test and Documentation Detection**: Identifies test files (e.g., `test_*.py`) and documented files (e.g., files with docstrings or comments).
- **Markdown Reports**: Generates structured Markdown reports with directory structure and statistics.
- **Command-Line Interface (CLI)**: Allows customization of the project path, file extensions, and statistics display via command-line arguments.
- **Flexible Statistics**: Option to show basic statistics (lines, sizes) or extended statistics (test coverage, documentation, largest files).
- **Smart Default Path**: When run with `python -m ProjectLens` without arguments, it processes the parent directory of the `ProjectLens` module.

## Installation

### Requirements
- Python 3.6 or higher.
- No external dependencies (uses standard libraries: `os`, `argparse`, `typing`).

### Steps
1. Clone the repository or download the project files to a local directory:
   ```bash
   git clone https://github.com/your-repo/ProjectLens.git
   ```
   or download and extract the ZIP file.

2. Navigate to the `ProjectLens` directory:
   ```bash
   cd ProjectLens
   ```

3. Run the tool using Python:
   ```bash
   python -m ProjectLens
   ```
   **Note**: Always use `python -m ProjectLens` to run the tool, as running `python main.py` directly will result in import errors due to the package structure.

## Usage

Run the tool using the `python -m ProjectLens` command. By default, it processes the parent directory of the `ProjectLens` module. You can customize the behavior with command-line arguments.

### Command-Line Options
```bash
python -m ProjectLens [options]
```

| Option                   | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `--path <path>`          | Path to the project directory to analyze (default: parent of ProjectLens).   |
| `--show-stats`           | Show file statistics (lines, size) (default: True).                          |
| `--show-extended-stats`  | Show extended statistics (test coverage, documentation, largest files).      |
| `--save-report`          | Save the report to a Markdown file (default: True).                          |
| `--extensions <exts>`    | Comma-separated list of file extensions to analyze (e.g., `.py,.js,.java`).  |

### Examples

1. **Analyze the parent directory of ProjectLens**:
   ```bash
   python -m ProjectLens
   ```
   - Processes the directory containing the `ProjectLens` folder.
   - Example: If `ProjectLens` is in `~/Desktop/ProjectLens`, it analyzes `~/Desktop/`.

2. **Analyze a specific directory**:
   ```bash
   python -m ProjectLens --path /path/to/your/project
   ```

3. **Analyze with extended statistics**:
   ```bash
   python -m ProjectLens --show-extended-stats
   ```
   - Includes test coverage, documentation coverage, and largest files in the output.

4. **Analyze specific file extensions**:
   ```bash
   python -m ProjectLens --extensions .py,.js
   ```
   - Only processes files with `.py` and `.js` extensions.

### Example Output
For a project in `/home/user/Desktop/` with `ProjectLens` in `/home/user/Desktop/ProjectLens`:
```plaintext
/home/user/Desktop/
Desktop/
├── OtherProject/
│   ├── file1.py [100 lines, 1.2KB]
│   ├── file2.js [50 lines, 0.8KB]
│       (2 files, 150 lines, 2.0KB)

Total folders: 1
Total files: 2
Total lines: 150
Total size: 2.0KB

File types:
- .py: 1 files (100 lines, 1.2KB)
- .js: 1 files (50 lines, 0.8KB)

Top 3 largest files:
- file1.py: 1.2KB
- file2.js: 0.8KB

Test coverage: 0/2 code files (0.0%)
Documentation coverage: 0/2 code files (0.0%)
```

Reports are saved to the `project_snapshots` folder as `YYYY-MM-DD_HHMMSS.md`.

## Configuration

The tool's configuration is defined in `config.py`. Key settings include:

- **search_path**: The default project directory (set to the parent of `ProjectLens` via CLI).
- **excluded**: List of files/folders to exclude (e.g., `.git`, `.venv`, `__pycache__`).
- **included_extensions**: File extensions to analyze (e.g., `.py`, `.js`, `.java`, `.cpp`).
- **show_file_stats**: Enable/disable basic file statistics (default: True).
- **show_extended_stats**: Enable/disable extended statistics (default: False).
- **save_to_file**: Save reports to Markdown files (default: True).
- **snapshot_folder**: Directory for saving reports (default: `project_snapshots`).

You can modify these settings via command-line arguments or by editing `config.py`.

## Project Structure

```plaintext
ProjectLens/
├── __main__.py         # Entry point for running the tool
├── cli.py             # Command-line interface parsing
├── config.py          # Configuration settings
├── directory_scanner.py # Directory traversal and tree printing
├── file_utils.py      # File operations (size, lines, test/doc detection)
├── main.py            # Main logic for running the tool
├── report_generator.py # Markdown report generation
├── stats_collector.py  # Statistics collection and summarization
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue on the repository or contact the maintainers.