from .base import Database
import sqlite3
import logging

class CartItemManager(Database):
    """Manages operations for the cart_items table in the database."""

    def add_cart_item(self, user_id, product_id, quantity):
        """Adds a product to a user's cart after checking stock availability."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                # Check product stock
                cursor.execute('SELECT stock_quantity FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()
                if not product or product['stock_quantity'] < quantity:
                    logging.warning(f"Insufficient stock for product {product_id} or product not found")
                    return None

                # Check if item already exists in cart
                cursor.execute('SELECT id, quantity FROM cart_items WHERE user_id = ? AND product_id = ?', (user_id, product_id))
                existing_item = cursor.fetchone()
                if existing_item:
                    new_quantity = existing_item['quantity'] + quantity
                    if product['stock_quantity'] < new_quantity:
                        logging.warning(f"Insufficient stock for product {product_id} to update quantity to {new_quantity}")
                        return None
                    return self.update_cart_item(existing_item['id'], new_quantity)

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
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ci.*, p.name, p.price
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.id = ?
                ''', (cart_item_id,))
                cart_item = cursor.fetchone()
                if cart_item:
                    cart_item_dict = dict(cart_item)
                    logging.info(f"Retrieved cart item with ID: {cart_item_id}")
                    return cart_item_dict
                logging.warning(f"No cart item found with ID: {cart_item_id}")
                return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart item by ID {cart_item_id}: {e}")
            return None

    def get_cart_items_by_user(self, user_id):
        """Retrieves all cart items for a user."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ci.*, p.name, p.price
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.user_id = ?
                ''', (user_id,))
                cart_items = [dict(item) for item in cursor.fetchall()]
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
                if quantity is not None:
                    # Check product stock
                    cursor.execute('''
                        SELECT p.stock_quantity
                        FROM cart_items ci
                        JOIN products p ON ci.product_id = p.id
                        WHERE ci.id = ?
                    ''', (cart_item_id,))
                    product = cursor.fetchone()
                    if not product or product['stock_quantity'] < quantity:
                        logging.warning(f"Insufficient stock for cart item {cart_item_id} to update quantity to {quantity}")
                        return False

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
                conn.row_factory = sqlite3.Row
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
                cart_items = [dict(item) for item in cursor.fetchall()]
                logging.info(f"Retrieved {len(cart_items)} cart items. Total: {total}")
                return cart_items, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart items: {e}")
            return [], 0

    def search_cart_items(self, user_id=None, product_id=None, page=1, per_page=20):
        """Searches cart items based on user_id or product_id with pagination."""
        try:
            with self.get_db_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                conditions = []
                params = []

                if user_id is not None:
                    conditions.append('ci.user_id = ?')
                    params.append(user_id)
                if product_id is not None:
                    conditions.append('ci.product_id = ?')
                    params.append(product_id)

                where_clause = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
                
                # Count total cart items matching the criteria
                count_query = f'''
                    SELECT COUNT(*) as total
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    {where_clause}
                '''
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']

                # Fetch cart items with pagination
                query = f'''
                    SELECT ci.*, p.name, p.price
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    {where_clause}
                    ORDER BY ci.added_at DESC
                    LIMIT ? OFFSET ?
                '''
                params.extend([per_page, (page - 1) * per_page])
                cursor.execute(query, params)
                cart_items = [dict(item) for item in cursor.fetchall()]
                logging.info(f"Found {len(cart_items)} cart items matching search criteria. Total: {total}")
                return cart_items, total
        except sqlite3.Error as e:
            logging.error(f"Error searching cart items: {e}")
            return [], 0

    def delete_cart_items_by_user(self, user_id):
        """Deletes all cart items for a specific user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} cart items for user {user_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting cart items for user {user_id}: {e}")
            return 0

    def delete_cart_items_by_product(self, product_id):
        """Deletes all cart items for a specific product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart_items WHERE product_id = ?', (product_id,))
                conn.commit()
                deleted_count = cursor.rowcount
                logging.info(f"Deleted {deleted_count} cart items for product {product_id}")
                return deleted_count
        except sqlite3.Error as e:
            logging.error(f"Error deleting cart items for product {product_id}: {e}")
            return 0

    def get_cart_stats(self):
        """Returns statistics about cart items."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_cart_items FROM cart_items')
                total_cart_items = cursor.fetchone()['total_cart_items']
                cursor.execute('SELECT COUNT(DISTINCT user_id) as users_with_cart_items FROM cart_items')
                users_with_cart_items = cursor.fetchone()['users_with_cart_items']
                cursor.execute('''
                    SELECT SUM(ci.quantity * p.price) as total_cart_value
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                ''')
                total_cart_value = cursor.fetchone()['total_cart_value'] or 0.0
                stats = {
                    'total_cart_items': total_cart_items,
                    'users_with_cart_items': users_with_cart_items,
                    'total_cart_value': round(total_cart_value, 2)
                }
                logging.info(f"Retrieved cart stats: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart stats: {e}")
            return {'total_cart_items': 0, 'users_with_cart_items': 0, 'total_cart_value': 0.0}

    def get_user_cart_stats(self, user_id):
        """Returns cart statistics for a specific user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total_items FROM cart_items WHERE user_id = ?', (user_id,))
                total_items = cursor.fetchone()['total_items']
                cursor.execute('''
                    SELECT SUM(ci.quantity * p.price) as cart_value
                    FROM cart_items ci
                    JOIN products p ON ci.product_id = p.id
                    WHERE ci.user_id = ?
                ''', (user_id,))
                cart_value = cursor.fetchone()['cart_value'] or 0.0
                stats = {
                    'total_items': total_items,
                    'cart_value': round(cart_value, 2)
                }
                logging.info(f"Retrieved cart stats for user {user_id}: {stats}")
                return stats
        except sqlite3.Error as e:
            logging.error(f"Error retrieving cart stats for user {user_id}: {e}")
            return {'total_items': 0, 'cart_value': 0.0}