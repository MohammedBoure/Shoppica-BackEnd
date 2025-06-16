from flask import Blueprint, request, jsonify
from database import ProductManager
from .auth import admin_required
import logging

products_bp = Blueprint('products', __name__)

# Initialize ProductManager
product_manager = ProductManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@products_bp.route('/products', methods=['POST'])
@admin_required
def add_product():
    """API to add a new product."""
    try:
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        stock_quantity = data.get('stock_quantity')
        category_id = data.get('category_id')
        description = data.get('description')
        image_url = data.get('image_url')
        is_active = data.get('is_active', 1)

        if not name or price is None or stock_quantity is None:
            logger.warning("Missing required fields: name, price, or stock_quantity")
            return jsonify({'error': 'Name, price, and stock quantity are required'}), 400

        if price < 0 or stock_quantity < 0:
            logger.warning(f"Invalid input: price={price}, stock_quantity={stock_quantity}")
            return jsonify({'error': 'Price and stock quantity must be non-negative'}), 400

        product_id = product_manager.add_product(name, price, stock_quantity, category_id, description, image_url, is_active)
        if product_id:
            logger.info(f"Product added successfully: product_id={product_id}")
            return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201
        logger.error("Failed to add product")
        return jsonify({'error': 'Failed to add product'}), 500
    except Exception as e:
        logger.error(f"Error adding product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """API to retrieve a product by ID."""
    try:
        product = product_manager.get_product_by_id(product_id)
        if product and product['is_active'] == 1:
            logger.info(f"Retrieved product: product_id={product_id}")
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
        logger.warning(f"Product not found or inactive: product_id={product_id}")
        return jsonify({'error': 'Product not found or inactive'}), 404
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """API to retrieve all products in a category."""
    try:
        products = product_manager.get_products_by_category(category_id)
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
            } for product in products if product['is_active'] == 1
        ]
        logger.info(f"Retrieved {len(products_list)} products for category_id={category_id}")
        return jsonify({'products': products_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving products for category {category_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """API to update product details."""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock_quantity = data.get('stock_quantity')
        category_id = data.get('category_id')
        image_url = data.get('image_url')
        is_active = data.get('is_active')

        if price is not None and price < 0:
            logger.warning(f"Invalid price: price={price} for product_id={product_id}")
            return jsonify({'error': 'Price must be non-negative'}), 400
        if stock_quantity is not None and stock_quantity < 0:
            logger.warning(f"Invalid stock_quantity: stock_quantity={stock_quantity} for product_id={product_id}")
            return jsonify({'error': 'Stock quantity must be non-negative'}), 400

        success = product_manager.update_product(product_id, name, description, price, stock_quantity, category_id, image_url, is_active)
        if success:
            logger.info(f"Product updated successfully: product_id={product_id}")
            return jsonify({'message': 'Product updated successfully'}), 200
        logger.warning(f"Failed to update product: product_id={product_id}")
        return jsonify({'error': 'Failed to update product'}), 400
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """API to delete a product by ID."""
    try:
        success = product_manager.delete_product(product_id)
        if success:
            logger.info(f"Product deleted successfully: product_id={product_id}")
            return jsonify({'message': 'Product deleted successfully'}), 200
        logger.warning(f"Product not found or failed to delete: product_id={product_id}")
        return jsonify({'error': 'Product not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products', methods=['GET'])
def get_products():
    """API to retrieve products with pagination."""
    try:
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
            } for product in products if product['is_active'] == 1
        ]
        logger.info(f"Retrieved {len(products_list)} products for page={page}, per_page={per_page}")
        return jsonify({
            'products': products_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500