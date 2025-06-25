from .base import Database, CartItem, Product, User
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import contextmanager

class CartItemManager(Database):
    """Manages operations for the cart_items table in the database using SQLAlchemy."""

    @contextmanager
    def session_scope(self):
        """Provides a transactional scope around a series of operations."""
        session = next(self.get_db_session())
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def add_cart_item(self, user_id, product_id, quantity):
        """Adds a product to a user's cart after checking stock availability."""
        try:
            with self.session_scope() as session:
                # Check product stock
                product = session.query(Product).filter(Product.id == product_id).first()
                if not product or product.stock_quantity < quantity:
                    logging.warning(f"Insufficient stock for product {product_id} or product not found")
                    return None

                # Check if item already exists in cart
                existing_item = session.query(CartItem).filter(
                    CartItem.user_id == user_id,
                    CartItem.product_id == product_id
                ).first()
                if existing_item:
                    new_quantity = existing_item.quantity + quantity
                    if product.stock_quantity < new_quantity:
                        logging.warning(f"Insufficient stock for product {product_id} to update quantity to {new_quantity}")
                        return None
                    return self.update_cart_item(existing_item.id, new_quantity)

                # Add new cart item
                cart_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity,
                    added_at=self.get_current_timestamp()
                )
                session.add(cart_item)
                session.flush()  # Ensure ID is available
                cart_item_id = cart_item.id
                logging.info(f"Added cart item for user {user_id}, product {product_id} with ID: {cart_item_id}")
                return cart_item_id
        except SQLAlchemyError as e:
            logging.error(f"Error adding cart item for user {user_id}, product {product_id}: {e}")
            return None

    def get_cart_item_by_id(self, cart_item_id):
        """Retrieves a cart item by its ID."""
        try:
            with self.session_scope() as session:
                cart_item = session.query(CartItem, Product.name, Product.price).join(
                    Product, CartItem.product_id == Product.id
                ).filter(CartItem.id == cart_item_id).first()
                if cart_item:
                    cart_item_dict = {
                        'id': cart_item.CartItem.id,
                        'user_id': cart_item.CartItem.user_id,
                        'product_id': cart_item.CartItem.product_id,
                        'quantity': cart_item.CartItem.quantity,
                        'added_at': cart_item.CartItem.added_at,
                        'name': cart_item.name,
                        'price': cart_item.price
                    }
                    logging.info(f"Retrieved cart item with ID: {cart_item_id}")
                    return cart_item_dict
                logging.warning(f"No cart item found with ID: {cart_item_id}")
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving cart item by ID {cart_item_id}: {e}")
            return None

    def get_cart_items_by_user(self, user_id):
        """Retrieves all cart items for a user."""
        try:
            with self.session_scope() as session:
                cart_items = session.query(CartItem, Product.name, Product.price).join(
                    Product, CartItem.product_id == Product.id
                ).filter(CartItem.user_id == user_id).all()
                cart_items_list = [
                    {
                        'id': item.CartItem.id,
                        'user_id': item.CartItem.user_id,
                        'product_id': item.CartItem.product_id,
                        'quantity': item.CartItem.quantity,
                        'added_at': item.CartItem.added_at,
                        'name': item.name,
                        'price': item.price
                    } for item in cart_items
                ]
                logging.info(f"Retrieved {len(cart_items_list)} cart items for user {user_id}")
                return cart_items_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving cart items for user {user_id}: {e}")
            return []

    def update_cart_item(self, cart_item_id, quantity=None):
        """Updates cart item details. Only provided fields are updated."""
        try:
            with self.session_scope() as session:
                cart_item = session.query(CartItem).filter(CartItem.id == cart_item_id).first()
                if not cart_item:
                    logging.warning(f"No cart item found with ID: {cart_item_id}")
                    return False

                if quantity is not None:
                    # Check product stock
                    product = session.query(Product).filter(
                        Product.id == cart_item.product_id
                    ).first()
                    if not product or product.stock_quantity < quantity:
                        logging.warning(f"Insufficient stock for cart item {cart_item_id} to update quantity to {quantity}")
                        return False
                    cart_item.quantity = quantity

                logging.info(f"Updated cart item with ID: {cart_item_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating cart item {cart_item_id}: {e}")
            return False

    def delete_cart_item(self, cart_item_id):
        """Deletes a cart item by its ID."""
        try:
            with self.session_scope() as session:
                cart_item = session.query(CartItem).filter(CartItem.id == cart_item_id).first()
                if cart_item:
                    session.delete(cart_item)
                    logging.info(f"Deleted cart item with ID: {cart_item_id}")
                    return True
                logging.warning(f"No cart item found with ID: {cart_item_id}")
                return False
        except SQLAlchemyError as e:
            logging.error(f"Error deleting cart item {cart_item_id}: {e}")
            return False

    def get_cart_items(self, page=1, per_page=20):
        """Retrieves cart items with pagination."""
        try:
            with self.session_scope() as session:
                total = session.query(CartItem).count()
                cart_items = session.query(CartItem, Product.name, Product.price).join(
                    Product, CartItem.product_id == Product.id
                ).order_by(CartItem.added_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
                cart_items_list = [
                    {
                        'id': item.CartItem.id,
                        'user_id': item.CartItem.user_id,
                        'product_id': item.CartItem.product_id,
                        'quantity': item.CartItem.quantity,
                        'added_at': item.CartItem.added_at,
                        'name': item.name,
                        'price': item.price
                    } for item in cart_items
                ]
                logging.info(f"Retrieved {len(cart_items_list)} cart items. Total: {total}")
                return cart_items_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving cart items: {e}")
            return [], 0

    def search_cart_items(self, user_id=None, product_id=None, page=1, per_page=20):
        """Searches cart items based on user_id or product_id with pagination."""
        try:
            with self.session_scope() as session:
                query = session.query(CartItem, Product.name, Product.price).join(
                    Product, CartItem.product_id == Product.id
                )
                if user_id is not None:
                    query = query.filter(CartItem.user_id == user_id)
                if product_id is not None:
                    query = query.filter(CartItem.product_id == product_id)

                total = query.count()
                cart_items = query.order_by(CartItem.added_at.desc()).limit(per_page).offset((page - 1) * per_page).all()
                cart_items_list = [
                    {
                        'id': item.CartItem.id,
                        'user_id': item.CartItem.user_id,
                        'product_id': item.CartItem.product_id,
                        'quantity': item.CartItem.quantity,
                        'added_at': item.CartItem.added_at,
                        'name': item.name,
                        'price': item.name
                    } for item in cart_items
                ]
                logging.info(f"Found {len(cart_items_list)} cart items matching search criteria. Total: {total}")
                return cart_items_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error searching cart items: {e}")
            return [], 0

    def delete_cart_items_by_user(self, user_id):
        """Deletes all cart items for a specific user."""
        try:
            with self.session_scope() as session:
                deleted_count = session.query(CartItem).filter(CartItem.user_id == user_id).delete()
                logging.info(f"Deleted {deleted_count} cart items for user {user_id}")
                return deleted_count
        except SQLAlchemyError as e:
            logging.error(f"Error deleting cart items for user {user_id}: {e}")
            return 0

    def delete_cart_items_by_product(self, product_id):
        """Deletes all cart items for a specific product."""
        try:
            with self.session_scope() as session:
                deleted_count = session.query(CartItem).filter(CartItem.product_id == product_id).delete()
                logging.info(f"Deleted {deleted_count} cart items for product {product_id}")
                return deleted_count
        except SQLAlchemyError as e:
            logging.error(f"Error deleting cart items for product {product_id}: {e}")
            return 0

    def get_cart_stats(self):
        """Returns statistics about cart items."""
        try:
            with self.session_scope() as session:
                total_cart_items = session.query(CartItem).count()
                users_with_cart_items = session.query(CartItem.user_id).distinct().count()
                total_cart_value = session.query(
                    CartItem.quantity * Product.price
                ).join(Product, CartItem.product_id == Product.id).scalar() or 0.0
                stats = {
                    'total_cart_items': total_cart_items,
                    'users_with_cart_items': users_with_cart_items,
                    'total_cart_value': round(total_cart_value, 2)
                }
                logging.info(f"Retrieved cart stats: {stats}")
                return stats
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving cart stats: {e}")
            return {'total_cart_items': 0, 'users_with_cart_items': 0, 'total_cart_value': 0.0}

    def get_user_cart_stats(self, user_id):
        """Returns cart statistics for a specific user."""
        try:
            with self.session_scope() as session:
                total_items = session.query(CartItem).filter(CartItem.user_id == user_id).count()
                cart_value = session.query(
                    CartItem.quantity * Product.price
                ).join(Product, CartItem.product_id == Product.id).filter(CartItem.user_id == user_id).scalar() or 0.0
                stats = {
                    'total_items': total_items,
                    'cart_value': round(cart_value, 2)
                }
                logging.info(f"Retrieved cart stats for user {user_id}: {stats}")
                return stats
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving cart stats for user {user_id}: {e}")
            return {'total_items': 0, 'cart_value': 0.0}