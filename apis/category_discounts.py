from flask import Blueprint, request, jsonify, session
from database import CategoryDiscountManager
import logging
import traceback

db = CategoryDiscountManager()
category_discounts_bp = Blueprint('category_discounts', __name__)
logger = logging.getLogger(__name__)

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_dicts(rows):
    return [dict(row) for row in rows]

def require_admin():
    if not session.get("is_admin"):
        return jsonify({'error': 'Unauthorized'}), 403

@category_discounts_bp.route('/category_discounts', methods=['POST'])
def add_category_discount():
    response = require_admin()
    if response: return response

    data = request.get_json()
    category_id = data.get('category_id')
    discount_percentage = data.get('discount_percent')
    start_date = data.get('starts_at')
    end_date = data.get('ends_at')
    is_active = data.get('is_active', True)

    try:
        discount_id = db.add_category_discount(
            category_id, discount_percentage, start_date, end_date, is_active
        )
        if discount_id is None:
            raise Exception("Failed to insert discount")
        logger.info(f"Category discount added: {discount_id}")
        new_discount = db.get_category_discount_by_id(discount_id)
        return jsonify({
            'message': 'Category discount added',
            'discount': row_to_dict(new_discount)
        }), 201
    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['GET'])
def get_category_discount(discount_id):
    try:
        discount = db.get_category_discount_by_id(discount_id)
        if discount:
            return jsonify(row_to_dict(discount)), 200
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts', methods=['GET'])
def get_category_discounts():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        discounts, total = db.get_category_discounts(page, per_page)
        return jsonify({
            'category_discounts': rows_to_dicts(discounts),
            'total': total
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts/valid/<int:category_id>', methods=['GET'])
def get_valid_category_discounts(category_id):
    try:
        discounts = db.get_valid_category_discounts(category_id)
        return jsonify({'category_discounts': rows_to_dicts(discounts)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts/category/<int:category_id>', methods=['GET'])
def get_category_discounts_by_category(category_id):
    try:
        discounts = db.get_category_discounts_by_category(category_id)
        return jsonify({'category_discounts': rows_to_dicts(discounts)}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['PUT'])
def update_category_discount(discount_id):
    response = require_admin()
    if response: return response

    data = request.get_json()
    discount_percentage = data.get('discount_percent')
    start_date = data.get('starts_at')
    end_date = data.get('ends_at')
    is_active = data.get('is_active')

    try:
        updated = db.update_category_discount(
            discount_id, discount_percentage, start_date, end_date, is_active
        )
        if updated:
            updated_discount = db.get_category_discount_by_id(discount_id)
            return jsonify(row_to_dict(updated_discount)), 200
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@category_discounts_bp.route('/category_discounts/<int:discount_id>', methods=['DELETE'])
def delete_category_discount(discount_id):
    response = require_admin()
    if response: return response

    try:
        deleted = db.delete_category_discount(discount_id)
        if deleted:
            return jsonify({'message': 'Deleted'}), 200
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
