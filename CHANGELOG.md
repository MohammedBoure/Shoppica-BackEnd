## [0.3.0] - 2025-05-24

### Added
- JWT authentication integrated for APIs using `flask_jwt_extended`
- Decorator-based route protection for admin-only and user-only APIs
- New API grouping:
  - `apis/` now contains all user and admin routes
  - Admin-only routes defined explicitly
- Unit tests for selected API endpoints
- Auto-generated `admin` user added to DB on initialization (`admin@gmail.com` / `admin`)
- `clear_all_users()` method added to `database/user.py` for database cleanup
- `__init__.py` added to `apis/` for better import management
- `requirements.txt` and `Procfile` added for deployment compatibility (e.g., Heroku)
- `project_snapshots/` folder added to store project state and stats per commit

### Changed
- Renamed `admin_apis/` to `apis/`
- Renamed test file `test1.py` to `all_tables.py` and updated user table test to account for default admin user
- `check_password()` and `hash_password()` in `database/base.py` now use `bcrypt` for secure hashing

### Fixed
- Bug fix in `apis/category_discounts.py`

------------------------------------------------------------

## [0.2.0] - 2025-05-23

### Added
- Admin API endpoints (tested with `curl`) under `admin_apis/`:
  - addresses.py
  - cart_item.py
  - category.py
  - category_discounts.py
  - discount_usage.py
  - discounts.py
  - order_item.py
  - orders.py
  - payment.py
  - product_discounts.py
  - products.py
  - review.py
  - user.py

### Changed
- Simplified Mermaid ER diagram by removing column-level details

### Fixed
- Typo in the README file

------------------------------------------------------------

## [0.1.0] - 2025-05-22

### Added
- Initial project structure for the `database/` module
- Base `Database` class to initialize SQLite schema and manage tables
- Classes for managing all major tables (users, products, orders, etc.)
- First integration test for database interaction
- Full bilingual (Arabic + English) documentation for the schema
- Mermaid ER diagram for visual representation of table relations
