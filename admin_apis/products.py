from flask import Blueprint, request, jsonify
from database import ProductManager
import logging

products_bp = Blueprint('products', __name__)

# Initialize ProductManager
product_manager = ProductManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@products_bp.route('/products', methods=['POST'])
def add_product():
    """API to add a new product."""
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock_quantity = data.get('stock_quantity')
    category_id = data.get('category_id')
    description = data.get('description')
    image_url = data.get('image_url')
    is_active = data.get('is_active', 1)

    if not name or price is None or stock_quantity is None:
        return jsonify({'error': 'Name, price, and stock quantity are required'}), 400

    product_id = product_manager.add_product(name, price, stock_quantity, category_id, description, image_url, is_active)
    if product_id:
        return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201
    return jsonify({'error': 'Failed to add product'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """API to retrieve a product by ID."""
    product = product_manager.get_product_by_id(product_id)
    if product:
        return jsonify({
            'id': product['id'],
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'stock_quantity': product['stock_quantity'],
            'category_id': product['category_id'],
            'image_url': product['image_url'],
            'is_active': product['is_active'],
            'created_at': product['created_at']
        }), 200
    return jsonify({'error': 'Product not found'}), 404

@products_bp.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """API to retrieve all products in a category."""
    products = product_manager.get_products_by_category(category_id)
    if products:
        products_list = [
            {
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'price': product['price'],
                'stock_quantity': product['stock_quantity'],
                'category_id': product['category_id'],
                'image_url': product['image_url'],
                'is_active': product['is_active'],
                'created_at': product['created_at']
            } for product in products
        ]
        return jsonify({'products': products_list}), 200
    return jsonify({'products': [], 'message': 'No products found for this category'}), 200

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """API to update product details."""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock_quantity = data.get('stock_quantity')
    category_id = data.get('category_id')
    image_url = data.get('image_url')
    is_active = data.get('is_active')

    success = product_manager.update_product(product_id, name, description, price, stock_quantity, category_id, image_url, is_active)
    if success:
        return jsonify({'message': 'Product updated successfully'}), 200
    return jsonify({'error': 'Failed to update product'}), 400

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """API to delete a product by ID."""
    success = product_manager.delete_product(product_id)
    if success:
        return jsonify({'message': 'Product deleted successfully'}), 200
    return jsonify({'error': 'Product not found or failed to delete'}), 404

@products_bp.route('/products', methods=['GET'])
def get_products():
    """API to retrieve products with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    products, total = product_manager.get_products(page, per_page)
    products_list = [
        {
            'id': product['id'],
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'stock_quantity': product['stock_quantity'],
            'category_id': product['category_id'],
            'image_url': product['image_url'],
            'is_active': product['is_active'],
            'created_at': product['created_at']
        } for product in products
    ]
    return jsonify({
        'products': products_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200