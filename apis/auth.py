from flask import Blueprint, request, jsonify, session
from database import UserManager
from functools import wraps

auth_bp = Blueprint('auth', __name__)
user_manager = UserManager()

def session_required(fn):
    """Decorator to ensure user is authenticated via session."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    """Decorator to restrict route access to admins only."""
    @wraps(fn)
    @session_required
    def wrapper(*args, **kwargs):
        print("Session:", dict(session))
        if not session.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and store session."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = user_manager.get_user_by_email(email)
    if user and user_manager.validate_password(user['id'], password):
        # Store user info in session
        session['user_id'] = user['id']
        session['is_admin'] = int(user['is_admin'])
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/auth/me', methods=['GET'])
@session_required
def get_current_user():
    print("Session in /me:", dict(session))
    """Return details of the currently authenticated user."""
    user_id = session['user_id']
    user = user_manager.get_user_by_id(int(user_id))
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

@auth_bp.route('/auth/logout', methods=['POST'])
@session_required
def logout():
    """Log out the current user by clearing the session."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200