from flask import Blueprint, request, jsonify, g, session
from database import AddressManager
from functools import wraps
import logging
from .auth import session_required, admin_required

addresses_bp = Blueprint('addresses', __name__)

# Initialize Manager
address_manager = AddressManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Custom Decorator for Session Authorization ---

def check_address_ownership(fn):
    """
    Custom decorator (session-based) to ensure the current user owns the address or is an admin.
    It fetches the address and passes it to the route function via the `g` object.
    """
    @wraps(fn)
    @session_required  # Ensures user is logged in first
    def wrapper(*args, **kwargs):
        address_id = kwargs.get("address_id")
        current_user_id = session['user_id']
        is_admin = session.get('is_admin', False)

        address = address_manager.get_address_by_id(address_id)
        if not address:
            return jsonify(error="Address not found"), 404

        # Allow access if the address belongs to the user OR if the user is an admin
        if address['user_id'] != current_user_id and not is_admin:
            return jsonify(error="Unauthorized access to this address"), 403
        
        # Pass the fetched address to the route function
        g.address = address
        return fn(*args, **kwargs)
    return wrapper


# --- API Endpoints for Users ---

@addresses_bp.route('/addresses', methods=['POST'])
@session_required
def add_address():
    """
    API to add a new address for the CURRENT user.
    The user_id is taken securely from the session.
    """
    current_user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify(error="Request body must be JSON"), 400

    address_line1 = data.get('address_line1')
    city = data.get('city')
    country = data.get('country')

    if not address_line1 or not city or not country:
        return jsonify(error="address_line1, city, and country are required"), 400

    try:
        address_id = address_manager.add_address(
            user_id=current_user_id,
            address_line1=address_line1,
            city=city,
            country=country,
            address_line2=data.get('address_line2'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            is_default=data.get('is_default', False)
        )
        if address_id:
            new_address = address_manager.get_address_by_id(address_id)
            return jsonify(dict(new_address)), 201
        return jsonify(error="Failed to add address"), 500
    except Exception as e:
        logger.error(f"Error adding address for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@addresses_bp.route('/addresses/me', methods=['GET'])
@session_required
def get_my_addresses():
    """API to retrieve all addresses for the currently authenticated user."""
    current_user_id = session['user_id']
    try:
        addresses = address_manager.get_addresses_by_user(current_user_id)
        return jsonify(addresses), 200
    except Exception as e:
        logger.error(f"Error getting addresses for user {current_user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@addresses_bp.route('/addresses/<int:address_id>', methods=['GET'])
@check_address_ownership
def get_address_by_id(address_id):
    """API to retrieve a specific address by its ID, checking ownership."""
    return jsonify(g.address), 200


@addresses_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@check_address_ownership
def update_address(address_id):
    """API to update an address, checking ownership."""
    data = request.get_json()
    if not data:
        return jsonify(error="Request body must be JSON"), 400

    try:
        success = address_manager.update_address(
            address_id=address_id,
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            is_default=data.get('is_default')
        )
        if success:
            updated_address = address_manager.get_address_by_id(address_id)
            return jsonify(dict(updated_address)), 200
        return jsonify(error="Failed to update address"), 400
    except Exception as e:
        logger.error(f"Error updating address {address_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@addresses_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@check_address_ownership
def delete_address(address_id):
    """API to delete an address, checking ownership."""
    try:
        success = address_manager.delete_address(address_id)
        if success:
            return jsonify(message="Address deleted successfully"), 200
        return jsonify(error="Address not found or failed to delete"), 404
    except Exception as e:
        logger.error(f"Error deleting address {address_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


# --- Admin-Only Endpoints ---

@addresses_bp.route('/admin/addresses/user/<int:user_id>', methods=['GET'])
@admin_required
def get_addresses_by_user_as_admin(user_id):
    """(Admin) API to retrieve all addresses for a specific user."""
    try:
        addresses = address_manager.get_addresses_by_user(user_id)
        return jsonify(addresses), 200
    except Exception as e:
        logger.error(f"Admin error getting addresses for user {user_id}: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500


@addresses_bp.route('/admin/addresses', methods=['GET'])
@admin_required
def get_all_addresses_paginated():
    """(Admin) API to retrieve all addresses with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        addresses, total = address_manager.get_addresses(page, per_page)
        return jsonify({
            'addresses': addresses,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Admin error getting paginated addresses: {e}", exc_info=True)
        return jsonify(error="An internal server error occurred"), 500