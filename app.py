from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from database import (
    Database, UserManager, AddressManager, CategoryManager, ProductManager,
    ReviewManager, CartItemManager, OrderManager, OrderItemManager,
    PaymentManager, DiscountManager, DiscountUsageManager,
    ProductDiscountManager, CategoryDiscountManager
)
from admin_apis.user import users_bp
from admin_apis.addresses import addresses_bp
from admin_apis.category import categories_bp
from admin_apis.products import products_bp
from admin_apis.review import reviews_bp
from admin_apis.cart_item import cart_items_bp
from admin_apis.orders import orders_bp
from admin_apis.order_item import order_items_bp
from admin_apis.payment import payments_bp
from admin_apis.discounts import discounts_bp
from admin_apis.discount_usage import discount_usages_bp
from admin_apis.product_discounts import product_discounts_bp
from admin_apis.category_discounts import category_discounts_bp







app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:5500",
    "https://educonnect-front-end.onrender.com",
    "https://educonnect-admin.onrender.com"
]}})

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'  # CHANGE THIS TO A SECURE RANDOM STRING!
jwt = JWTManager(app)

# Initialize database
user_manager = UserManager()
address_manager = AddressManager()
category_manager = CategoryManager()
product_manager = ProductManager()
review_manager = ReviewManager()
cart_item_manager = CartItemManager()
order_manager = OrderManager()
order_item_manager = OrderItemManager()
payment_manager = PaymentManager()
discount_manager = DiscountManager()
discount_usage_manager = DiscountUsageManager()
product_discount_manager = ProductDiscountManager()
category_discount_manager = CategoryDiscountManager()


# Register blueprints
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(addresses_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')
app.register_blueprint(products_bp, url_prefix='/api')
app.register_blueprint(reviews_bp, url_prefix='/api')
app.register_blueprint(cart_items_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(order_items_bp, url_prefix='/api')
app.register_blueprint(payments_bp, url_prefix='/api')
app.register_blueprint(discounts_bp, url_prefix='/api')
app.register_blueprint(discount_usages_bp, url_prefix='/api')
app.register_blueprint(product_discounts_bp, url_prefix='/api')
app.register_blueprint(category_discounts_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)