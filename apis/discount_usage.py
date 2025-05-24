from flask import Blueprint, request, jsonify
from database import DiscountUsageManager
from flask_jwt_extended import jwt_required, get_jwt
from .auth import admin_required
import logging

discount_usages_bp = Blueprint('discount_usages', __name__)

# Initialize DiscountUsageManager
discount_usage_manager = DiscountUsageManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@discount_usages_bp.route('/discount_usages', methods=['POST'])
@jwt_required()
def add_discount_usage():
    """API to add a new discount usage."""
    try:
        data = request.get_json()
        discount_id = data.get('discount_id')
        user_id = data.get('user_id')
        current_user_id = get_jwt()['sub']  # Get user_id from JWT token

        if not discount_id or not user_id:
            logger.warning("Missing required fields: discount_id or user_id")
            return jsonify({'error': 'Discount ID and user ID are required'}), 400

        if not isinstance(discount_id, int) or discount_id <= 0:
            logger.warning(f"Invalid discount_id: {discount_id}")
            return jsonify({'error': 'Discount ID must be a positive integer'}), 400

        if not isinstance(user_id, int) or user_id <= 0:
            logger.warning(f"Invalid user_id: {user_id}")
            return jsonify({'error': 'User ID must be a positive integer'}), 400

        if str(user_id) != current_user_id:
            logger.warning(f"Unauthorized attempt to add discount usage: user_id={user_id}, current_user_id={current_user_id}")
            return jsonify({'error': 'Unauthorized: User ID does not match authenticated user'}), 403

        usage_id = discount_usage_manager.add_discount_usage(discount_id, user_id)
        if usage_id:
            logger.info(f"Discount usage added successfully: usage_id={usage_id}, discount_id={discount_id}, user_id={user_id}")
            return jsonify({'message': 'Discount usage added successfully', 'usage_id': usage_id}), 201
        logger.error(f"Failed to add discount usage: discount_id={discount_id}, user_id={user_id}")
        return jsonify({'error': 'Failed to add discount usage'}), 500
    except Exception as e:
        logger.error(f"Error adding discount usage: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['GET'])
@admin_required
def get_discount_usage_by_id(usage_id):
    """API to retrieve a discount usage by ID."""
    try:
        usage = discount_usage_manager.get_discount_usage_by_id(usage_id)
        if usage:
            logger.info(f"Retrieved discount usage: usage_id={usage_id}")
            return jsonify({
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            }), 200
        logger.warning(f"Discount usage not found: usage_id={usage_id}")
        return jsonify({'error': 'Discount usage not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving discount usage {usage_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/discount/<int:discount_id>', methods=['GET'])
@admin_required
def get_discount_usages_by_discount(discount_id):
    """API to retrieve all discount usages for a discount."""
    try:
        usages = discount_usage_manager.get_discount_usages_by_discount(discount_id)
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages
        ]
        logger.info(f"Retrieved {len(usages_list)} discount usages for discount_id={discount_id}")
        return jsonify({'discount_usages': usages_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages for discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_discount_usages_by_user(user_id):
    """API to retrieve all discount usages for a user."""
    try:
        current_user_id = get_jwt()['sub']  # Get user_id from JWT token

        if str(user_id) != current_user_id:
            logger.warning(f"Unauthorized attempt to access discount usages: user_id={user_id}, current_user_id={current_user_id}")
            return jsonify({'error': 'Unauthorized: User ID does not match authenticated user'}), 403

        usages = discount_usage_manager.get_discount_usages_by_user(user_id)
        usages_list = [
            {
                'id': usage['id'],
                'discount_id': usage['discount_id'],
                'user_id': usage['user_id'],
                'used_at': usage['used_at']
            } for usage in usages
        ]
        logger.info(f"Retrieved {len(usages_list)} discount usages for user_id={user_id}")
        return jsonify({'discount_usages': usages_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages/<int:usage_id>', methods=['DELETE'])
@admin_required
def delete_discount_usage(usage_id):
    """API to delete a discount usage by ID."""
    try:
        success = discount_usage_manager.delete_discount_usage(usage_id)
        if success:
            logger.info(f"Discount usage deleted successfully: usage_id={usage_id}")
            return jsonify({'message': 'Discount usage deleted successfully'}), 200
        logger.warning(f"Discount usage not found or failed to delete: usage_id={usage_id}")
        return jsonify({'error': 'Discount usage not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting discount usage {usage_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discount_usages_bp.route('/discount_usages', methods=['GET'])
@admin_required
def get_discount_usages():
    """API to retrieve discount usages with pagination."""
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
            } for usage in usages
        ]
        logger.info(f"Retrieved {len(usages_list)} discount usages for page={page}, per_page={per_page}")
        return jsonify({
            'discount_usages': usages_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving discount usages: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500