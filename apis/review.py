from flask import Blueprint, request, jsonify, session
from database import ReviewManager
from .auth import admin_required, session_required
import logging

reviews_bp = Blueprint('reviews', __name__)

# Initialize ReviewManager
review_manager = ReviewManager()

@reviews_bp.route('/reviews', methods=['POST'])
@session_required
def add_review():
    """API to add a new review."""
    try:
        current_user_id = int(session.get('user_id'))
        is_admin = session.get('is_admin', False)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid session data'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    user_id = data.get('user_id')
    product_id = data.get('product_id')
    rating = data.get('rating')
    comment = data.get('comment')

    # Validate required fields and rating range
    if not user_id or not product_id or rating is None:
        return jsonify({'error': 'User ID, product ID, and rating are required'}), 400
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

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
        return jsonify(review), 200
    return jsonify({'error': 'Review not found'}), 404

@reviews_bp.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_reviews_by_product(product_id):
    """API to retrieve all reviews for a product."""
    reviews = review_manager.get_reviews_by_product(product_id)
    return jsonify({'reviews': reviews}), 200

@reviews_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@session_required
def update_review(review_id):
    """API to update review details."""
    try:
        current_user_id = int(session.get('user_id'))
        is_admin = session.get('is_admin', False)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid session data'}), 401

    review = review_manager.get_review_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    # Allow update if review belongs to the user or if admin
    if review['user_id'] != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to update this review'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    rating = data.get('rating')
    comment = data.get('comment')

    # Validate rating if provided
    if rating is not None and (not isinstance(rating, int) or rating < 1 or rating > 5):
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

    success = review_manager.update_review(review_id, rating, comment)
    if success:
        return jsonify({'message': 'Review updated successfully'}), 200
    return jsonify({'error': 'Failed to update review'}), 400

@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@session_required
def delete_review(review_id):
    """API to delete a review by ID."""
    try:
        current_user_id = int(session.get('user_id'))
        is_admin = session.get('is_admin', False)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid session data'}), 401

    review = review_manager.get_review_by_id(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404

    # Allow deletion if review belongs to the user or if admin
    if review['user_id'] != current_user_id and not is_admin:
        return jsonify({'error': 'Unauthorized to delete this review'}), 403

    success = review_manager.delete_review(review_id)
    if success:
        return jsonify({'message': 'Review deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete review'}), 500

@reviews_bp.route('/reviews', methods=['GET'])
@admin_required
def get_reviews():
    """API to retrieve reviews with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    if page < 1 or per_page < 1:
        return jsonify({'error': 'Page and per_page must be positive integers'}), 400

    reviews, total = review_manager.get_reviews(page, per_page)
    return jsonify({
        'reviews': reviews,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@reviews_bp.route('/reviews/search', methods=['GET'])
def search_reviews():
    """API to search for reviews based on various criteria with pagination, including comment keyword."""
    product_id = request.args.get('product_id', type=int)
    user_id = request.args.get('user_id', type=int)
    min_rating = request.args.get('min_rating', type=int)
    max_rating = request.args.get('max_rating', type=int)
    comment_keyword = request.args.get('comment', type=str)  # New: accept keyword from query
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Validate pagination parameters
    if page < 1 or per_page < 1:
        return jsonify({'error': 'Page and per_page must be positive integers'}), 400

    # Validate rating range
    if min_rating is not None and (min_rating < 1 or min_rating > 5):
        return jsonify({'error': 'min_rating must be between 1 and 5'}), 400
    if max_rating is not None and (max_rating < 1 or max_rating > 5):
        return jsonify({'error': 'max_rating must be between 1 and 5'}), 400
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        return jsonify({'error': 'min_rating cannot be greater than max_rating'}), 400

    # Require at least one search parameter
    if not any([product_id, user_id, min_rating, max_rating, comment_keyword]):
        return jsonify({'error': 'At least one search parameter (product_id, user_id, min_rating, max_rating, comment) is required'}), 400

    reviews, total = review_manager.search_reviews(
        product_id=product_id,
        user_id=user_id,
        min_rating=min_rating,
        max_rating=max_rating,
        comment_keyword=comment_keyword,  # Pass to backend method
        page=page,
        per_page=per_page
    )

    return jsonify({
        'reviews': reviews,
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200


@reviews_bp.route('/reviews/by-product/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_reviews_by_product(product_id):
    """API for admins to delete all reviews for a specific product."""
    deleted_count = review_manager.delete_reviews_by_product(product_id)
    if deleted_count > 0:
        return jsonify({
            'message': f'Successfully deleted {deleted_count} reviews for product ID {product_id}.'
        }), 200
    return jsonify({
        'message': f'No reviews found for product ID {product_id}.'
    }), 200

@reviews_bp.route('/reviews/by-user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_reviews_by_user(user_id):
    """API for admins to delete all reviews by a specific user."""
    deleted_count = review_manager.delete_reviews_by_user(user_id)
    if deleted_count > 0:
        return jsonify({
            'message': f'Successfully deleted {deleted_count} reviews by user ID {user_id}.'
        }), 200
    return jsonify({
        'message': f'No reviews found for user ID {user_id}.'
    }), 200

@reviews_bp.route('/reviews/stats/product/<int:product_id>', methods=['GET'])
def get_product_review_stats(product_id):
    """API to get review statistics for a specific product."""
    stats = review_manager.get_product_review_stats(product_id)
    return jsonify(stats), 200

@reviews_bp.route('/reviews/stats/overall', methods=['GET'])
@admin_required
def get_overall_review_stats():
    """API for admins to get overall review statistics for all products."""
    stats = review_manager.get_overall_review_stats()
    return jsonify(stats), 200