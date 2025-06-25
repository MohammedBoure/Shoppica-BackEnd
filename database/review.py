from .base import Database, Review, User, Product
from sqlalchemy import func, case
from sqlalchemy.exc import SQLAlchemyError
import logging

class ReviewManager(Database):
    """Manages operations for the reviews table in the database using SQLAlchemy ORM."""

    def add_review(self, user_id, product_id, rating, comment=None):
        """Adds a new review for a product."""
        try:
            with next(self.get_db_session()) as session:
                # Verify that user and product exist
                if not session.query(User).filter_by(id=user_id).first():
                    logging.error(f"User {user_id} does not exist")
                    return None
                if not session.query(Product).filter_by(id=product_id).first():
                    logging.error(f"Product {product_id} does not exist")
                    return None

                review = Review(
                    user_id=user_id,
                    product_id=product_id,
                    rating=rating,
                    comment=comment,
                    created_at=self.get_current_timestamp()
                )
                session.add(review)
                session.commit()
                logging.info(f"Review added for product {product_id} by user {user_id} with ID: {review.id}")
                return review.id
        except SQLAlchemyError as e:
            logging.error(f"Error adding review for product {product_id} by user {user_id}: {e}")
            session.rollback()
            return None

    def get_review_by_id(self, review_id):
        """Retrieves a review by its ID."""
        try:
            with next(self.get_db_session()) as session:
                review = session.query(Review).filter_by(id=review_id).first()
                if review:
                    review_dict = {
                        'id': review.id,
                        'user_id': review.user_id,
                        'product_id': review.product_id,
                        'rating': review.rating,
                        'comment': review.comment,
                        'created_at': review.created_at.isoformat() if review.created_at else None
                    }
                    logging.info(f"Retrieved review with ID: {review_id}")
                    return review_dict
                return None
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving review by ID {review_id}: {e}")
            return None

    def get_reviews_by_product(self, product_id):
        """Retrieves all reviews for a product."""
        try:
            with next(self.get_db_session()) as session:
                reviews = session.query(Review).filter_by(product_id=product_id).all()
                reviews_list = [{
                    'id': review.id,
                    'user_id': review.user_id,
                    'product_id': review.product_id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat() if review.created_at else None
                } for review in reviews]
                logging.info(f"Retrieved {len(reviews_list)} reviews for product {product_id}")
                return reviews_list
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving reviews for product {product_id}: {e}")
            return []

    def update_review(self, review_id, rating=None, comment=None):
        """Updates review details. Only provided fields are updated."""
        try:
            with next(self.get_db_session()) as session:
                review = session.query(Review).filter_by(id=review_id).first()
                if not review:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False

                if rating is not None:
                    review.rating = rating
                if comment is not None:
                    review.comment = comment

                if rating is None and comment is None:
                    logging.info(f"No updates provided for review ID: {review_id}")
                    return True

                session.commit()
                logging.info(f"Updated review with ID: {review_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error updating review {review_id}: {e}")
            session.rollback()
            return False

    def delete_review(self, review_id):
        """Deletes a review by its ID."""
        try:
            with next(self.get_db_session()) as session:
                review = session.query(Review).filter_by(id=review_id).first()
                if not review:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False

                session.delete(review)
                session.commit()
                logging.info(f"Deleted review with ID: {review_id}")
                return True
        except SQLAlchemyError as e:
            logging.error(f"Error deleting review {review_id}: {e}")
            session.rollback()
            return False

    def get_reviews(self, page=1, per_page=20):
        """Retrieves reviews with pagination."""
        try:
            with next(self.get_db_session()) as session:
                total = session.query(func.count(Review.id)).scalar()
                reviews = session.query(Review).order_by(Review.created_at.desc())\
                    .limit(per_page).offset((page - 1) * per_page).all()
                reviews_list = [{
                    'id': review.id,
                    'user_id': review.user_id,
                    'product_id': review.product_id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat() if review.created_at else None
                } for review in reviews]
                logging.info(f"Retrieved {len(reviews_list)} reviews. Total: {total}")
                return reviews_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving reviews: {e}")
            return [], 0

    from sqlalchemy import or_

    def search_reviews(self, product_id=None, user_id=None, min_rating=None, max_rating=None,
                    comment_keyword=None, page=1, per_page=20):
        """Searches reviews based on product_id, user_id, rating range, and comment keyword with pagination."""
        try:
            with next(self.get_db_session()) as session:
                query = session.query(Review)

                if product_id is not None:
                    query = query.filter(Review.product_id == product_id)
                if user_id is not None:
                    query = query.filter(Review.user_id == user_id)
                if min_rating is not None:
                    query = query.filter(Review.rating >= min_rating)
                if max_rating is not None:
                    query = query.filter(Review.rating <= max_rating)
                if comment_keyword:
                    query = query.filter(Review.comment.ilike(f'%{comment_keyword}%'))

                total = query.count()
                reviews = query.order_by(Review.created_at.desc()) \
                    .limit(per_page).offset((page - 1) * per_page).all()

                reviews_list = [{
                    'id': review.id,
                    'user_id': review.user_id,
                    'product_id': review.product_id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat() if review.created_at else None
                } for review in reviews]

                logging.info(f"Found {len(reviews_list)} reviews matching search criteria. Total: {total}")
                return reviews_list, total
        except SQLAlchemyError as e:
            logging.error(f"Error searching reviews: {e}")
            return [], 0

    def delete_reviews_by_product(self, product_id):
        """Deletes all reviews for a specific product."""
        try:
            with next(self.get_db_session()) as session:
                deleted_count = session.query(Review).filter_by(product_id=product_id).delete()
                session.commit()
                logging.info(f"Deleted {deleted_count} reviews for product {product_id}")
                return deleted_count
        except SQLAlchemyError as e:
            logging.error(f"Error deleting reviews for product {product_id}: {e}")
            session.rollback()
            return 0

    def delete_reviews_by_user(self, user_id):
        """Deletes all reviews by a specific user."""
        try:
            with next(self.get_db_session()) as session:
                deleted_count = session.query(Review).filter_by(user_id=user_id).delete()
                session.commit()
                logging.info(f"Deleted {deleted_count} reviews by user {user_id}")
                return deleted_count
        except SQLAlchemyError as e:
            logging.error(f"Error deleting reviews for user {user_id}: {e}")
            session.rollback()
            return 0

    def get_product_review_stats(self, product_id):
        """Returns statistics about reviews for a specific product."""
        try:
            with next(self.get_db_session()) as session:
                stats = session.query(
                    func.count(Review.id).label('total_reviews'),
                    func.avg(Review.rating).label('average_rating'),
                    func.sum(case((Review.rating == 1, 1), else_=0)).label('rating_1'),
                    func.sum(case((Review.rating == 2, 1), else_=0)).label('rating_2'),
                    func.sum(case((Review.rating == 3, 1), else_=0)).label('rating_3'),
                    func.sum(case((Review.rating == 4, 1), else_=0)).label('rating_4'),
                    func.sum(case((Review.rating == 5, 1), else_=0)).label('rating_5')
                ).filter(Review.product_id == product_id).one_or_none()

                if stats and stats.total_reviews > 0:
                    stats_dict = {
                        'total_reviews': stats.total_reviews,
                        'average_rating': round(float(stats.average_rating), 2) if stats.average_rating else 0.0,
                        'rating_distribution': {
                            '1': stats.rating_1,
                            '2': stats.rating_2,
                            '3': stats.rating_3,
                            '4': stats.rating_4,
                            '5': stats.rating_5
                        }
                    }
                    logging.info(f"Retrieved review stats for product {product_id}: {stats_dict}")
                    return stats_dict
                return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving review stats for product {product_id}: {e}")
            return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}

    def get_overall_review_stats(self):
        """Returns overall statistics for all reviews."""
        try:
            with next(self.get_db_session()) as session:
                stats = session.query(
                    func.count(Review.id).label('total_reviews'),
                    func.avg(Review.rating).label('average_rating'),
                    func.sum(case((Review.rating == 1, 1), else_=0)).label('rating_1'),
                    func.sum(case((Review.rating == 2, 1), else_=0)).label('rating_2'),
                    func.sum(case((Review.rating == 3, 1), else_=0)).label('rating_3'),
                    func.sum(case((Review.rating == 4, 1), else_=0)).label('rating_4'),
                    func.sum(case((Review.rating == 5, 1), else_=0)).label('rating_5')
                ).one_or_none()

                if stats and stats.total_reviews > 0:
                    stats_dict = {
                        'total_reviews': stats.total_reviews,
                        'average_rating': round(float(stats.average_rating), 2) if stats.average_rating else 0.0,
                        'rating_distribution': {
                            '1': stats.rating_1,
                            '2': stats.rating_2,
                            '3': stats.rating_3,
                            '4': stats.rating_4,
                            '5': stats.rating_5
                        }
                    }
                    logging.info(f"Retrieved overall review stats: {stats_dict}")
                    return stats_dict
                return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}
        except SQLAlchemyError as e:
            logging.error(f"Error retrieving overall review stats: {e}")
            return {'total_reviews': 0, 'average_rating': 0.0, 'rating_distribution': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}}