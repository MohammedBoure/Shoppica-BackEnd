from flask import Blueprint, request, jsonify
from database import ProductManager, ProductImageManager
from .auth import admin_required
import logging
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

products_bp = Blueprint('products', __name__)

# Initialize managers
product_manager = ProductManager()
product_image_manager = ProductImageManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads/products'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(prefix, identifier, extension):
    """Generate a unique filename with prefix, ID, timestamp, and random string."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_string = str(uuid.uuid4())[:8]
    return f"{prefix}_{identifier}_{timestamp}_{random_string}.{extension}"

@products_bp.route('/products', methods=['POST'])
@admin_required
def add_product():
    """API to add a new product with optional image upload."""
    try:
        name = request.form.get('name')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        is_active = request.form.get('is_active', 1, type=int)
        image_url = None

        if not name or price is None or stock_quantity is None:
            logger.warning("Missing required fields: name, price, or stock_quantity")
            return jsonify({'error': 'Name, price, and stock quantity are required'}), 400

        try:
            price = float(price)
            stock_quantity = int(stock_quantity)
        except (ValueError, TypeError):
            logger.warning(f"Invalid input: price={price}, stock_quantity={stock_quantity}")
            return jsonify({'error': 'Price and stock quantity must be valid numbers'}), 400

        if price < 0 or stock_quantity < 0:
            logger.warning(f"Invalid input: price={price}, stock_quantity={stock_quantity}")
            return jsonify({'error': 'Price and stock quantity must be non-negative'}), 400

        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Generate temporary product ID for filename (will update after insertion)
                temp_id = str(uuid.uuid4())[:8]
                filename = generate_unique_filename('product', temp_id, file.filename.rsplit('.', 1)[1].lower())
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                image_url = f"uploads/products/{filename}"
                logger.info(f"Image uploaded: {image_url}")
            else:
                logger.warning("Invalid or missing image file")
                return jsonify({'error': 'Invalid or missing image file. Allowed extensions: jpg, jpeg, png, gif'}), 400

        product_id = product_manager.add_product(name, price, stock_quantity, category_id, description, image_url, is_active)
        if product_id:
            # Update filename with actual product ID
            if image_url:
                old_path = os.path.join(UPLOAD_FOLDER, filename)
                new_filename = generate_unique_filename('product', product_id, filename.rsplit('.', 1)[1])
                new_path = os.path.join(UPLOAD_FOLDER, new_filename)
                os.rename(old_path, new_path)
                image_url = f"uploads/products/{new_filename}"
                product_manager.update_product(product_id, image_url=image_url)
                logger.info(f"Image filename updated for product_id={product_id}: {image_url}")

            logger.info(f"Product added successfully: product_id={product_id}")
            return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201
        logger.error("Failed to add product")
        return jsonify({'error': 'Failed to add product'}), 500
    except Exception as e:
        logger.error(f"Error adding product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """API to retrieve a product by ID, including its images."""
    try:
        product = product_manager.get_product_by_id(product_id)
        if product and product['is_active'] == 1:
            images = product_image_manager.get_images_by_product(product_id)
            images_list = [
                {
                    'id': image['id'],
                    'image_url': image['image_url'],
                    'created_at': image['created_at']
                } for image in images
            ]
            logger.info(f"Retrieved product: product_id={product_id} with {len(images_list)} images")
            return jsonify({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'price': product['price'],
                'stock_quantity': product['stock_quantity'],
                'category_id': product['category_id'],
                'image_url': product['image_url'],
                'is_active': product['is_active'],
                'created_at': product['created_at'],
                'images': images_list
            }), 200
        logger.warning(f"Product not found or inactive: product_id={product_id}")
        return jsonify({'error': 'Product not found or inactive'}), 404
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """API to retrieve all products in a category, including their images."""
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
                'created_at': product['created_at'],
                'images': [
                    {
                        'id': image['id'],
                        'image_url': image['image_url'],
                        'created_at': image['created_at']
                    } for image in product_image_manager.get_images_by_product(product['id'])
                ]
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
    """API to update product details with optional image upload."""
    try:
        data = request.form
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock_quantity = data.get('stock_quantity')
        category_id = data.get('category_id')
        is_active = data.get('is_active')
        image_url = None

        if price is not None:
            try:
                price = float(price)
                if price < 0:
                    logger.warning(f"Invalid price: price={price} for product_id={product_id}")
                    return jsonify({'error': 'Price must be non-negative'}), 400
            except (ValueError, TypeError):
                logger.warning(f"Invalid price format: price={price} for product_id={product_id}")
                return jsonify({'error': 'Price must be a valid number'}), 400

        if stock_quantity is not None:
            try:
                stock_quantity = int(stock_quantity)
                if stock_quantity < 0:
                    logger.warning(f"Invalid stock_quantity: stock_quantity={stock_quantity} for product_id={product_id}")
                    return jsonify({'error': 'Stock quantity must be non-negative'}), 400
            except (ValueError, TypeError):
                logger.warning(f"Invalid stock_quantity format: stock_quantity={stock_quantity} for product_id={product_id}")
                return jsonify({'error': 'Stock quantity must be a valid integer'}), 400

        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = generate_unique_filename('product', product_id, file.filename.rsplit('.', 1)[1].lower())
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                image_url = f"uploads/products/{filename}"
                logger.info(f"Image uploaded for update: {image_url}")
            else:
                logger.warning("Invalid or missing image file")
                return jsonify({'error': 'Invalid or missing image file. Allowed extensions: jpg, jpeg, png, gif'}), 400

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
    """API to retrieve products with pagination, including their images."""
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
                'created_at': product['created_at'],
                'images': [
                    {
                        'id': image['id'],
                        'image_url': image['image_url'],
                        'created_at': image['created_at']
                    } for image in product_image_manager.get_images_by_product(product['id'])
                ]
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

@products_bp.route('/products/<int:product_id>/images', methods=['POST'])
@admin_required
def add_product_image(product_id):
    """API to add a new product image via file upload."""
    try:
        # Check if product exists and is active
        product = product_manager.get_product_by_id(product_id)
        if not product or product['is_active'] != 1:
            logger.warning(f"Product not found or inactive: product_id={product_id}")
            return jsonify({'error': 'Product not found or inactive'}), 404

        if 'image' not in request.files:
            logger.warning("Missing required field: image file")
            return jsonify({'error': 'Image file is required'}), 400

        file = request.files['image']
        if not allowed_file(file.filename):
            logger.warning("Invalid image file extension")
            return jsonify({'error': 'Invalid image file. Allowed extensions: jpg, jpeg, png, gif'}), 400

        # Add product image to database with temporary filename
        temp_filename = generate_unique_filename('image', str(uuid.uuid4())[:8], file.filename.rsplit('.', 1)[1].lower())
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        temp_image_url = f"/static/uploads/products/{temp_filename}"

        image_id = product_image_manager.add_product_image(product_id, temp_image_url)
        if image_id:
            # Update filename with actual image ID
            extension = temp_filename.rsplit('.', 1)[1]
            new_filename = generate_unique_filename('image', image_id, extension)
            new_path = os.path.join(UPLOAD_FOLDER, new_filename)
            os.rename(temp_path, new_path)
            image_url = f"/static/uploads/products/{new_filename}"
            product_image_manager.update_product_image(image_id, image_url)
            logger.info(f"Product image added successfully: image_id={image_id} for product_id={product_id}")
            return jsonify({'message': 'Product image added successfully', 'image_id': image_id}), 201
        
        logger.error(f"Failed to add product image for product_id={product_id}")
        return jsonify({'error': 'Failed to add product image'}), 500
    except Exception as e:
        logger.error(f"Error adding product image for product_id={product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['GET'])
def get_product_image_by_id(image_id):
    """API to retrieve a product image by ID."""
    try:
        image = product_image_manager.get_product_image_by_id(image_id)
        if image:
            logger.info(f"Retrieved product image: image_id={image_id}")
            return jsonify({
                'id': image['id'],
                'product_id': image['product_id'],
                'image_url': image['image_url'],
                'created_at': image['created_at']
            }), 200
        logger.warning(f"Product image not found: image_id={image_id}")
        return jsonify({'error': 'Product image not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving product image {image_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/products/<int:product_id>/images', methods=['GET'])
def get_images_by_product(product_id):
    """API to retrieve all images for a specific product."""
    try:
        images = product_image_manager.get_images_by_product(product_id)
        images_list = [
            {
                'id': image['id'],
                'product_id': image['product_id'],
                'image_url': image['image_url'],
                'created_at': image['created_at']
            } for image in images
        ]
        logger.info(f"Retrieved {len(images_list)} images for product_id={product_id}")
        return jsonify({'images': images_list}), 200
    except Exception as e:
        logger.error(f"Error retrieving images for product_id={product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['PUT'])
@admin_required
def update_product_image(image_id):
    """API to update a product image's URL via file upload."""
    try:
        # Check if image exists
        existing_image = product_image_manager.get_product_image_by_id(image_id)
        if not existing_image:
            logger.warning(f"Product image not found: image_id={image_id}")
            return jsonify({'error': 'Product image not found'}), 404

        if 'image' not in request.files:
            logger.warning(f"No image file provided for image_id={image_id}")
            return jsonify({'error': 'Image file is required'}), 400

        file = request.files['image']
        if not allowed_file(file.filename):
            logger.warning("Invalid image file extension")
            return jsonify({'error': 'Invalid image file. Allowed extensions: jpg, jpeg, png, gif'}), 400

        # Delete old image file if it exists
        old_image_url = existing_image['image_url']
        if old_image_url and os.path.exists(os.path.join('static', old_image_url.lstrip('/static/'))):
            try:
                os.remove(os.path.join('static', old_image_url.lstrip('/static/')))
                logger.info(f"Deleted old image file: {old_image_url}")
            except Exception as e:
                logger.warning(f"Failed to delete old image file {old_image_url}: {str(e)}")

        # Save new image
        filename = generate_unique_filename('image', image_id, file.filename.rsplit('.', 1)[1].lower())
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        image_url = f"/static/uploads/products/{filename}"

        success = product_image_manager.update_product_image(image_id, image_url)
        if success:
            logger.info(f"Product image updated successfully: image_id={image_id}")
            return jsonify({'message': 'Product image updated successfully'}), 200
        
        logger.warning(f"Failed to update product image: image_id={image_id}")
        return jsonify({'error': 'Failed to update product image'}), 400
    except Exception as e:
        logger.error(f"Error updating product image {image_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['DELETE'])
@admin_required
def delete_product_image(image_id):
    """API to delete a product image by ID."""
    try:
        success = product_image_manager.delete_product_image(image_id)
        if success:
            logger.info(f"Product image deleted successfully: image_id={image_id}")
            return jsonify({'message': 'Product image deleted successfully'}), 200
        logger.warning(f"Product image not found or failed to delete: image_id={image_id}")
        return jsonify({'error': 'Product image not found or failed to delete'}), 404
    except Exception as e:
        logger.error(f"Error deleting product image {image_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/product_images', methods=['GET'])
def get_product_images():
    """API to retrieve product images with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        images, total = product_image_manager.get_product_images(page, per_page)
        images_list = [
            {
                'id': image['id'],
                'product_id': image['product_id'],
                'image_url': image['image_url'],
                'created_at': image['created_at']
            } for image in images
        ]
        logger.info(f"Retrieved {len(images_list)} product images for page={page}, per_page={per_page}")
        return jsonify({
            'images': images_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving product images: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500