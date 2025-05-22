from .base import Database
import sqlite3
import logging

class DiscountManager(Database):
    """Manages operations for the discounts table in the database."""

    def add_discount(self, code, discount_percent, max_uses=None, expires_at=None, description=None):
        """Adds a new discount."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO discounts (code, description, discount_percent, max_uses, expires_at, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (code, description, discount_percent, max_uses, expires_at))
                conn.commit()
                discount_id = cursor.lastrowid
                logging.info(f"Discount {code} added with ID: {discount_id}")
                return discount_id
        except sqlite3.Error as e:
            logging.error(f"Error adding discount {code}: {e}")
            return None

    def get_discount_by_id(self, discount_id):
        """Retrieves a discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM discounts WHERE id = ?', (discount_id,))
                discount = cursor.fetchone()
                logging.info(f"Retrieved discount with ID: {discount_id}")
                return discount
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount by ID {discount_id}: {e}")
            return None

    def get_discount_by_code(self, code):
        """Retrieves a discount by its code."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM discounts WHERE code = ?', (code,))
                discount = cursor.fetchone()
                logging.info(f"Retrieved discount with code: {code}")
                return discount
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount by code {code}: {e}")
            return None

    def get_valid_discount(self, code):
        """Retrieves a valid discount by code."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM discounts
                    WHERE code = ? AND is_active = 1
                    AND (expires_at IS NULL OR expires_at > ?)
                    AND (max_uses IS NULL OR (
                        SELECT COUNT(*) FROM discount_usage WHERE discount_id = discounts.id
                    ) < max_uses)
                ''', (code, self.get_current_timestamp()))
                discount = cursor.fetchone()
                logging.info(f"Retrieved valid discount with code: {code}")
                return discount
        except sqlite3.Error as e:
            logging.error(f"Error retrieving valid discount {code}: {e}")
            return None

    def update_discount(self, discount_id, code=None, description=None, discount_percent=None, max_uses=None, expires_at=None, is_active=None):
        """Updates discount details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if code is not None:
                    updates.append('code = ?')
                    params.append(code)
                if description is not None:
                    updates.append('description = ?')
                    params.append(description)
                if discount_percent is not None:
                    updates.append('discount_percent = ?')
                    params.append(discount_percent)
                if max_uses is not None:
                    updates.append('max_uses = ?')
                    params.append(max_uses)
                if expires_at is not None:
                    updates.append('expires_at = ?')
                    params.append(expires_at)
                if is_active is not None:
                    updates.append('is_active = ?')
                    params.append(is_active)
                
                if not updates:
                    logging.info(f"No updates provided for discount ID: {discount_id}")
                    return True

                params.append(discount_id)
                query = f'UPDATE discounts SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating discount {discount_id}: {e}")
            return False

    def delete_discount(self, discount_id):
        """Deletes a discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM discounts WHERE id = ?', (discount_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting discount {discount_id}: {e}")
            return False

    def get_discounts(self, page=1, per_page=20):
        """Retrieves discounts with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM discounts')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM discounts
                    ORDER BY id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} discounts. Total: {total}")
                return discounts, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discounts: {e}")
            return [], 0