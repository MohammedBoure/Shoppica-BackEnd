from .base import Database
import sqlite3
import logging

class ReviewManager(Database):
    """Manages operations for the reviews table in the database."""

    def add_review(self, user_id, product_id, rating, comment=None):
        """Adds a new review for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reviews (user_id, product_id, rating, comment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, product_id, rating, comment, self.get_current_timestamp()))
                conn.commit()
                review_id = cursor.lastrowid
                logging.info(f"Review added for product {product_id} by user {user_id} with ID: {review_id}")
                return review_id
        except sqlite3.Error as e:
            logging.error(f"Error adding review for product {product_id} by user {user_id}: {e}")
            return None

    def get_review_by_id(self, review_id):
        """Retrieves a review by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM reviews WHERE id = ?', (review_id,))
                review = cursor.fetchone()
                logging.info(f"Retrieved review with ID: {review_id}")
                return review
        except sqlite3.Error as e:
            logging.error(f"Error retrieving review by ID {review_id}: {e}")
            return None

    def get_reviews_by_product(self, product_id):
        """Retrieves all reviews for a product."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM reviews WHERE product_id = ?', (product_id,))
                reviews = cursor.fetchall()
                logging.info(f"Retrieved {len(reviews)} reviews for product {product_id}")
                return reviews
        except sqlite3.Error as e:
            logging.error(f"Error retrieving reviews for product {product_id}: {e}")
            return []

    def update_review(self, review_id, rating=None, comment=None):
        """Updates review details. Only provided fields are updated."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                updates = []
                params = []
                
                if rating is not None:
                    updates.append('rating = ?')
                    params.append(rating)
                if comment is not None:
                    updates.append('comment = ?')
                    params.append(comment)
                
                if not updates:
                    logging.info(f"No updates provided for review ID: {review_id}")
                    return True

                params.append(review_id)
                query = f'UPDATE reviews SET {", ".join(updates)} WHERE id = ?'
                cursor.execute(query, params)
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Updated review with ID: {review_id}")
                    return True
                else:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error updating review {review_id}: {e}")
            return False

    def delete_review(self, review_id):
        """Deletes a review by its ID."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Deleted review with ID: {review_id}")
                    return True
                else:
                    logging.warning(f"No review found with ID: {review_id}")
                    return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting review {review_id}: {e}")
            return False

    def get_reviews(self, page=1, per_page=20):
        """Retrieves reviews with pagination."""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as total FROM reviews')
                total = cursor.fetchone()['total']
                cursor.execute('''
                    SELECT * FROM reviews
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                ''', (per_page, (page - 1) * per_page))
                reviews = cursor.fetchall()
                logging.info(f"Retrieved {len(reviews)} reviews. Total: {total}")
                return reviews, total
        except sqlite3.Error as e:
            logging.error(f"Error retrieving reviews: {e}")
            return [], 0