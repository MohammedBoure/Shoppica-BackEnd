from .base import Database
import sqlite3
import logging

class PaymentManager(Database):
    """Manages operations for the payments table in the database."""

    def add_payment(self, order_id, payment_method, transaction_id=None, payment_status='unpaid'):
        """Adds a new payment for an order."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                paid_at = self.get_current_timestamp() if payment_status == 'paid' else None
                cursor.execute('''
                    INSERT INTO payments (order_id, payment_method, payment_status, transaction_id, paid_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, payment_method, payment_status, transaction_id, paid_at))
                conn.commit()
                payment_id = cursor.lastrowid
                logging.info(f"Payment added for order {order_id} with ID: {payment_id}")
                return payment_id
        except sqlite3.Error as e:
            logging.error(f"Error adding payment for order {order_id}: {e}")
            return None

    def get_payment_by_id(self, payment_id):
        """Retrieves a payment by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
                payment = cursor.fetchone()
                logging.info(f"Retrieved payment with ID: {payment_id}")
                return payment
        except sqlite3.Error as e:
            logging.error(f"Error retrieving payment by ID {payment_id}: {e}")
            return None

    def get_payments_by_order(self, order_id):
        """Retrieves all payments for an order."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM payments WHERE order_id = ?', (order_id,))
                payments = cursor.fetchall()
                logging.info(f"Retrieved {len(payments)} payments for order {order_id}")
                return payments
        except sqlite3.Error as e:
            logging.error(f"Error retrieving payments for order {order_id}: {e}")
            return []

    def update_payment(self, payment_id, payment_method=None, payment_status=None, transaction_id=None):
        """Updates payment details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if payment_method is not None:
                    updates.append('payment_method = ?')
                    params.append(payment_method)
                if payment_status is not None:
                    updates.append('payment_status = ?')
                    params.append(payment_status)
                    if payment_status == 'paid':
                        updates.append('paid_at = ?')
                        params.append(self.get_current_timestamp())
                    else:
                        updates.append('paid_at = ?')
                        params.append(None)
                if transaction_id is not None:
                    updates.append('transaction_id = ?')
                    params.append(transaction_id)
                
                if not updates:
                    logging.info(f"No updates provided for payment ID: {payment_id}")
                    return True

                params.append(payment_id)
                query = f'UPDATE payments SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated payment with ID: {payment_id}")
                    return True
                else:
                    logging.warning(f"No payment found with ID: {payment_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating payment {payment_id}: {e}")
            return False

    def delete_payment(self, payment_id):
        """Deletes a payment by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted payment with ID: {payment_id}")
                    return True
                else:
                    logging.warning(f"No payment found with ID: {payment_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting payment {payment_id}: {e}")
            return False

    def get_payments(self, page=1, per_page=20):
        """Retrieves payments with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM payments')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM payments
                    ORDER BY paid_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                payments = cursor.fetchall()
                logging.info(f"Retrieved {len(payments)} payments. Total: {total}")
                return payments, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving payments: {e}")
            return [], 0