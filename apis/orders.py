from flask import Blueprint, request, jsonify, session
from database import OrderManager
from .auth import session_required, admin_required
import logging

orders_bp = Blueprint('orders', __name__)

# Initialize OrderManager
order_manager = OrderManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

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

    if not user_id or not shipping_address_id or total_price is None:
        return jsonify({'error': 'User ID, shipping address ID, and total price are required'}), 400

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

    return jsonify({
        'id': order['id'],
        'user_id': order['user_id'],
        'status': order['status'],
        'total_price': order['total_price'],
        'shipping_address_id': order['shipping_address_id'],
        'created_at': order.get('created_at', '')
    }), 200

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
    orders_list = [
        {
            'id': order['id'],
            'user_id': order['user_id'],
            'status': order['status'],
            'total_price': order['total_price'],
            'shipping_address_id': order['shipping_address_id'],
            'created_at': order.get('created_at', '')
        } for order in orders or []
    ]
    return jsonify({'orders': orders_list, 'message': 'No orders found for this user' if not orders_list else ''}), 200

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

    success = order_manager.update_order(order_id, status, total_price, shipping_address_id)
    if success:
        return jsonify({'message': 'Order updated successfully'}), 200
    return jsonify({'error': 'Failed to update order'}), 400

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
    """API to retrieve orders with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    orders, total = order_manager.get_orders(page, per_page)
    orders_list = [
        {
            'id': order['id'],
            'user_id': order['user_id'],
            'status': order['status'],
            'total_price': order['total_price'],
            'shipping_address_id': order['shipping_address_id'],
            'created_at': order.get('created_at', '')
        } for order in orders or []
    ]
    return jsonify({
        'orders': orders_list,
        'total': total or 0,
        'page': page,
        'per_page': per_page
    }), 200