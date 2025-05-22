from flask import Blueprint, request, jsonify
from database import CategoryDiscountManager
import logging

category_discounts_bp = Blueprint('category_discounts', __name__)

# Initialize CategoryDiscountManager
category_discount_manager = CategoryDiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@category_discounts_bp.route('/category_discounts', methods=['POST'])
def add_category_discount():
    """API to add a new category discount."""
    data = request.get_json()
    category_id = data.get('category_id')
    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active', 1)

    if not category_id or discount_percent is None:
        return jsonify({'error': 'Category ID and discount percent are required'}), 400

    discount_id = category_discount_manager.add_category_discount(category_id, discount_percent, starts_at, ends_at, is_active)
    if discount_id:
        return jsonify({'message': 'Category discount added successfully', 'discount_id': discount_id}), 201
    return jsonify({'error': 'Failed to add category discount'}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['GET'])
def get_category_discount_by_id(discount_id):
    """API to retrieve a category discount by ID."""
    discount = category_discount_manager.get_category_discount_by_id(discount_id)
    if discount:
        return jsonify({
            'id': discount['id'],
            'category_id': discount['category_id'],
            'discount_percent': discount['discount_percent'],
            'starts_at': discount['starts_at'],
            'ends_at': discount['ends_at'],
            'is_active': discount['is_active']
        }), 200
    return jsonify({'error': 'Category discount not found'}), 404

@category_discounts_bp.route('/category_discounts/category/<int:category_id>', methods=['GET'])
def get_category_discounts_by_category(category_id):
    """API to retrieve all discounts for a category."""
    discounts = category_discount_manager.get_category_discounts_by_category(category_id)
    if discounts:
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
        return jsonify({'category_discounts': discounts_list}), 200
    return jsonify({'category_discounts': [], 'message': 'No discounts found for this category'}), 200

@category_discounts_bp.route('/category_discounts/valid/<int:category_id>', methods=['GET'])
def get_valid_category_discounts(category_id):
    """API to retrieve valid category discounts for a category."""
    discounts = category_discount_manager.get_valid_category_discounts(category_id)
    if discounts:
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
        return jsonify({'category_discounts': discounts_list}), 200
    return jsonify({'category_discounts': [], 'message': 'No valid discounts found for this category'}), 200

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['PUT'])
def update_category_discount(discount_id):
    """API to update category discount details."""
    data = request.get_json()
    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active')

    success = category_discount_manager.update_category_discount(discount_id, discount_percent, starts_at, ends_at, is_active)
    if success:
        return jsonify({'message': 'Category discount updated successfully'}), 200
    return jsonify({'error': 'Failed to update category discount'}), 400

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['DELETE'])
def delete_category_discount(discount_id):
    """API to delete a category discount by ID."""
    success = category_discount_manager.delete_category_discount(discount_id)
    if success:
        return jsonify({'message': 'Category discount deleted successfully'}), 200
    return jsonify({'error': 'Category discount not found or failed to delete'}), 404

@category_discounts_bp.route('/category_discounts', methods=['GET'])
def get_category_discounts():
    """API to retrieve category discounts with pagination."""
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
    return jsonify({
        'category_discounts': discounts_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200