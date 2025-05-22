from .base import Database
import sqlite3
import logging

class DiscountUsageManager(Database):
    """Manages operations for the discount_usage table in the database."""

    def add_discount_usage(self, discount_id, user_id):
        """Records a discount usage by a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO discount_usage (discount_id, user_id, used_at)
                    VALUES (?, ?, ?)
                ''', (discount_id, user_id, self.get_current_timestamp()))
                conn.commit()
                usage_id = cursor.lastrowid
                logging.info(f"Discount usage added for discount {discount_id} by user {user_id} with ID: {usage_id}")
                return usage_id
        except sqlite3.Error as e:
            logging.error(f"Error adding discount usage for discount {discount_id}, user {user_id}: {e}")
            return None

    def get_discount_usage_by_id(self, usage_id):
        """Retrieves a discount usage by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM discount_usage WHERE id = ?', (usage_id,))
                usage = cursor.fetchone()
                logging.info(f"Retrieved discount usage with ID: {usage_id}")
                return usage
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount usage by ID {usage_id}: {e}")
            return None

    def get_discount_usages_by_discount(self, discount_id):
        """Retrieves all usages for a discount."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM discount_usage WHERE discount_id = ?', (discount_id,))
                usages = cursor.fetchall()
                logging.info(f"Retrieved {len(usages)} discount usages for discount {discount_id}")
                return usages
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount usages for discount {discount_id}: {e}")
            return []

    def get_discount_usages_by_user(self, user_id):
        """Retrieves all discount usages for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM discount_usage WHERE user_id = ?', (user_id,))
                usages = cursor.fetchall()
                logging.info(f"Retrieved {len(usages)} discount usages for user {user_id}")
                return usages
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount usages for user {user_id}: {e}")
            return []

    def delete_discount_usage(self, usage_id):
        """Deletes a discount usage by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM discount_usage WHERE id = ?', (usage_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted discount usage with ID: {usage_id}")
                    return True
                else:
                    logging.warning(f"No discount usage found with ID: {usage_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting discount usage {usage_id}: {e}")
            return False

    def get_discount_usages(self, page=1, per_page=20):
        """Retrieves discount usages with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM discount_usage')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT du.*, d.code
                    FROM discount_usage du
                    JOIN discounts d ON du.discount_id = d.id
                    ORDER BY du.used_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                usages = cursor.fetchall()
                logging.info(f"Retrieved {len(usages)} discount usages. Total: {total}")
                return usages, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount usages: {e}")
            return [], 0