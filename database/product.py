from .base import Database, Product, ProductImage, Category
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
import uuid
from werkzeug.utils import secure_filename

class ProductManager(Database):
    """Manages operations for the products table in the database using SQLAlchemy ORM."""

    def add_product(
        self,
        name,
        price,
        purchase_price,
        stock_quantity,
        category_id=None,
        description=None,
        image_file=None,
        image_url='',
        is_active=True
    ):
        """Adds a new product with optional image and purchase price."""
        try:
            with next(self.get_db_session()) as session:
                # Validate required fields
                if not name:
                    logging.error("Product name is required")
                    return None
                if price is None or price < 0:
                    logging.error("Valid product price is required")
                    return None
                if purchase_price is None or purchase_price < 0:
                    logging.error("Valid purchase price is required")
                    return None
                if stock_quantity is None or stock_quantity < 0:
                    logging.error("Valid stock quantity is required")
                    return None

                # Handle image upload
                if image_file and self._allowed_file(image_file.filename):
                    image_url = self._save_image(image_file)
                    if not image_url:
                        logging.error("Invalid image file provided")
                        return None

                # Create new product instance
                new_product = Product(
                    name=name,
                    description=description,
                    price=price,
                    purchase_price=purchase_price,
                    stock_quantity=stock_quantity,
                    category_id=category_id,
                    image_url=image_url,
                    is_active=is_active
                )

                # Save to DB
                session.add(new_product)
                session.commit()
                product_id = new_product.id
                logging.info(f"Product {name} added with ID: {product_id}")
                return product_id

        except Exception as e:
            logging.error(f"Error adding product {name}: {e}")
            return None

    def get_product_by_id(self, product_id):
        """Retrieves a product by its ID."""
        try:
            with next(self.get_db_session()) as session:
                product = session.get(Product, product_id)
                if product:
                    logging.info(f"Retrieved product with ID: {product_id}")
                    return product
                else:
                    logging.warning(f"No product found with ID: {product_id}")
                    return None
        except Exception as e:
            logging.error(f"Error retrieving product by ID {product_id}: {e}")
            return None

    def get_products_by_category(self, category_id):
        """Retrieves all active products in a category."""
        try:
            with next(self.get_db_session()) as session:
                query = select(Product).where(Product.category_id == category_id, Product.is_active == True)
                products = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(products)} products for category {category_id}")
                return products
        except Exception as e:
            logging.error(f"Error retrieving products for category {category_id}: {e}")
            return []

    def update_product(self, product_id, name=None, description=None, price=None, purchase_price=None, stock_quantity=None, low_stock_threshold=None, category_id=None, image_file=None, image_url=None, is_active=None):
        """Updates product details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                product = session.get(Product, product_id)
                if not product:
                    logging.warning(f"No product found with ID: {product_id}")
                    return False

                # Validate and update fields
                if name is not None:
                    product.name = name

                if description is not None:
                    product.description = description

                if price is not None:
                    try:
                        price = float(price)
                        if price < 0:
                            raise ValueError("Price must be non-negative")
                        product.price = price
                    except (ValueError, TypeError) as e:
                        logging.error(f"Invalid price: {e}")
                        return False

                if purchase_price is not None:
                    try:
                        purchase_price = float(purchase_price)
                        if purchase_price < 0:
                            raise ValueError("Purchase price must be non-negative")
                        product.purchase_price = purchase_price
                    except (ValueError, TypeError) as e:
                        logging.error(f"Invalid purchase_price: {e}")
                        return False

                if stock_quantity is not None:
                    try:
                        stock_quantity = int(stock_quantity)
                        if stock_quantity < 0:
                            raise ValueError("Stock quantity must be non-negative")
                        product.stock_quantity = stock_quantity
                    except (ValueError, TypeError) as e:
                        logging.error(f"Invalid stock_quantity: {e}")
                        return False

                if low_stock_threshold is not None:
                    try:
                        low_stock_threshold = int(low_stock_threshold)
                        if low_stock_threshold < 0:
                            raise ValueError("Low stock threshold must be non-negative")
                        product.low_stock_threshold = low_stock_threshold
                    except (ValueError, TypeError) as e:
                        logging.error(f"Invalid low_stock_threshold: {e}")
                        return False

                if category_id is not None:
                    category = session.get(Category, category_id)
                    if not category:
                        logging.error(f"Invalid category_id: {category_id}")
                        return False
                    product.category_id = category_id

                if is_active is not None:
                    if is_active not in (0, 1, True, False):
                        logging.error("is_active must be 0 or 1")
                        return False
                    product.is_active = int(bool(is_active))

                # Handle image upload
                if image_file and self._allowed_file(image_file.filename):
                    new_image_url = self._save_image(image_file)
                    if new_image_url:
                        product.image_url = new_image_url
                elif image_url is not None:
                    product.image_url = image_url

                session.commit()
                logging.info(f"Updated product with ID: {product_id}")
                return True

        except Exception as e:
            logging.error(f"Error updating product {product_id}: {e}")
            return False


    def delete_product(self, product_id):
        """Deletes a product by its ID."""
        try:
            with next(self.get_db_session()) as session:
                product = session.get(Product, product_id)
                if not product:
                    logging.warning(f"No product found with ID: {product_id}")
                    return False

                session.delete(product)
                session.commit()
                logging.info(f"Deleted product with ID: {product_id}")
                return True
        except Exception as e:
            logging.error(f"Error deleting product {product_id}: {e}")
            return False

    def get_products(self, page=1, per_page=20):
        """Retrieves active products with pagination."""
        try:
            with next(self.get_db_session()) as session:
                # Get total count
                total_query = select(func.count()).select_from(Product).where(Product.is_active == True)
                total = session.execute(total_query).scalar()

                # Get paginated products
                query = select(Product).where(Product.is_active == True).order_by(Product.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
                products = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(products)} products. Total: {total}")
                return products, total
        except Exception as e:
            logging.error(f"Error retrieving products: {e}")
            return [], 0

    def search_products(self, search_term, page=1, per_page=20):
        """Searches active products by name with pagination."""
        try:
            with next(self.get_db_session()) as session:
                # Build search query
                search_pattern = f"%{search_term}%"
                query = select(Product).where(Product.name.ilike(search_pattern), Product.is_active == True)
                
                # Get total count
                total_query = select(func.count()).select_from(Product).where(Product.name.ilike(search_pattern), Product.is_active == True)
                total = session.execute(total_query).scalar()

                # Get paginated results
                query = query.order_by(Product.name).limit(per_page).offset((page - 1) * per_page)
                products = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(products)} products for search term '{search_term}'. Total: {total}")
                return products, total
        except Exception as e:
            logging.error(f"Error searching products with term '{search_term}': {e}")
            return [], 0
    
    def get_total_products(self):
        """Returns the total number of products in the database."""
        try:
            with next(self.get_db_session()) as session:
                total_products = session.query(Product).count()
                logging.info(f"Retrieved total products count: {total_products}")
                return total_products
        except SQLAlchemyError as e:
            logging.error(f"Failed to retrieve total products count: {e}")
            raise
    def get_low_stock_products(self):
        """Retrieves products that are at or below their low stock threshold."""
        try:
            with next(self.get_db_session()) as session:
                query = select(Product).where(
                    Product.stock_quantity <= Product.low_stock_threshold,
                    Product.is_active == True
                )
                products = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(products)} low stock products.")
                return products
        except Exception as e:
            logging.error(f"Error retrieving low stock products: {e}")
            return []


    def _allowed_file(self, filename):
        """Check if the file has an allowed extension."""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _save_image(self, file):
        """Save the uploaded image and return its relative URL."""
        from flask import current_app
        if not file or not self._allowed_file(file.filename):
            return None
        # Ensure the upload directory exists
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        # Generate a unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        # Return the relative URL
        return f"/static/uploads/products/{filename}"

class ProductImageManager(Database):
    """Manages operations for the product_images table in the database using SQLAlchemy ORM."""

    def add_product_image(self, product_id, image_file=None, image_url=None):
        """Adds a new product image."""
        try:
            with next(self.get_db_session()) as session:
                # Validate required fields
                if not product_id:
                    logging.error("Product ID is required")
                    return None
                if not image_file and not image_url:
                    logging.error("Either image file or image URL is required")
                    return None

                # Handle image upload
                if image_file and self._allowed_file(image_file.filename):
                    image_url = self._save_image(image_file)
                    if not image_url:
                        logging.error("Invalid image file provided")
                        return None
                elif image_url is None:
                    image_url = ''

                # Create new product image
                new_image = ProductImage(
                    product_id=product_id,
                    image_url=image_url
                )
                session.add(new_image)
                session.commit()
                image_id = new_image.id
                logging.info(f"Product image added for product ID {product_id} with image ID: {image_id}")
                return image_id
        except Exception as e:
            logging.error(f"Error adding product image for product ID {product_id}: {e}")
            return None

    def get_product_image_by_id(self, image_id):
        """Retrieves a product image by its ID."""
        try:
            with next(self.get_db_session()) as session:
                image = session.get(ProductImage, image_id)
                if image:
                    logging.info(f"Retrieved product image with ID: {image_id}")
                    return image
                else:
                    logging.warning(f"No product image found with ID: {image_id}")
                    return None
        except Exception as e:
            logging.error(f"Error retrieving product image by ID {image_id}: {e}")
            return None

    def get_images_by_product(self, product_id):
        """Retrieves all images for a specific product."""
        try:
            with next(self.get_db_session()) as session:
                query = select(ProductImage).where(ProductImage.product_id == product_id)
                images = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(images)} images for product ID {product_id}")
                return images
        except Exception as e:
            logging.error(f"Error retrieving images for product ID {product_id}: {e}")
            return []

    def update_product_image(self, image_id, image_file=None, image_url=None):
        """Updates a product image's URL."""
        try:
            with next(self.get_db_session()) as session:
                image = session.get(ProductImage, image_id)
                if not image:
                    logging.warning(f"No product image found with ID: {image_id}")
                    return False

                if image_file and self._allowed_file(image_file.filename):
                    image_url = self._save_image(image_file)
                    if not image_url:
                        logging.error("Invalid image file provided")
                        return False
                if image_url is not None:
                    image.image_url = image_url

                session.commit()
                logging.info(f"Updated product image with ID: {image_id}")
                return True
        except Exception as e:
            logging.error(f"Error updating product image {image_id}: {e}")
            return False

    def delete_product_image(self, image_id):
        """Deletes a product image by its ID."""
        try:
            with next(self.get_db_session()) as session:
                image = session.get(ProductImage, image_id)
                if not image:
                    logging.warning(f"No product image found with ID: {image_id}")
                    return False

                session.delete(image)
                session.commit()
                logging.info(f"Deleted product image with ID: {image_id}")
                return True
        except Exception as e:
            logging.error(f"Error deleting product image {image_id}: {e}")
            return False

    def get_product_images(self, page=1, per_page=20):
        """Retrieves product images with pagination."""
        try:
            with next(self.get_db_session()) as session:
                # Get total count
                total_query = select(func.count()).select_from(ProductImage)
                total = session.execute(total_query).scalar()

                # Get paginated images
                query = select(ProductImage).order_by(ProductImage.created_at.desc()).limit(per_page).offset((page - 1) * per_page)
                images = session.execute(query).scalars().all()
                logging.info(f"Retrieved {len(images)} product images. Total: {total}")
                return images, total
        except Exception as e:
            logging.error(f"Error retrieving product images: {e}")
            return [], 0

    def _allowed_file(self, filename):
        """Check if the file has an allowed extension."""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _save_image(self, file):
        """Save the uploaded image and return its relative URL."""
        from flask import current_app
        if not file or not self._allowed_file(file.filename):
            return None
        # Ensure the upload directory exists
        upload_folder = os.path.join(current_app.static_folder, 'uploads', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        # Generate a unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        # Return the relative URL
        return f"/static/uploads/products/{filename}"
    
    
