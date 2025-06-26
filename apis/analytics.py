from flask import Blueprint, request, jsonify, g, session
from database import AnalyticsManager
from functools import wraps
import logging
from .auth import admin_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

# Initialize Manager
analytics_manager = AnalyticsManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@analytics_bp.route('/analytics/products', methods=['GET'])
@admin_required
def get_top_selling_products():
    """
    API endpoint to retrieve top-selling products.
    
    Query Parameters:
        limit (int, optional): Number of products to return (default: 5)
    
    Returns:
        JSON response with top-selling products data or error message
    """
    try:
        limit = request.args.get('limit', default=5, type=int)
        if limit < 1 or limit > 100:
            return jsonify({'error': 'Limit must be between 1 and 100'}), 400
            
        products = analytics_manager.get_top_selling_products(limit=limit)
        products_data = [
            {
                'product_id': product.id,
                'product_name': product.name,
                'total_quantity_sold': int(product.total_quantity)
            }
            for product in products
        ]
        
        return jsonify({
            'status': 'success',
            'data': products_data,
            'count': len(products_data)
        }), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_top_selling_products: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_top_selling_products: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@analytics_bp.route('/analytics/sales', methods=['GET'])
@admin_required
def get_sales_statistics():
    """
    API endpoint to retrieve sales statistics.
    
    Query Parameters:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
    
    Returns:
        JSON response with sales statistics data or error message
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert string dates to datetime objects if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be later than end_date'}), 400
            
        stats = analytics_manager.get_sales_statistics(start_date=start_date, end_date=end_date)
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_sales_statistics: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_sales_statistics: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@analytics_bp.route('/analytics/users', methods=['GET'])
@admin_required
def get_user_statistics():
    """
    API endpoint to retrieve user statistics.
    
    Query Parameters:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
    
    Returns:
        JSON response with user statistics data or error message
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert string dates to datetime objects if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be later than end_date'}), 400
            
        stats = analytics_manager.get_user_statistics(start_date=start_date, end_date=end_date)
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user_statistics: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_user_statistics: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@analytics_bp.route('/analytics/customer-retention', methods=['GET'])
@admin_required
def get_customer_retention_rate():
    """
    API endpoint to retrieve customer retention rate.
    
    Query Parameters:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
    
    Returns:
        JSON response with customer retention rate data or error message
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert string dates to datetime objects if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be later than end_date'}), 400
            
        retention_stats = analytics_manager.get_customer_retention_rate(start_date=start_date, end_date=end_date)
        
        return jsonify({
            'status': 'success',
            'data': retention_stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid date format in get_customer_retention_rate: {str(e)}")
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_customer_retention_rate: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_customer_retention_rate: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@analytics_bp.route('/analytics/product-performance', methods=['GET'])
@admin_required
def get_product_performance_trend():
    """
    API endpoint to retrieve product performance trend.
    
    Query Parameters:
        product_id (int, required): ID of the product to analyze
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        interval (str, optional): Time interval for aggregation ('daily' or 'monthly', default: 'daily')
    
    Returns:
        JSON response with product performance trend data or error message
    """
    try:
        product_id = request.args.get('product_id', type=int)
        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
            
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        interval = request.args.get('interval', default='daily')
        
        # Validate interval
        if interval not in ['daily', 'monthly']:
            return jsonify({'error': 'Interval must be either "daily" or "monthly"'}), 400
            
        # Convert string dates to datetime objects if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be later than end_date'}), 400
            
        trend_data = analytics_manager.get_product_performance_trend(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        return jsonify({
            'status': 'success',
            'data': trend_data
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid input in get_product_performance_trend: {str(e)}")
        return jsonify({'error': 'Invalid input. Ensure product_id is valid and dates are in YYYY-MM-DD format'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_product_performance_trend: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_product_performance_trend: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@analytics_bp.route('/analytics/discount-effectiveness', methods=['GET'])
@admin_required
def get_discount_effectiveness():
    """
    API endpoint to retrieve discount effectiveness metrics.
    
    Query Parameters:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
    
    Returns:
        JSON response with discount effectiveness data or error message
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert string dates to datetime objects if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'start_date cannot be later than end_date'}), 400
            
        discount_stats = analytics_manager.get_discount_effectiveness(start_date=start_date, end_date=end_date)
        
        return jsonify({
            'status': 'success',
            'data': discount_stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid date format in get_discount_effectiveness: {str(e)}")
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_discount_effectiveness: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_discount_effectiveness: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500