from .base import Database, OrderItem, Product
from sqlalchemy.exc import SQLAlchemyError
import logging

class OrderItemManager(Database):
    """Manages operations for the order_items table in the database using SQLAlchemy."""

    def add_order_item(self, order_id, product_id, quantity, price):
        """Adds a new item to an order."""
        try:
            with next(self.get_db_session()) as session:
                order_item = OrderItem(
                    order_id=order_id,
                    product_id=product_id,
                    quantity=quantity,
                    price=price
                )
                session.add(order_item)
                session.commit()
                session.refresh(order_item)  # Refresh to get the generated ID
                logging.info(f"Order item added for order {order_id}, product {product_id} with ID: {order_item.id}")
                return order_item.id
        except SQLAlchemyError as e:
            logging.error(f"Error adding order item for order {order_id}, product {product_id}: {e}")
            session.rollback()
            return None

    def get_order_item_by_id(self, order_item_id):
        """Retrieves an order item by its ID."""
        try:
            with next(self.get_db_session()) as session:
                order_item = session.query(OrderItem).filter_by(id=order_item_id).first()
                if order_item:
                    logging.info(f"Retrieved order item with ID: {order_item_id}")
                    return order_item
                else:
                    logging.warning(f"No order item found with ID: {order_item_id}")
                    return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving order item by ID {order_item_id}: {e}")
            return None

    def get_order_items_by_order(self, order_id):
        """Retrieves all items for an order."""
        try:
            with next(self.get_db_session()) as session:
                order_items = (
                    session.query(OrderItem, Product.name)
                    .join(Product, OrderItem.product_id == Product.id)
                    .filter(OrderItem.order_id == order_id)
                    .all()
                )
                logging.info(f"Retrieved {len(order_items)} order items for order {order_id}")
                return order_items
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving order items for order {order_id}: {e}")
            return []

    def update_order_item(self, order_item_id, quantity=None, price=None):
        """Updates order item details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                order_item = session.query(OrderItem).filter_by(id=order_item_id).first()
                if not order_item:
                    logging.warning(f"No order item found with ID: {order_item_id}")
                    return False

                updates = False
                if quantity is not None:
                    order_item.quantity = quantity
                    updates = True
                if price is not None:
                    order_item.price = price
                    updates = True

                if not updates:
                    logging.info(f"No updates provided for order item ID: {order_item_id}")
                    return True

                session.commit()
                logging.info(f"Updated order item with ID: {order_item_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating order item {order_item_id}: {e}")
            session.rollback()
            return False

    def delete_order_item(self, order_item_id):
        """Deletes an order item by its ID."""
        try:
            with next(self.get_db_session()) as session:
                order_item = session.query(OrderItem).filter_by(id=order_item_id).first()
                if not order_item:
                    logging.warning(f"No order item found with ID: {order_item_id}")
                    return False

                session.delete(order_item)
                session.commit()
                logging.info(f"Deleted order item with ID: {order_item_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting order item {order_item_id}: {e}")
            session.rollback()
            return False

    def get_order_items(self, page=1, per_page=20):
        """Retrieves order items with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(OrderItem).count()
                order_items = (
                    session.query(OrderItem, Product.name)
                    .join(Product, OrderItem.product_id == Product.id)
                    .order_by(OrderItem.id)
                    .limit(per_page)
                    .offset((page - 1) * per_page)
                    .all()
                )
                logging.info(f"Retrieved {len(order_items)} order items. Total: {total}")
                return order_items, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving order items: {e}")
            return [], 0