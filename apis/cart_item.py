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
    It also fetches the cart item and passes it to the decorated function to avoid a second DB call.
    """
    @wraps(fn)
    @session_required  # Ensures user is logged in via session first
    def wrapper(*args, **kwargs):
        cart_item_id = kwargs.get("cart_item_id")
        current_user_id = session['user_id']
        is_admin = session.get('is_admin', False)

        cart_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
        if not cart_item:
            return jsonify(error="Cart item not found"), 404

        # Allow access if the item belongs to the user OR if the user is an admin
        if cart_item['user_id'] != current_user_id and not is_admin:
            return jsonify(error="Unauthorized access to this cart item"), 403
        
        # Pass the fetched item to the route function to avoid re-fetching
        g.cart_item = cart_item
        return fn(*args, **kwargs)
    return wrapper


# --- API Endpoints ---

@cart_items_bp.route('/cart/items', methods=['POST'])
@session_required  
def add_cart_item():
    """
    API to add a new item to the CURRENT user's cart.
    The user_id is taken from the session, not the request body.
    """
    current_user_id = session['user_id']  # Changed from get_jwt_identity()
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify(error="product_id and quantity are required"), 400

    try:
        cart_item_id = cart_item_manager.add_cart_item(
            user_id=current_user_id,
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        if cart_item_id:
            new_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
            return jsonify(new_item), 201
        return jsonify(error="Failed to add cart item"), 500
    except Exception as e:
        logger.error(f"Error adding cart item: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@cart_items_bp.route('/cart/items', methods=['GET'])
@session_required   
def get_my_cart_items():
    """API to retrieve all cart items for the currently authenticated user."""
    current_user_id = session['user_id']  # Changed from get_jwt_identity()
    try:
        cart_items = cart_item_manager.get_cart_items_by_user(current_user_id)
        return jsonify(cart_items), 200
    except Exception as e:
        logger.error(f"Error getting cart items for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['GET'])
@check_cart_item_ownership  # This decorator now uses sessions
def get_cart_item_by_id(cart_item_id):
    """API to retrieve a specific cart item by its ID."""
    return jsonify(g.cart_item), 200


@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['PUT'])
@check_cart_item_ownership  # This decorator now uses sessions
def update_cart_item(cart_item_id):
    """API to update a cart item's quantity."""
    data = request.get_json()
    quantity = data.get('quantity')
    if quantity is None or not isinstance(quantity, int) or quantity < 0:
        return jsonify(error="A valid quantity is required"), 400

    try:
        success = cart_item_manager.update_cart_item(cart_item_id, quantity)
        if success:
            updated_item = cart_item_manager.get_cart_item_by_id(cart_item_id)
            return jsonify(updated_item), 200
        return jsonify(error="Failed to update cart item"), 400
    except Exception as e:
        logger.error(f"Error updating cart item {cart_item_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@cart_items_bp.route('/cart/items/<int:cart_item_id>', methods=['DELETE'])
@check_cart_item_ownership  # This decorator now uses sessions
def delete_cart_item(cart_item_id):
    """API to delete a cart item by ID."""
    try:
        success = cart_item_manager.delete_cart_item(cart_item_id)
        if success:
            return jsonify(message="Cart item deleted successfully"), 200
        return jsonify(error="Cart item not found or failed to delete"), 404
    except Exception as e:
        logger.error(f"Error deleting cart item {cart_item_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


# --- Admin-Only Endpoints ---

@cart_items_bp.route('/admin/cart_items/user/<int:user_id>', methods=['GET'])
@admin_required  # Replaced custom JWT admin decorator with the one from auth.py
def get_cart_items_by_user_as_admin(user_id):
    """(Admin) API to retrieve all cart items for a specific user."""
    try:
        cart_items = cart_item_manager.get_cart_items_by_user(user_id)
        return jsonify(cart_items), 200
    except Exception as e:
        logger.error(f"Admin error getting cart items for user {user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@cart_items_bp.route('/admin/cart_items', methods=['GET'])
@admin_required  # Replaced custom JWT admin decorator with the one from auth.py
def get_all_cart_items_paginated():
    """(Admin) API to retrieve all cart items with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        cart_items, total = cart_item_manager.get_cart_items(page, per_page)
        return jsonify({
            'cart_items': cart_items,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Admin error getting paginated cart items: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500