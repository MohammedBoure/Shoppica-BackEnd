from flask import Blueprint, request, jsonify, session
from database import UserManager
from .auth import admin_required, session_required
import logging
import re
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

users_bp = Blueprint('users', __name__)

# Initialize UserManager
user_manager = UserManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_email(email):
    """Validate email format."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def serialize_user(user):
    """Convert user dictionary to JSON-serializable format."""
    return {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'full_name': user['full_name'],
        'phone_number': user['phone_number'],
        'is_admin': bool(user['is_admin']),  # Convert Integer to Boolean
        'created_at': user['created_at'].isoformat() if user['created_at'] else None  # Serialize datetime
    }

@users_bp.route('/users', methods=['POST'])
def add_user():
    """API to add a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    try:
        user_id = user_manager.add_user(username, email, password, full_name, phone_number, is_admin=0)
        if user_id:
            return jsonify({'message': 'User added successfully', 'user_id': user_id}), 201
        return jsonify({'error': 'Username or email already exists'}), 409
    except SQLAlchemyError as e:
        logging.error(f"Database error adding user {username}: {e}")
        return jsonify({'error': 'Failed to add user due to database error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@session_required
def get_user_by_id(user_id):
    """API to retrieve a user by ID."""
    current_user_id = session.get('user_id')  # Assume session stores user_id as int
    is_admin = session.get('is_admin', False)

    # Allow access if user is requesting their own data or is an admin
    if current_user_id != user_id and not is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403

    try:
        user = user_manager.get_user_by_id(user_id)
        if user:
            return jsonify(serialize_user(user)), 200
        return jsonify({'error': 'User not found'}), 404
    except SQLAlchemyError as e:
        logging.error(f"Database error retrieving user {user_id}: {e}")
        return jsonify({'error': 'Failed to retrieve user due to database error'}), 500

@users_bp.route('/users/email/<string:email>', methods=['GET'])
@session_required
def get_user_by_email(email):
    """API to retrieve a user by email."""
    current_user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    try:
        user = user_manager.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Allow access if user is requesting their own data or is an admin
        if user['id'] != current_user_id and not is_admin:
            return jsonify({'error': 'Unauthorized access'}), 403

        return jsonify(serialize_user(user)), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error retrieving user by email {email}: {e}")
        return jsonify({'error': 'Failed to retrieve user due to database error'}), 500

@users_bp.route('/users/username/<string:username>', methods=['GET'])
@session_required
def get_user_by_username(username):
    """API to retrieve a user by username."""
    current_user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    try:
        user = user_manager.get_user_by_username(username)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Allow access if user is requesting their own data or is an admin
        if user['id'] != current_user_id and not is_admin:
            return jsonify({'error': 'Unauthorized access'}), 403

        return jsonify(serialize_user(user)), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error retrieving user by username {username}: {e}")
        return jsonify({'error': 'Failed to retrieve user due to database error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@session_required
def update_user(user_id):
    """API to update user details."""
    current_user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    # Allow update if user is updating their own data or is an admin
    if current_user_id != user_id and not is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    is_admin_update = data.get('is_admin')
    password = data.get('password')

    # Restrict is_admin updates to admins only
    if is_admin_update is not None and not is_admin:
        return jsonify({'error': 'Only admins can update is_admin status'}), 403

    if password and len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    try:
        success = user_manager.update_user(user_id, full_name, phone_number, is_admin_update, password)
        if success:
            return jsonify({'message': 'User updated successfully'}), 200
        return jsonify({'error': 'User not found or no updates provided'}), 404
    except SQLAlchemyError as e:
        logging.error(f"Database error updating user {user_id}: {e}")
        return jsonify({'error': 'Failed to update user due to database error'}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """API to delete a user by ID."""
    try:
        success = user_manager.delete_user(user_id)
        if success:
            return jsonify({'message': 'User deleted successfully'}), 200
        return jsonify({'error': 'User not found or failed to delete'}), 404
    except SQLAlchemyError as e:
        logging.error(f"Database error deleting user {user_id}: {e}")
        return jsonify({'error': 'Failed to delete user due to database error'}), 500

@users_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """API to retrieve users with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    try:
        users, total = user_manager.get_users(page, per_page)
        users_list = [serialize_user(user) for user in users]
        return jsonify({
            'users': users_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error retrieving users: {e}")
        return jsonify({'error': 'Failed to retrieve users due to database error'}), 500

@users_bp.route('/users/<int:user_id>/validate-password', methods=['POST'])
@session_required
def validate_password(user_id):
    """API to validate a user's password."""
    current_user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)

    # Allow validation if user is validating their own password or is an admin
    if current_user_id != user_id and not is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    try:
        is_valid = user_manager.validate_password(user_id, password)
        if is_valid:
            return jsonify({'message': 'Password is valid'}), 200
        return jsonify({'error': 'Invalid password'}), 401
    except SQLAlchemyError as e:
        logging.error(f"Database error validating password for user {user_id}: {e}")
        return jsonify({'error': 'Failed to validate password due to database error'}), 500

@users_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users():
    """API to search for users by username or email with pagination."""
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Search query parameter "q" is required'}), 400

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    try:
        users, total = user_manager.search_users(query, page, per_page)
        users_list = [serialize_user(user) for user in users]
        return jsonify({
            'users': users_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error searching users with query {query}: {e}")
        return jsonify({'error': 'Failed to search users due to database error'}), 500

@users_bp.route('/users/clear-all', methods=['DELETE'])
@admin_required
def clear_all_users():
    """
    API to delete all users from the database.
    This is a destructive operation and should be used with caution.
    """
    try:
        user_manager.clear_all_users()
        return jsonify({'message': 'All users have been successfully deleted'}), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error clearing all users: {e}")
        return jsonify({'error': 'Failed to clear users due to database error'}), 500

@users_bp.route('/users/number', methods=['GET'])
@admin_required  # Only allow access to admins
def get_total_users():
    """
    API endpoint to return the total number of users in the database.
    Accessible only by admin users.
    """
    try:
        # Call UserManager method to get total user count
        total_users = user_manager.get_total_user_count()
        
        # Return the count as a JSON response
        return jsonify({'total_users': total_users}), 200

    except SQLAlchemyError as e:
        # Log any database errors
        logging.error(f"Error fetching total users: {e}")
        
        # Return server error message
        return jsonify({'error': 'Failed to retrieve user count'}), 500
