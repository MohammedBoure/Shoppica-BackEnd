from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import Flask, session
import datetime
from apis import *


app = Flask(__name__)
CORS(app,supports_credentials=True, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "https://shoppica-26gr.onrender.com",
    "https://shoppica-testsite.onrender.com",
    "http://127.0.0.1:5501"
]}})


# Configure secret key for session management
app.config['SECRET_KEY'] = 'your-secret-key-here'  # CHANGE THIS TO A SECURE RANDOM STRING!
app.config['SESSION_COOKIE_SECURE'] = True  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=10)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limit uploads to 5MB


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
app.register_blueprint(analytics_bp, url_prefix='/api')


@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        return '', 204

@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

@app.errorhandler(422)
def handle_unprocessable_entity(error):
    return jsonify({'error': 'Unprocessable Entity', 'details': str(error)}), 422

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)