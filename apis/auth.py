from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from database import UserManager
from functools import wraps

auth_bp = Blueprint('auth', __name__)
user_manager = UserManager()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = user_manager.get_user_by_email(email)
    if user and user_manager.validate_password(user['id'], password):  # Ensure this compares SHA256 hashes
        access_token = create_access_token(
            identity=str(user['id']),
            additional_claims={'is_admin': bool(user['is_admin'])}
        )
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Return details of the currently authenticated user."""
    current_user_id = get_jwt_identity()
    user = user_manager.get_user_by_id(int(current_user_id))
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': user['is_admin'],
            'full_name': user['full_name'],
            'phone_number': user['phone_number'],
            'created_at': user['created_at']
        }), 200
    return jsonify({'error': 'User not found'}), 404

def admin_required(fn):
    """Decorator to restrict route access to admins only."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    return wrapper
