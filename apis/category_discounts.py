from flask import Blueprint, request, jsonify, session
from database import CategoryDiscountManager
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db = CategoryDiscountManager()
category_discounts_bp = Blueprint('category_discounts', __name__)

def require_admin():
    """Check if the user is an admin based on session."""
    if not session.get('is_admin'):
        logger.warning("Unauthorized access attempt to admin route")
        return jsonify({'error': 'Unauthorized', 'message': 'Admin access required'}), 403
    return None

def parse_date(date_str):
    """Parse ISO 8601 date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else None
    except ValueError:
        raise ValueError("Invalid date format. Use ISO 8601 format (e.g., '2025-06-25T12:00:00Z')")

@category_discounts_bp.route('/category_discounts', methods=['POST'])
def add_category_discount():
    """Add a new category discount."""
    response = require_admin()
    if response:
        return response

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'Request body must be JSON'}), 400

    category_id = data.get('category_id')
    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active', 1)

    # Validate required fields
    if not category_id or discount_percent is None:
        return jsonify({'error': 'Bad Request', 'message': 'category_id and discount_percent are required'}), 400
    if not isinstance(discount_percent, (int, float)) or discount_percent <= 0:
        return jsonify({'error': 'Bad Request', 'message': 'discount_percent must be a positive number'}), 400

    try:
        # Parse dates if provided
        starts_at = parse_date(starts_at)
        ends_at = parse_date(ends_at)

        discount_id = db.add_category_discount(
            category_id=category_id,
            discount_percent=discount_percent,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active
        )
        if discount_id is None:
            return jsonify({'error': 'Internal Server Error', 'message': 'Failed to add category discount'}), 500

        new_discount = db.get_category_discount_by_id(discount_id)
        logger.info(f"Category discount added: ID {discount_id}")
        return jsonify({
            'message': 'Category discount added successfully',
            'discount': new_discount
        }), 201
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error adding category discount: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['GET'])
def get_category_discount(discount_id):
    """Retrieve a category discount by ID."""
    try:
        discount = db.get_category_discount_by_id(discount_id)
        if discount:
            return jsonify({'discount': discount}), 200
        logger.warning(f"Category discount not found: ID {discount_id}")
        return jsonify({'error': 'Not Found', 'message': 'Category discount not found'}), 404
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving discount {discount_id}: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts', methods=['GET'])
def get_category_discounts():
    """Retrieve category discounts with pagination."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        if page < 1 or per_page < 1:
            return jsonify({'error': 'Bad Request', 'message': 'Page and per_page must be positive'}), 400

        discounts, total = db.get_category_discounts(page, per_page)
        logger.info(f"Retrieved {len(discounts)} category discounts, total: {total}")
        return jsonify({
            'category_discounts': discounts,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except ValueError:
        return jsonify({'error': 'Bad Request', 'message': 'Invalid page or per_page value'}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving category discounts: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts/valid/<int:category_id>', methods=['GET'])
def get_valid_category_discounts(category_id):
    """Retrieve valid category discounts for a category."""
    try:
        discounts = db.get_valid_category_discounts(category_id)
        logger.info(f"Retrieved {len(discounts)} valid discounts for category {category_id}")
        return jsonify({
            'category_discounts': discounts,
            'category_id': category_id
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving valid discounts for category {category_id}: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts/category/<int:category_id>', methods=['GET'])
def get_category_discounts_by_category(category_id):
    """Retrieve all discounts for a category."""
    try:
        discounts = db.get_category_discounts_by_category(category_id)
        logger.info(f"Retrieved {len(discounts)} discounts for category {category_id}")
        return jsonify({
            'category_discounts': discounts,
            'category_id': category_id
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving discounts for category {category_id}: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['PUT'])
def update_category_discount(discount_id):
    """Update a category discount."""
    response = require_admin()
    if response:
        return response

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Bad Request', 'message': 'Request body must be JSON'}), 400

    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active')

    # Validate discount_percent if provided
    if discount_percent is not None:
        if not isinstance(discount_percent, (int, float)) or discount_percent <= 0:
            return jsonify({'error': 'Bad Request', 'message': 'discount_percent must be a positive number'}), 400

    try:
        # Parse dates if provided
        starts_at = parse_date(starts_at) if starts_at else None
        ends_at = parse_date(ends_at) if ends_at else None

        updated = db.update_category_discount(
            discount_id=discount_id,
            discount_percent=discount_percent,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active
        )
        if updated:
            updated_discount = db.get_category_discount_by_id(discount_id)
            logger.info(f"Category discount updated: ID {discount_id}")
            return jsonify({
                'message': 'Category discount updated successfully',
                'discount': updated_discount
            }), 200
        logger.warning(f"Category discount not found: ID {discount_id}")
        return jsonify({'error': 'Not Found', 'message': 'Category discount not found'}), 404
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': 'Bad Request', 'message': str(e)}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error updating discount {discount_id}: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['DELETE'])
def delete_category_discount(discount_id):
    """Delete a category discount."""
    response = require_admin()
    if response:
        return response

    try:
        deleted = db.delete_category_discount(discount_id)
        if deleted:
            logger.info(f"Category discount deleted: ID {discount_id}")
            return jsonify({'message': 'Category discount deleted successfully'}), 200
        logger.warning(f"Category discount not found: ID {discount_id}")
        return jsonify({'error': 'Not Found', 'message': 'Category discount not found'}), 404
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting discount {discount_id}: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': 'Database error'}), 500