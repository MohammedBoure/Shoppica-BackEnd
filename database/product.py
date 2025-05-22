from .base import Database
import sqlite3
import logging

class ProductManager(Database):
    """Manages operations for the products table in the database."""

    def add_product(self, name, price, stock_quantity, category_id=None, description=None, image_url=None, is_active=1):
        """Adds a new product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (name, description, price, stock_quantity, category_id, image_url, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, price, stock_quantity, category_id, image_url, is_active, self.get_current_timestamp()))
                conn.commit()
                product_id = cursor.lastrowid
                logging.info(f"Product {name} added with ID: {product_id}")
                return product_id
        except sqlite3.Error as e:
            logging.error(f"Error adding product {name}: {e}")
            return None

    def get_product_by_id(self, product_id):
        """Retrieves a product by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()
                logging.info(f"Retrieved product with ID: {product_id}")
                return product
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product by ID {product_id}: {e}")
            return None

    def get_products_by_category(self, category_id):
        """Retrieves all products in a category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products WHERE category_id = ? AND is_active = 1', (category_id,))
                products = cursor.fetchall()
                logging.info(f"Retrieved {len(products)} products for category {category_id}")
                return products
        except sqlite3.Error as e:
            logging.error(f"Error retrieving products for category {category_id}: {e}")
            return []

    def update_product(self, product_id, name=None, description=None, price=None, stock_quantity=None, category_id=None, image_url=None, is_active=None):
        """Updates product details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if name is not None:
                    updates.append('name = ?')
                    params.append(name)
                if description is not None:
                    updates.append('description = ?')
                    params.append(description)
                if price is not None:
                    updates.append('price = ?')
                    params.append(price)
                if stock_quantity is not None:
                    updates.append('stock_quantity = ?')
                    params.append(stock_quantity)
                if category_id is not None:
                    updates.append('category_id = ?')
                    params.append(category_id)
                if image_url is not None:
                    updates.append('image_url = ?')
                    params.append(image_url)
                if is_active is not None:
                    updates.append('is_active = ?')
                    params.append(is_active)
                
                if not updates:
                    logging.info(f"No updates provided for product ID: {product_id}")
                    return True

                params.append(product_id)
                query = f'UPDATE products SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated product with ID: {product_id}")
                    return True
                else:
                    logging.warning(f"No product found with ID: {product_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating product {product_id}: {e}")
            return False

    def delete_product(self, product_id):
        """Deletes a product by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted product with ID: {product_id}")
                    return True
                else:
                    logging.warning(f"No product found with ID: {product_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting product {product_id}: {e}")
            return False

    def get_products(self, page=1, per_page=20):
        """Retrieves products with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM products WHERE is_active = 1')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM products
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                products = cursor.fetchall()
                logging.info(f"Retrieved {len(products)} products. Total: {total}")
                return products, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving products: {e}")
            return [], 0