from flask import Blueprint, request, jsonify, session
from database import UserManager
from functools import wraps
import logging
import re
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__)
user_manager = UserManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def session_required(fn):
    """Decorator to ensure user is authenticated via session."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            logging.warning("Unauthorized access attempt: No user_id in session")
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    """Decorator to restrict route access to admins only."""
    @wraps(fn)
    @session_required
    def wrapper(*args, **kwargs):
        logging.debug(f"Session: {dict(session)}")
        if not session.get('is_admin', False):
            logging.warning("Access denied: Admin privileges required")
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and store session."""
    data = request.get_json()
    if not data:
        logging.warning("Login attempt with invalid JSON body")
        return jsonify({'error': 'Request body must be JSON'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        logging.warning("Login attempt with missing email or password")
        return jsonify({'error': 'Email and password are required'}), 400

    if not validate_email(email):
        logging.warning(f"Login attempt with invalid email format: {email}")
        return jsonify({'error': 'Invalid email format'}), 400

    try:
        user = user_manager.get_user_by_email(email)
        if user and user_manager.validate_password(user['id'], password):
            # Store user info in session
            session['user_id'] = user['id']
            session['is_admin'] = bool(user['is_admin'])  # Ensure boolean
            logging.info(f"User {user['id']} logged in successfully")
            return jsonify({
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': bool(user['is_admin'])  # Return boolean
                }
            }), 200
        logging.warning(f"Failed login attempt for email: {email}")
        return jsonify({'error': 'Invalid credentials'}), 401
    except SQLAlchemyError as e:
        logging.error(f"Database error during login for email {email}: {e}")
        return jsonify({'error': 'Failed to login due to database error'}), 500

@auth_bp.route('/auth/me', methods=['GET'])
@session_required
def get_current_user():
    """Return details of the currently authenticated user."""
    user_id = session['user_id']
    logging.debug(f"Fetching current user: {user_id}")
    try:
        user = user_manager.get_user_by_id(user_id)
        if user:
            return jsonify({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': bool(user['is_admin']),  # Ensure boolean
                'full_name': user['full_name'],
                'phone_number': user['phone_number'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None  # Serialize datetime
            }), 200
        logging.warning(f"User not found for ID: {user_id}")
        return jsonify({'error': 'User not found'}), 404
    except SQLAlchemyError as e:
        logging.error(f"Database error retrieving user {user_id}: {e}")
        return jsonify({'error': 'Failed to retrieve user due to database error'}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@session_required
def logout():
    """Log out the current user by clearing the session."""
    user_id = session.get('user_id')
    try:
        session.clear()
        logging.info(f"User {user_id} logged out successfully")
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        logging.error(f"Error during logout for user {user_id}: {e}")
        return jsonify({'error': 'Failed to logout due to server error'}), 500