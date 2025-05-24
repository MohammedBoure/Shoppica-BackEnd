from .auth import auth_bp
from .user import users_bp
from .addresses import addresses_bp
from .category import categories_bp
from .products import products_bp
from .review import reviews_bp
from .cart_item import cart_items_bp
from .orders import orders_bp
from .order_item import order_items_bp
from .payment import payments_bp
from .discounts import discounts_bp
from .discount_usage import discount_usages_bp
from .product_discounts import product_discounts_bp
from .category_discounts import category_discounts_bp

__all__ = [
    'auth_bp',
    'users_bp',
    'addresses_bp',
    'categories_bp',
    'products_bp',
    'reviews_bp',
    'cart_items_bp',
    'orders_bp',
    'order_items_bp',
    'payments_bp',
    'discounts_bp',
    'discount_usages_bp',
    'product_discounts_bp',
    'category_discounts_bp'
]
