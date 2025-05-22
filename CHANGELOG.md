## [0.1.0] - 2025-05-22

### Added
- Initial project structure for the `database/` module
- Base `Database` class to initialize SQLite schema and manage tables
- Classes for managing all major tables (users, products, orders, etc.)
- First integration test for database interaction
- Full bilingual (Arabic + English) documentation for the schema
- Mermaid ER diagram for visual representation of table relations

------------------------------------------------------------

## [0.2.1] - 2025-05-23

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