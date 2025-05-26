from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import traceback

from apis import *

app = Flask(__name__)
CORS(app,supports_credentials=True, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:5500",
    "http://localhost:3000",
]}})


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here'
jwt = JWTManager(app)


# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
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


@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        return '', 204

@app.errorhandler(Exception)
def handle_error(error):
    logging.error(f"Error: {str(error)}\n{traceback.format_exc()}")
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(422)
def handle_unprocessable_entity(error):
    logging.error(f"422 Error: {str(error)}\n{traceback.format_exc()}")
    return jsonify({'error': 'Unprocessable Entity', 'details': str(error)}), 422

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)