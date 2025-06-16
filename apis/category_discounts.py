from flask import Blueprint, request, jsonify
from database import CategoryDiscountManager
from .auth import admin_required
import logging
import iso8601
from datetime import datetime

category_discounts_bp = Blueprint('category_discounts', __name__)
category_discount_manager = CategoryDiscountManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _validate_discount_data(data, is_update=False):
    """Helper function to validate discount data for add and update operations."""
    category_id = data.get('category_id')
    discount_percent = data.get('discount_percent')
    starts_at_str = data.get('starts_at')
    ends_at_str = data.get('ends_at')
    
    # Required fields for creation
    if not is_update and (category_id is None or discount_percent is None):
        return None, (jsonify({'error': 'Category ID and discount percent are required'}), 400)

    # Validate category_id if present
    if category_id is not None and (not isinstance(category_id, int) or category_id <= 0):
        return None, (jsonify({'error': 'Category ID must be a positive integer'}), 400)
    
    # Validate discount_percent if present
    if discount_percent is not None and not (0 <= discount_percent <= 100):
        return None, (jsonify({'error': 'Discount percent must be between 0 and 100'}), 400)

    # Validate and parse dates
    try:
        starts_at_dt = iso8601.parse_date(starts_at_str) if starts_at_str else None
        ends_at_dt = iso8601.parse_date(ends_at_str) if ends_at_str else None
    except iso8601.ParseError as e:
        return None, (jsonify({'error': f'Invalid date format: {e}. Use ISO 8601 format.'}), 400)

    # Check date range consistency
    # This logic handles all cases: both dates present, only start, only end
    effective_start = starts_at_dt or (datetime.now(starts_at_dt.tzinfo) if starts_at_dt else None)
    if effective_start and ends_at_dt and effective_start > ends_at_dt:
        return None, (jsonify({'error': 'starts_at must be before ends_at'}), 400)
        
    return data, None


@category_discounts_bp.route('/category_discounts', methods=['POST'])
@admin_required
def add_category_discount():
    """API to add a new category discount."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    validated_data, error_response = _validate_discount_data(data)
    if error_response:
        return error_response

    try:
        discount_id = category_discount_manager.add_category_discount(
            category_id=validated_data['category_id'],
            discount_percent=validated_data['discount_percent'],
            starts_at=validated_data.get('starts_at'),
            ends_at=validated_data.get('ends_at'),
            is_active=validated_data.get('is_active', True)
        )
        if discount_id:
            logger.info(f"Category discount added successfully: discount_id={discount_id}")
            # Fetch and return the created object for better API design
            new_discount = category_discount_manager.get_category_discount_by_id(discount_id)
            return jsonify(new_discount), 201
        
        logger.error(f"Failed to add category discount for category_id={validated_data['category_id']}")
        return jsonify({'error': 'Failed to add category discount'}), 500
    except Exception as e:
        logger.error(f"Error adding category discount: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred'}), 500


@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_category_discount(discount_id):
    """API to update category discount details."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    validated_data, error_response = _validate_discount_data(data, is_update=True)
    if error_response:
        return error_response
    
    try:
        # Check if discount exists before updating
        if not category_discount_manager.get_category_discount_by_id(discount_id):
            return jsonify({'error': 'Category discount not found'}), 404

        success = category_discount_manager.update_category_discount(
            discount_id=discount_id,
            discount_percent=validated_data.get('discount_percent'),
            starts_at=validated_data.get('starts_at'),
            ends_at=validated_data.get('ends_at'),
            is_active=validated_data.get('is_active')
        )
        if success:
            logger.info(f"Category discount updated successfully: discount_id={discount_id}")
            updated_discount = category_discount_manager.get_category_discount_by_id(discount_id)
            return jsonify(updated_discount), 200
        
        # This case is less likely if the initial check passes, but good to have
        logger.warning(f"Update failed for unknown reason: discount_id={discount_id}")
        return jsonify({'error': 'Failed to update category discount'}), 400
    except Exception as e:
        logger.error(f"Error updating category discount {discount_id}: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred'}), 500

# The rest of your GET/DELETE endpoints are well-written and don't need major changes.
# I'll include them for completeness with minor cleanups.

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['GET'])
@admin_required # Keeping this as per original design
def get_category_discount_by_id(discount_id):
    """API to retrieve a category discount by ID."""
    try:
        discount = category_discount_manager.get_category_discount_by_id(discount_id)
        if discount:
            return jsonify(discount), 200
        return jsonify({'error': 'Category discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving discount {discount_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/category/<int:category_id>', methods=['GET'])
def get_category_discounts_by_category(category_id):
    """API to retrieve all discounts for a category."""
    try:
        discounts = category_discount_manager.get_category_discounts_by_category(category_id)
        return jsonify({'category_discounts': discounts}), 200
    except Exception as e:
        logger.error(f"Error retrieving discounts for category {category_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/valid/<int:category_id>', methods=['GET'])
def get_valid_category_discounts(category_id):
    """API to retrieve valid category discounts for a category."""
    try:
        discounts = category_discount_manager.get_valid_category_discounts(category_id)
        return jsonify({'category_discounts': discounts}), 200
    except Exception as e:
        logger.error(f"Error retrieving valid discounts for category {category_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['DELETE'])
@admin_required
def delete_category_discount(discount_id):
    """API to delete a category discount by ID."""
    try:
        success = category_discount_manager.delete_category_discount(discount_id)
        if success:
            logger.info(f"Category discount deleted successfully: discount_id={discount_id}")
            return jsonify({'message': 'Category discount deleted successfully'}), 200
        return jsonify({'error': 'Category discount not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting discount {discount_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts', methods=['GET'])
@admin_required
def get_category_discounts():
    """API to retrieve category discounts with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        discounts, total = category_discount_manager.get_category_discounts(page, per_page)
        return jsonify({
            'category_discounts': discounts,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving paginated discounts: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500