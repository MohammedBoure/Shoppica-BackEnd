from flask import Blueprint, request, jsonify, g, session
from database import CartItemManager
from functools import wraps
import logging
from .auth import session_required, admin_required

cart_items_bp = Blueprint('cart_items', __name__)

# Initialize Manager
cart_item_manager = CartItemManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Custom Decorator for Session Authorization ---

def check_cart_item_ownership(fn):
    """
    Custom decorator (session-based) to ensure the current user owns the cart item or is an admin.
    Fetches the cart item and passes it to the decorated function to avoid a second DB call.
    """
    @wraps(fn)
    @session_required
    def wrapper(*args, **kwargs):
        cart_item_id = kwargs.get("cart_item_id")
        current_user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)

        if not current_user_id:
            return jsonify(error="User not authenticated"), 401

        cart_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
        if not cart_item:
            return jsonify(error="Cart item not found"), 404

        # Allow access if the item belongs to the user OR if the user is an admin
        if cart_item['user_id'] != current_user_id and not is_admin:
            return jsonify(error="Unauthorized access to this cart item"), 403
        
        # Pass the fetched item to the route function
        g.cart_item = cart_item
        return fn(*args, **kwargs)
    return wrapper

# --- API Endpoints ---

@cart_items_bp.route('/cart/items', methods=['POST'])
@session_required
def add_cart_item():
    """Add a product to the current user's cart."""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(error="User not authenticated"), 401

    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify(error="product_id and quantity are required"), 400

    try:
        product_id = int(data['product_id'])
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify(error="Quantity must be a positive integer"), 400

        cart_item_id = cart_item_manager.add_cart_item(
            user_id=current_user_id,
            product_id=product_id,
            quantity=quantity
        )
        if cart_item_id:
            new_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
            if not new_item:
                return jsonify(error="Failed to retrieve newly added cart item"), 500
            return jsonify(new_item), 201  # Removed dict() as new_item is already a dict
        return jsonify(error="Failed to add cart item, possibly due to insufficient stock"), 400
    except ValueError:
        return jsonify(error="Invalid product_id or quantity format"), 400
    except Exception as e:
        logger.error(f"Error adding cart item for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/cart/items', methods=['GET'])
@session_required
def get_my_cart_items():
    """Retrieve all cart items for the current user."""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(error="User not authenticated"), 401

    try:
        cart_items = cart_item_manager.get_cart_items_by_user(current_user_id)
        return jsonify(cart_items), 200  # cart_items is already a list of dicts
    except Exception as e:
        logger.error(f"Error getting cart items for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['GET'])
@check_cart_item_ownership
def get_cart_item_by_id(cart_item_id):
    """Retrieve a specific cart item by ID."""
    return jsonify(g.cart_item), 200  # g.cart_item is already a dict

@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['PUT'])
@check_cart_item_ownership
def update_cart_item(cart_item_id):
    """Update the quantity of a specific cart item."""
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify(error="Quantity is required"), 400

    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify(error="Quantity must be a positive integer"), 400

        success = cart_item_manager.update_cart_item(cart_item_id, quantity)
        if success:
            updated_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
            if not updated_item:
                return jsonify(error="Failed to retrieve updated cart item"), 500
            return jsonify(updated_item), 200  # updated_item is already a dict
        return jsonify(error="Failed to update cart item, possibly due to insufficient stock"), 400
    except ValueError:
        return jsonify(error="Invalid quantity format"), 400
    except Exception as e:
        logger.error(f"Error updating cart item {cart_item_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['DELETE'])
@check_cart_item_ownership
def delete_cart_item(cart_item_id):
    """Delete a specific cart item."""
    try:
        success = cart_item_manager.delete_cart_item(cart_item_id)
        if success:
            return jsonify(message="Cart item deleted successfully"), 200
        return jsonify(error="Cart item not found"), 404
    except Exception as e:
        logger.error(f"Error deleting cart item {cart_item_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart_items/user/<int:user_id>', methods=['GET'])
@admin_required
def get_cart_items_by_user_as_admin(user_id):
    """(Admin) Retrieve all cart items for a specific user."""
    try:
        cart_items = cart_item_manager.get_cart_items_by_user(user_id)
        return jsonify(cart_items), 200  # cart_items is already a list of dicts
    except Exception as e:
        logger.error(f"Admin error getting cart items for user {user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart_items', methods=['GET'])
@admin_required
def get_all_cart_items_paginated():
    """(Admin) Retrieve paginated cart items."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        if page < 1 or per_page < 1:
            return jsonify(error="Invalid page or per_page value"), 400

        cart_items, total = cart_item_manager.get_cart_items(page, per_page)
        return jsonify({
            'cart_items': cart_items,  # cart_items is already a list of dicts
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Admin error getting paginated cart items: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/cart/clear', methods=['DELETE'])
@session_required
def clear_my_cart():
    """Clear all items from the current user's cart."""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(error="User not authenticated"), 401

    try:
        deleted_count = cart_item_manager.delete_cart_items_by_user(current_user_id)
        return jsonify(message=f"Cart cleared successfully. {deleted_count} items removed."), 200
    except Exception as e:
        logger.error(f"Error clearing cart for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/cart/stats', methods=['GET'])
@session_required
def get_my_cart_stats():
    """Retrieve statistics for the current user's cart."""
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify(error="User not authenticated"), 401

    try:
        stats = cart_item_manager.get_user_cart_stats(current_user_id)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting cart stats for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

# --- Admin-Only Endpoints ---

@cart_items_bp.route('/admin/cart_items/search', methods=['GET'])
@admin_required
def search_cart_items():
    """(Admin) Search for cart items based on user_id or product_id with pagination."""
    user_id = request.args.get('user_id', type=int)
    product_id = request.args.get('product_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not user_id and not product_id:
        return jsonify(error="At least one search parameter (user_id or product_id) is required"), 400

    if page < 1 or per_page < 1:
        return jsonify(error="Invalid page or per_page value"), 400

    try:
        items, total = cart_item_manager.search_cart_items(
            user_id=user_id, product_id=product_id, page=page, per_page=per_page
        )
        return jsonify({
            'cart_items': items,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Admin error searching cart items: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart_items/user/<int:user_id>', methods=['DELETE'])
@admin_required
def clear_user_cart_as_admin(user_id):
    """(Admin) Clear all cart items for a specific user."""
    try:
        deleted_count = cart_item_manager.delete_cart_items_by_user(user_id)
        return jsonify(message=f"Cart for user {user_id} cleared successfully. {deleted_count} items removed."), 200
    except Exception as e:
        logger.error(f"Admin error clearing cart for user {user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart_items/product/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_cart_items_by_product(product_id):
    """(Admin) Delete all cart items for a specific product."""
    try:
        deleted_count = cart_item_manager.delete_cart_items_by_product(product_id)
        return jsonify(message=f"All cart items for product {product_id} deleted successfully. {deleted_count} items removed."), 200
    except Exception as e:
        logger.error(f"Admin error deleting cart items for product {product_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart/stats', methods=['GET'])
@admin_required
def get_overall_cart_stats():
    """(Admin) Retrieve overall statistics for all cart items."""
    try:
        stats = cart_item_manager.get_cart_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Admin error getting overall cart stats: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500

@cart_items_bp.route('/admin/cart_items/user/<int:user_id>/stats', methods=['GET'])
@admin_required
def get_user_cart_stats_as_admin(user_id):
    """(Admin) Retrieve statistics for a specific user's cart."""
    try:
        stats = cart_item_manager.get_user_cart_stats(user_id)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Admin error getting cart stats for user {user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500