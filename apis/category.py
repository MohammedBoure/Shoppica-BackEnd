from flask import Blueprint, request, jsonify, current_app
from database import CategoryManager
from .auth import admin_required
import logging
import os
import uuid
from werkzeug.utils import secure_filename

# Configure logging (only if not already configured to avoid conflicts)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Blueprint definition
categories_bp = Blueprint('categories', __name__)

# Initialize CategoryManager
category_manager = CategoryManager()

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """Save the uploaded image and return its relative URL."""
    if not file or not allowed_file(file.filename):
        return None
    # Ensure the upload directory exists
    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'categories')
    os.makedirs(upload_folder, exist_ok=True)
    # Generate a unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    # Return the relative URL
    return f"/static/uploads/categories/{filename}"

@categories_bp.route('/categories', methods=['POST'])
@admin_required
def add_category():
    """API to add a new category with optional image upload."""
    name = request.form.get('name')
    parent_id = request.form.get('parent_id', type=int)
    image_url = request.form.get('image_url', '')  # Fallback to provided URL
    image_file = request.files.get('image')

    if not name:
        logging.error("Category name is required")
        return jsonify({'error': 'Category name is required'}), 400

    # Handle image upload
    if image_file and allowed_file(image_file.filename):
        image_url = save_image(image_file)
        if not image_url:
            logging.error("Invalid image file provided")
            return jsonify({'error': 'Invalid image file'}), 400

    category_id = category_manager.add_category(name, parent_id, image_url)
    if category_id:
        logging.info(f"Category {name} added via API with ID: {category_id}")
        return jsonify({'message': 'Category added successfully', 'category_id': category_id}), 201
    logging.error(f"Failed to add category {name}")
    return jsonify({'error': 'Failed to add category'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    """API to retrieve a category by ID."""
    category = category_manager.get_category_by_id(category_id)
    if category:
        return jsonify({
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent_id,
            'image_url': category.image_url
        }), 200
    logging.warning(f"Category not found with ID: {category_id}")
    return jsonify({'error': 'Category not found'}), 404

@categories_bp.route('/categories/parent', methods=['GET'])
def get_categories_by_parent():
    """API to retrieve categories by parent ID (or top-level if parent_id is not provided)."""
    parent_id = request.args.get('parent_id', type=int)
    categories = category_manager.get_categories_by_parent(parent_id)
    categories_list = [
        {
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent_id,
            'image_url': category.image_url
        } for category in categories
    ]
    logging.info(f"Retrieved {len(categories_list)} categories for parent_id: {parent_id}")
    return jsonify({
        'categories': categories_list,
        'message': 'No categories found for this parent' if not categories_list else 'Categories retrieved successfully'
    }), 200

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """API to update category details with optional image upload."""
    name = request.form.get('name')
    parent_id = request.form.get('parent_id', type=int)
    image_url = request.form.get('image_url')
    image_file = request.files.get('image')

    if not any([name, parent_id is not None, image_url, image_file]):
        logging.error(f"No valid fields provided for updating category ID: {category_id}")
        return jsonify({'error': 'At least one field (name, parent_id, image_url, or image) must be provided'}), 400

    # Handle image upload
    if image_file and allowed_file(image_file.filename):
        image_url = save_image(image_file)
        if not image_url:
            logging.error("Invalid image file provided")
            return jsonify({'error': 'Invalid image file'}), 400

    success = category_manager.update_category(category_id, name, parent_id, image_url)
    if success:
        logging.info(f"Category {category_id} updated via API")
        return jsonify({'message': 'Category updated successfully'}), 200
    logging.warning(f"Failed to update category {category_id}")
    return jsonify({'error': 'Category not found or failed to update'}), 404

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """API to delete a category by ID."""
    success = category_manager.delete_category(category_id)
    if success:
        logging.info(f"Category {category_id} deleted via API")
        return jsonify({'message': 'Category deleted successfully'}), 200
    logging.warning(f"Failed to delete category {category_id}")
    return jsonify({'error': 'Category not found or failed to delete'}), 404

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """API to retrieve categories with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    categories, total = category_manager.get_categories(page, per_page)
    
    categories_list = [
        {
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent_id,
            'image_url': category.image_url
        } for category in categories
    ]
    
    logging.info(f"Retrieved {len(categories_list)} categories for page {page}")
    return jsonify({
        'categories': categories_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@categories_bp.route('/categories/search', methods=['GET'])
def search_categories():
    """API to search categories by name with pagination."""
    search_term = request.args.get('search_term', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if not search_term:
        logging.error("Search term is required for category search")
        return jsonify({'error': 'Search term is required'}), 400

    categories, total = category_manager.search_categories(search_term, page, per_page)
    categories_list = [
        {
            'id': category.id,
            'name': category.name,
            'parent_id': category.parent_id,
            'image_url': category.image_url
        } for category in categories
    ]
    
    logging.info(f"Retrieved {len(categories_list)} categories for search term '{search_term}'")
    return jsonify({
        'categories': categories_list,
        'total': total,
        'page': page,
        'per_page': per_page,
        'message': 'No categories found for this search term' if not categories_list else 'Categories retrieved successfully'
    }), 200