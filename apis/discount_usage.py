from flask import Blueprint, request, jsonify, session
from database import DiscountUsageManager
from .auth import session_required, admin_required
import logging

discount_usages_bp = Blueprint('discount_usages', __name__)
discount_usage_manager = DiscountUsageManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@discount_usages_bp.route('/discount_usages', methods=['POST'])
@session_required
def add_discount_usage():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400

        discount_id = data.get('discount_id')
        user_id = data.get('user_id')
        current_user_id = int(session['user_id'])

        if not discount_id or not user_id:
            return jsonify({'error': 'Discount ID and user ID are required'}), 400
        if not isinstance(discount_id, int) or discount_id <= 0:
            return jsonify({'error': 'Discount ID must be a positive integer'}), 400
        if not isinstance(user_id, int) or user_id <= 0:
            return jsonify({'error': 'User ID must be a positive integer'}), 400
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized: User ID does not match authenticated user'}), 403

        usage_id = discount_usage_manager.add_discount_usage(discount_id, user_id)
        if usage_id:
            return jsonify({'message': 'Discount usage added successfully', 'usage_id': usage_id}), 201
        return jsonify({'error': 'Failed to add discount usage'}), 500
    except Exception as e:
        logger.error(f"Error adding discount usage: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['GET'])
@admin_required
def get_discount_usage_by_id(usage_id):
    try:
        usage = discount_usage_manager.get_discount_usage_by_id(usage_id)
        if usage:
            return jsonify({
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            }), 200
        return jsonify({'error': 'Discount usage not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving discount usage {usage_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/discount/<int:discount_id>', methods=['GET'])
@admin_required
def get_discount_usages_by_discount(discount_id):
    try:
        usages = discount_usage_manager.get_discount_usages_by_discount(discount_id)
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages or []
        ]
        return jsonify({'discount_usages': usages_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages for discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/user/<int:user_id>', methods=['GET'])
@session_required
def get_discount_usages_by_user(user_id):
    try:
        current_user_id = int(session['user_id'])
        if user_id != current_user_id:
            return jsonify({'error': 'Unauthorized: User ID does not match authenticated user'}), 403

        usages = discount_usage_manager.get_discount_usages_by_user(user_id)
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages or []
        ]
        return jsonify({'discount_usages': usages_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['DELETE'])
@admin_required
def delete_discount_usage(usage_id):
    try:
        success = discount_usage_manager.delete_discount_usage(usage_id)
        if success:
            return jsonify({'message': 'Discount usage deleted successfully'}), 200
        return jsonify({'error': 'Discount usage not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting discount usage {usage_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages', methods=['GET'])
@admin_required
def get_discount_usages():
    try:
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
            } for usage in usages or []
        ]
        return jsonify({
            'discount_usages': usages_list,
            'total': total or 0,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
