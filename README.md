# Shoppica BackEnd

Welcome to the backend repository for Shoppica, an e-commerce platform. This project contains the server-side logic, database structure, and documentation for the Shoppica application.

## Project Structure

The project is organized as follows:

- **database/**: Contains the database models and the SQLite database file (`shop.db`).
  - [Explore the database directory](./database/)
- **docs/**: Contains documentation in multiple languages.
  - [Arabic README](./docs/ar/README.md) (النسخة العربية)
  - English documentation
- **test/**: Contains test scripts for the database.
- **commit**: Utility script for version control.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Shoppica/BackEnd
   ```

2. **Install Dependencies**:
   Ensure you have Python installed, then install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   The database models are defined in the `database/` directory. The SQLite database file is located at `database/shop.db`. Refer to the [database documentation](./docs/ar/database.md) for details on the schema and usage.

4. **Running Tests**:
   Tests are located in the `test/database/` directory. Run them using:
   ```bash
   python -m unittest test/database/test1.py
   ```

## Documentation

- For detailed information about the database structure, check the following:
  - [Arabic Database Documentation](./docs/ar/database.md) (النسخة العربية)
  - [English Database Documentation](./docs/en/database.md)
- For Arabic general documentation, see the [Arabic README](./docs/ar/README.md).

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License.