from .base import Database
import sqlite3
import logging

class ProductDiscountManager(Database):
    """Manages operations for the product_discounts table in the database."""

    def add_product_discount(self, product_id, discount_percent, starts_at=None, ends_at=None, is_active=1):
        """Adds a new discount for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO product_discounts (product_id, discount_percent, starts_at, ends_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product_id, discount_percent, starts_at, ends_at, is_active))
                conn.commit()
                discount_id = cursor.lastrowid
                logging.info(f"Product discount added for product {product_id} with ID: {discount_id}")
                return discount_id
        except sqlite3.Error as e:
            logging.error(f"Error adding product discount for product {product_id}: {e}")
            return None

    def get_product_discount_by_id(self, discount_id):
        """Retrieves a product discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM product_discounts WHERE id = ?', (discount_id,))
                discount = cursor.fetchone()
                logging.info(f"Retrieved product discount with ID: {discount_id}")
                return discount
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product discount by ID {discount_id}: {e}")
            return None

    def get_product_discounts_by_product(self, product_id):
        """Retrieves all discounts for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM product_discounts WHERE product_id = ?', (product_id,))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} product discounts for product {product_id}")
                return discounts
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product discounts for product {product_id}: {e}")
            return []

    def get_valid_product_discounts(self, product_id):
        """Retrieves valid (active and within date range) discounts for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM product_discounts
                    WHERE product_id = ? AND is_active = 1
                    AND (starts_at IS NULL OR starts_at <= ?)
                    AND (ends_at IS NULL OR ends_at >= ?)
                ''', (product_id, self.get_current_timestamp(), self.get_current_timestamp()))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} valid product discounts for product {product_id}")
                return discounts
        except sqlite3.Error as e:
            logging.error(f"Error retrieving valid product discounts for product {product_id}: {e}")
            return []

    def update_product_discount(self, discount_id, discount_percent=None, starts_at=None, ends_at=None, is_active=None):
        """Updates product discount details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if discount_percent is not None:
                    updates.append('discount_percent = ?')
                    params.append(discount_percent)
                if starts_at is not None:
                    updates.append('starts_at = ?')
                    params.append(starts_at)
                if ends_at is not None:
                    updates.append('ends_at = ?')
                    params.append(ends_at)
                if is_active is not None:
                    updates.append('is_active = ?')
                    params.append(is_active)
                
                if not updates:
                    logging.info(f"No updates provided for product discount ID: {discount_id}")
                    return True

                params.append(discount_id)
                query = f'UPDATE product_discounts SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated product discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No product discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating product discount {discount_id}: {e}")
            return False

    def delete_product_discount(self, discount_id):
        """Deletes a product discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM product_discounts WHERE id = ?', (discount_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted product discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No product discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting product discount {discount_id}: {e}")
            return False

    def get_product_discounts(self, page=1, per_page=20):
        """Retrieves product discounts with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM product_discounts')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT pd.*, p.name
                    FROM product_discounts pd
                    JOIN products p ON pd.product_id = p.id
                    ORDER BY pd.id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} product discounts. Total: {total}")
                return discounts, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving product discounts: {e}")
            return [], 0