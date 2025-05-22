from .base import Database
import sqlite3
import logging

class OrderItemManager(Database):
    """Manages operations for the order_items table in the database."""

    def add_order_item(self, order_id, product_id, quantity, price):
        """Adds a new item to an order."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, product_id, quantity, price))
                conn.commit()
                order_item_id = cursor.lastrowid
                logging.info(f"Order item added for order {order_id}, product {product_id} with ID: {order_item_id}")
                return order_item_id
        except sqlite3.Error as e:
            logging.error(f"Error adding order item for order {order_id}, product {product_id}: {e}")
            return None

    def get_order_item_by_id(self, order_item_id):
        """Retrieves an order item by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM order_items WHERE id = ?', (order_item_id,))
                order_item = cursor.fetchone()
                logging.info(f"Retrieved order item with ID: {order_item_id}")
                return order_item
        except sqlite3.Error as e:
            logging.error(f"Error retrieving order item by ID {order_item_id}: {e}")
            return None

    def get_order_items_by_order(self, order_id):
        """Retrieves all items for an order."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT oi.*, p.name
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = ?
                ''', (order_id,))
                order_items = cursor.fetchall()
                logging.info(f"Retrieved {len(order_items)} order items for order {order_id}")
                return order_items
        except sqlite3.Error as e:
            logging.error(f"Error retrieving order items for order {order_id}: {e}")
            return []

    def update_order_item(self, order_item_id, quantity=None, price=None):
        """Updates order item details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if quantity is not None:
                    updates.append('quantity = ?')
                    params.append(quantity)
                if price is not None:
                    updates.append('price = ?')
                    params.append(price)
                
                if not updates:
                    logging.info(f"No updates provided for order item ID: {order_item_id}")
                    return True

                params.append(order_item_id)
                query = f'UPDATE order_items SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated order item with ID: {order_item_id}")
                    return True
                else:
                    logging.warning(f"No order item found with ID: {order_item_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating order item {order_item_id}: {e}")
            return False

    def delete_order_item(self, order_item_id):
        """Deletes an order item by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM order_items WHERE id = ?', (order_item_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted order item with ID: {order_item_id}")
                    return True
                else:
                    logging.warning(f"No order item found with ID: {order_item_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting order item {order_item_id}: {e}")
            return False

    def get_order_items(self, page=1, per_page=20):
        """Retrieves order items with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM order_items')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT oi.*, p.name
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    ORDER BY oi.id
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                order_items = cursor.fetchall()
                logging.info(f"Retrieved {len(order_items)} order items. Total: {total}")
                return order_items, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving order items: {e}")
            return [], 0