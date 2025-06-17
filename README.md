# Shoppica BackEnd

This is the backend repository for Shoppica, an e-commerce platform, containing server-side logic, database structure, and API documentation.

## Link BackEnd: 
 - https://shoppica-backend.onrender.com/api
## Project Structure

- **database/**: Database models and SQLite file (`shop.db`).
  - [Details](./database/)
- **docs/**: Documentation in multiple languages.
  - **ar/**: Arabic documentation.
    - [README](./docs/ar/README.md)
    - [Database](./docs/ar/database.md)
  - **en/**: English documentation for APIs and database.
- **test/**: Database test scripts.
- **commit**: Version control utility.

## Getting Started

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd Shoppica/BackEnd
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   SQLite database (`shop.db`) is in `database/`. See [database docs](./docs/en/database.md).

4. **Run Tests**:
   ```bash
   python -m unittest test/database/test1.py
   ```

## API Documentation

API details are in `/docs/en/`:
- [Addresses](./docs/en/addresses.md): Manage user addresses.
- [Cart Item](./docs/en/cart_item.md): Handle cart items.
- [Category](./docs/en/category.md): Manage product categories.
- [Category Discounts](./docs/en/category_discounts.md): Category-specific discounts.
- [Discount Usage](./docs/en/discount_usage.md): Track discount usage.
- [Discounts](./docs/en/discounts.md): Manage discount codes.
- [Order Item](./docs/en/order_item.md): Manage order items.
- [Orders](./docs/en/orders.md): Handle customer orders.
- [Payment](./docs/en/payment.md): Process payments.
- [Product Discounts](./docs/en/product_discounts.md): Product-specific discounts.
- [Products](./docs/en/products.md): Manage product listings.
- [Review](./docs/en/review.md): Manage product reviews.
- [User](./docs/en/user.md): User account management.

## Contributing

1. Fork the repository.
2. Create a branch (`git checkout -b feature-branch`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push branch (`git push origin feature-branch`).
5. Create a pull request.

## License

MIT License.# Shoppica-FrontEnd
