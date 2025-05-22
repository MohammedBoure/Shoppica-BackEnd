from flask import Blueprint, request, jsonify
from database import DiscountUsageManager
import logging

discount_usages_bp = Blueprint('discount_usages', __name__)

# Initialize DiscountUsageManager
discount_usage_manager = DiscountUsageManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@discount_usages_bp.route('/discount_usages', methods=['POST'])
def add_discount_usage():
    """API to add a new discount usage."""
    data = request.get_json()
    discount_id = data.get('discount_id')
    user_id = data.get('user_id')

    if not discount_id or not user_id:
        return jsonify({'error': 'Discount ID and user ID are required'}), 400

    usage_id = discount_usage_manager.add_discount_usage(discount_id, user_id)
    if usage_id:
        return jsonify({'message': 'Discount usage added successfully', 'usage_id': usage_id}), 201
    return jsonify({'error': 'Failed to add discount usage'}), 500

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['GET'])
def get_discount_usage_by_id(usage_id):
    """API to retrieve a discount usage by ID."""
    usage = discount_usage_manager.get_discount_usage_by_id(usage_id)
    if usage:
        return jsonify({
            'id': usage['id'],
            'discount_id': usage['discount_id'],
            'user_id': usage['user_id'],
            'used_at': usage['used_at']
        }), 200
    return jsonify({'error': 'Discount usage not found'}), 404

@discount_usages_bp.route('/discount_usages/discount/<int:discount_id>', methods=['GET'])
def get_discount_usages_by_discount(discount_id):
    """API to retrieve all discount usages for a discount."""
    usages = discount_usage_manager.get_discount_usages_by_discount(discount_id)
    if usages:
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages
        ]
        return jsonify({'discount_usages': usages_list}), 200
    return jsonify({'discount_usages': [], 'message': 'No discount usages found for this discount'}), 200

@discount_usages_bp.route('/discount_usages/user/<int:user_id>', methods=['GET'])
def get_discount_usages_by_user(user_id):
    """API to retrieve all discount usages for a user."""
    usages = discount_usage_manager.get_discount_usages_by_user(user_id)
    if usages:
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages
        ]
        return jsonify({'discount_usages': usages_list}), 200
    return jsonify({'discount_usages': [], 'message': 'No discount usages found for this user'}), 200

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['DELETE'])
def delete_discount_usage(usage_id):
    """API to delete a discount usage by ID."""
    success = discount_usage_manager.delete_discount_usage(usage_id)
    if success:
        return jsonify({'message': 'Discount usage deleted successfully'}), 200
    return jsonify({'error': 'Discount usage not found or failed to delete'}), 404

@discount_usages_bp.route('/discount_usages', methods=['GET'])
def get_discount_usages():
    """API to retrieve discount usages with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    usages, total = discount_usage_manager.get_discount_usages(page, per_page)
    usages_list = [
        {
            'id': usage['id'],
            'discount_id': usage['discount_id'],
            'user_id': usage['user_id'],
            'used_at': usage['used_at'],
            'discount_code': usage['code']
        } for usage in usages
    ]
    return jsonify({
        'discount_usages': usages_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200