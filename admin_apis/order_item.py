from flask import Blueprint, request, jsonify
from database import OrderItemManager
import logging

order_items_bp = Blueprint('order_items', __name__)

# Initialize OrderItemManager
order_item_manager = OrderItemManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@order_items_bp.route('/order_items', methods=['POST'])
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
def get_order_item_by_id(order_item_id):
    """API to retrieve an order item by ID."""
    order_item = order_item_manager.get_order_item_by_id(order_item_id)
    if order_item:
        return jsonify({
            'id': order_item['id'],
            'order_id': order_item['order_id'],
            'product_id': order_item['product_id'],
            'quantity': order_item['quantity'],
            'price': order_item['price']
        }), 200
    return jsonify({'error': 'Order item not found'}), 404

@order_items_bp.route('/order_items/order/<int:order_id>', methods=['GET'])
def get_order_items_by_order(order_id):
    """API to retrieve all order items for an order."""
    order_items = order_item_manager.get_order_items_by_order(order_id)
    if order_items:
        order_items_list = [
            {
                'id': item['id'],
                'order_id': item['order_id'],
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'price': item['price'],
                'product_name': item['name']
            } for item in order_items
        ]
        return jsonify({'order_items': order_items_list}), 200
    return jsonify({'order_items': [], 'message': 'No order items found for this order'}), 200

@order_items_bp.route('/order_items/<int:order_item_id>', methods=['PUT'])
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
def delete_order_item(order_item_id):
    """API to delete an order item by ID."""
    success = order_item_manager.delete_order_item(order_item_id)
    if success:
        return jsonify({'message': 'Order item deleted successfully'}), 200
    return jsonify({'error': 'Order item not found or failed to delete'}), 404

@order_items_bp.route('/order_items', methods=['GET'])
def get_order_items():
    """API to retrieve order items with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    order_items, total = order_item_manager.get_order_items(page, per_page)
    order_items_list = [
        {
            'id': item['id'],
            'order_id': item['order_id'],
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'price': item['price'],
            'product_name': item['name']
        } for item in order_items
    ]
    return jsonify({
        'order_items': order_items_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200