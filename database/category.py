from .base import Database
import sqlite3
import logging

class CategoryManager(Database):
    """Manages operations for the categories table in the database."""

    def add_category(self, name, parent_id=None):
        """Adds a new category."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO categories (name, parent_id)
                    VALUES (?, ?)
                ''', (name, parent_id))
                conn.commit()
                category_id = cursor.lastrowid
                logging.info(f"Category {name} added with ID: {category_id}")
                return category_id
        except sqlite3.Error as e:
            logging.error(f"Error adding category {name}: {e}")
            return None

    def get_category_by_id(self, category_id):
        """Retrieves a category by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
                category = cursor.fetchone()
                logging.info(f"Retrieved category with ID: {category_id}")
                return category
        except sqlite3.Error as e:
            logging.error(f"Error retrieving category by ID {category_id}: {e}")
            return None

    def get_categories_by_parent(self, parent_id=None):
        """Retrieves all categories with the specified parent_id (or top-level if None)."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if parent_id is None:
                    cursor.execute('SELECT * FROM categories WHERE parent_id IS NULL')
                else:
                    cursor.execute('SELECT * FROM categories WHERE parent_id = ?', (parent_id,))
                categories = cursor.fetchall()
                logging.info(f"Retrieved {len(categories)} categories with parent_id: {parent_id}")
                return categories
        except sqlite3.Error as e:
            logging.error(f"Error retrieving categories with parent_id {parent_id}: {e}")
            return []

    def update_category(self, category_id, name=None, parent_id=None):
        """Updates category details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if name is not None:
                    updates.append('name = ?')
                    params.append(name)
                if parent_id is not None:
                    updates.append('parent_id = ?')
                    params.append(parent_id)
                
                if not updates:
                    logging.info(f"No updates provided for category ID: {category_id}")
                    return True

                params.append(category_id)
                query = f'UPDATE categories SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated category with ID: {category_id}")
                    return True
                else:
                    logging.warning(f"No category found with ID: {category_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating category {category_id}: {e}")
            return False

    def delete_category(self, category_id):
        """Deletes a category by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted category with ID: {category_id}")
                    return True
                else:
                    logging.warning(f"No category found with ID: {category_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting category {category_id}: {e}")
            return False

    def get_categories(self, page=1, per_page=20):
        """Retrieves categories with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM categories')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM categories
                    ORDER BY name
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                categories = cursor.fetchall()
                logging.info(f"Retrieved {len(categories)} categories. Total: {total}")
                return categories, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving categories: {e}")
            return [], 0