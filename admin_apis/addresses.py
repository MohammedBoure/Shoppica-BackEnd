from flask import Blueprint, request, jsonify
from database import AddressManager
import logging

addresses_bp = Blueprint('addresses', __name__)

# Initialize AddressManager
address_manager = AddressManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@addresses_bp.route('/addresses', methods=['POST'])
def add_address():
    """API to add a new address."""
    data = request.get_json()
    user_id = data.get('user_id')
    address_line1 = data.get('address_line1')
    city = data.get('city')
    country = data.get('country')
    address_line2 = data.get('address_line2')
    state = data.get('state')
    postal_code = data.get('postal_code')
    is_default = data.get('is_default', 0)

    if not user_id or not address_line1 or not city or not country:
        return jsonify({'error': 'User ID, address line 1, city, and country are required'}), 400

    address_id = address_manager.add_address(user_id, address_line1, city, country, address_line2, state, postal_code, is_default)
    if address_id:
        return jsonify({'message': 'Address added successfully', 'address_id': address_id}), 201
    return jsonify({'error': 'Failed to add address'}), 500

@addresses_bp.route('/addresses/<int:address_id>', methods=['GET'])
def get_address_by_id(address_id):
    """API to retrieve an address by ID."""
    address = address_manager.get_address_by_id(address_id)
    if address:
        return jsonify({
            'id': address['id'],
            'user_id': address['user_id'],
            'address_line1': address['address_line1'],
            'address_line2': address['address_line2'],
            'city': address['city'],
            'state': address['state'],
            'postal_code': address['postal_code'],
            'country': address['country'],
            'is_default': address['is_default']
        }), 200
    return jsonify({'error': 'Address not found'}), 404

@addresses_bp.route('/addresses/user/<int:user_id>', methods=['GET'])
def get_addresses_by_user(user_id):
    """API to retrieve all addresses for a user."""
    addresses = address_manager.get_addresses_by_user(user_id)
    if addresses:
        addresses_list = [
            {
                'id': address['id'],
                'user_id': address['user_id'],
                'address_line1': address['address_line1'],
                'address_line2': address['address_line2'],
                'city': address['city'],
                'state': address['state'],
                'postal_code': address['postal_code'],
                'country': address['country'],
                'is_default': address['is_default']
            } for address in addresses
        ]
        return jsonify({'addresses': addresses_list}), 200
    return jsonify({'addresses': [], 'message': 'No addresses found for this user'}), 200

@addresses_bp.route('/addresses/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """API to update address details."""
    data = request.get_json()
    address_line1 = data.get('address_line1')
    address_line2 = data.get('address_line2')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    country = data.get('country')
    is_default = data.get('is_default')

    success = address_manager.update_address(address_id, address_line1, address_line2, city, state, postal_code, country, is_default)
    if success:
        return jsonify({'message': 'Address updated successfully'}), 200
    return jsonify({'error': 'Failed to update address'}), 400

@addresses_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """API to delete an address by ID."""
    success = address_manager.delete_address(address_id)
    if success:
        return jsonify({'message': 'Address deleted successfully'}), 200
    return jsonify({'error': 'Address not found or failed to delete'}), 404

@addresses_bp.route('/addresses', methods=['GET'])
def get_addresses():
    """API to retrieve addresses with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    addresses, total = address_manager.get_addresses(page, per_page)
    addresses_list = [
        {
            'id': address['id'],
            'user_id': address['user_id'],
            'address_line1': address['address_line1'],
            'address_line2': address['address_line2'],
            'city': address['city'],
            'state': address['state'],
            'postal_code': address['postal_code'],
            'country': address['country'],
            'is_default': address['is_default']
        } for address in addresses
    ]
    return jsonify({
        'addresses': addresses_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200