from flask import Blueprint, request, jsonify
from database import DiscountManager
from .auth import admin_required, session_required
import logging
from datetime import datetime

discounts_bp = Blueprint('discounts', __name__)

# Initialize DiscountManager
discount_manager = DiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@discounts_bp.route('/discounts', methods=['POST'])
@admin_required
def add_discount():
    """API to add a new discount."""
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided")
            return jsonify({'error': 'Request must contain JSON data'}), 400

        code = data.get('code')
        discount_percent = data.get('discount_percent')
        max_uses = data.get('max_uses')
        expires_at = data.get('expires_at')
        description = data.get('description')

        # Validate required fields
        if not code or discount_percent is None:
            logger.warning("Missing required fields: code or discount_percent")
            return jsonify({'error': 'Code and discount percent are required'}), 400

        # Validate discount_percent
        if not isinstance(discount_percent, (int, float)) or not (0 <= discount_percent <= 100):
            logger.warning(f"Invalid discount_percent: {discount_percent}")
            return jsonify({'error': 'Discount percent must be a number between 0 and 100'}), 400

        # Validate max_uses
        if max_uses is not None and (not isinstance(max_uses, int) or max_uses < 0):
            logger.warning(f"Invalid max_uses: {max_uses}")
            return jsonify({'error': 'Max uses must be a non-negative integer'}), 400

        # Validate expires_at if provided
        if expires_at:
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                logger.warning(f"Invalid expires_at format: {expires_at}")
                return jsonify({'error': 'Expires at must be a valid ISO datetime'}), 400

        discount_id = discount_manager.add_discount(code, discount_percent, max_uses, expires_at, description)
        if discount_id:
            logger.info(f"Discount added successfully: discount_id={discount_id}")
            return jsonify({'message': 'Discount added successfully', 'discount_id': discount_id}), 201
        logger.error("Failed to add discount")
        return jsonify({'error': 'Failed to add discount'}), 500
    except Exception as e:
        logger.error(f"Error adding discount: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts/<int:discount_id>', methods=['GET'])
@admin_required
def get_discount_by_id(discount_id):
    """API to retrieve a discount by ID."""
    try:
        discount = discount_manager.get_discount_by_id(discount_id)
        if discount:
            logger.info(f"Retrieved discount: discount_id={discount_id}")
            return jsonify({
                'id': discount.id,
                'code': discount.code,
                'description': discount.description,
                'discount_percent': discount.discount_percent,
                'max_uses': discount.max_uses,
                'expires_at': discount.expires_at.isoformat() if discount.expires_at else None,
                'is_active': bool(discount.is_active)
            }), 200
        logger.warning(f"Discount not found: discount_id={discount_id}")
        return jsonify({'error': 'Discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts/code/<string:code>', methods=['GET'])
@session_required
def get_discount_by_code(code):
    """API to retrieve a discount by code."""
    try:
        discount = discount_manager.get_discount_by_code(code)
        if discount:
            logger.info(f"Retrieved discount by code: code={code}")
            return jsonify({
                'id': discount.id,
                'code': discount.code,
                'description': discount.description,
                'discount_percent': discount.discount_percent,
                'max_uses': discount.max_uses,
                'expires_at': discount.expires_at.isoformat() if discount.expires_at else None,
                'is_active': bool(discount.is_active)
            }), 200
        logger.warning(f"Discount not found: code={code}")
        return jsonify({'error': 'Discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving discount by code {code}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts/valid/<string:code>', methods=['GET'])
@session_required
def get_valid_discount(code):
    """API to retrieve a valid discount by code."""
    try:
        discount = discount_manager.get_valid_discount(code)
        if discount:
            logger.info(f"Retrieved valid discount: code={code}")
            return jsonify({
                'id': discount.id,
                'code': discount.code,
                'description': discount.description,
                'discount_percent': discount.discount_percent,
                'max_uses': discount.max_uses,
                'expires_at': discount.expires_at.isoformat() if discount.expires_at else None,
                'is_active': bool(discount.is_active)
            }), 200
        logger.warning(f"Valid discount not found: code={code}")
        return jsonify({'error': 'Valid discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving valid discount {code}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_discount(discount_id):
    """API to update discount details."""
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided for update")
            return jsonify({'error': 'Request must contain JSON data'}), 400

        code = data.get('code')
        description = data.get('description')
        discount_percent = data.get('discount_percent')
        max_uses = data.get('max_uses')
        expires_at = data.get('expires_at')
        is_active = data.get('is_active')

        # Validate discount_percent if provided
        if discount_percent is not None:
            if not isinstance(discount_percent, (int, float)) or not (0 <= discount_percent <= 100):
                logger.warning(f"Invalid discount_percent: {discount_percent} for discount_id={discount_id}")
                return jsonify({'error': 'Discount percent must be a number between 0 and 100'}), 400

        # Validate max_uses if provided
        if max_uses is not None:
            if not isinstance(max_uses, int) or max_uses < 0:
                logger.warning(f"Invalid max_uses: {max_uses} for discount_id={discount_id}")
                return jsonify({'error': 'Max uses must be a non-negative integer'}), 400

        # Validate expires_at if provided
        if expires_at:
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except ValueError:
                logger.warning(f"Invalid expires_at format: {expires_at} for discount_id={discount_id}")
                return jsonify({'error': 'Expires at must be a valid ISO datetime'}), 400

        # Validate is_active if provided
        if is_active is not None:
            if not isinstance(is_active, bool):
                logger.warning(f"Invalid is_active: {is_active} for discount_id={discount_id}")
                return jsonify({'error': 'Is active must be a boolean'}), 400
            is_active = int(is_active)  # Convert to integer for database

        success = discount_manager.update_discount(discount_id, code, description, discount_percent, max_uses, expires_at, is_active)
        if success:
            logger.info(f"Discount updated successfully: discount_id={discount_id}")
            return jsonify({'message': 'Discount updated successfully'}), 200
        logger.warning(f"Failed to update discount: discount_id={discount_id}")
        return jsonify({'error': 'Discount not found or failed to update'}), 404
    except Exception as e:
        logger.error(f"Error updating discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts/<int:discount_id>', methods=['DELETE'])
@admin_required
def delete_discount(discount_id):
    """API to delete a discount by ID."""
    try:
        success = discount_manager.delete_discount(discount_id)
        if success:
            logger.info(f"Discount deleted successfully: discount_id={discount_id}")
            return jsonify({'message': 'Discount deleted successfully'}), 200
        logger.warning(f"Discount not found or failed to delete: discount_id={discount_id}")
        return jsonify({'error': 'Discount not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@discounts_bp.route('/discounts', methods=['GET'])
@admin_required
def get_discounts():
    """API to retrieve discounts with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Validate pagination parameters
        if page < 1:
            logger.warning(f"Invalid page number: {page}")
            return jsonify({'error': 'Page number must be positive'}), 400
        if per_page < 1:
            logger.warning(f"Invalid per_page value: {per_page}")
            return jsonify({'error': 'Per page must be positive'}), 400

        discounts, total = discount_manager.get_discounts(page, per_page)
        discounts_list = [
            {
                'id': discount.id,
                'code': discount.code,
                'description': discount.description,
                'discount_percent': discount.discount_percent,
                'max_uses': discount.max_uses,
                'expires_at': discount.expires_at.isoformat() if discount.expires_at else None,
                'is_active': bool(discount.is_active)
            } for discount in discounts
        ]
        logger.info(f"Retrieved {len(discounts_list)} discounts for page={page}, per_page={per_page}")
        return jsonify({
            'discounts': discounts_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving discounts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500