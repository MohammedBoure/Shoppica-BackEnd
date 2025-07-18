# Changelog


## [0.6.0] - 2025-06-26

### Added
- New analytics endpoints:
  - `/analytics/discount-effectiveness`
  - `/analytics/product-performance`
  - `/analytics/customer-retention`
- Initial DB functions for:
  - `/analytics/sales`
  - `/analytics/users`
  - `/analytics/products`
- Dashboard API endpoints:
  - `/products/low_stock`
  - `/orders/number`
  - `/users/number`
  - `/products/number`

### Fixed
- Image saving issue when adding product images via `/products/<int:product_id>/images`
- Image upload and update endpoints to ensure frontend access to uploaded images

### Refactored
- Migrated database layer from `sqlite3` to **SQLAlchemy**:
  - Replaced direct SQL with SQLAlchemy ORM
  - Updated `database/base.py` and all DB operations
- Added helper functions for improved search in APIs


## [0.5.0] - 2025-06-18

### Features
- **product_images**: Added a new `product_images` table to support multiple images per product.
  - Created API endpoints for uploading and retrieving images.
  - Updated related documentation to include `product_images`.

### Fixes
- **Authentication**
  - Fixed admin permission bug where `session['is_admin']` was incorrectly set to false.
  - Ensured admin status is correctly set and used in route protection.

- **Serialization**
  - Converted all `sqlite3.Row` objects to `dict` before using `jsonify` to prevent `TypeError`.
  - Applied to various APIs: addresses, admin endpoints, cart items, discounts.
  - Ensured consistent and valid JSON responses across all endpoints.

- **Address API**
  - Handled missing addresses with clear logging (includes user ID and admin status).
  - Returned proper 404 response if address does not exist.

- **Cart Items**
  - Improved error handling and logging using `logger.error(exc_info=True)`.
  - Applied session-based ownership checks using decorators.
  - Optimized DB calls by reusing fetched items.

- **Discount Endpoints**
  - Replaced `.get()` calls with dict-style access to maintain compatibility with `sqlite3.Row`.

- **Category Discounts**
  - Fixed and refactored all APIs in `apis/category_discounts.py`.

### Refactors
- **Session-Based Architecture**
  - Restructured app to use session-based authentication and user state handling.
  - Updated authentication documentation accordingly.

### Chores
- **CORS Policy**
  - Allowed `https://shoppica-26gr.onrender.com` in CORS.
  - Added `shoppica-testsite.onrender.com` to allowed origins.

- **Documentation**
  - Updated docs to reflect latest changes in architecture, APIs, and database structure.

## [0.4.0] - 2025-06-16

### Changed
- Migrated from **JWT-based authentication** to **session-based authentication** for improved security and better server-side control.

### Added
- Added a **logout endpoint** in `apis/auth.py` to allow users to sign out and invalidate their sessions.
- Implemented **session decorators** to protect routes and simplify session validation logic.

### Improved
- Improved **session creation and handling** to streamline developer experience and ensure more reliable authentication flow.


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
