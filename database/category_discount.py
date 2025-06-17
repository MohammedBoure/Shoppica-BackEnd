from .base import Database
import sqlite3
import logging

class CategoryDiscountManager(Database):
    """Manages operations for the category_discounts table in the database."""

    def add_category_discount(self, category_id, discount_percent, starts_at=None, ends_at=None, is_active=1):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO category_discounts (category_id, discount_percent, starts_at, ends_at, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (category_id, discount_percent, starts_at, ends_at, is_active))
                conn.commit()
                discount_id = cursor.lastrowid
                logging.info(f"Category discount added for category {category_id} with ID: {discount_id}")
                return discount_id
        except sqlite3.Error as e:
            logging.error(f"SQLite error adding category discount: {e}")
            return None


    def get_category_discount_by_id(self, discount_id):
        """Retrieves a category discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM category_discounts WHERE id = ?', (discount_id,))
                discount = cursor.fetchone()
                logging.info(f"Retrieved category discount with ID: {discount_id}")
                return discount
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discount by ID {discount_id}: {e}")
            return None

    def get_category_discounts_by_category(self, category_id):
        """Retrieves all discounts for a category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM category_discounts WHERE category_id = ?', (category_id,))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} category discounts for category {category_id}")
                return discounts
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discounts for category {category_id}: {e}")
            return []

    def get_valid_category_discounts(self, category_id):
        """Retrieves valid (active and within date range) discounts for a category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM category_discounts
                    WHERE category_id = ? AND is_active = 1
                    AND (starts_at IS NULL OR starts_at <= ?)
                    AND (ends_at IS NULL OR ends_at >= ?)
                ''', (category_id, self.get_current_timestamp(), self.get_current_timestamp()))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} valid category discounts for category {category_id}")
                return discounts
        except sqlite3.Error as e:
            logging.error(f"Error retrieving valid category discounts for category {category_id}: {e}")
            return []

    def update_category_discount(self, discount_id, discount_percent=None, starts_at=None, ends_at=None, is_active=None):
        """Updates category discount details. Only provided fields are updated."""
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
                    logging.info(f"No updates provided for category discount ID: {discount_id}")
                    return True

                params.append(discount_id)
                query = f'UPDATE category_discounts SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated category discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating category discount {discount_id}: {e}")
            return False

    def delete_category_discount(self, discount_id):
        """Deletes a category discount by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM category_discounts WHERE id = ?', (discount_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted category discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting category discount {discount_id}: {e}")
            return False

    def get_category_discounts(self, page=1, per_page=20):
        """Retrieves category discounts with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM category_discounts')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT cd.*, c.name
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    ORDER BY cd.id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                discounts = cursor.fetchall()
                logging.info(f"Retrieved {len(discounts)} category discounts. Total: {total}")
                return discounts, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discounts: {e}")
            return [], 0