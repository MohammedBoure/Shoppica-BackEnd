from flask import Blueprint, request, jsonify, current_app
from database.product import ProductManager, ProductImageManager, Product, ProductImage
from database.category import Category
from .auth import admin_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import logging
import os

# Blueprint definition
products_bp = Blueprint('products', __name__)

# Initialize managers
product_manager = ProductManager()
product_image_manager = ProductImageManager()

# Configure logging (assuming it's centralized at the application level)
logger = logging.getLogger(__name__)

@products_bp.route('/products', methods=['POST'])
@admin_required
def add_product():
    """API to add a new product with optional image upload."""
    try:
        with next(product_manager.get_db_session()) as session:
            name = request.form.get('name')
            price = request.form.get('price')
            stock_quantity = request.form.get('stock_quantity')
            category_id = request.form.get('category_id', type=int)
            description = request.form.get('description')
            is_active = request.form.get('is_active', 1, type=int)
            image_file = request.files.get('image')

            # Validate required fields
            if not name or price is None or stock_quantity is None:
                logger.warning("Missing required fields: name, price, or stock_quantity")
                return jsonify({'error': 'Name, price, and stock quantity are required', 'error_code': 'INVALID_INPUT'}), 400

            # Validate price and stock_quantity
            try:
                price = float(price)
                stock_quantity = int(stock_quantity)
            except (ValueError, TypeError):
                logger.warning(f"Invalid input: price={price}, stock_quantity={stock_quantity}")
                return jsonify({'error': 'Price must be a number and stock quantity must be an integer', 'error_code': 'INVALID_TYPE'}), 400

            if price < 0 or stock_quantity < 0:
                logger.warning(f"Invalid input: price={price}, stock_quantity={stock_quantity}")
                return jsonify({'error': 'Price and stock quantity must be non-negative', 'error_code': 'INVALID_VALUE'}), 400

            # Validate is_active
            if is_active not in (0, 1):
                logger.warning(f"Invalid is_active value: {is_active}")
                return jsonify({'error': 'is_active must be 0 or 1', 'error_code': 'INVALID_VALUE'}), 400

            # Validate category_id if provided
            if category_id is not None:
                category = session.get(Category, category_id)
                if not category:
                    logger.warning(f"Invalid category_id: {category_id}")
                    return jsonify({'error': 'Invalid category ID', 'error_code': 'INVALID_CATEGORY'}), 400

            product_id = product_manager.add_product(
                name=name,
                price=price,
                stock_quantity=stock_quantity,
                category_id=category_id,
                description=description,
                image_file=image_file,
                is_active=bool(is_active)
            )

            if product_id:
                logger.info(f"Product added successfully: product_id={product_id}")
                return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201
            logger.error("Failed to add product")
            session.rollback()
            return jsonify({'error': 'Failed to add product', 'error_code': 'DATABASE_ERROR'}), 500
    except SQLAlchemyError as e:
        logger.error(f"Database error adding product: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error adding product: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """API to retrieve a product by ID, including its images."""
    try:
        with next(product_manager.get_db_session()) as session:
            product = session.query(Product).options(joinedload(Product.images)).get(product_id)
            if product and product.is_active:
                images_list = [
                    {
                        'id': image.id,
                        'image_url': image.image_url,
                        'created_at': image.created_at.isoformat()
                    } for image in product.images
                ]
                logger.info(f"Retrieved product: product_id={product_id} with {len(images_list)} images")
                return jsonify({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'stock_quantity': product.stock_quantity,
                    'category_id': product.category_id,
                    'image_url': product.image_url,
                    'is_active': product.is_active,
                    'created_at': product.created_at.isoformat(),
                    'images': images_list
                }), 200
            logger.warning(f"Product not found or inactive: product_id={product_id}")
            return jsonify({'error': 'Product not found or inactive', 'error_code': 'NOT_FOUND'}), 404
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving product {product_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    """API to retrieve all active products in a category, including their images."""
    try:
        with next(product_manager.get_db_session()) as session:
            # Validate category_id
            category = session.get(Category, category_id)
            if not category:
                logger.warning(f"Invalid category_id: {category_id}")
                return jsonify({'error': 'Invalid category ID', 'error_code': 'INVALID_CATEGORY'}), 400

            products = session.query(Product).options(joinedload(Product.images)).filter(Product.category_id == category_id, Product.is_active == True).all()
            products_list = [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'stock_quantity': product.stock_quantity,
                    'category_id': product.category_id,
                    'image_url': product.image_url,
                    'is_active': product.is_active,
                    'created_at': product.created_at.isoformat(),
                    'images': [
                        {
                            'id': image.id,
                            'image_url': image.image_url,
                            'created_at': image.created_at.isoformat()
                        } for image in product.images
                    ]
                } for product in products
            ]
            logger.info(f"Retrieved {len(products_list)} products for category_id={category_id}")
            return jsonify({
                'products': products_list,
                'message': 'No products found for this category' if not products_list else 'Products retrieved successfully'
            }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving products for category {category_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving products for category {category_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """API to update product details with optional image upload."""
    try:
        with next(product_manager.get_db_session()) as session:
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price', type=float)
            stock_quantity = request.form.get('stock_quantity', type=int)
            category_id = request.form.get('category_id', type=int)
            is_active = request.form.get('is_active', type=int)
            image_file = request.files.get('image')

            if not any([name, description is not None, price is not None, stock_quantity is not None, category_id is not None, image_file, is_active is not None]):
                logger.warning(f"No valid fields provided for updating product_id={product_id}")
                return jsonify({'error': 'At least one field must be provided', 'error_code': 'INVALID_INPUT'}), 400

            if price is not None and price < 0:
                logger.warning(f"Invalid price: price={price} for product_id={product_id}")
                return jsonify({'error': 'Price must be non-negative', 'error_code': 'INVALID_VALUE'}), 400

            if stock_quantity is not None and stock_quantity < 0:
                logger.warning(f"Invalid stock_quantity: stock_quantity={stock_quantity} for product_id={product_id}")
                return jsonify({'error': 'Stock quantity must be non-negative', 'error_code': 'INVALID_VALUE'}), 400

            if is_active is not None and is_active not in (0, 1):
                logger.warning(f"Invalid is_active value: {is_active} for product_id={product_id}")
                return jsonify({'error': 'is_active must be 0 or 1', 'error_code': 'INVALID_VALUE'}), 400

            # Validate category_id if provided
            if category_id is not None:
                category = session.get(Category, category_id)
                if not category:
                    logger.warning(f"Invalid category_id: {category_id}")
                    return jsonify({'error': 'Invalid category ID', 'error_code': 'INVALID_CATEGORY'}), 400

            # Delete old image file if a new image is provided
            if image_file:
                existing_product = product_manager.get_product_by_id(product_id)
                if existing_product and existing_product.image_url:
                    image_path = os.path.join(current_app.static_folder, secure_filename(existing_product.image_url.lstrip('/')))
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            logger.info(f"Deleted old image file: {existing_product.image_url}")
                        except Exception as e:
                            logger.warning(f"Failed to delete old image file {existing_product.image_url}: {str(e)}")

            success = product_manager.update_product(
                product_id=product_id,
                name=name,
                description=description,
                price=price,
                stock_quantity=stock_quantity,
                category_id=category_id,
                image_file=image_file,
                is_active=is_active
            )

            if success:
                logger.info(f"Product updated successfully: product_id={product_id}")
                return jsonify({'message': 'Product updated successfully'}), 200
            logger.warning(f"Product not found or failed to update: product_id={product_id}")
            session.rollback()
            return jsonify({'error': 'Product not found or failed to update', 'error_code': 'NOT_FOUND'}), 404
    except SQLAlchemyError as e:
        logger.error(f"Database error updating product {product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """API to delete a product by ID."""
    try:
        with next(product_manager.get_db_session()) as session:
            product = product_manager.get_product_by_id(product_id)
            if not product:
                logger.warning(f"Product not found: product_id={product_id}")
                return jsonify({'error': 'Product not found', 'error_code': 'NOT_FOUND'}), 404

            # Delete associated image files
            if product.image_url:
                image_path = os.path.join(current_app.static_folder, secure_filename(product.image_url.lstrip('/')))
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        logger.info(f"Deleted product image file: {product.image_url}")
                    except Exception as e:
                        logger.warning(f"Failed to delete product image file {product.image_url}: {str(e)}")

            images = product_image_manager.get_images_by_product(product_id)
            for image in images:
                if image.image_url:
                    image_path = os.path.join(current_app.static_folder, secure_filename(image.image_url.lstrip('/')))
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            logger.info(f"Deleted product image file: {image.image_url}")
                        except Exception as e:
                            logger.warning(f"Failed to delete product image file {image.image_url}: {str(e)}")

            success = product_manager.delete_product(product_id)
            if success:
                logger.info(f"Product deleted successfully: product_id={product_id}")
                return jsonify({'message': 'Product deleted successfully'}), 200
            logger.warning(f"Failed to delete product: product_id={product_id}")
            session.rollback()
            return jsonify({'error': 'Failed to delete product', 'error_code': 'DATABASE_ERROR'}), 500
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting product {product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products', methods=['GET'])
def get_products():
    """API to retrieve products with pagination, including their images."""
    try:
        with next(product_manager.get_db_session()) as session:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            if page < 1 or per_page < 1:
                logger.warning(f"Invalid pagination parameters: page={page}, per_page={per_page}")
                return jsonify({'error': 'Page and per_page must be positive integers', 'error_code': 'INVALID_INPUT'}), 400

            products, total = product_manager.get_products(page, per_page)
            products = session.query(Product).options(joinedload(Product.images)).filter(Product.is_active == True).order_by(Product.created_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
            products_list = [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'stock_quantity': product.stock_quantity,
                    'category_id': product.category_id,
                    'image_url': product.image_url,
                    'is_active': product.is_active,
                    'created_at': product.created_at.isoformat(),
                    'images': [
                        {
                            'id': image.id,
                            'image_url': image.image_url,
                            'created_at': image.created_at.isoformat()
                        } for image in product.images
                    ]
                } for product in products
            ]
            logger.info(f"Retrieved {len(products_list)} products for page={page}, per_page={per_page}")
            return jsonify({
                'products': products_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'message': 'No products found' if not products_list else 'Products retrieved successfully'
            }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving products: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/search', methods=['GET'])
def search_products():
    """API to search products by name with pagination."""
    try:
        with next(product_manager.get_db_session()) as session:
            search_term = request.args.get('search_term', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            if not search_term:
                logger.warning("Search term is required")
                return jsonify({'error': 'Search term is required', 'error_code': 'INVALID_INPUT'}), 400

            if page < 1 or per_page < 1:
                logger.warning(f"Invalid pagination parameters: page={page}, per_page={per_page}")
                return jsonify({'error': 'Page and per_page must be positive integers', 'error_code': 'INVALID_INPUT'}), 400

            products, total = product_manager.search_products(search_term, page, per_page)
            products = session.query(Product).options(joinedload(Product.images)).filter(Product.name.ilike(f"%{search_term}%"), Product.is_active == True).order_by(Product.name).limit(per_page).offset((page - 1) * per_page).all()
            products_list = [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.price,
                    'stock_quantity': product.stock_quantity,
                    'category_id': product.category_id,
                    'image_url': product.image_url,
                    'is_active': product.is_active,
                    'created_at': product.created_at.isoformat(),
                    'images': [
                        {
                            'id': image.id,
                            'image_url': image.image_url,
                            'created_at': image.created_at.isoformat()
                        } for image in product.images
                    ]
                } for product in products
            ]
            logger.info(f"Retrieved {len(products_list)} products for search_term='{search_term}'")
            return jsonify({
                'products': products_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'message': 'No products found for this search term' if not products_list else 'Products retrieved successfully'
            }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error searching products with term '{search_term}': {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error searching products with term '{search_term}': {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/number', methods=['GET'])
def get_total_products():
    """API to retrieve the total number of products in the database."""
    try:
        total_products = product_manager.get_total_products()
        logger.info(f"Retrieved total products count: {total_products}")
        return jsonify({
            'total_products': total_products,
            'message': 'Total products count retrieved successfully'
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving total products count: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving total products count: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500
    
@products_bp.route('/products/low_stock', methods=['GET'])
@admin_required  
def get_low_stock_products():
    """API endpoint to get low stock products."""
    try:
        products = product_manager.get_low_stock_products()
        product_list = [
            {
                "id": product.id,
                "name": product.name,
                "stock_quantity": product.stock_quantity,
                "low_stock_threshold": product.low_stock_threshold,
                "category_id": product.category_id,
                "price": product.price,
                "image_url": product.image_url
            }
            for product in products
        ]
        return jsonify({
            "status": "success",
            "message": f"{len(product_list)} low stock products found.",
            "data": product_list
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching low stock products: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve low stock products."
        }), 500
    
@products_bp.route('/products/<int:product_id>/images', methods=['POST'])
@admin_required
def add_product_image(product_id):
    """API to add a new product image via file upload."""
    try:
        with next(product_manager.get_db_session()) as session:
            product = product_manager.get_product_by_id(product_id)
            if not product or not product.is_active:
                logger.warning(f"Product not found or inactive: product_id={product_id}")
                return jsonify({'error': 'Product not found or inactive', 'error_code': 'NOT_FOUND'}), 404

            image_file = request.files.get('image')
            if not image_file:
                logger.warning("Missing required field: image file")
                return jsonify({'error': 'Image file is required', 'error_code': 'INVALID_INPUT'}), 400

            if not product_image_manager._allowed_file(image_file.filename):
                logger.warning("Invalid image file extension")
                return jsonify({'error': 'Invalid image file. Allowed extensions: jpg, jpeg, png', 'error_code': 'INVALID_FILE'}), 400

            image_id = product_image_manager.add_product_image(product_id, image_file=image_file)
            if image_id:
                logger.info(f"Product image added successfully: image_id={image_id} for product_id={product_id}")
                return jsonify({'message': 'Product image added successfully', 'image_id': image_id}), 201
            logger.error(f"Failed to add product image for product_id={product_id}")
            session.rollback()
            return jsonify({'error': 'Failed to add product image', 'error_code': 'DATABASE_ERROR'}), 500
    except SQLAlchemyError as e:
        logger.error(f"Database error adding product image for product_id={product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error adding product image for product_id={product_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['GET'])
def get_product_image_by_id(image_id):
    """API to retrieve a product image by ID."""
    try:
        image = product_image_manager.get_product_image_by_id(image_id)
        if image:
            logger.info(f"Retrieved product image: image_id={image_id}")
            return jsonify({
                'id': image.id,
                'product_id': image.product_id,
                'image_url': image.image_url,
                'created_at': image.created_at.isoformat()
            }), 200
        logger.warning(f"Product image not found: image_id={image_id}")
        return jsonify({'error': 'Product image not found', 'error_code': 'NOT_FOUND'}), 404
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving product image {image_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving product image {image_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/<int:product_id>/images', methods=['GET'])
def get_images_by_product(product_id):
    """API to retrieve all images for a specific product."""
    try:
        images = product_image_manager.get_images_by_product(product_id)
        images_list = [
            {
                'id': image.id,
                'product_id': image.product_id,
                'image_url': image.image_url,
                'created_at': image.created_at.isoformat()
            } for image in images
        ]
        logger.info(f"Retrieved {len(images_list)} images for product_id={product_id}")
        return jsonify({
            'images': images_list,
            'message': 'No images found for this product' if not images_list else 'Images retrieved successfully'
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving images for product_id={product_id}: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving images for product_id={product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['PUT'])
@admin_required
def update_product_image(image_id):
    """API to update a product image via file upload."""
    try:
        with next(product_image_manager.get_db_session()) as session:
            existing_image = product_image_manager.get_product_image_by_id(image_id)
            if not existing_image:
                logger.warning(f"Product image not found: image_id={image_id}")
                return jsonify({'error': 'Product image not found', 'error_code': 'NOT_FOUND'}), 404

            image_file = request.files.get('image')
            if not image_file:
                logger.warning(f"No image file provided for image_id={image_id}")
                return jsonify({'error': 'Image file is required', 'error_code': 'INVALID_INPUT'}), 400

            if not product_image_manager._allowed_file(image_file.filename):
                logger.warning("Invalid image file extension")
                return jsonify({'error': 'Invalid image file. Allowed extensions: jpg, jpeg, png', 'error_code': 'INVALID_FILE'}), 400

            # Delete old image file if it exists
            if existing_image.image_url:
                image_path = os.path.join(current_app.static_folder, secure_filename(existing_image.image_url.lstrip('/')))
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        logger.info(f"Deleted old image file: {existing_image.image_url}")
                    except Exception as e:
                        logger.warning(f"Failed to delete old image file {existing_image.image_url}: {str(e)}")

            success = product_image_manager.update_product_image(image_id, image_file=image_file)
            if success:
                logger.info(f"Product image updated successfully: image_id={image_id}")
                return jsonify({'message': 'Product image updated successfully'}), 200
            logger.warning(f"Failed to update product image: image_id={image_id}")
            session.rollback()
            return jsonify({'error': 'Failed to update product image', 'error_code': 'DATABASE_ERROR'}), 500
    except SQLAlchemyError as e:
        logger.error(f"Database error updating product image {image_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error updating product image {image_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/products/images/<int:image_id>', methods=['DELETE'])
@admin_required
def delete_product_image(image_id):
    """API to delete a product image by ID."""
    try:
        with next(product_image_manager.get_db_session()) as session:
            image = product_image_manager.get_product_image_by_id(image_id)
            if not image:
                logger.warning(f"Product image not found: image_id={image_id}")
                return jsonify({'error': 'Product image not found', 'error_code': 'NOT_FOUND'}), 404

            if image.image_url:
                image_path = os.path.join(current_app.static_folder, secure_filename(image.image_url.lstrip('/')))
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        logger.info(f"Deleted image file: {image.image_url}")
                    except Exception as e:
                        logger.warning(f"Failed to delete image file {image.image_url}: {str(e)}")

            success = product_image_manager.delete_product_image(image_id)
            if success:
                logger.info(f"Product image deleted successfully: image_id={image_id}")
                return jsonify({'message': 'Product image deleted successfully'}), 200
            logger.warning(f"Failed to delete product image: image_id={image_id}")
            session.rollback()
            return jsonify({'error': 'Failed to delete product image', 'error_code': 'DATABASE_ERROR'}), 500
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting product image {image_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error deleting product image {image_id}: {str(e)}")
        session.rollback()
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500

@products_bp.route('/product_images', methods=['GET'])
def get_product_images():
    """API to retrieve product images with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            logger.warning(f"Invalid pagination parameters: page={page}, per_page={per_page}")
            return jsonify({'error': 'Page and per_page must be positive integers', 'error_code': 'INVALID_INPUT'}), 400

        images, total = product_image_manager.get_product_images(page, per_page)
        images_list = [
            {
                'id': image.id,
                'product_id': image.product_id,
                'image_url': image.image_url,
                'created_at': image.created_at.isoformat()
            } for image in images
        ]
        logger.info(f"Retrieved {len(images_list)} product images for page={page}, per_page={per_page}")
        return jsonify({
            'images': images_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'message': 'No images found' if not images_list else 'Images retrieved successfully'
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving product images: {str(e)}")
        return jsonify({'error': 'Database error', 'error_code': 'DATABASE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Error retrieving product images: {str(e)}")
        return jsonify({'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500