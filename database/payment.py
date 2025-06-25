import logging
from sqlalchemy.exc import SQLAlchemyError
from .base import Database, Payment

class PaymentManager(Database):
    """Manages operations for the payments table in the database using SQLAlchemy."""

    def add_payment(self, order_id, payment_method, transaction_id=None, payment_status='unpaid'):
        """Adds a new payment for an order."""
        try:
            with next(self.get_db_session()) as session:
                paid_at = self.get_current_timestamp() if payment_status == 'paid' else None
                new_payment = Payment(
                    order_id=order_id,
                    payment_method=payment_method,
                    payment_status=payment_status,
                    transaction_id=transaction_id,
                    paid_at=paid_at
                )
                session.add(new_payment)
                session.commit()
                logging.info(f"Payment added for order {order_id} with ID: {new_payment.id}")
                return new_payment.id
        except SQLAlchemyError as e:
            logging.error(f"Error adding payment for order {order_id}: {e}")
            session.rollback()
            return None

    def get_payment_by_id(self, payment_id):
        """Retrieves a payment by its ID."""
        try:
            with next(self.get_db_session()) as session:
                payment = session.query(Payment).filter_by(id=payment_id).first()
                if payment:
                    logging.info(f"Retrieved payment with ID: {payment_id}")
                    return payment
                else:
                    logging.warning(f"No payment found with ID: {payment_id}")
                    return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving payment by ID {payment_id}: {e}")
            return None

    def get_payments_by_order(self, order_id):
        """Retrieves all payments for an order."""
        try:
            with next(self.get_db_session()) as session:
                payments = session.query(Payment).filter_by(order_id=order_id).all()
                logging.info(f"Retrieved {len(payments)} payments for order {order_id}")
                return payments
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving payments for order {order_id}: {e}")
            return []

    def update_payment(self, payment_id, payment_method=None, payment_status=None, transaction_id=None):
        """Updates payment details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                payment = session.query(Payment).filter_by(id=payment_id).first()
                if not payment:
                    logging.warning(f"No payment found with ID: {payment_id}")
                    return False

                if payment_method is not None:
                    payment.payment_method = payment_method
                if payment_status is not None:
                    payment.payment_status = payment_status
                    payment.paid_at = self.get_current_timestamp() if payment_status == 'paid' else None
                if transaction_id is not None:
                    payment.transaction_id = transaction_id

                session.commit()
                logging.info(f"Updated payment with ID: {payment_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating payment {payment_id}: {e}")
            session.rollback()
            return False

    def delete_payment(self, payment_id):
        """Deletes a payment by its ID."""
        try:
            with next(self.get_db_session()) as session:
                payment = session.query(Payment).filter_by(id=payment_id).first()
                if not payment:
                    logging.warning(f"No payment found with ID: {payment_id}")
                    return False

                session.delete(payment)
                session.commit()
                logging.info(f"Deleted payment with ID: {payment_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting payment {payment_id}: {e}")
            session.rollback()
            return False

    def get_payments(self, page=1, per_page=20):
        """Retrieves payments with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(Payment).count()
                payments = (session.query(Payment)
                           .order_by(Payment.paid_at.desc())
                           .limit(per_page)
                           .offset((page - 1) * per_page)
                           .all())
                logging.info(f"Retrieved {len(payments)} payments. Total: {total}")
                return payments, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving payments: {e}")
            return [], 0