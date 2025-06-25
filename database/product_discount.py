from .base import Database, ProductDiscount, Product
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

class ProductDiscountManager(Database):
    """Manages operations for the product_discounts table in the database."""

    def add_product_discount(self, product_id, discount_percent, starts_at=None, ends_at=None, is_active=1):
        """Adds a new discount for a product."""
        try:
            with next(self.get_db_session()) as session:
                product_discount = ProductDiscount(
                    product_id=product_id,
                    discount_percent=discount_percent,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    is_active=is_active
                )
                session.add(product_discount)
                session.commit()
                discount_id = product_discount.id
                logging.info(f"Product discount added for product {product_id} with ID: {discount_id}")
                return discount_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding product discount for product {product_id}: {e}")
            return None

    def get_product_discount_by_id(self, discount_id):
        """Retrieves a product discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(ProductDiscount).filter_by(id=discount_id).first()
                if discount:
                    logging.info(f"Retrieved product discount with ID: {discount_id}")
                    return discount
                else:
                    logging.warning(f"No product discount found with ID: {discount_id}")
                    return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving product discount by ID {discount_id}: {e}")
            return None

    def get_product_discounts_by_product(self, product_id):
        """Retrieves all discounts for a product."""
        try:
            with next(self.get_db_session()) as session:
                discounts = session.query(ProductDiscount).filter_by(product_id=product_id).all()
                logging.info(f"Retrieved {len(discounts)} product discounts for product {product_id}")
                return discounts
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving product discounts for product {product_id}: {e}")
            return []

    def get_valid_product_discounts(self, product_id):
        """Retrieves valid (active and within date range) discounts for a product."""
        try:
            with next(self.get_db_session()) as session:
                current_time = self.get_current_timestamp()
                discounts = (
                    session.query(ProductDiscount)
                    .filter_by(product_id=product_id, is_active=1)
                    .filter(
                        (ProductDiscount.starts_at == None) | (ProductDiscount.starts_at <= current_time),
                        (ProductDiscount.ends_at == None) | (ProductDiscount.ends_at >= current_time)
                    )
                    .all()
                )
                logging.info(f"Retrieved {len(discounts)} valid product discounts for product {product_id}")
                return discounts
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving valid product discounts for product {product_id}: {e}")
            return []

    def update_product_discount(self, discount_id, discount_percent=None, starts_at=None, ends_at=None, is_active=None):
        """Updates product discount details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(ProductDiscount).filter_by(id=discount_id).first()
                if not discount:
                    logging.warning(f"No product discount found with ID: {discount_id}")
                    return False

                if discount_percent is not None:
                    discount.discount_percent = discount_percent
                if starts_at is not None:
                    discount.starts_at = starts_at
                if ends_at is not None:
                    discount.ends_at = ends_at
                if is_active is not None:
                    discount.is_active = is_active

                session.commit()
                logging.info(f"Updated product discount with ID: {discount_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating product discount {discount_id}: {e}")
            return False

    def delete_product_discount(self, discount_id):
        """Deletes a product discount by its ID."""
        try:
            with next(self.get_db_session()) as session:
                discount = session.query(ProductDiscount).filter_by(id=discount_id).first()
                if discount:
                    session.delete(discount)
                    session.commit()
                    logging.info(f"Deleted product discount with ID: {discount_id}")
                    return True
                else:
                    logging.warning(f"No product discount found with ID: {discount_id}")
                    return False
        except SQLAlchemyError as e:
            logging.error(f"Error deleting product discount {discount_id}: {e}")
            return False

    def get_product_discounts(self, page=1, per_page=20):
        """Retrieves product discounts with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(ProductDiscount).count()
                discounts = (
                    session.query(ProductDiscount, Product.name)
                    .join(Product, ProductDiscount.product_id == Product.id)
                    .order_by(ProductDiscount.id)
                    .limit(per_page)
                    .offset((page - 1) * per_page)
                    .all()
                )
                # Convert query results to a list of tuples for compatibility with original return format
                result = [(discount, product_name) for discount, product_name in discounts]
                logging.info(f"Retrieved {len(result)} product discounts. Total: {total}")
                return result, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving product discounts: {e}")
            return [], 0