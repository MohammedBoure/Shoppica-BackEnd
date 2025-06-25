from flask import Blueprint, request, jsonify
from database import ProductDiscountManager
from .auth import admin_required
import logging
from datetime import datetime
import iso8601

product_discounts_bp = Blueprint('product_discounts', __name__)

# Initialize ProductDiscountManager
product_discount_manager = ProductDiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_datetime(dt):
    """Helper function to serialize datetime objects to ISO format."""
    return dt.isoformat() if isinstance(dt, datetime) else None

@product_discounts_bp.route('/product_discounts', methods=['POST'])
@admin_required
def add_product_discount():
    """API to add a new product discount."""
    try:
        data = request.get_json()
        if not data:
            logger.warning("Invalid JSON payload")
            return jsonify({'error': 'Invalid JSON payload'}), 400

        product_id = data.get('product_id')
        discount_percent = data.get('discount_percent')
        starts_at = data.get('starts_at')
        ends_at = data.get('ends_at')
        is_active = data.get('is_active', 1)

        if not product_id or discount_percent is None:
            logger.warning("Missing required fields: product_id or discount_percent")
            return jsonify({'error': 'Product ID and discount percent are required'}), 400

        if not isinstance(product_id, int) or product_id <= 0:
            logger.warning(f"Invalid product_id: {product_id}")
            return jsonify({'error': 'Product ID must be a positive integer'}), 400

        if not isinstance(discount_percent, (int, float)) or not (0 <= discount_percent <= 100):
            logger.warning(f"Invalid discount_percent: {discount_percent}")
            return jsonify({'error': 'Discount percent must be a number between 0 and 100'}), 400

        starts_at_dt = None
        if starts_at:
            try:
                starts_at_dt = iso8601.parse_date(starts_at).replace(tzinfo=None)
            except iso8601.ParseError:
                logger.warning(f"Invalid starts_at format: {starts_at}")
                return jsonify({'error': 'starts_at must be in ISO 8601 format'}), 400

        ends_at_dt = None
        if ends_at:
            try:
                ends_at_dt = iso8601.parse_date(ends_at).replace(tzinfo=None)
            except iso8601.ParseError:
                logger.warning(f"Invalid ends_at format: {ends_at}")
                return jsonify({'error': 'ends_at must be in ISO 8601 format'}), 400

        if starts_at_dt and ends_at_dt and starts_at_dt > ends_at_dt:
            logger.warning(f"Invalid date range: starts_at={starts_at} is after ends_at={ends_at}")
            return jsonify({'error': 'starts_at must be before ends_at'}), 400

        if not isinstance(is_active, int) or is_active not in (0, 1):
            logger.warning(f"Invalid activity status: {is_active}")
            return jsonify({'error': 'is_active must be 0 or 1'}), 400

        discount_id = product_discount_manager.add_product_discount(
            product_id, discount_percent, starts_at_dt, ends_at_dt, is_active
        )
        if discount_id:
            logger.info(f"Product discount added successfully: discount_id={discount_id}, product_id={product_id}")
            return jsonify({'message': 'Product discount added successfully', 'discount_id': discount_id}), 201
        logger.error(f"Failed to add product discount: product_id={product_id}")
        return jsonify({'error': 'Failed to add product discount'}), 500
    except Exception as e:
        logger.error(f"Error adding product discount: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['GET'])
@admin_required
def get_product_discount_by_id(discount_id):
    """API to retrieve a product discount by ID."""
    try:
        discount = product_discount_manager.get_product_discount_by_id(discount_id)
        if discount:
            logger.info(f"Retrieved product discount: discount_id={discount_id}")
            return jsonify({
                'id': discount.id,
                'product_id': discount.product_id,
                'discount_percent': discount.discount_percent,
                'starts_at': serialize_datetime(discount.starts_at),
                'ends_at': serialize_datetime(discount.ends_at),
                'is_active': discount.is_active
            }), 200
        logger.warning(f"Product discount not found: discount_id={discount_id}")
        return jsonify({'error': 'Product discount not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving product discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts/product/<int:product_id>', methods=['GET'])
def get_product_discounts_by_product(product_id):
    """API to retrieve all discounts for a product."""
    try:
        if not isinstance(product_id, int) or product_id <= 0:
            logger.warning(f"Invalid product_id: {product_id}")
            return jsonify({'error': 'Product ID must be a positive integer'}), 400

        discounts = product_discount_manager.get_product_discounts_by_product(product_id)
        discounts_list = [
            {
                'id': discount.id,
                'product_id': discount.product_id,
                'discount_percent': discount.discount_percent,
                'starts_at': serialize_datetime(discount.starts_at),
                'ends_at': serialize_datetime(discount.ends_at),
                'is_active': discount.is_active
            } for discount in discounts or []
        ]
        logger.info(f"Retrieved {len(discounts_list)} product discounts for product_id={product_id}")
        return jsonify({'product_discounts': discounts_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving product discounts for product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts/valid/<int:product_id>', methods=['GET'])
def get_valid_product_discounts(product_id):
    """API to retrieve valid product discounts for a product."""
    try:
        if not isinstance(product_id, int) or product_id <= 0:
            logger.warning(f"Invalid product_id: {product_id}")
            return jsonify({'error': 'Product ID must be a positive integer'}), 400

        discounts = product_discount_manager.get_valid_product_discounts(product_id)
        discounts_list = [
            {
                'id': discount.id,
                'product_id': discount.product_id,
                'discount_percent': discount.discount_percent,
                'starts_at': serialize_datetime(discount.starts_at),
                'ends_at': serialize_datetime(discount.ends_at),
                'is_active': discount.is_active
            } for discount in discounts or []
        ]
        logger.info(f"Retrieved {len(discounts_list)} valid product discounts for product_id={product_id}")
        return jsonify({'product_discounts': discounts_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving valid product discounts for product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['PUT'])
@admin_required
def update_product_discount(discount_id):
    """API to update product discount details."""
    try:
        data = request.get_json()
        if not data:
            logger.warning("Invalid JSON payload")
            return jsonify({'error': 'Invalid JSON payload'}), 400

        discount_percent = data.get('discount_percent')
        starts_at = data.get('starts_at')
        ends_at = data.get('ends_at')
        is_active = data.get('is_active')

        if discount_percent is not None:
            if not isinstance(discount_percent, (int, float)) or not (0 <= discount_percent <= 100):
                logger.warning(f"Invalid discount_percent: {discount_percent} for discount_id={discount_id}")
                return jsonify({'error': 'Discount percent must be a number between 0 and 100'}), 400

        starts_at_dt = None
        if starts_at:
            try:
                starts_at_dt = iso8601.parse_date(starts_at).replace(tzinfo=None)
            except iso8601.ParseError:
                logger.warning(f"Invalid starts_at format: {starts_at} for discount_id={discount_id}")
                return jsonify({'error': 'starts_at must be in ISO 8601 format'}), 400

        ends_at_dt = None
        if ends_at:
            try:
                ends_at_dt = iso8601.parse_date(ends_at).replace(tzinfo=None)
            except iso8601.ParseError:
                logger.warning(f"Invalid ends_at format: {ends_at} for discount_id={discount_id}")
                return jsonify({'error': 'ends_at must be in ISO 8601 format'}), 400

        if starts_at_dt and ends_at_dt and starts_at_dt > ends_at_dt:
            logger.warning(f"Invalid date range: starts_at={starts_at} is after ends_at={ends_at} for discount_id={discount_id}")
            return jsonify({'error': 'starts_at must be before ends_at'}), 400

        if is_active is not None and (not isinstance(is_active, int) or is_active not in (0, 1)):
            logger.warning(f"Invalid is_active: {is_active} for discount_id={discount_id}")
            return jsonify({'error': 'is_active must be 0 or 1'}), 400

        success = product_discount_manager.update_product_discount(
            discount_id, discount_percent, starts_at_dt, ends_at_dt, is_active
        )
        if success:
            logger.info(f"Product discount updated successfully: discount_id={discount_id}")
            return jsonify({'message': 'Product discount updated successfully'}), 200
        logger.warning(f"Product discount not found: discount_id={discount_id}")
        return jsonify({'error': 'Product discount not found'}), 404
    except Exception as e:
        logger.error(f"Error updating product discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['DELETE'])
@admin_required
def delete_product_discount(discount_id):
    """API to delete a product discount by ID."""
    try:
        success = product_discount_manager.delete_product_discount(discount_id)
        if success:
            logger.info(f"Product discount deleted successfully: discount_id={discount_id}")
            return jsonify({'message': 'Product discount deleted successfully'}), 200
        logger.warning(f"Product discount not found: discount_id={discount_id}")
        return jsonify({'error': 'Product discount not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting product discount {discount_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@product_discounts_bp.route('/product_discounts', methods=['GET'])
@admin_required
def get_product_discounts():
    """API to retrieve product discounts with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            logger.warning(f"Invalid pagination parameters: page={page}, per_page={per_page}")
            return jsonify({'error': 'Page and per_page must be positive integers'}), 400

        discounts, total = product_discount_manager.get_product_discounts(page, per_page)
        discounts_list = [
            {
                'id': discount.id,
                'product_id': discount.product_id,
                'discount_percent': discount.discount_percent,
                'starts_at': serialize_datetime(discount.starts_at),
                'ends_at': serialize_datetime(discount.ends_at),
                'is_active': discount.is_active,
                'product_name': product_name
            } for discount, product_name in discounts or []
        ]
        logger.info(f"Retrieved {len(discounts_list)} product discounts for page={page}, per_page={per_page}")
        return jsonify({
            'product_discounts': discounts_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving product discounts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500