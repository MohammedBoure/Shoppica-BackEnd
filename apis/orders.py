from flask import Blueprint, request, jsonify, session
from datetime import datetime
from database import OrderManager
from .auth import session_required, admin_required
import logging

orders_bp = Blueprint('orders', __name__)

# Initialize OrderManager
order_manager = OrderManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@orders_bp.route('/orders', methods=['POST'])
@session_required
def add_order():
    """API to add a new order."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    user_id = data.get('user_id')
    shipping_address_id = data.get('shipping_address_id')
    total_price = data.get('total_price')
    status = data.get('status', 'pending')

    # Validate inputs
    if not all([user_id, shipping_address_id, total_price is not None]):
        return jsonify({'error': 'user_id, shipping_address_id, and total_price are required'}), 400
    if not isinstance(user_id, int) or not isinstance(shipping_address_id, int):
        return jsonify({'error': 'user_id and shipping_address_id must be integers'}), 400
    if not isinstance(total_price, (int, float)) or total_price < 0:
        return jsonify({'error': 'total_price must be a non-negative number'}), 400
    if status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': 'Invalid status value'}), 400

    # Allow adding order only for the current user or if admin
    if user_id != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to add order for another user'}), 403

    order_id = order_manager.add_order(user_id, shipping_address_id, total_price, status)
    if order_id:
        return jsonify({'message': 'Order added successfully', 'order_id': order_id}), 201
    return jsonify({'error': 'Failed to add order'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@session_required
def get_order_by_id(order_id):
    """API to retrieve an order by ID."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    order = order_manager.get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Allow access if order belongs to the user or if admin
    if order['user_id'] != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized access to this order'}), 403

    return jsonify(order), 200

@orders_bp.route('/orders/user/<int:user_id>', methods=['GET'])
@session_required
def get_orders_by_user(user_id):
    """API to retrieve all orders for a user."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    # Allow access if requesting own orders or if admin
    if user_id != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to view orders for another user'}), 403

    orders = order_manager.get_orders_by_user(user_id)
    return jsonify({
        'orders': orders,
        'message': 'No orders found for this user' if not orders else ''
    }), 200

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
@admin_required
def update_order(order_id):
    """API to update order details."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON payload'}), 400

    status = data.get('status')
    total_price = data.get('total_price')
    shipping_address_id = data.get('shipping_address_id')

    # Validate inputs
    if status and status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': 'Invalid status value'}), 400
    if total_price is not None and (not isinstance(total_price, (int, float)) or total_price < 0):
        return jsonify({'error': 'total_price must be a non-negative number'}), 400
    if shipping_address_id is not None and not isinstance(shipping_address_id, int):
        return jsonify({'error': 'shipping_address_id must be an integer'}), 400
    if not any([status, total_price is not None, shipping_address_id is not None]):
        return jsonify({'error': 'At least one field (status, total_price, shipping_address_id) must be provided'}), 400

    success = order_manager.update_order(order_id, status, total_price, shipping_address_id)
    if success:
        return jsonify({'message': 'Order updated successfully'}), 200
    return jsonify({'error': 'Order not found or failed to update'}), 404

@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
@admin_required
def delete_order(order_id):
    """API to delete an order by ID."""
    success = order_manager.delete_order(order_id)
    if success:
        return jsonify({'message': 'Order deleted successfully'}), 200
    return jsonify({'error': 'Order not found or failed to delete'}), 404

@orders_bp.route('/orders', methods=['GET'])
@admin_required
def get_orders():
    """API to retrieve paginated orders."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Validate pagination parameters
    if page < 1 or per_page < 1:
        return jsonify({'error': 'page and per_page must be positive integers'}), 400
    if per_page > 100:  # Limit to prevent excessive load
        return jsonify({'error': 'per_page cannot exceed 100'}), 400

    orders, total = order_manager.get_orders(page, per_page)
    return jsonify({
        'orders': orders,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@orders_bp.route('/orders/search', methods=['GET'])
@admin_required
def search_orders():
    """API to search orders with filters."""
    search_term = request.args.get('search_term')
    status = request.args.get('status')
    min_total = request.args.get('min_total', type=float)
    max_total = request.args.get('max_total', type=float)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate inputs
    if status and status not in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'error': 'Invalid status value'}), 400
    if min_total is not None and max_total is not None and min_total > max_total:
        return jsonify({'error': 'min_total cannot be greater than max_total'}), 400
    try:
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
    except (ValueError, TypeError):
        return jsonify({'error': 'start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    if start_date and end_date and start_date > end_date:
        return jsonify({'error': 'start_date cannot be later than end_date'}), 400

    orders = order_manager.search_orders(search_term, status, min_total, max_total, start_date, end_date)
    return jsonify({
        'orders': orders,
        'message': 'No orders found matching the criteria' if not orders else ''
    }), 200

@orders_bp.route('/orders/statistics', methods=['GET'])
@admin_required
def get_order_statistics():
    """API to retrieve order statistics."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Validate dates
    try:
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
    except (ValueError, TypeError):
        return jsonify({'error': 'start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    if start_date and end_date and start_date > end_date:
        return jsonify({'error': 'start_date cannot be later than end_date'}), 400

    stats = order_manager.get_order_statistics(start_date, end_date)
    return jsonify(stats), 200

@orders_bp.route('/orders/top-products', methods=['GET'])
@admin_required
def get_top_selling_products():
    """API to retrieve top-selling products."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 5, type=int)

    # Validate inputs
    try:
        start_date = datetime.fromisoformat(start_date) if start_date else None
        end_date = datetime.fromisoformat(end_date) if end_date else None
    except (ValueError, TypeError):
        return jsonify({'error': 'start_date and end_date must be in ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    if start_date and end_date and start_date > end_date:
        return jsonify({'error': 'start_date cannot be later than end_date'}), 400
    if limit < 1 or limit > 50:
        return jsonify({'error': 'limit must be between 1 and 50'}), 400

    products = order_manager.get_top_selling_products(start_date, end_date, limit)
    return jsonify({
        'top_products': products,
        'message': 'No products found for the given criteria' if not products else ''
    }), 200