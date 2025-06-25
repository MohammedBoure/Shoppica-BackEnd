import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, distinct, or_
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased
from .base import (
    Database,
    User,
    Address,
    Order,
    Product,
    OrderItem,
    Discount,
    Payment,
    Category,
    ProductImage,
    Review,
    CartItem,
    DiscountUsage,
    ProductDiscount,
    CategoryDiscount,
)

class AnalyticsManager:
    """Manages Analytic operations using SQLAlchemy ORM."""

    def __init__(self):
        """Initialize with a database instance."""
        self.db = Database()

    def get_top_selling_products(self, limit=5):
        """
        Retrieves the top-selling products based on total quantity sold.
        
        Args:
            limit (int): Number of top-selling products to return (default: 5)
        
        Returns:
            list: List of tuples containing (product_id, product_name, total_quantity_sold)
        
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with next(self.db.get_db_session()) as session:
                # Query to sum quantities from order_items, grouped by product
                top_products = (
                    session.query(
                        Product.id,
                        Product.name,
                        func.sum(OrderItem.quantity).label('total_quantity')
                    )
                    .join(OrderItem, Product.id == OrderItem.product_id)
                    .join(Order, OrderItem.order_id == Order.id)
                    .filter(Order.status == 'completed')  # Only count completed orders
                    .group_by(Product.id, Product.name)
                    .order_by(func.sum(OrderItem.quantity).desc())
                    .limit(limit)
                    .all()
                )
                
                logging.info(f"Retrieved {len(top_products)} top-selling products")
                return top_products
                
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving top-selling products: {e}")
            raise

    def get_sales_statistics(self, start_date=None, end_date=None):
        try:
            with next(self.db.get_db_session()) as session:
                CategoryAlias = aliased(Category)

                # Query total sales
                total_sales_query = session.query(
                    func.sum(Order.total_price).label('total_revenue'),
                    func.count(distinct(Order.id)).label('total_orders'),
                    func.sum(OrderItem.quantity).label('total_items_sold')
                ).join(OrderItem, Order.id == OrderItem.order_id
                ).filter(Order.status == 'completed')

                # Query sales by category - all joins explicit and clear
                category_sales_query = session.query(
                    CategoryAlias.id.label('category_id'),
                    CategoryAlias.name.label('category_name'),
                    func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue'),
                    func.sum(OrderItem.quantity).label('total_items_sold')
                ).select_from(OrderItem
                ).join(Order, OrderItem.order_id == Order.id
                ).join(Product, OrderItem.product_id == Product.id
                ).join(CategoryAlias, Product.category_id == CategoryAlias.id
                ).filter(Order.status == 'completed'
                ).group_by(CategoryAlias.id, CategoryAlias.name)

                if start_date:
                    total_sales_query = total_sales_query.filter(Order.created_at >= start_date)
                    category_sales_query = category_sales_query.filter(Order.created_at >= start_date)
                if end_date:
                    total_sales_query = total_sales_query.filter(Order.created_at <= end_date)
                    category_sales_query = category_sales_query.filter(Order.created_at <= end_date)

                total_sales = total_sales_query.first()
                category_sales = category_sales_query.all()

                return {
                    'total_sales': {
                        'total_revenue': float(total_sales.total_revenue or 0),
                        'total_orders': int(total_sales.total_orders or 0),
                        'total_items_sold': int(total_sales.total_items_sold or 0)
                    },
                    'sales_by_category': [
                        {
                            'category_id': row.category_id,
                            'category_name': row.category_name,
                            'total_revenue': float(row.total_revenue or 0),
                            'total_items_sold': int(row.total_items_sold or 0)
                        } for row in category_sales
                    ]
                }

        except SQLAlchemyError as e:
            logging.error(f"Error retrieving sales statistics: {e}")
            raise
    def get_user_statistics(self, start_date=None, end_date=None):
        """
        Retrieves user statistics including new and active users within a date range.
        
        Args:
            start_date (datetime, optional): Start of the date range
            end_date (datetime, optional): End of the date range
        
        Returns:
            dict: Dictionary containing user statistics
                  {
                      'new_users': {
                          'total': int,
                          'by_day': [{'date': str, 'count': int}, ...]
                      },
                      'active_users': {
                          'total': int,
                          'by_day': [{'date': str, 'count': int}, ...]
                      }
                  }
        
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with next(self.db.get_db_session()) as session:
                # Ensure end_date is set to now if not provided
                end_date = end_date or datetime.utcnow()
                start_date = start_date or (end_date - timedelta(days=30))

                # Query for new users (based on created_at)
                new_users_query = session.query(
                    func.date(User.created_at).label('date'),
                    func.count(User.id).label('count')
                ).filter(User.created_at >= start_date, User.created_at <= end_date
                ).group_by(func.date(User.created_at))

                # Query for active users (based on orders placed)
                active_users_query = session.query(
                    func.date(Order.created_at).label('date'),
                    func.count(distinct(Order.user_id)).label('count')
                ).filter(Order.created_at >= start_date, Order.created_at <= end_date
                ).group_by(func.date(Order.created_at))

                # Execute queries
                new_users = new_users_query.all()
                active_users = active_users_query.all()

                # Calculate totals
                total_new_users = sum(row.count for row in new_users)
                total_active_users = sum(row.count for row in active_users)

                # Format results
                result = {
                    'new_users': {
                        'total': int(total_new_users),
                        'by_day': [
                            {'date': row.date, 'count': int(row.count)}
                            for row in new_users
                        ]
                    },
                    'active_users': {
                        'total': int(total_active_users),
                        'by_day': [
                            {'date': row.date, 'count': int(row.count)}
                            for row in active_users
                        ]
                    }
                }

                logging.info("Retrieved user statistics successfully")
                return result

        except SQLAlchemyError as e:
            logging.error(f"Error retrieving user statistics: {e}")
            raise