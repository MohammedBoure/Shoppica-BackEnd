from flask import Blueprint, request, jsonify
from database import ProductDiscountManager
import logging

product_discounts_bp = Blueprint('product_discounts', __name__)

# Initialize ProductDiscountManager
product_discount_manager = ProductDiscountManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@product_discounts_bp.route('/product_discounts', methods=['POST'])
def add_product_discount():
    """API to add a new product discount."""
    data = request.get_json()
    product_id = data.get('product_id')
    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active', 1)

    if not product_id or discount_percent is None:
        return jsonify({'error': 'Product ID and discount percent are required'}), 400

    discount_id = product_discount_manager.add_product_discount(product_id, discount_percent, starts_at, ends_at, is_active)
    if discount_id:
        return jsonify({'message': 'Product discount added successfully', 'discount_id': discount_id}), 201
    return jsonify({'error': 'Failed to add product discount'}), 500

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['GET'])
def get_product_discount_by_id(discount_id):
    """API to retrieve a product discount by ID."""
    discount = product_discount_manager.get_product_discount_by_id(discount_id)
    if discount:
        return jsonify({
            'id': discount['id'],
            'product_id': discount['product_id'],
            'discount_percent': discount['discount_percent'],
            'starts_at': discount['starts_at'],
            'ends_at': discount['ends_at'],
            'is_active': discount['is_active']
        }), 200
    return jsonify({'error': 'Product discount not found'}), 404

@product_discounts_bp.route('/product_discounts/product/<int:product_id>', methods=['GET'])
def get_product_discounts_by_product(product_id):
    """API to retrieve all discounts for a product."""
    discounts = product_discount_manager.get_product_discounts_by_product(product_id)
    if discounts:
        discounts_list = [
            {
                'id': discount['id'],
                'product_id': discount['product_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active']
            } for discount in discounts
        ]
        return jsonify({'product_discounts': discounts_list}), 200
    return jsonify({'product_discounts': [], 'message': 'No discounts found for this product'}), 200

@product_discounts_bp.route('/product_discounts/valid/<int:product_id>', methods=['GET'])
def get_valid_product_discounts(product_id):
    """API to retrieve valid product discounts for a product."""
    discounts = product_discount_manager.get_valid_product_discounts(product_id)
    if discounts:
        discounts_list = [
            {
                'id': discount['id'],
                'product_id': discount['product_id'],
                'discount_percent': discount['discount_percent'],
                'starts_at': discount['starts_at'],
                'ends_at': discount['ends_at'],
                'is_active': discount['is_active']
            } for discount in discounts
        ]
        return jsonify({'product_discounts': discounts_list}), 200
    return jsonify({'product_discounts': [], 'message': 'No valid discounts found for this product'}), 200

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['PUT'])
def update_product_discount(discount_id):
    """API to update product discount details."""
    data = request.get_json()
    discount_percent = data.get('discount_percent')
    starts_at = data.get('starts_at')
    ends_at = data.get('ends_at')
    is_active = data.get('is_active')

    success = product_discount_manager.update_product_discount(discount_id, discount_percent, starts_at, ends_at, is_active)
    if success:
        return jsonify({'message': 'Product discount updated successfully'}), 200
    return jsonify({'error': 'Failed to update product discount'}), 400

@product_discounts_bp.route('/product_discounts/<int:discount_id>', methods=['DELETE'])
def delete_product_discount(discount_id):
    """API to delete a product discount by ID."""
    success = product_discount_manager.delete_product_discount(discount_id)
    if success:
        return jsonify({'message': 'Product discount deleted successfully'}), 200
    return jsonify({'error': 'Product discount not found or failed to delete'}), 404

@product_discounts_bp.route('/product_discounts', methods=['GET'])
def get_product_discounts():
    """API to retrieve product discounts with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    discounts, total = product_discount_manager.get_product_discounts(page, per_page)
    discounts_list = [
        {
            'id': discount['id'],
            'product_id': discount['product_id'],
            'discount_percent': discount['discount_percent'],
            'starts_at': discount['starts_at'],
            'ends_at': discount['ends_at'],
            'is_active': discount['is_active'],
            'product_name': discount['name']
        } for discount in discounts
    ]
    return jsonify({
        'product_discounts': discounts_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200