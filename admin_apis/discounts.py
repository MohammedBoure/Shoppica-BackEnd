from flask import Blueprint, request, jsonify
from database import DiscountManager
import logging

discounts_bp = Blueprint('discounts', __name__)

# Initialize DiscountManager
discount_manager = DiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@discounts_bp.route('/discounts', methods=['POST'])
def add_discount():
    """API to add a new discount."""
    data = request.get_json()
    code = data.get('code')
    discount_percent = data.get('discount_percent')
    max_uses = data.get('max_uses')
    expires_at = data.get('expires_at')
    description = data.get('description')

    if not code or discount_percent is None:
        return jsonify({'error': 'Code and discount percent are required'}), 400

    discount_id = discount_manager.add_discount(code, discount_percent, max_uses, expires_at, description)
    if discount_id:
        return jsonify({'message': 'Discount added successfully', 'discount_id': discount_id}), 201
    return jsonify({'error': 'Failed to add discount'}), 500

@discounts_bp.route('/discounts/<int:discount_id>', methods=['GET'])
def get_discount_by_id(discount_id):
    """API to retrieve a discount by ID."""
    discount = discount_manager.get_discount_by_id(discount_id)
    if discount:
        return jsonify({
            'id': discount['id'],
            'code': discount['code'],
            'description': discount['description'],
            'discount_percent': discount['discount_percent'],
            'max_uses': discount['max_uses'],
            'expires_at': discount['expires_at'],
            'is_active': discount['is_active']
        }), 200
    return jsonify({'error': 'Discount not found'}), 404

@discounts_bp.route('/discounts/code/<string:code>', methods=['GET'])
def get_discount_by_code(code):
    """API to retrieve a discount by code."""
    discount = discount_manager.get_discount_by_code(code)
    if discount:
        return jsonify({
            'id': discount['id'],
            'code': discount['code'],
            'description': discount['description'],
            'discount_percent': discount['discount_percent'],
            'max_uses': discount['max_uses'],
            'expires_at': discount['expires_at'],
            'is_active': discount['is_active']
        }), 200
    return jsonify({'error': 'Discount not found'}), 404

@discounts_bp.route('/discounts/valid/<string:code>', methods=['GET'])
def get_valid_discount(code):
    """API to retrieve a valid discount by code."""
    discount = discount_manager.get_valid_discount(code)
    if discount:
        return jsonify({
            'id': discount['id'],
            'code': discount['code'],
            'description': discount['description'],
            'discount_percent': discount['discount_percent'],
            'max_uses': discount['max_uses'],
            'expires_at': discount['expires_at'],
            'is_active': discount['is_active']
        }), 200
    return jsonify({'error': 'Valid discount not found'}), 404

@discounts_bp.route('/discounts/<int:discount_id>', methods=['PUT'])
def update_discount(discount_id):
    """API to update discount details."""
    data = request.get_json()
    code = data.get('code')
    description = data.get('description')
    discount_percent = data.get('discount_percent')
    max_uses = data.get('max_uses')
    expires_at = data.get('expires_at')
    is_active = data.get('is_active')

    success = discount_manager.update_discount(discount_id, code, description, discount_percent, max_uses, expires_at, is_active)
    if success:
        return jsonify({'message': 'Discount updated successfully'}), 200
    return jsonify({'error': 'Failed to update discount'}), 400

@discounts_bp.route('/discounts/<int:discount_id>', methods=['DELETE'])
def delete_discount(discount_id):
    """API to delete a discount by ID."""
    success = discount_manager.delete_discount(discount_id)
    if success:
        return jsonify({'message': 'Discount deleted successfully'}), 200
    return jsonify({'error': 'Discount not found or failed to delete'}), 404

@discounts_bp.route('/discounts', methods=['GET'])
def get_discounts():
    """API to retrieve discounts with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    discounts, total = discount_manager.get_discounts(page, per_page)
    discounts_list = [
        {
            'id': discount['id'],
            'code': discount['code'],
            'description': discount['description'],
            'discount_percent': discount['discount_percent'],
            'max_uses': discount['max_uses'],
            'expires_at': discount['expires_at'],
            'is_active': discount['is_active']
        } for discount in discounts
    ]
    return jsonify({
        'discounts': discounts_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200