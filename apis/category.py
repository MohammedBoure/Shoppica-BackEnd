from flask import Blueprint, request, jsonify
from database import CategoryManager
from .auth import admin_required
import logging

# Corrected Blueprint definition to use __name__
categories_bp = Blueprint('categories', __name__)

# Initialize CategoryManager
category_manager = CategoryManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@categories_bp.route('/categories', methods=['POST'])
@admin_required
def add_category():
    """API to add a new category."""
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    category_id = category_manager.add_category(name, parent_id)
    if category_id:
        return jsonify({'message': 'Category added successfully', 'category_id': category_id}), 201
    return jsonify({'error': 'Failed to add category'}), 500

# Corrected route syntax for URL variables
@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    """API to retrieve a category by ID."""
    category = category_manager.get_category_by_id(category_id)
    if category:
        return jsonify({
            'id': category['id'],
            'name': category['name'],
            'parent_id': category['parent_id']
        }), 200
    return jsonify({'error': 'Category not found'}), 404

@categories_bp.route('/categories/parent', methods=['GET'])
def get_categories_by_parent():
    """API to retrieve categories by parent ID (or top-level if parent_id is not provided)."""
    parent_id = request.args.get('parent_id', type=int)
    categories = category_manager.get_categories_by_parent(parent_id)
    if categories:
        categories_list = [
            {
                'id': category['id'],
                'name': category['name'],
                'parent_id': category['parent_id']
            } for category in categories
        ]
        return jsonify({'categories': categories_list}), 200
    return jsonify({'categories': [], 'message': 'No categories found for this parent'}), 200

# Corrected route syntax
@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """API to update category details."""
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')

    success = category_manager.update_category(category_id, name, parent_id)
    if success:
        return jsonify({'message': 'Category updated successfully'}), 200
    return jsonify({'error': 'Failed to update category'}), 400

# Corrected route syntax
@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """API to delete a category by ID."""
    success = category_manager.delete_category(category_id)
    if success:
        return jsonify({'message': 'Category deleted successfully'}), 200
    return jsonify({'error': 'Category not found or failed to delete'}), 404

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """API to retrieve categories with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    categories, total = category_manager.get_categories(page, per_page)
    
    categories_list = [
        {
            'id': category['id'],
            'name': category['name'],
            'parent_id': category['parent_id']
        } for category in categories
    ]
    
    return jsonify({
        'categories': categories_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200