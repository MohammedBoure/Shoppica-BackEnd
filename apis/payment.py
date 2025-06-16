from flask import Blueprint, request, jsonify
from database import PaymentManager
from .auth import admin_required, session_required
import logging

payments_bp = Blueprint('payments', __name__)

# Initialize PaymentManager
payment_manager = PaymentManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@payments_bp.route('/payments', methods=['POST'])
@session_required
def add_payment():
    """API to add a new payment."""
    data = request.get_json()
    order_id = data.get('order_id')
    payment_method = data.get('payment_method')
    transaction_id = data.get('transaction_id')
    payment_status = data.get('payment_status', 'unpaid')

    if not order_id or not payment_method:
        return jsonify({'error': 'Order ID and payment method are required'}), 400

    payment_id = payment_manager.add_payment(order_id, payment_method, transaction_id, payment_status)
    if payment_id:
        return jsonify({'message': 'Payment added successfully', 'payment_id': payment_id}), 201
    return jsonify({'error': 'Failed to add payment'}), 500

@payments_bp.route('/payments/<int:payment_id>', methods=['GET'])
@session_required
def get_payment_by_id(payment_id):
    """API to retrieve a payment by ID."""
    payment = payment_manager.get_payment_by_id(payment_id)
    if payment:
        return jsonify({
            'id': payment['id'],
            'order_id': payment['order_id'],
            'payment_method': payment['payment_method'],
            'payment_status': payment['payment_status'],
            'transaction_id': payment['transaction_id'],
            'paid_at': payment['paid_at']
        }), 200
    return jsonify({'error': 'Payment not found'}), 404

@payments_bp.route('/payments/order/<int:order_id>', methods=['GET'])
@session_required
def get_payments_by_order(order_id):
    """API to retrieve all payments for an order."""
    payments = payment_manager.get_payments_by_order(order_id)
    if payments:
        payments_list = [
            {
                'id': payment['id'],
                'order_id': payment['order_id'],
                'payment_method': payment['payment_method'],
                'payment_status': payment['payment_status'],
                'transaction_id': payment['transaction_id'],
                'paid_at': payment['paid_at']
            } for payment in payments
        ]
        return jsonify({'payments': payments_list}), 200
    return jsonify({'payments': [], 'message': 'No payments found for this order'}), 200

@payments_bp.route('/payments/<int:payment_id>', methods=['PUT'])
@admin_required
def update_payment(payment_id):
    """API to update payment details."""
    data = request.get_json()
    payment_method = data.get('payment_method')
    payment_status = data.get('payment_status')
    transaction_id = data.get('transaction_id')

    success = payment_manager.update_payment(payment_id, payment_method, payment_status, transaction_id)
    if success:
        return jsonify({'message': 'Payment updated successfully'}), 200
    return jsonify({'error': 'Failed to update payment'}), 400

@payments_bp.route('/payments/<int:payment_id>', methods=['DELETE'])
@admin_required
def delete_payment(payment_id):
    """API to delete a payment by ID."""
    success = payment_manager.delete_payment(payment_id)
    if success:
        return jsonify({'message': 'Payment deleted successfully'}), 200
    return jsonify({'error': 'Payment not found or failed to delete'}), 404

@payments_bp.route('/payments', methods=['GET'])
@admin_required
def get_payments():
    """API to retrieve payments with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    payments, total = payment_manager.get_payments(page, per_page)
    payments_list = [
        {
            'id': payment['id'],
            'order_id': payment['order_id'],
            'payment_method': payment['payment_method'],
            'payment_status': payment['payment_status'],
            'transaction_id': payment['transaction_id'],
            'paid_at': payment['paid_at']
        } for payment in payments
    ]
    return jsonify({
        'payments': payments_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200