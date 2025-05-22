from .base import Database
import sqlite3
import logging

class CartItemManager(Database):
    """Manages operations for the cart_items table in the database."""

    def add_cart_item(self, user_id, product_id, quantity):
        """Adds a product to a user's cart."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO cart_items (user_id, product_id, quantity, added_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, product_id, quantity, self.get_current_timestamp()))
                conn.commit()
                cart_item_id = cursor.lastrowid
                logging.info(f"Added cart item for user {user_id}, product {product_id} with ID: {cart_item_id}")
                return cart_item_id
        except sqlite3.Error as e:
            logging.error(f"Error adding cart item for user {user_id}, product {product_id}: {e}")
            return None

    def get_cart_item_by_id(self, cart_item_id):
        """Retrieves a cart item by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM cart_items WHERE id = ?', (cart_item_id,))
                cart_item = cursor.fetchone()
                logging.info(f"Retrieved cart item with ID: {cart_item_id}")
                return cart_item
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart item by ID {cart_item_id}: {e}")
            return None

    def get_cart_items_by_user(self, user_id):
        """Retrieves all cart items for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ci.*, p.name, p.price
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.user_id = ?
                ''', (user_id,))
                cart_items = cursor.fetchall()
                logging.info(f"Retrieved {len(cart_items)} cart items for user {user_id}")
                return cart_items
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart items for user {user_id}: {e}")
            return []

    def update_cart_item(self, cart_item_id, quantity=None):
        """Updates cart item details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if quantity is not None:
                    updates.append('quantity = ?')
                    params.append(quantity)
                
                if not updates:
                    logging.info(f"No updates provided for cart item ID: {cart_item_id}")
                    return True

                params.append(cart_item_id)
                query = f'UPDATE cart_items SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated cart item with ID: {cart_item_id}")
                    return True
                else:
                    logging.warning(f"No cart item found with ID: {cart_item_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating cart item {cart_item_id}: {e}")
            return False

    def delete_cart_item(self, cart_item_id):
        """Deletes a cart item by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart_items WHERE id = ?', (cart_item_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted cart item with ID: {cart_item_id}")
                    return True
                else:
                    logging.warning(f"No cart item found with ID: {cart_item_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting cart item {cart_item_id}: {e}")
            return False

    def get_cart_items(self, page=1, per_page=20):
        """Retrieves cart items with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM cart_items')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT ci.*, p.name, p.price
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    ORDER BY ci.added_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                cart_items = cursor.fetchall()
                logging.info(f"Retrieved {len(cart_items)} cart items. Total: {total}")
                return cart_items, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart items: {e}")
            return [], 0