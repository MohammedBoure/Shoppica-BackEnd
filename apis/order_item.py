from flask import Blueprint, request, jsonify, session
from database import OrderItemManager, OrderManager
from .auth import admin_required, session_required
import logging

order_items_bp = Blueprint('order_items', __name__)

# Initialize OrderItemManager and OrderManager
order_item_manager = OrderItemManager()
order_manager = OrderManager()

@order_items_bp.route('/order_items', methods=['POST'])
@admin_required
def add_order_item():
    """API to add a new order item."""
    data = request.get_json()
    order_id = data.get('order_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    price = data.get('price')

    if not order_id or not product_id or quantity is None or price is None:
        return jsonify({'error': 'Order ID, product ID, quantity, and price are required'}), 400

    order_item_id = order_item_manager.add_order_item(order_id, product_id, quantity, price)
    if order_item_id:
        return jsonify({'message': 'Order item added successfully', 'order_item_id': order_item_id}), 201
    return jsonify({'error': 'Failed to add order item'}), 500

@order_items_bp.route('/order_items/<int:order_item_id>', methods=['GET'])
@session_required
def get_order_item_by_id(order_item_id):
    """API to retrieve an order item by ID."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    order_item = order_item_manager.get_order_item_by_id(order_item_id)
    if not order_item:
        return jsonify({'error': 'Order item not found'}), 404

    # Check if the user owns the order or is admin
    order = order_manager.get_order_by_id(order_item.order_id)
    if not order:
        return jsonify({'error': 'Associated order not found'}), 404
    if order['user_id'] != current_user_id and not is_admin:  # Changed from order.user_id to order['user_id']
        return jsonify({'error': 'Unauthorized access to this order item'}), 403

    return jsonify({
        'id': order_item.id,
        'order_id': order_item.order_id,
        'product_id': order_item.product_id,
        'quantity': order_item.quantity,
        'price': order_item.price
    }), 200

@order_items_bp.route('/order_items/order/<int:order_id>', methods=['GET'])
@session_required
def get_order_items_by_order(order_id):
    """API to retrieve all order items for an order."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    # Check if the user owns the order or is admin
    order = order_manager.get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    if order['user_id'] != current_user_id and not is_admin:  # Changed from order.user_id to order['user_id']
        return jsonify({'error': 'Unauthorized to view items for this order'}), 403

    order_items = order_item_manager.get_order_items_by_order(order_id)
    order_items_list = [
        {
            'id': item[0].id,
            'order_id': item[0].order_id,
            'product_id': item[0].product_id,
            'quantity': item[0].quantity,
            'price': item[0].price,
            'product_name': item[1]
        } for item in order_items
    ]
    return jsonify({'order_items': order_items_list}), 200

@order_items_bp.route('/order_items/<int:order_item_id>', methods=['PUT'])
@admin_required
def update_order_item(order_item_id):
    """API to update order item details."""
    data = request.get_json()
    quantity = data.get('quantity')
    price = data.get('price')

    success = order_item_manager.update_order_item(order_item_id, quantity, price)
    if success:
        return jsonify({'message': 'Order item updated successfully'}), 200
    return jsonify({'error': 'Failed to update order item'}), 400

@order_items_bp.route('/order_items/<int:order_item_id>', methods=['DELETE'])
@admin_required
def delete_order_item(order_item_id):
    """API to delete an order item by ID."""
    success = order_item_manager.delete_order_item(order_item_id)
    if success:
        return jsonify({'message': 'Order item deleted successfully'}), 200
    return jsonify({'error': 'Order item not found or failed to delete'}), 404

@order_items_bp.route('/order_items', methods=['GET'])
@admin_required
def get_order_items():
    """API to retrieve order items with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    order_items, total = order_item_manager.get_order_items(page, per_page)
    order_items_list = [
        {
            'id': item[0].id,
            'order_id': item[0].order_id,
            'product_id': item[0].product_id,
            'quantity': item[0].quantity,
            'price': item[0].price,
            'product_name': item[1]
        } for item in order_items
    ]
    return jsonify({
        'order_items': order_items_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200