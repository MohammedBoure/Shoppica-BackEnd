from flask import Blueprint, request, jsonify
from database import CategoryDiscountManager
from flask_jwt_extended import jwt_required, get_jwt
from .auth import admin_required
import logging
import iso8601

category_discounts_bp = Blueprint('category_discounts', __name__)

# Initialize CategoryDiscountManager
category_discount_manager = CategoryDiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@category_discounts_bp.route('/category_discounts', methods=['POST'])
@admin_required
def add_category_discount():
    """API to add a new category discount."""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        discount_percent = data.get('discount_percent')
        starts_at = data.get('starts_at')
        ends_at = data.get('ends_at')
        is_active = data.get('is_active', 1)

        if not category_id or discount_percent is None:
            logger.warning("Missing required fields: category_id or discount_percent")
            return jsonify({'error': 'Category ID and discount percent are required'}), 400

        if not isinstance(category_id, int) or category_id <= 0:
            logger.warning(f"Invalid category_id: {category_id}")
            return jsonify({'error': 'Category ID must be a positive integer'}), 400

        if not (0 <= discount_percent <= 100):
            logger.warning(f"Invalid discount_percent: {discount_percent}")
            return jsonify({'error': 'Discount percent must be between 0 and 100'}), 400

        if starts_at:
            if not isinstance(starts_at, str):
                logger.warning(f"starts_at is not a string: {starts_at}")
                return jsonify({'error': 'starts_at must be a string in ISO 8601 format'}), 400
            try:
                iso8601.parse_date(starts_at)
            except iso8601.ParseError:
                logger.warning(f"Invalid starts_at format: {starts_at}")
                return jsonify({'error': 'starts_at must be in ISO 8601 format'}), 400


        if ends_at:
            if not isinstance(ends_at, str):
                logger.warning(f"ends_at is not a string: {ends_at}")
                return jsonify({'error': 'ends_at must be a string in ISO 8601 format'}), 400
            try:
                iso8601.parse_date(ends_at)
            except iso8601.ParseError:
                logger.warning(f"Invalid ends_at format: {ends_at}")
                return jsonify({'error': 'ends_at must be in ISO 8601 format'}), 400

        if starts_at and ends_at:
            start_date = iso8601.parse_date(starts_at)
            end_date = iso8601.parse_date(ends_at)
            if start_date > end_date:
                logger.warning(f"Invalid date range: starts_at={starts_at} is after ends_at={ends_at}")
                return jsonify({'error': 'starts_at must be before ends_at'}), 400

        discount_id = category_discount_manager.add_category_discount(category_id, discount_percent, starts_at, ends_at, is_active)
        if discount_id:
            logger.info(f"Category discount added successfully: discount_id={discount_id}, category_id={category_id}")
            return jsonify({'message': 'Category discount added successfully', 'discount_id': discount_id}), 201
        logger.error(f"Failed to add category discount: category_id={category_id}")
        return jsonify({'error': 'Failed to add category discount'}), 500
    except Exception as e:
        logger.error(f"Error adding category discount: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['GET'])
@admin_required
def get_category_discount_by_id(discount_id):
    """API to retrieve a category discount by ID."""
    try:
        discount = category_discount_manager.get_category_discount_by_id(discount_id)
        if discount:
            logger.info(f"Retrieved category discount: discount_id={discount_id}")
            return jsonify({
                'id': discount['id'],
                'category_id': discount['category_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active']
            }), 200
        logger.warning(f"Category discount not found: discount_id={discount_id}")
        return jsonify({'error': 'Category discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving category discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/category/<int:category_id>', methods=['GET'])
def get_category_discounts_by_category(category_id):
    """API to retrieve all discounts for a category."""
    try:
        if not isinstance(category_id, int) or category_id <= 0:
            logger.warning(f"Invalid category_id: {category_id}")
            return jsonify({'error': 'Category ID must be a positive integer'}), 400

        discounts = category_discount_manager.get_category_discounts_by_category(category_id)
        discounts_list = [
            {
                'id': discount['id'],
                'category_id': discount['category_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active']
            } for discount in discounts
        ]
        logger.info(f"Retrieved {len(discounts_list)} category discounts for category_id={category_id}")
        return jsonify({'category_discounts': discounts_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving category discounts for category {category_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/valid/<int:category_id>', methods=['GET'])
def get_valid_category_discounts(category_id):
    """API to retrieve valid category discounts for a category."""
    try:
        if not isinstance(category_id, int) or category_id <= 0:
            logger.warning(f"Invalid category_id: {category_id}")
            return jsonify({'error': 'Category ID must be a positive integer'}), 400

        discounts = category_discount_manager.get_valid_category_discounts(category_id)
        discounts_list = [
            {
                'id': discount['id'],
                'category_id': discount['category_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active']
            } for discount in discounts
        ]
        logger.info(f"Retrieved {len(discounts_list)} valid category discounts for category_id={category_id}")
        return jsonify({'category_discounts': discounts_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving valid category discounts for category {category_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_category_discount(discount_id):
    """API to update category discount details."""
    try:
        data = request.get_json()
        discount_percent = data.get('discount_percent')
        starts_at = data.get('starts_at')
        ends_at = data.get('ends_at')
        is_active = data.get('is_active')

        if discount_percent is not None and not (0 <= discount_percent <= 100):
            logger.warning(f"Invalid discount_percent: {discount_percent} for discount_id={discount_id}")
            return jsonify({'error': 'Discount percent must be between 0 and 100'}), 400

        if starts_at:
            try:
                iso8601.parse_date(starts_at)
            except iso8601.ParseError:
                logger.warning(f"Invalid starts_at format: {starts_at} for discount_id={discount_id}")
                return jsonify({'error': 'starts_at must be in ISO 8601 format'}), 400

        if ends_at:
            try:
                iso8601.parse_date(ends_at)
            except iso8601.ParseError:
                logger.warning(f"Invalid ends_at format: {ends_at} for discount_id={discount_id}")
                return jsonify({'error': 'ends_at must be in ISO 8601 format'}), 400

        if starts_at and ends_at:
            start_date = iso8601.parse_date(starts_at)
            end_date = iso8601.parse_date(ends_at)
            if start_date > end_date:
                logger.warning(f"Invalid date range: starts_at={starts_at} is after ends_at={ends_at} for discount_id={discount_id}")
                return jsonify({'error': 'starts_at must be before ends_at'}), 400

        success = category_discount_manager.update_category_discount(discount_id, discount_percent, starts_at, ends_at, is_active)
        if success:
            logger.info(f"Category discount updated successfully: discount_id={discount_id}")
            return jsonify({'message': 'Category discount updated successfully'}), 200
        logger.warning(f"Failed to update category discount: discount_id={discount_id}")
        return jsonify({'error': 'Failed to update category discount'}), 400
    except Exception as e:
        logger.error(f"Error updating category discount {discount_id}: {str(e)}")
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
        logger.warning(f"Category discount not found or failed to delete: discount_id={discount_id}")
        return jsonify({'error': 'Category discount not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting category discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@category_discounts_bp.route('/category_discounts', methods=['GET'])
@admin_required
def get_category_discounts():
    """API to retrieve category discounts with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        discounts, total = category_discount_manager.get_category_discounts(page, per_page)
        discounts_list = [
            {
                'id': discount['id'],
                'category_id': discount['category_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active'],
                'category_name': discount['name']
            } for discount in discounts
        ]
        logger.info(f"Retrieved {len(discounts_list)} category discounts for page={page}, per_page={per_page}")
        return jsonify({
            'category_discounts': discounts_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving category discounts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500