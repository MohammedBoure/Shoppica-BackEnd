from .base import Database
import sqlite3
import logging

class OrderManager(Database):
    """Manages operations for the orders table in the database."""

    def add_order(self, user_id, shipping_address_id, total_price, status='pending'):
        """Adds a new order for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO orders (user_id, status, total_price, shipping_address_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, status, total_price, shipping_address_id, self.get_current_timestamp()))
                conn.commit()
                order_id = cursor.lastrowid
                logging.info(f"Order added for user {user_id} with ID: {order_id}")
                return order_id
        except sqlite3.Error as e:
            logging.error(f"Error adding order for user {user_id}: {e}")
            return None

    def get_order_by_id(self, order_id):
        """Retrieves an order by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
                order = cursor.fetchone()
                logging.info(f"Retrieved order with ID: {order_id}")
                return order
        except sqlite3.Error as e:
            logging.error(f"Error retrieving order by ID {order_id}: {e}")
            return None

    def get_orders_by_user(self, user_id):
        """Retrieves all orders for a user."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,))
                orders = cursor.fetchall()
                logging.info(f"Retrieved {len(orders)} orders for user {user_id}")
                return orders
        except sqlite3.Error as e:
            logging.error(f"Error retrieving orders for user {user_id}: {e}")
            return []

    def update_order(self, order_id, status=None, total_price=None, shipping_address_id=None):
        """Updates order details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if status is not None:
                    updates.append('status = ?')
                    params.append(status)
                if total_price is not None:
                    updates.append('total_price = ?')
                    params.append(total_price)
                if shipping_address_id is not None:
                    updates.append('shipping_address_id = ?')
                    params.append(shipping_address_id)
                
                if not updates:
                    logging.info(f"No updates provided for order ID: {order_id}")
                    return True

                params.append(order_id)
                query = f'UPDATE orders SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated order with ID: {order_id}")
                    return True
                else:
                    logging.warning(f"No order found with ID: {order_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating order {order_id}: {e}")
            return False

    def delete_order(self, order_id):
        """Deletes an order by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted order with ID: {order_id}")
                    return True
                else:
                    logging.warning(f"No order found with ID: {order_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting order {order_id}: {e}")
            return False

    def get_orders(self, page=1, per_page=20):
        """Retrieves orders with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM orders')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM orders
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                orders = cursor.fetchall()
                logging.info(f"Retrieved {len(orders)} orders. Total: {total}")
                return orders, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving orders: {e}")
            return [], 0