from flask import Blueprint, request, jsonify, session
from database import ReviewManager
from .auth import admin_required, session_required
import logging

reviews_bp = Blueprint('reviews', __name__)

# Initialize ReviewManager
review_manager = ReviewManager()

# Configure logging
logging.basicConfig(level=logging.INFO)

@reviews_bp.route('/reviews', methods=['POST'])
@session_required
def add_review():
    """API to add a new review."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    data = request.get_json()
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment')

    if not user_id or not product_id or rating is None:
        return jsonify({'error': 'User ID, product ID, and rating are required'}), 400

    # Allow adding review only for the current user or if admin
    if user_id != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to add review for another user'}), 403

    review_id = review_manager.add_review(user_id, product_id, rating, comment)
    if review_id:
        return jsonify({'message': 'Review added successfully', 'review_id': review_id}), 201
    return jsonify({'error': 'Failed to add review'}), 500

@reviews_bp.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_by_id(review_id):
    """API to retrieve a review by ID."""
    review = review_manager.get_review_by_id(review_id)
    if review:
        return jsonify({
            'id': review['id'],
            'user_id': review['user_id'],
            'product_id': review['product_id'],
            'rating': review['rating'],
            'comment': review['comment'],
            'created_at': review['created_at']
        }), 200
    return jsonify({'error': 'Review not found'}), 404

@reviews_bp.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_reviews_by_product(product_id):
    """API to retrieve all reviews for a product."""
    reviews = review_manager.get_reviews_by_product(product_id)
    if reviews:
        reviews_list = [
            {
                'id': review['id'],
                'user_id': review['user_id'],
                'product_id': review['product_id'],
                'rating': review['rating'],
                'comment': review['comment'],
                'created_at': review['created_at']
            } for review in reviews
        ]
        return jsonify({'reviews': reviews_list}), 200
    return jsonify({'reviews': [], 'message': 'No reviews found for this product'}), 200

@reviews_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@session_required
def update_review(review_id):
    """API to update review details."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    review = review_manager.get_review_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    # Allow update if review belongs to the user or if admin
    if review['user_id'] != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to update this review'}), 403

    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')

    success = review_manager.update_review(review_id, rating, comment)
    if success:
        return jsonify({'message': 'Review updated successfully'}), 200
    return jsonify({'error': 'Failed to update review'}), 400

@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@session_required
def delete_review(review_id):
    """API to delete a review by ID."""
    current_user_id = int(session['user_id'])
    is_admin = session.get('is_admin', False)

    review = review_manager.get_review_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    # Allow deletion if review belongs to the user or if admin
    if review['user_id'] != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to delete this review'}), 403

    success = review_manager.delete_review(review_id)
    if success:
        return jsonify({'message': 'Review deleted successfully'}), 200
    return jsonify({'error': 'Review not found or failed to delete'}), 404

@reviews_bp.route('/reviews', methods=['GET'])
@admin_required
def get_reviews():
    """API to retrieve reviews with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    reviews, total = review_manager.get_reviews(page, per_page)
    reviews_list = [
        {
            'id': review['id'],
            'user_id': review['user_id'],
            'product_id': review['product_id'],
            'rating': review['rating'],
            'comment': review['comment'],
            'created_at': review['created_at']
        } for review in reviews
    ]
    return jsonify({
        'reviews': reviews_list,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200