from flask import Blueprint, request, jsonify
from database import CartItemManager
import logging

cart_items_bp = Blueprint('cart_items', __name__)

# Initialize CartItemManager
cart_item_manager = CartItemManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@cart_items_bp.route('/cart_items', methods=['POST'])
def add_cart_item():
    """API to add a new cart item."""
    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not user_id or not product_id or quantity is None:
        return jsonify({'error': 'User ID, product ID, and quantity are required'}), 400

    cart_item_id = cart_item_manager.add_cart_item(user_id, product_id, quantity)
    if cart_item_id:
        return jsonify({'message': 'Cart item added successfully', 'cart_item_id': cart_item_id}), 201
    return jsonify({'error': 'Failed to add cart item'}), 500

@cart_items_bp.route('/cart_items/<int:cart_item_id>', methods=['GET'])
def get_cart_item_by_id(cart_item_id):
    """API to retrieve a cart item by ID."""
    cart_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
    if cart_item:
        return jsonify({
            'id': cart_item['id'],
            'user_id': cart_item['user_id'],
            'product_id': cart_item['product_id'],
            'quantity': cart_item['quantity'],
            'added_at': cart_item['added_at']
        }), 200
    return jsonify({'error': 'Cart item not found'}), 404

@cart_items_bp.route('/cart_items/user/<int:user_id>', methods=['GET'])
def get_cart_items_by_user(user_id):
    """API to retrieve all cart items for a user."""
    cart_items = cart_item_manager.get_cart_items_by_user(user_id)
    if cart_items:
        cart_items_list = [
            {
                'id': item['id'],
                'user_id': item['user_id'],
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'added_at': item['added_at'],
                'product_name': item['name'],
                'product_price': item['price']
            } for item in cart_items
        ]
        return jsonify({'cart_items': cart_items_list}), 200
    return jsonify({'cart_items': [], 'message': 'No cart items found for this user'}), 200

@cart_items_bp.route('/cart_items/<int:cart_item_id>', methods=['PUT'])
def update_cart_item(cart_item_id):
    """API to update cart item details."""
    data = request.get_json()
    quantity = data.get('quantity')

    success = cart_item_manager.update_cart_item(cart_item_id, quantity)
    if success:
        return jsonify({'message': 'Cart item updated successfully'}), 200
    return jsonify({'error': 'Failed to update cart item'}), 400

@cart_items_bp.route('/cart_items/<int:cart_item_id>', methods=['DELETE'])
def delete_cart_item(cart_item_id):
    """API to delete a cart item by ID."""
    success = cart_item_manager.delete_cart_item(cart_item_id)
    if success:
        return jsonify({'message': 'Cart item deleted successfully'}), 200
    return jsonify({'error': 'Cart item not found or failed to delete'}), 404

@cart_items_bp.route('/cart_items', methods=['GET'])
def get_cart_items():
    """API to retrieve cart items with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cart_items, total = cart_item_manager.get_cart_items(page, per_page)
    cart_items_list = [
        {
            'id': item['id'],
            'user_id': item['user_id'],
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'added_at': item['added_at'],
            'product_name': item['name'],
            'product_price': item['price']
        } for item in cart_items
    ]
    return jsonify({
        'cart_items': cart_items_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200