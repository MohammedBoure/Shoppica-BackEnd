from .base import Database
import sqlite3
import logging

class CategoryDiscountManager(Database):
    """Manages operations for the category_discounts table in the database."""

    def add_category_discount(self, category_id, discount_percent, starts_at=None, ends_at=None, is_active=1):
        """Adds a new category discount."""
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
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cd.*, c.name
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    WHERE cd.id = ?
                ''', (discount_id,))
                discount = cursor.fetchone()
                if discount:
                    discount_dict = dict(discount)
                    logging.info(f"Retrieved category discount with ID: {discount_id}")
                    return discount_dict
                logging.warning(f"No category discount found with ID: {discount_id}")
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discount by ID {discount_id}: {e}")
            return None

    def get_category_discounts_by_category(self, category_id):
        """Retrieves all discounts for a category."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cd.*, c.name
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    WHERE cd.category_id = ?
                ''', (category_id,))
                discounts = [dict(discount) for discount in cursor.fetchall()]
                logging.info(f"Retrieved {len(discounts)} category discounts for category {category_id}")
                return discounts
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discounts for category {category_id}: {e}")
            return []

    def get_valid_category_discounts(self, category_id):
        """Retrieves valid (active and within date range) discounts for a category."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cd.*, c.name
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    WHERE cd.category_id = ? AND cd.is_active = 1
                    AND (cd.starts_at IS NULL OR cd.starts_at <= ?)
                    AND (cd.ends_at IS NULL OR cd.ends_at >= ?)
                ''', (category_id, self.get_current_timestamp(), self.get_current_timestamp()))
                discounts = [dict(discount) for discount in cursor.fetchall()]
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
                conn.row_factory = sqlite3.Row
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
                discounts = [dict(discount) for discount in cursor.fetchall()]
                logging.info(f"Retrieved {len(discounts)} category discounts. Total: {total}")
                return discounts, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discounts: {e}")
            return [], 0

    def search_category_discounts(self, category_id=None, min_discount=None, max_discount=None, is_active=None, page=1, per_page=20):
        """Searches category discounts based on category_id, discount range, or is_active with pagination."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                conditions = []
                params = []

                if category_id is not None:
                    conditions.append('cd.category_id = ?')
                    params.append(category_id)
                if min_discount is not None:
                    conditions.append('cd.discount_percent >= ?')
                    params.append(min_discount)
                if max_discount is not None:
                    conditions.append('cd.discount_percent <= ?')
                    params.append(max_discount)
                if is_active is not None:
                    conditions.append('cd.is_active = ?')
                    params.append(is_active)

                where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
                
                # Count total discounts matching the criteria
                count_query = f'''
                    SELECT COUNT(*) as total
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    {where_clause}
                '''
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # Fetch discounts with pagination
                query = f'''
                    SELECT cd.*, c.name
                    FROM category_discounts cd
                    JOIN categories c ON cd.category_id = c.id
                    {where_clause}
                    ORDER BY cd.id
                    LIMIT ? OFFSET ?
                '''
                params.extend([per_page, (page - 1) * per_page])
                cursor.execute(query, params)
                discounts = [dict(discount) for discount in cursor.fetchall()]
                logging.info(f"Found {len(discounts)} category discounts matching search criteria. Total: {total}")
                return discounts, total
        except sqlite3.Error as e:
            logging.error(f"Error searching category discounts: {e}")
            return [], 0

    def delete_category_discounts_by_category(self, category_id):
        """Deletes all discounts for a specific category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM category_discounts WHERE category_id = ?', (category_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} category discounts for category {category_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting category discounts for category {category_id}: {e}")
            return 0

    def get_category_discount_stats(self):
        """Returns statistics about category discounts."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_discounts FROM category_discounts')
                total_discounts = cursor.fetchone()['total_discounts']
                cursor.execute('SELECT COUNT(*) as active_discounts FROM category_discounts WHERE is_active = 1')
                active_discounts = cursor.fetchone()['active_discounts']
                cursor.execute('SELECT COUNT(DISTINCT category_id) as categories_with_discounts FROM category_discounts')
                categories_with_discounts = cursor.fetchone()['categories_with_discounts']
                cursor.execute('SELECT AVG(discount_percent) as average_discount FROM category_discounts')
                average_discount = cursor.fetchone()['average_discount'] or 0.0
                stats = {
                    'total_discounts': total_discounts,
                    'active_discounts': active_discounts,
                    'categories_with_discounts': categories_with_discounts,
                    'average_discount': round(average_discount, 2)
                }
                logging.info(f"Retrieved category discount stats: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category discount stats: {e}")
            return {'total_discounts': 0, 'active_discounts': 0, 'categories_with_discounts': 0, 'average_discount': 0.0}

    def get_category_discount_stats_by_category(self, category_id):
        """Returns discount statistics for a specific category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_discounts FROM category_discounts WHERE category_id = ?', (category_id,))
                total_discounts = cursor.fetchone()['total_discounts']
                cursor.execute('SELECT COUNT(*) as active_discounts FROM category_discounts WHERE category_id = ? AND is_active = 1', (category_id,))
                active_discounts = cursor.fetchone()['active_discounts']
                cursor.execute('SELECT AVG(discount_percent) as average_discount FROM category_discounts WHERE category_id = ?', (category_id,))
                average_discount = cursor.fetchone()['average_discount'] or 0.0
                stats = {
                    'total_discounts': total_discounts,
                    'active_discounts': active_discounts,
                    'average_discount': round(average_discount, 2)
                }
                logging.info(f"Retrieved discount stats for category {category_id}: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving discount stats for category {category_id}: {e}")
            return {'total_discounts': 0, 'active_discounts': 0, 'average_discount': 0.0}

    def toggle_category_discount_status(self, discount_id):
        """Toggles the is_active status of a category discount."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT is_active FROM category_discounts WHERE id = ?', (discount_id,))
                discount = cursor.fetchone()
                if not discount:
                    logging.warning(f"No category discount found with ID: {discount_id}")
                    return False
                new_status = 0 if discount['is_active'] == 1 else 1
                cursor.execute('UPDATE category_discounts SET is_active = ? WHERE id = ?', (new_status, discount_id))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Toggled category discount status with ID: {discount_id} to is_active={new_status}")
                    return True
                return False
        except sqlite3.Error as e:
            logging.error(f"Error toggling category discount status for ID {discount_id}: {e}")
            return False