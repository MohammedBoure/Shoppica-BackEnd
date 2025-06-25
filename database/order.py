import logging
from datetime import datetime
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from .base import Database, Order, OrderItem, Product, User

class OrderManager(Database):
    """Manages operations for the orders table in the database using SQLAlchemy."""

    def add_order(self, user_id, shipping_address_id, total_price, status='pending'):
        """Adds a new order for a user."""
        try:
            with next(self.get_db_session()) as session:
                new_order = Order(
                    user_id=user_id,
                    shipping_address_id=shipping_address_id,
                    total_price=total_price,
                    status=status,
                    created_at=self.get_current_timestamp()
                )
                session.add(new_order)
                session.commit()
                order_id = new_order.id
                logging.info(f"Order added for user {user_id} with ID: {order_id}")
                return order_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding order for user {user_id}: {e}")
            session.rollback()
            return None

    def get_order_by_id(self, order_id):
        """Retrieves an order by its ID."""
        try:
            with next(self.get_db_session()) as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if order:
                    order_dict = {
                        'id': order.id,
                        'user_id': order.user_id,
                        'status': order.status,
                        'total_price': order.total_price,
                        'shipping_address_id': order.shipping_address_id,
                        'created_at': order.created_at.isoformat() if order.created_at else None
                    }
                    logging.info(f"Retrieved order with ID: {order_id}")
                    return order_dict
                logging.warning(f"No order found with ID: {order_id}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving order by ID {order_id}: {e}")
            return None

    def get_orders_by_user(self, user_id):
        """Retrieves all orders for a user."""
        try:
            with next(self.get_db_session()) as session:
                orders = session.query(Order).filter(Order.user_id == user_id).all()
                orders_list = [
                    {
                        'id': order.id,
                        'user_id': order.user_id,
                        'status': order.status,
                        'total_price': order.total_price,
                        'shipping_address_id': order.shipping_address_id,
                        'created_at': order.created_at.isoformat() if order.created_at else None
                    } for order in orders
                ]
                logging.info(f"Retrieved {len(orders_list)} orders for user {user_id}")
                return orders_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving orders for user {user_id}: {e}")
            return []

    def update_order(self, order_id, status=None, total_price=None, shipping_address_id=None):
        """Updates order details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if not order:
                    logging.warning(f"No order found with ID: {order_id}")
                    return False

                if status is not None:
                    order.status = status
                if total_price is not None:
                    order.total_price = total_price
                if shipping_address_id is not None:
                    order.shipping_address_id = shipping_address_id

                session.commit()
                logging.info(f"Updated order with ID: {order_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating order {order_id}: {e}")
            session.rollback()
            return False

    def delete_order(self, order_id):
        """Deletes an order by its ID."""
        try:
            with next(self.get_db_session()) as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if not order:
                    logging.warning(f"No order found with ID: {order_id}")
                    return False
                session.delete(order)
                session.commit()
                logging.info(f"Deleted order with ID: {order_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting order {order_id}: {e}")
            session.rollback()
            return False

    def get_orders(self, page=1, per_page=20):
        """Retrieves orders with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(func.count(Order.id)).scalar()
                orders = session.query(Order).order_by(Order.created_at.desc())\
                    .limit(per_page).offset((page - 1) * per_page).all()
                orders_list = [
                    {
                        'id': order.id,
                        'user_id': order.user_id,
                        'status': order.status,
                        'total_price': order.total_price,
                        'shipping_address_id': order.shipping_address_id,
                        'created_at': order.created_at.isoformat() if order.created_at else None
                    } for order in orders
                ]
                logging.info(f"Retrieved {len(orders_list)} orders. Total: {total}")
                return orders_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving orders: {e}")
            return [], 0

    def search_orders(self, search_term=None, status=None, min_total=None, max_total=None, start_date=None, end_date=None):
        """Smart search for orders with multiple optional filters."""
        try:
            with next(self.get_db_session()) as session:
                query = session.query(Order).join(User, Order.user_id == User.id)
                
                if search_term:
                    query = query.filter(
                        or_(
                            User.username.ilike(f'%{search_term}%'),
                            User.email.ilike(f'%{search_term}%'),
                            Order.id == search_term
                        )
                    )
                if status:
                    query = query.filter(Order.status == status)
                if min_total is not None:
                    query = query.filter(Order.total_price >= min_total)
                if max_total is not None:
                    query = query.filter(Order.total_price <= max_total)
                if start_date:
                    query = query.filter(Order.created_at >= start_date)
                if end_date:
                    query = query.filter(Order.created_at <= end_date)

                orders = query.order_by(Order.created_at.desc()).all()
                orders_list = [
                    {
                        'id': order.id,
                        'user_id': order.user_id,
                        'status': order.status,
                        'total_price': order.total_price,
                        'shipping_address_id': order.shipping_address_id,
                        'created_at': order.created_at.isoformat() if order.created_at else None
                    } for order in orders
                ]
                logging.info(f"Retrieved {len(orders_list)} orders matching search criteria")
                return orders_list
        except SQLAlchemyError as e:
            logging.error(f"Error searching orders: {e}")
            return []

    def get_order_statistics(self, start_date=None, end_date=None):
        """Retrieve statistical data about orders."""
        try:
            with next(self.get_db_session()) as session:
                query = session.query(Order)
                if start_date:
                    query = query.filter(Order.created_at >= start_date)
                if end_date:
                    query = query.filter(Order.created_at <= end_date)

                total_orders = query.count()
                total_revenue = session.query(func.sum(Order.total_price)).filter(
                    Order.status.in_(['completed', 'shipped'])
                ).scalar() or 0.0
                avg_order_value = session.query(func.avg(Order.total_price)).filter(
                    Order.status.in_(['completed', 'shipped'])
                ).scalar() or 0.0
                status_counts = session.query(
                    Order.status, func.count(Order.id)
                ).group_by(Order.status).all()

                stats = {
                    'total_orders': total_orders,
                    'total_revenue': float(total_revenue),
                    'average_order_value': float(avg_order_value),
                    'status_distribution': {status: count for status, count in status_counts}
                }
                logging.info("Retrieved order statistics")
                return stats
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving order statistics: {e}")
            return {}

    def get_top_selling_products(self, start_date=None, end_date=None, limit=5):
        """Retrieve top-selling products based on order items."""
        try:
            with next(self.get_db_session()) as session:
                query = session.query(
                    Product.name,
                    func.sum(OrderItem.quantity).label('total_quantity')
                ).join(OrderItem, OrderItem.product_id == Product.id)\
                 .join(Order, OrderItem.order_id == Order.id)

                if start_date:
                    query = query.filter(Order.created_at >= start_date)
                if end_date:
                    query = query.filter(Order.created_at <= end_date)

                top_products = query.group_by(Product.name)\
                    .order_by(func.sum(OrderItem.quantity).desc())\
                    .limit(limit).all()

                products_list = [
                    {'product_name': name, 'total_quantity_sold': int(quantity)}
                    for name, quantity in top_products
                ]
                logging.info(f"Retrieved top {limit} selling products")
                return products_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving top selling products: {e}")
            return []