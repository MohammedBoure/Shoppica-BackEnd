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
                top_products = (
                    session.query(
                        Product.id,
                        Product.name,
                        func.sum(OrderItem.quantity).label('total_quantity')
                    )
                    .join(OrderItem, Product.id == OrderItem.product_id)
                    .join(Order, OrderItem.order_id == Order.id)
                    .filter(Order.status == 'completed')
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
        """
        Retrieves sales statistics including total revenue, orders, and items sold by category.
        
        Args:
            start_date (datetime, optional): Start of the date range
            end_date (datetime, optional): End of the date range
        
        Returns:
            dict: Sales statistics including total and category-wise breakdown
        """
        try:
            with next(self.db.get_db_session()) as session:
                CategoryAlias = aliased(Category)

                total_sales_query = session.query(
                    func.sum(Order.total_price).label('total_revenue'),
                    func.count(distinct(Order.id)).label('total_orders'),
                    func.sum(OrderItem.quantity).label('total_items_sold')
                ).join(OrderItem, Order.id == OrderItem.order_id
                ).filter(Order.status == 'completed')

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
        """
        try:
            with next(self.db.get_db_session()) as session:
                end_date = end_date or datetime.utcnow()
                start_date = start_date or (end_date - timedelta(days=30))

                new_users_query = session.query(
                    func.date(User.created_at).label('date'),
                    func.count(User.id).label('count')
                ).filter(User.created_at >= start_date, User.created_at <= end_date
                ).group_by(func.date(User.created_at))

                active_users_query = session.query(
                    func.date(Order.created_at).label('date'),
                    func.count(distinct(Order.user_id)).label('count')
                ).filter(Order.created_at >= start_date, Order.created_at <= end_date
                ).group_by(func.date(Order.created_at))

                new_users = new_users_query.all()
                active_users = active_users_query.all()

                total_new_users = sum(row.count for row in new_users)
                total_active_users = sum(row.count for row in active_users)

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

    def get_customer_retention_rate(self, start_date=None, end_date=None):
        """
        Calculates the customer retention rate based on repeat purchases.
        
        Args:
            start_date (datetime, optional): Start of the date range
            end_date (datetime, optional): End of the date range
        
        Returns:
            dict: Dictionary containing retention statistics
                  {
                      'total_customers': int,
                      'repeat_customers': int,
                      'retention_rate': float
                  }
        
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with next(self.db.get_db_session()) as session:
                end_date = end_date or datetime.utcnow()
                start_date = start_date or (end_date - timedelta(days=30))

                # Query total unique customers who placed orders
                total_customers_query = session.query(
                    func.count(distinct(Order.user_id)).label('total_customers')
                ).filter(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    Order.status == 'completed'
                )

                # Query customers with more than one order
                repeat_customers_query = session.query(
                    Order.user_id,
                    func.count(Order.id).label('order_count')
                ).filter(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    Order.status == 'completed'
                ).group_by(Order.user_id
                ).having(func.count(Order.id) > 1)

                total_customers = total_customers_query.first().total_customers
                repeat_customers = repeat_customers_query.count()

                retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0.0

                result = {
                    'total_customers': int(total_customers),
                    'repeat_customers': int(repeat_customers),
                    'retention_rate': round(float(retention_rate), 2)
                }

                logging.info(f"Retrieved customer retention rate: {retention_rate}%")
                return result

        except SQLAlchemyError as e:
            logging.error(f"Error retrieving customer retention rate: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in get_customer_retention_rate: {str(e)}")
            raise

    def get_product_performance_trend(self, product_id, start_date=None, end_date=None, interval='daily'):
        """
        Analyzes sales trend for a specific product over time.
        
        Args:
            product_id (int): ID of the product to analyze
            start_date (datetime, optional): Start of the date range
            end_date (datetime, optional): End of the date range
            interval (str): Time interval for aggregation ('daily' or 'monthly')
        
        Returns:
            dict: Product performance trend
                  {
                      'product_id': int,
                      'product_name': str,
                      'trend': [{'period': str, 'quantity_sold': int, 'revenue': float}, ...]
                  }
        
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with next(self.db.get_db_session()) as session:
                end_date = end_date or datetime.utcnow()
                start_date = start_date or (end_date - timedelta(days=30))

                # Choose aggregation function based on interval
                if interval == 'monthly':
                    period_func = func.strftime('%Y-%m', Order.created_at)
                else:  # default to daily
                    period_func = func.date(Order.created_at)

                trend_query = (
                    session.query(
                        period_func.label('period'),
                        func.sum(OrderItem.quantity).label('quantity_sold'),
                        func.sum(OrderItem.price * OrderItem.quantity).label('revenue')
                    )
                    .join(Order, OrderItem.order_id == Order.id)
                    .join(Product, OrderItem.product_id == Product.id)
                    .filter(
                        OrderItem.product_id == product_id,
                        Order.created_at >= start_date,
                        Order.created_at <= end_date,
                        Order.status == 'completed'
                    )
                    .group_by(period_func)
                    .order_by(period_func)
                )

                product = session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    raise ValueError(f"Product with ID {product_id} not found")

                trend_data = trend_query.all()

                result = {
                    'product_id': product_id,
                    'product_name': product.name,
                    'trend': [
                        {
                            'period': row.period,
                            'quantity_sold': int(row.quantity_sold or 0),
                            'revenue': float(row.revenue or 0)
                        } for row in trend_data
                    ]
                }

                logging.info(f"Retrieved performance trend for product ID {product_id}")
                return result

        except SQLAlchemyError as e:
            logging.error(f"Error retrieving product performance trend: {e}")
            raise
        except ValueError as e:
            logging.error(str(e))
            raise

    def get_discount_effectiveness(self, start_date=None, end_date=None):
        """
        Evaluates the effectiveness of discounts on sales and revenue.
        
        Args:
            start_date (datetime, optional): Start of the date range
            end_date (datetime, optional): End of the date range
        
        Returns:
            dict: Dictionary containing discount effectiveness metrics
                  {
                      'total_discounts_applied': int,
                      'discounts': [
                          {
                              'discount_id': int,
                              'discount_code': str,
                              'times_used': int,
                              'total_revenue_impact': float,
                              'average_discount_amount': float
                          }, ...
                      ]
                  }
        
        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            with next(self.db.get_db_session()) as session:
                end_date = end_date or datetime.utcnow()
                start_date = start_date or (end_date - timedelta(days=30))

                discount_query = (
                    session.query(
                        Discount.id.label('discount_id'),
                        Discount.code.label('discount_code'),
                        func.count(DiscountUsage.id).label('times_used'),
                        func.sum(Order.total_price).label('total_revenue_impact'),
                        func.avg(Discount.discount_percent).label('average_discount_amount')
                    )
                    .join(DiscountUsage, Discount.id == DiscountUsage.discount_id)
                    .join(Order, DiscountUsage.user_id == Order.user_id)
                    .filter(
                        DiscountUsage.used_at >= start_date,
                        DiscountUsage.used_at <= end_date,
                        Order.created_at >= start_date,
                        Order.created_at <= end_date,
                        Order.status == 'completed'
                    )
                    .group_by(Discount.id, Discount.code)
                )

                discount_data = discount_query.all()
                total_discounts_applied = sum(row.times_used for row in discount_data)

                result = {
                    'total_discounts_applied': int(total_discounts_applied),
                    'discounts': [
                        {
                            'discount_id': row.discount_id,
                            'discount_code': row.discount_code,
                            'times_used': int(row.times_used or 0),
                            'total_revenue_impact': float(row.total_revenue_impact or 0),
                            'average_discount_amount': float(row.average_discount_amount or 0)
                        } for row in discount_data
                    ]
                }

                logging.info("Retrieved discount effectiveness metrics successfully")
                return result

        except SQLAlchemyError as e:
            logging.error(f"Error retrieving discount effectiveness: {e}")
            raise