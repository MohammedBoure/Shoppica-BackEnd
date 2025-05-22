from flask import Blueprint, request, jsonify
from database import UserManager
import logging

users_bp = Blueprint('users', __name__)

# Initialize UserManager
user_manager = UserManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@users_bp.route('/users', methods=['POST'])
def add_user():
    """API to add a new user."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    is_admin = data.get('is_admin', 0)

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    user_id = user_manager.add_user(username, email, password, full_name, phone_number, is_admin)
    if user_id:
        return jsonify({'message': 'User added successfully', 'user_id': user_id}), 201
    return jsonify({'error': 'Failed to add user'}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """API to retrieve a user by ID."""
    user = user_manager.get_user_by_id(user_id)
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'phone_number': user['phone_number'],
            'is_admin': user['is_admin'],
            'created_at': user['created_at']
        }), 200
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/users/email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    """API to retrieve a user by email."""
    user = user_manager.get_user_by_email(email)
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'phone_number': user['phone_number'],
            'is_admin': user['is_admin'],
            'created_at': user['created_at']
        }), 200
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/users/username/<string:username>', methods=['GET'])
def get_user_by_username(username):
    """API to retrieve a user by username."""
    user = user_manager.get_user_by_username(username)
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'phone_number': user['phone_number'],
            'is_admin': user['is_admin'],
            'created_at': user['created_at']
        }), 200
    return jsonify({'error': 'User not found'}), 404

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """API to update user details."""
    data = request.get_json()
    full_name = data.get('full_name')
    phone_number = data.get('phone_number')
    is_admin = data.get('is_admin')
    password = data.get('password')

    success = user_manager.update_user(user_id, full_name, phone_number, is_admin, password)
    if success:
        return jsonify({'message': 'User updated successfully'}), 200
    return jsonify({'error': 'Failed to update user'}), 400

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """API to delete a user by ID."""
    success = user_manager.delete_user(user_id)
    if success:
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found or failed to delete'}), 404

@users_bp.route('/users', methods=['GET'])
def get_users():
    """API to retrieve users with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    users, total = user_manager.get_users(page, per_page)
    users_list = [
        {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'phone_number': user['phone_number'],
            'is_admin': user['is_admin'],
            'created_at': user['created_at']
        } for user in users
    ]
    return jsonify({
        'users': users_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@users_bp.route('/users/<int:user_id>/validate-password', methods=['POST'])
def validate_password(user_id):
    """API to validate a user's password."""
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'error': 'Password is required'}), 400

    is_valid = user_manager.validate_password(user_id, password)
    if is_valid:
        return jsonify({'message': 'Password is valid'}), 200
    return jsonify({'error': 'Invalid password'}), 401